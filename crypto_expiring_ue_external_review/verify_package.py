"""Read-only external-package integrity and claim-status checks.

No network calls, external communication, or candidate protocol implementation.
"""
import hashlib
import json
import re
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent


def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


checks = []
for row in read(ROOT / "INPUT_LOCK.json")["files"]:
    p = Path(row["path"])
    checks.append({"kind": "historical_input_hash", "path": str(p),
                   "pass": p.is_file() and sha(p) == row["sha256"]})

for row in read(ROOT / "ARTIFACT_MANIFEST.json")["files"]:
    p = ROOT / row["path"]
    checks.append({"kind": "new_artifact_hash", "path": row["path"],
                   "pass": p.is_file() and sha(p) == row["sha256"]})

reg = read(ROOT / "SOURCE_AND_RESPONSE_REGISTER.json")
upd = read(ROOT / "PREMISE_UPDATE.json")
before = read(upd["prior_matrix"]["path"])
before_by_id = {p["id"]: p for p in before["premises"]}
for row in upd["updates"]:
    checks.append({"kind": "premise_preservation", "id": row["id"],
                   "pass": row["before_actual_author_version"] == before_by_id[row["id"]]["status"]
                   == row["after_actual_author_version"] and row["changed"] is False})
checks.append({"kind": "scope", "id": "all_seven_premises",
               "pass": {p["id"] for p in upd["updates"]} == {f"P{i}" for i in range(1, 8)}})
checks.append({"kind": "scope", "id": "waiting_without_overclaim",
               "pass": upd["state"] == "WAITING_FOR_EXTERNAL_SPEC" and
               upd["concrete_author_version_attack"] is False and
               upd["technical_premise_changes"] == []})

package = (ROOT / "EXTERNAL_REVIEW_PACKAGE.md").read_text(encoding="utf-8")
body = package.split("<!-- EMAIL_BODY_BEGIN -->", 1)[1].split("<!-- EMAIL_BODY_END -->", 1)[0].strip()
checks.append({"kind": "communication_draft", "id": "body_matches_package_and_hash",
               "pass": (ROOT / "INQUIRY_BODY.txt").read_bytes() == (body + "\n").encode("utf-8")
               and sha(ROOT / "INQUIRY_BODY.txt") == reg["communication"]["inquiry_body_sha256"]})
checks.append({"kind": "communication_draft", "id": "one_page_length_target",
               "pass": len(re.findall(r"\S+", body)) == reg["communication"]["body_word_count_whitespace"] <= 350})
checks.append({"kind": "communication_draft", "id": "package_version_bound",
               "pass": sha(ROOT / "EXTERNAL_REVIEW_PACKAGE.md") == reg["communication"]["annex_package_sha256"]})
checks.append({"kind": "communication_draft", "id": "unsent_and_unapproved",
               "pass": reg["communication"]["messages_sent"] == 0 and
               reg["communication"]["recipients_approved"] is False and
               reg["communication"]["final_body_approved"] is False})

for source in reg["sources"]:
    for field in ["file", "raw_download"]:
        f = source.get(field)
        if f:
            checks.append({"kind": "source_bytes", "id": source["id"] + "/" + field,
                           "pass": Path(f["path"]).is_file() and sha(f["path"]) == f["sha256"]})

slides = ROOT / "sources/author_slides.pdf"
checks.append({"kind": "source_format", "id": "slides_real_PDF_42_pages",
               "pass": slides.read_bytes().startswith(b"%PDF") and len(PdfReader(str(slides)).pages) == 42})
for filename in ["eprint_latest.bin", "eprint_versions.bin"]:
    checks.append({"kind": "source_format", "id": filename + "_not_misreported_as_PDF",
                   "pass": not (ROOT / "sources" / filename).read_bytes().startswith(b"%PDF")})
checks.append({"kind": "declared_scope", "id": "zero_native_zero_candidate_implementation",
               "pass": upd["native_AS_RP_requests"] == reg["native_AS_RP_requests"] == 0 and
               upd["candidate_protocol_implementation"] == reg["candidate_protocol_implementation"] == 0})

print(json.dumps({
    "schema": "EE-R-EXTERNAL-VALIDATION-1", "read_only": True,
    "checks": checks,
    "counts": {"total": len(checks), "passed": sum(x["pass"] for x in checks),
               "failed": sum(not x["pass"] for x in checks)},
    "all_pass": all(x["pass"] for x in checks),
    "proves_cryptographic_security": False,
    "waiting_evidence": ["Version-specific full expiry binding", "Typed complete correctness trace", "Calibrated author game and Lemma5"],
}, ensure_ascii=False, indent=2))
