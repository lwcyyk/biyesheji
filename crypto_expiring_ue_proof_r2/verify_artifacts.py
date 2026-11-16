"""Read-only integrity and finite-check validator, separate from security proofs.

Usage: python verify_artifacts.py
No network, no writes, no protocol implementation.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


checks = []
locked = read_json(ROOT / "STARTING_POINT_LOCK.json")
for row in locked["files"]:
    path = Path(row["path"])
    exists = path.is_file()
    checks.append({"kind": "historical_input", "path": str(path),
                   "exists": exists,
                   "pass": exists and digest(path) == row["sha256"]})

manifest = read_json(ROOT / "ARTIFACT_MANIFEST.json")
for row in manifest["files"]:
    path = ROOT / row["path"]
    exists = path.is_file()
    checks.append({"kind": "new_artifact", "path": row["path"],
                   "exists": exists,
                   "pass": exists and digest(path) == row["sha256"]})

math = read_json(ROOT / "MATHEMATICAL_CHECKS.json")
for row in math["checks"]:
    checks.append({"kind": "finite_math_result", "id": row["id"],
                   "pass": row["pass"] is True})

verdict = read_json(ROOT / "VERDICT.json")
checks.append({"kind": "scope", "id": "game_and_result_grade",
               "pass": verdict["game"] == "EE-R-PA1" and
               verdict["primary_result"] == "PROOF_TECHNIQUE_OBSTRUCTION"})
gate = verdict["implementation_gate"]
checks.append({"kind": "scope", "id": "paper_only_declared_scope",
               "pass": gate["candidate_protocol_code_written"] == 0 and
               gate["native_AS_RP_requests"] == 0 and gate["passed"] is False})

source_register = read_json(ROOT / "SOURCE_REGISTER_R2.json")
for row in source_register["sources"]:
    if row.get("path") and row.get("sha256"):
        path = Path(row["path"])
        checks.append({"kind": "source_reference", "id": row["id"],
                       "pass": path.is_file() and digest(path) == row["sha256"]})

print(json.dumps({
    "schema": "R2-OFFLINE-VALIDATION-1",
    "read_only": True,
    "checks": checks,
    "counts": {"total": len(checks),
               "passed": sum(row["pass"] for row in checks),
               "failed": sum(not row["pass"] for row in checks)},
    "all_pass": all(row["pass"] for row in checks),
    "proves_cryptographic_security": False,
    "unresolved_evidence": [
        "Author extended PDF, historical-version fulltexts and erratum not verified",
        "RCCA19 and independent DSG [43] fulltexts missing",
        "Typed complete author construction and enhanced hybrid proof unresolved",
        "No author confirmation, proof-assistant or external peer review",
    ],
}, ensure_ascii=False, indent=2))
