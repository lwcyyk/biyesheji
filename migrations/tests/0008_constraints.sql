-- Rollback-only Stage 2 schema smoke after loading migrations 0002 through 0008.
.bail on

SELECT 'stage2 migration row',
       CASE WHEN EXISTS (
         SELECT 1 FROM schema_migrations
         WHERE version = 8
           AND name = '0008_stage2_protocol_closure'
           AND length(checksum_sha256) = 32
       ) THEN 1 ELSE 0 END;

SELECT 'stage2 user_version',
       CASE WHEN (SELECT user_version FROM pragma_user_version) = 8 THEN 1 ELSE 0 END;

SELECT 'final order adapter tables',
       CASE WHEN (
         SELECT count(*) FROM sqlite_schema
         WHERE type = 'table'
           AND name IN (
             'final_order_snapshots_v2',
             'final_order_candidates_v2',
             'final_order_receipts_v2',
             'final_order_checkpoints_v2',
             'final_order_resolutions_v2',
             'site_confirmation_evidence_v21',
             'device_revocation_layers_v2'
           )
       ) = 7 THEN 1 ELSE 0 END;

BEGIN IMMEDIATE;

INSERT INTO final_order_snapshots_v2(adapter_kind, revision, state_json, updated_at_ms)
VALUES('RESEARCH_ADAPTER', 1, X'7b7d', 0);

INSERT INTO site_confirmation_evidence_v21(
  evidence_digest, change_id, namespace_id, credential_id, candidate_version,
  evidence_schema, evidence_level, trust_kind, decision_state, created_at_ms
) VALUES(
  randomblob(32), randomblob(32), randomblob(16), randomblob(32), 2,
  2, 0, 'BROWSER_OBSERVATION', 'UNKNOWN', 0
);

INSERT INTO device_revocation_layers_v2(
  namespace_id, device_id,
  control_plane_status, secret_isolation_status, external_remediation_status,
  known_credential_set_digest, future_blocked_set_digest,
  remediation_required_digest, updated_at_ms
) VALUES(
  randomblob(16), randomblob(16),
  'PENDING', 'PENDING', 'UNKNOWN',
  randomblob(32), randomblob(32), randomblob(32), 0
);

ROLLBACK;

SELECT 'stage2_constraint_smoke_ok';
