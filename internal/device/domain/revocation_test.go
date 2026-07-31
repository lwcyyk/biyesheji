package domain

import (
	"testing"

	"vdns.local/vdns/internal/protocol"
)

func TestRevocationSeparatesControlIsolationAndExternalRepair(t *testing.T) {
	t.Parallel()
	revoked := deviceID(1)
	remaining := deviceID(2)
	first, second := credentialID(11), credentialID(12)
	plan, err := NewDeviceRevocationPlan(
		revoked, 1, []protocol.CredentialID{first, second},
	)
	if err != nil {
		t.Fatal(err)
	}
	if plan.OperationAllowed(revoked, 10) {
		t.Fatal("pending control-plane revocation accepted a new operation")
	}
	if err := plan.FinalizeControlPlane(10); err != nil {
		t.Fatal(err)
	}
	if !plan.OperationAllowed(revoked, 9) ||
		plan.OperationAllowed(revoked, 10) ||
		plan.OperationAllowed(revoked, 11) {
		t.Fatal("revocation final sequence was not enforced")
	}
	if err := plan.CompleteSecretIsolation(
		2, []protocol.DeviceID{remaining},
	); err != nil {
		t.Fatal(err)
	}
	if plan.CanReceiveGeneration(revoked, 2) ||
		!plan.CanReceiveGeneration(remaining, 2) {
		t.Fatal("new generation recipient boundary failed")
	}
	snapshot := plan.Snapshot()
	if len(snapshot.KnownCredentialSet) != 2 ||
		len(snapshot.FutureAccessBlockedSet) != 2 ||
		len(snapshot.RemediationRequiredSet) != 2 {
		t.Fatalf("revocation sets=%+v", snapshot)
	}
	// Revocation cannot make a previously known password stop working.
	if !plan.HistoricalCredentialMayStillWork(first) {
		t.Fatal("old password residual risk was hidden")
	}
	if err := plan.RecordRemediation(first, RemediationCompleted); err != nil {
		t.Fatal(err)
	}
	if plan.HistoricalCredentialMayStillWork(first) {
		t.Fatal("completed external remediation remained pending")
	}
	for _, status := range []RemediationStatus{
		RemediationPending, RemediationUnknown, RemediationFailed,
	} {
		if err := plan.RecordRemediation(second, status); err != nil {
			t.Fatal(err)
		}
		if !plan.HistoricalCredentialMayStillWork(second) {
			t.Fatalf("%s incorrectly removed the remediation obligation", status)
		}
	}
}

func TestRevokedDeviceCannotReceiveNewRoot(t *testing.T) {
	t.Parallel()
	revoked := deviceID(3)
	plan, _ := NewDeviceRevocationPlan(
		revoked, 4, []protocol.CredentialID{credentialID(21)},
	)
	_ = plan.FinalizeControlPlane(20)
	if err := plan.CompleteSecretIsolation(
		5, []protocol.DeviceID{revoked},
	); err == nil {
		t.Fatal("revoked device was included in new root recipients")
	}
	if plan.CanReceiveGeneration(revoked, 5) {
		t.Fatal("revoked device can request the new root")
	}
}

func deviceID(value byte) protocol.DeviceID {
	var result protocol.DeviceID
	for index := range result {
		result[index] = value
	}
	return result
}

func credentialID(value byte) protocol.CredentialID {
	var result protocol.CredentialID
	for index := range result {
		result[index] = value
	}
	return result
}
