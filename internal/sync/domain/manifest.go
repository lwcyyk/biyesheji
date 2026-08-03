// Package domain defines signed, cloud-neutral synchronization manifests.
package domain

import (
	"bytes"
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"errors"
	"sort"

	"vpass.local/vpass/internal/protocol"
)

var (
	ErrInvalidSyncManifest      = errors.New("invalid sync manifest")
	ErrSyncManifestContext      = errors.New("sync manifest context mismatch")
	ErrSyncManifestVerification = errors.New("sync manifest signature verification failed")
)

const MaxManifestObjects = 10_000

type ObjectReference struct {
	ObjectDigest [sha256.Size]byte      `cbor:"object_digest"`
	ObjectType   protocol.ObjectType    `cbor:"object_type"`
	CredentialID *protocol.CredentialID `cbor:"credential_id"`
	Version      *uint64                `cbor:"version"`
	Size         uint64                 `cbor:"size"`
}

type ManifestPayload struct {
	Domain               string               `cbor:"domain"`
	NamespaceID          protocol.NamespaceID `cbor:"namespace_id"`
	DeviceID             protocol.DeviceID    `cbor:"device_id"`
	BaseCheckpoint       [sha256.Size]byte    `cbor:"base_checkpoint"`
	TargetCheckpoint     [sha256.Size]byte    `cbor:"target_checkpoint"`
	HighestDeviceCounter uint64               `cbor:"highest_device_counter"`
	ObjectSetRoot        [sha256.Size]byte    `cbor:"object_set_root"`
	ObjectCount          uint64               `cbor:"object_count"`
	CreatedSequence      uint64               `cbor:"created_sequence"`
}

type SignedManifest struct {
	payload   ManifestPayload
	objects   []ObjectReference
	sigInput  []byte
	signature protocol.Signature
	digest    [sha256.Size]byte
}

type manifestSigningPayload struct {
	Manifest ManifestPayload   `cbor:"manifest"`
	Objects  []ObjectReference `cbor:"objects"`
}

func SignManifest(
	privateKey ed25519.PrivateKey,
	chainID string,
	keyGeneration uint64,
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
	baseCheckpoint [sha256.Size]byte,
	targetCheckpoint [sha256.Size]byte,
	highestDeviceCounter uint64,
	createdSequence uint64,
	objects []ObjectReference,
) (*SignedManifest, error) {
	if len(privateKey) != ed25519.PrivateKeySize {
		return nil, ErrInvalidSyncManifest
	}
	canonicalObjects, root, err := canonicalObjectSet(objects)
	if err != nil {
		return nil, err
	}
	payload := ManifestPayload{
		Domain:      protocol.DomainPrefix + "SYNC-MANIFEST",
		NamespaceID: namespaceID, DeviceID: deviceID,
		BaseCheckpoint: baseCheckpoint, TargetCheckpoint: targetCheckpoint,
		HighestDeviceCounter: highestDeviceCounter,
		ObjectSetRoot:        root, ObjectCount: uint64(len(canonicalObjects)),
		CreatedSequence: createdSequence,
	}
	if validateManifestPayload(payload) != nil {
		return nil, ErrInvalidSyncManifest
	}
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, err := protocol.KeyIDFromPublicKey(publicKey)
	if err != nil {
		return nil, ErrInvalidSyncManifest
	}
	inner, err := protocol.MarshalDeterministic(manifestSigningPayload{
		Manifest: payload, Objects: canonicalObjects,
	})
	if err != nil {
		return nil, ErrInvalidSyncManifest
	}
	input := protocol.NewSigInput(
		protocol.ObjectTypeSyncManifest, chainID, namespaceID,
		keyID, keyGeneration, inner,
	)
	signature, err := protocol.Sign(privateKey, input)
	if err != nil {
		return nil, err
	}
	encoded, err := protocol.EncodeSigInput(input)
	if err != nil {
		return nil, err
	}
	return buildSignedManifest(payload, canonicalObjects, encoded, signature), nil
}

func ParseAndVerifyManifest(
	encodedSigInput []byte,
	signature protocol.Signature,
	publicKey ed25519.PublicKey,
	expected protocol.VerificationContext,
) (*SignedManifest, error) {
	var input protocol.SigInput
	if err := protocol.UnmarshalDeterministic(encodedSigInput, &input); err != nil {
		return nil, ErrInvalidSyncManifest
	}
	if err := protocol.Verify(publicKey, input, signature, expected); err != nil {
		return nil, errors.Join(ErrSyncManifestVerification, err)
	}
	if input.ObjectType != protocol.ObjectTypeSyncManifest {
		return nil, ErrSyncManifestContext
	}
	var inner manifestSigningPayload
	if err := protocol.UnmarshalDeterministic(input.Payload, &inner); err != nil ||
		validateManifestPayload(inner.Manifest) != nil ||
		inner.Manifest.NamespaceID != input.NamespaceID {
		return nil, ErrInvalidSyncManifest
	}
	objects, root, err := canonicalObjectSet(inner.Objects)
	if err != nil || !objectSetsEqual(objects, inner.Objects) ||
		root != inner.Manifest.ObjectSetRoot ||
		uint64(len(objects)) != inner.Manifest.ObjectCount {
		return nil, ErrInvalidSyncManifest
	}
	canonical, err := protocol.EncodeSigInput(input)
	if err != nil || subtle.ConstantTimeCompare(canonical, encodedSigInput) != 1 {
		return nil, ErrInvalidSyncManifest
	}
	return buildSignedManifest(inner.Manifest, objects, canonical, signature), nil
}

func canonicalObjectSet(
	input []ObjectReference,
) ([]ObjectReference, [sha256.Size]byte, error) {
	if len(input) == 0 || len(input) > MaxManifestObjects {
		return nil, [sha256.Size]byte{}, ErrInvalidSyncManifest
	}
	objects := cloneObjectReferences(input)
	sort.Slice(objects, func(i, j int) bool {
		return compareObjectReference(objects[i], objects[j]) < 0
	})
	leaves := make([][sha256.Size]byte, len(objects))
	for index, object := range objects {
		if validateObjectReference(object) != nil ||
			(index > 0 && compareObjectReference(objects[index-1], object) == 0) {
			return nil, [sha256.Size]byte{}, ErrInvalidSyncManifest
		}
		encoded, err := protocol.MarshalDeterministic(object)
		if err != nil {
			return nil, [sha256.Size]byte{}, ErrInvalidSyncManifest
		}
		hasher := sha256.New()
		_, _ = hasher.Write([]byte{0x00})
		_, _ = hasher.Write([]byte(protocol.DomainPrefix + "SYNC-OBJECT-LEAF"))
		_, _ = hasher.Write(encoded)
		copy(leaves[index][:], hasher.Sum(nil))
	}
	for len(leaves) > 1 {
		next := make([][sha256.Size]byte, 0, (len(leaves)+1)/2)
		for index := 0; index < len(leaves); index += 2 {
			if index+1 == len(leaves) {
				next = append(next, leaves[index])
				continue
			}
			hasher := sha256.New()
			_, _ = hasher.Write([]byte{0x01})
			_, _ = hasher.Write([]byte(protocol.DomainPrefix + "SYNC-OBJECT-NODE"))
			_, _ = hasher.Write(leaves[index][:])
			_, _ = hasher.Write(leaves[index+1][:])
			var parent [sha256.Size]byte
			copy(parent[:], hasher.Sum(nil))
			next = append(next, parent)
		}
		leaves = next
	}
	return objects, leaves[0], nil
}

func validateManifestPayload(payload ManifestPayload) error {
	if payload.Domain != protocol.DomainPrefix+"SYNC-MANIFEST" ||
		allZero(payload.NamespaceID[:]) || allZero(payload.DeviceID[:]) ||
		allZero(payload.BaseCheckpoint[:]) ||
		allZero(payload.TargetCheckpoint[:]) ||
		payload.BaseCheckpoint == payload.TargetCheckpoint ||
		payload.HighestDeviceCounter == 0 ||
		allZero(payload.ObjectSetRoot[:]) || payload.ObjectCount == 0 ||
		payload.ObjectCount > MaxManifestObjects || payload.CreatedSequence == 0 {
		return ErrInvalidSyncManifest
	}
	return nil
}

func validateObjectReference(object ObjectReference) error {
	if allZero(object.ObjectDigest[:]) || !object.ObjectType.Valid() ||
		object.Size == 0 ||
		(object.CredentialID == nil) != (object.Version == nil) {
		return ErrInvalidSyncManifest
	}
	if object.CredentialID != nil &&
		(allZero(object.CredentialID[:]) || *object.Version == 0) {
		return ErrInvalidSyncManifest
	}
	return nil
}

func compareObjectReference(left, right ObjectReference) int {
	if comparison := bytes.Compare(left.ObjectDigest[:], right.ObjectDigest[:]); comparison != 0 {
		return comparison
	}
	if left.ObjectType < right.ObjectType {
		return -1
	}
	if left.ObjectType > right.ObjectType {
		return 1
	}
	leftCredential := optionalCredentialBytes(left.CredentialID)
	rightCredential := optionalCredentialBytes(right.CredentialID)
	if comparison := bytes.Compare(leftCredential, rightCredential); comparison != 0 {
		return comparison
	}
	leftVersion, rightVersion := uint64(0), uint64(0)
	if left.Version != nil {
		leftVersion = *left.Version
	}
	if right.Version != nil {
		rightVersion = *right.Version
	}
	if leftVersion < rightVersion {
		return -1
	}
	if leftVersion > rightVersion {
		return 1
	}
	if left.Size < right.Size {
		return -1
	}
	if left.Size > right.Size {
		return 1
	}
	return 0
}

func optionalCredentialBytes(value *protocol.CredentialID) []byte {
	if value == nil {
		return nil
	}
	return value[:]
}

func objectSetsEqual(left, right []ObjectReference) bool {
	if len(left) != len(right) {
		return false
	}
	for index := range left {
		if compareObjectReference(left[index], right[index]) != 0 {
			return false
		}
	}
	return true
}

func cloneObjectReferences(input []ObjectReference) []ObjectReference {
	result := make([]ObjectReference, len(input))
	for index, object := range input {
		result[index] = object
		if object.CredentialID != nil {
			value := *object.CredentialID
			result[index].CredentialID = &value
		}
		if object.Version != nil {
			value := *object.Version
			result[index].Version = &value
		}
	}
	return result
}

func buildSignedManifest(
	payload ManifestPayload,
	objects []ObjectReference,
	encoded []byte,
	signature protocol.Signature,
) *SignedManifest {
	hasher := sha256.New()
	_, _ = hasher.Write(encoded)
	_, _ = hasher.Write(signature[:])
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	return &SignedManifest{
		payload: payload, objects: cloneObjectReferences(objects),
		sigInput:  append([]byte(nil), encoded...),
		signature: signature, digest: digest,
	}
}

func (manifest *SignedManifest) Payload() ManifestPayload {
	if manifest == nil {
		return ManifestPayload{}
	}
	return manifest.payload
}

func (manifest *SignedManifest) Objects() []ObjectReference {
	if manifest == nil {
		return nil
	}
	return cloneObjectReferences(manifest.objects)
}

func (manifest *SignedManifest) SigInputCBOR() []byte {
	if manifest == nil {
		return nil
	}
	return append([]byte(nil), manifest.sigInput...)
}

func (manifest *SignedManifest) Signature() protocol.Signature {
	if manifest == nil {
		return protocol.Signature{}
	}
	return manifest.signature
}

func (manifest *SignedManifest) Digest() [sha256.Size]byte {
	if manifest == nil {
		return [sha256.Size]byte{}
	}
	return manifest.digest
}

func allZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}
