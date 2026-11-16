"""Independent offline M3 state/receipt/native evidence scorer."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def score(root):
    root = Path(root)
    outcome = json.loads((root / "runner/outcome.json").read_text())
    checks = []
    def verify(name, ok):checks.append({"name": name, "pass": bool(ok)})
    if outcome["status"] != "OBSERVED":
        result = {"status": "ABORTED", "reason": "INCOMPLETE_TRACE"}
        (root / "scorer/result.json").write_text(json.dumps(result));return result
    with sqlite3.connect("file:" + str(root / "authority/authority.db") + "?mode=ro", uri=True) as con:
        sealed = con.execute("SELECT ciphertext FROM authority_state WHERE id=1").fetchone()[0]
        events = [(v, op, json.loads(body)) for v, op, body in con.execute("SELECT version,operation,projection FROM authority_events ORDER BY version")]
    state = json.loads(AESGCM((root / "secure/authority.key").read_bytes()).decrypt(sealed[:12], sealed[12:], b"auth-lifecycle/online-state/schema-1"))
    receipt = json.loads((root / "runner/closure_receipt.json").read_text())
    spec = importlib.util.spec_from_file_location("independent_receipt_checker", Path(__file__).with_name("check_reconciliation_receipt.py"))
    checker = importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    result_check = checker.check(receipt)
    verify("independent_receipt_validation", result_check["status"] != "INVALID")
    target = state["requests"]["A1"]
    window = state["reconciliation_windows"][target["origin"]["account"]]
    verify("receipt_is_committed", window.get("receipt") == receipt)
    verify("attempt_source_bound", receipt["target"]["attempt_id"] == target["attempt_id"] and receipt["target"]["request_digest"] == target["digest"])
    a_grant = state["grants"][target["origin"]["grant_id"]]
    verify("A_retired", a_grant["active"] is False)
    verify("B_creating_blocked_and_resource_works", outcome["B_creation_paused"]["status"] == "REJECTED" and outcome["B_inside_window"]["status"] == outcome["B_after_disposal"]["status"] == "RESULT_AVAILABLE")
    frozen = set();ordered = True
    for version, op, event in events:
        result = event["result"]
        if op == "revoke" and result["status"] == "LOCAL_REVOKE_COMMITTED":frozen.add(result["grant_id"])
        if op == "release" and result.get("send"):
            req = next(r for r in event["state"]["requests"] if r["rid"] == result["rid"])
            ordered &= req["origin"]["grant_id"] not in frozen
    verify("no_new_A_release_after_revoke", ordered)
    profile = json.loads((root / "secure/native_profile.json").read_text())
    with sqlite3.connect("file:" + str(Path(profile["batch"]) / "native_budget.db") + "?mode=ro", uri=True) as con:
        sends = con.execute("SELECT COUNT(*) FROM requests WHERE operation='refresh' AND category='method' AND attempt_id=?", (target["attempt_id"],)).fetchone()[0]
        points = con.execute("SELECT COUNT(*) FROM requests WHERE operation='get_token' AND actor=?", (profile["actor"]["name"],)).fetchone()[0]
        broad = con.execute("SELECT COUNT(*) FROM requests WHERE operation IN ('get_tokens','list_tokens') AND actor=?", (profile["actor"]["name"],)).fetchone()[0]
        creators = con.execute("SELECT COUNT(*) FROM requests WHERE category='method' AND operation IN ('issue','refresh') AND actor=?", (profile["actor"]["name"],)).fetchone()[0]
    verify("actual_send_count", sends == receipt["facts"]["actual_sends"] == 1)
    verify("no_unsafe_broad_enumeration", broad == 0)
    verify("registered_fixture_creators_only", creators == 3)
    # The native HTTP implementation has no plural-list route. Point responses are
    # tied to a verified identifier receipt, which is re-bound below.
    initial = json.loads((root / "scorer/initial_native.json").read_text())
    final = json.loads((root / "scorer/final_native.json").read_text())
    verify("native_B_preserved", any(r["rid"] == "B0" and r["accepted"] is True for r in final["rows"]))
    verify("initial_materials_accepted", len(initial["rows"]) == 2 and all(r["accepted"] is True for r in initial["rows"]))
    if receipt["claim"] == "CLOSED":
        known_a = [r for r in final["rows"] if r["rid"].startswith("A")]
        verify("closed_A_units_native_inactive", len(known_a) == 2 and all(r["accepted"] is False and r.get("refresh_rejected") is True for r in known_a))
        verify("closed_remaining_effects_zero", receipt["remaining_creation_bound"] == 0 and points >= 1 and target["phase"] == "DISPOSED")
        verify("closed_no_attempt_obligation", "A1" not in outcome["final_state"]["obligations"])
    else:
        verify("unknown_attempt_obligation_retained", "A1" in outcome["final_state"]["obligations"])
    if outcome["scenario"] == "M3-02":
        empty = json.loads((root / "runner/empty_receipt.json").read_text())
        verify("pre_send_empty_not_closed", empty["claim"] == "UNKNOWN" and empty["facts"]["actual_sends"] == 0 and empty["remaining_creation_bound"] == 1)
        verify("empty_was_local_identifier_observation", empty["evidence"]["packet"]["query"]["query_kind"] == "none")
    metadata = [json.loads(line) for line in (root / "provider/identifier_receipts.jsonl").read_text().splitlines()]
    matching = [r for r in metadata if r["attempt_id"] == target["attempt_id"]]
    verify("identifier_receipt_matches_actual_journal", len(matching) == 1 and matching[0]["origin"] == target["origin"] and matching[0]["digest"] == target["digest"])
    if receipt["claim"] == "CLOSED":
        expected = receipt["evidence"]["packet"]["query"]["identifier_receipt"]
        verify("receipt_journal_content", expected == matching[0])
    secret_values = [profile["actor"]["password"], profile["client_secret"]]
    for request in state["requests"].values():
        material = request.get("result_material")
        if isinstance(material, dict):
            secret_values += [v for k,v in material["native"].items() if k in {"access_token","refresh_token","id_token"} and v]
    for role in ("controller","authority","provider"):
        config = json.loads((root / "secure" / (role + ".json")).read_text())
        secret_values += list(config["identities"].values())
    leaks = []
    for directory in ("runner","controller","control","provider","authority","scorer"):
        for path in (root / directory).rglob("*"):
            if path.is_file() and path.suffix in {".json",".jsonl",".txt",".stderr"} and path.name not in {"native_inbox.jsonl"}:
                if any(value.encode() in path.read_bytes() for value in secret_values):leaks.append(str(path.relative_to(root)))
    verify("public_projections_do_not_export_material", not leaks)
    role_events = [json.loads(line) for line in (root / "control/processes.jsonl").read_text().splitlines()]
    started = sorted(r["child_pid"] for r in role_events if r["event"] == "started")
    exited = sorted(r["child_pid"] for r in role_events if r["event"] == "terminated_and_waited")
    verify("all_own_processes_exited", started == exited)
    status = ("PASS_CLOSED" if receipt["claim"] == "CLOSED" else "PASS_CONSERVATIVE_UNKNOWN") if all(r["pass"] for r in checks) else "SAFETY_FAILURE"
    result = {"status": status, "checks": checks, "closure": receipt["claim"], "receipt_checker": result_check,
              "remaining_obligations": outcome["final_state"]["obligations"], "native_point_queries": points,
              "leak_paths":leaks,
              "observed_G": len({r["native_unit_ref"] for observation in (initial, final) for r in observation["native_units"]}),
              "scope": "conditional one-attempt effect exhaustion; no whole-account or arbitrary RP claim"}
    (root / "scorer/result.json").write_text(json.dumps(result, indent=2) + "\n");return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser();parser.add_argument("--case", required=True)
    args = parser.parse_args();result = score(args.case);print(json.dumps({"status":result["status"]}))
    raise SystemExit(1 if result["status"] == "SAFETY_FAILURE" else 0)
