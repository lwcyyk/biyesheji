package cryptokit

import (
	"crypto/hmac"
	"crypto/sha256"
	"io"
	"unicode/utf8"

	"golang.org/x/crypto/hkdf"

	"vdns.local/vdns/internal/protocol"
)

const (
	KeySize             = 32
	DevicePseudonymSize = 16
	OriginBindingSize   = sha256.Size
	maxBeaconOutputSize = 1024
	maxAccountIDBytes   = 4096
	maxCanonicalOrigin  = 4096
)

// NamespaceKeys contains the five generation-wide VDNS-PM/2 keys. Callers
// receive purpose-scoped handles and cannot retag raw material.
type NamespaceKeys struct {
	Wrap     *Key
	Name     *Key
	Audit    *Key
	Relation *Key
	Rotation *Key
}

// Destroy clears every key owned by the bundle.
func (keys *NamespaceKeys) Destroy() {
	if keys == nil {
		return
	}
	for _, key := range []*Key{keys.Wrap, keys.Name, keys.Audit, keys.Relation, keys.Rotation} {
		if key != nil {
			key.Destroy()
		}
	}
}

// ExtractNamespacePRK performs RFC 5869 Extract for one independent
// namespace-root generation.
func ExtractNamespacePRK(
	root *Secret,
	namespaceID protocol.NamespaceID,
	generation uint64,
) (*Key, error) {
	if root == nil || generation == 0 {
		return nil, ErrInvalidInput
	}
	saltInput, err := encodeDomain(
		protocol.DomainPrefix+"NAMESPACE-PRK",
		namespaceID,
		generation,
	)
	if err != nil {
		return nil, err
	}
	salt := sha256.Sum256(saltInput)
	wipe(saltInput)

	var result *Key
	err = root.withBytes(func(rootBytes []byte) error {
		if len(rootBytes) != KeySize {
			return ErrInvalidInput
		}
		prk := hkdf.Extract(sha256.New, rootBytes, salt[:])
		defer wipe(prk)
		result, err = newKeyWithPurpose(prk, purposeNamespacePRK)
		return err
	})
	wipe(salt[:])
	if err != nil {
		return nil, err
	}
	return result, nil
}

// DeriveNamespaceKeys derives strictly separated content, name, audit,
// relation and rotation roots.
func DeriveNamespaceKeys(prk *Key) (*NamespaceKeys, error) {
	specs := []struct {
		label   string
		purpose keyPurpose
	}{
		{"CREDENTIAL-WRAP", purposeCredentialWrap},
		{"CREDENTIAL-NAME", purposeCredentialName},
		{"AUDIT", purposeAuditRoot},
		{"RELATION", purposeRelation},
		{"ROTATION", purposeRotationRoot},
	}
	derived := make([]*Key, 0, len(specs))
	for _, spec := range specs {
		key, err := expandLabel(
			prk,
			purposeNamespacePRK,
			spec.purpose,
			protocol.DomainPrefix+spec.label,
		)
		if err != nil {
			for _, existing := range derived {
				existing.Destroy()
			}
			return nil, err
		}
		derived = append(derived, key)
	}
	return &NamespaceKeys{
		Wrap: derived[0], Name: derived[1], Audit: derived[2],
		Relation: derived[3], Rotation: derived[4],
	}, nil
}

// DeriveAuditKey binds an epoch key to the verified beacon, chain, namespace,
// root-secret generation and epoch.
func DeriveAuditKey(
	auditRoot *Key,
	chainID string,
	namespaceID protocol.NamespaceID,
	generation uint64,
	epoch uint64,
	beaconOutput []byte,
) (*Key, error) {
	if auditRoot == nil || chainID == "" || len(chainID) > protocol.MaxChainIDBytes ||
		!utf8.ValidString(chainID) || generation == 0 ||
		len(beaconOutput) == 0 || len(beaconOutput) > maxBeaconOutputSize {
		return nil, ErrInvalidInput
	}
	beaconHash := sha256.Sum256(beaconOutput)
	info, err := encodeDomain(
		protocol.DomainPrefix+"AUDIT-EPOCH",
		chainID,
		namespaceID,
		generation,
		epoch,
		beaconHash,
	)
	if err != nil {
		return nil, err
	}
	defer wipe(info)
	return expandKey(auditRoot, purposeAuditRoot, purposeAudit, info)
}

// DeriveEventKey derives a unique event key from an audit epoch and public
// epoch pseudonym.
func DeriveEventKey(
	auditKey *Key,
	eventID protocol.EventID,
	devicePseudonym [DevicePseudonymSize]byte,
) (*Key, error) {
	info, err := encodeDomain(protocol.DomainPrefix+"AUDIT-EVENT", eventID, devicePseudonym)
	if err != nil {
		return nil, err
	}
	defer wipe(info)
	return expandKey(auditKey, purposeAudit, purposeEvent, info)
}

// DeriveRotationKey binds a campaign key to the affected set and future
// verified beacon epoch.
func DeriveRotationKey(
	rotationRoot *Key,
	campaignID protocol.CampaignID,
	affectedRoot [sha256.Size]byte,
	selectedEpoch uint64,
	beaconOutput []byte,
) (*Key, error) {
	if len(beaconOutput) == 0 || len(beaconOutput) > maxBeaconOutputSize {
		return nil, ErrInvalidInput
	}
	beaconHash := sha256.Sum256(beaconOutput)
	info, err := encodeDomain(
		protocol.DomainPrefix+"ROTATION-CAMPAIGN",
		campaignID,
		affectedRoot,
		selectedEpoch,
		beaconHash,
	)
	if err != nil {
		return nil, err
	}
	defer wipe(info)
	return expandKey(rotationRoot, purposeRotationRoot, purposeRotation, info)
}

// DeriveDevicePseudonym computes a public 16-byte epoch pseudonym. It is not
// an authorization identity and changes across epochs.
func DeriveDevicePseudonym(
	auditRoot *Key,
	deviceID protocol.DeviceID,
	epoch uint64,
) ([DevicePseudonymSize]byte, error) {
	var pseudonym [DevicePseudonymSize]byte
	input, err := encodeDomain(protocol.DomainPrefix+"DEVICE-PSEUDONYM", deviceID, epoch)
	if err != nil {
		return pseudonym, err
	}
	defer wipe(input)

	err = auditRoot.withPurposeBytes(purposeAuditRoot, func(key []byte) error {
		mac := hmac.New(sha256.New, key)
		_, _ = mac.Write(input)
		full := mac.Sum(nil)
		copy(pseudonym[:], full[:DevicePseudonymSize])
		wipe(full)
		return nil
	})
	if err != nil {
		return [DevicePseudonymSize]byte{}, err
	}
	return pseudonym, nil
}

// DeriveOriginBinding hides the canonical Origin/account relation while
// binding field ciphertext and local routing to the exact normalized pair.
// Inputs are copied only inside this call and never returned.
func DeriveOriginBinding(
	nameKey *Key,
	canonicalOrigin []byte,
	accountID []byte,
) ([OriginBindingSize]byte, error) {
	var binding [OriginBindingSize]byte
	if len(canonicalOrigin) == 0 || len(canonicalOrigin) > maxCanonicalOrigin ||
		len(accountID) == 0 || len(accountID) > maxAccountIDBytes ||
		!utf8.Valid(canonicalOrigin) || !utf8.Valid(accountID) {
		return binding, ErrInvalidInput
	}
	input, err := encodeDomain(
		protocol.DomainPrefix+"ORIGIN-BINDING",
		append([]byte(nil), canonicalOrigin...),
		append([]byte(nil), accountID...),
	)
	if err != nil {
		return binding, err
	}
	defer wipe(input)
	err = nameKey.withPurposeBytes(purposeCredentialName, func(key []byte) error {
		mac := hmac.New(sha256.New, key)
		_, _ = mac.Write(input)
		sum := mac.Sum(nil)
		copy(binding[:], sum)
		wipe(sum)
		return nil
	})
	if err != nil {
		wipe(binding[:])
		return [OriginBindingSize]byte{}, err
	}
	return binding, nil
}

func deriveFieldEnvelopeKey(
	wrapRoot *Key,
	credentialID protocol.CredentialID,
	credentialVersion uint64,
	fieldType FieldType,
	envelopeID FieldEnvelopeID,
) (*Key, error) {
	if credentialVersion == 0 || !fieldType.Valid() {
		return nil, ErrInvalidInput
	}
	info, err := encodeDomain(
		protocol.DomainPrefix+"FIELD-DEK-ENVELOPE",
		credentialID,
		credentialVersion,
		uint64(fieldType),
		envelopeID,
	)
	if err != nil {
		return nil, err
	}
	defer wipe(info)
	return expandKey(wrapRoot, purposeCredentialWrap, purposeFieldEnvelope, info)
}

func expandLabel(prk *Key, inputPurpose, outputPurpose keyPurpose, label string) (*Key, error) {
	info, err := encodeDomain(label)
	if err != nil {
		return nil, err
	}
	defer wipe(info)
	return expandKey(prk, inputPurpose, outputPurpose, info)
}

func expandKey(prk *Key, inputPurpose, outputPurpose keyPurpose, info []byte) (*Key, error) {
	if prk == nil || len(info) == 0 {
		return nil, ErrInvalidInput
	}
	var material [KeySize]byte
	err := prk.withPurposeBytes(inputPurpose, func(prkBytes []byte) error {
		_, readErr := io.ReadFull(hkdf.Expand(sha256.New, prkBytes, info), material[:])
		return readErr
	})
	if err != nil {
		wipe(material[:])
		return nil, err
	}
	key, err := newKeyFromArray(material, outputPurpose)
	wipe(material[:])
	if err != nil {
		return nil, err
	}
	return key, nil
}

func encodeDomain(parts ...any) ([]byte, error) {
	encoded, err := protocol.MarshalDeterministic(parts)
	if err != nil {
		return nil, ErrInvalidInput
	}
	return encoded, nil
}
