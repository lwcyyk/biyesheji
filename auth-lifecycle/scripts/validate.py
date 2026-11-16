"""Reproducible validation. Creates a NEW output directory, preserves failures."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
from dataclasses import asdict
import argparse, json, os, platform, subprocess, sys, unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from auth_lifecycle import __version__, candidate, reference
from auth_lifecycle.fixtures import regression_cases
from auth_lifecycle.certificates import produce
from auth_lifecycle.checker import check_policy, check_impossibility
from auth_lifecycle.schema import Status, canonical


def hash_sources():
    return {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p.read_bytes()).hexdigest()
            for p in sorted(ROOT.rglob("*")) if p.is_file() and "results" not in p.relative_to(ROOT).parts
            and (p.suffix in {".py", ".toml", ".ps1"} or (p.suffix == ".json" and "examples" in p.relative_to(ROOT).parts))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=False)
    os.environ["AUTH_L0_RESULT_DIR"] = str(out)
    started = datetime.now(timezone.utc).isoformat()
    manifest = hash_sources()
    (out/"source_hashes.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        git = subprocess.run(["git", "-C", str(ROOT), "status", "--short", "--branch"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        git_info = {"git_exit": git.returncode, "git_stdout": git.stdout, "git_stderr": git.stderr}
    except FileNotFoundError:
        git_info = {"git_exit": None, "git_stdout": "", "git_stderr": "git executable unavailable"}
    environment = {"version": __version__, "python": sys.version, "platform": platform.platform(),
                   "started_utc": started, "command": [sys.executable, str(Path(__file__).resolve()), "--out", str(out)],
                   **git_info,
                   "source_bundle_sha256": sha256(canonical(manifest).encode()).hexdigest(),
                   "formal_experiments_H_A_H_B_H_AB": "NOT_RUN"}
    (out/"environment.json").write_text(json.dumps(environment, ensure_ascii=False, indent=2), encoding="utf-8")
    events = []

    class RecordingResult(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test); events.append({"test": test.id(), "status": "PASS"})
        def addFailure(self, test, err):
            super().addFailure(test, err); events.append({"test": test.id(), "status": "FAIL", "detail": self._exc_info_to_string(err,test)})
        def addError(self, test, err):
            super().addError(test, err); events.append({"test": test.id(), "status": "ERROR", "detail": self._exc_info_to_string(err,test)})
        def addSkip(self, test, reason):
            super().addSkip(test, reason); events.append({"test": test.id(), "status": "NOT_RUN", "reason": reason})
        def addSubTest(self, test, subtest, err):
            super().addSubTest(test, subtest, err)
            if err:events.append({"test": subtest.id(), "status": "FAIL", "detail": self._exc_info_to_string(err,test)})

    with (out/"unittest.log").open("w", encoding="utf-8") as log:
        suite = unittest.defaultTestLoader.discover(str(ROOT/"tests"))
        result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=RecordingResult).run(suite)
    (out/"tests.json").write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
    inputs = out/"inputs"; inputs.mkdir()
    artifacts = out/"artifacts"; artifacts.mkdir()
    rows = []
    for name, spec, expected in regression_cases():
        (inputs/f"{name}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        c, r = candidate.solve(spec), reference.solve(spec)
        check = None; certificate = None
        if c.status is Status.FEASIBLE:check = asdict(check_policy(spec, c.policy))
        elif c.status is Status.IMPOSSIBLE:
            _, certificate, _ = produce(spec)
            check = asdict(check_impossibility(spec, certificate))
        payload = {"case_id": name, "expected": expected, "candidate": asdict(c), "reference": asdict(r),
                   "check": check, "certificate": certificate}
        (artifacts/f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        rows.append({"case_id": name, "expected": expected, "candidate": c.status.value, "reference": r.status.value,
                     "check": check["verdict"] if check else "NOT_APPLICABLE",
                     "matches": c.status.value == expected == r.status.value and (check is None or check["verdict"] == "ACCEPTED")})
    (out/"regressions.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    from auth_lifecycle.fixtures import stay_finish, declared_regime_change
    from auth_lifecycle.schema import prepare, refs_json
    from auth_lifecycle.semantics import observe, terminal
    demo_model = stay_finish(horizon=8); current = prepare(demo_model)[1]; progress = []
    for _ in range(demo_model["horizon"]):
        if terminal(demo_model, current):break
        status, menu = candidate.allowed_actions(demo_model, current)
        if not menu:break
        picked = "stay" if "stay" in menu else "finish"
        progress.append({"remaining_before": current.remaining, "menu_status": status, "allowed": menu, "chosen": picked})
        current = observe(demo_model, current, picked, "same" if picked == "stay" else "finished")
    (out/"progress_demo.json").write_text(json.dumps({"input":demo_model,"legacy_cycle":["s","stay","s"],
        "unranked_possible_completion_does_not_force_progress":True,"bounded_trace":progress,
        "actual_terminal":terminal(demo_model,current),"remaining_after":current.remaining},ensure_ascii=False,indent=2),encoding="utf-8")
    bm = declared_regime_change(); after = observe(bm,prepare(bm)[1],"probe","unregistered-v3")
    boundary_record = {"input":bm,"action":"probe","observed":"unregistered-v3","expected":"UNKNOWN",
        "updated_belief":refs_json(after.knowledge),"remaining":after.remaining,"boundary":after.boundary,
        "candidate":asdict(candidate.solve(bm,knowledge=after.knowledge,horizon=after.remaining,boundary=after.boundary)),
        "reference":asdict(reference.solve(bm,knowledge=after.knowledge,horizon=after.remaining,boundary=after.boundary))}
    (out/"boundary_demo.json").write_text(json.dumps(boundary_record,ensure_ascii=False,indent=2),encoding="utf-8")
    from auth_lifecycle.controller import BoundedController
    from auth_lifecycle.adapters import TableAdapter
    controller = BoundedController(demo_model); adapter = TableAdapter(demo_model,("w","s"))
    dispatches = [asdict(controller.step("stay",adapter)) for _ in range(7)]
    rejected_last_stay = asdict(controller.step("stay",adapter))
    finish = asdict(controller.step("finish",adapter))
    runtime_demo = {"dispatches":dispatches,"last_stay":rejected_last_stay,"finish":finish,
        "controller_events":controller.events,"actual_adapter_events":adapter.history,
        "actual_state":adapter.audit_state(),"remaining":controller.state.remaining}
    (out/"runtime_progress_demo.json").write_text(json.dumps(runtime_demo,ensure_ascii=False,indent=2),encoding="utf-8")
    history_path = ROOT/"docs"/"audit"/"historical_manifest.json"
    changed = []
    if history_path.exists():
        for relative, expected_hash in json.loads(history_path.read_text(encoding="utf-8")).items():
            original = ROOT.parent/relative
            if not original.is_file() or sha256(original.read_bytes()).hexdigest() != expected_hash:changed.append(relative)
    sources_unchanged = hash_sources() == manifest
    summary = {"version": __version__, "tests_run": result.testsRun,
               "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
               "regression_cases": len(rows), "regression_mismatches": sum(not r["matches"] for r in rows),
               "historical_changes": changed, "sources_unchanged_during_run": sources_unchanged,
               "ended_utc": datetime.now(timezone.utc).isoformat(), "source_bundle_sha256": environment["source_bundle_sha256"],
               "not_run": ["H-A", "H-B", "H-AB", "live OAuth/browser/AI experiments", "machine-checked general proof"]}
    summary["progress_demo_valid"] = terminal(demo_model,current) and len(progress) <= demo_model["horizon"]
    summary["boundary_demo_valid"] = boundary_record["candidate"]["status"] == Status.UNKNOWN and boundary_record["reference"]["status"] == Status.UNKNOWN
    summary["runtime_progress_valid"] = rejected_last_stay["status"] == "REJECTED" and finish["status"] == "COMPLETED" and len(adapter.history) == 8 and controller.state.remaining == 0
    ok = result.wasSuccessful() and not changed and sources_unchanged and all(r["matches"] for r in rows) and summary["progress_demo_valid"] and summary["boundary_demo_valid"] and summary["runtime_progress_valid"]
    summary["status"] = "PASS_FINITE_L0_ONLY" if ok else "FAIL"
    (out/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    if not result.wasSuccessful():print((out/"unittest.log").read_text(encoding="utf-8")[-16000:])
    return 0 if ok else 1


if __name__ == "__main__":raise SystemExit(main())
