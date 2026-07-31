//go:build linux

// Package objectfs implements the durable, content-addressed ciphertext store.
// Callers provide complete encrypted object bytes; this package never accepts
// plaintext metadata or constructs object headers.
package objectfs

import (
	"context"
	"crypto/sha256"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"

	"golang.org/x/sys/unix"

	"vdns.local/vdns/internal/platform"
)

const (
	// MaxObjectSize matches the largest frozen first-version object class,
	// ProofBundle. Smaller object types enforce their own limits before this
	// infrastructure boundary.
	MaxObjectSize = 1 << 20
	objectSuffix  = ".obj"
)

var (
	ErrInvalidDataRoot    = errors.New("invalid object-store data root")
	ErrInvalidObject      = errors.New("invalid ciphertext object")
	ErrObjectNotFound     = errors.New("ciphertext object not found")
	ErrObjectCorrupt      = errors.New("ciphertext object is corrupt")
	ErrUnsafeObjectPath   = errors.New("unsafe object-store path")
	ErrAtomicMoveRequired = errors.New("atomic no-replace rename is unavailable")
)

// Store keeps immutable object bytes under a private data root.
type Store struct {
	dataRoot      string
	objectsRoot   string
	temporaryRoot string
	quarantine    string
}

// RecoveryReport describes stale temporary files moved out of the commit
// path. Quarantine is recoverable and intentionally separate from GC.
type RecoveryReport struct {
	Quarantined int
	Skipped     int
}

// New creates the private directory layout and rejects symlinked roots.
func New(dataRoot string) (*Store, error) {
	if strings.TrimSpace(dataRoot) == "" {
		return nil, ErrInvalidDataRoot
	}
	absolute, err := filepath.Abs(dataRoot)
	if err != nil || absolute == string(filepath.Separator) {
		return nil, ErrInvalidDataRoot
	}
	if err := rejectSymlinkComponents(absolute); err != nil {
		return nil, fmt.Errorf("%w: %v", ErrInvalidDataRoot, err)
	}
	if err := ensurePrivateDirectory(absolute); err != nil {
		return nil, fmt.Errorf("%w: %v", ErrInvalidDataRoot, err)
	}
	store := &Store{
		dataRoot:      absolute,
		objectsRoot:   filepath.Join(absolute, "objects", "sha256"),
		temporaryRoot: filepath.Join(absolute, "objects", ".tmp"),
		quarantine:    filepath.Join(absolute, "objects", ".quarantine"),
	}
	for _, directory := range []string{
		filepath.Join(absolute, "objects"),
		store.objectsRoot,
		store.temporaryRoot,
		store.quarantine,
	} {
		if err := ensurePrivateDirectory(directory); err != nil {
			return nil, err
		}
	}
	return store, nil
}

// PutIfAbsent durably publishes bytes at their SHA-256 address. An existing
// object is reused only after its length and digest have been revalidated.
func (store *Store) PutIfAbsent(ctx context.Context, object []byte) (platform.ObjectRef, error) {
	if store == nil || ctx == nil || len(object) == 0 || len(object) > MaxObjectSize {
		return platform.ObjectRef{}, ErrInvalidObject
	}
	if err := ctx.Err(); err != nil {
		return platform.ObjectRef{}, err
	}
	digest := sha256.Sum256(object)
	reference := platform.ObjectRef{Digest: digest, Size: uint64(len(object))}
	finalPath, finalDirectory, err := store.pathFor(reference)
	if err != nil {
		return platform.ObjectRef{}, err
	}
	if err := ensurePrivateDirectory(filepath.Dir(finalDirectory)); err != nil {
		return platform.ObjectRef{}, err
	}
	if err := ensurePrivateDirectory(finalDirectory); err != nil {
		return platform.ObjectRef{}, err
	}

	if present, err := validateFile(finalPath, reference); present || err != nil {
		if err != nil {
			return platform.ObjectRef{}, err
		}
		return reference, nil
	}

	temporary, err := os.CreateTemp(store.temporaryRoot, "pending-*")
	if err != nil {
		return platform.ObjectRef{}, err
	}
	temporaryPath := temporary.Name()
	keepTemporary := true
	defer func() {
		_ = temporary.Close()
		if !keepTemporary {
			_ = os.Remove(temporaryPath)
		}
	}()
	if err := temporary.Chmod(0o600); err != nil {
		return platform.ObjectRef{}, err
	}
	if err := writeAll(ctx, temporary, object); err != nil {
		return platform.ObjectRef{}, err
	}
	if err := temporary.Sync(); err != nil {
		return platform.ObjectRef{}, err
	}
	if err := temporary.Close(); err != nil {
		return platform.ObjectRef{}, err
	}
	if present, err := validateFile(temporaryPath, reference); !present || err != nil {
		if err == nil {
			err = ErrObjectCorrupt
		}
		return platform.ObjectRef{}, err
	}
	if err := ctx.Err(); err != nil {
		return platform.ObjectRef{}, err
	}

	err = unix.Renameat2(
		unix.AT_FDCWD,
		temporaryPath,
		unix.AT_FDCWD,
		finalPath,
		unix.RENAME_NOREPLACE,
	)
	switch {
	case err == nil:
		keepTemporary = false
		if err := syncDirectory(finalDirectory); err != nil {
			return platform.ObjectRef{}, err
		}
	case errors.Is(err, unix.EEXIST):
		if present, validateErr := validateFile(finalPath, reference); !present || validateErr != nil {
			if validateErr == nil {
				validateErr = ErrObjectCorrupt
			}
			return platform.ObjectRef{}, validateErr
		}
		keepTemporary = false
	case errors.Is(err, unix.ENOSYS), errors.Is(err, unix.EINVAL), errors.Is(err, unix.ENOTSUP):
		return platform.ObjectRef{}, ErrAtomicMoveRequired
	default:
		return platform.ObjectRef{}, err
	}
	return reference, nil
}

// Get loads and revalidates the exact immutable bytes.
func (store *Store) Get(ctx context.Context, reference platform.ObjectRef) ([]byte, error) {
	if store == nil || ctx == nil || reference.Size == 0 || reference.Size > MaxObjectSize {
		return nil, ErrInvalidObject
	}
	path, _, err := store.pathFor(reference)
	if err != nil {
		return nil, err
	}
	file, err := openRegularNoFollow(path)
	if errors.Is(err, os.ErrNotExist) {
		return nil, ErrObjectNotFound
	}
	if err != nil {
		return nil, err
	}
	defer file.Close()
	info, err := file.Stat()
	if err != nil {
		return nil, err
	}
	if info.Size() != int64(reference.Size) || info.Size() > MaxObjectSize {
		return nil, ErrObjectCorrupt
	}
	object := make([]byte, reference.Size)
	if _, err := io.ReadFull(&contextReader{ctx: ctx, reader: file}, object); err != nil {
		clear(object)
		return nil, ErrObjectCorrupt
	}
	var trailing [1]byte
	if count, err := file.Read(trailing[:]); count != 0 || (err != nil && !errors.Is(err, io.EOF)) {
		clear(object)
		return nil, ErrObjectCorrupt
	}
	actual := sha256.Sum256(object)
	if actual != reference.Digest {
		clear(object)
		return nil, ErrObjectCorrupt
	}
	return object, nil
}

// Has returns true only for a present object whose full bytes still match the
// requested reference. Corruption is an error, never a cache miss.
func (store *Store) Has(ctx context.Context, reference platform.ObjectRef) (bool, error) {
	object, err := store.Get(ctx, reference)
	if errors.Is(err, ErrObjectNotFound) {
		return false, nil
	}
	if err != nil {
		return false, err
	}
	clear(object)
	return true, nil
}

// RelativePath returns the normalized database locator for an object. It does
// not touch the filesystem and never exposes the absolute data root.
func (store *Store) RelativePath(reference platform.ObjectRef) (string, error) {
	if store == nil {
		return "", ErrInvalidObject
	}
	path, _, err := store.pathFor(reference)
	if err != nil {
		return "", err
	}
	relative, err := filepath.Rel(store.dataRoot, path)
	if err != nil || relative == "." || strings.HasPrefix(relative, ".."+string(filepath.Separator)) {
		return "", ErrUnsafeObjectPath
	}
	return filepath.ToSlash(relative), nil
}

// RecoverTemporary moves regular stale temporary files into quarantine. It
// never follows links and never deletes potentially useful bytes.
func (store *Store) RecoverTemporary(ctx context.Context, olderThan time.Time) (RecoveryReport, error) {
	var report RecoveryReport
	if store == nil || ctx == nil || olderThan.IsZero() {
		return report, ErrInvalidObject
	}
	entries, err := os.ReadDir(store.temporaryRoot)
	if err != nil {
		return report, err
	}
	for _, entry := range entries {
		if err := ctx.Err(); err != nil {
			return report, err
		}
		info, err := entry.Info()
		if err != nil {
			return report, err
		}
		if !info.Mode().IsRegular() || !info.ModTime().Before(olderThan) {
			report.Skipped++
			continue
		}
		source := filepath.Join(store.temporaryRoot, entry.Name())
		destination, err := uniqueQuarantinePath(store.quarantine, entry.Name())
		if err != nil {
			return report, err
		}
		if err := unix.Renameat2(
			unix.AT_FDCWD,
			source,
			unix.AT_FDCWD,
			destination,
			unix.RENAME_NOREPLACE,
		); err != nil {
			return report, err
		}
		report.Quarantined++
	}
	if report.Quarantined > 0 {
		if err := syncDirectory(store.temporaryRoot); err != nil {
			return report, err
		}
		if err := syncDirectory(store.quarantine); err != nil {
			return report, err
		}
	}
	return report, nil
}

func (store *Store) pathFor(reference platform.ObjectRef) (string, string, error) {
	if reference.Size == 0 || reference.Size > MaxObjectSize {
		return "", "", ErrInvalidObject
	}
	hexDigest := fmt.Sprintf("%x", reference.Digest)
	directory := filepath.Join(store.objectsRoot, hexDigest[:2], hexDigest[2:4])
	path := filepath.Join(directory, hexDigest+objectSuffix)
	if !pathWithin(store.objectsRoot, path) {
		return "", "", ErrUnsafeObjectPath
	}
	return path, directory, nil
}

func validateFile(path string, reference platform.ObjectRef) (bool, error) {
	file, err := openRegularNoFollow(path)
	if errors.Is(err, os.ErrNotExist) {
		return false, nil
	}
	if err != nil {
		return false, err
	}
	defer file.Close()
	info, err := file.Stat()
	if err != nil {
		return false, err
	}
	if info.Size() != int64(reference.Size) || info.Size() <= 0 || info.Size() > MaxObjectSize {
		return true, ErrObjectCorrupt
	}
	hash := sha256.New()
	written, err := io.Copy(hash, io.LimitReader(file, MaxObjectSize+1))
	if err != nil || written != info.Size() || written != int64(reference.Size) {
		return true, ErrObjectCorrupt
	}
	var actual [sha256.Size]byte
	copy(actual[:], hash.Sum(nil))
	if actual != reference.Digest {
		return true, ErrObjectCorrupt
	}
	return true, nil
}

func openRegularNoFollow(path string) (*os.File, error) {
	descriptor, err := unix.Open(path, unix.O_RDONLY|unix.O_CLOEXEC|unix.O_NOFOLLOW, 0)
	if err != nil {
		if errors.Is(err, unix.ENOENT) {
			return nil, os.ErrNotExist
		}
		if errors.Is(err, unix.ELOOP) {
			return nil, ErrUnsafeObjectPath
		}
		return nil, err
	}
	file := os.NewFile(uintptr(descriptor), path)
	info, err := file.Stat()
	if err != nil {
		_ = file.Close()
		return nil, err
	}
	if !info.Mode().IsRegular() {
		_ = file.Close()
		return nil, ErrUnsafeObjectPath
	}
	return file, nil
}

func writeAll(ctx context.Context, destination *os.File, value []byte) error {
	for len(value) > 0 {
		if err := ctx.Err(); err != nil {
			return err
		}
		count, err := destination.Write(value)
		if err != nil {
			return err
		}
		if count <= 0 {
			return io.ErrShortWrite
		}
		value = value[count:]
	}
	return nil
}

func ensurePrivateDirectory(path string) error {
	info, err := os.Lstat(path)
	created := false
	if errors.Is(err, os.ErrNotExist) {
		if err := os.Mkdir(path, 0o700); err != nil && !errors.Is(err, os.ErrExist) {
			return err
		}
		created = true
		info, err = os.Lstat(path)
	}
	if err != nil {
		return err
	}
	if info.Mode()&os.ModeSymlink != 0 || !info.IsDir() || info.Mode().Perm()&0o077 != 0 {
		return ErrUnsafeObjectPath
	}
	if created {
		if err := syncDirectory(filepath.Dir(path)); err != nil {
			return err
		}
	}
	return nil
}

func rejectSymlinkComponents(path string) error {
	clean := filepath.Clean(path)
	current := string(filepath.Separator)
	for _, component := range strings.Split(strings.TrimPrefix(clean, string(filepath.Separator)), string(filepath.Separator)) {
		if component == "" {
			continue
		}
		current = filepath.Join(current, component)
		info, err := os.Lstat(current)
		if errors.Is(err, os.ErrNotExist) {
			return nil
		}
		if err != nil {
			return err
		}
		if info.Mode()&os.ModeSymlink != 0 {
			return ErrUnsafeObjectPath
		}
	}
	return nil
}

func syncDirectory(path string) error {
	directory, err := openDirectoryNoFollow(path)
	if err != nil {
		return err
	}
	defer directory.Close()
	return directory.Sync()
}

func openDirectoryNoFollow(path string) (*os.File, error) {
	descriptor, err := unix.Open(path, unix.O_RDONLY|unix.O_CLOEXEC|unix.O_DIRECTORY|unix.O_NOFOLLOW, 0)
	if err != nil {
		return nil, err
	}
	return os.NewFile(uintptr(descriptor), path), nil
}

func uniqueQuarantinePath(directory, base string) (string, error) {
	for attempt := 0; attempt < 32; attempt++ {
		candidate := filepath.Join(directory, fmt.Sprintf("%d-%d-%s", time.Now().UnixNano(), attempt, base))
		if _, err := os.Lstat(candidate); errors.Is(err, os.ErrNotExist) {
			return candidate, nil
		} else if err != nil {
			return "", err
		}
	}
	return "", os.ErrExist
}

func pathWithin(root, candidate string) bool {
	relative, err := filepath.Rel(root, candidate)
	return err == nil && relative != "." && relative != ".." && !strings.HasPrefix(relative, ".."+string(filepath.Separator)) && !filepath.IsAbs(relative)
}

type contextReader struct {
	ctx    context.Context
	reader io.Reader
}

func (reader *contextReader) Read(buffer []byte) (int, error) {
	if err := reader.ctx.Err(); err != nil {
		return 0, err
	}
	return reader.reader.Read(buffer)
}

var _ platform.CiphertextObjectStore = (*Store)(nil)
