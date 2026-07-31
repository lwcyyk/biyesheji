-- Rollback-only G2 smoke after loading 0002_v2_initial.sql and 0003_g2_core.sql.
PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

CREATE TEMP TABLE smoke_assertions_g2 (
    label TEXT PRIMARY KEY,
    ok    INTEGER NOT NULL CHECK (ok = 1)
) STRICT;

INSERT INTO smoke_assertions_g2(label, ok)
SELECT 'g2 migration identity',
       CASE WHEN EXISTS (
         SELECT 1 FROM schema_migrations
         WHERE version = 3
           AND name = '0003_g2_core'
           AND checksum_sha256 = X'70934a17beba6ac5cd942c57f5b310d04ca9257a5e6dda9d3f6d027a1a696a9e'
       ) THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g2(label, ok)
SELECT 'g2 user_version',
       CASE WHEN (SELECT user_version FROM pragma_user_version) = 3 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g2(label, ok)
SELECT 'g2 table set',
       CASE WHEN (
         SELECT count(*) FROM sqlite_schema
         WHERE type = 'table' AND name IN (
           'vault_profiles','root_capsules','recovery_capsules','route_entries',
           'password_policies','credential_envelopes_v2',
           'state_descriptors_v2','credential_acceptance_v2'
         )
       ) = 8 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g2(label, ok)
SELECT 'route indexes are private fixed width',
       CASE WHEN instr(sql, 'length(route_id) = 32') > 0
                  AND instr(sql, 'length(origin_index) = 32') > 0
                  AND instr(sql, 'encrypted_origin') > 0
                  AND instr(sql, 'encrypted_account_id') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'route_entries';

INSERT INTO smoke_assertions_g2(label, ok)
SELECT 'state descriptor frozen lifecycle',
       CASE WHEN instr(sql, '''ACTIVE''') > 0
                  AND instr(sql, '''SITE_CONFIRM_PENDING''') > 0
                  AND instr(sql, '''CONFLICTED''') > 0
                  AND instr(sql, 'updater_signature') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'state_descriptors_v2';

INSERT INTO smoke_assertions_g2(label, ok)
SELECT 'accepted pointers bind both control objects',
       CASE WHEN instr(sql, 'accepted_descriptor_hash') > 0
                  AND instr(sql, 'accepted_envelope_hash') > 0
                  AND instr(sql, 'updated_sequence') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'credential_acceptance_v2';

INSERT INTO smoke_assertions_g2(label, ok)
SELECT 'foreign keys clean',
       CASE WHEN NOT EXISTS (SELECT 1 FROM pragma_foreign_key_check)
            THEN 1 ELSE 0 END;

SELECT 'constraint_smoke_g2_ok';
ROLLBACK;
