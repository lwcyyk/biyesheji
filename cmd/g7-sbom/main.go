// Command g7-sbom emits a deterministic CycloneDX inventory and a separately
// reviewable license inventory from the resolved Go module graph.
package main

import (
	"bufio"
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
)

type module struct {
	Path     string `json:"Path"`
	Version  string `json:"Version"`
	Sum      string `json:"Sum"`
	Dir      string `json:"Dir"`
	GoMod    string `json:"GoMod"`
	Main     bool   `json:"Main"`
	Indirect bool   `json:"Indirect"`
}

type property struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

type licenseChoice struct {
	License struct {
		ID string `json:"id"`
	} `json:"license"`
}

type component struct {
	Type       string          `json:"type"`
	BOMRef     string          `json:"bom-ref"`
	Group      string          `json:"group,omitempty"`
	Name       string          `json:"name"`
	Version    string          `json:"version"`
	Scope      string          `json:"scope"`
	PURL       string          `json:"purl"`
	Licenses   []licenseChoice `json:"licenses,omitempty"`
	Properties []property      `json:"properties,omitempty"`
}

type dependency struct {
	Ref       string   `json:"ref"`
	DependsOn []string `json:"dependsOn"`
}

type bom struct {
	BOMFormat    string `json:"bomFormat"`
	SpecVersion  string `json:"specVersion"`
	SerialNumber string `json:"serialNumber"`
	Version      int    `json:"version"`
	Metadata     struct {
		Tools []struct {
			Vendor  string `json:"vendor"`
			Name    string `json:"name"`
			Version string `json:"version"`
		} `json:"tools"`
		Component component `json:"component"`
	} `json:"metadata"`
	Components   []component  `json:"components"`
	Dependencies []dependency `json:"dependencies"`
}

type licenseRecord struct {
	Module       string `json:"module"`
	Version      string `json:"version"`
	License      string `json:"license"`
	LicenseFile  string `json:"licenseFile,omitempty"`
	LicenseHash  string `json:"licenseHash,omitempty"`
	ReviewStatus string `json:"reviewStatus"`
}

func main() {
	output := flag.String("out", "docs/security/vdns-pm.cdx.json", "CycloneDX output")
	licensesOutput := flag.String("licenses-out", "docs/security/licenses.json", "license inventory output")
	flag.Parse()
	modules, goVersion, err := resolvedModules()
	if err != nil {
		fatal(err)
	}
	result, licenses, err := buildBOM(modules, goVersion)
	if err != nil {
		fatal(err)
	}
	if err := os.MkdirAll(filepath.Dir(*output), 0o750); err != nil {
		fatal(err)
	}
	if err := writeJSON(*output, result); err != nil {
		fatal(err)
	}
	if err := writeJSON(*licensesOutput, map[string]any{
		"schemaVersion": "1.0.0",
		"policy": map[string]any{
			"allowed":               []string{"Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MIT", "MPL-2.0"},
			"denied":                []string{"AGPL-*", "GPL-*", "SSPL-*"},
			"unknownRequiresReview": true,
		},
		"modules": licenses,
	}); err != nil {
		fatal(err)
	}
	fmt.Println("g7-sbom-ok")
}

func resolvedModules() ([]module, string, error) {
	command := exec.Command("go", "list", "-m", "-json", "all")
	command.Env = withoutEnvironment(os.Environ(), "GOPATH")
	output, err := command.Output()
	if err != nil {
		return nil, "", err
	}
	decoder := json.NewDecoder(bytes.NewReader(output))
	var modules []module
	for decoder.More() {
		var current module
		if err := decoder.Decode(&current); err != nil {
			return nil, "", err
		}
		modules = append(modules, current)
	}
	versionCommand := exec.Command("go", "env", "GOVERSION")
	versionCommand.Env = withoutEnvironment(os.Environ(), "GOPATH")
	versionBytes, err := versionCommand.Output()
	if err != nil {
		return nil, "", err
	}
	return modules, strings.TrimSpace(string(versionBytes)), nil
}

func buildBOM(modules []module, goVersion string) (bom, []licenseRecord, error) {
	if len(modules) == 0 || !modules[0].Main {
		return bom{}, nil, errors.New("main module missing")
	}
	goSum, err := os.ReadFile("go.sum")
	if err != nil {
		return bom{}, nil, err
	}
	serialDigest := sha256.Sum256(append([]byte(goVersion+"\x00"), goSum...))
	serialHex := hex.EncodeToString(serialDigest[:16])
	serial := fmt.Sprintf(
		"urn:uuid:%s-%s-%s-%s-%s",
		serialHex[0:8], serialHex[8:12], serialHex[12:16],
		serialHex[16:20], serialHex[20:32],
	)
	root := component{
		Type: "application", BOMRef: "pkg:golang/vdns.local/vdns",
		Name: "vdns-pm", Version: "0.7.0", Scope: "required",
		PURL: "pkg:golang/vdns.local/vdns",
		Properties: []property{
			{Name: "vdns:protocol", Value: "VDNS-PM/2"},
			{Name: "vdns:suite", Value: "VDNS-PM-CP-2"},
			{Name: "vdns:go-toolchain", Value: goVersion},
		},
	}
	result := bom{
		BOMFormat: "CycloneDX", SpecVersion: "1.5",
		SerialNumber: serial, Version: 1,
	}
	result.Metadata.Tools = append(result.Metadata.Tools, struct {
		Vendor  string `json:"vendor"`
		Name    string `json:"name"`
		Version string `json:"version"`
	}{Vendor: "VDNS-PM", Name: "g7-sbom", Version: "1.0.0"})
	result.Metadata.Component = root
	var licenses []licenseRecord
	rootDependency := dependency{Ref: root.BOMRef}
	for _, current := range modules {
		if current.Main {
			continue
		}
		name := current.Path
		group := ""
		if before, after, ok := strings.Cut(current.Path, "/"); ok {
			group, name = before, after
		}
		bomRef := "pkg:golang/" + current.Path + "@" + url.PathEscape(current.Version)
		licenseID, file, digest := detectLicense(current.Dir)
		scope := "required"
		if current.Indirect {
			scope = "optional"
		}
		item := component{
			Type: "library", BOMRef: bomRef, Group: group, Name: name,
			Version: current.Version, Scope: scope, PURL: bomRef,
			Properties: []property{
				{Name: "vdns:go-module-path", Value: current.Path},
				{Name: "vdns:go-module-sum", Value: current.Sum},
				{Name: "vdns:dependency-kind", Value: scope},
			},
		}
		if licenseID != "NOASSERTION" {
			var choice licenseChoice
			choice.License.ID = licenseID
			item.Licenses = []licenseChoice{choice}
		}
		result.Components = append(result.Components, item)
		rootDependency.DependsOn = append(rootDependency.DependsOn, bomRef)
		review := "APPROVED"
		if licenseID == "NOASSERTION" {
			review = "MANUAL_REVIEW_REQUIRED"
		}
		licenses = append(licenses, licenseRecord{
			Module: current.Path, Version: current.Version, License: licenseID,
			LicenseFile: file, LicenseHash: digest, ReviewStatus: review,
		})
	}
	sort.Slice(result.Components, func(i, j int) bool {
		return result.Components[i].BOMRef < result.Components[j].BOMRef
	})
	sort.Strings(rootDependency.DependsOn)
	sort.Slice(licenses, func(i, j int) bool { return licenses[i].Module < licenses[j].Module })
	result.Dependencies = []dependency{rootDependency}
	for _, current := range result.Components {
		result.Dependencies = append(result.Dependencies, dependency{Ref: current.BOMRef, DependsOn: []string{}})
	}
	return result, licenses, nil
}

func detectLicense(directory string) (string, string, string) {
	if directory == "" {
		return "NOASSERTION", "", ""
	}
	entries, err := os.ReadDir(directory)
	if err != nil {
		return "NOASSERTION", "", ""
	}
	for _, entry := range entries {
		upper := strings.ToUpper(entry.Name())
		if entry.IsDir() || (!strings.HasPrefix(upper, "LICENSE") &&
			!strings.HasPrefix(upper, "COPYING")) {
			continue
		}
		path := filepath.Join(directory, entry.Name())
		content, readErr := os.ReadFile(path)
		if readErr != nil || len(content) == 0 || len(content) > 1024*1024 {
			continue
		}
		digest := sha256.Sum256(content)
		return classifyLicense(content), entry.Name(), hex.EncodeToString(digest[:])
	}
	return "NOASSERTION", "", ""
}

func classifyLicense(content []byte) string {
	text := strings.ToLower(string(content))
	switch {
	case strings.Contains(text, "mozilla public license") &&
		strings.Contains(text, "version 2.0"):
		return "MPL-2.0"
	case strings.Contains(text, "apache license") && strings.Contains(text, "version 2.0"):
		return "Apache-2.0"
	case strings.Contains(text, "permission is hereby granted, free of charge"):
		return "MIT"
	case strings.Contains(text, "redistribution and use in source and binary forms") &&
		strings.Contains(text, "neither the name"):
		return "BSD-3-Clause"
	case strings.Contains(text, "redistribution and use in source and binary forms"):
		return "BSD-2-Clause"
	case strings.Contains(text, "permission to use, copy, modify, and/or distribute"):
		return "ISC"
	default:
		scanner := bufio.NewScanner(bytes.NewReader(content))
		if scanner.Scan() && strings.Contains(strings.ToLower(scanner.Text()), "public domain") {
			return "NOASSERTION"
		}
		return "NOASSERTION"
	}
}

func withoutEnvironment(environment []string, key string) []string {
	prefix := key + "="
	filtered := make([]string, 0, len(environment))
	for _, entry := range environment {
		if !strings.HasPrefix(entry, prefix) {
			filtered = append(filtered, entry)
		}
	}
	return filtered
}

func writeJSON(path string, value any) error {
	encoded, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	encoded = append(encoded, '\n')
	return os.WriteFile(path, encoded, 0o640)
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, "g7-sbom:", err)
	os.Exit(1)
}
