package domain

import (
	"context"
	"crypto/sha256"
	"errors"

	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
)

var (
	ErrCloudObjectMissing = errors.New("sync cloud object is missing")
	ErrCloudObjectCorrupt = errors.New("sync cloud object is corrupt")
	ErrCloudCursor        = errors.New("sync cloud cursor is invalid")
)

// ManifestRecord contains only signed public control bytes. The cloud does not
// interpret them or select a current credential version.
type ManifestRecord struct {
	NamespaceID    protocol.NamespaceID
	ManifestDigest [sha256.Size]byte
	SigInputCBOR   []byte
	Signature      protocol.Signature
}

func RecordFromManifest(manifest *SignedManifest) (ManifestRecord, error) {
	if manifest == nil {
		return ManifestRecord{}, ErrInvalidSyncManifest
	}
	payload := manifest.Payload()
	return ManifestRecord{
		NamespaceID: payload.NamespaceID, ManifestDigest: manifest.Digest(),
		SigInputCBOR: manifest.SigInputCBOR(), Signature: manifest.Signature(),
	}, nil
}

type ManifestPage struct {
	Items      []ManifestRecord
	NextCursor string
}

type CloudStore interface {
	PutObject(context.Context, platform.ObjectRef, []byte) error
	FetchObject(context.Context, platform.ObjectRef) ([]byte, error)
	PublishManifest(context.Context, ManifestRecord, []ObjectReference) error
	PullManifests(
		context.Context,
		protocol.NamespaceID,
		string,
		int,
	) (ManifestPage, error)
}
