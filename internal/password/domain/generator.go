package domain

import (
	"crypto/rand"
	"errors"
	"io"
	"strings"

	"vpass.local/vpass/internal/cryptokit"
)

var ErrPasswordGeneration = errors.New("password generation failed")

// GeneratePassword uses the OS CSPRNG and unbiased rejection sampling.
func GeneratePassword(
	policy *PasswordPolicy,
	requestedLength int,
) (*cryptokit.Secret, error) {
	generated, err := generatePasswordBytes(policy, requestedLength, rand.Reader)
	if err != nil {
		return nil, err
	}
	defer clear(generated)
	secret, err := cryptokit.NewSecret(generated)
	if err != nil {
		return nil, ErrPasswordGeneration
	}
	return secret, nil
}

func generatePasswordBytes(
	policy *PasswordPolicy,
	requestedLength int,
	random io.Reader,
) ([]byte, error) {
	if policy == nil || random == nil || validatePolicyConfig(policy.config) != nil {
		return nil, ErrPasswordGeneration
	}
	config := policy.config
	length := requestedLength
	if length == 0 {
		length = config.DefaultLength
	}
	if length < config.MinimumLength || length > config.MaximumLength {
		return nil, ErrPasswordGeneration
	}
	forbidden := config.ForbiddenCharacters
	lower := removeForbidden(lowercaseAlphabet, forbidden)
	upper := removeForbidden(uppercaseAlphabet, forbidden)
	digits := removeForbidden(digitAlphabet, forbidden)
	symbols := removeForbidden(config.AllowedSymbols, forbidden)
	classes := []struct {
		alphabet string
		minimum  int
		allowed  bool
	}{
		{lower, config.MinimumLowercase, config.AllowLowercase},
		{upper, config.MinimumUppercase, config.AllowUppercase},
		{digits, config.MinimumDigits, config.AllowDigits},
		{symbols, config.MinimumSymbols, symbols != ""},
	}
	required := 0
	var combined strings.Builder
	for _, class := range classes {
		if class.minimum < 0 || class.minimum > length ||
			(class.minimum > 0 && (!class.allowed || class.alphabet == "")) {
			return nil, ErrPasswordGeneration
		}
		required += class.minimum
		if class.allowed {
			combined.WriteString(class.alphabet)
		}
	}
	if required > length || combined.Len() == 0 || combined.Len() > 256 {
		return nil, ErrPasswordGeneration
	}

	output := make([]byte, 0, length)
	for _, class := range classes {
		for count := 0; count < class.minimum; count++ {
			value, err := unbiasedCharacter(random, class.alphabet)
			if err != nil {
				clear(output)
				return nil, ErrPasswordGeneration
			}
			output = append(output, value)
		}
	}
	alphabet := canonicalCharacters(combined.String())
	for len(output) < length {
		value, err := unbiasedCharacter(random, alphabet)
		if err != nil {
			clear(output)
			return nil, ErrPasswordGeneration
		}
		output = append(output, value)
	}
	for index := len(output) - 1; index > 0; index-- {
		swap, err := unbiasedIndex(random, index+1)
		if err != nil {
			clear(output)
			return nil, ErrPasswordGeneration
		}
		output[index], output[swap] = output[swap], output[index]
	}
	if !policyAcceptsBytes(policy, output) {
		clear(output)
		return nil, ErrPasswordGeneration
	}
	return output, nil
}

func policyAcceptsBytes(policy *PasswordPolicy, candidate []byte) bool {
	if policy == nil || validatePolicyConfig(policy.config) != nil ||
		len(candidate) < policy.config.MinimumLength ||
		len(candidate) > policy.config.MaximumLength {
		return false
	}
	config := policy.config
	counts := [4]int{}
	allowed := ""
	if config.AllowLowercase {
		allowed += removeForbidden(lowercaseAlphabet, config.ForbiddenCharacters)
	}
	if config.AllowUppercase {
		allowed += removeForbidden(uppercaseAlphabet, config.ForbiddenCharacters)
	}
	if config.AllowDigits {
		allowed += removeForbidden(digitAlphabet, config.ForbiddenCharacters)
	}
	allowed += removeForbidden(config.AllowedSymbols, config.ForbiddenCharacters)
	for _, value := range candidate {
		if !strings.ContainsRune(allowed, rune(value)) {
			return false
		}
		switch {
		case strings.ContainsRune(lowercaseAlphabet, rune(value)):
			counts[0]++
		case strings.ContainsRune(uppercaseAlphabet, rune(value)):
			counts[1]++
		case strings.ContainsRune(digitAlphabet, rune(value)):
			counts[2]++
		case strings.ContainsRune(config.AllowedSymbols, rune(value)):
			counts[3]++
		default:
			return false
		}
	}
	return counts[0] >= config.MinimumLowercase &&
		counts[1] >= config.MinimumUppercase &&
		counts[2] >= config.MinimumDigits &&
		counts[3] >= config.MinimumSymbols
}

func unbiasedCharacter(random io.Reader, alphabet string) (byte, error) {
	if len(alphabet) == 0 || len(alphabet) > 256 {
		return 0, ErrPasswordGeneration
	}
	index, err := unbiasedIndex(random, len(alphabet))
	if err != nil {
		return 0, err
	}
	return alphabet[index], nil
}

func unbiasedIndex(random io.Reader, size int) (int, error) {
	if random == nil || size < 1 || size > 256 {
		return 0, ErrPasswordGeneration
	}
	if size == 256 {
		var value [1]byte
		if _, err := io.ReadFull(random, value[:]); err != nil {
			return 0, err
		}
		return int(value[0]), nil
	}
	limit := 256 - (256 % size)
	var value [1]byte
	for attempts := 0; attempts < 4096; attempts++ {
		if _, err := io.ReadFull(random, value[:]); err != nil {
			return 0, err
		}
		if int(value[0]) < limit {
			return int(value[0]) % size, nil
		}
	}
	return 0, ErrPasswordGeneration
}
