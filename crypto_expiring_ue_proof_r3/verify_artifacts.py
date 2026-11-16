"""Read-only EE-R-PA3 provenance and scope checks; no security-proof claim."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


checks = []
for row in read(ROOT / "STARTING_POINT_LOCK.json")["files"]:
    p = Path(row["path"])
    checks.append({"kind": "historical_hash", "path": str(p),
                   "pass": p.is_file() and sha(p) == row["sha256"]})

for row in read(ROOT / "ARTIFACT_MANIFEST.json")["files"]:
    p = ROOT / row["path"]
    checks.append({"kind": "new_artifact_hash", "path": row["path"],
                   "pass": p.is_file() and sha(p) == row["sha256"]})

math = read(ROOT / "FINITE_MATH_RESULTS.json")
for row in math["new_checks"]:
    checks.append({"kind": "finite_new_math", "id": row["id"], "pass": row["pass"]})
for row in math["R2_reuse"]["raw_result"]["checks"]:
    checks.append({"kind": "finite_inherited_math", "id": row["id"], "pass": row["pass"]})

v = read(ROOT / "VERDICT.json")
matrix = read(ROOT / "ATTACK_PREMISE_MATRIX.json")
by_id = {row["id"]: row for row in matrix["premises"]}
checks.append({"kind": "scope", "id": "seven_premises",
               "pass": set(by_id) == {f"P{i}" for i in range(1, 8)}})
checks.append({"kind": "scope", "id": "branch_C_source_unresolved",
               "pass": v["branch"] == "C" and v["primary_result"] == "SOURCE_UNRESOLVED"})
checks.append({"kind": "scope", "id": "separate_body_and_actual_construction",
               "pass": by_id["P2"]["publication_literal"] == "CONFIRMED" and
               by_id["P2"]["status"] == "SOURCE_UNRESOLVED" and
               by_id["P6"]["status"] == "CONFIRMED"})
checks.append({"kind": "scope", "id": "no_overpromoted_attack",
               "pass": v["R2_EXP"]["concrete_author_version_attack_established"] is False and
               matrix["all_actual_author_attack_premises_confirmed"] is False})
checks.append({"kind": "scope", "id": "paper_only",
               "pass": v["candidate_protocol_implementation"] == 0 and
               v["native_AS_RP_requests"] == 0 and v["author_contact_sent"] is False})
for row in matrix["premises"]:
    checks.append({"kind": "premise_status", "id": row["id"],
                   "pass": row["status"] in matrix["status_values"]})

pre = read(ROOT / "sources/TCC_PDF_PREFLIGHT.json")
checks.append({"kind": "PDF_structure_only", "id": "TCC31",
               "pass": pre["verdict"] == "PASS" and pre["reader_page_count"] == 31})
old = read(ROOT / "R2_INTEGRITY_RECHECK.json")
checks.append({"kind": "R2_integrity_recheck", "id": "original_check_denominator_retained",
               "pass": old["all_pass"] is True and old["counts"]["total"] == 63})
print(json.dumps({
    "schema": "EE-R-PA3-VALIDATION-1", "read_only": True,
    "checks": checks,
    "counts": {"total": len(checks), "pass": sum(x["pass"] for x in checks),
               "fail": sum(not x["pass"] for x in checks)},
    "all_pass": all(x["pass"] for x in checks),
    "proves_cryptographic_security": False,
    "missing_evidence_remains_visible": [
        "Version-confirmed author full construction and historical version",
        "Complete expiry encoding, metadata validation and typed Gen-to-K3 correctness",
        "Original full-version security game mapping",
        "Author or external peer confirmation and priority review",
    ],
}, ensure_ascii=False, indent=2))
