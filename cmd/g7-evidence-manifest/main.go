// Command g7-evidence-manifest verifies the AC map and writes a deterministic
// SHA-256 manifest for final G7 machine evidence.
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

type acceptanceMap struct {
	SchemaVersion      string                `json:"schemaVersion"`
	SpecVersion        string                `json:"specVersion"`
	AcceptanceCriteria []acceptanceCriterion `json:"acceptanceCriteria"`
}

type acceptanceCriterion struct {
	ID       string   `json:"id"`
	Status   string   `json:"status"`
	Evidence []string `json:"evidence"`
}

type manifestEntry struct {
	Path   string `json:"path"`
	Bytes  int64  `json:"bytes"`
	SHA256 string `json:"sha256"`
}

type manifest struct {
	SchemaVersion       string          `json:"schemaVersion"`
	SpecVersion         string          `json:"specVersion"`
	Classification      string          `json:"classification"`
	AcceptancePassed    int             `json:"acceptancePassed"`
	AcceptanceTotal     int             `json:"acceptanceTotal"`
	AcceptanceMapSHA256 string          `json:"acceptanceMapSha256"`
	DatasetSHA256       string          `json:"datasetSha256"`
	SpecBaselineSHA256  string          `json:"specBaselineSha256"`
	Files               []manifestEntry `json:"files"`
	AggregateSHA256     string          `json:"aggregateSha256"`
}

func main() {
	repository := flag.String("repo", ".", "repository root")
	evidenceDirectory := flag.String("evidence", "test-results/g7", "evidence directory")
	mapPath := flag.String("map", "experiments/g7/ac-evidence-map.json", "acceptance evidence map")
	outputPath := flag.String("out", "test-results/g7/evidence-manifest.json", "manifest output")
	flag.Parse()

	root, err := filepath.Abs(*repository)
	if err != nil {
		fatal(err)
	}
	mapping, mapDigest, err := readAcceptanceMap(filepath.Join(root, *mapPath))
	if err != nil {
		fatal(err)
	}
	if err := verifyAcceptanceMap(root, mapping); err != nil {
		fatal(err)
	}

	outputAbsolute := filepath.Join(root, *outputPath)
	entries, err := walkEvidence(root, filepath.Join(root, *evidenceDirectory), outputAbsolute)
	if err != nil {
		fatal(err)
	}
	datasetDigest, err := hashFile(filepath.Join(root, "experiments/g7/datasets.json"))
	if err != nil {
		fatal(err)
	}
	baselineDigest, err := hashFile(filepath.Join(root, "specs/001-vdns-audit-rotation/BASELINE.json"))
	if err != nil {
		fatal(err)
	}
	passed := 0
	for _, criterion := range mapping.AcceptanceCriteria {
		if criterion.Status == "PASSED" {
			passed++
		}
	}
	result := manifest{
		SchemaVersion: "1.0.0", SpecVersion: mapping.SpecVersion,
		Classification:      "DETERMINISTIC_G7_EVIDENCE_MANIFEST",
		AcceptancePassed:    passed,
		AcceptanceTotal:     len(mapping.AcceptanceCriteria),
		AcceptanceMapSHA256: mapDigest,
		DatasetSHA256:       datasetDigest,
		SpecBaselineSHA256:  baselineDigest,
		Files:               entries,
		AggregateSHA256:     aggregateDigest(entries),
	}
	if err := writeJSON(outputAbsolute, result); err != nil {
		fatal(err)
	}
	fmt.Printf("g7-evidence-manifest-ok files=%d ac=%d/%d\n", len(entries), passed, len(mapping.AcceptanceCriteria))
}

func readAcceptanceMap(path string) (acceptanceMap, string, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return acceptanceMap{}, "", err
	}
	var mapping acceptanceMap
	if err := json.Unmarshal(content, &mapping); err != nil {
		return acceptanceMap{}, "", err
	}
	sum := sha256.Sum256(content)
	return mapping, hex.EncodeToString(sum[:]), nil
}

func verifyAcceptanceMap(root string, mapping acceptanceMap) error {
	if len(mapping.AcceptanceCriteria) != 21 {
		return fmt.Errorf("acceptance map must contain 21 criteria, got %d", len(mapping.AcceptanceCriteria))
	}
	seen := make(map[string]bool, len(mapping.AcceptanceCriteria))
	for index, criterion := range mapping.AcceptanceCriteria {
		expected := fmt.Sprintf("AC-%03d", index+1)
		if criterion.ID != expected {
			return fmt.Errorf("acceptance criterion %d must be %s, got %s", index, expected, criterion.ID)
		}
		if seen[criterion.ID] {
			return fmt.Errorf("duplicate acceptance criterion %s", criterion.ID)
		}
		seen[criterion.ID] = true
		if criterion.Status != "PASSED" {
			return fmt.Errorf("%s is not PASSED", criterion.ID)
		}
		if len(criterion.Evidence) == 0 {
			return fmt.Errorf("%s has no evidence", criterion.ID)
		}
		for _, evidencePath := range criterion.Evidence {
			clean := filepath.Clean(evidencePath)
			if filepath.IsAbs(clean) || clean == ".." || strings.HasPrefix(clean, ".."+string(filepath.Separator)) {
				return fmt.Errorf("%s contains unsafe evidence path %q", criterion.ID, evidencePath)
			}
			info, err := os.Stat(filepath.Join(root, clean))
			if err != nil {
				return fmt.Errorf("%s evidence %s: %w", criterion.ID, evidencePath, err)
			}
			if !info.Mode().IsRegular() {
				return fmt.Errorf("%s evidence is not a regular file: %s", criterion.ID, evidencePath)
			}
		}
	}
	return nil
}

func walkEvidence(root, evidenceDirectory, outputPath string) ([]manifestEntry, error) {
	var entries []manifestEntry
	err := filepath.WalkDir(evidenceDirectory, func(path string, entry os.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() {
			return nil
		}
		if path == outputPath {
			return nil
		}
		info, err := entry.Info()
		if err != nil {
			return err
		}
		if !info.Mode().IsRegular() {
			return fmt.Errorf("non-regular evidence file: %s", path)
		}
		digest, err := hashFile(path)
		if err != nil {
			return err
		}
		relative, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		entries = append(entries, manifestEntry{
			Path: filepath.ToSlash(relative), Bytes: info.Size(), SHA256: digest,
		})
		return nil
	})
	sort.Slice(entries, func(left, right int) bool { return entries[left].Path < entries[right].Path })
	return entries, err
}

func hashFile(path string) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()
	hash := sha256.New()
	if _, err := io.Copy(hash, file); err != nil {
		return "", err
	}
	return hex.EncodeToString(hash.Sum(nil)), nil
}

func aggregateDigest(entries []manifestEntry) string {
	hash := sha256.New()
	for _, entry := range entries {
		fmt.Fprintf(hash, "%s\x00%d\x00%s\n", entry.Path, entry.Bytes, entry.SHA256)
	}
	return hex.EncodeToString(hash.Sum(nil))
}

func writeJSON(path string, value any) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o750); err != nil {
		return err
	}
	content, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	content = append(content, '\n')
	temporary, err := os.CreateTemp(filepath.Dir(path), ".evidence-manifest-*")
	if err != nil {
		return err
	}
	temporaryName := temporary.Name()
	defer os.Remove(temporaryName)
	if err := temporary.Chmod(0o640); err != nil {
		temporary.Close()
		return err
	}
	if _, err := temporary.Write(content); err != nil {
		temporary.Close()
		return err
	}
	if err := temporary.Sync(); err != nil {
		temporary.Close()
		return err
	}
	if err := temporary.Close(); err != nil {
		return err
	}
	return os.Rename(temporaryName, path)
}

func fatal(err error) {
	if err == nil {
		err = errors.New("unknown error")
	}
	fmt.Fprintln(os.Stderr, "g7-evidence-manifest:", err)
	os.Exit(1)
}
