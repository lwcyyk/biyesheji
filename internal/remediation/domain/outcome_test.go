package domain

import "testing"

func TestCompletedActionsEnforceTheirMinimalFieldSet(t *testing.T) {
	before := FieldDigests{
		FieldOrigin: {1}, FieldUsername: {2}, FieldPassword: {3},
		FieldTOTP: {4}, FieldRecoveryCodes: {5}, FieldNotes: {6},
	}
	tests := []struct {
		name       string
		action     Action
		newVersion uint64
		mutate     func(FieldDigests)
		wantError  error
	}{
		{
			name: "recovery channel", action: ActionChangeRecoveryChannel, newVersion: 2,
			mutate: func(fields FieldDigests) { fields[FieldRecoveryCodes] = [32]byte{9} },
		},
		{
			name: "reset MFA", action: ActionResetMFA, newVersion: 2,
			mutate: func(fields FieldDigests) { fields[FieldTOTP] = [32]byte{9} },
		},
		{
			name: "revoke session external state", action: ActionRevokeSession, newVersion: 1,
			mutate: func(FieldDigests) {},
		},
		{
			name: "revoke session cannot alter vault field", action: ActionRevokeSession, newVersion: 1,
			mutate:    func(fields FieldDigests) { fields[FieldNotes] = [32]byte{9} },
			wantError: ErrUnrelatedMutation,
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			after := make(FieldDigests, len(before))
			for field, digest := range before {
				after[field] = digest
			}
			test.mutate(after)
			err := validateOutcome(ItemOutcome{
				Action: test.action, OldVersion: 1, NewVersion: test.newVersion,
				Status: OutcomeCompleted, EvidenceDigest: [32]byte{8},
				BeforeFields: before, AfterFields: after,
			})
			if err != test.wantError {
				t.Fatalf("validateOutcome = %v, want %v", err, test.wantError)
			}
		})
	}
}
