-- VDNS SQLite schema migration
-- Version: 0006
-- Name: g5_local_api
-- Adds hashed local installation identity, durable API idempotency and async operations.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;

BEGIN IMMEDIATE;

CREATE TABLE local_api_installations_v2 (
    installation_id             BLOB PRIMARY KEY CHECK (length(installation_id) = 32),
    install_token_hash          BLOB NOT NULL UNIQUE CHECK (length(install_token_hash) = 32),
    extension_origin_hash       BLOB NOT NULL CHECK (length(extension_origin_hash) = 32),
    status                      TEXT NOT NULL CHECK (status IN ('ACTIVE','ROTATED','REVOKED')),
    created_at_ms               INTEGER NOT NULL CHECK (created_at_ms >= 0),
    rotated_at_ms               INTEGER CHECK (rotated_at_ms IS NULL OR rotated_at_ms >= created_at_ms),
    CHECK (
      (status = 'ACTIVE' AND rotated_at_ms IS NULL)
      OR
      (status IN ('ROTATED','REVOKED') AND rotated_at_ms IS NOT NULL)
    )
) STRICT;

CREATE TABLE local_api_idempotency_v2 (
    key_hash                    BLOB PRIMARY KEY CHECK (length(key_hash) = 32),
    operation_scope            TEXT NOT NULL CHECK (length(operation_scope) BETWEEN 1 AND 512),
    request_hash               BLOB NOT NULL CHECK (length(request_hash) = 32),
    response_status            INTEGER NOT NULL CHECK (response_status BETWEEN 200 AND 299),
    response_headers_json      BLOB NOT NULL CHECK (length(response_headers_json) BETWEEN 2 AND 16384),
    response_body              BLOB NOT NULL CHECK (length(response_body) <= 1048576),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    expires_at_ms              INTEGER NOT NULL CHECK (expires_at_ms > created_at_ms)
) STRICT;

CREATE INDEX ix_local_api_idempotency_expiry_v2
ON local_api_idempotency_v2(expires_at_ms);

CREATE TABLE local_api_operations_v2 (
    operation_id               BLOB PRIMARY KEY CHECK (length(operation_id) = 16),
    operation_kind             TEXT NOT NULL CHECK (length(operation_kind) BETWEEN 1 AND 64),
    namespace_id               BLOB CHECK (namespace_id IS NULL OR length(namespace_id) = 16),
    device_id                  BLOB CHECK (device_id IS NULL OR length(device_id) = 16),
    request_hash               BLOB NOT NULL CHECK (length(request_hash) = 32),
    state                      TEXT NOT NULL CHECK (state IN (
                                 'QUEUED','RUNNING','COMPLETED','PENDING',
                                 'FAILED','UNKNOWN'
                               )),
    result_reference           TEXT CHECK (
                                 result_reference IS NULL
                                 OR length(result_reference) BETWEEN 1 AND 512
                               ),
    error_code                 TEXT CHECK (
                                 error_code IS NULL
                                 OR length(error_code) BETWEEN 3 AND 64
                               ),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    CHECK (
      (state = 'FAILED' AND error_code IS NOT NULL)
      OR
      (state <> 'FAILED' AND error_code IS NULL)
    )
) STRICT;

CREATE INDEX ix_local_api_operations_state_v2
ON local_api_operations_v2(state, updated_at_ms, operation_id);

INSERT INTO schema_migrations(version, name, checksum_sha256, applied_at_ms)
VALUES (
  6,
  '0006_g5_local_api',
  X'8d0f548d0dc65ab00f4b9e4a13b4cc80b64b09c4ffe0e7fb8527200c1d45e056',
  CAST(strftime('%s', 'now') AS INTEGER) * 1000
);

PRAGMA user_version = 6;
COMMIT;
