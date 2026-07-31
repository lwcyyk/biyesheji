// Package application coordinates append-only log state and signed tree heads.
package application

import (
	"crypto/ed25519"
	"errors"
	"sync"

	"vdns.local/vdns/internal/protocol"
	transparencydomain "vdns.local/vdns/internal/transparency/domain"
)

var (
	ErrLogConfiguration = errors.New("invalid transparency log configuration")
	ErrLogSequence      = errors.New("transparency log final sequence is not monotonic")
)

// Log serializes appends and signs every resulting head. Durable adapters may
// persist the returned leaf/head pair in one transaction.
type Log struct {
	mu            sync.RWMutex
	namespaceID   protocol.NamespaceID
	logID         transparencydomain.LogID
	chainID       string
	keyGeneration uint64
	privateKey    ed25519.PrivateKey
	tree          *transparencydomain.Tree
	finalSequence uint64
}

func NewLog(
	namespaceID protocol.NamespaceID,
	logID transparencydomain.LogID,
	chainID string,
	keyGeneration uint64,
	privateKey ed25519.PrivateKey,
) (*Log, error) {
	if namespaceID == (protocol.NamespaceID{}) ||
		logID == (transparencydomain.LogID{}) ||
		chainID == "" || keyGeneration == 0 ||
		len(privateKey) != ed25519.PrivateKeySize {
		return nil, ErrLogConfiguration
	}
	return &Log{
		namespaceID: namespaceID, logID: logID, chainID: chainID,
		keyGeneration: keyGeneration,
		privateKey:    append(ed25519.PrivateKey(nil), privateKey...),
		tree:          transparencydomain.NewTree(),
	}, nil
}

func (log *Log) Append(
	leaf transparencydomain.LogLeaf,
) (uint64, [32]byte, *transparencydomain.SignedTreeHead, error) {
	if log == nil {
		return 0, [32]byte{}, nil, ErrLogConfiguration
	}
	log.mu.Lock()
	defer log.mu.Unlock()
	if leaf.FinalSequence <= log.finalSequence {
		return 0, [32]byte{}, nil, ErrLogSequence
	}
	index, leafHash, err := log.tree.Append(leaf)
	if err != nil {
		return 0, [32]byte{}, nil, err
	}
	head, err := transparencydomain.SignTreeHead(
		log.privateKey, log.chainID, log.keyGeneration,
		transparencydomain.TreeHeadPayload{
			NamespaceID: log.namespaceID, LogID: log.logID,
			TreeSize: log.tree.Size(), RootHash: log.tree.Root(),
			FinalSequence: leaf.FinalSequence, SuiteID: protocol.SuiteID,
		},
	)
	if err != nil {
		return 0, [32]byte{}, nil, err
	}
	log.finalSequence = leaf.FinalSequence
	return index, leafHash, head, nil
}

func (log *Log) InclusionProof(
	leafIndex, treeSize uint64,
) ([][32]byte, error) {
	if log == nil {
		return nil, ErrLogConfiguration
	}
	log.mu.RLock()
	defer log.mu.RUnlock()
	return log.tree.InclusionProof(leafIndex, treeSize)
}

func (log *Log) ConsistencyProof(
	oldSize, newSize uint64,
) ([][32]byte, error) {
	if log == nil {
		return nil, ErrLogConfiguration
	}
	log.mu.RLock()
	defer log.mu.RUnlock()
	return log.tree.ConsistencyProof(oldSize, newSize)
}
