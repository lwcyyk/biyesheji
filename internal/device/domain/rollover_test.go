package domain

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"testing"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

func TestGenerationRolloverEncryptsOnlyForRemainingActiveDevices(t *testing.T) {
	t.Parallel()
	var namespaceID protocol.NamespaceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x11}, len(namespaceID)))
	devices := make([]RolloverDevice, 4)
	privateKeys := make(map[protocol.DeviceID]*cryptokit.HPKEPrivateKey)
	for index := range devices {
		copy(devices[index].DeviceID[:], bytes.Repeat(
			[]byte{byte(index + 1)}, len(devices[index].DeviceID),
		))
		publicKey, privateKey, err := cryptokit.GenerateHPKEKeyPair()
		if err != nil {
			t.Fatal(err)
		}
		privateKeys[devices[index].DeviceID] = privateKey
		t.Cleanup(privateKey.Destroy)
		devices[index].HPKEPublicKey = publicKey
		devices[index].Status = DeviceActive
	}
	revokedID := devices[2].DeviceID
	devices[2].Status = DeviceRevoked
	devices[3].Status = DeviceSuspended
	rollover, err := NewGenerationRollover(
		namespaceID, 4, revokedID, devices,
	)
	if err != nil {
		t.Fatal(err)
	}
	recipients := rollover.Recipients()
	if len(recipients) != 2 {
		t.Fatalf("recipient count=%d", len(recipients))
	}
	generationSecret, err := cryptokit.NewSecret(
		bytes.Repeat([]byte{0xa5}, cryptokit.KeySize),
	)
	if err != nil {
		t.Fatal(err)
	}
	defer generationSecret.Destroy()
	for index, recipient := range recipients {
		envelopeID, err := cryptokit.GenerateEnvelopeID()
		if err != nil {
			t.Fatal(err)
		}
		info := cryptokit.NewHPKEInfo(
			namespaceID, recipient.DeviceID, recipient.HPKEPublicKey,
			rollover.NewGeneration(), uint64(20+index),
			cryptokit.HPKEPurposeSecretGeneration,
			protocol.ObjectTypeSecretEnvelope, envelopeID,
		)
		envelope, err := cryptokit.SealHPKE(
			recipient.HPKEPublicKey, info, generationSecret,
		)
		if err != nil {
			t.Fatal(err)
		}
		encoded, err := envelope.MarshalBinary()
		if err != nil {
			t.Fatal(err)
		}
		if err := rollover.AttachEnvelope(
			recipient.DeviceID, sha256.Sum256(encoded),
		); err != nil {
			t.Fatal(err)
		}
		opened, err := cryptokit.OpenHPKE(
			privateKeys[recipient.DeviceID], info, envelope,
		)
		if err != nil {
			t.Fatal(err)
		}
		equal, err := cryptokit.SecretsEqual(generationSecret, opened)
		opened.Destroy()
		if err != nil || !equal {
			t.Fatal("recipient could not recover generation secret")
		}
	}
	if rollover.Status() != RolloverEnvelopesCreated {
		t.Fatalf("status=%d", rollover.Status())
	}
	if err := rollover.AttachEnvelope(
		revokedID, sha256.Sum256([]byte("forbidden")),
	); !errors.Is(err, ErrRolloverTransition) {
		t.Fatalf("revoked recipient error=%v", err)
	}
	if err := rollover.AcceptFinalSequence(42); err != nil {
		t.Fatal(err)
	}
	if err := rollover.Activate(); err != nil {
		t.Fatal(err)
	}
	if rollover.Status() != RolloverActive {
		t.Fatal("rollover did not activate")
	}
}

func TestGenerationRolloverRequiresRevokedTargetAndUniqueDevices(t *testing.T) {
	t.Parallel()
	namespaceID, deviceID := enrollmentIDs()
	publicKey, privateKey, err := cryptokit.GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	defer privateKey.Destroy()
	devices := []RolloverDevice{
		{DeviceID: deviceID, HPKEPublicKey: publicKey, Status: DeviceActive},
		{DeviceID: deviceID, HPKEPublicKey: publicKey, Status: DeviceRevoked},
	}
	if _, err := NewGenerationRollover(
		namespaceID, 1, deviceID, devices,
	); !errors.Is(err, ErrRolloverRecipient) {
		t.Fatalf("duplicate device error=%v", err)
	}
}
