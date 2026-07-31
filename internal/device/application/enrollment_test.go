package application

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"sync"
	"testing"

	"vdns.local/vdns/internal/cryptokit"
	devicedomain "vdns.local/vdns/internal/device/domain"
	"vdns.local/vdns/internal/protocol"
)

func TestEnrollmentCoordinatorRequiresPairingAndRejectsConsumeReplay(t *testing.T) {
	t.Parallel()
	var namespaceID protocol.NamespaceID
	var newDeviceID protocol.DeviceID
	var approverID protocol.DeviceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x11}, len(namespaceID)))
	copy(newDeviceID[:], bytes.Repeat([]byte{0x22}, len(newDeviceID)))
	copy(approverID[:], bytes.Repeat([]byte{0x33}, len(approverID)))
	authPublic := ed25519.PublicKey(bytes.Repeat([]byte{0x44}, ed25519.PublicKeySize))
	hpkePublic, hpkePrivate, err := cryptokit.GenerateHPKEKeyPair()
	if err != nil {
		t.Fatal(err)
	}
	defer hpkePrivate.Destroy()
	challenge, code, err := devicedomain.NewEnrollmentChallenge(
		namespaceID, newDeviceID, authPublic, hpkePublic,
		protocol.CapabilityRead|protocol.CapabilityAutofill,
		sha256.Sum256([]byte("namespace-scope")), 100,
	)
	if err != nil {
		t.Fatal(err)
	}
	store := &memoryEnrollmentStore{}
	ports := &enrollmentPorts{}
	coordinator, err := NewEnrollmentCoordinator(
		store, ports, ports, ports, ports,
	)
	if err != nil {
		t.Fatal(err)
	}
	if err := coordinator.SaveChallenge(context.Background(), challenge); err != nil {
		t.Fatal(err)
	}
	challengeID := challenge.Snapshot().ChallengeID
	if err := coordinator.Approve(
		context.Background(), challengeID, "000000", approverID, 20,
	); !errors.Is(err, devicedomain.ErrPairingCodeMismatch) {
		t.Fatalf("wrong pairing code error=%v", err)
	}
	if ports.authorizeCalls != 0 || ports.sealCalls != 0 {
		t.Fatal("wrong pairing code invoked privileged ports")
	}
	if err := coordinator.Approve(
		context.Background(), challengeID, code, approverID, 20,
	); err != nil {
		t.Fatal(err)
	}
	approved, _ := store.Load(context.Background(), challengeID)
	if approved.Status != devicedomain.EnrollmentApproved ||
		approved.RootEnvelopeHash == nil ||
		approved.DeviceCredentialHash == nil ||
		ports.authorizeCalls != 1 || ports.issueCalls != 1 ||
		ports.sealCalls != 1 {
		t.Fatalf("approval did not persist all bindings: %+v", approved)
	}
	if err := coordinator.Consume(
		context.Background(), challengeID, 30,
	); err != nil {
		t.Fatal(err)
	}
	if ports.activateCalls != 1 {
		t.Fatal("new device was not activated")
	}
	if err := coordinator.Consume(
		context.Background(), challengeID, 31,
	); !errors.Is(err, devicedomain.ErrEnrollmentReplay) {
		t.Fatalf("consume replay error=%v", err)
	}
	if ports.activateCalls != 1 {
		t.Fatal("replay invoked activation again")
	}
}

type memoryEnrollmentStore struct {
	mu       sync.Mutex
	snapshot devicedomain.EnrollmentSnapshot
	created  bool
}

func (store *memoryEnrollmentStore) Create(
	_ context.Context,
	snapshot devicedomain.EnrollmentSnapshot,
) error {
	store.mu.Lock()
	defer store.mu.Unlock()
	if store.created || snapshot.Status != devicedomain.EnrollmentIssued {
		return ErrEnrollmentCoordination
	}
	store.snapshot = snapshot
	store.created = true
	return nil
}

func (store *memoryEnrollmentStore) Load(
	_ context.Context,
	challengeID devicedomain.ChallengeID,
) (devicedomain.EnrollmentSnapshot, error) {
	store.mu.Lock()
	defer store.mu.Unlock()
	if !store.created || store.snapshot.ChallengeID != challengeID {
		return devicedomain.EnrollmentSnapshot{}, ErrEnrollmentCoordination
	}
	return store.snapshot, nil
}

func (store *memoryEnrollmentStore) CompareAndSwap(
	_ context.Context,
	snapshot devicedomain.EnrollmentSnapshot,
	expected devicedomain.EnrollmentStatus,
) error {
	store.mu.Lock()
	defer store.mu.Unlock()
	if !store.created || store.snapshot.Status != expected ||
		store.snapshot.ChallengeID != snapshot.ChallengeID {
		return ErrEnrollmentCoordination
	}
	store.snapshot = snapshot
	return nil
}

type enrollmentPorts struct {
	authorizeCalls int
	issueCalls     int
	sealCalls      int
	activateCalls  int
}

func (ports *enrollmentPorts) AuthorizeEnrollment(
	_ context.Context,
	snapshot devicedomain.EnrollmentSnapshot,
	_ protocol.DeviceID,
	_ uint64,
) (protocol.EventID, error) {
	ports.authorizeCalls++
	var eventID protocol.EventID
	copy(eventID[:], snapshot.ChallengeID[:])
	eventID[0] ^= 0x11
	return eventID, nil
}

func (ports *enrollmentPorts) IssueDeviceCredential(
	_ context.Context,
	snapshot devicedomain.EnrollmentSnapshot,
	_ uint64,
) ([sha256.Size]byte, error) {
	ports.issueCalls++
	return sha256.Sum256(append(
		[]byte("credential"), snapshot.ChallengeID[:]...,
	)), nil
}

func (ports *enrollmentPorts) SealRootBundle(
	_ context.Context,
	snapshot devicedomain.EnrollmentSnapshot,
	_ uint64,
) ([sha256.Size]byte, error) {
	ports.sealCalls++
	return sha256.Sum256(append(
		[]byte("envelope"), snapshot.ChallengeID[:]...,
	)), nil
}

func (ports *enrollmentPorts) ActivateNewDevice(
	_ context.Context,
	_ devicedomain.EnrollmentSnapshot,
	_ uint64,
) error {
	ports.activateCalls++
	return nil
}
