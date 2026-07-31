package application

import (
	"crypto/sha256"

	"vdns.local/vdns/internal/protocol"
	resolverdomain "vdns.local/vdns/internal/resolver/domain"
	transparencydomain "vdns.local/vdns/internal/transparency/domain"
)

// ResolveRequest contains receiver-owned trust context and an untrusted
// candidate package. There is deliberately no CloudCurrentVersion field.
type ResolveRequest struct {
	L1              L1Input
	L2              L2Input
	Dynamic         TrustedDynamicState
	ProofAvailable  bool
	BundleSigInput  []byte
	BundleSignature protocol.Signature
	L4Trust         L4Trust
	Policy          PolicyInput
}

// Resolve executes L1-L5 in order and returns the VDNS-selected state. A
// cryptographically invalid proof is a rejection, while an absent proof may
// enter the explicit L5 offline policy.
func Resolve(request ResolveRequest) (resolverdomain.Resolution, error) {
	var result resolverdomain.Resolution
	identity, l1, err := VerifyL1(request.L1)
	result.Layers[0] = l1
	if err != nil {
		return rejectedResolution(result, protocol.VerdictRejectIdentity), err
	}
	result.Principal = identity.Principal

	request.L2.Identity = identity
	authorization, l2, err := VerifyL2(request.L2)
	result.Layers[1] = l2
	if err != nil {
		return rejectedResolution(result, protocol.VerdictRejectCapability), err
	}
	result.Authorization = authorization

	l3, err := VerifyL3(identity, request.Dynamic)
	result.Layers[2] = l3
	if err != nil {
		if l3.Code == resolverdomain.CodeStateRevoked {
			return rejectedResolution(result, protocol.VerdictRejectRevoked), err
		} else if l3.Code == resolverdomain.CodeStateConflict {
			return rejectedResolution(result, protocol.VerdictReviewRequired), err
		} else {
			return rejectedResolution(result, protocol.VerdictRejectCausal), err
		}
	}
	state := identity.Descriptor.Payload()
	result.State = state
	result.CurrentVersion = state.ActiveVersion

	if request.ProofAvailable {
		request.L4Trust.ExpectedSubjectDigest = identity.Descriptor.Digest()
		request.L4Trust.ExpectedFinalSequence = state.FinalSequence
		deviceCredentialObject, objectErr := identity.Credential.MarshalBinary()
		if objectErr != nil {
			return rejectedResolution(result, protocol.VerdictRejectIdentity), objectErr
		}
		rootTrustObject, objectErr := encodeRootTrustObject(request.L1)
		if objectErr != nil {
			return rejectedResolution(result, protocol.VerdictRejectIdentity), objectErr
		}
		rootChainDigest, objectErr := transparencydomain.RootChainDigest(
			[][]byte{rootTrustObject},
		)
		if objectErr != nil {
			result.Verdict = protocol.VerdictRejectIdentity
			return result, objectErr
		}
		request.L4Trust.ExpectedRootChainDigest = rootChainDigest
		request.L4Trust.ExpectedDeviceCredentialObjectHash =
			sha256.Sum256(deviceCredentialObject)
		audit, bundle, l4, proofErr := VerifyL4(
			request.BundleSigInput, request.BundleSignature, request.L4Trust,
		)
		result.Layers[3] = l4
		if proofErr != nil {
			return rejectedResolution(result, protocol.VerdictRejectProof), proofErr
		}
		result.Audit = audit
		result.ProofDigest = bundle.Digest()
		request.Policy.L4Available = true
		request.Policy.PendingAnchor = audit.PendingAnchor
	} else {
		result.Layers[3] = resolverdomain.LayerResult{
			Layer: resolverdomain.LayerTransparency,
			Code:  resolverdomain.CodePolicyOffline,
		}
		request.Policy.L4Available = false
	}
	request.Policy.Operation = authorization.Operation
	verdict, l5 := EvaluateL5(request.Policy)
	result.Layers[4] = l5
	result.Verdict = verdict
	if !verdict.Accepted() {
		return rejectedResolution(result, verdict), ErrVerificationRejected
	}
	return result, nil
}

// rejectedResolution retains stable per-layer diagnostic codes while clearing
// every verified projection. Callers can diagnose the failing layer but cannot
// accidentally consume identity, authorization, state or audit data from an
// incomplete L1-L5 run.
func rejectedResolution(
	result resolverdomain.Resolution,
	verdict protocol.Verdict,
) resolverdomain.Resolution {
	layers := result.Layers
	return resolverdomain.Resolution{Verdict: verdict, Layers: layers}
}

type rootTrustProjection struct {
	ChainID           string               `cbor:"chain_id"`
	NamespaceID       protocol.NamespaceID `cbor:"namespace_id"`
	RootPublicKey     []byte               `cbor:"root_public_key"`
	RootKeyGeneration uint64               `cbor:"root_key_generation"`
}

func encodeRootTrustObject(input L1Input) ([]byte, error) {
	return protocol.MarshalDeterministic(rootTrustProjection{
		ChainID:           input.ChainID,
		NamespaceID:       input.NamespaceID,
		RootPublicKey:     append([]byte(nil), input.RootPublicKey...),
		RootKeyGeneration: input.RootKeyGeneration,
	})
}
