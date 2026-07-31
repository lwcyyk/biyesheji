package mocksiteweb

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestMockSiteRegistrationLoginAndOutcomes(t *testing.T) {
	t.Parallel()
	site := New()
	server := httptest.NewServer(site)
	defer server.Close()
	post := func(path string, input any) (int, map[string]any) {
		body, _ := json.Marshal(input)
		response, err := http.Post(server.URL+path, "application/json", bytes.NewReader(body))
		if err != nil {
			t.Fatal(err)
		}
		defer response.Body.Close()
		var value map[string]any
		if err := json.NewDecoder(response.Body).Decode(&value); err != nil {
			t.Fatal(err)
		}
		return response.StatusCode, value
	}
	if status, _ := post("/register", map[string]any{
		"accountId": "alice", "password": "initial-password-value",
	}); status != http.StatusCreated {
		t.Fatalf("register status=%d", status)
	}
	if status, _ := post("/login", map[string]any{
		"accountId": "alice", "password": "wrong-password-value",
	}); status != http.StatusUnauthorized {
		t.Fatalf("wrong login status=%d", status)
	}
	site.SetNextOutcome(OutcomeUnknown)
	status, result := post("/change-password", map[string]any{
		"accountId": "alice", "currentPassword": "initial-password-value",
		"newPassword": "replacement-password-value",
	})
	if status != http.StatusOK || result["outcome"] != string(OutcomeUnknown) {
		t.Fatalf("unknown = %d %#v", status, result)
	}
	if status, _ := post("/login", map[string]any{
		"accountId": "alice", "password": "initial-password-value",
	}); status != http.StatusOK {
		t.Fatalf("unknown changed password, login status=%d", status)
	}
}
