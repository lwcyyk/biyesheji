package memorysync

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"errors"
	"testing"

	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
	syncdomain "vdns.local/vdns/internal/sync/domain"
)

func TestStorePublishesImmutableObjectsAndPaginatesManifests(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	store := New()
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x71}, ed25519.SeedSize))
	namespaceID, deviceID := syncIDs()
	firstObject := []byte("encrypted-envelope-v1")
	secondObject := []byte("signed-state-v1")

	first, firstObjects := signedRecord(
		t, privateKey, namespaceID, deviceID, 1, 1,
		sha256.Sum256([]byte("checkpoint-0")),
		sha256.Sum256([]byte("checkpoint-1")),
		[][]byte{firstObject},
	)
	second, secondObjects := signedRecord(
		t, privateKey, namespaceID, deviceID, 2, 2,
		sha256.Sum256([]byte("checkpoint-1")),
		sha256.Sum256([]byte("checkpoint-2")),
		[][]byte{secondObject},
	)
	putObjects(t, ctx, store, firstObjects, [][]byte{firstObject})
	putObjects(t, ctx, store, secondObjects, [][]byte{secondObject})
	if err := store.PublishManifest(ctx, first, firstObjects); err != nil {
		t.Fatal(err)
	}
	if err := store.PublishManifest(ctx, first, firstObjects); err != nil {
		t.Fatalf("idempotent publish failed: %v", err)
	}
	if err := store.PublishManifest(ctx, second, secondObjects); err != nil {
		t.Fatal(err)
	}

	page, err := store.PullManifests(ctx, namespaceID, "", 1)
	if err != nil {
		t.Fatal(err)
	}
	if len(page.Items) != 1 || page.Items[0].ManifestDigest != first.ManifestDigest ||
		page.NextCursor == "" {
		t.Fatalf("unexpected first page: %+v", page)
	}
	page.Items[0].SigInputCBOR[0] ^= 1
	next, err := store.PullManifests(ctx, namespaceID, page.NextCursor, 1)
	if err != nil {
		t.Fatal(err)
	}
	if len(next.Items) != 1 || next.Items[0].ManifestDigest != second.ManifestDigest ||
		next.NextCursor != "" {
		t.Fatalf("unexpected second page: %+v", next)
	}
	reloaded, err := store.PullManifests(ctx, namespaceID, "", 1)
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(reloaded.Items[0].SigInputCBOR, first.SigInputCBOR) {
		t.Fatal("caller mutated stored manifest bytes")
	}

	got, err := store.FetchObject(ctx, reference(firstObjects[0]))
	if err != nil {
		t.Fatal(err)
	}
	got[0] ^= 1
	again, err := store.FetchObject(ctx, reference(firstObjects[0]))
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(again, firstObject) {
		t.Fatal("caller mutated stored object bytes")
	}
}

func TestStoreRejectsIncompletePublicationAndExposesAdversarialViews(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	store := New()
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x72}, ed25519.SeedSize))
	namespaceID, deviceID := syncIDs()
	object := []byte("encrypted-envelope")
	record, objects := signedRecord(
		t, privateKey, namespaceID, deviceID, 1, 1,
		sha256.Sum256([]byte("base")), sha256.Sum256([]byte("target")),
		[][]byte{object},
	)
	if err := store.PublishManifest(ctx, record, objects); !errors.Is(err, syncdomain.ErrCloudObjectMissing) {
		t.Fatalf("incomplete manifest publish error = %v", err)
	}
	putObjects(t, ctx, store, objects, [][]byte{object})
	if err := store.PublishManifest(ctx, record, objects); err != nil {
		t.Fatal(err)
	}

	digest := objects[0].ObjectDigest
	store.SetFaults(Faults{OmitObject: &digest})
	if _, err := store.FetchObject(ctx, reference(objects[0])); !errors.Is(err, syncdomain.ErrCloudObjectMissing) {
		t.Fatalf("omission error = %v", err)
	}
	store.SetFaults(Faults{CorruptObject: &digest})
	corrupt, err := store.FetchObject(ctx, reference(objects[0]))
	if err != nil {
		t.Fatal(err)
	}
	if sha256.Sum256(corrupt) == digest {
		t.Fatal("fault did not corrupt returned bytes")
	}
	hiddenAt := 0
	store.SetFaults(Faults{HideAfterIndex: &hiddenAt})
	page, err := store.PullManifests(ctx, namespaceID, "", 10)
	if err != nil {
		t.Fatal(err)
	}
	if len(page.Items) != 0 {
		t.Fatal("cloud equivocation view should be able to hide manifests")
	}
	if _, err := store.PullManifests(ctx, namespaceID, "not-a-canonical-cursor", 1); !errors.Is(err, syncdomain.ErrCloudCursor) {
		t.Fatalf("bad cursor error = %v", err)
	}
}

func TestStoreManifestOrderingIsNotAValiditySignal(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	store := New()
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x73}, ed25519.SeedSize))
	namespaceID, deviceID := syncIDs()
	var records []syncdomain.ManifestRecord
	for sequence := uint64(1); sequence <= 2; sequence++ {
		object := []byte{byte(sequence), 0xaa}
		record, objects := signedRecord(
			t, privateKey, namespaceID, deviceID, sequence, sequence,
			sha256.Sum256([]byte{byte(sequence - 1), 0xbb}),
			sha256.Sum256([]byte{byte(sequence), 0xbb}),
			[][]byte{object},
		)
		putObjects(t, ctx, store, objects, [][]byte{object})
		if err := store.PublishManifest(ctx, record, objects); err != nil {
			t.Fatal(err)
		}
		records = append(records, record)
	}
	store.SetFaults(Faults{ReverseManifestOrder: true})
	page, err := store.PullManifests(ctx, namespaceID, "", 10)
	if err != nil {
		t.Fatal(err)
	}
	if len(page.Items) != 2 ||
		page.Items[0].ManifestDigest != records[1].ManifestDigest ||
		page.Items[1].ManifestDigest != records[0].ManifestDigest {
		t.Fatal("reverse-order fault was not observable")
	}
}

func signedRecord(
	t *testing.T,
	privateKey ed25519.PrivateKey,
	namespaceID protocol.NamespaceID,
	deviceID protocol.DeviceID,
	counter uint64,
	sequence uint64,
	base [sha256.Size]byte,
	target [sha256.Size]byte,
	objectBytes [][]byte,
) (syncdomain.ManifestRecord, []syncdomain.ObjectReference) {
	t.Helper()
	var credentialID protocol.CredentialID
	copy(credentialID[:], bytes.Repeat([]byte{0x44}, len(credentialID)))
	objects := make([]syncdomain.ObjectReference, len(objectBytes))
	for index, object := range objectBytes {
		version := sequence
		objects[index] = syncdomain.ObjectReference{
			ObjectDigest: sha256.Sum256(object),
			ObjectType:   protocol.ObjectTypeCredentialEnvelope,
			CredentialID: &credentialID,
			Version:      &version,
			Size:         uint64(len(object)),
		}
	}
	manifest, err := syncdomain.SignManifest(
		privateKey, "sync-chain", 1, namespaceID, deviceID,
		base, target, counter, sequence, objects,
	)
	if err != nil {
		t.Fatal(err)
	}
	record, err := syncdomain.RecordFromManifest(manifest)
	if err != nil {
		t.Fatal(err)
	}
	return record, manifest.Objects()
}

func putObjects(
	t *testing.T,
	ctx context.Context,
	store *Store,
	objects []syncdomain.ObjectReference,
	objectBytes [][]byte,
) {
	t.Helper()
	for index, object := range objects {
		if err := store.PutObject(ctx, reference(object), objectBytes[index]); err != nil {
			t.Fatal(err)
		}
	}
}

func reference(object syncdomain.ObjectReference) platform.ObjectRef {
	return platform.ObjectRef{Digest: object.ObjectDigest, Size: object.Size}
}

func syncIDs() (protocol.NamespaceID, protocol.DeviceID) {
	var namespaceID protocol.NamespaceID
	var deviceID protocol.DeviceID
	copy(namespaceID[:], bytes.Repeat([]byte{0x11}, len(namespaceID)))
	copy(deviceID[:], bytes.Repeat([]byte{0x22}, len(deviceID)))
	return namespaceID, deviceID
}
