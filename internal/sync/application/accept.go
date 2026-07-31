// Package application verifies untrusted-cloud synchronization candidates
// before handing a complete batch to one atomic local committer.
package application

import (
	"bytes"
	"context"
	"crypto/sha256"
	"errors"
	"sort"

	credential "vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
	syncdomain "vdns.local/vdns/internal/sync/domain"
)

var (
	ErrInvalidSyncAcceptance = errors.New("invalid sync acceptance request")
	ErrUntrustedManifest     = errors.New("sync manifest is not trusted")
	ErrIncompleteCandidate   = errors.New("sync candidate object set is incomplete")
	ErrCandidateMismatch     = errors.New("sync candidate conflicts with trusted state")
)

// ManifestTrustVerifier supplies signature, device authorization, revocation
// and counter checks. G4 binds its implementation to the VDNS five-layer
// verifier; the cloud record itself never selects a key.
type ManifestTrustVerifier interface {
	VerifyManifest(context.Context, syncdomain.ManifestRecord) (*syncdomain.SignedManifest, error)
}

// DescriptorTrustVerifier verifies a complete descriptor object using
// receiver-owned key generation and authorization context.
type DescriptorTrustVerifier interface {
	VerifyStateDescriptorObject(
		context.Context,
		protocol.NamespaceID,
		[]byte,
	) (*credential.SignedStateDescriptor, error)
}

// TrustedCredentialState is resolved from a receiver-accepted checkpoint, not
// from cloud ordering or manifest claims.
type TrustedCredentialState struct {
	NamespaceID            protocol.NamespaceID
	CredentialID           protocol.CredentialID
	Version                uint64
	EnvelopeHash           [sha256.Size]byte
	DescriptorHash         [sha256.Size]byte
	PreviousDescriptorHash *[sha256.Size]byte
	CryptoPolicyHash       [sha256.Size]byte
	DescriptorBindingHash  [sha256.Size]byte
	Checkpoint             [sha256.Size]byte
}

type SnapshotTrustResolver interface {
	ResolveCredentialState(
		context.Context,
		protocol.NamespaceID,
		[sha256.Size]byte,
		protocol.CredentialID,
		uint64,
	) (TrustedCredentialState, error)
}

// CandidateBundle owns all bytes needed for one accepted credential version.
// Objects includes ciphertext and wrapped-key objects referenced by Envelope.
type CandidateBundle struct {
	ManifestDigest [sha256.Size]byte
	Checkpoint     [sha256.Size]byte
	Envelope       *credential.CredentialEnvelope
	Descriptor     *credential.SignedStateDescriptor
	Objects        map[[sha256.Size]byte][]byte
}

// CandidateCommitter must persist the entire slice and advance accepted
// pointers in one transaction. It is never called for a partial batch.
type CandidateCommitter interface {
	CommitCandidates(context.Context, []CandidateBundle) error
}

type AcceptanceService struct {
	cloud       syncdomain.CloudStore
	manifests   ManifestTrustVerifier
	descriptors DescriptorTrustVerifier
	trust       SnapshotTrustResolver
	committer   CandidateCommitter
}

func NewAcceptanceService(
	cloud syncdomain.CloudStore,
	manifests ManifestTrustVerifier,
	descriptors DescriptorTrustVerifier,
	trust SnapshotTrustResolver,
	committer CandidateCommitter,
) (*AcceptanceService, error) {
	if cloud == nil || manifests == nil || descriptors == nil ||
		trust == nil || committer == nil {
		return nil, ErrInvalidSyncAcceptance
	}
	return &AcceptanceService{
		cloud: cloud, manifests: manifests, descriptors: descriptors,
		trust: trust, committer: committer,
	}, nil
}

// AcceptManifest verifies every referenced object before making any local
// mutation. expectedCheckpoint is receiver state and must not be derived from
// the cloud response.
func (service *AcceptanceService) AcceptManifest(
	ctx context.Context,
	record syncdomain.ManifestRecord,
	expectedNamespace protocol.NamespaceID,
	expectedCheckpoint [sha256.Size]byte,
) error {
	if service == nil || ctx == nil || allZero(expectedNamespace[:]) ||
		allZero(expectedCheckpoint[:]) || record.NamespaceID != expectedNamespace {
		return ErrInvalidSyncAcceptance
	}
	manifest, err := service.manifests.VerifyManifest(ctx, record)
	if err != nil || manifest == nil || manifest.Digest() != record.ManifestDigest {
		return errors.Join(ErrUntrustedManifest, err)
	}
	payload := manifest.Payload()
	if payload.NamespaceID != expectedNamespace ||
		payload.TargetCheckpoint != expectedCheckpoint {
		return ErrUntrustedManifest
	}

	objects, err := service.fetchCompleteObjectSet(ctx, manifest.Objects())
	if err != nil {
		return err
	}
	defer clearObjectMap(objects)
	candidates, err := service.validateCandidates(
		ctx, manifest, expectedCheckpoint, objects,
	)
	if err != nil {
		return err
	}
	if err := service.committer.CommitCandidates(ctx, candidates); err != nil {
		clearBundles(candidates)
		return err
	}
	clearBundles(candidates)
	return nil
}

type candidateKey struct {
	credentialID protocol.CredentialID
	version      uint64
}

type candidateReferences struct {
	envelope   *syncdomain.ObjectReference
	descriptor *syncdomain.ObjectReference
	all        []syncdomain.ObjectReference
}

func (service *AcceptanceService) fetchCompleteObjectSet(
	ctx context.Context,
	references []syncdomain.ObjectReference,
) (map[[sha256.Size]byte][]byte, error) {
	objects := make(map[[sha256.Size]byte][]byte, len(references))
	for _, reference := range references {
		object, err := service.cloud.FetchObject(ctx, platform.ObjectRef{
			Digest: reference.ObjectDigest, Size: reference.Size,
		})
		if err != nil {
			clearObjectMap(objects)
			return nil, errors.Join(ErrIncompleteCandidate, err)
		}
		if uint64(len(object)) != reference.Size ||
			sha256.Sum256(object) != reference.ObjectDigest {
			clear(object)
			clearObjectMap(objects)
			return nil, ErrIncompleteCandidate
		}
		objects[reference.ObjectDigest] = object
	}
	return objects, nil
}

func (service *AcceptanceService) validateCandidates(
	ctx context.Context,
	manifest *syncdomain.SignedManifest,
	checkpoint [sha256.Size]byte,
	objects map[[sha256.Size]byte][]byte,
) ([]CandidateBundle, error) {
	groups := make(map[candidateKey]*candidateReferences)
	for _, reference := range manifest.Objects() {
		if reference.CredentialID == nil || reference.Version == nil {
			continue
		}
		key := candidateKey{
			credentialID: *reference.CredentialID,
			version:      *reference.Version,
		}
		group := groups[key]
		if group == nil {
			group = &candidateReferences{}
			groups[key] = group
		}
		group.all = append(group.all, reference)
		switch reference.ObjectType {
		case protocol.ObjectTypeCredentialEnvelope:
			if group.envelope != nil {
				return nil, ErrCandidateMismatch
			}
			copy := reference
			group.envelope = &copy
		case protocol.ObjectTypeStateDescriptor:
			if group.descriptor != nil {
				return nil, ErrCandidateMismatch
			}
			copy := reference
			group.descriptor = &copy
		}
	}
	if len(groups) == 0 {
		return nil, ErrIncompleteCandidate
	}
	bundles := make([]CandidateBundle, 0, len(groups))
	keys := make([]candidateKey, 0, len(groups))
	for key := range groups {
		keys = append(keys, key)
	}
	sort.Slice(keys, func(i, j int) bool {
		if comparison := bytes.Compare(
			keys[i].credentialID[:], keys[j].credentialID[:],
		); comparison != 0 {
			return comparison < 0
		}
		return keys[i].version < keys[j].version
	})
	for _, key := range keys {
		group := groups[key]
		if group.envelope == nil || group.descriptor == nil {
			clearBundles(bundles)
			return nil, ErrIncompleteCandidate
		}
		envelope, err := credential.ParseCredentialEnvelope(
			objects[group.envelope.ObjectDigest],
		)
		if err != nil || envelope.NamespaceID() != manifest.Payload().NamespaceID ||
			envelope.CredentialID() != key.credentialID ||
			envelope.Version() != key.version {
			clearBundles(bundles)
			return nil, errors.Join(ErrCandidateMismatch, err)
		}
		descriptor, err := service.descriptors.VerifyStateDescriptorObject(
			ctx, manifest.Payload().NamespaceID,
			objects[group.descriptor.ObjectDigest],
		)
		if err != nil || descriptor == nil {
			clearBundles(bundles)
			return nil, errors.Join(ErrCandidateMismatch, err)
		}
		state := descriptor.Payload()
		if state.NamespaceID != manifest.Payload().NamespaceID ||
			state.CredentialID != key.credentialID ||
			state.ActiveVersion != key.version {
			clearBundles(bundles)
			return nil, ErrCandidateMismatch
		}
		trusted, trustErr := service.trust.ResolveCredentialState(
			ctx, manifest.Payload().NamespaceID, checkpoint,
			key.credentialID, key.version,
		)
		if trustErr != nil || !matchesTrustedState(
			trusted, state, envelope, descriptor, checkpoint,
		) || !envelopeObjectsComplete(envelope, objects, group.all) {
			clearBundles(bundles)
			return nil, errors.Join(ErrCandidateMismatch, trustErr)
		}
		bundles = append(bundles, CandidateBundle{
			ManifestDigest: manifest.Digest(),
			Checkpoint:     checkpoint,
			Envelope:       envelope,
			Descriptor:     descriptor,
			Objects:        cloneCandidateObjects(group.all, objects),
		})
	}
	return bundles, nil
}

func matchesTrustedState(
	trusted TrustedCredentialState,
	state credential.StateDescriptorPayload,
	envelope *credential.CredentialEnvelope,
	descriptor *credential.SignedStateDescriptor,
	checkpoint [sha256.Size]byte,
) bool {
	return trusted.NamespaceID == state.NamespaceID &&
		trusted.CredentialID == state.CredentialID &&
		trusted.Version == state.ActiveVersion &&
		trusted.EnvelopeHash == state.ActiveEnvelopeHash &&
		trusted.EnvelopeHash == envelope.Digest() &&
		trusted.DescriptorHash == descriptor.Digest() &&
		hashPointersEqual(trusted.PreviousDescriptorHash, state.PreviousDescriptorHash) &&
		trusted.CryptoPolicyHash == envelope.PolicyHash() &&
		trusted.DescriptorBindingHash == envelope.DescriptorBindingHash() &&
		trusted.Checkpoint == checkpoint &&
		state.AuditCheckpoint == checkpoint &&
		state.LifecycleStatus == protocol.LifecycleActive
}

func envelopeObjectsComplete(
	envelope *credential.CredentialEnvelope,
	objects map[[sha256.Size]byte][]byte,
	references []syncdomain.ObjectReference,
) bool {
	type fieldHashPair struct {
		ciphertext [sha256.Size]byte
		wrappedKey [sha256.Size]byte
	}
	available := make(map[fieldHashPair]struct{}, len(references))
	for _, reference := range references {
		if reference.ObjectType != protocol.ObjectTypeSecretEnvelope {
			continue
		}
		encrypted, err := cryptokit.ParseEncryptedField(
			objects[reference.ObjectDigest],
		)
		if err != nil {
			return false
		}
		field, err := encrypted.Reference()
		if err != nil {
			return false
		}
		context, err := encrypted.Context()
		if err != nil || context.CredentialID != envelope.CredentialID() ||
			context.NamespaceID != envelope.NamespaceID() ||
			context.CredentialVersion != envelope.Version() ||
			context.CryptoPolicyHash != envelope.PolicyHash() ||
			context.OriginBinding != envelope.OriginBinding() {
			return false
		}
		available[fieldHashPair{
			ciphertext: field.ObjectHash,
			wrappedKey: field.EnvelopeHash,
		}] = struct{}{}
	}
	for _, field := range envelope.Fields() {
		if _, exists := available[fieldHashPair{
			ciphertext: field.CiphertextDigest,
			wrappedKey: field.WrappedKeyDigest,
		}]; !exists {
			return false
		}
	}
	return true
}

func cloneCandidateObjects(
	references []syncdomain.ObjectReference,
	objects map[[sha256.Size]byte][]byte,
) map[[sha256.Size]byte][]byte {
	result := make(map[[sha256.Size]byte][]byte, len(references))
	for _, reference := range references {
		result[reference.ObjectDigest] = append(
			[]byte(nil), objects[reference.ObjectDigest]...,
		)
	}
	return result
}

func hashPointersEqual(left, right *[sha256.Size]byte) bool {
	if left == nil || right == nil {
		return left == nil && right == nil
	}
	return *left == *right
}

func clearBundles(bundles []CandidateBundle) {
	for index := range bundles {
		clearObjectMap(bundles[index].Objects)
	}
}

func clearObjectMap(objects map[[sha256.Size]byte][]byte) {
	for digest, object := range objects {
		clear(object)
		delete(objects, digest)
	}
}

func allZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}
