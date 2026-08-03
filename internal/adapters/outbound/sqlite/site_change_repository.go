package sqlite

import (
	"bytes"
	"context"
	"crypto/sha256"
	"database/sql"
	"errors"
	"math"

	"vpass.local/vpass/internal/platform"
	"vpass.local/vpass/internal/protocol"
	siteapp "vpass.local/vpass/internal/site/application"
	sitedomain "vpass.local/vpass/internal/site/domain"
)

var (
	ErrInvalidSiteChangeAttempt = errors.New("invalid site change attempt")
	ErrSiteCandidateNotDurable  = errors.New("site change candidate is not durable")
)

type SiteChangeAttemptRepository struct {
	database *Database
	clock    platform.Clock
}

func NewSiteChangeAttemptRepository(
	database *Database,
	clock platform.Clock,
) (*SiteChangeAttemptRepository, error) {
	if database == nil || database.db == nil || clock == nil {
		return nil, ErrInvalidSiteChangeAttempt
	}
	return &SiteChangeAttemptRepository{database: database, clock: clock}, nil
}

func (repository *SiteChangeAttemptRepository) Create(
	ctx context.Context,
	attempt siteapp.ChangeAttempt,
) error {
	if repository == nil || ctx == nil ||
		attempt.Status != siteapp.AttemptCandidateDurable ||
		bytesAllZero(attempt.ChangeID[:]) ||
		bytesAllZero(attempt.NamespaceID[:]) ||
		bytesAllZero(attempt.CredentialID[:]) ||
		attempt.PreviousVersion == 0 ||
		attempt.CandidateVersion != attempt.PreviousVersion+1 ||
		bytesAllZero(attempt.CandidateDescriptorHash[:]) ||
		bytesAllZero(attempt.PolicyHash[:]) ||
		bytesAllZero(attempt.RequestHash[:]) {
		return ErrInvalidSiteChangeAttempt
	}
	statusName, _ := attempt.Status.DatabaseName()
	now := repository.clock.Now().UTC().UnixMilli()
	if now < 0 {
		return ErrInvalidSiteChangeAttempt
	}
	transaction, err := repository.database.BeginImmediate(ctx)
	if err != nil {
		return err
	}
	defer func() { _ = transaction.Rollback() }()
	if err := requireDurableSiteCandidate(ctx, transaction, attempt); err != nil {
		return err
	}
	if _, err := transaction.ExecContext(
		ctx,
		`INSERT INTO site_change_attempts (
  change_id, namespace_id, credential_id,
  previous_version, candidate_version, candidate_descriptor_hash,
  request_hash, status, created_at_ms, updated_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
		attempt.ChangeID[:], attempt.NamespaceID[:], attempt.CredentialID[:],
		attempt.PreviousVersion, attempt.CandidateVersion,
		attempt.CandidateDescriptorHash[:], attempt.RequestHash[:],
		statusName, now, now,
	); err != nil {
		return err
	}
	return transaction.Commit()
}

func requireDurableSiteCandidate(
	ctx context.Context,
	transaction *Transaction,
	attempt siteapp.ChangeAttempt,
) error {
	var namespaceID, descriptorHash, policyHash []byte
	var candidateStatus, previousStatus, descriptorObjectState string
	var fieldCount, committedFieldCount int
	err := transaction.QueryRowContext(
		ctx,
		`SELECT c.namespace_id, candidate.descriptor_hash,
        candidate.policy_hash, candidate.status,
        previous.status, descriptor_object.state,
        count(fields.field_type),
        coalesce(sum(CASE WHEN field_object.state = 'COMMITTED' THEN 1 ELSE 0 END), 0)
 FROM credentials c
 JOIN credential_versions candidate
   ON candidate.credential_id = c.credential_id
  AND candidate.version = ?
 JOIN credential_versions previous
   ON previous.credential_id = c.credential_id
  AND previous.version = ?
 JOIN content_objects descriptor_object
   ON descriptor_object.object_hash = candidate.descriptor_object_hash
 LEFT JOIN credential_version_fields fields
   ON fields.credential_id = candidate.credential_id
  AND fields.version = candidate.version
 LEFT JOIN content_objects field_object
   ON field_object.object_hash = fields.object_hash
 WHERE c.credential_id = ?
 GROUP BY c.namespace_id, candidate.descriptor_hash,
          candidate.policy_hash, candidate.status,
          previous.status, descriptor_object.state`,
		attempt.CandidateVersion, attempt.PreviousVersion,
		attempt.CredentialID[:],
	).Scan(
		&namespaceID, &descriptorHash, &policyHash, &candidateStatus,
		&previousStatus, &descriptorObjectState,
		&fieldCount, &committedFieldCount,
	)
	if errors.Is(err, sql.ErrNoRows) {
		return ErrSiteCandidateNotDurable
	}
	if err != nil {
		return err
	}
	if !bytes.Equal(namespaceID, attempt.NamespaceID[:]) ||
		!bytes.Equal(descriptorHash, attempt.CandidateDescriptorHash[:]) ||
		!bytes.Equal(policyHash, attempt.PolicyHash[:]) ||
		candidateStatus != "PENDING_CANDIDATE" ||
		previousStatus != "ACTIVE" ||
		descriptorObjectState != "COMMITTED" ||
		fieldCount == 0 || fieldCount != committedFieldCount {
		return ErrSiteCandidateNotDurable
	}
	return nil
}

func (repository *SiteChangeAttemptRepository) Load(
	ctx context.Context,
	changeID sitedomain.ChangeID,
) (siteapp.ChangeAttempt, error) {
	if repository == nil || ctx == nil || bytesAllZero(changeID[:]) {
		return siteapp.ChangeAttempt{}, ErrInvalidSiteChangeAttempt
	}
	var namespaceID, credentialID, descriptorHash, policyHash, requestHash,
		receiptHash, eventID []byte
	var previousVersion, candidateVersion uint64
	var statusName string
	var receiptStatus, evidence sql.NullInt64
	err := repository.database.QueryRowContext(
		ctx,
		`SELECT namespace_id, credential_id, previous_version,
        candidate_version, candidate_descriptor_hash, request_hash,
        status, site_receipt_hash, site_receipt_status,
        evidence_level, confirmation_event_id
 FROM site_change_attempts
 WHERE change_id = ?`,
		changeID[:],
	).Scan(
		&namespaceID, &credentialID, &previousVersion,
		&candidateVersion, &descriptorHash, &requestHash,
		&statusName, &receiptHash, &receiptStatus,
		&evidence, &eventID,
	)
	if errors.Is(err, sql.ErrNoRows) {
		return siteapp.ChangeAttempt{}, ErrInvalidSiteChangeAttempt
	}
	if err != nil {
		return siteapp.ChangeAttempt{}, err
	}
	// Policy is immutable on the candidate version and avoids duplicating a
	// second trust source in site_change_attempts.
	if err := repository.database.QueryRowContext(
		ctx,
		`SELECT policy_hash FROM credential_versions
 WHERE credential_id = ? AND version = ?`,
		credentialID, candidateVersion,
	).Scan(&policyHash); err != nil {
		return siteapp.ChangeAttempt{}, err
	}
	status, err := siteapp.ParseAttemptStatus(statusName)
	if err != nil || len(namespaceID) != len(protocol.NamespaceID{}) ||
		len(credentialID) != len(protocol.CredentialID{}) ||
		len(descriptorHash) != sha256.Size || len(policyHash) != sha256.Size ||
		len(requestHash) != sha256.Size {
		return siteapp.ChangeAttempt{}, ErrInvalidSiteChangeAttempt
	}
	attempt := siteapp.ChangeAttempt{
		ChangeID: changeID, PreviousVersion: previousVersion,
		CandidateVersion: candidateVersion, Status: status,
	}
	copy(attempt.NamespaceID[:], namespaceID)
	copy(attempt.CredentialID[:], credentialID)
	copy(attempt.CandidateDescriptorHash[:], descriptorHash)
	copy(attempt.PolicyHash[:], policyHash)
	copy(attempt.RequestHash[:], requestHash)
	if receiptStatus.Valid {
		if receiptStatus.Int64 < 1 || receiptStatus.Int64 > 5 ||
			len(receiptHash) != sha256.Size {
			return siteapp.ChangeAttempt{}, ErrInvalidSiteChangeAttempt
		}
		value := sitedomain.ReceiptStatus(receiptStatus.Int64)
		digest := [sha256.Size]byte{}
		copy(digest[:], receiptHash)
		attempt.ReceiptStatus = &value
		attempt.ReceiptDigest = &digest
	} else if len(receiptHash) != 0 {
		return siteapp.ChangeAttempt{}, ErrInvalidSiteChangeAttempt
	}
	var v21Evidence, v21Schema sql.NullInt64
	var v21Decision, v21Trust sql.NullString
	v21Err := repository.database.QueryRowContext(
		ctx,
		`SELECT evidence_schema, evidence_level, trust_kind, decision_state
		   FROM site_confirmation_evidence_v21
		  WHERE change_id = ?`,
		changeID[:],
	).Scan(&v21Schema, &v21Evidence, &v21Trust, &v21Decision)
	if v21Err != nil && !errors.Is(v21Err, sql.ErrNoRows) {
		return siteapp.ChangeAttempt{}, v21Err
	}
	if v21Err == nil {
		if !v21Schema.Valid || v21Schema.Int64 != 2 ||
			!v21Evidence.Valid || v21Evidence.Int64 < 0 ||
			v21Evidence.Int64 > 5 || !v21Trust.Valid || !v21Decision.Valid {
			return siteapp.ChangeAttempt{}, ErrInvalidSiteChangeAttempt
		}
		value := protocol.EvidenceLevel(v21Evidence.Int64)
		if !value.Valid() {
			return siteapp.ChangeAttempt{}, ErrInvalidSiteChangeAttempt
		}
		attempt.Evidence = &value
		attempt.EvidenceSchemaVersion = 2
		attempt.EvidenceTrustKind = v21Trust.String
		if v21Decision.String == "REVIEW_REQUIRED" {
			attempt.Status = siteapp.AttemptReviewRequired
		}
	} else if evidence.Valid {
		// Old values 1-5 have legacy semantics and cannot be reinterpreted as
		// E1-E5. Disposable research databases must be rebuilt or explicitly
		// imported into the v2.1 evidence table.
		return siteapp.ChangeAttempt{}, ErrInvalidSiteChangeAttempt
	}
	if len(eventID) != 0 {
		if len(eventID) != len(protocol.EventID{}) {
			return siteapp.ChangeAttempt{}, ErrInvalidSiteChangeAttempt
		}
		value := protocol.EventID{}
		copy(value[:], eventID)
		attempt.ConfirmationEventID = &value
	}
	return attempt, nil
}

func (repository *SiteChangeAttemptRepository) Transition(
	ctx context.Context,
	changeID sitedomain.ChangeID,
	expected siteapp.AttemptStatus,
	next siteapp.AttemptStatus,
	receipt *sitedomain.SignedReceipt,
	evidence *protocol.EvidenceLevel,
	eventID *protocol.EventID,
) error {
	if repository == nil || ctx == nil || bytesAllZero(changeID[:]) ||
		!expected.Valid() || !next.Valid() || !expected.CanTransitionTo(next) {
		return ErrInvalidSiteChangeAttempt
	}
	expectedName := physicalAttemptStatus(expected)
	nextName := physicalAttemptStatus(next)
	var receiptHash, receiptCBOR, receiptSignature any
	var receiptStatus any
	if receipt != nil {
		digest := receipt.Digest()
		signature := receipt.Signature()
		payload := receipt.Payload()
		receiptHash, receiptCBOR = digest[:], receipt.Encoded()
		receiptSignature, receiptStatus = signature[:], int64(payload.Status)
	}
	var eventValue any
	if evidence != nil {
		if !evidence.Valid() {
			return ErrInvalidSiteChangeAttempt
		}
	}
	if eventID != nil {
		if bytesAllZero(eventID[:]) {
			return ErrInvalidSiteChangeAttempt
		}
		eventValue = eventID[:]
	}
	now := repository.clock.Now().UTC().UnixMilli()
	if now < 0 || now > math.MaxInt64 {
		return ErrInvalidSiteChangeAttempt
	}
	transaction, err := repository.database.BeginImmediate(ctx)
	if err != nil {
		return err
	}
	defer func() { _ = transaction.Rollback() }()
	result, err := transaction.ExecContext(
		ctx,
		`UPDATE site_change_attempts
 SET status = ?,
     site_receipt_hash = coalesce(?, site_receipt_hash),
     site_receipt_status = coalesce(?, site_receipt_status),
     site_receipt_cbor = coalesce(?, site_receipt_cbor),
     site_receipt_signature = coalesce(?, site_receipt_signature),
     evidence_level = coalesce(?, evidence_level),
     confirmation_event_id = coalesce(?, confirmation_event_id),
     updated_at_ms = ?
 WHERE change_id = ? AND status = ?`,
		nextName, receiptHash, receiptStatus, receiptCBOR, receiptSignature,
		nil, eventValue, now, changeID[:], expectedName,
	)
	if err != nil {
		return err
	}
	affected, err := result.RowsAffected()
	if err != nil {
		return err
	}
	if affected != 1 {
		return ErrInvalidSiteChangeAttempt
	}
	if evidence != nil {
		var namespaceID, credentialID []byte
		var candidateVersion uint64
		if err := transaction.QueryRowContext(
			ctx,
			`SELECT namespace_id, credential_id, candidate_version
			   FROM site_change_attempts WHERE change_id = ?`,
			changeID[:],
		).Scan(&namespaceID, &credentialID, &candidateVersion); err != nil {
			return err
		}
		levelName, _ := evidence.DatabaseName()
		decisionName := evidenceDecisionState(next)
		if decisionName == "" {
			return ErrInvalidSiteChangeAttempt
		}
		digestInput := append(
			[]byte(protocol.DomainPrefix+"SITE-EVIDENCE-V21"),
			changeID[:]...,
		)
		digestInput = append(digestInput, byte(*evidence))
		digestInput = append(digestInput, []byte(levelName)...)
		digestInput = append(digestInput, []byte(decisionName)...)
		evidenceDigest := sha256.Sum256(digestInput)
		clear(digestInput)
		trustKind := evidenceTrustKind(*evidence)
		_, err = transaction.ExecContext(
			ctx,
			`INSERT INTO site_confirmation_evidence_v21(
			   evidence_digest, change_id, namespace_id, credential_id,
			   candidate_version, evidence_schema, evidence_level, trust_kind,
			   decision_state, receipt_digest, created_at_ms
			 ) VALUES(?, ?, ?, ?, ?, 2, ?, ?, ?, ?, ?)
			 ON CONFLICT(change_id) DO UPDATE SET
			   evidence_digest = excluded.evidence_digest,
			   evidence_level = excluded.evidence_level,
			   trust_kind = excluded.trust_kind,
			   decision_state = excluded.decision_state,
			   receipt_digest = coalesce(excluded.receipt_digest, receipt_digest),
			   created_at_ms = excluded.created_at_ms`,
			evidenceDigest[:], changeID[:], namespaceID, credentialID,
			candidateVersion, int64(*evidence), trustKind, decisionName,
			receiptHash, now,
		)
		if err != nil {
			return err
		}
	} else {
		decisionName := evidenceDecisionState(next)
		if decisionName == "" {
			return ErrInvalidSiteChangeAttempt
		}
		if _, err := transaction.ExecContext(
			ctx,
			`UPDATE site_confirmation_evidence_v21
			    SET decision_state = ?
			  WHERE change_id = ?`,
			decisionName, changeID[:],
		); err != nil {
			return err
		}
	}
	return transaction.Commit()
}

func physicalAttemptStatus(status siteapp.AttemptStatus) string {
	if status == siteapp.AttemptReviewRequired {
		return "SITE_STATUS_UNKNOWN"
	}
	name, _ := status.DatabaseName()
	return name
}

func evidenceTrustKind(evidence protocol.EvidenceLevel) string {
	switch evidence {
	case protocol.EvidenceNewPasswordReloginConfirmed:
		return "RELOGIN_POLICY"
	case protocol.EvidenceSiteSignedReceipt:
		// Stage 2 has no production E4 connector registry. Persist the safe
		// research boundary; a future trusted connector must provide an
		// authenticated trust-kind input instead of reusing this default.
		return "MOCK_SITE_E4"
	case protocol.EvidenceUserSignedConfirmation:
		return "USER_SIGNED"
	default:
		return "BROWSER_OBSERVATION"
	}
}

func evidenceDecisionState(status siteapp.AttemptStatus) string {
	switch status {
	case siteapp.AttemptSiteStatusUnknown:
		return "UNKNOWN"
	case siteapp.AttemptReviewRequired:
		return "REVIEW_REQUIRED"
	case siteapp.AttemptFailedRetryable, siteapp.AttemptAborted:
		return "FAILED"
	case siteapp.AttemptCandidateDurable, siteapp.AttemptSiteUpdatePending,
		siteapp.AttemptSiteChangedLocalCommitPending,
		siteapp.AttemptSiteConfirmPending:
		return "SITE_CONFIRM_PENDING"
	case siteapp.AttemptActive:
		return "ACTIVE"
	default:
		return ""
	}
}

var _ siteapp.AttemptStore = (*SiteChangeAttemptRepository)(nil)
