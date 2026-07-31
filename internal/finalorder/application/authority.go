// Package application implements the single-node research final-order
// authority. It provides deterministic ordering and conflict preservation, not
// Byzantine fault tolerance or multi-node consensus.
package application

import (
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"sort"
	"sync"

	finalorderdomain "vdns.local/vdns/internal/finalorder/domain"
	"vdns.local/vdns/internal/finalorder/ports"
	"vdns.local/vdns/internal/protocol"
)

var ErrInvalidAuthority = errors.New("invalid research final-order authority")

// FinalOrderAuthority is the frozen Stage 2 ordering boundary.
type FinalOrderAuthority interface {
	SubmitCandidate(context.Context, finalorderdomain.Candidate) (finalorderdomain.CandidateRecord, error)
	AssignFinalSequence(context.Context, [sha256.Size]byte) (finalorderdomain.FinalOrderReceipt, error)
	GetFinalizedState(context.Context, protocol.NamespaceID, protocol.CredentialID) (finalorderdomain.FinalizedState, error)
	GetConflictSet(context.Context, protocol.NamespaceID, protocol.CredentialID) ([]finalorderdomain.CandidateRecord, error)
	ResolveConflict(context.Context, finalorderdomain.ResolutionRequest) (finalorderdomain.ResolutionRecord, error)
	GetTrustedCheckpoint(context.Context, protocol.NamespaceID) (finalorderdomain.TrustedCheckpoint, error)
}

type ResearchSingleNodeFinalOrderAuthority struct {
	mu            sync.Mutex
	store         ports.SnapshotStore
	privateKey    ed25519.PrivateKey
	publicKey     ed25519.PublicKey
	keyID         [sha256.Size]byte
	keyGeneration uint64
}

func NewResearchSingleNodeFinalOrderAuthority(
	store ports.SnapshotStore,
	privateKey ed25519.PrivateKey,
	keyGeneration uint64,
) (*ResearchSingleNodeFinalOrderAuthority, error) {
	if store == nil || len(privateKey) != ed25519.PrivateKeySize || keyGeneration == 0 {
		return nil, ErrInvalidAuthority
	}
	publicKey := append(ed25519.PublicKey(nil), privateKey.Public().(ed25519.PublicKey)...)
	return &ResearchSingleNodeFinalOrderAuthority{
		store: store, privateKey: append(ed25519.PrivateKey(nil), privateKey...),
		publicKey: publicKey, keyID: sha256.Sum256(publicKey),
		keyGeneration: keyGeneration,
	}, nil
}

func (authority *ResearchSingleNodeFinalOrderAuthority) AdapterKind() string {
	return finalorderdomain.AdapterKind
}

func (authority *ResearchSingleNodeFinalOrderAuthority) PublicKey() ed25519.PublicKey {
	if authority == nil {
		return nil
	}
	return append(ed25519.PublicKey(nil), authority.publicKey...)
}

func (authority *ResearchSingleNodeFinalOrderAuthority) SubmitCandidate(
	ctx context.Context,
	candidate finalorderdomain.Candidate,
) (finalorderdomain.CandidateRecord, error) {
	if authority == nil || ctx == nil || candidate.Validate() != nil {
		return finalorderdomain.CandidateRecord{}, finalorderdomain.ErrInvalidCandidate
	}
	digest, _ := candidate.Digest()
	authority.mu.Lock()
	defer authority.mu.Unlock()
	state, err := authority.store.Load(ctx)
	if err != nil {
		return finalorderdomain.CandidateRecord{}, err
	}
	initializeState(&state)
	idempotency := hex.EncodeToString(candidate.IdempotencyKeyHash[:])
	if previous, ok := state.Idempotency[idempotency]; ok {
		if previous != digest {
			return finalorderdomain.CandidateRecord{}, finalorderdomain.ErrIdempotency
		}
		if record, found := findCandidate(state.Candidates, digest); found {
			return record, nil
		}
		return finalorderdomain.CandidateRecord{}, finalorderdomain.ErrPersistenceConflict
	}
	if record, found := findCandidate(state.Candidates, digest); found {
		state.Idempotency[idempotency] = digest
		if err := saveState(ctx, authority.store, state); err != nil {
			return finalorderdomain.CandidateRecord{}, err
		}
		return record, nil
	}

	branches := candidateBranches(state.Candidates, candidate)
	current, hasCurrent := findState(state.States, candidate.NamespaceID, candidate.CredentialID)
	if len(branches) == 0 && hasCurrent {
		if current.Status == finalorderdomain.StateConflicted {
			return finalorderdomain.CandidateRecord{}, finalorderdomain.ErrConflictRequired
		}
		if current.CurrentVersion != candidate.BaseVersion ||
			current.DescriptorHash != candidate.BaseDescriptorHash {
			return finalorderdomain.CandidateRecord{}, finalorderdomain.ErrPredecessor
		}
	}

	record := finalorderdomain.CandidateRecord{
		Candidate: candidate, CandidateDigest: digest,
		Disposition: finalorderdomain.DispositionPending,
	}
	state.Candidates = append(state.Candidates, record)
	state.Idempotency[idempotency] = digest
	branches = append(branches, len(state.Candidates)-1)
	if len(branches) > 1 {
		conflictDigests := make([][sha256.Size]byte, 0, len(branches))
		for _, index := range branches {
			state.Candidates[index].Disposition = finalorderdomain.DispositionConflict
			conflictDigests = append(conflictDigests, state.Candidates[index].CandidateDigest)
		}
		setState(&state, finalorderdomain.FinalizedState{
			NamespaceID: candidate.NamespaceID, CredentialID: candidate.CredentialID,
			Status: finalorderdomain.StateConflicted, CurrentVersion: candidate.BaseVersion,
			DescriptorHash:  candidate.BaseDescriptorHash,
			ConflictDigests: finalorderdomain.SortedDigests(conflictDigests),
		})
		record = state.Candidates[len(state.Candidates)-1]
	} else if !hasCurrent {
		setState(&state, finalorderdomain.FinalizedState{
			NamespaceID: candidate.NamespaceID, CredentialID: candidate.CredentialID,
			Status: finalorderdomain.StateCandidate, CurrentVersion: candidate.BaseVersion,
			DescriptorHash:  candidate.BaseDescriptorHash,
			ConflictDigests: [][sha256.Size]byte{digest},
		})
	}
	if err := saveState(ctx, authority.store, state); err != nil {
		return finalorderdomain.CandidateRecord{}, err
	}
	return record, nil
}

func (authority *ResearchSingleNodeFinalOrderAuthority) AssignFinalSequence(
	ctx context.Context,
	candidateDigest [sha256.Size]byte,
) (finalorderdomain.FinalOrderReceipt, error) {
	if authority == nil || ctx == nil || bytesZero(candidateDigest[:]) {
		return finalorderdomain.FinalOrderReceipt{}, finalorderdomain.ErrInvalidCandidate
	}
	authority.mu.Lock()
	defer authority.mu.Unlock()
	state, err := authority.store.Load(ctx)
	if err != nil {
		return finalorderdomain.FinalOrderReceipt{}, err
	}
	initializeState(&state)
	index := candidateIndex(state.Candidates, candidateDigest)
	if index < 0 {
		return finalorderdomain.FinalOrderReceipt{}, finalorderdomain.ErrCandidateNotFound
	}
	if state.Candidates[index].FinalSequence != 0 {
		if receipt, found := findReceipt(state.Receipts, state.Candidates[index].ReceiptDigest); found {
			return receipt, nil
		}
		return finalorderdomain.FinalOrderReceipt{}, finalorderdomain.ErrPersistenceConflict
	}
	candidate := state.Candidates[index].Candidate
	receipt, checkpoint, err := authority.orderObject(
		state, candidate.NamespaceID, candidate.CredentialID, candidateDigest,
	)
	if err != nil {
		return finalorderdomain.FinalOrderReceipt{}, err
	}
	state.NextSequence = receipt.Payload.FinalSequence
	state.Candidates[index].FinalSequence = receipt.Payload.FinalSequence
	state.Candidates[index].ReceiptDigest = receipt.Digest
	if state.Candidates[index].Disposition == finalorderdomain.DispositionPending {
		state.Candidates[index].Disposition = finalorderdomain.DispositionOrdered
		current, _ := findState(state.States, candidate.NamespaceID, candidate.CredentialID)
		current.Status = finalorderdomain.StateActive
		current.CurrentVersion = candidate.CandidateVersion
		current.DescriptorHash = candidate.DescriptorHash
		current.FinalSequence = receipt.Payload.FinalSequence
		current.ConflictDigests = nil
		setState(&state, current)
	} else {
		current, _ := findState(state.States, candidate.NamespaceID, candidate.CredentialID)
		current.FinalSequence = receipt.Payload.FinalSequence
		setState(&state, current)
	}
	state.Receipts = append(state.Receipts, receipt)
	state.Checkpoints = appendOrReplaceCheckpoint(state.Checkpoints, checkpoint)
	if err := saveState(ctx, authority.store, state); err != nil {
		return finalorderdomain.FinalOrderReceipt{}, err
	}
	return receipt, nil
}

func (authority *ResearchSingleNodeFinalOrderAuthority) GetFinalizedState(
	ctx context.Context,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
) (finalorderdomain.FinalizedState, error) {
	if authority == nil || ctx == nil || bytesZero(namespaceID[:]) || bytesZero(credentialID[:]) {
		return finalorderdomain.FinalizedState{}, finalorderdomain.ErrCandidateNotFound
	}
	authority.mu.Lock()
	defer authority.mu.Unlock()
	state, err := authority.store.Load(ctx)
	if err != nil {
		return finalorderdomain.FinalizedState{}, err
	}
	result, ok := findState(state.States, namespaceID, credentialID)
	if !ok {
		return finalorderdomain.FinalizedState{}, finalorderdomain.ErrCandidateNotFound
	}
	return cloneFinalizedState(result), nil
}

func (authority *ResearchSingleNodeFinalOrderAuthority) GetConflictSet(
	ctx context.Context,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
) ([]finalorderdomain.CandidateRecord, error) {
	if authority == nil || ctx == nil {
		return nil, finalorderdomain.ErrCandidateNotFound
	}
	authority.mu.Lock()
	defer authority.mu.Unlock()
	state, err := authority.store.Load(ctx)
	if err != nil {
		return nil, err
	}
	current, ok := findState(state.States, namespaceID, credentialID)
	if !ok || current.Status != finalorderdomain.StateConflicted {
		return nil, finalorderdomain.ErrConflictRequired
	}
	wanted := make(map[[sha256.Size]byte]bool, len(current.ConflictDigests))
	for _, digest := range current.ConflictDigests {
		wanted[digest] = true
	}
	result := make([]finalorderdomain.CandidateRecord, 0, len(wanted))
	for _, record := range state.Candidates {
		if wanted[record.CandidateDigest] {
			result = append(result, record)
		}
	}
	sort.Slice(result, func(i, j int) bool {
		return string(result[i].CandidateDigest[:]) < string(result[j].CandidateDigest[:])
	})
	return result, nil
}

func (authority *ResearchSingleNodeFinalOrderAuthority) ResolveConflict(
	ctx context.Context,
	request finalorderdomain.ResolutionRequest,
) (finalorderdomain.ResolutionRecord, error) {
	if authority == nil || ctx == nil || request.Validate() != nil {
		return finalorderdomain.ResolutionRecord{}, finalorderdomain.ErrInvalidResolution
	}
	authority.mu.Lock()
	defer authority.mu.Unlock()
	state, err := authority.store.Load(ctx)
	if err != nil {
		return finalorderdomain.ResolutionRecord{}, err
	}
	initializeState(&state)
	idempotency := hex.EncodeToString(request.IdempotencyKeyHash[:])
	current, ok := findState(state.States, request.NamespaceID, request.CredentialID)
	if !ok || current.Status != finalorderdomain.StateConflicted {
		if digest, exists := state.Idempotency[idempotency]; exists {
			for _, resolution := range state.Resolutions {
				if resolution.ResolutionDigest == digest {
					return resolution, nil
				}
			}
		}
		return finalorderdomain.ResolutionRecord{}, finalorderdomain.ErrConflictRequired
	}
	if !sameDigestSet(current.ConflictDigests, request.CandidateDigests) {
		return finalorderdomain.ResolutionRecord{}, finalorderdomain.ErrInvalidResolution
	}
	maxVersion := uint64(0)
	for _, digest := range current.ConflictDigests {
		index := candidateIndex(state.Candidates, digest)
		if index < 0 {
			return finalorderdomain.ResolutionRecord{}, finalorderdomain.ErrPersistenceConflict
		}
		if state.Candidates[index].Candidate.DescriptorHash == request.ResolutionDescriptorHash {
			return finalorderdomain.ResolutionRecord{}, finalorderdomain.ErrInvalidResolution
		}
		if state.Candidates[index].Candidate.CandidateVersion > maxVersion {
			maxVersion = state.Candidates[index].Candidate.CandidateVersion
		}
	}
	resolutionDigest, err := digestResolution(request, maxVersion+1)
	if err != nil {
		return finalorderdomain.ResolutionRecord{}, err
	}
	if previous, exists := state.Idempotency[idempotency]; exists {
		if previous != resolutionDigest {
			return finalorderdomain.ResolutionRecord{}, finalorderdomain.ErrIdempotency
		}
		for _, resolution := range state.Resolutions {
			if resolution.ResolutionDigest == resolutionDigest {
				return resolution, nil
			}
		}
		return finalorderdomain.ResolutionRecord{}, finalorderdomain.ErrPersistenceConflict
	}
	receipt, checkpoint, err := authority.orderObject(
		state, request.NamespaceID, request.CredentialID, resolutionDigest,
	)
	if err != nil {
		return finalorderdomain.ResolutionRecord{}, err
	}
	for index := range state.Candidates {
		if containsDigest(current.ConflictDigests, state.Candidates[index].CandidateDigest) {
			if state.Candidates[index].CandidateDigest == request.SelectedCandidateDigest {
				state.Candidates[index].Disposition = finalorderdomain.DispositionSelected
			} else {
				state.Candidates[index].Disposition = finalorderdomain.DispositionRejected
			}
		}
	}
	resolution := finalorderdomain.ResolutionRecord{
		Request: request, ResolutionDigest: resolutionDigest,
		NewVersion: maxVersion + 1, Receipt: receipt,
	}
	state.NextSequence = receipt.Payload.FinalSequence
	state.Receipts = append(state.Receipts, receipt)
	state.Resolutions = append(state.Resolutions, resolution)
	state.Checkpoints = appendOrReplaceCheckpoint(state.Checkpoints, checkpoint)
	state.Idempotency[idempotency] = resolutionDigest
	setState(&state, finalorderdomain.FinalizedState{
		NamespaceID: request.NamespaceID, CredentialID: request.CredentialID,
		Status: finalorderdomain.StateActive, CurrentVersion: maxVersion + 1,
		DescriptorHash: request.ResolutionDescriptorHash,
		FinalSequence:  receipt.Payload.FinalSequence,
	})
	if err := saveState(ctx, authority.store, state); err != nil {
		return finalorderdomain.ResolutionRecord{}, err
	}
	return resolution, nil
}

func (authority *ResearchSingleNodeFinalOrderAuthority) GetTrustedCheckpoint(
	ctx context.Context,
	namespaceID protocol.NamespaceID,
) (finalorderdomain.TrustedCheckpoint, error) {
	if authority == nil || ctx == nil || bytesZero(namespaceID[:]) {
		return finalorderdomain.TrustedCheckpoint{}, finalorderdomain.ErrCandidateNotFound
	}
	authority.mu.Lock()
	defer authority.mu.Unlock()
	state, err := authority.store.Load(ctx)
	if err != nil {
		return finalorderdomain.TrustedCheckpoint{}, err
	}
	var best finalorderdomain.TrustedCheckpoint
	for _, checkpoint := range state.Checkpoints {
		if checkpoint.NamespaceID == namespaceID &&
			checkpoint.FinalSequence > best.FinalSequence {
			best = checkpoint
		}
	}
	if best.FinalSequence == 0 {
		return finalorderdomain.TrustedCheckpoint{}, finalorderdomain.ErrCandidateNotFound
	}
	return best, nil
}

func (authority *ResearchSingleNodeFinalOrderAuthority) orderObject(
	state finalorderdomain.PersistentState,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
	objectDigest [sha256.Size]byte,
) (finalorderdomain.FinalOrderReceipt, finalorderdomain.TrustedCheckpoint, error) {
	sequence := state.NextSequence + 1
	var previous *[sha256.Size]byte
	var lastReceipt [sha256.Size]byte
	var lastSequence uint64
	for _, receipt := range state.Receipts {
		if receipt.Payload.NamespaceID == namespaceID &&
			receipt.Payload.FinalSequence < sequence &&
			receipt.Payload.FinalSequence > lastSequence {
			copyValue := receipt.Payload.OrderedObjectDigest
			previous = &copyValue
			lastReceipt = receipt.Digest
			lastSequence = receipt.Payload.FinalSequence
		}
	}
	payload := finalorderdomain.FinalOrderReceiptPayload{
		Domain:     protocol.DomainPrefix + "FINAL-ORDER-RECEIPT",
		ProtocolID: protocol.ProtocolID, ProtocolVersion: protocol.ProtocolVersion,
		SuiteID: protocol.SuiteID, AdapterKind: finalorderdomain.AdapterKind,
		NamespaceID: namespaceID, CredentialID: credentialID,
		OrderedObjectDigest: objectDigest, FinalSequence: sequence,
		PreviousOrderedDigest: previous, AuthorityKeyID: authority.keyID,
		AuthorityKeyGeneration: authority.keyGeneration,
	}
	receipt, err := finalorderdomain.SignReceipt(authority.privateKey, payload)
	if err != nil {
		return finalorderdomain.FinalOrderReceipt{}, finalorderdomain.TrustedCheckpoint{}, err
	}
	lastReceipt = receipt.Digest
	root, err := stateRoot(state.States, namespaceID, objectDigest, sequence)
	if err != nil {
		return finalorderdomain.FinalOrderReceipt{}, finalorderdomain.TrustedCheckpoint{}, err
	}
	checkpoint, err := finalorderdomain.SignCheckpoint(authority.privateKey, finalorderdomain.TrustedCheckpoint{
		Domain:      protocol.DomainPrefix + "FINAL-ORDER-CHECKPOINT",
		AdapterKind: finalorderdomain.AdapterKind, NamespaceID: namespaceID,
		FinalSequence: sequence, StateRoot: root, LastReceiptDigest: lastReceipt,
		AuthorityKeyID: authority.keyID, KeyGeneration: authority.keyGeneration,
	})
	return receipt, checkpoint, err
}

func initializeState(state *finalorderdomain.PersistentState) {
	if state.Idempotency == nil {
		state.Idempotency = make(map[string][sha256.Size]byte)
	}
}

func saveState(
	ctx context.Context,
	store ports.SnapshotStore,
	state finalorderdomain.PersistentState,
) error {
	expected := state.Revision
	state.Revision++
	return store.CompareAndSwap(ctx, expected, state)
}

func findCandidate(records []finalorderdomain.CandidateRecord, digest [sha256.Size]byte) (finalorderdomain.CandidateRecord, bool) {
	index := candidateIndex(records, digest)
	if index < 0 {
		return finalorderdomain.CandidateRecord{}, false
	}
	return records[index], true
}

func candidateIndex(records []finalorderdomain.CandidateRecord, digest [sha256.Size]byte) int {
	for index := range records {
		if records[index].CandidateDigest == digest {
			return index
		}
	}
	return -1
}

func candidateBranches(records []finalorderdomain.CandidateRecord, candidate finalorderdomain.Candidate) []int {
	result := make([]int, 0, 3)
	for index, record := range records {
		if record.Candidate.NamespaceID == candidate.NamespaceID &&
			record.Candidate.CredentialID == candidate.CredentialID &&
			record.Candidate.BaseVersion == candidate.BaseVersion &&
			record.Candidate.BaseDescriptorHash == candidate.BaseDescriptorHash {
			result = append(result, index)
		}
	}
	return result
}

func findState(
	states []finalorderdomain.FinalizedState,
	namespaceID protocol.NamespaceID,
	credentialID protocol.CredentialID,
) (finalorderdomain.FinalizedState, bool) {
	for _, state := range states {
		if state.NamespaceID == namespaceID && state.CredentialID == credentialID {
			return state, true
		}
	}
	return finalorderdomain.FinalizedState{}, false
}

func setState(state *finalorderdomain.PersistentState, value finalorderdomain.FinalizedState) {
	for index := range state.States {
		if state.States[index].NamespaceID == value.NamespaceID &&
			state.States[index].CredentialID == value.CredentialID {
			state.States[index] = cloneFinalizedState(value)
			return
		}
	}
	state.States = append(state.States, cloneFinalizedState(value))
}

func cloneFinalizedState(value finalorderdomain.FinalizedState) finalorderdomain.FinalizedState {
	value.ConflictDigests = append([][sha256.Size]byte(nil), value.ConflictDigests...)
	return value
}

func findReceipt(
	receipts []finalorderdomain.FinalOrderReceipt,
	digest [sha256.Size]byte,
) (finalorderdomain.FinalOrderReceipt, bool) {
	for _, receipt := range receipts {
		if receipt.Digest == digest {
			return receipt, true
		}
	}
	return finalorderdomain.FinalOrderReceipt{}, false
}

func appendOrReplaceCheckpoint(
	values []finalorderdomain.TrustedCheckpoint,
	checkpoint finalorderdomain.TrustedCheckpoint,
) []finalorderdomain.TrustedCheckpoint {
	for index := range values {
		if values[index].NamespaceID == checkpoint.NamespaceID {
			values[index] = checkpoint
			return values
		}
	}
	return append(values, checkpoint)
}

func sameDigestSet(left, right [][sha256.Size]byte) bool {
	left = finalorderdomain.SortedDigests(left)
	right = finalorderdomain.SortedDigests(right)
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

func containsDigest(values [][sha256.Size]byte, wanted [sha256.Size]byte) bool {
	for _, value := range values {
		if value == wanted {
			return true
		}
	}
	return false
}

func digestResolution(
	request finalorderdomain.ResolutionRequest,
	newVersion uint64,
) ([sha256.Size]byte, error) {
	type projection struct {
		Domain           string                `cbor:"domain"`
		NamespaceID      protocol.NamespaceID  `cbor:"namespace_id"`
		CredentialID     protocol.CredentialID `cbor:"credential_id"`
		CandidateDigests [][sha256.Size]byte   `cbor:"candidate_digests"`
		Selected         [sha256.Size]byte     `cbor:"selected"`
		Resolution       [sha256.Size]byte     `cbor:"resolution_descriptor"`
		NewVersion       uint64                `cbor:"new_version"`
		ResolvedBy       string                `cbor:"resolved_by"`
		Basis            string                `cbor:"basis"`
	}
	encoded, err := protocol.MarshalDeterministic(projection{
		Domain:      protocol.DomainPrefix + "CONFLICT-RESOLUTION",
		NamespaceID: request.NamespaceID, CredentialID: request.CredentialID,
		CandidateDigests: finalorderdomain.SortedDigests(request.CandidateDigests),
		Selected:         request.SelectedCandidateDigest,
		Resolution:       request.ResolutionDescriptorHash, NewVersion: newVersion,
		ResolvedBy: request.ResolvedBy, Basis: request.Basis,
	})
	if err != nil {
		return [sha256.Size]byte{}, finalorderdomain.ErrInvalidResolution
	}
	return sha256.Sum256(encoded), nil
}

func stateRoot(
	states []finalorderdomain.FinalizedState,
	namespaceID protocol.NamespaceID,
	pendingDigest [sha256.Size]byte,
	sequence uint64,
) ([sha256.Size]byte, error) {
	filtered := make([]finalorderdomain.FinalizedState, 0, len(states))
	for _, state := range states {
		if state.NamespaceID == namespaceID {
			filtered = append(filtered, cloneFinalizedState(state))
		}
	}
	sort.Slice(filtered, func(i, j int) bool {
		return string(filtered[i].CredentialID[:]) < string(filtered[j].CredentialID[:])
	})
	encoded, err := protocol.MarshalDeterministic(struct {
		Domain        string                            `cbor:"domain"`
		States        []finalorderdomain.FinalizedState `cbor:"states"`
		PendingDigest [sha256.Size]byte                 `cbor:"pending_digest"`
		Sequence      uint64                            `cbor:"sequence"`
	}{
		Domain: protocol.DomainPrefix + "FINAL-ORDER-STATE-ROOT",
		States: filtered, PendingDigest: pendingDigest, Sequence: sequence,
	})
	if err != nil {
		return [sha256.Size]byte{}, err
	}
	return sha256.Sum256(encoded), nil
}

func bytesZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}

var _ FinalOrderAuthority = (*ResearchSingleNodeFinalOrderAuthority)(nil)
