package domain

import (
	"crypto/sha256"
	"errors"

	"vdns.local/vdns/internal/protocol"
)

var (
	ErrInvalidAggregateState      = errors.New("invalid credential aggregate state")
	ErrInvalidAggregateTransition = errors.New("invalid credential aggregate transition")
	ErrAggregateEvidence          = errors.New("credential aggregate evidence is insufficient")
)

// AggregatePhase includes the two local creation phases that do not yet have
// a publishable LifecycleStatus.
type AggregatePhase uint8

const (
	PhaseNonexistent AggregatePhase = iota + 1
	PhaseCreatePending
	PhaseActive
	PhaseUpdatePending
	PhaseSiteConfirmPending
	PhaseSuspended
	PhaseRevoked
	PhaseConflicted
)

func (phase AggregatePhase) Valid() bool {
	return phase >= PhaseNonexistent && phase <= PhaseConflicted
}

// CanTransitionTo is the sole aggregate lifecycle edge table.
func (phase AggregatePhase) CanTransitionTo(next AggregatePhase) bool {
	switch phase {
	case PhaseNonexistent:
		return next == PhaseCreatePending
	case PhaseCreatePending:
		return next == PhaseActive || next == PhaseNonexistent
	case PhaseActive:
		return next == PhaseUpdatePending || next == PhaseSuspended ||
			next == PhaseConflicted
	case PhaseUpdatePending:
		return next == PhaseSiteConfirmPending || next == PhaseConflicted
	case PhaseSiteConfirmPending:
		return next == PhaseActive || next == PhaseConflicted
	case PhaseSuspended:
		return next == PhaseRevoked
	case PhaseConflicted:
		return next == PhaseActive
	default:
		return false
	}
}

func (phase AggregatePhase) LifecycleStatus() (protocol.LifecycleStatus, error) {
	switch phase {
	case PhaseActive:
		return protocol.LifecycleActive, nil
	case PhaseUpdatePending:
		return protocol.LifecycleUpdatePending, nil
	case PhaseSiteConfirmPending:
		return protocol.LifecycleSiteConfirmPending, nil
	case PhaseSuspended:
		return protocol.LifecycleSuspended, nil
	case PhaseRevoked:
		return protocol.LifecycleRevoked, nil
	case PhaseConflicted:
		return protocol.LifecycleConflicted, nil
	default:
		return 0, ErrInvalidAggregateState
	}
}

// CredentialAggregate is the in-memory decision model. Hashes are public
// control-object digests; no password material is retained here.
type CredentialAggregate struct {
	phase                AggregatePhase
	activeVersion        uint64
	activeDescriptorHash [sha256.Size]byte
	candidateVersion     uint64
	candidateDescriptor  [sha256.Size]byte
	conflictCandidates   []DescriptorCandidate
}

type DescriptorCandidate struct {
	Version        uint64
	DescriptorHash [sha256.Size]byte
}

type AggregateSnapshot struct {
	Phase                AggregatePhase
	ActiveVersion        uint64
	ActiveDescriptorHash [sha256.Size]byte
	CandidateVersion     uint64
	CandidateDescriptor  [sha256.Size]byte
	ConflictCandidates   []DescriptorCandidate
}

func NewCredentialAggregate() *CredentialAggregate {
	return &CredentialAggregate{phase: PhaseNonexistent}
}

func RestoreCredentialAggregate(snapshot AggregateSnapshot) (*CredentialAggregate, error) {
	aggregate := &CredentialAggregate{
		phase: snapshot.Phase, activeVersion: snapshot.ActiveVersion,
		activeDescriptorHash: snapshot.ActiveDescriptorHash,
		candidateVersion:     snapshot.CandidateVersion,
		candidateDescriptor:  snapshot.CandidateDescriptor,
		conflictCandidates:   cloneCandidates(snapshot.ConflictCandidates),
	}
	if aggregate.validate() != nil {
		return nil, ErrInvalidAggregateState
	}
	return aggregate, nil
}

func (aggregate *CredentialAggregate) Snapshot() AggregateSnapshot {
	if aggregate == nil {
		return AggregateSnapshot{}
	}
	return AggregateSnapshot{
		Phase: aggregate.phase, ActiveVersion: aggregate.activeVersion,
		ActiveDescriptorHash: aggregate.activeDescriptorHash,
		CandidateVersion:     aggregate.candidateVersion,
		CandidateDescriptor:  aggregate.candidateDescriptor,
		ConflictCandidates:   cloneCandidates(aggregate.conflictCandidates),
	}
}

func (aggregate *CredentialAggregate) BeginCreate(
	descriptorHash [sha256.Size]byte,
) error {
	if aggregate == nil || aggregate.phase != PhaseNonexistent ||
		allZero(descriptorHash[:]) {
		return ErrInvalidAggregateTransition
	}
	aggregate.phase = PhaseCreatePending
	aggregate.candidateVersion = 1
	aggregate.candidateDescriptor = descriptorHash
	return nil
}

func (aggregate *CredentialAggregate) AbortCreate() error {
	if aggregate == nil || aggregate.phase != PhaseCreatePending {
		return ErrInvalidAggregateTransition
	}
	aggregate.phase = PhaseNonexistent
	aggregate.candidateVersion = 0
	aggregate.candidateDescriptor = [sha256.Size]byte{}
	return nil
}

func (aggregate *CredentialAggregate) ActivateCreated(
	evidence protocol.EvidenceLevel,
) error {
	if aggregate == nil || aggregate.phase != PhaseCreatePending ||
		!evidence.ActivatesCredential() {
		return ErrAggregateEvidence
	}
	aggregate.phase = PhaseActive
	aggregate.activeVersion = aggregate.candidateVersion
	aggregate.activeDescriptorHash = aggregate.candidateDescriptor
	aggregate.clearCandidate()
	return aggregate.validate()
}

func (aggregate *CredentialAggregate) BeginUpdate(
	expectedVersion uint64,
	previousDescriptorHash [sha256.Size]byte,
	candidateDescriptorHash [sha256.Size]byte,
) error {
	if aggregate == nil || aggregate.phase != PhaseActive ||
		expectedVersion != aggregate.activeVersion ||
		previousDescriptorHash != aggregate.activeDescriptorHash ||
		allZero(candidateDescriptorHash[:]) ||
		candidateDescriptorHash == previousDescriptorHash {
		return ErrInvalidAggregateTransition
	}
	aggregate.phase = PhaseUpdatePending
	aggregate.candidateVersion = aggregate.activeVersion + 1
	aggregate.candidateDescriptor = candidateDescriptorHash
	return aggregate.validate()
}

// MarkSiteConfirmPending is allowed only after the new ciphertext is already
// durable locally. The aggregate intentionally keeps the old active pointer.
func (aggregate *CredentialAggregate) MarkSiteConfirmPending() error {
	if aggregate == nil || aggregate.phase != PhaseUpdatePending {
		return ErrInvalidAggregateTransition
	}
	aggregate.phase = PhaseSiteConfirmPending
	return aggregate.validate()
}

func (aggregate *CredentialAggregate) ConfirmUpdate(
	evidence protocol.EvidenceLevel,
) error {
	if aggregate == nil || aggregate.phase != PhaseSiteConfirmPending {
		return ErrInvalidAggregateTransition
	}
	if !evidence.ActivatesCredential() {
		return ErrAggregateEvidence
	}
	aggregate.phase = PhaseActive
	aggregate.activeVersion = aggregate.candidateVersion
	aggregate.activeDescriptorHash = aggregate.candidateDescriptor
	aggregate.clearCandidate()
	return aggregate.validate()
}

func (aggregate *CredentialAggregate) Suspend() error {
	if aggregate == nil || aggregate.phase != PhaseActive {
		return ErrInvalidAggregateTransition
	}
	aggregate.phase = PhaseSuspended
	return nil
}

func (aggregate *CredentialAggregate) Revoke() error {
	if aggregate == nil || aggregate.phase != PhaseSuspended {
		return ErrInvalidAggregateTransition
	}
	aggregate.phase = PhaseRevoked
	return nil
}

// MarkConflict retains both current and competing descriptors. Nothing is
// selected or overwritten automatically.
func (aggregate *CredentialAggregate) MarkConflict(
	competingVersion uint64,
	competingDescriptor [sha256.Size]byte,
) error {
	if aggregate == nil ||
		(aggregate.phase != PhaseActive && aggregate.phase != PhaseUpdatePending &&
			aggregate.phase != PhaseSiteConfirmPending) ||
		competingVersion == 0 || allZero(competingDescriptor[:]) {
		return ErrInvalidAggregateTransition
	}
	retained := []DescriptorCandidate{{
		Version: aggregate.activeVersion, DescriptorHash: aggregate.activeDescriptorHash,
	}}
	if !allZero(aggregate.candidateDescriptor[:]) &&
		aggregate.candidateDescriptor != aggregate.activeDescriptorHash {
		retained = append(retained, DescriptorCandidate{
			Version:        aggregate.candidateVersion,
			DescriptorHash: aggregate.candidateDescriptor,
		})
	}
	competing := DescriptorCandidate{
		Version: competingVersion, DescriptorHash: competingDescriptor,
	}
	if !candidateMember(retained, competing) {
		retained = append(retained, competing)
	}
	if len(retained) < 2 {
		return ErrInvalidAggregateTransition
	}
	aggregate.phase = PhaseConflicted
	aggregate.conflictCandidates = retained
	return aggregate.validate()
}

// ResolveConflict requires strong evidence and an explicitly retained
// descriptor. The caller must publish a separate resolution event.
func (aggregate *CredentialAggregate) ResolveConflict(
	selectedVersion uint64,
	selectedDescriptor [sha256.Size]byte,
	evidence protocol.EvidenceLevel,
) error {
	if aggregate == nil || aggregate.phase != PhaseConflicted ||
		!evidence.ActivatesCredential() {
		return ErrAggregateEvidence
	}
	if selectedVersion < aggregate.activeVersion ||
		!candidateMember(aggregate.conflictCandidates, DescriptorCandidate{
			Version: selectedVersion, DescriptorHash: selectedDescriptor,
		}) {
		return ErrInvalidAggregateTransition
	}
	aggregate.phase = PhaseActive
	aggregate.activeVersion = selectedVersion
	aggregate.activeDescriptorHash = selectedDescriptor
	aggregate.clearCandidate()
	aggregate.conflictCandidates = nil
	return aggregate.validate()
}

func (aggregate *CredentialAggregate) clearCandidate() {
	aggregate.candidateVersion = 0
	aggregate.candidateDescriptor = [sha256.Size]byte{}
}

func (aggregate *CredentialAggregate) validate() error {
	if aggregate == nil || !aggregate.phase.Valid() {
		return ErrInvalidAggregateState
	}
	switch aggregate.phase {
	case PhaseNonexistent:
		if aggregate.activeVersion != 0 || aggregate.candidateVersion != 0 ||
			!allZero(aggregate.activeDescriptorHash[:]) ||
			!allZero(aggregate.candidateDescriptor[:]) ||
			len(aggregate.conflictCandidates) != 0 {
			return ErrInvalidAggregateState
		}
	case PhaseCreatePending:
		if aggregate.activeVersion != 0 || aggregate.candidateVersion != 1 ||
			allZero(aggregate.candidateDescriptor[:]) {
			return ErrInvalidAggregateState
		}
	case PhaseActive, PhaseSuspended, PhaseRevoked:
		if aggregate.activeVersion == 0 || allZero(aggregate.activeDescriptorHash[:]) ||
			aggregate.candidateVersion != 0 ||
			!allZero(aggregate.candidateDescriptor[:]) ||
			len(aggregate.conflictCandidates) != 0 {
			return ErrInvalidAggregateState
		}
	case PhaseUpdatePending, PhaseSiteConfirmPending:
		if aggregate.activeVersion == 0 || allZero(aggregate.activeDescriptorHash[:]) ||
			aggregate.candidateVersion != aggregate.activeVersion+1 ||
			allZero(aggregate.candidateDescriptor[:]) ||
			aggregate.candidateDescriptor == aggregate.activeDescriptorHash {
			return ErrInvalidAggregateState
		}
	case PhaseConflicted:
		if aggregate.activeVersion == 0 || allZero(aggregate.activeDescriptorHash[:]) ||
			len(aggregate.conflictCandidates) < 2 ||
			!candidateMember(aggregate.conflictCandidates, DescriptorCandidate{
				Version:        aggregate.activeVersion,
				DescriptorHash: aggregate.activeDescriptorHash,
			}) {
			return ErrInvalidAggregateState
		}
		for _, candidate := range aggregate.conflictCandidates {
			if candidate.Version == 0 || allZero(candidate.DescriptorHash[:]) {
				return ErrInvalidAggregateState
			}
		}
	}
	return nil
}

func candidateMember(values []DescriptorCandidate, target DescriptorCandidate) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}

func cloneCandidates(values []DescriptorCandidate) []DescriptorCandidate {
	return append([]DescriptorCandidate(nil), values...)
}
