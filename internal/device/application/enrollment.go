// Package application coordinates one-use device enrollment without exposing
// RootSecretBundle to general application code.
package application

import (
	"context"
	"crypto/sha256"
	"errors"

	devicedomain "vdns.local/vdns/internal/device/domain"
	"vdns.local/vdns/internal/protocol"
)

var ErrEnrollmentCoordination = errors.New("device enrollment coordination failed")

type EnrollmentStore interface {
	Create(context.Context, devicedomain.EnrollmentSnapshot) error
	Load(context.Context, devicedomain.ChallengeID) (devicedomain.EnrollmentSnapshot, error)
	CompareAndSwap(
		context.Context,
		devicedomain.EnrollmentSnapshot,
		devicedomain.EnrollmentStatus,
	) error
}

// ApprovalAuthorizer persists a capability-checked signed DEVICE_ENROLL event.
type ApprovalAuthorizer interface {
	AuthorizeEnrollment(
		context.Context,
		devicedomain.EnrollmentSnapshot,
		protocol.DeviceID,
		uint64,
	) (protocol.EventID, error)
}

// DeviceCredentialIssuer creates and durably stores the root-signed operation
// credential requested by the challenge.
type DeviceCredentialIssuer interface {
	IssueDeviceCredential(
		context.Context,
		devicedomain.EnrollmentSnapshot,
		uint64,
	) ([sha256.Size]byte, error)
}

// RootBundleSealer seals the root bundle to the new device HPKE key and stores
// the immutable SecretEnvelope before returning its content hash.
type RootBundleSealer interface {
	SealRootBundle(
		context.Context,
		devicedomain.EnrollmentSnapshot,
		uint64,
	) ([sha256.Size]byte, error)
}

// NewDeviceActivator opens the HPKE envelope inside a secure key owner,
// creates a device-specific RootCapsule, and registers the new device.
type NewDeviceActivator interface {
	ActivateNewDevice(
		context.Context,
		devicedomain.EnrollmentSnapshot,
		uint64,
	) error
}

type EnrollmentCoordinator struct {
	store      EnrollmentStore
	authorizer ApprovalAuthorizer
	issuer     DeviceCredentialIssuer
	sealer     RootBundleSealer
	activator  NewDeviceActivator
}

func NewEnrollmentCoordinator(
	store EnrollmentStore,
	authorizer ApprovalAuthorizer,
	issuer DeviceCredentialIssuer,
	sealer RootBundleSealer,
	activator NewDeviceActivator,
) (*EnrollmentCoordinator, error) {
	if store == nil || authorizer == nil || issuer == nil ||
		sealer == nil || activator == nil {
		return nil, ErrEnrollmentCoordination
	}
	return &EnrollmentCoordinator{
		store: store, authorizer: authorizer, issuer: issuer,
		sealer: sealer, activator: activator,
	}, nil
}

func (coordinator *EnrollmentCoordinator) SaveChallenge(
	ctx context.Context,
	challenge *devicedomain.EnrollmentChallenge,
) error {
	if coordinator == nil || ctx == nil || challenge == nil ||
		challenge.Snapshot().Status != devicedomain.EnrollmentIssued {
		return ErrEnrollmentCoordination
	}
	return coordinator.store.Create(ctx, challenge.Snapshot())
}

func (coordinator *EnrollmentCoordinator) Approve(
	ctx context.Context,
	challengeID devicedomain.ChallengeID,
	pairingCode string,
	approver protocol.DeviceID,
	atSequence uint64,
) error {
	if coordinator == nil || ctx == nil || allZero(challengeID[:]) ||
		allZero(approver[:]) || atSequence == 0 {
		return ErrEnrollmentCoordination
	}
	snapshot, err := coordinator.store.Load(ctx, challengeID)
	if err != nil {
		return err
	}
	challenge, err := devicedomain.RestoreEnrollmentChallenge(snapshot)
	if err != nil {
		return errors.Join(ErrEnrollmentCoordination, err)
	}
	if snapshot.Status != devicedomain.EnrollmentIssued ||
		atSequence > snapshot.ExpiresAtSequence {
		return devicedomain.ErrEnrollmentExpired
	}
	if err := challenge.VerifyPairingCode(pairingCode); err != nil {
		return errors.Join(ErrEnrollmentCoordination, err)
	}
	eventID, err := coordinator.authorizer.AuthorizeEnrollment(
		ctx, snapshot, approver, atSequence,
	)
	if err != nil || allZero(eventID[:]) {
		return errors.Join(ErrEnrollmentCoordination, err)
	}
	credentialHash, err := coordinator.issuer.IssueDeviceCredential(
		ctx, snapshot, atSequence,
	)
	if err != nil || allZero(credentialHash[:]) {
		return errors.Join(ErrEnrollmentCoordination, err)
	}
	envelopeHash, err := coordinator.sealer.SealRootBundle(
		ctx, snapshot, atSequence,
	)
	if err != nil || allZero(envelopeHash[:]) {
		return errors.Join(ErrEnrollmentCoordination, err)
	}
	if err := challenge.Approve(
		atSequence, approver, eventID, envelopeHash, credentialHash,
	); err != nil {
		return err
	}
	return coordinator.store.CompareAndSwap(
		ctx, challenge.Snapshot(), devicedomain.EnrollmentIssued,
	)
}

func (coordinator *EnrollmentCoordinator) Consume(
	ctx context.Context,
	challengeID devicedomain.ChallengeID,
	atSequence uint64,
) error {
	if coordinator == nil || ctx == nil || allZero(challengeID[:]) ||
		atSequence == 0 {
		return ErrEnrollmentCoordination
	}
	snapshot, err := coordinator.store.Load(ctx, challengeID)
	if err != nil {
		return err
	}
	challenge, err := devicedomain.RestoreEnrollmentChallenge(snapshot)
	if err != nil {
		return err
	}
	if snapshot.Status == devicedomain.EnrollmentConsumed {
		return devicedomain.ErrEnrollmentReplay
	}
	if snapshot.Status != devicedomain.EnrollmentApproved ||
		atSequence > snapshot.ExpiresAtSequence {
		return devicedomain.ErrEnrollmentExpired
	}
	if err := coordinator.activator.ActivateNewDevice(
		ctx, snapshot, atSequence,
	); err != nil {
		return err
	}
	if err := challenge.Consume(atSequence); err != nil {
		return err
	}
	return coordinator.store.CompareAndSwap(
		ctx, challenge.Snapshot(), devicedomain.EnrollmentApproved,
	)
}

func allZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}
