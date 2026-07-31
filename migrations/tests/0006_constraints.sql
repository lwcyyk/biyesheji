-- Rollback-only G5 smoke after loading migrations 0002 through 0006.
PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

CREATE TEMP TABLE smoke_assertions_g5 (
    label TEXT PRIMARY KEY,
    ok    INTEGER NOT NULL CHECK (ok = 1)
) STRICT;

INSERT INTO smoke_assertions_g5(label, ok)
SELECT 'g5 migration identity',
       CASE WHEN EXISTS (
         SELECT 1 FROM schema_migrations
         WHERE version = 6
           AND name = '0006_g5_local_api'
           AND checksum_sha256 = X'8d0f548d0dc65ab00f4b9e4a13b4cc80b64b09c4ffe0e7fb8527200c1d45e056'
       ) THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g5(label, ok)
SELECT 'g5 user_version',
       CASE WHEN (SELECT user_version FROM pragma_user_version) = 6 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g5(label, ok)
SELECT 'g5 table set',
       CASE WHEN (
         SELECT count(*) FROM sqlite_schema
         WHERE type = 'table' AND name IN (
           'local_api_installations_v2',
           'local_api_idempotency_v2',
           'local_api_operations_v2'
         )
       ) = 3 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g5(label, ok)
SELECT 'installation token hash only',
       CASE WHEN instr(sql, 'install_token_hash') > 0
                  AND instr(sql, 'install_token ') = 0
                  AND instr(sql, 'master_password') = 0
                  AND instr(sql, 'secret_value') = 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'local_api_installations_v2';

INSERT INTO smoke_assertions_g5(label, ok)
SELECT 'idempotency key hash only',
       CASE WHEN instr(sql, 'key_hash') > 0
                  AND instr(sql, 'request_hash') > 0
                  AND instr(sql, 'expires_at_ms') > 0
                  AND instr(sql, 'idempotency_key') = 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'local_api_idempotency_v2';

INSERT INTO smoke_assertions_g5(label, ok)
SELECT 'operation unknown retained',
       CASE WHEN instr(sql, '''PENDING''') > 0
                  AND instr(sql, '''UNKNOWN''') > 0
                  AND instr(sql, '''COMPLETED''') > 0
                  AND instr(sql, 'request_hash') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'local_api_operations_v2';

INSERT INTO smoke_assertions_g5(label, ok)
SELECT 'foreign keys clean',
       CASE WHEN NOT EXISTS (SELECT 1 FROM pragma_foreign_key_check)
            THEN 1 ELSE 0 END;

SELECT 'constraint_smoke_g5_ok';
ROLLBACK;
