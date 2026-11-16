"""R16: A01-A20 plus unchanged H01-H24; owned memory SQLite and no live access."""
import argparse
import ast
import _thread
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys
import threading
import time
import traceback
import unittest


PROJECT = Path(__file__).absolute().parent.parent
R15 = PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r15"
RECORD = PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r16"
ARTIFACT = PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r15_activation_offline"
FIXTURE = PROJECT / "tests/fixtures/dsat_authority_host_activation"
OLD_FIXTURE = PROJECT / "tests/fixtures/dsat_authority_read_host"
OLD_TEST = PROJECT / "tests/test_dsat_authority_read_host.py"
SOURCES = [PROJECT / "src/auth_lifecycle/online_state/services.py",
    PROJECT / "src/auth_lifecycle/online_state/dsat_authority_read_host.py",
    PROJECT / "src/auth_lifecycle/online_state/dsat_authority_host_activation.py",
    PROJECT / "scripts/read_dsat_authority_once.py",
    PROJECT / "tests/test_dsat_authority_host_activation.py", Path(__file__).absolute()]
AUDIT = {"memory_connections": 0, "forbidden_SQLite": 0, "network": 0, "process": 0,
         "private_file": 0, "outside_write": 0, "forbidden_SQL": 0, "violations": []}
OWNED, SECRETS = [], []
REGISTRATION_EVENTS = []
PHASE = "PREFLIGHT"
sys.dont_write_bytecode = True


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def redact(text):
    for value in SECRETS:
        text = text.replace(value, "[REDACTED_SYNTHETIC_CANARY]")
    return text


def checked(path):
    path = Path(path).absolute()
    if not path.is_relative_to(ARTIFACT):
        raise RuntimeError("ARTIFACT_PATH_DENIED")
    for part in (path, *path.parents):
        if part.exists() and (part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise RuntimeError("ARTIFACT_REPARSE_DENIED")
    if path.resolve() != path:
        raise RuntimeError("ARTIFACT_PATH_DENIED")
    return path


def write(path, data):
    checked(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def deny(kind):
    AUDIT[kind] += 1
    AUDIT["violations"].append("A1_ISOLATION_BLOCKED")
    raise RuntimeError("A1_ISOLATION_BLOCKED")


def audit(event, args):
    if event == "sqlite3.connect":
        if PHASE != "A1" or args[0] != ":memory:" or AUDIT["memory_connections"] >= 32:
            deny("forbidden_SQLite")
        AUDIT["memory_connections"] += 1
    if event in {"sqlite3.enable_load_extension", "sqlite3.load_extension"}:
        deny("forbidden_SQL")
    if event.startswith("socket."):
        deny("network")
    if event in {"subprocess.Popen", "os.system", "os.startfile", "os.fork", "os.exec"}:
        deny("process")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        raw = os.fsdecode(args[0])
        path = Path(raw).absolute()
        norm = raw.replace("\\", "/").lower()
        if "/.runtime/" in norm or "/secure/" in norm or path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".key", ".pem", ".pfx", ".aes"}:
            deny("private_file")
        mode, flags = args[1], args[2]
        writing = (type(mode) is str and any(c in mode for c in "wax+")) or (
            type(flags) is int and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not path.is_relative_to(ARTIFACT):
            deny("outside_write")
    if event in {"os.mkdir", "os.remove", "os.rmdir", "os.rename", "os.chmod", "os.link", "os.symlink"}:
        values = args[:2] if event in {"os.rename", "os.link", "os.symlink"} else args[:1]
        for value in values:
            if isinstance(value, (str, bytes, os.PathLike)) and not Path(os.fsdecode(value)).absolute().is_relative_to(ARTIFACT):
                deny("outside_write")


def connect_memory():
    connection = sqlite3.connect(":memory:", check_same_thread=False, isolation_level=None)
    connection.row_factory = sqlite3.Row
    def guard(action, arg1, arg2, database, trigger):
        if action in {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH} or (
                action == sqlite3.SQLITE_FUNCTION and str(arg2).lower() == "load_extension"):
            deny("forbidden_SQL")
        return sqlite3.SQLITE_OK
    connection.set_authorizer(guard)
    OWNED.append(connection)
    return connection


def preflight():
    approval = load(RECORD / "APPROVAL_RECEIPT.json")
    if approval["approved"] is not True or not approval["no_real_runtime"]:
        raise RuntimeError("A1_APPROVAL_REQUIRED")
    if sha(Path(approval["request_path"])) != approval["request_sha256"]:
        raise RuntimeError("APPROVAL_CHANGED")
    plan = load(R15 / "H2_HOST_ACTIVATION_PLAN.json")
    if plan["A1"]["command_proposed"] != [sys.executable, "-B", str(Path(__file__).absolute())]:
        raise RuntimeError("FROZEN_COMMAND_CHANGED")
    if sys.version_info[:3] != (3, 12, 14):
        raise RuntimeError("FROZEN_PYTHON_VERSION_CHANGED")
    baseline = load(RECORD / "sources/PRECHECK_LOCK.json")
    changed = {row["path"]: row for row in baseline["allowed_modifications"]}
    for row in changed.values():
        if sha(Path(row["snapshot"])) != row["before_sha256"]:
            raise RuntimeError("ORIGINAL_BYTES_LOST")
    exceptions = 0
    for row in baseline["checks"]:
        if row["path"] in changed:
            if row["expected"] != changed[row["path"]]["before_sha256"]:
                raise RuntimeError("UNRECOGNIZED_OLD_VERSION")
            exceptions += 1
        elif sha(Path(row["path"])) != row["expected"]:
            raise RuntimeError("PROTECTED_HISTORY_CHANGED")
    if [x["id"] for x in plan["A1"]["new_tests"]] != ["A%02d" % i for i in range(1, 21)]:
        raise RuntimeError("FROZEN_NEW20_CHANGED")
    for path in (SOURCES[1], SOURCES[2], SOURCES[3], SOURCES[4]):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        forbidden = {"services", "storage", "materials", "cryptography", "lab", "native_provider", "native_http"}
        if any(set(name.split(".")) & forbidden for name in imports):
            raise RuntimeError("RUNTIME_IMPORT_REFINEMENT_GAP")
    return plan, baseline, exceptions


class Results(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows, self.started = [], 0

    def startTest(self, test):
        self.started = time.perf_counter_ns()
        super().startTest(test)

    def _exc_info_to_string(self, err, test):
        return redact(super()._exc_info_to_string(err, test))

    def record(self, test, status, detail=None):
        row = {"id": test._testMethodName.split("_")[1], "status": status, "executed": True,
               "elapsed_ns": time.perf_counter_ns() - self.started}
        if detail:
            row["detail"] = redact(detail)
        self.rows.append(row)

    def addSuccess(self, test):
        super().addSuccess(test); self.record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err); self.record(test, "FAIL", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err); self.record(test, "ERROR", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason); self.record(test, "SKIP", reason)


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_group(cls, count, stream):
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
    if suite.countTestCases() != count:
        raise RuntimeError("FROZEN_TEST_COUNT_CHANGED")
    return unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Results).run(suite)


def main():
    global PHASE
    start = time.perf_counter_ns()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    plan, baseline, exceptions = preflight()
    checked(ARTIFACT).mkdir(exist_ok=True)
    index = 1
    while (ARTIFACT / ("run_%03d" % index)).exists():
        index += 1
    run = checked(ARTIFACT / ("run_%03d" % index)); run.mkdir()
    code = [{"path": str(p), "sha256": sha(p)} for p in SOURCES]
    fixtures = [{"path": str(p), "sha256": sha(p)} for p in sorted(FIXTURE.glob("*.json"))]
    old_inputs = [{"path": str(p), "sha256": sha(p)} for p in sorted(OLD_FIXTURE.glob("*.json"))]
    for root in (FIXTURE, OLD_FIXTURE):
        SECRETS.extend(load(root / "CANARIES.json")["values"].values() if root == FIXTURE
                       else load(root / "CANARIES.json")["values"].values())
    snap = run / "code_snapshot"; snap.mkdir()
    for p in SOURCES:
        (snap / (p.name + ".txt")).write_bytes(p.read_bytes())
    write(run / "RUN_START.json", {"argv": sys.orig_argv, "python": sys.version, "sqlite": sqlite3.sqlite_version,
          "date_china": "2026-11-11", "started_utc": started, "code": code,
          "fixtures": fixtures, "H1_inputs": old_inputs, "original_H1_test_sha256": sha(OLD_TEST)})
    timer = threading.Timer(max(.01, 120 - (time.perf_counter_ns() - start) / 1e9), _thread.interrupt_main)
    timer.daemon = True; timer.start()
    try:
        sys.path.insert(0, str(PROJECT / "src"))
        new = module_at("a1_activation_cases", SOURCES[4])
        new.configure(plan, FIXTURE, connect_memory)
        original_mount = new.a.mount_authority_host
        def observed_mount(*args, **kwargs):
            t = time.perf_counter_ns()
            outcome = "REFUSED"
            try:
                value = original_mount(*args, **kwargs)
                outcome = "DISABLED" if value is None else "MOUNTED"
                return value
            finally:
                REGISTRATION_EVENTS.append({"outcome": outcome, "elapsed_ns": time.perf_counter_ns() - t})
        new.a.mount_authority_host = observed_mount
        with (run / "stdout.log").open("w", encoding="utf-8") as log:
            PHASE = "A1"
            first = run_group(new.ActivationCases, 20, log)
            new.a.mount_authority_host = original_mount
            for connection in OWNED:
                connection.close()
            PHASE = "H1"
            old = module_at("a1_unchanged_h1_cases", OLD_TEST)
            old.configure(load(PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r13/REAL_READONLY_TEST_PLAN.json"), OLD_FIXTURE)
            second = run_group(old.H1Cases, 24, log)
        PHASE = "POSTCHECK"
        preflight()
        if any(sha(Path(row["path"])) != row["sha256"] for row in code + fixtures + old_inputs):
            raise RuntimeError("INPUT_OR_CODE_CHANGED_DURING_RUN")
        rows = first.rows + second.rows
        original = {x["id"]: x for x in plan["A1"]["new_tests"]}
        original.update({x["id"]: x for x in load(PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r13/REAL_READONLY_TEST_PLAN.json")["H1"]["cases"]})
        cases = [{**row, "original_spec": original[row["id"]]} for row in rows]
        counts = lambda group: {status: sum(x["status"] == status for x in group) for status in ("PASS", "FAIL", "ERROR", "SKIP")}
        sink = (run / "stdout.log").read_text(encoding="utf-8") + json.dumps(new.DETAILS) + json.dumps(old.DETAILS)
        clean = all(value not in sink for value in SECRETS)
        result = {"schema": "r16-a1-actual-results/1", "run": str(run), "date_china": "2026-11-11",
             "started_utc": started, "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "argv": sys.orig_argv, "python": sys.version, "sqlite_version": sqlite3.sqlite_version,
             "elapsed_ns": time.perf_counter_ns() - start, "A1_NEW_TESTS": 20, "H1_REGRESSION_TESTS": 24,
             "new_counts": counts(first.rows), "H1_counts": counts(second.rows), "counts": counts(rows),
             "executed": len(rows), "cases": cases, "A1_details": new.DETAILS, "H1_details": old.DETAILS,
             "registration_events": REGISTRATION_EVENTS,
             "code_hashes": code, "fixture_hashes": fixtures, "H1_fixture_hashes": old_inputs,
             "protected_comparisons": len(baseline["checks"]), "authorized_modified_path_rows": exceptions,
             "scope_audit": AUDIT, "public_sink_scan": "CLEAN" if clean else "FAIL",
             "production_module_imports": [x for x in sys.modules if x in {"auth_lifecycle.online_state.services", "auth_lifecycle.online_state.storage", "auth_lifecycle.online_state.materials", "cryptography"}],
             "real_runtime_access": 0, "real_key_loads": 0, "real_RPC": 0,
             "P1": 0, "P2": 0, "B2": 0, "S5": 0, "old115_46_33_or_native_tests": 0}
        result["passed_authorized_scope"] = counts(rows) == {"PASS": 44, "FAIL": 0, "ERROR": 0, "SKIP": 0} and clean and not AUDIT["violations"] and not result["production_module_imports"]
        write(run / "RESULTS.json", result)
    except BaseException:
        write(run / "EARLY_FAILURE.json", {"status": "EARLY_FAILURE", "traceback": redact(traceback.format_exc()), "scope_audit": AUDIT})
        raise
    finally:
        timer.cancel()
        for connection in OWNED:
            try:
                connection.close()
            except Exception:
                pass
    path = ARTIFACT / "TEST_RUNS.json"
    history = load(path) if path.exists() else {"schema": "r16-a1-runs/1", "runs": []}
    history["runs"].append({"path": str(run / "RESULTS.json"), "sha256": sha(run / "RESULTS.json"),
                            "counts": result["counts"], "passed": result["passed_authorized_scope"]})
    write(path, history)
    print(json.dumps({"run": str(run), "A1": result["new_counts"], "H1": result["H1_counts"], "passed": result["passed_authorized_scope"]}))
    return 0 if result["passed_authorized_scope"] else 1


if __name__ == "__main__":
    sys.addaudithook(audit)
    argparse.ArgumentParser(description=__doc__).parse_args()
    raise SystemExit(main())
