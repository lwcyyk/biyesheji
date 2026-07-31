-- VDNS SQLite schema migration
-- Version: 0002
-- Name: v2_initial
-- Source: specs/001-vdns-audit-rotation/data-model.md §6 (G0.2 / CP-2 baseline)
-- New-install schema only. Existing CP-1 databases require explicit export, re-encryption and import.
-- This published migration is append-only; never edit it after release.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;

BEGIN IMMEDIATE;

CREATE TABLE schema_migrations (
    version             INTEGER PRIMARY KEY CHECK (version > 0),
    name                TEXT NOT NULL UNIQUE,
    checksum_sha256     BLOB NOT NULL CHECK (length(checksum_sha256) = 32),
    applied_at_ms       INTEGER NOT NULL CHECK (applied_at_ms >= 0)
) STRICT;

CREATE TABLE namespaces (
    namespace_id                BLOB PRIMARY KEY CHECK (length(namespace_id) = 16),
    protocol_version            INTEGER NOT NULL CHECK (protocol_version = 2),
    suite_id                    TEXT NOT NULL CHECK (suite_id = 'VDNS-PM-CP-2'),
    chain_id                    TEXT NOT NULL CHECK (length(chain_id) BETWEEN 1 AND 128),
    root_signing_public_key     BLOB NOT NULL CHECK (length(root_signing_public_key) = 32),
    root_key_id                 BLOB NOT NULL UNIQUE CHECK (length(root_key_id) = 32),
    current_secret_generation   INTEGER NOT NULL CHECK (current_secret_generation >= 1),
    status                      TEXT NOT NULL CHECK (status IN ('ACTIVE','SUSPENDED','REVOKED')),
    created_at_ms               INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms               INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms)
) STRICT;

CREATE TABLE root_signing_keys (
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    root_key_id                BLOB NOT NULL CHECK (length(root_key_id) = 32),
    public_key                 BLOB NOT NULL CHECK (length(public_key) = 32),
    secure_store_ref           TEXT UNIQUE CHECK (secure_store_ref IS NULL OR length(secure_store_ref) BETWEEN 1 AND 255),
    status                     TEXT NOT NULL CHECK (status IN ('ACTIVE','VERIFY_ONLY','DESTROYED')),
    valid_from_anchor_sequence INTEGER CHECK (valid_from_anchor_sequence IS NULL OR valid_from_anchor_sequence >= 0),
    retired_at_ms              INTEGER CHECK (retired_at_ms IS NULL OR retired_at_ms >= 0),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    PRIMARY KEY (namespace_id, root_key_id),
    UNIQUE (namespace_id, public_key),
    CHECK (status <> 'ACTIVE' OR secure_store_ref IS NOT NULL),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_namespace_one_active_root_key
ON root_signing_keys(namespace_id)
WHERE status = 'ACTIVE';

CREATE TABLE namespace_key_generations (
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    generation                 INTEGER NOT NULL CHECK (generation >= 1),
    secure_store_ref           TEXT NOT NULL UNIQUE CHECK (length(secure_store_ref) BETWEEN 1 AND 255),
    status                     TEXT NOT NULL CHECK (status IN ('ACTIVE','DECRYPT_ONLY','DESTROYED')),
    valid_from_anchor_sequence INTEGER CHECK (valid_from_anchor_sequence IS NULL OR valid_from_anchor_sequence >= 0),
    retired_at_ms              INTEGER CHECK (retired_at_ms IS NULL OR retired_at_ms >= 0),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    PRIMARY KEY (namespace_id, generation),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_namespace_one_active_generation
ON namespace_key_generations(namespace_id)
WHERE status = 'ACTIVE';

CREATE TABLE devices (
    device_id                  BLOB PRIMARY KEY CHECK (length(device_id) = 16),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    signing_public_key         BLOB NOT NULL CHECK (length(signing_public_key) = 32),
    hpke_public_key            BLOB NOT NULL CHECK (length(hpke_public_key) = 32),
    current_key_generation     INTEGER NOT NULL CHECK (current_key_generation >= 1),
    status                     TEXT NOT NULL CHECK (status IN ('ACTIVE','SUSPENDED','REVOKED')),
    last_accepted_counter      INTEGER NOT NULL DEFAULT 0 CHECK (last_accepted_counter >= 0),
    current_credential_hash    BLOB CHECK (current_credential_hash IS NULL OR length(current_credential_hash) = 32),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    UNIQUE (namespace_id, signing_public_key),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_devices_namespace_status
ON devices(namespace_id, status);

CREATE TABLE device_key_generations (
    device_id                  BLOB NOT NULL CHECK (length(device_id) = 16),
    key_generation             INTEGER NOT NULL CHECK (key_generation >= 1),
    signing_public_key         BLOB NOT NULL CHECK (length(signing_public_key) = 32),
    hpke_public_key            BLOB NOT NULL CHECK (length(hpke_public_key) = 32),
    signing_secret_ref         TEXT NOT NULL UNIQUE,
    hpke_secret_ref            TEXT NOT NULL UNIQUE,
    status                     TEXT NOT NULL CHECK (status IN ('ACTIVE','DECRYPT_ONLY','DESTROYED')),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    retired_at_ms              INTEGER CHECK (retired_at_ms IS NULL OR retired_at_ms >= created_at_ms),
    PRIMARY KEY (device_id, key_generation),
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_device_one_active_key_generation
ON device_key_generations(device_id)
WHERE status = 'ACTIVE';

CREATE TABLE device_operation_credentials (
    credential_hash            BLOB PRIMARY KEY CHECK (length(credential_hash) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    device_id                  BLOB NOT NULL CHECK (length(device_id) = 16),
    credential_cbor            BLOB NOT NULL CHECK (length(credential_cbor) BETWEEN 1 AND 65536),
    scope_kind                 TEXT NOT NULL CHECK (scope_kind IN ('NAMESPACE','EXPLICIT_SET','MERKLE_ROOT')),
    scope_root                 BLOB CHECK (scope_root IS NULL OR length(scope_root) = 32),
    valid_from_ms              INTEGER NOT NULL CHECK (valid_from_ms >= 0),
    valid_until_ms             INTEGER NOT NULL CHECK (valid_until_ms > valid_from_ms),
    secret_generation          INTEGER NOT NULL CHECK (secret_generation >= 1),
    status_reference_hash      BLOB NOT NULL CHECK (length(status_reference_hash) = 32),
    issuer_key_id              BLOB NOT NULL CHECK (length(issuer_key_id) = 32),
    root_signature             BLOB NOT NULL CHECK (length(root_signature) = 64),
    issued_at_ms               INTEGER NOT NULL CHECK (issued_at_ms >= 0),
    superseded_at_ms           INTEGER CHECK (superseded_at_ms IS NULL OR superseded_at_ms >= issued_at_ms),
    UNIQUE (namespace_id, device_id, credential_hash),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE RESTRICT,
    FOREIGN KEY (namespace_id, secret_generation)
        REFERENCES namespace_key_generations(namespace_id, generation) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_device_credentials_active_lookup
ON device_operation_credentials(namespace_id, device_id, valid_from_ms, valid_until_ms);

CREATE TABLE device_capabilities (
    credential_hash            BLOB NOT NULL CHECK (length(credential_hash) = 32),
    capability                 TEXT NOT NULL CHECK (capability IN ('READ','AUTOFILL','PUBLISH_AUDIT','CREATE','UPDATE','ROTATE','MIGRATE','REVOKE','DEVICE_ENROLL','RELATION_PUBLISH','AUDIT_ANALYZE')),
    PRIMARY KEY (credential_hash, capability),
    FOREIGN KEY (credential_hash) REFERENCES device_operation_credentials(credential_hash) ON DELETE CASCADE
) STRICT;

CREATE TABLE device_scope_items (
    credential_hash            BLOB NOT NULL CHECK (length(credential_hash) = 32),
    scoped_credential_id       BLOB NOT NULL CHECK (length(scoped_credential_id) = 32),
    PRIMARY KEY (credential_hash, scoped_credential_id),
    FOREIGN KEY (credential_hash) REFERENCES device_operation_credentials(credential_hash) ON DELETE CASCADE
) STRICT;

CREATE TABLE revocations (
    revocation_id              BLOB PRIMARY KEY CHECK (length(revocation_id) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    target_type                TEXT NOT NULL CHECK (target_type IN ('DEVICE','DEVICE_CREDENTIAL','CREDENTIAL','CAMPAIGN','KEY_GENERATION')),
    target_id                  BLOB NOT NULL CHECK (length(target_id) BETWEEN 1 AND 32),
    reason_code                TEXT NOT NULL CHECK (length(reason_code) BETWEEN 1 AND 128),
    status                     TEXT NOT NULL CHECK (status IN ('PENDING','FINALIZED')),
    event_id                   BLOB CHECK (event_id IS NULL OR length(event_id) = 32),
    log_id                     BLOB CHECK (log_id IS NULL OR length(log_id) = 16),
    leaf_index                 INTEGER CHECK (leaf_index IS NULL OR leaf_index >= 0),
    effective_anchor_sequence  INTEGER CHECK (effective_anchor_sequence IS NULL OR effective_anchor_sequence >= 0),
    new_secret_generation      INTEGER CHECK (new_secret_generation IS NULL OR new_secret_generation >= 1),
    root_signature             BLOB NOT NULL CHECK (length(root_signature) = 64),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    finalized_at_ms            INTEGER CHECK (finalized_at_ms IS NULL OR finalized_at_ms >= created_at_ms),
    CHECK (
      (status = 'PENDING' AND effective_anchor_sequence IS NULL AND finalized_at_ms IS NULL)
      OR
      (status = 'FINALIZED' AND effective_anchor_sequence IS NOT NULL AND finalized_at_ms IS NOT NULL)
    ),
    UNIQUE (namespace_id, target_type, target_id, effective_anchor_sequence),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_revocations_target
ON revocations(namespace_id, target_type, target_id, status);

CREATE TABLE content_objects (
    object_hash                BLOB PRIMARY KEY CHECK (length(object_hash) = 32),
    object_type                TEXT NOT NULL CHECK (object_type IN (
                                 'CREDENTIAL_DESCRIPTOR','CREDENTIAL_FIELD','AUDIT_EVENT','DEVICE_ENVELOPE',
                                 'PROOF_BUNDLE','SITE_EVIDENCE','MONITOR_EVIDENCE','CAMPAIGN_ATTACHMENT'
                               )),
    cipher_suite               TEXT NOT NULL CHECK (length(cipher_suite) BETWEEN 1 AND 64),
    key_generation             INTEGER CHECK (key_generation IS NULL OR key_generation >= 1),
    nonce                      BLOB CHECK (nonce IS NULL OR length(nonce) = 12),
    aad_hash                   BLOB CHECK (aad_hash IS NULL OR length(aad_hash) = 32),
    ciphertext_length          INTEGER NOT NULL CHECK (ciphertext_length >= 0),
    storage_relpath            TEXT NOT NULL UNIQUE
                                 CHECK (length(storage_relpath) BETWEEN 1 AND 512)
                                 CHECK (substr(storage_relpath, 1, 1) <> '/')
                                 CHECK (instr(storage_relpath, '..') = 0),
    state                      TEXT NOT NULL CHECK (state IN ('COMMITTED','MISSING','CORRUPT','GC_PENDING')),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    verified_at_ms             INTEGER CHECK (verified_at_ms IS NULL OR verified_at_ms >= created_at_ms)
) STRICT;

CREATE INDEX ix_content_objects_state_created
ON content_objects(state, created_at_ms);

CREATE TABLE namespace_generation_envelopes (
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    generation                 INTEGER NOT NULL CHECK (generation >= 1),
    device_id                  BLOB NOT NULL CHECK (length(device_id) = 16),
    device_key_generation      INTEGER NOT NULL CHECK (device_key_generation >= 1),
    envelope_object_hash       BLOB NOT NULL CHECK (length(envelope_object_hash) = 32),
    status                     TEXT NOT NULL CHECK (status IN ('ACTIVE','RETIRED')),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    acknowledged_at_ms         INTEGER CHECK (acknowledged_at_ms IS NULL OR acknowledged_at_ms >= created_at_ms),
    PRIMARY KEY (namespace_id, generation, device_id),
    UNIQUE (envelope_object_hash),
    FOREIGN KEY (namespace_id, generation)
        REFERENCES namespace_key_generations(namespace_id, generation) ON DELETE RESTRICT,
    FOREIGN KEY (device_id, device_key_generation)
        REFERENCES device_key_generations(device_id, key_generation) ON DELETE RESTRICT,
    FOREIGN KEY (envelope_object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_generation_envelopes_device
ON namespace_generation_envelopes(device_id, generation DESC, status);

CREATE TABLE credentials (
    credential_id              BLOB PRIMARY KEY CHECK (length(credential_id) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    aggregate_status           TEXT NOT NULL CHECK (aggregate_status IN ('ACTIVE','SUSPENDED','REVOKED')),
    current_local_version      INTEGER CHECK (current_local_version IS NULL OR current_local_version >= 1),
    current_accepted_version   INTEGER CHECK (current_accepted_version IS NULL OR current_accepted_version >= 1),
    origin_commitment          BLOB NOT NULL CHECK (length(origin_commitment) = 32),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    CHECK (
      current_accepted_version IS NULL
      OR (current_local_version IS NOT NULL AND current_local_version >= current_accepted_version)
    ),
    UNIQUE (namespace_id, credential_id),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_credentials_namespace_status
ON credentials(namespace_id, aggregate_status);

CREATE INDEX ix_credentials_origin_commitment
ON credentials(namespace_id, origin_commitment);

CREATE TABLE credential_versions (
    credential_id              BLOB NOT NULL CHECK (length(credential_id) = 32),
    version                    INTEGER NOT NULL CHECK (version >= 1),
    password_version           INTEGER NOT NULL CHECK (password_version >= 1),
    status                     TEXT NOT NULL CHECK (status IN (
                                 'PENDING_CANDIDATE','SITE_UPDATE_PENDING','FAILED_RETRYABLE',
                                 'SITE_STATUS_UNKNOWN','SITE_CHANGED_LOCAL_COMMIT_PENDING',
                                 'ACTIVE_LOCAL_PENDING_PROOF','ACTIVE','SUPERSEDED','ABORTED'
                               )),
    descriptor_hash            BLOB NOT NULL CHECK (length(descriptor_hash) = 32),
    descriptor_object_hash     BLOB NOT NULL CHECK (length(descriptor_object_hash) = 32),
    previous_descriptor_hash   BLOB CHECK (previous_descriptor_hash IS NULL OR length(previous_descriptor_hash) = 32),
    policy_hash                BLOB NOT NULL CHECK (length(policy_hash) = 32),
    created_by_event_id        BLOB CHECK (created_by_event_id IS NULL OR length(created_by_event_id) = 32),
    site_evidence_object_hash  BLOB CHECK (site_evidence_object_hash IS NULL OR length(site_evidence_object_hash) = 32),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    confirmed_at_ms            INTEGER CHECK (confirmed_at_ms IS NULL OR confirmed_at_ms >= created_at_ms),
    PRIMARY KEY (credential_id, version),
    UNIQUE (credential_id, descriptor_hash),
    CHECK (
      (version = 1 AND previous_descriptor_hash IS NULL)
      OR (version > 1 AND previous_descriptor_hash IS NOT NULL)
    ),
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT,
    FOREIGN KEY (descriptor_object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT,
    FOREIGN KEY (site_evidence_object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_one_active_version_per_credential
ON credential_versions(credential_id)
WHERE status = 'ACTIVE';

CREATE UNIQUE INDEX ux_one_local_pending_proof_per_credential
ON credential_versions(credential_id)
WHERE status = 'ACTIVE_LOCAL_PENDING_PROOF';

CREATE INDEX ix_credential_versions_status
ON credential_versions(credential_id, status, version DESC);

CREATE TABLE credential_version_fields (
    credential_id              BLOB NOT NULL CHECK (length(credential_id) = 32),
    version                    INTEGER NOT NULL CHECK (version >= 1),
    field_type                 TEXT NOT NULL CHECK (field_type IN ('ORIGIN','USERNAME','PASSWORD','TOTP','RECOVERY_CODES','NOTE')),
    encryption_version         INTEGER NOT NULL CHECK (encryption_version >= 1 AND encryption_version <= version),
    field_object_id            BLOB NOT NULL CHECK (length(field_object_id) = 32),
    field_object_hash          BLOB NOT NULL CHECK (length(field_object_hash) = 32),
    envelope_id                BLOB NOT NULL CHECK (length(envelope_id) = 32),
    envelope_hash              BLOB NOT NULL CHECK (length(envelope_hash) = 32),
    object_hash                BLOB NOT NULL CHECK (length(object_hash) = 32),
    wrapped_dek                BLOB NOT NULL CHECK (length(wrapped_dek) BETWEEN 1 AND 4096),
    wrapped_dek_suite          TEXT NOT NULL CHECK (length(wrapped_dek_suite) BETWEEN 1 AND 64),
    crypto_policy_hash         BLOB NOT NULL CHECK (length(crypto_policy_hash) = 32),
    origin_binding             BLOB NOT NULL CHECK (length(origin_binding) = 32),
    field_digest               BLOB NOT NULL CHECK (length(field_digest) = 32),
    secret_generation          INTEGER NOT NULL CHECK (secret_generation >= 1),
    PRIMARY KEY (credential_id, version, field_type),
    FOREIGN KEY (credential_id, version)
        REFERENCES credential_versions(credential_id, version) ON DELETE RESTRICT,
    FOREIGN KEY (object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_version_fields_object
ON credential_version_fields(object_hash);

CREATE TABLE operation_events (
    event_id                   BLOB PRIMARY KEY CHECK (length(event_id) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    device_id                  BLOB NOT NULL CHECK (length(device_id) = 16),
    device_credential_hash     BLOB NOT NULL CHECK (length(device_credential_hash) = 32),
    credential_id              BLOB CHECK (credential_id IS NULL OR length(credential_id) = 32),
    operation_type             TEXT NOT NULL CHECK (operation_type IN (
                                 'CREATE','RESOLVE','AUTOFILL','USE_OBSERVED','UPDATE_PREPARE',
                                 'UPDATE_CONFIRM','SYNC_PUBLISH','SYNC_ACCEPT','ROTATE','MIGRATE',
                                 'SUSPEND','REVOKE','DEVICE_ENROLL','RELATION_PUBLISH',
                                 'AUDIT_ANALYZE','ANALYZE_EXPOSURE','REMEDIATION_COMMIT'
                               )),
    old_version                INTEGER CHECK (old_version IS NULL OR old_version >= 1),
    new_version                INTEGER CHECK (new_version IS NULL OR new_version >= 1),
    device_pseudonym           BLOB NOT NULL CHECK (length(device_pseudonym) = 16),
    origin_commitment          BLOB CHECK (origin_commitment IS NULL OR length(origin_commitment) = 32),
    event_payload_hash         BLOB NOT NULL CHECK (length(event_payload_hash) = 32),
    vrf_epoch                  INTEGER CHECK (vrf_epoch IS NULL OR vrf_epoch >= 0),
    secret_generation          INTEGER NOT NULL CHECK (secret_generation >= 1),
    device_counter             INTEGER NOT NULL CHECK (device_counter >= 1),
    previous_event_hash        BLOB CHECK (previous_event_hash IS NULL OR length(previous_event_hash) = 32),
    event_cbor                 BLOB NOT NULL CHECK (length(event_cbor) BETWEEN 1 AND 1048576),
    event_digest               BLOB NOT NULL UNIQUE CHECK (length(event_digest) = 32),
    device_signature           BLOB NOT NULL CHECK (length(device_signature) = 64),
    observed_at_ms             INTEGER CHECK (observed_at_ms IS NULL OR observed_at_ms >= 0),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    UNIQUE (namespace_id, device_id, device_counter),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE RESTRICT,
    FOREIGN KEY (device_credential_hash)
        REFERENCES device_operation_credentials(credential_hash) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT,
    FOREIGN KEY (namespace_id, secret_generation)
        REFERENCES namespace_key_generations(namespace_id, generation) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_operation_events_credential_version
ON operation_events(credential_id, new_version, created_at_ms);

CREATE INDEX ix_operation_events_epoch
ON operation_events(namespace_id, vrf_epoch, created_at_ms);

CREATE TABLE event_publication_outbox (
    event_id                   BLOB PRIMARY KEY CHECK (length(event_id) = 32),
    object_hash                BLOB CHECK (object_hash IS NULL OR length(object_hash) = 32),
    publication_state          TEXT NOT NULL CHECK (publication_state IN (
                                 'LOCAL_PENDING','OBJECT_STORED','LOG_INCLUDED',
                                 'CHECKPOINT_ANCHORED','FAILED_RETRYABLE'
                               )),
    retry_count                INTEGER NOT NULL DEFAULT 0 CHECK (retry_count >= 0),
    next_attempt_at_ms         INTEGER CHECK (next_attempt_at_ms IS NULL OR next_attempt_at_ms >= 0),
    log_id                     BLOB CHECK (log_id IS NULL OR length(log_id) = 16),
    leaf_index                 INTEGER CHECK (leaf_index IS NULL OR leaf_index >= 0),
    included_tree_size         INTEGER CHECK (included_tree_size IS NULL OR included_tree_size >= 1),
    anchor_sequence            INTEGER CHECK (anchor_sequence IS NULL OR anchor_sequence >= 0),
    lease_token                BLOB CHECK (lease_token IS NULL OR length(lease_token) = 16),
    lease_expires_at_ms        INTEGER CHECK (lease_expires_at_ms IS NULL OR lease_expires_at_ms >= 0),
    last_error_code            TEXT CHECK (last_error_code IS NULL OR length(last_error_code) <= 128),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    FOREIGN KEY (event_id) REFERENCES operation_events(event_id) ON DELETE RESTRICT,
    FOREIGN KEY (object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_outbox_ready
ON event_publication_outbox(publication_state, next_attempt_at_ms, lease_expires_at_ms);

CREATE TABLE event_verdicts (
    verdict_id                 INTEGER PRIMARY KEY,
    event_id                   BLOB NOT NULL CHECK (length(event_id) = 32),
    evaluated_tree_size        INTEGER CHECK (evaluated_tree_size IS NULL OR evaluated_tree_size >= 0),
    evaluated_anchor_sequence  INTEGER CHECK (evaluated_anchor_sequence IS NULL OR evaluated_anchor_sequence >= 0),
    policy_hash                BLOB NOT NULL CHECK (length(policy_hash) = 32),
    verdict                    TEXT NOT NULL CHECK (verdict IN (
                                 'ACCEPT','DEGRADED_OFFLINE','DEGRADED_PENDING_LOG',
                                 'DEGRADED_LOCAL_COMMIT_PENDING','REJECT'
                               )),
    reason_code                TEXT CHECK (reason_code IS NULL OR length(reason_code) <= 128),
    layer_trace_cbor           BLOB NOT NULL CHECK (length(layer_trace_cbor) BETWEEN 1 AND 1048576),
    is_final                   INTEGER NOT NULL CHECK (is_final IN (0,1)),
    evaluated_at_ms            INTEGER NOT NULL CHECK (evaluated_at_ms >= 0),
    CHECK (is_final = 0 OR verdict IN ('ACCEPT','REJECT')),
    UNIQUE (event_id, evaluated_tree_size, evaluated_anchor_sequence, policy_hash),
    FOREIGN KEY (event_id) REFERENCES operation_events(event_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE idempotency_records (
    idempotency_key            TEXT PRIMARY KEY CHECK (length(idempotency_key) BETWEEN 16 AND 255),
    operation_scope            TEXT NOT NULL CHECK (length(operation_scope) BETWEEN 1 AND 128),
    request_body_hash          BLOB NOT NULL CHECK (length(request_body_hash) = 32),
    response_status            INTEGER NOT NULL CHECK (response_status BETWEEN 100 AND 599),
    response_body              BLOB NOT NULL CHECK (length(response_body) <= 1048576),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    expires_at_ms              INTEGER NOT NULL CHECK (expires_at_ms > created_at_ms)
) STRICT;

CREATE INDEX ix_idempotency_expiry ON idempotency_records(expires_at_ms);

CREATE TABLE transparency_logs (
    log_id                     BLOB PRIMARY KEY CHECK (length(log_id) = 16),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    log_public_key             BLOB NOT NULL CHECK (length(log_public_key) = 32),
    hash_algorithm             TEXT NOT NULL CHECK (hash_algorithm = 'SHA-256'),
    tree_size                  INTEGER NOT NULL DEFAULT 0 CHECK (tree_size >= 0),
    root_hash                  BLOB NOT NULL CHECK (length(root_hash) = 32),
    status                     TEXT NOT NULL CHECK (status IN ('ACTIVE','FROZEN')),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    UNIQUE (namespace_id, log_id),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE transparency_leaves (
    log_id                     BLOB NOT NULL CHECK (length(log_id) = 16),
    leaf_index                 INTEGER NOT NULL CHECK (leaf_index >= 0),
    leaf_cbor                  BLOB NOT NULL CHECK (length(leaf_cbor) BETWEEN 1 AND 1048576),
    leaf_hash                  BLOB NOT NULL CHECK (length(leaf_hash) = 32),
    event_digest               BLOB NOT NULL CHECK (length(event_digest) = 32),
    epoch                      INTEGER NOT NULL CHECK (epoch >= 0),
    device_pseudonym           BLOB NOT NULL CHECK (length(device_pseudonym) = 16),
    appended_at_ms             INTEGER NOT NULL CHECK (appended_at_ms >= 0),
    PRIMARY KEY (log_id, leaf_index),
    UNIQUE (log_id, event_digest),
    FOREIGN KEY (log_id) REFERENCES transparency_logs(log_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_transparency_leaves_epoch
ON transparency_leaves(log_id, epoch, leaf_index);

CREATE TABLE transparency_nodes (
    log_id                     BLOB NOT NULL CHECK (length(log_id) = 16),
    level                      INTEGER NOT NULL CHECK (level >= 0),
    node_index                 INTEGER NOT NULL CHECK (node_index >= 0),
    node_hash                  BLOB NOT NULL CHECK (length(node_hash) = 32),
    PRIMARY KEY (log_id, level, node_index),
    FOREIGN KEY (log_id) REFERENCES transparency_logs(log_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE signed_tree_heads (
    log_id                     BLOB NOT NULL CHECK (length(log_id) = 16),
    tree_size                  INTEGER NOT NULL CHECK (tree_size >= 0),
    root_hash                  BLOB NOT NULL CHECK (length(root_hash) = 32),
    checkpoint_cbor            BLOB NOT NULL CHECK (length(checkpoint_cbor) BETWEEN 1 AND 65536),
    checkpoint_hash            BLOB NOT NULL UNIQUE CHECK (length(checkpoint_hash) = 32),
    log_key_id                 BLOB NOT NULL CHECK (length(log_key_id) = 32),
    log_signature              BLOB NOT NULL CHECK (length(log_signature) = 64),
    anchor_sequence            INTEGER CHECK (anchor_sequence IS NULL OR anchor_sequence >= 0),
    trust_state                TEXT NOT NULL CHECK (trust_state IN ('OBSERVED','ACCEPTED','CONFLICTING','REJECTED')),
    source_id                  TEXT NOT NULL CHECK (length(source_id) BETWEEN 1 AND 128),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    PRIMARY KEY (log_id, tree_size, root_hash),
    FOREIGN KEY (log_id) REFERENCES transparency_logs(log_id) ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_one_accepted_root_per_tree_size
ON signed_tree_heads(log_id, tree_size)
WHERE trust_state = 'ACCEPTED';

CREATE TABLE consistency_proofs (
    log_id                     BLOB NOT NULL CHECK (length(log_id) = 16),
    from_tree_size             INTEGER NOT NULL CHECK (from_tree_size >= 0),
    to_tree_size               INTEGER NOT NULL CHECK (to_tree_size > from_tree_size),
    from_root_hash             BLOB NOT NULL CHECK (length(from_root_hash) = 32),
    to_root_hash               BLOB NOT NULL CHECK (length(to_root_hash) = 32),
    proof_cbor                 BLOB NOT NULL CHECK (length(proof_cbor) BETWEEN 1 AND 1048576),
    verified                   INTEGER NOT NULL CHECK (verified IN (0,1)),
    verified_at_ms             INTEGER CHECK (verified_at_ms IS NULL OR verified_at_ms >= 0),
    PRIMARY KEY (log_id, from_tree_size, to_tree_size, from_root_hash, to_root_hash),
    FOREIGN KEY (log_id) REFERENCES transparency_logs(log_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE event_log_receipts (
    event_id                   BLOB PRIMARY KEY CHECK (length(event_id) = 32),
    log_id                     BLOB NOT NULL CHECK (length(log_id) = 16),
    leaf_index                 INTEGER NOT NULL CHECK (leaf_index >= 0),
    included_tree_size         INTEGER NOT NULL CHECK (included_tree_size > leaf_index),
    checkpoint_hash            BLOB NOT NULL CHECK (length(checkpoint_hash) = 32),
    inclusion_proof_cbor       BLOB NOT NULL CHECK (length(inclusion_proof_cbor) BETWEEN 1 AND 1048576),
    verified_at_ms             INTEGER NOT NULL CHECK (verified_at_ms >= 0),
    UNIQUE (log_id, leaf_index),
    FOREIGN KEY (event_id) REFERENCES operation_events(event_id) ON DELETE RESTRICT,
    FOREIGN KEY (log_id, leaf_index) REFERENCES transparency_leaves(log_id, leaf_index) ON DELETE RESTRICT,
    FOREIGN KEY (checkpoint_hash) REFERENCES signed_tree_heads(checkpoint_hash) ON DELETE RESTRICT
) STRICT;

CREATE TABLE namespace_state_roots (
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    root_type                  TEXT NOT NULL CHECK (root_type IN ('IDENTITY','AUTHORIZATION','REVOCATION','CREDENTIAL','AUDIT','ROTATION')),
    sequence                   INTEGER NOT NULL CHECK (sequence >= 0),
    root_hash                  BLOB NOT NULL CHECK (length(root_hash) = 32),
    source_event_id            BLOB CHECK (source_event_id IS NULL OR length(source_event_id) = 32),
    anchor_status              TEXT NOT NULL CHECK (anchor_status IN ('PREPARED','SUBMITTED','FINALIZED','REORGED','REJECTED')),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    PRIMARY KEY (namespace_id, root_type, sequence),
    UNIQUE (namespace_id, root_type, sequence, root_hash),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (source_event_id) REFERENCES operation_events(event_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE vrf_epochs (
    chain_id                   TEXT NOT NULL CHECK (length(chain_id) BETWEEN 1 AND 128),
    epoch                      INTEGER NOT NULL CHECK (epoch >= 0),
    provider_type              TEXT NOT NULL CHECK (provider_type IN ('RFC9381','SIMULATED')),
    suite_id                   TEXT NOT NULL CHECK (length(suite_id) BETWEEN 1 AND 128),
    public_key                 BLOB NOT NULL CHECK (length(public_key) BETWEEN 1 AND 256),
    alpha_hash                 BLOB NOT NULL CHECK (length(alpha_hash) = 32),
    output                     BLOB NOT NULL CHECK (length(output) BETWEEN 1 AND 256),
    proof                      BLOB NOT NULL CHECK (length(proof) BETWEEN 1 AND 4096),
    proof_hash                 BLOB NOT NULL CHECK (length(proof_hash) = 32),
    status                     TEXT NOT NULL CHECK (status IN ('OBSERVED','FINALIZED','REJECTED')),
    finalized_anchor_sequence  INTEGER CHECK (finalized_anchor_sequence IS NULL OR finalized_anchor_sequence >= 0),
    observed_at_ms             INTEGER NOT NULL CHECK (observed_at_ms >= 0),
    finalized_at_ms            INTEGER CHECK (finalized_at_ms IS NULL OR finalized_at_ms >= observed_at_ms),
    PRIMARY KEY (chain_id, epoch),
    CHECK (
      (status = 'FINALIZED' AND finalized_anchor_sequence IS NOT NULL AND finalized_at_ms IS NOT NULL)
      OR status <> 'FINALIZED'
    )
) STRICT;

CREATE TABLE anchors (
    chain_id                   TEXT NOT NULL CHECK (length(chain_id) BETWEEN 1 AND 128),
    namespace_commitment       BLOB NOT NULL CHECK (length(namespace_commitment) = 32),
    checkpoint_type            TEXT NOT NULL CHECK (checkpoint_type IN (
                                 'IDENTITY','AUTHORIZATION','REVOCATION','CREDENTIAL',
                                 'AUDIT','AFFECTED','ROTATION','VRF'
                               )),
    sequence                   INTEGER NOT NULL CHECK (sequence >= 0),
    epoch                      INTEGER CHECK (epoch IS NULL OR epoch >= 0),
    tree_size                  INTEGER CHECK (tree_size IS NULL OR tree_size >= 0),
    root_hash                  BLOB NOT NULL CHECK (length(root_hash) = 32),
    vrf_output_hash            BLOB CHECK (vrf_output_hash IS NULL OR length(vrf_output_hash) = 32),
    vrf_proof_hash             BLOB CHECK (vrf_proof_hash IS NULL OR length(vrf_proof_hash) = 32),
    affected_root              BLOB CHECK (affected_root IS NULL OR length(affected_root) = 32),
    rotation_root              BLOB CHECK (rotation_root IS NULL OR length(rotation_root) = 32),
    tx_hash                    BLOB CHECK (tx_hash IS NULL OR length(tx_hash) = 32),
    block_number               INTEGER CHECK (block_number IS NULL OR block_number >= 0),
    confirmation_depth         INTEGER NOT NULL DEFAULT 0 CHECK (confirmation_depth >= 0),
    status                     TEXT NOT NULL CHECK (status IN ('PREPARED','SUBMITTED','FINALIZED','REORGED','REJECTED')),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    finalized_at_ms            INTEGER CHECK (finalized_at_ms IS NULL OR finalized_at_ms >= created_at_ms),
    PRIMARY KEY (chain_id, namespace_commitment, checkpoint_type, sequence),
    CHECK (
      (status = 'FINALIZED' AND tx_hash IS NOT NULL AND block_number IS NOT NULL AND finalized_at_ms IS NOT NULL)
      OR status <> 'FINALIZED'
    )
) STRICT;

CREATE INDEX ix_anchors_finality
ON anchors(chain_id, namespace_commitment, status, sequence DESC);

CREATE TABLE exposure_analyses (
    analysis_id                 BLOB PRIMARY KEY CHECK (length(analysis_id) = 32),
    namespace_id                BLOB NOT NULL CHECK (length(namespace_id) = 16),
    window_start_ms             INTEGER NOT NULL CHECK (window_start_ms >= 0),
    window_end_ms               INTEGER NOT NULL CHECK (window_end_ms >= window_start_ms),
    start_epoch                 INTEGER CHECK (start_epoch IS NULL OR start_epoch >= 0),
    end_epoch                   INTEGER CHECK (end_epoch IS NULL OR end_epoch >= 0),
    time_confidence             TEXT NOT NULL CHECK (time_confidence IN ('HIGH','LOW_UNKNOWN_START','LOW_UNKNOWN_END','LOW_BOTH')),
    evidence_threshold          TEXT NOT NULL CHECK (evidence_threshold IN (
                                  'AUTOFILL_OBSERVED','SUBMIT_OBSERVED','LOGIN_INFERRED',
                                  'USER_CONFIRMED','SITE_CONFIRMED'
                                )),
    analysis_policy_version     INTEGER NOT NULL CHECK (analysis_policy_version >= 1),
    analysis_policy_hash        BLOB NOT NULL CHECK (length(analysis_policy_hash) = 32),
    source_log_id               BLOB NOT NULL CHECK (length(source_log_id) = 16),
    source_tree_size            INTEGER NOT NULL CHECK (source_tree_size >= 0),
    source_root_hash            BLOB NOT NULL CHECK (length(source_root_hash) = 32),
    secret_generation           INTEGER NOT NULL CHECK (secret_generation >= 1),
    status                      TEXT NOT NULL CHECK (status IN ('PENDING','RUNNING','COMPLETED','FAILED')),
    result_count                INTEGER NOT NULL DEFAULT 0 CHECK (result_count >= 0),
    created_at_ms               INTEGER NOT NULL CHECK (created_at_ms >= 0),
    completed_at_ms             INTEGER CHECK (completed_at_ms IS NULL OR completed_at_ms >= created_at_ms),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (source_log_id) REFERENCES transparency_logs(log_id) ON DELETE RESTRICT,
    FOREIGN KEY (namespace_id, secret_generation)
        REFERENCES namespace_key_generations(namespace_id, generation) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_exposure_window
ON exposure_analyses(namespace_id, window_start_ms, window_end_ms, status);

CREATE TABLE exposure_analysis_items (
    analysis_id                 BLOB NOT NULL CHECK (length(analysis_id) = 32),
    credential_id              BLOB NOT NULL CHECK (length(credential_id) = 32),
    old_version                INTEGER NOT NULL CHECK (old_version >= 1),
    current_version            INTEGER NOT NULL CHECK (current_version >= 1),
    risk_class                 TEXT NOT NULL CHECK (risk_class IN (
                                  'CURRENT_DIRECT','HISTORICAL_EXPOSURE','INSUFFICIENT_EVIDENCE',
                                  'REMEDIATED','UNAFFECTED'
                                )),
    strongest_evidence         TEXT CHECK (strongest_evidence IS NULL OR strongest_evidence IN (
                                  'AUTOFILL_OBSERVED','SUBMIT_OBSERVED','LOGIN_INFERRED',
                                  'USER_CONFIRMED','SITE_CONFIRMED'
                                )),
    supporting_event_root      BLOB CHECK (supporting_event_root IS NULL OR length(supporting_event_root) = 32),
    supporting_event_count     INTEGER NOT NULL DEFAULT 0 CHECK (supporting_event_count >= 0),
    affected_leaf_hash         BLOB CHECK (affected_leaf_hash IS NULL OR length(affected_leaf_hash) = 32),
    default_included           INTEGER NOT NULL CHECK (default_included IN (0,1)),
    user_decision              TEXT NOT NULL CHECK (user_decision IN ('DEFAULT','INCLUDE','EXCLUDE')),
    decision_device_id         BLOB CHECK (decision_device_id IS NULL OR length(decision_device_id) = 16),
    decision_signature         BLOB CHECK (decision_signature IS NULL OR length(decision_signature) = 64),
    proof_bundle_object_hash   BLOB CHECK (proof_bundle_object_hash IS NULL OR length(proof_bundle_object_hash) = 32),
    PRIMARY KEY (analysis_id, credential_id),
    FOREIGN KEY (analysis_id) REFERENCES exposure_analyses(analysis_id) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT,
    FOREIGN KEY (decision_device_id) REFERENCES devices(device_id) ON DELETE RESTRICT,
    FOREIGN KEY (proof_bundle_object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT,
    CHECK (
      (user_decision = 'DEFAULT' AND decision_device_id IS NULL AND decision_signature IS NULL)
      OR
      (user_decision <> 'DEFAULT' AND decision_device_id IS NOT NULL AND decision_signature IS NOT NULL)
    )
) STRICT;

CREATE TABLE rotation_campaigns (
    campaign_id                 BLOB PRIMARY KEY CHECK (length(campaign_id) = 32),
    namespace_id                BLOB NOT NULL CHECK (length(namespace_id) = 16),
    analysis_id                 BLOB NOT NULL CHECK (length(analysis_id) = 32),
    header_cbor                 BLOB NOT NULL CHECK (length(header_cbor) BETWEEN 1 AND 1048576),
    header_hash                 BLOB NOT NULL UNIQUE CHECK (length(header_hash) = 32),
    source_checkpoint_hash      BLOB NOT NULL CHECK (length(source_checkpoint_hash) = 32),
    secret_generation           INTEGER NOT NULL CHECK (secret_generation >= 1),
    affected_root               BLOB NOT NULL CHECK (length(affected_root) = 32),
    old_version_root            BLOB NOT NULL CHECK (length(old_version_root) = 32),
    credential_count            INTEGER NOT NULL CHECK (credential_count >= 1),
    status                      TEXT NOT NULL CHECK (status IN (
                                  'DRAFT','AFFECTED_COMMITTED','AWAITING_BEACON','IN_PROGRESS',
                                  'PARTIAL','COMPLETED','CANCELLED','FAILED'
                                )),
    commit_log_id               BLOB CHECK (commit_log_id IS NULL OR length(commit_log_id) = 16),
    commit_tree_size            INTEGER CHECK (commit_tree_size IS NULL OR commit_tree_size >= 1),
    commit_anchor_sequence      INTEGER CHECK (commit_anchor_sequence IS NULL OR commit_anchor_sequence >= 0),
    checkpoint_epoch            INTEGER CHECK (checkpoint_epoch IS NULL OR checkpoint_epoch >= 0),
    min_future_epoch_k          INTEGER NOT NULL DEFAULT 1 CHECK (min_future_epoch_k >= 1),
    selected_vrf_epoch          INTEGER CHECK (selected_vrf_epoch IS NULL OR selected_vrf_epoch >= 0),
    beacon_output_hash          BLOB CHECK (beacon_output_hash IS NULL OR length(beacon_output_hash) = 32),
    beacon_proof_hash           BLOB CHECK (beacon_proof_hash IS NULL OR length(beacon_proof_hash) = 32),
    rotation_policy_hash        BLOB NOT NULL CHECK (length(rotation_policy_hash) = 32),
    completed_count             INTEGER NOT NULL DEFAULT 0 CHECK (completed_count >= 0),
    pending_count               INTEGER NOT NULL CHECK (pending_count >= 0),
    result_root                 BLOB CHECK (result_root IS NULL OR length(result_root) = 32),
    initiator_device_id         BLOB NOT NULL CHECK (length(initiator_device_id) = 16),
    initiator_signature         BLOB NOT NULL CHECK (length(initiator_signature) = 64),
    created_at_ms               INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms               INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    finalized_at_ms             INTEGER CHECK (finalized_at_ms IS NULL OR finalized_at_ms >= created_at_ms),
    CHECK (completed_count + pending_count <= credential_count),
    CHECK (
      selected_vrf_epoch IS NULL
      OR (checkpoint_epoch IS NOT NULL AND selected_vrf_epoch > checkpoint_epoch + min_future_epoch_k - 1)
    ),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (analysis_id) REFERENCES exposure_analyses(analysis_id) ON DELETE RESTRICT,
    FOREIGN KEY (source_checkpoint_hash) REFERENCES signed_tree_heads(checkpoint_hash) ON DELETE RESTRICT,
    FOREIGN KEY (commit_log_id) REFERENCES transparency_logs(log_id) ON DELETE RESTRICT,
    FOREIGN KEY (initiator_device_id) REFERENCES devices(device_id) ON DELETE RESTRICT,
    FOREIGN KEY (namespace_id, secret_generation)
        REFERENCES namespace_key_generations(namespace_id, generation) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_rotation_campaign_status
ON rotation_campaigns(namespace_id, status, updated_at_ms);

CREATE TABLE rotation_items (
    campaign_id                 BLOB NOT NULL CHECK (length(campaign_id) = 32),
    credential_id               BLOB NOT NULL CHECK (length(credential_id) = 32),
    old_version                 INTEGER NOT NULL CHECK (old_version >= 1),
    new_version                 INTEGER NOT NULL CHECK (new_version > old_version),
    policy_hash                 BLOB NOT NULL CHECK (length(policy_hash) = 32),
    supporting_event_root       BLOB NOT NULL CHECK (length(supporting_event_root) = 32),
    affected_leaf_hash          BLOB NOT NULL CHECK (length(affected_leaf_hash) = 32),
    status                      TEXT NOT NULL CHECK (status IN (
                                  'PENDING','SITE_UPDATE_PENDING','SITE_CONFIRMED','RESULT_ANCHORED',
                                  'FAILED_RETRYABLE','SITE_STATUS_UNKNOWN','CANCELLED'
                                )),
    attempt_no                  INTEGER NOT NULL DEFAULT 0 CHECK (attempt_no >= 0),
    candidate_password_object_hash BLOB CHECK (candidate_password_object_hash IS NULL OR length(candidate_password_object_hash) = 32),
    site_evidence_object_hash   BLOB CHECK (site_evidence_object_hash IS NULL OR length(site_evidence_object_hash) = 32),
    site_result_digest          BLOB CHECK (site_result_digest IS NULL OR length(site_result_digest) = 32),
    last_error_code             TEXT CHECK (last_error_code IS NULL OR length(last_error_code) <= 128),
    lease_token                 BLOB CHECK (lease_token IS NULL OR length(lease_token) = 16),
    lease_expires_at_ms         INTEGER CHECK (lease_expires_at_ms IS NULL OR lease_expires_at_ms >= 0),
    created_at_ms               INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms               INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    confirmed_at_ms             INTEGER CHECK (confirmed_at_ms IS NULL OR confirmed_at_ms >= created_at_ms),
    anchored_at_ms              INTEGER CHECK (anchored_at_ms IS NULL OR anchored_at_ms >= created_at_ms),
    PRIMARY KEY (campaign_id, credential_id),
    FOREIGN KEY (campaign_id) REFERENCES rotation_campaigns(campaign_id) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id, old_version)
        REFERENCES credential_versions(credential_id, version) ON DELETE RESTRICT,
    FOREIGN KEY (candidate_password_object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT,
    FOREIGN KEY (site_evidence_object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_rotation_items_work_queue
ON rotation_items(campaign_id, status, lease_expires_at_ms, updated_at_ms);

CREATE TABLE monitor_checkpoints (
    monitor_id                  BLOB NOT NULL CHECK (length(monitor_id) = 16),
    log_id                      BLOB NOT NULL CHECK (length(log_id) = 16),
    tree_size                   INTEGER NOT NULL CHECK (tree_size >= 0),
    root_hash                   BLOB NOT NULL CHECK (length(root_hash) = 32),
    checkpoint_hash             BLOB NOT NULL CHECK (length(checkpoint_hash) = 32),
    anchor_sequence             INTEGER CHECK (anchor_sequence IS NULL OR anchor_sequence >= 0),
    source_id                   TEXT NOT NULL CHECK (length(source_id) BETWEEN 1 AND 128),
    observed_at_ms              INTEGER NOT NULL CHECK (observed_at_ms >= 0),
    PRIMARY KEY (monitor_id, log_id, tree_size, root_hash)
) STRICT;

CREATE INDEX ix_monitor_checkpoint_latest
ON monitor_checkpoints(monitor_id, log_id, tree_size DESC);

CREATE TABLE monitor_findings (
    finding_id                  BLOB PRIMARY KEY CHECK (length(finding_id) = 32),
    monitor_id                  BLOB NOT NULL CHECK (length(monitor_id) = 16),
    log_id                      BLOB CHECK (log_id IS NULL OR length(log_id) = 16),
    finding_type                TEXT NOT NULL CHECK (finding_type IN (
                                  'SPLIT_VIEW','INCONSISTENT_HISTORY','CHECKPOINT_ROLLBACK',
                                  'DOUBLE_PUBLISH','ANCHOR_CONFLICT'
                                )),
    severity                    TEXT NOT NULL CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    first_evidence_hash         BLOB NOT NULL CHECK (length(first_evidence_hash) = 32),
    second_evidence_hash        BLOB NOT NULL CHECK (length(second_evidence_hash) = 32),
    evidence_object_hash        BLOB NOT NULL CHECK (length(evidence_object_hash) = 32),
    status                      TEXT NOT NULL CHECK (status IN ('OPEN','ACKNOWLEDGED','RESOLVED','FALSE_POSITIVE')),
    detected_at_ms              INTEGER NOT NULL CHECK (detected_at_ms >= 0),
    resolved_at_ms              INTEGER CHECK (resolved_at_ms IS NULL OR resolved_at_ms >= detected_at_ms),
    FOREIGN KEY (evidence_object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_monitor_findings_open
ON monitor_findings(status, severity, detected_at_ms DESC);

-- 指向的版本必须真实存在；循环外键改用触发器，便于同一 deferred 事务创建聚合和首版本。
CREATE TRIGGER trg_credentials_pointer_insert
BEFORE INSERT ON credentials
WHEN
  (NEW.current_local_version IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM credential_versions
    WHERE credential_id = NEW.credential_id AND version = NEW.current_local_version
  ))
  OR
  (NEW.current_accepted_version IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM credential_versions
    WHERE credential_id = NEW.credential_id AND version = NEW.current_accepted_version
  ))
BEGIN
  SELECT RAISE(ABORT, 'credential current version pointer does not exist');
END;

CREATE TRIGGER trg_credentials_pointer_update
BEFORE UPDATE OF current_local_version, current_accepted_version ON credentials
WHEN
  (NEW.current_local_version IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM credential_versions
    WHERE credential_id = NEW.credential_id AND version = NEW.current_local_version
  ))
  OR
  (NEW.current_accepted_version IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM credential_versions
    WHERE credential_id = NEW.credential_id AND version = NEW.current_accepted_version
  ))
BEGIN
  SELECT RAISE(ABORT, 'credential current version pointer does not exist');
END;

-- 签名事件、日志叶和固定 Merkle 节点是 append-only 事实。
CREATE TRIGGER trg_operation_events_no_update
BEFORE UPDATE ON operation_events BEGIN
  SELECT RAISE(ABORT, 'operation_events are immutable');
END;

CREATE TRIGGER trg_operation_events_no_delete
BEFORE DELETE ON operation_events BEGIN
  SELECT RAISE(ABORT, 'operation_events are immutable');
END;

CREATE TRIGGER trg_transparency_leaves_no_update
BEFORE UPDATE ON transparency_leaves BEGIN
  SELECT RAISE(ABORT, 'transparency leaves are immutable');
END;

CREATE TRIGGER trg_transparency_leaves_no_delete
BEFORE DELETE ON transparency_leaves BEGIN
  SELECT RAISE(ABORT, 'transparency leaves are immutable');
END;

CREATE TRIGGER trg_transparency_nodes_no_update
BEFORE UPDATE ON transparency_nodes BEGIN
  SELECT RAISE(ABORT, 'transparency nodes are immutable');
END;

CREATE TRIGGER trg_transparency_nodes_no_delete
BEFORE DELETE ON transparency_nodes BEGIN
  SELECT RAISE(ABORT, 'transparency nodes are immutable');
END;

-- The checksum covers the frozen DDL body copied verbatim from data-model.md
-- lines 283-1066, including its final LF. It deliberately excludes this
-- migration wrapper and this metadata row to avoid a self-referential digest.
INSERT INTO schema_migrations(version, name, checksum_sha256, applied_at_ms)
VALUES (
  2,
  '0002_v2_initial',
  X'18bd457a1fbf4e5d904c46512402c31dcc8bb96cb51b75eb62b8cca0566af152',
  CAST(strftime('%s', 'now') AS INTEGER) * 1000
);

PRAGMA user_version = 2;
COMMIT;
