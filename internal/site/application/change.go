// Package application coordinates crash-recoverable site password changes.
// Candidate ciphertext durability and signed confirmation are persistence
// boundaries supplied by ports; no password bytes are written here.
package application

import (
	"context"
	"crypto/sha256"
	"errors"

	"vdns.local/vdns/internal/protocol"
	sitedomain "vdns.local/vdns/internal/site/domain"
)

var (
	ErrInvalidChangeFlow    = errors.New("invalid password change flow")
	ErrChangeTransition     = errors.New("invalid password change transition")
	ErrConfirmationRequired = errors.New("strong signed confirmation is required")
)

type AttemptStatus uint8

const (
	AttemptCandidateDurable AttemptStatus = iota + 1
	AttemptSiteUpdatePending
	AttemptFailedRetryable
	AttemptSiteStatusUnknown
	AttemptSiteChangedLocalCommitPending
	AttemptSiteConfirmPending
	AttemptReviewRequired
	AttemptActive
	AttemptAborted
)

func (status AttemptStatus) Valid() bool {
	return status >= AttemptCandidateDurable && status <= AttemptAborted
}

func (status AttemptStatus) CanTransitionTo(next AttemptStatus) bool {
	switch status {
	case AttemptCandidateDurable:
		return next == AttemptSiteUpdatePending || next == AttemptAborted
	case AttemptSiteUpdatePending:
		return next == AttemptFailedRetryable ||
			next == AttemptSiteStatusUnknown ||
			next == AttemptSiteChangedLocalCommitPending
	case AttemptFailedRetryable:
		return next == AttemptSiteUpdatePending || next == AttemptAborted
	case AttemptSiteStatusUnknown:
		return next == AttemptSiteUpdatePending ||
			next == AttemptSiteConfirmPending ||
			next == AttemptReviewRequired
	case AttemptSiteChangedLocalCommitPending:
		return next == AttemptSiteConfirmPending
	case AttemptSiteConfirmPending:
		return next == AttemptSiteStatusUnknown ||
			next == AttemptReviewRequired ||
			next == AttemptActive
	case AttemptReviewRequired:
		return next == AttemptSiteConfirmPending
	default:
		return false
	}
}

func (status AttemptStatus) DatabaseName() (string, error) {
	switch status {
	case AttemptCandidateDurable:
		return "CANDIDATE_DURABLE", nil
	case AttemptSiteUpdatePending:
		return "SITE_UPDATE_PENDING", nil
	case AttemptFailedRetryable:
		return "FAILED_RETRYABLE", nil
	case AttemptSiteStatusUnknown:
		return "SITE_STATUS_UNKNOWN", nil
	case AttemptSiteChangedLocalCommitPending:
		return "SITE_CHANGED_LOCAL_COMMIT_PENDING", nil
	case AttemptSiteConfirmPending:
		return "SITE_CONFIRM_PENDING", nil
	case AttemptReviewRequired:
		return "REVIEW_REQUIRED", nil
	case AttemptActive:
		return "ACTIVE", nil
	case AttemptAborted:
		return "ABORTED", nil
	default:
		return "", ErrChangeTransition
	}
}

func ParseAttemptStatus(value string) (AttemptStatus, error) {
	for status := AttemptCandidateDurable; status <= AttemptAborted; status++ {
		name, _ := status.DatabaseName()
		if name == value {
			return status, nil
		}
	}
	return 0, ErrChangeTransition
}

type ChangeAttempt struct {
	ChangeID                sitedomain.ChangeID
	NamespaceID             protocol.NamespaceID
	CredentialID            protocol.CredentialID
	PreviousVersion         uint64
	CandidateVersion        uint64
	CandidateDescriptorHash [sha256.Size]byte
	PolicyHash              [sha256.Size]byte
	RequestHash             [sha256.Size]byte
	Status                  AttemptStatus
	ReceiptStatus           *sitedomain.ReceiptStatus
	ReceiptDigest           *[sha256.Size]byte
	Evidence                *protocol.EvidenceLevel
	EvidenceSchemaVersion   uint64
	EvidenceTrustKind       string
	ConfirmationEventID     *protocol.EventID
}

// AttemptStore.Create must prove the referenced candidate version and all of
// its ciphertext objects are durable before inserting CandidateDurable.
type AttemptStore interface {
	Create(context.Context, ChangeAttempt) error
	Load(context.Context, sitedomain.ChangeID) (ChangeAttempt, error)
	Transition(
		context.Context,
		sitedomain.ChangeID,
		AttemptStatus,
		AttemptStatus,
		*sitedomain.SignedReceipt,
		*protocol.EvidenceLevel,
		*protocol.EventID,
	) error
}

// ConfirmationAuthorizer verifies capability and persists a signed
// UPDATE_CONFIRM operation event before returning its EventID.
type ConfirmationAuthorizer interface {
	AuthorizeConfirmation(
		context.Context,
		ChangeAttempt,
		protocol.EvidenceLevel,
	) (protocol.EventID, error)
}

type Coordinator struct {
	connector  sitedomain.Connector
	store      AttemptStore
	authorizer ConfirmationAuthorizer
	policy     protocol.EvidenceActivationPolicy
}

func NewCoordinator(
	connector sitedomain.Connector,
	store AttemptStore,
	authorizer ConfirmationAuthorizer,
) (*Coordinator, error) {
	if connector == nil || store == nil || authorizer == nil {
		return nil, ErrInvalidChangeFlow
	}
	return &Coordinator{
		connector: connector, store: store, authorizer: authorizer,
		policy: protocol.EvidenceActivationPolicy{
			AllowUserConfirmation: true,
		},
	}, nil
}

func NewCoordinatorWithPolicy(
	connector sitedomain.Connector,
	store AttemptStore,
	authorizer ConfirmationAuthorizer,
	policy protocol.EvidenceActivationPolicy,
) (*Coordinator, error) {
	coordinator, err := NewCoordinator(connector, store, authorizer)
	if err != nil {
		return nil, err
	}
	coordinator.policy = policy
	return coordinator, nil
}

// Start persists the candidate first, then calls the site. Even a verified
// APPLIED receipt stops at SiteConfirmPending; activation is a separate signed
// Confirm step.
func (coordinator *Coordinator) Start(
	ctx context.Context,
	request sitedomain.ChangeRequest,
	namespaceID protocol.NamespaceID,
	candidateDescriptorHash [sha256.Size]byte,
) (AttemptStatus, error) {
	if coordinator == nil || ctx == nil || request.Validate() != nil ||
		allZero(namespaceID[:]) || allZero(candidateDescriptorHash[:]) {
		return 0, ErrInvalidChangeFlow
	}
	requestHash, err := request.PublicDigest()
	if err != nil {
		return 0, ErrInvalidChangeFlow
	}
	attempt := ChangeAttempt{
		ChangeID: request.ChangeID, NamespaceID: namespaceID,
		CredentialID:            request.CredentialID,
		PreviousVersion:         request.ExpectedVersion,
		CandidateVersion:        request.NewVersion,
		CandidateDescriptorHash: candidateDescriptorHash,
		PolicyHash:              request.PolicyHash,
		RequestHash:             requestHash,
		Status:                  AttemptCandidateDurable,
	}
	if err := coordinator.store.Create(ctx, attempt); err != nil {
		return 0, err
	}
	if err := coordinator.store.Transition(
		ctx, request.ChangeID, AttemptCandidateDurable,
		AttemptSiteUpdatePending, nil, nil, nil,
	); err != nil {
		return 0, err
	}
	receipt, changeErr := coordinator.connector.ChangePassword(ctx, request)
	if errors.Is(changeErr, sitedomain.ErrSiteResponseLost) ||
		errors.Is(changeErr, sitedomain.ErrSiteTimeout) {
		receipt, changeErr = coordinator.connector.QueryReceipt(
			ctx, request.ChangeID, request.CredentialID,
		)
	}
	if changeErr != nil || receipt == nil {
		if err := coordinator.store.Transition(
			ctx, request.ChangeID, AttemptSiteUpdatePending,
			AttemptSiteStatusUnknown, nil, nil, nil,
		); err != nil {
			return 0, err
		}
		return AttemptSiteStatusUnknown, nil
	}
	verified, err := sitedomain.ParseAndVerifyReceipt(
		receipt.Encoded(), receipt.Signature(),
		coordinator.connector.ReceiptPublicKey(),
		request.ChangeID, request.CredentialID,
	)
	if err != nil {
		_ = coordinator.store.Transition(
			ctx, request.ChangeID, AttemptSiteUpdatePending,
			AttemptSiteStatusUnknown, nil, nil, nil,
		)
		return AttemptSiteStatusUnknown, err
	}
	payload := verified.Payload()
	if payload.ExpectedVersion != request.ExpectedVersion ||
		payload.NewVersion != request.NewVersion ||
		payload.PolicyHash != request.PolicyHash {
		_ = coordinator.store.Transition(
			ctx, request.ChangeID, AttemptSiteUpdatePending,
			AttemptSiteStatusUnknown, nil, nil, nil,
		)
		return AttemptSiteStatusUnknown, sitedomain.ErrSiteReceipt
	}
	switch payload.Status {
	case sitedomain.ReceiptApplied:
		if err := coordinator.store.Transition(
			ctx, request.ChangeID, AttemptSiteUpdatePending,
			AttemptSiteChangedLocalCommitPending, verified, nil, nil,
		); err != nil {
			return 0, err
		}
		if err := coordinator.store.Transition(
			ctx, request.ChangeID, AttemptSiteChangedLocalCommitPending,
			AttemptSiteConfirmPending, nil, nil, nil,
		); err != nil {
			return 0, err
		}
		return AttemptSiteConfirmPending, nil
	case sitedomain.ReceiptUnknown:
		if err := coordinator.store.Transition(
			ctx, request.ChangeID, AttemptSiteUpdatePending,
			AttemptSiteStatusUnknown, verified, nil, nil,
		); err != nil {
			return 0, err
		}
		return AttemptSiteStatusUnknown, nil
	default:
		if err := coordinator.store.Transition(
			ctx, request.ChangeID, AttemptSiteUpdatePending,
			AttemptFailedRetryable, verified, nil, nil,
		); err != nil {
			return 0, err
		}
		return AttemptFailedRetryable, nil
	}
}

// Confirm records all E0-E5 outcomes and activates only evidence allowed by the
// explicit L5 policy. A Mock Site receipt never satisfies trusted E4.
func (coordinator *Coordinator) Confirm(
	ctx context.Context,
	changeID sitedomain.ChangeID,
	evidence protocol.EvidenceLevel,
) error {
	if coordinator == nil || ctx == nil || allZero(changeID[:]) ||
		!evidence.Valid() {
		return ErrConfirmationRequired
	}
	attempt, err := coordinator.store.Load(ctx, changeID)
	if err != nil {
		return err
	}
	policy := coordinator.policy
	policy.TrustedSiteConnector =
		coordinator.connector.TrustKind() == sitedomain.ConnectorTrustedSite
	if !evidence.CanActivateCredential(policy) {
		next := AttemptSiteStatusUnknown
		if evidence == protocol.EvidencePageSuccessIndicated ||
			evidence == protocol.EvidenceNewPasswordReloginConfirmed ||
			evidence == protocol.EvidenceSiteSignedReceipt {
			next = AttemptReviewRequired
		}
		if attempt.Status == AttemptSiteConfirmPending &&
			attempt.Status.CanTransitionTo(next) {
			_ = coordinator.store.Transition(
				ctx, changeID, attempt.Status, next, nil, &evidence, nil,
			)
		}
		return ErrConfirmationRequired
	}
	if attempt.Status == AttemptSiteStatusUnknown ||
		attempt.Status == AttemptReviewRequired {
		if err := coordinator.store.Transition(
			ctx, changeID, attempt.Status,
			AttemptSiteConfirmPending, nil, nil, nil,
		); err != nil {
			return err
		}
		attempt.Status = AttemptSiteConfirmPending
	}
	if attempt.Status != AttemptSiteConfirmPending {
		return ErrChangeTransition
	}
	if evidence == protocol.EvidenceSiteSignedReceipt &&
		(attempt.ReceiptStatus == nil ||
			*attempt.ReceiptStatus != sitedomain.ReceiptApplied ||
			attempt.ReceiptDigest == nil) {
		return ErrConfirmationRequired
	}
	eventID, err := coordinator.authorizer.AuthorizeConfirmation(
		ctx, attempt, evidence,
	)
	if err != nil || allZero(eventID[:]) {
		return errors.Join(ErrConfirmationRequired, err)
	}
	return coordinator.store.Transition(
		ctx, changeID, AttemptSiteConfirmPending,
		AttemptActive, nil, &evidence, &eventID,
	)
}

func allZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}
