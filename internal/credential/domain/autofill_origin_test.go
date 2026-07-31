package domain

import (
	"errors"
	"testing"

	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

func TestAuthorizeAutofillRouteCanonicalTopFrame(t *testing.T) {
	nameKey := testOriginNameKey(t)
	origin, _ := NormalizeOrigin("https://xn--bcher-kva.example")
	expected, err := ComputeOriginBinding(nameKey, origin, []byte("alice"))
	origin.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	request := autofillRequest(expected)
	authorization, err := AuthorizeAutofillRoute(
		nameKey,
		TrustedFrameContext{
			TopFrameOrigin: "HTTPS://BÜCHER.example:443/",
			TargetOrigin:   "https://xn--bcher-kva.example",
			IsTopFrame:     true,
		},
		request,
		FrameAuthorizationPolicy{},
	)
	if err != nil {
		t.Fatal(err)
	}
	if authorization.CredentialID != request.ResolvedCredentialID ||
		authorization.OriginBinding != expected {
		t.Fatal("authorization changed the locally resolved route")
	}
}

func TestAuthorizeAutofillRouteRejectsOpaqueAndUntrustedSchemes(t *testing.T) {
	nameKey := testOriginNameKey(t)
	expected := sessionBytes32(31)
	request := autofillRequest(expected)
	invalid := []string{
		"", "null", "data:text/html,hello", "about:blank",
		"blob:https://example.test/id", "javascript:alert(1)",
		"http://public.example",
	}
	for _, raw := range invalid {
		t.Run(raw, func(t *testing.T) {
			if result, err := AuthorizeAutofillRoute(
				nameKey,
				TrustedFrameContext{TopFrameOrigin: raw, TargetOrigin: raw, IsTopFrame: true},
				request,
				FrameAuthorizationPolicy{},
			); result != (AutofillAuthorization{}) || !errors.Is(err, ErrAutofillOriginRejected) {
				t.Fatalf("origin %q = %#v, %v", raw, result, err)
			}
		})
	}
}

func TestAuthorizeAutofillRouteIframePolicy(t *testing.T) {
	nameKey := testOriginNameKey(t)
	origin, _ := NormalizeOrigin("https://example.test")
	expected, _ := ComputeOriginBinding(nameKey, origin, []byte("alice"))
	origin.Destroy()
	request := autofillRequest(expected)
	frame := TrustedFrameContext{
		TopFrameOrigin: "https://example.test",
		TargetOrigin:   "https://example.test:443",
		IsTopFrame:     false,
	}
	if _, err := AuthorizeAutofillRoute(nameKey, frame, request, FrameAuthorizationPolicy{}); !errors.Is(err, ErrAutofillOriginRejected) {
		t.Fatalf("default iframe policy = %v", err)
	}
	if _, err := AuthorizeAutofillRoute(
		nameKey,
		frame,
		request,
		FrameAuthorizationPolicy{AllowSameOriginIframe: true},
	); err != nil {
		t.Fatalf("same-origin iframe = %v", err)
	}
	frame.TargetOrigin = "https://attacker.test"
	if _, err := AuthorizeAutofillRoute(
		nameKey,
		frame,
		request,
		FrameAuthorizationPolicy{AllowSameOriginIframe: true},
	); !errors.Is(err, ErrAutofillOriginRejected) {
		t.Fatalf("cross-origin iframe = %v", err)
	}
}

func TestAuthorizeAutofillRouteRejectsWrongAccountBindingAndHint(t *testing.T) {
	nameKey := testOriginNameKey(t)
	origin, _ := NormalizeOrigin("https://example.test")
	expected, _ := ComputeOriginBinding(nameKey, origin, []byte("alice"))
	origin.Destroy()
	frame := TrustedFrameContext{
		TopFrameOrigin: "https://example.test",
		TargetOrigin:   "https://example.test",
		IsTopFrame:     true,
	}
	tests := []AutofillRouteRequest{
		func() AutofillRouteRequest {
			value := autofillRequest(expected)
			value.AccountID = []byte("bob")
			return value
		}(),
		func() AutofillRouteRequest {
			value := autofillRequest(expected)
			value.ExpectedOriginBinding[0] ^= 1
			return value
		}(),
		func() AutofillRouteRequest {
			value := autofillRequest(expected)
			hint := value.ResolvedCredentialID
			hint[0] ^= 1
			value.HintedCredentialID = &hint
			return value
		}(),
	}
	for _, request := range tests {
		if result, err := AuthorizeAutofillRoute(
			nameKey, frame, request, FrameAuthorizationPolicy{},
		); result != (AutofillAuthorization{}) || !errors.Is(err, ErrAutofillOriginRejected) {
			t.Fatalf("bad route = %#v, %v", result, err)
		}
	}
}

func TestAuthorizeAutofillRouteLoopbackDevelopmentException(t *testing.T) {
	nameKey := testOriginNameKey(t)
	origin, _ := NormalizeOrigin("http://127.0.0.1:8080")
	expected, _ := ComputeOriginBinding(nameKey, origin, []byte("alice"))
	origin.Destroy()
	frame := TrustedFrameContext{
		TopFrameOrigin: "http://127.0.0.1:8080",
		TargetOrigin:   "http://127.0.0.1:8080",
		IsTopFrame:     true,
	}
	request := autofillRequest(expected)
	if _, err := AuthorizeAutofillRoute(
		nameKey, frame, request, FrameAuthorizationPolicy{},
	); !errors.Is(err, ErrAutofillOriginRejected) {
		t.Fatalf("loopback without exception = %v", err)
	}
	if _, err := AuthorizeAutofillRoute(
		nameKey,
		frame,
		request,
		FrameAuthorizationPolicy{AllowLoopbackHTTP: true},
	); err != nil {
		t.Fatalf("loopback development exception = %v", err)
	}
}

func TestRedirectAlwaysReroutesAndInvalidatesCrossOriginHandle(t *testing.T) {
	t.Parallel()
	same, err := EvaluateTopLevelRedirect(
		"https://example.test/login",
		"https://example.test/account",
		FrameAuthorizationPolicy{},
	)
	if err == nil {
		// Redirect inputs are trusted Origins, not arbitrary URLs with paths.
		t.Fatal("redirect URL with path was silently truncated")
	}
	same, err = EvaluateTopLevelRedirect(
		"https://example.test",
		"https://example.test:443",
		FrameAuthorizationPolicy{},
	)
	if err != nil || !same.SameOrigin || same.InvalidatePreviousHandle ||
		!same.RequiresRouteRevalidation {
		t.Fatalf("same-origin redirect=%+v err=%v", same, err)
	}
	cross, err := EvaluateTopLevelRedirect(
		"https://example.test",
		"https://login.example.test",
		FrameAuthorizationPolicy{},
	)
	if err != nil || cross.SameOrigin || !cross.InvalidatePreviousHandle ||
		!cross.RequiresRouteRevalidation {
		t.Fatalf("cross-origin redirect=%+v err=%v", cross, err)
	}
	if _, err := EvaluateTopLevelRedirect(
		"https://example.test",
		"http://example.test",
		FrameAuthorizationPolicy{},
	); !errors.Is(err, ErrAutofillOriginRejected) {
		t.Fatalf("HTTPS downgrade error=%v", err)
	}
}

func TestMultipleOriginAccountRequiresExplicitExactPolicy(t *testing.T) {
	t.Parallel()
	policy, err := NewExplicitMultiOriginPolicy(
		[]string{"https://example.test", "https://login.example.test"},
		FrameAuthorizationPolicy{},
	)
	if err != nil {
		t.Fatal(err)
	}
	defer policy.Destroy()
	if !policy.Allows("https://example.test:443") ||
		!policy.Allows("https://login.example.test") ||
		policy.Allows("https://other.example.test") {
		t.Fatal("explicit multi-origin policy lost exact-origin isolation")
	}
	if _, err := NewExplicitMultiOriginPolicy(
		[]string{"https://example.test", "https://EXAMPLE.test:443"},
		FrameAuthorizationPolicy{},
	); !errors.Is(err, ErrAutofillOriginRejected) {
		t.Fatalf("duplicate canonical origin error=%v", err)
	}
}

func autofillRequest(binding [cryptokit.OriginBindingSize]byte) AutofillRouteRequest {
	var credentialID protocol.CredentialID
	copy(credentialID[:], sessionBytes(len(credentialID), 71))
	return AutofillRouteRequest{
		AccountID: []byte("alice"), ResolvedCredentialID: credentialID,
		ExpectedOriginBinding: binding,
	}
}
