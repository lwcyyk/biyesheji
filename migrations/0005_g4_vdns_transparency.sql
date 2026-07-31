-- VDNS SQLite schema migration
-- Version: 0005
-- Name: g4_vdns_transparency
-- Adds CP-2 VDNS decisions, proof bundles, public checkpoints and monitor evidence.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;

BEGIN IMMEDIATE;

CREATE TABLE transparency_logs_v2 (
    log_id                     BLOB PRIMARY KEY CHECK (length(log_id) = 16),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    log_public_key             BLOB NOT NULL CHECK (length(log_public_key) = 32),
    key_generation             INTEGER NOT NULL CHECK (key_generation >= 1),
    tree_size                  INTEGER NOT NULL DEFAULT 0 CHECK (tree_size >= 0),
    root_hash                  BLOB NOT NULL CHECK (length(root_hash) = 32),
    final_sequence             INTEGER NOT NULL DEFAULT 0 CHECK (final_sequence >= 0),
    status                     TEXT NOT NULL CHECK (status IN ('ACTIVE','FROZEN')),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms              INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    UNIQUE (namespace_id, log_id),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE transparency_leaves_v2 (
    log_id                     BLOB NOT NULL CHECK (length(log_id) = 16),
    leaf_index                 INTEGER NOT NULL CHECK (leaf_index >= 0),
    leaf_cbor                  BLOB NOT NULL CHECK (length(leaf_cbor) BETWEEN 1 AND 65536),
    leaf_hash                  BLOB NOT NULL CHECK (length(leaf_hash) = 32),
    object_digest              BLOB NOT NULL CHECK (length(object_digest) = 32),
    object_type                INTEGER NOT NULL CHECK (object_type BETWEEN 1 AND 16),
    operation_type             INTEGER NOT NULL CHECK (operation_type BETWEEN 1 AND 17),
    subject_pseudonym          BLOB NOT NULL CHECK (length(subject_pseudonym) = 32),
    final_sequence             INTEGER NOT NULL CHECK (final_sequence >= 1),
    epoch                      INTEGER NOT NULL CHECK (epoch >= 1),
    appended_at_ms             INTEGER NOT NULL CHECK (appended_at_ms >= 0),
    PRIMARY KEY (log_id, leaf_index),
    UNIQUE (log_id, object_digest),
    FOREIGN KEY (log_id) REFERENCES transparency_logs_v2(log_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_transparency_leaves_v2_epoch
ON transparency_leaves_v2(log_id, epoch, leaf_index);

CREATE TABLE signed_tree_heads_v2 (
    tree_head_digest           BLOB PRIMARY KEY CHECK (length(tree_head_digest) = 32),
    log_id                     BLOB NOT NULL CHECK (length(log_id) = 16),
    tree_size                  INTEGER NOT NULL CHECK (tree_size >= 1),
    root_hash                  BLOB NOT NULL CHECK (length(root_hash) = 32),
    final_sequence             INTEGER NOT NULL CHECK (final_sequence >= 1),
    sig_input_cbor             BLOB NOT NULL CHECK (length(sig_input_cbor) BETWEEN 1 AND 65536),
    log_signature              BLOB NOT NULL CHECK (length(log_signature) = 64),
    trust_state                TEXT NOT NULL CHECK (trust_state IN (
                                 'OBSERVED','ACCEPTED','CONFLICTING','REJECTED'
                               )),
    source_id                  TEXT NOT NULL CHECK (length(source_id) BETWEEN 1 AND 128),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    UNIQUE (log_id, tree_size, root_hash),
    FOREIGN KEY (log_id) REFERENCES transparency_logs_v2(log_id) ON DELETE RESTRICT
) STRICT;

CREATE UNIQUE INDEX ux_one_accepted_root_v2
ON signed_tree_heads_v2(log_id, tree_size)
WHERE trust_state = 'ACCEPTED';

CREATE TABLE consistency_proofs_v2 (
    log_id                     BLOB NOT NULL CHECK (length(log_id) = 16),
    from_tree_size             INTEGER NOT NULL CHECK (from_tree_size >= 0),
    to_tree_size               INTEGER NOT NULL CHECK (to_tree_size > from_tree_size),
    from_root_hash             BLOB NOT NULL CHECK (length(from_root_hash) = 32),
    to_root_hash               BLOB NOT NULL CHECK (length(to_root_hash) = 32),
    proof_cbor                 BLOB NOT NULL CHECK (length(proof_cbor) BETWEEN 1 AND 65536),
    proof_hash_count           INTEGER NOT NULL CHECK (proof_hash_count BETWEEN 0 AND 64),
    verified                   INTEGER NOT NULL CHECK (verified IN (0,1)),
    verified_at_ms             INTEGER CHECK (verified_at_ms IS NULL OR verified_at_ms >= 0),
    PRIMARY KEY (log_id, from_tree_size, to_tree_size, from_root_hash, to_root_hash),
    FOREIGN KEY (log_id) REFERENCES transparency_logs_v2(log_id) ON DELETE RESTRICT,
    CHECK ((verified = 1) = (verified_at_ms IS NOT NULL))
) STRICT;

CREATE TABLE checkpoints_v2 (
    checkpoint_digest          BLOB PRIMARY KEY CHECK (length(checkpoint_digest) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    namespace_state_root       BLOB NOT NULL CHECK (length(namespace_state_root) = 32),
    device_state_root          BLOB NOT NULL CHECK (length(device_state_root) = 32),
    credential_state_root      BLOB NOT NULL CHECK (length(credential_state_root) = 32),
    audit_log_root             BLOB NOT NULL CHECK (length(audit_log_root) = 32),
    revocation_root            BLOB NOT NULL CHECK (length(revocation_root) = 32),
    crypto_policy_hash         BLOB NOT NULL CHECK (length(crypto_policy_hash) = 32),
    checkpoint_height          INTEGER NOT NULL CHECK (checkpoint_height >= 1),
    final_sequence             INTEGER NOT NULL CHECK (final_sequence >= 1),
    provider_kind              TEXT NOT NULL CHECK (provider_kind IN (
                                 'SIMULATED','ANVIL','CONSENSUS'
                               )),
    vrf_output_hash            BLOB CHECK (vrf_output_hash IS NULL OR length(vrf_output_hash) = 32),
    sig_input_cbor             BLOB NOT NULL CHECK (length(sig_input_cbor) BETWEEN 1 AND 65536),
    checkpoint_signature       BLOB NOT NULL CHECK (length(checkpoint_signature) = 64),
    created_at_ms              INTEGER NOT NULL CHECK (created_at_ms >= 0),
    UNIQUE (namespace_id, checkpoint_height, audit_log_root),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT
) STRICT;

CREATE TABLE announcement_receipts_v2 (
    checkpoint_digest          BLOB NOT NULL CHECK (length(checkpoint_digest) = 32),
    provider_kind              TEXT NOT NULL CHECK (provider_kind IN (
                                 'SIMULATED','ANVIL','CONSENSUS'
                               )),
    external_reference         TEXT NOT NULL CHECK (length(external_reference) BETWEEN 1 AND 256),
    observed_height            INTEGER NOT NULL CHECK (observed_height >= 1),
    announced_at_ms            INTEGER NOT NULL CHECK (announced_at_ms >= 0),
    PRIMARY KEY (checkpoint_digest, provider_kind, external_reference),
    FOREIGN KEY (checkpoint_digest) REFERENCES checkpoints_v2(checkpoint_digest) ON DELETE RESTRICT
) STRICT;

CREATE TABLE proof_bundles_v2 (
    proof_bundle_digest        BLOB PRIMARY KEY CHECK (length(proof_bundle_digest) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    subject_digest             BLOB NOT NULL CHECK (length(subject_digest) = 32),
    starting_checkpoint_digest BLOB NOT NULL CHECK (length(starting_checkpoint_digest) = 32),
    candidate_tree_head_digest BLOB NOT NULL CHECK (length(candidate_tree_head_digest) = 32),
    leaf_index                 INTEGER NOT NULL CHECK (leaf_index >= 0),
    inclusion_hash_count       INTEGER NOT NULL CHECK (inclusion_hash_count BETWEEN 0 AND 64),
    consistency_hash_count     INTEGER NOT NULL CHECK (consistency_hash_count BETWEEN 0 AND 64),
    local_policy_input_hash    BLOB NOT NULL CHECK (length(local_policy_input_hash) = 32),
    sig_input_cbor             BLOB NOT NULL CHECK (length(sig_input_cbor) BETWEEN 1 AND 65536),
    resolver_signature         BLOB NOT NULL CHECK (length(resolver_signature) = 64),
    verification_state         TEXT NOT NULL CHECK (verification_state IN (
                                 'RECEIVED','VERIFIED','REJECTED'
                               )),
    rejection_code             TEXT CHECK (rejection_code IS NULL OR length(rejection_code) BETWEEN 1 AND 128),
    verified_at_ms             INTEGER CHECK (verified_at_ms IS NULL OR verified_at_ms >= 0),
    CHECK (
      (verification_state = 'VERIFIED' AND rejection_code IS NULL AND verified_at_ms IS NOT NULL)
      OR
      (verification_state = 'REJECTED' AND rejection_code IS NOT NULL AND verified_at_ms IS NOT NULL)
      OR
      (verification_state = 'RECEIVED' AND rejection_code IS NULL AND verified_at_ms IS NULL)
    ),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (starting_checkpoint_digest) REFERENCES checkpoints_v2(checkpoint_digest) ON DELETE RESTRICT,
    FOREIGN KEY (candidate_tree_head_digest) REFERENCES signed_tree_heads_v2(tree_head_digest) ON DELETE RESTRICT
) STRICT;

CREATE TABLE vdns_resolutions_v2 (
    resolution_id              BLOB PRIMARY KEY CHECK (length(resolution_id) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    credential_id              BLOB NOT NULL CHECK (length(credential_id) = 32),
    descriptor_digest          BLOB NOT NULL CHECK (length(descriptor_digest) = 32),
    current_version            INTEGER NOT NULL CHECK (current_version >= 1),
    principal_device_id        BLOB NOT NULL CHECK (length(principal_device_id) = 16),
    operation_type             INTEGER NOT NULL CHECK (operation_type BETWEEN 1 AND 17),
    proof_bundle_digest        BLOB CHECK (proof_bundle_digest IS NULL OR length(proof_bundle_digest) = 32),
    l1_code                    TEXT NOT NULL CHECK (length(l1_code) BETWEEN 1 AND 128),
    l2_code                    TEXT NOT NULL CHECK (length(l2_code) BETWEEN 1 AND 128),
    l3_code                    TEXT NOT NULL CHECK (length(l3_code) BETWEEN 1 AND 128),
    l4_code                    TEXT NOT NULL CHECK (length(l4_code) BETWEEN 1 AND 128),
    l5_code                    TEXT NOT NULL CHECK (length(l5_code) BETWEEN 1 AND 128),
    verdict                    TEXT NOT NULL CHECK (verdict IN (
                                 'ACCEPT','DEGRADED_OFFLINE','DEGRADED_PENDING_LOG',
                                 'REVIEW_REQUIRED','REJECT_IDENTITY','REJECT_CAPABILITY',
                                 'REJECT_REVOKED','REJECT_CAUSAL','REJECT_PROOF',
                                 'REJECT_ORIGIN','REJECT_POLICY','REJECT_OBJECT'
                               )),
    decided_at_ms              INTEGER NOT NULL CHECK (decided_at_ms >= 0),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT,
    FOREIGN KEY (descriptor_digest) REFERENCES state_descriptors_v2(descriptor_hash) ON DELETE RESTRICT,
    FOREIGN KEY (proof_bundle_digest) REFERENCES proof_bundles_v2(proof_bundle_digest) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_vdns_current_decision
ON vdns_resolutions_v2(namespace_id, credential_id, decided_at_ms DESC);

CREATE TABLE monitor_evidence_v2 (
    evidence_digest            BLOB PRIMARY KEY CHECK (length(evidence_digest) = 32),
    namespace_id               BLOB NOT NULL CHECK (length(namespace_id) = 16),
    finding_kind               TEXT NOT NULL CHECK (finding_kind IN (
                                 'SPLIT_VIEW','TREE_ROLLBACK','BAD_CONSISTENCY',
                                 'DOUBLE_DESCRIPTOR','ANCHOR_CONFLICT'
                               )),
    first_object_hash          BLOB NOT NULL CHECK (length(first_object_hash) = 32),
    second_object_hash         BLOB NOT NULL CHECK (length(second_object_hash) = 32),
    first_position             INTEGER NOT NULL CHECK (first_position >= 1),
    second_position            INTEGER NOT NULL CHECK (second_position >= 1),
    subject_commitment         BLOB CHECK (subject_commitment IS NULL OR length(subject_commitment) = 32),
    evidence_cbor              BLOB NOT NULL CHECK (length(evidence_cbor) BETWEEN 1 AND 65536),
    detected_at_ms             INTEGER NOT NULL CHECK (detected_at_ms >= 0),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT
) STRICT;

INSERT INTO schema_migrations(version, name, checksum_sha256, applied_at_ms)
VALUES (
  5,
  '0005_g4_vdns_transparency',
  X'8706b8da3cab1a182d70ae1d053556d1274c7d88ea612988abc3c53bce043f9b',
  CAST(strftime('%s', 'now') AS INTEGER) * 1000
);

PRAGMA user_version = 5;
COMMIT;
