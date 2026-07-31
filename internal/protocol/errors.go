package protocol

import (
	"errors"
	"fmt"
)

// ErrorCode is a stable, machine-readable protocol rejection reason.
type ErrorCode string

const (
	CodeInvalidInput        ErrorCode = "REJECT_INVALID_INPUT"
	CodeInvalidID           ErrorCode = "REJECT_INVALID_ID"
	CodeInsecureRandom      ErrorCode = "REJECT_INSECURE_RANDOM"
	CodeResourceLimit       ErrorCode = "REJECT_RESOURCE_LIMIT"
	CodeCBORInvalid         ErrorCode = "REJECT_CBOR_INVALID"
	CodeCBORNonCanonical    ErrorCode = "REJECT_CBOR_NON_CANONICAL"
	CodeUnsupportedProtocol ErrorCode = "REJECT_UNSUPPORTED_PROTOCOL"
	CodeUnsupportedSuite    ErrorCode = "REJECT_UNSUPPORTED_SUITE"
	CodeUnsupportedObject   ErrorCode = "REJECT_UNSUPPORTED_OBJECT_TYPE"
	CodeContextMismatch     ErrorCode = "REJECT_CONTEXT_MISMATCH"
	CodeInvalidKey          ErrorCode = "REJECT_INVALID_KEY"
	CodeInvalidSignature    ErrorCode = "REJECT_BAD_SIGNATURE"
)

// Error carries a stable code without exposing secret or attacker-controlled
// bytes in its text form.
type Error struct {
	Code  ErrorCode
	Field string
	Cause error
}

func (e *Error) Error() string {
	if e == nil {
		return "<nil>"
	}
	if e.Field == "" {
		return string(e.Code)
	}
	return fmt.Sprintf("%s: %s", e.Code, e.Field)
}

func (e *Error) Unwrap() error {
	if e == nil {
		return nil
	}
	return e.Cause
}

// CodeOf returns the stable code in err's chain.
func CodeOf(err error) (ErrorCode, bool) {
	var protocolErr *Error
	if !errors.As(err, &protocolErr) {
		return "", false
	}
	return protocolErr.Code, true
}

func reject(code ErrorCode, field string, cause error) error {
	return &Error{Code: code, Field: field, Cause: cause}
}
