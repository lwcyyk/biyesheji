-- VDNS SQLite schema migration
-- Version: 0008
-- Name: stage2_protocol_closure
-- Research final-order persistence and explicit v2.1 evidence/revocation state.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;

BEGIN IMMEDIATE;

CREATE TABLE final_order_snapshots_v2 (
    adapter_kind       TEXT PRIMARY KEY CHECK (adapter_kind = 'RESEARCH_ADAPTER'),
    revision           INTEGER NOT NULL CHECK (revision >= 1),
    state_json         BLOB NOT NULL CHECK (length(state_json) BETWEEN 2 AND 16777216),
    updated_at_ms      INTEGER NOT NULL CHECK (updated_at_ms >= 0)
) STRICT;

CREATE TABLE final_order_candidates_v2 (
    candidate_digest       BLOB PRIMARY KEY CHECK (length(candidate_digest) = 32),
    namespace_id           BLOB NOT NULL CHECK (length(namespace_id) = 16),
    credential_id          BLOB NOT NULL CHECK (length(credential_id) = 32),
    base_version           INTEGER NOT NULL CHECK (base_version >= 1),
    candidate_version      INTEGER NOT NULL CHECK (candidate_version = base_version + 1),
    base_descriptor_hash   BLOB NOT NULL CHECK (length(base_descriptor_hash) = 32),
    descriptor_hash        BLOB NOT NULL CHECK (length(descriptor_hash) = 32),
    envelope_hash          BLOB NOT NULL CHECK (length(envelope_hash) = 32),
    device_id              BLOB NOT NULL CHECK (length(device_id) = 16),
    submitted_by           TEXT NOT NULL CHECK (length(submitted_by) BETWEEN 1 AND 128),
    idempotency_key_hash   BLOB NOT NULL UNIQUE CHECK (length(idempotency_key_hash) = 32),
    disposition            TEXT NOT NULL CHECK (disposition IN (
                               'PENDING','ORDERED','CONFLICTED','SELECTED','REJECTED'
                             )),
    final_sequence         INTEGER CHECK (final_sequence IS NULL OR final_sequence >= 1),
    receipt_digest         BLOB CHECK (receipt_digest IS NULL OR length(receipt_digest) = 32),
    CHECK (
      (final_sequence IS NULL AND receipt_digest IS NULL)
      OR (final_sequence IS NOT NULL AND receipt_digest IS NOT NULL)
    )
) STRICT;

CREATE INDEX ix_final_order_candidate_branch
ON final_order_candidates_v2(
  namespace_id, credential_id, base_version, base_descriptor_hash
);

CREATE TABLE final_order_receipts_v2 (
    receipt_digest            BLOB PRIMARY KEY CHECK (length(receipt_digest) = 32),
    namespace_id              BLOB NOT NULL CHECK (length(namespace_id) = 16),
    credential_id             BLOB NOT NULL CHECK (length(credential_id) = 32),
    ordered_object_digest     BLOB NOT NULL UNIQUE CHECK (length(ordered_object_digest) = 32),
    final_sequence            INTEGER NOT NULL UNIQUE CHECK (final_sequence >= 1),
    previous_ordered_digest   BLOB CHECK (
                                 previous_ordered_digest IS NULL
                                 OR length(previous_ordered_digest) = 32
                               ),
    authority_key_id          BLOB NOT NULL CHECK (length(authority_key_id) = 32),
    authority_key_generation  INTEGER NOT NULL CHECK (authority_key_generation >= 1),
    signature                 BLOB NOT NULL CHECK (length(signature) = 64),
    adapter_kind              TEXT NOT NULL CHECK (adapter_kind = 'RESEARCH_ADAPTER')
) STRICT;

CREATE TABLE final_order_checkpoints_v2 (
    checkpoint_digest    BLOB PRIMARY KEY CHECK (length(checkpoint_digest) = 32),
    namespace_id         BLOB NOT NULL CHECK (length(namespace_id) = 16),
    final_sequence       INTEGER NOT NULL CHECK (final_sequence >= 1),
    state_root           BLOB NOT NULL CHECK (length(state_root) = 32),
    last_receipt_digest  BLOB NOT NULL CHECK (length(last_receipt_digest) = 32),
    authority_key_id     BLOB NOT NULL CHECK (length(authority_key_id) = 32),
    key_generation       INTEGER NOT NULL CHECK (key_generation >= 1),
    signature            BLOB NOT NULL CHECK (length(signature) = 64),
    adapter_kind         TEXT NOT NULL CHECK (adapter_kind = 'RESEARCH_ADAPTER'),
    UNIQUE(namespace_id, final_sequence)
) STRICT;

CREATE TABLE final_order_resolutions_v2 (
    resolution_digest            BLOB PRIMARY KEY CHECK (length(resolution_digest) = 32),
    namespace_id                 BLOB NOT NULL CHECK (length(namespace_id) = 16),
    credential_id                BLOB NOT NULL CHECK (length(credential_id) = 32),
    selected_candidate_digest    BLOB NOT NULL CHECK (length(selected_candidate_digest) = 32),
    candidate_set_digest         BLOB NOT NULL CHECK (length(candidate_set_digest) = 32),
    resolution_descriptor_hash   BLOB NOT NULL CHECK (length(resolution_descriptor_hash) = 32),
    new_version                  INTEGER NOT NULL CHECK (new_version >= 2),
    resolved_by                  TEXT NOT NULL CHECK (length(resolved_by) BETWEEN 1 AND 128),
    basis                        TEXT NOT NULL CHECK (length(basis) BETWEEN 1 AND 256),
    final_sequence               INTEGER NOT NULL UNIQUE CHECK (final_sequence >= 1),
    receipt_digest               BLOB NOT NULL UNIQUE CHECK (length(receipt_digest) = 32)
) STRICT;

CREATE TABLE site_confirmation_evidence_v21 (
    evidence_digest       BLOB PRIMARY KEY CHECK (length(evidence_digest) = 32),
    change_id             BLOB NOT NULL UNIQUE CHECK (length(change_id) = 32),
    namespace_id          BLOB NOT NULL CHECK (length(namespace_id) = 16),
    credential_id         BLOB NOT NULL CHECK (length(credential_id) = 32),
    candidate_version     INTEGER NOT NULL CHECK (candidate_version >= 2),
    evidence_schema       INTEGER NOT NULL CHECK (evidence_schema = 2),
    evidence_level        INTEGER NOT NULL CHECK (evidence_level BETWEEN 0 AND 5),
    trust_kind            TEXT NOT NULL CHECK (trust_kind IN (
                                'BROWSER_OBSERVATION','RELOGIN_POLICY',
                                'MOCK_SITE_E4','TRUSTED_SITE_E4','USER_SIGNED'
                              )),
    decision_state        TEXT NOT NULL CHECK (decision_state IN (
                                'UNKNOWN','REVIEW_REQUIRED','FAILED',
                                'SITE_CONFIRM_PENDING','ACTIVE'
                              )),
    receipt_digest        BLOB CHECK (receipt_digest IS NULL OR length(receipt_digest) = 32),
    created_at_ms         INTEGER NOT NULL CHECK (created_at_ms >= 0)
) STRICT;

CREATE TABLE device_revocation_layers_v2 (
    namespace_id                  BLOB NOT NULL CHECK (length(namespace_id) = 16),
    device_id                     BLOB NOT NULL CHECK (length(device_id) = 16),
    control_plane_status          TEXT NOT NULL CHECK (control_plane_status IN (
                                           'PENDING','COMPLETED','FAILED','UNKNOWN'
                                         )),
    control_final_sequence        INTEGER CHECK (
                                           control_final_sequence IS NULL
                                           OR control_final_sequence >= 1
                                         ),
    secret_isolation_status       TEXT NOT NULL CHECK (secret_isolation_status IN (
                                           'PENDING','COMPLETED','FAILED','UNKNOWN'
                                         )),
    new_secret_generation         INTEGER CHECK (
                                           new_secret_generation IS NULL
                                           OR new_secret_generation >= 2
                                         ),
    external_remediation_status   TEXT NOT NULL CHECK (external_remediation_status IN (
                                           'PENDING','COMPLETED','FAILED','UNKNOWN'
                                         )),
    known_credential_set_digest   BLOB NOT NULL CHECK (length(known_credential_set_digest) = 32),
    future_blocked_set_digest     BLOB NOT NULL CHECK (length(future_blocked_set_digest) = 32),
    remediation_required_digest  BLOB NOT NULL CHECK (length(remediation_required_digest) = 32),
    updated_at_ms                 INTEGER NOT NULL CHECK (updated_at_ms >= 0),
    PRIMARY KEY(namespace_id, device_id),
    CHECK (
      control_plane_status != 'COMPLETED'
      OR control_final_sequence IS NOT NULL
    ),
    CHECK (
      secret_isolation_status != 'COMPLETED'
      OR new_secret_generation IS NOT NULL
    )
) STRICT;

INSERT INTO schema_migrations(version, name, checksum_sha256, applied_at_ms)
VALUES (
  8,
  '0008_stage2_protocol_closure',
  X'7c11ff6b5af6959c41c160789f395187440aa385aec441dbe034a32276b13b07',
  CAST(strftime('%s', 'now') AS INTEGER) * 1000
);

PRAGMA user_version = 8;
COMMIT;
