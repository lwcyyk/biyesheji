// Package domain implements versioned site password policies and an unbiased
// password generator without depending on HTTP, SQL or browser adapters.
package domain

import (
	"bytes"
	"crypto/sha256"
	"errors"
	"sort"
	"strings"

	"vpass.local/vpass/internal/protocol"
)

const (
	MinimumPasswordLength = 12
	MaximumPasswordLength = 256
)

var ErrInvalidPasswordPolicy = errors.New("invalid password policy")

const (
	lowercaseAlphabet = "abcdefghijklmnopqrstuvwxyz"
	uppercaseAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	digitAlphabet     = "0123456789"
	defaultSymbols    = "!#$%&()*+,-./:;<=>?@[]^_{|}~"
)

// PasswordPolicyConfig is the caller-facing, versioned site constraint set.
// Minimum counts are separate from allowed classes so sites that prohibit a
// class can be represented without silently weakening another requirement.
type PasswordPolicyConfig struct {
	Version             uint64
	MinimumLength       int
	MaximumLength       int
	DefaultLength       int
	AllowLowercase      bool
	AllowUppercase      bool
	AllowDigits         bool
	AllowedSymbols      string
	MinimumLowercase    int
	MinimumUppercase    int
	MinimumDigits       int
	MinimumSymbols      int
	ForbiddenCharacters string
}

// PasswordPolicy is canonical and immutable.
type PasswordPolicy struct {
	config PasswordPolicyConfig
	hash   [sha256.Size]byte
}

type passwordPolicyWire struct {
	Domain              string `cbor:"domain"`
	ProtocolID          string `cbor:"protocol_id"`
	ProtocolVersion     uint64 `cbor:"protocol_version"`
	SuiteID             string `cbor:"suite_id"`
	Version             uint64 `cbor:"version"`
	MinimumLength       uint64 `cbor:"minimum_length"`
	MaximumLength       uint64 `cbor:"maximum_length"`
	DefaultLength       uint64 `cbor:"default_length"`
	AllowLowercase      bool   `cbor:"allow_lowercase"`
	AllowUppercase      bool   `cbor:"allow_uppercase"`
	AllowDigits         bool   `cbor:"allow_digits"`
	AllowedSymbols      string `cbor:"allowed_symbols"`
	MinimumLowercase    uint64 `cbor:"minimum_lowercase"`
	MinimumUppercase    uint64 `cbor:"minimum_uppercase"`
	MinimumDigits       uint64 `cbor:"minimum_digits"`
	MinimumSymbols      uint64 `cbor:"minimum_symbols"`
	ForbiddenCharacters string `cbor:"forbidden_characters"`
}

func DefaultPasswordPolicy(version uint64) (*PasswordPolicy, error) {
	return NewPasswordPolicy(PasswordPolicyConfig{
		Version: version, MinimumLength: 12, MaximumLength: 128, DefaultLength: 20,
		AllowLowercase: true, AllowUppercase: true, AllowDigits: true,
		AllowedSymbols:   defaultSymbols,
		MinimumLowercase: 1, MinimumUppercase: 1, MinimumDigits: 1, MinimumSymbols: 1,
	})
}

func NewPasswordPolicy(config PasswordPolicyConfig) (*PasswordPolicy, error) {
	config.AllowedSymbols = canonicalCharacters(config.AllowedSymbols)
	config.ForbiddenCharacters = canonicalCharacters(config.ForbiddenCharacters)
	if validatePolicyConfig(config) != nil {
		return nil, ErrInvalidPasswordPolicy
	}
	wire := policyWire(config)
	encoded, err := protocol.MarshalDeterministic(wire)
	if err != nil {
		return nil, ErrInvalidPasswordPolicy
	}
	return &PasswordPolicy{config: config, hash: sha256.Sum256(encoded)}, nil
}

func (policy *PasswordPolicy) Version() uint64 {
	if policy == nil {
		return 0
	}
	return policy.config.Version
}

func (policy *PasswordPolicy) Hash() [sha256.Size]byte {
	if policy == nil {
		return [sha256.Size]byte{}
	}
	return policy.hash
}

func (policy *PasswordPolicy) Config() PasswordPolicyConfig {
	if policy == nil {
		return PasswordPolicyConfig{}
	}
	return policy.config
}

func (policy *PasswordPolicy) MarshalBinary() ([]byte, error) {
	if policy == nil || validatePolicyConfig(policy.config) != nil {
		return nil, ErrInvalidPasswordPolicy
	}
	encoded, err := protocol.MarshalDeterministic(policyWire(policy.config))
	if err != nil || sha256.Sum256(encoded) != policy.hash {
		return nil, ErrInvalidPasswordPolicy
	}
	return encoded, nil
}

func ParsePasswordPolicy(encoded []byte) (*PasswordPolicy, error) {
	var wire passwordPolicyWire
	if err := protocol.UnmarshalDeterministic(encoded, &wire); err != nil ||
		wire.Domain != protocol.DomainPrefix+"PASSWORD-POLICY" ||
		wire.ProtocolID != protocol.ProtocolID ||
		wire.ProtocolVersion != protocol.ProtocolVersion ||
		wire.SuiteID != protocol.SuiteID {
		return nil, ErrInvalidPasswordPolicy
	}
	config := PasswordPolicyConfig{
		Version: wire.Version, MinimumLength: int(wire.MinimumLength),
		MaximumLength: int(wire.MaximumLength), DefaultLength: int(wire.DefaultLength),
		AllowLowercase: wire.AllowLowercase, AllowUppercase: wire.AllowUppercase,
		AllowDigits: wire.AllowDigits, AllowedSymbols: wire.AllowedSymbols,
		MinimumLowercase:    int(wire.MinimumLowercase),
		MinimumUppercase:    int(wire.MinimumUppercase),
		MinimumDigits:       int(wire.MinimumDigits),
		MinimumSymbols:      int(wire.MinimumSymbols),
		ForbiddenCharacters: wire.ForbiddenCharacters,
	}
	policy, err := NewPasswordPolicy(config)
	if err != nil {
		return nil, err
	}
	canonical, err := policy.MarshalBinary()
	if err != nil || !bytes.Equal(canonical, encoded) {
		return nil, ErrInvalidPasswordPolicy
	}
	return policy, nil
}

func validatePolicyConfig(config PasswordPolicyConfig) error {
	if config.Version == 0 ||
		config.MinimumLength < MinimumPasswordLength ||
		config.MaximumLength > MaximumPasswordLength ||
		config.MaximumLength < config.MinimumLength ||
		config.DefaultLength < config.MinimumLength ||
		config.DefaultLength > config.MaximumLength ||
		config.MinimumLowercase < 0 || config.MinimumUppercase < 0 ||
		config.MinimumDigits < 0 || config.MinimumSymbols < 0 ||
		(config.MinimumLowercase > 0 && !config.AllowLowercase) ||
		(config.MinimumUppercase > 0 && !config.AllowUppercase) ||
		(config.MinimumDigits > 0 && !config.AllowDigits) ||
		(config.MinimumSymbols > 0 && config.AllowedSymbols == "") ||
		(!config.AllowLowercase && !config.AllowUppercase && !config.AllowDigits &&
			config.AllowedSymbols == "") ||
		config.MinimumLowercase+config.MinimumUppercase+
			config.MinimumDigits+config.MinimumSymbols > config.MinimumLength {
		return ErrInvalidPasswordPolicy
	}
	for _, value := range config.AllowedSymbols {
		if value < 0x21 || value > 0x7e ||
			strings.ContainsRune(lowercaseAlphabet+uppercaseAlphabet+digitAlphabet, value) {
			return ErrInvalidPasswordPolicy
		}
	}
	for _, value := range config.ForbiddenCharacters {
		if value < 0x21 || value > 0x7e {
			return ErrInvalidPasswordPolicy
		}
	}
	for class, allowed := range map[string]bool{
		lowercaseAlphabet: config.AllowLowercase,
		uppercaseAlphabet: config.AllowUppercase,
		digitAlphabet:     config.AllowDigits,
	} {
		if allowed && removeForbidden(class, config.ForbiddenCharacters) == "" {
			return ErrInvalidPasswordPolicy
		}
	}
	return nil
}

func policyWire(config PasswordPolicyConfig) passwordPolicyWire {
	return passwordPolicyWire{
		Domain:     protocol.DomainPrefix + "PASSWORD-POLICY",
		ProtocolID: protocol.ProtocolID, ProtocolVersion: protocol.ProtocolVersion,
		SuiteID: protocol.SuiteID, Version: config.Version,
		MinimumLength:  uint64(config.MinimumLength),
		MaximumLength:  uint64(config.MaximumLength),
		DefaultLength:  uint64(config.DefaultLength),
		AllowLowercase: config.AllowLowercase, AllowUppercase: config.AllowUppercase,
		AllowDigits: config.AllowDigits, AllowedSymbols: config.AllowedSymbols,
		MinimumLowercase:    uint64(config.MinimumLowercase),
		MinimumUppercase:    uint64(config.MinimumUppercase),
		MinimumDigits:       uint64(config.MinimumDigits),
		MinimumSymbols:      uint64(config.MinimumSymbols),
		ForbiddenCharacters: config.ForbiddenCharacters,
	}
}

func canonicalCharacters(input string) string {
	values := []rune(input)
	sort.Slice(values, func(i, j int) bool { return values[i] < values[j] })
	result := values[:0]
	for _, value := range values {
		if len(result) == 0 || result[len(result)-1] != value {
			result = append(result, value)
		}
	}
	return string(result)
}

func removeForbidden(alphabet, forbidden string) string {
	var result strings.Builder
	for _, value := range alphabet {
		if !strings.ContainsRune(forbidden, value) {
			result.WriteRune(value)
		}
	}
	return result.String()
}
