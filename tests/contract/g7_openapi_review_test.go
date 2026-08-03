package contract_test

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"sort"
	"strings"
	"testing"
)

func TestG7OpenAPIReferencesResolveAndOperationsAreUnique(t *testing.T) {
	t.Parallel()
	root, document := loadRawOpenAPI(t)
	seen := make(map[string]bool)
	walkJSON(t, document, func(path string, object map[string]any) {
		reference, ok := object["$ref"].(string)
		if !ok {
			return
		}
		if !strings.HasPrefix(reference, "#/") {
			t.Errorf("%s has non-local reference %q", path, reference)
			return
		}
		if _, ok := resolveJSONPointer(document, reference); !ok {
			t.Errorf("%s has unresolved reference %q", path, reference)
		}
	})
	paths := objectMap(t, document, "paths")
	resourcePath := regexp.MustCompile(`^/[a-z][a-z0-9-]*(/\{[a-z][A-Za-z0-9]*\}|/[a-z][a-z0-9-]*)*$`)
	for path, rawPath := range paths {
		if !resourcePath.MatchString(path) || strings.Contains(path, "_") {
			t.Errorf("path is not a kebab-case resource: %s", path)
		}
		for method, rawOperation := range mapValue(t, rawPath) {
			if !isHTTPMethod(method) {
				continue
			}
			operation := mapValue(t, rawOperation)
			operationID, _ := operation["operationId"].(string)
			if operationID == "" || seen[operationID] {
				t.Errorf("%s %s has missing/duplicate operationId %q", method, path, operationID)
			}
			seen[operationID] = true
		}
	}
	if len(seen) != 23 {
		t.Fatalf("operation count=%d, want 23", len(seen))
	}
	baseline := loadJSONFile(t, filepath.Join(root, "specs", "001-vdns-audit-rotation", "BASELINE.json"))
	artifacts := objectMap(t, baseline, "artifacts")
	expected, ok := artifacts["specs/001-vdns-audit-rotation/contracts/openapi.json"].(string)
	if !ok {
		t.Fatal("frozen OpenAPI digest missing from baseline")
	}
	content, err := os.ReadFile(filepath.Join(root, "specs", "001-vdns-audit-rotation", "contracts", "openapi.json"))
	if err != nil {
		t.Fatal(err)
	}
	actual := sha256.Sum256(content)
	if hex.EncodeToString(actual[:]) != expected {
		t.Fatal("OpenAPI changed without an explicit baseline amendment")
	}
}

func TestG7OpenAPIResolvedParametersErrorsPaginationAndSecretHandles(t *testing.T) {
	t.Parallel()
	_, document := loadRawOpenAPI(t)
	paths := objectMap(t, document, "paths")
	for path, rawPath := range paths {
		for method, rawOperation := range mapValue(t, rawPath) {
			if !isHTTPMethod(method) {
				continue
			}
			operation := mapValue(t, rawOperation)
			parameters := resolvedParameters(t, document, operation)
			for _, pathName := range pathParameters(path) {
				parameter, ok := parameters[pathName]
				if !ok || parameter["in"] != "path" || parameter["required"] != true {
					t.Errorf("%s %s lacks required path parameter %s", method, path, pathName)
				}
			}
			if method == "post" && path != "/credential-route-resolutions" &&
				path != "/state-resolutions" && path != "/vdns-resolutions" {
				if _, ok := parameters["Idempotency-Key"]; !ok {
					t.Errorf("POST %s lacks Idempotency-Key", path)
				}
			}
			if method == "get" && (path == "/credentials" || strings.HasSuffix(path, "/versions")) {
				limit, ok := parameters["limit"]
				if !ok {
					t.Errorf("GET %s lacks limit", path)
				} else {
					schema := mapValue(t, limit["schema"])
					if number(schema["maximum"]) != 200 || number(schema["default"]) != 50 {
						t.Errorf("GET %s limit schema=%v", path, schema)
					}
				}
				if _, ok := parameters["cursor"]; !ok {
					t.Errorf("GET %s lacks cursor", path)
				}
			}
			responses := mapValue(t, operation["responses"])
			for status, rawResponse := range responses {
				if status[0] != '4' && status[0] != '5' {
					continue
				}
				resolved := resolveObject(t, document, mapValue(t, rawResponse))
				content := mapValue(t, resolved["content"])
				media := mapValue(t, content["application/json"])
				schema := resolveObject(t, document, mapValue(t, media["schema"]))
				required := stringSet(schema["required"])
				if !required["code"] || !required["message"] || !required["requestId"] {
					t.Errorf("%s %s response %s is not the unified Error schema", method, path, status)
				}
			}
		}
	}
	components := objectMap(t, document, "components")
	schemas := objectMap(t, components, "schemas")
	for name, rawSchema := range schemas {
		walkJSON(t, rawSchema, func(path string, object map[string]any) {
			properties, ok := object["properties"].(map[string]any)
			if !ok {
				return
			}
			for property := range properties {
				lower := strings.ToLower(property)
				if lower == "password" || lower == "masterpassword" ||
					lower == "recoverysecret" || lower == "deviceprivatekey" {
					t.Errorf("schema %s%s exposes plaintext secret property %q", name, path, property)
				}
				if (strings.Contains(lower, "password") || strings.Contains(lower, "secret")) &&
					(strings.Contains(lower, "value") || strings.Contains(lower, "material")) &&
					!strings.HasSuffix(lower, "handle") && !strings.HasSuffix(lower, "digest") {
					t.Errorf("schema %s%s exposes secret material %q", name, path, property)
				}
			}
		})
	}
}

func loadRawOpenAPI(t *testing.T) (string, map[string]any) {
	t.Helper()
	_, source, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("resolve contract test source")
	}
	root := filepath.Clean(filepath.Join(filepath.Dir(source), "..", ".."))
	return root, loadJSONFile(
		t, filepath.Join(root, "specs", "001-vdns-audit-rotation", "contracts", "openapi.json"),
	)
}

func loadJSONFile(t *testing.T, path string) map[string]any {
	t.Helper()
	content, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var document map[string]any
	if err := json.Unmarshal(content, &document); err != nil {
		t.Fatal(err)
	}
	return document
}

func walkJSON(t *testing.T, value any, visit func(string, map[string]any)) {
	t.Helper()
	var walk func(string, any)
	walk = func(path string, current any) {
		switch typed := current.(type) {
		case map[string]any:
			visit(path, typed)
			keys := make([]string, 0, len(typed))
			for key := range typed {
				keys = append(keys, key)
			}
			sort.Strings(keys)
			for _, key := range keys {
				walk(path+"/"+key, typed[key])
			}
		case []any:
			for index, child := range typed {
				walk(path+"/"+string(rune(index)), child)
			}
		}
	}
	walk("", value)
}

func resolveJSONPointer(document map[string]any, reference string) (any, bool) {
	var current any = document
	for _, token := range strings.Split(strings.TrimPrefix(reference, "#/"), "/") {
		token = strings.ReplaceAll(strings.ReplaceAll(token, "~1", "/"), "~0", "~")
		object, ok := current.(map[string]any)
		if !ok {
			return nil, false
		}
		current, ok = object[token]
		if !ok {
			return nil, false
		}
	}
	return current, true
}

func resolveObject(t *testing.T, document map[string]any, object map[string]any) map[string]any {
	t.Helper()
	reference, ok := object["$ref"].(string)
	if !ok {
		return object
	}
	value, ok := resolveJSONPointer(document, reference)
	if !ok {
		t.Fatalf("unresolved reference %s", reference)
	}
	return mapValue(t, value)
}

func resolvedParameters(
	t *testing.T,
	document map[string]any,
	operation map[string]any,
) map[string]map[string]any {
	t.Helper()
	result := make(map[string]map[string]any)
	raw, _ := operation["parameters"].([]any)
	for _, item := range raw {
		parameter := resolveObject(t, document, mapValue(t, item))
		name, _ := parameter["name"].(string)
		if name == "" {
			t.Fatal("resolved parameter has no name")
		}
		result[name] = parameter
	}
	return result
}

func objectMap(t *testing.T, object map[string]any, key string) map[string]any {
	t.Helper()
	return mapValue(t, object[key])
}

func mapValue(t *testing.T, value any) map[string]any {
	t.Helper()
	typed, ok := value.(map[string]any)
	if !ok {
		t.Fatalf("expected JSON object, got %T", value)
	}
	return typed
}

func number(value any) int {
	switch typed := value.(type) {
	case float64:
		return int(typed)
	case int:
		return typed
	default:
		return 0
	}
}

func stringSet(value any) map[string]bool {
	result := make(map[string]bool)
	raw, _ := value.([]any)
	for _, item := range raw {
		if text, ok := item.(string); ok {
			result[text] = true
		}
	}
	return result
}

func pathParameters(path string) []string {
	var result []string
	for _, segment := range strings.Split(path, "/") {
		if strings.HasPrefix(segment, "{") && strings.HasSuffix(segment, "}") {
			result = append(result, strings.TrimSuffix(strings.TrimPrefix(segment, "{"), "}"))
		}
	}
	return result
}

func isHTTPMethod(value string) bool {
	switch value {
	case "get", "post", "put", "patch", "delete":
		return true
	default:
		return false
	}
}
