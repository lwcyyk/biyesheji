// Package researchsync implements an HTTP sync adapter for controlled
// localhost experiments. It is an untrusted opaque-object transport and is not
// a production cloud service.
package researchsync

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"sync"
	"time"

	"vdns.local/vdns/internal/adapters/outbound/memorysync"
	"vdns.local/vdns/internal/platform"
	"vdns.local/vdns/internal/protocol"
	syncdomain "vdns.local/vdns/internal/sync/domain"
)

const (
	AdapterKind       = "RESEARCH_HTTP_SYNC_ADAPTER"
	DefaultMaxBody    = int64(16 << 20)
	DefaultBatchLimit = 256
)

var (
	ErrInvalidRequest      = errors.New("invalid research HTTP sync request")
	ErrBodyTooLarge        = errors.New("research HTTP sync request body too large")
	ErrIdempotencyConflict = errors.New("research HTTP sync idempotency conflict")
	ErrPartialResponse     = errors.New("research HTTP sync partial response")
	ErrRemote              = errors.New("research HTTP sync remote error")
)

// ObjectUpload is one opaque content-addressed object in a batch.
type ObjectUpload struct {
	Reference platform.ObjectRef
	Object    []byte
}

// Faults alter only the adapter's response view. They are available through a
// direct test hook and are deliberately not exposed as an HTTP control API.
type Faults struct {
	Cloud             memorysync.Faults
	Delay             time.Duration
	TemporaryFailures int
	PartialBatchAfter *int
	TruncateResponses bool
}

type idempotentResult struct {
	RequestDigest [sha256.Size]byte
	Status        int
	Body          []byte
}

// Server exposes a real HTTP boundary around the existing opaque cloud model.
type Server struct {
	mu         sync.Mutex
	store      *memorysync.Store
	maxBody    int64
	batchLimit int
	faults     Faults
	idempotent map[string]idempotentResult
}

func NewServer(maxBody int64, batchLimit int) (*Server, error) {
	if maxBody <= 0 || batchLimit < 1 || batchLimit > 10_000 {
		return nil, ErrInvalidRequest
	}
	return &Server{
		store: memorysync.New(), maxBody: maxBody, batchLimit: batchLimit,
		idempotent: make(map[string]idempotentResult),
	}, nil
}

func (server *Server) AdapterKind() string {
	return AdapterKind
}

func (server *Server) SetFaults(faults Faults) {
	if server == nil {
		return
	}
	server.mu.Lock()
	server.faults = faults
	server.store.SetFaults(faults.Cloud)
	server.mu.Unlock()
}

func (server *Server) ServeHTTP(writer http.ResponseWriter, request *http.Request) {
	if server == nil || request == nil {
		writeError(writer, http.StatusInternalServerError, ErrInvalidRequest)
		return
	}
	server.mu.Lock()
	faults := server.faults
	if server.faults.TemporaryFailures > 0 {
		server.faults.TemporaryFailures--
		server.mu.Unlock()
		writeError(writer, http.StatusServiceUnavailable, ErrRemote)
		return
	}
	server.mu.Unlock()
	if faults.Delay > 0 {
		timer := time.NewTimer(faults.Delay)
		defer timer.Stop()
		select {
		case <-request.Context().Done():
			return
		case <-timer.C:
		}
	}

	switch {
	case request.Method == http.MethodGet && request.URL.Path == "/research-sync/v1/meta":
		writeJSON(writer, http.StatusOK, map[string]any{
			"adapterKind": AdapterKind, "production": false,
		})
	case request.Method == http.MethodPost &&
		request.URL.Path == "/research-sync/v1/objects:batch":
		server.handleObjectBatch(writer, request, faults)
	case strings.HasPrefix(request.URL.Path, "/research-sync/v1/objects/"):
		server.handleObject(writer, request, faults)
	case request.URL.Path == "/research-sync/v1/manifests" &&
		request.Method == http.MethodPost:
		server.handleManifestPublish(writer, request, faults)
	case request.URL.Path == "/research-sync/v1/manifests" &&
		request.Method == http.MethodGet:
		server.handleManifestPull(writer, request, faults)
	default:
		writeError(writer, http.StatusNotFound, ErrInvalidRequest)
	}
}

type objectWire struct {
	Digest string `json:"digest"`
	Size   uint64 `json:"size"`
	Data   string `json:"data"`
}

type objectBatchWire struct {
	Objects []objectWire `json:"objects"`
}

func (server *Server) handleObjectBatch(
	writer http.ResponseWriter,
	request *http.Request,
	faults Faults,
) {
	body, ok := server.readIdempotentBody(writer, request)
	if !ok {
		return
	}
	var input objectBatchWire
	if json.Unmarshal(body, &input) != nil ||
		len(input.Objects) == 0 || len(input.Objects) > server.batchLimit {
		writeError(writer, http.StatusBadRequest, ErrInvalidRequest)
		return
	}
	accepted := len(input.Objects)
	if faults.PartialBatchAfter != nil && *faults.PartialBatchAfter < accepted {
		accepted = *faults.PartialBatchAfter
		if accepted < 0 {
			accepted = 0
		}
	}
	for index := 0; index < accepted; index++ {
		upload, err := decodeObject(input.Objects[index])
		if err != nil || server.store.PutObject(
			request.Context(), upload.Reference, upload.Object,
		) != nil {
			writeError(writer, http.StatusBadRequest, ErrInvalidRequest)
			return
		}
	}
	response := map[string]any{"accepted": accepted, "requested": len(input.Objects)}
	status := http.StatusOK
	if accepted != len(input.Objects) {
		status = http.StatusPartialContent
	}
	server.writeIdempotent(writer, request, body, status, response, faults)
}

func (server *Server) handleObject(
	writer http.ResponseWriter,
	request *http.Request,
	faults Faults,
) {
	digest, err := decodeDigest(strings.TrimPrefix(
		request.URL.Path, "/research-sync/v1/objects/",
	))
	size, sizeErr := strconv.ParseUint(request.URL.Query().Get("size"), 10, 64)
	if err != nil || sizeErr != nil || size == 0 {
		writeError(writer, http.StatusBadRequest, ErrInvalidRequest)
		return
	}
	reference := platform.ObjectRef{Digest: digest, Size: size}
	switch request.Method {
	case http.MethodPut:
		body, ok := server.readIdempotentBody(writer, request)
		if !ok {
			return
		}
		if putErr := server.store.PutObject(
			request.Context(), reference, body,
		); putErr != nil {
			writeError(writer, http.StatusBadRequest, putErr)
			return
		}
		server.writeIdempotent(
			writer, request, body, http.StatusNoContent, nil, faults,
		)
	case http.MethodGet:
		object, fetchErr := server.store.FetchObject(request.Context(), reference)
		if fetchErr != nil {
			status := http.StatusNotFound
			if errors.Is(fetchErr, syncdomain.ErrCloudObjectCorrupt) {
				status = http.StatusBadGateway
			}
			writeError(writer, status, fetchErr)
			return
		}
		writer.Header().Set("Content-Type", "application/octet-stream")
		writer.Header().Set("X-Content-SHA256", hex.EncodeToString(digest[:]))
		writer.WriteHeader(http.StatusOK)
		if faults.TruncateResponses && len(object) > 0 {
			object = object[:len(object)-1]
		}
		_, _ = writer.Write(object)
	default:
		writeError(writer, http.StatusMethodNotAllowed, ErrInvalidRequest)
	}
}

type manifestRecordWire struct {
	NamespaceID    string `json:"namespaceId"`
	ManifestDigest string `json:"manifestDigest"`
	SigInputCBOR   string `json:"sigInputCbor"`
	Signature      string `json:"signature"`
}

type objectReferenceWire struct {
	ObjectDigest string  `json:"objectDigest"`
	ObjectType   uint8   `json:"objectType"`
	CredentialID *string `json:"credentialId,omitempty"`
	Version      *uint64 `json:"version,omitempty"`
	Size         uint64  `json:"size"`
}

type manifestPublishWire struct {
	Record  manifestRecordWire    `json:"record"`
	Objects []objectReferenceWire `json:"objects"`
}

func (server *Server) handleManifestPublish(
	writer http.ResponseWriter,
	request *http.Request,
	faults Faults,
) {
	body, ok := server.readIdempotentBody(writer, request)
	if !ok {
		return
	}
	var input manifestPublishWire
	if json.Unmarshal(body, &input) != nil {
		writeError(writer, http.StatusBadRequest, ErrInvalidRequest)
		return
	}
	record, objects, err := decodeManifestPublish(input)
	if err != nil {
		writeError(writer, http.StatusBadRequest, err)
		return
	}
	if err := server.store.PublishManifest(
		request.Context(), record, objects,
	); err != nil {
		writeError(writer, http.StatusBadRequest, err)
		return
	}
	server.writeIdempotent(
		writer, request, body, http.StatusNoContent, nil, faults,
	)
}

type manifestPageWire struct {
	Items      []manifestRecordWire `json:"items"`
	NextCursor string               `json:"nextCursor,omitempty"`
}

func (server *Server) handleManifestPull(
	writer http.ResponseWriter,
	request *http.Request,
	faults Faults,
) {
	namespaceID, err := decodeNamespace(request.URL.Query().Get("namespaceId"))
	limit, limitErr := strconv.Atoi(request.URL.Query().Get("limit"))
	if err != nil || limitErr != nil {
		writeError(writer, http.StatusBadRequest, ErrInvalidRequest)
		return
	}
	page, pullErr := server.store.PullManifests(
		request.Context(), namespaceID, request.URL.Query().Get("cursor"), limit,
	)
	if pullErr != nil {
		writeError(writer, http.StatusBadRequest, pullErr)
		return
	}
	output := manifestPageWire{NextCursor: page.NextCursor}
	for _, item := range page.Items {
		output.Items = append(output.Items, encodeManifestRecord(item))
	}
	if faults.TruncateResponses {
		encoded, _ := json.Marshal(output)
		writer.Header().Set("Content-Type", "application/json")
		writer.WriteHeader(http.StatusOK)
		if len(encoded) > 0 {
			encoded = encoded[:len(encoded)-1]
		}
		_, _ = writer.Write(encoded)
		return
	}
	writeJSON(writer, http.StatusOK, output)
}

func (server *Server) readIdempotentBody(
	writer http.ResponseWriter,
	request *http.Request,
) ([]byte, bool) {
	key := strings.TrimSpace(request.Header.Get("Idempotency-Key"))
	if key == "" || len(key) > 200 {
		writeError(writer, http.StatusBadRequest, ErrInvalidRequest)
		return nil, false
	}
	body, err := io.ReadAll(http.MaxBytesReader(writer, request.Body, server.maxBody))
	if err != nil {
		writeError(writer, http.StatusRequestEntityTooLarge, ErrBodyTooLarge)
		return nil, false
	}
	digest := sha256.Sum256(body)
	server.mu.Lock()
	previous, found := server.idempotent[key]
	server.mu.Unlock()
	if found {
		if previous.RequestDigest != digest {
			writeError(writer, http.StatusConflict, ErrIdempotencyConflict)
			return nil, false
		}
		writer.WriteHeader(previous.Status)
		_, _ = writer.Write(previous.Body)
		return nil, false
	}
	return body, true
}

func (server *Server) writeIdempotent(
	writer http.ResponseWriter,
	request *http.Request,
	requestBody []byte,
	status int,
	value any,
	faults Faults,
) {
	var body []byte
	if value != nil {
		body, _ = json.Marshal(value)
		writer.Header().Set("Content-Type", "application/json")
	}
	server.mu.Lock()
	server.idempotent[request.Header.Get("Idempotency-Key")] = idempotentResult{
		RequestDigest: sha256.Sum256(requestBody), Status: status,
		Body: append([]byte(nil), body...),
	}
	server.mu.Unlock()
	writer.WriteHeader(status)
	if faults.TruncateResponses && len(body) > 0 {
		body = body[:len(body)-1]
	}
	_, _ = writer.Write(body)
}

// Client implements syncdomain.CloudStore over actual HTTP requests.
type Client struct {
	baseURL    string
	httpClient *http.Client
	maxRetries int
	batchLimit int
}

func NewClient(
	baseURL string,
	httpClient *http.Client,
	maxRetries int,
	batchLimit int,
) (*Client, error) {
	parsed, err := url.Parse(baseURL)
	if err != nil || parsed.Scheme == "" || parsed.Host == "" ||
		httpClient == nil || maxRetries < 0 ||
		batchLimit < 1 || batchLimit > 10_000 {
		return nil, ErrInvalidRequest
	}
	return &Client{
		baseURL: strings.TrimRight(baseURL, "/"), httpClient: httpClient,
		maxRetries: maxRetries, batchLimit: batchLimit,
	}, nil
}

func (client *Client) AdapterKind() string {
	return AdapterKind
}

func (client *Client) PutObject(
	ctx context.Context,
	reference platform.ObjectRef,
	object []byte,
) error {
	if reference.Size == 0 || uint64(len(object)) != reference.Size ||
		sha256.Sum256(object) != reference.Digest {
		return ErrInvalidRequest
	}
	endpoint := fmt.Sprintf(
		"%s/research-sync/v1/objects/%x?size=%d",
		client.baseURL, reference.Digest, reference.Size,
	)
	response, err := client.do(
		ctx, http.MethodPut, endpoint, object,
		"object-"+hex.EncodeToString(reference.Digest[:]),
	)
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusNoContent {
		return remoteError(response)
	}
	return nil
}

// PutObjects uploads in bounded batches and verifies that every request was
// fully accepted. The method supplements the one-object CloudStore contract.
func (client *Client) PutObjects(
	ctx context.Context,
	uploads []ObjectUpload,
	idempotencyPrefix string,
) error {
	if len(uploads) == 0 || strings.TrimSpace(idempotencyPrefix) == "" {
		return ErrInvalidRequest
	}
	for start := 0; start < len(uploads); start += client.batchLimit {
		end := start + client.batchLimit
		if end > len(uploads) {
			end = len(uploads)
		}
		wire := objectBatchWire{Objects: make([]objectWire, 0, end-start)}
		for _, upload := range uploads[start:end] {
			if upload.Reference.Size == 0 ||
				uint64(len(upload.Object)) != upload.Reference.Size ||
				sha256.Sum256(upload.Object) != upload.Reference.Digest {
				return ErrInvalidRequest
			}
			wire.Objects = append(wire.Objects, encodeObject(upload))
		}
		body, _ := json.Marshal(wire)
		response, err := client.do(
			ctx, http.MethodPost,
			client.baseURL+"/research-sync/v1/objects:batch", body,
			fmt.Sprintf("%s-%d-%d", idempotencyPrefix, start, end),
		)
		if err != nil {
			return err
		}
		var result struct {
			Accepted  int `json:"accepted"`
			Requested int `json:"requested"`
		}
		decodeErr := json.NewDecoder(response.Body).Decode(&result)
		response.Body.Close()
		if response.StatusCode != http.StatusOK {
			return remoteErrorStatus(response.StatusCode)
		}
		if decodeErr != nil || result.Accepted != end-start ||
			result.Requested != end-start {
			return ErrPartialResponse
		}
	}
	return nil
}

func (client *Client) FetchObject(
	ctx context.Context,
	reference platform.ObjectRef,
) ([]byte, error) {
	if reference.Size == 0 {
		return nil, ErrInvalidRequest
	}
	endpoint := fmt.Sprintf(
		"%s/research-sync/v1/objects/%x?size=%d",
		client.baseURL, reference.Digest, reference.Size,
	)
	response, err := client.do(ctx, http.MethodGet, endpoint, nil, "")
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()
	if response.StatusCode == http.StatusNotFound {
		return nil, syncdomain.ErrCloudObjectMissing
	}
	if response.StatusCode != http.StatusOK {
		return nil, remoteError(response)
	}
	body, err := io.ReadAll(response.Body)
	if err != nil || uint64(len(body)) != reference.Size ||
		sha256.Sum256(body) != reference.Digest {
		return nil, syncdomain.ErrCloudObjectCorrupt
	}
	return body, nil
}

func (client *Client) PublishManifest(
	ctx context.Context,
	record syncdomain.ManifestRecord,
	objects []syncdomain.ObjectReference,
) error {
	wire, err := encodeManifestPublish(record, objects)
	if err != nil {
		return err
	}
	body, _ := json.Marshal(wire)
	response, err := client.do(
		ctx, http.MethodPost, client.baseURL+"/research-sync/v1/manifests",
		body, "manifest-"+hex.EncodeToString(record.ManifestDigest[:]),
	)
	if err != nil {
		return err
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusNoContent {
		return remoteError(response)
	}
	return nil
}

func (client *Client) PullManifests(
	ctx context.Context,
	namespaceID protocol.NamespaceID,
	cursor string,
	limit int,
) (syncdomain.ManifestPage, error) {
	if allZero(namespaceID[:]) || limit < 1 || limit > 10_000 {
		return syncdomain.ManifestPage{}, ErrInvalidRequest
	}
	values := url.Values{}
	values.Set("namespaceId", hex.EncodeToString(namespaceID[:]))
	values.Set("cursor", cursor)
	values.Set("limit", strconv.Itoa(limit))
	response, err := client.do(
		ctx, http.MethodGet,
		client.baseURL+"/research-sync/v1/manifests?"+values.Encode(), nil, "",
	)
	if err != nil {
		return syncdomain.ManifestPage{}, err
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		return syncdomain.ManifestPage{}, remoteError(response)
	}
	var wire manifestPageWire
	if json.NewDecoder(response.Body).Decode(&wire) != nil {
		return syncdomain.ManifestPage{}, ErrPartialResponse
	}
	page := syncdomain.ManifestPage{NextCursor: wire.NextCursor}
	for _, item := range wire.Items {
		record, decodeErr := decodeManifestRecord(item)
		if decodeErr != nil {
			return syncdomain.ManifestPage{}, ErrPartialResponse
		}
		page.Items = append(page.Items, record)
	}
	return page, nil
}

func (client *Client) do(
	ctx context.Context,
	method, endpoint string,
	body []byte,
	idempotencyKey string,
) (*http.Response, error) {
	for attempt := 0; attempt <= client.maxRetries; attempt++ {
		request, err := http.NewRequestWithContext(
			ctx, method, endpoint, bytes.NewReader(body),
		)
		if err != nil {
			return nil, ErrInvalidRequest
		}
		if idempotencyKey != "" {
			request.Header.Set("Idempotency-Key", idempotencyKey)
		}
		if len(body) > 0 {
			request.Header.Set("Content-Type", "application/json")
		}
		response, err := client.httpClient.Do(request)
		if err == nil && response.StatusCode != http.StatusTooManyRequests &&
			response.StatusCode < http.StatusInternalServerError {
			return response, nil
		}
		if response != nil {
			_, _ = io.Copy(io.Discard, response.Body)
			response.Body.Close()
		}
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		if attempt == client.maxRetries {
			if err != nil {
				return nil, errors.Join(ErrRemote, err)
			}
			return nil, ErrRemote
		}
	}
	return nil, ErrRemote
}

func encodeObject(upload ObjectUpload) objectWire {
	return objectWire{
		Digest: hex.EncodeToString(upload.Reference.Digest[:]),
		Size:   upload.Reference.Size,
		Data:   base64.RawStdEncoding.EncodeToString(upload.Object),
	}
}

func decodeObject(wire objectWire) (ObjectUpload, error) {
	digest, err := decodeDigest(wire.Digest)
	object, objectErr := base64.RawStdEncoding.DecodeString(wire.Data)
	if err != nil || objectErr != nil || wire.Size == 0 ||
		uint64(len(object)) != wire.Size || sha256.Sum256(object) != digest {
		return ObjectUpload{}, ErrInvalidRequest
	}
	return ObjectUpload{
		Reference: platform.ObjectRef{Digest: digest, Size: wire.Size},
		Object:    object,
	}, nil
}

func encodeManifestPublish(
	record syncdomain.ManifestRecord,
	objects []syncdomain.ObjectReference,
) (manifestPublishWire, error) {
	if allZero(record.NamespaceID[:]) || allZero(record.ManifestDigest[:]) ||
		len(record.SigInputCBOR) == 0 || len(objects) == 0 {
		return manifestPublishWire{}, ErrInvalidRequest
	}
	output := manifestPublishWire{
		Record:  encodeManifestRecord(record),
		Objects: make([]objectReferenceWire, 0, len(objects)),
	}
	for _, object := range objects {
		wire := objectReferenceWire{
			ObjectDigest: hex.EncodeToString(object.ObjectDigest[:]),
			ObjectType:   uint8(object.ObjectType), Version: object.Version,
			Size: object.Size,
		}
		if object.CredentialID != nil {
			value := hex.EncodeToString(object.CredentialID[:])
			wire.CredentialID = &value
		}
		output.Objects = append(output.Objects, wire)
	}
	return output, nil
}

func decodeManifestPublish(
	wire manifestPublishWire,
) (syncdomain.ManifestRecord, []syncdomain.ObjectReference, error) {
	record, err := decodeManifestRecord(wire.Record)
	if err != nil || len(wire.Objects) == 0 ||
		len(wire.Objects) > syncdomain.MaxManifestObjects {
		return syncdomain.ManifestRecord{}, nil, ErrInvalidRequest
	}
	objects := make([]syncdomain.ObjectReference, 0, len(wire.Objects))
	for _, item := range wire.Objects {
		digest, digestErr := decodeDigest(item.ObjectDigest)
		if digestErr != nil || item.Size == 0 {
			return syncdomain.ManifestRecord{}, nil, ErrInvalidRequest
		}
		object := syncdomain.ObjectReference{
			ObjectDigest: digest, ObjectType: protocol.ObjectType(item.ObjectType),
			Version: item.Version, Size: item.Size,
		}
		if item.CredentialID != nil {
			value, credentialErr := decodeCredential(*item.CredentialID)
			if credentialErr != nil {
				return syncdomain.ManifestRecord{}, nil, ErrInvalidRequest
			}
			object.CredentialID = &value
		}
		objects = append(objects, object)
	}
	return record, objects, nil
}

func encodeManifestRecord(record syncdomain.ManifestRecord) manifestRecordWire {
	return manifestRecordWire{
		NamespaceID:    hex.EncodeToString(record.NamespaceID[:]),
		ManifestDigest: hex.EncodeToString(record.ManifestDigest[:]),
		SigInputCBOR:   base64.RawStdEncoding.EncodeToString(record.SigInputCBOR),
		Signature:      base64.RawStdEncoding.EncodeToString(record.Signature[:]),
	}
}

func decodeManifestRecord(wire manifestRecordWire) (syncdomain.ManifestRecord, error) {
	namespaceID, namespaceErr := decodeNamespace(wire.NamespaceID)
	digest, digestErr := decodeDigest(wire.ManifestDigest)
	input, inputErr := base64.RawStdEncoding.DecodeString(wire.SigInputCBOR)
	signatureBytes, signatureErr := base64.RawStdEncoding.DecodeString(wire.Signature)
	if namespaceErr != nil || digestErr != nil || inputErr != nil ||
		signatureErr != nil || len(input) == 0 ||
		len(signatureBytes) != len(protocol.Signature{}) {
		return syncdomain.ManifestRecord{}, ErrInvalidRequest
	}
	var signature protocol.Signature
	copy(signature[:], signatureBytes)
	return syncdomain.ManifestRecord{
		NamespaceID: namespaceID, ManifestDigest: digest,
		SigInputCBOR: input, Signature: signature,
	}, nil
}

func decodeDigest(value string) ([sha256.Size]byte, error) {
	var digest [sha256.Size]byte
	decoded, err := hex.DecodeString(value)
	if err != nil || len(decoded) != sha256.Size ||
		value != strings.ToLower(value) ||
		hex.EncodeToString(decoded) != value {
		return digest, ErrInvalidRequest
	}
	copy(digest[:], decoded)
	return digest, nil
}

func decodeNamespace(value string) (protocol.NamespaceID, error) {
	var result protocol.NamespaceID
	decoded, err := decodeFixedHex(value, len(result))
	copy(result[:], decoded)
	return result, err
}

func decodeCredential(value string) (protocol.CredentialID, error) {
	var result protocol.CredentialID
	decoded, err := decodeFixedHex(value, len(result))
	copy(result[:], decoded)
	return result, err
}

func decodeFixedHex(value string, size int) ([]byte, error) {
	decoded, err := hex.DecodeString(value)
	if err != nil || len(decoded) != size ||
		value != strings.ToLower(value) ||
		hex.EncodeToString(decoded) != value {
		return nil, ErrInvalidRequest
	}
	return decoded, nil
}

func remoteError(response *http.Response) error {
	body, _ := io.ReadAll(io.LimitReader(response.Body, 1024))
	if len(body) == 0 {
		return remoteErrorStatus(response.StatusCode)
	}
	return fmt.Errorf(
		"%w: HTTP %d: %s", ErrRemote, response.StatusCode,
		strings.TrimSpace(string(body)),
	)
}

func remoteErrorStatus(status int) error {
	return fmt.Errorf("%w: HTTP %d", ErrRemote, status)
}

func writeJSON(writer http.ResponseWriter, status int, value any) {
	writer.Header().Set("Content-Type", "application/json")
	writer.WriteHeader(status)
	_ = json.NewEncoder(writer).Encode(value)
}

func writeError(writer http.ResponseWriter, status int, err error) {
	writeJSON(writer, status, map[string]string{"error": err.Error()})
}

func allZero(value []byte) bool {
	var result byte
	for _, item := range value {
		result |= item
	}
	return result == 0
}
