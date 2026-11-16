"""Offline M2 scorer with independent state, source, and native checks."""

import argparse
import base64
import hashlib
import json
from pathlib import Path
import sqlite3

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def score(case):
    case = Path(case)
    outcome = json.loads((case / "runner/outcome.json").read_text())
    if outcome["status"] != "OBSERVED":
        result = {"status": "UNKNOWN", "reason": "RUNTIME_TRACE_INCOMPLETE", "runtime": outcome["status"]}
        (case / "scorer/result.json").write_text(json.dumps(result, indent=2))
        return result
    profile = json.loads((case / "secure/native_profile.json").read_text())
    checks = []
    def check(name, ok):
        checks.append({"name": name, "pass": bool(ok)})
    with sqlite3.connect("file:" + str(case / "authority/authority.db") + "?mode=ro", uri=True) as con:
        version, sealed = con.execute("SELECT version,ciphertext FROM authority_state WHERE id=1").fetchone()
        events = [(v, op, json.loads(body)) for v, op, body in con.execute("SELECT version,operation,projection FROM authority_events ORDER BY version")]
    state = json.loads(AESGCM((case / "secure/authority.key").read_bytes()).decrypt(sealed[:12], sealed[12:], b"auth-lifecycle/online-state/schema-1"))
    check("atomic_version_sequence", [e[0] for e in events] == list(range(1, version + 1)))
    revoked = set()
    ordered = True
    for v, op, event in events:
        result = event["result"]
        if op == "revoke" and result["status"] == "LOCAL_REVOKE_COMMITTED":
            revoked.add(result["grant_id"])
        if op == "release" and result.get("send"):
            row = next(r for r in event["state"]["requests"] if r["rid"] == result["rid"])
            ordered &= row["origin"]["grant_id"] not in revoked and row["release_version"] == v
    check("no_new_release_after_local_revoke", ordered and outcome["A_after_ack"]["status"] == "REJECTED")
    sources = True
    for req in state["requests"].values():
        grant = state["grants"][req["origin"]["grant_id"]]
        sources &= all(req["origin"][k] == grant[k] for k in req["origin"])
        sources &= req["digest"] == hashlib.sha256(canonical({"caller": req["origin"]["caller"], "request": req["request"]})).hexdigest()
        if req["result_digest"]:
            envelope = {k: req[k] for k in ("rid", "digest", "origin", "attempt_id", "release_version")}
            envelope.update(material=req["result_material"], outcome="OK")
            sources &= req["result_digest"] == hashlib.sha256(canonical(envelope)).hexdigest()
            material = req["result_material"]
            sources &= material["expected_account"] == req["origin"]["account"] == profile["actor"]["id"]
            sources &= material["client"] == req["origin"]["audience"] == profile["client_id"]
    check("immutable_request_and_result_origin", sources)
    for grant in state["grants"].values():
        requests = [r for r in state["requests"].values() if r["origin"]["grant_id"] == grant["grant_id"]]
        reserved = sum(r["phase"] == "QUEUED" for r in requests)
        spent = sum(r["phase"] in {"DISPATCHED_UNKNOWN", "RESULT_AVAILABLE", "QUARANTINED", "DISPOSED"} for r in requests)
        check("budget_" + grant["task"], reserved == grant["reserved"] and spent == grant["spent"] and reserved + spent <= grant["limit"])
    initial = json.loads((case / "scorer/initial_native.json").read_text())
    final = json.loads((case / "scorer/final_native.json").read_text())
    check("initial_A_B_accepted", len(initial["rows"]) == 2 and all(r["accepted"] is True for r in initial["rows"]))
    known_a = [r for r in final["rows"] if r["rid"].startswith("A") and r["runner_has_result"]]
    check("known_A_userinfo_and_RT_rejected", bool(known_a) and all(r["accepted"] is False and r.get("refresh_rejected") is True for r in known_a))
    check("B_kept_before_account_cleanup", any(r["rid"] == "B0" and r["accepted"] is True for r in final["rows"])
          and outcome["B_continue"]["status"] == "RESULT_AVAILABLE")
    if outcome["scenario"] == "M2-02":
        req = state["requests"]["A1"]
        check("late_result_stays_A_g0", req["origin"]["task"] == "A" and req["origin"]["generation"] == "g0" and req["phase"] == "DISPOSED")
        before = outcome["visible_before_delivery"]
        check("held_result_not_controller_visible", next(r for r in before["requests"] if r["rid"] == "A1")["phase"] == "DISPATCHED_UNKNOWN")
    if outcome["scenario"] == "M2-03":
        req = state["requests"]["A1"]
        check("unknown_effect_not_laundered_or_retried", req["phase"] == "DISPATCHED_UNKNOWN" and req["result_material"] is None
              and outcome["lookup_unknown"]["status"] == "UNKNOWN")
        check("extra_native_child_truth_kept_separate", any(r["rid"] == "A1" and r["accepted"] is True and not r["runner_has_result"] for r in final["rows"]))
    if outcome["scenario"] == "M2-04":
        check("authority_outage_is_unknown", outcome["authority_outage"]["status"] == "UNKNOWN")
    logs = [json.loads(line) for line in (case / "provider/native_events.jsonl").read_text().splitlines()]
    received = [r for r in logs if r["event"] == "native_response_received"]
    check("one_native_perform_per_rid", len({r["rid"] for r in received}) == len(received))
    secrets = [profile["actor"]["password"], profile["client_secret"]]
    batch = Path(profile["batch"])
    http_key = batch / "secure/http.key"
    if http_key.exists():
        cipher = AESGCM(http_key.read_bytes())
        for path in (batch / "secure/http").glob("*.aes"):
            raw = path.read_bytes()
            record = json.loads(cipher.decrypt(raw[:12], raw[12:], b"native-http-v1"))
            if record["actor"] == profile["actor"]["name"]:
                body = record["response"].get("body")
                if isinstance(body, dict):
                    secrets += [body[k] for k in ("access_token", "refresh_token", "id_token") if body.get(k)]
    for req in state["requests"].values():
        if req["result_material"]:
            secrets += [x for k, x in req["result_material"]["native"].items() if k in {"access_token", "refresh_token", "id_token"} and x]
    for role in ("controller", "authority", "provider"):
        config = json.loads((case / "secure" / (role + ".json")).read_text())
        secrets += list(config["identities"].values())
    leaks = []
    for folder in ("runner", "controller", "control", "provider", "authority", "scorer"):
        for path in (case / folder).rglob("*"):
            if path.is_file() and path.suffix in {".json", ".jsonl", ".txt", ".stderr"} and path.name != "native_inbox.jsonl":
                raw = path.read_bytes()
                if any(s.encode() in raw for s in secrets):leaks.append(str(path.relative_to(case)))
    check("custody_public_logs_errors_and_management", not leaks)
    processes = [json.loads(line) for line in (case / "control/processes.jsonl").read_text().splitlines()]
    starts = [r for r in processes if r["event"] == "started"]
    exits = [r for r in processes if r["event"] == "terminated_and_waited"]
    check("all_case_processes_exited", sorted(r["child_pid"] for r in starts) == sorted(r["child_pid"] for r in exits))
    if outcome["scenario"] in {"M2-03", "M2-04"}:
        check("real_controller_restart", len([r for r in starts if r["role"] == "controller"]) == 2)
    units = {r["native_unit_ref"] for stage in (initial, final) for r in stage["native_units"]}
    strings = {r[k] for stage in (initial, final) for r in stage["rows"] for k in ("access_ref", "refresh_ref")}
    result = {"status": "PASS" if all(r["pass"] for r in checks) else "SAFETY_FAILURE", "checks": checks,
              "known_A_materials_checked": [r["rid"] for r in known_a], "leak_paths": leaks,
              "final_obligations": [r["rid"] for r in state["requests"].values() if r["phase"] in {"DISPATCHED_UNKNOWN", "QUARANTINED"}],
              "observed_native_units_G": len(units), "token_string_references": len(strings),
              "G_scope": "scorer-mapped native token record rows, union of initial/final samples",
              "all_descendants_closed": "UNPROVED_OUTSIDE_FINITE_REGISTERED_TRAJECTORY",
              "external_effect_termination": "USERINFO_ACCEPTANCE_ONLY",
              "accesses": ["read-only authority SQLite and decryption key", "initial/final independent native observations", "provider metadata and process logs"],
              "cryptography_research": "FROZEN"}
    (case / "scorer/result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser();parser.add_argument("--case", required=True)
    args = parser.parse_args()
    result = score(args.case)
    print(json.dumps({"status": result["status"]}))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
