// Package application orchestrates the daily credential use cases. Secret
// keys remain owned by VaultSession; this layer handles only protected Secret
// values, ciphertext objects and signed public control projections.
package application

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"time"

	"vdns.local/vdns/internal/adapters/outbound/sqlite"
	credential "vdns.local/vdns/internal/credential/domain"
	"vdns.local/vdns/internal/cryptokit"
	operation "vdns.local/vdns/internal/operation/domain"
	password "vdns.local/vdns/internal/password/domain"
	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
)

var (
	ErrInvalidDailyVaultRequest = errors.New("invalid daily vault request")
	ErrDailyVaultVerification   = errors.New("credential verification failed")
)

// DeviceControlSigner is backed by the device secure key store in production.
type DeviceControlSigner interface {
	SignOperation(operation.Payload) (*operation.SignedEvent, error)
	SignState(credential.StateDescriptorPayload) (*credential.SignedStateDescriptor, error)
}

// StateDescriptorVerifier is the G2 verification seam. G4 supplies the full
// VDNS five-layer verifier at this boundary.
type StateDescriptorVerifier interface {
	VerifyStateDescriptor(
		ctx context.Context,
		namespaceID protocol.NamespaceID,
		descriptorHash [sha256.Size]byte,
		sigInput []byte,
		signature protocol.Signature,
	) (credential.StateDescriptorPayload, error)
}

type DailyVaultService struct {
	database    *sqlite.Database
	objectStore platform.CiphertextObjectStore
	session     *credential.VaultSession
	signer      DeviceControlSigner
	verifier    StateDescriptorVerifier
	chainID     string
	credentials *sqlite.CredentialRepository
	routes      *sqlite.RouteRepository
	operations  *sqlite.OperationRepository
	controls    *sqlite.CredentialControlRepository
}

func NewDailyVaultService(
	database *sqlite.Database,
	objectStore platform.CiphertextObjectStore,
	session *credential.VaultSession,
	signer DeviceControlSigner,
	verifier StateDescriptorVerifier,
) (*DailyVaultService, error) {
	if database == nil || objectStore == nil || session == nil || signer == nil {
		return nil, ErrInvalidDailyVaultRequest
	}
	chainSigner, ok := signer.(ChainContextSigner)
	if !ok || chainSigner.ChainID() == "" ||
		len(chainSigner.ChainID()) > protocol.MaxChainIDBytes {
		return nil, ErrInvalidDailyVaultRequest
	}
	credentials, err := sqlite.NewCredentialRepository(database)
	if err != nil {
		return nil, err
	}
	routes, err := sqlite.NewRouteRepository(database)
	if err != nil {
		return nil, err
	}
	operations, err := sqlite.NewOperationRepository(database)
	if err != nil {
		return nil, err
	}
	controls, err := sqlite.NewCredentialControlRepository(database)
	if err != nil {
		return nil, err
	}
	return &DailyVaultService{
		database: database, objectStore: objectStore, session: session,
		signer: signer, verifier: verifier, chainID: chainSigner.ChainID(),
		credentials: credentials,
		routes:      routes, operations: operations, controls: controls,
	}, nil
}

type CreateCredentialRequest struct {
	Now                  time.Time
	Origin               string
	AccountID            []byte
	Policy               *password.PasswordPolicy
	PasswordLength       int
	InstallationID       credential.InstallationID
	HandleTTL            time.Duration
	DeviceCredentialHash [sha256.Size]byte
	DeviceCounter        uint64
	PreviousEventHash    *[sha256.Size]byte
	AuditEpoch           uint64
	VerifiedBeacon       []byte
	AuthorizedDeviceRoot [sha256.Size]byte
	AuditCheckpoint      [sha256.Size]byte
	FinalSequence        uint64
}

type CreateCredentialResult struct {
	CredentialID   protocol.CredentialID
	Version        uint64
	EnvelopeHash   [sha256.Size]byte
	DescriptorHash [sha256.Size]byte
	PasswordHandle credential.SecretHandleID
}

type createAuditRecord struct {
	Operation     protocol.OperationType            `cbor:"operation"`
	CredentialID  protocol.CredentialID             `cbor:"credential_id"`
	Version       uint64                            `cbor:"version"`
	OriginBinding [cryptokit.OriginBindingSize]byte `cbor:"origin_binding"`
	EnvelopeHash  [sha256.Size]byte                 `cbor:"envelope_hash"`
}

// CreateCredential implements NONEXISTENT -> ACTIVE(v1). All ciphertext files
// are fsynced first; all database pointers, RouteMap, CREATE event, outbox and
// accepted state then commit in one SQLite transaction.
func (service *DailyVaultService) CreateCredential(
	ctx context.Context,
	request CreateCredentialRequest,
) (CreateCredentialResult, error) {
	if service == nil || service.database == nil || service.objectStore == nil ||
		service.session == nil || service.signer == nil || ctx == nil ||
		request.Now.IsZero() || request.Now.UnixMilli() <= 0 ||
		len(request.AccountID) == 0 || request.Policy == nil ||
		request.HandleTTL <= 0 || bytesAllZero(request.InstallationID[:]) ||
		bytesAllZero(request.DeviceCredentialHash[:]) ||
		request.DeviceCounter == 0 || request.AuditEpoch == 0 ||
		len(request.VerifiedBeacon) == 0 ||
		bytesAllZero(request.AuthorizedDeviceRoot[:]) ||
		bytesAllZero(request.AuditCheckpoint[:]) || request.FinalSequence == 0 {
		return CreateCredentialResult{}, ErrInvalidDailyVaultRequest
	}
	origin, err := credential.NormalizeOrigin(request.Origin)
	if err != nil {
		return CreateCredentialResult{}, ErrInvalidDailyVaultRequest
	}
	defer origin.Destroy()
	metadata, err := service.session.Metadata(request.Now)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	originBinding, err := service.session.AuthorizeOriginForAccount(
		request.Now, origin, request.AccountID,
	)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	credentialID, err := protocol.NewCredentialID()
	if err != nil {
		return CreateCredentialResult{}, err
	}
	eventID, err := protocol.NewEventID()
	if err != nil {
		return CreateCredentialResult{}, err
	}
	route, err := service.session.BuildEncryptedRouteEntry(
		request.Now, origin, request.AccountID, credentialID, 1,
	)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	passwordSecret, err := password.GeneratePassword(
		request.Policy, request.PasswordLength,
	)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	defer passwordSecret.Destroy()

	fields := make([]credential.FieldMapping, 0, 3)
	fieldPaths := make(map[cryptokit.FieldType]string, 3)
	originSecret := secretFromOrigin(origin)
	if originSecret == nil {
		return CreateCredentialResult{}, ErrInvalidDailyVaultRequest
	}
	if err := service.prepareField(
		ctx, request.Now, metadata, credentialID, originBinding,
		request.Policy.Hash(), cryptokit.FieldOrigin,
		originSecret,
		&fields, fieldPaths,
	); err != nil {
		originSecret.Destroy()
		return CreateCredentialResult{}, err
	}
	originSecret.Destroy()
	accountSecret, err := cryptokit.NewSecret(request.AccountID)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	if err := service.prepareField(
		ctx, request.Now, metadata, credentialID, originBinding,
		request.Policy.Hash(), cryptokit.FieldUsername, accountSecret,
		&fields, fieldPaths,
	); err != nil {
		accountSecret.Destroy()
		return CreateCredentialResult{}, err
	}
	accountSecret.Destroy()
	if err := service.prepareField(
		ctx, request.Now, metadata, credentialID, originBinding,
		request.Policy.Hash(), cryptokit.FieldPassword, passwordSecret,
		&fields, fieldPaths,
	); err != nil {
		return CreateCredentialResult{}, err
	}
	draft, err := credential.NewVersionDraft(
		credentialID, 1, 1, credential.VersionActive, nil,
		request.Policy.Hash(), fields,
	)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	draftBytes := draft.DescriptorCBOR()
	draftObject, err := service.objectStore.PutIfAbsent(ctx, draftBytes)
	clear(draftBytes)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	envelope, err := credential.NewCredentialEnvelope(
		metadata.NamespaceID, draft, originBinding,
	)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	auditRecordBytes, err := protocol.MarshalDeterministic(createAuditRecord{
		Operation: protocol.OperationCreate, CredentialID: credentialID,
		Version: 1, OriginBinding: originBinding, EnvelopeHash: envelope.Digest(),
	})
	if err != nil {
		return CreateCredentialResult{}, err
	}
	auditSecret, err := cryptokit.NewSecret(auditRecordBytes)
	clear(auditRecordBytes)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	eventEnvelope, pseudonym, err := service.session.SealAuditEvent(
		request.Now, service.chainID, eventID,
		request.AuditEpoch, request.VerifiedBeacon, auditSecret,
	)
	auditSecret.Destroy()
	if err != nil {
		return CreateCredentialResult{}, err
	}
	eventBytes, err := eventEnvelope.MarshalBinary()
	if err != nil {
		return CreateCredentialResult{}, err
	}
	eventObject, err := service.objectStore.PutIfAbsent(ctx, eventBytes)
	clear(eventBytes)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	versionOne := uint64(1)
	observedAt := uint64(request.Now.UnixMilli())
	event, err := service.signer.SignOperation(operation.Payload{
		EventID: eventID, NamespaceID: metadata.NamespaceID,
		DeviceID:             metadata.DeviceID,
		DeviceCredentialHash: request.DeviceCredentialHash,
		CredentialID:         &credentialID, OperationType: protocol.OperationCreate,
		NewVersion: &versionOne, DevicePseudonym: pseudonym,
		OriginCommitment:       &originBinding,
		EventPayloadHash:       eventEnvelope.PayloadHash(),
		VRFEpoch:               &request.AuditEpoch,
		SecretGeneration:       metadata.SecretGeneration,
		DeviceCounter:          request.DeviceCounter,
		PreviousEventHash:      cloneHash(request.PreviousEventHash),
		ObservedAtMilliseconds: &observedAt,
	})
	if err != nil {
		return CreateCredentialResult{}, err
	}
	state, err := service.signer.SignState(credential.StateDescriptorPayload{
		NamespaceID: metadata.NamespaceID, CredentialID: credentialID,
		ActiveVersion: 1, ActiveEnvelopeHash: envelope.Digest(),
		LifecycleStatus:      protocol.LifecycleActive,
		LastOperationEvent:   event.Digest(),
		AuthorizedDeviceRoot: request.AuthorizedDeviceRoot,
		AuditCheckpoint:      request.AuditCheckpoint,
		FinalSequence:        request.FinalSequence, UpdaterDeviceID: metadata.DeviceID,
	})
	if err != nil {
		return CreateCredentialResult{}, err
	}

	createdAt := uint64(request.Now.UnixMilli())
	transaction, err := service.database.BeginImmediate(ctx)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	defer func() { _ = transaction.Rollback() }()
	if _, err := service.credentials.CreateVersion(
		ctx, transaction, sqlite.CommitCredentialVersionRequest{
			NamespaceID: metadata.NamespaceID, OriginCommitment: originBinding,
			Draft: draft, DescriptorObject: draftObject,
			DescriptorStoragePath: objectPath(draftObject.Digest),
			FieldStoragePaths:     fieldPaths, AdvanceLocalPointer: true,
			CreatedAtMilliseconds: createdAt,
		},
	); err != nil {
		return CreateCredentialResult{}, err
	}
	if err := service.routes.CreateSealedRoute(
		ctx, transaction, route, createdAt,
	); err != nil {
		return CreateCredentialResult{}, err
	}
	if _, err := service.operations.CreateOrLoad(
		ctx, transaction, sqlite.CommitEventRequest{
			Event: event,
			Object: sqlite.EventObject{
				Reference: eventObject, StorageRelativePath: objectPath(eventObject.Digest),
				KeyGeneration: metadata.SecretGeneration,
			},
			CreatedAtMilliseconds: createdAt,
		},
	); err != nil {
		return CreateCredentialResult{}, err
	}
	accepted, err := service.controls.AcceptState(
		ctx, transaction, sqlite.AcceptCredentialStateRequest{
			NamespaceID: metadata.NamespaceID, Envelope: envelope,
			Descriptor: state, CreatedAtMilliseconds: createdAt,
		},
	)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	if err := transaction.Commit(); err != nil {
		return CreateCredentialResult{}, err
	}
	handle, err := service.session.IssueSecretHandle(
		request.Now, request.HandleTTL,
		credential.SecretHandleContext{
			InstallationID: request.InstallationID,
			OriginBinding:  originBinding, CredentialID: credentialID,
			FieldType: cryptokit.FieldPassword,
		},
		passwordSecret,
	)
	if err != nil {
		return CreateCredentialResult{}, err
	}
	return CreateCredentialResult{
		CredentialID: credentialID, Version: 1,
		EnvelopeHash: envelope.Digest(), DescriptorHash: accepted.DescriptorHash,
		PasswordHandle: handle,
	}, nil
}

type ReadCredentialRequest struct {
	Now            time.Time
	Origin         string
	AccountID      []byte
	InstallationID credential.InstallationID
	HandleTTL      time.Duration
}

type ReadCredentialResult struct {
	CredentialID protocol.CredentialID
	Version      uint64
	Handle       credential.SecretHandleID
}

// ReadCredential follows RouteMap -> verified accepted state -> Envelope ->
// content object -> AEAD -> one-time handle. No plaintext is returned.
func (service *DailyVaultService) ReadCredential(
	ctx context.Context,
	request ReadCredentialRequest,
) (ReadCredentialResult, error) {
	if service == nil || service.verifier == nil || ctx == nil ||
		request.Now.IsZero() || len(request.AccountID) == 0 ||
		bytesAllZero(request.InstallationID[:]) ||
		request.HandleTTL <= 0 || request.HandleTTL > credential.MaxSecretHandleTTL {
		return ReadCredentialResult{}, ErrInvalidDailyVaultRequest
	}
	origin, err := credential.NormalizeOrigin(request.Origin)
	if err != nil {
		return ReadCredentialResult{}, ErrInvalidDailyVaultRequest
	}
	defer origin.Destroy()
	metadata, err := service.session.Metadata(request.Now)
	if err != nil {
		return ReadCredentialResult{}, err
	}
	lookup, err := service.session.BuildRouteLookup(
		request.Now, origin, request.AccountID,
	)
	if err != nil {
		return ReadCredentialResult{}, err
	}
	resolution, err := service.routes.ResolveLookup(
		ctx, metadata.NamespaceID, lookup,
	)
	if err != nil {
		return ReadCredentialResult{}, err
	}
	accepted, err := service.controls.LoadAccepted(
		ctx, metadata.NamespaceID, resolution.CredentialID,
	)
	if err != nil {
		return ReadCredentialResult{}, err
	}
	payload, err := service.verifier.VerifyStateDescriptor(
		ctx, metadata.NamespaceID, accepted.DescriptorHash,
		accepted.DescriptorSigInput, accepted.DescriptorSignature,
	)
	if err != nil || payload.NamespaceID != metadata.NamespaceID ||
		payload.CredentialID != resolution.CredentialID ||
		payload.ActiveVersion != accepted.AcceptedVersion ||
		payload.ActiveEnvelopeHash != accepted.Envelope.Digest() ||
		payload.LifecycleStatus != protocol.LifecycleActive ||
		accepted.Envelope.OriginBinding() != lookup.OriginBinding {
		return ReadCredentialResult{}, ErrDailyVaultVerification
	}
	mapping, err := service.credentials.LoadFieldMapping(
		ctx, resolution.CredentialID, accepted.AcceptedVersion,
		cryptokit.FieldPassword,
	)
	if err != nil {
		return ReadCredentialResult{}, err
	}
	reference := mapping.Reference()
	if reference.OriginBinding != lookup.OriginBinding ||
		reference.CryptoPolicyHash != accepted.Envelope.PolicyHash() ||
		!envelopeContainsField(accepted.Envelope, reference) {
		return ReadCredentialResult{}, ErrDailyVaultVerification
	}
	objectBytes, err := service.objectStore.Get(ctx, mapping.ObjectReference())
	if err != nil {
		return ReadCredentialResult{}, err
	}
	encrypted, err := cryptokit.ParseEncryptedField(objectBytes)
	clear(objectBytes)
	if err != nil {
		return ReadCredentialResult{}, ErrDailyVaultVerification
	}
	secret, err := service.session.DecryptCredentialField(
		request.Now, resolution.CredentialID, reference, encrypted,
	)
	if err != nil {
		return ReadCredentialResult{}, ErrDailyVaultVerification
	}
	defer secret.Destroy()
	handle, err := service.session.IssueSecretHandle(
		request.Now, request.HandleTTL,
		credential.SecretHandleContext{
			InstallationID: request.InstallationID,
			OriginBinding:  lookup.OriginBinding,
			CredentialID:   resolution.CredentialID,
			FieldType:      cryptokit.FieldPassword,
		},
		secret,
	)
	if err != nil {
		return ReadCredentialResult{}, err
	}
	return ReadCredentialResult{
		CredentialID: resolution.CredentialID,
		Version:      accepted.AcceptedVersion, Handle: handle,
	}, nil
}

func (service *DailyVaultService) prepareField(
	ctx context.Context,
	now time.Time,
	metadata credential.VaultSessionMetadata,
	credentialID protocol.CredentialID,
	originBinding [cryptokit.OriginBindingSize]byte,
	policyHash [sha256.Size]byte,
	fieldType cryptokit.FieldType,
	plaintext *cryptokit.Secret,
	fields *[]credential.FieldMapping,
	fieldPaths map[cryptokit.FieldType]string,
) error {
	if plaintext == nil {
		return ErrInvalidDailyVaultRequest
	}
	encrypted, err := service.session.EncryptCredentialField(
		now,
		cryptokit.FieldContext{
			NamespaceID: metadata.NamespaceID, CredentialID: credentialID,
			CredentialVersion: 1, FieldType: fieldType,
			KeyGeneration:    metadata.SecretGeneration,
			CryptoPolicyHash: policyHash, OriginBinding: originBinding,
		},
		plaintext,
	)
	if err != nil {
		return err
	}
	encoded, err := encrypted.MarshalBinary()
	if err != nil {
		return err
	}
	reference, err := service.objectStore.PutIfAbsent(ctx, encoded)
	clear(encoded)
	if err != nil {
		return err
	}
	mapping, err := credential.NewFieldMapping(encrypted, reference)
	if err != nil {
		return err
	}
	*fields = append(*fields, mapping)
	fieldPaths[fieldType] = objectPath(reference.Digest)
	return nil
}

func secretFromOrigin(origin credential.Origin) *cryptokit.Secret {
	var result *cryptokit.Secret
	_ = origin.UseCanonical(func(canonical []byte) error {
		result, _ = cryptokit.NewSecret(canonical)
		return nil
	})
	return result
}

func envelopeContainsField(
	envelope *credential.CredentialEnvelope,
	reference cryptokit.FieldReference,
) bool {
	for _, field := range envelope.Fields() {
		if field.FieldType == reference.FieldType {
			return field.EncryptionVersion == reference.EncryptionVersion &&
				field.CiphertextDigest == reference.ObjectHash &&
				field.WrappedKeyDigest == reference.EnvelopeHash
		}
	}
	return false
}

func objectPath(digest [sha256.Size]byte) string {
	encoded := hex.EncodeToString(digest[:])
	return "objects/sha256/" + encoded[:2] + "/" + encoded[2:4] + "/" + encoded + ".obj"
}

func bytesAllZero(value []byte) bool {
	var accumulator byte
	for _, item := range value {
		accumulator |= item
	}
	return accumulator == 0
}

func cloneHash(value *[sha256.Size]byte) *[sha256.Size]byte {
	if value == nil {
		return nil
	}
	result := *value
	return &result
}

// ChainContextSigner lets the session derive audit keys in the exact chain
// domain used by the device signer.
type ChainContextSigner interface {
	DeviceControlSigner
	ChainID() string
}
