package domain_test

import (
	"errors"
	"testing"

	exposuredomain "vpass.local/vpass/internal/exposure/domain"
	"vpass.local/vpass/internal/protocol"
	remediationapp "vpass.local/vpass/internal/remediation/application"
	remediationdomain "vpass.local/vpass/internal/remediation/domain"
)

func TestPlannerSupportsAllActionsAndChoosesLowestSafeCost(t *testing.T) {
	campaign := protocol.CampaignID{1}
	allowed := map[remediationdomain.Action]bool{}
	affected := make([]remediationdomain.AffectedCredential, 0, 7)
	for action := remediationdomain.ActionRotatePassword; action <= remediationdomain.ActionRevokeAPIToken; action++ {
		allowed[action] = true
		affected = append(affected, remediationdomain.AffectedCredential{
			CredentialID: protocol.CredentialID{byte(action)}, OldVersion: 1,
			Candidates: []remediationdomain.CandidateAction{{
				Action: action, Cost: uint64(action) + 10,
				Preconditions: remediationdomain.PreconditionCurrentAuthValid,
				RecoveryRisk:  remediationdomain.RecoveryRiskModerate,
			}},
		})
	}
	// A lower-cost but lockout-risk candidate must not be selected.
	affected[0].Candidates = append(affected[0].Candidates, remediationdomain.CandidateAction{
		Action: remediationdomain.ActionRevokeDevice, Cost: 1,
		Preconditions: remediationdomain.PreconditionCurrentAuthValid,
		RecoveryRisk:  remediationdomain.RecoveryRiskLockout,
	})
	plan, err := remediationdomain.BuildPlan(campaign, affected, remediationdomain.PlanPolicy{
		AvailablePreconditions: remediationdomain.PreconditionCurrentAuthValid,
		MaximumRecoveryRisk:    remediationdomain.RecoveryRiskModerate,
		AllowedActions:         allowed,
	})
	if err != nil || len(plan.Items) != 7 {
		t.Fatalf("plan = %+v, %v", plan, err)
	}
	if plan.Items[0].Action != remediationdomain.ActionRotatePassword ||
		plan.Items[0].RecoveryRisk > remediationdomain.RecoveryRiskModerate {
		t.Fatal("planner selected an unsafe action")
	}
}

func TestRotationRootBindsRealOutcomesAndRejectsReplayOrUnrelatedChanges(t *testing.T) {
	plan, scope := remediationFixture(t)
	outcomes := make([]remediationdomain.ItemOutcome, len(plan.Items))
	statuses := []remediationdomain.OutcomeStatus{
		remediationdomain.OutcomeCompleted,
		remediationdomain.OutcomePending,
		remediationdomain.OutcomeFailed,
		remediationdomain.OutcomeUnknown,
	}
	for index, item := range plan.Items {
		before := fieldDigests(byte(20 + index))
		after := cloneFieldDigests(before)
		newVersion := item.OldVersion
		if statuses[index] == remediationdomain.OutcomeCompleted {
			after[remediationdomain.FieldPassword] = [32]byte{99}
			newVersion++
		}
		outcomes[index] = remediationdomain.ItemOutcome{
			ItemID: item.ItemID, CredentialID: item.CredentialID, Action: item.Action,
			OldVersion: item.OldVersion, NewVersion: newVersion, Attempt: 1,
			Status: statuses[index], EvidenceDigest: [32]byte{byte(index + 1)},
			BeforeFields: before, AfterFields: after,
		}
	}
	registry := remediationapp.NewMemoryAttemptRegistry()
	commitment, err := remediationdomain.BuildRotationCommitment(plan, scope, outcomes, registry)
	if err != nil {
		t.Fatal(err)
	}
	if commitment.Counts != (remediationdomain.OutcomeCounts{
		Completed: 1, Pending: 1, Failed: 1, Unknown: 1,
	}) || len(commitment.ChangedSet) != 1 ||
		commitment.ChangedSet[0] != outcomes[0].CredentialID {
		t.Fatalf("incorrect real outcome partition: %+v", commitment)
	}
	if _, err := remediationdomain.BuildRotationCommitment(plan, scope, outcomes, registry); !errors.Is(err, remediationdomain.ErrAttemptReplay) {
		t.Fatalf("attempt replay = %v", err)
	}

	tampered := cloneOutcomes(outcomes)
	tampered[0].Attempt = 2
	tampered[0].AfterFields[remediationdomain.FieldUsername] = [32]byte{100}
	if _, err := remediationdomain.BuildRotationCommitment(
		plan, scope, tampered, remediationapp.NewMemoryAttemptRegistry(),
	); !errors.Is(err, remediationdomain.ErrUnrelatedMutation) {
		t.Fatalf("unrelated mutation = %v", err)
	}

	pendingChanged := cloneOutcomes(outcomes)
	pendingChanged[1].Attempt = 2
	pendingChanged[1].AfterFields[remediationdomain.FieldPassword] = [32]byte{101}
	if _, err := remediationdomain.BuildRotationCommitment(
		plan, scope, pendingChanged, remediationapp.NewMemoryAttemptRegistry(),
	); !errors.Is(err, remediationdomain.ErrOutcomeMismatch) {
		t.Fatalf("pending claimed as changed = %v", err)
	}

	outOfScope := cloneOutcomes(outcomes)
	outOfScope[0].CredentialID = protocol.CredentialID{200}
	if _, err := remediationdomain.BuildRotationCommitment(
		plan, scope, outOfScope, remediationapp.NewMemoryAttemptRegistry(),
	); !errors.Is(err, remediationdomain.ErrOutOfScope) {
		t.Fatalf("out-of-scope mutation = %v", err)
	}
}

func remediationFixture(
	t *testing.T,
) (remediationdomain.Plan, remediationapp.ValidatedAffectedScope) {
	t.Helper()
	entries := make([]exposuredomain.SnapshotEntry, 4)
	affectedItems := make([]exposuredomain.AffectedItem, 4)
	credentials := make([]remediationdomain.AffectedCredential, 4)
	for index := range entries {
		id := protocol.CredentialID{byte(index + 1)}
		entries[index] = exposuredomain.SnapshotEntry{
			CredentialID: id, CredentialVersion: 1,
			EventDigest: [32]byte{byte(index + 2)}, Epoch: 1,
			ObservedBucket: uint64(10 + index),
		}
		affectedItems[index] = exposuredomain.AffectedItem{
			CredentialID: id, ReasonDigest: [32]byte{byte(index + 10)},
		}
		credentials[index] = remediationdomain.AffectedCredential{
			CredentialID: id, OldVersion: 1,
			Candidates: []remediationdomain.CandidateAction{{
				Action: remediationdomain.ActionRotatePassword, Cost: uint64(index + 1),
				Preconditions: remediationdomain.PreconditionSiteReachable |
					remediationdomain.PreconditionCurrentAuthValid,
				RecoveryRisk: remediationdomain.RecoveryRiskLow,
			}},
		}
	}
	snapshot, err := exposuredomain.NewIncidentSnapshot(
		protocol.NamespaceID{1}, 10, 20, [32]byte{3}, [32]byte{4}, entries,
	)
	if err != nil {
		t.Fatal(err)
	}
	set, err := exposuredomain.NewAffectedSet(snapshot, affectedItems)
	if err != nil {
		t.Fatal(err)
	}
	scope, err := remediationapp.NewValidatedAffectedScope(snapshot, set)
	if err != nil {
		t.Fatal(err)
	}
	plan, err := remediationdomain.BuildPlan(
		protocol.CampaignID{5}, credentials,
		remediationdomain.PlanPolicy{
			AvailablePreconditions: remediationdomain.PreconditionSiteReachable |
				remediationdomain.PreconditionCurrentAuthValid,
			MaximumRecoveryRisk: remediationdomain.RecoveryRiskModerate,
			AllowedActions: map[remediationdomain.Action]bool{
				remediationdomain.ActionRotatePassword: true,
			},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	return plan, scope
}

func fieldDigests(seed byte) remediationdomain.FieldDigests {
	return remediationdomain.FieldDigests{
		remediationdomain.FieldOrigin:        {0: seed + 1},
		remediationdomain.FieldUsername:      {0: seed + 2},
		remediationdomain.FieldPassword:      {0: seed + 3},
		remediationdomain.FieldTOTP:          {0: seed + 4},
		remediationdomain.FieldRecoveryCodes: {0: seed + 5},
		remediationdomain.FieldNotes:         {0: seed + 6},
	}
}

func cloneFieldDigests(input remediationdomain.FieldDigests) remediationdomain.FieldDigests {
	output := make(remediationdomain.FieldDigests, len(input))
	for field, digest := range input {
		output[field] = digest
	}
	return output
}

func cloneOutcomes(input []remediationdomain.ItemOutcome) []remediationdomain.ItemOutcome {
	output := append([]remediationdomain.ItemOutcome(nil), input...)
	for index := range output {
		output[index].BeforeFields = cloneFieldDigests(input[index].BeforeFields)
		output[index].AfterFields = cloneFieldDigests(input[index].AfterFields)
	}
	return output
}
