package sqlite

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/json"
	"errors"
	"time"

	finalorderdomain "vpass.local/vpass/internal/finalorder/domain"
)

type FinalOrderSnapshotStore struct {
	database *Database
}

func NewFinalOrderSnapshotStore(database *Database) (*FinalOrderSnapshotStore, error) {
	if database == nil || database.db == nil {
		return nil, finalorderdomain.ErrPersistenceConflict
	}
	return &FinalOrderSnapshotStore{database: database}, nil
}

func (store *FinalOrderSnapshotStore) Load(
	ctx context.Context,
) (finalorderdomain.PersistentState, error) {
	if store == nil || ctx == nil {
		return finalorderdomain.PersistentState{}, finalorderdomain.ErrPersistenceConflict
	}
	var revision uint64
	var encoded []byte
	err := store.database.QueryRowContext(
		ctx,
		`SELECT revision, state_json
		   FROM final_order_snapshots_v2
		  WHERE adapter_kind = 'RESEARCH_ADAPTER'`,
	).Scan(&revision, &encoded)
	if errors.Is(err, sql.ErrNoRows) {
		return finalorderdomain.PersistentState{
			Idempotency: make(map[string][sha256.Size]byte),
		}, nil
	}
	if err != nil {
		return finalorderdomain.PersistentState{}, err
	}
	var state finalorderdomain.PersistentState
	if err := json.Unmarshal(encoded, &state); err != nil || state.Revision != revision {
		return finalorderdomain.PersistentState{}, finalorderdomain.ErrPersistenceConflict
	}
	if state.Idempotency == nil {
		state.Idempotency = make(map[string][sha256.Size]byte)
	}
	return state, nil
}

func (store *FinalOrderSnapshotStore) CompareAndSwap(
	ctx context.Context,
	expectedRevision uint64,
	state finalorderdomain.PersistentState,
) error {
	if store == nil || ctx == nil || state.Revision != expectedRevision+1 {
		return finalorderdomain.ErrPersistenceConflict
	}
	encoded, err := json.Marshal(state)
	if err != nil || len(encoded) > 16*1024*1024 {
		return finalorderdomain.ErrPersistenceConflict
	}
	transaction, err := store.database.BeginImmediate(ctx)
	if err != nil {
		return err
	}
	defer func() { _ = transaction.Rollback() }()
	var result sql.Result
	if expectedRevision == 0 {
		result, err = transaction.ExecContext(
			ctx,
			`INSERT INTO final_order_snapshots_v2(
			   adapter_kind, revision, state_json, updated_at_ms
			 ) VALUES('RESEARCH_ADAPTER', ?, ?, ?)`,
			state.Revision, encoded, time.Now().UnixMilli(),
		)
	} else {
		result, err = transaction.ExecContext(
			ctx,
			`UPDATE final_order_snapshots_v2
			    SET revision = ?, state_json = ?, updated_at_ms = ?
			  WHERE adapter_kind = 'RESEARCH_ADAPTER' AND revision = ?`,
			state.Revision, encoded, time.Now().UnixMilli(), expectedRevision,
		)
	}
	if err != nil {
		return errors.Join(finalorderdomain.ErrPersistenceConflict, err)
	}
	affected, err := result.RowsAffected()
	if err != nil || affected != 1 {
		return finalorderdomain.ErrPersistenceConflict
	}
	for _, record := range state.Candidates {
		var sequence any
		var receipt any
		if record.FinalSequence != 0 {
			sequence = record.FinalSequence
			receipt = record.ReceiptDigest[:]
		}
		_, err = transaction.ExecContext(
			ctx,
			`INSERT INTO final_order_candidates_v2(
			   candidate_digest, namespace_id, credential_id,
			   base_version, candidate_version, base_descriptor_hash,
			   descriptor_hash, envelope_hash, device_id, submitted_by,
			   idempotency_key_hash, disposition, final_sequence, receipt_digest
			 ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
			 ON CONFLICT(candidate_digest) DO UPDATE SET
			   disposition = excluded.disposition,
			   final_sequence = excluded.final_sequence,
			   receipt_digest = excluded.receipt_digest`,
			record.CandidateDigest[:], record.Candidate.NamespaceID[:],
			record.Candidate.CredentialID[:], record.Candidate.BaseVersion,
			record.Candidate.CandidateVersion, record.Candidate.BaseDescriptorHash[:],
			record.Candidate.DescriptorHash[:], record.Candidate.EnvelopeHash[:],
			record.Candidate.DeviceID[:], record.Candidate.SubmittedBy,
			record.Candidate.IdempotencyKeyHash[:], string(record.Disposition),
			sequence, receipt,
		)
		if err != nil {
			return err
		}
	}
	for _, receipt := range state.Receipts {
		var previous any
		if receipt.Payload.PreviousOrderedDigest != nil {
			previous = receipt.Payload.PreviousOrderedDigest[:]
		}
		_, err = transaction.ExecContext(
			ctx,
			`INSERT INTO final_order_receipts_v2(
			   receipt_digest, namespace_id, credential_id,
			   ordered_object_digest, final_sequence, previous_ordered_digest,
			   authority_key_id, authority_key_generation, signature, adapter_kind
			 ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, 'RESEARCH_ADAPTER')
			 ON CONFLICT(receipt_digest) DO NOTHING`,
			receipt.Digest[:], receipt.Payload.NamespaceID[:],
			receipt.Payload.CredentialID[:], receipt.Payload.OrderedObjectDigest[:],
			receipt.Payload.FinalSequence, previous,
			receipt.Payload.AuthorityKeyID[:],
			receipt.Payload.AuthorityKeyGeneration, receipt.Signature[:],
		)
		if err != nil {
			return err
		}
	}
	for _, checkpoint := range state.Checkpoints {
		_, err = transaction.ExecContext(
			ctx,
			`INSERT INTO final_order_checkpoints_v2(
			   checkpoint_digest, namespace_id, final_sequence, state_root,
			   last_receipt_digest, authority_key_id, key_generation,
			   signature, adapter_kind
			 ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, 'RESEARCH_ADAPTER')
			 ON CONFLICT(namespace_id, final_sequence) DO NOTHING`,
			checkpoint.Digest[:], checkpoint.NamespaceID[:],
			checkpoint.FinalSequence, checkpoint.StateRoot[:],
			checkpoint.LastReceiptDigest[:], checkpoint.AuthorityKeyID[:],
			checkpoint.KeyGeneration, checkpoint.Signature[:],
		)
		if err != nil {
			return err
		}
	}
	for _, resolution := range state.Resolutions {
		setDigest := digestSet(resolution.Request.CandidateDigests)
		_, err = transaction.ExecContext(
			ctx,
			`INSERT INTO final_order_resolutions_v2(
			   resolution_digest, namespace_id, credential_id,
			   selected_candidate_digest, candidate_set_digest,
			   resolution_descriptor_hash, new_version, resolved_by,
			   basis, final_sequence, receipt_digest
			 ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
			 ON CONFLICT(resolution_digest) DO NOTHING`,
			resolution.ResolutionDigest[:], resolution.Request.NamespaceID[:],
			resolution.Request.CredentialID[:],
			resolution.Request.SelectedCandidateDigest[:], setDigest[:],
			resolution.Request.ResolutionDescriptorHash[:], resolution.NewVersion,
			resolution.Request.ResolvedBy, resolution.Request.Basis,
			resolution.Receipt.Payload.FinalSequence, resolution.Receipt.Digest[:],
		)
		if err != nil {
			return err
		}
	}
	return transaction.Commit()
}

func digestSet(values [][sha256.Size]byte) [sha256.Size]byte {
	values = finalorderdomain.SortedDigests(values)
	hasher := sha256.New()
	for _, value := range values {
		_, _ = hasher.Write(value[:])
	}
	var digest [sha256.Size]byte
	copy(digest[:], hasher.Sum(nil))
	return digest
}
