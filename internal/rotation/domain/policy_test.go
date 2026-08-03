package domain

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"math"
	"strings"
	"testing"
	"unicode/utf8"

	"vpass.local/vpass/internal/protocol"
)

var errDeterministicPolicyPRF = errors.New("deterministic policy PRF unavailable")

// deterministicPolicyPRF is deliberately test-only. Production code receives
// a cryptokit.Key through the RotationPRF interface and never accepts raw key
// bytes in rotation/domain.
type deterministicPolicyPRF struct {
	key       [sha256.Size]byte
	calls     int
	destroyed bool
	fail      bool
}

func newDeterministicPolicyPRF(seed []byte) *deterministicPolicyPRF {
	prf := &deterministicPolicyPRF{}
	copy(prf.key[:], seed)
	return prf
}

func (prf *deterministicPolicyPRF) PolicyHMAC(input []byte) ([sha256.Size]byte, error) {
	var block [sha256.Size]byte
	if prf == nil || prf.destroyed || prf.fail {
		return block, errDeterministicPolicyPRF
	}
	prf.calls++
	mac := hmac.New(sha256.New, prf.key[:])
	_, _ = mac.Write(input)
	copy(block[:], mac.Sum(nil))
	return block, nil
}

func (prf *deterministicPolicyPRF) Destroy() {
	if prf == nil {
		return
	}
	clear(prf.key[:])
	prf.destroyed = true
}

type constantPolicyPRF struct {
	block [sha256.Size]byte
	calls int
}

func (prf *constantPolicyPRF) PolicyHMAC([]byte) ([sha256.Size]byte, error) {
	prf.calls++
	return prf.block, nil
}

func TestPolicyEncodeFixedVector(t *testing.T) {
	t.Parallel()
	policy := mustPolicy(t, PolicySpec{Length: 16, Alphabet: "abcdefghij"})
	wantPolicyHash, err := hex.DecodeString("eb86d2923b1208c5751ee1e9fb81f33a4d583b27bf7615c53ebc7304cd97b8af")
	if err != nil {
		t.Fatal(err)
	}
	if got := policy.Hash(); !bytes.Equal(got[:], wantPolicyHash) {
		t.Fatalf("PolicyHash = %x, want %x", got, wantPolicyHash)
	}
	prf, context := fixedPolicyInputs(t, policy)
	defer prf.Destroy()

	encoded, err := encodePolicyStreamContext(context, 0, 0)
	if err != nil {
		t.Fatal(err)
	}
	wantContext, err := hex.DecodeString("875820000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f025820eb86d2923b1208c5751ee1e9fb81f33a4d583b27bf7615c53ebc7304cd97b8af5820404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f030000")
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(encoded, wantContext) {
		t.Fatalf("stream context = %x, want %x", encoded, wantContext)
	}
	clear(encoded)

	result, err := PolicyEncode(prf, context, policy)
	if err != nil {
		t.Fatal(err)
	}
	defer result.Password.Destroy()
	if !result.Password.EqualBytes([]byte("cjejbdgdfaaddbcc")) {
		actual := passwordBytesForTest(t, result.Password)
		defer clear(actual)
		t.Fatalf("candidate %q differs from the independent HMAC-SHA256 vector", actual)
	}
	if result.CandidateCounter != 0 {
		t.Fatalf("candidate counter = %d, want 0", result.CandidateCounter)
	}
	if !result.HighRisk || result.ConservativeEntropyBits >= minimumSafeEntropyBits {
		t.Fatal("small fixed-vector policy was not marked high risk")
	}

	again, err := PolicyEncode(prf, context, policy)
	if err != nil {
		t.Fatal(err)
	}
	defer again.Password.Destroy()
	if !again.Password.EqualBytes([]byte("cjejbdgdfaaddbcc")) || again.CandidateCounter != result.CandidateCounter {
		t.Fatal("identical inputs did not produce the same result")
	}
}

func TestPasswordPolicyCommitmentSchemaAndCanonicalization(t *testing.T) {
	t.Parallel()
	base := mustPolicy(t, PolicySpec{
		Length:   12,
		Alphabet: "abAB12!@",
		RequiredClasses: []RequiredClassSpec{
			{Name: "upper", Characters: "BA", MinCount: 1},
			{Name: "lower", Characters: "ba", MinCount: 2},
		},
		ForbiddenCharacters: "@!",
		ForbiddenPatterns:   []string{"ab", "12"},
	})
	want, err := hex.DecodeString("9fd453ed6f3d3330bbc5d105ea99efe29cc2c9461aefbae187d8450788e24004")
	if err != nil {
		t.Fatal(err)
	}
	if got := base.Hash(); !bytes.Equal(got[:], want) {
		t.Fatalf("rich PolicyHash = %x, want %x", got, want)
	}

	// Class/pattern order and set order are semantically irrelevant and are
	// canonicalized; alphabet order is generation semantics and is preserved.
	equivalent := mustPolicy(t, PolicySpec{
		Length:   12,
		Alphabet: "abAB12!@",
		RequiredClasses: []RequiredClassSpec{
			{Name: "lower", Characters: "ab", MinCount: 2},
			{Name: "upper", Characters: "AB", MinCount: 1},
		},
		ForbiddenCharacters: "!@@",
		ForbiddenPatterns:   []string{"12", "ab"},
	})
	if base.Hash() != equivalent.Hash() {
		t.Fatal("semantically equivalent set/order forms changed PolicyHash")
	}
	differentAlphabetOrder := mustPolicy(t, PolicySpec{
		Length:              12,
		Alphabet:            "baAB12!@",
		RequiredClasses:     []RequiredClassSpec{{Name: "lower", Characters: "ab", MinCount: 2}, {Name: "upper", Characters: "AB", MinCount: 1}},
		ForbiddenCharacters: "!@",
		ForbiddenPatterns:   []string{"12", "ab"},
	})
	if base.Hash() == differentAlphabetOrder.Hash() {
		t.Fatal("generation-significant alphabet order was normalized away")
	}

	returned := base.Hash()
	returned[0] ^= 1
	if returned == base.Hash() {
		t.Fatal("Hash() did not return the commitment by value")
	}
	composed := mustPolicy(t, PolicySpec{Length: 8, Alphabet: "éa"})
	decomposed := mustPolicy(t, PolicySpec{Length: 8, Alphabet: "e\u0301a"})
	if composed.Hash() == decomposed.Hash() {
		t.Fatal("byte-exact Unicode policy inputs were unexpectedly normalized")
	}
}

func TestPolicyEncodeBindsEveryContextField(t *testing.T) {
	t.Parallel()
	policy := mustPolicy(t, PolicySpec{
		Length:   24,
		Alphabet: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
	})
	prf, baseContext := fixedPolicyInputs(t, policy)
	defer prf.Destroy()
	base, err := PolicyEncode(prf, baseContext, policy)
	if err != nil {
		t.Fatal(err)
	}
	defer base.Password.Destroy()
	baseBytes := passwordBytesForTest(t, base.Password)
	defer clear(baseBytes)

	credentialID, campaignID := fixedContextIDs()
	policyHash := policy.Hash()
	mutations := []struct {
		name         string
		credentialID protocol.CredentialID
		newVersion   uint64
		policyHash   [32]byte
		campaignID   protocol.CampaignID
		attemptNo    uint64
	}{
		{name: "credential", credentialID: mutateCredentialID(credentialID), newVersion: 2, policyHash: policyHash, campaignID: campaignID, attemptNo: 3},
		{name: "version", credentialID: credentialID, newVersion: 3, policyHash: policyHash, campaignID: campaignID, attemptNo: 3},
		{name: "campaign", credentialID: credentialID, newVersion: 2, policyHash: policyHash, campaignID: mutateCampaignID(campaignID), attemptNo: 3},
		{name: "site attempt", credentialID: credentialID, newVersion: 2, policyHash: policyHash, campaignID: campaignID, attemptNo: 4},
	}

	for _, mutation := range mutations {
		mutation := mutation
		t.Run(mutation.name, func(t *testing.T) {
			context, err := NewPolicyContext(mutation.credentialID, mutation.newVersion, mutation.policyHash, mutation.campaignID, mutation.attemptNo)
			if err != nil {
				t.Fatal(err)
			}
			result, err := PolicyEncode(prf, context, policy)
			if err != nil {
				t.Fatal(err)
			}
			defer result.Password.Destroy()
			if result.Password.EqualBytes(baseBytes) {
				t.Fatal("context mutation did not change the candidate")
			}
		})
	}
}

func TestPolicyEncodeRejectsMismatchedCommittedPolicyHash(t *testing.T) {
	t.Parallel()
	policy := mustPolicy(t, PolicySpec{Length: 16, Alphabet: "abcdefghij"})
	prf, _ := fixedPolicyInputs(t, policy)
	defer prf.Destroy()
	credentialID, campaignID := fixedContextIDs()
	wrongHash := mutatePolicyHash(policy.Hash())
	context, err := NewPolicyContext(credentialID, 2, wrongHash, campaignID, 3)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := PolicyEncode(prf, context, policy); !errors.Is(err, ErrPolicyHashMismatch) {
		t.Fatalf("PolicyEncode() error = %v, want ErrPolicyHashMismatch", err)
	}
	if prf.calls != 0 {
		t.Fatalf("mismatched policy reached secret PRF %d times", prf.calls)
	}
}

func TestPolicyEncodeRejectsMissingOrFailedPRF(t *testing.T) {
	t.Parallel()
	policy := mustPolicy(t, PolicySpec{Length: 16, Alphabet: "abcdefghij"})
	prf, context := fixedPolicyInputs(t, policy)
	defer prf.Destroy()
	if _, err := PolicyEncode(nil, context, policy); !errors.Is(err, ErrPolicyPRF) {
		t.Fatalf("nil PRF error = %v, want ErrPolicyPRF", err)
	}
	prf.fail = true
	if _, err := PolicyEncode(prf, context, policy); !errors.Is(err, ErrPolicyPRF) {
		t.Fatalf("failed PRF error = %v, want ErrPolicyPRF", err)
	}
}

func TestPolicyEncodeRejectsWholeCandidateAndSatisfiesConstraints(t *testing.T) {
	t.Parallel()
	policy := mustPolicy(t, PolicySpec{
		Length:              4,
		Alphabet:            "ab!",
		RequiredClasses:     []RequiredClassSpec{{Name: "only-a", Characters: "a", MinCount: 4}},
		ForbiddenCharacters: "!",
	})
	prf, context := fixedPolicyInputs(t, policy)
	defer prf.Destroy()
	result, err := PolicyEncode(prf, context, policy)
	if err != nil {
		t.Fatal(err)
	}
	defer result.Password.Destroy()
	if !result.Password.EqualBytes([]byte("aaaa")) {
		t.Fatal("accepted candidate does not satisfy the required class")
	}
	// The independently checked vector first reaches "aaaa" in candidate
	// domain 28. This proves the implementation rejects complete candidates
	// instead of repairing characters in candidate domain 0.
	if result.CandidateCounter != 28 {
		t.Fatalf("candidate counter = %d, want 28", result.CandidateCounter)
	}
}

func TestPolicyEncodeRequiredClassesAndForbiddenPatterns(t *testing.T) {
	t.Parallel()
	policy := mustPolicy(t, PolicySpec{
		Length:   24,
		Alphabet: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
		RequiredClasses: []RequiredClassSpec{
			{Name: "lower", Characters: "abcdefghijklmnopqrstuvwxyz", MinCount: 2},
			{Name: "upper", Characters: "ABCDEFGHIJKLMNOPQRSTUVWXYZ", MinCount: 2},
			{Name: "digit", Characters: "0123456789", MinCount: 2},
			{Name: "symbol", Characters: "!@#$%^&*", MinCount: 2},
		},
		ForbiddenCharacters: "@",
		ForbiddenPatterns:   []string{"password", "1234", "AAAA"},
	})
	prf, context := fixedPolicyInputs(t, policy)
	defer prf.Destroy()
	result, err := PolicyEncode(prf, context, policy)
	if err != nil {
		t.Fatal(err)
	}
	defer result.Password.Destroy()
	password := passwordBytesForTest(t, result.Password)
	defer clear(password)
	if !utf8.Valid(password) || !policy.accepts(bytes.Runes(password)) {
		t.Fatal("PolicyEncode returned a candidate outside the compiled policy")
	}
	if bytes.ContainsRune(password, '@') {
		t.Fatal("candidate contains a forbidden character")
	}
	if result.HighRisk || result.ConservativeEntropyBits < minimumSafeEntropyBits {
		t.Fatalf("strong policy unexpectedly high risk (lower bound %.2f bits)", result.ConservativeEntropyBits)
	}
}

func TestPolicyEncodeStopsAfter1024RejectedCandidates(t *testing.T) {
	t.Parallel()
	policy := mustPolicy(t, PolicySpec{
		Length:            1,
		Alphabet:          "ab",
		ForbiddenPatterns: []string{"a", "b"},
	})
	prf, context := fixedPolicyInputs(t, policy)
	defer prf.Destroy()
	result, err := PolicyEncode(prf, context, policy)
	result.Password.Destroy()
	if !errors.Is(err, ErrNoPolicyCandidate) {
		t.Fatalf("PolicyEncode() error = %v, want ErrNoPolicyCandidate", err)
	}
	if prf.calls != maxPolicyCandidates {
		t.Fatalf("PRF calls = %d, want exactly %d candidate domains", prf.calls, maxPolicyCandidates)
	}
}

func TestPolicyEncodeCapsRejectedStreamBlocksAt8192(t *testing.T) {
	t.Parallel()
	alphabetRunes := make([]rune, 129)
	for index := range alphabetRunes {
		alphabetRunes[index] = rune(0x1000 + index)
	}
	policy := mustPolicy(t, PolicySpec{Length: 1, Alphabet: string(alphabetRunes)})
	credentialID, campaignID := fixedContextIDs()
	context, err := NewPolicyContext(credentialID, 2, policy.Hash(), campaignID, 3)
	if err != nil {
		t.Fatal(err)
	}
	prf := &constantPolicyPRF{}
	for index := range prf.block {
		prf.block[index] = 0xff // rejected for a 129-symbol alphabet
	}
	if _, err := PolicyEncode(prf, context, policy); !errors.Is(err, ErrNoPolicyCandidate) {
		t.Fatalf("PolicyEncode() error = %v, want ErrNoPolicyCandidate", err)
	}
	if prf.calls != maxPolicyStreamBlocks {
		t.Fatalf("PRF calls = %d, want stream cap %d", prf.calls, maxPolicyStreamBlocks)
	}
}

func TestPolicyEntropyBoundaryIsConservative(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name     string
		length   uint16
		wantRisk bool
		wantBits float64
	}{
		{name: "below threshold", length: 71, wantRisk: true, wantBits: 71},
		{name: "exact threshold", length: 72, wantRisk: false, wantBits: 72},
		{name: "above threshold", length: 73, wantRisk: false, wantBits: 73},
	}
	for _, test := range tests {
		policy := mustPolicy(t, PolicySpec{Length: test.length, Alphabet: "ab"})
		if policy.HighRisk() != test.wantRisk {
			t.Fatalf("%s: HighRisk() = %v", test.name, policy.HighRisk())
		}
		if math.Abs(policy.ConservativeEntropyBits()-test.wantBits) > 1e-9 {
			t.Fatalf("%s: entropy = %.6f, want %.6f", test.name, policy.ConservativeEntropyBits(), test.wantBits)
		}
	}

	// Subtracting a forbidden-pattern union bound can only lower the reported
	// entropy; it must never claim the unconstrained search space.
	unconstrained := mustPolicy(t, PolicySpec{Length: 40, Alphabet: "abcdefghij"})
	constrained := mustPolicy(t, PolicySpec{Length: 40, Alphabet: "abcdefghij", ForbiddenPatterns: []string{"abc", "def"}})
	if constrained.ConservativeEntropyBits() >= unconstrained.ConservativeEntropyBits() {
		t.Fatal("forbidden patterns did not reduce the conservative lower bound")
	}
}

func TestPolicyRejectionSamplingDistribution(t *testing.T) {
	// Ten symbols do not divide the 256 possible source-byte values. A direct
	// byte modulo mapping would overrepresent symbols 0..5. The deterministic
	// sample below is large enough to distinguish that bias while remaining a
	// stable, non-probabilistic test vector.
	policy := mustPolicy(t, PolicySpec{Length: 512, Alphabet: "abcdefghij"})
	prf, _ := fixedPolicyInputs(t, policy)
	defer prf.Destroy()
	credentialID, campaignID := fixedContextIDs()
	policyHash := policy.Hash()
	counts := make([]int, 10)
	total := 0
	for attempt := uint64(0); attempt < 128; attempt++ {
		context, err := NewPolicyContext(credentialID, 2, policyHash, campaignID, attempt)
		if err != nil {
			t.Fatal(err)
		}
		result, err := PolicyEncode(prf, context, policy)
		if err != nil {
			t.Fatal(err)
		}
		value := passwordBytesForTest(t, result.Password)
		result.Password.Destroy()
		for _, symbol := range value {
			counts[int(symbol-'a')]++
			total++
		}
		clear(value)
	}

	expected := float64(total) / float64(len(counts))
	chiSquared := 0.0
	for _, count := range counts {
		difference := float64(count) - expected
		chiSquared += difference * difference / expected
	}
	if chiSquared >= 35.0 {
		t.Fatalf("rejection-sampled distribution failed fixed chi-square bound: %.3f", chiSquared)
	}
}

func TestPolicyByteMappingExhaustivelyRejectsModuloBias(t *testing.T) {
	counts := make([]int, 10)
	rejected := 0
	for value := 0; value < 256; value++ {
		index, accepted := unbiasedAlphabetIndex(byte(value), len(counts))
		if !accepted {
			rejected++
			continue
		}
		if index < 0 || index >= len(counts) {
			t.Fatalf("mapped byte %d outside alphabet: %d", value, index)
		}
		counts[index]++
	}
	if rejected != 6 {
		t.Fatalf("rejected bytes = %d, want 6 (250..255)", rejected)
	}
	for index, count := range counts {
		if count != 25 {
			t.Fatalf("alphabet index %d count = %d, want 25", index, count)
		}
	}

	for value := 0; value < 256; value++ {
		index, accepted := unbiasedAlphabetIndex(byte(value), 256)
		if !accepted || index != value {
			t.Fatalf("256-symbol mapping changed byte %d: index=%d accepted=%v", value, index, accepted)
		}
	}
	if _, accepted := unbiasedAlphabetIndex(0, 0); accepted {
		t.Fatal("zero-size alphabet was accepted")
	}
}

func TestUnicodePolicyCountsSymbolsNotBytes(t *testing.T) {
	t.Parallel()
	policy := mustPolicy(t, PolicySpec{
		Length:          12,
		Alphabet:        "甲乙丙丁",
		RequiredClasses: []RequiredClassSpec{{Name: "first-pair", Characters: "甲乙", MinCount: 1}},
	})
	prf, context := fixedPolicyInputs(t, policy)
	defer prf.Destroy()
	result, err := PolicyEncode(prf, context, policy)
	if err != nil {
		t.Fatal(err)
	}
	defer result.Password.Destroy()
	value := passwordBytesForTest(t, result.Password)
	defer clear(value)
	if !utf8.Valid(value) || utf8.RuneCount(value) != 12 || !policy.accepts(bytes.Runes(value)) {
		t.Fatal("Unicode policy length or constraints were not preserved")
	}
}

func TestNewPasswordPolicyRejectsMalformedSpecifications(t *testing.T) {
	t.Parallel()
	tooManySymbols := make([]rune, 257)
	for i := range tooManySymbols {
		tooManySymbols[i] = rune(0x1000 + i)
	}
	invalidUTF8 := string([]byte{0xff})
	tests := []PolicySpec{
		{},
		{Length: 1025, Alphabet: "ab"},
		{Length: 8, Alphabet: ""},
		{Length: 8, Alphabet: "aabc"},
		{Length: 8, Alphabet: string(tooManySymbols)},
		{Length: 8, Alphabet: invalidUTF8},
		{Length: 8, Alphabet: "ab", ForbiddenCharacters: "ab"},
		{Length: 8, Alphabet: "ab", RequiredClasses: []RequiredClassSpec{{Name: "", Characters: "a", MinCount: 1}}},
		{Length: 8, Alphabet: "ab", RequiredClasses: []RequiredClassSpec{{Name: "a", Characters: "a", MinCount: 0}}},
		{Length: 8, Alphabet: "ab", RequiredClasses: []RequiredClassSpec{{Name: "a", Characters: "a", MinCount: 9}}},
		{Length: 8, Alphabet: "ab", RequiredClasses: []RequiredClassSpec{{Name: "a", Characters: "aa", MinCount: 1}}},
		{Length: 8, Alphabet: "ab", RequiredClasses: []RequiredClassSpec{{Name: "c", Characters: "c", MinCount: 1}}},
		{Length: 8, Alphabet: "ab", ForbiddenCharacters: "a", RequiredClasses: []RequiredClassSpec{{Name: "a", Characters: "a", MinCount: 1}}},
		{Length: 8, Alphabet: "ab", RequiredClasses: []RequiredClassSpec{{Name: "same", Characters: "a", MinCount: 1}, {Name: "same", Characters: "b", MinCount: 1}}},
		{Length: 8, Alphabet: "ab", ForbiddenPatterns: []string{""}},
		{Length: 8, Alphabet: "ab", ForbiddenPatterns: []string{"a", "a"}},
		{Length: 8, Alphabet: "ab", ForbiddenPatterns: []string{invalidUTF8}},
	}
	for index, spec := range tests {
		if policy, err := NewPasswordPolicy(spec); !errors.Is(err, ErrInvalidPasswordPolicy) {
			_ = policy
			t.Fatalf("case %d error = %v, want ErrInvalidPasswordPolicy", index, err)
		}
	}
}

func TestPasswordPolicyResourceLimits(t *testing.T) {
	t.Parallel()
	requiredTooMany := make([]RequiredClassSpec, maxRequiredClasses+1)
	for index := range requiredTooMany {
		requiredTooMany[index] = RequiredClassSpec{Name: fmt.Sprintf("class-%02d", index), Characters: "a", MinCount: 1}
	}
	patternsTooMany := make([]string, maxForbiddenPatterns+1)
	for index := range patternsTooMany {
		patternsTooMany[index] = fmt.Sprintf("pattern-%02d", index)
	}

	largeClassRunes := make([]rune, maxPolicyItemRunes)
	for index := range largeClassRunes {
		largeClassRunes[index] = rune(0x1000 + index)
	}
	largeAlphabet := string(largeClassRunes)
	totalClasses := make([]RequiredClassSpec, 9) // 9*256 > total-rune cap.
	for index := range totalClasses {
		totalClasses[index] = RequiredClassSpec{Name: fmt.Sprintf("total-%02d", index), Characters: largeAlphabet, MinCount: 1}
	}
	totalPatterns := make([]string, maxForbiddenPatterns)
	for index := range totalPatterns {
		totalPatterns[index] = fmt.Sprintf("%02d%s", index, strings.Repeat("a", 63))
	}

	tests := []PolicySpec{
		{Length: 8, Alphabet: "ab", RequiredClasses: requiredTooMany},
		{Length: 8, Alphabet: "ab", ForbiddenPatterns: patternsTooMany},
		{Length: 8, Alphabet: "ab", RequiredClasses: []RequiredClassSpec{{Name: strings.Repeat("n", maxPolicyNameBytes+1), Characters: "a", MinCount: 1}}},
		{Length: 8, Alphabet: "ab", ForbiddenCharacters: strings.Repeat("a", maxPolicySetRunes+1)},
		{Length: 8, Alphabet: "ab", ForbiddenPatterns: []string{strings.Repeat("a", maxPolicyItemRunes+1)}},
		{Length: 8, Alphabet: largeAlphabet, RequiredClasses: totalClasses},
		{Length: 8, Alphabet: "ab", ForbiddenPatterns: totalPatterns},
	}
	for index, spec := range tests {
		if _, err := NewPasswordPolicy(spec); !errors.Is(err, ErrInvalidPasswordPolicy) {
			t.Fatalf("resource case %d error = %v, want ErrInvalidPasswordPolicy", index, err)
		}
	}
}

func TestCompiledForbiddenPatternHandlesOverlaps(t *testing.T) {
	t.Parallel()
	pattern := compilePattern([]rune("ababaca"))
	if !containsRunes([]rune("zzabababacayy"), pattern) {
		t.Fatal("KMP matcher missed an overlapping pattern")
	}
	if containsRunes([]rune("zzabababaxayy"), pattern) {
		t.Fatal("KMP matcher accepted a non-match")
	}
}

func TestPolicySecretsDoNotFormatOrSerialize(t *testing.T) {
	t.Parallel()
	policy := mustPolicy(t, PolicySpec{Length: 16, Alphabet: "abcdefghij"})
	prf, context := fixedPolicyInputs(t, policy)
	result, err := PolicyEncode(prf, context, policy)
	if err != nil {
		t.Fatal(err)
	}
	defer result.Password.Destroy()

	for _, value := range []any{context, result.Password} {
		for _, rendered := range []string{
			fmt.Sprintf("%s", value),
			fmt.Sprintf("%v", value),
			fmt.Sprintf("%+v", value),
			fmt.Sprintf("%#v", value),
			fmt.Sprintf("%q", value),
		} {
			if strings.Contains(rendered, "dfdbafbbdbfifbfe") || strings.Contains(rendered, "[0 1 2 3") {
				t.Fatalf("secret appeared in formatted output: %q", rendered)
			}
		}
		encoded, err := json.Marshal(value)
		if err == nil {
			t.Fatal("secret JSON serialization unexpectedly succeeded")
		}
		if bytes.Contains(encoded, []byte("dfdbafbbdbfifbfe")) || strings.Contains(err.Error(), "dfdbafbbdbfifbfe") {
			t.Fatal("secret appeared in JSON output or error")
		}
	}

	prf.Destroy()
	if _, err := PolicyEncode(prf, context, policy); !errors.Is(err, ErrPolicyPRF) {
		t.Fatalf("use after PRF destruction error = %v", err)
	}
	copyOfPassword := result.Password
	result.Password.Destroy()
	if err := copyOfPassword.UseBytes(func([]byte) error { return nil }); !errors.Is(err, ErrPasswordDestroyed) {
		t.Fatalf("use after password destruction error = %v", err)
	}
}

func TestPolicyContextValidation(t *testing.T) {
	t.Parallel()
	credentialID, campaignID := fixedContextIDs()
	policyHash := mustPolicy(t, PolicySpec{Length: 8, Alphabet: "ab"}).Hash()
	if _, err := NewPolicyContext(credentialID, 0, policyHash, campaignID, 0); !errors.Is(err, ErrInvalidPolicyContext) {
		t.Fatal("zero version accepted")
	}
}

func fixedPolicyInputs(t *testing.T, policy PasswordPolicy) (*deterministicPolicyPRF, PolicyContext) {
	t.Helper()
	keyBytes := make([]byte, 32)
	for i := range keyBytes {
		keyBytes[i] = byte(i)
	}
	prf := newDeterministicPolicyPRF(keyBytes)
	clear(keyBytes)
	credentialID, campaignID := fixedContextIDs()
	context, err := NewPolicyContext(credentialID, 2, policy.Hash(), campaignID, 3)
	if err != nil {
		prf.Destroy()
		t.Fatal(err)
	}
	return prf, context
}

func fixedContextIDs() (credentialID protocol.CredentialID, campaignID protocol.CampaignID) {
	for i := range credentialID {
		credentialID[i] = byte(i)
	}
	for i := range campaignID {
		campaignID[i] = byte(0x40 + i)
	}
	return credentialID, campaignID
}

func mustPolicy(t *testing.T, spec PolicySpec) PasswordPolicy {
	t.Helper()
	policy, err := NewPasswordPolicy(spec)
	if err != nil {
		t.Fatalf("NewPasswordPolicy() error = %v", err)
	}
	return policy
}

func passwordBytesForTest(t *testing.T, password GeneratedPassword) []byte {
	t.Helper()
	var result []byte
	if err := password.UseBytes(func(value []byte) error {
		result = append([]byte(nil), value...)
		return nil
	}); err != nil {
		t.Fatalf("UseBytes() error = %v", err)
	}
	return result
}

func mutateCredentialID(input protocol.CredentialID) protocol.CredentialID {
	input[0] ^= 1
	return input
}

func mutatePolicyHash(input [32]byte) [32]byte {
	input[0] ^= 1
	return input
}

func mutateCampaignID(input protocol.CampaignID) protocol.CampaignID {
	input[0] ^= 1
	return input
}

func FuzzNewPasswordPolicy(f *testing.F) {
	f.Add(uint16(16), "abcABC123!", "!", "abc")
	f.Add(uint16(1), "ab", "", "a")
	f.Add(uint16(0), "", "", "")
	f.Fuzz(func(t *testing.T, length uint16, alphabet, forbiddenChars, forbiddenPattern string) {
		patterns := []string(nil)
		if forbiddenPattern != "" {
			patterns = []string{forbiddenPattern}
		}
		policy, err := NewPasswordPolicy(PolicySpec{
			Length:              length,
			Alphabet:            alphabet,
			ForbiddenCharacters: forbiddenChars,
			ForbiddenPatterns:   patterns,
		})
		if err != nil {
			return
		}
		if policy.Length() < 1 || policy.Length() > maxPasswordSymbols || policy.AlphabetSize() < 1 || policy.AlphabetSize() > 256 || math.IsNaN(policy.ConservativeEntropyBits()) {
			t.Fatal("successful policy violated compiled invariants")
		}
	})
}

func FuzzPolicyEncode(f *testing.F) {
	f.Add([]byte("seed"), uint8(16), uint8(10), uint64(0))
	f.Add([]byte("another seed"), uint8(1), uint8(2), uint64(7))
	f.Add([]byte{}, uint8(64), uint8(70), ^uint64(0))
	f.Fuzz(func(t *testing.T, seed []byte, rawLength, rawAlphabetSize uint8, attempt uint64) {
		length := uint16(rawLength%64 + 1)
		alphabetSize := int(rawAlphabetSize%94 + 1)
		const printable = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
		policy, err := NewPasswordPolicy(PolicySpec{Length: length, Alphabet: printable[:alphabetSize]})
		if err != nil {
			t.Fatal(err)
		}

		keyDigest := sha256.Sum256(append([]byte("key"), seed...))
		credentialDigest := sha256.Sum256(append([]byte("credential"), seed...))
		campaignDigest := sha256.Sum256(append([]byte("campaign"), seed...))
		prf := newDeterministicPolicyPRF(keyDigest[:])
		defer prf.Destroy()
		credentialID, err := protocol.CredentialIDFromBytes(credentialDigest[:protocol.CredentialIDSize])
		if err != nil {
			t.Fatal(err)
		}
		campaignID, err := protocol.CampaignIDFromBytes(campaignDigest[:])
		if err != nil {
			t.Fatal(err)
		}
		context, err := NewPolicyContext(credentialID, 1, policy.Hash(), campaignID, attempt)
		if err != nil {
			t.Fatal(err)
		}

		first, err := PolicyEncode(prf, context, policy)
		if err != nil {
			t.Fatal(err)
		}
		defer first.Password.Destroy()
		second, err := PolicyEncode(prf, context, policy)
		if err != nil {
			t.Fatal(err)
		}
		defer second.Password.Destroy()
		firstBytes := passwordBytesForTest(t, first.Password)
		defer clear(firstBytes)
		if !second.Password.EqualBytes(firstBytes) || utf8.RuneCount(firstBytes) != int(length) {
			t.Fatal("PolicyEncode was non-deterministic or returned the wrong symbol length")
		}
	})
}
