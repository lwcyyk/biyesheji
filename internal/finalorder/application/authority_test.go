package application_test

import (
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/json"
	"errors"
	"path/filepath"
	"sync"
	"testing"

	"vpass.local/vpass/internal/adapters/outbound/sqlite"
	finalorderapp "vpass.local/vpass/internal/finalorder/application"
	finalorderdomain "vpass.local/vpass/internal/finalorder/domain"
	"vpass.local/vpass/internal/protocol"
)

func TestResearchAuthorityDetectsTwoAndThreeDeviceBranches(t *testing.T) {
	t.Parallel()
	authority, _ := newMemoryAuthority(t)
	base := digest(10)
	first := candidate(1, base, digest(21), 1)
	second := candidate(2, base, digest(22), 2)
	third := candidate(3, base, digest(23), 3)

	firstRecord, err := authority.SubmitCandidate(context.Background(), first)
	if err != nil {
		t.Fatal(err)
	}
	firstReceipt, err := authority.AssignFinalSequence(
		context.Background(), firstRecord.CandidateDigest,
	)
	if err != nil || firstReceipt.Payload.FinalSequence != 1 {
		t.Fatalf("first receipt=%+v err=%v", firstReceipt, err)
	}
	for _, branch := range []finalorderdomain.Candidate{second, third} {
		record, err := authority.SubmitCandidate(context.Background(), branch)
		if err != nil || record.Disposition != finalorderdomain.DispositionConflict {
			t.Fatalf("branch record=%+v err=%v", record, err)
		}
		if _, err := authority.AssignFinalSequence(
			context.Background(), record.CandidateDigest,
		); err != nil {
			t.Fatal(err)
		}
	}
	state, err := authority.GetFinalizedState(
		context.Background(), first.NamespaceID, first.CredentialID,
	)
	if err != nil || state.Status != finalorderdomain.StateConflicted ||
		len(state.ConflictDigests) != 3 {
		t.Fatalf("state=%+v err=%v", state, err)
	}
	conflicts, err := authority.GetConflictSet(
		context.Background(), first.NamespaceID, first.CredentialID,
	)
	if err != nil || len(conflicts) != 3 {
		t.Fatalf("conflicts=%d err=%v", len(conflicts), err)
	}
	// A cloud that returns only the first branch cannot hide the authority's
	// independently resolved CONFLICTED state.
	if state.Status == finalorderdomain.StateActive {
		t.Fatal("hidden branch caused a silent active choice")
	}
}

func TestResearchAuthorityIsIdempotentAndArrivalOrderDoesNotSelect(t *testing.T) {
	t.Parallel()
	authority, _ := newMemoryAuthority(t)
	base := digest(30)
	left := candidate(1, base, digest(31), 1)
	right := candidate(2, base, digest(32), 2)
	leftRecord, err := authority.SubmitCandidate(context.Background(), left)
	if err != nil {
		t.Fatal(err)
	}
	duplicate, err := authority.SubmitCandidate(context.Background(), left)
	if err != nil || duplicate.CandidateDigest != leftRecord.CandidateDigest {
		t.Fatalf("duplicate=%+v err=%v", duplicate, err)
	}
	rightRecord, err := authority.SubmitCandidate(context.Background(), right)
	if err != nil {
		t.Fatal(err)
	}
	rightReceipt, err := authority.AssignFinalSequence(
		context.Background(), rightRecord.CandidateDigest,
	)
	if err != nil {
		t.Fatal(err)
	}
	leftReceipt, err := authority.AssignFinalSequence(
		context.Background(), leftRecord.CandidateDigest,
	)
	if err != nil {
		t.Fatal(err)
	}
	if rightReceipt.Payload.FinalSequence >= leftReceipt.Payload.FinalSequence {
		t.Fatalf("out-of-order assignment was not preserved: right=%d left=%d",
			rightReceipt.Payload.FinalSequence, leftReceipt.Payload.FinalSequence)
	}
	retry, err := authority.AssignFinalSequence(
		context.Background(), rightRecord.CandidateDigest,
	)
	if err != nil || retry.Digest != rightReceipt.Digest {
		t.Fatalf("receipt retry=%+v err=%v", retry, err)
	}
	if err := finalorderdomain.VerifyReceipt(rightReceipt, authority.PublicKey()); err != nil {
		t.Fatal(err)
	}
	encodedReceipt, err := rightReceipt.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	parsedReceipt, err := finalorderdomain.ParseReceipt(encodedReceipt)
	if err != nil || parsedReceipt.Digest != rightReceipt.Digest {
		t.Fatalf("receipt wire round trip = %+v, %v", parsedReceipt, err)
	}
	mutatedWire := append([]byte(nil), encodedReceipt...)
	mutatedWire[len(mutatedWire)-1] ^= 1
	parsedMutated, err := finalorderdomain.ParseReceipt(mutatedWire)
	if err != nil {
		t.Fatal(err)
	}
	if err := finalorderdomain.VerifyReceipt(
		parsedMutated, authority.PublicKey(),
	); !errors.Is(err, finalorderdomain.ErrReceiptSignature) {
		t.Fatalf("mutated receipt verification error = %v", err)
	}
	tampered := rightReceipt
	tampered.Payload.FinalSequence++
	if err := finalorderdomain.VerifyReceipt(tampered, authority.PublicKey()); !errors.Is(
		err, finalorderdomain.ErrReceiptSignature,
	) {
		t.Fatalf("tampered receipt error=%v", err)
	}
}

func TestResearchAuthorityRequiresExplicitResolutionAndCreatesNewVersion(t *testing.T) {
	t.Parallel()
	authority, _ := newMemoryAuthority(t)
	base := digest(40)
	left := candidate(1, base, digest(41), 1)
	right := candidate(2, base, digest(42), 2)
	leftRecord, _ := authority.SubmitCandidate(context.Background(), left)
	rightRecord, _ := authority.SubmitCandidate(context.Background(), right)
	_, _ = authority.AssignFinalSequence(context.Background(), leftRecord.CandidateDigest)
	_, _ = authority.AssignFinalSequence(context.Background(), rightRecord.CandidateDigest)

	request := finalorderdomain.ResolutionRequest{
		NamespaceID: left.NamespaceID, CredentialID: left.CredentialID,
		CandidateDigests: [][sha256.Size]byte{
			rightRecord.CandidateDigest, leftRecord.CandidateDigest,
		},
		SelectedCandidateDigest:  leftRecord.CandidateDigest,
		ResolutionDescriptorHash: digest(49), ResolvedBy: "user-device-A",
		Basis:              "user verified the new password against the target account",
		IdempotencyKeyHash: digest(50),
	}
	resolution, err := authority.ResolveConflict(context.Background(), request)
	if err != nil || resolution.NewVersion != 3 {
		t.Fatalf("resolution=%+v err=%v", resolution, err)
	}
	retry, err := authority.ResolveConflict(context.Background(), request)
	if err != nil || retry.ResolutionDigest != resolution.ResolutionDigest {
		t.Fatalf("resolution retry=%+v err=%v", retry, err)
	}
	state, err := authority.GetFinalizedState(
		context.Background(), left.NamespaceID, left.CredentialID,
	)
	if err != nil || state.Status != finalorderdomain.StateActive ||
		state.CurrentVersion != 3 ||
		state.DescriptorHash != request.ResolutionDescriptorHash {
		t.Fatalf("resolved state=%+v err=%v", state, err)
	}
	if _, err := authority.GetConflictSet(
		context.Background(), left.NamespaceID, left.CredentialID,
	); !errors.Is(err, finalorderdomain.ErrConflictRequired) {
		t.Fatalf("resolved conflict set error=%v", err)
	}
	// A previously offline losing device can retry its exact candidate without
	// deleting history or re-opening the selected pointer.
	offlineRetry, err := authority.SubmitCandidate(context.Background(), right)
	if err != nil || offlineRetry.Disposition != finalorderdomain.DispositionRejected {
		t.Fatalf("offline retry=%+v err=%v", offlineRetry, err)
	}
}

func TestResearchAuthorityRejectsWrongPredecessorAndIdempotencyReuse(t *testing.T) {
	t.Parallel()
	authority, _ := newMemoryAuthority(t)
	base := digest(60)
	first := candidate(1, base, digest(61), 1)
	firstRecord, _ := authority.SubmitCandidate(context.Background(), first)
	_, _ = authority.AssignFinalSequence(context.Background(), firstRecord.CandidateDigest)

	wrong := candidate(2, digest(99), digest(62), 2)
	wrong.BaseVersion = 2
	wrong.CandidateVersion = 3
	if _, err := authority.SubmitCandidate(
		context.Background(), wrong,
	); !errors.Is(err, finalorderdomain.ErrPredecessor) {
		t.Fatalf("wrong predecessor error=%v", err)
	}
	reused := candidate(2, base, digest(63), 3)
	reused.IdempotencyKeyHash = first.IdempotencyKeyHash
	if _, err := authority.SubmitCandidate(
		context.Background(), reused,
	); !errors.Is(err, finalorderdomain.ErrIdempotency) {
		t.Fatalf("idempotency reuse error=%v", err)
	}
}

func TestResearchAuthorityCrashBeforeCASAndSQLiteRestartRecovery(t *testing.T) {
	t.Parallel()
	store := &memoryStore{failNext: true}
	_, privateKey, _ := ed25519.GenerateKey(nil)
	authority, err := finalorderapp.NewResearchSingleNodeFinalOrderAuthority(store, privateKey, 1)
	if err != nil {
		t.Fatal(err)
	}
	item := candidate(1, digest(70), digest(71), 1)
	if _, err := authority.SubmitCandidate(context.Background(), item); err == nil {
		t.Fatal("injected persistence failure was accepted")
	}
	store.failNext = false
	record, err := authority.SubmitCandidate(context.Background(), item)
	if err != nil {
		t.Fatal(err)
	}
	if record.FinalSequence != 0 {
		t.Fatal("failed pre-CAS attempt leaked a final sequence")
	}

	path := filepath.Join(t.TempDir(), "authority.db")
	database, err := sqlite.Open(context.Background(), path)
	if err != nil {
		t.Fatal(err)
	}
	sqlStore, _ := sqlite.NewFinalOrderSnapshotStore(database)
	persistent, _ := finalorderapp.NewResearchSingleNodeFinalOrderAuthority(sqlStore, privateKey, 1)
	persisted, err := persistent.SubmitCandidate(context.Background(), item)
	if err != nil {
		t.Fatal(err)
	}
	receipt, err := persistent.AssignFinalSequence(context.Background(), persisted.CandidateDigest)
	if err != nil {
		t.Fatal(err)
	}
	if err := database.Close(); err != nil {
		t.Fatal(err)
	}

	database, err = sqlite.Open(context.Background(), path)
	if err != nil {
		t.Fatal(err)
	}
	defer database.Close()
	sqlStore, _ = sqlite.NewFinalOrderSnapshotStore(database)
	restarted, _ := finalorderapp.NewResearchSingleNodeFinalOrderAuthority(sqlStore, privateKey, 1)
	retried, err := restarted.AssignFinalSequence(
		context.Background(), persisted.CandidateDigest,
	)
	if err != nil || retried.Digest != receipt.Digest {
		t.Fatalf("restart receipt=%+v err=%v", retried, err)
	}
	checkpoint, err := restarted.GetTrustedCheckpoint(
		context.Background(), item.NamespaceID,
	)
	if err != nil || checkpoint.AdapterKind != finalorderdomain.AdapterKind ||
		checkpoint.FinalSequence != receipt.Payload.FinalSequence {
		t.Fatalf("checkpoint=%+v err=%v", checkpoint, err)
	}
	if err := finalorderdomain.VerifyCheckpoint(
		checkpoint, restarted.PublicKey(),
	); err != nil {
		t.Fatalf("verify checkpoint: %v", err)
	}
	tamperedCheckpoint := checkpoint
	tamperedCheckpoint.StateRoot[0] ^= 1
	if err := finalorderdomain.VerifyCheckpoint(
		tamperedCheckpoint, restarted.PublicKey(),
	); !errors.Is(err, finalorderdomain.ErrCheckpointSignature) {
		t.Fatalf("tampered checkpoint error = %v", err)
	}
}

func newMemoryAuthority(
	t *testing.T,
) (*finalorderapp.ResearchSingleNodeFinalOrderAuthority, *memoryStore) {
	t.Helper()
	_, privateKey, err := ed25519.GenerateKey(nil)
	if err != nil {
		t.Fatal(err)
	}
	store := &memoryStore{}
	authority, err := finalorderapp.NewResearchSingleNodeFinalOrderAuthority(
		store, privateKey, 1,
	)
	if err != nil {
		t.Fatal(err)
	}
	return authority, store
}

func candidate(
	deviceByte byte,
	baseDescriptor [sha256.Size]byte,
	descriptor [sha256.Size]byte,
	idempotencyByte byte,
) finalorderdomain.Candidate {
	var namespaceID protocol.NamespaceID
	var credentialID protocol.CredentialID
	var deviceID protocol.DeviceID
	for index := range namespaceID {
		namespaceID[index] = 1
	}
	for index := range credentialID {
		credentialID[index] = 2
	}
	for index := range deviceID {
		deviceID[index] = deviceByte
	}
	return finalorderdomain.Candidate{
		NamespaceID: namespaceID, CredentialID: credentialID,
		BaseVersion: 1, CandidateVersion: 2,
		BaseDescriptorHash: baseDescriptor, DescriptorHash: descriptor,
		EnvelopeHash: digest(deviceByte + 100), DeviceID: deviceID,
		SubmittedBy:        "device-subject",
		IdempotencyKeyHash: digest(idempotencyByte + 120),
	}
}

func digest(value byte) [sha256.Size]byte {
	var result [sha256.Size]byte
	for index := range result {
		result[index] = value
	}
	return result
}

type memoryStore struct {
	mu       sync.Mutex
	state    finalorderdomain.PersistentState
	failNext bool
}

func (store *memoryStore) Load(
	_ context.Context,
) (finalorderdomain.PersistentState, error) {
	store.mu.Lock()
	defer store.mu.Unlock()
	return cloneState(store.state)
}

func (store *memoryStore) CompareAndSwap(
	_ context.Context,
	expected uint64,
	state finalorderdomain.PersistentState,
) error {
	store.mu.Lock()
	defer store.mu.Unlock()
	if store.failNext {
		store.failNext = false
		return errors.New("injected crash before durable commit")
	}
	if store.state.Revision != expected {
		return finalorderdomain.ErrPersistenceConflict
	}
	cloned, err := cloneState(state)
	if err != nil {
		return err
	}
	store.state = cloned
	return nil
}

func cloneState(
	state finalorderdomain.PersistentState,
) (finalorderdomain.PersistentState, error) {
	encoded, err := json.Marshal(state)
	if err != nil {
		return finalorderdomain.PersistentState{}, err
	}
	var result finalorderdomain.PersistentState
	if err := json.Unmarshal(encoded, &result); err != nil {
		return finalorderdomain.PersistentState{}, err
	}
	return result, nil
}
