"""L0 first, then development measurements; never formal H-A/H-AB testing."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys
from time import perf_counter
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from auth_lifecycle.a import __version__, compiler, fixtures, candidate, joint_reference, audit, runtime, ablations
from auth_lifecycle.schema import canonical
from auth_lifecycle.reference import solve as ri


def dump(path, obj):path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_hashes():
    paths = [p for folder in ["src", "scripts", "tests"] for p in (ROOT/folder).rglob("*.py")]
    paths += list((ROOT/"examples/a_ab").glob("*.json")) + [ROOT/"docs/a_ab/DEVELOPMENT_LOCK.json"]
    return {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def methods(bundle, node_limit=100_000):
    return {"A1": lambda: candidate.solve(bundle, node_limit=node_limit),
            "B-A": lambda: candidate.solve(bundle, method="B-A", node_limit=node_limit),
            "AB1": lambda: candidate.solve(bundle, feedback=True, node_limit=node_limit),
            "B-AB": lambda: candidate.solve(bundle, feedback=False, node_limit=node_limit),
            "R-J": lambda: joint_reference.solve(bundle, node_limit=node_limit)}


def main():
    p = argparse.ArgumentParser(); p.add_argument("--out", required=True); p.add_argument("--replay-of")
    args = p.parse_args(); out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=False)
    for folder in ["inputs", "artifacts", "compiled"]:(out/folder).mkdir()
    hashes = source_hashes(); dump(out/"source_hashes.json", hashes)
    environment = {"version": __version__, "python": sys.version, "platform": platform.platform(), "processor": platform.processor(),
                   "started_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
                   "source_sha256": sha256(canonical(hashes).encode()).hexdigest(), "git": "not a Git repository",
                   "formal_H_A_H_AB": "NOT_RUN"}
    dump(out/"environment.json", environment); tests = []

    class Recording(unittest.TextTestResult):
        def addSuccess(self, t):super().addSuccess(t); tests.append({"test": t.id(), "status": "PASS"})
        def addFailure(self, t, e):super().addFailure(t, e); tests.append({"test": t.id(), "status": "FAIL", "detail": self._exc_info_to_string(e, t)})
        def addError(self, t, e):super().addError(t, e); tests.append({"test": t.id(), "status": "ERROR", "detail": self._exc_info_to_string(e, t)})
        def addSkip(self, t, reason):super().addSkip(t, reason); tests.append({"test": t.id(), "status": "NOT_RUN", "reason": reason})
        def addSubTest(self, t, sub, e):
            super().addSubTest(t, sub, e)
            if e:tests.append({"test": str(sub), "status": "FAIL", "detail": self._exc_info_to_string(e, t)})
    with (out/"unittest.log").open("w", encoding="utf-8") as log:
        tested = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Recording).run(unittest.defaultTestLoader.discover(str(ROOT/"tests"), pattern="test_a_ab.py"))
    dump(out/"tests.json", tests)
    if not tested.wasSuccessful():
        summary = {"status": "FAIL_L0_GATE", "tests": tested.testsRun, "failures": len(tested.failures), "errors": len(tested.errors),
                   "development_measurement": "NOT_RUN", "source_sha256": environment["source_sha256"]}
        dump(out/"summary.json", summary); print(json.dumps(summary)); return 1
    regression = []; timing = []; safe = True
    for name, source, expected in fixtures.cases():
        dump(out/"inputs"/(name + ".json"), source)
        started = perf_counter(); compiled = compiler.compile_model(source); compile_seconds = perf_counter() - started
        if compiled.status != "COMPILED":raise RuntimeError(name + ": " + compiled.reason)
        bundle = compiled.bundle; started = perf_counter(); checked = audit.check_compilation(bundle); audit_seconds = perf_counter() - started
        dump(out/"compiled"/(name + ".json"), bundle)
        payload = {"case": name, "expected": expected, "audit": checked, "source_digest": bundle["source_digest"], "results": {}}
        actual_ri = ri(bundle["l0"]); payload["R-I"] = asdict(actual_ri)
        ok = checked["verdict"] == "ACCEPTED" and actual_ri.status.value == expected
        timing.append({"case": name, "compile_seconds": compile_seconds, "audit_seconds": audit_seconds, "concrete_nodes": compiled.nodes})
        for label, run in methods(bundle).items():
            started = perf_counter(); answer = run(); seconds = perf_counter() - started
            started = perf_counter(); scored = runtime.evaluate(bundle, answer); score_seconds = perf_counter() - started
            payload["results"][label] = {"solver": asdict(answer), "metrics": scored}
            timing.append({"case": name, "method": label, "solve_seconds": seconds, "score_seconds": score_seconds, "work": answer.stats})
            ok &= answer.status == expected
            if expected == "FEASIBLE":ok &= scored.get("completion") == 1 and scored["external_requests"] == answer.worst_requests
            ok &= not scored["safety_counterexamples"]
        reference = payload["results"]["R-J"]["solver"]
        for label in ["A1", "B-A", "AB1", "B-AB"]:
            answer = payload["results"][label]["solver"]
            if expected == "FEASIBLE":ok &= answer["worst_requests"] >= reference["worst_requests"]
        ok &= canonical(payload["results"]["A1"]) == canonical(payload["results"]["B-AB"])
        b_only = ablations.no_acquisition(bundle)
        payload["no_acquisition_ablation"] = {"solver": asdict(b_only), "metrics": runtime.evaluate(bundle, b_only), "scope": "restricted policy choices, same available interfaces; not global infeasibility"}
        if name in {"session_side_effect", "opaque_handle_no_cleanup"}:
            payload["obligation_ablation_2x2"] = []
            for feedback in [False, True]:
                diagnostic = ablations.missing_obligation_abstraction(bundle, feedback=feedback)
                diagnostic["controller_result"] = asdict(diagnostic["controller_result"])
                payload["obligation_ablation_2x2"].append(diagnostic)
                ok &= diagnostic["audit"]["verdict"] == "REJECTED" and diagnostic["scorer"]["completion"] == 0 and bool(diagnostic["scorer"]["safety_counterexamples"])
        dump(out/"artifacts"/(name + ".json"), payload)
        row = {"case": name, "expected": expected, "matches": bool(ok), "methods": {}}
        for method, x in payload["results"].items():
            metrics = x["metrics"]
            row["methods"][method] = {key: metrics[key] for key in ["status", "completion", "refusal", "UNKNOWN", "INCONCLUSIVE", "external_requests", "C_Q", "probe_side_effects", "unresolved_obligations"]}
            row["methods"][method]["solver_work"] = x["solver"]["stats"]
        regression.append(row); safe &= bool(ok)
    dump(out/"regressions.json", regression); dump(out/"timings.json", timing)
    finite = []
    with (out/"finite.jsonl").open("w", encoding="utf-8") as log:
        for name, source in fixtures.finite_models():
            c = compiler.compile_model(source)
            if c.status != "COMPILED":raise RuntimeError(name + ": " + c.reason)
            check = audit.check_compilation(c.bundle); expected = ri(c.bundle["l0"]); r = joint_reference.solve(c.bundle)
            values = {label: fn() for label, fn in methods(c.bundle).items() if label != "R-J"}; values["R-J"] = r
            ok = check["verdict"] == "ACCEPTED" and all(v.status == expected.status.value for v in values.values())
            checks = {label: runtime.evaluate(c.bundle, v) for label, v in values.items()}
            for label, v in values.items():
                ok &= not checks[label]["safety_counterexamples"]
                if v.status == "FEASIBLE":ok &= v.worst_requests >= r.worst_requests and checks[label]["completion"] == 1
            row = {"case": name, "source": source, "nodes": c.nodes, "matches": bool(ok), "audit": check,
                   "results": {k: asdict(v) for k, v in values.items()}, "execution": checks}
            log.write(canonical(row) + "\n"); finite.append({"case": name, "matches": bool(ok), "status": r.status,
                       "Q": {k: v.worst_requests for k, v in values.items()}}); safe &= bool(ok)
    dump(out/"finite_summary.json", finite)
    # Cost measurement gate is after the independent finite checks.
    performance = []
    if safe:
        for worlds in [2, 4, 8]:
            s = fixtures.acquisition(nuisance=worlds//2, horizon=4); c = compiler.compile_model(s)
            dump(out/"inputs"/f"scale_{worlds}.json", s)
            for name, run in methods(c.bundle, node_limit=50_000).items():
                started = perf_counter(); result = run(); elapsed = perf_counter() - started
                performance.append({"worlds": worlds, "nodes": c.nodes, "method": name, "solve_seconds": elapsed,
                                    "status": result.status, "worst_requests": result.worst_requests, "work": result.stats,
                                    "execution": runtime.evaluate(c.bundle, result)})
    dump(out/"performance.json", performance)
    limited = compiler.compile_model(fixtures.acquisition()).bundle
    dump(out/"limits.json", {"compile": asdict(compiler.compile_model(fixtures.acquisition(), node_limit=0)),
                             "candidate": asdict(candidate.solve(limited, node_limit=0)), "R-J": asdict(joint_reference.solve(limited, node_limit=0)),
                             "trace": runtime.evaluate(limited, candidate.solve(limited), trace_limit=0)})
    aggregation = {}
    for method in ["A1", "B-A", "AB1", "B-AB", "R-J"]:
        rows = [r["methods"][method] for r in regression]
        aggregation[method] = {"inputs": len(rows), "completed": sum(x["completion"] for x in rows),
            "completion_rate": sum(x["completion"] for x in rows)/len(rows), "refused": sum(x["refusal"] for x in rows),
            "refusal_rate": sum(x["refusal"] for x in rows)/len(rows), "UNKNOWN": sum(x["UNKNOWN"] for x in rows),
            "INCONCLUSIVE": sum(x["INCONCLUSIVE"] for x in rows),
            "requests_by_input": [x["external_requests"] for x in rows], "C_Q_by_input": [x["C_Q"] for x in rows],
            "probe_side_effects_sum_of_case_maxima": sum(x["probe_side_effects"] for x in rows),
            "unresolved_obligations": sum(x["unresolved_obligations"] for x in rows),
            "interpretation": "descriptive robust completion per declared synthetic input; not a population rate or statistical test"}
    dump(out/"metrics.json", aggregation)
    baseline = json.loads((ROOT/"docs/a_ab/baseline_manifest.json").read_text(encoding="utf-8"))
    changed = [name for name, h in baseline.items() if not (ROOT/name).is_file() or sha256((ROOT/name).read_bytes()).hexdigest() != h]
    summary = {"status": "PASS_FINITE_A_AB_ONLY" if safe and not changed and hashes == source_hashes() else "FAIL",
               "tests": tested.testsRun, "failures": len(tested.failures), "errors": len(tested.errors), "skipped": len(tested.skipped),
               "named_cases": len(regression), "named_mismatches": sum(not x["matches"] for x in regression),
               "finite_models": len(finite), "finite_mismatches": sum(not x["matches"] for x in finite),
               "fixed_baseline_files": len(baseline), "baseline_changes": changed, "source_unchanged": hashes == source_hashes(),
               "source_sha256": environment["source_sha256"], "formal_H_A_H_AB": "NOT_RUN",
               "not_run": ["real OAuth/browser/AI deployment", "machine-checked general abstraction proof", "formal H-A/H-AB statistics"]}
    if args.replay_of:
        old = Path(args.replay_of).resolve(); targets = ["source_hashes.json", "regressions.json", "finite.jsonl", "finite_summary.json", "metrics.json", "limits.json"]
        targets += [p.relative_to(out).as_posix() for p in (out/"artifacts").glob("*.json")]
        mismatch = [name for name in targets if not (old/name).exists() or (old/name).read_bytes() != (out/name).read_bytes()]
        dump(out/"replay.json", {"prior": str(old), "compared": len(targets), "mismatches": mismatch, "timings": "excluded"})
        summary["replay_mismatches"] = mismatch
        if mismatch:summary["status"] = "FAIL"
    dump(out/"summary.json", summary); print(json.dumps(summary, ensure_ascii=False))
    return int(summary["status"] != "PASS_FINITE_A_AB_ONLY")


if __name__ == "__main__":raise SystemExit(main())
