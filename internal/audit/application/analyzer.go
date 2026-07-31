package application

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"errors"
	"sort"
	"strconv"
	"strings"

	auditdomain "vdns.local/vdns/internal/audit/domain"
	"vdns.local/vdns/internal/cryptokit"
	operationdomain "vdns.local/vdns/internal/operation/domain"
	"vdns.local/vdns/internal/protocol"
	resolverdomain "vdns.local/vdns/internal/resolver/domain"
	transparencydomain "vdns.local/vdns/internal/transparency/domain"
)

var (
	ErrAuditAnalyzeDenied  = errors.New("AUDIT_ANALYZE authorization denied")
	ErrAuditHandleRejected = errors.New("audit secret handle rejected")
	ErrAuditAnalysis       = errors.New("security analysis failed")
	ErrAuditCursor         = errors.New("security analysis cursor rejected")
)

type SecretHandle interface {
	// Consume atomically invalidates the handle before invoking the callback.
	Consume(func(*cryptokit.Secret) error) error
}

type AnalysisAuthorization struct {
	Resolution       resolverdomain.Resolution
	DeviceCredential *operationdomain.SignedDeviceOperationCredential
	ProofBundle      *transparencydomain.SignedProofBundle
	TargetIDs        []protocol.CredentialID
	SecretGeneration uint64
	SecretHandle     SecretHandle
}

// AuthorizeAnalysis verifies the independently resolved L1-L5 projection and
// the private device scope. PUBLISH_AUDIT never satisfies AUDIT_ANALYZE.
func AuthorizeAnalysis(input AnalysisAuthorization) error {
	if input.DeviceCredential == nil || input.ProofBundle == nil ||
		input.SecretHandle == nil || input.SecretGeneration == 0 ||
		len(input.TargetIDs) == 0 {
		return ErrAuditAnalyzeDenied
	}
	resolution := input.Resolution
	if resolution.Verdict != protocol.VerdictAccept ||
		resolution.Authorization.Operation != protocol.OperationAuditAnalyze ||
		!resolution.Authorization.Capabilities.Allows(protocol.CapabilityAuditAnalyze) ||
		resolution.Principal.SecretGeneration != input.SecretGeneration ||
		resolution.ProofDigest != input.ProofBundle.Digest() {
		return ErrAuditAnalyzeDenied
	}
	for _, layer := range resolution.Layers {
		if !layer.Passed {
			return ErrAuditAnalyzeDenied
		}
	}
	credential := input.DeviceCredential.Payload()
	if input.DeviceCredential.Digest() != resolution.Principal.DeviceCredentialHash ||
		credential.NamespaceID != resolution.Principal.NamespaceID ||
		credential.DeviceID != resolution.Principal.DeviceID ||
		credential.SecretGeneration != input.SecretGeneration ||
		credential.ScopeDigest != resolution.Authorization.ScopeDigest ||
		credential.IssuanceCounter != resolution.Authorization.IssuanceCounter ||
		resolution.Authorization.FinalSequence < credential.ValidFromSequence ||
		resolution.Authorization.FinalSequence > credential.ValidUntilSequence ||
		!credential.Capabilities.Allows(protocol.CapabilityAuditAnalyze) {
		return ErrAuditAnalyzeDenied
	}
	proof := input.ProofBundle.Payload()
	if proof.NamespaceID != resolution.Principal.NamespaceID ||
		proof.SubjectDigest != resolution.ProofDigest &&
			proof.SubjectDigest != resolution.State.LastOperationEvent {
		// A ProofBundle may prove either the analysis operation object itself
		// or the current state event it authorizes. Other contexts are rejected.
		return ErrAuditAnalyzeDenied
	}
	for _, target := range input.TargetIDs {
		target := target
		if !credential.Scope.Allows(&target, nil) {
			return ErrAuditAnalyzeDenied
		}
	}
	return nil
}

type AnalysisRecord struct {
	CredentialID       protocol.CredentialID
	Version            uint64
	Epoch              uint64
	ObservedTimeBucket uint64
	UpdatedTimeBucket  uint64
	Witness            cryptokit.ReuseTag
	DeviceAuthorized   bool
	RollbackObserved   bool
	ConflictObserved   bool
	EvidenceDigests    [][sha256.Size]byte
}

type WitnessDeriver func(epoch uint64, password *cryptokit.Secret) (cryptokit.ReuseTag, error)

type AnalysisRequest struct {
	Authorization    AnalysisAuthorization
	Records          []AnalysisRecord
	CurrentBucket    uint64
	StaleAfterBucket uint64
	AnalysisSalt     [sha256.Size]byte
	DeriveWitness    WitnessDeriver
}

// RunAuthorizedAnalysis consumes the one-use secret only after all capability,
// scope, generation and ProofBundle checks pass. Results contain no secret,
// handle or stable reuse witness.
func RunAuthorizedAnalysis(request AnalysisRequest) ([]auditdomain.Finding, error) {
	if err := AuthorizeAnalysis(request.Authorization); err != nil {
		return nil, err
	}
	if len(request.Records) == 0 || request.CurrentBucket == 0 ||
		request.StaleAfterBucket == 0 || auditBytesZero(request.AnalysisSalt[:]) ||
		request.DeriveWitness == nil {
		return nil, ErrAuditAnalysis
	}
	var findings []auditdomain.Finding
	consumed := false
	err := request.Authorization.SecretHandle.Consume(func(secret *cryptokit.Secret) error {
		if consumed || secret == nil {
			return ErrAuditHandleRejected
		}
		consumed = true
		epochs := make(map[uint64]cryptokit.ReuseTag)
		for _, record := range request.Records {
			if _, exists := epochs[record.Epoch]; exists {
				continue
			}
			tag, err := request.DeriveWitness(record.Epoch, secret)
			if err != nil {
				return err
			}
			epochs[record.Epoch] = tag
		}
		defer func() {
			for epoch, tag := range epochs {
				clear(tag[:])
				delete(epochs, epoch)
			}
		}()
		var err error
		findings, err = analyzeRecords(request, epochs)
		return err
	})
	if err != nil || !consumed {
		return nil, errors.Join(ErrAuditHandleRejected, err)
	}
	return auditdomain.CanonicalFindings(findings)
}

type reuseGroupKey struct {
	epoch   uint64
	witness cryptokit.ReuseTag
}

func analyzeRecords(
	request AnalysisRequest,
	candidateByEpoch map[uint64]cryptokit.ReuseTag,
) ([]auditdomain.Finding, error) {
	groups := make(map[reuseGroupKey][]int)
	for index, record := range request.Records {
		if record.Version == 0 || record.Epoch == 0 ||
			record.ObservedTimeBucket == 0 || record.UpdatedTimeBucket == 0 ||
			auditBytesZero(record.CredentialID[:]) || auditBytesZero(record.Witness[:]) ||
			len(record.EvidenceDigests) == 0 {
			return nil, ErrAuditAnalysis
		}
		for _, digest := range record.EvidenceDigests {
			if auditBytesZero(digest[:]) {
				return nil, ErrAuditAnalysis
			}
		}
		groups[reuseGroupKey{epoch: record.Epoch, witness: record.Witness}] =
			append(groups[reuseGroupKey{epoch: record.Epoch, witness: record.Witness}], index)
	}
	findings := make([]auditdomain.Finding, 0, len(request.Records))
	for index, record := range request.Records {
		pseudonym := analysisPseudonym(request.AnalysisSalt, record.CredentialID)
		base := auditdomain.Finding{
			CredentialPseudonym:   pseudonym,
			Confidence:            ConfidenceForEvidence(record.EvidenceDigests),
			EvidenceObjectDigests: append([][sha256.Size]byte(nil), record.EvidenceDigests...),
			ObservedTimeBucket:    record.ObservedTimeBucket,
			CurrentVersion:        record.Version,
		}
		key := reuseGroupKey{epoch: record.Epoch, witness: record.Witness}
		if relatedIndexes := groups[key]; len(relatedIndexes) > 1 {
			finding := base
			finding.Kind = auditdomain.RiskPasswordReuse
			for _, relatedIndex := range relatedIndexes {
				if relatedIndex == index {
					continue
				}
				finding.RelatedPseudonyms = append(
					finding.RelatedPseudonyms,
					analysisPseudonym(request.AnalysisSalt, request.Records[relatedIndex].CredentialID),
				)
			}
			sort.Slice(finding.RelatedPseudonyms, func(i, j int) bool {
				return bytes.Compare(
					finding.RelatedPseudonyms[i][:], finding.RelatedPseudonyms[j][:],
				) < 0
			})
			findings = append(findings, finding)
		}
		if candidate, exists := candidateByEpoch[record.Epoch]; exists &&
			cryptokit.ReuseTagsEqual(candidate, record.Witness) {
			finding := base
			finding.Kind = auditdomain.RiskHistoricalUse
			findings = append(findings, finding)
		}
		if request.CurrentBucket >= record.UpdatedTimeBucket &&
			request.CurrentBucket-record.UpdatedTimeBucket >= request.StaleAfterBucket {
			finding := base
			finding.Kind = auditdomain.RiskStaleCredential
			findings = append(findings, finding)
		}
		for kind, observed := range map[auditdomain.RiskKind]bool{
			auditdomain.RiskAnomalousDevice: !record.DeviceAuthorized,
			auditdomain.RiskRollback:        record.RollbackObserved,
			auditdomain.RiskConflict:        record.ConflictObserved,
		} {
			if observed {
				finding := base
				finding.Kind = kind
				findings = append(findings, finding)
			}
		}
	}
	return findings, nil
}

func ConfidenceForEvidence(evidence [][sha256.Size]byte) auditdomain.Confidence {
	switch {
	case len(evidence) >= 2:
		return auditdomain.ConfidenceStrong
	case len(evidence) == 1:
		return auditdomain.ConfidenceMedium
	default:
		return auditdomain.ConfidenceWeak
	}
}

func analysisPseudonym(
	salt [sha256.Size]byte,
	credentialID protocol.CredentialID,
) [sha256.Size]byte {
	mac := hmac.New(sha256.New, salt[:])
	_, _ = mac.Write([]byte(protocol.DomainPrefix + "ANALYSIS-CREDENTIAL"))
	_, _ = mac.Write(credentialID[:])
	var result [sha256.Size]byte
	copy(result[:], mac.Sum(nil))
	return result
}

type FindingPage struct {
	Items      []auditdomain.Finding `json:"items"`
	NextCursor string                `json:"nextCursor,omitempty"`
}

// PaginateFindings uses a scope-bound authenticated cursor. Cursor contents do
// not include credential identifiers or evidence.
func PaginateFindings(
	findings []auditdomain.Finding,
	cursor string,
	limit int,
	analysisID string,
	cursorKey [sha256.Size]byte,
) (FindingPage, error) {
	canonical, err := auditdomain.CanonicalFindings(findings)
	if err != nil || limit < 1 || limit > 200 || analysisID == "" ||
		auditBytesZero(cursorKey[:]) {
		return FindingPage{}, ErrAuditCursor
	}
	offset, err := decodeAnalysisCursor(cursor, analysisID, cursorKey)
	if err != nil || offset > len(canonical) {
		return FindingPage{}, ErrAuditCursor
	}
	end := offset + limit
	if end > len(canonical) {
		end = len(canonical)
	}
	page := FindingPage{Items: append([]auditdomain.Finding(nil), canonical[offset:end]...)}
	if end < len(canonical) {
		page.NextCursor = encodeAnalysisCursor(end, analysisID, cursorKey)
	}
	return page, nil
}

func encodeAnalysisCursor(offset int, analysisID string, key [sha256.Size]byte) string {
	payload := strconv.Itoa(offset) + "|" + analysisID
	mac := hmac.New(sha256.New, key[:])
	_, _ = mac.Write([]byte(protocol.DomainPrefix + "ANALYSIS-CURSOR|" + payload))
	tag := mac.Sum(nil)
	return base64.RawURLEncoding.EncodeToString(
		[]byte(payload + "|" + base64.RawURLEncoding.EncodeToString(tag[:16])),
	)
}

func decodeAnalysisCursor(
	cursor, analysisID string,
	key [sha256.Size]byte,
) (int, error) {
	if cursor == "" {
		return 0, nil
	}
	if len(cursor) > 512 {
		return 0, ErrAuditCursor
	}
	decoded, err := base64.RawURLEncoding.DecodeString(cursor)
	if err != nil {
		return 0, ErrAuditCursor
	}
	parts := strings.Split(string(decoded), "|")
	if len(parts) != 3 || parts[1] != analysisID {
		return 0, ErrAuditCursor
	}
	payload := strings.Join(parts[:2], "|")
	mac := hmac.New(sha256.New, key[:])
	_, _ = mac.Write([]byte(protocol.DomainPrefix + "ANALYSIS-CURSOR|" + payload))
	expected := base64.RawURLEncoding.EncodeToString(mac.Sum(nil)[:16])
	if subtle.ConstantTimeCompare([]byte(parts[2]), []byte(expected)) != 1 {
		return 0, ErrAuditCursor
	}
	offset, err := strconv.Atoi(parts[0])
	if err != nil || offset < 0 {
		return 0, ErrAuditCursor
	}
	return offset, nil
}
