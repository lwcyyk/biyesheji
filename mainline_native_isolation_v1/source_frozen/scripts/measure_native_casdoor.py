"""Independent native observations for one explicitly owned M2 account.

Shares only the bounded HTTP transport/accounting helper with the runtime.
Material verification, scoring, and state interpretation use independent code.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from auth_lifecycle.online_state.native_http import NativeHTTP, private_http_records


def ref(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def observe(batch, case, stage):
    batch, case = Path(batch), Path(case)
    profile = json.loads((case / "secure/native_profile.json").read_text())
    actor = profile["actor"]
    category = "cleanup" if stage == "cleanup" else "measurement"
    http = NativeHTTP(batch, category, enabled=True)
    events_path = case / "provider/native_events.jsonl"
    events = [json.loads(line) for line in events_path.read_text().splitlines()] if events_path.exists() else []
    labels = {e["native_sequence"]: e["rid"] for e in events if e["event"] == "native_response_received"}
    visible_path = case / "runner" / ("initial_visible.json" if stage == "initial" else "final_visible.json")
    visible = json.loads(visible_path.read_text())
    known = {r["rid"]: r for r in visible["requests"]}
    material_records = [r for r in private_http_records(batch) if r["actor"] == actor["name"]
                        and r["operation"] in {"issue", "refresh"}
                        and isinstance(r["response"].get("body"), dict)
                        and r["response"]["body"].get("access_token")]
    # Each distinct material is inspected at most once in this observation stage.
    pairs = {}
    for r in material_records:
        body = r["response"]["body"]
        pairs[body["access_token"]] = (labels.get(r["sequence"], "measurement_created"), body)
    rows = []
    for access_token, (rid, body) in pairs.items():
        answer = http.call("userinfo", actor=actor["name"], headers={"Authorization": "Bearer " + access_token})
        accepted = answer["http"] == 200 and answer["body"].get("sub") == actor["id"]
        determinate = answer["http"] in {200, 400, 401, 403}
        row = {"rid": rid, "access_ref": ref(access_token), "refresh_ref": ref(body.get("refresh_token")),
               "userinfo_http": answer["http"], "accepted": accepted if determinate else None,
               "runner_has_result": known.get(rid, {}).get("phase") in {"RESULT_AVAILABLE", "QUARANTINED", "DISPOSED"},
               "userinfo_native_sequence": answer["sequence"]}
        if stage == "final" and rid.startswith("A") and row["runner_has_result"] and not profile.get("measurement_no_refresh"):
            attempted = http.call("refresh", actor=actor["name"], form={
                "client_id": profile["client_id"], "client_secret": profile["client_secret"],
                "grant_type": "refresh_token", "refresh_token": body["refresh_token"], "scope": "openid"})
            row["refresh_http"] = attempted["http"]
            row["refresh_rejected"] = attempted["http"] in {400, 401, 403} and not attempted["body"].get("access_token")
        if stage == "final" and rid.startswith("A") and row["runner_has_result"] and profile.get("measurement_no_refresh"):
            active_rt = http.call("introspect", actor=actor["name"], form={
                "client_id": profile["client_id"], "client_secret": profile["client_secret"],
                "token": body["refresh_token"], "token_type_hint": "refresh_token"})
            row["refresh_introspection_active"] = active_rt["body"].get("active") if active_rt["http"] == 200 else None
            row["refresh_rejected"] = row["refresh_introspection_active"] is False
            row["refresh_check_kind"] = "READ_ONLY_INTROSPECTION"
        if stage == "final":
            active = http.call("introspect", actor=actor["name"], form={
                "client_id": profile["client_id"], "client_secret": profile["client_secret"],
                "token": access_token, "token_type_hint": "access_token"})
            value = active["body"].get("active") if active["http"] == 200 else None
            row["introspection_active"] = value if type(value) is bool else None
            row["introspection_http"] = active["http"]
        rows.append(row)
    database = Path(profile["native_database"])
    unit_rows = []
    with sqlite3.connect("file:" + str(database) + "?mode=ro", uri=True) as connection:
        records = connection.execute('SELECT name,access_token,access_token_hash,refresh_token,expires_in FROM token WHERE user=? AND application=?',
                                     (actor["name"], profile.get("application_name", "app-l1-0"))).fetchall()
        for name, at, at_hash, rt, expires in records:
            for access_token, (rid, body) in pairs.items():
                if at == access_token or at_hash == hashlib.sha256(access_token.encode()).hexdigest():
                    unit_rows.append({"rid": rid, "access_ref": ref(access_token), "refresh_ref": ref(body["refresh_token"]),
                                      "native_unit_ref": ref(name), "native_refresh_matches": rt == body["refresh_token"],
                                      "expires_in_field": expires})
    result = {"stage": stage, "rows": rows, "native_units": unit_rows,
              "accesses": [{"path": "secure/http/*.aes", "role": "scorer_only_native_responses"},
                           {"path": str(database), "mode": "read_only", "filter_user": actor["name"],
                            "filter_application": profile.get("application_name", "app-l1-0"), "SQL_queries": 1}],
              "cookie_free": True, "HTTP_category": category}
    target = case / "scorer" / (stage + "_native.json")
    target.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--stage", choices=["initial", "final", "cleanup"], required=True)
    args = parser.parse_args()
    result = observe(args.batch, args.case, args.stage)
    print(json.dumps({"stage": args.stage, "observations": len(result["rows"])}))
