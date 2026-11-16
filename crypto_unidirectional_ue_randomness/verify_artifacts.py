"""Read-only integrity/scope checks; this script is not a cryptographic proof."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


checks = []
for row in read(ROOT / "INPUT_LOCK.json")["files"]:
    p = Path(row["path"])
    checks.append({"kind": "historical_hash", "path": str(p),
                   "pass": p.is_file() and sha(p) == row["sha256"]})
for row in read(ROOT / "ARTIFACT_MANIFEST.json")["files"]:
    p = ROOT / row["path"]
    checks.append({"kind": "new_hash", "path": row["path"],
                   "pass": p.is_file() and sha(p) == row["sha256"]})

for row in read(ROOT / "SOURCE_REGISTER.json")["sources"]:
    p = Path(row["source"]["path"])
    checks.append({"kind": "source", "id": row["id"],
                   "pass": p.is_file() and sha(p) == row["source"]["sha256"] and
                   p.read_bytes().startswith(b"%PDF")})
for row in read(ROOT / "MATHEMATICAL_CHECKS.json")["checks"]:
    checks.append({"kind": "finite_math", "id": row["id"], "pass": row["pass"]})
v = read(ROOT / "VERDICT.json")
checks.append({"kind": "scope", "id": "fixed_profile",
               "pass": v["game"] == "UNI-R-CPA-1" and v["main_security"]["challenge_epoch"] == 2
               and v["main_security"]["new_beyond_profile_adaptive_corruption_claim"] is False})
checks.append({"kind": "scope", "id": "only_two_deep_objects",
               "pass": v["specification_status"]["deeply_audited_concrete_UE_objects"] == 2})
checks.append({"kind": "scope", "id": "not_a_resource_separation",
               "pass": v["implementation_gate"]["strict_resource_separation_instance"] is False and
               v["implementation_gate"]["candidate_protocol_implementation"] == 0})
checks.append({"kind": "scope", "id": "no_native_or_external_contact",
               "pass": v["external_contact"] == v["email_sent"] == v["native_AS_RP_requests"] == 0})
checks.append({"kind": "scope", "id": "separate_frodo_parameter_uncertainty",
               "pass": v["FRODO_FI"]["unsatisfied_sufficient_condition_treated_as_correctness_attack"] is False})
checks.append({"kind": "scope", "id": "sampling_failure_explicit",
               "pass": "epsilon_samp" in v["main_security"]["standard_DDH_bound"]})
for ident in ["frodo", "rc26", "gp23", "mpw23"]:
    p = read(ROOT / "sources" / (ident + "_preflight.json"))
    checks.append({"kind": "PDF_structure_only", "id": ident, "pass": p["verdict"] == "PASS"})
for name in ["gp23_extended.bin", "mpw23_extended.bin"]:
    checks.append({"kind": "missing_fulltext_not_promoted", "id": name,
                   "pass": not (ROOT / "sources" / name).read_bytes().startswith(b"%PDF")})
print(json.dumps({
    "schema": "UNI-R-OFFLINE-VALIDATION-1", "read_only": True,
    "checks": checks,
    "counts": {"total": len(checks), "passed": sum(x["pass"] for x in checks),
               "failed": sum(not x["pass"] for x in checks)},
    "all_pass": all(x["pass"] for x in checks),
    "proves_general_security": False,
    "independent_external_review": False,
}, ensure_ascii=False, indent=2))
