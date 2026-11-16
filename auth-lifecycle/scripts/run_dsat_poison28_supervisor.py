"""R45 Windows supervisor. Only definitions and stdlib imports run on import.

Execution requires an independently approved complete policy. The historical
R44 resource maxima are null. R45 authorizes source creation/static review only.
"""

import argparse
import base64
import ctypes
import datetime
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys


BASE = Path(r"D:\毕业设计\research_g2_dsat_implementation")
PROJECT = Path(r"D:\毕业设计\auth-lifecycle")
DRIVER = PROJECT / "tests/test_dsat_runner_poison_classification.py"
RUNNER = PROJECT / "scripts/run_dsat_current_build_regressions.py"
PYTHON = Path(r"C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
DRIVER_SHA = "28e9ccf96f20a634b274f5350e8044da87b33f0c73905448664a68a3c41c67fd"
RUNNER_SHA = "245a35d4786fdf4e43b532d11a70a9db1b9be1d5d81d1f6a3f78e1ecfd96646f"
MANIFEST = BASE / "2026-11-15_r42/R42_28_TEST_MANIFEST.json"
MANIFEST_SHA = "aaf20e86f733b2eaa7b09254bfaca86b4d23ca69ef4ebf6fc001e11b9db0219d"
RESOURCE_NAMES = (
    "fault injection/clock-transition arms total",
    "metadata/read/write/flush/fsync/open/close call ceilings",
    "lock objects and in-memory fixture/stream counts",
    "maximum newly created directories",
    "whole interpreter RSS/working-set budget and enforcement",
    "actual total cumulative payload write-byte ceiling",
    "complete normal/failure evidence demand within each artifact cap",
    "120s external supervision/abort/cleanup contract",
)
WORK_SECONDS, READ_SECONDS, HARD_SECONDS = 90, 115, 120
EVIDENCE_BYTES = 2097152
CHILD_ARTIFACT_CAP_SUM = 933888
IO_FIELDS = ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
             "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")
HANDLE = ctypes.c_void_p
DWORD = ctypes.c_uint32
WORD = ctypes.c_uint16
BOOL = ctypes.c_int32
SIZE_T = ctypes.c_size_t
ULONG_PTR = ctypes.c_size_t
LARGE_INTEGER = ctypes.c_int64
ULONGLONG = ctypes.c_uint64
LPVOID = ctypes.c_void_p
LPWSTR = ctypes.c_wchar_p
CLEANUP_API_RESERVE = 32


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("nLength", DWORD), ("lpSecurityDescriptor", LPVOID), ("bInheritHandle", BOOL)]


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [("ReadOperationCount", ULONGLONG), ("WriteOperationCount", ULONGLONG),
                ("OtherOperationCount", ULONGLONG), ("ReadTransferCount", ULONGLONG),
                ("WriteTransferCount", ULONGLONG), ("OtherTransferCount", ULONGLONG)]


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", DWORD), ("dwHighDateTime", DWORD)]


class STARTUPINFOW(ctypes.Structure):
    _fields_ = [("cb", DWORD), ("lpReserved", LPWSTR), ("lpDesktop", LPWSTR), ("lpTitle", LPWSTR),
                ("dwX", DWORD), ("dwY", DWORD), ("dwXSize", DWORD), ("dwYSize", DWORD),
                ("dwXCountChars", DWORD), ("dwYCountChars", DWORD), ("dwFillAttribute", DWORD),
                ("dwFlags", DWORD), ("wShowWindow", WORD), ("cbReserved2", WORD),
                ("lpReserved2", LPVOID), ("hStdInput", HANDLE), ("hStdOutput", HANDLE), ("hStdError", HANDLE)]


class STARTUPINFOEXW(ctypes.Structure):
    _fields_ = [("StartupInfo", STARTUPINFOW), ("lpAttributeList", LPVOID)]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [("hProcess", HANDLE), ("hThread", HANDLE), ("dwProcessId", DWORD), ("dwThreadId", DWORD)]


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", LARGE_INTEGER), ("PerJobUserTimeLimit", LARGE_INTEGER),
                ("LimitFlags", DWORD), ("MinimumWorkingSetSize", SIZE_T), ("MaximumWorkingSetSize", SIZE_T),
                ("ActiveProcessLimit", DWORD), ("Affinity", ULONG_PTR), ("PriorityClass", DWORD),
                ("SchedulingClass", DWORD)]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION), ("IoInfo", IO_COUNTERS),
                ("ProcessMemoryLimit", SIZE_T), ("JobMemoryLimit", SIZE_T),
                ("PeakProcessMemoryUsed", SIZE_T), ("PeakJobMemoryUsed", SIZE_T)]


class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
    _fields_ = [("TotalUserTime", LARGE_INTEGER), ("TotalKernelTime", LARGE_INTEGER),
                ("ThisPeriodTotalUserTime", LARGE_INTEGER), ("ThisPeriodTotalKernelTime", LARGE_INTEGER),
                ("TotalPageFaultCount", DWORD), ("TotalProcesses", DWORD), ("ActiveProcesses", DWORD),
                ("TotalTerminatedProcesses", DWORD)]


class JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION(ctypes.Structure):
    _fields_ = [("BasicInfo", JOBOBJECT_BASIC_ACCOUNTING_INFORMATION), ("IoInfo", IO_COUNTERS)]


class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [("cb", DWORD), ("PageFaultCount", DWORD), ("PeakWorkingSetSize", SIZE_T),
                ("WorkingSetSize", SIZE_T), ("QuotaPeakPagedPoolUsage", SIZE_T),
                ("QuotaPagedPoolUsage", SIZE_T), ("QuotaPeakNonPagedPoolUsage", SIZE_T),
                ("QuotaNonPagedPoolUsage", SIZE_T), ("PagefileUsage", SIZE_T),
                ("PeakPagefileUsage", SIZE_T), ("PrivateUsage", SIZE_T)]


class AdmissionError(RuntimeError):
    pass


def require(value, code):
    if not value:
        raise AdmissionError(code)


def error_record(error, operation):
    return {"operation": operation, "type": type(error).__name__, "message": str(error),
            "errno": getattr(error, "errno", None), "winerror": getattr(error, "winerror", None)}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


class ExplicitIO:
    """Python call/byte accounting; loader, kernel and physical I/O stay outside."""

    MAX = (1 << 63) - 1
    FIELDS = ("attempts", "successes", "failures", "refusals", "read_requested",
              "read_returned", "write_requested", "write_accepted", "files_opened",
              "metadata_attempts", "unknown_read_returns", "unknown_write_returns", "result_unconfirmed")

    def __init__(self):
        self.phase = "PRE_QPC_COST"
        self.rows = {}
        self.totals = {}
        self.limits = None
        self.persisted_serialized = 0
        self.uncertain_serialized = 0

    def configure(self, values, approved):
        names = ("io_attempts", "read_requested_bytes", "read_returned_bytes",
                 "runtime_files", "runtime_source_bytes")
        require(type(values) is dict, "SOURCE_READ_BUDGET_UNAPPROVED")
        for name in names:
            value = positive_int(values.get(name), "SOURCE_READ_BUDGET_UNAPPROVED")
            maximum = positive_int(approved.get("pre_qpc_" + name), "SOURCE_READ_BUDGET_UNAPPROVED")
            require(value <= maximum, "SOURCE_READ_BUDGET_EXCEEDS_APPROVAL")
        self.limits = {name: values[name] for name in names}
        total = self.totals.get("PRE_QPC_COST", {})
        require(total.get("attempts", 0) <= values["io_attempts"]
                and total.get("read_requested", 0) <= values["read_requested_bytes"]
                and total.get("read_returned", 0) <= values["read_returned_bytes"],
                "PRE_QPC_BOOTSTRAP_COST_EXCEEDS_APPROVAL")

    def call(self, site, operation, action, *args, requested=0, direction=None, result_bytes=None):
        require(type(requested) is int and 0 <= requested <= self.MAX, "IO_REQUEST_INVALID")
        key = self.phase + "/" + site
        row = self.rows.setdefault(key, {name: 0 for name in self.FIELDS})
        total = self.totals.setdefault(self.phase, {name: 0 for name in self.FIELDS})
        try:
            require(all(value < self.MAX for value in total.values()), "IO_COUNTER_RANGE")
            if direction == "read":
                require(total["read_requested"] + requested <= self.MAX
                        and total["read_returned"] + requested <= self.MAX, "IO_COUNTER_RANGE")
            if direction == "write":
                require(total["write_requested"] + requested <= self.MAX
                        and total["write_accepted"] + requested <= self.MAX, "IO_COUNTER_RANGE")
            if self.phase == "PRE_QPC_COST" and self.limits is not None:
                require(total["attempts"] < self.limits["io_attempts"], "PRE_QPC_IO_LIMIT")
                if direction == "read":
                    require(total["read_requested"] + requested <= self.limits["read_requested_bytes"]
                            and total["read_returned"] + requested <= self.limits["read_returned_bytes"],
                            "PRE_QPC_READ_LIMIT")
        except BaseException:
            row["refusals"] += 1
            total["refusals"] += 1
            raise
        for counts in (row, total):
            counts["attempts"] += 1
            if operation == "metadata": counts["metadata_attempts"] += 1
            if direction is not None: counts[direction + "_requested"] += requested
        try:
            value = action(*args)
        except BaseException:
            for counts in (row, total):
                counts["failures"] += 1
                if direction is not None: counts["unknown_" + direction + "_returns"] += 1
            raise
        for counts in (row, total):
            counts["successes"] += 1
            if operation == "open": counts["files_opened"] += 1
        if direction is not None:
            try:
                amount = result_bytes(value) if result_bytes is not None else len(value)
                require(type(amount) is int and 0 <= amount <= requested, "IO_RETURN_INVALID")
            except BaseException:
                for counts in (row, total):
                    counts["result_unconfirmed"] += 1
                    counts["unknown_" + direction + "_returns"] += 1
                raise
            label = "read_returned" if direction == "read" else "write_accepted"
            row[label] += amount
            total[label] += amount
        return value

    def snapshot(self, pre_qpc=False):
        selected = "PRE_QPC_COST" if pre_qpc else "QPC_SCOPED_COST"
        return {"phase": selected, "boundary": "BEFORE_THIS_RECORD_SERIALIZATION",
                "callsites": {key: dict(value) for key, value in self.rows.items()
                              if key.startswith(selected + "/")},
                "totals": dict(self.totals.get(selected, {})),
                "persisted_serialized_before_snapshot": self.persisted_serialized,
                "uncertain_serialized_before_snapshot": self.uncertain_serialized,
                "unobserved": ["interpreter_bootstrap", "implicit_loader_IO", "physical_IO",
                               "native_syscall_count", "parent_exit_tail"]}


def checked_path(path, exists=True, audit=None):
    path = Path(path)
    raw = str(path)
    require(path.is_absolute() and not raw.startswith(("\\\\", "//")) and ":" not in raw[2:]
            and all(part not in {".", ".."} and not part.endswith((".", " ")) for part in path.parts[1:]),
            "PATH_SCOPE")
    def metadata(site, action):
        return audit.call(site, "metadata", action) if audit is not None else action()
    for part in reversed((path, *path.parents)):
        if metadata("path.exists", part.exists):
            info = metadata("path.lstat", part.lstat)
            require(not metadata("path.is_symlink", part.is_symlink)
                    and not (getattr(info, "st_file_attributes", 0) & 0x400), "REPARSE_REFUSED")
    if exists:
        require(metadata("path.is_file", path.is_file)
                and metadata("path.stat_identity", path.stat).st_nlink == 1, "SOURCE_FILE_IDENTITY")
    return path


def positive_int(value, code):
    require(type(value) is int and 0 < value <= (1 << 63) - 1, code)
    return value


class PolicyValidator:
    """Read-only admission. No WindowsApi, output creation or target imports."""

    def __init__(self):
        self.io = ExplicitIO()
        self.pins = []
        self.source_reads = []

    @property
    def read_bytes(self):
        return self.io.totals.get("PRE_QPC_COST", {}).get("read_returned", 0)

    def source_record(self, path, kind):
        require(len(self.source_reads) < 32789, "SOURCE_READ_CATALOGUE_LIMIT")
        row = {"read_id": len(self.source_reads) + 1, "kind": kind,
               "path_sha256": hashlib.sha256(str(path).encode("utf-8")).hexdigest(),
               "file_identity": "PATH_CHECKS_ONLY_NATIVE_FILE_ID_UNKNOWN",
               "file_size_before": None, "read_calls": 0, "read_requested": 0,
               "read_returned": 0, "hashed_bytes": 0, "eof": False,
               "hash_complete": False, "metadata_matched": False,
               "sha256": "UNKNOWN", "state": "ENTERED", "close_status": "NOT_OPENED"}
        self.source_reads.append(row)
        return row

    def read_hashed(self, path, expected, kind, size_limit):
        row = self.source_record(path, kind)
        stream = None
        try:
            path = checked_path(path, audit=self.io)
            before = self.io.call("source.stat_before", "metadata", path.stat)
            size = before.st_size
            require(type(size) is int and 0 <= size <= size_limit, "SOURCE_SIZE_LIMIT")
            row["file_size_before"] = size
            if kind == "runtime": require(size == size_limit, "RUNTIME_SOURCE_SIZE_CHANGED")
            digest = hashlib.sha256()
            chunks = [] if kind == "control" else None
            stream = self.io.call("source.open", "open", lambda: path.open("rb", buffering=0))
            row["close_status"] = "PENDING"
            def read_block(request):
                row["read_calls"] += 1
                row["read_requested"] += request
                return stream.read(request)
            while True:
                request = min(65536, size + 1 - row["read_returned"])
                require(request > 0, "SOURCE_GREW")
                row["state"] = "READ_ATTEMPT"
                block = self.io.call("source.read", "read", read_block, request,
                                     requested=request, direction="read")
                row["read_returned"] += len(block)
                if not block:
                    row["eof"] = True
                    break
                require(row["read_returned"] <= size, "SOURCE_GREW")
                digest.update(block)
                row["hashed_bytes"] += len(block)
                if chunks is not None: chunks.append(block)
            require(row["read_returned"] == size, "SOURCE_SHORT_READ")
            after = self.io.call("source.stat_after", "metadata", path.stat)
            require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
                    == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), "SOURCE_CHANGED")
            row["metadata_matched"] = True
            row["sha256"] = digest.hexdigest()
            row["hash_complete"] = True
            if expected is not None:
                require(row["sha256"] == expected, "SOURCE_HASH_MISMATCH")
            row["state"] = "VERIFIED"
            self.pins.append({"path": str(path), "sha256": row["sha256"]})
            return b"".join(chunks) if chunks is not None else None
        except BaseException:
            row["state"] = "READ_OR_VERIFY_UNCONFIRMED"
            raise
        finally:
            if stream is not None:
                try:
                    self.io.call("source.close", "close", stream.close)
                    row["close_status"] = "RETURNED_SUCCESS"
                except BaseException:
                    row["close_status"] = "UNCONFIRMED"
                    raise

    def read(self, path, expected=None):
        path = Path(path)
        require(path.is_relative_to(BASE) or path.is_relative_to(PROJECT) or path.is_relative_to(PYTHON.parent)
                or path.is_relative_to(Path(r"C:\Users\a1887\.codex\attachments")), "INPUT_ROOT_SCOPE")
        require(path.suffix.lower() in {".json", ".md", ".txt", ".py", ".exe"}, "INPUT_KIND_SCOPE")
        return self.read_hashed(path, expected, "control", EVIDENCE_BYTES)

    def document(self, reference):
        return json.loads(self.read(reference["path"], reference["sha256"]))

    def verify_source_file(self, path, expected, declared_size):
        path = Path(path)
        require(path.is_relative_to(PYTHON.parent) or path.is_relative_to(PROJECT)
                or path.is_relative_to(Path(os.environ.get("SystemRoot", r"C:\Windows"))), "RUNTIME_PATH_SCOPE")
        require(path.suffix.lower() in {".py", ".pyc", ".dll", ".pyd", ".exe", ".json", ".txt", ".zip"}
                or path.name in {"METADATA", "RECORD", "WHEEL"},
                "RUNTIME_FILE_KIND")
        self.read_hashed(path, expected, "runtime", declared_size)
        require(self.source_reads[-1]["file_size_before"] == declared_size, "RUNTIME_SOURCE_SIZE_CHANGED")

    def read_pe_header(self):
        row = self.source_record(PYTHON, "pe")
        stream = None
        try:
            stream = self.io.call("pe.open", "open", lambda: PYTHON.open("rb", buffering=0))
            row["close_status"] = "PENDING"
            def read_part(size):
                row["read_calls"] += 1
                row["read_requested"] += size
                return stream.read(size)
            values = []
            for index, size in enumerate((64, 6)):
                if index:
                    self.io.call("pe.seek", "seek", stream.seek, int.from_bytes(values[0][60:64], "little"))
                data = self.io.call("pe.read", "read", read_part, size, requested=size, direction="read")
                row["read_returned"] += len(data)
                require(len(data) == size, "PYTHON_PE_HEADER")
                if index == 0: require(data[:2] == b"MZ", "PYTHON_PE_HEADER")
                values.append(data)
            require(values[0][:2] == b"MZ" and values[1][:4] == b"PE\x00\x00"
                    and values[1][4:6] == b"\x64\x86", "AMD64_PYTHON_REQUIRED")
            row["state"] = "PE_HEADER_VERIFIED_NOT_FULL_HASH"
            return values
        except BaseException:
            row["state"] = "PE_HEADER_UNCONFIRMED"
            raise
        finally:
            if stream is not None:
                try:
                    self.io.call("pe.close", "close", stream.close)
                    row["close_status"] = "RETURNED_SUCCESS"
                except BaseException:
                    row["close_status"] = "UNCONFIRMED"
                    raise

    def validate(self, policy_path):
        policy_path = checked_path(policy_path, audit=self.io)
        root = policy_path.parent
        require(root.parent == BASE, "POLICY_ROOT")
        parts = root.name.split("_")
        require(len(parts) == 2 and parts[1].startswith("r") and parts[1][1:].isdigit()
                and int(parts[1][1:]) > 45 and datetime.date.fromisoformat(parts[0]) >= datetime.date(2026, 11, 16),
                "SUCCESSOR_REQUIRED")
        raw = self.read(policy_path)
        policy = json.loads(raw)
        require(policy.get("schema") == "r45-poison-supervisor-policy/1", "POLICY_SCHEMA")
        rows = policy.get("resources", [])
        require(len(rows) == 8, "RESOURCE_LIMIT_NOT_APPROVED")
        for index, row in enumerate(rows):
            require(row.get("resource_id") == "R" + str(index + 1)
                    and row.get("original_name") == RESOURCE_NAMES[index]
                    and row.get("approved_maximum") is not None and row.get("approval_status") == "APPROVED",
                    "RESOURCE_LIMIT_NOT_APPROVED")
            require(type(row["approved_maximum"]) is dict and bool(row["approved_maximum"]), "RESOURCE_LIMIT_NOT_APPROVED")
            for value in row["approved_maximum"].values():
                positive_int(value, "RESOURCE_LIMIT_NOT_APPROVED")
        require(policy.get("approved") is True and policy.get("execution_authorized") is True,
                "INDEPENDENT_EXECUTION_APPROVAL_REQUIRED")
        approval = self.document(policy["approval_record"])
        body = {key: value for key, value in policy.items() if key != "approval_record"}
        require(approval.get("approved") is True and approval.get("policy_body_sha256") == hashlib.sha256(canonical(body)).hexdigest()
                and approval.get("action") == "RUN_ONE_SUPERVISED_POISON28" and approval.get("max_launches") == 1,
                "APPROVAL_BINDING")
        self.io.configure(policy.get("pre_qpc_accounting_limits"), rows[1]["approved_maximum"])
        resource_proof = self.document(policy["resource_bound_certificate"])
        require(resource_proof.get("approved") is True and resource_proof.get("complete") is True
                and resource_proof.get("supervisor_sha256") == policy["supervisor_sha256"]
                and resource_proof.get("driver_sha256") == DRIVER_SHA, "RESOURCE_BOUND_UNRESOLVED")
        for row in rows:
            upper_bounds = resource_proof["bounds"][row["resource_id"]]
            for name, maximum in row["approved_maximum"].items():
                require(positive_int(upper_bounds.get(name), "RESOURCE_BOUND_UNRESOLVED") <= maximum,
                        "RESOURCE_BOUND_EXCEEDS_APPROVAL")
        runtime = self.document(policy["runtime_origin_lock"])
        require(runtime.get("approved") is True and runtime.get("closure_verified") is True
                and runtime.get("driver_sha256") == DRIVER_SHA and runtime.get("runner_sha256") == RUNNER_SHA,
                "RUNTIME_ORIGIN_UNRESOLVED")
        require(type(runtime.get("files")) is list and bool(runtime["files"]), "RUNTIME_ORIGIN_UNRESOLVED")
        require(len(runtime["files"]) <= min(32768, self.io.limits["runtime_files"]), "RUNTIME_CATALOGUE_LIMIT")
        for item in runtime["files"]:
            require(type(item.get("bytes")) is int and 0 <= item["bytes"] <= ExplicitIO.MAX,
                    "RUNTIME_SOURCE_SIZE_UNRESOLVED")
        require(sum(item["bytes"] for item in runtime["files"]) <= self.io.limits["runtime_source_bytes"],
                "RUNTIME_SOURCE_BYTES_LIMIT")
        for item in runtime["files"]:
            self.verify_source_file(item["path"], item["sha256"], item["bytes"])
        require(runtime.get("G4_resolution_approved") is True and type(runtime.get("windows_build")) is int,
                "RUNTIME_ORIGIN_UNRESOLVED")
        runtime_paths = {str(Path(item["path"])): item["sha256"] for item in runtime["files"]}
        require(runtime_paths.get(str(PYTHON)) == policy["python_sha256"]
                and runtime.get("supervisor_sha256") == policy["supervisor_sha256"], "RUNTIME_BUILD_BINDING")
        require(policy["python_path"] == str(PYTHON) and policy["driver_path"] == str(DRIVER)
                and policy["runner_path"] == str(RUNNER) and Path(sys.executable) == PYTHON
                and policy["architecture"] == "AMD64" and struct.calcsize("P") == 8
                and os.name == "nt", "PLATFORM_OR_SOURCE_PATH")
        require(sys.flags.isolated and sys.dont_write_bytecode and sys.flags.utf8_mode, "SUPERVISOR_PYTHON_FLAGS")
        self.read(RUNNER, RUNNER_SHA)
        self.read(DRIVER, DRIVER_SHA)
        self.read(PYTHON, policy["python_sha256"])
        self.read_pe_header()
        self.read(Path(__file__).absolute(), policy["supervisor_sha256"])
        manifest = json.loads(self.read(MANIFEST, MANIFEST_SHA))
        ids = [row["test_id"] for row in manifest["rows"]]
        require(len(ids) == len(set(ids)) == 28 and policy["test_ids"] == ids, "TEST_IDENTITY")
        child_ref = policy["driver_execution_lock"]
        child_path = checked_path(child_ref["path"], audit=self.io)
        require(child_path.parent == root, "DRIVER_LOCK_ROOT")
        child = self.document(child_ref)
        require(child.get("schema") == "r43-poison28-execution/1" and child.get("approved") is True
                and child.get("execution_authorized") is True and child.get("test_IDs") == ids,
                "DRIVER_POLICY_NOT_APPROVED")
        for key in ("eight_resource_budgets_closed", "normal_and_failure_evidence_bound_proved",
                    "runtime_closure_approved", "external_wall_supervision_approved"):
            require(child.get(key) is True, "DRIVER_PROOF_GATE")
        require(child.get("max_suite_runs") == 1 and child.get("automatic_reruns") == 0 and child.get("wall_seconds") == 120
                and child.get("t20_primary_call") == "State.observe_result(A01,PASS,1000000)", "DRIVER_CONTRACT")
        child_approval = checked_path(child["approval_response_path"], audit=self.io)
        require(child_approval.suffix.lower() in {".txt", ".md", ".json"}
                and (child_approval.is_relative_to(BASE) or child_approval.is_relative_to(Path(r"C:\Users\a1887\.codex\attachments"))),
                "DRIVER_APPROVAL_SCOPE")
        self.read(child_approval, child["approval_response_sha256"])
        expected_inputs = {str(DRIVER), str(RUNNER), str(PYTHON), str(MANIFEST),
            str(BASE / "2026-11-14_r40/sources/PROTOCOL_PREFIX.jsonl"),
            str(BASE / "2026-11-14_r40/sources/CAPACITY_INPUT_RECIPE.json"),
            str(BASE / "2026-11-12_r33/R33_68_TEST_MANIFEST.json"),
            str(BASE / "2026-11-14_r41/R41_BUDGET_AND_POISON_CLASSIFICATION.json")}
        require(set(child["input_pins"]) == expected_inputs, "DRIVER_INPUT_CATALOGUE")
        for path, digest in child["input_pins"].items(): self.read(path, digest)
        require(child["input_pins"][str(DRIVER)] == DRIVER_SHA
                and child["input_pins"][str(RUNNER)] == RUNNER_SHA
                and child["input_pins"][str(PYTHON)] == policy["python_sha256"]
                and child["input_pins"][str(MANIFEST)] == MANIFEST_SHA, "DRIVER_SOURCE_BINDING")
        mappings = {"fault_arms": (0, "callback_arms"), "observation_events": (1, "observation_events"),
            "model_api_calls": (1, "model_api_calls"), "native_api_calls": (1, "child_native_api_calls"),
            "fixture_total": (2, "fixture_total"), "lock_total": (2, "lock_total"),
            "new_directories": (3, "driver_directories"), "whole_process_rss_bytes": (4, "child_peak_working_set_bytes"),
            "cumulative_native_payload_bytes": (5, "child_payload_bytes")}
        for name, (index, maximum) in mappings.items():
            require(positive_int(child["limits"].get(name), "DRIVER_LIMIT_MISSING")
                    <= rows[index]["approved_maximum"][maximum], "DRIVER_LIMIT_EXCEEDS_APPROVAL")
        require(policy["time"] == {"work_seconds": 90, "read_seconds": 115, "hard_seconds": 120,
                "work_cutoff_action": "TERMINATE_OWNED_JOB"}, "DEADLINE_CONTRACT")
        require(rows[7]["approved_maximum"]["wall_seconds"] == 120, "TIME_LIMIT_NOT_APPROVED")
        require(policy["evidence"]["total_bytes"] == EVIDENCE_BYTES and policy["evidence"]["full_payload_bound_proved"] is True,
                "ARTIFACT_BUDGET_UNPROVEN")
        bounds = self.document(policy["evidence_bound_certificate"])
        require(bounds.get("approved") is True and bounds.get("complete") is True
                and bounds.get("supervisor_sha256") == policy["supervisor_sha256"]
                and bounds.get("driver_sha256") == DRIVER_SHA, "ARTIFACT_PROOF_BINDING")
        evidence = policy["evidence"]
        for key in ("witness_bytes", "failure_reserve_bytes", "max_record_bytes", "stdout_raw_bytes", "stderr_raw_bytes"):
            positive_int(evidence[key], "ARTIFACT_CAP_NOT_APPROVED")
        require(evidence["failure_reserve_bytes"] <= evidence["witness_bytes"]
                and evidence["max_record_bytes"] <= evidence["failure_reserve_bytes"], "FAILURE_RESERVE")
        require(positive_int(bounds.get("supervisor_record_upper"), "RECORD_BOUND_MISSING") <= evidence["max_record_bytes"]
                and positive_int(bounds.get("supervisor_failure_suffix_upper"), "FAILURE_BOUND_MISSING") <= evidence["failure_reserve_bytes"]
                and positive_int(bounds.get("supervisor_total_upper"), "TOTAL_BOUND_MISSING") <= evidence["witness_bytes"],
                "ARTIFACT_BOUND_EXCEEDS_CAP")
        require(CHILD_ARTIFACT_CAP_SUM + evidence["witness_bytes"] <= EVIDENCE_BYTES
                and evidence["witness_bytes"] <= rows[6]["approved_maximum"]["supervisor_witness_bytes"], "JOINT_EVIDENCE_CAP")
        require(evidence["witness_bytes"] + child["limits"]["cumulative_native_payload_bytes"]
                <= rows[5]["approved_maximum"]["joint_payload_bytes"] <= EVIDENCE_BYTES, "JOINT_PAYLOAD_CAP")
        require(rows[3]["approved_maximum"]["supervisor_directories"] >= 1, "DIRECTORY_LIMIT_NOT_APPROVED")
        observer = policy["observer"]
        for key in ("poll_ms", "max_samples", "max_api_calls", "pipe_chunk_bytes", "pipe_buffer_bytes", "max_drain_chunks",
                    "attribute_buffer_bytes"):
            positive_int(observer[key], "OBSERVER_LIMIT_NOT_APPROVED")
        require(observer["max_api_calls"] <= rows[1]["approved_maximum"]["supervisor_api_calls"], "OBSERVER_API_APPROVAL")
        require(observer["max_api_calls"] >= 64 + CLEANUP_API_RESERVE and observer["pipe_chunk_bytes"] <= 65536
                and observer["pipe_buffer_bytes"] <= 1048576 and observer["poll_ms"] <= 1000,
                "OBSERVER_SAFETY_DOMAIN")
        require(observer["max_samples"] <= rows[1]["approved_maximum"]["supervisor_samples"], "SAMPLE_CAP_UNAPPROVED")
        require(rows[0]["approved_maximum"].get("virtual_clock_assignments", 0) > 0
                and rows[0]["approved_maximum"].get("configuration_operations", 0) > 0,
                "RESOURCE_LIMIT_NOT_APPROVED")
        require(rows[7]["approved_maximum"].get("poll_ms", 0) >= observer["poll_ms"], "POLL_INTERVAL_UNAPPROVED")
        require(evidence["stdout_raw_bytes"] <= rows[6]["approved_maximum"]["stdout_raw_bytes"]
                and evidence["stderr_raw_bytes"] <= rows[6]["approved_maximum"]["stderr_raw_bytes"], "PIPE_CAP_UNAPPROVED")
        require(rows[2]["approved_maximum"]["supervisor_handles"] >= 9
                and rows[2]["approved_maximum"]["job_count"] >= 1
                and rows[2]["approved_maximum"]["root_child_count"] == 1, "HANDLE_OR_PROCESS_LIMIT")
        require(observer["attribute_buffer_bytes"] <= rows[2]["approved_maximum"]["attribute_buffer_bytes"]
                and 2 * observer["pipe_buffer_bytes"] <= rows[2]["approved_maximum"]["pipe_buffer_bytes"],
                "NATIVE_BUFFER_NOT_APPROVED")
        positive_int(rows[4]["approved_maximum"]["supervisor_peak_working_set_bytes"], "PARENT_MEMORY_UNAPPROVED")
        require(policy["job"]["kill_on_close"] is True and policy["job"]["active_process_limit"] == 1
                and policy["job"]["breakaway"] is False and policy["job"]["creation_time_assignment"] is True,
                "JOB_CONFIGURATION")
        if policy["job"]["commit_limits_enabled"]:
            require(positive_int(policy["job"]["process_commit_bytes"], "QUOTA_UNAPPROVED")
                    <= rows[4]["approved_maximum"]["child_commit_bytes"], "PROCESS_QUOTA_UNAPPROVED")
            require(positive_int(policy["job"]["job_commit_bytes"], "QUOTA_UNAPPROVED")
                    <= rows[4]["approved_maximum"]["job_commit_bytes"], "JOB_QUOTA_UNAPPROVED")
        require(policy["output_root"] == str(root / "observer_run_001")
                and child["output_root"] == str(root / "verification_runs/poison28_001"), "OUTPUT_ROOT_BINDING")
        for path in (root / "observer_run_001", root / "verification_runs"):
            checked_path(path, exists=False, audit=self.io)
            require(not self.io.call("output.preflight_exists", "metadata", path.exists), "RUN_ALREADY_CLAIMED")
        argv = [str(PYTHON), "-I", "-B", "-X", "utf8", str(DRIVER), "--execution-lock", str(child_path)]
        require(policy["child_argv"] == argv and policy["working_directory"] == str(PROJECT), "DRIVER_INTERFACE_BLOCKED")
        require(policy["max_launches"] == 1 and policy["automatic_reruns"] == 0, "ONE_LAUNCH_CONTRACT")
        require(policy["parent_and_child_resource_scope_approved"] is True, "SUPERVISOR_OVERHEAD_UNAPPROVED")
        policy["_policy_sha256"] = hashlib.sha256(raw).hexdigest()
        policy["_source_lock_sha256"] = policy["runtime_origin_lock"]["sha256"]
        policy["_validated_reads"] = self.read_bytes
        policy["_windows_build"] = runtime["windows_build"]
        policy["_explicit_io"] = self.io
        policy["_source_read_records"] = self.source_reads
        policy["_pre_qpc_cost"] = self.io.snapshot(pre_qpc=True)
        return policy


class WindowsApi:
    """System32 DLL resolution and ABI checks occur only after policy admission."""

    def __init__(self, max_calls):
        require(os.name == "nt" and ctypes.sizeof(HANDLE) == 8 and ctypes.sizeof(ctypes.c_wchar) == 2, "AMD64_ABI_REQUIRED")
        expected = {SECURITY_ATTRIBUTES: 24, IO_COUNTERS: 48, FILETIME: 8, STARTUPINFOW: 104,
            STARTUPINFOEXW: 112, PROCESS_INFORMATION: 24, JOBOBJECT_BASIC_LIMIT_INFORMATION: 64,
            JOBOBJECT_EXTENDED_LIMIT_INFORMATION: 144, JOBOBJECT_BASIC_ACCOUNTING_INFORMATION: 48,
            JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION: 96, PROCESS_MEMORY_COUNTERS_EX: 80}
        for structure, size in expected.items(): require(ctypes.sizeof(structure) == size, "WIN32_LAYOUT_MISMATCH")
        self.dll = ctypes.WinDLL("kernel32.dll", use_last_error=True, winmode=0x00000800)
        self.counts, self.max_calls = {}, max_calls
        self.deadline = None
        self.functions = {}
        ptr = ctypes.POINTER
        signatures = {
            "CreateJobObjectW": ([ptr(SECURITY_ATTRIBUTES), LPWSTR], HANDLE),
            "SetInformationJobObject": ([HANDLE, ctypes.c_int32, LPVOID, DWORD], BOOL),
            "AssignProcessToJobObject": ([HANDLE, HANDLE], BOOL),
            "QueryInformationJobObject": ([HANDLE, ctypes.c_int32, LPVOID, DWORD, ptr(DWORD)], BOOL),
            "TerminateJobObject": ([HANDLE, ctypes.c_uint32], BOOL),
            "CloseHandle": ([HANDLE], BOOL),
            "IsProcessInJob": ([HANDLE, HANDLE, ptr(BOOL)], BOOL),
            "InitializeProcThreadAttributeList": ([LPVOID, DWORD, DWORD, ptr(SIZE_T)], BOOL),
            "UpdateProcThreadAttribute": ([LPVOID, DWORD, ULONG_PTR, LPVOID, SIZE_T, LPVOID, ptr(SIZE_T)], BOOL),
            "DeleteProcThreadAttributeList": ([LPVOID], None),
            "CreateProcessW": ([LPWSTR, LPWSTR, ptr(SECURITY_ATTRIBUTES), ptr(SECURITY_ATTRIBUTES), BOOL,
                DWORD, LPVOID, LPWSTR, ptr(STARTUPINFOW), ptr(PROCESS_INFORMATION)], BOOL),
            "ResumeThread": ([HANDLE], DWORD),
            "WaitForSingleObject": ([HANDLE, DWORD], DWORD),
            "GetExitCodeProcess": ([HANDLE, ptr(DWORD)], BOOL),
            "TerminateProcess": ([HANDLE, ctypes.c_uint32], BOOL),
            "GetCurrentProcess": ([], HANDLE), "GetCurrentProcessId": ([], DWORD),
            "GetProcessTimes": ([HANDLE, ptr(FILETIME), ptr(FILETIME), ptr(FILETIME), ptr(FILETIME)], BOOL),
            "GetProcessIoCounters": ([HANDLE, ptr(IO_COUNTERS)], BOOL),
            "K32GetProcessMemoryInfo": ([HANDLE, ptr(PROCESS_MEMORY_COUNTERS_EX), DWORD], BOOL),
            "QueryPerformanceCounter": ([ptr(LARGE_INTEGER)], BOOL),
            "QueryPerformanceFrequency": ([ptr(LARGE_INTEGER)], BOOL),
            "QueryFullProcessImageNameW": ([HANDLE, DWORD, LPWSTR, ptr(DWORD)], BOOL),
            "CreatePipe": ([ptr(HANDLE), ptr(HANDLE), ptr(SECURITY_ATTRIBUTES), DWORD], BOOL),
            "SetHandleInformation": ([HANDLE, DWORD, DWORD], BOOL),
            "CreateFileW": ([LPWSTR, DWORD, DWORD, ptr(SECURITY_ATTRIBUTES), DWORD, DWORD, HANDLE], HANDLE),
            "PeekNamedPipe": ([HANDLE, LPVOID, DWORD, ptr(DWORD), ptr(DWORD), ptr(DWORD)], BOOL),
            "ReadFile": ([HANDLE, LPVOID, DWORD, ptr(DWORD), LPVOID], BOOL),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.dll, name)
            function.argtypes, function.restype = arguments, result
            self.functions[name] = function

    def call(self, name, *args, cleanup=False):
        # A fixed emergency allowance is reserved inside the approved API ceiling.
        ceiling = self.max_calls if cleanup else self.max_calls - CLEANUP_API_RESERVE
        require(sum(self.counts.values()) < ceiling, "SUPERVISOR_API_BUDGET_EXCEEDED")
        self.counts[name] = self.counts.get(name, 0) + 1
        ctypes.set_last_error(0)
        result = self.functions[name](*args)
        code = ctypes.get_last_error()
        return result, code

    def check(self, name, *args, cleanup=False):
        result, code = self.call(name, *args, cleanup=cleanup)
        if not result:
            raise ctypes.WinError(code)
        return result

    def handle(self, name, *args):
        result, code = self.call(name, *args)
        if result is None or result == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(code)
        return result

    def close(self, handle):
        if handle is not None:
            if self.deadline is not None:
                require(self.deadline.elapsed(cleanup=True) < HARD_SECONDS, "HANDLE_CLOSE_DEADLINE")
            self.check("CloseHandle", handle, cleanup=True)


class DeadlineController:
    def __init__(self, api):
        self.api = api
        frequency = LARGE_INTEGER()
        api.check("QueryPerformanceFrequency", ctypes.byref(frequency))
        require(frequency.value > 0, "QPC_FREQUENCY")
        self.frequency = frequency.value
        self.start = self.now()

    def now(self, cleanup=False):
        tick = LARGE_INTEGER()
        self.api.check("QueryPerformanceCounter", ctypes.byref(tick), cleanup=cleanup)
        return tick.value

    def elapsed(self, cleanup=False):
        return (self.now(cleanup) - self.start) / self.frequency

    def admit(self, seconds=READ_SECONDS, cleanup=False):
        require(self.elapsed(cleanup=cleanup) < seconds, "SUPERVISOR_DEADLINE")

    def wait_ms(self, maximum_ms, seconds):
        remaining = max(0.0, seconds - self.elapsed())
        return max(0, min(maximum_ms, int(remaining * 1000)))


class JobController:
    def __init__(self, api):
        self.api, self.handle = api, None
        self.termination_requested = False
        self.termination_api_confirmed = False
        self.close_attempted = self.closed_confirmed = False
        self.created = False

    def create(self, config):
        self.handle = self.api.handle("CreateJobObjectW", None, None)
        self.created = True
        limits = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limits.BasicLimitInformation.LimitFlags = 0x2000 | 0x8
        limits.BasicLimitInformation.ActiveProcessLimit = 1
        if config["commit_limits_enabled"]:
            limits.BasicLimitInformation.LimitFlags |= 0x100 | 0x200
            limits.ProcessMemoryLimit = config["process_commit_bytes"]
            limits.JobMemoryLimit = config["job_commit_bytes"]
        self.api.check("SetInformationJobObject", self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits))
        observed = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        self.api.check("QueryInformationJobObject", self.handle, 9, ctypes.byref(observed), ctypes.sizeof(observed), None)
        require(observed.BasicLimitInformation.LimitFlags == limits.BasicLimitInformation.LimitFlags
                and observed.BasicLimitInformation.ActiveProcessLimit == 1, "JOB_LIMIT_READBACK")
        if config["commit_limits_enabled"]:
            require(observed.ProcessMemoryLimit == limits.ProcessMemoryLimit
                    and observed.JobMemoryLimit == limits.JobMemoryLimit, "JOB_MEMORY_LIMIT_READBACK")
        return limits

    def assign(self, process):
        self.api.check("AssignProcessToJobObject", self.handle, process)

    def contains(self, process):
        member = BOOL()
        self.api.check("IsProcessInJob", process, self.handle, ctypes.byref(member))
        return bool(member.value)

    def accounting(self):
        basic = JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION()
        memory = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        self.api.check("QueryInformationJobObject", self.handle, 8, ctypes.byref(basic), ctypes.sizeof(basic), None)
        self.api.check("QueryInformationJobObject", self.handle, 9, ctypes.byref(memory), ctypes.sizeof(memory), None)
        return {"io": {name: getattr(basic.IoInfo, name) for name in IO_FIELDS},
                "active_processes": basic.BasicInfo.ActiveProcesses, "total_processes": basic.BasicInfo.TotalProcesses,
                "JobMemoryUsage": "UNKNOWN", "JobPeakMemoryUsage": memory.PeakJobMemoryUsed,
                "PeakProcessCommit": memory.PeakProcessMemoryUsed,
                "memory_units": "COMMITTED_BYTES", "ExtendedLimit_IoInfo": "RESERVED_NOT_USED"}

    def terminate(self, exit_code):
        if self.termination_requested: return
        self.termination_requested = True
        self.api.check("TerminateJobObject", self.handle, exit_code, cleanup=True)
        self.termination_api_confirmed = True

    def close(self):
        if self.handle is None or self.close_attempted: return
        self.close_attempted = True
        self.api.close(self.handle)
        self.closed_confirmed = True
        self.handle = None


class OutputController:
    def __init__(self, api, deadline, policy):
        self.api, self.deadline, self.policy = api, deadline, policy
        self.io = policy["_explicit_io"]
        self.io.phase = "QPC_SCOPED_COST"
        self.handles = {}
        self.stream = None
        self.charged = 0
        self.poisoned = False
        self.raw_counts = {"stdout": 0, "stderr": 0}
        self.raw_hashers = {name: hashlib.sha256() for name in self.raw_counts}
        empty = hashlib.sha256(b"").hexdigest()
        self.raw_prefixes = {name: {"read_bytes": 0, "read_frames": 0, "read_sha256": empty,
            "accepted_bytes": 0, "accepted_frames": 0, "accepted_sha256": empty,
            "persisted_bytes": 0, "persisted_frames": 0, "persisted_sha256": empty,
            "pending": None} for name in self.raw_counts}
        self.witness_prefix = {"sequence": 0, "bytes": 0, "sha256": "0" * 64,
            "raw": {name: {"bytes": 0, "frames": 0, "sha256": empty, "last_witness_seq": 0}
                    for name in self.raw_counts}}
        self.pre_qpc_ref = "UNKNOWN"
        self.eof = {"stdout": False, "stderr": False}
        self.close_errors = []
        self.close_attempted = set()
        self.file_close_attempted = False

    @property
    def confirmed(self):
        return self.witness_prefix["bytes"]

    @property
    def sequence(self):
        return self.witness_prefix["sequence"]

    @property
    def head(self):
        return self.witness_prefix["sha256"]

    def prefix_snapshot(self):
        return {name: {**value, "pending": dict(value["pending"]) if value["pending"] else None,
                       "witness_committed": dict(self.witness_prefix["raw"][name]),
                       "confirmation_scope": "COMPLETE_FRAMES_AFTER_FSYNC_RETURN",
                       "last_confirmation_phase": "AFTER_FSYNC_AND_PREFIX_PUBLICATION"}
                for name, value in self.raw_prefixes.items()}

    def open(self):
        self.deadline.admit()
        root = checked_path(self.policy["output_root"], exists=False, audit=self.io)
        self.io.call("witness.mkdir", "mkdir", lambda: root.mkdir(exist_ok=False))
        self.stream = self.io.call("witness.open", "open", lambda:
            (root / "SUPERVISOR_WITNESS.jsonl").open("xb", buffering=0))
        security = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, True)
        self.handles["stdin"] = self.api.handle("CreateFileW", "NUL", 0x80000000, 3,
            ctypes.byref(security), 3, 0, None)
        for name in ("stdout", "stderr"):
            self.deadline.admit()
            reader, writer = HANDLE(), HANDLE()
            self.api.check("CreatePipe", ctypes.byref(reader), ctypes.byref(writer),
                ctypes.byref(security), self.policy["observer"]["pipe_buffer_bytes"])
            self.handles[name + "_read"] = reader.value
            self.handles[name + "_write"] = writer.value
            self.api.check("SetHandleInformation", reader.value, 1, 0)

    def inherited(self):
        return (self.handles["stdin"], self.handles["stdout_write"], self.handles["stderr_write"])

    def release_child_ends(self):
        for name in ("stdin", "stdout_write", "stderr_write"):
            try:
                self.close_handle(name)
            except Exception as error:
                self.close_errors.append(error_record(error, "CloseHandle:" + name))
                raise

    def close_handle(self, name):
        handle = self.handles.get(name)
        if handle is None or name in self.close_attempted: return
        self.close_attempted.add(name)
        self.api.close(handle)
        del self.handles[name]

    def append(self, stage, value, final=False, raw_frame=None):
        self.deadline.admit(cleanup=final)
        require(self.stream is not None and not self.poisoned, "WITNESS_UNAVAILABLE")
        raw_name = None
        if raw_frame is not None:
            raw_name = raw_frame["name"]
            previous = self.witness_prefix["raw"][raw_name]
            state = self.raw_prefixes[raw_name]
            require(stage == "CHILD_" + raw_name.upper() and not final
                    and raw_frame["global_seq"] == self.sequence + 1
                    and raw_frame["stream_seq"] == previous["frames"] + 1
                    and raw_frame["start"] == previous["bytes"] == state["persisted_bytes"] == state["accepted_bytes"]
                    and raw_frame["end"] == state["read_bytes"]
                    and value["raw_bytes"] == raw_frame["end"] - raw_frame["start"]
                    and value["base64"] == raw_frame["base64"], "RAW_FRAME_PREFIX_MISMATCH")
        else:
            require(stage not in {"CHILD_STDOUT", "CHILD_STDERR"}, "RAW_FRAME_BINDING_REQUIRED")
        evidence = self.policy["evidence"]
        event = {"schema": "r45-supervisor-witness/1", "seq": self.sequence + 1,
            "previous_sha256": self.head, "stage": stage, "value": value}
        raw = canonical(event)
        digest = hashlib.sha256(raw).hexdigest()
        data = canonical({**event, "sha256": digest}) + b"\n"
        cap = evidence["witness_bytes"]
        if not final:
            cap -= evidence["failure_reserve_bytes"]
        require(len(data) <= evidence["max_record_bytes"] and self.charged + len(data) <= cap,
                "WITNESS_CAP_EXCEEDED")
        self.charged += len(data)
        write_attempted = persisted = False
        try:
            self.deadline.admit(cleanup=final)
            write_attempted = True
            count = self.io.call("witness.write", "write", self.stream.write, data,
                                 requested=len(data), direction="write", result_bytes=lambda result: result)
            require(count == len(data), "WITNESS_SHORT_WRITE")
            if raw_name is not None:
                self.raw_prefixes[raw_name] = {**self.raw_prefixes[raw_name], "accepted_bytes": raw_frame["end"],
                    "accepted_frames": raw_frame["stream_seq"], "accepted_sha256": raw_frame["sha256"]}
                self.raw_prefixes[raw_name]["pending"]["stage"] = "RAW_WRITE_ACCEPTED_PREFIX"
            self.deadline.admit(cleanup=final)
            self.io.call("witness.flush", "flush", self.stream.flush)
            if raw_name is not None: self.raw_prefixes[raw_name]["pending"]["flush"] = "RETURNED_SUCCESS"
            self.deadline.admit(cleanup=final)
            descriptor = self.io.call("witness.fileno", "fileno", self.stream.fileno)
            self.io.call("witness.fsync", "fsync", os.fsync, descriptor)
            persisted = True
            self.io.persisted_serialized += len(data)
            committed_raw = {name: dict(prefix) for name, prefix in self.witness_prefix["raw"].items()}
            if raw_name is not None:
                self.raw_prefixes[raw_name] = {**self.raw_prefixes[raw_name], "persisted_bytes": raw_frame["end"],
                    "persisted_frames": raw_frame["stream_seq"], "persisted_sha256": raw_frame["sha256"]}
                self.raw_prefixes[raw_name]["pending"].update(
                    fsync="RETURNED_SUCCESS", stage="RAW_PERSISTENCE_CONFIRMED_PREFIX")
                committed_raw[raw_name] = {"bytes": raw_frame["end"], "frames": raw_frame["stream_seq"],
                    "sha256": raw_frame["sha256"], "last_witness_seq": self.sequence + 1}
            # One reference publication is the authoritative in-memory commit point.
            committed = {"sequence": self.sequence + 1, "bytes": self.confirmed + len(data),
                         "sha256": digest, "raw": committed_raw}
            self.witness_prefix = committed
            if raw_name is not None: self.raw_prefixes[raw_name]["pending"] = None
            if stage == "ADMITTED":
                self.pre_qpc_ref = {"sequence": self.sequence, "sha256": self.head,
                                    "field": "value.PRE_QPC_COST"}
        except BaseException:
            if write_attempted and not persisted: self.io.uncertain_serialized += len(data)
            if raw_name is not None and self.raw_prefixes[raw_name]["pending"] is not None:
                self.raw_prefixes[raw_name]["pending"]["stage"] = (
                    "POST_COMMIT_ACCOUNTING_UNCONFIRMED" if self.sequence == event["seq"] and self.head == digest
                    else "WITNESS_COMMIT_UNCONFIRMED" if persisted else "RAW_PERSISTENCE_UNCERTAIN")
            self.poisoned = True
            raise

    def drain(self, child):
        for _ in range(self.policy["observer"]["max_drain_chunks"]):
            progress = False
            for name in ("stdout", "stderr"):
                if child.resumed and not child.exited and self.deadline.elapsed() >= WORK_SECONDS:
                    child.terminate_owned()
                self.deadline.admit()
                if self.eof[name]: continue
                handle = self.handles[name + "_read"]
                available = DWORD()
                ok, code = self.api.call("PeekNamedPipe", handle, None, 0, None, ctypes.byref(available), None)
                if not ok:
                    if code == 109:
                        self.eof[name] = True
                        continue
                    raise ctypes.WinError(code)
                if not available.value: continue
                size = min(available.value, self.policy["observer"]["pipe_chunk_bytes"])
                buffer, returned = ctypes.create_string_buffer(size), DWORD()
                self.io.call("pipe.read", "read", lambda:
                    self.api.check("ReadFile", handle, buffer, size, ctypes.byref(returned), None),
                    requested=size, direction="read", result_bytes=lambda result: returned.value)
                require(returned.value <= size, "PIPE_RETURN_INVALID")
                start = self.raw_counts[name]
                self.raw_counts[name] += returned.value
                state = self.raw_prefixes[name]
                state["read_bytes"] = self.raw_counts[name]
                state["read_frames"] += 1
                state["read_sha256"] = "UNKNOWN"
                state["pending"] = {"start": start, "end": self.raw_counts[name],
                    "global_seq": self.sequence + 1, "stream_seq": state["read_frames"],
                    "stage": "RAW_READ_PREFIX", "flush": "NOT_ATTEMPTED", "fsync": "NOT_ATTEMPTED"}
                raw = buffer.raw[:returned.value]
                self.raw_hashers[name].update(raw)
                state["read_sha256"] = self.raw_hashers[name].hexdigest()
                require(self.raw_counts[name] <= self.policy["evidence"][name + "_raw_bytes"], "PIPE_OUTPUT_LIMIT")
                encoded = base64.b64encode(raw).decode("ascii")
                frame = {"name": name, "start": start, "end": self.raw_counts[name],
                    "global_seq": self.sequence + 1, "stream_seq": state["read_frames"],
                    "sha256": state["read_sha256"], "base64": encoded}
                self.append("CHILD_" + name.upper(), {"raw_bytes": returned.value, "base64": encoded}, raw_frame=frame)
                progress = True
            if not progress: break

    def close_pipes(self):
        for name in list(self.handles):
            try:
                self.close_handle(name)
            except Exception as error:
                self.close_errors.append(error_record(error, "CloseHandle:" + name))

    def close_file(self):
        if self.stream is None or self.stream.closed or self.file_close_attempted: return
        self.file_close_attempted = True
        try:
            self.deadline.admit(HARD_SECONDS, cleanup=True)
            self.io.call("witness.close", "close", self.stream.close)
            require(self.stream.closed, "WITNESS_CLOSE_UNCONFIRMED")
        except Exception as error:
            self.close_errors.append(error_record(error, "WITNESS_CLOSE"))


class ChildProcessController:
    def __init__(self, api, job, deadline):
        self.api, self.job, self.deadline = api, job, deadline
        self.process = self.thread = None
        self.pid = self.tid = None
        self.creation_time = "UNKNOWN"
        self.member = False
        self.resumed = self.creation_attempted = self.exited = False
        self.exit_code = "UNKNOWN"
        self.cleanup_errors = []
        self.attribute_cleanup_error = None
        self.close_attempted = set()
        self.fallback_termination_requested = False

    def create(self, policy, outputs):
        require(not self.creation_attempted, "CHILD_CREATION_RETRY_REFUSED")
        self.creation_attempted = True
        self.deadline.admit(WORK_SECONDS)
        size = SIZE_T()
        result, code = self.api.call("InitializeProcThreadAttributeList", None, 2, 0, ctypes.byref(size))
        require(not result and code == 122 and size.value > 0, "ATTRIBUTE_LIST_SIZE_QUERY")
        require(size.value <= policy["observer"]["attribute_buffer_bytes"], "ATTRIBUTE_BUFFER_LIMIT")
        storage = ctypes.create_string_buffer(size.value)
        attributes = ctypes.cast(storage, LPVOID)
        initialized = False
        try:
            self.api.check("InitializeProcThreadAttributeList", attributes, 2, 0, ctypes.byref(size))
            initialized = True
            inherited = (HANDLE * 3)(*outputs.inherited())
            jobs = (HANDLE * 1)(self.job.handle)
            self.api.check("UpdateProcThreadAttribute", attributes, 0, 0x00020002,
                ctypes.cast(inherited, LPVOID), ctypes.sizeof(inherited), None, None)
            self.api.check("UpdateProcThreadAttribute", attributes, 0, 0x0002000D,
                ctypes.cast(jobs, LPVOID), ctypes.sizeof(jobs), None, None)
            startup = STARTUPINFOEXW()
            startup.StartupInfo.cb = ctypes.sizeof(STARTUPINFOEXW)
            startup.StartupInfo.dwFlags = 0x100
            startup.StartupInfo.hStdInput, startup.StartupInfo.hStdOutput, startup.StartupInfo.hStdError = outputs.inherited()
            startup.lpAttributeList = attributes
            command = ctypes.create_unicode_buffer(subprocess.list2cmdline(policy["child_argv"]))
            info = PROCESS_INFORMATION()
            flags = 0x4 | 0x00080000 | 0x08000000
            self.deadline.admit(WORK_SECONDS)
            self.api.check("CreateProcessW", str(PYTHON), command, None, None, True, flags,
                None, str(PROJECT), ctypes.cast(ctypes.byref(startup), ctypes.POINTER(STARTUPINFOW)), ctypes.byref(info))
            self.process, self.thread = info.hProcess, info.hThread
            self.pid, self.tid = info.dwProcessId, info.dwThreadId
            outputs.release_child_ends()
            require(self.job.contains(self.process), "CREATED_CHILD_JOB_MISMATCH")
            self.member = True
            self.creation_time = process_times(self.api, self.process)["creation_time"]
            image = ctypes.create_unicode_buffer(32768)
            length = DWORD(32768)
            self.api.check("QueryFullProcessImageNameW", self.process, 0, image, ctypes.byref(length))
            require(Path(image.value) == PYTHON, "CHILD_IMAGE_IDENTITY")
        finally:
            if initialized:
                try:
                    self.api.call("DeleteProcThreadAttributeList", attributes, cleanup=True)
                except Exception as error:
                    self.attribute_cleanup_error = error_record(error, "DeleteProcThreadAttributeList")
                    self.cleanup_errors.append(self.attribute_cleanup_error)

    def resume(self):
        self.deadline.admit(WORK_SECONDS)
        require(self.process is not None and self.member and not self.resumed, "CHILD_RESUME_SCOPE")
        require(self.attribute_cleanup_error is None, "ATTRIBUTE_CLEANUP_UNCONFIRMED")
        require(self.job.contains(self.process), "CHILD_JOB_MEMBERSHIP_LOST")
        value, code = self.api.call("ResumeThread", self.thread)
        if value == 0xFFFFFFFF: raise ctypes.WinError(code)
        require(value == 1, "SUSPEND_COUNT_UNEXPECTED")
        self.resumed = True

    def wait(self, milliseconds, cleanup=False):
        status, code = self.api.call("WaitForSingleObject", self.process, milliseconds, cleanup=cleanup)
        if status == 0:
            self.exited = True
            result = DWORD()
            self.api.check("GetExitCodeProcess", self.process, ctypes.byref(result), cleanup=cleanup)
            self.exit_code = result.value
        elif status == 0xFFFFFFFF:
            raise ctypes.WinError(code)
        else:
            require(status == 258, "PROCESS_WAIT_UNEXPECTED")
        return self.exited

    def terminate_owned(self):
        if self.process is None or self.exited: return
        if self.member:
            self.job.terminate(1)
        else:
            # The returned creation handle is owned even if membership validation failed.
            if self.fallback_termination_requested: return
            self.fallback_termination_requested = True
            self.api.check("TerminateProcess", self.process, 1, cleanup=True)

    def close(self):
        for name in ("thread", "process"):
            handle = getattr(self, name)
            if handle is None or name in self.close_attempted: continue
            self.close_attempted.add(name)
            try:
                self.api.close(handle)
                setattr(self, name, None)
            except Exception as error:
                self.cleanup_errors.append(error_record(error, "CloseHandle:" + name))


def process_times(api, process):
    creation, exit_time, kernel, user = FILETIME(), FILETIME(), FILETIME(), FILETIME()
    api.check("GetProcessTimes", process, ctypes.byref(creation), ctypes.byref(exit_time),
              ctypes.byref(kernel), ctypes.byref(user))
    value = lambda item: (item.dwHighDateTime << 32) | item.dwLowDateTime
    return {"creation_time": value(creation), "kernel_100ns": value(kernel), "user_100ns": value(user)}


class ResourceObserver:
    def __init__(self, api, deadline, policy):
        self.api, self.deadline, self.policy = api, deadline, policy
        self.parent, _ = api.call("GetCurrentProcess")  # borrowed pseudo-handle, never closed
        require(self.parent is not None, "PARENT_PSEUDOHANDLE")
        self.parent_pid, _ = api.call("GetCurrentProcessId")
        self.parent_creation = process_times(api, self.parent)["creation_time"]
        self.samples = 0
        self.first = self.last = None
        self.last_good_memory = {}

    def process_snapshot(self, handle, owner):
        io_value, memory = IO_COUNTERS(), PROCESS_MEMORY_COUNTERS_EX()
        self.api.check("GetProcessIoCounters", handle, ctypes.byref(io_value))
        memory.cb = ctypes.sizeof(memory)
        result = {"io": {name: getattr(io_value, name) for name in IO_FIELDS}}
        try:
            self.api.check("K32GetProcessMemoryInfo", handle, ctypes.byref(memory), ctypes.sizeof(memory))
            result["memory"] = {name: getattr(memory, name) for name in
                ("PeakWorkingSetSize", "WorkingSetSize", "PrivateUsage", "PeakPagefileUsage")}
            self.last_good_memory[owner] = {"qpc": self.deadline.now(), **result["memory"]}
        except OSError as error:
            result["memory"] = "UNKNOWN"
            result["memory_error"] = error_record(error, "GetProcessMemoryInfo")
        return result

    def sample(self, child, job, after_exit=False):
        self.deadline.admit()
        require(self.samples < self.policy["observer"]["max_samples"], "SAMPLE_LIMIT")
        self.samples += 1
        result = {"qpc": self.deadline.now(), "sample": self.samples,
            "CHILD_PROCESS_IO": self.process_snapshot(child.process, "child"),
            "SUPERVISOR_PROCESS_IO": self.process_snapshot(self.parent, "parent"),
            "JOB_AGGREGATE_IO": job.accounting(), "after_confirmed_exit": after_exit,
            "SIMULTANEOUS_TREE_PEAK": "UNKNOWN", "ETW": "NOT_ENABLED",
            "FULL_IO_COUNT_PROVED": False, "PHYSICAL_DISK_IO_PROVED": False}
        if self.first is None: self.first = result
        self.last = result
        for owner, key, limit in (("child", "CHILD_PROCESS_IO", "child_peak_working_set_bytes"),
                                 ("parent", "SUPERVISOR_PROCESS_IO", "supervisor_peak_working_set_bytes")):
            value = result[key]["memory"]
            if value == "UNKNOWN":
                require(after_exit, "MEMORY_OBSERVATION_INCOMPLETE")
            else:
                require(value["PeakWorkingSetSize"] <= self.policy["resources"][4]["approved_maximum"][limit],
                        "WORKING_SET_LIMIT_EXCEEDED")
        return result


def supervise(policy):
    api = WindowsApi(policy["observer"]["max_api_calls"])
    deadline = DeadlineController(api)
    api.deadline = deadline
    job = JobController(api)
    output = OutputController(api, deadline, policy)
    child = ChildProcessController(api, job, deadline)
    observer = None
    primary = None
    cleanup_errors = []
    receipt = None
    try:
        version = sys.getwindowsversion()
        require(version.major >= 10 and version.build == policy["_windows_build"], "RUNTIME_OS_BUILD_UNRESOLVED")
        observer = ResourceObserver(api, deadline, policy)
        parent_job = BOOL()
        api.check("IsProcessInJob", observer.parent, None, ctypes.byref(parent_job))
        output.open()
        output.append("ADMITTED", {"supervisor_pid": observer.parent_pid,
            "supervisor_creation_time": observer.parent_creation, "host_in_job": bool(parent_job.value),
            "source_lock_digest": policy["_source_lock_sha256"], "policy_digest": policy["_policy_sha256"],
            "QPC_start": deadline.start, "QPC_frequency": deadline.frequency,
            "input_read_bytes_before_QPC": policy["_validated_reads"],
            "PRE_QPC_COST": {"explicit_io": policy["_pre_qpc_cost"],
                "source_reads": policy["_source_read_records"],
                "run_id": policy["_policy_sha256"],
                "unobserved_startup": ["Python_initialization", "module_imports", "DLL_lazy_loading",
                                       "native_loader_IO", "elapsed_time_before_QPC"],
                "completeness_status": "EXPLICIT_READS_ACCOUNTED_BOOTSTRAP_AND_NATIVE_IO_UNPROVEN"}})
        job.create(policy["job"])
        output.append("LAUNCH_INTENT", {"executable": str(PYTHON), "argv": policy["child_argv"], "launches": 1})
        child.create(policy, output)
        output.append("CHILD_SUSPENDED", {"child_pid": child.pid, "child_creation_time": child.creation_time,
            "job_identity": "private creation-time job bound to this invocation", "membership_confirmed": child.member})
        output.append("RESOURCE_BEFORE", observer.sample(child, job))
        child.resume()
        while not child.exited:
            elapsed = deadline.elapsed()
            if elapsed >= WORK_SECONDS and not job.termination_requested:
                job.terminate(1)
            if elapsed >= READ_SECONDS: break
            output.drain(child)
            output.append("RESOURCE_SAMPLE", observer.sample(child, job))
            child.wait(deadline.wait_ms(policy["observer"]["poll_ms"], WORK_SECONDS if not job.termination_requested else READ_SECONDS))
        if child.exited and deadline.elapsed() < READ_SECONDS:
            while not all(output.eof.values()):
                deadline.admit()
                output.drain(child)
            output.append("RESOURCE_AFTER_EXIT", observer.sample(child, job, after_exit=True))
    except BaseException as error:
        primary = error_record(error, "SUPERVISE")
    finally:
        if child.process is not None and not child.exited:
            try: child.terminate_owned()
            except Exception as error: cleanup_errors.append(error_record(error, "TERMINATE_OWNED"))
            try:
                if deadline.elapsed(cleanup=True) < READ_SECONDS:
                    # One bounded cleanup wait consumes reserved calls, with no retry loop.
                    remaining = max(0, int((READ_SECONDS - deadline.elapsed(cleanup=True)) * 1000))
                    child.wait(remaining, cleanup=True)
            except Exception as error: cleanup_errors.append(error_record(error, "WAIT_CLEANUP"))
        output.close_pipes()
        # Query final Job counters before closing the last owned Job handle.
        job_after = "UNKNOWN"
        if job.handle is not None:
            try:
                deadline.admit()
                job_after = job.accounting()
            except Exception as error: cleanup_errors.append(error_record(error, "FINAL_JOB_QUERY"))
        child.close()
        try: job.close()
        except Exception as error: cleanup_errors.append(error_record(error, "JOB_CLOSE"))
        cleanup_errors.extend(child.cleanup_errors + output.close_errors)
        try:
            tick = deadline.now(cleanup=True)
            receipt = {"supervisor_pid": observer.parent_pid if observer else "UNKNOWN",
                "supervisor_creation_time": observer.parent_creation if observer else "UNKNOWN",
                "child_pid": child.pid or "UNKNOWN", "child_creation_time": child.creation_time,
                "job_identity": {"kind": "owned unnamed creation-time Job", "created": job.created,
                    "policy_binding": policy["_policy_sha256"], "kernel_object_identifier": "UNKNOWN"},
                "executable_path": str(PYTHON),
                "argv": policy["child_argv"], "source_lock_digest": policy["_source_lock_sha256"],
                "policy_digest": policy["_policy_sha256"], "QPC_start": deadline.start, "QPC_end": tick,
                "elapsed_time": (tick - deadline.start) / deadline.frequency,
                "child_exit_code": child.exit_code,
                "termination_requested": job.termination_requested or child.fallback_termination_requested,
                "termination_confirmed": child.exited,
                "exit_status": "EXITED" if child.exited else "TERMINATION_PENDING" if child.pid is not None else "EXIT_CODE_UNKNOWN",
                "cleanup_status": "CLEANUP_UNCONFIRMED",
                "owned_api_cleanup_status": "CLEANUP_CONFIRMED" if not cleanup_errors and child.exited else "CLEANUP_UNCONFIRMED",
                "receipt_close_confirmation": "REQUIRES_EXTERNAL_EXIT_AND_FILE_OBSERVATION",
                "process_io_before": observer.first if observer and observer.first else "UNKNOWN",
                "process_io_after": observer.last if observer and observer.last else "UNKNOWN",
                "job_io_before": observer.first["JOB_AGGREGATE_IO"] if observer and observer.first else "UNKNOWN",
                "job_io_after": job_after, "process_memory_peak": observer.last_good_memory if observer else "UNKNOWN",
                "job_memory_peak": job_after, "SIMULTANEOUS_TREE_PEAK": "UNKNOWN",
                "parent_overhead": {"api_calls": dict(api.counts), "preflight_input_bytes": policy["_validated_reads"]},
                "output_bytes": {"charged_before_receipt": output.charged, "confirmed_before_receipt": output.confirmed,
                                 "child_stdio_raw": output.raw_counts},
                "stdio_eof_confirmed": dict(output.eof),
                "owned_handle_cleanup": {"job_closed": job.closed_confirmed,
                    "remaining_pipe_handles": sorted(output.handles),
                    "process_close_confirmed": child.process is None, "thread_close_confirmed": child.thread is None},
                "evidence_persistence_status": "CONFIRMED_PREFIX_ONLY_FINAL_RECEIPT_REQUIRES_FSYNC",
                "primary_error": primary, "cleanup_errors": cleanup_errors, "ETW": "NOT_ENABLED",
                "STRICT_120S_COMPLETION_PROVED": False,
                "unknown_fields": ["physical_disk_IO", "T20_per_phase_durable_trace", "receipt_self_close", "native_termination_lag"]}
            receipt["accounting"] = {
                "run_id": policy["_policy_sha256"],
                "receipt_id": policy["_policy_sha256"] + "/FINAL_RECEIPT/" + str(output.sequence + 1),
                "supervisor_identity_ref": ["supervisor_pid", "supervisor_creation_time"],
                "child_identity_ref": ["child_pid", "child_creation_time"],
                "witness_file": {"relative_path": "SUPERVISOR_WITNESS.jsonl",
                    "ownership": "EXCLUSIVE_XB_IN_POLICY_OUTPUT_ROOT", "native_file_id": "UNKNOWN"},
                "pre_qpc_cost_ref": output.pre_qpc_ref,
                "explicit_io": output.io.snapshot(),
                "raw_prefixes": output.prefix_snapshot(),
                "witness_prefix_before_receipt": {key: output.witness_prefix[key]
                    for key in ("sequence", "bytes", "sha256")},
                "coverage_start": "POLICY_VALIDATOR_CREATED_BOOTSTRAP_EXCLUDED",
                "coverage_end": {"phase": "BEFORE_FINAL_RECEIPT_SERIALIZATION", "qpc_observed_before_build": tick},
                "last_api_snapshot_ref": "parent_overhead.api_calls",
                "last_io_snapshot_ref": "process_io_after; sequential query timestamps apply",
                "last_memory_snapshot_ref": "process_memory_peak; per-owner qpc applies",
                "raw_confirmation_phase": "AFTER_FULL_FRAME_WRITE_FLUSH_FSYNC_RETURN",
                "witness_commit_phase": "AUTHORITATIVE_PREFIX_REFERENCE_PUBLICATION",
                "handle_close_attempted": {"job": job.close_attempted,
                    "child": sorted(child.close_attempted), "stdio": sorted(output.close_attempted),
                    "witness_file": output.file_close_attempted},
                "handle_close_confirmed_ref": "owned_handle_cleanup",
                "termination_requested_ref": "termination_requested",
                "termination_confirmed_ref": "termination_confirmed",
                "receipt_own_persistence": "PENDING_AT_SERIALIZATION_REQUIRES_EXTERNAL_VERIFICATION",
                "post_receipt_operations": {"wrapped_QPC_calls_upper": 5,
                    "CloseHandle_calls": 0, "Wait_calls": 0,
                    "other": ["JSON_and_digest", "write", "flush", "fileno", "fsync", "FileIO_close",
                              "return_evaluation", "interpreter_exit"]},
                "uncovered_costs": ["pre_QPC_elapsed_and_implicit_IO", "receipt_own_write_and_confirmation",
                    "FileIO_close_and_exit_tail", "final_parent_memory_peak", "physical_IO"],
                "completeness_status": ["RECEIPT_COVERS_CONFIRMED_PREFIX", "RECEIPT_COVERS_OBSERVED_PHASES",
                    "POST_RECEIPT_COST_UNOBSERVED", "FINAL_CLEANUP_UNCONFIRMED",
                    "FULL_LIFECYCLE_COVERAGE_UNPROVEN", "EXTERNAL_TAIL_OBSERVER_REQUIRED"]}
            output.append("FINAL_RECEIPT", receipt, final=True)
        except Exception as error:
            cleanup_errors.append(error_record(error, "FINAL_RECEIPT"))
        finally:
            output.close_file()
    return 0 if (primary is None and child.exited and child.exit_code == 0 and not job.termination_requested
                 and not cleanup_errors and not output.close_errors and output.stream is not None
                 and output.stream.closed and not output.poisoned and receipt is not None
                 and all(output.eof.values()) and job.closed_confirmed
                 and child.process is None and child.thread is None and not output.handles) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--policy", required=True)
    args = parser.parse_args(argv)
    validator = PolicyValidator()
    policy = validator.validate(args.policy)
    return supervise(policy)


if __name__ == "__main__":
    raise SystemExit(main())
