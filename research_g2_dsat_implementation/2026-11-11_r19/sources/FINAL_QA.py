"""Final document/integrity QA. No application imports or service execution."""
import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(r"D:\毕业设计")
PROJECT = ROOT / "auth-lifecycle"
BASE = ROOT / "research_g2_dsat_implementation"
RECORD = BASE / "2026-11-11_r19"
OFFLINE = BASE / "2026-11-11_r19_offline"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks = []


def check(label, condition, detail=None):
    checks.append({"label": label, "passed": bool(condition), "detail": detail})


required = ["01_IMPLEMENTATION_SUMMARY.md", "02_BOOTSTRAP_AND_DORMANT_ACTIVATION.md",
    "03_ENVIRONMENT_ISOLATION_AND_SECURITY.md", "04_TEST_RESULTS.md", "05_CODE_DIFF_AND_INTEGRITY.md",
    "06_FINAL_VERDICT_AND_NEXT_STEP.md", "D1A_FILE_LOCK.json", "D1A_ACTUAL_RESULTS.json",
    "D1A_TEST_RUNS.json", "D1A_SECURITY_AUDIT.json", "D1B_COMMAND_LOCK.json", "P1A_COMMAND_LOCK.json",
    "P1B_COMMAND_LOCK.json", "CODE_DIFF.json", "SOURCE_LOCK.json"]
check("ALL_15_REQUIRED_DELIVERABLES", all((RECORD / x).is_file() for x in required))
verdict = (RECORD / "06_FINAL_VERDICT_AND_NEXT_STEP.md").read_text(encoding="utf-8")
check("Q1_THROUGH_Q15_ANSWERED", all(re.search(r"\| Q" + str(i) + r"\b", verdict) for i in range(1, 16)))
manifest = load(BASE / "2026-11-11_r18/D1_IMPLEMENTATION_TASKS.json")
file_lock = load(RECORD / "D1A_FILE_LOCK.json")
check("SEVEN_EXACT_FROZEN_TARGETS", [x["path"] for x in file_lock] == [x["path"] for x in manifest["D1_A"]["targets"]])
check("FILE_LOCK_NO_PLACEHOLDERS", all(x["entry"] and x["inputs"] and x["outputs"] and x["allowed_tests"] and x["safety_boundary"] for x in file_lock))

baseline = load(RECORD / "sources/PRECHECK_LOCK.json")
allowed = baseline["allowed_modification"]
expected_new = next(x["after_sha256"] for x in file_lock if x["path"] == allowed["path"])
rows = []
for row in baseline["checks"]:
    current = sha(Path(row["path"]))
    authorized = row["path"] == allowed["path"]
    good = current == (expected_new if authorized else row["expected"])
    rows.append({"path": row["path"], "historical_sha256": row["expected"],
                 "current_sha256": current, "authorized_change": authorized, "matches_contract": good})
check("HISTORICAL_1441_COMPARISONS", len(rows) == 1441 and all(x["matches_contract"] for x in rows))
check("ONLY_SERVICES_NINE_AUTHORIZED_ROWS", sum(x["authorized_change"] for x in rows) == 9)
check("OTHER_1432_ROWS_UNCHANGED", sum(not x["authorized_change"] for x in rows) == 1432)
check("ORIGINAL_SERVICES_SNAPSHOT", sha(Path(allowed["snapshot"])) == allowed["before_sha256"])
check("R18_READING_SOURCE_HASHES", all(sha(Path(x["path"])) == x["sha256"] for x in baseline["R18_read"]))
confirmed = BASE / "2026-11-11_r18_parameter_confirmation/H2_ENVIRONMENT_CONFIG_CONFIRMED.json"
fixture_confirmed = PROJECT / "tests/fixtures/dsat_authority_runtime/CONFIRMED_CONFIG.json"
check("CONFIRMATION_EXACT_FIXTURE_COPY", confirmed.read_bytes() == fixture_confirmed.read_bytes())

final_new = load(OFFLINE / "d1a_002/RESULTS.json")
final_old = load(OFFLINE / "regressions_002/RESULTS.json")
check("FINAL_CODE_HASHES_IDENTICAL", final_new["code"] == final_old["code"])
check("CURRENT_CODE_MATCHES_FINAL_SUITES", all(sha(Path(x["path"])) == x["sha256"] for x in final_new["code"]))
check("CURRENT_INPUTS_MATCH_FINAL_SUITES", all(sha(Path(x["path"])) == x["sha256"] for r in (final_new, final_old) for x in r["inputs"]))
check("NEW_IDS_D01_D24", [x["id"] for x in final_new["cases"]] == ["D%02d" % i for i in range(1, 25)])
check("OLD_IDS_A01_A20_H01_H24", [x["id"] for x in final_old["cases"]] == ["A%02d" % i for i in range(1, 21)] + ["H%02d" % i for i in range(1, 25)])
check("FINAL_68_PASS", final_new["counts"] == {"PASS": 24, "FAIL": 0, "ERROR": 0, "SKIP": 0} and final_old["counts"] == {"PASS": 44, "FAIL": 0, "ERROR": 0, "SKIP": 0})
check("2056_SATISFIED_CHECKS", sum(len(c["checks"]) for r in (final_new, final_old) for c in r["details"]) == 2056 and all(x["satisfied"] for r in (final_new, final_old) for c in r["details"] for x in c["checks"]))
for result in (final_new, final_old):
    name = result["suite"]
    a = result["scope_audit"]
    check(name + "_NO_FORBIDDEN_SIDE_EFFECT", all(a[k] == 0 for k in ("file_SQLite", "socket", "process", "private_file", "deployment_access", "outside_write", "forbidden_SQL")) and a["violations"] == [])
    check(name + "_NO_REAL_SERVICE_IMPORT", result["production_module_imports"] == [])
    check(name + "_TEST_SPAWNED_SUBPROCESS_ZERO", result["test_spawned_subprocesses"] == 0)
    check(name + "_NO_REAL_GATED_EXECUTIONS", result["service_DB_key_RPC_process_bind"] == result["D1B_P1a_P1b_P2_B2_S5"] == 0)
check("CRYPTO_DOMAINS_SEPARATE", final_new["cryptography_imported"] is True and final_old["cryptography_imported"] is False)
check("MEMORY_CONNECTIONS_WITHIN_FROZEN_SCOPE", final_new["scope_audit"]["memory_connections"] == 1 and final_old["scope_audit"]["memory_connections"] == 18)

runs = load(RECORD / "D1A_TEST_RUNS.json")
check("FOUR_COMPLETED_RUNS_RETAINED", len(runs["runs"]) == 4 and all(sha(Path(x["path"])) == x["sha256"] for x in runs["runs"]))
failure = load(OFFLINE / "preflight_001/EARLY_FAILURE.json")
check("EARLY_FAILURE_RETAINED", failure["exception"] == "UnicodeDecodeError" and failure["tests_executed"] == 0 and len(runs["early_failures"]) == 1 and sha(Path(runs["early_failures"][0]["path"])) == runs["early_failures"][0]["sha256"])
snapshots = []
for folder in sorted(x for x in OFFLINE.iterdir() if x.is_dir()):
    source = load(folder / "RESULTS.json") if (folder / "RESULTS.json").exists() else load(folder / "EARLY_FAILURE.json")
    for row in source["code"]:
        p = folder / "code_snapshot" / (Path(row["path"]).name + ".txt")
        snapshots.append(p.is_file() and sha(p) == row["sha256"])
check("ALL_FIVE_RUN_CODE_SNAPSHOTS_BOUND", len(snapshots) == 30 and all(snapshots))
for name in ("D1B_COMMAND_LOCK.json", "P1A_COMMAND_LOCK.json", "P1B_COMMAND_LOCK.json"):
    d = load(RECORD / name)
    check(name + "_CLOSED", d["AUTHORIZED"] is d["EXECUTED"] is d["command_executable"] is False and d["actual_argv"] is None)
check("DEPLOYMENT_ROOT_ABSENT_METADATA_ONLY", not (ROOT / "h2_test_runtime/h2-authority-synth-001").exists())

secret_files = [PROJECT / "tests/fixtures" / x / "CANARIES.json" for x in
                ("dsat_authority_runtime", "dsat_authority_host_activation", "dsat_authority_read_host")]
values = sorted(set(v for p in secret_files for v in load(p)["values"].values()))
needles = []
for value in values:
    needles.append(value.encode("utf-8"))
    needles.append(json.dumps(value, ensure_ascii=True)[1:-1].encode("ascii"))
    needles.append(json.dumps(value, ensure_ascii=False)[1:-1].encode("utf-8"))
public_files = sorted(p for root in (RECORD, OFFLINE) for p in root.rglob("*") if p.is_file() and p.name != "DELIVERY_QA.json")
secret_hits = []
json_errors = []
phrasing_hits = []
for p in public_files:
    raw = p.read_bytes()
    if any(x in raw for x in needles):
        secret_hits.append(str(p))
    if p.suffix == ".json":
        try:
            load(p)
        except Exception:
            json_errors.append(str(p))
    if p.suffix == ".md" and "不是" in raw.decode("utf-8-sig"):
        phrasing_hits.append(str(p))
check("PUBLIC_CANARY_SCAN", not secret_hits, {"hits": secret_hits, "unique_canaries": len(values), "input_hashes": [{"path": str(p), "sha256": sha(p)} for p in secret_files]})
check("PUBLIC_JSON_PARSE", not json_errors, json_errors)
check("REPORT_PHRASING", not phrasing_hits, phrasing_hits)
source_lock = load(RECORD / "SOURCE_LOCK.json")
check("SOURCE_LOCK_FILE_BINDINGS", source_lock["file_lock_sha256"] == sha(RECORD / "D1A_FILE_LOCK.json") and source_lock["final_status_sha256"] == sha(RECORD / "FINAL_STATUS.json") and source_lock["approval_sha256"] == sha(RECORD / "APPROVAL_RECEIPT.json"))

payload = {"schema": "r19-delivery-qa/1", "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "method": "document/hash/JSON/static QA only; no application import, test rerun or deployment",
    "passed": all(x["passed"] for x in checks), "checks": checks,
    "historical_comparison_count": len(rows), "authorized_modified_source": allowed["path"],
    "public_file_count": len(public_files), "secret_scan": "CLEAN" if not secret_hits else "FAIL",
    "files": [{"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size} for p in public_files],
    "open_responsibilities": ["live issuer/admission and R16 session linkage", "OS/ACL/source/single-active epoch provider", "real key/TLS/Schema2/SQL budgets", "pre-listen failure cleanup and exact owned-process start/stop", "P1a real target/provider and independent P1/P2 approvals"],
    "self_hash_policy": "this file excluded from its own manifest"}
(RECORD / "sources/DELIVERY_QA.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"passed": payload["passed"], "qa_checks": len(checks), "files_scanned": len(public_files),
    "historical_rows": len(rows), "canary_hits": len(secret_hits), "json_errors": len(json_errors),
    "failed_checks": [x["label"] for x in checks if not x["passed"]]}, ensure_ascii=True))
raise SystemExit(0 if payload["passed"] else 1)
