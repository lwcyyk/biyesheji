"""Budgeted M1 runner. Decisions use only runner APIs and explicit fault barriers."""

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from .lab import Laboratory, approval, request_for
from .protocol import write_json


SCENARIOS = ("normal", "pending_before_commit", "release_before_send",
             "effect_before_registration", "revoke_before_commit",
             "old_cache_after_ack", "authority_outage")


class ObservedSafetyFailure(RuntimeError):
    pass


class TraceInconclusive(RuntimeError):
    pass


def require_status(result, expected):
    if result.get("status") in {"UNKNOWN", "INCONCLUSIVE"}:
        raise TraceInconclusive("REQUIRED_OBSERVATION_UNAVAILABLE")
    if result.get("status") != expected:
        raise ObservedSafetyFailure("UNEXPECTED_OBSERVABLE_DECISION")


def run_trace(root, scenario):
    started = time.monotonic()
    fault = {"pending_before_commit": "before_admit", "release_before_send": "after_release",
             "effect_before_registration": "after_effect", "revoke_before_commit": "before_revoke"}.get(scenario)
    # Reserve two SQL reads for the independent offline scorer.
    lab = Laboratory(root, operation_limit=98)
    outcome = {"scenario": scenario, "status": "RUNNING", "native_requests": 0}
    try:
        lab.start_all(fault)
        user = lab.client()
        grant_a = user.call("grant", approval("A", "g0"))
        grant_b = user.call("grant", approval("B", "g1"))
        outcome["grants"] = [grant_a, grant_b]
        if grant_a.get("status") != "GRANTED" or grant_b.get("status") != "GRANTED":
            raise RuntimeError("SETUP_APPROVAL_FAILED")
        user.call("recover", {})
        snapshot = lab.snapshot_cache()
        (lab.root / "control" / "old_cache_snapshot.json").write_bytes(snapshot)
        request_a = request_for(grant_a["handle"], "A", "g0", "A1")
        request_b = request_for(grant_b["handle"], "B", "g1", "B1")
        revoke = {"revoke_op": "revoke_A_g0", "grant_id": grant_a["grant_id"]}
        if scenario in {"pending_before_commit", "release_before_send", "effect_before_registration"}:
            pending = lab.async_call("agentA", "call", request_a)
            lab.wait_barrier(fault)
            lab.stop("controller")
            outcome["interrupted_A"] = pending.result(timeout=5)
            lab.start("controller")
        else:
            outcome["A_result"] = lab.client("agentA").call("call", request_a)
        if scenario == "revoke_before_commit":
            pending = lab.async_call("user", "revoke", revoke)
            lab.wait_barrier(fault)
            lab.stop("controller")
            outcome["interrupted_revoke"] = pending.result(timeout=5)
            lab.start("controller")
        outcome["revoke_ack"] = user.call("revoke", revoke)
        require_status(outcome["revoke_ack"], "LOCAL_REVOKE_COMMITTED")
        if scenario == "old_cache_after_ack":
            lab.stop("controller")
            lab.restore_cache(snapshot)
            lab.start("controller")
        if scenario == "authority_outage":
            lab.stop("controller")
            lab.stop("authority")
            lab.start("controller")
            outcome["outage_recover"] = user.call("recover", {})
            outcome["outage_B"] = lab.client("agentB").call("call", request_b)
            lab.start("authority")
        recovery_started = time.monotonic()
        outcome["recovered"] = user.call("recover", {})
        outcome["post_ack_A"] = lab.client("agentA").call(
            "call", request_for(grant_a["handle"], "A", "g0", "A_after_ack"))
        require_status(outcome["post_ack_A"], "REJECTED")
        if scenario in {"release_before_send", "effect_before_registration"}:
            outcome["repeat_unknown_A"] = lab.client("agentA").call("call", request_a)
        outcome["B_result"] = lab.client("agentB").call("call", request_b)
        require_status(outcome["B_result"], "RESULT_AVAILABLE")
        outcome["B_after_recovery_seconds"] = time.monotonic() - recovery_started
        if scenario not in {"pending_before_commit", "release_before_send"}:
            outcome["late_result"] = user.call("deliver", {"rid": "A1"})
        outcome["final_visible_state"] = user.call("status", {})
        outcome["status"] = "OBSERVED"
    except ObservedSafetyFailure as error:
        outcome["status"] = "SAFETY_FAILURE"
        outcome["exception_type"] = type(error).__name__
    except TraceInconclusive as error:
        outcome["status"] = "INCONCLUSIVE"
        outcome["exception_type"] = type(error).__name__
    except Exception as error:
        outcome["status"] = "ABORTED"
        outcome["exception_type"] = type(error).__name__
    finally:
        lab.close()
        outcome["elapsed_seconds"] = time.monotonic() - started
        write_json(lab.root / "runner" / "outcome.json", outcome)
    return outcome


def continuation_plan(previous_result, authorization_id):
    previous = json.loads(Path(previous_result).read_text())
    if previous["authorization_id"] != authorization_id:
        raise ValueError("CONTINUATION_AUTHORIZATION_MISMATCH")
    if any(r["status"] == "SAFETY_FAILURE" for r in previous["records"]):
        raise ValueError("SAFETY_FAILURE_REQUIRES_SEPARATE_BATCH_AUTHORIZATION")
    full_plan = {(scenario, repeat) for scenario in SCENARIOS for repeat in range(1, 4)}
    recorded = [(row["scenario"], row["repeat"]) for row in previous["records"]]
    if len(recorded) != 21 or set(recorded) != full_plan:
        raise ValueError("INVALID_ORIGINAL_DENOMINATOR")
    return {pair for pair, row in zip(recorded, previous["records"]) if row["status"] == "NOT_RUN"}


def run_acceptance(output, authorization_id, continue_from=None):
    selected = continuation_plan(continue_from, authorization_id) if continue_from else None
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    repo = Path(__file__).resolve().parents[3]
    files = list((repo / "src" / "auth_lifecycle" / "online_state").glob("*"))
    files += [repo / "scripts" / "online_state.py", repo / "scripts" / "score_online_state.py"]
    manifest = [{"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in files if p.is_file()]
    write_json(output / "batch_lock.json", {
        "authorization_id": authorization_id, "scenarios": list(SCENARIOS), "repeats": 3,
        "max_traces": 21, "max_trace_seconds": 60, "max_batch_seconds": 1800,
        "max_sql_statements_per_trace": 100, "source_manifest": manifest,
        "native_requests": 0, "rerun_requires_separate_authorization": True,
        "continuation_of": str(continue_from) if continue_from else None,
        "selected_original_slots": sorted(selected) if selected is not None else None})
    started = time.monotonic()
    records = []
    stopped = False
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(repo / "src")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for scenario in SCENARIOS:
        for repeat in range(1, 4):
            if selected is not None and (scenario, repeat) not in selected:
                continue
            name = scenario + "_" + str(repeat)
            record = {"scenario": scenario, "repeat": repeat, "path": name}
            # Reserve the trace window, scoring, and process cleanup within 30 min.
            if stopped or time.monotonic() - started >= 1710:
                record["status"] = "NOT_RUN"
                records.append(record)
                continue
            root = output / name
            command = [sys.executable, "-B", "-m", "auth_lifecycle.online_state.cli", "trace",
                       "--root", str(root), "--scenario", scenario]
            flags = (subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == "nt" else 0
            with (output / (name + ".runner.txt")).open("wb") as log:
                process = subprocess.Popen(command, env=environment, stdout=log, stderr=log,
                                           creationflags=flags, start_new_session=os.name != "nt")
                try:
                    process.wait(timeout=min(60, max(0.1, 1800 - (time.monotonic() - started))))
                except subprocess.TimeoutExpired:
                    if os.name == "nt":
                        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                       capture_output=True, timeout=8)
                    else:
                        os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
                    record["status"] = "INCONCLUSIVE"
                    record["reason"] = "OBSERVATION_WINDOW_EXHAUSTED"
            if "status" not in record:
                outcome_path = root / "runner" / "outcome.json"
                if process.returncode != 0 or not outcome_path.exists():
                    record["status"] = "ABORTED"
                    record["reason"] = "TRACE_PROCESS_FAILED"
                    stopped = True
                else:
                    outcome = json.loads(outcome_path.read_text())
                    if outcome["status"] in {"ABORTED", "SAFETY_FAILURE", "INCONCLUSIVE"}:
                        record["status"] = outcome["status"]
                        stopped = outcome["status"] in {"ABORTED", "SAFETY_FAILURE"}
                    else:
                        score_command = [sys.executable, "-B", str(repo / "scripts" / "score_online_state.py"),
                                         "--root", str(root)]
                        with (output / (name + ".score.txt")).open("wb") as log:
                            scored = subprocess.run(score_command, stdout=log, stderr=log, timeout=15)
                        score_path = root / "scorer" / "result.json"
                        if score_path.exists():
                            score_result = json.loads(score_path.read_text())
                            record["status"] = score_result["status"]
                            record["metrics"] = score_result["metrics"]
                            record["final_obligations"] = score_result["final_obligations"]
                            record["failed_checks"] = [x["name"] for x in score_result["checks"] if not x["pass"]]
                        else:
                            record["status"] = "ABORTED"
                        if record["status"] in {"SAFETY_FAILURE", "ABORTED"}:
                            stopped = True
            records.append(record)
            write_json(output / "results.json", {"records": records,
                       "counts": dict(Counter(r["status"] for r in records)),
                       "elapsed_seconds": time.monotonic() - started, "native_requests": 0})
            print(json.dumps({"trace": name, "status": record["status"]}), flush=True)
    result = {"records": records, "counts": dict(Counter(r["status"] for r in records)),
              "elapsed_seconds": time.monotonic() - started, "native_requests": 0,
              "authorization_id": authorization_id, "automatic_reruns": 0}
    result["continuation_of"] = str(continue_from) if continue_from else None
    write_json(output / "results.json", result)
    return result
