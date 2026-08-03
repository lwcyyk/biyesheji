// Command g7-research-runner produces reproducible performance and scale
// evidence for E1-E8. Fixed seeds control only synthetic public fixtures;
// production cryptographic operations continue to use the OS CSPRNG.
package main

import (
	"bytes"
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/binary"
	"encoding/csv"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"math"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"syscall"
	"time"

	sqliteadapter "vpass.local/vpass/internal/adapters/outbound/sqlite"
	credentialdomain "vpass.local/vpass/internal/credential/domain"
	"vpass.local/vpass/internal/cryptokit"
	"vpass.local/vpass/internal/protocol"
	syncdomain "vpass.local/vpass/internal/sync/domain"
	transparencydomain "vpass.local/vpass/internal/transparency/domain"
)

const (
	schemaVersion   = "1.0.0"
	datasetVersion  = "vpass-g7-datasets-v1"
	experimentSeed  = uint64(20260723)
	warmupCount     = 10
	repetitionCount = 30
)

type metric struct {
	Experiment        string  `json:"experiment"`
	Name              string  `json:"name"`
	Unit              string  `json:"unit"`
	Samples           int     `json:"samples"`
	P50               int64   `json:"p50"`
	P95               int64   `json:"p95"`
	P99               int64   `json:"p99"`
	Mean              float64 `json:"mean"`
	StandardDeviation float64 `json:"standardDeviation"`
	Bootstrap95Low    float64 `json:"bootstrap95Low"`
	Bootstrap95High   float64 `json:"bootstrap95High"`
	AllocatedBytes    uint64  `json:"allocatedBytes"`
	CPUUserNanos      int64   `json:"cpuUserNanoseconds"`
	CPUSystemNanos    int64   `json:"cpuSystemNanoseconds"`
	MaxRSSBytes       uint64  `json:"maxRssBytes"`
	Target            int64   `json:"target"`
	Passed            bool    `json:"passed"`
	Notes             string  `json:"notes,omitempty"`
}

type environment struct {
	Commit              string   `json:"commit"`
	ProtocolID          string   `json:"protocolId"`
	ProtocolVersion     uint64   `json:"protocolVersion"`
	SuiteID             string   `json:"suiteId"`
	GoVersion           string   `json:"goVersion"`
	NodeVersion         string   `json:"nodeVersion"`
	BrowserVersion      string   `json:"browserVersion"`
	OS                  string   `json:"os"`
	Architecture        string   `json:"architecture"`
	CPU                 string   `json:"cpu"`
	LogicalCores        int      `json:"logicalCores"`
	MemoryBytes         uint64   `json:"memoryBytes"`
	Storage             string   `json:"storage"`
	BuildFlags          []string `json:"buildFlags"`
	DatasetVersion      string   `json:"datasetVersion"`
	Seed                uint64   `json:"seed"`
	WarmupRepetitions   int      `json:"warmupRepetitions"`
	MeasuredRepetitions int      `json:"measuredRepetitions"`
	ProviderKinds       []string `json:"providerKinds"`
	StartedAt           string   `json:"startedAt"`
	FinishedAt          string   `json:"finishedAt"`
}

type experiment struct {
	ID             string   `json:"id"`
	Status         string   `json:"status"`
	Provider       string   `json:"provider"`
	Evidence       []string `json:"evidence"`
	FailureSamples []string `json:"failureSamples,omitempty"`
	Notes          string   `json:"notes"`
}

type evidence struct {
	SchemaVersion  string       `json:"schemaVersion"`
	DatasetVersion string       `json:"datasetVersion"`
	DatasetDigest  string       `json:"datasetDigest"`
	Seed           uint64       `json:"seed"`
	Environment    environment  `json:"environment"`
	Metrics        []metric     `json:"metrics"`
	Experiments    []experiment `json:"experiments"`
	ClaimBoundary  []string     `json:"claimBoundary"`
}

func main() {
	outputDirectory := flag.String("out", "test-results/g7", "evidence output directory")
	datasetPath := flag.String("dataset", "experiments/g7/datasets.json", "fixed dataset manifest")
	flag.Parse()
	if err := os.MkdirAll(*outputDirectory, 0o750); err != nil {
		fatal(err)
	}
	datasetBytes, err := os.ReadFile(*datasetPath)
	if err != nil {
		fatal(err)
	}
	datasetDigest := sha256.Sum256(datasetBytes)
	started := time.Now().UTC()
	metrics, experimentResults, err := runExperiments(*outputDirectory)
	if err != nil {
		fatal(err)
	}
	result := evidence{
		SchemaVersion: schemaVersion, DatasetVersion: datasetVersion,
		DatasetDigest: hex.EncodeToString(datasetDigest[:]), Seed: experimentSeed,
		Environment: collectEnvironment(started, time.Now().UTC()),
		Metrics:     metrics, Experiments: experimentResults,
		ClaimBoundary: []string{
			"结果证明研究原型在固定合成数据与本机环境中的机制性质，不代表生产拜占庭网络。",
			"Mock Site 不代表全部真实网站；SIMULATED/LOCAL 不等于生产链或生产透明日志。",
			"撤销不能回收已被撤销设备复制的历史明文。",
			"SCOPE-ZK 与通用 zkVM 未配置时保持 UNAVAILABLE，不伪造证明时间或大小。",
			"Epoch 隔离不隐藏网络时序、IP、未填充前的长度模式或已受控本地端点。",
		},
	}
	if err := writeJSON(filepath.Join(*outputDirectory, "e1-e8-summary.json"), result); err != nil {
		fatal(err)
	}
	if err := writeMetricsCSV(filepath.Join(*outputDirectory, "performance.csv"), metrics); err != nil {
		fatal(err)
	}
	fmt.Println("g7-research-evidence-ok")
}

func runExperiments(outputDirectory string) ([]metric, []experiment, error) {
	e1, err := runE1()
	if err != nil {
		return nil, nil, fmt.Errorf("E1: %w", err)
	}
	e2, err := runE2(outputDirectory)
	if err != nil {
		return nil, nil, fmt.Errorf("E2: %w", err)
	}
	e3, err := runE3()
	if err != nil {
		return nil, nil, fmt.Errorf("E3: %w", err)
	}
	e5, proof100K, proof1M, err := runE5()
	if err != nil {
		return nil, nil, fmt.Errorf("E5: %w", err)
	}
	metrics := append(append(append(e1, e2...), e3...), e5...)
	experiments := []experiment{
		{
			ID: "E1", Status: statusForMetrics(e1), Provider: "REAL_LOCAL_CRYPTO",
			Evidence:       []string{"e1-e8-summary.json", "../g1 cryptographic KAT tests"},
			FailureSamples: []string{"wrong master password", "wrong device secret", "copied device capsule"},
			Notes:          "实际 Argon2id RootCapsule 解锁；错误设备绑定必须拒绝。",
		},
		{
			ID: "E2", Status: statusForMetrics(e2), Provider: "REAL_LOCAL_SQLITE_AND_CRYPTO",
			Evidence:       []string{"e1-e8-summary.json", "../g5/autofill-p95.json", "../g5/daily-mocksite-e2e.json"},
			FailureSamples: []string{"cross-Origin", "opaque Origin", "iframe", "handle replay"},
			Notes:          "SQLite RouteMap、字段解密与 HTTP/Native 自动填充证据分开记录。",
		},
		{
			ID: "E3", Status: statusForMetrics(e3), Provider: "REAL_LOCAL_SYNC_PROTOCOL",
			Evidence:       []string{"e1-e8-summary.json", "../g3/e3-sync-untrusted-cloud.json"},
			FailureSamples: []string{"rollback", "replacement", "missing object", "same-version conflict"},
			Notes:          "10k 对象按 100×100 分批，使用真实确定性编码、Merkle 集合根与 Ed25519。",
		},
		{
			ID: "E4", Status: "COMPLETED", Provider: "MOCK_SITE",
			Evidence:       []string{"../g3/e4-lifecycle-site-confirmation.json", "../g5/daily-mocksite-e2e.json"},
			FailureSamples: []string{"explicit failure", "lost response", "UNKNOWN", "crash recovery"},
			Notes:          "Mock Site 只证明连接器和生命周期状态机，不外推到所有网站。",
		},
		{
			ID: "E5", Status: statusForMetrics(e5), Provider: "SIMULATED_LOG_AND_ANVIL_BOUNDARY",
			Evidence:       []string{"e1-e8-summary.json", "../g4/e5-l1-l5-mutation-matrix.json", "../g4/e5-transparency-proofs.json"},
			FailureSamples: []string{"bad signature", "bad capability", "bad state", "bad inclusion", "fork"},
			Notes: fmt.Sprintf(
				"真实构造 1m 叶内存树；100k/1m inclusion proof 分别为 %d/%d 个 hash。",
				proof100K, proof1M,
			),
		},
		{
			ID: "E6", Status: "COMPLETED", Provider: "REAL_LOCAL_PROTOCOL",
			Evidence:       []string{"../g3/e6-revocation-generation.json", "../g4/e5-l1-l5-mutation-matrix.json"},
			FailureSamples: []string{"backdated observedAt", "old capability", "old counter", "old generation"},
			Notes:          "最终序与新秘密代际由负向矩阵验证。",
		},
		{
			ID: "E7", Status: "COMPLETED", Provider: "REAL_LOCAL_AUDIT",
			Evidence:       []string{"../g6/e7-privacy-overhead.json", "../g6/e7-100k-scan.json"},
			FailureSamples: []string{"stable public witness", "cross-epoch link", "out-of-scope analysis"},
			Notes:          "完整扫描与公开面证据来自 G6 固定 100k 数据集。",
		},
		{
			ID: "E8", Status: "COMPLETED_WITH_OPTIONAL_PROVIDERS_UNAVAILABLE", Provider: "LOCAL_BASELINE",
			Evidence:       []string{"../g6/e8-optional-response.json", "../g6/e8-provider-comparison.csv"},
			FailureSamples: []string{"out-of-scope mutation", "attempt replay", "unrelated field mutation"},
			Notes:          "本地基线完成；SCOPE-ZK/通用 zkVM 未配置并明确标记 UNAVAILABLE。",
		},
	}
	return metrics, experiments, nil
}

func runE1() ([]metric, error) {
	namespace := filledNamespace(0x11)
	device := filledDevice(0x21)
	wrongDevice := filledDevice(0x22)
	master, _ := cryptokit.NewSecret([]byte("TEST_ONLY-g7-master-password-input"))
	deviceSecret, _ := cryptokit.NewSecret(bytes.Repeat([]byte{0x31}, cryptokit.KeySize))
	defer master.Destroy()
	defer deviceSecret.Destroy()
	bundle, _, err := cryptokit.GenerateRootSecretBundle(1, 1)
	if err != nil {
		return nil, err
	}
	defer bundle.Destroy()
	capsule, err := cryptokit.SealRootCapsule(
		master, deviceSecret, namespace, device, cryptokit.DefaultArgon2Params, bundle,
	)
	if err != nil {
		return nil, err
	}
	if opened, err := cryptokit.OpenRootCapsule(
		master, deviceSecret, namespace, wrongDevice, capsule,
	); err == nil {
		opened.Destroy()
		return nil, errors.New("copied capsule was accepted by another device")
	}
	unlock := measure("E1", "root_capsule_unlock", 1500*time.Millisecond, func() error {
		opened, openErr := cryptokit.OpenRootCapsule(
			master, deviceSecret, namespace, device, capsule,
		)
		if opened != nil {
			opened.Destroy()
		}
		return openErr
	})
	unlock.Notes = fmt.Sprintf(
		"Argon2id memory=%dKiB iterations=%d lanes=%d; copied-device rejection=100%%",
		cryptokit.DefaultArgon2Params.MemoryKiB,
		cryptokit.DefaultArgon2Params.Iterations,
		cryptokit.DefaultArgon2Params.Lanes,
	)
	return []metric{unlock}, nil
}

func runE2(outputDirectory string) ([]metric, error) {
	namespace := filledNamespace(0x41)
	credentialID := filledCredential(0x51)
	root, _ := cryptokit.NewSecret(bytes.Repeat([]byte{0x61}, cryptokit.KeySize))
	prk, err := cryptokit.ExtractNamespacePRK(root, namespace, 1)
	root.Destroy()
	if err != nil {
		return nil, err
	}
	keys, err := cryptokit.DeriveNamespaceKeys(prk)
	prk.Destroy()
	if err != nil {
		return nil, err
	}
	defer keys.Destroy()
	origin, err := credentialdomain.NormalizeOrigin("https://route.synthetic.invalid")
	if err != nil {
		return nil, err
	}
	defer origin.Destroy()
	entry, err := credentialdomain.BuildEncryptedRouteEntry(
		keys.Name, namespace, origin, []byte("account-target"), credentialID, 1,
	)
	if err != nil {
		return nil, err
	}
	lookup := entry.Lookup()
	policyHash := sha256.Sum256([]byte("TEST_ONLY-g7-crypto-policy"))
	plaintext, _ := cryptokit.NewSecret([]byte("TEST_ONLY-generated-password-value"))
	defer plaintext.Destroy()
	encrypted, err := cryptokit.EncryptField(keys.Wrap, cryptokit.FieldContext{
		NamespaceID: namespace, CredentialID: credentialID, CredentialVersion: 1,
		FieldType: cryptokit.FieldPassword, KeyGeneration: 1,
		CryptoPolicyHash: policyHash, OriginBinding: lookup.OriginBinding,
	}, plaintext)
	if err != nil {
		return nil, err
	}
	fieldMetric := measure("E2", "single_password_field_decrypt", 10*time.Millisecond, func() error {
		opened, openErr := cryptokit.DecryptField(keys.Wrap, cryptokit.FieldContext{
			NamespaceID: namespace, CredentialID: credentialID, CredentialVersion: 1,
			FieldType: cryptokit.FieldPassword, KeyGeneration: 1,
			CryptoPolicyHash: policyHash, OriginBinding: lookup.OriginBinding,
		}, encrypted)
		if opened != nil {
			opened.Destroy()
		}
		return openErr
	})
	temporary, err := os.MkdirTemp(outputDirectory, ".route-scale-")
	if err != nil {
		return nil, err
	}
	defer os.RemoveAll(temporary)
	database, err := sqliteadapter.Open(context.Background(), filepath.Join(temporary, "routes.db"))
	if err != nil {
		return nil, err
	}
	defer database.Close()
	rootPublicKey := bytes.Repeat([]byte{0xa1}, ed25519.PublicKeySize)
	rootKeyID := sha256.Sum256(rootPublicKey)
	if _, err := database.ExecContext(
		context.Background(),
		`INSERT INTO namespaces (
  namespace_id, protocol_version, suite_id, chain_id,
  root_signing_public_key, root_key_id, current_secret_generation,
  status, created_at_ms, updated_at_ms
) VALUES (?, 2, ?, 'g7-research-chain', ?, ?, 1, 'ACTIVE', 1, 1)`,
		namespace[:], protocol.SuiteID, rootPublicKey, rootKeyID[:],
	); err != nil {
		return nil, err
	}
	originCommitment := sha256.Sum256([]byte("TEST_ONLY-origin-commitment"))
	if _, err := database.ExecContext(
		context.Background(),
		`INSERT INTO vault_profiles (
  namespace_id, protocol_version, suite_id, active_secret_generation,
  root_public_key, crypto_policy_hash, created_at_ms
) VALUES (?, 2, ?, 1, ?, ?, 1)`,
		namespace[:], protocol.SuiteID, rootPublicKey, policyHash[:],
	); err != nil {
		return nil, err
	}
	if _, err := database.ExecContext(
		context.Background(),
		`INSERT INTO credentials (
  credential_id, namespace_id, aggregate_status, origin_commitment,
  created_at_ms, updated_at_ms
) VALUES (?, ?, 'ACTIVE', ?, 1, 1)`,
		credentialID[:], namespace[:], originCommitment[:],
	); err != nil {
		return nil, err
	}
	repository, err := sqliteadapter.NewRouteRepository(database)
	if err != nil {
		return nil, err
	}
	if err := repository.Create(context.Background(), keys.Name, entry, 1); err != nil {
		return nil, err
	}
	if err := insertSyntheticRoutes(database, namespace, credentialID, entry, 1, 9_999); err != nil {
		return nil, err
	}
	route10K := measure("E2", "sqlite_route_lookup_10k", 5*time.Millisecond, func() error {
		resolved, resolveErr := repository.ResolveLookup(context.Background(), namespace, lookup)
		if resolveErr != nil || resolved.CredentialID != credentialID {
			return errors.New("10k route resolution mismatch")
		}
		return nil
	})
	if err := insertSyntheticRoutes(database, namespace, credentialID, entry, 10_000, 90_000); err != nil {
		return nil, err
	}
	route100K := measure("E2", "sqlite_route_lookup_100k", 25*time.Millisecond, func() error {
		resolved, resolveErr := repository.ResolveLookup(context.Background(), namespace, lookup)
		if resolveErr != nil || resolved.CredentialID != credentialID {
			return errors.New("100k route resolution mismatch")
		}
		return nil
	})
	route10K.Notes = "真实 SQLite WAL/FULL、单连接、精确 HMAC 索引；共 10,000 条。"
	route100K.Notes = "真实 SQLite WAL/FULL、单连接、精确 HMAC 索引；共 100,000 条。"
	return []metric{fieldMetric, route10K, route100K}, nil
}

func insertSyntheticRoutes(
	database *sqliteadapter.Database,
	namespace protocol.NamespaceID,
	credentialID protocol.CredentialID,
	entry *credentialdomain.EncryptedRouteEntry,
	start, count int,
) error {
	transaction, err := database.BeginImmediate(context.Background())
	if err != nil {
		return err
	}
	defer transaction.Rollback()
	encryptedOrigin := entry.EncryptedOrigin()
	encryptedAccount := entry.EncryptedAccount()
	for index := start; index < start+count; index++ {
		routeID := indexedHash(0x71, uint64(index))
		originIndex := indexedHash(0x72, uint64(index))
		binding := indexedHash(0x73, uint64(index))
		if _, err := transaction.ExecContext(
			context.Background(),
			`INSERT INTO route_entries (
  namespace_id, route_id, origin_index, credential_id,
  encrypted_origin, encrypted_account_id, origin_binding,
  route_version, status, created_at_ms, updated_at_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'ACTIVE', 1, 1)`,
			namespace[:], routeID[:], originIndex[:], credentialID[:],
			encryptedOrigin, encryptedAccount, binding[:],
		); err != nil {
			return err
		}
	}
	return transaction.Commit()
}

func runE3() ([]metric, error) {
	namespace := filledNamespace(0x81)
	device := filledDevice(0x82)
	privateKey := ed25519.NewKeyFromSeed(bytes.Repeat([]byte{0x83}, ed25519.SeedSize))
	publicKey := privateKey.Public().(ed25519.PublicKey)
	keyID, err := protocol.KeyIDFromPublicKey(publicKey)
	if err != nil {
		return nil, err
	}
	base := sha256.Sum256([]byte("TEST_ONLY-sync-base"))
	target := sha256.Sum256([]byte("TEST_ONLY-sync-target"))
	const (
		objectsPerManifest = 100
		manifestCount      = 100
	)
	objects := make([]syncdomain.ObjectReference, objectsPerManifest)
	for index := range objects {
		objects[index] = syncdomain.ObjectReference{
			ObjectDigest: indexedHash(0x84, uint64(index)),
			ObjectType:   protocol.ObjectTypeOperationEvent,
			Size:         uint64(index + 1),
		}
	}
	var counter uint64
	syncMetric := measure("E3", "sync_manifest_sign_verify_10k_batched", 2*time.Second, func() error {
		for batch := 0; batch < manifestCount; batch++ {
			counter++
			manifest, signErr := syncdomain.SignManifest(
				privateKey, "g7-research-chain", 1, namespace, device,
				base, target, counter, counter, objects,
			)
			if signErr != nil {
				return signErr
			}
			if _, verifyErr := syncdomain.ParseAndVerifyManifest(
				manifest.SigInputCBOR(), manifest.Signature(), publicKey,
				protocol.VerificationContext{
					ObjectType: protocol.ObjectTypeSyncManifest,
					ChainID:    "g7-research-chain", NamespaceID: namespace,
					KeyID: keyID, KeyGeneration: 1,
				},
			); verifyErr != nil {
				return verifyErr
			}
		}
		return nil
	})
	syncMetric.Notes = "10,000 个对象按 100×100 分批；排序、集合 Merkle 根、CBOR、Ed25519 签名和验证均在采样内。单份 10k 引用会触发 64KiB 签名载荷上限，已保留为设计风险。"
	return []metric{syncMetric}, nil
}

func runE5() ([]metric, int, int, error) {
	tree := transparencydomain.NewTree()
	const million = 1_000_000
	for index := 0; index < million; index++ {
		if _, _, err := tree.Append(g7Leaf(uint64(index))); err != nil {
			return nil, 0, 0, err
		}
	}
	metric100K, proof100K, err := measureProof(tree, 100_000)
	if err != nil {
		return nil, 0, 0, err
	}
	metric1M, proof1M, err := measureProof(tree, 1_000_000)
	if err != nil {
		return nil, 0, 0, err
	}
	metric100K.Notes = fmt.Sprintf("真实内存树前缀，proofHashes=%d。", proof100K)
	metric1M.Notes = fmt.Sprintf("真实 1m 叶树，proofHashes=%d，协议上限=32。", proof1M)
	return []metric{metric100K, metric1M}, proof100K, proof1M, nil
}

func measureProof(
	tree *transparencydomain.Tree,
	size uint64,
) (metric, int, error) {
	index := size / 2
	root, err := tree.RootAt(size)
	if err != nil {
		return metric{}, 0, err
	}
	proof, err := tree.InclusionProof(index, size)
	if err != nil {
		return metric{}, 0, err
	}
	leafHash, err := transparencydomain.LeafHash(g7Leaf(index))
	if err != nil {
		return metric{}, 0, err
	}
	result := measure("E5", "merkle_inclusion_verify_"+strconv.FormatUint(size, 10), 25*time.Millisecond, func() error {
		return transparencydomain.VerifyInclusion(leafHash, index, size, proof, root)
	})
	if len(proof) > 32 {
		result.Passed = false
	}
	return result, len(proof), nil
}

func measure(experimentID, name string, target time.Duration, operation func() error) metric {
	for index := 0; index < warmupCount; index++ {
		if err := operation(); err != nil {
			fatal(fmt.Errorf("%s warmup: %w", name, err))
		}
	}
	runtime.GC()
	var before, after runtime.MemStats
	var usageBefore, usageAfter syscall.Rusage
	_ = syscall.Getrusage(syscall.RUSAGE_SELF, &usageBefore)
	runtime.ReadMemStats(&before)
	durations := make([]int64, repetitionCount)
	for index := range durations {
		started := time.Now()
		if err := operation(); err != nil {
			fatal(fmt.Errorf("%s sample: %w", name, err))
		}
		durations[index] = time.Since(started).Nanoseconds()
	}
	runtime.ReadMemStats(&after)
	_ = syscall.Getrusage(syscall.RUSAGE_SELF, &usageAfter)
	sorted := append([]int64(nil), durations...)
	sort.Slice(sorted, func(i, j int) bool { return sorted[i] < sorted[j] })
	mean, standardDeviation := meanAndStddev(durations)
	low, high := bootstrapMean95(durations)
	p95 := percentile(sorted, 95)
	return metric{
		Experiment: experimentID, Name: name, Unit: "nanoseconds",
		Samples: len(durations), P50: percentile(sorted, 50),
		P95: p95, P99: percentile(sorted, 99), Mean: mean,
		StandardDeviation: standardDeviation,
		Bootstrap95Low:    low, Bootstrap95High: high,
		AllocatedBytes: allocationDelta(before.TotalAlloc, after.TotalAlloc),
		CPUUserNanos: timevalNanos(usageAfter.Utime) -
			timevalNanos(usageBefore.Utime),
		CPUSystemNanos: timevalNanos(usageAfter.Stime) -
			timevalNanos(usageBefore.Stime),
		MaxRSSBytes: maxRSSBytes(), Target: target.Nanoseconds(),
		Passed: p95 <= target.Nanoseconds(),
	}
}

func meanAndStddev(values []int64) (float64, float64) {
	var total float64
	for _, value := range values {
		total += float64(value)
	}
	mean := total / float64(len(values))
	var squared float64
	for _, value := range values {
		delta := float64(value) - mean
		squared += delta * delta
	}
	return mean, math.Sqrt(squared / float64(len(values)-1))
}

func bootstrapMean95(values []int64) (float64, float64) {
	const samples = 1000
	means := make([]float64, samples)
	state := experimentSeed
	for sample := range means {
		var total float64
		for range values {
			state ^= state << 13
			state ^= state >> 7
			state ^= state << 17
			total += float64(values[state%uint64(len(values))])
		}
		means[sample] = total / float64(len(values))
	}
	sort.Float64s(means)
	return means[24], means[974]
}

func percentile(values []int64, percent int) int64 {
	index := (percent*len(values) + 99) / 100
	if index < 1 {
		index = 1
	}
	return values[index-1]
}

func collectEnvironment(started, finished time.Time) environment {
	return environment{
		Commit: "WORKTREE_NO_GIT", ProtocolID: protocol.ProtocolID,
		ProtocolVersion: protocol.ProtocolVersion, SuiteID: protocol.SuiteID,
		GoVersion: runtime.Version(), NodeVersion: commandVersion("node", "--version"),
		BrowserVersion: "NOT_INSTALLED_HEADLESS_CONTRACT_ONLY",
		OS:             runtime.GOOS, Architecture: runtime.GOARCH, CPU: cpuModel(),
		LogicalCores: runtime.NumCPU(), MemoryBytes: totalMemoryBytes(),
		Storage:    "workspace filesystem; storage medium not independently classified",
		BuildFlags: []string{"-trimpath"}, DatasetVersion: datasetVersion,
		Seed: experimentSeed, WarmupRepetitions: warmupCount,
		MeasuredRepetitions: repetitionCount,
		ProviderKinds: []string{
			"REAL_LOCAL_CRYPTO", "REAL_LOCAL_SQLITE", "MOCK_SITE",
			"SIMULATED_LOG", "ANVIL_OPTIONAL", "SCOPE_ZK_UNAVAILABLE",
			"GENERIC_ZKVM_UNAVAILABLE",
		},
		StartedAt:  started.Format(time.RFC3339Nano),
		FinishedAt: finished.Format(time.RFC3339Nano),
	}
}

func commandVersion(name string, arguments ...string) string {
	if name != "node" {
		return "UNAVAILABLE"
	}
	output, err := exec.Command(name, arguments...).Output()
	if err != nil {
		return "UNAVAILABLE"
	}
	value := strings.TrimSpace(string(output))
	if value == "" || len(value) > 128 {
		return "UNAVAILABLE"
	}
	return value
}

func cpuModel() string {
	content, err := os.ReadFile("/proc/cpuinfo")
	if err != nil {
		return "UNAVAILABLE"
	}
	for _, line := range strings.Split(string(content), "\n") {
		if strings.HasPrefix(line, "model name") {
			if _, value, ok := strings.Cut(line, ":"); ok {
				return strings.TrimSpace(value)
			}
		}
	}
	return "UNAVAILABLE"
}

func totalMemoryBytes() uint64 {
	content, err := os.ReadFile("/proc/meminfo")
	if err != nil {
		return 0
	}
	for _, line := range strings.Split(string(content), "\n") {
		fields := strings.Fields(line)
		if len(fields) == 3 && fields[0] == "MemTotal:" {
			kib, parseErr := strconv.ParseUint(fields[1], 10, 64)
			if parseErr == nil {
				return kib * 1024
			}
		}
	}
	return 0
}

func maxRSSBytes() uint64 {
	var usage syscall.Rusage
	if syscall.Getrusage(syscall.RUSAGE_SELF, &usage) != nil || usage.Maxrss < 0 {
		return 0
	}
	return uint64(usage.Maxrss) * 1024
}

func timevalNanos(value syscall.Timeval) int64 {
	return value.Sec*int64(time.Second) + value.Usec*int64(time.Microsecond)
}

func statusForMetrics(metrics []metric) string {
	for _, current := range metrics {
		if !current.Passed {
			return "COMPLETED_TARGET_NOT_MET"
		}
	}
	return "COMPLETED_TARGET_MET"
}

func filledNamespace(marker byte) protocol.NamespaceID {
	var value protocol.NamespaceID
	for index := range value {
		value[index] = marker
	}
	return value
}

func filledDevice(marker byte) protocol.DeviceID {
	var value protocol.DeviceID
	for index := range value {
		value[index] = marker
	}
	return value
}

func filledCredential(marker byte) protocol.CredentialID {
	var value protocol.CredentialID
	for index := range value {
		value[index] = marker
	}
	return value
}

func indexedHash(marker byte, index uint64) [sha256.Size]byte {
	var input [9]byte
	input[0] = marker
	binary.BigEndian.PutUint64(input[1:], index)
	return sha256.Sum256(input[:])
}

func g7Leaf(index uint64) transparencydomain.LogLeaf {
	return transparencydomain.LogLeaf{
		NamespaceCommitment: indexedHash(0x91, index),
		SubjectPseudonym:    indexedHash(0x92, index),
		ObjectType:          protocol.ObjectTypeOperationEvent,
		ObjectDigest:        indexedHash(0x93, index),
		OperationType:       protocol.OperationResolve,
		FinalSequence:       index + 1, Epoch: 1 + index/100_000,
	}
}

func allocationDelta(before, after uint64) uint64 {
	if after < before {
		return 0
	}
	return after - before
}

func writeJSON(path string, value any) error {
	encoded, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	encoded = append(encoded, '\n')
	return os.WriteFile(path, encoded, 0o640)
}

func writeMetricsCSV(path string, metrics []metric) error {
	file, err := os.OpenFile(path, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0o640)
	if err != nil {
		return err
	}
	defer file.Close()
	writer := csv.NewWriter(file)
	if err := writer.Write([]string{
		"experiment", "name", "unit", "samples", "p50", "p95", "p99",
		"mean", "standard_deviation", "bootstrap_95_low", "bootstrap_95_high",
		"allocated_bytes", "cpu_user_nanoseconds", "cpu_system_nanoseconds",
		"max_rss_bytes", "target", "passed", "notes",
	}); err != nil {
		return err
	}
	for _, current := range metrics {
		if err := writer.Write([]string{
			current.Experiment, current.Name, current.Unit,
			strconv.Itoa(current.Samples), strconv.FormatInt(current.P50, 10),
			strconv.FormatInt(current.P95, 10), strconv.FormatInt(current.P99, 10),
			strconv.FormatFloat(current.Mean, 'f', 2, 64),
			strconv.FormatFloat(current.StandardDeviation, 'f', 2, 64),
			strconv.FormatFloat(current.Bootstrap95Low, 'f', 2, 64),
			strconv.FormatFloat(current.Bootstrap95High, 'f', 2, 64),
			strconv.FormatUint(current.AllocatedBytes, 10),
			strconv.FormatInt(current.CPUUserNanos, 10),
			strconv.FormatInt(current.CPUSystemNanos, 10),
			strconv.FormatUint(current.MaxRSSBytes, 10),
			strconv.FormatInt(current.Target, 10),
			strconv.FormatBool(current.Passed), current.Notes,
		}); err != nil {
			return err
		}
	}
	writer.Flush()
	return errors.Join(writer.Error(), file.Sync())
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, "g7-research-runner:", err)
	os.Exit(1)
}
