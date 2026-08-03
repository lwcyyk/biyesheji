// Package mocksiteweb provides the deterministic browser-facing site used by
// G5 daily E2E tests. It is not a production authentication implementation.
package mocksiteweb

import (
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"encoding/json"
	"io"
	"net/http"
	"sync"

	"golang.org/x/crypto/pbkdf2"
)

const (
	maxBodyBytes = 16 * 1024
	iterations   = 100_000
)

type Outcome string

const (
	OutcomeSucceeded   Outcome = "SUCCEEDED"
	OutcomeFailed      Outcome = "FAILED"
	OutcomeMFARequired Outcome = "MFA_REQUIRED"
	OutcomeUnknown     Outcome = "UNKNOWN"
)

type accountRecord struct {
	salt     [16]byte
	verifier [sha256.Size]byte
	version  uint64
}

type Site struct {
	mu       sync.Mutex
	accounts map[string]accountRecord
	outcome  Outcome
}

func New() *Site {
	return &Site{accounts: make(map[string]accountRecord), outcome: OutcomeSucceeded}
}

func (site *Site) SetNextOutcome(outcome Outcome) {
	site.mu.Lock()
	defer site.mu.Unlock()
	site.outcome = outcome
}

func (site *Site) ServeHTTP(writer http.ResponseWriter, request *http.Request) {
	writer.Header().Set("Cache-Control", "no-store")
	if request.Method == http.MethodGet && request.URL.Path == "/" {
		writer.Header().Set("Content-Type", "text/html; charset=utf-8")
		_, _ = io.WriteString(writer, `<!doctype html><title>VPass Mock Site</title><form><input autocomplete="username"><input type="password" autocomplete="current-password"><input type="password" autocomplete="new-password"></form>`)
		return
	}
	if request.Method != http.MethodPost {
		writeSiteJSON(writer, http.StatusNotFound, map[string]any{"code": "NOT_FOUND"})
		return
	}
	request.Body = http.MaxBytesReader(writer, request.Body, maxBodyBytes)
	var input struct {
		AccountID       string `json:"accountId"`
		Password        string `json:"password,omitempty"`
		CurrentPassword string `json:"currentPassword,omitempty"`
		NewPassword     string `json:"newPassword,omitempty"`
		MFAProof        string `json:"mfaProof,omitempty"`
	}
	decoder := json.NewDecoder(request.Body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&input); err != nil || input.AccountID == "" ||
		len(input.AccountID) > 512 {
		writeSiteJSON(writer, http.StatusUnprocessableEntity, map[string]any{"code": "INVALID_INPUT"})
		return
	}
	switch request.URL.Path {
	case "/register":
		site.register(writer, input.AccountID, input.Password)
	case "/login":
		site.login(writer, input.AccountID, input.Password)
	case "/change-password":
		site.change(writer, input.AccountID, input.CurrentPassword, input.NewPassword, input.MFAProof)
	default:
		writeSiteJSON(writer, http.StatusNotFound, map[string]any{"code": "NOT_FOUND"})
	}
}

func (site *Site) register(writer http.ResponseWriter, accountID, password string) {
	if len(password) < 12 || len(password) > 256 {
		writeSiteJSON(writer, http.StatusUnprocessableEntity, map[string]any{"code": "POLICY_REJECTED"})
		return
	}
	record, ok := newAccount(password, 1)
	if !ok {
		writeSiteJSON(writer, http.StatusInternalServerError, map[string]any{"code": "SITE_ERROR"})
		return
	}
	site.mu.Lock()
	defer site.mu.Unlock()
	if _, exists := site.accounts[accountID]; exists {
		writeSiteJSON(writer, http.StatusConflict, map[string]any{"code": "ACCOUNT_EXISTS"})
		return
	}
	site.accounts[accountID] = record
	writeSiteJSON(writer, http.StatusCreated, map[string]any{"state": "REGISTERED", "version": 1})
}

func (site *Site) login(writer http.ResponseWriter, accountID, password string) {
	site.mu.Lock()
	record, exists := site.accounts[accountID]
	site.mu.Unlock()
	if !exists || !matches(record, password) {
		writeSiteJSON(writer, http.StatusUnauthorized, map[string]any{"code": "LOGIN_REJECTED"})
		return
	}
	writeSiteJSON(writer, http.StatusOK, map[string]any{"state": "AUTHENTICATED", "version": record.version})
}

func (site *Site) change(
	writer http.ResponseWriter,
	accountID, currentPassword, newPassword, mfaProof string,
) {
	site.mu.Lock()
	defer site.mu.Unlock()
	record, exists := site.accounts[accountID]
	if !exists || !matches(record, currentPassword) {
		writeSiteJSON(writer, http.StatusUnauthorized, map[string]any{"code": "LOGIN_REJECTED"})
		return
	}
	outcome := site.outcome
	site.outcome = OutcomeSucceeded
	if outcome == OutcomeMFARequired && mfaProof == "" {
		writeSiteJSON(writer, http.StatusOK, siteReceipt(accountID, record.version+1, OutcomeMFARequired))
		return
	}
	if outcome == OutcomeFailed || outcome == OutcomeUnknown {
		writeSiteJSON(writer, http.StatusOK, siteReceipt(accountID, record.version+1, outcome))
		return
	}
	if len(newPassword) < 12 || len(newPassword) > 256 {
		writeSiteJSON(writer, http.StatusOK, siteReceipt(accountID, record.version+1, OutcomeFailed))
		return
	}
	next, ok := newAccount(newPassword, record.version+1)
	if !ok {
		writeSiteJSON(writer, http.StatusInternalServerError, map[string]any{"code": "SITE_ERROR"})
		return
	}
	site.accounts[accountID] = next
	writeSiteJSON(writer, http.StatusOK, siteReceipt(accountID, next.version, OutcomeSucceeded))
}

func newAccount(password string, version uint64) (accountRecord, bool) {
	var record accountRecord
	if _, err := io.ReadFull(rand.Reader, record.salt[:]); err != nil {
		return accountRecord{}, false
	}
	derived := pbkdf2.Key([]byte(password), record.salt[:], iterations, sha256.Size, sha256.New)
	copy(record.verifier[:], derived)
	clear(derived)
	record.version = version
	return record, true
}

func matches(record accountRecord, password string) bool {
	derived := pbkdf2.Key([]byte(password), record.salt[:], iterations, sha256.Size, sha256.New)
	equal := subtle.ConstantTimeCompare(derived, record.verifier[:]) == 1
	clear(derived)
	return equal
}

func siteReceipt(accountID string, version uint64, outcome Outcome) map[string]any {
	digest := sha256.Sum256([]byte(accountID + "|" + string(outcome) + "|" + base64.RawURLEncoding.EncodeToString([]byte{byte(version)})))
	return map[string]any{
		"outcome": outcome, "version": version,
		"receiptDigest": base64.RawURLEncoding.EncodeToString(digest[:]),
	}
}

func writeSiteJSON(writer http.ResponseWriter, status int, value any) {
	writer.Header().Set("Content-Type", "application/json")
	writer.WriteHeader(status)
	_ = json.NewEncoder(writer).Encode(value)
}
