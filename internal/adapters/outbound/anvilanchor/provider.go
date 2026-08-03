// Package anvilanchor adapts a local Anvil JSON-RPC client boundary without
// claiming production consensus or finality.
package anvilanchor

import (
	"context"
	"crypto/sha256"
	"errors"
	"strings"

	anchordomain "vpass.local/vpass/internal/anchor/domain"
)

var ErrAnvilPublication = errors.New("Anvil checkpoint publication failed")

// Client is implemented by the G5/G7 chain RPC boundary or a deterministic
// fake. Raw credentials and signing keys never cross this interface.
type Client interface {
	PublishCheckpoint(
		context.Context,
		[]byte,
		[sha256.Size]byte,
	) (transactionHash string, blockHeight uint64, err error)
}

type Provider struct {
	client Client
}

func New(client Client) (*Provider, error) {
	if client == nil {
		return nil, ErrAnvilPublication
	}
	return &Provider{client: client}, nil
}

func (*Provider) Kind() anchordomain.ProviderKind {
	return anchordomain.ProviderAnvil
}

func (provider *Provider) Announce(
	ctx context.Context,
	announcement anchordomain.PublicAnnouncement,
) (anchordomain.AnnouncementReceipt, error) {
	if provider == nil || provider.client == nil || ctx == nil ||
		announcement.Validate() != nil ||
		announcement.Payload.ProviderKind != anchordomain.ProviderAnvil {
		return anchordomain.AnnouncementReceipt{}, ErrAnvilPublication
	}
	txHash, height, err := provider.client.PublishCheckpoint(
		ctx, append([]byte(nil), announcement.CheckpointObject...),
		announcement.CheckpointDigest,
	)
	if err != nil || strings.TrimSpace(txHash) == "" || height == 0 {
		return anchordomain.AnnouncementReceipt{}, ErrAnvilPublication
	}
	return anchordomain.AnnouncementReceipt{
		ProviderKind:      anchordomain.ProviderAnvil,
		CheckpointDigest:  announcement.CheckpointDigest,
		ExternalReference: txHash,
		ObservedHeight:    height,
	}, nil
}
