"""Run ONLY the two R06-authorized offline modules and retain immutable records."""
import argparse
import ast
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys
from time import perf_counter_ns
import traceback
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEST_MODULES = ("test_dsat_projection", "test_dsat_certificate")
AUDIT_PATHS = (
    "src/auth_lifecycle/__init__.py", "src/auth_lifecycle/online_state/__init__.py",
    "src/auth_lifecycle/online_state/dsat_types.py",
    "src/auth_lifecycle/online_state/dsat_projection.py",
    "src/auth_lifecycle/online_state/dsat_flow.py",
    "scripts/check_dsat_certificate.py", "tests/dsat_test_support.py",
    "tests/test_dsat_projection.py", "tests/test_dsat_certificate.py",
)
ALLOWED_IMPORTS = {"argparse", "ast", "copy", "dataclasses", "hashlib", "importlib", "json", "pathlib",
                   "re", "socket", "time", "tracemalloc", "unittest", "dsat_test_support", "dsat_types",
                   "auth_lifecycle", "sys"}


def preflight():
    audit = []
    for name in AUDIT_PATHS:
        p = ROOT / name
        raw = p.read_bytes()
        tree = ast.parse(raw.decode("utf-8-sig"))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        for module in imported:
            if module == "networkx" and name == "src/auth_lifecycle/online_state/dsat_flow.py":
                continue  # R07 approved pinned backend; checker and S1 remain isolated.
            if module.split(".")[0] not in ALLOWED_IMPORTS:
                raise RuntimeError("UNAPPROVED_IMPORT")
            if any(bad in module.split(".") for bad in ("storage", "services", "native_provider", "native_http")):
                raise RuntimeError("RUNTIME_IMPORT_BLOCKED")
        audit.append({"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "imports": imported})
    for p in sorted((ROOT / "tests" / "fixtures" / "dsat").glob("*.json")):
        audit.append({"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    return audit


class Tee:
    def __init__(self, file):
        self.file = file

    def write(self, text):
        self.file.write(text)
        sys.stdout.write(text)

    def flush(self):
        self.file.flush()
        sys.stdout.flush()


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = {}

    def startTest(self, test):
        self.records[test.id()] = {"test": test.id(), "status": "RUNNING", "started_ns": perf_counter_ns()}
        super().startTest(test)

    def addSuccess(self, test):
        self.records[test.id()]["status"] = "PASS"
        super().addSuccess(test)

    def addFailure(self, test, err):
        self.records[test.id()].update(status="FAIL", traceback=self._exc_info_to_string(err, test))
        super().addFailure(test, err)

    def addError(self, test, err):
        self.records[test.id()].update(status="ERROR", traceback=self._exc_info_to_string(err, test))
        super().addError(test, err)

    def addSkip(self, test, reason):
        self.records[test.id()].update(status="SKIP", reason=reason)
        super().addSkip(test, reason)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self.records[test.id()].update(status="FAIL", traceback=self._exc_info_to_string(err, test))
        super().addSubTest(test, subtest, err)

    def stopTest(self, test):
        rec = self.records[test.id()]
        rec["elapsed_ns"] = perf_counter_ns() - rec.pop("started_ns")
        super().stopTest(test)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-root", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    parent = Path(args.records_root).resolve()
    allowed = (ROOT.parent / "research_g2_dsat_implementation").resolve()
    if not parent.is_relative_to(allowed) or not re.fullmatch(r"run_[0-9]{3}", args.run_id):
        raise SystemExit("RECORD_PATH_OUT_OF_SCOPE")
    directory = parent / "runs" / args.run_id
    directory.mkdir(parents=True, exist_ok=False)
    command = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]
    started = perf_counter_ns()
    record = {"schema": "dsat-offline-run/1", "command": command, "cwd": str(Path.cwd()),
              "python": sys.version, "test_modules": list(TEST_MODULES), "native_calls": 0,
              "source_mode": "SYNTHETIC_CONTRACT", "optimizer_executed": False}
    with (directory / "stdout.log").open("w", encoding="utf-8") as logfile:
        try:
            record["preflight"] = preflight()
            sys.path.insert(0, str(ROOT / "src"))
            sys.path.insert(0, str(ROOT / "tests"))
            modules = [importlib.import_module(name) for name in TEST_MODULES]
            for module, name in zip(modules, TEST_MODULES):
                if Path(module.__file__).resolve() != (ROOT / "tests" / (name + ".py")).resolve():
                    raise RuntimeError("TEST_MODULE_PATH_MISMATCH")
            suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(module) for module in modules)
            result = unittest.TextTestRunner(stream=Tee(logfile), verbosity=2, resultclass=RecordedResult).run(suite)
            records = list(result.records.values())
            counts = {status: sum(r["status"] == status for r in records) for status in ("PASS", "FAIL", "ERROR", "SKIP")}
            record.update(test_count=result.testsRun, counts=counts, tests=records,
                          successful=result.wasSuccessful(),
                          scope="approved pure S1/S2 optimization and independent synthetic proof checking only")
            support = importlib.import_module("dsat_test_support")
            flow_module = importlib.import_module("auth_lifecycle.online_state.dsat_flow")
            record["backend_metadata"] = flow_module.backend_status()
            record["backend"] = record["backend_metadata"]["status"]
            record["optimizer_executed"] = any(
                any(call.startswith("network_simplex:") for call in metric["backend_calls"])
                for row in support.CASE_RESULTS.values() for metric in row.get("automatic_solver_metrics", []))
            (directory / "CASE_RESULTS.json").write_text(json.dumps(support.CASE_RESULTS, indent=2) + "\n", encoding="utf-8")
            proofs = directory / "proofs"
            proofs.mkdir()
            proof_files = []
            for name, packet in sorted(support.CORE_PACKETS.items()):
                p = proofs / (name + ".json")
                p.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
                proof_files.append({"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size})
            record["proof_files"] = proof_files
            code = 0 if result.wasSuccessful() else 1
        except Exception:
            trace = traceback.format_exc()
            Tee(logfile).write(trace)
            record.update(successful=False, preflight_or_import_error=trace,
                          test_count=0, counts={"PASS": 0, "FAIL": 0, "ERROR": 1, "SKIP": 0})
            code = 2
    record["C_total_offline_ns"] = perf_counter_ns() - started
    (directory / "RUN_RESULT.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run": str(directory), "counts": record["counts"], "successful": record["successful"]}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
