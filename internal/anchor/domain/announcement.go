package domain

import (
	"crypto/sha256"
	"errors"
	"strings"
)

var ErrInvalidAnnouncement = errors.New("invalid checkpoint announcement")

// PublicAnnouncement contains the signed checkpoint object and its digest.
// The object can only decode as the CheckpointPayload whitelist.
type PublicAnnouncement struct {
	CheckpointDigest [sha256.Size]byte
	CheckpointObject []byte
	Payload          CheckpointPayload
}

func (announcement PublicAnnouncement) Validate() error {
	if bytesZero(announcement.CheckpointDigest[:]) ||
		len(announcement.CheckpointObject) == 0 ||
		announcement.Payload.Validate() != nil {
		return ErrInvalidAnnouncement
	}
	return nil
}

// AnnouncementReceipt is public operational evidence, not a consensus claim.
type AnnouncementReceipt struct {
	ProviderKind      ProviderKind
	CheckpointDigest  [sha256.Size]byte
	ExternalReference string
	ObservedHeight    uint64
}

func (receipt AnnouncementReceipt) Validate() error {
	if !receipt.ProviderKind.Valid() ||
		bytesZero(receipt.CheckpointDigest[:]) ||
		strings.TrimSpace(receipt.ExternalReference) == "" ||
		receipt.ObservedHeight == 0 {
		return ErrInvalidAnnouncement
	}
	return nil
}
