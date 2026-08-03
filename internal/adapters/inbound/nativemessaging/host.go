// Package nativemessaging implements Chrome's length-prefixed Native
// Messaging protocol. It is the only adapter allowed to receive plaintext
// secure-input values or release a one-use autofill value.
package nativemessaging

import (
	"bufio"
	"bytes"
	"encoding/binary"
	"encoding/json"
	"errors"
	"io"
	"regexp"
	"strings"

	localapp "vpass.local/vpass/internal/localapi/application"
)

const maxMessageBytes = 1024 * 1024

var loopbackBaseURL = regexp.MustCompile(`^http://127\.0\.0\.1:([1-9][0-9]{0,4})$`)

type Config struct {
	BaseURL      string
	InstallToken string
}

type Host struct {
	localClient *localapp.LocalSecureClient
	config      Config
}

type request struct {
	RequestID        string `json:"requestId"`
	Command          string `json:"command"`
	DeviceID         string `json:"deviceId,omitempty"`
	NamespaceID      string `json:"namespaceId,omitempty"`
	SessionID        string `json:"sessionId,omitempty"`
	Origin           string `json:"origin,omitempty"`
	AccountID        string `json:"accountId,omitempty"`
	FieldType        string `json:"fieldType,omitempty"`
	SecretHandle     string `json:"secretHandle,omitempty"`
	SecretValue      string `json:"secretValue,omitempty"`
	CredentialID     string `json:"credentialId,omitempty"`
	CandidateVersion uint64 `json:"candidateVersion,omitempty"`
	ResultReference  string `json:"resultReference,omitempty"`
	Cursor           string `json:"cursor,omitempty"`
	Limit            int    `json:"limit,omitempty"`
}

type response struct {
	RequestID    string `json:"requestId"`
	OK           bool   `json:"ok"`
	Code         string `json:"code,omitempty"`
	BaseURL      string `json:"baseURL,omitempty"`
	InstallToken string `json:"installToken,omitempty"`
	SecretHandle string `json:"secretHandle,omitempty"`
	SecretValue  string `json:"secretValue,omitempty"`
	Result       any    `json:"result,omitempty"`
}

func New(localClient *localapp.LocalSecureClient, config Config) (*Host, error) {
	match := loopbackBaseURL.FindStringSubmatch(config.BaseURL)
	if localClient == nil || match == nil || len(config.InstallToken) < 32 ||
		len(config.InstallToken) > 512 || strings.ContainsAny(config.InstallToken, "\r\n") {
		return nil, errors.New("invalid Native Messaging configuration")
	}
	return &Host{localClient: localClient, config: config}, nil
}

// Run processes a persistent Native Messaging connection. It emits no logs;
// callers must use process exit status and stable response codes.
func (host *Host) Run(input io.Reader, output io.Writer) error {
	if host == nil || input == nil || output == nil {
		return errors.New("invalid Native Messaging channel")
	}
	reader := bufio.NewReader(input)
	for {
		message, err := readFrame(reader)
		if errors.Is(err, io.EOF) {
			return nil
		}
		if err != nil {
			return err
		}
		reply := host.Handle(message)
		clear(message)
		if err := writeFrame(output, reply); err != nil {
			clear(reply)
			return err
		}
		clear(reply)
	}
}

// Handle validates one request and always returns a secret-free error. The
// success value for consumeSecretHandle is intentionally short-lived and is
// cleared after frame serialization by Run.
func (host *Host) Handle(message []byte) []byte {
	var input request
	decoder := json.NewDecoder(bytes.NewReader(message))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&input); err != nil || input.RequestID == "" ||
		len(input.RequestID) > 128 || input.Command == "" {
		return marshalResponse(response{RequestID: safeRequestID(input.RequestID), Code: "NATIVE_REQUEST_REJECTED"})
	}
	var trailing any
	if decoder.Decode(&trailing) != io.EOF {
		return marshalResponse(response{RequestID: safeRequestID(input.RequestID), Code: "NATIVE_REQUEST_REJECTED"})
	}
	secretBytes := []byte(input.SecretValue)
	input.SecretValue = ""
	defer clear(secretBytes)

	result := response{RequestID: input.RequestID}
	switch input.Command {
	case "connectionInfo":
		if len(secretBytes) != 0 {
			result.Code = "NATIVE_REQUEST_REJECTED"
			break
		}
		result.OK = true
		result.BaseURL = host.config.BaseURL
		result.InstallToken = host.config.InstallToken
	case "stageMasterPassword":
		handle, err := host.localClient.StageMasterPassword(input.DeviceID, secretBytes)
		if err != nil {
			result.Code = stableCode(err)
			break
		}
		result.OK, result.SecretHandle = true, handle
	case "stageRecoverySecret":
		handle, err := host.localClient.StageRecoverySecret(input.NamespaceID, input.DeviceID, secretBytes)
		if err != nil {
			result.Code = stableCode(err)
			break
		}
		result.OK, result.SecretHandle = true, handle
	case "stageCredentialField":
		handle, err := host.localClient.StageCredentialField(
			input.SessionID, input.Origin, input.AccountID, input.FieldType, secretBytes,
		)
		if err != nil {
			result.Code = stableCode(err)
			break
		}
		result.OK, result.SecretHandle = true, handle
	case "stageAuditAnalysisSecret":
		handle, err := host.localClient.StageAuditAnalysisSecret(input.SessionID, secretBytes)
		if err != nil {
			result.Code = stableCode(err)
			break
		}
		result.OK, result.SecretHandle = true, handle
	case "consumeSecretHandle":
		if len(secretBytes) != 0 {
			result.Code = "NATIVE_REQUEST_REJECTED"
			break
		}
		var exposed []byte
		err := host.localClient.ConsumeNativeHandle(
			input.SessionID, input.SecretHandle, input.Origin, input.FieldType,
			func(value []byte) error {
				exposed = append(exposed, value...)
				return nil
			},
		)
		if err != nil {
			clear(exposed)
			result.Code = stableCode(err)
			break
		}
		result.OK, result.SecretValue = true, string(exposed)
		clear(exposed)
	case "authorizeCandidateField":
		if len(secretBytes) != 0 {
			result.Code = "NATIVE_REQUEST_REJECTED"
			break
		}
		handle, fault := host.localClient.AuthorizeCandidateField(
			input.SessionID, input.CredentialID, input.CandidateVersion,
			input.Origin, input.FieldType,
		)
		if fault != nil {
			result.Code = fault.Code
			break
		}
		result.OK, result.SecretHandle = true, handle.SecretHandle
	case "readSecurityAnalysisResult":
		if len(secretBytes) != 0 {
			result.Code = "NATIVE_REQUEST_REJECTED"
			break
		}
		page, fault := host.localClient.ListSecurityFindings(
			input.SessionID, input.ResultReference, input.Cursor, input.Limit,
		)
		if fault != nil {
			result.Code = fault.Code
			break
		}
		result.OK, result.Result = true, page
	default:
		result.Code = "NATIVE_COMMAND_REJECTED"
	}
	return marshalResponse(result)
}

func readFrame(reader io.Reader) ([]byte, error) {
	var size uint32
	if err := binary.Read(reader, binary.LittleEndian, &size); err != nil {
		return nil, err
	}
	if size == 0 || size > maxMessageBytes {
		return nil, errors.New("invalid Native Messaging frame size")
	}
	message := make([]byte, size)
	if _, err := io.ReadFull(reader, message); err != nil {
		clear(message)
		return nil, err
	}
	return message, nil
}

func writeFrame(writer io.Writer, message []byte) error {
	if len(message) == 0 || len(message) > maxMessageBytes {
		return errors.New("invalid Native Messaging response size")
	}
	if err := binary.Write(writer, binary.LittleEndian, uint32(len(message))); err != nil {
		return err
	}
	_, err := writer.Write(message)
	return err
}

func marshalResponse(value response) []byte {
	encoded, err := json.Marshal(value)
	value.InstallToken = ""
	value.SecretHandle = ""
	value.SecretValue = ""
	value.Result = nil
	if err != nil {
		return []byte(`{"requestId":"invalid","ok":false,"code":"NATIVE_RESPONSE_FAILED"}`)
	}
	return encoded
}

func safeRequestID(value string) string {
	if value == "" || len(value) > 128 {
		return "invalid"
	}
	for _, current := range value {
		if current < 0x21 || current > 0x7e {
			return "invalid"
		}
	}
	return value
}

func stableCode(err error) string {
	var fault *localapp.Fault
	if errors.As(err, &fault) && fault.Code != "" {
		return fault.Code
	}
	return "NATIVE_OPERATION_REJECTED"
}
