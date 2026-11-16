"""Independent M5 offline rules. Does not import the controller or its scorer."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def read(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def canon(value): return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def score_scene(root, filename):
    root = Path(root)
    scene = read(root / filename)
    number = int(scene["scenario"].split("-")[1])
    checks, accesses = [], []

    def check(name, condition, security=True):
        checks.append({"name": name, "pass": bool(condition), "security": security})

    def result(row): return row.get("result", {})
    def denied(row): return row.get("reached") is True and result(row).get("status") == "REJECTED"
    def success(row): return row.get("reached") is True and result(row).get("status") == "RESULT_AVAILABLE"
    def os_denied(rows, expected):
        return len(rows) == expected and all(r.get("allowed") is False and r.get("winerror") == 5 for r in rows)
    def os_check(name, rows, expected):
        check(name, os_denied(rows, expected), any(r.get("allowed") is True for r in rows))
    def service_check(name, rows, expected):
        check(name, len(rows) == expected and all(denied(r) for r in rows),
              any(r.get("reached") and not denied(r) for r in rows))

    db = root / "trusted" / "authority" / "authority.db"
    key = root / "trusted" / "secure" / "authority.key"
    accesses += [{"path": str(db), "mode": "read_only_sqlite"}, {"path": str(key), "mode": "scorer_only_decryption_key"}]
    with sqlite3.connect("file:" + str(db) + "?mode=ro", uri=True) as c:
        version, encrypted = c.execute("SELECT version,ciphertext FROM authority_state WHERE id=1").fetchone()
        events = [{"version": v, "operation": op, **json.loads(p)} for v, op, p in
                  c.execute("SELECT version,operation,projection FROM authority_events ORDER BY version")]
    state = json.loads(AESGCM(key.read_bytes()).decrypt(encrypted[:12], encrypted[12:], b"auth-lifecycle/online-state/schema-1"))
    lock = read(root / "ENVIRONMENT_LOCK.json")
    controls = read(root / "SETUP_CONTROLS.json")
    for task in ("A", "B"):
        token = controls["identities"][task]["token"]
        check(task + "_primary_low_restricted_token", token["token_type"] == 1 and token["elevated"] == 0
              and token["integrity"] == "S-1-16-4096" and token["user"] == lock["owner_sid"]
              and lock["restricting_sids"][task] in {s["sid"] for s in token["restricting_sids"]})
        check(task + "_own_workdir_positive", controls["identities"][task]["own_read_write"], False)
    os_check("runtime_cannot_read_scorer_private_key", controls["runtime_scorer_probe"], 1)
    check("all_registered_targets_exist", all(x["exists"] for x in controls["targets"].values()), False)
    check("scene_within_observation_window", scene["elapsed_seconds"] <= 60, False)
    check("no_native_requests", lock["native_requests"] == 0)
    check("atomic_event_sequence", [e["version"] for e in events] == list(range(1, version + 1)))
    revoked, releases = set(), {}
    order_valid = True
    for event in events:
        r = event["result"]
        if event["operation"] == "revoke" and r["status"] == "LOCAL_REVOKE_COMMITTED": revoked.add(r["grant_id"])
        if event["operation"] == "release" and r.get("send"):
            req = next(x for x in event["state"]["requests"] if x["rid"] == r["rid"])
            order_valid &= req["origin"]["grant_id"] not in revoked
            order_valid &= req["release_version"] == event["version"]
            releases[req["attempt_id"]] = req
    check("no_new_release_after_withdraw_commit", order_valid)
    truth = root / "trusted" / "provider" / "truth.jsonl"
    effects = [json.loads(s) for s in truth.read_text().splitlines()] if truth.exists() else []
    accesses.append({"path": str(truth), "mode": "independent_provider_truth"})
    check("effects_bind_durable_original_release", all(e["attempt_id"] in releases and all(
        e[k] == releases[e["attempt_id"]][k] for k in ("rid", "digest", "origin", "release_version")) for e in effects))
    check("no_unknown_automatic_resend", all(n == 1 for n in Counter(e["rid"] for e in effects).values()))
    for grant in state["grants"].values():
        reqs = [r for r in state["requests"].values() if r["origin"]["grant_id"] == grant["grant_id"]]
        reserved = sum(r["phase"] == "QUEUED" for r in reqs)
        spent = sum(r["attempt_id"] is not None for r in reqs)
        check("budget_" + grant["task"], (reserved, spent) == (grant["reserved"], grant["spent"]) and spent + reserved <= grant["limit"])
        check("request_provenance_" + grant["task"], all(all(r["origin"][k] == grant[k] for k in r["origin"])
            and hashlib.sha256(canon({"caller": r["origin"]["caller"], "request": r["request"]})).hexdigest() == r["digest"] for r in reqs))

    before, after = scene["before"], scene["after"]
    if number in {1, 2}:
        check("legal_call_succeeded", success(scene["call"]), False)
        check("positive_workspace", scene["positive"]["own_read_write"], False)
    elif number == 3:
        os_check("all_nine_secret_targets_denied_by_OS", scene["attacks"], 9)
    elif number == 4:
        os_check("four_trusted_writes_denied_by_OS", scene["attacks"], 4)
        os_check("four_owner_DACL_rewrites_denied_by_OS", scene.get("acl_attacks", []), 4)
    elif number == 5:
        attack = scene["attacks"]
        rows = attack["processes"]
        sensitive = [r for r in rows if r["operation"] != "QUERY_LIMITED"]
        check("registered_processes_exist_and_sensitive_access_denied", len(sensitive) == 18 and all(
            r["allowed"] is False and r["winerror"] == 5 for r in sensitive))
        check("no_trusted_primary_token_duplication", all(not r.get("token_duplicate_assign", {}).get("allowed") for r in rows))
        check("agent_cannot_raise_own_integrity", attack.get("raise_own_integrity", {}).get("allowed") is False)
        canary = attack.get("canary_handle", {})
        check("parent_canary_not_inherited", not canary.get("resolved_path", "") or
              "handle_canary.bin" not in canary["resolved_path"])
        expected_env = {"SYSTEMROOT", "TEMP", "TMP", "PYTHONUTF8", "PYTHONDONTWRITEBYTECODE", "LC_CTYPE"}
        check("agent_environment_allowlist", {k.upper() for k in scene["agent_environment"]["environment"]} <= expected_env)
    elif number == 6:
        service_check("all_eleven_role_attacks_denied_at_reached_services", scene["attacks"], 11)
        check("invalid_capability_denied", denied(scene["wrong_capability"]))
        status = result(scene["status"])
        check("A_status_does_not_expose_B_state", scene["status"].get("reached") and status.get("status") == "RECOVERED"
              and all(g["caller"] == "agentA" for g in status["approvals"])
              and all(r["origin"]["caller"] == "agentA" for r in status["requests"]))
        check("recovery_role_positive", scene["recovery_positive"].get("status") == "RECOVERED", False)
        check("management_recovery_role_separation", scene["management_cannot_recover"].get("status") == "REJECTED"
              and scene["recovery_cannot_grant"].get("status") == "REJECTED")
    elif number == 7:
        service_check("stolen_B_handle_and_all_binding_tampering_denied", scene["attacks"], 6)
        check("B_handle_still_works_for_B", success(scene["B_positive"]), False)
    elif number == 8:
        check("first_call_completed", success(scene["initial"]), False)
        check("identical_replay_duplicate", result(scene["duplicate"]).get("status") == "DUPLICATE")
        check("conflicting_body_rejected", result(scene["conflict"]).get("status") == "CONFLICT")
        check("replay_spends_once", sum(e["rid"] == "own_replay" for e in effects) == 1
              and next(g for g in after["approvals"] if g["task"] == "A")["spent"] ==
              next(g for g in before["approvals"] if g["task"] == "A")["spent"] + 1)
    elif number == 9:
        check("four_parse_errors_rejected", len(scene["parse"]) == 4 and all(denied(x) for x in scene["parse"]))
        check("permission_error_rejected", denied(scene["permission"]))
        check("provider_unavailable_preserves_unknown", result(scene["provider_error"]).get("status") == "UNKNOWN"
              and state["requests"].get("A_provider_unknown", {}).get("phase") == "DISPATCHED_UNKNOWN")
        check("provider_recovery_positive", success(scene["provider_positive"]), False)
    elif number == 10:
        check("durable_revoke_ACK", scene["ack"].get("status") == "LOCAL_REVOKE_COMMITTED")
        check("old_handle_capability_denied", denied(scene["attack"]))
        check("B_after_revoke_positive", success(scene["B_positive"]), False)
    elif number == 11:
        check("new_controller_after_old_exit", scene["old_controller_pid"] != scene["new_controller_pid"])
        check("malicious_agent_remained_alive", scene["A_still_alive"], False)
        check("old_cache_cannot_restore_A_authority", denied(scene["attack"]))
        check("B_after_controller_recovery_positive", success(scene["B_positive"]), False)
    elif number == 12:
        check("both_requests_unknown_when_authority_down", all(result(scene[k]).get("status") == "UNKNOWN"
              for k in ("A_during_outage", "B_during_outage")))
        unchanged = scene["after_outage_before_resume"]
        check("outage_no_spend_or_obligation_loss", unchanged["approvals"] == before["approvals"]
              and unchanged["requests"] == before["requests"] and unchanged["obligations"] == before["obligations"])
        check("recovery_role_positive", scene["recovery_positive"].get("status") == "RECOVERED", False)
        check("B_final_recovery_positive", success(scene["B_positive"]), False)

    # Material/credential check on actual responses, exception projections,
    # transport and security logs. Expected full values never enter runtime APIs.
    expected_path = root / "scorer_private" / "expected.json"
    expected = read(expected_path)
    accesses.append({"path": str(expected_path), "mode": "scorer_private_expected_values"})
    forbidden = [s.encode() for s in expected["markers"].values()]
    for role, values in expected["capabilities"].items():
        forbidden += [s.encode() for s in values.values()]
    forbidden += [b"synthetic_result_", b"synthetic_debug_secret_do_not_export"]
    files = [root / filename]
    for d in (root / "trusted" / "authority", root / "trusted" / "controller", root / "trusted" / "provider"):
        files += list(d.glob("*.jsonl"))
    files = [p for p in files if p.name != "encrypted_results.jsonl"]
    leaks = []
    for p in files:
        raw = p.read_bytes()
        for secret in forbidden:
            if secret and secret in raw: leaks.append({"path": str(p), "secret_sha256": hashlib.sha256(secret).hexdigest()})
    check("responses_errors_and_logs_contain_no_forbidden_secrets", not leaks)
    # Strict top-level response whitelist; nested projections are checked against
    # full secret values above and original-provenance rules.
    def responses(value):
        if isinstance(value, dict):
            if "reached" in value and "result" in value: yield value["result"]
            for child in value.values(): yield from responses(child)
        elif isinstance(value, list):
            for child in value: yield from responses(child)
    allowed = {"status", "reason", "version", "rid", "digest", "origin", "phase", "attempt_id", "release_version",
               "approvals", "requests", "obligations", "disposals"}
    check("agent_response_top_level_whitelist", all(set(r) <= allowed for r in responses(scene)))
    failures = [c for c in checks if not c["pass"]]
    status = "FAIL_SECURITY" if any(c["security"] for c in failures) else "INCONCLUSIVE" if failures else "PASS"
    return {"scenario": scene["scenario"], "status": status, "checks": checks, "leaks": leaks,
            "scorer_access_log": accesses, "authority_version": version, "effects": len(effects)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--scene")
    args = parser.parse_args()
    root = Path(args.root)
    if args.scene:
        result = score_scene(root, args.scene)
    else:
        results = []
        for i in range(1, 13):
            filename = f"M5-{i:02d}.json"
            results.append(score_scene(root, filename) if (root / filename).exists() else
                           {"scenario": f"M5-{i:02d}", "status": "NOT_RUN"})
        result = {"planned": 12, "counts": dict(Counter(x["status"] for x in results)), "results": results,
                  "native_requests": 0}
        (root / "INDEPENDENT_SCORES.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
    raise SystemExit(2 if result.get("status") == "FAIL_SECURITY" else 0)


if __name__ == "__main__": main()
