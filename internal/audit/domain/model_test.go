package domain

import (
	"bytes"
	"encoding/json"
	"testing"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

func TestPrivateUseEventCanonicalRoundTripAndNoJSONWitness(t *testing.T) {
	event := PrivateUseEvent{
		FormatVersion: AuditPayloadVersion,
		CredentialID:  protocol.CredentialID{1}, CredentialVersion: 4,
		DeviceID:           protocol.DeviceID{2},
		EvidenceLevel:      protocol.EvidenceSubmitObserved,
		ObservedTimeBucket: 77, DescriptorDigest: [32]byte{3},
		ReuseWitness: cryptokit.ReuseTag{4},
	}
	encoded, err := MarshalPrivateUseEvent(event)
	if err != nil {
		t.Fatal(err)
	}
	parsed, err := ParsePrivateUseEvent(encoded)
	if err != nil || parsed != event {
		t.Fatalf("round trip = %+v, %v", parsed, err)
	}
	if bytes.Contains(encoded, []byte("password")) {
		t.Fatal("private event unexpectedly contained plaintext")
	}
	if _, err := json.Marshal(event.ReuseWitness); err == nil {
		t.Fatal("ReuseWitness entered ordinary JSON")
	}
	changed := append(append([]byte(nil), encoded...), 0)
	if _, err := ParsePrivateUseEvent(changed); err == nil {
		t.Fatal("non-canonical/mutated event accepted")
	}
}

func TestCanonicalFindingsMinimizedAndStable(t *testing.T) {
	first := Finding{
		Kind: RiskConflict, CredentialPseudonym: [32]byte{2},
		Confidence: ConfidenceStrong, EvidenceObjectDigests: [][32]byte{{8}, {9}},
		ObservedTimeBucket: 11, CurrentVersion: 2,
	}
	second := Finding{
		Kind: RiskPasswordReuse, CredentialPseudonym: [32]byte{1},
		RelatedPseudonyms: [][32]byte{{2}},
		Confidence:        ConfidenceMedium, EvidenceObjectDigests: [][32]byte{{7}},
		ObservedTimeBucket: 10, CurrentVersion: 1,
	}
	canonical, err := CanonicalFindings([]Finding{first, second})
	if err != nil {
		t.Fatal(err)
	}
	if canonical[0].CredentialPseudonym != second.CredentialPseudonym {
		t.Fatal("finding order is not deterministic")
	}
	encoded, err := json.Marshal(canonical)
	if err != nil {
		t.Fatal(err)
	}
	for _, forbidden := range [][]byte{
		[]byte("password"), []byte("secretHandle"), []byte("reuseWitness"),
		[]byte("credentialId"), []byte("deviceId"),
	} {
		if bytes.Contains(encoded, forbidden) {
			t.Fatalf("minimized result exposed %q", forbidden)
		}
	}
}

func FuzzParsePrivateUseEvent(f *testing.F) {
	seed, _ := MarshalPrivateUseEvent(PrivateUseEvent{
		FormatVersion: AuditPayloadVersion,
		CredentialID:  protocol.CredentialID{1}, CredentialVersion: 1,
		DeviceID:           protocol.DeviceID{2},
		EvidenceLevel:      protocol.EvidenceAutofillObserved,
		ObservedTimeBucket: 1, DescriptorDigest: [32]byte{3},
		ReuseWitness: cryptokit.ReuseTag{4},
	})
	f.Add(seed)
	f.Add([]byte{0xff})
	f.Fuzz(func(t *testing.T, encoded []byte) {
		if len(encoded) > cryptokit.MaxEventPlaintextSize {
			return
		}
		event, err := ParsePrivateUseEvent(encoded)
		if err != nil {
			return
		}
		canonical, err := MarshalPrivateUseEvent(event)
		if err != nil || !bytes.Equal(canonical, encoded) {
			t.Fatal("accepted private event was not canonical")
		}
	})
}
