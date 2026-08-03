// Package application coordinates private audit-event publication and
// authorized local security analysis.
package application

import (
	"context"
	"crypto/sha256"
	"errors"
	"time"

	auditdomain "vpass.local/vpass/internal/audit/domain"
	credentialdomain "vpass.local/vpass/internal/credential/domain"
	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
	transparencydomain "vpass.local/vpass/internal/transparency/domain"
)

var (
	ErrAuditPublication = errors.New("audit event publication failed")
	ErrAuditOffline     = errors.New("audit publication queued for retry")
)

type DurableAuditRecord struct {
	EventID           protocol.EventID
	CredentialID      protocol.CredentialID
	Epoch             uint64
	EvidenceLevel     protocol.EvidenceLevel
	ObservedBucket    uint64
	EncryptedEnvelope []byte
	EncryptedDigest   [sha256.Size]byte
	PublicLeaf        transparencydomain.LogLeaf
	PublicationState  string
}

// AuditOutbox persists encrypted bytes and their minimal public projection in
// one local durable transaction before any network publication is attempted.
type AuditOutbox interface {
	PutAuditRecord(context.Context, DurableAuditRecord) error
}

type PublishUseRequest struct {
	Now                 time.Time
	ChainID             string
	EventID             protocol.EventID
	CredentialID        protocol.CredentialID
	CredentialVersion   uint64
	DeviceID            protocol.DeviceID
	DescriptorDigest    [sha256.Size]byte
	EvidenceLevel       protocol.EvidenceLevel
	ObservedTimeBucket  uint64
	Epoch               uint64
	VerifiedBeacon      []byte
	FinalSequence       uint64
	NamespaceCommitment [sha256.Size]byte
	Password            *cryptokit.Secret
}

type Publisher struct {
	session *credentialdomain.VaultSession
	outbox  AuditOutbox
}

func NewPublisher(session *credentialdomain.VaultSession, outbox AuditOutbox) (*Publisher, error) {
	if session == nil || outbox == nil {
		return nil, ErrAuditPublication
	}
	return &Publisher{session: session, outbox: outbox}, nil
}

// PublishUse returns after the exact encrypted object and outbox record are
// durable. Log inclusion and checkpoint anchoring are asynchronous.
func (publisher *Publisher) PublishUse(
	ctx context.Context,
	request PublishUseRequest,
) (DurableAuditRecord, error) {
	if publisher == nil || ctx == nil || request.Password == nil ||
		request.Now.IsZero() || request.ChainID == "" ||
		request.CredentialVersion == 0 || !request.EvidenceLevel.Valid() ||
		request.ObservedTimeBucket == 0 || request.Epoch == 0 ||
		request.FinalSequence == 0 || auditBytesZero(request.EventID[:]) ||
		auditBytesZero(request.CredentialID[:]) || auditBytesZero(request.DeviceID[:]) ||
		auditBytesZero(request.DescriptorDigest[:]) ||
		auditBytesZero(request.NamespaceCommitment[:]) ||
		len(request.VerifiedBeacon) == 0 {
		return DurableAuditRecord{}, ErrAuditPublication
	}
	witness, err := publisher.session.ComputeAuditReuseTag(
		request.Now, request.ChainID, request.Epoch,
		request.VerifiedBeacon, request.Password,
	)
	if err != nil {
		return DurableAuditRecord{}, errors.Join(ErrAuditPublication, err)
	}
	defer clear(witness[:])
	privateBytes, err := auditdomain.MarshalPrivateUseEvent(auditdomain.PrivateUseEvent{
		FormatVersion: auditdomain.AuditPayloadVersion,
		CredentialID:  request.CredentialID, CredentialVersion: request.CredentialVersion,
		DeviceID: request.DeviceID, EvidenceLevel: request.EvidenceLevel,
		ObservedTimeBucket: request.ObservedTimeBucket,
		DescriptorDigest:   request.DescriptorDigest, ReuseWitness: witness,
	})
	if err != nil {
		return DurableAuditRecord{}, errors.Join(ErrAuditPublication, err)
	}
	privateSecret, err := cryptokit.NewSecret(privateBytes)
	clear(privateBytes)
	if err != nil {
		return DurableAuditRecord{}, errors.Join(ErrAuditPublication, err)
	}
	defer privateSecret.Destroy()
	envelope, pseudonym, err := publisher.session.SealAuditEvent(
		request.Now, request.ChainID, request.EventID, request.Epoch,
		request.VerifiedBeacon, privateSecret,
	)
	if err != nil {
		return DurableAuditRecord{}, errors.Join(ErrAuditPublication, err)
	}
	encodedEnvelope, err := envelope.MarshalBinary()
	if err != nil {
		return DurableAuditRecord{}, errors.Join(ErrAuditPublication, err)
	}
	subjectPseudonym := sha256.Sum256(append(
		[]byte(protocol.DomainPrefix+"AUDIT-PUBLIC-SUBJECT"), pseudonym[:]...,
	))
	record := DurableAuditRecord{
		EventID: request.EventID, CredentialID: request.CredentialID,
		Epoch: request.Epoch, EvidenceLevel: request.EvidenceLevel,
		ObservedBucket:    request.ObservedTimeBucket,
		EncryptedEnvelope: append([]byte(nil), encodedEnvelope...),
		EncryptedDigest:   envelope.PayloadHash(),
		PublicLeaf: transparencydomain.LogLeaf{
			NamespaceCommitment: request.NamespaceCommitment,
			SubjectPseudonym:    subjectPseudonym,
			ObjectType:          protocol.ObjectTypeAuditEvent,
			ObjectDigest:        envelope.PayloadHash(),
			OperationType:       protocol.OperationUseObserved,
			FinalSequence:       request.FinalSequence, Epoch: request.Epoch,
		},
		PublicationState: "OBJECT_STORED",
	}
	clear(encodedEnvelope)
	if record.PublicLeaf.Validate() != nil {
		return DurableAuditRecord{}, ErrAuditPublication
	}
	if err := publisher.outbox.PutAuditRecord(ctx, cloneDurableRecord(record)); err != nil {
		return DurableAuditRecord{}, errors.Join(ErrAuditPublication, err)
	}
	return cloneDurableRecord(record), nil
}

func cloneDurableRecord(record DurableAuditRecord) DurableAuditRecord {
	record.EncryptedEnvelope = append([]byte(nil), record.EncryptedEnvelope...)
	return record
}

func auditBytesZero(value []byte) bool {
	var combined byte
	for _, item := range value {
		combined |= item
	}
	return combined == 0
}
