-- VDNS SQLite schema migration
-- Version: 0007
-- Name: g6_privacy_response
-- Adds private audit evidence, minimized findings and optional incident-response state.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;

BEGIN IMMEDIATE;

CREATE TABLE audit_events_v2 (
    event_id                    BLOB PRIMARY KEY CHECK (length(event_id) = 32),
    credential_id               BLOB NOT NULL CHECK (length(credential_id) = 32),
    credential_version          INTEGER NOT NULL CHECK (credential_version >= 1),
    epoch                       INTEGER NOT NULL CHECK (epoch >= 1),
    encrypted_payload_digest    BLOB NOT NULL UNIQUE CHECK (length(encrypted_payload_digest) = 32),
    encrypted_object_hash       BLOB NOT NULL UNIQUE CHECK (length(encrypted_object_hash) = 32),
    evidence_level              INTEGER NOT NULL CHECK (evidence_level BETWEEN 1 AND 5),
    observed_time_bucket        INTEGER NOT NULL CHECK (observed_time_bucket >= 1),
    public_leaf_digest          BLOB NOT NULL UNIQUE CHECK (length(public_leaf_digest) = 32),
    publication_state           TEXT NOT NULL CHECK (publication_state IN (
                                  'OBJECT_STORED','FAILED_RETRYABLE',
                                  'LOG_INCLUDED','CHECKPOINT_ANCHORED'
                                )),
    final_sequence              INTEGER CHECK (final_sequence IS NULL OR final_sequence >= 1),
    created_at_ms               INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms               INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    CHECK (
      publication_state IN ('OBJECT_STORED','FAILED_RETRYABLE')
      OR final_sequence IS NOT NULL
    ),
    FOREIGN KEY (event_id) REFERENCES operation_events(event_id) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id, credential_version)
        REFERENCES credential_versions(credential_id, version) ON DELETE RESTRICT,
    FOREIGN KEY (encrypted_object_hash) REFERENCES content_objects(object_hash) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_audit_events_v2_scan
ON audit_events_v2(epoch, observed_time_bucket, credential_id);

CREATE INDEX ix_audit_events_v2_publication
ON audit_events_v2(publication_state, updated_at_ms);

CREATE TABLE security_analyses_v2 (
    analysis_id                 BLOB PRIMARY KEY CHECK (length(analysis_id) = 32),
    namespace_id                BLOB NOT NULL CHECK (length(namespace_id) = 16),
    requested_by_device_id      BLOB NOT NULL CHECK (length(requested_by_device_id) = 16),
    window_start_bucket         INTEGER NOT NULL CHECK (window_start_bucket >= 1),
    window_end_bucket           INTEGER NOT NULL CHECK (window_end_bucket >= window_start_bucket),
    policy_hash                 BLOB NOT NULL CHECK (length(policy_hash) = 32),
    source_checkpoint_digest    BLOB NOT NULL CHECK (length(source_checkpoint_digest) = 32),
    proof_bundle_digest         BLOB NOT NULL CHECK (length(proof_bundle_digest) = 32),
    secret_generation           INTEGER NOT NULL CHECK (secret_generation >= 1),
    result_object_digest        BLOB CHECK (result_object_digest IS NULL OR length(result_object_digest) = 32),
    result_count                INTEGER NOT NULL DEFAULT 0 CHECK (result_count >= 0),
    status                      TEXT NOT NULL CHECK (status IN (
                                  'QUEUED','RUNNING','COMPLETED','FAILED'
                                )),
    stable_error_code           TEXT CHECK (
                                  stable_error_code IS NULL
                                  OR length(stable_error_code) BETWEEN 3 AND 64
                                ),
    created_sequence            INTEGER NOT NULL CHECK (created_sequence >= 1),
    created_at_ms               INTEGER NOT NULL CHECK (created_at_ms >= 0),
    completed_at_ms             INTEGER CHECK (completed_at_ms IS NULL OR completed_at_ms >= created_at_ms),
    CHECK (
      (status = 'COMPLETED' AND result_object_digest IS NOT NULL
                            AND completed_at_ms IS NOT NULL
                            AND stable_error_code IS NULL)
      OR
      (status = 'FAILED' AND result_object_digest IS NULL
                         AND completed_at_ms IS NOT NULL
                         AND stable_error_code IS NOT NULL)
      OR
      (status IN ('QUEUED','RUNNING') AND result_object_digest IS NULL
                                      AND completed_at_ms IS NULL
                                      AND stable_error_code IS NULL)
    ),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (requested_by_device_id) REFERENCES devices(device_id) ON DELETE RESTRICT,
    FOREIGN KEY (source_checkpoint_digest)
        REFERENCES checkpoints_v2(checkpoint_digest) ON DELETE RESTRICT,
    FOREIGN KEY (proof_bundle_digest)
        REFERENCES proof_bundles_v2(proof_bundle_digest) ON DELETE RESTRICT,
    FOREIGN KEY (result_object_digest) REFERENCES content_objects(object_hash) ON DELETE RESTRICT,
    FOREIGN KEY (namespace_id, secret_generation)
        REFERENCES namespace_key_generations(namespace_id, generation) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_security_analyses_v2_status
ON security_analyses_v2(namespace_id, status, created_sequence);

CREATE TABLE security_findings_v2 (
    analysis_id                 BLOB NOT NULL CHECK (length(analysis_id) = 32),
    ordinal                     INTEGER NOT NULL CHECK (ordinal >= 0),
    risk_kind                   TEXT NOT NULL CHECK (risk_kind IN (
                                  'PASSWORD_REUSE','HISTORICAL_USE',
                                  'STALE_CREDENTIAL','ANOMALOUS_DEVICE',
                                  'ROLLBACK','CONFLICT'
                                )),
    credential_pseudonym        BLOB NOT NULL CHECK (length(credential_pseudonym) = 32),
    confidence                  TEXT NOT NULL CHECK (confidence IN ('WEAK','MEDIUM','STRONG')),
    evidence_reference_cbor     BLOB NOT NULL CHECK (length(evidence_reference_cbor) BETWEEN 1 AND 65536),
    finding_digest              BLOB NOT NULL UNIQUE CHECK (length(finding_digest) = 32),
    observed_time_bucket        INTEGER NOT NULL CHECK (observed_time_bucket >= 1),
    current_version             INTEGER NOT NULL CHECK (current_version >= 1),
    PRIMARY KEY (analysis_id, ordinal),
    UNIQUE (analysis_id, risk_kind, credential_pseudonym, finding_digest),
    FOREIGN KEY (analysis_id) REFERENCES security_analyses_v2(analysis_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_security_findings_v2_page
ON security_findings_v2(analysis_id, ordinal, risk_kind);

CREATE TABLE exposure_analyses_v2 (
    analysis_id                 BLOB PRIMARY KEY CHECK (length(analysis_id) = 32),
    namespace_id                BLOB NOT NULL CHECK (length(namespace_id) = 16),
    snapshot_root               BLOB NOT NULL CHECK (length(snapshot_root) = 32),
    incident_commitment         BLOB NOT NULL CHECK (length(incident_commitment) = 32),
    affected_root               BLOB CHECK (affected_root IS NULL OR length(affected_root) = 32),
    source_checkpoint_digest    BLOB NOT NULL CHECK (length(source_checkpoint_digest) = 32),
    window_start_bucket         INTEGER NOT NULL CHECK (window_start_bucket >= 1),
    window_end_bucket           INTEGER NOT NULL CHECK (window_end_bucket >= window_start_bucket),
    proof_system                TEXT NOT NULL CHECK (proof_system IN ('SCOPE_ZK','GENERIC_ZKVM')),
    proof_digest                BLOB CHECK (proof_digest IS NULL OR length(proof_digest) = 32),
    affected_count              INTEGER NOT NULL DEFAULT 0 CHECK (affected_count >= 0),
    status                      TEXT NOT NULL CHECK (status IN (
                                  'QUEUED','RUNNING','COMPLETED','FAILED'
                                )),
    stable_error_code           TEXT CHECK (
                                  stable_error_code IS NULL
                                  OR length(stable_error_code) BETWEEN 3 AND 64
                                ),
    created_at_ms               INTEGER NOT NULL CHECK (created_at_ms >= 0),
    completed_at_ms             INTEGER CHECK (completed_at_ms IS NULL OR completed_at_ms >= created_at_ms),
    CHECK (
      (status = 'COMPLETED' AND affected_root IS NOT NULL
                            AND proof_digest IS NOT NULL
                            AND completed_at_ms IS NOT NULL
                            AND stable_error_code IS NULL)
      OR
      (status = 'FAILED' AND affected_root IS NULL
                         AND proof_digest IS NULL
                         AND completed_at_ms IS NOT NULL
                         AND stable_error_code IS NOT NULL)
      OR
      (status IN ('QUEUED','RUNNING') AND affected_root IS NULL
                                      AND proof_digest IS NULL
                                      AND completed_at_ms IS NULL
                                      AND stable_error_code IS NULL)
    ),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (source_checkpoint_digest)
        REFERENCES checkpoints_v2(checkpoint_digest) ON DELETE RESTRICT
) STRICT;

CREATE TABLE remediation_campaigns_v2 (
    campaign_id                 BLOB PRIMARY KEY CHECK (length(campaign_id) = 32),
    namespace_id                BLOB NOT NULL CHECK (length(namespace_id) = 16),
    exposure_analysis_id        BLOB NOT NULL UNIQUE CHECK (length(exposure_analysis_id) = 32),
    affected_root               BLOB NOT NULL CHECK (length(affected_root) = 32),
    cost_policy_hash            BLOB NOT NULL CHECK (length(cost_policy_hash) = 32),
    total_cost                  INTEGER NOT NULL CHECK (total_cost >= 1),
    item_count                  INTEGER NOT NULL CHECK (item_count BETWEEN 1 AND 100000),
    completed_count             INTEGER NOT NULL DEFAULT 0 CHECK (completed_count >= 0),
    pending_count               INTEGER NOT NULL DEFAULT 0 CHECK (pending_count >= 0),
    failed_count                INTEGER NOT NULL DEFAULT 0 CHECK (failed_count >= 0),
    unknown_count               INTEGER NOT NULL DEFAULT 0 CHECK (unknown_count >= 0),
    rotation_root               BLOB CHECK (rotation_root IS NULL OR length(rotation_root) = 32),
    status                      TEXT NOT NULL CHECK (status IN (
                                  'PLANNED','IN_PROGRESS','PARTIAL',
                                  'COMPLETED','FAILED','CANCELLED'
                                )),
    created_at_ms               INTEGER NOT NULL CHECK (created_at_ms >= 0),
    updated_at_ms               INTEGER NOT NULL CHECK (updated_at_ms >= created_at_ms),
    CHECK (
      completed_count + pending_count + failed_count + unknown_count <= item_count
    ),
    CHECK (
      (status IN ('PARTIAL','COMPLETED','FAILED') AND rotation_root IS NOT NULL)
      OR
      (status IN ('PLANNED','IN_PROGRESS','CANCELLED') AND rotation_root IS NULL)
    ),
    FOREIGN KEY (namespace_id) REFERENCES namespaces(namespace_id) ON DELETE RESTRICT,
    FOREIGN KEY (exposure_analysis_id)
        REFERENCES exposure_analyses_v2(analysis_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_remediation_campaigns_v2_status
ON remediation_campaigns_v2(namespace_id, status, updated_at_ms);

CREATE TABLE remediation_items_v2 (
    campaign_id                 BLOB NOT NULL CHECK (length(campaign_id) = 32),
    item_id                     BLOB NOT NULL CHECK (length(item_id) = 32),
    credential_id               BLOB NOT NULL CHECK (length(credential_id) = 32),
    action                      TEXT NOT NULL CHECK (action IN (
                                  'ROTATE_PASSWORD','REVOKE_SESSION',
                                  'CHANGE_RECOVERY_CHANNEL','REMOVE_SSO_BINDING',
                                  'RESET_MFA','REVOKE_DEVICE','REVOKE_API_TOKEN'
                                )),
    old_version                 INTEGER NOT NULL CHECK (old_version >= 1),
    new_version                 INTEGER NOT NULL CHECK (new_version >= old_version),
    attempt                     INTEGER NOT NULL CHECK (attempt >= 1),
    precondition_hash           BLOB NOT NULL CHECK (length(precondition_hash) = 32),
    cost                        INTEGER NOT NULL CHECK (cost >= 1),
    recovery_risk               TEXT NOT NULL CHECK (recovery_risk IN (
                                  'LOW','MODERATE','HIGH','LOCKOUT'
                                )),
    outcome_status              TEXT NOT NULL CHECK (outcome_status IN (
                                  'COMPLETED','PENDING','FAILED','UNKNOWN'
                                )),
    evidence_digest             BLOB NOT NULL CHECK (length(evidence_digest) = 32),
    before_fields_digest        BLOB NOT NULL CHECK (length(before_fields_digest) = 32),
    after_fields_digest         BLOB NOT NULL CHECK (length(after_fields_digest) = 32),
    receipt_digest              BLOB CHECK (receipt_digest IS NULL OR length(receipt_digest) = 32),
    stable_error_code           TEXT CHECK (
                                  stable_error_code IS NULL
                                  OR length(stable_error_code) BETWEEN 3 AND 64
                                ),
    updated_at_ms               INTEGER NOT NULL CHECK (updated_at_ms >= 0),
    PRIMARY KEY (campaign_id, item_id),
    UNIQUE (campaign_id, credential_id, action),
    CHECK (
      (outcome_status = 'COMPLETED' AND receipt_digest IS NOT NULL
                                    AND stable_error_code IS NULL)
      OR
      (outcome_status = 'FAILED' AND receipt_digest IS NULL
                                 AND stable_error_code IS NOT NULL)
      OR
      (outcome_status IN ('PENDING','UNKNOWN') AND receipt_digest IS NULL)
    ),
    CHECK (
      (outcome_status <> 'COMPLETED' AND new_version = old_version
                                       AND before_fields_digest = after_fields_digest)
      OR
      (outcome_status = 'COMPLETED'
       AND action IN ('ROTATE_PASSWORD','CHANGE_RECOVERY_CHANNEL','RESET_MFA')
       AND new_version = old_version + 1
       AND before_fields_digest <> after_fields_digest)
      OR
      (outcome_status = 'COMPLETED'
       AND action NOT IN ('ROTATE_PASSWORD','CHANGE_RECOVERY_CHANNEL','RESET_MFA')
       AND new_version = old_version
       AND before_fields_digest = after_fields_digest)
    ),
    FOREIGN KEY (campaign_id)
        REFERENCES remediation_campaigns_v2(campaign_id) ON DELETE RESTRICT,
    FOREIGN KEY (credential_id) REFERENCES credentials(credential_id) ON DELETE RESTRICT
) STRICT;

CREATE INDEX ix_remediation_items_v2_outcome
ON remediation_items_v2(campaign_id, outcome_status, item_id);

CREATE TABLE rotation_attempt_receipts_v2 (
    campaign_id                 BLOB NOT NULL CHECK (length(campaign_id) = 32),
    item_id                     BLOB NOT NULL CHECK (length(item_id) = 32),
    attempt                     INTEGER NOT NULL CHECK (attempt >= 1),
    action                      TEXT NOT NULL CHECK (length(action) BETWEEN 3 AND 64),
    old_version                 INTEGER NOT NULL CHECK (old_version >= 1),
    new_version                 INTEGER NOT NULL CHECK (new_version >= old_version),
    outcome_status              TEXT NOT NULL CHECK (outcome_status IN (
                                  'COMPLETED','PENDING','FAILED','UNKNOWN'
                                )),
    evidence_digest             BLOB NOT NULL CHECK (length(evidence_digest) = 32),
    receipt_digest              BLOB NOT NULL CHECK (length(receipt_digest) = 32),
    committed_at_ms             INTEGER NOT NULL CHECK (committed_at_ms >= 0),
    PRIMARY KEY (campaign_id, item_id, attempt),
    FOREIGN KEY (campaign_id, item_id)
        REFERENCES remediation_items_v2(campaign_id, item_id) ON DELETE RESTRICT
) STRICT;

INSERT INTO schema_migrations(version, name, checksum_sha256, applied_at_ms)
VALUES (
  7,
  '0007_g6_privacy_response',
  X'bda97d75cd1717c7afa0f1172be04781f01ac0e327647d423883746db8cc67eb',
  CAST(strftime('%s', 'now') AS INTEGER) * 1000
);

PRAGMA user_version = 7;
COMMIT;
