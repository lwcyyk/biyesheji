// Package domain defines privacy-preserving audit events and minimized
// security-analysis results. Hidden reuse witnesses exist only in the private
// event payload and cannot be serialized through ordinary JSON or text paths.
package domain

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"sort"

	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

const (
	AuditPayloadVersion = uint64(1)
	MaxEvidenceRefs     = 16
	MaxFindings         = 1_000_000
)

var (
	ErrInvalidAuditEvent = errors.New("invalid private audit event")
	ErrInvalidFinding    = errors.New("invalid security finding")
)

// PrivateUseEvent is encoded with deterministic CBOR and immediately sealed.
// CredentialID, DeviceID and ReuseTag must never be copied into a public leaf.
type PrivateUseEvent struct {
	FormatVersion      uint64                 `cbor:"format_version"`
	CredentialID       protocol.CredentialID  `cbor:"credential_id"`
	CredentialVersion  uint64                 `cbor:"credential_version"`
	DeviceID           protocol.DeviceID      `cbor:"device_id"`
	EvidenceLevel      protocol.EvidenceLevel `cbor:"evidence_level"`
	ObservedTimeBucket uint64                 `cbor:"observed_time_bucket"`
	DescriptorDigest   [sha256.Size]byte      `cbor:"descriptor_digest"`
	ReuseWitness       cryptokit.ReuseTag     `cbor:"reuse_witness"`
}

func (event PrivateUseEvent) Validate() error {
	if event.FormatVersion != AuditPayloadVersion ||
		auditZero(event.CredentialID[:]) || event.CredentialVersion == 0 ||
		auditZero(event.DeviceID[:]) || !event.EvidenceLevel.Valid() ||
		event.ObservedTimeBucket == 0 ||
		auditZero(event.DescriptorDigest[:]) ||
		auditZero(event.ReuseWitness[:]) {
		return ErrInvalidAuditEvent
	}
	return nil
}

// MarshalPrivateUseEvent is intentionally named private: its result must be
// handed directly to an authenticated-encryption boundary, never to JSON,
// logs, telemetry or public transparency objects.
func MarshalPrivateUseEvent(event PrivateUseEvent) ([]byte, error) {
	if event.Validate() != nil {
		return nil, ErrInvalidAuditEvent
	}
	encoded, err := protocol.MarshalDeterministic(event)
	if err != nil {
		return nil, ErrInvalidAuditEvent
	}
	return encoded, nil
}

func ParsePrivateUseEvent(encoded []byte) (PrivateUseEvent, error) {
	var event PrivateUseEvent
	if len(encoded) == 0 || len(encoded) > cryptokit.MaxEventPlaintextSize {
		return event, ErrInvalidAuditEvent
	}
	if err := protocol.UnmarshalDeterministic(encoded, &event); err != nil ||
		event.Validate() != nil {
		return PrivateUseEvent{}, ErrInvalidAuditEvent
	}
	canonical, err := protocol.MarshalDeterministic(event)
	if err != nil || !bytes.Equal(canonical, encoded) {
		return PrivateUseEvent{}, ErrInvalidAuditEvent
	}
	return event, nil
}

type RiskKind uint8

const (
	RiskPasswordReuse   RiskKind = 1
	RiskHistoricalUse   RiskKind = 2
	RiskStaleCredential RiskKind = 3
	RiskAnomalousDevice RiskKind = 4
	RiskRollback        RiskKind = 5
	RiskConflict        RiskKind = 6
)

func (kind RiskKind) Valid() bool {
	return kind >= RiskPasswordReuse && kind <= RiskConflict
}

type Confidence uint8

const (
	ConfidenceWeak   Confidence = 1
	ConfidenceMedium Confidence = 2
	ConfidenceStrong Confidence = 3
)

func (confidence Confidence) Valid() bool {
	return confidence >= ConfidenceWeak && confidence <= ConfidenceStrong
}

// Finding contains a per-analysis credential pseudonym and proof references.
// Passwords, ReuseTags, stable device identifiers and secret handles are
// structurally absent.
type Finding struct {
	Kind                  RiskKind            `cbor:"kind" json:"kind"`
	CredentialPseudonym   [sha256.Size]byte   `cbor:"credential_pseudonym" json:"credentialPseudonym"`
	RelatedPseudonyms     [][sha256.Size]byte `cbor:"related_pseudonyms" json:"relatedPseudonyms,omitempty"`
	Confidence            Confidence          `cbor:"confidence" json:"confidence"`
	EvidenceObjectDigests [][sha256.Size]byte `cbor:"evidence_digests" json:"evidenceDigests"`
	ObservedTimeBucket    uint64              `cbor:"observed_time_bucket" json:"observedTimeBucket"`
	CurrentVersion        uint64              `cbor:"current_version" json:"currentVersion"`
}

func (finding Finding) Validate() error {
	if !finding.Kind.Valid() || !finding.Confidence.Valid() ||
		auditZero(finding.CredentialPseudonym[:]) ||
		len(finding.RelatedPseudonyms) > MaxEvidenceRefs ||
		len(finding.EvidenceObjectDigests) == 0 ||
		len(finding.EvidenceObjectDigests) > MaxEvidenceRefs ||
		finding.ObservedTimeBucket == 0 || finding.CurrentVersion == 0 {
		return ErrInvalidFinding
	}
	for _, value := range finding.RelatedPseudonyms {
		if auditZero(value[:]) {
			return ErrInvalidFinding
		}
	}
	for _, value := range finding.EvidenceObjectDigests {
		if auditZero(value[:]) {
			return ErrInvalidFinding
		}
	}
	return nil
}

// CanonicalFindings returns a deterministic copy suitable for result-object
// hashing and stable pagination.
func CanonicalFindings(findings []Finding) ([]Finding, error) {
	if len(findings) > MaxFindings {
		return nil, ErrInvalidFinding
	}
	result := make([]Finding, len(findings))
	for index, finding := range findings {
		if finding.Validate() != nil {
			return nil, ErrInvalidFinding
		}
		result[index] = cloneFinding(finding)
	}
	sort.Slice(result, func(i, j int) bool {
		if comparison := bytes.Compare(
			result[i].CredentialPseudonym[:], result[j].CredentialPseudonym[:],
		); comparison != 0 {
			return comparison < 0
		}
		if result[i].Kind != result[j].Kind {
			return result[i].Kind < result[j].Kind
		}
		return result[i].ObservedTimeBucket < result[j].ObservedTimeBucket
	})
	return result, nil
}

func cloneFinding(finding Finding) Finding {
	finding.RelatedPseudonyms = append([][sha256.Size]byte(nil), finding.RelatedPseudonyms...)
	finding.EvidenceObjectDigests = append([][sha256.Size]byte(nil), finding.EvidenceObjectDigests...)
	return finding
}

func auditZero(value []byte) bool {
	var combined byte
	for _, item := range value {
		combined |= item
	}
	return combined == 0
}
