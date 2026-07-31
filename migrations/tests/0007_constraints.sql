-- Rollback-only G6 schema smoke after loading migrations 0002 through 0007.
PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

CREATE TEMP TABLE smoke_assertions_g6 (
    label TEXT PRIMARY KEY,
    ok    INTEGER NOT NULL CHECK (ok = 1)
) STRICT;

INSERT INTO smoke_assertions_g6(label, ok)
SELECT 'g6 migration identity',
       CASE WHEN EXISTS (
         SELECT 1 FROM schema_migrations
         WHERE version = 7
           AND name = '0007_g6_privacy_response'
           AND checksum_sha256 = X'bda97d75cd1717c7afa0f1172be04781f01ac0e327647d423883746db8cc67eb'
       ) THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g6(label, ok)
SELECT 'g6 user_version',
       CASE WHEN (SELECT user_version FROM pragma_user_version) = 7 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g6(label, ok)
SELECT 'g6 table set',
       CASE WHEN (
         SELECT count(*) FROM sqlite_schema
         WHERE type = 'table' AND name IN (
           'audit_events_v2',
           'security_analyses_v2',
           'security_findings_v2',
           'exposure_analyses_v2',
           'remediation_campaigns_v2',
           'remediation_items_v2',
           'rotation_attempt_receipts_v2'
         )
       ) = 7 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g6(label, ok)
SELECT 'audit encrypted witness only',
       CASE WHEN instr(sql, 'encrypted_payload_digest') > 0
                  AND instr(sql, 'encrypted_object_hash') > 0
                  AND instr(sql, 'reuse_tag') = 0
                  AND instr(sql, 'reuse_witness') = 0
                  AND instr(sql, 'password ') = 0
                  AND instr(sql, 'secret_handle') = 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'audit_events_v2';

INSERT INTO smoke_assertions_g6(label, ok)
SELECT 'analysis results minimized',
       CASE WHEN instr(sql, 'credential_pseudonym') > 0
                  AND instr(sql, 'evidence_reference_cbor') > 0
                  AND instr(sql, 'credential_id') = 0
                  AND instr(sql, 'device_id') = 0
                  AND instr(sql, 'secret_handle') = 0
                  AND instr(sql, 'reuse_tag') = 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'security_findings_v2';

INSERT INTO smoke_assertions_g6(label, ok)
SELECT 'optional analysis no false unavailable row',
       CASE WHEN instr(sql, '''COMPLETED''') > 0
                  AND instr(sql, 'affected_root IS NOT NULL') > 0
                  AND instr(sql, 'proof_digest IS NOT NULL') > 0
                  AND instr(sql, 'OPTIONAL_FEATURE_UNAVAILABLE') = 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'exposure_analyses_v2';

INSERT INTO smoke_assertions_g6(label, ok)
SELECT 'real outcome partition',
       CASE WHEN instr(sql, '''COMPLETED''') > 0
                  AND instr(sql, '''PENDING''') > 0
                  AND instr(sql, '''FAILED''') > 0
                  AND instr(sql, '''UNKNOWN''') > 0
                  AND instr(sql, 'before_fields_digest = after_fields_digest') > 0
                  AND instr(sql, 'new_version = old_version + 1') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'remediation_items_v2';

INSERT INTO smoke_assertions_g6(label, ok)
SELECT 'attempt replay key',
       CASE WHEN instr(sql, 'PRIMARY KEY (campaign_id, item_id, attempt)') > 0
                  AND instr(sql, 'evidence_digest') > 0
                  AND instr(sql, 'receipt_digest') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'rotation_attempt_receipts_v2';

INSERT INTO smoke_assertions_g6(label, ok)
SELECT 'foreign keys clean',
       CASE WHEN NOT EXISTS (SELECT 1 FROM pragma_foreign_key_check)
            THEN 1 ELSE 0 END;

SELECT 'constraint_smoke_g6_ok';
ROLLBACK;
