package mocksite

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"testing"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
	site "vpass.local/vpass/internal/site/domain"
)

func TestMockSiteScenariosAndRepeatableReceipts(t *testing.T) {
	t.Parallel()
	scenarios := []struct {
		name        string
		behavior    Behavior
		withMFA     bool
		wantStatus  site.ReceiptStatus
		wantError   error
		wantVersion uint64
	}{
		{"success", BehaviorSuccess, false, site.ReceiptApplied, nil, 2},
		{"rejected", BehaviorRejected, false, site.ReceiptNotApplied, nil, 1},
		{"mfa missing", BehaviorMFARequired, false, site.ReceiptMFARequired, nil, 1},
		{"mfa success", BehaviorMFARequired, true, site.ReceiptApplied, nil, 2},
		{"policy", BehaviorPolicyRejected, false, site.ReceiptRejectedPolicy, nil, 1},
		{"timeout unknown", BehaviorTimeoutUnknown, false, site.ReceiptUnknown, site.ErrSiteTimeout, 1},
		{"response lost", BehaviorResponseLostAfterApply, false, site.ReceiptApplied, site.ErrSiteResponseLost, 2},
	}
	for index, scenario := range scenarios {
		scenario := scenario
		t.Run(scenario.name, func(t *testing.T) {
			t.Parallel()
			connector, credentialID, current, replacement, mfa, request := mockFixture(
				t, scenario.behavior, byte(index+1),
			)
			defer connector.Close()
			defer current.Destroy()
			defer replacement.Destroy()
			defer mfa.Destroy()
			if scenario.withMFA {
				request.MFAProof = mfa
			}
			receipt, err := connector.ChangePassword(context.Background(), request)
			if !errors.Is(err, scenario.wantError) {
				t.Fatalf("first error = %v, want %v", err, scenario.wantError)
			}
			if scenario.wantError != nil {
				if receipt != nil {
					t.Fatal("transport failure returned a receipt directly")
				}
				receipt, err = connector.QueryReceipt(
					context.Background(), request.ChangeID, credentialID,
				)
				if err != nil {
					t.Fatal(err)
				}
			}
			if receipt.Payload().Status != scenario.wantStatus {
				t.Fatalf("receipt status = %d", receipt.Payload().Status)
			}
			verified, err := site.ParseAndVerifyReceipt(
				receipt.Encoded(), receipt.Signature(),
				connector.ReceiptPublicKey(), request.ChangeID, credentialID,
			)
			if err != nil || verified.Digest() != receipt.Digest() {
				t.Fatalf("receipt verification = %v", err)
			}
			version, _ := connector.CurrentVersion(credentialID)
			if version != scenario.wantVersion {
				t.Fatalf("site version = %d, want %d", version, scenario.wantVersion)
			}
			repeated, err := connector.ChangePassword(
				context.Background(), request,
			)
			if err != nil || repeated.Digest() != receipt.Digest() {
				t.Fatalf("repeat = %v, %v", repeated, err)
			}
			matchesReplacement, _ := connector.PasswordMatches(
				credentialID, replacement,
			)
			if matchesReplacement != (scenario.wantVersion == 2) {
				t.Fatal("site password does not match receipt outcome")
			}
		})
	}
}

func TestMockSiteRejectsIdempotencyConflictAndBadCurrentPassword(t *testing.T) {
	t.Parallel()
	connector, _, current, replacement, mfa, request := mockFixture(
		t, BehaviorSuccess, 0x41,
	)
	defer connector.Close()
	defer current.Destroy()
	defer replacement.Destroy()
	defer mfa.Destroy()
	if _, err := connector.ChangePassword(context.Background(), request); err != nil {
		t.Fatal(err)
	}
	different, _ := cryptokit.NewSecret([]byte("different-new-password"))
	defer different.Destroy()
	conflict := request
	conflict.NewPassword = different
	if _, err := connector.ChangePassword(
		context.Background(), conflict,
	); !errors.Is(err, site.ErrSiteChangeConflict) {
		t.Fatalf("idempotency conflict error = %v", err)
	}

	connector2, _, current2, replacement2, mfa2, request2 := mockFixture(
		t, BehaviorSuccess, 0x42,
	)
	defer connector2.Close()
	defer current2.Destroy()
	defer replacement2.Destroy()
	defer mfa2.Destroy()
	wrong, _ := cryptokit.NewSecret([]byte("wrong-current"))
	defer wrong.Destroy()
	request2.CurrentPassword = wrong
	if _, err := connector2.ChangePassword(
		context.Background(), request2,
	); !errors.Is(err, ErrMockCredential) {
		t.Fatalf("wrong current password error = %v", err)
	}
}

func TestSiteReceiptTamperFailsClosed(t *testing.T) {
	t.Parallel()
	connector, credentialID, current, replacement, mfa, request := mockFixture(
		t, BehaviorSuccess, 0x51,
	)
	defer connector.Close()
	defer current.Destroy()
	defer replacement.Destroy()
	defer mfa.Destroy()
	receipt, err := connector.ChangePassword(context.Background(), request)
	if err != nil {
		t.Fatal(err)
	}
	encoded := receipt.Encoded()
	encoded[len(encoded)-1] ^= 1
	if _, err := site.ParseAndVerifyReceipt(
		encoded, receipt.Signature(), connector.ReceiptPublicKey(),
		request.ChangeID, credentialID,
	); !errors.Is(err, site.ErrSiteReceipt) {
		t.Fatalf("tampered receipt error = %v", err)
	}
}

func mockFixture(
	t *testing.T,
	behavior Behavior,
	marker byte,
) (*Connector, protocol.CredentialID, *cryptokit.Secret, *cryptokit.Secret, *cryptokit.Secret, site.ChangeRequest) {
	t.Helper()
	privateKey := ed25519.NewKeyFromSeed(
		bytes.Repeat([]byte{0x61}, ed25519.SeedSize),
	)
	policyHash := sha256.Sum256([]byte("required-policy"))
	mfa, _ := cryptokit.NewSecret([]byte("123456"))
	connector, err := New(Config{
		ReceiptPrivateKey: privateKey, Behavior: behavior,
		RequiredPolicyHash: policyHash, MFAProof: mfa,
	})
	if err != nil {
		t.Fatal(err)
	}
	var credentialID protocol.CredentialID
	copy(credentialID[:], bytes.Repeat([]byte{marker}, len(credentialID)))
	current, _ := cryptokit.NewSecret([]byte("current-password"))
	replacement, _ := cryptokit.NewSecret([]byte("replacement-password"))
	if err := connector.SeedCredential(credentialID, 1, current); err != nil {
		t.Fatal(err)
	}
	var changeID site.ChangeID
	copy(changeID[:], bytes.Repeat([]byte{marker + 1}, len(changeID)))
	return connector, credentialID, current, replacement, mfa, site.ChangeRequest{
		ChangeID: changeID, CredentialID: credentialID,
		ExpectedVersion: 1, NewVersion: 2, PolicyHash: policyHash,
		CurrentPassword: current, NewPassword: replacement,
	}
}
