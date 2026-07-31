package domain

import (
	"crypto/subtle"
	"errors"
	"net/url"
	"strings"

	"vdns.local/vdns/internal/cryptokit"
	"vdns.local/vdns/internal/protocol"
)

var ErrAutofillOriginRejected = errors.New("autofill origin rejected")

// TrustedFrameContext must be populated from the browser's trusted extension
// API, never from page-controlled message fields.
type TrustedFrameContext struct {
	TopFrameOrigin string
	TargetOrigin   string
	IsTopFrame     bool
}

type FrameAuthorizationPolicy struct {
	AllowSameOriginIframe bool
	AllowLoopbackHTTP     bool
}

type AutofillRouteRequest struct {
	AccountID             []byte
	ResolvedCredentialID  protocol.CredentialID
	HintedCredentialID    *protocol.CredentialID
	ExpectedOriginBinding [cryptokit.OriginBindingSize]byte
}

type AutofillAuthorization struct {
	CredentialID  protocol.CredentialID
	OriginBinding [cryptokit.OriginBindingSize]byte
}

type RedirectDecision struct {
	RequiresRouteRevalidation bool
	InvalidatePreviousHandle  bool
	SameOrigin                bool
}

// EvaluateTopLevelRedirect never authorizes a credential. It only determines
// whether a previously issued handle must be invalidated; the caller must
// always repeat RouteMap, VDNS and OriginBinding checks for the final target.
func EvaluateTopLevelRedirect(
	previousTopOrigin string,
	currentTopOrigin string,
	policy FrameAuthorizationPolicy,
) (RedirectDecision, error) {
	previous, err := NormalizeOrigin(previousTopOrigin)
	if err != nil {
		return RedirectDecision{}, ErrAutofillOriginRejected
	}
	defer previous.Destroy()
	current, err := NormalizeOrigin(currentTopOrigin)
	if err != nil {
		return RedirectDecision{}, ErrAutofillOriginRejected
	}
	defer current.Destroy()
	if !originAllowedByTransport(previous, policy.AllowLoopbackHTTP) ||
		!originAllowedByTransport(current, policy.AllowLoopbackHTTP) {
		return RedirectDecision{}, ErrAutofillOriginRejected
	}
	same := previous.Equal(current)
	return RedirectDecision{
		RequiresRouteRevalidation: true,
		InvalidatePreviousHandle:  !same,
		SameOrigin:                same,
	}, nil
}

type ExplicitMultiOriginPolicy struct {
	origins []Origin
}

func NewExplicitMultiOriginPolicy(
	rawOrigins []string,
	framePolicy FrameAuthorizationPolicy,
) (*ExplicitMultiOriginPolicy, error) {
	if len(rawOrigins) == 0 || len(rawOrigins) > 16 {
		return nil, ErrAutofillOriginRejected
	}
	result := &ExplicitMultiOriginPolicy{}
	for _, raw := range rawOrigins {
		origin, err := NormalizeOrigin(raw)
		if err != nil || !originAllowedByTransport(origin, framePolicy.AllowLoopbackHTTP) {
			origin.Destroy()
			result.Destroy()
			return nil, ErrAutofillOriginRejected
		}
		for _, existing := range result.origins {
			if existing.Equal(origin) {
				origin.Destroy()
				result.Destroy()
				return nil, ErrAutofillOriginRejected
			}
		}
		result.origins = append(result.origins, origin)
	}
	return result, nil
}

func (policy *ExplicitMultiOriginPolicy) Allows(raw string) bool {
	if policy == nil {
		return false
	}
	candidate, err := NormalizeOrigin(raw)
	if err != nil {
		return false
	}
	defer candidate.Destroy()
	for _, allowed := range policy.origins {
		if allowed.Equal(candidate) {
			return true
		}
	}
	return false
}

func (policy *ExplicitMultiOriginPolicy) Destroy() {
	if policy == nil {
		return
	}
	for _, origin := range policy.origins {
		origin.Destroy()
	}
	policy.origins = nil
}

// AuthorizeAutofillRoute enforces top-frame/target policy, reuses the locally
// resolved credential rather than an extension hint, and recomputes the
// OriginBinding immediately before a secret handle may be issued.
func AuthorizeAutofillRoute(
	nameKey *cryptokit.Key,
	frame TrustedFrameContext,
	request AutofillRouteRequest,
	policy FrameAuthorizationPolicy,
) (AutofillAuthorization, error) {
	if nameKey == nil || len(request.AccountID) == 0 ||
		allZero(request.ResolvedCredentialID[:]) ||
		allZero(request.ExpectedOriginBinding[:]) {
		return AutofillAuthorization{}, ErrAutofillOriginRejected
	}
	top, err := NormalizeOrigin(frame.TopFrameOrigin)
	if err != nil {
		return AutofillAuthorization{}, ErrAutofillOriginRejected
	}
	defer top.Destroy()
	target, err := NormalizeOrigin(frame.TargetOrigin)
	if err != nil {
		return AutofillAuthorization{}, ErrAutofillOriginRejected
	}
	defer target.Destroy()

	if !originAllowedByTransport(top, policy.AllowLoopbackHTTP) ||
		!originAllowedByTransport(target, policy.AllowLoopbackHTTP) {
		return AutofillAuthorization{}, ErrAutofillOriginRejected
	}
	if frame.IsTopFrame {
		if !top.Equal(target) {
			return AutofillAuthorization{}, ErrAutofillOriginRejected
		}
	} else if !policy.AllowSameOriginIframe || !top.Equal(target) {
		return AutofillAuthorization{}, ErrAutofillOriginRejected
	}
	if request.HintedCredentialID != nil &&
		subtle.ConstantTimeCompare(
			request.HintedCredentialID[:],
			request.ResolvedCredentialID[:],
		) != 1 {
		return AutofillAuthorization{}, ErrAutofillOriginRejected
	}

	binding, err := ComputeOriginBinding(nameKey, target, request.AccountID)
	if err != nil || subtle.ConstantTimeCompare(
		binding[:],
		request.ExpectedOriginBinding[:],
	) != 1 {
		return AutofillAuthorization{}, ErrAutofillOriginRejected
	}
	return AutofillAuthorization{
		CredentialID:  request.ResolvedCredentialID,
		OriginBinding: binding,
	}, nil
}

func originAllowedByTransport(origin Origin, allowLoopbackHTTP bool) bool {
	allowed := false
	_ = origin.UseCanonical(func(canonical []byte) error {
		value := string(canonical)
		if strings.HasPrefix(value, "https://") {
			allowed = true
			return nil
		}
		if !allowLoopbackHTTP || !strings.HasPrefix(value, "http://") {
			return nil
		}
		parsed, err := url.Parse(value)
		if err != nil {
			return nil
		}
		host := strings.TrimSuffix(strings.ToLower(parsed.Hostname()), ".")
		allowed = host == "localhost" || host == "127.0.0.1" || host == "::1"
		return nil
	})
	return allowed
}
