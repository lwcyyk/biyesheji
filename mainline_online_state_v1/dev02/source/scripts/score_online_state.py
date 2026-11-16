"""Independent offline scorer: no imports from auth_lifecycle or its runtime."""

import argparse
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode()


def lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def score(root):
    root = Path(root)
    accesses = []
    checks = []

    def check(name, condition):
        checks.append({"name": name, "pass": bool(condition)})

    database = root / "authority" / "authority.db"
    accesses.append({"path": str(database), "mode": "sqlite_read_only"})
    with sqlite3.connect("file:" + str(database) + "?mode=ro", uri=True) as connection:
        version, sealed = connection.execute("SELECT version,ciphertext FROM authority_state WHERE id=1").fetchone()
        events = [{"version": v, "operation": op, **json.loads(raw)} for v, op, raw in
                  connection.execute("SELECT version,operation,projection FROM authority_events ORDER BY version")]
    key_path = root / "secure" / "authority.key"
    accesses.append({"path": str(key_path), "mode": "scorer_privileged_key_read"})
    state = json.loads(AESGCM(key_path.read_bytes()).decrypt(sealed[:12], sealed[12:],
                                                          b"auth-lifecycle/online-state/schema-1"))
    truth_path = root / "provider" / "truth.jsonl"
    accesses.append({"path": str(truth_path), "mode": "scorer_only_effect_truth"})
    effects = [e for e in lines(truth_path) if e["event"] == "effect"]
    outcome = json.loads((root / "runner" / "outcome.json").read_text())
    check("committed_event_sequence", [e["version"] for e in events] == list(range(1, version + 1)))
    releases = {}
    revoked = set()
    release_order_valid = True
    for event in events:
        result = event["result"]
        if event["operation"] == "revoke" and result["status"] == "LOCAL_REVOKE_COMMITTED":
            revoked.add(result["grant_id"])
        if event["operation"] == "release" and result.get("send"):
            req = next(r for r in event["state"]["requests"] if r["rid"] == result["rid"])
            release_order_valid &= req["origin"]["grant_id"] not in revoked
            release_order_valid &= req["release_version"] == event["version"]
            releases[req["attempt_id"]] = req
    check("no_new_release_after_revoke_commit", release_order_valid)
    check("every_provider_effect_has_matching_durable_release", all(
        e["attempt_id"] in releases and all(e[k] == releases[e["attempt_id"]][k]
        for k in ("rid", "digest", "origin", "release_version")) for e in effects))
    counts = Counter(e["rid"] for e in effects)
    check("no_automatic_unknown_request_retransmission", all(n <= 1 for n in counts.values()))
    for grant in state["grants"].values():
        requests = [r for r in state["requests"].values() if r["origin"]["grant_id"] == grant["grant_id"]]
        reserved = sum(r["phase"] == "QUEUED" for r in requests)
        spent = sum(r["phase"] in {"DISPATCHED_UNKNOWN", "RESULT_AVAILABLE", "QUARANTINED"} for r in requests)
        check("budget_" + grant["task"], reserved == grant["reserved"] and spent == grant["spent"]
              and reserved + spent <= grant["limit"])
    source_correct = True
    result_correct = True
    for req in state["requests"].values():
        grant = state["grants"][req["origin"]["grant_id"]]
        source_correct &= all(req["origin"][k] == grant[k] for k in req["origin"])
        original = {"caller": req["origin"]["caller"], "request": req["request"]}
        source_correct &= hashlib.sha256(canonical(original)).hexdigest() == req["digest"]
        if req["result_digest"]:
            result = {k: req[k] for k in ("rid", "digest", "origin", "attempt_id", "release_version")}
            result.update(material=req["result_material"], outcome="OK")
            result_correct &= hashlib.sha256(canonical(result)).hexdigest() == req["result_digest"]
    check("request_source_and_digest", source_correct)
    check("result_registration_atomic_binding", result_correct)
    a = next(g for g in state["grants"].values() if g["task"] == "A")
    b_requests = [r for r in state["requests"].values() if r["origin"]["task"] == "B"]
    check("A_revoked_and_new_admission_rejected", not a["active"] and
          outcome.get("post_ack_A", {}).get("status") == "REJECTED")
    check("B_completed_after_recovery", any(r["phase"] == "RESULT_AVAILABLE" for r in b_requests)
          and outcome.get("B_result", {}).get("status") == "RESULT_AVAILABLE")
    a_request = state["requests"].get("A1")
    if a_request and a_request["result_digest"]:
        check("late_A_is_quarantined_under_original_generation", a_request["phase"] == "QUARANTINED"
              and a_request["origin"]["generation"] == "g0")
    expected_effect = outcome["scenario"] not in {"pending_before_commit", "release_before_send"}
    check("scenario_A_effect_count", counts.get("A1", 0) == int(expected_effect))
    if outcome["scenario"] == "release_before_send":
        check("unresolved_release_retained", a_request is not None and a_request["phase"] == "DISPATCHED_UNKNOWN")
    if outcome["scenario"] == "authority_outage":
        check("authority_outage_returns_unknown", outcome.get("outage_recover", {}).get("status") == "UNKNOWN")
    process_events = lines(root / "control" / "processes.jsonl")
    active = {}
    ordered = True
    controller_starts = 0
    for event in process_events:
        if event["event"] == "started":
            ordered &= event["role"] not in active
            active[event["role"]] = event["child_pid"]
            controller_starts += int(event["role"] == "controller")
        elif event["event"] == "terminated_and_waited":
            ordered &= active.pop(event["role"], None) == event["child_pid"]
    check("single_active_process_and_cleanup", ordered and not active)
    if outcome["scenario"] != "normal":
        check("real_controller_restart", controller_starts >= 2)
    operation_rows = lines(root / "authority" / "database_ops.jsonl")
    check("database_budget_100", len(operation_rows) <= 100)
    check("trace_window_60_seconds", outcome["elapsed_seconds"] <= 60)
    secrets_to_scan = [g["material"] for g in state["grants"].values()]
    secrets_to_scan += [r["result_material"] for r in state["requests"].values() if r["result_material"]]
    for role in ("authority", "controller", "provider"):
        cfg = json.loads((root / "secure" / (role + ".json")).read_text())
        secrets_to_scan.extend(cfg["identities"].values())
    secrets_to_scan.append("synthetic_debug_secret_do_not_export")
    leaks = []
    for folder in ("controller", "runner", "control", "scorer"):
        for path in (root / folder).rglob("*"):
            if path.is_file():
                raw = path.read_bytes()
                if any(value.encode() in raw for value in secrets_to_scan):
                    leaks.append(str(path.relative_to(root)))
    event_bytes = canonical(events)
    if any(value.encode() in event_bytes for value in secrets_to_scan):
        leaks.append("authority_events_projection")
    check("no_secret_in_logs_exceptions_or_management_projection", not leaks)
    rpc = lines(root / "runner" / "rpc.jsonl")
    recovery_rpc = [r for r in lines(root / "controller" / "events.jsonl")
                    if r["event"] == "rpc" and r["operation"] == "recover"]
    budget_checks = {"database_budget_100", "trace_window_60_seconds"}
    failed = [c["name"] for c in checks if not c["pass"]]
    verdict = "PASS"
    if any(name not in budget_checks for name in failed):
        verdict = "SAFETY_FAILURE"
    elif failed:
        verdict = "INCONCLUSIVE"
    result = {
        "status": verdict,
        "scenario": outcome["scenario"], "checks": checks, "leak_paths": leaks,
        "metrics": {"authority_sql_statements_including_setup": len(operation_rows),
                    "committed_transactions": len(events),
                    "conflict_decisions": sum(e["result"]["status"] == "CONFLICT" for e in events),
                    "sqlite_retry_count": 0,
                    "bound_value_bytes_proxy": sum(r.get("bound_value_bytes", 0) for r in operation_rows),
                    "logical_state_snapshot_bytes_written": sum(e["logical_state_bytes"] for e in events),
                    "runner_rpc_request_json_bytes": sum(r.get("request_json_bytes", 0) for r in rpc),
                    "runner_rpc_response_json_bytes": sum(r.get("response_json_bytes", 0) for r in rpc),
                    "recovery_response_json_bytes": sum(r.get("response_json_bytes", 0) for r in recovery_rpc),
                    "authority_db_file_bytes": database.stat().st_size,
                    "authority_wal_file_bytes_at_score": (database.with_name(database.name + "-wal")).stat().st_size
                       if database.with_name(database.name + "-wal").exists() else 0,
                    "physical_WAL_bytes_written": None, "fsync_count": None,
                    "B_after_recovery_seconds": outcome.get("B_after_recovery_seconds"),
                    "trace_seconds": outcome["elapsed_seconds"], "provider_effects": len(effects)},
        "final_obligations": [r["rid"] for r in state["requests"].values()
                              if r["phase"] in {"DISPATCHED_UNKNOWN", "QUARANTINED"}],
        "native_requests": 0, "scope": "finite local process/cache fault trace",
        "accesses": accesses,
    }
    (root / "scorer" / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    result = score(args.root)
    print(json.dumps({"status": result["status"], "scenario": result["scenario"]}))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
