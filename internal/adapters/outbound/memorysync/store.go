package memorysync

import (
	"context"
	"crypto/sha256"
	"encoding/base64"
	"errors"
	"strconv"
	"sync"

	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
	syncdomain "vdns.local/vdns/internal/sync/domain"
)

var (
	ErrInvalidMemorySync = errors.New("invalid memory sync request")
	ErrManifestConflict  = errors.New("sync manifest digest conflict")
)

// Faults are test-only read-path mutations. The underlying stored bytes remain
// unchanged so experiments can compare honest and adversarial views.
type Faults struct {
	OmitObject           *[sha256.Size]byte
	CorruptObject        *[sha256.Size]byte
	HideAfterIndex       *int
	ReverseManifestOrder bool
}

type storedManifest struct {
	record  syncdomain.ManifestRecord
	objects []syncdomain.ObjectReference
}

// Store is an untrusted-cloud simulator. It stores opaque bytes and signed
// manifests but has no API that returns a trusted current version.
type Store struct {
	mu        sync.RWMutex
	objects   map[[sha256.Size]byte][]byte
	manifests []storedManifest
	faults    Faults
}

func New() *Store {
	return &Store{objects: make(map[[sha256.Size]byte][]byte)}
}

func (store *Store) SetFaults(faults Faults) {
	if store == nil {
		return
	}
	store.mu.Lock()
	defer store.mu.Unlock()
	store.faults = faults
}

func (store *Store) PutObject(
	ctx context.Context,
	reference platform.ObjectRef,
	object []byte,
) error {
	if store == nil || ctx == nil || reference.Size == 0 ||
		uint64(len(object)) != reference.Size ||
		sha256.Sum256(object) != reference.Digest {
		return ErrInvalidMemorySync
	}
	if err := ctx.Err(); err != nil {
		return err
	}
	store.mu.Lock()
	defer store.mu.Unlock()
	if existing, found := store.objects[reference.Digest]; found {
		if sha256.Sum256(existing) != reference.Digest ||
			len(existing) != len(object) {
			return syncdomain.ErrCloudObjectCorrupt
		}
		return nil
	}
	store.objects[reference.Digest] = append([]byte(nil), object...)
	return nil
}

func (store *Store) FetchObject(
	ctx context.Context,
	reference platform.ObjectRef,
) ([]byte, error) {
	if store == nil || ctx == nil || reference.Size == 0 {
		return nil, ErrInvalidMemorySync
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	store.mu.RLock()
	defer store.mu.RUnlock()
	if store.faults.OmitObject != nil &&
		*store.faults.OmitObject == reference.Digest {
		return nil, syncdomain.ErrCloudObjectMissing
	}
	object, found := store.objects[reference.Digest]
	if !found {
		return nil, syncdomain.ErrCloudObjectMissing
	}
	result := append([]byte(nil), object...)
	if store.faults.CorruptObject != nil &&
		*store.faults.CorruptObject == reference.Digest &&
		len(result) != 0 {
		result[len(result)-1] ^= 1
		return result, nil
	}
	if uint64(len(result)) != reference.Size ||
		sha256.Sum256(result) != reference.Digest {
		return nil, syncdomain.ErrCloudObjectCorrupt
	}
	return result, nil
}

func (store *Store) PublishManifest(
	ctx context.Context,
	record syncdomain.ManifestRecord,
	objects []syncdomain.ObjectReference,
) error {
	if store == nil || ctx == nil || allZero(record.NamespaceID[:]) ||
		allZero(record.ManifestDigest[:]) || len(record.SigInputCBOR) == 0 ||
		len(objects) == 0 {
		return ErrInvalidMemorySync
	}
	if err := ctx.Err(); err != nil {
		return err
	}
	store.mu.Lock()
	defer store.mu.Unlock()
	for _, object := range objects {
		stored, found := store.objects[object.ObjectDigest]
		if !found || uint64(len(stored)) != object.Size ||
			sha256.Sum256(stored) != object.ObjectDigest {
			return syncdomain.ErrCloudObjectMissing
		}
	}
	for _, existing := range store.manifests {
		if existing.record.ManifestDigest == record.ManifestDigest {
			if existing.record.NamespaceID != record.NamespaceID ||
				!bytesEqual(existing.record.SigInputCBOR, record.SigInputCBOR) ||
				existing.record.Signature != record.Signature {
				return ErrManifestConflict
			}
			return nil
		}
	}
	clonedRecord := record
	clonedRecord.SigInputCBOR = append([]byte(nil), record.SigInputCBOR...)
	store.manifests = append(store.manifests, storedManifest{
		record:  clonedRecord,
		objects: cloneObjects(objects),
	})
	return nil
}

func (store *Store) PullManifests(
	ctx context.Context,
	namespaceID protocol.NamespaceID,
	cursor string,
	limit int,
) (syncdomain.ManifestPage, error) {
	if store == nil || ctx == nil || allZero(namespaceID[:]) ||
		limit < 1 || limit > 10_000 {
		return syncdomain.ManifestPage{}, ErrInvalidMemorySync
	}
	if err := ctx.Err(); err != nil {
		return syncdomain.ManifestPage{}, err
	}
	start, err := decodeCursor(cursor)
	if err != nil {
		return syncdomain.ManifestPage{}, err
	}
	store.mu.RLock()
	defer store.mu.RUnlock()
	visible := store.manifests
	if store.faults.HideAfterIndex != nil {
		end := *store.faults.HideAfterIndex
		if end < 0 {
			end = 0
		}
		if end < len(visible) {
			visible = visible[:end]
		}
	}
	filtered := make([]syncdomain.ManifestRecord, 0, len(visible))
	for _, manifest := range visible {
		if manifest.record.NamespaceID == namespaceID {
			filtered = append(filtered, cloneRecord(manifest.record))
		}
	}
	if store.faults.ReverseManifestOrder {
		for left, right := 0, len(filtered)-1; left < right; left, right = left+1, right-1 {
			filtered[left], filtered[right] = filtered[right], filtered[left]
		}
	}
	if start > len(filtered) {
		return syncdomain.ManifestPage{}, syncdomain.ErrCloudCursor
	}
	end := start + limit
	if end > len(filtered) {
		end = len(filtered)
	}
	page := syncdomain.ManifestPage{
		Items: append([]syncdomain.ManifestRecord(nil), filtered[start:end]...),
	}
	if end < len(filtered) {
		page.NextCursor = encodeCursor(end)
	}
	return page, nil
}

func encodeCursor(index int) string {
	return base64.RawURLEncoding.EncodeToString([]byte(strconv.Itoa(index)))
}

func decodeCursor(cursor string) (int, error) {
	if cursor == "" {
		return 0, nil
	}
	raw, err := base64.RawURLEncoding.DecodeString(cursor)
	if err != nil || base64.RawURLEncoding.EncodeToString(raw) != cursor {
		return 0, syncdomain.ErrCloudCursor
	}
	index, err := strconv.Atoi(string(raw))
	if err != nil || index < 0 {
		return 0, syncdomain.ErrCloudCursor
	}
	return index, nil
}

func cloneRecord(record syncdomain.ManifestRecord) syncdomain.ManifestRecord {
	record.SigInputCBOR = append([]byte(nil), record.SigInputCBOR...)
	return record
}

func cloneObjects(input []syncdomain.ObjectReference) []syncdomain.ObjectReference {
	result := make([]syncdomain.ObjectReference, len(input))
	for index, object := range input {
		result[index] = object
		if object.CredentialID != nil {
			value := *object.CredentialID
			result[index].CredentialID = &value
		}
		if object.Version != nil {
			value := *object.Version
			result[index].Version = &value
		}
	}
	return result
}

func allZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}

func bytesEqual(left, right []byte) bool {
	if len(left) != len(right) {
		return false
	}
	var difference byte
	for index := range left {
		difference |= left[index] ^ right[index]
	}
	return difference == 0
}

var _ syncdomain.CloudStore = (*Store)(nil)
