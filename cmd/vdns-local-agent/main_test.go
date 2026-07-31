package main

import (
	"encoding/base64"
	"os"
	"path/filepath"
	"testing"
)

func TestRestrictedSecretFile(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "secret")
	value := make([]byte, 32)
	for index := range value {
		value[index] = byte(index + 1)
	}
	if err := os.WriteFile(path, []byte(base64.RawURLEncoding.EncodeToString(value)+"\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	loaded, err := readRestrictedBase64Secret(path, 32)
	if err != nil || len(loaded) != 32 {
		t.Fatalf("load = %d, %v", len(loaded), err)
	}
	if err := os.Chmod(path, 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := readRestrictedBase64Secret(path, 32); err == nil {
		t.Fatal("world-readable secret file accepted")
	}
}

func TestExtensionIDAndStableStartupErrors(t *testing.T) {
	t.Parallel()
	if !validExtensionID("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa") ||
		validExtensionID("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz") {
		t.Fatal("extension ID validation mismatch")
	}
	if stableStartupError(&pathError{}) != "startup rejected" {
		t.Fatal("startup error exposed a path")
	}
}

type pathError struct{}

func (*pathError) Error() string { return "open /sensitive/path: failed" }
