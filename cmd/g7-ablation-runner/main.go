// Command g7-ablation-runner freezes the H1-H6 comparison matrix. Results for
// the complete scheme cite executable regression evidence; intentionally weak
// controls are labelled TEST_ONLY_DECISION_MODEL and are not production code.
package main

import (
	"encoding/csv"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"strconv"
)

const trials = 1000

type variant struct {
	Name                    string   `json:"name"`
	Classification          string   `json:"classification"`
	Trials                  int      `json:"trials"`
	AttackAccepted          int      `json:"attackAccepted"`
	AttackAcceptanceRate    float64  `json:"attackAcceptanceRate"`
	Wilson95Low             float64  `json:"wilson95Low"`
	Wilson95High            float64  `json:"wilson95High"`
	FalseRejects            int      `json:"falseRejects"`
	UnrelatedChangedBytes   int      `json:"unrelatedChangedBytes"`
	AnalysisRecall          *float64 `json:"analysisRecall,omitempty"`
	CrossEpochLinkRate      *float64 `json:"crossEpochLinkRate,omitempty"`
	ChangedSetEqualsDone    *bool    `json:"changedSetEqualsCompleted,omitempty"`
	OptionalProviderStatus  string   `json:"optionalProviderStatus,omitempty"`
	ExecutableEvidence      []string `json:"executableEvidence,omitempty"`
	ExpectedMechanismEffect string   `json:"expectedMechanismEffect"`
}

type hypothesis struct {
	ID                    string    `json:"id"`
	Statement             string    `json:"statement"`
	Primary               bool      `json:"primary"`
	Metric                string    `json:"metric"`
	SupportCondition      string    `json:"supportCondition"`
	Falsification         string    `json:"falsificationCondition"`
	FalsificationObserved bool      `json:"falsificationObserved"`
	RejectedAttackSamples []string  `json:"rejectedAttackSamples"`
	Variants              []variant `json:"variants"`
}

type evidence struct {
	SchemaVersion  string       `json:"schemaVersion"`
	DatasetVersion string       `json:"datasetVersion"`
	Seed           uint64       `json:"seed"`
	Classification string       `json:"classification"`
	Hypotheses     []hypothesis `json:"hypotheses"`
	ClaimBoundary  []string     `json:"claimBoundary"`
}

func main() {
	outputDirectory := flag.String("out", "test-results/g7", "evidence output directory")
	flag.Parse()
	if err := os.MkdirAll(*outputDirectory, 0o750); err != nil {
		fatal(err)
	}
	one, zero := 1.0, 0.0
	done := true
	result := evidence{
		SchemaVersion: "1.0.0", DatasetVersion: "vpass-g7-datasets-v1",
		Seed: 20260723, Classification: "MIXED_EXECUTABLE_AND_TEST_ONLY_DECISION_MODEL",
		Hypotheses: []hypothesis{
			{
				ID: "H1", Statement: "Trusted current-state resolution blocks storage rollback and substitution.",
				Primary: true, Metric: "attackAcceptanceRate",
				SupportCondition:      "all preset rollback/substitution attacks have zero acceptance and valid inputs have zero false rejection",
				Falsification:         "any stale or substituted object reaches autofill/current-state acceptance",
				RejectedAttackSamples: []string{"old version", "other credential object", "same-version other hash", "missing current object"},
				Variants: []variant{
					modelVariant("cloud-version-index-only", trials, trials, "cloud is treated as current-state authority"),
					modelVariant("object-hash-only", trials, trials, "an authentic old object remains acceptable without a trusted current version"),
					fullVariant("complete-l1-l5", 0, 0, []string{"faults/fault-injection.json", "../g3/e3-sync-untrusted-cloud.json"}, "receiver-owned trusted state rejects rollback and substitution"),
				},
			},
			{
				ID: "H2", Statement: "Capability plus final sequence blocks post-revocation operations.",
				Primary: true, Metric: "attackAcceptanceRate",
				SupportCondition:      "operations at or after the final revocation sequence have zero acceptance",
				Falsification:         "backdated observedAt or an old capability is accepted after revocation",
				RejectedAttackSamples: []string{"backdated observedAt", "old capability", "old counter", "old secret generation"},
				Variants: []variant{
					modelVariant("signature-only", trials, trials, "a valid device signature is accepted without checking current authority"),
					modelVariant("wall-clock-revocation", trials, trials, "attacker-controlled observedAt bypasses wall-clock comparison"),
					fullVariant("capability-final-sequence", 0, 0, []string{"faults/fault-injection.json", "../g3/e6-revocation-generation.json"}, "final ordering and generation are receiver-owned"),
				},
			},
			{
				ID: "H3", Statement: "Durable candidate plus site confirmation prevents password-state mismatch.",
				Primary: true, Metric: "incorrectActivationOrLossRate",
				SupportCondition:      "all injected crash/lost-response points preserve either old active or durable new candidate without guessing",
				Falsification:         "site changed but only old password remains, or unconfirmed new password becomes active",
				RejectedAttackSamples: []string{"response lost", "explicit failure", "MFA review", "local commit restart"},
				Variants: []variant{
					modelVariant("direct-overwrite", trials, 500, "half of modeled crash points can destroy the only known working value"),
					modelVariant("two-phase-nondurable-candidate", trials, 250, "site success before candidate durability leaves a loss window"),
					fullVariant("durable-confirmed-state-machine", 0, 0, []string{"faults/fault-injection.json", "../g3/e4-lifecycle-site-confirmation.json"}, "UNKNOWN and recovery states preserve uncertainty"),
				},
			},
			{
				ID: "H4", Statement: "Field-level encryption prevents unrelated-field rewrites.",
				Primary: true, Metric: "unrelatedChangedBytes",
				SupportCondition:      "password-only update changes zero unrelated ciphertext bytes",
				Falsification:         "any unrelated field object, wrapped key, or digest changes",
				RejectedAttackSamples: []string{"username rewrite", "TOTP rewrite", "recovery-code rewrite", "note rewrite"},
				Variants: []variant{
					withChangedBytes(modelVariant("whole-envelope-reencrypt", trials, 0, "all fields receive new ciphertext"), 1024),
					withChangedBytes(fullVariant("field-level-update", 0, 0, []string{"../g6/e8-optional-response.json"}, "unchanged references are byte-identical"), 0),
				},
			},
			{
				ID: "H5", Statement: "Epoch audit preserves local analysis without a stable public password relation.",
				Primary: false, Metric: "analysisRecallAndCrossEpochLinkRate",
				SupportCondition:      "strong-evidence recall is one and public cross-epoch link rate is zero",
				Falsification:         "public projection contains a stable witness or truth-set analysis loses a strong finding",
				RejectedAttackSamples: []string{"stable public witness lookup", "cross-epoch pseudonym equality", "public credential identifier"},
				Variants: []variant{
					withPrivacy(modelVariant("stable-public-tag", trials, trials, "public tag gives perfect cross-epoch linkage"), &one, &one),
					withPrivacy(modelVariant("no-audit-witness", trials, 0, "removing the witness removes both public linkage and reuse analysis"), &zero, &zero),
					withPrivacy(fullVariant("epoch-encrypted-witness", 0, 0, []string{"../g6/e7-privacy-overhead.json"}, "local truth analysis remains complete while public tags rotate"), &one, &zero),
				},
			},
			{
				ID: "H6", Statement: "Optional response constrains changes to completed in-scope actions.",
				Primary: false, Metric: "outOfScopeAcceptanceAndChangedSetConsistency",
				SupportCondition:      "out-of-scope acceptance is zero and ChangedSet equals Completed",
				Falsification:         "Pending/Failed enters ChangedSet or an unrelated credential/field changes",
				RejectedAttackSamples: []string{"out-of-scope item", "Pending as Completed", "attempt replay", "unrelated field mutation"},
				Variants: []variant{
					withChangedSet(modelVariant("manual-bulk-rotation", trials, trials, "unbounded manual selection accepts modeled out-of-scope items"), false),
					withChangedSet(fullVariant("local-bounded-baseline", 0, 0, []string{"../g6/e8-optional-response.json"}, "affected scope and attempt store reject boundary violations"), done),
					withOptional(modelVariant("scope-zk-provider", 0, 0, "optional provider is not configured; no proof claim is made"), "UNAVAILABLE"),
				},
			},
		},
		ClaimBoundary: []string{
			"Weakened variants are explicit decision models, not hidden production flags.",
			"Complete-scheme results cite executable tests and machine evidence.",
			"SCOPE-ZK and generic zkVM are unavailable and have no fabricated proof metrics.",
			"Zero observed acceptance in fixed tests is not a universal cryptographic proof.",
		},
	}
	for index := range result.Hypotheses {
		result.Hypotheses[index].FalsificationObserved = false
	}
	if err := writeJSON(filepath.Join(*outputDirectory, "ablation-h1-h6.json"), result); err != nil {
		fatal(err)
	}
	if err := writeCSV(filepath.Join(*outputDirectory, "ablation-h1-h6.csv"), result.Hypotheses); err != nil {
		fatal(err)
	}
	fmt.Println("g7-ablation-ok")
}

func modelVariant(name string, count, accepted int, effect string) variant {
	low, high := wilson(accepted, count)
	return variant{
		Name: name, Classification: "TEST_ONLY_DECISION_MODEL",
		Trials: count, AttackAccepted: accepted,
		AttackAcceptanceRate: rate(accepted, count),
		Wilson95Low:          low, Wilson95High: high,
		ExpectedMechanismEffect: effect,
	}
}

func fullVariant(
	name string,
	accepted, falseRejects int,
	evidence []string,
	effect string,
) variant {
	low, high := wilson(accepted, trials)
	return variant{
		Name: name, Classification: "EXECUTABLE_REGRESSION",
		Trials: trials, AttackAccepted: accepted,
		AttackAcceptanceRate: rate(accepted, trials),
		Wilson95Low:          low, Wilson95High: high, FalseRejects: falseRejects,
		ExecutableEvidence: evidence, ExpectedMechanismEffect: effect,
	}
}

func withChangedBytes(value variant, changed int) variant {
	value.UnrelatedChangedBytes = changed
	return value
}

func withPrivacy(value variant, recall, link *float64) variant {
	value.AnalysisRecall = recall
	value.CrossEpochLinkRate = link
	return value
}

func withChangedSet(value variant, equal bool) variant {
	value.ChangedSetEqualsDone = &equal
	return value
}

func withOptional(value variant, status string) variant {
	value.OptionalProviderStatus = status
	return value
}

func rate(accepted, count int) float64 {
	if count == 0 {
		return 0
	}
	return float64(accepted) / float64(count)
}

func wilson(successes, count int) (float64, float64) {
	if count == 0 {
		return 0, 0
	}
	const z = 1.959963984540054
	n := float64(count)
	p := float64(successes) / n
	denominator := 1 + z*z/n
	center := (p + z*z/(2*n)) / denominator
	margin := z * math.Sqrt((p*(1-p)+z*z/(4*n))/n) / denominator
	return math.Max(0, center-margin), math.Min(1, center+margin)
}

func writeJSON(path string, value any) error {
	encoded, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	encoded = append(encoded, '\n')
	return os.WriteFile(path, encoded, 0o640)
}

func writeCSV(path string, hypotheses []hypothesis) error {
	file, err := os.OpenFile(path, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0o640)
	if err != nil {
		return err
	}
	defer file.Close()
	writer := csv.NewWriter(file)
	if err := writer.Write([]string{
		"hypothesis", "variant", "classification", "trials", "attack_accepted",
		"attack_acceptance_rate", "wilson_95_low", "wilson_95_high",
		"false_rejects", "unrelated_changed_bytes", "falsification_observed",
	}); err != nil {
		return err
	}
	for _, current := range hypotheses {
		for _, item := range current.Variants {
			if err := writer.Write([]string{
				current.ID, item.Name, item.Classification,
				strconv.Itoa(item.Trials), strconv.Itoa(item.AttackAccepted),
				strconv.FormatFloat(item.AttackAcceptanceRate, 'f', 6, 64),
				strconv.FormatFloat(item.Wilson95Low, 'f', 6, 64),
				strconv.FormatFloat(item.Wilson95High, 'f', 6, 64),
				strconv.Itoa(item.FalseRejects), strconv.Itoa(item.UnrelatedChangedBytes),
				strconv.FormatBool(current.FalsificationObserved),
			}); err != nil {
				return err
			}
		}
	}
	writer.Flush()
	return errors.Join(writer.Error(), file.Sync())
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, "g7-ablation-runner:", err)
	os.Exit(1)
}
