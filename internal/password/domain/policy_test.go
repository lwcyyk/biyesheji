package domain

import (
	"bytes"
	"encoding/hex"
	"errors"
	"io"
	"strings"
	"testing"
)

func TestPasswordPolicyCanonicalHashAndRoundTripKAT(t *testing.T) {
	t.Parallel()
	policy, err := NewPasswordPolicy(PasswordPolicyConfig{
		Version: 7, MinimumLength: 12, MaximumLength: 64, DefaultLength: 20,
		AllowLowercase: true, AllowUppercase: true, AllowDigits: true,
		AllowedSymbols:   "@!!#",
		MinimumLowercase: 1, MinimumUppercase: 1, MinimumDigits: 2, MinimumSymbols: 2,
		ForbiddenCharacters: "`'\"",
	})
	if err != nil {
		t.Fatal(err)
	}
	const wantHash = "7478443deb886a9868c5409152102b4d7060a1120bd7231879d8c15a231985ea"
	hash := policy.Hash()
	if got := hex.EncodeToString(hash[:]); got != wantHash {
		t.Fatalf("policy hash KAT = %s", got)
	}
	if policy.Config().AllowedSymbols != "!#@" ||
		policy.Config().ForbiddenCharacters != "\"'`" {
		t.Fatal("policy characters were not canonicalized")
	}
	encoded, err := policy.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	parsed, err := ParsePasswordPolicy(encoded)
	if err != nil || parsed.Hash() != hash {
		t.Fatalf("policy round trip = %#v, %v", parsed, err)
	}
}

func TestPasswordPolicyRejectsImpossibleConstraints(t *testing.T) {
	t.Parallel()
	valid := PasswordPolicyConfig{
		Version: 1, MinimumLength: 12, MaximumLength: 32, DefaultLength: 20,
		AllowLowercase: true, MinimumLowercase: 1,
	}
	tests := []func(*PasswordPolicyConfig){
		func(value *PasswordPolicyConfig) { value.Version = 0 },
		func(value *PasswordPolicyConfig) { value.MinimumLength = 11 },
		func(value *PasswordPolicyConfig) { value.MaximumLength = 257 },
		func(value *PasswordPolicyConfig) { value.DefaultLength = 40 },
		func(value *PasswordPolicyConfig) { value.AllowLowercase = false },
		func(value *PasswordPolicyConfig) { value.MinimumLowercase = 13 },
		func(value *PasswordPolicyConfig) {
			value.AllowedSymbols = "a"
			value.MinimumSymbols = 1
		},
		func(value *PasswordPolicyConfig) {
			value.ForbiddenCharacters = lowercaseAlphabet
		},
	}
	for index, mutate := range tests {
		config := valid
		mutate(&config)
		if _, err := NewPasswordPolicy(config); !errors.Is(err, ErrInvalidPasswordPolicy) {
			t.Fatalf("invalid policy %d error = %v", index, err)
		}
	}
}

func TestPasswordGeneratorSatisfiesPolicyAndForbiddenCharacters(t *testing.T) {
	t.Parallel()
	policy, err := NewPasswordPolicy(PasswordPolicyConfig{
		Version: 1, MinimumLength: 16, MaximumLength: 32, DefaultLength: 24,
		AllowLowercase: true, AllowUppercase: true, AllowDigits: true,
		AllowedSymbols:   "!@#$%",
		MinimumLowercase: 3, MinimumUppercase: 3, MinimumDigits: 3, MinimumSymbols: 3,
		ForbiddenCharacters: "0OolI1!",
	})
	if err != nil {
		t.Fatal(err)
	}
	entropy := &cyclingReader{}
	for iteration := 0; iteration < 1000; iteration++ {
		generated, err := generatePasswordBytes(policy, 24, entropy)
		if err != nil {
			t.Fatal(err)
		}
		if len(generated) != 24 || !policyAcceptsBytes(policy, generated) ||
			strings.ContainsAny(string(generated), policy.Config().ForbiddenCharacters) {
			t.Fatalf("generated password violates policy")
		}
		clear(generated)
	}
	secret, err := GeneratePassword(policy, 0)
	if err != nil {
		t.Fatal(err)
	}
	if secret.Len() != policy.Config().DefaultLength {
		t.Fatal("public generator ignored default length")
	}
	secret.Destroy()
}

func TestUnbiasedIndexUsesRejectionSampling(t *testing.T) {
	t.Parallel()
	// 252 is the largest multiple of six below 256. Values 252..255 must be
	// rejected, leaving exactly equal buckets over complete byte cycles.
	reader := &cyclingReader{}
	counts := make([]int, 6)
	for sample := 0; sample < 6000; sample++ {
		index, err := unbiasedIndex(reader, len(counts))
		if err != nil {
			t.Fatal(err)
		}
		counts[index]++
	}
	for index, count := range counts {
		if count != 1000 {
			t.Fatalf("bucket %d = %d, want 1000", index, count)
		}
	}
	rejectForever := bytes.NewReader(bytes.Repeat([]byte{0xff}, 4096))
	if _, err := unbiasedIndex(rejectForever, 3); !errors.Is(err, ErrPasswordGeneration) {
		t.Fatalf("rejection bound error = %v", err)
	}
}

func TestPasswordGeneratorRejectsLengthAndEntropyFailure(t *testing.T) {
	t.Parallel()
	policy, _ := DefaultPasswordPolicy(1)
	if generated, err := generatePasswordBytes(
		policy, 11, bytes.NewReader(nil),
	); generated != nil || !errors.Is(err, ErrPasswordGeneration) {
		t.Fatalf("short request = %q, %v", generated, err)
	}
	if generated, err := generatePasswordBytes(
		policy, 20, io.LimitReader(bytes.NewReader([]byte{1}), 1),
	); generated != nil || !errors.Is(err, ErrPasswordGeneration) {
		t.Fatalf("entropy failure = %q, %v", generated, err)
	}
}

func FuzzPasswordPolicyParse(f *testing.F) {
	policy, _ := DefaultPasswordPolicy(1)
	encoded, _ := policy.MarshalBinary()
	f.Add(encoded)
	f.Add([]byte{0xa0})
	f.Fuzz(func(t *testing.T, input []byte) {
		parsed, err := ParsePasswordPolicy(input)
		if err == nil {
			canonical, marshalErr := parsed.MarshalBinary()
			if marshalErr != nil || !bytes.Equal(canonical, input) {
				t.Fatal("accepted non-canonical policy")
			}
		}
	})
}

type cyclingReader struct {
	next byte
}

func (reader *cyclingReader) Read(output []byte) (int, error) {
	for index := range output {
		output[index] = reader.next
		reader.next++
	}
	return len(output), nil
}
