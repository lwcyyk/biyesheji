package protocol

import (
	"bytes"
	"encoding"
	"errors"
	"fmt"
	"reflect"
	"unicode/utf8"

	"github.com/fxamacker/cbor/v2"
)

const (
	MaxCBORBytes      = 128 * 1024
	MaxCBORNesting    = 16
	MaxCBORMapPairs   = 128
	MaxCBORArrayItems = 10_000
)

var (
	deterministicEnc cbor.EncMode
	strictDec        cbor.DecMode
)

func init() {
	encOptions := cbor.CoreDetEncOptions()
	encOptions.ByteArray = cbor.ByteArrayToByteSlice
	encOptions.TextMarshaler = cbor.TextMarshalerNone
	encOptions.BinaryMarshaler = cbor.BinaryMarshalerNone
	encOptions.TagsMd = cbor.TagsForbidden
	var err error
	deterministicEnc, err = encOptions.EncMode()
	if err != nil {
		panic(fmt.Sprintf("protocol: initialize CBOR encoder: %v", err))
	}

	strictDec, err = (cbor.DecOptions{
		DupMapKey:         cbor.DupMapKeyEnforcedAPF,
		MaxNestedLevels:   MaxCBORNesting,
		MaxArrayElements:  MaxCBORArrayItems,
		MaxMapPairs:       MaxCBORMapPairs,
		IndefLength:       cbor.IndefLengthForbidden,
		TagsMd:            cbor.TagsForbidden,
		ExtraReturnErrors: cbor.ExtraDecErrorUnknownField,
		UTF8:              cbor.UTF8RejectInvalid,
		NaN:               cbor.NaNDecodeForbidden,
		Inf:               cbor.InfDecodeForbidden,
		TextUnmarshaler:   cbor.TextUnmarshalerNone,
		BinaryUnmarshaler: cbor.BinaryUnmarshalerNone,
		FieldNameMatching: cbor.FieldNameMatchingCaseSensitive,
	}).DecMode()
	if err != nil {
		panic(fmt.Sprintf("protocol: initialize CBOR decoder: %v", err))
	}
}

// ValidateDeterministic validates a complete, schema-independent CBOR value.
// It is intended for already encoded nested payloads; schema-aware callers
// should prefer UnmarshalDeterministic.
func ValidateDeterministic(data []byte) error {
	if len(data) == 0 {
		return reject(CodeCBORInvalid, "cbor", errors.New("empty input"))
	}
	if len(data) > MaxCBORBytes {
		return reject(CodeResourceLimit, "cbor", nil)
	}
	var decoded any
	if err := strictDec.Unmarshal(data, &decoded); err != nil {
		return reject(CodeCBORInvalid, "cbor", err)
	}
	if err := validateCBORValue(reflect.ValueOf(decoded), 0, make(map[visit]struct{})); err != nil {
		return err
	}
	reencoded, err := MarshalDeterministic(decoded)
	if err != nil {
		return err
	}
	if !bytes.Equal(data, reencoded) {
		return reject(CodeCBORNonCanonical, "cbor", nil)
	}
	return nil
}

// MarshalDeterministic encodes a strongly typed value using RFC 8949 Core
// Deterministic CBOR. Floats, tags, custom CBOR encoders and inputs beyond the
// protocol resource limits are rejected.
func MarshalDeterministic(value any) ([]byte, error) {
	if value == nil {
		return nil, reject(CodeInvalidInput, "value", errors.New("nil value"))
	}
	root := reflect.ValueOf(value)
	if root.Kind() == reflect.Pointer && root.IsNil() {
		return nil, reject(CodeInvalidInput, "value", errors.New("nil root pointer"))
	}
	if err := validateCBORValue(root, 0, make(map[visit]struct{})); err != nil {
		return nil, err
	}
	encoded, err := deterministicEnc.Marshal(value)
	if err != nil {
		return nil, reject(CodeCBORInvalid, "value", err)
	}
	if len(encoded) > MaxCBORBytes {
		return nil, reject(CodeResourceLimit, "cbor", nil)
	}
	return encoded, nil
}

// UnmarshalDeterministic strictly decodes a canonical CBOR map into a concrete
// struct. The destination is updated only after all validation succeeds.
func UnmarshalDeterministic(data []byte, out any) error {
	if len(data) == 0 {
		return reject(CodeCBORInvalid, "cbor", errors.New("empty input"))
	}
	if len(data) > MaxCBORBytes {
		return reject(CodeResourceLimit, "cbor", nil)
	}
	destination := reflect.ValueOf(out)
	if destination.Kind() != reflect.Pointer || destination.IsNil() || destination.Elem().Kind() != reflect.Struct {
		return reject(CodeInvalidInput, "out", errors.New("expected non-nil pointer to struct"))
	}
	if err := validateCBORTargetType(destination.Elem().Type(), make(map[reflect.Type]struct{})); err != nil {
		return err
	}
	temporary := reflect.New(destination.Elem().Type())
	if err := strictDec.Unmarshal(data, temporary.Interface()); err != nil {
		return reject(CodeCBORInvalid, "cbor", err)
	}
	if err := validateCBORValue(temporary.Elem(), 0, make(map[visit]struct{})); err != nil {
		return err
	}
	reencoded, err := MarshalDeterministic(temporary.Elem().Interface())
	if err != nil {
		return err
	}
	if !bytes.Equal(data, reencoded) {
		return reject(CodeCBORNonCanonical, "cbor", nil)
	}
	destination.Elem().Set(temporary.Elem())
	return nil
}

type visit struct {
	typeOf reflect.Type
	ptr    uintptr
}

var (
	cborMarshalerType     = reflect.TypeOf((*cbor.Marshaler)(nil)).Elem()
	cborUnmarshalerType   = reflect.TypeOf((*cbor.Unmarshaler)(nil)).Elem()
	binaryMarshalerType   = reflect.TypeOf((*encoding.BinaryMarshaler)(nil)).Elem()
	binaryUnmarshalerType = reflect.TypeOf((*encoding.BinaryUnmarshaler)(nil)).Elem()
)

func validateCBORTargetType(valueType reflect.Type, seen map[reflect.Type]struct{}) error {
	if valueType == nil {
		return nil
	}
	if _, exists := seen[valueType]; exists {
		return nil
	}
	seen[valueType] = struct{}{}
	if implementsCodec(valueType, cborUnmarshalerType) {
		return reject(CodeCBORInvalid, "out", errors.New("custom CBOR unmarshaler forbidden"))
	}
	if implementsCodec(valueType, binaryMarshalerType) || implementsCodec(valueType, binaryUnmarshalerType) {
		return reject(CodeCBORInvalid, "out", errors.New("custom binary codec forbidden"))
	}

	switch valueType.Kind() {
	case reflect.Pointer, reflect.Slice, reflect.Array:
		if valueType.Elem().Kind() == reflect.Uint8 {
			return nil
		}
		return validateCBORTargetType(valueType.Elem(), seen)
	case reflect.Map:
		if err := validateCBORTargetType(valueType.Key(), seen); err != nil {
			return err
		}
		return validateCBORTargetType(valueType.Elem(), seen)
	case reflect.Struct:
		for i := 0; i < valueType.NumField(); i++ {
			field := valueType.Field(i)
			if field.PkgPath != "" || field.Tag.Get("cbor") == "-" {
				continue
			}
			if err := validateCBORTargetType(field.Type, seen); err != nil {
				return err
			}
		}
	}
	return nil
}

func implementsCodec(valueType, interfaceType reflect.Type) bool {
	if valueType.Implements(interfaceType) {
		return true
	}
	return valueType.Kind() != reflect.Pointer && reflect.PointerTo(valueType).Implements(interfaceType)
}

func validateCBORValue(value reflect.Value, depth int, active map[visit]struct{}) error {
	if !value.IsValid() {
		return nil
	}
	if value.Kind() == reflect.Interface {
		if value.IsNil() {
			return nil
		}
		return validateCBORValue(value.Elem(), depth, active)
	}
	if value.Kind() == reflect.Pointer {
		if value.IsNil() {
			// Nested nil pointers are the strongly typed representation of a
			// protocol-level CBOR null. The root value remains non-null.
			return nil
		}
		key := visit{typeOf: value.Type(), ptr: value.Pointer()}
		if _, exists := active[key]; exists {
			return reject(CodeCBORInvalid, "value", errors.New("cyclic value"))
		}
		active[key] = struct{}{}
		defer delete(active, key)
		return validateCBORValue(value.Elem(), depth, active)
	}

	if value.CanInterface() && (implementsCodec(value.Type(), cborMarshalerType) ||
		implementsCodec(value.Type(), cborUnmarshalerType)) {
		return reject(CodeCBORInvalid, "value", errors.New("custom CBOR codec forbidden"))
	}
	if value.CanInterface() && (implementsCodec(value.Type(), binaryMarshalerType) ||
		implementsCodec(value.Type(), binaryUnmarshalerType)) {
		return reject(CodeCBORInvalid, "value", errors.New("custom binary codec forbidden"))
	}
	if value.Type().PkgPath() == "github.com/fxamacker/cbor/v2" ||
		value.Type().PkgPath() == "math/big" ||
		(value.Type().PkgPath() == "time" && value.Type().Name() == "Time") {
		return reject(CodeCBORInvalid, "value", errors.New("special CBOR type forbidden"))
	}

	switch value.Kind() {
	case reflect.Float32, reflect.Float64:
		return reject(CodeCBORInvalid, "float", nil)
	case reflect.Complex64, reflect.Complex128, reflect.Chan, reflect.Func, reflect.UnsafePointer:
		return reject(CodeCBORInvalid, "value", errors.New("unsupported Go type"))
	case reflect.String:
		if !utf8.ValidString(value.String()) {
			return reject(CodeCBORInvalid, "text", nil)
		}
		return nil
	case reflect.Struct:
		if depth+1 > MaxCBORNesting {
			return reject(CodeResourceLimit, "cborNesting", nil)
		}
		exportedFields := 0
		for i := 0; i < value.NumField(); i++ {
			field := value.Type().Field(i)
			if field.PkgPath != "" { // unexported fields aren't encoded
				continue
			}
			if field.Tag.Get("cbor") == "-" {
				continue
			}
			exportedFields++
			if exportedFields > MaxCBORMapPairs {
				return reject(CodeResourceLimit, "cborMapPairs", nil)
			}
			if err := validateCBORValue(value.Field(i), depth+1, active); err != nil {
				return err
			}
		}
		return nil
	case reflect.Map:
		if value.IsNil() {
			return nil
		}
		if value.Len() > MaxCBORMapPairs {
			return reject(CodeResourceLimit, "cborMapPairs", nil)
		}
		if depth+1 > MaxCBORNesting {
			return reject(CodeResourceLimit, "cborNesting", nil)
		}
		key := visit{typeOf: value.Type(), ptr: value.Pointer()}
		if _, exists := active[key]; exists {
			return reject(CodeCBORInvalid, "value", errors.New("cyclic value"))
		}
		active[key] = struct{}{}
		defer delete(active, key)
		iterator := value.MapRange()
		for iterator.Next() {
			if err := validateCBORValue(iterator.Key(), depth+1, active); err != nil {
				return err
			}
			if err := validateCBORValue(iterator.Value(), depth+1, active); err != nil {
				return err
			}
		}
		return nil
	case reflect.Slice:
		if value.IsNil() {
			return nil
		}
		if value.Type().Elem().Kind() == reflect.Uint8 {
			return nil
		}
		return validateCBORSequence(value, depth, active)
	case reflect.Array:
		if value.Type().Elem().Kind() == reflect.Uint8 {
			return nil
		}
		return validateCBORSequence(value, depth, active)
	default:
		return nil
	}
}

func validateCBORSequence(value reflect.Value, depth int, active map[visit]struct{}) error {
	if value.Len() > MaxCBORArrayItems {
		return reject(CodeResourceLimit, "cborArrayItems", nil)
	}
	if depth+1 > MaxCBORNesting {
		return reject(CodeResourceLimit, "cborNesting", nil)
	}
	var key visit
	if value.Kind() == reflect.Slice {
		key = visit{typeOf: value.Type(), ptr: value.Pointer()}
		if _, exists := active[key]; exists {
			return reject(CodeCBORInvalid, "value", errors.New("cyclic value"))
		}
		active[key] = struct{}{}
		defer delete(active, key)
	}
	for i := 0; i < value.Len(); i++ {
		if err := validateCBORValue(value.Index(i), depth+1, active); err != nil {
			return err
		}
	}
	return nil
}
