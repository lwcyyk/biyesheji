package researchsync

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"vdns.local/vdns/internal/adapters/outbound/memorysync"
	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
	syncdomain "vdns.local/vdns/internal/sync/domain"
)

func TestResearchHTTPAdapterTenThousandObjectBatchAndManifestPaging(t *testing.T) {
	server, err := NewServer(16<<20, 250)
	if err != nil {
		t.Fatal(err)
	}
	httpServer := httptest.NewServer(server)
	defer httpServer.Close()
	client, err := NewClient(httpServer.URL, httpServer.Client(), 1, 250)
	if err != nil {
		t.Fatal(err)
	}

	const objectCount = 10_000
	uploads := make([]ObjectUpload, objectCount)
	for index := range uploads {
		object := []byte(fmt.Sprintf("encrypted-object-%05d", index))
		uploads[index] = ObjectUpload{
			Reference: platform.ObjectRef{
				Digest: sha256.Sum256(object), Size: uint64(len(object)),
			},
			Object: object,
		}
	}
	if err := client.PutObjects(
		context.Background(), uploads, "ten-thousand",
	); err != nil {
		t.Fatal(err)
	}
	// An identical retry is idempotent and does not create divergent content.
	if err := client.PutObjects(
		context.Background(), uploads, "ten-thousand",
	); err != nil {
		t.Fatal(err)
	}
	for _, index := range []int{0, objectCount / 2, objectCount - 1} {
		got, fetchErr := client.FetchObject(
			context.Background(), uploads[index].Reference,
		)
		if fetchErr != nil || !bytes.Equal(got, uploads[index].Object) {
			t.Fatalf("fetch %d = %q, %v", index, got, fetchErr)
		}
	}

	namespaceID := testNamespace(0x11)
	for index := 0; index < 3; index++ {
		record := testManifestRecord(namespaceID, byte(index+1))
		reference := syncdomain.ObjectReference{
			ObjectDigest: uploads[index].Reference.Digest,
			ObjectType:   protocol.ObjectTypeCredentialEnvelope,
			Size:         uploads[index].Reference.Size,
		}
		if err := client.PublishManifest(
			context.Background(), record, []syncdomain.ObjectReference{reference},
		); err != nil {
			t.Fatal(err)
		}
	}
	page, err := client.PullManifests(
		context.Background(), namespaceID, "", 2,
	)
	if err != nil || len(page.Items) != 2 || page.NextCursor == "" {
		t.Fatalf("first page = %+v, %v", page, err)
	}
	second, err := client.PullManifests(
		context.Background(), namespaceID, page.NextCursor, 2,
	)
	if err != nil || len(second.Items) != 1 || second.NextCursor != "" {
		t.Fatalf("second page = %+v, %v", second, err)
	}
}

func TestResearchHTTPAdapterFaultAndRetryMatrix(t *testing.T) {
	server, _ := NewServer(1<<20, 8)
	httpServer := httptest.NewServer(server)
	defer httpServer.Close()
	client, _ := NewClient(httpServer.URL, httpServer.Client(), 2, 8)
	object := []byte("ciphertext")
	upload := ObjectUpload{
		Reference: platform.ObjectRef{
			Digest: sha256.Sum256(object), Size: uint64(len(object)),
		},
		Object: object,
	}

	server.SetFaults(Faults{TemporaryFailures: 2})
	if err := client.PutObject(
		context.Background(), upload.Reference, upload.Object,
	); err != nil {
		t.Fatalf("retry did not recover: %v", err)
	}

	corrupt := upload.Reference.Digest
	server.SetFaults(Faults{
		Cloud: memorysync.Faults{CorruptObject: &corrupt},
	})
	if _, err := client.FetchObject(
		context.Background(), upload.Reference,
	); !errors.Is(err, syncdomain.ErrCloudObjectCorrupt) {
		t.Fatalf("corrupt object error = %v", err)
	}
	omit := upload.Reference.Digest
	server.SetFaults(Faults{
		Cloud: memorysync.Faults{OmitObject: &omit},
	})
	if _, err := client.FetchObject(
		context.Background(), upload.Reference,
	); !errors.Is(err, syncdomain.ErrCloudObjectMissing) {
		t.Fatalf("missing object error = %v", err)
	}

	server.SetFaults(Faults{TruncateResponses: true})
	if _, err := client.FetchObject(
		context.Background(), upload.Reference,
	); !errors.Is(err, syncdomain.ErrCloudObjectCorrupt) {
		t.Fatalf("truncated object error = %v", err)
	}

	partial := 0
	server.SetFaults(Faults{PartialBatchAfter: &partial})
	if err := client.PutObjects(
		context.Background(), []ObjectUpload{upload}, "partial",
	); !errors.Is(err, ErrRemote) {
		t.Fatalf("partial batch error = %v", err)
	}

	timeoutClient := &http.Client{Timeout: 5 * time.Millisecond}
	timeoutAdapter, _ := NewClient(httpServer.URL, timeoutClient, 0, 8)
	server.SetFaults(Faults{Delay: 100 * time.Millisecond})
	if err := timeoutAdapter.PutObject(
		context.Background(), upload.Reference, upload.Object,
	); !errors.Is(err, ErrRemote) {
		t.Fatalf("timeout error = %v", err)
	}
}

func TestResearchHTTPAdapterCloudCanHideBranchAndReturnOldManifest(t *testing.T) {
	server, _ := NewServer(1<<20, 4)
	httpServer := httptest.NewServer(server)
	defer httpServer.Close()
	client, _ := NewClient(httpServer.URL, httpServer.Client(), 0, 4)
	namespaceID := testNamespace(0x21)

	uploads := make([]ObjectUpload, 2)
	for index := range uploads {
		data := []byte{byte(index + 1), 0xaa}
		uploads[index] = ObjectUpload{
			Reference: platform.ObjectRef{
				Digest: sha256.Sum256(data), Size: uint64(len(data)),
			},
			Object: data,
		}
	}
	if err := client.PutObjects(context.Background(), uploads, "branches"); err != nil {
		t.Fatal(err)
	}
	for index, upload := range uploads {
		record := testManifestRecord(namespaceID, byte(index+1))
		if err := client.PublishManifest(
			context.Background(), record,
			[]syncdomain.ObjectReference{{
				ObjectDigest: upload.Reference.Digest,
				ObjectType:   protocol.ObjectTypeCredentialEnvelope,
				Size:         upload.Reference.Size,
			}},
		); err != nil {
			t.Fatal(err)
		}
	}

	hideAfter := 1
	server.SetFaults(Faults{
		Cloud: memorysync.Faults{HideAfterIndex: &hideAfter},
	})
	page, err := client.PullManifests(context.Background(), namespaceID, "", 10)
	if err != nil || len(page.Items) != 1 ||
		page.Items[0].ManifestDigest != testManifestRecord(namespaceID, 1).ManifestDigest {
		t.Fatalf("hidden branch/old manifest page = %+v, %v", page, err)
	}
	// This test demonstrates transport adversarial behavior only. A receiver
	// must compare the page with VDNS finalized/conflict state before accepting.
}

func TestResearchHTTPAdapterRejectsIdempotencyReuseAndOversizeBody(t *testing.T) {
	server, _ := NewServer(32, 2)
	httpServer := httptest.NewServer(server)
	defer httpServer.Close()
	digest := sha256.Sum256([]byte("a"))
	endpoint := fmt.Sprintf(
		"%s/research-sync/v1/objects/%x?size=1", httpServer.URL, digest,
	)
	put := func(body []byte, key string) int {
		request, _ := http.NewRequest(http.MethodPut, endpoint, bytes.NewReader(body))
		request.Header.Set("Idempotency-Key", key)
		response, err := httpServer.Client().Do(request)
		if err != nil {
			t.Fatal(err)
		}
		defer response.Body.Close()
		return response.StatusCode
	}
	if got := put([]byte("a"), "same"); got != http.StatusNoContent {
		t.Fatalf("first status = %d", got)
	}
	if got := put([]byte("b"), "same"); got != http.StatusConflict {
		t.Fatalf("reuse status = %d", got)
	}

	request, _ := http.NewRequest(
		http.MethodPost,
		httpServer.URL+"/research-sync/v1/objects:batch",
		bytes.NewReader(bytes.Repeat([]byte("x"), 64)),
	)
	request.Header.Set("Idempotency-Key", "oversize")
	response, err := httpServer.Client().Do(request)
	if err != nil {
		t.Fatal(err)
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusRequestEntityTooLarge {
		t.Fatalf("oversize status = %d", response.StatusCode)
	}
}

func TestResearchHTTPAdapterNetworkInterruption(t *testing.T) {
	server, _ := NewServer(1<<20, 2)
	httpServer := httptest.NewServer(server)
	client, _ := NewClient(httpServer.URL, httpServer.Client(), 0, 2)
	httpServer.Close()
	object := []byte("offline")
	reference := platform.ObjectRef{
		Digest: sha256.Sum256(object), Size: uint64(len(object)),
	}
	if err := client.PutObject(
		context.Background(), reference, object,
	); !errors.Is(err, ErrRemote) {
		t.Fatalf("network interruption error = %v", err)
	}
}

func testNamespace(fill byte) protocol.NamespaceID {
	var result protocol.NamespaceID
	for index := range result {
		result[index] = fill
	}
	return result
}

func testManifestRecord(
	namespaceID protocol.NamespaceID,
	fill byte,
) syncdomain.ManifestRecord {
	input := []byte{fill, 0x90}
	var signature protocol.Signature
	for index := range signature {
		signature[index] = fill
	}
	digest := sha256.Sum256([]byte{fill})
	return syncdomain.ManifestRecord{
		NamespaceID: namespaceID, ManifestDigest: digest,
		SigInputCBOR: input, Signature: signature,
	}
}

func TestDigestWireRequiresCanonicalLowercase(t *testing.T) {
	digest := sha256.Sum256([]byte("case"))
	value := hex.EncodeToString(digest[:])
	if _, err := decodeDigest(value); err != nil {
		t.Fatal(err)
	}
	if _, err := decodeDigest(strings.ToUpper(value)); !errors.Is(err, ErrInvalidRequest) {
		t.Fatalf("uppercase digest error = %v", err)
	}
}
