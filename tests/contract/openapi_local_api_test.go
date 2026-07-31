package contract_test

import (
	"encoding/json"
	"os"
	"path/filepath"
	"reflect"
	"runtime"
	"sort"
	"strings"
	"testing"

	"vdns.local/vdns/internal/adapters/inbound/httpapi"
)

type openAPIDocument struct {
	Info struct {
		Version string `json:"version"`
	} `json:"info"`
	Security []map[string][]string `json:"security"`
	Paths    map[string]map[string]struct {
		OperationID string `json:"operationId"`
		Parameters  []struct {
			Ref string `json:"$ref"`
		} `json:"parameters"`
		Responses map[string]json.RawMessage `json:"responses"`
	} `json:"paths"`
	Components struct {
		SecuritySchemes map[string]struct {
			Type   string `json:"type"`
			Scheme string `json:"scheme"`
		} `json:"securitySchemes"`
		Schemas map[string]json.RawMessage `json:"schemas"`
	} `json:"components"`
}

func TestFrozenOpenAPIOperationsMatchImplementation(t *testing.T) {
	t.Parallel()
	document := loadOpenAPI(t)
	var contract []string
	for path, methods := range document.Paths {
		if !strings.HasPrefix(path, "/") {
			t.Fatalf("non-resource path %q", path)
		}
		for method, operation := range methods {
			switch method {
			case "get", "post", "delete", "put", "patch":
				if operation.OperationID == "" {
					t.Fatalf("%s %s has no operationId", method, path)
				}
				contract = append(contract, operation.OperationID)
			}
		}
	}
	implemented := httpapi.ImplementedOperationIDs()
	sort.Strings(contract)
	sort.Strings(implemented)
	if !reflect.DeepEqual(contract, implemented) {
		t.Fatalf("OpenAPI operations=%v implementation=%v", contract, implemented)
	}
	if document.Info.Version != "2.1.0" {
		t.Fatalf("OpenAPI version=%q", document.Info.Version)
	}
}

func TestOpenAPISecurityAndMutationHeaders(t *testing.T) {
	t.Parallel()
	document := loadOpenAPI(t)
	scheme, ok := document.Components.SecuritySchemes["InstallToken"]
	if !ok || scheme.Type != "http" || scheme.Scheme != "bearer" {
		t.Fatalf("InstallToken scheme=%+v", scheme)
	}
	if len(document.Security) != 1 {
		t.Fatalf("global security=%#v", document.Security)
	}
	if _, ok := document.Security[0]["InstallToken"]; !ok {
		t.Fatalf("global security=%#v", document.Security)
	}
	for path, methods := range document.Paths {
		for method, operation := range methods {
			if method != "post" {
				continue
			}
			refs := make(map[string]bool)
			for _, parameter := range operation.Parameters {
				refs[parameter.Ref] = true
			}
			if path != "/credential-route-resolutions" && path != "/vdns-resolutions" &&
				!refs["#/components/parameters/IdempotencyKey"] {
				t.Errorf("POST %s lacks Idempotency-Key", path)
			}
		}
	}
}

func TestOpenAPISecretValuesAreHandlesOnly(t *testing.T) {
	t.Parallel()
	document := loadOpenAPI(t)
	for schemaName, raw := range document.Components.Schemas {
		var schema any
		if err := json.Unmarshal(raw, &schema); err != nil {
			t.Fatalf("decode schema %s: %v", schemaName, err)
		}
		walkProperties(t, schemaName, schema)
	}
}

func walkProperties(t *testing.T, schemaName string, value any) {
	t.Helper()
	switch current := value.(type) {
	case map[string]any:
		if properties, ok := current["properties"].(map[string]any); ok {
			for property := range properties {
				lower := strings.ToLower(property)
				switch lower {
				case "masterpassword", "password", "recoverysecret", "rootsecret",
					"namespaceroot", "deviceprivatekey":
					t.Errorf("schema %s exposes forbidden secret property %q", schemaName, property)
				}
				if (strings.Contains(lower, "password") || strings.Contains(lower, "secret")) &&
					!strings.HasSuffix(lower, "handle") && !strings.HasSuffix(lower, "digest") {
					// Policy/analysis names are not values. Only reject likely
					// material-bearing properties.
					if strings.Contains(lower, "value") || strings.Contains(lower, "material") {
						t.Errorf("schema %s exposes secret material property %q", schemaName, property)
					}
				}
			}
		}
		for _, child := range current {
			walkProperties(t, schemaName, child)
		}
	case []any:
		for _, child := range current {
			walkProperties(t, schemaName, child)
		}
	}
}

func loadOpenAPI(t *testing.T) openAPIDocument {
	t.Helper()
	_, source, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("resolve contract test source")
	}
	root := filepath.Clean(filepath.Join(filepath.Dir(source), "..", ".."))
	path := filepath.Join(root, "specs", "001-vdns-audit-rotation", "contracts", "openapi.json")
	content, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read %s: %v", path, err)
	}
	var document openAPIDocument
	if err := json.Unmarshal(content, &document); err != nil {
		t.Fatalf("decode OpenAPI: %v", err)
	}
	return document
}
