-- Rollback-only CP-2 smoke for the new-install v2 schema.
-- Run with sqlite3 -bail after loading migrations/0002_v2_initial.sql.

PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

CREATE TEMP TABLE smoke_assertions (
    label TEXT PRIMARY KEY,
    ok    INTEGER NOT NULL CHECK (ok = 1)
) STRICT;

INSERT INTO smoke_assertions(label, ok)
SELECT 'v2 migration identity',
       CASE WHEN EXISTS (
         SELECT 1 FROM schema_migrations
         WHERE version = 2
           AND name = '0002_v2_initial'
           AND checksum_sha256 = X'18bd457a1fbf4e5d904c46512402c31dcc8bb96cb51b75eb62b8cca0566af152'
       ) THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions(label, ok)
SELECT 'v2 user_version',
       CASE WHEN (SELECT user_version FROM pragma_user_version) = 2 THEN 1 ELSE 0 END;

INSERT INTO namespaces(
  namespace_id, protocol_version, suite_id, chain_id,
  root_signing_public_key, root_key_id, current_secret_generation,
  status, created_at_ms, updated_at_ms
) VALUES (
  zeroblob(16), 2, 'VDNS-PM-CP-2', 'test-chain',
  zeroblob(32), zeroblob(32), 1, 'ACTIVE', 0, 0
);

INSERT OR IGNORE INTO credentials(
  credential_id, namespace_id, aggregate_status, origin_commitment,
  created_at_ms, updated_at_ms
) VALUES (
  randomblob(16), zeroblob(16), 'ACTIVE', randomblob(32), 0, 0
);

INSERT INTO credentials(
  credential_id, namespace_id, aggregate_status, origin_commitment,
  created_at_ms, updated_at_ms
) VALUES (
  zeroblob(32), zeroblob(16), 'ACTIVE', randomblob(32), 0, 0
);

INSERT INTO smoke_assertions(label, ok)
SELECT 'CredentialID is exactly 32 bytes',
       CASE WHEN
         NOT EXISTS (SELECT 1 FROM credentials WHERE length(credential_id) = 16)
         AND EXISTS (SELECT 1 FROM credentials WHERE length(credential_id) = 32)
       THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions(label, ok)
SELECT 'CP-2 field schema',
       CASE WHEN instr(sql, '''ORIGIN''') > 0
                  AND instr(sql, 'crypto_policy_hash') > 0
                  AND instr(sql, 'origin_binding') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'credential_version_fields';

INSERT INTO smoke_assertions(label, ok)
SELECT 'CP-2 operation registry',
       CASE WHEN instr(sql, '''SYNC_PUBLISH''') > 0
                  AND instr(sql, '''DEVICE_ENROLL''') > 0
                  AND instr(sql, '''REMEDIATION_COMMIT''') > 0
                  AND instr(sql, '''ROTATION_PREPARE''') = 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'operation_events';

INSERT INTO smoke_assertions(label, ok)
SELECT 'CP-2 capability registry',
       CASE WHEN instr(sql, '''AUTOFILL''') > 0
                  AND instr(sql, '''RELATION_PUBLISH''') > 0
                  AND instr(sql, '''USE_AUDIT''') = 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'device_capabilities';

SELECT 'constraint_smoke_v2_ok';
ROLLBACK;
