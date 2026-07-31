-- Rollback-only G3 smoke after loading migrations 0002 through 0004.
PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

CREATE TEMP TABLE smoke_assertions_g3 (
    label TEXT PRIMARY KEY,
    ok    INTEGER NOT NULL CHECK (ok = 1)
) STRICT;

INSERT INTO smoke_assertions_g3(label, ok)
SELECT 'g3 migration identity',
       CASE WHEN EXISTS (
         SELECT 1 FROM schema_migrations
         WHERE version = 4
           AND name = '0004_g3_lifecycle_sync'
           AND checksum_sha256 = X'c064e22d26cd0b703c82a3b8f53145110c799d6cd8a7ba5b03fb4501b89b2ac7'
       ) THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g3(label, ok)
SELECT 'g3 user_version',
       CASE WHEN (SELECT user_version FROM pragma_user_version) = 4 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g3(label, ok)
SELECT 'g3 table set',
       CASE WHEN (
         SELECT count(*) FROM sqlite_schema
         WHERE type = 'table' AND name IN (
           'site_change_attempts','sync_manifests_v2',
           'sync_manifest_objects_v2','sync_peer_acceptance',
           'credential_conflicts_v2','device_enrollment_challenges',
           'secret_generation_rollovers','secret_generation_recipients',
           'backup_snapshots_v2','recovery_runs_v2'
         )
       ) = 10 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions_g3(label, ok)
SELECT 'site activation requires strong evidence',
       CASE WHEN instr(sql, 'evidence_level IN (4,5)') > 0
                  AND instr(sql, 'confirmation_event_id IS NOT NULL') > 0
                  AND instr(sql, '''SITE_STATUS_UNKNOWN''') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'site_change_attempts';

INSERT INTO smoke_assertions_g3(label, ok)
SELECT 'manifest binds checkpoints root counter signature',
       CASE WHEN instr(sql, 'base_checkpoint') > 0
                  AND instr(sql, 'target_checkpoint') > 0
                  AND instr(sql, 'object_set_root') > 0
                  AND instr(sql, 'highest_device_counter') > 0
                  AND instr(sql, 'publisher_signature') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'sync_manifests_v2';

INSERT INTO smoke_assertions_g3(label, ok)
SELECT 'manifest object completion is explicit',
       CASE WHEN instr(sql, '''MISSING''') > 0
                  AND instr(sql, '''VERIFIED''') > 0
                  AND instr(sql, '''CORRUPT''') > 0
                  AND instr(sql, '(credential_id IS NULL) = (credential_version IS NULL)') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'sync_manifest_objects_v2';

INSERT INTO smoke_assertions_g3(label, ok)
SELECT 'conflicts retain both descriptors',
       CASE WHEN instr(sql, '''RETAINED''') > 0
                  AND instr(sql, 'descriptor_hash') > 0
                  AND instr(sql, 'resolution_event_id') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'credential_conflicts_v2';

INSERT INTO smoke_assertions_g3(label, ok)
SELECT 'enrollment challenge is one-use state',
       CASE WHEN instr(sql, '''ISSUED''') > 0
                  AND instr(sql, '''APPROVED''') > 0
                  AND instr(sql, '''CONSUMED''') > 0
                  AND instr(sql, 'short_code_commitment') > 0
                  AND instr(sql, 'root_bundle_envelope_hash') > 0
                  AND instr(sql, 'issued_device_credential_hash') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'device_enrollment_challenges';

INSERT INTO smoke_assertions_g3(label, ok)
SELECT 'recovery requires VDNS verification',
       CASE WHEN instr(sql, '''OBJECTS_VERIFIED''') > 0
                  AND instr(sql, '''VDNS_VERIFIED''') > 0
                  AND instr(sql, 'verified_checkpoint') > 0
            THEN 1 ELSE 0 END
FROM sqlite_schema
WHERE type = 'table' AND name = 'recovery_runs_v2';

INSERT INTO smoke_assertions_g3(label, ok)
SELECT 'foreign keys clean',
       CASE WHEN NOT EXISTS (SELECT 1 FROM pragma_foreign_key_check)
            THEN 1 ELSE 0 END;

SELECT 'constraint_smoke_g3_ok';
ROLLBACK;
