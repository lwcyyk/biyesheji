package protocol

import (
	"bytes"
	"encoding/hex"
	"testing"

	"github.com/fxamacker/cbor/v2"
)

type cborSample struct {
	B uint64 `cbor:"b"`
	A string `cbor:"a"`
}

func TestCoreDeterministicCBORFixedVector(t *testing.T) {
	encoded, err := MarshalDeterministic(cborSample{B: 2, A: "x"})
	if err != nil {
		t.Fatalf("MarshalDeterministic: %v", err)
	}
	const expectedHex = "a261616178616202"
	if got := hex.EncodeToString(encoded); got != expectedHex {
		t.Fatalf("CBOR = %s, want %s", got, expectedHex)
	}

	var decoded cborSample
	if err := UnmarshalDeterministic(encoded, &decoded); err != nil {
		t.Fatalf("UnmarshalDeterministic: %v", err)
	}
	if decoded != (cborSample{B: 2, A: "x"}) {
		t.Fatalf("decoded = %#v", decoded)
	}
}

func TestRFC8949AppendixAFixedVectors(t *testing.T) {
	tests := []struct {
		name  string
		value any
		hex   string
	}{
		{"zero", uint64(0), "00"},
		{"twenty-three", uint64(23), "17"},
		{"twenty-four", uint64(24), "1818"},
		{"one-thousand", uint64(1000), "1903e8"},
		{"byte string", []byte{1, 2, 3, 4}, "4401020304"},
		{"text", "a", "6161"},
		{"array", []uint64{1, 2, 3}, "83010203"},
		{"map", map[uint64]uint64{1: 2, 3: 4}, "a201020304"},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			encoded, err := MarshalDeterministic(test.value)
			if err != nil {
				t.Fatal(err)
			}
			if got := hex.EncodeToString(encoded); got != test.hex {
				t.Fatalf("encoded = %s, want %s", got, test.hex)
			}
		})
	}
}

func TestAllIDArraysEncodeAsCBORByteStrings(t *testing.T) {
	namespaceID, _ := NamespaceIDFromBytes(bytes.Repeat([]byte{0x11}, NamespaceIDSize))
	deviceID, _ := DeviceIDFromBytes(bytes.Repeat([]byte{0x22}, DeviceIDSize))
	credentialID, _ := CredentialIDFromBytes(bytes.Repeat([]byte{0x33}, CredentialIDSize))
	eventID, _ := EventIDFromBytes(bytes.Repeat([]byte{0x44}, EventIDSize))
	campaignID, _ := CampaignIDFromBytes(bytes.Repeat([]byte{0x55}, CampaignIDSize))
	keyID, _ := KeyIDFromBytes(bytes.Repeat([]byte{0x66}, KeyIDSize))

	assertIDCBORByteString(t, "namespace", namespaceID, NamespaceIDSize)
	assertIDCBORByteString(t, "device", deviceID, DeviceIDSize)
	assertIDCBORByteString(t, "credential", credentialID, CredentialIDSize)
	assertIDCBORByteString(t, "event", eventID, EventIDSize)
	assertIDCBORByteString(t, "campaign", campaignID, CampaignIDSize)
	assertIDCBORByteString(t, "key", keyID, KeyIDSize)
}

func TestNullableStructFieldRoundTripsAsCanonicalNull(t *testing.T) {
	type nullableValue struct {
		Value *uint64 `cbor:"value"`
	}
	encoded, err := MarshalDeterministic(nullableValue{})
	if err != nil {
		t.Fatal(err)
	}
	var decoded nullableValue
	if err := UnmarshalDeterministic(encoded, &decoded); err != nil {
		t.Fatal(err)
	}
	if decoded.Value != nil {
		t.Fatal("CBOR null did not remain absent")
	}
	var root *nullableValue
	if _, err := MarshalDeterministic(root); err == nil {
		t.Fatal("nil root pointer was accepted")
	}
}

func assertIDCBORByteString[T comparable](t *testing.T, name string, id T, byteSize int) {
	t.Helper()
	t.Run(name, func(t *testing.T) {
		type object struct {
			ID T `cbor:"id"`
		}
		encoded, err := MarshalDeterministic(object{ID: id})
		if err != nil {
			t.Fatal(err)
		}
		prefix := []byte{0xa1, 0x62, 'i', 'd'}
		if byteSize <= 23 {
			prefix = append(prefix, byte(0x40+byteSize))
		} else {
			prefix = append(prefix, 0x58, byte(byteSize))
		}
		if !bytes.HasPrefix(encoded, prefix) {
			t.Fatalf("ID isn't a %d-byte CBOR byte string: %x", byteSize, encoded)
		}
		var decoded object
		if err := UnmarshalDeterministic(encoded, &decoded); err != nil || decoded.ID != id {
			t.Fatalf("ID CBOR round trip = %#v, %v", decoded, err)
		}
	})
}

func TestStrictCBORRejectsMalformedAndNonCanonicalInputs(t *testing.T) {
	type one struct {
		A uint64 `cbor:"a"`
	}
	type two struct {
		A uint64 `cbor:"a"`
		B uint64 `cbor:"b"`
	}
	type dynamic struct {
		A any `cbor:"a"`
	}

	tests := []struct {
		name string
		hex  string
		out  any
		want ErrorCode
	}{
		{"duplicate key", "a2616101616102", &one{}, CodeCBORInvalid},
		{"indefinite map", "bf616101ff", &one{}, CodeCBORInvalid},
		{"float", "a16161f93c00", &dynamic{}, CodeCBORInvalid},
		{"non-shortest integer", "a161611801", &one{}, CodeCBORNonCanonical},
		{"non-canonical map order", "a2616202616101", &two{}, CodeCBORNonCanonical},
		{"unknown field", "a2616101617802", &one{}, CodeCBORInvalid},
		{"case-variant unknown field", "a1614101", &one{}, CodeCBORInvalid},
		{"invalid UTF-8", "a1616161ff", &dynamic{}, CodeCBORInvalid},
		{"tag", "c0a1616101", &one{}, CodeCBORInvalid},
		{"trailing bytes", "a161610100", &one{}, CodeCBORInvalid},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			data, err := hex.DecodeString(test.hex)
			if err != nil {
				t.Fatal(err)
			}
			if err := UnmarshalDeterministic(data, test.out); code(err) != test.want {
				t.Fatalf("code = %q, want %q (err=%v)", code(err), test.want, err)
			}
		})
	}
}

func TestCBORDecoderDoesNotPartiallyMutateDestination(t *testing.T) {
	type object struct {
		A uint64 `cbor:"a"`
	}
	destination := object{A: 99}
	nonCanonical, _ := hex.DecodeString("a161611801")
	if err := UnmarshalDeterministic(nonCanonical, &destination); err == nil {
		t.Fatal("accepted non-canonical input")
	}
	if destination.A != 99 {
		t.Fatalf("destination partially mutated: %#v", destination)
	}
}

func TestCBORResourceLimitsAndUnsafeTypes(t *testing.T) {
	if _, err := MarshalDeterministic(make([]any, MaxCBORArrayItems+1)); code(err) != CodeResourceLimit {
		t.Fatalf("array limit code = %q", code(err))
	}
	largeMap := make(map[uint64]uint64, MaxCBORMapPairs+1)
	for i := uint64(0); i <= MaxCBORMapPairs; i++ {
		largeMap[i] = i
	}
	if _, err := MarshalDeterministic(largeMap); code(err) != CodeResourceLimit {
		t.Fatalf("map limit code = %q", code(err))
	}
	if _, err := MarshalDeterministic(bytes.Repeat([]byte{1}, MaxCBORBytes)); code(err) != CodeResourceLimit {
		t.Fatalf("byte-size limit code = %q", code(err))
	}
	if _, err := MarshalDeterministic(1.5); code(err) != CodeCBORInvalid {
		t.Fatalf("float code = %q", code(err))
	}
	if _, err := MarshalDeterministic(cbor.RawMessage{0x01}); code(err) != CodeCBORInvalid {
		t.Fatalf("raw CBOR code = %q", code(err))
	}

	cycle := map[string]any{}
	cycle["self"] = cycle
	if _, err := MarshalDeterministic(cycle); code(err) != CodeCBORInvalid {
		t.Fatalf("cycle code = %q", code(err))
	}

	var nested any = uint64(1)
	for i := 0; i <= MaxCBORNesting; i++ {
		nested = []any{nested}
	}
	if _, err := MarshalDeterministic(nested); code(err) != CodeResourceLimit {
		t.Fatalf("nesting limit code = %q", code(err))
	}
}

type binaryCodecBypass struct {
	Value uint64 `cbor:"value"`
}

func (binaryCodecBypass) MarshalBinary() ([]byte, error) {
	return []byte{0x01}, nil
}

func (*binaryCodecBypass) UnmarshalBinary([]byte) error {
	return nil
}

func TestCBORRejectsCustomBinaryCodecBypass(t *testing.T) {
	if _, err := MarshalDeterministic(binaryCodecBypass{Value: 7}); code(err) != CodeCBORInvalid {
		t.Fatalf("binary marshaler code = %q (err=%v)", code(err), err)
	}
	canonical, _ := hex.DecodeString("a16576616c756507")
	destination := binaryCodecBypass{Value: 99}
	if err := UnmarshalDeterministic(canonical, &destination); code(err) != CodeCBORInvalid {
		t.Fatalf("binary unmarshaler code = %q (err=%v)", code(err), err)
	}
	if destination.Value != 99 {
		t.Fatalf("binary codec rejection mutated destination: %#v", destination)
	}
}

var customCBORUnmarshalCalls int

type customCBORUnmarshaler struct {
	Value uint64 `cbor:"value"`
}

func (value *customCBORUnmarshaler) UnmarshalCBOR([]byte) error {
	customCBORUnmarshalCalls++
	value.Value = 1
	return nil
}

func TestCBORRejectsCustomUnmarshalerBeforeAnySideEffect(t *testing.T) {
	type outer struct {
		Inner customCBORUnmarshaler `cbor:"inner"`
	}
	canonical, _ := hex.DecodeString("a165696e6e6572a16576616c756507")
	destination := outer{Inner: customCBORUnmarshaler{Value: 99}}
	customCBORUnmarshalCalls = 0
	if err := UnmarshalDeterministic(canonical, &destination); code(err) != CodeCBORInvalid {
		t.Fatalf("custom CBOR unmarshaler code = %q (err=%v)", code(err), err)
	}
	if customCBORUnmarshalCalls != 0 {
		t.Fatalf("custom UnmarshalCBOR executed %d times before rejection", customCBORUnmarshalCalls)
	}
	if destination.Inner.Value != 99 {
		t.Fatalf("custom CBOR rejection mutated destination: %#v", destination)
	}
}

func TestValidateDeterministicPayload(t *testing.T) {
	canonical, _ := hex.DecodeString("a1616101")
	if err := ValidateDeterministic(canonical); err != nil {
		t.Fatalf("canonical payload: %v", err)
	}
	for _, value := range []string{"a161611801", "bf616101ff", "f93c00"} {
		data, _ := hex.DecodeString(value)
		if err := ValidateDeterministic(data); err == nil {
			t.Fatalf("accepted invalid payload %s", value)
		}
	}
}

func TestUnmarshalRequiresConcreteStructDestination(t *testing.T) {
	data, _ := hex.DecodeString("a1616101")
	var mapDestination map[string]uint64
	if err := UnmarshalDeterministic(data, &mapDestination); code(err) != CodeInvalidInput {
		t.Fatalf("map destination code = %q", code(err))
	}
	if err := UnmarshalDeterministic(data, nil); code(err) != CodeInvalidInput {
		t.Fatalf("nil destination code = %q", code(err))
	}
}

func FuzzValidateDeterministic(f *testing.F) {
	f.Add([]byte{0xa1, 0x61, 0x61, 0x01})
	f.Add([]byte{0xbf, 0xff})
	f.Add([]byte{0xf9, 0x3c, 0x00})
	f.Fuzz(func(t *testing.T, data []byte) {
		_ = ValidateDeterministic(data)
	})
}

func FuzzUnmarshalDeterministic(f *testing.F) {
	f.Add([]byte{0xa1, 0x61, 0x61, 0x01})
	f.Add([]byte{0xa1, 0x61, 0x61, 0x18, 0x01})
	f.Fuzz(func(t *testing.T, data []byte) {
		var destination struct {
			A uint64 `cbor:"a"`
		}
		_ = UnmarshalDeterministic(data, &destination)
	})
}
