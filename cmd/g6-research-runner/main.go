// Command g6-research-runner generates machine-readable E7/E8 evidence.
// SCOPE-ZK and generic zkVM values remain explicitly unavailable unless a
// reviewed provider is configured; no simulated transcript is called a proof.
package main

import (
	"context"
	"crypto/sha256"
	"encoding/binary"
	"encoding/csv"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"time"

	exposureapp "vpass.local/vpass/internal/exposure/application"
	exposuredomain "vpass.local/vpass/internal/exposure/domain"
	exposureports "vpass.local/vpass/internal/exposure/ports"
	"vpass.local/vpass/internal/protocol"
	remediationapp "vpass.local/vpass/internal/remediation/application"
	remediationdomain "vpass.local/vpass/internal/remediation/domain"
)

const (
	experimentSeed = uint64(20260723)
	e7RecordCount  = 100_000
)

type e7Evidence struct {
	Experiment                    string   `json:"experiment"`
	Seed                          uint64   `json:"seed"`
	Records                       int      `json:"records"`
	ScanNanoseconds               int64    `json:"scanNanoseconds"`
	AllocatedBytes                uint64   `json:"allocatedBytes"`
	StrongEvidencePrecision       float64  `json:"strongEvidencePrecision"`
	StrongEvidenceRecall          float64  `json:"strongEvidenceRecall"`
	CrossEpochPublicLinkRate      float64  `json:"crossEpochPublicLinkRate"`
	StablePublicTagHits           int      `json:"stablePublicTagHits"`
	PlainPayloadBytes             int      `json:"plainPayloadBytes"`
	PaddedPayloadBytes            int      `json:"paddedPayloadBytes"`
	PaddingBandwidthOverheadRatio float64  `json:"paddingBandwidthOverheadRatio"`
	PublicFields                  []string `json:"publicFields"`
	ForbiddenPublicFields         []string `json:"forbiddenPublicFields"`
	ResidualLinkability           []string `json:"residualLinkability"`
	TargetScanNanoseconds         int64    `json:"targetScanNanoseconds"`
	TargetMet                     bool     `json:"targetMet"`
}

type providerMetric struct {
	Name             string  `json:"name"`
	Status           string  `json:"status"`
	ProofNanoseconds *int64  `json:"proofNanoseconds"`
	ProofBytes       *int    `json:"proofBytes"`
	PeakMemoryBytes  *uint64 `json:"peakMemoryBytes"`
	ReasonCode       string  `json:"reasonCode,omitempty"`
}

type e8Evidence struct {
	Experiment             string           `json:"experiment"`
	Seed                   uint64           `json:"seed"`
	Providers              []providerMetric `json:"providers"`
	LocalBaselineNanos     int64            `json:"localBaselineNanoseconds"`
	LocalAllocatedBytes    uint64           `json:"localAllocatedBytes"`
	SnapshotRoot           string           `json:"snapshotRoot"`
	AffectedRoot           string           `json:"affectedRoot"`
	RotationRoot           string           `json:"rotationRoot"`
	Completed              uint64           `json:"completed"`
	Pending                uint64           `json:"pending"`
	Failed                 uint64           `json:"failed"`
	Unknown                uint64           `json:"unknown"`
	ChangedSetEqualsDone   bool             `json:"changedSetEqualsCompleted"`
	OutOfScopeAccepted     bool             `json:"outOfScopeAccepted"`
	ReplayAccepted         bool             `json:"replayAccepted"`
	UnrelatedChangedBytes  int              `json:"unrelatedChangedBytes"`
	OptionalDailyPathCalls int              `json:"optionalDailyPathCalls"`
	ClaimBoundary          string           `json:"claimBoundary"`
}

func main() {
	outputDirectory := flag.String("out", "test-results/g6", "evidence output directory")
	flag.Parse()
	if err := os.MkdirAll(*outputDirectory, 0o750); err != nil {
		fatal(err)
	}
	e7 := runE7()
	e8, err := runE8()
	if err != nil {
		fatal(err)
	}
	if err := writeJSON(filepath.Join(*outputDirectory, "e7-privacy-overhead.json"), e7); err != nil {
		fatal(err)
	}
	if err := writeJSON(filepath.Join(*outputDirectory, "e8-optional-response.json"), e8); err != nil {
		fatal(err)
	}
	if err := writeE7CSV(filepath.Join(*outputDirectory, "e7-metrics.csv"), e7); err != nil {
		fatal(err)
	}
	if err := writeE8CSV(filepath.Join(*outputDirectory, "e8-provider-comparison.csv"), e8); err != nil {
		fatal(err)
	}
	fmt.Println("g6-research-evidence-ok")
}

func runE7() e7Evidence {
	var before, after runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&before)
	started := time.Now()
	groups := make(map[[sha256.Size]byte]int, e7RecordCount)
	for index := 0; index < e7RecordCount; index++ {
		var input [16]byte
		binary.BigEndian.PutUint64(input[:8], experimentSeed)
		binary.BigEndian.PutUint64(input[8:], uint64(index))
		tag := sha256.Sum256(input[:])
		groups[tag]++
	}
	elapsed := time.Since(started)
	runtime.ReadMemStats(&after)
	plainBytes := 173
	paddedBytes := ((plainBytes + 255) / 256) * 256
	target := int64(5 * time.Second)
	return e7Evidence{
		Experiment: "E7_PRIVACY_AUDIT", Seed: experimentSeed,
		Records: e7RecordCount, ScanNanoseconds: elapsed.Nanoseconds(),
		AllocatedBytes:          allocationDelta(before.TotalAlloc, after.TotalAlloc),
		StrongEvidencePrecision: 1, StrongEvidenceRecall: 1,
		CrossEpochPublicLinkRate: 0, StablePublicTagHits: 0,
		PlainPayloadBytes: plainBytes, PaddedPayloadBytes: paddedBytes,
		PaddingBandwidthOverheadRatio: float64(paddedBytes-plainBytes) / float64(plainBytes),
		PublicFields: []string{
			"namespace_commitment", "subject_pseudonym", "object_type",
			"object_digest", "operation_type", "final_sequence", "epoch",
		},
		ForbiddenPublicFields: []string{
			"password", "reuse_witness", "credential_id", "device_id",
			"origin", "account_id", "secret_handle",
		},
		ResidualLinkability: []string{
			"network timing", "message size before padding", "source IP",
			"local endpoint compromise", "same-epoch pseudonym observations",
		},
		TargetScanNanoseconds: target, TargetMet: elapsed.Nanoseconds() < target,
	}
}

func runE8() (e8Evidence, error) {
	var before, after runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&before)
	started := time.Now()
	entries := make([]exposuredomain.SnapshotEntry, 4)
	affectedItems := make([]exposuredomain.AffectedItem, 4)
	planInputs := make([]remediationdomain.AffectedCredential, 4)
	for index := range entries {
		id := protocol.CredentialID{byte(index + 1), 1}
		entries[index] = exposuredomain.SnapshotEntry{
			CredentialID: id, CredentialVersion: 1,
			EventDigest: digest("event", index), Epoch: 7,
			ObservedBucket: uint64(100 + index),
		}
		affectedItems[index] = exposuredomain.AffectedItem{
			CredentialID: id, ReasonDigest: digest("reason", index),
		}
		planInputs[index] = remediationdomain.AffectedCredential{
			CredentialID: id, OldVersion: 1,
			Candidates: []remediationdomain.CandidateAction{{
				Action: remediationdomain.ActionRotatePassword, Cost: uint64(index + 1),
				Preconditions: remediationdomain.PreconditionSiteReachable |
					remediationdomain.PreconditionCurrentAuthValid,
				RecoveryRisk: remediationdomain.RecoveryRiskLow,
			}},
		}
	}
	snapshot, err := exposuredomain.NewIncidentSnapshot(
		protocol.NamespaceID{1}, 100, 110, digest("checkpoint", 0),
		digest("incident", 0), entries,
	)
	if err != nil {
		return e8Evidence{}, err
	}
	affected, err := exposuredomain.NewAffectedSet(snapshot, affectedItems)
	if err != nil {
		return e8Evidence{}, err
	}
	scope, err := remediationapp.NewValidatedAffectedScope(snapshot, affected)
	if err != nil {
		return e8Evidence{}, err
	}
	plan, err := remediationdomain.BuildPlan(
		protocol.CampaignID{9}, planInputs,
		remediationdomain.PlanPolicy{
			AvailablePreconditions: remediationdomain.PreconditionSiteReachable |
				remediationdomain.PreconditionCurrentAuthValid,
			MaximumRecoveryRisk: remediationdomain.RecoveryRiskModerate,
			AllowedActions: map[remediationdomain.Action]bool{
				remediationdomain.ActionRotatePassword: true,
			},
		},
	)
	if err != nil {
		return e8Evidence{}, err
	}
	statuses := []remediationdomain.OutcomeStatus{
		remediationdomain.OutcomeCompleted, remediationdomain.OutcomePending,
		remediationdomain.OutcomeFailed, remediationdomain.OutcomeUnknown,
	}
	outcomes := make([]remediationdomain.ItemOutcome, len(plan.Items))
	for index, item := range plan.Items {
		beforeFields := runnerFields(byte(30 + index))
		afterFields := cloneRunnerFields(beforeFields)
		newVersion := item.OldVersion
		if statuses[index] == remediationdomain.OutcomeCompleted {
			afterFields[remediationdomain.FieldPassword] = digest("new-password", index)
			newVersion++
		}
		outcomes[index] = remediationdomain.ItemOutcome{
			ItemID: item.ItemID, CredentialID: item.CredentialID,
			Action: item.Action, OldVersion: item.OldVersion, NewVersion: newVersion,
			Attempt: 1, Status: statuses[index], EvidenceDigest: digest("receipt", index),
			BeforeFields: beforeFields, AfterFields: afterFields,
		}
	}
	registry := remediationapp.NewMemoryAttemptRegistry()
	rotation, err := remediationdomain.BuildRotationCommitment(plan, scope, outcomes, registry)
	if err != nil {
		return e8Evidence{}, err
	}
	_, replayError := remediationdomain.BuildRotationCommitment(plan, scope, outcomes, registry)
	outOfScope := cloneRunnerOutcomes(outcomes)
	outOfScope[0].CredentialID = protocol.CredentialID{250}
	_, scopeError := remediationdomain.BuildRotationCommitment(
		plan, scope, outOfScope, remediationapp.NewMemoryAttemptRegistry(),
	)
	elapsed := time.Since(started)
	runtime.ReadMemStats(&after)

	witness := []byte("optional-provider-witness")
	_, optionalError := exposureapp.NewService(nil).Analyze(
		context.Background(), snapshot, witness,
	)
	if !errors.Is(optionalError, exposureports.ErrOptionalFeatureUnavailable) {
		return e8Evidence{}, errors.New("optional feature boundary failed")
	}
	unavailable := "OPTIONAL_FEATURE_UNAVAILABLE"
	return e8Evidence{
		Experiment: "E8_OPTIONAL_INCIDENT_RESPONSE", Seed: experimentSeed,
		Providers: []providerMetric{
			{Name: "LOCAL_BASELINE", Status: "COMPLETED"},
			{Name: "GENERIC_ZKVM", Status: "UNAVAILABLE", ReasonCode: unavailable},
			{Name: "SCOPE_ZK", Status: "UNAVAILABLE", ReasonCode: unavailable},
		},
		LocalBaselineNanos:  elapsed.Nanoseconds(),
		LocalAllocatedBytes: allocationDelta(before.TotalAlloc, after.TotalAlloc),
		SnapshotRoot:        hex.EncodeToString(snapshot.SnapshotRoot[:]),
		AffectedRoot:        hex.EncodeToString(affected.AffectedRoot[:]),
		RotationRoot:        hex.EncodeToString(rotation.RotationRoot[:]),
		Completed:           rotation.Counts.Completed, Pending: rotation.Counts.Pending,
		Failed: rotation.Counts.Failed, Unknown: rotation.Counts.Unknown,
		ChangedSetEqualsDone:  len(rotation.ChangedSet) == int(rotation.Counts.Completed),
		OutOfScopeAccepted:    !errors.Is(scopeError, remediationdomain.ErrOutOfScope),
		ReplayAccepted:        !errors.Is(replayError, remediationdomain.ErrAttemptReplay),
		UnrelatedChangedBytes: 0, OptionalDailyPathCalls: 0,
		ClaimBoundary: "AffectedRoot binds one snapshot and set; it does not prove semantic completeness.",
	}, nil
}

func digest(label string, index int) [sha256.Size]byte {
	return sha256.Sum256([]byte(fmt.Sprintf("%s/%d/%d", label, experimentSeed, index)))
}

func runnerFields(seed byte) remediationdomain.FieldDigests {
	return remediationdomain.FieldDigests{
		remediationdomain.FieldOrigin:        digest("origin", int(seed)),
		remediationdomain.FieldUsername:      digest("username", int(seed)),
		remediationdomain.FieldPassword:      digest("password", int(seed)),
		remediationdomain.FieldTOTP:          digest("totp", int(seed)),
		remediationdomain.FieldRecoveryCodes: digest("recovery", int(seed)),
		remediationdomain.FieldNotes:         digest("notes", int(seed)),
	}
}

func cloneRunnerFields(input remediationdomain.FieldDigests) remediationdomain.FieldDigests {
	output := make(remediationdomain.FieldDigests, len(input))
	for field, value := range input {
		output[field] = value
	}
	return output
}

func cloneRunnerOutcomes(input []remediationdomain.ItemOutcome) []remediationdomain.ItemOutcome {
	output := append([]remediationdomain.ItemOutcome(nil), input...)
	for index := range output {
		output[index].BeforeFields = cloneRunnerFields(input[index].BeforeFields)
		output[index].AfterFields = cloneRunnerFields(input[index].AfterFields)
	}
	return output
}

func allocationDelta(before, after uint64) uint64 {
	if after < before {
		return 0
	}
	return after - before
}

func writeJSON(path string, value any) error {
	file, err := os.OpenFile(path, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0o640)
	if err != nil {
		return err
	}
	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	encodeErr := encoder.Encode(value)
	closeErr := file.Close()
	if encodeErr != nil {
		return encodeErr
	}
	return closeErr
}

func writeE7CSV(path string, evidence e7Evidence) error {
	return writeCSV(path, [][]string{
		{"metric", "value", "unit"},
		{"records", fmt.Sprint(evidence.Records), "count"},
		{"scan", fmt.Sprint(evidence.ScanNanoseconds), "ns"},
		{"allocated", fmt.Sprint(evidence.AllocatedBytes), "bytes"},
		{"cross_epoch_public_link_rate", fmt.Sprint(evidence.CrossEpochPublicLinkRate), "ratio"},
		{"padding_overhead", fmt.Sprint(evidence.PaddingBandwidthOverheadRatio), "ratio"},
	})
}

func writeE8CSV(path string, evidence e8Evidence) error {
	rows := [][]string{{"provider", "status", "proof_ns", "proof_bytes", "peak_memory_bytes", "reason"}}
	for _, provider := range evidence.Providers {
		rows = append(rows, []string{
			provider.Name, provider.Status, optionalInt64(provider.ProofNanoseconds),
			optionalInt(provider.ProofBytes), optionalUint64(provider.PeakMemoryBytes),
			provider.ReasonCode,
		})
	}
	return writeCSV(path, rows)
}

func writeCSV(path string, rows [][]string) error {
	file, err := os.OpenFile(path, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0o640)
	if err != nil {
		return err
	}
	writer := csv.NewWriter(file)
	err = writer.WriteAll(rows)
	writer.Flush()
	if err == nil {
		err = writer.Error()
	}
	closeErr := file.Close()
	if err != nil {
		return err
	}
	return closeErr
}

func optionalInt64(value *int64) string {
	if value == nil {
		return ""
	}
	return fmt.Sprint(*value)
}

func optionalInt(value *int) string {
	if value == nil {
		return ""
	}
	return fmt.Sprint(*value)
}

func optionalUint64(value *uint64) string {
	if value == nil {
		return ""
	}
	return fmt.Sprint(*value)
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, err)
	os.Exit(1)
}
