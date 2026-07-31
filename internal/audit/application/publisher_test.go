package application

import (
	"bytes"
	"context"
	"errors"
	"sync"
	"testing"
	"time"

	credentialdomain "vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

type memoryAuditOutbox struct {
	mu      sync.Mutex
	records []DurableAuditRecord
	err     error
}

func (outbox *memoryAuditOutbox) PutAuditRecord(
	_ context.Context,
	record DurableAuditRecord,
) error {
	outbox.mu.Lock()
	defer outbox.mu.Unlock()
	if outbox.err != nil {
		return outbox.err
	}
	outbox.records = append(outbox.records, cloneDurableRecord(record))
	return nil
}

func TestPublishUseSealsWitnessAndPersistsMinimalRetryRecord(t *testing.T) {
	now := time.Unix(1_700_000_000, 0).UTC()
	session := auditVaultSession(t, now)
	defer session.Lock()
	outbox := &memoryAuditOutbox{}
	publisher, err := NewPublisher(session, outbox)
	if err != nil {
		t.Fatal(err)
	}
	password, _ := cryptokit.NewSecret([]byte("Do-Not-Leak-This-Password!"))
	defer password.Destroy()
	request := PublishUseRequest{
		Now: now, ChainID: "anvil:31337",
		EventID: eventIDPattern(1), CredentialID: credentialIDPattern(33),
		CredentialVersion: 3, DeviceID: deviceIDPattern(65),
		DescriptorDigest:   digestPattern(81),
		EvidenceLevel:      protocol.EvidenceSubmitObserved,
		ObservedTimeBucket: 100, Epoch: 9, VerifiedBeacon: []byte("verified-vrf-9"),
		FinalSequence: 44, NamespaceCommitment: digestPattern(97), Password: password,
	}
	result, err := publisher.PublishUse(context.Background(), request)
	if err != nil {
		t.Fatal(err)
	}
	if len(outbox.records) != 1 || result.PublicationState != "OBJECT_STORED" ||
		result.PublicLeaf.OperationType != protocol.OperationUseObserved ||
		result.PublicLeaf.Epoch != request.Epoch ||
		!bytes.Equal(result.EncryptedEnvelope, outbox.records[0].EncryptedEnvelope) {
		t.Fatalf("unexpected durable record: %+v", result)
	}
	if bytes.Contains(result.EncryptedEnvelope, []byte("Do-Not-Leak")) {
		t.Fatal("encrypted event exposed password bytes")
	}
	publicBytes, err := protocol.MarshalDeterministic(result.PublicLeaf)
	if err != nil {
		t.Fatal(err)
	}
	if bytes.Contains(publicBytes, request.CredentialID[:]) ||
		bytes.Contains(publicBytes, request.DeviceID[:]) {
		t.Fatal("public leaf exposed private identifier")
	}

	request.EventID[0] = 7
	request.Epoch = 10
	request.FinalSequence++
	request.VerifiedBeacon = []byte("verified-vrf-10")
	second, err := publisher.PublishUse(context.Background(), request)
	if err != nil {
		t.Fatal(err)
	}
	if second.PublicLeaf.SubjectPseudonym == result.PublicLeaf.SubjectPseudonym {
		t.Fatal("public pseudonym remained linkable across epochs")
	}
}

func TestPublishUseFailsClosedBeforeNetworkWhenDurableOutboxFails(t *testing.T) {
	now := time.Unix(1_700_000_000, 0).UTC()
	session := auditVaultSession(t, now)
	defer session.Lock()
	outbox := &memoryAuditOutbox{err: errors.New("disk full")}
	publisher, _ := NewPublisher(session, outbox)
	password, _ := cryptokit.NewSecret([]byte("password"))
	defer password.Destroy()
	_, err := publisher.PublishUse(context.Background(), PublishUseRequest{
		Now: now, ChainID: "chain", EventID: protocol.EventID{1},
		CredentialID: protocol.CredentialID{2}, CredentialVersion: 1,
		DeviceID: protocol.DeviceID{3}, DescriptorDigest: [32]byte{4},
		EvidenceLevel:      protocol.EvidenceAutofillObserved,
		ObservedTimeBucket: 1, Epoch: 1, VerifiedBeacon: []byte{1},
		FinalSequence: 1, NamespaceCommitment: [32]byte{5}, Password: password,
	})
	if !errors.Is(err, ErrAuditPublication) || len(outbox.records) != 0 {
		t.Fatalf("outbox failure = %v, records=%d", err, len(outbox.records))
	}
}

func auditVaultSession(t *testing.T, now time.Time) *credentialdomain.VaultSession {
	t.Helper()
	bundle, _, err := cryptokit.GenerateRootSecretBundle(1, 1)
	if err != nil {
		t.Fatal(err)
	}
	session, err := credentialdomain.NewVaultSession(
		bundle, protocol.NamespaceID{1}, protocol.DeviceID{2},
		credentialdomain.VaultSessionConfig{
			CreatedAt: now, IdleTimeout: time.Minute, AbsoluteTimeout: time.Hour,
			MaxHandles:            4,
			AllowedOriginBindings: [][cryptokit.OriginBindingSize]byte{{1}},
		},
	)
	if err != nil {
		bundle.Destroy()
		t.Fatal(err)
	}
	return session
}

func eventIDPattern(start byte) protocol.EventID {
	var value protocol.EventID
	for index := range value {
		value[index] = start + byte(index)
	}
	return value
}

func credentialIDPattern(start byte) protocol.CredentialID {
	var value protocol.CredentialID
	for index := range value {
		value[index] = start + byte(index)
	}
	return value
}

func deviceIDPattern(start byte) protocol.DeviceID {
	var value protocol.DeviceID
	for index := range value {
		value[index] = start + byte(index)
	}
	return value
}

func digestPattern(start byte) [32]byte {
	var value [32]byte
	for index := range value {
		value[index] = start + byte(index)
	}
	return value
}
