// Package domain contains password-rotation domain values and invariants.
package domain

import (
	"crypto/sha256"
	"crypto/subtle"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"math"
	"math/big"
	"sort"
	"sync"
	"unicode/utf8"

	"vdns.local/vdns/internal/protocol"
)

const (
	policyHashBytes        = 32
	policySchemaVersion    = uint64(1)
	maxPasswordSymbols     = 1024
	maxPolicyCandidates    = 1024
	maxPolicyStreamBlocks  = 8192
	maxRequiredClasses     = 16
	maxForbiddenPatterns   = 32
	maxPolicyNameBytes     = 128
	maxPolicyAlphabetBytes = 1024
	maxPolicySetBytes      = 1024
	maxPolicySetRunes      = 256
	maxPolicyItemBytes     = 1024
	maxPolicyItemRunes     = 256
	maxPolicyTotalBytes    = 8192
	maxPolicyTotalRunes    = 2048
	minimumSafeEntropyBits = 72
	redactedPolicyContext  = "[REDACTED POLICY CONTEXT]"
	redactedPassword       = "[REDACTED PASSWORD]"
)

var (
	ErrInvalidPasswordPolicy = errors.New("invalid password policy")
	ErrInvalidPolicyContext  = errors.New("invalid policy context")
	ErrPolicyHashMismatch    = errors.New("password policy hash mismatch")
	ErrPolicyPRF             = errors.New("password stream PRF failed")
	ErrNoPolicyCandidate     = errors.New("password policy requires manual handling")
	ErrPolicyEncoding        = errors.New("password stream context encoding failed")
	ErrPasswordDestroyed     = errors.New("password is unavailable")
	ErrSecretSerialization   = errors.New("secret cannot be serialized implicitly")
)

// RequiredClassSpec describes a character class that must occur at least
// MinCount times. Characters are Unicode code points, while Length in
// PolicySpec is a count of code points rather than UTF-8 bytes.
type RequiredClassSpec struct {
	Name       string
	Characters string
	MinCount   uint16
}

// PolicySpec is the validated input to NewPasswordPolicy. ForbiddenPatterns
// are case-sensitive literal code-point sequences, not regular expressions;
// this makes matching and conservative search-space accounting deterministic.
type PolicySpec struct {
	Length              uint16
	Alphabet            string
	RequiredClasses     []RequiredClassSpec
	ForbiddenCharacters string
	ForbiddenPatterns   []string
}

// PasswordPolicy is an immutable, validated password-generation policy.
type PasswordPolicy struct {
	length            int
	alphabet          []rune
	requiredClasses   []requiredClass
	forbiddenPatterns []compiledPattern
	entropyLowerBound *big.Int
	entropyBits       float64
	highRisk          bool
	hash              [sha256.Size]byte
}

type requiredClass struct {
	name       string
	characters map[rune]struct{}
	minCount   int
}

type compiledPattern struct {
	symbols []rune
	failure []int
}

// policyCommitment is the frozen v1 PolicyHash schema. Canonicalization rules:
//   - raw and effective alphabet order is preserved because index order changes
//     generated passwords;
//   - required classes are sorted by bytewise UTF-8 name; duplicate class
//     characters are rejected and the remaining set is sorted by code point;
//   - forbidden characters are a set, deduplicated and sorted by code point;
//   - forbidden literal patterns are sorted bytewise after duplicates are
//     rejected;
//   - valid UTF-8 is preserved byte-exactly: no NFC/NFKC normalization occurs.
//
// Both raw and effective alphabets are committed so removal of forbidden
// characters cannot silently change the byte-to-symbol mapping.
type policyCommitment struct {
	Version             uint64                          `cbor:"version"`
	Length              uint64                          `cbor:"length"`
	RawAlphabet         string                          `cbor:"raw_alphabet"`
	EffectiveAlphabet   string                          `cbor:"effective_alphabet"`
	RequiredClasses     []policyRequiredClassCommitment `cbor:"required_classes"`
	ForbiddenCharacters string                          `cbor:"forbidden_characters"`
	ForbiddenPatterns   []string                        `cbor:"forbidden_patterns"`
}

type policyRequiredClassCommitment struct {
	Name       string `cbor:"name"`
	Characters string `cbor:"characters"`
	MinCount   uint64 `cbor:"min_count"`
}

// NewPasswordPolicy validates, canonicalizes, commits, and compiles a site
// policy. Duplicate alphabet or class symbols are rejected because duplicates
// would make either generation weights or the committed input ambiguous.
func NewPasswordPolicy(spec PolicySpec) (PasswordPolicy, error) {
	if spec.Length == 0 || spec.Length > maxPasswordSymbols ||
		len(spec.RequiredClasses) > maxRequiredClasses || len(spec.ForbiddenPatterns) > maxForbiddenPatterns ||
		len(spec.Alphabet) > maxPolicyAlphabetBytes || len(spec.ForbiddenCharacters) > maxPolicySetBytes ||
		utf8.RuneCountInString(spec.ForbiddenCharacters) > maxPolicySetRunes ||
		!utf8.ValidString(spec.Alphabet) || !utf8.ValidString(spec.ForbiddenCharacters) {
		return PasswordPolicy{}, ErrInvalidPasswordPolicy
	}

	canonicalForbidden := canonicalRuneSetString(spec.ForbiddenCharacters)
	forbiddenChars := runeSet([]rune(canonicalForbidden))
	alphabetInput := []rune(spec.Alphabet)
	if len(alphabetInput) == 0 || len(alphabetInput) > 256 || hasDuplicateRunes(alphabetInput) {
		return PasswordPolicy{}, ErrInvalidPasswordPolicy
	}
	alphabet := make([]rune, 0, len(alphabetInput))
	alphabetSet := make(map[rune]struct{}, len(alphabetInput))
	for _, symbol := range alphabetInput {
		if _, forbidden := forbiddenChars[symbol]; forbidden {
			continue
		}
		alphabet = append(alphabet, symbol)
		alphabetSet[symbol] = struct{}{}
	}
	if len(alphabet) == 0 {
		return PasswordPolicy{}, ErrInvalidPasswordPolicy
	}

	requiredSpecs := append([]RequiredClassSpec(nil), spec.RequiredClasses...)
	sort.Slice(requiredSpecs, func(left, right int) bool {
		return requiredSpecs[left].Name < requiredSpecs[right].Name
	})
	required := make([]requiredClass, 0, len(requiredSpecs))
	requiredCommitments := make([]policyRequiredClassCommitment, 0, len(requiredSpecs))
	classNames := make(map[string]struct{}, len(requiredSpecs))
	totalClassBytes := 0
	totalClassRunes := 0
	for _, classSpec := range requiredSpecs {
		classRuneCount := utf8.RuneCountInString(classSpec.Characters)
		totalClassBytes += len(classSpec.Name) + len(classSpec.Characters)
		totalClassRunes += classRuneCount + utf8.RuneCountInString(classSpec.Name)
		if classSpec.Name == "" || len(classSpec.Name) > maxPolicyNameBytes ||
			len(classSpec.Characters) > maxPolicyItemBytes || classRuneCount > maxPolicyItemRunes ||
			totalClassBytes > maxPolicyTotalBytes || totalClassRunes > maxPolicyTotalRunes ||
			!utf8.ValidString(classSpec.Name) || classSpec.MinCount == 0 || int(classSpec.MinCount) > int(spec.Length) || !utf8.ValidString(classSpec.Characters) {
			return PasswordPolicy{}, ErrInvalidPasswordPolicy
		}
		if _, duplicate := classNames[classSpec.Name]; duplicate {
			return PasswordPolicy{}, ErrInvalidPasswordPolicy
		}
		classNames[classSpec.Name] = struct{}{}

		classRunes := []rune(classSpec.Characters)
		if len(classRunes) == 0 || hasDuplicateRunes(classRunes) {
			return PasswordPolicy{}, ErrInvalidPasswordPolicy
		}
		canonicalClassCharacters := sortedRuneString(classRunes)
		characters := make(map[rune]struct{}, len(classRunes))
		for _, symbol := range classRunes {
			if _, allowed := alphabetSet[symbol]; allowed {
				characters[symbol] = struct{}{}
			}
		}
		if len(characters) == 0 {
			return PasswordPolicy{}, ErrInvalidPasswordPolicy
		}
		required = append(required, requiredClass{
			name:       classSpec.Name,
			characters: characters,
			minCount:   int(classSpec.MinCount),
		})
		requiredCommitments = append(requiredCommitments, policyRequiredClassCommitment{
			Name:       classSpec.Name,
			Characters: canonicalClassCharacters,
			MinCount:   uint64(classSpec.MinCount),
		})
	}

	// Empty collections are always encoded as CBOR arrays, never null, so Go
	// and TypeScript produce the same PolicyHash for a policy with no patterns.
	canonicalPatterns := make([]string, len(spec.ForbiddenPatterns))
	copy(canonicalPatterns, spec.ForbiddenPatterns)
	seenPatterns := make(map[string]struct{}, len(canonicalPatterns))
	totalPatternBytes := 0
	totalPatternRunes := 0
	for _, pattern := range canonicalPatterns {
		patternRuneCount := utf8.RuneCountInString(pattern)
		totalPatternBytes += len(pattern)
		totalPatternRunes += patternRuneCount
		if pattern == "" || len(pattern) > maxPolicyItemBytes || patternRuneCount > maxPolicyItemRunes ||
			totalPatternBytes > maxPolicyTotalBytes || totalPatternRunes > maxPolicyTotalRunes || !utf8.ValidString(pattern) {
			return PasswordPolicy{}, ErrInvalidPasswordPolicy
		}
		if _, duplicate := seenPatterns[pattern]; duplicate {
			return PasswordPolicy{}, ErrInvalidPasswordPolicy
		}
		seenPatterns[pattern] = struct{}{}
	}
	sort.Strings(canonicalPatterns)
	patterns := make([]compiledPattern, 0, len(canonicalPatterns))
	for _, pattern := range canonicalPatterns {
		patterns = append(patterns, compilePattern([]rune(pattern)))
	}

	commitment := policyCommitment{
		Version:             policySchemaVersion,
		Length:              uint64(spec.Length),
		RawAlphabet:         spec.Alphabet,
		EffectiveAlphabet:   string(alphabet),
		RequiredClasses:     requiredCommitments,
		ForbiddenCharacters: canonicalForbidden,
		ForbiddenPatterns:   canonicalPatterns,
	}
	commitmentBytes, err := protocol.MarshalDeterministic(commitment)
	if err != nil {
		return PasswordPolicy{}, ErrPolicyEncoding
	}
	policyHash := sha256.Sum256(commitmentBytes)
	clear(commitmentBytes)

	lowerBound := conservativeSearchSpace(len(alphabet), int(spec.Length), required, patterns, alphabetSet)
	threshold := new(big.Int).Lsh(big.NewInt(1), minimumSafeEntropyBits)
	policy := PasswordPolicy{
		length:            int(spec.Length),
		alphabet:          append([]rune(nil), alphabet...),
		requiredClasses:   required,
		forbiddenPatterns: patterns,
		entropyLowerBound: lowerBound,
		entropyBits:       log2BigInt(lowerBound),
		highRisk:          lowerBound.Cmp(threshold) < 0,
		hash:              policyHash,
	}
	return policy, nil
}

func runeSet(symbols []rune) map[rune]struct{} {
	result := make(map[rune]struct{}, len(symbols))
	for _, symbol := range symbols {
		result[symbol] = struct{}{}
	}
	return result
}

func canonicalRuneSetString(value string) string {
	set := runeSet([]rune(value))
	symbols := make([]rune, 0, len(set))
	for symbol := range set {
		symbols = append(symbols, symbol)
	}
	return sortedRuneString(symbols)
}

func sortedRuneString(symbols []rune) string {
	ordered := append([]rune(nil), symbols...)
	sort.Slice(ordered, func(left, right int) bool { return ordered[left] < ordered[right] })
	return string(ordered)
}

func hasDuplicateRunes(symbols []rune) bool {
	seen := make(map[rune]struct{}, len(symbols))
	for _, symbol := range symbols {
		if _, exists := seen[symbol]; exists {
			return true
		}
		seen[symbol] = struct{}{}
	}
	return false
}

// Length is the number of generated Unicode code points.
func (p PasswordPolicy) Length() int { return p.length }

// AlphabetSize reports the number of equiprobable allowed symbols after
// forbidden characters have been removed.
func (p PasswordPolicy) AlphabetSize() int { return len(p.alphabet) }

// ConservativeEntropyBits is log2 of a lower bound on the number of valid
// candidates. It may deliberately understate entropy when constraints overlap.
func (p PasswordPolicy) ConservativeEntropyBits() float64 { return p.entropyBits }

// HighRisk reports whether the conservative lower bound is below 72 bits.
func (p PasswordPolicy) HighRisk() bool { return p.highRisk }

// Hash returns the SHA-256 PolicyHash commitment by value. Mutating the return
// value cannot change the immutable policy.
func (p PasswordPolicy) Hash() [sha256.Size]byte { return p.hash }

func conservativeSearchSpace(alphabetSize, length int, required []requiredClass, patterns []compiledPattern, alphabetSet map[rune]struct{}) *big.Int {
	base := big.NewInt(int64(alphabetSize))
	total := new(big.Int).Exp(base, big.NewInt(int64(length)), nil)
	invalidUpperBound := new(big.Int)

	for _, class := range required {
		classSize := int64(len(class.characters))
		otherSize := int64(alphabetSize) - classSize
		classInvalid := new(big.Int)
		for count := 0; count < class.minCount; count++ {
			term := new(big.Int).Binomial(int64(length), int64(count))
			term.Mul(term, new(big.Int).Exp(big.NewInt(classSize), big.NewInt(int64(count)), nil))
			term.Mul(term, new(big.Int).Exp(big.NewInt(otherSize), big.NewInt(int64(length-count)), nil))
			classInvalid.Add(classInvalid, term)
		}
		invalidUpperBound.Add(invalidUpperBound, classInvalid)
	}

	for _, pattern := range patterns {
		if len(pattern.symbols) > length || !allRunesAllowed(pattern.symbols, alphabetSet) {
			continue
		}
		positions := int64(length - len(pattern.symbols) + 1)
		patternUpper := new(big.Int).Exp(base, big.NewInt(int64(length-len(pattern.symbols))), nil)
		patternUpper.Mul(patternUpper, big.NewInt(positions))
		invalidUpperBound.Add(invalidUpperBound, patternUpper)
	}

	lowerBound := new(big.Int).Sub(total, invalidUpperBound)
	if lowerBound.Sign() < 0 {
		lowerBound.SetInt64(0)
	}
	return lowerBound
}

func allRunesAllowed(symbols []rune, allowed map[rune]struct{}) bool {
	for _, symbol := range symbols {
		if _, exists := allowed[symbol]; !exists {
			return false
		}
	}
	return true
}

func log2BigInt(value *big.Int) float64 {
	if value == nil || value.Sign() <= 0 {
		return 0
	}
	bitLength := value.BitLen()
	shift := bitLength - 53
	if shift < 0 {
		shift = 0
	}
	top := new(big.Int).Rsh(new(big.Int).Set(value), uint(shift)).Uint64()
	return math.Log2(float64(top)) + float64(shift)
}

// RotationPRF is the only secret-bearing capability PolicyEncode needs. The
// implementation owns Krotate, must compute HMAC-SHA-256 over input, must not
// retain input, and must fail after its key is destroyed. cryptokit.Key is the
// production implementation; deterministic implementations belong in tests.
type RotationPRF interface {
	PolicyHMAC(input []byte) ([sha256.Size]byte, error)
}

// PolicyContext binds every candidate to one credential version, policy,
// campaign, and external site-attempt counter.
type PolicyContext struct {
	credentialID protocol.CredentialID
	newVersion   uint64
	policyHash   [policyHashBytes]byte
	campaignID   protocol.CampaignID
	attemptNo    uint64
}

func NewPolicyContext(credentialID protocol.CredentialID, newVersion uint64, policyHash [policyHashBytes]byte, campaignID protocol.CampaignID, attemptNo uint64) (PolicyContext, error) {
	if newVersion == 0 {
		return PolicyContext{}, ErrInvalidPolicyContext
	}
	return PolicyContext{
		credentialID: credentialID,
		newVersion:   newVersion,
		policyHash:   policyHash,
		campaignID:   campaignID,
		attemptNo:    attemptNo,
	}, nil
}

func (PolicyContext) String() string   { return redactedPolicyContext }
func (PolicyContext) GoString() string { return redactedPolicyContext }
func (PolicyContext) Format(state fmt.State, _ rune) {
	_, _ = io.WriteString(state, redactedPolicyContext)
}
func (PolicyContext) MarshalJSON() ([]byte, error) { return nil, ErrSecretSerialization }

// EncodeResult contains the generated secret plus auditable, non-secret
// generation metadata.
type EncodeResult struct {
	Password                GeneratedPassword
	CandidateCounter        uint16
	ConservativeEntropyBits float64
	HighRisk                bool
}

// PolicyEncode generates a deterministic, uniformly mapped candidate. It
// rejects complete candidates that violate any policy constraint and tries at
// most 1,024 candidate-counter domains.
func PolicyEncode(prf RotationPRF, context PolicyContext, policy PasswordPolicy) (EncodeResult, error) {
	if policy.length == 0 || len(policy.alphabet) == 0 || policy.entropyLowerBound == nil || context.newVersion == 0 {
		return EncodeResult{}, ErrInvalidPasswordPolicy
	}
	if subtle.ConstantTimeCompare(context.policyHash[:], policy.hash[:]) != 1 {
		return EncodeResult{}, ErrPolicyHashMismatch
	}
	if prf == nil {
		return EncodeResult{}, ErrPolicyPRF
	}

	for candidateCounter := uint16(0); candidateCounter < maxPolicyCandidates; candidateCounter++ {
		candidate, err := generateUniformCandidate(prf, context, candidateCounter, policy)
		if err != nil {
			return EncodeResult{}, err
		}
		if !policy.accepts(candidate) {
			clear(candidate)
			continue
		}
		passwordBytes := runesToUTF8(candidate)
		clear(candidate)
		return EncodeResult{
			Password:                newGeneratedPassword(passwordBytes),
			CandidateCounter:        candidateCounter,
			ConservativeEntropyBits: policy.entropyBits,
			HighRisk:                policy.highRisk,
		}, nil
	}
	return EncodeResult{}, ErrNoPolicyCandidate
}

func generateUniformCandidate(prf RotationPRF, context PolicyContext, candidateCounter uint16, policy PasswordPolicy) ([]rune, error) {
	candidate := make([]rune, 0, policy.length)

	for blockNo := uint64(0); len(candidate) < policy.length && blockNo < maxPolicyStreamBlocks; blockNo++ {
		encoded, err := encodePolicyStreamContext(context, candidateCounter, blockNo)
		if err != nil {
			clear(candidate)
			return nil, err
		}
		block, err := prf.PolicyHMAC(encoded)
		clear(encoded)
		if err != nil {
			clear(candidate)
			clear(block[:])
			return nil, ErrPolicyPRF
		}

		for _, raw := range block[:] {
			index, accepted := unbiasedAlphabetIndex(raw, len(policy.alphabet))
			if !accepted {
				continue
			}
			candidate = append(candidate, policy.alphabet[index])
			if len(candidate) == policy.length {
				break
			}
		}
		clear(block[:])
	}
	if len(candidate) != policy.length {
		clear(candidate)
		return nil, ErrNoPolicyCandidate
	}
	return candidate, nil
}

func unbiasedAlphabetIndex(raw byte, alphabetSize int) (int, bool) {
	if alphabetSize < 1 || alphabetSize > 256 {
		return 0, false
	}
	acceptLimit := 256 - (256 % alphabetSize)
	if int(raw) >= acceptLimit {
		return 0, false
	}
	return int(raw) % alphabetSize, true
}

type policyStreamContext struct {
	_                struct{} `cbor:",toarray"`
	CredentialID     []byte
	NewVersion       uint64
	PolicyHash       []byte
	CampaignID       []byte
	AttemptNo        uint64
	CandidateCounter uint16
	BlockNo          uint64
}

func encodePolicyStreamContext(context PolicyContext, candidateCounter uint16, blockNo uint64) ([]byte, error) {
	encoded, err := protocol.MarshalDeterministic(policyStreamContext{
		CredentialID:     context.credentialID[:],
		NewVersion:       context.newVersion,
		PolicyHash:       context.policyHash[:],
		CampaignID:       context.campaignID[:],
		AttemptNo:        context.attemptNo,
		CandidateCounter: candidateCounter,
		BlockNo:          blockNo,
	})
	if err != nil {
		return nil, ErrPolicyEncoding
	}
	return encoded, nil
}

func (p PasswordPolicy) accepts(candidate []rune) bool {
	if len(candidate) != p.length {
		return false
	}
	for _, class := range p.requiredClasses {
		count := 0
		for _, symbol := range candidate {
			if _, present := class.characters[symbol]; present {
				count++
			}
		}
		if count < class.minCount {
			return false
		}
	}
	for _, pattern := range p.forbiddenPatterns {
		if containsRunes(candidate, pattern) {
			return false
		}
	}
	return true
}

func compilePattern(symbols []rune) compiledPattern {
	pattern := compiledPattern{
		symbols: append([]rune(nil), symbols...),
		failure: make([]int, len(symbols)),
	}
	for index, matched := 1, 0; index < len(pattern.symbols); {
		if pattern.symbols[index] == pattern.symbols[matched] {
			matched++
			pattern.failure[index] = matched
			index++
			continue
		}
		if matched > 0 {
			matched = pattern.failure[matched-1]
			continue
		}
		pattern.failure[index] = 0
		index++
	}
	return pattern
}

// containsRunes uses a precomputed KMP failure table, making every forbidden
// pattern check linear in candidate length rather than length×pattern length.
func containsRunes(candidate []rune, pattern compiledPattern) bool {
	if len(pattern.symbols) == 0 || len(pattern.symbols) > len(candidate) {
		return false
	}
	matched := 0
	for _, symbol := range candidate {
		for matched > 0 && symbol != pattern.symbols[matched] {
			matched = pattern.failure[matched-1]
		}
		if symbol == pattern.symbols[matched] {
			matched++
		}
		if matched == len(pattern.symbols) {
			return true
		}
	}
	return false
}

func runesToUTF8(symbols []rune) []byte {
	result := make([]byte, 0, len(symbols)*2)
	for _, symbol := range symbols {
		result = utf8.AppendRune(result, symbol)
	}
	return result
}

// GeneratedPassword is an erasable password value that cannot be formatted or
// serialized by default. Copies share the same underlying state.
type GeneratedPassword struct {
	state *passwordState
}

type passwordState struct {
	mu        sync.RWMutex
	value     []byte
	destroyed bool
}

func newGeneratedPassword(value []byte) GeneratedPassword {
	return GeneratedPassword{state: &passwordState{value: value}}
}

// UseBytes supplies a temporary password copy and erases it after fn returns.
func (p GeneratedPassword) UseBytes(fn func([]byte) error) error {
	if fn == nil || p.state == nil {
		return ErrPasswordDestroyed
	}
	p.state.mu.RLock()
	if p.state.destroyed || len(p.state.value) == 0 {
		p.state.mu.RUnlock()
		return ErrPasswordDestroyed
	}
	value := append([]byte(nil), p.state.value...)
	p.state.mu.RUnlock()
	defer clear(value)
	return fn(value)
}

// EqualBytes compares a live password with expected bytes without disclosing
// the generated value. It is primarily intended for protocol vector checks.
func (p GeneratedPassword) EqualBytes(expected []byte) bool {
	if p.state == nil {
		return false
	}
	p.state.mu.RLock()
	defer p.state.mu.RUnlock()
	return !p.state.destroyed && len(p.state.value) == len(expected) && subtle.ConstantTimeCompare(p.state.value, expected) == 1
}

func (p GeneratedPassword) Destroy() {
	if p.state == nil {
		return
	}
	p.state.mu.Lock()
	defer p.state.mu.Unlock()
	clear(p.state.value)
	p.state.value = nil
	p.state.destroyed = true
}

func (GeneratedPassword) String() string   { return redactedPassword }
func (GeneratedPassword) GoString() string { return redactedPassword }
func (GeneratedPassword) Format(state fmt.State, _ rune) {
	_, _ = io.WriteString(state, redactedPassword)
}
func (GeneratedPassword) LogValue() slog.Value         { return slog.StringValue(redactedPassword) }
func (GeneratedPassword) MarshalJSON() ([]byte, error) { return nil, ErrSecretSerialization }

var (
	_ fmt.Stringer   = PolicyContext{}
	_ fmt.GoStringer = PolicyContext{}
	_ json.Marshaler = PolicyContext{}
	_ fmt.Stringer   = GeneratedPassword{}
	_ fmt.GoStringer = GeneratedPassword{}
	_ slog.LogValuer = GeneratedPassword{}
	_ json.Marshaler = GeneratedPassword{}
)
