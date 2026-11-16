"""Two one-shot native reconciliation traces, using the M3 authorization."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
import subprocess
import sys
import time

from .native_acceptance import preflight, create_actor, configure_case, native_request, observe, cleanup_actor, require
from .native_http import create_budget
from .lab import protect_directory
from .protocol import write_json


LIMITS = {"environment": 30, "method": 45, "measurement": 35, "cleanup": 50}


def source_model(output, repo):
    native = repo.parent / "research_main_innovation/ci01_contract_audit/sources/casdoor-v4.25.0"
    sources = [native / "object/token_oauth_util.go", native / "object/token.go", native / "object/token_jwt.go",
               repo / "src/auth_lifecycle/online_state/native_http.py", repo / "src/auth_lifecycle/online_state/protocol.py"]
    target = output / "model_sources"
    target.mkdir()
    rows = []
    for index, path in enumerate(sources):
        copied = target / (str(index) + "_" + path.name)
        copied.write_bytes(path.read_bytes())
        rows.append({"path": str(copied), "sha256": hashlib.sha256(copied.read_bytes()).hexdigest(), "original": str(path)})
    model = {"per_send_effect_bound": 1, "single_open_no_retry": True,
             "external_writers_excluded": True, "source_files": rows,
             "source_lemma_ref": "CAPABILITY_AND_CLOSURE_CONDITIONS.md:RefreshToken-single-insert",
             "premise_scope": "trusted controlled fixture; source fidelity and external writer exclusion remain explicit assumptions"}
    write_json(output / "MODEL.json", model)
    return model


def wait_file(path, seconds=15):
    deadline = time.monotonic() + seconds
    while not path.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    if not path.exists():
        raise TimeoutError("CONTROLLED_BARRIER_NOT_REACHED")


def run_case(batch, root, profile, model, scenario):
    lab = configure_case(root, profile)
    lab.configs["provider"]["permissions"]["adapter"].append("reconcile_query")
    lab.configs["controller"]["permissions"]["user"] += ["begin_reconciliation", "reconcile"]
    lab.configs["controller"]["reconciliation_model"] = model
    lab.configs["authority"]["permissions"]["controller"] += ["begin_reconciliation", "reconciliation_context", "save_reconciliation"]
    for role, config in lab.configs.items():
        write_json(root / "secure" / (role + ".json"), config)
    outcome = {"scenario": scenario, "status": "RUNNING"}
    try:
        lab.start_all()
        user = lab.client(timeout=12)
        grants = {}
        for task, generation in (("A", "g0"), ("B", "g1")):
            login = {"schema": 2, "kind": "casdoor_login", "issuer": profile["base"], "client": profile["client_id"],
                     "expected_account": profile["actor"]["id"], "username": profile["actor"]["name"], "password": profile["actor"]["password"]}
            grants[task] = require(user.call("grant", {"approval_op": task, "caller": "agent" + task, "task": task,
                "account": profile["actor"]["id"], "audience": profile["client_id"], "generation": generation,
                "operations": ["issue", "refresh", "userinfo"], "budget": 10, "material": login}), "GRANTED")
            req = native_request(grants[task]["handle"], profile, task, generation, task + "0", "issue")
            require(lab.client("agent" + task, timeout=12).call("call", req), "RESULT_AVAILABLE")
        write_json(root / "runner/initial_visible.json", user.call("status", {}))
        initial = observe(batch, root, "initial")
        if not all(r["accepted"] is True for r in initial["rows"]):
            raise RuntimeError("INITIAL_ACCEPTANCE_MISMATCH")
        if scenario == "M3-01":
            lab.restart_controller("after_effect")
        refresh = native_request(grants["A"]["handle"], profile, "A", "g0", "A1", "refresh", "A0")
        pending = lab.async_call("agentA", "call", refresh)
        if scenario == "M3-01":
            lab.wait_barrier("after_effect")
            lab.stop("controller")
            outcome["lost_response"] = pending.result(timeout=5)
            lab.start("controller")
        else:
            wait_file(root / "provider/before_native_refresh.json")
        outcome["ack"] = require(user.call("revoke", {"revoke_op": "withdrawA", "grant_id": grants["A"]["grant_id"]}), "LOCAL_REVOKE_COMMITTED")
        require(user.call("begin_reconciliation", {"rid": "A1", "window_id": "window1"}), "WINDOW_OPEN")
        blocked_b = native_request(grants["B"]["handle"], profile, "B", "g1", "B_create_paused", "refresh", "B0")
        outcome["B_creation_paused"] = require(lab.client("agentB").call("call", blocked_b), "REJECTED")
        b_inside = native_request(grants["B"]["handle"], profile, "B", "g1", "B_inside", "userinfo", "B0")
        outcome["B_inside_window"] = require(lab.client("agentB", timeout=12).call("call", b_inside), "RESULT_AVAILABLE")
        query = {"rid": "A1", "window_id": "window1", "step": "discover", "B_rid": ""}
        if scenario == "M3-02":
            empty = user.call("reconcile", query)
            outcome["empty_identifier_observation"] = require(empty, "UNKNOWN")
            write_json(root / "runner/empty_receipt.json", empty["receipt"])
            (root / "provider/before_native_refresh.release").touch()
            wait_file(root / "provider/identifier_ready.json")
        discovery = user.call("reconcile", query)
        outcome["discovery"] = discovery
        b_after = native_request(grants["B"]["handle"], profile, "B", "g1", "B_after", "userinfo", "B0")
        outcome["B_after_disposal"] = require(lab.client("agentB", timeout=12).call("call", b_after), "RESULT_AVAILABLE")
        finished = user.call("reconcile", {"rid": "A1", "window_id": "window1", "step": "finish", "B_rid": "B_after"})
        outcome["closure"] = finished
        if "receipt" in finished:
            write_json(root / "runner/closure_receipt.json", finished["receipt"])
        if scenario == "M3-02":
            (root / "provider/identifier_ready.release").touch()
            outcome["late_original_delivery"] = pending.result(timeout=15)
        outcome["final_state"] = user.call("status", {})
        write_json(root / "runner/final_visible.json", outcome["final_state"])
        observe(batch, root, "final")
        outcome["status"] = "OBSERVED"
    except Exception as error:
        outcome["status"] = "UNKNOWN"
        outcome["exception_type"] = type(error).__name__
        try:
            write_json(root / "runner/final_visible.json", lab.client().call("status", {}))
        except Exception:
            pass
    finally:
        lab.close()
        write_json(root / "runner/outcome.json", outcome)
    return outcome


def run(output, authorization_id, allow_native=False):
    if not allow_native:
        raise ValueError("EXPLICIT_NATIVE_ENABLE_REQUIRED")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "secure").mkdir()
    protect_directory(output / "secure")
    suffix = secrets.token_hex(5)
    names = ["l1-m3-" + suffix + "-" + str(i) for i in (1, 2)]
    create_budget(output, authorization_id, names, LIMITS, 160, 2, 2, 2400, point_reads=True)
    repo = Path(__file__).resolve().parents[3]
    model = source_model(output, repo)
    files = list((repo / "src/auth_lifecycle/online_state").glob("*")) + list((repo / "scripts").glob("*reconcil*.py"))
    write_json(output / "SOURCE_LOCK.json", {"files": [{"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.is_file()], "authorization_id": authorization_id})
    records=[]
    stopped=False
    started=time.monotonic()
    admin=template=None
    try:
        admin,template,original=preflight(output,repo / ".runtime/l1")
        for scenario,name in zip(("M3-01","M3-02"),names):
            if stopped or time.monotonic()-started>2250:
                records.append({"scenario":scenario,"status":"NOT_RUN"})
                continue
            actor=None
            root=output / scenario
            try:
                admin.category="environment"
                actor=create_actor(admin,output,name)
                profile={**template,"actor":actor,"durable_inbox":False,"identifier_journal":True,
                         "hold_before_native_refresh":scenario=="M3-02","hold_after_identifier":scenario=="M3-02"}
                outcome=run_case(output,root,profile,model,scenario)
                script=repo / "scripts/score_reconciliation.py"
                with (root / "scorer/console.txt").open("wb") as stream:
                    subprocess.run([sys.executable,"-B",str(script),"--case",str(root)],stdout=stream,stderr=stream,timeout=30)
                path=root / "scorer/result.json"
                score=json.loads(path.read_text()) if path.exists() else {"status":"ABORTED"}
                records.append({"scenario":scenario,"status":score["status"],"closure":outcome.get("closure",{}).get("status")})
                stopped=score["status"] not in {"PASS_CLOSED","PASS_CONSERVATIVE_UNKNOWN"}
            except Exception as error:
                records.append({"scenario":scenario,"status":"ABORTED","error_type":type(error).__name__})
                stopped=True
            finally:
                if actor is not None:
                    cleanup=cleanup_actor(admin,output,{**template,"actor":actor},root)
                    if not cleanup.get("account_absent") or not cleanup.get("all_observed_access_rejected",False):
                        stopped=True
                elif (output / "secure" / (name+".json")).exists():
                    admin.category="cleanup"
                    intent=json.loads((output / "secure" / (name+".json")).read_text())
                    row=admin.call("get_user",actor=name)["body"].get("data")
                    if row and intent.get("precheck_absent"):
                        intent["id"]=row["id"]
                        cleanup_actor(admin,output,{**template,"actor":intent},root)
            write_json(output / "RESULTS.json",{"records":records,"counts":dict(Counter(r['status'] for r in records))})
        admin.category="environment"
        app=admin.call("application")["body"].get("data",{})
        unchanged=all(app.get(k)==v for k,v in original.items())
    except Exception as error:
        stopped=True
        unchanged=None
        write_json(output / "ERROR.json",{"exception_type":type(error).__name__,"reason":"ENVIRONMENT_OR_EXECUTION_UNAVAILABLE"})
    seen={r["scenario"] for r in records}
    records.extend({"scenario":s,"status":"NOT_RUN"} for s in ("M3-01","M3-02") if s not in seen)
    with sqlite3.connect(output / "native_budget.db") as con:
        cost=dict(con.execute('SELECT category,COUNT(*) FROM requests GROUP BY category'))
    result={"authorization_id":authorization_id,"records":records,"counts":dict(Counter(r["status"] for r in records)),
            "HTTP_categories":cost,"HTTP_total":sum(cost.values()),"elapsed_seconds_including_cleanup":time.monotonic()-started,
            "application_unchanged":unchanged,"stopped_early":stopped,"automatic_resampling":0}
    write_json(output / "RESULTS.json",result)
    print(json.dumps(result),flush=True)
    return result
