// Command g7-fault-runner executes the release fault matrix against real
// adapters and protocol tests. It records test output digests and never
// interprets a process exit as a successful business operation.
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

const seed = uint64(20260723)

type scenario struct {
	ID        string   `json:"id"`
	Component string   `json:"component"`
	Fault     string   `json:"fault"`
	Expected  string   `json:"expected"`
	Command   []string `json:"command"`
}

type result struct {
	scenario
	ExitCode            int    `json:"exitCode"`
	OutputDigest        string `json:"outputDigest"`
	OutputPath          string `json:"outputPath"`
	DurationNanoseconds int64  `json:"durationNanoseconds"`
	Passed              bool   `json:"passed"`
}

type evidence struct {
	SchemaVersion string   `json:"schemaVersion"`
	Seed          uint64   `json:"seed"`
	StartedAt     string   `json:"startedAt"`
	FinishedAt    string   `json:"finishedAt"`
	Scenarios     []result `json:"scenarios"`
	Passed        bool     `json:"passed"`
}

func main() {
	outputDirectory := flag.String("out", "test-results/g7/faults", "fault evidence directory")
	flag.Parse()
	if err := os.MkdirAll(*outputDirectory, 0o750); err != nil {
		fatal(err)
	}
	matrix := []scenario{
		{
			ID: "FI-CLOUD-001", Component: "encrypted-sync-service",
			Fault:    "cloud returns rollback, replacement, missing and incomplete objects",
			Expected: "candidate rejected before the single accepted-state commit",
			Command: []string{
				"go", "test", "-count=1", "./internal/sync/application",
				"-run", "TestAcceptanceRejectsMissingCorruptAndIncompleteObjectsWithoutCommit|TestAcceptanceRejectsCloudRollbackAndTrustedStateMismatch",
			},
		},
		{
			ID: "FI-LOG-001", Component: "transparency-log",
			Fault:    "inclusion path mutation, fork, old root and bad consistency proof",
			Expected: "proof verification or monitor rejects with no accepted transition",
			Command: []string{
				"go", "test", "-count=1", "./internal/transparency/domain", "./internal/monitoring/domain",
				"-run", "TestProofMutationRejected|TestMonitorDetectsForkRollbackAndBadConsistency",
			},
		},
		{
			ID: "FI-CHAIN-001", Component: "checkpoint-anchor",
			Fault:    "provider mismatch or local Anvil adapter presented as production consensus",
			Expected: "provider kind remains explicit and no production-consensus claim is emitted",
			Command: []string{
				"go", "test", "-count=1", "./internal/anchor/application", "./internal/adapters/outbound/anvilanchor",
				"-run", "TestPublisherLabelsSimulatorAndRejectsProviderMismatch|TestAnvilProviderNeverClaimsConsensus",
			},
		},
		{
			ID: "FI-NETWORK-001", Component: "browser-extension/local-secure-client/mock-site",
			Fault:    "Mock Site becomes unreachable after a verified local version is cached",
			Expected: "bounded offline read works; remote login and high-risk completion are not claimed",
			Command: []string{
				"go", "test", "-count=1", "./tests/e2e",
				"-run", "TestDailyMockSiteRegisterLoginChangeSyncRevokeAndOffline",
			},
		},
		{
			ID: "FI-DISK-001", Component: "object-store",
			Fault:    "object corruption, stale temporary file and unsafe symlink root",
			Expected: "corrupt object is rejected and recovery only quarantines scoped stale files",
			Command: []string{
				"go", "test", "-count=1", "./internal/adapters/outbound/objectfs",
				"-run", "TestCorruptionIsRejectedAndNeverOverwritten|TestSymlinkAndUnsafeRootsAreRejected|TestRecoverTemporaryQuarantinesOnlyStaleRegularFiles",
			},
		},
		{
			ID: "FI-PROCESS-001", Component: "local-secure-client/sqlite",
			Fault:    "handler or process restarts with durable idempotency/outbox state",
			Expected: "same request replays original result; pending and unknown are retained",
			Command: []string{
				"go", "test", "-count=1", "./internal/adapters/inbound/httpapi", "./internal/adapters/outbound/sqlite",
				"-run", "TestHTTPDurableIdempotencySurvivesHandlerRestart|TestLocalAPIRepositoryHashesKeysAndSurvivesRestart|TestOperationOutboxLeaseRetryRestartAndIdempotentInclusion|TestLocalOperationRepositoryRetainsPendingAndUnknown",
			},
		},
		{
			ID: "FI-LIFECYCLE-001", Component: "site-change-coordinator",
			Fault:    "site succeeds but response is lost, or site returns an explicit negative result",
			Expected: "UNKNOWN/review or retryable state is preserved; new version is not guessed active",
			Command: []string{
				"go", "test", "-count=1", "./internal/site/application",
				"-run", "TestCoordinatorRecoversLostResponseAndSeparatesUnknownReview|TestCoordinatorMapsNegativeReceiptsToRetryableWithoutActivation",
			},
		},
		{
			ID: "FI-REVOCATION-001", Component: "device-generation",
			Fault:    "revoked device requests next-generation root material",
			Expected: "new generation is encrypted only to remaining active devices",
			Command: []string{
				"go", "test", "-count=1", "./internal/device/domain",
				"-run", "TestGenerationRolloverEncryptsOnlyForRemainingActiveDevices|TestGenerationRolloverRequiresRevokedTargetAndUniqueDevices",
			},
		},
	}
	started := time.Now().UTC()
	results := make([]result, 0, len(matrix))
	allPassed := true
	for _, current := range matrix {
		results = append(results, execute(*outputDirectory, current))
		if !results[len(results)-1].Passed {
			allPassed = false
		}
	}
	report := evidence{
		SchemaVersion: "1.0.0", Seed: seed,
		StartedAt:  started.Format(time.RFC3339Nano),
		FinishedAt: time.Now().UTC().Format(time.RFC3339Nano),
		Scenarios:  results, Passed: allPassed,
	}
	if err := writeJSON(filepath.Join(*outputDirectory, "fault-injection.json"), report); err != nil {
		fatal(err)
	}
	if !allPassed {
		fatal(errors.New("one or more fault scenarios failed"))
	}
	fmt.Println("g7-fault-injection-ok")
}

func execute(outputDirectory string, current scenario) result {
	started := time.Now()
	command := exec.Command(current.Command[0], current.Command[1:]...)
	command.Env = withoutEnvironment(os.Environ(), "GOPATH")
	output, err := command.CombinedOutput()
	exitCode := 0
	if err != nil {
		exitCode = 1
		var exitError *exec.ExitError
		if errors.As(err, &exitError) {
			exitCode = exitError.ExitCode()
		}
	}
	digest := sha256.Sum256(output)
	outputName := strings.ToLower(strings.ReplaceAll(current.ID, "-", "_")) + ".txt"
	if writeErr := os.WriteFile(
		filepath.Join(outputDirectory, outputName), output, 0o640,
	); writeErr != nil {
		exitCode = 1
	}
	return result{
		scenario: current, ExitCode: exitCode,
		OutputDigest: hex.EncodeToString(digest[:]), OutputPath: outputName,
		DurationNanoseconds: time.Since(started).Nanoseconds(),
		Passed:              exitCode == 0,
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
	fmt.Fprintln(os.Stderr, "g7-fault-runner:", err)
	os.Exit(1)
}
