-- Rollback-only G4 smoke after loading migrations 0002 through 0005.
PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

CREATE TEMP TABLE smoke_assertions_g4 (
    label TEXT PRIMARY KEY,
    ok    INTEGER NOT NULL CHECK (ok = 1)
) STRICT;

INSERT INTO smoke_assertions_g4(label, ok)
SELECT 'g4 migration identity',
       CASE WHEN EXISTS (
         SELECT 1 FROM schema_migrations
         WHERE version = 5
           AND name = '0005_g4_vdns_transparency'
           AND checksum_sha256 = X'8706b8da3cab1a182d70ae1d053556d1274c7d88ea612988abc3c53bce043f9b'
       ) THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g4(label, ok)
SELECT 'g4 user_version',
       CASE WHEN (SELECT user_version FROM pragma_user_version) = 5 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g4(label, ok)
SELECT 'g4 table set',
       CASE WHEN (
         SELECT count(*) FROM sqlite_schema
         WHERE type = 'table' AND name IN (
           'transparency_logs_v2','transparency_leaves_v2',
           'signed_tree_heads_v2','consistency_proofs_v2',
           'checkpoints_v2','announcement_receipts_v2',
           'proof_bundles_v2','vdns_resolutions_v2','monitor_evidence_v2'
         )
       ) = 9 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g4(label, ok)
SELECT 'checkpoint public whitelist',
       CASE WHEN instr(sql, 'namespace_state_root') > 0
                  AND instr(sql, 'device_state_root') > 0
                  AND instr(sql, 'credential_state_root') > 0
                  AND instr(sql, 'audit_log_root') > 0
                  AND instr(sql, 'revocation_root') > 0
                  AND instr(sql, 'crypto_policy_hash') > 0
                  AND instr(sql, 'provider_kind') > 0
                  AND instr(sql, 'password') = 0
                  AND instr(sql, 'origin') = 0
                  AND instr(sql, 'username') = 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'checkpoints_v2';

INSERT INTO smoke_assertions_g4(label, ok)
SELECT 'proof counts bounded',
       CASE WHEN instr(sql, 'inclusion_hash_count BETWEEN 0 AND 64') > 0
                  AND instr(sql, 'consistency_hash_count BETWEEN 0 AND 64') > 0
                  AND instr(sql, 'local_policy_input_hash') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'proof_bundles_v2';

INSERT INTO smoke_assertions_g4(label, ok)
SELECT 'verdict registry complete',
       CASE WHEN instr(sql, '''ACCEPT''') > 0
                  AND instr(sql, '''DEGRADED_OFFLINE''') > 0
                  AND instr(sql, '''DEGRADED_PENDING_LOG''') > 0
                  AND instr(sql, '''REVIEW_REQUIRED''') > 0
                  AND instr(sql, '''REJECT_PROOF''') > 0
                  AND instr(sql, '''REJECT_POLICY''') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'vdns_resolutions_v2';

INSERT INTO smoke_assertions_g4(label, ok)
SELECT 'monitor evidence kinds',
       CASE WHEN instr(sql, '''SPLIT_VIEW''') > 0
                  AND instr(sql, '''TREE_ROLLBACK''') > 0
                  AND instr(sql, '''BAD_CONSISTENCY''') > 0
                  AND instr(sql, '''DOUBLE_DESCRIPTOR''') > 0
                  AND instr(sql, '''ANCHOR_CONFLICT''') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'monitor_evidence_v2';

INSERT INTO smoke_assertions_g4(label, ok)
SELECT 'foreign keys clean',
       CASE WHEN NOT EXISTS (SELECT 1 FROM pragma_foreign_key_check)
            THEN 1 ELSE 0 END;

SELECT 'constraint_smoke_g4_ok';
ROLLBACK;
