package sqlite

import (
	"context"
	"crypto/sha256"
	"testing"

	"github.com/google/uuid"

	localports "vpass.local/vpass/internal/localapi/ports"
)

func TestLocalOperationRepositoryRetainsPendingAndUnknown(t *testing.T) {
	t.Parallel()
	repository, _ := NewLocalAPIRepository(openTestDatabase(t))
	record := localports.LocalOperation{
		OperationID: uuid.NewString(), OperationKind: "SYNC_PULL",
		RequestHash: sha256.Sum256([]byte("request")), State: "PENDING",
		ResultReference: "local-operation:sync_pull",
		CreatedAtMS:     10, UpdatedAtMS: 10,
	}
	if err := repository.PutOperation(context.Background(), record); err != nil {
		t.Fatal(err)
	}
	loaded, found, err := repository.LoadOperation(context.Background(), record.OperationID)
	if err != nil || !found || loaded.State != "PENDING" {
		t.Fatalf("LoadOperation = %+v, %v, %v", loaded, found, err)
	}
	record.State = "UNKNOWN"
	record.UpdatedAtMS = 11
	if err := repository.PutOperation(context.Background(), record); err != nil {
		t.Fatal(err)
	}
	loaded, found, err = repository.LoadOperation(context.Background(), record.OperationID)
	if err != nil || !found || loaded.State != "UNKNOWN" {
		t.Fatalf("unknown LoadOperation = %+v, %v, %v", loaded, found, err)
	}
}
