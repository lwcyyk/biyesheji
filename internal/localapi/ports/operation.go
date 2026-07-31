package ports

import (
	"context"
	"crypto/sha256"
)

type LocalOperation struct {
	OperationID     string
	OperationKind   string
	NamespaceID     []byte
	DeviceID        []byte
	RequestHash     [sha256.Size]byte
	State           string
	ResultReference string
	ErrorCode       string
	CreatedAtMS     uint64
	UpdatedAtMS     uint64
}

type OperationStore interface {
	PutOperation(context.Context, LocalOperation) error
	LoadOperation(context.Context, string) (LocalOperation, bool, error)
}
