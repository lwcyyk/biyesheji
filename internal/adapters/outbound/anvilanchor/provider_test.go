package anvilanchor

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"testing"

	anchordomain "vpass.local/vpass/internal/anchor/domain"
	"vpass.local/vpass/internal/protocol"
)

type fakeClient struct {
	called bool
}

func (client *fakeClient) PublishCheckpoint(
	_ context.Context,
	object []byte,
	digest [sha256.Size]byte,
) (string, uint64, error) {
	client.called = len(object) != 0 && digest != [sha256.Size]byte{}
	return "0xabc123", 31337, nil
}

func TestAnvilProviderNeverClaimsConsensus(t *testing.T) {
	client := &fakeClient{}
	provider, err := New(client)
	if err != nil {
		t.Fatal(err)
	}
	if provider.Kind() != anchordomain.ProviderAnvil ||
		provider.Kind().Name() != "ANVIL" {
		t.Fatalf("kind = %v", provider.Kind())
	}
	checkpoint := anvilCheckpoint(t)
	object, _ := checkpoint.MarshalBinary()
	receipt, err := provider.Announce(
		context.Background(),
		anchordomain.PublicAnnouncement{
			CheckpointDigest: checkpoint.Digest(),
			CheckpointObject: object,
			Payload:          checkpoint.Payload(),
		},
	)
	if err != nil || !client.called ||
		receipt.ProviderKind != anchordomain.ProviderAnvil ||
		receipt.ProviderKind == anchordomain.ProviderConsensus {
		t.Fatalf("receipt=%+v called=%v err=%v", receipt, client.called, err)
	}
}

func anvilCheckpoint(t *testing.T) *anchordomain.SignedCheckpoint {
	t.Helper()
	key := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x71}, ed25519.SeedSize))
	hash := func(marker byte) [sha256.Size]byte {
		var result [sha256.Size]byte
		for index := range result {
			result[index] = marker
		}
		return result
	}
	checkpoint, err := anchordomain.SignCheckpoint(
		key, "anvil-31337", 1,
		anchordomain.CheckpointPayload{
			NamespaceID:        protocol.NamespaceID{1},
			NamespaceStateRoot: hash(1), DeviceStateRoot: hash(2),
			CredentialStateRoot: hash(3), AuditLogRoot: hash(4),
			RevocationRoot: hash(5), CryptoPolicyHash: hash(6),
			CheckpointHeight: 7, FinalSequence: 8,
			ProviderKind: anchordomain.ProviderAnvil,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	return checkpoint
}
