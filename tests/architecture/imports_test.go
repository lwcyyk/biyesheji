package architecture_test

import (
	"encoding/json"
	"fmt"
	"io"
	"os/exec"
	"sort"
	"strings"
	"testing"
)

const modulePath = "vpass.local/vpass"

type listedPackage struct {
	ImportPath  string
	Imports     []string
	TestImports []string
}

func TestCoreImportBoundaries(t *testing.T) {
	command := exec.Command("go", "list", "-json", "./...")
	output, err := command.Output()
	if err != nil {
		if exitError, ok := err.(*exec.ExitError); ok {
			t.Fatalf("go list failed: %s", exitError.Stderr)
		}
		t.Fatal(err)
	}
	decoder := json.NewDecoder(strings.NewReader(string(output)))
	var violations []string
	for {
		var pkg listedPackage
		if err := decoder.Decode(&pkg); err == io.EOF {
			break
		} else if err != nil {
			t.Fatal(err)
		}
		imports := append(append([]string(nil), pkg.Imports...), pkg.TestImports...)
		for _, imported := range imports {
			if violation := importViolation(pkg.ImportPath, imported); violation != "" {
				violations = append(violations, violation)
			}
		}
	}
	if len(violations) != 0 {
		sort.Strings(violations)
		t.Fatalf("architecture boundary violations:\n%s", strings.Join(violations, "\n"))
	}
}

func importViolation(importer, imported string) string {
	if !strings.HasPrefix(importer, modulePath+"/") {
		return ""
	}
	if !strings.HasPrefix(importer, modulePath+"/cmd/") && strings.Contains(imported, "/internal/testkit") {
		return fmt.Sprintf("%s imports production-forbidden testkit %s", importer, imported)
	}
	if strings.Contains(importer, "/domain") || importer == modulePath+"/internal/protocol" ||
		importer == modulePath+"/internal/cryptokit" {
		for _, forbidden := range []string{
			modulePath + "/internal/adapters",
			"database/sql",
			"net/http",
			"os",
			"path/filepath",
		} {
			if imported == forbidden || strings.HasPrefix(imported, forbidden+"/") {
				return fmt.Sprintf("core package %s imports infrastructure %s", importer, imported)
			}
		}
	}
	if strings.Contains(importer, "/adapters/inbound/httpapi") &&
		strings.Contains(imported, "/adapters/outbound/") {
		return fmt.Sprintf("HTTP API %s imports repository implementation %s", importer, imported)
	}
	if strings.Contains(importer, "/domain") && strings.Contains(imported, "/domain") {
		importerModule := boundedModule(importer)
		importedModule := boundedModule(imported)
		if importerModule != "" && importedModule != "" && importerModule != importedModule {
			return fmt.Sprintf("domain %s crosses bounded context into %s", importer, imported)
		}
	}
	return ""
}

func boundedModule(path string) string {
	prefix := modulePath + "/internal/"
	if !strings.HasPrefix(path, prefix) {
		return ""
	}
	remainder := strings.TrimPrefix(path, prefix)
	module, _, found := strings.Cut(remainder, "/")
	if !found || module == "protocol" || module == "cryptokit" || module == "platform" {
		return ""
	}
	return module
}
