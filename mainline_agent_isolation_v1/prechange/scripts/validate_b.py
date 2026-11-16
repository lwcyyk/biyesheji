"""Repeatable development validation. New output directory mandatory; no H-B test."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import sys
from time import perf_counter
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from auth_lifecycle.b import __version__, fixtures, search, baselines, reference, certificates, checker
from auth_lifecycle.schema import canonical


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def hashes():
    files = [p for name in ["src", "scripts", "tests"] for p in (ROOT/name).rglob("*.py")]
    files += list((ROOT/"examples/b").glob("*.json"))
    files += [ROOT/"docs/b/OBJECTIVE_LOCK.json", ROOT/"pyproject.toml"]
    return {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--out", required=True)
    parser.add_argument("--replay-of"); args = parser.parse_args()
    out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=False)
    (out/"inputs").mkdir(); (out/"artifacts").mkdir(); source = hashes(); dump(out/"source_hashes.json", source)
    environment = {"b_version": __version__, "base_version": "0.16.0", "python": sys.version,
                   "platform": platform.platform(), "processor": platform.processor(), "cpu_count": os.cpu_count(),
                   "started_utc": datetime.now(timezone.utc).isoformat(), "command": [sys.executable, *sys.argv],
                   "source_sha256": sha256(canonical(source).encode()).hexdigest(),
                   "git": "not a Git repository; use content hashes", "H_B": "NOT_RUN"}
    dump(out/"environment.json", environment); events = []

    class Recording(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test); events.append({"test": test.id(), "status": "PASS"})
        def addFailure(self, test, err):
            super().addFailure(test, err); events.append({"test": test.id(), "status": "FAIL", "detail": self._exc_info_to_string(err, test)})
        def addError(self, test, err):
            super().addError(test, err); events.append({"test": test.id(), "status": "ERROR", "detail": self._exc_info_to_string(err, test)})
        def addSkip(self, test, reason):
            super().addSkip(test, reason); events.append({"test": test.id(), "status": "NOT_RUN", "reason": reason})
        def addSubTest(self, test, subtest, err):
            super().addSubTest(test, subtest, err)
            if err:events.append({"test": str(subtest), "status": "FAIL", "detail": self._exc_info_to_string(err, test)})

    with (out/"unittest.log").open("w", encoding="utf-8") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Recording).run(
            unittest.defaultTestLoader.discover(str(ROOT/"tests"), pattern="test_b.py"))
    dump(out/"tests.json", events)
    methods = {"B": search.solve, "B-B": baselines.solve, "reference": reference.solve}
    rows = []; timings = []
    for name, model, expected, expected_g in fixtures.cases():
        # Full 16-path, 8-task example belongs to the capped performance profile.
        if name == "eight_task_boundary":continue
        dump(out/"inputs"/(name + ".json"), model)
        payload = {"case": name, "expected_status": expected, "expected_G": expected_g, "methods": {}}
        ok = True
        for method, solve in methods.items():
            start = perf_counter(); value = solve(model); elapsed = perf_counter() - start
            record = asdict(value); check = None
            if value.delivery:check = checker.check_delivery(model, value.delivery)
            payload["methods"][method] = {"result": record, "check": check}
            timings.append({"case": name, "method": method, "seconds": elapsed, "work": value.stats, "status": value.status})
            if method != "B-B":
                ok &= value.status == expected and (expected_g is None or value.metrics["G"] == expected_g)
            elif expected != "FEASIBLE":
                ok &= value.status == ("UNKNOWN" if expected == "UNKNOWN" else "NO_BASELINE_SOLUTION")
            if value.delivery:ok &= check["verdict"] == "ACCEPTED"
        b = payload["methods"]["B"]["result"]; r = payload["methods"]["reference"]["result"]
        ok &= b["configuration"] == r["configuration"]
        if expected == "IMPOSSIBLE":
            conflict = certificates.produce(model); checked = checker.check_conflict(model, conflict["certificate"])
            payload.update(conflict=conflict, conflict_check=checked); ok &= checked["verdict"] == "ACCEPTED"
        if b["configuration"] is not None:payload["G_audit"] = checker.audit_G(model, b["configuration"])
        dump(out/"artifacts"/(name + ".json"), payload)
        rows.append({"case": name, "matches": bool(ok), "B": b["status"], "reference": r["status"],
                     "B_G": b["metrics"]["G"] if b["metrics"] else None,
                     "BB": payload["methods"]["B-B"]["result"]["status"],
                     "BB_G": payload["methods"]["B-B"]["result"]["metrics"]["G"] if payload["methods"]["B-B"]["result"]["metrics"] else None})
    dump(out/"regressions.json", rows); dump(out/"timings.json", timings)
    matrix = []; counts = {}; structural = []
    with (out/"finite_inputs.jsonl").open("w", encoding="utf-8") as inputs, (out/"finite_results.jsonl").open("w", encoding="utf-8") as results:
        for name, m in fixtures.finite_models():
            inputs.write(canonical({"case": name, "model": m}) + "\n")
            b, r, bb = search.solve(m), reference.solve(m), baselines.solve(m)
            ok = b.status == r.status and b.configuration == r.configuration
            if b.status == "FEASIBLE":
                ok &= b.metrics["G"] == r.metrics["G"] == bb.metrics["G"]
                ok &= all(checker.check_delivery(m, d)["verdict"] == "ACCEPTED" for d in [b.delivery, r.delivery, bb.delivery])
            elif b.status == "IMPOSSIBLE":
                proof = certificates.produce(m); verification = checker.check_conflict(m, proof["certificate"])
                ok &= verification["verdict"] == "ACCEPTED"
            row = {"case": name, "matches": bool(ok), "B": asdict(b), "reference": asdict(r), "B-B": asdict(bb)}
            if b.status == "IMPOSSIBLE":row.update(conflict=proof, conflict_check=verification)
            results.write(canonical(row) + "\n"); matrix.append({"case": name, "matches": bool(ok), "status": b.status})
            counts[b.status] = counts.get(b.status, 0) + 1
    dump(out/"finite_summary.json", {"models": len(matrix), "counts": counts, "mismatches": sum(not x["matches"] for x in matrix),
          "scope": "2 tasks; 4 paths; 3 native domains; local/remote x preserve/no-preserve x all-material/refresh-only x 4 approval packs x requests {1,3,8} x H {0,1,2,3}"})
    with (out/"structural.jsonl").open("w", encoding="utf-8") as log:
        for name, m in fixtures.structural_models():
            b, r, bb = search.solve(m), reference.solve(m), baselines.solve(m)
            ok = b.status == r.status and b.configuration == r.configuration
            if b.status == "FEASIBLE":ok &= b.metrics["G"] == r.metrics["G"]
            if bb.status == "FEASIBLE":ok &= b.status == "FEASIBLE" and bb.metrics["G"] >= b.metrics["G"]
            for value in [b, r, bb]:
                if value.delivery:ok &= checker.check_delivery(m, value.delivery)["verdict"] == "ACCEPTED"
            row = {"case": name, "model": m, "B": asdict(b), "reference": asdict(r), "B-B": asdict(bb), "matches": bool(ok)}
            structural.append({"case": name, "matches": bool(ok), "B": b.status, "BB": bb.status,
                               "B_G": b.metrics["G"] if b.metrics else None, "BB_G": bb.metrics["G"] if bb.metrics else None})
            log.write(canonical(row) + "\n")
    dump(out/"structural_summary.json", structural)
    performance = []
    # Fixed development scale sweep. One timing per method; not an inferential sample.
    for n in [2, 4, 6, 8]:
        m = fixtures.local_only(n); dump(out/"inputs"/f"scale_{n}.json", m)
        for method, solve in methods.items():
            start = perf_counter(); value = solve(m, limit=50_000); elapsed = perf_counter() - start
            check = checker.check_delivery(m, value.delivery) if value.delivery else None
            performance.append({"tasks": n, "paths": len(m["paths"]), "catalog_subsets": 2 ** len(m["paths"]),
                                "method": method, "work_limit": 50_000, "seconds": elapsed,
                                "result": asdict(value), "incumbent_check": check})
    dump(out/"performance.json", performance)
    baseline = json.loads((ROOT/"docs/b/v216_baseline_manifest.json").read_text(encoding="utf-8"))
    changed = [p for p, h in baseline.items() if not (ROOT/p).is_file() or sha256((ROOT/p).read_bytes()).hexdigest() != h]
    # README is a current navigation page; accepted source and evidence must remain byte-identical.
    unexpected = [p for p in changed if p != "README.md"]
    summary = {"status": "PASS_FINITE_B_ONLY", "unit_tests": result.testsRun, "failures": len(result.failures),
               "errors": len(result.errors), "skips": len(result.skipped), "regressions": len(rows),
               "regression_mismatches": sum(not x["matches"] for x in rows), "finite_models": len(matrix),
               "finite_mismatches": sum(not x["matches"] for x in matrix), "finite_status_counts": counts,
               "structural_models": len(structural), "structural_mismatches": sum(not x["matches"] for x in structural),
               "v216_manifest_files": len(baseline), "changed_baseline_files": changed,
               "unexpected_baseline_changes": unexpected, "source_unchanged": source == hashes(),
               "source_sha256": environment["source_sha256"], "formal_H_B": "NOT_RUN",
               "not_run": ["L1 native auth adapters", "L2 AI experiments", "formal H-B statistics", "machine-checked general proof"]}
    if not result.wasSuccessful() or unexpected or not summary["source_unchanged"] or summary["regression_mismatches"] or summary["finite_mismatches"] or summary["structural_mismatches"]:summary["status"] = "FAIL"
    if args.replay_of:
        prior = Path(args.replay_of).resolve()
        targets = ["source_hashes.json", "regressions.json", "finite_inputs.jsonl", "finite_results.jsonl", "finite_summary.json", "structural.jsonl", "structural_summary.json"]
        targets += [p.relative_to(out).as_posix() for p in (out/"artifacts").glob("*.json")]
        mismatch = [p for p in targets if not (prior/p).exists() or (prior/p).read_bytes() != (out/p).read_bytes()]
        dump(out/"replay.json", {"prior": str(prior), "compared": len(targets), "mismatch": mismatch, "timing_comparison": "excluded"})
        summary["replay_mismatches"] = mismatch
        if mismatch:summary["status"] = "FAIL"
    dump(out/"summary.json", summary); print(json.dumps(summary, ensure_ascii=False))
    return int(summary["status"] == "FAIL")


if __name__ == "__main__":raise SystemExit(main())
