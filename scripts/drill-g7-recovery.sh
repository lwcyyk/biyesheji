#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="${1:-${repo_root}/test-results/g7/recovery}"
mkdir -p "${output_dir}"

jsonl="$(mktemp)"
trap 'rm -f "${jsonl}"' EXIT

run_case() {
  local id="$1"
  local scenario="$2"
  local expected="$3"
  shift 3
  local log_file="${output_dir}/${id}.txt"
  local started_ns finished_ns duration_ns status exit_code

  started_ns="$(date +%s%N)"
  set +e
  (
    cd "${repo_root}"
    env -u GOPATH "$@"
  ) >"${log_file}" 2>&1
  exit_code=$?
  set -e
  finished_ns="$(date +%s%N)"
  duration_ns=$((finished_ns - started_ns))
  status="PASSED"
  if [[ "${exit_code}" -ne 0 ]]; then
    status="FAILED"
  fi

  jq -n \
    --arg id "${id}" \
    --arg scenario "${scenario}" \
    --arg expected "${expected}" \
    --arg status "${status}" \
    --arg log "$(basename "${log_file}")" \
    --argjson exitCode "${exit_code}" \
    --argjson durationNs "${duration_ns}" \
    '{
      id: $id,
      scenario: $scenario,
      expectedOutcome: $expected,
      status: $status,
      exitCode: $exitCode,
      durationNs: $durationNs,
      evidence: $log
    }' >>"${jsonl}"
}

run_case "DRILL_LOCK_001" \
  "锁定、会话超时和句柄绑定" \
  "锁定或超时后根和一次性句柄不可继续使用" \
  go test ./internal/localapi/application ./internal/credential/domain \
  -run 'TestLocalSecureClientSessionExpiryAndHandleBinding|TestVaultSessionLockAndTimeoutDestroyHandlesAndRoots' \
  -count=1

run_case "DRILL_OFFLINE_001" \
  "断网期间的日常使用和重连同步" \
  "已缓存且已验证凭据可按策略使用，撤销设备不能获得新代际" \
  go test ./tests/e2e \
  -run '^TestDailyMockSiteRegisterLoginChangeSyncRevokeAndOffline$' \
  -count=1

run_case "DRILL_RESTART_001" \
  "进程重启后的仓库、outbox 和改密候选恢复" \
  "幂等键、待发送事件、RouteMap 和候选状态保持一致" \
  go test ./internal/adapters/outbound/sqlite \
  -run 'TestLocalAPIRepositoryHashesKeysAndSurvivesRestart|TestOperationOutboxLeaseRetryRestartAndIdempotentInclusion|TestRouteRepositorySameOriginAccountsRestartAndRemoval|TestSiteChangeRepositoryRequiresDurableCandidateAndPersistsRecoveryState|TestVaultProfileRepositoryRestartRecoveryAndNoBareRoot' \
  -count=1

run_case "DRILL_BACKUP_001" \
  "高熵恢复秘密、胶囊、对象和可信状态联合恢复" \
  "完整且一致的恢复材料成功；错误秘密、缺对象和回滚均失败关闭" \
  go test ./internal/cryptokit ./internal/recovery/domain \
  -run 'TestRecoveryCapsuleRoundTripAndHighEntropySecretRequirement|TestRecoveryRequiresCapsuleObjectsTrustedStateAndRootConsistency|TestRecoveryRejectsMissingObjectsRollbackAndBypass' \
  -count=1

run_case "DRILL_DEVICE_LOSS_001" \
  "设备丢失后的撤销与名称空间秘密代际轮换" \
  "只有剩余活动设备收到新代际，丢失设备不能解密新对象" \
  go test ./internal/device/domain \
  -run 'TestGenerationRolloverEncryptsOnlyForRemainingActiveDevices|TestGenerationRolloverRequiresRevokedTargetAndUniqueDevices' \
  -count=1

run_case "DRILL_CONFLICT_001" \
  "并发更新冲突和显式人工裁决" \
  "两个分支都被保留，系统不静默覆盖且只接受显式选择" \
  go test ./internal/credential/domain ./internal/sync/domain \
  -run 'TestAggregateConflictRetainsBothAndRequiresExplicitResolution|TestSyncManifestRejectsDuplicateReorderAndWrongContext' \
  -count=1

run_case "DRILL_UNKNOWN_001" \
  "网站改密响应丢失或结果不明确" \
  "进入 UNKNOWN/REVIEW，保留旧版本和耐久候选，不猜测激活" \
  go test ./internal/site/application ./internal/credential/domain \
  -run 'TestCoordinatorRecoversLostResponseAndSeparatesUnknownReview|TestVersionCrashRecoveryActionsAndEvidenceGate' \
  -count=1

failed="$(jq -s '[.[] | select(.status != "PASSED")] | length' "${jsonl}")"
jq -s \
  --arg schemaVersion "1.0.0" \
  --arg datasetVersion "vpass-g7-datasets-v1" \
  --arg classification "EXECUTABLE_RECOVERY_DRILL" \
  --argjson seed 20260723 \
  --argjson failed "${failed}" \
  '{
    schemaVersion: $schemaVersion,
    datasetVersion: $datasetVersion,
    seed: $seed,
    classification: $classification,
    summary: {
      total: length,
      passed: (length - $failed),
      failed: $failed
    },
    drills: .
  }' "${jsonl}" >"${output_dir}/recovery-drill.json"

if [[ "${failed}" -ne 0 ]]; then
  jq '.summary' "${output_dir}/recovery-drill.json"
  exit 1
fi

echo "g7-recovery-drill-ok"
