package mocksite

import (
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"sync"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
	site "vpass.local/vpass/internal/site/domain"
)

var (
	ErrInvalidMockSite = errors.New("invalid mock site configuration")
	ErrMockCredential  = errors.New("mock site credential mismatch")
)

type Behavior uint8

const (
	BehaviorSuccess Behavior = iota + 1
	BehaviorRejected
	BehaviorMFARequired
	BehaviorPolicyRejected
	BehaviorTimeoutUnknown
	BehaviorResponseLostAfterApply
)

func (behavior Behavior) valid() bool {
	return behavior >= BehaviorSuccess &&
		behavior <= BehaviorResponseLostAfterApply
}

type Config struct {
	ReceiptPrivateKey  ed25519.PrivateKey
	Behavior           Behavior
	RequiredPolicyHash [sha256.Size]byte
	MFAProof           *cryptokit.Secret
}

type credentialState struct {
	version  uint64
	password *cryptokit.Secret
	revision uint64
}

type changeRecord struct {
	credentialID protocol.CredentialID
	expected     uint64
	next         uint64
	policyHash   [sha256.Size]byte
	current      *cryptokit.Secret
	replacement  *cryptokit.Secret
	hadMFA       bool
	receipt      *site.SignedReceipt
	firstError   error
}

type Connector struct {
	mu             sync.Mutex
	privateKey     ed25519.PrivateKey
	publicKey      ed25519.PublicKey
	behavior       Behavior
	requiredPolicy [sha256.Size]byte
	mfaProof       *cryptokit.Secret
	credentials    map[protocol.CredentialID]*credentialState
	changes        map[site.ChangeID]*changeRecord
	closed         bool
}

// TrustKind prevents the research fixture signature from being presented as a
// real site's cryptographic receipt.
func (connector *Connector) TrustKind() site.ConnectorTrustKind {
	return site.ConnectorMockSite
}

func New(config Config) (*Connector, error) {
	if len(config.ReceiptPrivateKey) != ed25519.PrivateKeySize ||
		!config.Behavior.valid() ||
		allZero(config.RequiredPolicyHash[:]) {
		return nil, ErrInvalidMockSite
	}
	var mfa *cryptokit.Secret
	var err error
	if config.MFAProof != nil {
		mfa, err = config.MFAProof.Clone()
		if err != nil {
			return nil, ErrInvalidMockSite
		}
	}
	privateKey := append(ed25519.PrivateKey(nil), config.ReceiptPrivateKey...)
	publicKey := append(ed25519.PublicKey(nil), privateKey.Public().(ed25519.PublicKey)...)
	return &Connector{
		privateKey: privateKey, publicKey: publicKey,
		behavior: config.Behavior, requiredPolicy: config.RequiredPolicyHash,
		mfaProof:    mfa,
		credentials: make(map[protocol.CredentialID]*credentialState),
		changes:     make(map[site.ChangeID]*changeRecord),
	}, nil
}

func (connector *Connector) SetBehavior(behavior Behavior) error {
	if connector == nil || !behavior.valid() {
		return ErrInvalidMockSite
	}
	connector.mu.Lock()
	defer connector.mu.Unlock()
	if connector.closed {
		return ErrInvalidMockSite
	}
	connector.behavior = behavior
	return nil
}

func (connector *Connector) SeedCredential(
	credentialID protocol.CredentialID,
	version uint64,
	password *cryptokit.Secret,
) error {
	if connector == nil || allZero(credentialID[:]) || version == 0 ||
		password == nil || password.Len() == 0 {
		return ErrInvalidMockSite
	}
	cloned, err := password.Clone()
	if err != nil {
		return ErrInvalidMockSite
	}
	connector.mu.Lock()
	defer connector.mu.Unlock()
	if connector.closed {
		cloned.Destroy()
		return ErrInvalidMockSite
	}
	if existing := connector.credentials[credentialID]; existing != nil {
		existing.password.Destroy()
	}
	connector.credentials[credentialID] = &credentialState{
		version: version, password: cloned, revision: 1,
	}
	return nil
}

func (connector *Connector) ChangePassword(
	ctx context.Context,
	request site.ChangeRequest,
) (*site.SignedReceipt, error) {
	if connector == nil || ctx == nil || request.Validate() != nil {
		return nil, site.ErrInvalidSiteChange
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	connector.mu.Lock()
	defer connector.mu.Unlock()
	if connector.closed {
		return nil, ErrInvalidMockSite
	}
	if existing := connector.changes[request.ChangeID]; existing != nil {
		if !sameRequest(existing, request) {
			return nil, site.ErrSiteChangeConflict
		}
		// A repeated request returns the durable receipt. Transient first-call
		// transport loss is not replayed.
		return existing.receipt, nil
	}
	state := connector.credentials[request.CredentialID]
	if state == nil || state.version != request.ExpectedVersion {
		return nil, ErrMockCredential
	}
	currentMatches, err := cryptokit.SecretsEqual(
		state.password, request.CurrentPassword,
	)
	if err != nil || !currentMatches {
		return nil, ErrMockCredential
	}
	currentClone, err := request.CurrentPassword.Clone()
	if err != nil {
		return nil, ErrInvalidMockSite
	}
	replacementClone, err := request.NewPassword.Clone()
	if err != nil {
		currentClone.Destroy()
		return nil, ErrInvalidMockSite
	}
	record := &changeRecord{
		credentialID: request.CredentialID,
		expected:     request.ExpectedVersion, next: request.NewVersion,
		policyHash: request.PolicyHash,
		current:    currentClone, replacement: replacementClone,
		hadMFA: request.MFAProof != nil,
	}
	status := site.ReceiptNotApplied
	receiptPolicy := request.PolicyHash
	var firstError error
	switch connector.behavior {
	case BehaviorSuccess:
		status = site.ReceiptApplied
	case BehaviorRejected:
		status = site.ReceiptNotApplied
	case BehaviorMFARequired:
		if request.MFAProof == nil || connector.mfaProof == nil {
			status = site.ReceiptMFARequired
		} else {
			matches, compareErr := cryptokit.SecretsEqual(
				connector.mfaProof, request.MFAProof,
			)
			if compareErr != nil || !matches {
				status = site.ReceiptMFARequired
			} else {
				status = site.ReceiptApplied
			}
		}
	case BehaviorPolicyRejected:
		status = site.ReceiptRejectedPolicy
		receiptPolicy = connector.requiredPolicy
	case BehaviorTimeoutUnknown:
		status = site.ReceiptUnknown
		firstError = site.ErrSiteTimeout
	case BehaviorResponseLostAfterApply:
		status = site.ReceiptApplied
		firstError = site.ErrSiteResponseLost
	default:
		currentClone.Destroy()
		replacementClone.Destroy()
		return nil, ErrInvalidMockSite
	}
	if status == site.ReceiptApplied {
		state.password.Destroy()
		state.password, err = request.NewPassword.Clone()
		if err != nil {
			currentClone.Destroy()
			replacementClone.Destroy()
			return nil, ErrInvalidMockSite
		}
		state.version = request.NewVersion
		state.revision++
	}
	receipt, err := site.SignReceipt(
		connector.privateKey,
		site.NewReceiptPayload(
			request, status, receiptPolicy, state.revision,
		),
	)
	if err != nil {
		currentClone.Destroy()
		replacementClone.Destroy()
		return nil, err
	}
	record.receipt = receipt
	record.firstError = firstError
	connector.changes[request.ChangeID] = record
	if firstError != nil {
		return nil, firstError
	}
	return receipt, nil
}

func (connector *Connector) QueryReceipt(
	ctx context.Context,
	changeID site.ChangeID,
	credentialID protocol.CredentialID,
) (*site.SignedReceipt, error) {
	if connector == nil || ctx == nil || allZero(changeID[:]) ||
		allZero(credentialID[:]) {
		return nil, site.ErrInvalidSiteChange
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	connector.mu.Lock()
	defer connector.mu.Unlock()
	record := connector.changes[changeID]
	if connector.closed || record == nil || record.credentialID != credentialID {
		return nil, site.ErrInvalidSiteChange
	}
	return record.receipt, nil
}

func (connector *Connector) ReceiptPublicKey() ed25519.PublicKey {
	if connector == nil {
		return nil
	}
	connector.mu.Lock()
	defer connector.mu.Unlock()
	return append(ed25519.PublicKey(nil), connector.publicKey...)
}

func (connector *Connector) CurrentVersion(
	credentialID protocol.CredentialID,
) (uint64, error) {
	if connector == nil {
		return 0, ErrInvalidMockSite
	}
	connector.mu.Lock()
	defer connector.mu.Unlock()
	state := connector.credentials[credentialID]
	if connector.closed || state == nil {
		return 0, ErrMockCredential
	}
	return state.version, nil
}

func (connector *Connector) PasswordMatches(
	credentialID protocol.CredentialID,
	password *cryptokit.Secret,
) (bool, error) {
	if connector == nil || password == nil {
		return false, ErrInvalidMockSite
	}
	connector.mu.Lock()
	defer connector.mu.Unlock()
	state := connector.credentials[credentialID]
	if connector.closed || state == nil {
		return false, ErrMockCredential
	}
	return cryptokit.SecretsEqual(state.password, password)
}

func (connector *Connector) Close() {
	if connector == nil {
		return
	}
	connector.mu.Lock()
	defer connector.mu.Unlock()
	if connector.closed {
		return
	}
	for credentialID, state := range connector.credentials {
		if state != nil && state.password != nil {
			state.password.Destroy()
		}
		delete(connector.credentials, credentialID)
	}
	for changeID, record := range connector.changes {
		if record != nil {
			if record.current != nil {
				record.current.Destroy()
			}
			if record.replacement != nil {
				record.replacement.Destroy()
			}
		}
		delete(connector.changes, changeID)
	}
	if connector.mfaProof != nil {
		connector.mfaProof.Destroy()
		connector.mfaProof = nil
	}
	clear(connector.privateKey)
	connector.privateKey = nil
	connector.publicKey = nil
	connector.closed = true
}

func sameRequest(record *changeRecord, request site.ChangeRequest) bool {
	if record == nil || record.credentialID != request.CredentialID ||
		record.expected != request.ExpectedVersion ||
		record.next != request.NewVersion ||
		record.policyHash != request.PolicyHash ||
		record.hadMFA != (request.MFAProof != nil) {
		return false
	}
	currentEqual, currentErr := cryptokit.SecretsEqual(
		record.current, request.CurrentPassword,
	)
	replacementEqual, replacementErr := cryptokit.SecretsEqual(
		record.replacement, request.NewPassword,
	)
	return currentErr == nil && replacementErr == nil &&
		currentEqual && replacementEqual
}

func allZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}

var _ site.Connector = (*Connector)(nil)
