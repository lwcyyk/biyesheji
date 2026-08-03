package application

import (
	"context"
	"crypto/sha256"
	"errors"
	"testing"

	exposuredomain "vpass.local/vpass/internal/exposure/domain"
	exposureports "vpass.local/vpass/internal/exposure/ports"
	"vpass.local/vpass/internal/protocol"
)

type fixedProvider struct {
	result exposureports.Result
	err    error
}

func (provider fixedProvider) Analyze(
	_ context.Context,
	_ exposureports.Request,
) (exposureports.Result, error) {
	return provider.result, provider.err
}

func TestDisabledScopeZKReturnsStableOptionalBoundaryAndClearsWitness(t *testing.T) {
	snapshot := exposureSnapshot(t)
	witness := []byte("incident-password-witness")
	_, err := NewService(nil).Analyze(context.Background(), snapshot, witness)
	if !errors.Is(err, exposureports.ErrOptionalFeatureUnavailable) {
		t.Fatalf("disabled provider = %v", err)
	}
	for _, value := range witness {
		if value != 0 {
			t.Fatal("incident witness was not cleared")
		}
	}
}

func TestConfiguredProviderMustReturnSnapshotBoundProof(t *testing.T) {
	snapshot := exposureSnapshot(t)
	set, err := exposuredomain.NewAffectedSet(snapshot, []exposuredomain.AffectedItem{{
		CredentialID: snapshot.Entries[0].CredentialID, ReasonDigest: [32]byte{7},
	}})
	if err != nil {
		t.Fatal(err)
	}
	proof := []byte("research-provider-proof")
	service := NewService(fixedProvider{result: exposureports.Result{
		Affected: set, ProofBytes: proof, ProofDigest: sha256.Sum256(proof),
		System: exposureports.ProofSystemScopeZK,
	}})
	result, err := service.Analyze(context.Background(), snapshot, []byte("witness"))
	if err != nil || result.Affected.AffectedRoot != set.AffectedRoot {
		t.Fatalf("configured provider = %+v, %v", result, err)
	}

	other := exposureSnapshot(t)
	other.IncidentCommitment[0] ^= 1
	service = NewService(fixedProvider{result: exposureports.Result{
		Affected: set, ProofBytes: proof, ProofDigest: sha256.Sum256(proof),
		System: exposureports.ProofSystemScopeZK,
	}})
	if _, err := service.Analyze(context.Background(), other, []byte("witness")); err == nil {
		t.Fatal("provider result escaped snapshot binding")
	}
}

func exposureSnapshot(t *testing.T) exposuredomain.IncidentSnapshot {
	t.Helper()
	snapshot, err := exposuredomain.NewIncidentSnapshot(
		protocol.NamespaceID{1}, 10, 20, [32]byte{2}, [32]byte{3},
		[]exposuredomain.SnapshotEntry{{
			CredentialID: protocol.CredentialID{4}, CredentialVersion: 1,
			EventDigest: [32]byte{5}, Epoch: 1, ObservedBucket: 11,
		}},
	)
	if err != nil {
		t.Fatal(err)
	}
	return snapshot
}
