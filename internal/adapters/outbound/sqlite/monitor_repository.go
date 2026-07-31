package sqlite

import (
	"context"
	"errors"

	monitoringdomain "vdns.local/vdns/internal/monitoring/domain"
	"vdns.local/vdns/internal/protocol"
)

var ErrMonitorEvidenceConflict = errors.New("monitor evidence persistence conflict")

// MonitorEvidenceRepository preserves canonical, secret-free evidence.
type MonitorEvidenceRepository struct {
	database *Database
}

func NewMonitorEvidenceRepository(database *Database) (*MonitorEvidenceRepository, error) {
	if database == nil {
		return nil, ErrMonitorEvidenceConflict
	}
	return &MonitorEvidenceRepository{database: database}, nil
}

func (repository *MonitorEvidenceRepository) Save(
	ctx context.Context,
	evidence monitoringdomain.Evidence,
) error {
	if repository == nil || repository.database == nil || ctx == nil ||
		evidence.Validate() != nil {
		return monitoringdomain.ErrInvalidEvidence
	}
	encoded, err := protocol.MarshalDeterministic(evidence)
	if err != nil {
		return monitoringdomain.ErrInvalidEvidence
	}
	kind, err := monitorKindName(evidence.Kind)
	if err != nil {
		return err
	}
	var subject any
	if evidence.SubjectCommitment != nil {
		subject = evidence.SubjectCommitment[:]
	}
	result, err := repository.database.ExecContext(
		ctx,
		`INSERT INTO monitor_evidence_v2 (
  evidence_digest, namespace_id, finding_kind,
  first_object_hash, second_object_hash, first_position, second_position,
  subject_commitment, evidence_cbor, detected_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(evidence_digest) DO NOTHING`,
		evidence.EvidenceDigest[:], evidence.NamespaceID[:], kind,
		evidence.FirstObjectHash[:], evidence.SecondObjectHash[:],
		evidence.FirstPosition, evidence.SecondPosition,
		subject, encoded, uint64(0),
	)
	if err != nil {
		return err
	}
	affected, err := result.RowsAffected()
	if err != nil {
		return err
	}
	if affected == 1 {
		return nil
	}
	var stored []byte
	if err := repository.database.QueryRowContext(
		ctx,
		"SELECT evidence_cbor FROM monitor_evidence_v2 WHERE evidence_digest = ?",
		evidence.EvidenceDigest[:],
	).Scan(&stored); err != nil {
		return err
	}
	if string(stored) != string(encoded) {
		return ErrMonitorEvidenceConflict
	}
	return nil
}

func monitorKindName(kind monitoringdomain.FindingKind) (string, error) {
	switch kind {
	case monitoringdomain.FindingSplitView:
		return "SPLIT_VIEW", nil
	case monitoringdomain.FindingTreeRollback:
		return "TREE_ROLLBACK", nil
	case monitoringdomain.FindingBadConsistency:
		return "BAD_CONSISTENCY", nil
	case monitoringdomain.FindingDoubleDescriptor:
		return "DOUBLE_DESCRIPTOR", nil
	case monitoringdomain.FindingAnchorConflict:
		return "ANCHOR_CONFLICT", nil
	default:
		return "", monitoringdomain.ErrInvalidEvidence
	}
}
