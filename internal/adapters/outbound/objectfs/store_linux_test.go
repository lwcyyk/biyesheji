//go:build linux

package objectfs

import (
	"bytes"
	"context"
	"crypto/sha256"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"testing"
	"time"

	"vdns.local/vdns/internal/platform"
)

func TestPutGetHasAndDuplicateReuse(t *testing.T) {
	t.Parallel()
	store := newTestStore(t)
	object := []byte("VDNS encrypted object bytes")

	first, err := store.PutIfAbsent(context.Background(), object)
	if err != nil {
		t.Fatal(err)
	}
	second, err := store.PutIfAbsent(context.Background(), append([]byte(nil), object...))
	if err != nil {
		t.Fatal(err)
	}
	if first != second || first.Digest != sha256.Sum256(object) || first.Size != uint64(len(object)) {
		t.Fatal("content address or duplicate reuse differs")
	}
	relative, err := store.RelativePath(first)
	if err != nil {
		t.Fatal(err)
	}
	wantRelative := "objects/sha256/" + firstDigestPrefix(first, 0, 2) + "/" + firstDigestPrefix(first, 2, 4) + "/" +
		firstDigestPrefix(first, 0, 64) + ".obj"
	if relative != wantRelative {
		t.Fatalf("relative path = %q, want %q", relative, wantRelative)
	}

	present, err := store.Has(context.Background(), first)
	if err != nil || !present {
		t.Fatalf("Has = %v, %v", present, err)
	}
	loaded, err := store.Get(context.Background(), first)
	if err != nil {
		t.Fatal(err)
	}
	defer clear(loaded)
	if !bytes.Equal(loaded, object) {
		t.Fatal("loaded object differs")
	}

	path, _, err := store.pathFor(first)
	if err != nil {
		t.Fatal(err)
	}
	info, err := os.Stat(path)
	if err != nil {
		t.Fatal(err)
	}
	if info.Mode().Perm() != 0o600 {
		t.Fatalf("object mode = %o, want 600", info.Mode().Perm())
	}
	entries, err := os.ReadDir(store.temporaryRoot)
	if err != nil {
		t.Fatal(err)
	}
	if len(entries) != 0 {
		t.Fatalf("successful commit left %d temporary files", len(entries))
	}
}

func firstDigestPrefix(reference platform.ObjectRef, start, end int) string {
	return fmt.Sprintf("%x", reference.Digest)[start:end]
}

func TestCorruptionIsRejectedAndNeverOverwritten(t *testing.T) {
	t.Parallel()
	store := newTestStore(t)
	object := []byte("ciphertext that must remain immutable")
	reference, err := store.PutIfAbsent(context.Background(), object)
	if err != nil {
		t.Fatal(err)
	}
	path, _, err := store.pathFor(reference)
	if err != nil {
		t.Fatal(err)
	}
	corrupt := bytes.Repeat([]byte{0xff}, len(object))
	if err := os.WriteFile(path, corrupt, 0o600); err != nil {
		t.Fatal(err)
	}
	if _, err := store.Get(context.Background(), reference); !errors.Is(err, ErrObjectCorrupt) {
		t.Fatalf("Get corrupt error = %v", err)
	}
	if _, err := store.PutIfAbsent(context.Background(), object); !errors.Is(err, ErrObjectCorrupt) {
		t.Fatalf("Put over corrupt final error = %v", err)
	}
	remains, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(remains, corrupt) {
		t.Fatal("corrupt address was silently overwritten")
	}
}

func TestSymlinkAndUnsafeRootsAreRejected(t *testing.T) {
	t.Parallel()
	base := t.TempDir()
	realRoot := filepath.Join(base, "real")
	if err := os.Mkdir(realRoot, 0o700); err != nil {
		t.Fatal(err)
	}
	linkedRoot := filepath.Join(base, "linked")
	if err := os.Symlink(realRoot, linkedRoot); err != nil {
		t.Fatal(err)
	}
	if _, err := New(linkedRoot); !errors.Is(err, ErrInvalidDataRoot) {
		t.Fatalf("symlinked root error = %v", err)
	}
	linkedParent := filepath.Join(base, "linked-parent")
	if err := os.Symlink(realRoot, linkedParent); err != nil {
		t.Fatal(err)
	}
	if _, err := New(filepath.Join(linkedParent, "child")); !errors.Is(err, ErrInvalidDataRoot) {
		t.Fatalf("symlinked parent error = %v", err)
	}

	store := newTestStore(t)
	reference := platform.ObjectRef{Digest: sha256.Sum256([]byte("target")), Size: 6}
	path, directory, err := store.pathFor(reference)
	if err != nil {
		t.Fatal(err)
	}
	if err := ensurePrivateDirectory(filepath.Dir(directory)); err != nil {
		t.Fatal(err)
	}
	if err := ensurePrivateDirectory(directory); err != nil {
		t.Fatal(err)
	}
	target := filepath.Join(t.TempDir(), "target")
	if err := os.WriteFile(target, []byte("target"), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(target, path); err != nil {
		t.Fatal(err)
	}
	if _, err := store.Get(context.Background(), reference); !errors.Is(err, ErrUnsafeObjectPath) {
		t.Fatalf("symlinked object error = %v", err)
	}
}

func TestRecoverTemporaryQuarantinesOnlyStaleRegularFiles(t *testing.T) {
	t.Parallel()
	store := newTestStore(t)
	stale := filepath.Join(store.temporaryRoot, "pending-stale")
	fresh := filepath.Join(store.temporaryRoot, "pending-fresh")
	if err := os.WriteFile(stale, []byte("partial"), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(fresh, []byte("active"), 0o600); err != nil {
		t.Fatal(err)
	}
	staleTime := time.Now().Add(-2 * time.Hour)
	if err := os.Chtimes(stale, staleTime, staleTime); err != nil {
		t.Fatal(err)
	}

	report, err := store.RecoverTemporary(context.Background(), time.Now().Add(-time.Hour))
	if err != nil {
		t.Fatal(err)
	}
	if report.Quarantined != 1 || report.Skipped != 1 {
		t.Fatalf("recovery report = %+v", report)
	}
	if _, err := os.Stat(stale); !errors.Is(err, os.ErrNotExist) {
		t.Fatalf("stale temporary still present: %v", err)
	}
	if _, err := os.Stat(fresh); err != nil {
		t.Fatalf("fresh temporary moved: %v", err)
	}
	quarantined, err := os.ReadDir(store.quarantine)
	if err != nil {
		t.Fatal(err)
	}
	if len(quarantined) != 1 {
		t.Fatalf("quarantine files = %d, want 1", len(quarantined))
	}
}

func TestLimitsMissingAndCancellation(t *testing.T) {
	t.Parallel()
	store := newTestStore(t)
	if _, err := store.PutIfAbsent(context.Background(), nil); !errors.Is(err, ErrInvalidObject) {
		t.Fatalf("empty object error = %v", err)
	}
	if _, err := store.PutIfAbsent(context.Background(), make([]byte, MaxObjectSize+1)); !errors.Is(err, ErrInvalidObject) {
		t.Fatalf("oversize object error = %v", err)
	}
	missing := platform.ObjectRef{Digest: sha256.Sum256([]byte("missing")), Size: 7}
	if present, err := store.Has(context.Background(), missing); err != nil || present {
		t.Fatalf("missing Has = %v, %v", present, err)
	}
	cancelled, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := store.PutIfAbsent(cancelled, []byte("value")); !errors.Is(err, context.Canceled) {
		t.Fatalf("cancelled Put error = %v", err)
	}
}

func newTestStore(t *testing.T) *Store {
	t.Helper()
	store, err := New(filepath.Join(t.TempDir(), "data"))
	if err != nil {
		t.Fatal(err)
	}
	return store
}
