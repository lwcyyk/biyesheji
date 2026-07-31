-- VDNS SQLite schema migration
-- Version: 0004
-- Name: g3_lifecycle_sync
-- Adds crash-recoverable lifecycle, synchronization, enrollment and recovery state.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;

BEGIN IMMEDIATE;

CREATE TABLE site_change_attempts (
    change_id                  BLOB PRIMARY KEY CHECK (length(change_id) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    credential_id              BLOB NOT NULL CHECK (length(credential_id) = 32),
    previous_version           INTEGER NOT NULL CHECK (previous_version >= 1),
    candidate_version          INTEGER NOT NULL CHECK (candidate_version = previous_version + 1),
    candidate_descriptor_hash  BLOB NOT NULL CHECK (length(candidate_descriptor_hash) = 32),
    request_hash               BLOB NOT NULL CHECK (length(request_hash) = 32),
    status                     TEXT NOT NULL CHECK (status IN (
                                 'CANDIDATE_DURABLE','SITE_UPDATE_PENDING',
                                 'FAILED_RETRYABLE','SITE_STATUS_UNKNOWN',
                                 'SITE_CHANGED_LOCAL_COMMIT_PENDING',
                                 'SITE_CONFIRM_PENDING','ACTIVE','ABORTED'
                               )),
    evidence_level             INTEGER CHECK (evidence_level IS NULL OR evidence_level BETWEEN 1 AND 5),
    site_receipt_hash          BLOB CHECK (site_receipt_hash IS NULL OR length(site_receipt_hash) = 32),
    site_receipt_status        INTEGER CHECK (site_receipt_status IS NULL OR site_receipt_status BETWEEN 1 AND 5),
    site_receipt_cbor          BLOB CHECK (site_receipt_cbor IS NULL OR length(site_receipt_cbor) BETWEEN 1 AND 65536),
    site_receipt_signature     BLOB CHECK (site_receipt_signature IS NULL OR length(site_receipt_signature) = 64),
    confirmation_event_id      BLOB CHECK (confirmation_event_id IS NULL OR length(confirmation_event_id) = 32),
    last_error_code            TEXT CHECK (last_error_code IS NULL OR length(last_error_code) BETWEEN 1 AND 128),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    CHECK (
      (site_receipt_cbor IS NULL AND site_receipt_signature IS NULL
                                 AND site_receipt_hash IS NULL AND site_receipt_status IS NULL)
      OR
      (site_receipt_cbor IS NOT NULL AND site_receipt_signature IS NOT NULL
                                     AND site_receipt_hash IS NOT NULL AND site_receipt_status IS NOT NULL)
    ),
    CHECK (
      status <> 'ACTIVE'
      OR (evidence_level IN (4,5) AND confirmation_event_id IS NOT NULL)
    ),
    UNIQUE (namespace_id, credential_id, candidate_version),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id, previous_version)
        REFERENCES credential_versions(credential_id, version) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id, candidate_version)
        REFERENCES credential_versions(credential_id, version) ON DELETE RESTRICT,
    FOREIGN KEY (confirmation_event_id) REFERENCES operation_events(event_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_site_change_recovery
ON site_change_attempts(status, updated_at_ms);

CREATE TABLE sync_manifests_v2 (
    manifest_digest            BLOB PRIMARY KEY CHECK (length(manifest_digest) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    publisher_device_id        BLOB NOT NULL CHECK (length(publisher_device_id) = 16),
    base_checkpoint            BLOB NOT NULL CHECK (length(base_checkpoint) = 32),
    target_checkpoint          BLOB NOT NULL CHECK (length(target_checkpoint) = 32),
    highest_device_counter     INTEGER NOT NULL CHECK (highest_device_counter >= 1),
    object_set_root            BLOB NOT NULL CHECK (length(object_set_root) = 32),
    object_count               INTEGER NOT NULL CHECK (object_count BETWEEN 1 AND 10000),
    created_sequence           INTEGER NOT NULL CHECK (created_sequence >= 1),
    sig_input_cbor             BLOB NOT NULL CHECK (length(sig_input_cbor) BETWEEN 1 AND 1048576),
    publisher_signature        BLOB NOT NULL CHECK (length(publisher_signature) = 64),
    acceptance_state           TEXT NOT NULL CHECK (acceptance_state IN (
                                 'RECEIVED','VERIFIED','OBJECTS_COMPLETE',
                                 'ACCEPTED','REJECTED','CONFLICTED'
                               )),
    rejection_code             TEXT CHECK (rejection_code IS NULL OR length(rejection_code) BETWEEN 1 AND 128),
    received_at_ms             INTEGER NOT NULL CHECK (received_at_ms >= 0),
    accepted_at_ms             INTEGER CHECK (accepted_at_ms IS NULL OR accepted_at_ms >= received_at_ms),
    CHECK (base_checkpoint <> target_checkpoint),
    CHECK (
      (acceptance_state = 'ACCEPTED' AND accepted_at_ms IS NOT NULL AND rejection_code IS NULL)
      OR
      (acceptance_state = 'REJECTED' AND accepted_at_ms IS NULL AND rejection_code IS NOT NULL)
      OR
      (acceptance_state NOT IN ('ACCEPTED','REJECTED') AND accepted_at_ms IS NULL)
    ),
    UNIQUE (namespace_id, publisher_device_id, highest_device_counter),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (publisher_device_id) REFERENCES devices(device_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_sync_manifest_checkpoint
ON sync_manifests_v2(namespace_id, target_checkpoint, acceptance_state);

CREATE TABLE sync_manifest_objects_v2 (
    manifest_digest            BLOB NOT NULL CHECK (length(manifest_digest) = 32),
    ordinal                    INTEGER NOT NULL CHECK (ordinal BETWEEN 0 AND 9999),
    object_digest              BLOB NOT NULL CHECK (length(object_digest) = 32),
    object_type                INTEGER NOT NULL CHECK (object_type BETWEEN 1 AND 16),
    credential_id              BLOB CHECK (credential_id IS NULL OR length(credential_id) = 32),
    credential_version         INTEGER CHECK (credential_version IS NULL OR credential_version >= 1),
    object_size                INTEGER NOT NULL CHECK (object_size >= 1),
    fetch_state                TEXT NOT NULL CHECK (fetch_state IN (
                                 'MISSING','FETCHED','VERIFIED','CORRUPT'
                               )),
    PRIMARY KEY (manifest_digest, ordinal),
    UNIQUE (manifest_digest, object_digest, object_type, credential_id, credential_version, object_size),
    CHECK ((credential_id IS NULL) = (credential_version IS NULL)),
    FOREIGN KEY (manifest_digest) REFERENCES sync_manifests_v2(manifest_digest) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_sync_objects_completion
ON sync_manifest_objects_v2(manifest_digest, fetch_state);

CREATE TABLE sync_peer_acceptance (
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    publisher_device_id        BLOB NOT NULL CHECK (length(publisher_device_id) = 16),
    accepted_manifest_digest   BLOB NOT NULL CHECK (length(accepted_manifest_digest) = 32),
    accepted_checkpoint        BLOB NOT NULL CHECK (length(accepted_checkpoint) = 32),
    highest_accepted_counter   INTEGER NOT NULL CHECK (highest_accepted_counter >= 1),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= 0),
    PRIMARY KEY (namespace_id, publisher_device_id),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (publisher_device_id) REFERENCES devices(device_id) ON DELETE RESTRICT,
    FOREIGN KEY (accepted_manifest_digest) REFERENCES sync_manifests_v2(manifest_digest) ON DELETE RESTRICT
) STRICT;

CREATE TABLE credential_conflicts_v2 (
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    credential_id              BLOB NOT NULL CHECK (length(credential_id) = 32),
    credential_version         INTEGER NOT NULL CHECK (credential_version >= 1),
    descriptor_hash            BLOB NOT NULL CHECK (length(descriptor_hash) = 32),
    envelope_hash              BLOB NOT NULL CHECK (length(envelope_hash) = 32),
    observed_manifest_digest   BLOB NOT NULL CHECK (length(observed_manifest_digest) = 32),
    disposition                TEXT NOT NULL CHECK (disposition IN ('RETAINED','SELECTED','REJECTED')),
    resolution_event_id        BLOB CHECK (resolution_event_id IS NULL OR length(resolution_event_id) = 32),
    observed_at_ms             INTEGER NOT NULL CHECK (observed_at_ms >= 0),
    resolved_at_ms             INTEGER CHECK (resolved_at_ms IS NULL OR resolved_at_ms >= observed_at_ms),
    PRIMARY KEY (namespace_id, credential_id, credential_version, descriptor_hash),
    CHECK (
      (disposition = 'RETAINED' AND resolution_event_id IS NULL AND resolved_at_ms IS NULL)
      OR
      (disposition IN ('SELECTED','REJECTED') AND resolution_event_id IS NOT NULL AND resolved_at_ms IS NOT NULL)
    ),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT,
    FOREIGN KEY (descriptor_hash) REFERENCES state_descriptors_v2(descriptor_hash) ON DELETE RESTRICT,
    FOREIGN KEY (envelope_hash) REFERENCES credential_envelopes_v2(envelope_hash) ON DELETE RESTRICT,
    FOREIGN KEY (observed_manifest_digest) REFERENCES sync_manifests_v2(manifest_digest) ON DELETE RESTRICT,
    FOREIGN KEY (resolution_event_id) REFERENCES operation_events(event_id) ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_one_selected_conflict
ON credential_conflicts_v2(namespace_id, credential_id, credential_version)
WHERE disposition = 'SELECTED';

CREATE TABLE device_enrollment_challenges (
    challenge_id               BLOB PRIMARY KEY CHECK (length(challenge_id) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    challenge_nonce            BLOB NOT NULL UNIQUE CHECK (length(challenge_nonce) = 32),
    short_code_commitment      BLOB NOT NULL CHECK (length(short_code_commitment) = 32),
    new_device_id              BLOB NOT NULL CHECK (length(new_device_id) = 16),
    new_signing_public_key     BLOB NOT NULL CHECK (length(new_signing_public_key) = 32),
    new_hpke_public_key        BLOB NOT NULL CHECK (length(new_hpke_public_key) = 32),
    requested_capabilities_cbor BLOB NOT NULL CHECK (length(requested_capabilities_cbor) BETWEEN 1 AND 65536),
    status                     TEXT NOT NULL CHECK (status IN (
                                 'ISSUED','APPROVED','CONSUMED','EXPIRED','REJECTED'
                               )),
    expires_at_sequence        INTEGER NOT NULL CHECK (expires_at_sequence >= 1),
    approved_by_device_id      BLOB CHECK (approved_by_device_id IS NULL OR length(approved_by_device_id) = 16),
    approval_event_id          BLOB CHECK (approval_event_id IS NULL OR length(approval_event_id) = 32),
    root_bundle_envelope_hash  BLOB CHECK (root_bundle_envelope_hash IS NULL OR length(root_bundle_envelope_hash) = 32),
    issued_device_credential_hash BLOB CHECK (issued_device_credential_hash IS NULL OR length(issued_device_credential_hash) = 32),
    consumed_at_sequence       INTEGER CHECK (consumed_at_sequence IS NULL OR consumed_at_sequence >= 1),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    CHECK (
      (status = 'ISSUED' AND approved_by_device_id IS NULL AND approval_event_id IS NULL
                         AND root_bundle_envelope_hash IS NULL
                         AND issued_device_credential_hash IS NULL
                         AND consumed_at_sequence IS NULL)
      OR
      (status = 'APPROVED' AND approved_by_device_id IS NOT NULL AND approval_event_id IS NOT NULL
                           AND root_bundle_envelope_hash IS NOT NULL
                           AND issued_device_credential_hash IS NOT NULL
                           AND consumed_at_sequence IS NULL)
      OR
      (status = 'CONSUMED' AND approved_by_device_id IS NOT NULL AND approval_event_id IS NOT NULL
                           AND root_bundle_envelope_hash IS NOT NULL
                           AND issued_device_credential_hash IS NOT NULL
                           AND consumed_at_sequence IS NOT NULL)
      OR
      (status IN ('EXPIRED','REJECTED') AND consumed_at_sequence IS NULL)
    ),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (approved_by_device_id) REFERENCES devices(device_id) ON DELETE RESTRICT,
    FOREIGN KEY (approval_event_id) REFERENCES operation_events(event_id) ON DELETE RESTRICT,
    FOREIGN KEY (root_bundle_envelope_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_enrollment_new_device_open
ON device_enrollment_challenges(namespace_id, new_device_id)
WHERE status IN ('ISSUED','APPROVED');

CREATE TABLE secret_generation_rollovers (
    rollover_id                BLOB PRIMARY KEY CHECK (length(rollover_id) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    old_generation             INTEGER NOT NULL CHECK (old_generation >= 1),
    new_generation             INTEGER NOT NULL CHECK (new_generation = old_generation + 1),
    trigger_revocation_id      BLOB NOT NULL CHECK (length(trigger_revocation_id) = 32),
    final_sequence             INTEGER CHECK (final_sequence IS NULL OR final_sequence >= 1),
    status                     TEXT NOT NULL CHECK (status IN (
                                 'PREPARED','ENVELOPES_CREATED',
                                 'FINAL_SEQUENCE_ACCEPTED','ACTIVE','FAILED'
                               )),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    CHECK (
      status IN ('PREPARED','ENVELOPES_CREATED','FAILED')
      OR final_sequence IS NOT NULL
    ),
    UNIQUE (namespace_id, new_generation),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (namespace_id, old_generation)
        REFERENCES namespace_key_generations(namespace_id, generation) ON DELETE RESTRICT,
    FOREIGN KEY (namespace_id, new_generation)
        REFERENCES namespace_key_generations(namespace_id, generation) ON DELETE RESTRICT,
    FOREIGN KEY (trigger_revocation_id) REFERENCES revocations(revocation_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE secret_generation_recipients (
    rollover_id                BLOB NOT NULL CHECK (length(rollover_id) = 32),
    device_id                  BLOB NOT NULL CHECK (length(device_id) = 16),
    envelope_object_hash       BLOB NOT NULL CHECK (length(envelope_object_hash) = 32),
    acknowledged_at_ms         INTEGER CHECK (acknowledged_at_ms IS NULL OR acknowledged_at_ms >= 0),
    PRIMARY KEY (rollover_id, device_id),
    UNIQUE (envelope_object_hash),
    FOREIGN KEY (rollover_id) REFERENCES secret_generation_rollovers(rollover_id) ON DELETE RESTRICT,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE RESTRICT,
    FOREIGN KEY (envelope_object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT
) STRICT;

CREATE TABLE backup_snapshots_v2 (
    backup_id                  BLOB PRIMARY KEY CHECK (length(backup_id) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    secret_generation          INTEGER NOT NULL CHECK (secret_generation >= 1),
    encrypted_manifest_hash    BLOB NOT NULL UNIQUE CHECK (length(encrypted_manifest_hash) = 32),
    recovery_capsule_digest    BLOB NOT NULL CHECK (length(recovery_capsule_digest) = 32),
    route_map_root             BLOB NOT NULL CHECK (length(route_map_root) = 32),
    credential_state_root      BLOB NOT NULL CHECK (length(credential_state_root) = 32),
    object_set_root            BLOB NOT NULL CHECK (length(object_set_root) = 32),
    accepted_checkpoint        BLOB NOT NULL CHECK (length(accepted_checkpoint) = 32),
    status                     TEXT NOT NULL CHECK (status IN ('PREPARING','COMPLETE','SUPERSEDED','CORRUPT')),
    created_sequence           INTEGER NOT NULL CHECK (created_sequence >= 1),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    verified_at_ms             INTEGER CHECK (verified_at_ms IS NULL OR verified_at_ms >= created_at_ms),
    CHECK (status <> 'COMPLETE' OR verified_at_ms IS NOT NULL),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (namespace_id, secret_generation)
        REFERENCES namespace_key_generations(namespace_id, generation) ON DELETE RESTRICT,
    FOREIGN KEY (encrypted_manifest_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT,
    FOREIGN KEY (recovery_capsule_digest) REFERENCES recovery_capsules(object_digest) ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_one_complete_backup
ON backup_snapshots_v2(namespace_id)
WHERE status = 'COMPLETE';

CREATE TABLE recovery_runs_v2 (
    recovery_run_id            BLOB PRIMARY KEY CHECK (length(recovery_run_id) = 32),
    backup_id                  BLOB NOT NULL CHECK (length(backup_id) = 32),
    target_device_id           BLOB NOT NULL CHECK (length(target_device_id) = 16),
    status                     TEXT NOT NULL CHECK (status IN (
                                 'PREPARED','ROOT_RECOVERED','OBJECTS_VERIFIED',
                                 'VDNS_VERIFIED','COMPLETED','FAILED'
                               )),
    verified_checkpoint        BLOB CHECK (verified_checkpoint IS NULL OR length(verified_checkpoint) = 32),
    error_code                 TEXT CHECK (error_code IS NULL OR length(error_code) BETWEEN 1 AND 128),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    CHECK (
      (status IN ('VDNS_VERIFIED','COMPLETED') AND verified_checkpoint IS NOT NULL AND error_code IS NULL)
      OR
      (status = 'FAILED' AND error_code IS NOT NULL)
      OR
      (status IN ('PREPARED','ROOT_RECOVERED','OBJECTS_VERIFIED')
       AND verified_checkpoint IS NULL AND error_code IS NULL)
    ),
    FOREIGN KEY (backup_id) REFERENCES backup_snapshots_v2(backup_id) ON DELETE RESTRICT
) STRICT;

INSERT INTO schema_migrations(version, name, checksum_sha256, applied_at_ms)
VALUES (
  4,
  '0004_g3_lifecycle_sync',
  X'c064e22d26cd0b703c82a3b8f53145110c799d6cd8a7ba5b03fb4501b89b2ac7',
  CAST(strftime('%s', 'now') AS INTEGER) * 1000
);

PRAGMA user_version = 4;
COMMIT;
