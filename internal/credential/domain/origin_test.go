package domain

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

func TestNormalizeOriginCanonicalCases(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name string
		raw  string
		want string
	}{
		{name: "lowercase host", raw: "https://Example.COM", want: "https://example.com"},
		{name: "default slash", raw: "https://example.com/", want: "https://example.com"},
		{name: "http default port", raw: "http://Example.COM:80", want: "http://example.com"},
		{name: "https default port", raw: "HTTPS://Example.COM:443", want: "https://example.com"},
		{name: "nondefault port", raw: "https://Example.COM:8443", want: "https://example.com:8443"},
		{name: "idn lookup profile", raw: "https://BÜCHER.example:443", want: "https://xn--bcher-kva.example"},
		{name: "ipv4", raw: "http://127.0.0.1:8080", want: "http://127.0.0.1:8080"},
		{name: "ipv6 compression", raw: "https://[2001:0db8:0:0:0:0:0:1]:443", want: "https://[2001:db8::1]"},
	}

	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			origin, err := NormalizeOrigin(test.raw)
			if err != nil {
				t.Fatalf("NormalizeOrigin() error = %v", err)
			}
			defer origin.Destroy()
			if got := originCanonicalForTest(t, origin); got != test.want {
				t.Fatalf("canonical = %q, want %q", got, test.want)
			}

			roundTrip, err := NormalizeOrigin(test.want)
			if err != nil {
				t.Fatalf("canonical value did not parse: %v", err)
			}
			defer roundTrip.Destroy()
			if !origin.Equal(roundTrip) {
				t.Fatal("canonical round trip changed the origin")
			}
		})
	}
}

func TestNormalizeOriginRejectsNonOrigins(t *testing.T) {
	t.Parallel()
	invalid := []string{
		"",
		" example.com",
		"example.com",
		"//example.com",
		"ftp://example.com",
		"javascript:alert(1)",
		"http:example.com",
		"https://",
		"https://user@example.com",
		"https://user:password@example.com",
		"https://example.com:",
		"https://example.com:65536",
		"https://example.com:not-a-port",
		"https://example.com:0",
		"https://2001:db8::1",
		"https://[not-ipv6]",
		"https://[fe80::1%25eth0]",
		"https://example.com/path",
		"https://example.com//",
		"https://example.com?",
		"https://example.com?query=value",
		"https://example.com#",
		"https://example.com#fragment",
		"https://exa_mple.com",
		"https://-example.com",
		"https://example-.com",
		"https://example..com",
		"https://example.com.",
		"https://127.000.0.1",
		"https://\u200d.example",
	}

	for _, raw := range invalid {
		raw := raw
		t.Run(fmt.Sprintf("case_%d", len(raw)), func(t *testing.T) {
			t.Parallel()
			origin, err := NormalizeOrigin(raw)
			if !errors.Is(err, ErrInvalidOrigin) {
				origin.Destroy()
				t.Fatalf("NormalizeOrigin() error = %v, want ErrInvalidOrigin", err)
			}
			if !origin.IsZero() {
				t.Fatal("rejected input returned a live origin")
			}
		})
	}
}

func TestCanonicalOriginFixedVectors(t *testing.T) {
	t.Parallel()
	type validVector struct {
		Input             string `json:"input"`
		AllowLoopbackHTTP bool   `json:"allowLoopbackHttp"`
		Canonical         string `json:"canonical"`
	}
	var vectors struct {
		Valid   []validVector `json:"valid"`
		Invalid []string      `json:"invalid"`
	}
	_, source, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("resolve test source")
	}
	path := filepath.Join(
		filepath.Dir(source), "..", "..", "..",
		"specs", "001-vdns-audit-rotation", "canonical-origin-vectors.json",
	)
	content, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := json.Unmarshal(content, &vectors); err != nil {
		t.Fatal(err)
	}
	for _, vector := range vectors.Valid {
		origin, err := NormalizeOrigin(vector.Input)
		if err != nil {
			t.Fatalf("valid vector %q: %v", vector.Input, err)
		}
		if !originAllowedByTransport(origin, vector.AllowLoopbackHTTP) {
			origin.Destroy()
			t.Fatalf("valid vector transport %q", vector.Input)
		}
		if got := originCanonicalForTest(t, origin); got != vector.Canonical {
			origin.Destroy()
			t.Fatalf("vector %q=%q want=%q", vector.Input, got, vector.Canonical)
		}
		origin.Destroy()
	}
	for _, raw := range vectors.Invalid {
		origin, err := NormalizeOrigin(raw)
		if err == nil && originAllowedByTransport(origin, false) {
			origin.Destroy()
			t.Fatalf("invalid vector accepted: %q", raw)
		}
		origin.Destroy()
	}
}

func TestOriginDoesNotLeakThroughFormattingJSONOrLogging(t *testing.T) {
	t.Parallel()
	const raw = "https://private-account.example:8443"
	origin, err := NormalizeOrigin(raw)
	if err != nil {
		t.Fatal(err)
	}
	defer origin.Destroy()

	for _, rendered := range []string{
		fmt.Sprintf("%s", origin),
		fmt.Sprintf("%v", origin),
		fmt.Sprintf("%+v", origin),
		fmt.Sprintf("%#v", origin),
		fmt.Sprintf("%q", origin),
	} {
		if strings.Contains(rendered, "private-account") || rendered != redactedOrigin {
			t.Fatalf("unsafe formatted representation: %q", rendered)
		}
	}

	encoded, err := json.Marshal(struct {
		Origin Origin `json:"origin"`
	}{Origin: origin})
	if err == nil {
		t.Fatal("json.Marshal unexpectedly succeeded")
	}
	if bytes.Contains(encoded, []byte("private-account")) || strings.Contains(err.Error(), "private-account") {
		t.Fatal("JSON path disclosed the origin")
	}

	var log bytes.Buffer
	logger := slog.New(slog.NewTextHandler(&log, nil))
	logger.Info("origin test", "origin", origin)
	if strings.Contains(log.String(), "private-account") || !strings.Contains(log.String(), redactedOrigin) {
		t.Fatalf("unsafe structured log: %q", log.String())
	}
}

func TestOriginExplicitUseCopiesAndDestroyInvalidatesCopies(t *testing.T) {
	t.Parallel()
	origin, err := NormalizeOrigin("https://secret.example")
	if err != nil {
		t.Fatal(err)
	}
	copyOfOrigin := origin

	err = origin.UseCanonical(func(value []byte) error {
		clear(value)
		return nil
	})
	if err != nil {
		t.Fatal(err)
	}
	if got := originCanonicalForTest(t, origin); got != "https://secret.example" {
		t.Fatal("consumer mutation changed the protected value")
	}

	origin.Destroy()
	if !copyOfOrigin.IsZero() {
		t.Fatal("destroying one copy did not invalidate the other")
	}
	if err := copyOfOrigin.UseCanonical(func([]byte) error { return nil }); !errors.Is(err, ErrOriginDestroyed) {
		t.Fatalf("use after destroy error = %v", err)
	}
}

func originCanonicalForTest(t *testing.T, origin Origin) string {
	t.Helper()
	var result string
	if err := origin.UseCanonical(func(value []byte) error {
		result = string(value)
		return nil
	}); err != nil {
		t.Fatalf("UseCanonical() error = %v", err)
	}
	return result
}

func FuzzNormalizeOrigin(f *testing.F) {
	for _, seed := range []string{
		"https://example.com",
		"HTTPS://BÜCHER.example:443/",
		"http://[::1]:8080",
		"https://user@example.com",
		"https://example.com/path?query#fragment",
		"\x00",
	} {
		f.Add(seed)
	}

	f.Fuzz(func(t *testing.T, raw string) {
		origin, err := NormalizeOrigin(raw)
		if err != nil {
			return
		}
		defer origin.Destroy()
		canonical := originCanonicalForTest(t, origin)
		roundTrip, err := NormalizeOrigin(canonical)
		if err != nil {
			t.Fatal("successful result was not itself a valid origin")
		}
		defer roundTrip.Destroy()
		if !origin.Equal(roundTrip) {
			t.Fatal("successful normalization was not idempotent")
		}
	})
}
