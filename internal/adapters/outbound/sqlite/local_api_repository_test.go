package sqlite

import (
	"context"
	"crypto/sha256"
	"errors"
	"testing"

	localports "vdns.local/vdns/internal/localapi/ports"
)

func TestLocalAPIRepositoryHashesKeysAndSurvivesRestart(t *testing.T) {
	t.Parallel()
	database := openTestDatabase(t)
	repository, err := NewLocalAPIRepository(database)
	if err != nil {
		t.Fatal(err)
	}
	keyHash := sha256.Sum256([]byte("idempotency-key-never-persisted"))
	requestHash := sha256.Sum256([]byte("canonical request"))
	record := localports.IdempotencyResponse{
		KeyHash: keyHash, OperationScope: "POST /api/v2/credentials",
		RequestHash: requestHash, Status: 201,
		Headers: map[string][]string{
			"Content-Type": {"application/json"},
			"Location":     {"/api/v2/credentials/example"},
		},
		Body:        []byte(`{"credentialId":"opaque"}`),
		CreatedAtMS: 100, ExpiresAtMS: 200,
	}
	if err := repository.Put(context.Background(), record); err != nil {
		t.Fatal(err)
	}
	loaded, found, err := repository.Load(context.Background(), keyHash, 150)
	if err != nil || !found || loaded.RequestHash != requestHash ||
		string(loaded.Body) != string(record.Body) {
		t.Fatalf("Load = %+v, %v, %v", loaded, found, err)
	}
	var plaintextCount int
	if err := database.QueryRowContext(
		context.Background(),
		"SELECT count(*) FROM local_api_idempotency_v2 WHERE CAST(key_hash AS TEXT) = ?",
		"idempotency-key-never-persisted",
	).Scan(&plaintextCount); err != nil {
		t.Fatal(err)
	}
	if plaintextCount != 0 {
		t.Fatal("plaintext idempotency key was persisted")
	}
	if _, found, err := repository.Load(context.Background(), keyHash, 200); err != nil || found {
		t.Fatalf("expired Load found=%v err=%v", found, err)
	}
}

func TestLocalAPIRepositoryConflictsAndHeaderAllowlist(t *testing.T) {
	t.Parallel()
	repository, _ := NewLocalAPIRepository(openTestDatabase(t))
	keyHash := sha256.Sum256([]byte("key"))
	first := localports.IdempotencyResponse{
		KeyHash: keyHash, OperationScope: "POST /one",
		RequestHash: sha256.Sum256([]byte("one")), Status: 201,
		Headers: map[string][]string{"Content-Type": {"application/json"}},
		Body:    []byte(`{}`), CreatedAtMS: 100, ExpiresAtMS: 200,
	}
	if err := repository.Put(context.Background(), first); err != nil {
		t.Fatal(err)
	}
	changed := first
	changed.RequestHash = sha256.Sum256([]byte("two"))
	if err := repository.Put(context.Background(), changed); !errors.Is(err, ErrLocalAPIConflict) {
		t.Fatalf("conflict error = %v", err)
	}
	unsafe := first
	unsafe.KeyHash = sha256.Sum256([]byte("other"))
	unsafe.Headers = map[string][]string{"Authorization": {"Bearer forbidden"}}
	if err := repository.Put(context.Background(), unsafe); !errors.Is(err, ErrInvalidLocalAPIRecord) {
		t.Fatalf("unsafe header error = %v", err)
	}
}
