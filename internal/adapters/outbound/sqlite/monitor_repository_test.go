package sqlite

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"testing"

	monitoringdomain "vdns.local/vdns/internal/monitoring/domain"
	"vdns.local/vdns/internal/protocol"
)

func TestMonitorEvidenceRepositoryPreservesIdempotentEvidence(t *testing.T) {
	database := openTestDatabase(t)
	ctx := context.Background()
	namespace := protocol.NamespaceID{1, 2, 3}
	rootKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x31}, ed25519.SeedSize))
	rootPublic := rootKey.Public().(ed25519.PublicKey)
	rootKeyID, _ := protocol.KeyIDFromPublicKey(rootPublic)
	if _, err := database.ExecContext(
		ctx,
		`INSERT INTO namespaces (
  namespace_id, protocol_version, suite_id, chain_id, root_signing_public_key,
  root_key_id, current_secret_generation, status, created_at_ms, updated_at_ms
) VALUES (?, 2, ?, 'monitor-chain', ?, ?, 1, 'ACTIVE', 0, 0)`,
		namespace[:], protocol.SuiteID, rootPublic, rootKeyID[:],
	); err != nil {
		t.Fatal(err)
	}
	repository, err := NewMonitorEvidenceRepository(database)
	if err != nil {
		t.Fatal(err)
	}
	first := sha256.Sum256([]byte("first signed head"))
	second := sha256.Sum256([]byte("second signed head"))
	evidence, err := monitoringdomain.NewEvidence(
		monitoringdomain.FindingSplitView, namespace,
		first, second, 7, 7, nil,
	)
	if err != nil {
		t.Fatal(err)
	}
	if err := repository.Save(ctx, evidence); err != nil {
		t.Fatal(err)
	}
	if err := repository.Save(ctx, evidence); err != nil {
		t.Fatal(err)
	}
	assertScalar(t, database, "SELECT count(*) FROM monitor_evidence_v2", 1)

	tampered := evidence
	tampered.EvidenceDigest[0] ^= 1
	if err := repository.Save(ctx, tampered); err == nil {
		t.Fatal("tampered evidence accepted")
	}
}
