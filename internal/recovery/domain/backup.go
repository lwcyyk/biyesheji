// Package domain defines backup and restore consistency gates. Encryption of
// the manifest is mandatory at the adapter boundary; this package handles only
// fixed-width digests and receiver-verified checkpoints.
package domain

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"sort"

	"vpass.local/vpass/internal/platform"
	"vpass.local/vpass/internal/protocol"
)

var (
	ErrInvalidBackup      = errors.New("invalid backup snapshot")
	ErrRecoveryTransition = errors.New("invalid recovery transition")
	ErrRecoveryObjects    = errors.New("recovery object set is incomplete")
	ErrRecoveryState      = errors.New("recovery state checkpoint is not trusted")
)

const MaxBackupObjects = 100_000

type BackupSnapshot struct {
	NamespaceID           protocol.NamespaceID
	SecretGeneration      uint64
	RecoveryCapsuleDigest [sha256.Size]byte
	EncryptedManifestHash [sha256.Size]byte
	RouteMapRoot          [sha256.Size]byte
	CredentialStateRoot   [sha256.Size]byte
	ObjectSetRoot         [sha256.Size]byte
	AcceptedCheckpoint    [sha256.Size]byte
	CreatedSequence       uint64
	objects               []platform.ObjectRef
}

type backupObjectLeaf struct {
	Digest [sha256.Size]byte `cbor:"digest"`
	Size   uint64            `cbor:"size"`
}

func NewBackupSnapshot(
	namespaceID protocol.NamespaceID,
	secretGeneration uint64,
	recoveryCapsuleDigest [sha256.Size]byte,
	encryptedManifestHash [sha256.Size]byte,
	routeMapRoot [sha256.Size]byte,
	credentialStateRoot [sha256.Size]byte,
	acceptedCheckpoint [sha256.Size]byte,
	createdSequence uint64,
	objects []platform.ObjectRef,
) (BackupSnapshot, error) {
	canonical, root, err := canonicalBackupObjects(objects)
	if err != nil || allZero(namespaceID[:]) || secretGeneration == 0 ||
		allZero(recoveryCapsuleDigest[:]) ||
		allZero(encryptedManifestHash[:]) || allZero(routeMapRoot[:]) ||
		allZero(credentialStateRoot[:]) ||
		allZero(acceptedCheckpoint[:]) || createdSequence == 0 {
		return BackupSnapshot{}, ErrInvalidBackup
	}
	return BackupSnapshot{
		NamespaceID: namespaceID, SecretGeneration: secretGeneration,
		RecoveryCapsuleDigest: recoveryCapsuleDigest,
		EncryptedManifestHash: encryptedManifestHash,
		RouteMapRoot:          routeMapRoot, CredentialStateRoot: credentialStateRoot,
		ObjectSetRoot: root, AcceptedCheckpoint: acceptedCheckpoint,
		CreatedSequence: createdSequence, objects: canonical,
	}, nil
}

func (snapshot BackupSnapshot) Objects() []platform.ObjectRef {
	return append([]platform.ObjectRef(nil), snapshot.objects...)
}

type RecoveryStatus uint8

const (
	RecoveryPrepared RecoveryStatus = iota + 1
	RecoveryRootRecovered
	RecoveryObjectsVerified
	RecoveryStateVerified
	RecoveryCompleted
	RecoveryFailed
)

type RecoverySession struct {
	snapshot           BackupSnapshot
	status             RecoveryStatus
	verifiedCheckpoint *[sha256.Size]byte
}

func NewRecoverySession(snapshot BackupSnapshot) (*RecoverySession, error) {
	if _, root, err := canonicalBackupObjects(snapshot.objects); err != nil ||
		root != snapshot.ObjectSetRoot ||
		allZero(snapshot.NamespaceID[:]) {
		return nil, ErrInvalidBackup
	}
	return &RecoverySession{
		snapshot: snapshot, status: RecoveryPrepared,
	}, nil
}

func (session *RecoverySession) Status() RecoveryStatus {
	if session == nil {
		return 0
	}
	return session.status
}

func (session *RecoverySession) MarkRootRecovered(
	openedCapsuleDigest [sha256.Size]byte,
	secretGeneration uint64,
) error {
	if session == nil || session.status != RecoveryPrepared ||
		openedCapsuleDigest != session.snapshot.RecoveryCapsuleDigest ||
		secretGeneration != session.snapshot.SecretGeneration {
		return ErrRecoveryTransition
	}
	session.status = RecoveryRootRecovered
	return nil
}

func (session *RecoverySession) VerifyObjects(
	available []platform.ObjectRef,
) error {
	if session == nil || session.status != RecoveryRootRecovered {
		return ErrRecoveryTransition
	}
	canonical, root, err := canonicalBackupObjects(available)
	if err != nil || root != session.snapshot.ObjectSetRoot ||
		!objectRefsEqual(canonical, session.snapshot.objects) {
		return ErrRecoveryObjects
	}
	session.status = RecoveryObjectsVerified
	return nil
}

// VerifyTrustedState is called only after the Local State Verifier accepts a proof
// bundle. The checkpoint must equal the backup's accepted checkpoint; backup
// metadata itself cannot authorize an older or different state.
func (session *RecoverySession) VerifyTrustedState(
	receiverTrustedCheckpoint [sha256.Size]byte,
	proofAccepted bool,
) error {
	if session == nil || session.status != RecoveryObjectsVerified {
		return ErrRecoveryTransition
	}
	if !proofAccepted ||
		receiverTrustedCheckpoint != session.snapshot.AcceptedCheckpoint {
		return ErrRecoveryState
	}
	value := receiverTrustedCheckpoint
	session.verifiedCheckpoint = &value
	session.status = RecoveryStateVerified
	return nil
}

func (session *RecoverySession) Complete(
	restoredRouteMapRoot [sha256.Size]byte,
	restoredCredentialStateRoot [sha256.Size]byte,
) error {
	if session == nil || session.status != RecoveryStateVerified ||
		session.verifiedCheckpoint == nil ||
		restoredRouteMapRoot != session.snapshot.RouteMapRoot ||
		restoredCredentialStateRoot != session.snapshot.CredentialStateRoot {
		return ErrRecoveryTransition
	}
	session.status = RecoveryCompleted
	return nil
}

func canonicalBackupObjects(
	input []platform.ObjectRef,
) ([]platform.ObjectRef, [sha256.Size]byte, error) {
	if len(input) == 0 || len(input) > MaxBackupObjects {
		return nil, [sha256.Size]byte{}, ErrInvalidBackup
	}
	objects := append([]platform.ObjectRef(nil), input...)
	sort.Slice(objects, func(i, j int) bool {
		if comparison := bytes.Compare(
			objects[i].Digest[:], objects[j].Digest[:],
		); comparison != 0 {
			return comparison < 0
		}
		return objects[i].Size < objects[j].Size
	})
	leaves := make([][sha256.Size]byte, len(objects))
	for index, object := range objects {
		if allZero(object.Digest[:]) || object.Size == 0 ||
			(index > 0 && objects[index-1] == object) {
			return nil, [sha256.Size]byte{}, ErrInvalidBackup
		}
		encoded, err := protocol.MarshalDeterministic(backupObjectLeaf{
			Digest: object.Digest, Size: object.Size,
		})
		if err != nil {
			return nil, [sha256.Size]byte{}, ErrInvalidBackup
		}
		hasher := sha256.New()
		_, _ = hasher.Write([]byte{0x00})
		_, _ = hasher.Write([]byte(protocol.DomainPrefix + "BACKUP-OBJECT"))
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
			_, _ = hasher.Write([]byte(protocol.DomainPrefix + "BACKUP-NODE"))
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

func objectRefsEqual(left, right []platform.ObjectRef) bool {
	if len(left) != len(right) {
		return false
	}
	for index := range left {
		if left[index] != right[index] {
			return false
		}
	}
	return true
}

func allZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}
