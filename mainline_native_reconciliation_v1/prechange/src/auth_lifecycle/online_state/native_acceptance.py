"""Four-account, one-shot Casdoor acceptance with a separate cleanup reserve."""

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import subprocess
import sys
import time
import zipfile

from .lab import Laboratory, protect_directory
from .native_http import NativeHTTP, create_budget, private_http_records
from .protocol import write_json


SCENARIOS = ("M2-01", "M2-02", "M2-03", "M2-04")


def require(response, status):
    if response.get("status") != status:
        raise RuntimeError("UNEXPECTED_" + str(response.get("status", "RESPONSE")))
    return response


def preflight(batch, runtime):
    binary = runtime / "dist/casdoor/casdoor.exe"
    archive = runtime / "downloads/casdoor_Windows_x86_64.zip"
    if hashlib.sha256(archive.read_bytes()).hexdigest() != "24457f4383e33639d851514ddbb49fcaac85fca630f4736901c14d13a1114b32":
        raise RuntimeError("ENVIRONMENT_ARCHIVE_MISMATCH")
    with zipfile.ZipFile(archive) as zipped:
        member = next(n for n in zipped.namelist() if Path(n).name.lower() == "casdoor.exe")
        binary_hash = hashlib.sha256(zipped.read(member)).hexdigest()
    if hashlib.sha256(binary.read_bytes()).hexdigest() != binary_hash:
        raise RuntimeError("ENVIRONMENT_BINARY_MISMATCH")
    command = "[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); Get-CimInstance Win32_Process -Filter \"name='casdoor.exe'\" | Select-Object ProcessId,ExecutablePath,CommandLine | ConvertTo-Json"
    process = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, timeout=15)
    running = json.loads(process.stdout.decode("utf-8-sig"))
    running = running if isinstance(running, list) else [running]
    if not any(Path(p["ExecutablePath"]).resolve() == binary.resolve() for p in running):
        raise RuntimeError("ENVIRONMENT_PROCESS_MISMATCH")
    admin = NativeHTTP(batch, "environment", cookies=True, enabled=True)
    credentials = json.loads((runtime / "secrets.json").read_text())
    login = admin.call("admin_login", payload={"type": "login", "organization": "built-in", "username": "admin",
        "password": credentials["casdoor_password"], "application": "app-built-in", "autoSignin": True})
    if login["http"] != 200 or login["body"].get("status") != "ok":
        raise RuntimeError("ENVIRONMENT_ADMIN_AUTH_FAILED")
    answer = admin.call("application")
    app = answer["body"].get("data")
    if (not isinstance(app, dict) or app.get("organization") != "l1-study"
            or app.get("clientId") != "l1-client-0" or app.get("tokenFormat") != "JWT"
            or app.get("expireInHours") != 1 or app.get("refreshExpireInHours") != 1
            or bool(app.get("disableRefreshRotation", False))
            or not {"password", "refresh_token"}.issubset(app.get("grantTypes", []))):
        raise RuntimeError("ENVIRONMENT_APPLICATION_PROFILE_MISMATCH")
    discovery = admin.call("discovery")["body"]
    if discovery.get("userinfo_endpoint") != "http://127.0.0.1:18081/api/userinfo" or discovery.get("jwks_uri") != "http://127.0.0.1:18081/.well-known/jwks":
        raise RuntimeError("ENVIRONMENT_DISCOVERY_MISMATCH")
    jwks = admin.call("jwks")["body"]
    if not isinstance(jwks.get("keys"), list):
        raise RuntimeError("ENVIRONMENT_JWKS_UNAVAILABLE")
    fields = ("name", "clientId", "organization", "grantTypes", "expireInHours", "refreshExpireInHours", "tokenFormat", "disableRefreshRotation")
    public = {k: app.get(k) for k in fields}
    write_json(batch / "ENVIRONMENT_LOCK.json", {
        "provider": "Casdoor", "version": "4.25.0", "base": "http://127.0.0.1:18081",
        "binary_sha256": binary_hash, "binary_matches_release_archive": True,
        "source_commit_reference": "528a0213f01caf70b9f41009cbf7b2f67bdd67ec",
        "source_reproducible_build": "UNPROVED", "running_processes": running,
        "application": public, "discovery": {k: discovery.get(k) for k in
        ("issuer", "token_endpoint", "userinfo_endpoint", "jwks_uri", "revocation_endpoint", "introspection_endpoint")},
        "userinfo_contract": "fresh cookie-free bearer request, exact expected sub",
        "local_ack": "LOCAL_REVOKE_COMMITTED; native outcomes separately recorded"})
    template = {"enabled": True, "version": "4.25.0", "base": "http://127.0.0.1:18081",
                "client_id": app["clientId"], "client_secret": app["clientSecret"], "jwks": jwks,
                "batch": str(batch), "native_database": str(runtime / "casdoor-l1.db")}
    write_json(batch / "secure/profile_template.json", template)
    return admin, template, public


def create_actor(admin, batch, name):
    prior = admin.call("get_user", actor=name)
    if prior["http"] != 200 or prior["body"].get("data") is not None:
        raise RuntimeError("TEST_ACCOUNT_NAME_ALREADY_PRESENT")
    actor = {"name": name, "password": secrets.token_urlsafe(22), "owner": "l1-study",
             "precheck_absent": True, "creation_attempted": True}
    write_json(batch / "secure" / (name + ".json"), actor)
    answer = admin.call("add_user", actor=name, payload={
        "owner": "l1-study", "name": name, "displayName": "M2 owned fixture", "type": "normal-user",
        "password": actor["password"], "email": name + "@example.invalid", "isAdmin": False, "isForbidden": False})
    if answer["http"] != 200 or answer["body"].get("status") != "ok":
        raise RuntimeError("TEST_ACCOUNT_CREATION_UNCERTAIN")
    row = admin.call("get_user", actor=name)["body"].get("data")
    if not row or row.get("name") != name or row.get("owner") != "l1-study":
        raise RuntimeError("TEST_ACCOUNT_ID_UNAVAILABLE")
    actor.update(id=row["id"], created_verified=True)
    write_json(batch / "secure" / (name + ".json"), actor)
    return actor


def configure_case(root, profile):
    lab = Laboratory(root)
    write_json(lab.root / "secure/native_profile.json", profile)
    lab.configs["provider"]["native_profile"] = str(lab.root / "secure/native_profile.json")
    lab.configs["provider"]["permissions"]["adapter"].append("dispose")
    lab.configs["controller"]["permissions"]["user"].append("dispose")
    lab.configs["authority"]["permissions"]["controller"] += ["prepare_disposal", "record_disposal"]
    for role, config in lab.configs.items():
        write_json(lab.root / "secure" / (role + ".json"), config)
    return lab


def native_request(handle, profile, task, generation, rid, operation, source=None):
    return {"rid": rid, "handle": handle, "task": task, "account": profile["actor"]["id"],
            "audience": profile["client_id"], "generation": generation, "operation": operation,
            "payload": {} if operation == "issue" else {"source_rid": source}}


def observe(batch, root, stage):
    script = Path(__file__).resolve().parents[3] / "scripts/measure_native_casdoor.py"
    with (root / "scorer" / (stage + ".console.txt")).open("wb") as stream:
        result = subprocess.run([sys.executable, "-B", str(script), "--batch", str(batch),
                                 "--case", str(root), "--stage", stage], stdout=stream, stderr=stream, timeout=40)
    if result.returncode:
        raise RuntimeError("INDEPENDENT_OBSERVATION_FAILED")
    return json.loads((root / "scorer" / (stage + "_native.json")).read_text())


def run_case(batch, root, profile, scenario):
    lab = configure_case(root, profile)
    outcome = {"scenario": scenario, "status": "RUNNING"}
    try:
        lab.start_all()
        user = lab.client(timeout=12)
        grants = {}
        for task, generation in (("A", "g0"), ("B", "g1")):
            login = {"schema": 2, "kind": "casdoor_login", "issuer": profile["base"],
                     "client": profile["client_id"], "expected_account": profile["actor"]["id"],
                     "username": profile["actor"]["name"], "password": profile["actor"]["password"]}
            grants[task] = require(user.call("grant", {"approval_op": "approve_" + task, "caller": "agent" + task,
                "task": task, "account": profile["actor"]["id"], "audience": profile["client_id"],
                "generation": generation, "operations": ["issue", "refresh", "userinfo"], "budget": 8,
                "material": login}), "GRANTED")
            request = native_request(grants[task]["handle"], profile, task, generation, task + "0", "issue")
            outcome[task + "_issue"] = require(lab.client("agent" + task, timeout=12).call("call", request), "RESULT_AVAILABLE")
        outcome["grants"] = grants
        write_json(root / "runner/initial_visible.json", user.call("status", {}))
        initial = observe(batch, root, "initial")
        if len(initial["rows"]) != 2 or not all(x["accepted"] is True for x in initial["rows"]):
            raise RuntimeError("INITIAL_NATIVE_ACCEPTANCE_MISMATCH")
        snapshot = lab.snapshot_cache()
        pending = None
        if scenario in {"M2-02", "M2-03"}:
            refresh = native_request(grants["A"]["handle"], profile, "A", "g0", "A1", "refresh", "A0")
            if scenario == "M2-03":
                lab.restart_controller("after_effect")
            pending = lab.async_call("agentA", "call", refresh)
            if scenario == "M2-02":
                barrier = root / "provider/refresh_received.json"
                deadline = time.monotonic() + 15
                while not barrier.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                if not barrier.exists():
                    raise TimeoutError("NATIVE_REFRESH_BARRIER")
                outcome["visible_before_delivery"] = user.call("status", {})
            else:
                lab.wait_barrier("after_effect")
                lab.stop("controller")
                outcome["lost_result"] = pending.result(timeout=5)
                lab.start("controller")
        revoke = {"revoke_op": "revoke_A", "grant_id": grants["A"]["grant_id"]}
        outcome["ack"] = require(user.call("revoke", revoke), "LOCAL_REVOKE_COMMITTED")
        if scenario == "M2-04":
            lab.stop("controller")
            lab.restore_cache(snapshot)
            lab.stop("authority")
            lab.start("controller")
            outcome["authority_outage"] = user.call("recover", {})
            require(outcome["authority_outage"], "UNKNOWN")
            unavailable_b = native_request(grants["B"]["handle"], profile, "B", "g1", "B_during_outage", "userinfo", "B0")
            outcome["admission_during_outage"] = lab.client("agentB").call("call", unavailable_b)
            require(outcome["admission_during_outage"], "UNKNOWN")
            lab.start("authority")
        outcome["recovered"] = require(user.call("recover", {}), "RECOVERED")
        denied = native_request(grants["A"]["handle"], profile, "A", "g0", "A_after_ack", "issue")
        outcome["A_after_ack"] = require(lab.client("agentA").call("call", denied), "REJECTED")
        use_b = native_request(grants["B"]["handle"], profile, "B", "g1", "B_use", "userinfo", "B0")
        outcome["B_continue"] = require(lab.client("agentB", timeout=12).call("call", use_b), "RESULT_AVAILABLE")
        if scenario == "M2-02":
            (root / "provider/refresh_received.release").touch()
            outcome["late_A"] = require(pending.result(timeout=15), "QUARANTINED")
        if scenario == "M2-03":
            outcome["lookup_unknown"] = require(user.call("deliver", {"rid": "A1"}), "UNKNOWN")
        for rid in (["A0", "A1"] if scenario == "M2-02" else ["A0"]):
            outcome["disposal_" + rid] = user.call("dispose", {"disposal_op": "dispose_" + rid, "rid": rid})
        outcome["visible_final"] = user.call("status", {})
        write_json(root / "runner/final_visible.json", outcome["visible_final"])
        observe(batch, root, "final")
        outcome["status"] = "OBSERVED"
    except Exception as error:
        outcome["status"] = "UNKNOWN"
        outcome["exception_type"] = type(error).__name__
        # A late result is never recovered from scorer-private files here.
        try:
            write_json(root / "runner/final_visible.json", lab.client().call("status", {}))
        except Exception:
            pass
    finally:
        lab.close()
        write_json(root / "runner/outcome.json", outcome)
    return outcome


def cleanup_actor(admin, batch, profile, root):
    actor = profile["actor"]
    admin.category = "cleanup"
    response_records = private_http_records(batch)
    refresh_tokens = {r["response"]["body"]["refresh_token"] for r in response_records
        if r["actor"] == actor["name"] and isinstance(r["response"].get("body"), dict)
        and r["response"]["body"].get("refresh_token")}
    cleanup_http = NativeHTTP(batch, "cleanup", enabled=True)
    revoked = []
    for token in refresh_tokens:
        result = cleanup_http.call("revoke", actor=actor["name"], form={"client_id": profile["client_id"],
            "client_secret": profile["client_secret"], "token": token, "token_type_hint": "refresh_token"})
        revoked.append(result["http"])
    disabled = admin.call("disable_user", actor=actor["name"], payload={"owner": "l1-study", "name": actor["name"], "isForbidden": True})
    deleted = admin.call("delete_user", actor=actor["name"], payload={"owner": "l1-study", "name": actor["name"]})
    absent = admin.call("get_user", actor=actor["name"])
    result = {"account": actor["name"], "revoke_responses": revoked,
              "disable_ok": disabled["body"].get("status") == "ok", "delete_ok": deleted["body"].get("status") == "ok",
              "account_absent": absent["http"] == 200 and absent["body"].get("data") is None,
              "scope": "final whole-owned-account cleanup after B preservation window"}
    if (root / "runner/final_visible.json").exists():
        try:
            checks = observe(batch, root, "cleanup")
            result["all_observed_access_rejected"] = all(r["accepted"] is False for r in checks["rows"])
        except Exception as error:
            result["observation_error"] = type(error).__name__
    write_json(root / "scorer/cleanup.json", result)
    return result


def run_native(batch, authorization_id, allow_native=False):
    if not allow_native:
        raise ValueError("EXPLICIT_NATIVE_ENABLE_REQUIRED")
    batch = Path(batch).resolve()
    batch.mkdir(parents=True, exist_ok=False)
    (batch / "secure").mkdir()
    protect_directory(batch / "secure")
    suffix = secrets.token_hex(5)
    names = ["l1-m2-" + suffix + "-" + str(i) for i in range(1, 5)]
    create_budget(batch, authorization_id, names)
    repo = Path(__file__).resolve().parents[3]
    files = list((repo / "src/auth_lifecycle/online_state").glob("*.py")) + list((repo / "src/auth_lifecycle/online_state").glob("*.sql"))
    files += list((repo / "scripts").glob("*native_casdoor*.py"))
    write_json(batch / "SOURCE_LOCK.json", {"files": [{"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files], "authorization_id": authorization_id})
    runtime = repo / ".runtime/l1"
    records = []
    admin = template = None
    stopped = False
    started = time.monotonic()
    try:
        admin, template, original_app = preflight(batch, runtime)
        for scenario, name in zip(SCENARIOS, names):
            if stopped or time.monotonic() - started > 3450:
                records.append({"scenario": scenario, "status": "NOT_RUN"})
                continue
            actor = None
            root = batch / scenario
            try:
                admin.category = "environment"
                actor = create_actor(admin, batch, name)
                profile = {**template, "actor": actor, "durable_inbox": scenario != "M2-03", "hold_refresh": scenario == "M2-02"}
                outcome = run_case(batch, root, profile, scenario)
                scorer = repo / "scripts/score_native_casdoor.py"
                with (root / "scorer/console.txt").open("wb") as stream:
                    checked = subprocess.run([sys.executable, "-B", str(scorer), "--case", str(root)], stdout=stream, stderr=stream, timeout=30)
                score_path = root / "scorer/result.json"
                score = json.loads(score_path.read_text()) if score_path.exists() else {"status": "ABORTED"}
                record = {"scenario": scenario, "runtime_status": outcome["status"], "status": score["status"]}
                records.append(record)
                stopped = score["status"] != "PASS"
            except Exception as error:
                records.append({"scenario": scenario, "status": "ABORTED", "exception_type": type(error).__name__})
                stopped = True
            finally:
                if actor is not None:
                    cleanup = cleanup_actor(admin, batch, {**template, "actor": actor}, root)
                    if not cleanup.get("account_absent") or not cleanup.get("all_observed_access_rejected", False):
                        stopped = True
                elif (batch / "secure" / (name + ".json")).exists():
                    admin.category = "cleanup"
                    pending_actor = json.loads((batch / "secure" / (name + ".json")).read_text())
                    row = admin.call("get_user", actor=name)["body"].get("data")
                    if row and pending_actor.get("precheck_absent"):
                        pending_actor["id"] = row["id"]
                        root.mkdir(exist_ok=True)
                        (root / "scorer").mkdir(exist_ok=True)
                        cleanup_actor(admin, batch, {**template, "actor": pending_actor}, root)
            write_json(batch / "RESULTS.json", {"records": records, "counts": dict(Counter(r["status"] for r in records))})
        admin.category = "environment"
        after = admin.call("application")["body"].get("data", {})
        unchanged = all(after.get(k) == v for k, v in original_app.items())
    except Exception as error:
        stopped = True
        unchanged = None
        write_json(batch / "ENVIRONMENT_ERROR.json", {"exception_type": type(error).__name__, "reason": str(error) if str(error).startswith("ENVIRONMENT_") else "SAFE_FAILURE"})
    existing = {r["scenario"] for r in records}
    records.extend({"scenario": s, "status": "NOT_RUN"} for s in SCENARIOS if s not in existing)
    con = sqlite3.connect(batch / "native_budget.db")
    costs = dict(con.execute("SELECT category,COUNT(*) FROM requests GROUP BY category"))
    con.close()
    result = {"authorization_id": authorization_id, "records": records, "counts": dict(Counter(r["status"] for r in records)),
              "native_HTTP": costs, "native_HTTP_total": sum(costs.values()), "application_unchanged": unchanged,
              "elapsed_seconds_including_cleanup": time.monotonic() - started, "stopped_early": stopped,
              "automatic_resampling": 0, "crypto_auxiliary_line": "FROZEN"}
    write_json(batch / "RESULTS.json", result)
    print(json.dumps(result), flush=True)
    return result
