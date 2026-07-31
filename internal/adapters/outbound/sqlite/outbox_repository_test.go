//go:build linux

package sqlite

import (
	"bytes"
	"context"
	"errors"
	"testing"
)

func TestOperationOutboxLeaseRetryRestartAndIdempotentInclusion(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	fixture := newOperationFixture(t)
	first := fixture.sealAndSign(
		t, fixture.eventID, 1, nil, []byte("first durable event"),
	)
	firstPersisted, err := fixture.repository.CommitEvent(ctx, first.request)
	if err != nil {
		t.Fatal(err)
	}
	secondEventID := fixture.eventID
	secondEventID[0] ^= 0x41
	second := fixture.sealAndSign(
		t, secondEventID, 2, &firstPersisted.EventDigest, []byte("second durable event"),
	)
	if _, err := fixture.repository.CommitEvent(ctx, second.request); err != nil {
		t.Fatal(err)
	}

	const now = uint64(1_700_000_010_000)
	jobs, err := fixture.repository.ClaimReadyOutbox(ctx, ClaimOutboxRequest{
		NowMilliseconds: now, LeaseMilliseconds: 1_000, Limit: 10,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(jobs) != 2 {
		t.Fatalf("claimed jobs = %d", len(jobs))
	}
	byID := map[string]OutboxJob{
		string(jobs[0].EventID[:]): jobs[0],
		string(jobs[1].EventID[:]): jobs[1],
	}
	firstJob := byID[string(fixture.eventID[:])]
	secondJob := byID[string(secondEventID[:])]
	if firstJob.EventDigest != firstPersisted.EventDigest ||
		firstJob.ObjectReference != firstPersisted.ObjectReference ||
		!bytes.Equal(firstJob.SigInputCBOR, firstPersisted.SigInputCBOR) ||
		bytesAllZero(firstJob.LeaseToken[:]) {
		t.Fatal("claim changed immutable publication material")
	}
	if again, err := fixture.repository.ClaimReadyOutbox(ctx, ClaimOutboxRequest{
		NowMilliseconds: now + 500, LeaseMilliseconds: 1_000, Limit: 10,
	}); err != nil || len(again) != 0 {
		t.Fatalf("active lease reclaimed early: jobs=%d err=%v", len(again), err)
	}
	if err := fixture.repository.MarkOutboxRetry(ctx, MarkOutboxRetryRequest{
		EventID: fixture.eventID, LeaseToken: firstJob.LeaseToken,
		NowMilliseconds: now + 600, NextAttemptAtMS: now + 2_000,
		ErrorCode: "LOG_TEMPORARILY_UNAVAILABLE",
	}); err != nil {
		t.Fatal(err)
	}

	var sequence int
	var databaseName, databasePath string
	if err := fixture.identityDatabase().QueryRowContext(
		ctx, "PRAGMA database_list",
	).Scan(&sequence, &databaseName, &databasePath); err != nil {
		t.Fatal(err)
	}
	if err := fixture.database.Close(); err != nil {
		t.Fatal(err)
	}
	reopened, err := Open(ctx, databasePath)
	if err != nil {
		t.Fatal(err)
	}
	defer reopened.Close()
	fixture.database = reopened
	fixture.repository, err = NewOperationRepository(reopened)
	if err != nil {
		t.Fatal(err)
	}

	// The second worker crashed. Its lease is reclaimable after restart and
	// expiry, while the first job still respects its persisted retry backoff.
	reclaimed, err := fixture.repository.ClaimReadyOutbox(ctx, ClaimOutboxRequest{
		NowMilliseconds: now + 1_500, LeaseMilliseconds: 1_000, Limit: 10,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(reclaimed) != 1 || reclaimed[0].EventID != secondEventID ||
		reclaimed[0].LeaseToken == secondJob.LeaseToken {
		t.Fatal("restart did not reclaim exactly the expired lease")
	}
	logID := LogID{1, 2, 3, 4}
	if err := fixture.repository.MarkLogIncluded(ctx, MarkLogIncludedRequest{
		EventID: secondEventID, LeaseToken: reclaimed[0].LeaseToken,
		NowMilliseconds: now + 1_600, LogID: logID,
		LeafIndex: 0, IncludedTreeSize: 1,
	}); err != nil {
		t.Fatal(err)
	}

	retried, err := fixture.repository.ClaimReadyOutbox(ctx, ClaimOutboxRequest{
		NowMilliseconds: now + 2_500, LeaseMilliseconds: 1_000, Limit: 10,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(retried) != 1 || retried[0].EventID != fixture.eventID ||
		retried[0].RetryCount != 1 || retried[0].LeaseToken == firstJob.LeaseToken {
		t.Fatal("retry did not preserve counter or issue a new lease")
	}
	wrongToken := retried[0].LeaseToken
	wrongToken[0] ^= 1
	if err := fixture.repository.MarkLogIncluded(ctx, MarkLogIncludedRequest{
		EventID: fixture.eventID, LeaseToken: wrongToken,
		NowMilliseconds: now + 2_600, LogID: logID,
		LeafIndex: 1, IncludedTreeSize: 2,
	}); !errors.Is(err, ErrOutboxLeaseLost) {
		t.Fatalf("wrong lease error = %v", err)
	}
	inclusion := MarkLogIncludedRequest{
		EventID: fixture.eventID, LeaseToken: retried[0].LeaseToken,
		NowMilliseconds: now + 2_600, LogID: logID,
		LeafIndex: 1, IncludedTreeSize: 2,
	}
	if err := fixture.repository.MarkLogIncluded(ctx, inclusion); err != nil {
		t.Fatal(err)
	}
	if err := fixture.repository.MarkLogIncluded(ctx, inclusion); err != nil {
		t.Fatalf("idempotent inclusion retry: %v", err)
	}
	inclusion.LeafIndex = 0
	if err := fixture.repository.MarkLogIncluded(
		ctx, inclusion,
	); !errors.Is(err, ErrOutboxStateConflict) {
		t.Fatalf("conflicting inclusion error = %v", err)
	}
	assertScalar(t, reopened, "SELECT count(*) FROM event_publication_outbox WHERE publication_state = 'LOG_INCLUDED'", 2)
	assertScalar(t, reopened, "SELECT sum(retry_count) FROM event_publication_outbox", 1)
	assertScalar(t, reopened, "SELECT count(lease_token) FROM event_publication_outbox", 0)
}

func (fixture *operationFixture) identityDatabase() *Database {
	return fixture.database
}

func TestOperationOutboxRejectsInvalidLeaseRequests(t *testing.T) {
	t.Parallel()
	fixture := newOperationFixture(t)
	if _, err := fixture.repository.ClaimReadyOutbox(
		context.Background(),
		ClaimOutboxRequest{NowMilliseconds: 1, LeaseMilliseconds: 0, Limit: 1},
	); !errors.Is(err, ErrInvalidOutboxRequest) {
		t.Fatalf("zero lease error = %v", err)
	}
	if err := fixture.repository.MarkOutboxRetry(
		context.Background(),
		MarkOutboxRetryRequest{},
	); !errors.Is(err, ErrInvalidOutboxRequest) {
		t.Fatalf("empty retry error = %v", err)
	}
}
