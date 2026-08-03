// Package domain defines the target-site password-change boundary. It contains
// no browser, HTTP or storage implementation.
package domain

import (
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"crypto/subtle"
	"errors"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

var (
	ErrInvalidSiteChange  = errors.New("invalid site password change")
	ErrSiteTimeout        = errors.New("site password change timed out")
	ErrSiteResponseLost   = errors.New("site password change response was lost")
	ErrSiteChangeConflict = errors.New("site change idempotency conflict")
	ErrSiteReceipt        = errors.New("site receipt verification failed")
)

type ChangeID [sha256.Size]byte

type ChangeRequest struct {
	ChangeID        ChangeID
	CredentialID    protocol.CredentialID
	ExpectedVersion uint64
	NewVersion      uint64
	PolicyHash      [sha256.Size]byte
	CurrentPassword *cryptokit.Secret
	NewPassword     *cryptokit.Secret
	MFAProof        *cryptokit.Secret
}

type changeRequestPublicProjection struct {
	Domain          string                `cbor:"domain"`
	ChangeID        ChangeID              `cbor:"change_id"`
	CredentialID    protocol.CredentialID `cbor:"credential_id"`
	ExpectedVersion uint64                `cbor:"expected_version"`
	NewVersion      uint64                `cbor:"new_version"`
	PolicyHash      [sha256.Size]byte     `cbor:"policy_hash"`
	HasMFAProof     bool                  `cbor:"has_mfa_proof"`
}

func (request ChangeRequest) Validate() error {
	if allZero(request.ChangeID[:]) || allZero(request.CredentialID[:]) ||
		request.ExpectedVersion == 0 ||
		request.NewVersion != request.ExpectedVersion+1 ||
		allZero(request.PolicyHash[:]) ||
		request.CurrentPassword == nil || request.CurrentPassword.Len() == 0 ||
		request.NewPassword == nil || request.NewPassword.Len() == 0 {
		return ErrInvalidSiteChange
	}
	return nil
}

// PublicDigest commits to idempotency-relevant public metadata without
// hashing either password. A low-entropy password hash must not become an
// offline guessing oracle in the local control database.
func (request ChangeRequest) PublicDigest() ([sha256.Size]byte, error) {
	if err := request.Validate(); err != nil {
		return [sha256.Size]byte{}, err
	}
	encoded, err := protocol.MarshalDeterministic(changeRequestPublicProjection{
		Domain:   protocol.DomainPrefix + "SITE-CHANGE-REQUEST",
		ChangeID: request.ChangeID, CredentialID: request.CredentialID,
		ExpectedVersion: request.ExpectedVersion, NewVersion: request.NewVersion,
		PolicyHash: request.PolicyHash, HasMFAProof: request.MFAProof != nil,
	})
	if err != nil {
		return [sha256.Size]byte{}, ErrInvalidSiteChange
	}
	return sha256.Sum256(encoded), nil
}

type ReceiptStatus uint8

const (
	ReceiptApplied ReceiptStatus = iota + 1
	ReceiptNotApplied
	ReceiptRejectedPolicy
	ReceiptMFARequired
	ReceiptUnknown
)

func (status ReceiptStatus) Valid() bool {
	return status >= ReceiptApplied && status <= ReceiptUnknown
}

type ReceiptPayload struct {
	Domain          string                `cbor:"domain"`
	ProtocolID      string                `cbor:"protocol_id"`
	ProtocolVersion uint64                `cbor:"protocol_version"`
	SuiteID         string                `cbor:"suite_id"`
	ChangeID        ChangeID              `cbor:"change_id"`
	CredentialID    protocol.CredentialID `cbor:"credential_id"`
	ExpectedVersion uint64                `cbor:"expected_version"`
	NewVersion      uint64                `cbor:"new_version"`
	Status          ReceiptStatus         `cbor:"status"`
	PolicyHash      [sha256.Size]byte     `cbor:"policy_hash"`
	SiteRevision    uint64                `cbor:"site_revision"`
}

type SignedReceipt struct {
	payload   ReceiptPayload
	encoded   []byte
	signature protocol.Signature
	digest    [sha256.Size]byte
}

func SignReceipt(
	privateKey ed25519.PrivateKey,
	payload ReceiptPayload,
) (*SignedReceipt, error) {
	if len(privateKey) != ed25519.PrivateKeySize ||
		validateReceiptPayload(payload) != nil {
		return nil, ErrInvalidSiteChange
	}
	encoded, err := protocol.MarshalDeterministic(payload)
	if err != nil {
		return nil, ErrInvalidSiteChange
	}
	raw := ed25519.Sign(privateKey, encoded)
	var signature protocol.Signature
	copy(signature[:], raw)
	return buildSignedReceipt(payload, encoded, signature), nil
}

func ParseAndVerifyReceipt(
	encoded []byte,
	signature protocol.Signature,
	publicKey ed25519.PublicKey,
	expectedChangeID ChangeID,
	expectedCredentialID protocol.CredentialID,
) (*SignedReceipt, error) {
	var payload ReceiptPayload
	if err := protocol.UnmarshalDeterministic(encoded, &payload); err != nil ||
		validateReceiptPayload(payload) != nil {
		return nil, ErrSiteReceipt
	}
	if payload.ChangeID != expectedChangeID ||
		payload.CredentialID != expectedCredentialID ||
		len(publicKey) != ed25519.PublicKeySize ||
		!ed25519.Verify(publicKey, encoded, signature[:]) {
		return nil, ErrSiteReceipt
	}
	canonical, err := protocol.MarshalDeterministic(payload)
	if err != nil || subtle.ConstantTimeCompare(canonical, encoded) != 1 {
		return nil, ErrSiteReceipt
	}
	return buildSignedReceipt(payload, canonical, signature), nil
}

func buildSignedReceipt(
	payload ReceiptPayload,
	encoded []byte,
	signature protocol.Signature,
) *SignedReceipt {
	hasher := sha256.New()
	_, _ = hasher.Write(encoded)
	_, _ = hasher.Write(signature[:])
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	return &SignedReceipt{
		payload: payload, encoded: append([]byte(nil), encoded...),
		signature: signature, digest: digest,
	}
}

func validateReceiptPayload(payload ReceiptPayload) error {
	if payload.Domain != protocol.DomainPrefix+"SITE-RECEIPT" ||
		payload.ProtocolID != protocol.ProtocolID ||
		payload.ProtocolVersion != protocol.ProtocolVersion ||
		payload.SuiteID != protocol.SuiteID ||
		allZero(payload.ChangeID[:]) || allZero(payload.CredentialID[:]) ||
		payload.ExpectedVersion == 0 ||
		payload.NewVersion != payload.ExpectedVersion+1 ||
		!payload.Status.Valid() || allZero(payload.PolicyHash[:]) ||
		payload.SiteRevision == 0 {
		return ErrInvalidSiteChange
	}
	return nil
}

func NewReceiptPayload(
	request ChangeRequest,
	status ReceiptStatus,
	policyHash [sha256.Size]byte,
	siteRevision uint64,
) ReceiptPayload {
	return ReceiptPayload{
		Domain:     protocol.DomainPrefix + "SITE-RECEIPT",
		ProtocolID: protocol.ProtocolID, ProtocolVersion: protocol.ProtocolVersion,
		SuiteID: protocol.SuiteID, ChangeID: request.ChangeID,
		CredentialID:    request.CredentialID,
		ExpectedVersion: request.ExpectedVersion, NewVersion: request.NewVersion,
		Status: status, PolicyHash: policyHash, SiteRevision: siteRevision,
	}
}

func (receipt *SignedReceipt) Payload() ReceiptPayload {
	if receipt == nil {
		return ReceiptPayload{}
	}
	return receipt.payload
}

func (receipt *SignedReceipt) Encoded() []byte {
	if receipt == nil {
		return nil
	}
	return append([]byte(nil), receipt.encoded...)
}

func (receipt *SignedReceipt) Signature() protocol.Signature {
	if receipt == nil {
		return protocol.Signature{}
	}
	return receipt.signature
}

func (receipt *SignedReceipt) Digest() [sha256.Size]byte {
	if receipt == nil {
		return [sha256.Size]byte{}
	}
	return receipt.digest
}

type Connector interface {
	ChangePassword(context.Context, ChangeRequest) (*SignedReceipt, error)
	QueryReceipt(context.Context, ChangeID, protocol.CredentialID) (*SignedReceipt, error)
	ReceiptPublicKey() ed25519.PublicKey
	TrustKind() ConnectorTrustKind
}

type ConnectorTrustKind string

const (
	ConnectorMockSite        ConnectorTrustKind = "MOCK_SITE_E4"
	ConnectorTrustedSite     ConnectorTrustKind = "TRUSTED_SITE_E4"
	ConnectorBrowserObserved ConnectorTrustKind = "BROWSER_OBSERVATION"
)

func allZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}
