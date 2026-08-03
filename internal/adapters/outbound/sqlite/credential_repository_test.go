//go:build linux

package sqlite

import (
	"bytes"
	"context"
	"crypto/sha256"
	"errors"
	"sync"
	"testing"

	credential "vpass.local/vpass/internal/credential/domain"
	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
)

func TestCredentialRepositoryCASAllowsOnlyOneConcurrentVersion(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	identity := newOperationFixture(t)
	repository, err := NewCredentialRepository(identity.database)
	if err != nil {
		t.Fatal(err)
	}
	fieldRoot := credentialFieldRoot(t, identity.namespaceID)
	credentialID := identity.credentialID
	credentialID[0] ^= 0x6a
	originCommitment := sha256.Sum256([]byte("https://credential.example"))
	policyHash := sha256.Sum256([]byte("password-policy-v1"))

	username, usernamePath := storedCredentialField(
		t, identity, fieldRoot, credentialID, 1, cryptokit.FieldUsername, "alice@example.test",
	)
	passwordV1, passwordV1Path := storedCredentialField(
		t, identity, fieldRoot, credentialID, 1, cryptokit.FieldPassword, "password-v1",
	)
	v1, err := credential.NewVersionDraft(
		credentialID,
		1,
		1,
		credential.VersionActive,
		nil,
		policyHash,
		[]credential.FieldMapping{passwordV1, username},
	)
	if err != nil {
		t.Fatal(err)
	}
	v1Request := storedCredentialRequest(
		t,
		identity,
		v1,
		identity.namespaceID,
		originCommitment,
		nil,
		map[cryptokit.FieldType]string{
			cryptokit.FieldUsername: usernamePath,
			cryptokit.FieldPassword: passwordV1Path,
		},
		true,
		true,
		1_700_000_001_000,
	)
	created, err := repository.CommitVersion(ctx, v1Request)
	if err != nil {
		t.Fatal(err)
	}
	if created.CurrentLocalVersion != 1 || created.CurrentAcceptedVersion == nil || *created.CurrentAcceptedVersion != 1 {
		t.Fatalf("initial pointers = %+v", created)
	}

	previous := v1.DescriptorHash()
	expected := uint64(1)
	passwordA, passwordAPath := storedCredentialField(
		t, identity, fieldRoot, credentialID, 2, cryptokit.FieldPassword, "candidate-a",
	)
	passwordB, passwordBPath := storedCredentialField(
		t, identity, fieldRoot, credentialID, 2, cryptokit.FieldPassword, "candidate-b",
	)
	draftA, err := credential.NewVersionDraft(
		credentialID, 2, 2, credential.VersionPendingCandidate, &previous, policyHash,
		[]credential.FieldMapping{username, passwordA},
	)
	if err != nil {
		t.Fatal(err)
	}
	draftB, err := credential.NewVersionDraft(
		credentialID, 2, 2, credential.VersionPendingCandidate, &previous, policyHash,
		[]credential.FieldMapping{username, passwordB},
	)
	if err != nil {
		t.Fatal(err)
	}
	requestA := storedCredentialRequest(
		t,
		identity,
		draftA,
		identity.namespaceID,
		originCommitment,
		&expected,
		map[cryptokit.FieldType]string{
			cryptokit.FieldUsername: usernamePath,
			cryptokit.FieldPassword: passwordAPath,
		},
		false,
		false,
		1_700_000_002_000,
	)
	requestB := storedCredentialRequest(
		t,
		identity,
		draftB,
		identity.namespaceID,
		originCommitment,
		&expected,
		map[cryptokit.FieldType]string{
			cryptokit.FieldUsername: usernamePath,
			cryptokit.FieldPassword: passwordBPath,
		},
		false,
		false,
		1_700_000_002_001,
	)

	requests := []CommitCredentialVersionRequest{requestA, requestB}
	errorsByWriter := make([]error, len(requests))
	var wait sync.WaitGroup
	for index := range requests {
		index := index
		wait.Add(1)
		go func() {
			defer wait.Done()
			_, errorsByWriter[index] = repository.CommitVersion(ctx, requests[index])
		}()
	}
	wait.Wait()
	successes := 0
	conflicts := 0
	for _, commitErr := range errorsByWriter {
		switch {
		case commitErr == nil:
			successes++
		case errors.Is(commitErr, &CredentialCASConflictError{}):
			conflicts++
			var conflict *CredentialCASConflictError
			if !errors.As(commitErr, &conflict) || conflict.CurrentLocalVersion == nil || *conflict.CurrentLocalVersion != 1 {
				t.Fatalf("CAS conflict did not report current version: %v", commitErr)
			}
		default:
			t.Fatalf("unexpected concurrent commit error: %v", commitErr)
		}
	}
	if successes != 1 || conflicts != 1 {
		t.Fatalf("concurrent results: success=%d conflict=%d", successes, conflicts)
	}

	assertScalar(t, identity.database, "SELECT count(*) FROM credential_versions WHERE credential_id = x'"+hexID(credentialID[:])+"'", 2)
	assertScalar(t, identity.database, "SELECT current_local_version FROM credentials WHERE credential_id = x'"+hexID(credentialID[:])+"'", 1)
	assertScalar(t, identity.database, "SELECT current_accepted_version FROM credentials WHERE credential_id = x'"+hexID(credentialID[:])+"'", 1)
	assertScalar(t, identity.database, "SELECT count(*) FROM credential_versions WHERE credential_id = x'"+hexID(credentialID[:])+"' AND status = 'ACTIVE'", 1)
	assertScalar(t, identity.database, "SELECT count(*) FROM credential_versions WHERE credential_id = x'"+hexID(credentialID[:])+"' AND version = 2", 1)

	var usernameV1, usernameV2 []byte
	if err := identity.database.QueryRowContext(
		ctx,
		"SELECT object_hash FROM credential_version_fields WHERE credential_id = ? AND version = 1 AND field_type = 'USERNAME'",
		credentialID[:],
	).Scan(&usernameV1); err != nil {
		t.Fatal(err)
	}
	if err := identity.database.QueryRowContext(
		ctx,
		"SELECT object_hash FROM credential_version_fields WHERE credential_id = ? AND version = 2 AND field_type = 'USERNAME'",
		credentialID[:],
	).Scan(&usernameV2); err != nil {
		t.Fatal(err)
	}
	usernameObject := username.ObjectReference()
	if !bytes.Equal(usernameV1, usernameV2) || !bytes.Equal(usernameV1, usernameObject.Digest[:]) {
		t.Fatal("unchanged username object was rewritten during password candidate creation")
	}
}

func TestCredentialRepositoryRejectsStaleDescriptorWithoutPartialRows(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	identity := newOperationFixture(t)
	repository, _ := NewCredentialRepository(identity.database)
	fieldRoot := credentialFieldRoot(t, identity.namespaceID)
	credentialID := identity.credentialID
	credentialID[0] ^= 0x42
	origin := sha256.Sum256([]byte("origin"))
	policy := sha256.Sum256([]byte("policy"))
	password, passwordPath := storedCredentialField(t, identity, fieldRoot, credentialID, 1, cryptokit.FieldPassword, "v1")
	v1, _ := credential.NewVersionDraft(
		credentialID, 1, 1, credential.VersionActive, nil, policy, []credential.FieldMapping{password},
	)
	request := storedCredentialRequest(
		t, identity, v1, identity.namespaceID, origin, nil,
		map[cryptokit.FieldType]string{cryptokit.FieldPassword: passwordPath}, true, true, 1_700_000_003_000,
	)
	if _, err := repository.CommitVersion(ctx, request); err != nil {
		t.Fatal(err)
	}

	wrongPrevious := sha256.Sum256([]byte("stale descriptor"))
	passwordV2, passwordV2Path := storedCredentialField(t, identity, fieldRoot, credentialID, 2, cryptokit.FieldPassword, "v2")
	v2, _ := credential.NewVersionDraft(
		credentialID, 2, 2, credential.VersionPendingCandidate, &wrongPrevious, policy, []credential.FieldMapping{passwordV2},
	)
	expected := uint64(1)
	stale := storedCredentialRequest(
		t, identity, v2, identity.namespaceID, origin, &expected,
		map[cryptokit.FieldType]string{cryptokit.FieldPassword: passwordV2Path}, false, false, 1_700_000_004_000,
	)
	if _, err := repository.CommitVersion(ctx, stale); !errors.Is(err, &CredentialCASConflictError{}) {
		t.Fatalf("stale descriptor error = %v", err)
	}
	assertScalar(t, identity.database, "SELECT count(*) FROM credential_versions WHERE credential_id = x'"+hexID(credentialID[:])+"'", 1)
	assertScalar(t, identity.database, "SELECT count(*) FROM credential_version_fields WHERE credential_id = x'"+hexID(credentialID[:])+"'", 1)
}

func credentialFieldRoot(t *testing.T, namespaceID protocol.NamespaceID) *cryptokit.Key {
	t.Helper()
	root, err := cryptokit.NewSecret(bytes.Repeat([]byte{0x91}, cryptokit.KeySize))
	if err != nil {
		t.Fatal(err)
	}
	prk, err := cryptokit.ExtractNamespacePRK(root, namespaceID, 1)
	root.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	keys, err := cryptokit.DeriveNamespaceKeys(prk)
	prk.Destroy()
	if err != nil {
		t.Fatal(err)
	}
	keys.Name.Destroy()
	keys.Audit.Destroy()
	keys.Relation.Destroy()
	keys.Rotation.Destroy()
	t.Cleanup(keys.Wrap.Destroy)
	return keys.Wrap
}

func storedCredentialField(
	t *testing.T,
	identity *operationFixture,
	fieldRoot *cryptokit.Key,
	credentialID protocol.CredentialID,
	version uint64,
	fieldType cryptokit.FieldType,
	plaintextValue string,
) (credential.FieldMapping, string) {
	t.Helper()
	plaintext, err := cryptokit.NewSecret([]byte(plaintextValue))
	if err != nil {
		t.Fatal(err)
	}
	defer plaintext.Destroy()
	encrypted, err := cryptokit.EncryptField(fieldRoot, cryptokit.FieldContext{
		NamespaceID:       identity.namespaceID,
		CredentialID:      credentialID,
		CredentialVersion: version,
		FieldType:         fieldType,
		KeyGeneration:     1,
		CryptoPolicyHash:  sha256.Sum256([]byte("test-policy")),
		OriginBinding:     sha256.Sum256([]byte("test-origin-binding")),
	}, plaintext)
	if err != nil {
		t.Fatal(err)
	}
	encoded, err := encrypted.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	reference, err := identity.objectStore.PutIfAbsent(context.Background(), encoded)
	clear(encoded)
	if err != nil {
		t.Fatal(err)
	}
	path, err := identity.objectStore.RelativePath(reference)
	if err != nil {
		t.Fatal(err)
	}
	mapping, err := credential.NewFieldMapping(encrypted, reference)
	if err != nil {
		t.Fatal(err)
	}
	return mapping, path
}

func storedCredentialRequest(
	t *testing.T,
	identity *operationFixture,
	draft *credential.VersionDraft,
	namespaceID protocol.NamespaceID,
	origin [sha256.Size]byte,
	expected *uint64,
	fieldPaths map[cryptokit.FieldType]string,
	advanceLocal bool,
	advanceAccepted bool,
	createdAt uint64,
) CommitCredentialVersionRequest {
	t.Helper()
	descriptor := draft.DescriptorCBOR()
	reference, err := identity.objectStore.PutIfAbsent(context.Background(), descriptor)
	clear(descriptor)
	if err != nil {
		t.Fatal(err)
	}
	path, err := identity.objectStore.RelativePath(reference)
	if err != nil {
		t.Fatal(err)
	}
	return CommitCredentialVersionRequest{
		NamespaceID:            namespaceID,
		OriginCommitment:       origin,
		ExpectedLocalVersion:   expected,
		Draft:                  draft,
		DescriptorObject:       reference,
		DescriptorStoragePath:  path,
		FieldStoragePaths:      fieldPaths,
		AdvanceLocalPointer:    advanceLocal,
		AdvanceAcceptedPointer: advanceAccepted,
		CreatedAtMilliseconds:  createdAt,
	}
}

func hexID(value []byte) string {
	const digits = "0123456789abcdef"
	encoded := make([]byte, len(value)*2)
	for index, current := range value {
		encoded[index*2] = digits[current>>4]
		encoded[index*2+1] = digits[current&0x0f]
	}
	return string(encoded)
}
