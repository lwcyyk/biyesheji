// Package domain models out-of-band verified, one-use device enrollment.
package domain

import (
	"crypto/ed25519"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/binary"
	"errors"
	"fmt"
	"io"

	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

const PairingCodeDigits = 6

var (
	ErrInvalidEnrollment   = errors.New("invalid device enrollment")
	ErrEnrollmentExpired   = errors.New("device enrollment challenge expired")
	ErrEnrollmentReplay    = errors.New("device enrollment challenge was already consumed")
	ErrPairingCodeMismatch = errors.New("device enrollment pairing code mismatch")
)

type ChallengeID [sha256.Size]byte

type EnrollmentStatus uint8

const (
	EnrollmentIssued EnrollmentStatus = iota + 1
	EnrollmentApproved
	EnrollmentConsumed
	EnrollmentExpired
	EnrollmentRejected
)

func (status EnrollmentStatus) Valid() bool {
	return status >= EnrollmentIssued && status <= EnrollmentRejected
}

type EnrollmentChallenge struct {
	challengeID           ChallengeID
	namespaceID           protocol.NamespaceID
	nonce                 [sha256.Size]byte
	newDeviceID           protocol.DeviceID
	newAuthPublicKey      [ed25519.PublicKeySize]byte
	newHPKEPublicKey      cryptokit.HPKEPublicKey
	requestedCapabilities protocol.Capability
	requestedScopeDigest  [sha256.Size]byte
	expiresAtSequence     uint64
	shortCodeCommitment   [sha256.Size]byte
	status                EnrollmentStatus
	approvedByDeviceID    *protocol.DeviceID
	approvalEventID       *protocol.EventID
	rootEnvelopeHash      *[sha256.Size]byte
	deviceCredentialHash  *[sha256.Size]byte
	consumedAtSequence    *uint64
}

type EnrollmentSnapshot struct {
	ChallengeID           ChallengeID
	NamespaceID           protocol.NamespaceID
	Nonce                 [sha256.Size]byte
	NewDeviceID           protocol.DeviceID
	NewAuthPublicKey      [ed25519.PublicKeySize]byte
	NewHPKEPublicKey      cryptokit.HPKEPublicKey
	RequestedCapabilities protocol.Capability
	RequestedScopeDigest  [sha256.Size]byte
	ExpiresAtSequence     uint64
	ShortCodeCommitment   [sha256.Size]byte
	Status                EnrollmentStatus
	ApprovedByDeviceID    *protocol.DeviceID
	ApprovalEventID       *protocol.EventID
	RootEnvelopeHash      *[sha256.Size]byte
	DeviceCredentialHash  *[sha256.Size]byte
	ConsumedAtSequence    *uint64
}

type pairingProjection struct {
	Domain                string                      `cbor:"domain"`
	ChallengeID           ChallengeID                 `cbor:"challenge_id"`
	NamespaceID           protocol.NamespaceID        `cbor:"namespace_id"`
	Nonce                 [sha256.Size]byte           `cbor:"nonce"`
	NewDeviceID           protocol.DeviceID           `cbor:"new_device_id"`
	NewAuthPublicKey      [ed25519.PublicKeySize]byte `cbor:"new_auth_public_key"`
	NewHPKEPublicKey      cryptokit.HPKEPublicKey     `cbor:"new_hpke_public_key"`
	RequestedCapabilities protocol.Capability         `cbor:"requested_capabilities"`
	ScopeDigest           [sha256.Size]byte           `cbor:"scope_digest"`
	ExpiresAtSequence     uint64                      `cbor:"expires_at_sequence"`
}

func NewEnrollmentChallenge(
	namespaceID protocol.NamespaceID,
	newDeviceID protocol.DeviceID,
	newAuthPublicKey ed25519.PublicKey,
	newHPKEPublicKey cryptokit.HPKEPublicKey,
	requestedCapabilities protocol.Capability,
	requestedScopeDigest [sha256.Size]byte,
	expiresAtSequence uint64,
) (*EnrollmentChallenge, string, error) {
	return newEnrollmentChallengeWithReader(
		namespaceID, newDeviceID, newAuthPublicKey, newHPKEPublicKey,
		requestedCapabilities, requestedScopeDigest, expiresAtSequence, rand.Reader,
	)
}

func newEnrollmentChallengeWithReader(
	namespaceID protocol.NamespaceID,
	newDeviceID protocol.DeviceID,
	newAuthPublicKey ed25519.PublicKey,
	newHPKEPublicKey cryptokit.HPKEPublicKey,
	requestedCapabilities protocol.Capability,
	requestedScopeDigest [sha256.Size]byte,
	expiresAtSequence uint64,
	reader io.Reader,
) (*EnrollmentChallenge, string, error) {
	if allZero(namespaceID[:]) || allZero(newDeviceID[:]) ||
		len(newAuthPublicKey) != ed25519.PublicKeySize ||
		allZero(newAuthPublicKey) ||
		!requestedCapabilities.Valid() || allZero(requestedScopeDigest[:]) ||
		expiresAtSequence == 0 || reader == nil {
		return nil, "", ErrInvalidEnrollment
	}
	if _, err := cryptokit.ParseHPKEPublicKey(newHPKEPublicKey[:]); err != nil {
		return nil, "", ErrInvalidEnrollment
	}
	challenge := &EnrollmentChallenge{
		namespaceID: namespaceID, newDeviceID: newDeviceID,
		newHPKEPublicKey:      newHPKEPublicKey,
		requestedCapabilities: requestedCapabilities,
		requestedScopeDigest:  requestedScopeDigest,
		expiresAtSequence:     expiresAtSequence, status: EnrollmentIssued,
	}
	copy(challenge.newAuthPublicKey[:], newAuthPublicKey)
	if _, err := io.ReadFull(reader, challenge.challengeID[:]); err != nil ||
		allZero(challenge.challengeID[:]) {
		return nil, "", ErrInvalidEnrollment
	}
	if _, err := io.ReadFull(reader, challenge.nonce[:]); err != nil ||
		allZero(challenge.nonce[:]) {
		return nil, "", ErrInvalidEnrollment
	}
	code, commitment, err := pairingCodeAndCommitment(challenge)
	if err != nil {
		return nil, "", err
	}
	challenge.shortCodeCommitment = commitment
	return challenge, code, nil
}

func RestoreEnrollmentChallenge(
	snapshot EnrollmentSnapshot,
) (*EnrollmentChallenge, error) {
	challenge := &EnrollmentChallenge{
		challengeID: snapshot.ChallengeID,
		namespaceID: snapshot.NamespaceID, nonce: snapshot.Nonce,
		newDeviceID:           snapshot.NewDeviceID,
		newAuthPublicKey:      snapshot.NewAuthPublicKey,
		newHPKEPublicKey:      snapshot.NewHPKEPublicKey,
		requestedCapabilities: snapshot.RequestedCapabilities,
		requestedScopeDigest:  snapshot.RequestedScopeDigest,
		expiresAtSequence:     snapshot.ExpiresAtSequence,
		shortCodeCommitment:   snapshot.ShortCodeCommitment,
		status:                snapshot.Status,
		approvedByDeviceID:    cloneDeviceID(snapshot.ApprovedByDeviceID),
		approvalEventID:       cloneEventID(snapshot.ApprovalEventID),
		rootEnvelopeHash:      cloneHash(snapshot.RootEnvelopeHash),
		deviceCredentialHash:  cloneHash(snapshot.DeviceCredentialHash),
		consumedAtSequence:    cloneUint64(snapshot.ConsumedAtSequence),
	}
	if challenge.validate() != nil {
		return nil, ErrInvalidEnrollment
	}
	return challenge, nil
}

func (challenge *EnrollmentChallenge) VerifyPairingCode(code string) error {
	if challenge == nil || len(code) != PairingCodeDigits {
		return ErrPairingCodeMismatch
	}
	expected, commitment, err := pairingCodeAndCommitment(challenge)
	if err != nil ||
		subtle.ConstantTimeCompare([]byte(expected), []byte(code)) != 1 ||
		subtle.ConstantTimeCompare(
			commitment[:], challenge.shortCodeCommitment[:],
		) != 1 {
		return ErrPairingCodeMismatch
	}
	return nil
}

func (challenge *EnrollmentChallenge) Approve(
	atSequence uint64,
	approver protocol.DeviceID,
	approvalEventID protocol.EventID,
	rootEnvelopeHash [sha256.Size]byte,
	deviceCredentialHash [sha256.Size]byte,
) error {
	if challenge == nil || challenge.status != EnrollmentIssued ||
		atSequence == 0 || atSequence > challenge.expiresAtSequence ||
		allZero(approver[:]) || approver == challenge.newDeviceID ||
		allZero(approvalEventID[:]) || allZero(rootEnvelopeHash[:]) ||
		allZero(deviceCredentialHash[:]) {
		if challenge != nil && atSequence > challenge.expiresAtSequence {
			return ErrEnrollmentExpired
		}
		return ErrInvalidEnrollment
	}
	challenge.status = EnrollmentApproved
	challenge.approvedByDeviceID = &approver
	challenge.approvalEventID = &approvalEventID
	challenge.rootEnvelopeHash = &rootEnvelopeHash
	challenge.deviceCredentialHash = &deviceCredentialHash
	return challenge.validate()
}

func (challenge *EnrollmentChallenge) Consume(atSequence uint64) error {
	if challenge == nil {
		return ErrInvalidEnrollment
	}
	if challenge.status == EnrollmentConsumed {
		return ErrEnrollmentReplay
	}
	if challenge.status != EnrollmentApproved {
		return ErrInvalidEnrollment
	}
	if atSequence == 0 || atSequence > challenge.expiresAtSequence {
		return ErrEnrollmentExpired
	}
	challenge.status = EnrollmentConsumed
	challenge.consumedAtSequence = &atSequence
	return challenge.validate()
}

func (challenge *EnrollmentChallenge) Expire(atSequence uint64) error {
	if challenge == nil || atSequence <= challenge.expiresAtSequence ||
		(challenge.status != EnrollmentIssued &&
			challenge.status != EnrollmentApproved) {
		return ErrInvalidEnrollment
	}
	challenge.status = EnrollmentExpired
	return nil
}

func (challenge *EnrollmentChallenge) Reject() error {
	if challenge == nil || challenge.status != EnrollmentIssued {
		return ErrInvalidEnrollment
	}
	challenge.status = EnrollmentRejected
	return nil
}

func (challenge *EnrollmentChallenge) Snapshot() EnrollmentSnapshot {
	if challenge == nil {
		return EnrollmentSnapshot{}
	}
	return EnrollmentSnapshot{
		ChallengeID: challenge.challengeID,
		NamespaceID: challenge.namespaceID, Nonce: challenge.nonce,
		NewDeviceID:           challenge.newDeviceID,
		NewAuthPublicKey:      challenge.newAuthPublicKey,
		NewHPKEPublicKey:      challenge.newHPKEPublicKey,
		RequestedCapabilities: challenge.requestedCapabilities,
		RequestedScopeDigest:  challenge.requestedScopeDigest,
		ExpiresAtSequence:     challenge.expiresAtSequence,
		ShortCodeCommitment:   challenge.shortCodeCommitment,
		Status:                challenge.status,
		ApprovedByDeviceID:    cloneDeviceID(challenge.approvedByDeviceID),
		ApprovalEventID:       cloneEventID(challenge.approvalEventID),
		RootEnvelopeHash:      cloneHash(challenge.rootEnvelopeHash),
		DeviceCredentialHash:  cloneHash(challenge.deviceCredentialHash),
		ConsumedAtSequence:    cloneUint64(challenge.consumedAtSequence),
	}
}

func (challenge *EnrollmentChallenge) validate() error {
	if challenge == nil || allZero(challenge.challengeID[:]) ||
		allZero(challenge.namespaceID[:]) || allZero(challenge.nonce[:]) ||
		allZero(challenge.newDeviceID[:]) ||
		allZero(challenge.newAuthPublicKey[:]) ||
		!challenge.requestedCapabilities.Valid() ||
		allZero(challenge.requestedScopeDigest[:]) ||
		challenge.expiresAtSequence == 0 ||
		allZero(challenge.shortCodeCommitment[:]) || !challenge.status.Valid() {
		return ErrInvalidEnrollment
	}
	if _, err := cryptokit.ParseHPKEPublicKey(challenge.newHPKEPublicKey[:]); err != nil {
		return ErrInvalidEnrollment
	}
	switch challenge.status {
	case EnrollmentIssued:
		if challenge.approvedByDeviceID != nil ||
			challenge.approvalEventID != nil ||
			challenge.rootEnvelopeHash != nil ||
			challenge.deviceCredentialHash != nil ||
			challenge.consumedAtSequence != nil {
			return ErrInvalidEnrollment
		}
	case EnrollmentApproved:
		if challenge.approvedByDeviceID == nil ||
			challenge.approvalEventID == nil ||
			challenge.rootEnvelopeHash == nil ||
			challenge.deviceCredentialHash == nil ||
			challenge.consumedAtSequence != nil {
			return ErrInvalidEnrollment
		}
	case EnrollmentConsumed:
		if challenge.approvedByDeviceID == nil ||
			challenge.approvalEventID == nil ||
			challenge.rootEnvelopeHash == nil ||
			challenge.deviceCredentialHash == nil ||
			challenge.consumedAtSequence == nil {
			return ErrInvalidEnrollment
		}
	case EnrollmentExpired:
		if challenge.consumedAtSequence != nil {
			return ErrInvalidEnrollment
		}
	case EnrollmentRejected:
		if challenge.approvedByDeviceID != nil ||
			challenge.approvalEventID != nil ||
			challenge.rootEnvelopeHash != nil ||
			challenge.deviceCredentialHash != nil ||
			challenge.consumedAtSequence != nil {
			return ErrInvalidEnrollment
		}
	}
	return nil
}

func pairingCodeAndCommitment(
	challenge *EnrollmentChallenge,
) (string, [sha256.Size]byte, error) {
	if challenge == nil {
		return "", [sha256.Size]byte{}, ErrInvalidEnrollment
	}
	encoded, err := protocol.MarshalDeterministic(pairingProjection{
		Domain:      protocol.DomainPrefix + "DEVICE-ENROLL-PAIRING",
		ChallengeID: challenge.challengeID,
		NamespaceID: challenge.namespaceID, Nonce: challenge.nonce,
		NewDeviceID:           challenge.newDeviceID,
		NewAuthPublicKey:      challenge.newAuthPublicKey,
		NewHPKEPublicKey:      challenge.newHPKEPublicKey,
		RequestedCapabilities: challenge.requestedCapabilities,
		ScopeDigest:           challenge.requestedScopeDigest,
		ExpiresAtSequence:     challenge.expiresAtSequence,
	})
	if err != nil {
		return "", [sha256.Size]byte{}, ErrInvalidEnrollment
	}
	digest := sha256.Sum256(encoded)
	code := fmt.Sprintf("%06d", binary.BigEndian.Uint64(digest[:8])%1_000_000)
	hasher := sha256.New()
	_, _ = hasher.Write([]byte(protocol.DomainPrefix + "DEVICE-ENROLL-SHORT-CODE"))
	_, _ = hasher.Write(challenge.challengeID[:])
	_, _ = hasher.Write(challenge.nonce[:])
	_, _ = hasher.Write([]byte(code))
	var commitment [sha256.Size]byte
	copy(commitment[:], hasher.Sum(nil))
	return code, commitment, nil
}

func cloneHash(value *[sha256.Size]byte) *[sha256.Size]byte {
	if value == nil {
		return nil
	}
	copy := *value
	return &copy
}

func cloneDeviceID(value *protocol.DeviceID) *protocol.DeviceID {
	if value == nil {
		return nil
	}
	copy := *value
	return &copy
}

func cloneEventID(value *protocol.EventID) *protocol.EventID {
	if value == nil {
		return nil
	}
	copy := *value
	return &copy
}

func cloneUint64(value *uint64) *uint64 {
	if value == nil {
		return nil
	}
	copy := *value
	return &copy
}

func allZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}
