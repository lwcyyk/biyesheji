// Package application coordinates signed checkpoint publication.
package application

import (
	"context"
	"errors"

	anchordomain "vpass.local/vpass/internal/anchor/domain"
	"vpass.local/vpass/internal/anchor/ports"
)

var ErrProviderKindMismatch = errors.New("checkpoint provider kind mismatch")

type Publisher struct {
	provider ports.AnnouncementProvider
}

func NewPublisher(provider ports.AnnouncementProvider) (*Publisher, error) {
	if provider == nil || !provider.Kind().Valid() {
		return nil, anchordomain.ErrInvalidAnnouncement
	}
	return &Publisher{provider: provider}, nil
}

// Publish sends only the signed whitelist object to the configured provider.
func (publisher *Publisher) Publish(
	ctx context.Context,
	checkpoint *anchordomain.SignedCheckpoint,
) (anchordomain.AnnouncementReceipt, error) {
	if publisher == nil || publisher.provider == nil || ctx == nil ||
		checkpoint == nil {
		return anchordomain.AnnouncementReceipt{}, anchordomain.ErrInvalidAnnouncement
	}
	payload := checkpoint.Payload()
	if payload.ProviderKind != publisher.provider.Kind() {
		return anchordomain.AnnouncementReceipt{}, ErrProviderKindMismatch
	}
	object, err := checkpoint.MarshalBinary()
	if err != nil {
		return anchordomain.AnnouncementReceipt{}, err
	}
	announcement := anchordomain.PublicAnnouncement{
		CheckpointDigest: checkpoint.Digest(),
		CheckpointObject: object,
		Payload:          payload,
	}
	if announcement.Validate() != nil {
		return anchordomain.AnnouncementReceipt{}, anchordomain.ErrInvalidAnnouncement
	}
	receipt, err := publisher.provider.Announce(ctx, announcement)
	if err != nil {
		return anchordomain.AnnouncementReceipt{}, err
	}
	if receipt.Validate() != nil ||
		receipt.ProviderKind != publisher.provider.Kind() ||
		receipt.CheckpointDigest != checkpoint.Digest() {
		return anchordomain.AnnouncementReceipt{}, anchordomain.ErrInvalidAnnouncement
	}
	return receipt, nil
}
