package domain

import (
	"crypto/sha256"
	"errors"
	"testing"

	"vpass.local/vpass/internal/protocol"
)

func TestAggregateLifecycleHappyPathsAndOldVersionRetention(t *testing.T) {
	t.Parallel()
	v1 := sha256.Sum256([]byte("descriptor-v1"))
	v2 := sha256.Sum256([]byte("descriptor-v2"))
	aggregate := NewCredentialAggregate()
	if err := aggregate.BeginCreate(v1); err != nil {
		t.Fatal(err)
	}
	if err := aggregate.ActivateCreated(protocol.EvidenceSubmitObserved); !errors.Is(err, ErrAggregateEvidence) {
		t.Fatalf("weak create evidence = %v", err)
	}
	if err := aggregate.ActivateCreated(protocol.EvidenceSiteSignedReceipt); err != nil {
		t.Fatal(err)
	}
	if err := aggregate.BeginUpdate(1, v1, v2); err != nil {
		t.Fatal(err)
	}
	pending := aggregate.Snapshot()
	if pending.Phase != PhaseUpdatePending || pending.ActiveVersion != 1 ||
		pending.ActiveDescriptorHash != v1 || pending.CandidateVersion != 2 {
		t.Fatalf("update pending snapshot = %+v", pending)
	}
	if err := aggregate.MarkSiteConfirmPending(); err != nil {
		t.Fatal(err)
	}
	if err := aggregate.ConfirmUpdate(protocol.EvidenceNewPasswordReloginConfirmed); !errors.Is(err, ErrAggregateEvidence) {
		t.Fatalf("weak update evidence = %v", err)
	}
	stillPending := aggregate.Snapshot()
	if stillPending.ActiveVersion != 1 || stillPending.ActiveDescriptorHash != v1 {
		t.Fatal("weak evidence replaced the old active version")
	}
	if err := aggregate.ConfirmUpdate(protocol.EvidenceUserSignedConfirmation); err != nil {
		t.Fatal(err)
	}
	active := aggregate.Snapshot()
	if active.Phase != PhaseActive || active.ActiveVersion != 2 ||
		active.ActiveDescriptorHash != v2 || active.CandidateVersion != 0 {
		t.Fatalf("confirmed snapshot = %+v", active)
	}
	if err := aggregate.Suspend(); err != nil {
		t.Fatal(err)
	}
	if err := aggregate.Revoke(); err != nil {
		t.Fatal(err)
	}
	if aggregate.Snapshot().Phase != PhaseRevoked {
		t.Fatal("revocation did not reach terminal state")
	}
}

func TestAggregateConflictRetainsBothAndRequiresExplicitResolution(t *testing.T) {
	t.Parallel()
	v1 := sha256.Sum256([]byte("descriptor-v1"))
	competing := sha256.Sum256([]byte("competing-v1"))
	aggregate, err := RestoreCredentialAggregate(AggregateSnapshot{
		Phase: PhaseActive, ActiveVersion: 1, ActiveDescriptorHash: v1,
	})
	if err != nil {
		t.Fatal(err)
	}
	if err := aggregate.MarkConflict(1, competing); err != nil {
		t.Fatal(err)
	}
	snapshot := aggregate.Snapshot()
	if snapshot.Phase != PhaseConflicted || len(snapshot.ConflictCandidates) != 2 ||
		!candidateMember(snapshot.ConflictCandidates, DescriptorCandidate{
			Version: 1, DescriptorHash: v1,
		}) ||
		!candidateMember(snapshot.ConflictCandidates, DescriptorCandidate{
			Version: 1, DescriptorHash: competing,
		}) {
		t.Fatalf("conflict snapshot = %+v", snapshot)
	}
	snapshot.ConflictCandidates[0] = DescriptorCandidate{}
	if aggregate.Snapshot().ConflictCandidates[0] == (DescriptorCandidate{}) {
		t.Fatal("snapshot exposed mutable conflict storage")
	}
	unknown := sha256.Sum256([]byte("unknown"))
	if err := aggregate.ResolveConflict(
		1, unknown, protocol.EvidenceUserSignedConfirmation,
	); !errors.Is(err, ErrInvalidAggregateTransition) {
		t.Fatalf("unknown resolution error = %v", err)
	}
	if err := aggregate.ResolveConflict(
		1, competing, protocol.EvidenceSubmitObserved,
	); !errors.Is(err, ErrAggregateEvidence) {
		t.Fatalf("weak resolution error = %v", err)
	}
	if err := aggregate.ResolveConflict(
		1, competing, protocol.EvidenceUserSignedConfirmation,
	); err != nil {
		t.Fatal(err)
	}
	if aggregate.Snapshot().ActiveDescriptorHash != competing {
		t.Fatal("explicit conflict resolution selected wrong descriptor")
	}
}

func TestAggregateTransitionMatrixAndRestoreRejectInvalid(t *testing.T) {
	t.Parallel()
	allowed := map[[2]AggregatePhase]bool{
		{PhaseNonexistent, PhaseCreatePending}:        true,
		{PhaseCreatePending, PhaseActive}:             true,
		{PhaseCreatePending, PhaseNonexistent}:        true,
		{PhaseActive, PhaseUpdatePending}:             true,
		{PhaseActive, PhaseSuspended}:                 true,
		{PhaseActive, PhaseConflicted}:                true,
		{PhaseUpdatePending, PhaseSiteConfirmPending}: true,
		{PhaseUpdatePending, PhaseConflicted}:         true,
		{PhaseSiteConfirmPending, PhaseActive}:        true,
		{PhaseSiteConfirmPending, PhaseConflicted}:    true,
		{PhaseSuspended, PhaseRevoked}:                true,
		{PhaseConflicted, PhaseActive}:                true,
	}
	for current := PhaseNonexistent; current <= PhaseConflicted; current++ {
		for next := PhaseNonexistent; next <= PhaseConflicted; next++ {
			if got := current.CanTransitionTo(next); got != allowed[[2]AggregatePhase{current, next}] {
				t.Fatalf("transition %d -> %d = %v", current, next, got)
			}
		}
	}
	if _, err := RestoreCredentialAggregate(AggregateSnapshot{
		Phase: PhaseActive, ActiveVersion: 1,
	}); !errors.Is(err, ErrInvalidAggregateState) {
		t.Fatalf("invalid restore error = %v", err)
	}
}
