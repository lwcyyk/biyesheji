package protocol

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"testing"
)

type idTestCase struct {
	name        string
	byteSize    int
	textSize    int
	fromBytes   func([]byte) (fmt.Stringer, error)
	parse       func(string) (fmt.Stringer, error)
	newID       func() (fmt.Stringer, error)
	generate    func(RandomSource) error
	destination func() fmt.Stringer
}

func allIDTestCases() []idTestCase {
	return []idTestCase{
		{
			name: "namespace", byteSize: NamespaceIDSize, textSize: id128TextSize,
			fromBytes:   func(value []byte) (fmt.Stringer, error) { id, err := NamespaceIDFromBytes(value); return id, err },
			parse:       func(value string) (fmt.Stringer, error) { id, err := ParseNamespaceID(value); return id, err },
			newID:       func() (fmt.Stringer, error) { id, err := NewNamespaceID(); return id, err },
			generate:    func(source RandomSource) error { _, err := GenerateNamespaceID(source); return err },
			destination: func() fmt.Stringer { return new(NamespaceID) },
		},
		{
			name: "device", byteSize: DeviceIDSize, textSize: id128TextSize,
			fromBytes:   func(value []byte) (fmt.Stringer, error) { id, err := DeviceIDFromBytes(value); return id, err },
			parse:       func(value string) (fmt.Stringer, error) { id, err := ParseDeviceID(value); return id, err },
			newID:       func() (fmt.Stringer, error) { id, err := NewDeviceID(); return id, err },
			generate:    func(source RandomSource) error { _, err := GenerateDeviceID(source); return err },
			destination: func() fmt.Stringer { return new(DeviceID) },
		},
		{
			name: "credential", byteSize: CredentialIDSize, textSize: id256TextSize,
			fromBytes:   func(value []byte) (fmt.Stringer, error) { id, err := CredentialIDFromBytes(value); return id, err },
			parse:       func(value string) (fmt.Stringer, error) { id, err := ParseCredentialID(value); return id, err },
			newID:       func() (fmt.Stringer, error) { id, err := NewCredentialID(); return id, err },
			generate:    func(source RandomSource) error { _, err := GenerateCredentialID(source); return err },
			destination: func() fmt.Stringer { return new(CredentialID) },
		},
		{
			name: "event", byteSize: EventIDSize, textSize: id256TextSize,
			fromBytes:   func(value []byte) (fmt.Stringer, error) { id, err := EventIDFromBytes(value); return id, err },
			parse:       func(value string) (fmt.Stringer, error) { id, err := ParseEventID(value); return id, err },
			newID:       func() (fmt.Stringer, error) { id, err := NewEventID(); return id, err },
			generate:    func(source RandomSource) error { _, err := GenerateEventID(source); return err },
			destination: func() fmt.Stringer { return new(EventID) },
		},
		{
			name: "campaign", byteSize: CampaignIDSize, textSize: id256TextSize,
			fromBytes:   func(value []byte) (fmt.Stringer, error) { id, err := CampaignIDFromBytes(value); return id, err },
			parse:       func(value string) (fmt.Stringer, error) { id, err := ParseCampaignID(value); return id, err },
			newID:       func() (fmt.Stringer, error) { id, err := NewCampaignID(); return id, err },
			generate:    func(source RandomSource) error { _, err := GenerateCampaignID(source); return err },
			destination: func() fmt.Stringer { return new(CampaignID) },
		},
		{
			name: "key", byteSize: KeyIDSize, textSize: id256TextSize,
			fromBytes:   func(value []byte) (fmt.Stringer, error) { id, err := KeyIDFromBytes(value); return id, err },
			parse:       func(value string) (fmt.Stringer, error) { id, err := ParseKeyID(value); return id, err },
			newID:       func() (fmt.Stringer, error) { id, err := NewKeyID(); return id, err },
			generate:    func(source RandomSource) error { _, err := GenerateKeyID(source); return err },
			destination: func() fmt.Stringer { return new(KeyID) },
		},
	}
}

func TestFrozenIDByteAndTextSizes(t *testing.T) {
	if NamespaceIDSize != 16 || DeviceIDSize != 16 {
		t.Fatal("namespace or device ID no longer matches the frozen 128-bit data model")
	}
	if CredentialIDSize != 32 || EventIDSize != 32 || CampaignIDSize != 32 || KeyIDSize != 32 {
		t.Fatal("public ID sizes no longer match the frozen 256-bit data model")
	}
	if len(NamespaceID{}) != NamespaceIDSize || len(DeviceID{}) != DeviceIDSize ||
		len(CredentialID{}) != CredentialIDSize || len(EventID{}) != EventIDSize ||
		len(CampaignID{}) != CampaignIDSize || len(KeyID{}) != KeyIDSize {
		t.Fatal("strong ID array type does not match its exported size constant")
	}
}

func TestAllIDsUseCanonicalRawBase64URLAndJSON(t *testing.T) {
	for _, test := range allIDTestCases() {
		t.Run(test.name, func(t *testing.T) {
			raw := make([]byte, test.byteSize)
			for i := range raw {
				raw[i] = byte(i)
			}
			id, err := test.fromBytes(raw)
			if err != nil {
				t.Fatalf("fromBytes: %v", err)
			}
			want := rawIDEncoding(raw)
			if got := id.String(); got != want || len(got) != test.textSize || strings.Contains(got, "=") {
				t.Fatalf("canonical text = %q (len %d), want %q (len %d)", got, len(got), want, test.textSize)
			}
			parsed, err := test.parse(want)
			if err != nil || parsed.String() != want {
				t.Fatalf("parse = %v, %v", parsed, err)
			}

			encodedJSON, err := json.Marshal(id)
			if err != nil {
				t.Fatalf("json.Marshal: %v", err)
			}
			if string(encodedJSON) != `"`+want+`"` {
				t.Fatalf("JSON = %s", encodedJSON)
			}
			destination := test.destination()
			if err := json.Unmarshal(encodedJSON, destination); err != nil || destination.String() != want {
				t.Fatalf("JSON round trip = %v, %v", destination, err)
			}

			raw[0] ^= 0xff
			if id.String() != want {
				t.Fatal("ID aliases caller-owned bytes")
			}
		})
	}
}

func TestAllIDsRejectBadByteAndTextLengths(t *testing.T) {
	for _, test := range allIDTestCases() {
		t.Run(test.name, func(t *testing.T) {
			for _, size := range []int{test.byteSize - 1, test.byteSize + 1} {
				if _, err := test.fromBytes(make([]byte, size)); code(err) != CodeInvalidID {
					t.Errorf("fromBytes length %d code = %q", size, code(err))
				}
			}
			valid := rawIDEncoding(make([]byte, test.byteSize))
			invalid := []string{
				"",
				valid + "=",
				valid[:len(valid)-1],
				"!" + valid[1:],
			}
			for _, value := range invalid {
				if _, err := test.parse(value); code(err) != CodeInvalidID {
					t.Errorf("parse %q code = %q", value, code(err))
				}
				destination := test.destination()
				if err := json.Unmarshal([]byte(`"`+value+`"`), destination); code(err) != CodeInvalidID {
					t.Errorf("JSON %q code = %q (err=%v)", value, code(err), err)
				}
			}
		})
	}
}

func TestAllProductionIDGeneratorsRejectTestAndBrokenRandom(t *testing.T) {
	for _, test := range allIDTestCases() {
		t.Run(test.name, func(t *testing.T) {
			testSource := NewTestOnlyRandomSource(bytes.NewReader(make([]byte, test.byteSize)))
			if err := test.generate(testSource); code(err) != CodeInsecureRandom {
				t.Fatalf("test RNG code = %q", code(err))
			}
			if err := test.generate(RandomSource{}); code(err) != CodeInsecureRandom {
				t.Fatalf("zero RNG code = %q", code(err))
			}
			broken := RandomSource{reader: bytes.NewReader(make([]byte, test.byteSize-1))}
			if err := test.generate(broken); code(err) != CodeInsecureRandom {
				t.Fatalf("short RNG code = %q", code(err))
			}
		})
	}
}

func TestAllIDGeneratorsClearPartialRandomOutputOnFailure(t *testing.T) {
	tests := []struct {
		name     string
		byteSize int
		generate func(RandomSource) ([]byte, error)
	}{
		{"namespace", NamespaceIDSize, func(source RandomSource) ([]byte, error) {
			id, err := GenerateNamespaceID(source)
			return append([]byte(nil), id[:]...), err
		}},
		{"device", DeviceIDSize, func(source RandomSource) ([]byte, error) {
			id, err := GenerateDeviceID(source)
			return append([]byte(nil), id[:]...), err
		}},
		{"credential", CredentialIDSize, func(source RandomSource) ([]byte, error) {
			id, err := GenerateCredentialID(source)
			return append([]byte(nil), id[:]...), err
		}},
		{"event", EventIDSize, func(source RandomSource) ([]byte, error) {
			id, err := GenerateEventID(source)
			return append([]byte(nil), id[:]...), err
		}},
		{"campaign", CampaignIDSize, func(source RandomSource) ([]byte, error) {
			id, err := GenerateCampaignID(source)
			return append([]byte(nil), id[:]...), err
		}},
		{"key", KeyIDSize, func(source RandomSource) ([]byte, error) {
			id, err := GenerateKeyID(source)
			return append([]byte(nil), id[:]...), err
		}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			partial := bytes.NewReader(bytes.Repeat([]byte{0xa5}, test.byteSize-1))
			id, err := test.generate(RandomSource{reader: partial})
			if code(err) != CodeInsecureRandom {
				t.Fatalf("partial RNG code = %q (err=%v)", code(err), err)
			}
			if !bytes.Equal(id, make([]byte, test.byteSize)) {
				t.Fatalf("partially generated ID wasn't cleared: %x", id)
			}
		})
	}
}

func TestAllSystemGeneratedIDsDoNotCollideInSample(t *testing.T) {
	for _, test := range allIDTestCases() {
		t.Run(test.name, func(t *testing.T) {
			seen := make(map[string]struct{}, 512)
			for i := 0; i < 512; i++ {
				id, err := test.newID()
				if err != nil {
					t.Fatalf("new ID: %v", err)
				}
				if _, exists := seen[id.String()]; exists {
					t.Fatalf("collision at sample %d", i)
				}
				seen[id.String()] = struct{}{}
			}
		})
	}
}

func TestNilIDTextDestinationDoesNotPanic(t *testing.T) {
	tests := []func() error{
		func() error { var id *NamespaceID; return id.UnmarshalText([]byte(strings.Repeat("A", id128TextSize))) },
		func() error { var id *DeviceID; return id.UnmarshalText([]byte(strings.Repeat("A", id128TextSize))) },
		func() error {
			var id *CredentialID
			return id.UnmarshalText([]byte(strings.Repeat("A", id128TextSize)))
		},
		func() error { var id *EventID; return id.UnmarshalText([]byte(strings.Repeat("A", id256TextSize))) },
		func() error { var id *CampaignID; return id.UnmarshalText([]byte(strings.Repeat("A", id256TextSize))) },
		func() error { var id *KeyID; return id.UnmarshalText([]byte(strings.Repeat("A", id256TextSize))) },
	}
	for i, test := range tests {
		if err := test(); code(err) != CodeInvalidInput {
			t.Errorf("nil destination %d code = %q", i, code(err))
		}
	}
}

func TestProtocolErrorCodeSurvivesWrapping(t *testing.T) {
	err := reject(CodeInvalidID, "id", errors.New("detail"))
	if got, ok := CodeOf(errors.Join(errors.New("outer"), err)); !ok || got != CodeInvalidID {
		t.Fatalf("CodeOf() = %q, %v", got, ok)
	}
}

func FuzzParseNamespaceID(f *testing.F) {
	f.Add("AAECAwQFBgcICQoLDA0ODw")
	f.Add("")
	f.Add(strings.Repeat("_", id128TextSize))
	f.Fuzz(func(t *testing.T, value string) {
		id, err := ParseNamespaceID(value)
		if err == nil && id.String() != value {
			t.Fatalf("accepted non-canonical value %q", value)
		}
	})
}

func FuzzParseCredentialID(f *testing.F) {
	f.Add(rawIDEncoding(make([]byte, CredentialIDSize)))
	f.Add("")
	f.Add("not-base64!")
	f.Fuzz(func(t *testing.T, value string) {
		id, err := ParseCredentialID(value)
		if err != nil {
			return
		}
		if len(id.String()) != id256TextSize {
			t.Fatal("successful CredentialID parse returned non-canonical width")
		}
	})
}

func FuzzParseEventID(f *testing.F) {
	f.Add("AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8")
	f.Add("")
	f.Add(strings.Repeat("_", id256TextSize))
	f.Fuzz(func(t *testing.T, value string) {
		id, err := ParseEventID(value)
		if err == nil && id.String() != value {
			t.Fatalf("accepted non-canonical value %q", value)
		}
	})
}

func rawIDEncoding(value []byte) string {
	return formatID(value)
}

func code(err error) ErrorCode {
	result, _ := CodeOf(err)
	return result
}
