"""Read-only proof-package provenance/scope checks; no theorem verification."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


checks = []
for row in read(ROOT / "INPUT_LOCK.json")["files"]:
    p = Path(row["path"])
    checks.append({"kind": "historical_hash", "path": str(p),
                   "pass": p.is_file() and sha(p) == row["sha256"]})
for row in read(ROOT / "ARTIFACT_MANIFEST.json")["files"]:
    p = ROOT / row["path"]
    checks.append({"kind": "new_hash", "path": row["path"],
                   "pass": p.is_file() and sha(p) == row["sha256"]})
math = read(ROOT / "MATHEMATICAL_CHECKS.json")
for row in math["checks"]:
    checks.append({"kind": "finite_math", "id": row["id"], "pass": row["pass"]})
v = read(ROOT / "VERDICT.json")
checks.append({"kind": "scope", "id": "two_distinct_complete_games",
               "pass": set(v["games"]) == {"G-ALL-ADAPT", "G-SELECT-ADAPT"}
               and all(x["game_complete"] for x in v["games"].values())})
checks.append({"kind": "scope", "id": "no_fictional_all_future_key",
               "pass": v["games"]["G-ALL-ADAPT"]["legal_future_keys_exist"] is False})
witness = v["games"]["G-SELECT-ADAPT"]["legitimate_future_key_witness"]
checks.append({"kind": "scope", "id": "complete_legal_future_witness",
               "pass": witness["legal"] is True and witness["key_closure"] == [3, 4]
               and witness["challenge_closure"] == [2]})
checks.append({"kind": "scope", "id": "ideal_factors_separate",
               "pass": v["games"]["G-ALL-ADAPT"]["ideal_DDH_star_exact_factor"] == "L-1"
               and v["games"]["G-SELECT-ADAPT"]["ideal_DDH_star_exact_factor"] == "L*(L-1)/2"})
checks.append({"kind": "scope", "id": "zero_execution_budget_use",
               "pass": v["candidate_protocol_implementation"] == v["external_contact"]
               == v["email_sent"] == v["native_AS_RP_requests"] == 0})
checks.append({"kind": "scope", "id": "review_level_separate",
               "pass": v["external_peer_review"] is False and v["priority_cleared"] is False
               and v["proof_assistant"] is False})
checks.append({"kind": "scope", "id": "Frodo_no_promotion",
               "pass": v["Frodo_candidate"]["uses_random_tape_leak"] is False
               and v["Frodo_candidate"]["message_recovery_claim"] is False
               and v["Frodo_candidate"]["new_repairs_or_parameter_experiments"] == 0})
print(json.dumps({
    "schema": "UNI-ADAPTIVE-R2-VALIDATION-1", "read_only": True,
    "checks": checks,
    "counts": {"total": len(checks), "passed": sum(x["pass"] for x in checks),
               "failed": sum(not x["pass"] for x in checks)},
    "all_pass": all(x["pass"] for x in checks),
    "verifies_general_theorem": False,
    "independent_peer_review": False,
}, ensure_ascii=False, indent=2))
