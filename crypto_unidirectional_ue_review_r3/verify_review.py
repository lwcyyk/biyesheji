"""Read-only provenance/grade checks; not a proof assistant or isolated reviewer."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


checks = []
manifest = read(ROOT / "REVIEW_INPUT_MANIFEST.json")
for row in manifest["frozen_inputs"]:
    p = Path(row["path"])
    checks.append({"kind": "historical_hash", "path": str(p),
                   "pass": p.is_file() and sha(p) == row["sha256"]})
for row in manifest["phase1_packet"]["files"]:
    p = Path(row["path"])
    checks.append({"kind": "phase1_packet_hash", "path": str(p),
                   "pass": p.is_file() and sha(p) == row["sha256"]})
for row in read(ROOT / "ARTIFACT_MANIFEST.json")["files"]:
    p = ROOT / row["path"]
    checks.append({"kind": "new_hash", "path": row["path"],
                   "pass": p.is_file() and sha(p) == row["sha256"]})
v = read(ROOT / "REVIEW_VERDICT.json")
stage = manifest["isolated_derivation"]
checks.append({"kind": "execution_honesty", "id": "no_fictitious_isolated_result",
               "pass": stage["executed"] is False and stage["task_id"] is None
               and stage["first_result_sha256"] is None and stage["first_result_time_utc"] is None
               and v["independent_derivation"]["executed"] is False})
checks.append({"kind": "execution_honesty", "id": "actual_same_session_review",
               "pass": manifest["actual_review"]["new_model_instance"] is False
               and manifest["actual_review"]["reviewer_already_knew_and_had_read_target_proof"] is True
               and manifest["finite_check_execution"]["independent_language_model_task"] is False})
fallback = manifest["actual_review"]["reconstruction_result"]
checks.append({"kind": "actual_result_hash", "id": "informed_reconstruction",
               "pass": sha(fallback["path"]) == fallback["sha256"]})
for row in read(ROOT / "REVIEW_CHECKS.json")["checks"]:
    checks.append({"kind": "finite_check", "id": row["id"], "pass": row["pass"]})
checks.append({"kind": "scope", "id": "original_bound_retained",
               "pass": v["bound_audit"]["original_conservative_bound_status"] == "VALID_NO_REQUIRED_COEFFICIENT_INCREASE"})
checks.append({"kind": "scope", "id": "no_scheme_or_ideal_game_change",
               "pass": v["algorithm_or_ideal_game_changed"] is False})
checks.append({"kind": "scope", "id": "no_new_execution_or_contact",
               "pass": v["candidate_protocol_implementation"] == v["external_contact"]
               == v["email_sent"] == v["native_AS_RP_requests"] == 0})
print(json.dumps({
    "schema": "SELECT-REVIEW-R3-VALIDATION-1", "read_only": True,
    "checks": checks,
    "counts": {"total": len(checks), "passed": sum(x["pass"] for x in checks),
               "failed": sum(not x["pass"] for x in checks)},
    "all_pass": all(x["pass"] for x in checks),
    "independent_derivation_executed": False,
    "general_theorem_verified_by_program": False,
}, ensure_ascii=False, indent=2))
