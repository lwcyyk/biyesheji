-- Pure-SQL, rollback-only smoke for migration 0001.
-- Run with sqlite3 -bail after loading migrations/0001_initial.sql.

PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

CREATE TEMP TABLE smoke_assertions (
    label TEXT PRIMARY KEY,
    ok    INTEGER NOT NULL CHECK (ok = 1)
) STRICT;

INSERT INTO smoke_assertions(label, ok)
SELECT 'schema migration row',
       CASE WHEN EXISTS (
         SELECT 1
         FROM schema_migrations
         WHERE version = 1
           AND name = '0001_initial'
           AND checksum_sha256 = X'b15af2e0a284b3a4357d03713e63102eb68d1868931800684b8b6625e697190d'
       ) THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions(label, ok)
SELECT 'user_version',
       CASE WHEN (SELECT user_version FROM pragma_user_version) = 1 THEN 1 ELSE 0 END;

-- Identifier length CHECK must reject a 15-byte NamespaceID.
INSERT OR IGNORE INTO namespaces(
  namespace_id, protocol_version, suite_id, chain_id,
  root_signing_public_key, root_key_id, current_secret_generation,
  status, created_at_ms, updated_at_ms
) VALUES (
  randomblob(15), 1, 'VDNS-CP-1', 'anvil-local',
  randomblob(32), randomblob(32), 1,
  'ACTIVE', 0, 0
);

INSERT INTO smoke_assertions(label, ok)
SELECT 'namespace id length CHECK',
       CASE WHEN NOT EXISTS (
         SELECT 1 FROM namespaces WHERE length(namespace_id) = 15
       ) THEN 1 ELSE 0 END;

-- Enum and timestamp-order CHECKs must reject unknown or regressing values.
INSERT OR IGNORE INTO namespaces(
  namespace_id, protocol_version, suite_id, chain_id,
  root_signing_public_key, root_key_id, current_secret_generation,
  status, created_at_ms, updated_at_ms
) VALUES (
  randomblob(16), 1, 'VDNS-CP-1', 'anvil-local',
  randomblob(32), randomblob(32), 1,
  'UNKNOWN', 0, 0
);

INSERT OR IGNORE INTO namespaces(
  namespace_id, protocol_version, suite_id, chain_id,
  root_signing_public_key, root_key_id, current_secret_generation,
  status, created_at_ms, updated_at_ms
) VALUES (
  randomblob(16), 1, 'VDNS-CP-1', 'anvil-local',
  randomblob(32), randomblob(32), 1,
  'ACTIVE', 10, 9
);

INSERT INTO smoke_assertions(label, ok)
SELECT 'namespace enum CHECK',
       CASE WHEN NOT EXISTS (
         SELECT 1 FROM namespaces WHERE status = 'UNKNOWN'
       ) THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions(label, ok)
SELECT 'namespace timestamp CHECK',
       CASE WHEN NOT EXISTS (
         SELECT 1 FROM namespaces WHERE updated_at_ms < created_at_ms
       ) THEN 1 ELSE 0 END;

-- A valid namespace supplies parents for subsequent index/foreign-key checks.
INSERT INTO namespaces(
  namespace_id, protocol_version, suite_id, chain_id,
  root_signing_public_key, root_key_id, current_secret_generation,
  status, created_at_ms, updated_at_ms
) VALUES (
  zeroblob(16), 1, 'VDNS-CP-1', 'anvil-local',
  zeroblob(32), zeroblob(32), 1,
  'ACTIVE', 0, 0
);

-- Namespace root_key_id is globally unique.
INSERT OR IGNORE INTO namespaces(
  namespace_id, protocol_version, suite_id, chain_id,
  root_signing_public_key, root_key_id, current_secret_generation,
  status, created_at_ms, updated_at_ms
) VALUES (
  randomblob(16), 1, 'VDNS-CP-1', 'anvil-local',
  randomblob(32), zeroblob(32), 1,
  'ACTIVE', 0, 0
);

INSERT INTO smoke_assertions(label, ok)
SELECT 'root key unique constraint',
       CASE WHEN (SELECT count(*) FROM namespaces WHERE root_key_id = zeroblob(32)) = 1
       THEN 1 ELSE 0 END;

-- Partial unique index allows at most one ACTIVE root signing key per namespace.
INSERT INTO root_signing_keys(
  namespace_id, root_key_id, public_key, secure_store_ref, status,
  valid_from_anchor_sequence, retired_at_ms, created_at_ms
) VALUES (
  zeroblob(16), randomblob(32), randomblob(32), 'secure://root/one', 'ACTIVE',
  0, NULL, 0
);

INSERT OR IGNORE INTO root_signing_keys(
  namespace_id, root_key_id, public_key, secure_store_ref, status,
  valid_from_anchor_sequence, retired_at_ms, created_at_ms
) VALUES (
  zeroblob(16), randomblob(32), randomblob(32), 'secure://root/two', 'ACTIVE',
  0, NULL, 0
);

INSERT INTO smoke_assertions(label, ok)
SELECT 'one active root partial unique index',
       CASE WHEN (
         SELECT count(*) FROM root_signing_keys
         WHERE namespace_id = zeroblob(16) AND status = 'ACTIVE'
       ) = 1 THEN 1 ELSE 0 END;

-- Content-addressed object paths must be relative and traversal-free.
INSERT OR IGNORE INTO content_objects(
  object_hash, object_type, cipher_suite, key_generation, nonce, aad_hash,
  ciphertext_length, storage_relpath, state, created_at_ms, verified_at_ms
) VALUES (
  randomblob(32), 'AUDIT_EVENT', 'AES-256-GCM', 1, randomblob(12), randomblob(32),
  16, 'objects/../escape.obj', 'COMMITTED', 0, NULL
);

INSERT INTO smoke_assertions(label, ok)
SELECT 'object path traversal CHECK',
       CASE WHEN NOT EXISTS (
         SELECT 1 FROM content_objects WHERE instr(storage_relpath, '..') > 0
       ) THEN 1 ELSE 0 END;

-- FINALIZED anchors require chain evidence and a finalized timestamp.
INSERT OR IGNORE INTO anchors(
  chain_id, namespace_commitment, checkpoint_type, sequence, epoch, tree_size,
  root_hash, confirmation_depth, status, created_at_ms
) VALUES (
  'anvil-local', randomblob(32), 'AUDIT', 0, 0, 0,
  randomblob(32), 1, 'FINALIZED', 0
);

INSERT INTO smoke_assertions(label, ok)
SELECT 'anchor finality CHECK',
       CASE WHEN NOT EXISTS (
         SELECT 1 FROM anchors WHERE status = 'FINALIZED'
       ) THEN 1 ELSE 0 END;

-- Idempotency records cannot expire at or before creation time.
INSERT OR IGNORE INTO idempotency_records(
  idempotency_key, operation_scope, request_body_hash,
  response_status, response_body, created_at_ms, expires_at_ms
) VALUES (
  '0123456789abcdef', 'credential-create', randomblob(32),
  201, X'', 10, 10
);

INSERT INTO smoke_assertions(label, ok)
SELECT 'idempotency expiry CHECK',
       CASE WHEN NOT EXISTS (
         SELECT 1 FROM idempotency_records WHERE expires_at_ms <= created_at_ms
       ) THEN 1 ELSE 0 END;

-- Force immediate foreign keys to defer so their negative case can be inspected
-- without aborting this pure-SQL smoke; remove the bad row before rollback.
PRAGMA defer_foreign_keys = ON;

INSERT INTO devices(
  device_id, namespace_id, signing_public_key, hpke_public_key,
  current_key_generation, status, last_accepted_counter,
  current_credential_hash, created_at_ms, updated_at_ms
) VALUES (
  randomblob(16), randomblob(16), randomblob(32), randomblob(32),
  1, 'ACTIVE', 0, NULL, 0, 0
);

INSERT INTO smoke_assertions(label, ok)
SELECT 'foreign key violation detected',
       CASE WHEN EXISTS (
         SELECT 1 FROM pragma_foreign_key_check WHERE "table" = 'devices'
       ) THEN 1 ELSE 0 END;

DELETE FROM devices WHERE namespace_id <> zeroblob(16);

-- Runtime tests for RAISE(ABORT) triggers need isolated expected-failure
-- connections; this smoke verifies that every frozen guard is installed.
INSERT INTO smoke_assertions(label, ok)
SELECT 'credential pointer guards installed',
       CASE WHEN (
         SELECT count(*) FROM sqlite_schema
         WHERE type = 'trigger'
           AND name IN ('trg_credentials_pointer_insert', 'trg_credentials_pointer_update')
       ) = 2 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions(label, ok)
SELECT 'append-only guards installed',
       CASE WHEN (
         SELECT count(*) FROM sqlite_schema
         WHERE type = 'trigger'
           AND name IN (
             'trg_operation_events_no_update', 'trg_operation_events_no_delete',
             'trg_transparency_leaves_no_update', 'trg_transparency_leaves_no_delete',
             'trg_transparency_nodes_no_update', 'trg_transparency_nodes_no_delete'
           )
       ) = 6 THEN 1 ELSE 0 END;

INSERT INTO smoke_assertions(label, ok)
SELECT 'outbox lease index installed',
       CASE WHEN EXISTS (
         SELECT 1 FROM sqlite_schema
         WHERE type = 'index' AND name = 'ix_outbox_ready'
       ) AND (
         SELECT count(*) FROM pragma_table_info('event_publication_outbox')
         WHERE name IN ('publication_state', 'lease_token', 'lease_expires_at_ms')
       ) = 3 THEN 1 ELSE 0 END;

-- G0.1 registry corrections must be present in the executable schema.
INSERT INTO smoke_assertions(label, ok)
SELECT 'g0.1 protocol registry projections',
       CASE WHEN
         instr((SELECT sql FROM sqlite_schema WHERE type = 'table' AND name = 'device_capabilities'), 'AUDIT_ANALYZE') > 0
         AND instr((SELECT sql FROM sqlite_schema WHERE type = 'table' AND name = 'operation_events'), 'ANALYZE_EXPOSURE') > 0
         AND instr((SELECT sql FROM sqlite_schema WHERE type = 'table' AND name = 'operation_events'), 'length(device_pseudonym) = 16') > 0
         AND instr((SELECT sql FROM sqlite_schema WHERE type = 'table' AND name = 'transparency_leaves'), 'length(device_pseudonym) = 16') > 0
         AND (
           SELECT count(*) FROM pragma_table_info('credential_version_fields')
           WHERE name IN ('encryption_version','field_object_id','field_object_hash','envelope_id','envelope_hash')
         ) = 5
       THEN 1 ELSE 0 END;

SELECT CASE WHEN count(*) = 15 THEN 'constraint_smoke_ok' ELSE 'constraint_smoke_incomplete' END
FROM smoke_assertions;

ROLLBACK;
