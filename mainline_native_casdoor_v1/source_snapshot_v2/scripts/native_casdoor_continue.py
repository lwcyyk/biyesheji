"""Continue the original unsampled M2-04 slot after a verified scorer false alarm.

This uses the original four-account authorization and persistent HTTP budget.
It never repeats a sampled account/trajectory and preserves the original verdict.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from auth_lifecycle.online_state.native_acceptance import create_actor, run_case, cleanup_actor
from auth_lifecycle.online_state.native_http import NativeHTTP
from auth_lifecycle.online_state.protocol import write_json


def validate_continuation(batch, review, authorization_id):
    prior = json.loads((batch / "RESULTS.json").read_text())
    gate = json.loads(review.read_text())
    if prior["authorization_id"] != authorization_id:
        raise ValueError("ORIGINAL_AUTHORIZATION_REQUIRED")
    if [r["scenario"] for r in prior["records"] if r["status"] == "NOT_RUN"] != ["M2-04"]:
        raise ValueError("ONLY_ORIGINAL_UNSAMPLED_SLOT_ALLOWED")
    if (gate["eligible_unexecuted_slot"] != "M2-04" or gate["failed_original_checks"] != ["real_controller_restart"]
            or gate["corrected_scoring"] != "PASS" or not gate["raw_input_unchanged"]):
        raise ValueError("VERIFIED_SCORER_CORRECTION_REQUIRED")
    original_case = batch / "M2-03"
    for item in gate["original_case_file_hashes"]:
        if hashlib.sha256((original_case / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("ORIGINAL_EVIDENCE_CHANGED")
    scorer = Path(__file__).with_name("score_native_casdoor.py")
    if hashlib.sha256(scorer.read_bytes()).hexdigest() != gate["corrected_scorer_sha256"]:
        raise ValueError("REVIEWED_SCORER_CHANGED")
    return json.loads((batch / "BUDGET_AND_AUTHORIZATION.json").read_text())["account_names"][3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--review", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--authorization-id", required=True)
    args = parser.parse_args()
    batch, output, review = Path(args.batch), Path(args.out), Path(args.review)
    name = validate_continuation(batch, review, args.authorization_id)
    output.mkdir(parents=True, exist_ok=False)
    with (batch / "secure/M2-04_continuation_claim.json").open("x") as stream:
        stream.write(json.dumps({"authorization_id": args.authorization_id, "account": name, "review": str(review)}))
    template = json.loads((batch / "secure/profile_template.json").read_text())
    environment = json.loads((batch / "ENVIRONMENT_LOCK.json").read_text())
    admin = NativeHTTP(batch, "environment", cookies=True, enabled=True)
    runtime = Path(__file__).resolve().parents[1] / ".runtime/l1"
    credentials = json.loads((runtime / "secrets.json").read_text())
    login = admin.call("admin_login", payload={"type": "login", "organization": "built-in", "username": "admin",
        "password": credentials["casdoor_password"], "application": "app-built-in", "autoSignin": True})
    if login["body"].get("status") != "ok":raise RuntimeError("ENVIRONMENT_LOGIN_FAILED")
    app = admin.call("application")["body"].get("data", {})
    if not all(app.get(k) == v for k, v in environment["application"].items()):
        raise RuntimeError("ENVIRONMENT_APPLICATION_CHANGED")
    if admin.call("jwks")["body"] != template["jwks"]:
        raise RuntimeError("ENVIRONMENT_SIGNING_KEYS_CHANGED")
    binary = runtime / "dist/casdoor/casdoor.exe"
    if hashlib.sha256(binary.read_bytes()).hexdigest() != environment["binary_sha256"]:
        raise RuntimeError("ENVIRONMENT_BINARY_CHANGED")
    files = list((Path(__file__).resolve().parents[1] / "src/auth_lifecycle/online_state").glob("*"))
    files += list(Path(__file__).parent.glob("*native_casdoor*.py"))
    write_json(output / "SOURCE_LOCK.json", {"files": [{"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.is_file()],
        "original_authorization": args.authorization_id, "original_budget": str(batch / "native_budget.db"),
        "selected_slot": "M2-04", "resampled_slots": 0, "review": str(review)})
    actor = None
    root = output / "M2-04"
    try:
        actor = create_actor(admin, batch, name)
        profile = {**template, "actor": actor, "durable_inbox": True, "hold_refresh": False}
        outcome = run_case(batch, root, profile, "M2-04")
        with (root / "scorer/console.txt").open("wb") as stream:
            subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("score_native_casdoor.py")),
                            "--case", str(root)], stdout=stream, stderr=stream, timeout=30)
        result = json.loads((root / "scorer/result.json").read_text())
        write_json(output / "RESULTS.json", {"scenario": "M2-04", "status": result["status"],
                   "runtime_status": outcome["status"], "resampled_slots": 0, "authorization_id": args.authorization_id})
    finally:
        if actor is not None:
            cleanup_actor(admin, batch, {**template, "actor": actor}, root)
        elif (batch / "secure" / (name + ".json")).exists():
            intent = json.loads((batch / "secure" / (name + ".json")).read_text())
            admin.category = "cleanup"
            row = admin.call("get_user", actor=name)["body"].get("data")
            if row and intent.get("precheck_absent") and row.get("name") == name and row.get("owner") == "l1-study":
                intent["id"] = row["id"]
                cleanup_actor(admin, batch, {**template, "actor": intent}, root)
    print((output / "RESULTS.json").read_text())


if __name__ == "__main__":
    main()
