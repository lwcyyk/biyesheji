package protocol

import "testing"

func TestFrozenRegistryValuesAndCapabilities(t *testing.T) {
	t.Parallel()
	tests := []struct {
		operation  OperationType
		value      uint16
		capability Capability
	}{
		{OperationCreate, 1, CapabilityCreate},
		{OperationResolve, 2, CapabilityRead},
		{OperationAutofill, 3, CapabilityAutofill},
		{OperationUseObserved, 4, CapabilityPublishAudit},
		{OperationUpdatePrepare, 5, CapabilityUpdate},
		{OperationUpdateConfirm, 6, CapabilityUpdate},
		{OperationSyncPublish, 7, CapabilityUpdate},
		{OperationSyncAccept, 8, CapabilityRead},
		{OperationRotate, 9, CapabilityRotate},
		{OperationMigrate, 10, CapabilityMigrate},
		{OperationSuspend, 11, CapabilityRevoke},
		{OperationRevoke, 12, CapabilityRevoke},
		{OperationDeviceEnroll, 13, CapabilityDeviceEnroll},
		{OperationRelationPublish, 14, CapabilityRelationPublish},
		{OperationAuditAnalyze, 15, CapabilityAuditAnalyze},
		{OperationExposureAnalyze, 16, CapabilityAuditAnalyze},
		{OperationRemediationCommit, 17, CapabilityRotate},
	}
	for _, test := range tests {
		if uint16(test.operation) != test.value || !test.operation.Valid() {
			t.Fatalf("operation %d does not match frozen registry", test.value)
		}
		capability, err := test.operation.RequiredCapability()
		if err != nil || capability != test.capability {
			t.Fatalf("operation %d capability = %d, %v; want %d", test.value, capability, err, test.capability)
		}
	}

	allCapabilities := CapabilityRead |
		CapabilityAutofill |
		CapabilityPublishAudit |
		CapabilityCreate |
		CapabilityUpdate |
		CapabilityRotate |
		CapabilityMigrate |
		CapabilityRevoke |
		CapabilityDeviceEnroll |
		CapabilityRelationPublish |
		CapabilityAuditAnalyze
	if !allCapabilities.Valid() {
		t.Fatal("registered capability set is invalid")
	}
	for _, capability := range []Capability{
		CapabilityRead,
		CapabilityAutofill,
		CapabilityPublishAudit,
		CapabilityCreate,
		CapabilityUpdate,
		CapabilityRotate,
		CapabilityMigrate,
		CapabilityRevoke,
		CapabilityDeviceEnroll,
		CapabilityRelationPublish,
		CapabilityAuditAnalyze,
	} {
		if !allCapabilities.Allows(capability) {
			t.Fatalf("capability set does not allow bit %#x", capability)
		}
	}
	for value := EvidenceAutofillObserved; value <= EvidenceUserSignedConfirmation; value++ {
		if !value.Valid() {
			t.Fatalf("registered evidence %d is invalid", value)
		}
	}
	for value := RiskCurrentDirect; value <= RiskUnaffected; value++ {
		if !value.Valid() {
			t.Fatalf("registered risk %d is invalid", value)
		}
	}
	for value := CheckpointIdentity; value <= CheckpointVRF; value++ {
		if !value.Valid() {
			t.Fatalf("registered checkpoint %d is invalid", value)
		}
	}
	for value := ScopeNamespaceAll; value <= ScopeSingleCredential; value++ {
		if !value.Valid() {
			t.Fatalf("registered credential scope %d is invalid", value)
		}
	}
}

func TestFrozenRegistryRejectsZeroAndUnknown(t *testing.T) {
	t.Parallel()
	if OperationType(0).Valid() || OperationType(18).Valid() {
		t.Fatal("unregistered operation accepted")
	}
	if _, err := OperationType(0).RequiredCapability(); err == nil {
		t.Fatal("unregistered operation received a capability")
	}
	if Capability(0).Valid() || Capability(1<<11).Valid() ||
		(CapabilityRead | Capability(1<<15)).Valid() ||
		EvidenceLevel(6).Valid() ||
		RiskClass(0).Valid() || RiskClass(6).Valid() ||
		CheckpointType(0).Valid() || CheckpointType(9).Valid() ||
		CredentialScopeType(0).Valid() || CredentialScopeType(5).Valid() {
		t.Fatal("zero or unregistered registry value accepted")
	}
}

func TestOperationDatabaseProjectionRoundTrip(t *testing.T) {
	t.Parallel()
	for operation := OperationCreate; operation <= OperationRemediationCommit; operation++ {
		name, err := operation.DatabaseName()
		if err != nil {
			t.Fatalf("DatabaseName(%d): %v", operation, err)
		}
		parsed, err := ParseOperationDatabaseName(name)
		if err != nil || parsed != operation {
			t.Fatalf("ParseOperationDatabaseName(%q) = %d, %v; want %d", name, parsed, err, operation)
		}
	}
	if _, err := OperationType(0).DatabaseName(); err == nil {
		t.Fatal("invalid operation received a database name")
	}
	for _, invalid := range []string{"use_observed", "ROTATION_PREPARE", "KEY_GENERATION_ROTATE"} {
		if _, err := ParseOperationDatabaseName(invalid); err == nil {
			t.Fatalf("non-v2 operation spelling %q was accepted", invalid)
		}
	}
}

func TestEvidenceActivationPolicy(t *testing.T) {
	t.Parallel()
	if EvidenceAutofillObserved.ActivatesCredential() ||
		EvidenceSubmitObserved.ActivatesCredential() ||
		EvidencePageSuccessIndicated.ActivatesCredential() ||
		EvidenceNewPasswordReloginConfirmed.ActivatesCredential() {
		t.Fatal("weak browser evidence activated a credential version")
	}
	if !EvidenceUserSignedConfirmation.ActivatesCredential() ||
		!EvidenceSiteSignedReceipt.ActivatesCredential() {
		t.Fatal("confirmation evidence did not activate a credential version")
	}
	if EvidenceNewPasswordReloginConfirmed.CanActivateCredential(
		EvidenceActivationPolicy{},
	) || !EvidenceNewPasswordReloginConfirmed.CanActivateCredential(
		EvidenceActivationPolicy{AllowStrictRelogin: true},
	) {
		t.Fatal("E3 strict-relogin policy was not enforced")
	}
	if EvidenceSiteSignedReceipt.CanActivateCredential(
		EvidenceActivationPolicy{},
	) || !EvidenceSiteSignedReceipt.CanActivateCredential(
		EvidenceActivationPolicy{TrustedSiteConnector: true},
	) {
		t.Fatal("E4 trusted connector policy was not enforced")
	}
	if EvidenceUserSignedConfirmation.CanActivateCredential(
		EvidenceActivationPolicy{},
	) || !EvidenceUserSignedConfirmation.CanActivateCredential(
		EvidenceActivationPolicy{AllowUserConfirmation: true},
	) {
		t.Fatal("E5 user policy was not enforced")
	}
	names := []string{
		"AUTOFILL_OBSERVED", "SUBMIT_OBSERVED", "PAGE_SUCCESS_INDICATED",
		"NEW_PASSWORD_RELOGIN_CONFIRMED", "SITE_SIGNED_RECEIPT",
		"USER_SIGNED_CONFIRMATION",
	}
	for value, name := range names {
		evidence := EvidenceLevel(value)
		got, err := evidence.DatabaseName()
		if err != nil || got != name {
			t.Fatalf("evidence %d name=%q err=%v", value, got, err)
		}
		parsed, err := ParseEvidenceDatabaseName(name)
		if err != nil || parsed != evidence {
			t.Fatalf("parse evidence %q=%d err=%v", name, parsed, err)
		}
	}
}

func TestLifecycleStatusRegistry(t *testing.T) {
	t.Parallel()
	names := []string{
		"ACTIVE",
		"UPDATE_PENDING",
		"SITE_CONFIRM_PENDING",
		"SUSPENDED",
		"SUPERSEDED",
		"REVOKED",
		"CONFLICTED",
	}
	for index, name := range names {
		status := LifecycleStatus(index + 1)
		if !status.Valid() {
			t.Fatalf("status %d is not valid", status)
		}
		got, err := status.DatabaseName()
		if err != nil || got != name {
			t.Fatalf("status %d name = %q, %v", status, got, err)
		}
		parsed, err := ParseLifecycleDatabaseName(name)
		if err != nil || parsed != status {
			t.Fatalf("parse %q = %d, %v", name, parsed, err)
		}
	}
	if LifecycleStatus(0).Valid() || LifecycleStatus(8).Valid() {
		t.Fatal("unknown lifecycle status accepted")
	}
	if _, err := ParseLifecycleDatabaseName("ACTIVE_LOCAL"); err == nil {
		t.Fatal("unknown lifecycle projection accepted")
	}
}

func TestVerdictRegistry(t *testing.T) {
	t.Parallel()
	names := []string{
		"ACCEPT", "DEGRADED_OFFLINE", "DEGRADED_PENDING_LOG",
		"REVIEW_REQUIRED", "REJECT_IDENTITY", "REJECT_CAPABILITY",
		"REJECT_REVOKED", "REJECT_CAUSAL", "REJECT_PROOF",
		"REJECT_ORIGIN", "REJECT_POLICY", "REJECT_OBJECT",
	}
	for index, name := range names {
		verdict := Verdict(index + 1)
		if !verdict.Valid() {
			t.Fatalf("verdict %d invalid", verdict)
		}
		got, err := verdict.DatabaseName()
		if err != nil || got != name {
			t.Fatalf("verdict %d name = %q, %v", verdict, got, err)
		}
		wantAccepted := index < 3
		if verdict.Accepted() != wantAccepted {
			t.Fatalf("verdict %d accepted = %v", verdict, verdict.Accepted())
		}
	}
	if Verdict(0).Valid() || Verdict(13).Valid() {
		t.Fatal("unknown verdict accepted")
	}
}
