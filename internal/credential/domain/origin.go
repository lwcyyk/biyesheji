// Package domain contains credential-domain values and invariants.
package domain

import (
	"crypto/subtle"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net"
	"net/url"
	"strconv"
	"strings"
	"sync"
	"unicode/utf8"

	"golang.org/x/net/idna"
)

const (
	redactedOrigin = "[REDACTED ORIGIN]"
	maxOriginBytes = 2048
)

var (
	// ErrInvalidOrigin is deliberately non-specific so parsing errors cannot
	// accidentally echo a sensitive origin into logs.
	ErrInvalidOrigin = errors.New("invalid origin")

	// ErrOriginDestroyed reports an attempted use after the value was erased.
	ErrOriginDestroyed = errors.New("origin is unavailable")

	// ErrOriginSerialization prevents accidental JSON or text disclosure.
	ErrOriginSerialization = errors.New("origin cannot be serialized implicitly")
)

// Origin is a normalized RFC 6454 scheme/host/port tuple.  Its representation
// is intentionally hidden: callers must use UseCanonical to cross an explicit
// secret-handling boundary.
//
// Copies of Origin refer to the same state, so destroying any copy invalidates
// all copies and erases the shared byte buffer.
type Origin struct {
	state *originState
}

type originState struct {
	mu        sync.RWMutex
	canonical []byte
	destroyed bool
}

// NormalizeOrigin parses and canonicalizes a pure HTTP(S) origin.  A single
// trailing slash is accepted as the URL parser's default path, but no path,
// query, fragment, user information, or opaque form is retained.
func NormalizeOrigin(raw string) (Origin, error) {
	if raw == "" || len(raw) > maxOriginBytes || !utf8.ValidString(raw) || strings.TrimSpace(raw) != raw {
		return Origin{}, ErrInvalidOrigin
	}
	// Bare delimiters are otherwise indistinguishable from empty values in
	// parts of net/url's parsed representation.
	if strings.ContainsAny(raw, "?#") {
		return Origin{}, ErrInvalidOrigin
	}

	u, err := url.Parse(raw)
	if err != nil || u == nil || u.Opaque != "" || u.User != nil {
		return Origin{}, ErrInvalidOrigin
	}
	if u.RawPath != "" || (u.Path != "" && u.Path != "/") || u.RawQuery != "" || u.ForceQuery || u.Fragment != "" || u.RawFragment != "" {
		return Origin{}, ErrInvalidOrigin
	}

	scheme := strings.ToLower(u.Scheme)
	if scheme != "http" && scheme != "https" {
		return Origin{}, ErrInvalidOrigin
	}
	if u.Host == "" || strings.Contains(u.Host, "%") {
		return Origin{}, ErrInvalidOrigin
	}

	host, bracketed, explicitPort, err := splitOriginAuthority(u.Host)
	if err != nil {
		return Origin{}, ErrInvalidOrigin
	}
	host, isIPv6, err := normalizeOriginHost(host, bracketed)
	if err != nil {
		return Origin{}, ErrInvalidOrigin
	}

	port, err := normalizeOriginPort(explicitPort)
	if err != nil {
		return Origin{}, ErrInvalidOrigin
	}
	hasPort := explicitPort != ""
	if (scheme == "http" && port == 80) || (scheme == "https" && port == 443) {
		hasPort = false
	}

	var b strings.Builder
	b.Grow(len(scheme) + len(host) + 12)
	b.WriteString(scheme)
	b.WriteString("://")
	if isIPv6 {
		b.WriteByte('[')
		b.WriteString(host)
		b.WriteByte(']')
	} else {
		b.WriteString(host)
	}
	if hasPort {
		b.WriteByte(':')
		b.WriteString(strconv.FormatUint(uint64(port), 10))
	}

	canonical := []byte(b.String())
	return Origin{state: &originState{canonical: canonical}}, nil
}

// splitOriginAuthority separates a syntactically valid URI host and optional
// port while rejecting empty ports and unbracketed IPv6 literals.
func splitOriginAuthority(authority string) (host string, bracketed bool, port string, err error) {
	if strings.HasPrefix(authority, "[") {
		closeBracket := strings.IndexByte(authority, ']')
		if closeBracket <= 1 {
			return "", false, "", ErrInvalidOrigin
		}
		host = authority[1:closeBracket]
		remainder := authority[closeBracket+1:]
		switch {
		case remainder == "":
			return host, true, "", nil
		case strings.HasPrefix(remainder, ":") && len(remainder) > 1:
			return host, true, remainder[1:], nil
		default:
			return "", false, "", ErrInvalidOrigin
		}
	}

	colonCount := strings.Count(authority, ":")
	if colonCount > 1 {
		return "", false, "", ErrInvalidOrigin
	}
	if colonCount == 1 {
		parts := strings.SplitN(authority, ":", 2)
		if parts[0] == "" || parts[1] == "" {
			return "", false, "", ErrInvalidOrigin
		}
		return parts[0], false, parts[1], nil
	}
	return authority, false, "", nil
}

func normalizeOriginHost(host string, bracketed bool) (normalized string, isIPv6 bool, err error) {
	if host == "" || strings.HasSuffix(host, ".") {
		return "", false, ErrInvalidOrigin
	}
	if ip := net.ParseIP(host); ip != nil {
		if ip4 := ip.To4(); ip4 != nil {
			if bracketed {
				return "", false, ErrInvalidOrigin
			}
			return ip4.String(), false, nil
		}
		if !bracketed {
			return "", false, ErrInvalidOrigin
		}
		return ip.String(), true, nil
	}
	if bracketed {
		return "", false, ErrInvalidOrigin
	}
	allNumericDots := true
	for _, current := range host {
		if (current < '0' || current > '9') && current != '.' {
			allNumericDots = false
			break
		}
	}
	if allNumericDots {
		// An IPv4-looking name that net.ParseIP rejected must not fall back to
		// a DNS name with browser-dependent octal/short-address semantics.
		return "", false, ErrInvalidOrigin
	}

	ascii, err := idna.Lookup.ToASCII(host)
	if err != nil {
		return "", false, ErrInvalidOrigin
	}
	ascii = strings.ToLower(ascii)
	if !validASCIIDomain(ascii) {
		return "", false, ErrInvalidOrigin
	}
	return ascii, false, nil
}

func validASCIIDomain(host string) bool {
	if host == "" {
		return false
	}
	withoutRootDot := strings.TrimSuffix(host, ".")
	if withoutRootDot == "" || len(withoutRootDot) > 253 {
		return false
	}
	for _, label := range strings.Split(withoutRootDot, ".") {
		if len(label) == 0 || len(label) > 63 || label[0] == '-' || label[len(label)-1] == '-' {
			return false
		}
		for i := 0; i < len(label); i++ {
			c := label[i]
			if (c < 'a' || c > 'z') && (c < '0' || c > '9') && c != '-' {
				return false
			}
		}
	}
	return true
}

func normalizeOriginPort(port string) (uint16, error) {
	if port == "" {
		return 0, nil
	}
	parsed, err := strconv.ParseUint(port, 10, 16)
	if err != nil || parsed == 0 {
		return 0, ErrInvalidOrigin
	}
	return uint16(parsed), nil
}

// UseCanonical provides a temporary copy of the normalized bytes to an
// explicit secret consumer.  The copy is erased immediately after fn returns.
func (o Origin) UseCanonical(fn func([]byte) error) error {
	if fn == nil {
		return ErrInvalidOrigin
	}
	canonical, err := o.canonicalCopy()
	if err != nil {
		return err
	}
	defer clear(canonical)
	return fn(canonical)
}

func (o Origin) canonicalCopy() ([]byte, error) {
	if o.state == nil {
		return nil, ErrOriginDestroyed
	}
	o.state.mu.RLock()
	defer o.state.mu.RUnlock()
	if o.state.destroyed || len(o.state.canonical) == 0 {
		return nil, ErrOriginDestroyed
	}
	return append([]byte(nil), o.state.canonical...), nil
}

// Equal compares two live normalized origins without disclosing either value.
func (o Origin) Equal(other Origin) bool {
	left, err := o.canonicalCopy()
	if err != nil {
		return false
	}
	defer clear(left)
	right, err := other.canonicalCopy()
	if err != nil {
		return false
	}
	defer clear(right)
	return len(left) == len(right) && subtle.ConstantTimeCompare(left, right) == 1
}

// Destroy erases the canonical buffer and invalidates every copy of o.
func (o Origin) Destroy() {
	if o.state == nil {
		return
	}
	o.state.mu.Lock()
	defer o.state.mu.Unlock()
	clear(o.state.canonical)
	o.state.canonical = nil
	o.state.destroyed = true
}

// IsZero reports whether the value was never initialized or was destroyed.
func (o Origin) IsZero() bool {
	if o.state == nil {
		return true
	}
	o.state.mu.RLock()
	defer o.state.mu.RUnlock()
	return o.state.destroyed || len(o.state.canonical) == 0
}

func (Origin) String() string   { return redactedOrigin }
func (Origin) GoString() string { return redactedOrigin }

// Format prevents alternate fmt verbs (including %#v and %q) from bypassing
// the redacted String representation.
func (Origin) Format(state fmt.State, _ rune) {
	_, _ = io.WriteString(state, redactedOrigin)
}

// LogValue prevents structured logging from reflecting private fields.
func (Origin) LogValue() slog.Value { return slog.StringValue(redactedOrigin) }

// MarshalJSON refuses implicit public serialization.
func (Origin) MarshalJSON() ([]byte, error) { return nil, ErrOriginSerialization }

// UnmarshalJSON forces callers through NormalizeOrigin and its validation.
func (*Origin) UnmarshalJSON([]byte) error { return ErrOriginSerialization }

// MarshalText refuses implicit serialization by configuration and logging
// libraries that consult encoding.TextMarshaler.
func (Origin) MarshalText() ([]byte, error) { return nil, ErrOriginSerialization }

var (
	_ fmt.Stringer   = Origin{}
	_ fmt.GoStringer = Origin{}
	_ slog.LogValuer = Origin{}
	_ json.Marshaler = Origin{}
)
