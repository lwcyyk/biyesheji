package application

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"testing"

	"vdns.local/vdns/internal/adapters/outbound/memoryanchor"
	anchordomain "vdns.local/vdns/internal/anchor/domain"
	"vdns.local/vdns/internal/protocol"
)

func TestPublisherLabelsSimulatorAndRejectsProviderMismatch(t *testing.T) {
	provider := memoryanchor.New()
	publisher, err := NewPublisher(provider)
	if err != nil {
		t.Fatal(err)
	}
	checkpoint := publisherCheckpoint(t, anchordomain.ProviderSimulated)
	receipt, err := publisher.Publish(context.Background(), checkpoint)
	if err != nil || receipt.ProviderKind != anchordomain.ProviderSimulated ||
		receipt.ProviderKind.Name() != "SIMULATED" || provider.Count() != 1 {
		t.Fatalf("receipt = %+v, count=%d, err=%v", receipt, provider.Count(), err)
	}
	if _, err := publisher.Publish(context.Background(), checkpoint); err != nil ||
		provider.Count() != 1 {
		t.Fatalf("idempotent publish count=%d, err=%v", provider.Count(), err)
	}
	anvilCheckpoint := publisherCheckpoint(t, anchordomain.ProviderAnvil)
	if _, err := publisher.Publish(context.Background(), anvilCheckpoint); err != ErrProviderKindMismatch {
		t.Fatalf("provider mismatch error = %v", err)
	}
}

func publisherCheckpoint(
	t *testing.T,
	kind anchordomain.ProviderKind,
) *anchordomain.SignedCheckpoint {
	t.Helper()
	namespace := protocol.NamespaceID{1, 2, 3}
	key := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x61}, ed25519.SeedSize))
	value := func(marker byte) [sha256.Size]byte {
		var result [sha256.Size]byte
		for index := range result {
			result[index] = marker
		}
		return result
	}
	checkpoint, err := anchordomain.SignCheckpoint(
		key, "publisher-chain", 1,
		anchordomain.CheckpointPayload{
			NamespaceID:        namespace,
			NamespaceStateRoot: value(1), DeviceStateRoot: value(2),
			CredentialStateRoot: value(3), AuditLogRoot: value(4),
			RevocationRoot: value(5), CryptoPolicyHash: value(6),
			CheckpointHeight: 7, FinalSequence: 8, ProviderKind: kind,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	return checkpoint
}
