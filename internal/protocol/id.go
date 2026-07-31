package protocol

import (
	"crypto/rand"
	"encoding/base64"
	"errors"
	"io"
)

const (
	NamespaceIDSize  = 16
	DeviceIDSize     = 16
	CredentialIDSize = 32
	EventIDSize      = 32
	CampaignIDSize   = 32
	KeyIDSize        = 32

	id128TextSize = 22
	id256TextSize = 43
)

// IDs are distinct protocol types with the byte lengths frozen by the data
// model. Namespace and device identifiers are 128-bit; credential, event,
// campaign and key identifiers are 256-bit.
type (
	NamespaceID  [NamespaceIDSize]byte
	DeviceID     [DeviceIDSize]byte
	CredentialID [CredentialIDSize]byte
	EventID      [EventIDSize]byte
	CampaignID   [CampaignIDSize]byte
	KeyID        [KeyIDSize]byte
)

// RandomSource is deliberately not constructible as production-safe by
// callers. SystemRandomSource is the only production source; test readers are
// explicitly tainted and rejected by every Generate* function.
type RandomSource struct {
	reader   io.Reader
	testOnly bool
}

// SystemRandomSource returns the operating system CSPRNG.
func SystemRandomSource() RandomSource {
	return RandomSource{reader: rand.Reader}
}

// NewTestOnlyRandomSource labels a deterministic or injected reader as test
// only. It exists for negative tests and can never be used to generate an ID.
func NewTestOnlyRandomSource(reader io.Reader) RandomSource {
	return RandomSource{reader: reader, testOnly: true}
}

func fillRandomID(source RandomSource, destination []byte) error {
	if source.reader == nil || source.testOnly {
		return reject(CodeInsecureRandom, "randomSource", nil)
	}
	if _, err := io.ReadFull(source.reader, destination); err != nil {
		clear(destination)
		return reject(CodeInsecureRandom, "randomSource", err)
	}
	return nil
}

func validateIDBytes(value []byte, expectedSize int) error {
	if len(value) != expectedSize {
		return reject(CodeInvalidID, "length", nil)
	}
	return nil
}

func decodeIDText(value string, byteSize, textSize int) ([]byte, error) {
	if len(value) != textSize {
		return nil, reject(CodeInvalidID, "encoding", nil)
	}
	decoded, err := base64.RawURLEncoding.DecodeString(value)
	if err != nil || len(decoded) != byteSize {
		return nil, reject(CodeInvalidID, "encoding", err)
	}
	if base64.RawURLEncoding.EncodeToString(decoded) != value {
		return nil, reject(CodeInvalidID, "encoding", nil)
	}
	return decoded, nil
}

func formatID(value []byte) string {
	return base64.RawURLEncoding.EncodeToString(value)
}

func unmarshalIDText(destination, value []byte, textSize int) error {
	if destination == nil {
		return reject(CodeInvalidInput, "id", errors.New("nil destination"))
	}
	decoded, err := decodeIDText(string(value), len(destination), textSize)
	if err != nil {
		return err
	}
	copy(destination, decoded)
	return nil
}

func NewNamespaceID() (NamespaceID, error)   { return GenerateNamespaceID(SystemRandomSource()) }
func NewDeviceID() (DeviceID, error)         { return GenerateDeviceID(SystemRandomSource()) }
func NewCredentialID() (CredentialID, error) { return GenerateCredentialID(SystemRandomSource()) }
func NewEventID() (EventID, error)           { return GenerateEventID(SystemRandomSource()) }
func NewCampaignID() (CampaignID, error)     { return GenerateCampaignID(SystemRandomSource()) }
func NewKeyID() (KeyID, error)               { return GenerateKeyID(SystemRandomSource()) }

func GenerateNamespaceID(source RandomSource) (NamespaceID, error) {
	var id NamespaceID
	return id, fillRandomID(source, id[:])
}

func GenerateDeviceID(source RandomSource) (DeviceID, error) {
	var id DeviceID
	return id, fillRandomID(source, id[:])
}

func GenerateCredentialID(source RandomSource) (CredentialID, error) {
	var id CredentialID
	return id, fillRandomID(source, id[:])
}

func GenerateEventID(source RandomSource) (EventID, error) {
	var id EventID
	return id, fillRandomID(source, id[:])
}

func GenerateCampaignID(source RandomSource) (CampaignID, error) {
	var id CampaignID
	return id, fillRandomID(source, id[:])
}

func GenerateKeyID(source RandomSource) (KeyID, error) {
	var id KeyID
	return id, fillRandomID(source, id[:])
}

func NamespaceIDFromBytes(value []byte) (NamespaceID, error) {
	var id NamespaceID
	if err := validateIDBytes(value, NamespaceIDSize); err != nil {
		return id, err
	}
	copy(id[:], value)
	return id, nil
}

func DeviceIDFromBytes(value []byte) (DeviceID, error) {
	var id DeviceID
	if err := validateIDBytes(value, DeviceIDSize); err != nil {
		return id, err
	}
	copy(id[:], value)
	return id, nil
}

func CredentialIDFromBytes(value []byte) (CredentialID, error) {
	var id CredentialID
	if err := validateIDBytes(value, CredentialIDSize); err != nil {
		return id, err
	}
	copy(id[:], value)
	return id, nil
}

func EventIDFromBytes(value []byte) (EventID, error) {
	var id EventID
	if err := validateIDBytes(value, EventIDSize); err != nil {
		return id, err
	}
	copy(id[:], value)
	return id, nil
}

func CampaignIDFromBytes(value []byte) (CampaignID, error) {
	var id CampaignID
	if err := validateIDBytes(value, CampaignIDSize); err != nil {
		return id, err
	}
	copy(id[:], value)
	return id, nil
}

func KeyIDFromBytes(value []byte) (KeyID, error) {
	var id KeyID
	if err := validateIDBytes(value, KeyIDSize); err != nil {
		return id, err
	}
	copy(id[:], value)
	return id, nil
}

func ParseNamespaceID(value string) (NamespaceID, error) {
	var id NamespaceID
	decoded, err := decodeIDText(value, NamespaceIDSize, id128TextSize)
	if err != nil {
		return id, err
	}
	copy(id[:], decoded)
	return id, nil
}

func ParseDeviceID(value string) (DeviceID, error) {
	var id DeviceID
	decoded, err := decodeIDText(value, DeviceIDSize, id128TextSize)
	if err != nil {
		return id, err
	}
	copy(id[:], decoded)
	return id, nil
}

func ParseCredentialID(value string) (CredentialID, error) {
	var id CredentialID
	decoded, err := decodeIDText(value, CredentialIDSize, id256TextSize)
	if err != nil {
		return id, err
	}
	copy(id[:], decoded)
	return id, nil
}

func ParseEventID(value string) (EventID, error) {
	var id EventID
	decoded, err := decodeIDText(value, EventIDSize, id256TextSize)
	if err != nil {
		return id, err
	}
	copy(id[:], decoded)
	return id, nil
}

func ParseCampaignID(value string) (CampaignID, error) {
	var id CampaignID
	decoded, err := decodeIDText(value, CampaignIDSize, id256TextSize)
	if err != nil {
		return id, err
	}
	copy(id[:], decoded)
	return id, nil
}

func ParseKeyID(value string) (KeyID, error) {
	var id KeyID
	decoded, err := decodeIDText(value, KeyIDSize, id256TextSize)
	if err != nil {
		return id, err
	}
	copy(id[:], decoded)
	return id, nil
}

func (id NamespaceID) String() string  { return formatID(id[:]) }
func (id DeviceID) String() string     { return formatID(id[:]) }
func (id CredentialID) String() string { return formatID(id[:]) }
func (id EventID) String() string      { return formatID(id[:]) }
func (id CampaignID) String() string   { return formatID(id[:]) }
func (id KeyID) String() string        { return formatID(id[:]) }

func (id NamespaceID) MarshalText() ([]byte, error)  { return []byte(id.String()), nil }
func (id DeviceID) MarshalText() ([]byte, error)     { return []byte(id.String()), nil }
func (id CredentialID) MarshalText() ([]byte, error) { return []byte(id.String()), nil }
func (id EventID) MarshalText() ([]byte, error)      { return []byte(id.String()), nil }
func (id CampaignID) MarshalText() ([]byte, error)   { return []byte(id.String()), nil }
func (id KeyID) MarshalText() ([]byte, error)        { return []byte(id.String()), nil }

func (id *NamespaceID) UnmarshalText(value []byte) error {
	if id == nil {
		return reject(CodeInvalidInput, "id", errors.New("nil destination"))
	}
	return unmarshalIDText(id[:], value, id128TextSize)
}

func (id *DeviceID) UnmarshalText(value []byte) error {
	if id == nil {
		return reject(CodeInvalidInput, "id", errors.New("nil destination"))
	}
	return unmarshalIDText(id[:], value, id128TextSize)
}

func (id *CredentialID) UnmarshalText(value []byte) error {
	if id == nil {
		return reject(CodeInvalidInput, "id", errors.New("nil destination"))
	}
	return unmarshalIDText(id[:], value, id256TextSize)
}

func (id *EventID) UnmarshalText(value []byte) error {
	if id == nil {
		return reject(CodeInvalidInput, "id", errors.New("nil destination"))
	}
	return unmarshalIDText(id[:], value, id256TextSize)
}

func (id *CampaignID) UnmarshalText(value []byte) error {
	if id == nil {
		return reject(CodeInvalidInput, "id", errors.New("nil destination"))
	}
	return unmarshalIDText(id[:], value, id256TextSize)
}

func (id *KeyID) UnmarshalText(value []byte) error {
	if id == nil {
		return reject(CodeInvalidInput, "id", errors.New("nil destination"))
	}
	return unmarshalIDText(id[:], value, id256TextSize)
}
