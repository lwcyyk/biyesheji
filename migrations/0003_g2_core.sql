-- VDNS SQLite schema migration
-- Version: 0003
-- Name: g2_core
-- Adds the local daily-vault persistence required by Spec 001 G2.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;

BEGIN IMMEDIATE;

CREATE TABLE vault_profiles (
    namespace_id              BLOB PRIMARY KEY CHECK (length(namespace_id) = 16),
    protocol_version          INTEGER NOT NULL CHECK (protocol_version = 2),
    suite_id                  TEXT NOT NULL CHECK (suite_id = 'VDNS-PM-CP-2'),
    active_secret_generation  INTEGER NOT NULL CHECK (active_secret_generation >= 1),
    root_public_key           BLOB NOT NULL CHECK (length(root_public_key) = 32),
    crypto_policy_hash        BLOB NOT NULL CHECK (length(crypto_policy_hash) = 32),
    created_at_ms             INTEGER NOT NULL CHECK (created_at_ms >= 0),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE root_capsules (
    namespace_id              BLOB NOT NULL CHECK (length(namespace_id) = 16),
    device_id                 BLOB NOT NULL CHECK (length(device_id) = 16),
    capsule_version           INTEGER NOT NULL CHECK (capsule_version = 1),
    argon_salt                BLOB NOT NULL CHECK (length(argon_salt) = 16),
    argon_memory_kib          INTEGER NOT NULL CHECK (argon_memory_kib BETWEEN 8192 AND 1048576),
    argon_iterations          INTEGER NOT NULL CHECK (argon_iterations BETWEEN 1 AND 10),
    argon_lanes               INTEGER NOT NULL CHECK (argon_lanes BETWEEN 1 AND 16),
    nonce                     BLOB NOT NULL CHECK (length(nonce) = 12),
    ciphertext                BLOB NOT NULL CHECK (length(ciphertext) BETWEEN 16 AND 16384),
    bundle_schema_version     INTEGER NOT NULL CHECK (bundle_schema_version = 1),
    capsule_cbor              BLOB NOT NULL CHECK (length(capsule_cbor) BETWEEN 1 AND 16384),
    object_digest             BLOB NOT NULL UNIQUE CHECK (length(object_digest) = 32),
    created_at_ms             INTEGER NOT NULL CHECK (created_at_ms >= 0),
    PRIMARY KEY (namespace_id, device_id),
    FOREIGN KEY (namespace_id) REFERENCES vault_profiles(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE recovery_capsules (
    recovery_id               BLOB PRIMARY KEY CHECK (length(recovery_id) = 32),
    namespace_id              BLOB NOT NULL CHECK (length(namespace_id) = 16),
    policy_version            INTEGER NOT NULL CHECK (policy_version >= 1),
    created_sequence          INTEGER NOT NULL CHECK (created_sequence >= 1),
    salt                      BLOB NOT NULL CHECK (length(salt) = 16),
    nonce                     BLOB NOT NULL CHECK (length(nonce) = 12),
    ciphertext                BLOB NOT NULL CHECK (length(ciphertext) BETWEEN 16 AND 16384),
    capsule_cbor              BLOB NOT NULL CHECK (length(capsule_cbor) BETWEEN 1 AND 16384),
    object_digest             BLOB NOT NULL UNIQUE CHECK (length(object_digest) = 32),
    status                    TEXT NOT NULL CHECK (status IN ('ACTIVE','SUPERSEDED','REVOKED')),
    created_at_ms             INTEGER NOT NULL CHECK (created_at_ms >= 0),
    FOREIGN KEY (namespace_id) REFERENCES vault_profiles(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_one_active_recovery_capsule
ON recovery_capsules(namespace_id)
WHERE status = 'ACTIVE';

CREATE TABLE route_entries (
    namespace_id              BLOB NOT NULL CHECK (length(namespace_id) = 16),
    route_id                  BLOB NOT NULL CHECK (length(route_id) = 32),
    origin_index              BLOB NOT NULL CHECK (length(origin_index) = 32),
    credential_id             BLOB NOT NULL CHECK (length(credential_id) = 32),
    encrypted_origin          BLOB NOT NULL CHECK (length(encrypted_origin) BETWEEN 1 AND 8192),
    encrypted_account_id      BLOB NOT NULL CHECK (length(encrypted_account_id) BETWEEN 1 AND 8192),
    origin_binding            BLOB NOT NULL CHECK (length(origin_binding) = 32),
    route_version             INTEGER NOT NULL CHECK (route_version >= 1),
    status                    TEXT NOT NULL CHECK (status IN ('ACTIVE','REMOVED')),
    created_at_ms             INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms             INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    PRIMARY KEY (namespace_id, route_id),
    FOREIGN KEY (namespace_id) REFERENCES vault_profiles(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_route_origin_accounts
ON route_entries(namespace_id, origin_index, status, route_id);

CREATE TABLE password_policies (
    namespace_id              BLOB NOT NULL CHECK (length(namespace_id) = 16),
    policy_hash               BLOB NOT NULL CHECK (length(policy_hash) = 32),
    origin_binding            BLOB NOT NULL CHECK (length(origin_binding) = 32),
    policy_version            INTEGER NOT NULL CHECK (policy_version >= 1),
    encrypted_policy_digest   BLOB NOT NULL CHECK (length(encrypted_policy_digest) = 32),
    source                    TEXT NOT NULL CHECK (source IN ('DEFAULT','USER','SITE','MOCK_SITE')),
    verification_level        TEXT NOT NULL CHECK (verification_level IN ('UNVERIFIED','USER_VERIFIED','SITE_VERIFIED')),
    created_at_ms             INTEGER NOT NULL CHECK (created_at_ms >= 0),
    PRIMARY KEY (namespace_id, origin_binding, policy_version),
    UNIQUE (namespace_id, policy_hash),
    FOREIGN KEY (namespace_id) REFERENCES vault_profiles(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE credential_envelopes_v2 (
    envelope_hash             BLOB PRIMARY KEY CHECK (length(envelope_hash) = 32),
    namespace_id              BLOB NOT NULL CHECK (length(namespace_id) = 16),
    credential_id             BLOB NOT NULL CHECK (length(credential_id) = 32),
    credential_version        INTEGER NOT NULL CHECK (credential_version >= 1),
    envelope_cbor             BLOB NOT NULL CHECK (length(envelope_cbor) BETWEEN 1 AND 131072),
    descriptor_binding_hash   BLOB NOT NULL CHECK (length(descriptor_binding_hash) = 32),
    crypto_policy_hash        BLOB NOT NULL CHECK (length(crypto_policy_hash) = 32),
    origin_binding            BLOB NOT NULL CHECK (length(origin_binding) = 32),
    created_at_ms             INTEGER NOT NULL CHECK (created_at_ms >= 0),
    UNIQUE (namespace_id, credential_id, credential_version, envelope_hash),
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE state_descriptors_v2 (
    descriptor_hash           BLOB PRIMARY KEY CHECK (length(descriptor_hash) = 32),
    namespace_id              BLOB NOT NULL CHECK (length(namespace_id) = 16),
    credential_id             BLOB NOT NULL CHECK (length(credential_id) = 32),
    active_version            INTEGER NOT NULL CHECK (active_version >= 1),
    active_envelope_hash      BLOB NOT NULL CHECK (length(active_envelope_hash) = 32),
    previous_descriptor_hash  BLOB CHECK (previous_descriptor_hash IS NULL OR length(previous_descriptor_hash) = 32),
    lifecycle_status          TEXT NOT NULL CHECK (lifecycle_status IN (
                                 'ACTIVE','UPDATE_PENDING','SITE_CONFIRM_PENDING',
                                 'SUSPENDED','SUPERSEDED','REVOKED','CONFLICTED'
                               )),
    last_operation_event      BLOB NOT NULL CHECK (length(last_operation_event) = 32),
    authorized_device_set_root BLOB NOT NULL CHECK (length(authorized_device_set_root) = 32),
    audit_checkpoint          BLOB NOT NULL CHECK (length(audit_checkpoint) = 32),
    final_sequence            INTEGER NOT NULL CHECK (final_sequence >= 1),
    updater_device_id         BLOB NOT NULL CHECK (length(updater_device_id) = 16),
    sig_input_cbor            BLOB NOT NULL CHECK (length(sig_input_cbor) BETWEEN 1 AND 65536),
    updater_signature         BLOB NOT NULL CHECK (length(updater_signature) = 64),
    created_at_ms             INTEGER NOT NULL CHECK (created_at_ms >= 0),
    UNIQUE (namespace_id, credential_id, active_version, descriptor_hash),
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE credential_acceptance_v2 (
    namespace_id              BLOB NOT NULL CHECK (length(namespace_id) = 16),
    credential_id             BLOB NOT NULL CHECK (length(credential_id) = 32),
    accepted_version          INTEGER NOT NULL CHECK (accepted_version >= 1),
    accepted_descriptor_hash  BLOB NOT NULL CHECK (length(accepted_descriptor_hash) = 32),
    accepted_envelope_hash    BLOB NOT NULL CHECK (length(accepted_envelope_hash) = 32),
    updated_sequence          INTEGER NOT NULL CHECK (updated_sequence >= 1),
    PRIMARY KEY (namespace_id, credential_id),
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT,
    FOREIGN KEY (accepted_descriptor_hash) REFERENCES state_descriptors_v2(descriptor_hash) ON DELETE RESTRICT,
    FOREIGN KEY (accepted_envelope_hash) REFERENCES credential_envelopes_v2(envelope_hash) ON DELETE RESTRICT
) STRICT;

INSERT INTO schema_migrations(version, name, checksum_sha256, applied_at_ms)
VALUES (
  3,
  '0003_g2_core',
  X'70934a17beba6ac5cd942c57f5b310d04ca9257a5e6dda9d3f6d027a1a696a9e',
  CAST(strftime('%s', 'now') AS INTEGER) * 1000
);

PRAGMA user_version = 3;
COMMIT;
