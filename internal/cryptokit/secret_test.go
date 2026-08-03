package cryptokit

import (
	"encoding/json"
	"fmt"
	"log"
	"log/slog"
	"strings"
	"testing"
)

func TestSecretDoesNotLeakThroughFormattingOrJSON(t *testing.T) {
	t.Parallel()

	const sample = "vpass-super-secret-sample"
	secret, err := NewSecret([]byte(sample))
	if err != nil {
		t.Fatalf("NewSecret: %v", err)
	}
	t.Cleanup(secret.Destroy)

	value := *secret
	formatted := []string{
		fmt.Sprint(secret),
		fmt.Sprint(value),
		fmt.Sprintf("%s", secret),
		fmt.Sprintf("%s", value),
		fmt.Sprintf("%q", secret),
		fmt.Sprintf("%q", value),
		fmt.Sprintf("%x", secret),
		fmt.Sprintf("%x", value),
		fmt.Sprintf("%+v", secret),
		fmt.Sprintf("%+v", value),
		fmt.Sprintf("%#v", secret),
		fmt.Sprintf("%#v", value),
		strings.Join([]string{"command", fmt.Sprint(secret)}, " "),
		strings.Join([]string{"VPASS_SECRET=" + fmt.Sprint(secret)}, " "),
	}
	for _, output := range formatted {
		if strings.Contains(output, sample) {
			t.Fatalf("formatted output leaked secret: %q", output)
		}
		if !strings.Contains(output, redactedSecret) {
			t.Fatalf("formatted output did not contain redaction: %q", output)
		}
	}

	var logOutput strings.Builder
	logger := log.New(&logOutput, "", 0)
	logger.Printf("secret=%v", secret)
	if strings.Contains(logOutput.String(), sample) {
		t.Fatalf("log output leaked secret: %q", logOutput.String())
	}
	var slogOutput strings.Builder
	slogger := slog.New(slog.NewTextHandler(&slogOutput, nil))
	slogger.Info("secret test", "pointer", secret, "value", value)
	if strings.Contains(slogOutput.String(), sample) || !strings.Contains(slogOutput.String(), redactedSecret) {
		t.Fatalf("slog output was unsafe: %q", slogOutput.String())
	}

	encoded, err := json.Marshal(secret)
	if err == nil || encoded != nil {
		t.Fatalf("json.Marshal = %q, %v; want refusal", encoded, err)
	}
	if strings.Contains(err.Error(), sample) {
		t.Fatalf("JSON error leaked secret: %v", err)
	}
	if encoded, err = json.Marshal(value); err == nil || encoded != nil {
		t.Fatalf("json.Marshal(value) = %q, %v; want refusal", encoded, err)
	}
}

func TestSecretDestroyClearsOwnedBufferAndPreventsUse(t *testing.T) {
	t.Parallel()

	input := []byte("owned-secret")
	secret, err := NewSecret(input)
	if err != nil {
		t.Fatalf("NewSecret: %v", err)
	}
	input[0] = 'X'

	var observed []byte
	if err := secret.withBytes(func(value []byte) error {
		observed = append(observed, value...)
		return nil
	}); err != nil {
		t.Fatalf("withBytes: %v", err)
	}
	if got, want := string(observed), "owned-secret"; got != want {
		t.Fatalf("owned copy = %q, want %q", got, want)
	}

	copyHandle := *secret
	backing := secret.state.material
	secret.Destroy()
	for i, value := range backing {
		if value != 0 {
			t.Fatalf("owned buffer byte %d was not cleared", i)
		}
	}
	if secret.Len() != 0 {
		t.Fatalf("Len after Destroy = %d, want 0", secret.Len())
	}
	if err := secret.withBytes(func([]byte) error { return nil }); err != ErrSecretDestroyed {
		t.Fatalf("withBytes after Destroy = %v, want %v", err, ErrSecretDestroyed)
	}
	if err := copyHandle.withBytes(func([]byte) error { return nil }); err != ErrSecretDestroyed {
		t.Fatalf("copied handle after Destroy = %v, want %v", err, ErrSecretDestroyed)
	}

	secret.Destroy()
}

func TestKeyDoesNotLeakAndDestroys(t *testing.T) {
	t.Parallel()

	material := []byte("0123456789abcdef0123456789abcdef")
	key, err := NewKey(material)
	if err != nil {
		t.Fatalf("NewKey: %v", err)
	}
	value := *key
	for _, output := range []string{
		fmt.Sprintf("%v", key), fmt.Sprintf("%v", value),
		fmt.Sprintf("%+v", key), fmt.Sprintf("%+v", value),
		fmt.Sprintf("%#v", key), fmt.Sprintf("%#v", value),
		fmt.Sprintf("%x", key), fmt.Sprintf("%x", value),
	} {
		if strings.Contains(output, string(material)) || !strings.Contains(output, redactedSecret) {
			t.Fatalf("key formatting was unsafe: %q", output)
		}
	}
	var slogOutput strings.Builder
	slogger := slog.New(slog.NewJSONHandler(&slogOutput, nil))
	slogger.Info("key test", "pointer", key, "value", value)
	if strings.Contains(slogOutput.String(), string(material)) || !strings.Contains(slogOutput.String(), redactedSecret) {
		t.Fatalf("key slog output was unsafe: %q", slogOutput.String())
	}
	if _, err := json.Marshal(key); err == nil {
		t.Fatal("json.Marshal(key) succeeded; want refusal")
	}
	if _, err := json.Marshal(value); err == nil {
		t.Fatal("json.Marshal(key value) succeeded; want refusal")
	}

	key.Destroy()
	for i, value := range key.state.material {
		if value != 0 {
			t.Fatalf("key byte %d was not cleared", i)
		}
	}
	if err := key.withPurposeBytes(purposeUnscoped, func([]byte) error { return nil }); err != ErrSecretDestroyed {
		t.Fatalf("key use after Destroy = %v, want %v", err, ErrSecretDestroyed)
	}
}

func TestSecretRejectsEmptyAndKeyRejectsWrongLength(t *testing.T) {
	t.Parallel()

	if _, err := NewSecret(nil); err != ErrInvalidInput {
		t.Fatalf("NewSecret(nil) = %v, want %v", err, ErrInvalidInput)
	}
	if _, err := NewKey(make([]byte, KeySize-1)); err != ErrInvalidInput {
		t.Fatalf("NewKey(short) = %v, want %v", err, ErrInvalidInput)
	}
}
