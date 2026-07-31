// Package domain defines minimal-impact remediation plans and deterministic
// outcome commitments. A plan is not evidence of completion.
package domain

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"sort"

	"vdns.local/vdns/internal/protocol"
)

var (
	ErrInvalidRemediation = errors.New("invalid remediation")
	ErrOutOfScope         = errors.New("remediation target is outside affected set")
	ErrOutcomeMismatch    = errors.New("remediation outcome does not match evidence")
	ErrAttemptReplay      = errors.New("remediation attempt replay")
	ErrUnrelatedMutation  = errors.New("unrelated credential field was modified")
)

type Action uint8

const (
	ActionRotatePassword        Action = 1
	ActionRevokeSession         Action = 2
	ActionChangeRecoveryChannel Action = 3
	ActionRemoveSSOBinding      Action = 4
	ActionResetMFA              Action = 5
	ActionRevokeDevice          Action = 6
	ActionRevokeAPIToken        Action = 7
)

func (action Action) Valid() bool {
	return action >= ActionRotatePassword && action <= ActionRevokeAPIToken
}

type RecoveryRisk uint8

const (
	RecoveryRiskLow      RecoveryRisk = 1
	RecoveryRiskModerate RecoveryRisk = 2
	RecoveryRiskHigh     RecoveryRisk = 3
	RecoveryRiskLockout  RecoveryRisk = 4
)

func (risk RecoveryRisk) Valid() bool {
	return risk >= RecoveryRiskLow && risk <= RecoveryRiskLockout
}

type Precondition uint16

const (
	PreconditionSiteReachable        Precondition = 1 << 0
	PreconditionCurrentAuthValid     Precondition = 1 << 1
	PreconditionRecoveryPathVerified Precondition = 1 << 2
	PreconditionSecondFactorPresent  Precondition = 1 << 3
	PreconditionAdminApproval        Precondition = 1 << 4
)

const allPreconditions = PreconditionSiteReachable |
	PreconditionCurrentAuthValid | PreconditionRecoveryPathVerified |
	PreconditionSecondFactorPresent | PreconditionAdminApproval

func (conditions Precondition) Valid() bool {
	return conditions != 0 && conditions&^allPreconditions == 0
}

type CandidateAction struct {
	Action        Action
	Cost          uint64
	Preconditions Precondition
	RecoveryRisk  RecoveryRisk
}

type AffectedCredential struct {
	CredentialID protocol.CredentialID
	OldVersion   uint64
	Candidates   []CandidateAction
}

type PlanPolicy struct {
	AvailablePreconditions Precondition
	MaximumRecoveryRisk    RecoveryRisk
	AllowedActions         map[Action]bool
}

type PlanItem struct {
	ItemID        [sha256.Size]byte
	CredentialID  protocol.CredentialID
	OldVersion    uint64
	Action        Action
	Cost          uint64
	Preconditions Precondition
	RecoveryRisk  RecoveryRisk
}

type Plan struct {
	CampaignID protocol.CampaignID
	Items      []PlanItem
	TotalCost  uint64
}

// BuildPlan selects the lowest-cost allowed action for every affected
// credential without crossing recovery-risk or prerequisite boundaries.
func BuildPlan(
	campaignID protocol.CampaignID,
	affected []AffectedCredential,
	policy PlanPolicy,
) (Plan, error) {
	if remediationZero(campaignID[:]) || len(affected) == 0 ||
		!policy.AvailablePreconditions.Valid() ||
		!policy.MaximumRecoveryRisk.Valid() || len(policy.AllowedActions) == 0 {
		return Plan{}, ErrInvalidRemediation
	}
	ordered := append([]AffectedCredential(nil), affected...)
	sort.Slice(ordered, func(i, j int) bool {
		return bytes.Compare(ordered[i].CredentialID[:], ordered[j].CredentialID[:]) < 0
	})
	items := make([]PlanItem, 0, len(ordered))
	var total uint64
	for index, credential := range ordered {
		if remediationZero(credential.CredentialID[:]) || credential.OldVersion == 0 ||
			len(credential.Candidates) == 0 ||
			index > 0 && credential.CredentialID == ordered[index-1].CredentialID {
			return Plan{}, ErrInvalidRemediation
		}
		var selected *CandidateAction
		for candidateIndex := range credential.Candidates {
			candidate := credential.Candidates[candidateIndex]
			if !candidate.Action.Valid() || candidate.Cost == 0 ||
				!candidate.Preconditions.Valid() || !candidate.RecoveryRisk.Valid() {
				return Plan{}, ErrInvalidRemediation
			}
			if !policy.AllowedActions[candidate.Action] ||
				candidate.RecoveryRisk > policy.MaximumRecoveryRisk ||
				candidate.Preconditions&^policy.AvailablePreconditions != 0 {
				continue
			}
			if selected == nil || candidate.Cost < selected.Cost ||
				candidate.Cost == selected.Cost && candidate.Action < selected.Action {
				value := candidate
				selected = &value
			}
		}
		if selected == nil || total > ^uint64(0)-selected.Cost {
			return Plan{}, ErrInvalidRemediation
		}
		itemBody := struct {
			Domain       string
			CampaignID   protocol.CampaignID
			CredentialID protocol.CredentialID
			OldVersion   uint64
			Action       Action
		}{
			Domain:     protocol.DomainPrefix + "REMEDIATION-PLAN-ITEM",
			CampaignID: campaignID, CredentialID: credential.CredentialID,
			OldVersion: credential.OldVersion, Action: selected.Action,
		}
		encoded, err := protocol.MarshalDeterministic(itemBody)
		if err != nil {
			return Plan{}, ErrInvalidRemediation
		}
		item := PlanItem{
			ItemID: sha256.Sum256(encoded), CredentialID: credential.CredentialID,
			OldVersion: credential.OldVersion, Action: selected.Action,
			Cost: selected.Cost, Preconditions: selected.Preconditions,
			RecoveryRisk: selected.RecoveryRisk,
		}
		total += selected.Cost
		items = append(items, item)
	}
	return Plan{CampaignID: campaignID, Items: items, TotalCost: total}, nil
}

type OutcomeStatus uint8

const (
	OutcomeCompleted OutcomeStatus = 1
	OutcomePending   OutcomeStatus = 2
	OutcomeFailed    OutcomeStatus = 3
	OutcomeUnknown   OutcomeStatus = 4
)

func (status OutcomeStatus) Valid() bool {
	return status >= OutcomeCompleted && status <= OutcomeUnknown
}

type FieldType uint8

const (
	FieldOrigin        FieldType = 1
	FieldUsername      FieldType = 2
	FieldPassword      FieldType = 3
	FieldTOTP          FieldType = 4
	FieldRecoveryCodes FieldType = 5
	FieldNotes         FieldType = 6
)

type FieldDigests map[FieldType][sha256.Size]byte

type ItemOutcome struct {
	ItemID         [sha256.Size]byte
	CredentialID   protocol.CredentialID
	Action         Action
	OldVersion     uint64
	NewVersion     uint64
	Attempt        uint64
	Status         OutcomeStatus
	EvidenceDigest [sha256.Size]byte
	BeforeFields   FieldDigests
	AfterFields    FieldDigests
}

type OutcomeCounts struct {
	Completed uint64
	Pending   uint64
	Failed    uint64
	Unknown   uint64
}

type RotationCommitment struct {
	CampaignID   protocol.CampaignID
	AffectedRoot [sha256.Size]byte
	Items        []ItemOutcome
	ChangedSet   []protocol.CredentialID
	Counts       OutcomeCounts
	RotationRoot [sha256.Size]byte
}

// AffectedScope prevents the remediation package from importing a separate
// bounded context while still requiring an independently validated set.
type AffectedScope interface {
	Contains(protocol.CredentialID) bool
	Root() [sha256.Size]byte
}

type AttemptRegistry interface {
	LastAttempt(campaignID protocol.CampaignID, itemID [sha256.Size]byte) uint64
	CommitAttempt(campaignID protocol.CampaignID, itemID [sha256.Size]byte, attempt uint64) error
}

func BuildRotationCommitment(
	plan Plan,
	scope AffectedScope,
	outcomes []ItemOutcome,
	attempts AttemptRegistry,
) (RotationCommitment, error) {
	affectedRoot := [sha256.Size]byte{}
	if scope != nil {
		affectedRoot = scope.Root()
	}
	if remediationZero(plan.CampaignID[:]) || len(plan.Items) == 0 ||
		scope == nil || remediationZero(affectedRoot[:]) || attempts == nil ||
		len(outcomes) != len(plan.Items) {
		return RotationCommitment{}, ErrInvalidRemediation
	}
	planned := make(map[[sha256.Size]byte]PlanItem, len(plan.Items))
	for _, item := range plan.Items {
		planned[item.ItemID] = item
	}
	canonical := append([]ItemOutcome(nil), outcomes...)
	sort.Slice(canonical, func(i, j int) bool {
		return bytes.Compare(canonical[i].ItemID[:], canonical[j].ItemID[:]) < 0
	})
	changed := make([]protocol.CredentialID, 0, len(canonical))
	var counts OutcomeCounts
	for index := range canonical {
		outcome := &canonical[index]
		item, exists := planned[outcome.ItemID]
		if !exists || outcome.CredentialID != item.CredentialID ||
			outcome.Action != item.Action || outcome.OldVersion != item.OldVersion ||
			!scope.Contains(outcome.CredentialID) || outcome.Attempt == 0 ||
			!outcome.Status.Valid() {
			return RotationCommitment{}, ErrOutOfScope
		}
		if outcome.Attempt <= attempts.LastAttempt(plan.CampaignID, outcome.ItemID) {
			return RotationCommitment{}, ErrAttemptReplay
		}
		if err := validateOutcome(*outcome); err != nil {
			return RotationCommitment{}, err
		}
		switch outcome.Status {
		case OutcomeCompleted:
			counts.Completed++
			changed = append(changed, outcome.CredentialID)
		case OutcomePending:
			counts.Pending++
		case OutcomeFailed:
			counts.Failed++
		case OutcomeUnknown:
			counts.Unknown++
		}
	}
	sort.Slice(changed, func(i, j int) bool {
		return bytes.Compare(changed[i][:], changed[j][:]) < 0
	})
	body := struct {
		Domain       string
		CampaignID   protocol.CampaignID
		AffectedRoot [sha256.Size]byte
		Items        []ItemOutcome
		Counts       OutcomeCounts
		ChangedSet   []protocol.CredentialID
	}{
		Domain:     protocol.DomainPrefix + "ROTATION-ROOT",
		CampaignID: plan.CampaignID, AffectedRoot: affectedRoot,
		Items: canonical, Counts: counts, ChangedSet: changed,
	}
	encoded, err := protocol.MarshalDeterministic(body)
	if err != nil {
		return RotationCommitment{}, ErrInvalidRemediation
	}
	for _, outcome := range canonical {
		if err := attempts.CommitAttempt(plan.CampaignID, outcome.ItemID, outcome.Attempt); err != nil {
			return RotationCommitment{}, ErrAttemptReplay
		}
	}
	return RotationCommitment{
		CampaignID: plan.CampaignID, AffectedRoot: affectedRoot,
		Items: canonical, ChangedSet: changed, Counts: counts,
		RotationRoot: sha256.Sum256(encoded),
	}, nil
}

func validateOutcome(outcome ItemOutcome) error {
	if remediationZero(outcome.EvidenceDigest[:]) ||
		len(outcome.BeforeFields) == 0 || len(outcome.AfterFields) == 0 ||
		len(outcome.BeforeFields) != len(outcome.AfterFields) {
		return ErrOutcomeMismatch
	}
	allowed := allowedChangedFields(outcome.Action)
	changed := 0
	for field, before := range outcome.BeforeFields {
		after, exists := outcome.AfterFields[field]
		if !exists || remediationZero(before[:]) || remediationZero(after[:]) {
			return ErrOutcomeMismatch
		}
		if before != after {
			changed++
			if !allowed[field] {
				return ErrUnrelatedMutation
			}
		}
	}
	if outcome.Status != OutcomeCompleted {
		if changed != 0 || outcome.NewVersion != outcome.OldVersion {
			return ErrOutcomeMismatch
		}
		return nil
	}
	if outcome.Action == ActionRotatePassword {
		if outcome.NewVersion != outcome.OldVersion+1 || changed != 1 ||
			outcome.BeforeFields[FieldPassword] == outcome.AfterFields[FieldPassword] {
			return ErrOutcomeMismatch
		}
		return nil
	}
	if outcome.Action == ActionChangeRecoveryChannel {
		if outcome.NewVersion != outcome.OldVersion+1 || changed != 1 ||
			outcome.BeforeFields[FieldRecoveryCodes] ==
				outcome.AfterFields[FieldRecoveryCodes] {
			return ErrOutcomeMismatch
		}
		return nil
	}
	if outcome.Action == ActionResetMFA {
		if outcome.NewVersion != outcome.OldVersion+1 || changed < 1 || changed > 2 {
			return ErrOutcomeMismatch
		}
		return nil
	}
	if outcome.NewVersion != outcome.OldVersion || changed != 0 {
		return ErrOutcomeMismatch
	}
	return nil
}

func allowedChangedFields(action Action) map[FieldType]bool {
	switch action {
	case ActionRotatePassword:
		return map[FieldType]bool{FieldPassword: true}
	case ActionChangeRecoveryChannel:
		return map[FieldType]bool{FieldRecoveryCodes: true}
	case ActionResetMFA:
		return map[FieldType]bool{FieldTOTP: true, FieldRecoveryCodes: true}
	default:
		return map[FieldType]bool{}
	}
}

func remediationZero(value []byte) bool {
	var combined byte
	for _, item := range value {
		combined |= item
	}
	return combined == 0
}
