package domain

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"testing"

	"vpass.local/vpass/internal/platform"
	"vpass.local/vpass/internal/protocol"
)

func TestRecoveryRequiresCapsuleObjectsTrustedStateAndRootConsistency(t *testing.T) {
	t.Parallel()
	snapshot, objects := backupFixture(t)
	session, err := NewRecoverySession(snapshot)
	if err != nil {
		t.Fatal(err)
	}
	if err := session.MarkRootRecovered(
		snapshot.RecoveryCapsuleDigest, snapshot.SecretGeneration,
	); err != nil {
		t.Fatal(err)
	}
	reordered := []platform.ObjectRef{objects[2], objects[0], objects[1]}
	if err := session.VerifyObjects(reordered); err != nil {
		t.Fatal(err)
	}
	if err := session.VerifyTrustedState(snapshot.AcceptedCheckpoint, true); err != nil {
		t.Fatal(err)
	}
	if err := session.Complete(
		snapshot.RouteMapRoot, snapshot.CredentialStateRoot,
	); err != nil {
		t.Fatal(err)
	}
	if session.Status() != RecoveryCompleted {
		t.Fatalf("status=%d", session.Status())
	}
}

func TestRecoveryRejectsMissingObjectsRollbackAndBypass(t *testing.T) {
	t.Parallel()
	t.Run("missing-object", func(t *testing.T) {
		t.Parallel()
		snapshot, objects := backupFixture(t)
		session, _ := NewRecoverySession(snapshot)
		_ = session.MarkRootRecovered(
			snapshot.RecoveryCapsuleDigest, snapshot.SecretGeneration,
		)
		if err := session.VerifyObjects(objects[:2]); !errors.Is(err, ErrRecoveryObjects) {
			t.Fatalf("missing object error=%v", err)
		}
		if session.Status() != RecoveryRootRecovered {
			t.Fatal("missing objects advanced recovery")
		}
	})
	t.Run("checkpoint-rollback", func(t *testing.T) {
		t.Parallel()
		snapshot, objects := backupFixture(t)
		session, _ := NewRecoverySession(snapshot)
		_ = session.MarkRootRecovered(
			snapshot.RecoveryCapsuleDigest, snapshot.SecretGeneration,
		)
		_ = session.VerifyObjects(objects)
		old := sha256.Sum256([]byte("old-checkpoint"))
		if err := session.VerifyTrustedState(old, true); !errors.Is(err, ErrRecoveryState) {
			t.Fatalf("rollback error=%v", err)
		}
		if err := session.Complete(
			snapshot.RouteMapRoot, snapshot.CredentialStateRoot,
		); !errors.Is(err, ErrRecoveryTransition) {
			t.Fatalf("trusted state bypass error=%v", err)
		}
	})
}

func backupFixture(t *testing.T) (BackupSnapshot, []platform.ObjectRef) {
	t.Helper()
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x11}, len(namespaceID)))
	objects := []platform.ObjectRef{
		{Digest: sha256.Sum256([]byte("capsule")), Size: 123},
		{Digest: sha256.Sum256([]byte("route-map")), Size: 456},
		{Digest: sha256.Sum256([]byte("credential-object")), Size: 789},
	}
	snapshot, err := NewBackupSnapshot(
		namespaceID, 3,
		sha256.Sum256([]byte("recovery-capsule")),
		sha256.Sum256([]byte("encrypted-manifest")),
		sha256.Sum256([]byte("route-root")),
		sha256.Sum256([]byte("credential-root")),
		sha256.Sum256([]byte("accepted-checkpoint")),
		99, objects,
	)
	if err != nil {
		t.Fatal(err)
	}
	return snapshot, objects
}
