"""R14 H1-only runner:24 frozen cases, synthetic input, no runtime services."""
import argparse
import ast
import _thread
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback
import unittest


PROJECT = Path(__file__).absolute().parent.parent
R13 = PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r13"
R14 = PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r14"
ARTIFACT_ROOT = PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r13_h1_offline"
FIXTURES = PROJECT / "tests/fixtures/dsat_authority_read_host"
SOURCES = [PROJECT / "src/auth_lifecycle/online_state/dsat_authority_read_host.py",
           PROJECT / "tests/test_dsat_authority_read_host.py", Path(__file__).absolute()]
AUDIT = {"sqlite_attempts": 0, "network_attempts": 0, "process_attempts": 0,
         "private_file_attempts": 0, "unauthorized_write_attempts": 0, "violations": []}
SECRETS = []
sys.dont_write_bytecode = True


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    path = Path(path).absolute()
    if not path.is_relative_to(ARTIFACT_ROOT):
        raise RuntimeError("HOST_ISOLATION_BLOCKED")
    for part in (path, *path.parents):
        if part.exists() and (part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise RuntimeError("HOST_ISOLATION_BLOCKED")
    if path.resolve() != path:
        raise RuntimeError("HOST_ISOLATION_BLOCKED")
    return path


def deny(kind):
    AUDIT[kind] += 1
    AUDIT["violations"].append("HOST_ISOLATION_BLOCKED")
    raise RuntimeError("HOST_ISOLATION_BLOCKED")


def audit(event, args):
    if event.startswith("sqlite3.connect"):
        deny("sqlite_attempts")
    if event.startswith("socket."):
        deny("network_attempts")
    if event in {"subprocess.Popen", "os.system", "os.startfile", "os.exec", "os.fork"}:
        deny("process_attempts")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        raw = os.fsdecode(args[0])
        path = Path(raw).absolute()
        normalized = raw.replace("\\", "/").lower()
        if ("/.runtime/" in normalized or "/secure/" in normalized
                or path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".key", ".aes", ".pem", ".pfx"}):
            deny("private_file_attempts")
        mode, flags = args[1], args[2]
        writing = (type(mode) is str and any(c in mode for c in "wax+")) or (
            type(flags) is int and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not path.is_relative_to(ARTIFACT_ROOT):
            deny("unauthorized_write_attempts")
    if event in {"os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.rename", "os.link", "os.symlink"}:
        paths = args[:2] if event in {"os.rename", "os.link", "os.symlink"} else args[:1]
        for raw in paths:
            if isinstance(raw, (str, bytes, os.PathLike)) and not Path(os.fsdecode(raw)).absolute().is_relative_to(ARTIFACT_ROOT):
                deny("unauthorized_write_attempts")


def write(path, data):
    artifact(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sanitized(text):
    for value in SECRETS:
        text = text.replace(value, "[REDACTED_SYNTHETIC_CANARY]")
    return text


def preflight():
    approval = load(R14 / "APPROVAL_RECEIPT.json")
    if approval["approved"] is not True or approval["scope"] != "R13 four new targets and24 H1 synthetic offline cases only":
        raise RuntimeError("H1_APPROVAL_REQUIRED")
    if sha(Path(approval["request_path"])) != approval["request_sha256"]:
        raise RuntimeError("H1_APPROVAL_SOURCE_CHANGED")
    auth, plan = load(R13 / "H1_H2_AUTHORIZATION_REQUEST.json"), load(R13 / "REAL_READONLY_TEST_PLAN.json")
    baseline = load(R14 / "sources/PRECHECK_LOCK.json")
    for entry in baseline["checks"]:
        if sha(Path(entry["path"])) != entry["expected"]:
            raise RuntimeError("PROTECTED_SOURCE_OR_HISTORY_CHANGED")
    expected_command = [sys.executable, "-B", str(Path(__file__).absolute())]
    if auth["H1"]["command"] != expected_command or approval["command"] != expected_command:
        raise RuntimeError("FROZEN_COMMAND_MISMATCH")
    if sys.version_info[:3] != (3, 12, 14):
        raise RuntimeError("FROZEN_INTERPRETER_VERSION_MISMATCH")
    interpreter = load(R13 / "SOURCE_LOCK.json")["interpreter"]
    if sha(Path(sys.executable)) != interpreter["sha256"]:
        raise RuntimeError("FROZEN_INTERPRETER_HASH_MISMATCH")
    if [x["id"] for x in plan["H1"]["cases"]] != ["H%02d" % i for i in range(1, 25)]:
        raise RuntimeError("FROZEN24_SCOPE_CHANGED")
    if auth["H1"]["new_paths"] != [str(SOURCES[0]), str(SOURCES[1]), str(FIXTURES), str(SOURCES[2])]:
        raise RuntimeError("FROZEN_FOUR_TARGETS_CHANGED")
    for source in SOURCES[:2]:
        tree = ast.parse(source.read_text(encoding="utf-8"))
        imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        forbidden = {"storage", "services", "sqlite3", "native_provider", "native_http", "lab", "networkx"}
        if any(set(name.split(".")) & forbidden for name in imports):
            raise RuntimeError("HOST_ISOLATION_BLOCKED")
    return plan, baseline


class Results(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows, self.started, self.redactions = [], 0, 0

    def startTest(self, test):
        self.started = time.perf_counter_ns()
        super().startTest(test)

    def _exc_info_to_string(self, err, test):
        text = super()._exc_info_to_string(err, test)
        self.redactions += sum(text.count(value) for value in SECRETS)
        return sanitized(text)

    def record(self, test, status, detail=None):
        row = {"id": test._testMethodName.split("_")[1], "status": status, "executed": True,
               "elapsed_ns": time.perf_counter_ns() - self.started}
        if detail:
            row["detail"] = sanitized(detail)
        self.rows.append(row)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, "FAIL", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, "ERROR", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "SKIP", reason)


def main():
    start = time.perf_counter_ns()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    plan, baseline = preflight()
    artifact(ARTIFACT_ROOT).mkdir(exist_ok=True)
    index = 1
    while (ARTIFACT_ROOT / ("run_%03d" % index)).exists():
        index += 1
    run = artifact(ARTIFACT_ROOT / ("run_%03d" % index))
    run.mkdir()
    inputs = [{"path": str(path), "sha256": sha(path)} for path in sorted(FIXTURES.glob("*.json"))]
    code = [{"path": str(path), "sha256": sha(path)} for path in SOURCES]
    SECRETS.extend(load(FIXTURES / "CANARIES.json")["values"].values())
    snapshot = run / "code_snapshot"
    snapshot.mkdir()
    for path in SOURCES:
        (snapshot / (path.name + ".txt")).write_bytes(path.read_bytes())
    write(run / "RUN_START.json", {"argv": sys.orig_argv, "sys_argv": sys.argv, "python": sys.version,
          "command": [sys.executable, "-B", str(Path(__file__).absolute())], "date_china": "2026-11-11",
          "started_utc": started, "code": code, "inputs": inputs, "scope": "R13 H01-H24 only"})
    timer = threading.Timer(max(.01, 120 - (time.perf_counter_ns() - start) / 1e9), _thread.interrupt_main)
    timer.daemon = True
    timer.start()
    try:
        sys.path.insert(0, str(PROJECT / "src"))
        name = "test_dsat_authority_read_host"
        spec = importlib.util.spec_from_file_location(name, SOURCES[1])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        module.configure(plan, FIXTURES)
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.H1Cases)
        actual_ids = sorted(test._testMethodName.split("_")[1] for test in suite)
        if actual_ids != [x["id"] for x in plan["H1"]["cases"]]:
            raise RuntimeError("FROZEN24_EXECUTABLE_SCOPE_MISMATCH")
        with (run / "stdout.log").open("w", encoding="utf-8") as stream:
            actual = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Results).run(suite)
        rows = {row["id"]: row for row in actual.rows}
        cases = [{**rows.get(original["id"], {"id": original["id"], "status": "NOT_RUN", "executed": False}),
                  "R13_original_case": original} for original in plan["H1"]["cases"]]
        counts = {key: sum(row["status"] == key for row in cases) for key in ("PASS", "FAIL", "ERROR", "SKIP", "NOT_RUN")}
        preflight()
        if any(sha(Path(row["path"])) != row["sha256"] for row in code + inputs):
            raise RuntimeError("H1_INPUT_OR_CODE_CHANGED_DURING_RUN")
        sink = (run / "stdout.log").read_text(encoding="utf-8") + json.dumps(module.DETAILS, ensure_ascii=True)
        clean = all(value not in sink for value in SECRETS)
        result = {"schema": "r14-h1-actual-results/1", "date_china": "2026-11-11", "run": str(run),
                  "started_utc": started, "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "argv": sys.orig_argv, "python": sys.version, "elapsed_ns": time.perf_counter_ns() - start,
                  "frozen_denominator": 24, "executed": len(actual.rows), "counts": counts, "cases": cases,
                  "details": module.DETAILS, "additional_tests": {"executed": 0, "counts": {}},
                  "code_hashes": code, "fixture_hashes": inputs, "protected_comparisons": len(baseline["checks"]),
                  "scope_audit": AUDIT, "public_sink_scan": "CLEAN" if clean else "FAIL",
                  "failure_log_redactions": actual.redactions, "old_tests_rerun": 0,
                  "real_authority_reads": 0, "real_key_loads": 0, "production_writes": 0,
                  "H2_operations": 0, "S3B2_operations": 0, "S5_operations": 0}
        result["passed_authorized_scope"] = counts == {"PASS": 24, "FAIL": 0, "ERROR": 0, "SKIP": 0, "NOT_RUN": 0} and clean and not AUDIT["violations"]
        write(run / "RESULTS.json", result)
        write(run / "HOST_SUMMARY_SCHEMA.json", hostmod_schema(module))
    except BaseException:
        write(run / "EARLY_FAILURE.json", {"status": "EARLY_FAILURE", "traceback": sanitized(traceback.format_exc()), "scope_audit": AUDIT})
        raise
    finally:
        timer.cancel()
    path = ARTIFACT_ROOT / "TEST_RUNS.json"
    history = load(path) if path.exists() else {"schema": "r14-h1-runs/1", "runs": []}
    history["runs"].append({"path": str(run / "RESULTS.json"), "sha256": sha(run / "RESULTS.json"),
                            "counts": counts, "passed": result["passed_authorized_scope"]})
    write(path, history)
    print(json.dumps({"run": str(run), "counts": counts, "passed_authorized_scope": result["passed_authorized_scope"]}))
    return 0 if result["passed_authorized_scope"] else 1


def hostmod_schema(module):
    return module.hostmod.summary_schema()


if __name__ == "__main__":
    sys.addaudithook(audit)
    argparse.ArgumentParser(description=__doc__).parse_args()
    raise SystemExit(main())
