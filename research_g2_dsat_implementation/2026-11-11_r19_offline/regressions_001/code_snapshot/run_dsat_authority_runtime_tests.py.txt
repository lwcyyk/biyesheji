"""R19 scoped driver. Two direct invocations; no child processes or services."""
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
RECORD = PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r19"
ARTIFACT = PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r19_offline"
DEPLOY = PROJECT.parent / "h2_test_runtime/h2-authority-synth-001"
FIXTURE = PROJECT / "tests/fixtures/dsat_authority_runtime"
OLD_H1 = PROJECT / "tests/fixtures/dsat_authority_read_host"
OLD_A1 = PROJECT / "tests/fixtures/dsat_authority_host_activation"
SOURCES = [PROJECT / "src/auth_lifecycle/online_state/services.py",
    PROJECT / "src/auth_lifecycle/online_state/dsat_authority_runtime.py",
    PROJECT / "scripts/run_h2_authority_service.py", PROJECT / "scripts/inspect_h2_authority_metadata.py",
    PROJECT / "tests/test_dsat_authority_runtime.py", Path(__file__).absolute()]
AUDIT = {"memory_connections": 0, "file_SQLite": 0, "socket": 0, "process": 0, "private_file": 0,
         "deployment_access": 0, "outside_write": 0, "forbidden_SQL": 0, "violations": []}
PHASE, SUITE = "PRECHECK", None
OWNED, SECRETS = [], []
sys.dont_write_bytecode = True


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def redact(text):
    for value in SECRETS:
        text = text.replace(value, "[REDACTED_SYNTHETIC_CANARY]")
    return text


def target(path):
    path = Path(path).absolute()
    if not path.is_relative_to(ARTIFACT):
        raise RuntimeError("OUTPUT_SCOPE_DENIED")
    for part in (path, *path.parents):
        if part.exists() and (part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise RuntimeError("OUTPUT_REPARSE_DENIED")
    if path.resolve() != path:
        raise RuntimeError("OUTPUT_SCOPE_DENIED")
    return path


def write(path, data):
    target(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def deny(kind):
    AUDIT[kind] += 1
    AUDIT["violations"].append("D1A_ISOLATION_BLOCKED")
    raise RuntimeError("D1A_ISOLATION_BLOCKED")


def audit(event, args):
    if event == "sqlite3.connect":
        limit = 8 if SUITE == "d1a" else 32
        if PHASE not in {"D1A", "A1"} or args[0] != ":memory:" or AUDIT["memory_connections"] >= limit:
            deny("file_SQLite")
        AUDIT["memory_connections"] += 1
    if event in {"sqlite3.enable_load_extension", "sqlite3.load_extension"}:
        deny("forbidden_SQL")
    if event.startswith("socket."):
        deny("socket")
    if event in {"subprocess.Popen", "os.system", "os.startfile", "os.fork", "os.exec"}:
        deny("process")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        raw = os.fsdecode(args[0]); path = Path(raw).absolute(); norm = raw.replace("\\", "/").lower()
        if path.is_relative_to(DEPLOY):
            deny("deployment_access")
        if "/.runtime/" in norm or "/secure/" in norm or path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".key", ".aes", ".pem", ".pfx"}:
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
    conn = sqlite3.connect(":memory:", check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    def guard(action, arg1, arg2, database, trigger):
        if action in {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH} or (
                action == sqlite3.SQLITE_FUNCTION and str(arg2).lower() == "load_extension"):
            deny("forbidden_SQL")
        return sqlite3.SQLITE_OK
    conn.set_authorizer(guard)
    OWNED.append(conn)
    return conn


def preflight():
    approval = load(RECORD / "APPROVAL_RECEIPT.json")
    if approval["approved"] is not True or sha(Path(approval["request_path"])) != approval["request_sha256"]:
        raise RuntimeError("D1A_APPROVAL_REQUIRED")
    expected_python = approval["python"] if SUITE == "d1a" else approval["regression_python"]
    if sys.executable != expected_python or sys.version_info[:3] != (3, 12, 14):
        raise RuntimeError("INTERPRETER_SCOPE_MISMATCH")
    baseline = load(RECORD / "sources/PRECHECK_LOCK.json")
    modified = baseline["allowed_modification"]
    if sha(Path(modified["snapshot"])) != modified["before_sha256"]:
        raise RuntimeError("ORIGINAL_SOURCE_LOST")
    changed_rows = 0
    for row in baseline["checks"]:
        if row["path"] == modified["path"]:
            if row["expected"] != modified["before_sha256"]:
                raise RuntimeError("UNEXPECTED_OLD_SERVICE_VERSION")
            changed_rows += 1
        elif sha(Path(row["path"])) != row["expected"]:
            raise RuntimeError("PROTECTED_FILE_CHANGED")
    for path in SOURCES[1:5]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        forbidden = {"services", "storage", "materials", "lab", "native_provider"}
        if any(set(name.split(".")) & forbidden for name in imports):
            raise RuntimeError("REAL_SERVICE_IMPORT_DENIED")
    return baseline, changed_rows


class Results(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.rows, self.started = [], 0

    def startTest(self, test):
        self.started = time.perf_counter_ns(); super().startTest(test)

    def _exc_info_to_string(self, err, test):
        return redact(super()._exc_info_to_string(err, test))

    def record(self, test, status, detail=None):
        row = {"id": test._testMethodName.split("_")[1], "status": status, "executed": True,
               "elapsed_ns": time.perf_counter_ns() - self.started}
        if detail: row["detail"] = redact(detail)
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
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_class(cls, ids, output):
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
    if sorted(t._testMethodName.split("_")[1] for t in suite) != ids:
        raise RuntimeError("TEST_IDENTITY_COUNT_CHANGED")
    return unittest.TextTestRunner(stream=output, verbosity=2, resultclass=Results).run(suite)


def main():
    global PHASE, SUITE
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=["d1a", "regressions"], required=True)
    SUITE = parser.parse_args().suite
    started = datetime.datetime.now(datetime.timezone.utc).isoformat(); clock = time.perf_counter_ns()
    baseline, changed = preflight()
    target(ARTIFACT).mkdir(exist_ok=True)
    index = 1
    while (ARTIFACT / (SUITE + "_%03d" % index)).exists(): index += 1
    run = target(ARTIFACT / (SUITE + "_%03d" % index)); run.mkdir()
    code = [{"path": str(p), "sha256": sha(p)} for p in SOURCES]
    roots = [FIXTURE] if SUITE == "d1a" else [OLD_A1, OLD_H1]
    inputs = [{"path": str(p), "sha256": sha(p)} for root in roots for p in sorted(root.glob("*.json"))]
    for root in roots: SECRETS.extend(load(root / "CANARIES.json")["values"].values())
    snap = run / "code_snapshot"; snap.mkdir()
    for path in SOURCES: (snap / (path.name + ".txt")).write_bytes(path.read_bytes())
    write(run / "RUN_START.json", {"argv": sys.orig_argv, "python": sys.version, "suite": SUITE,
          "date_china": "2026-11-11", "code": code, "inputs": inputs, "started_utc": started})
    timer = threading.Timer(max(.01, 120 - (time.perf_counter_ns() - clock) / 1e9), _thread.interrupt_main)
    timer.daemon = True; timer.start()
    try:
        sys.path.insert(0, str(PROJECT / "src"))
        with (run / "stdout.log").open("w", encoding="utf-8") as log:
            if SUITE == "d1a":
                PHASE = "D1A"
                plan = load(RECORD / "D1A_TEST_PLAN.json")
                new = module_at("r19_d1a_cases", SOURCES[4])
                new.configure(plan, FIXTURE, connect_memory, run)
                results = [run_class(new.D1ACases, [x["id"] for x in plan["new_cases"]], log)]
                details = new.DETAILS
            else:
                PHASE = "A1"
                plan = load(PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r15/H2_HOST_ACTIVATION_PLAN.json")
                a1 = module_at("r19_original_a1", PROJECT / "tests/test_dsat_authority_host_activation.py")
                a1.configure(plan, OLD_A1, connect_memory)
                first = run_class(a1.ActivationCases, ["A%02d" % i for i in range(1, 21)], log)
                PHASE = "H1"
                h1 = module_at("r19_original_h1", PROJECT / "tests/test_dsat_authority_read_host.py")
                h1.configure(load(PROJECT.parent / "research_g2_dsat_implementation/2026-11-11_r13/REAL_READONLY_TEST_PLAN.json"), OLD_H1)
                second = run_class(h1.H1Cases, ["H%02d" % i for i in range(1, 25)], log)
                results, details = [first, second], a1.DETAILS + h1.DETAILS
        PHASE = "POSTCHECK"
        preflight()
        if any(sha(Path(row["path"])) != row["sha256"] for row in code + inputs): raise RuntimeError("CODE_OR_INPUT_CHANGED")
        rows = [row for result in results for row in result.rows]
        counts = {s: sum(row["status"] == s for row in rows) for s in ("PASS", "FAIL", "ERROR", "SKIP")}
        text = (run / "stdout.log").read_text(encoding="utf-8") + json.dumps(details)
        clean = all(v not in text for v in SECRETS)
        production = [n for n in sys.modules if n in {"auth_lifecycle.online_state.services", "auth_lifecycle.online_state.storage", "auth_lifecycle.online_state.materials"}]
        result = {"schema": "r19-d1a-actual-results/1", "suite": SUITE, "run": str(run), "date_china": "2026-11-11",
             "argv": sys.orig_argv, "python": sys.version, "sqlite_version": sqlite3.sqlite_version,
             "started_utc": started, "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "elapsed_ns": time.perf_counter_ns() - clock, "counts": counts, "executed": len(rows),
             "cases": rows, "details": details, "code": code, "inputs": inputs,
             "protected_comparisons": len(baseline["checks"]), "authorized_modified_source_rows": changed,
             "scope_audit": AUDIT, "public_sink_scan": "CLEAN" if clean else "FAIL",
             "cryptography_imported": "cryptography" in sys.modules, "production_module_imports": production,
             "deployment_root_created": False, "service_DB_key_RPC_process_bind": 0,
             "D1B_P1a_P1b_P2_B2_S5": 0, "test_spawned_subprocesses": 0}
        expected = 24 if SUITE == "d1a" else 44
        result["passed_authorized_scope"] = counts == {"PASS": expected, "FAIL": 0, "ERROR": 0, "SKIP": 0} and clean and not AUDIT["violations"] and not production
        write(run / "RESULTS.json", result)
    except BaseException:
        write(run / "EARLY_FAILURE.json", {"status": "EARLY_FAILURE", "traceback": redact(traceback.format_exc()), "scope_audit": AUDIT})
        raise
    finally:
        timer.cancel()
        for conn in OWNED:
            try: conn.close()
            except Exception: pass
    history_path = ARTIFACT / "TEST_RUNS.json"
    history = load(history_path) if history_path.exists() else {"schema": "r19-test-runs/1", "runs": []}
    history["runs"].append({"path": str(run / "RESULTS.json"), "sha256": sha(run / "RESULTS.json"), "suite": SUITE,
                            "counts": counts, "passed": result["passed_authorized_scope"]})
    write(history_path, history)
    print(json.dumps({"run": str(run), "suite": SUITE, "counts": counts, "passed": result["passed_authorized_scope"]}))
    return 0 if result["passed_authorized_scope"] else 1


if __name__ == "__main__":
    sys.addaudithook(audit)
    raise SystemExit(main())
