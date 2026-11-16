"""R43: isolated, grant-gated tests of the actual R41 checkpoint implementation.

Static implementation only. Importing this file defines data/classes/functions;
it performs no imports, input reads, target loading, allocation of test fixtures,
or output writes. A separately approved complete execution packet is required.
Model FileIO observations are not native syscalls or physical durability proof.
"""

SUT_FILE = r"D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py"
SUT_SHA256 = "245a35d4786fdf4e43b532d11a70a9db1b9be1d5d81d1f6a3f78e1ecfd96646f"
PYTHON_FILE = r"C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
RESEARCH = r"D:\毕业设计\research_g2_dsat_implementation"
MANIFEST_FILE = RESEARCH + r"\2026-11-15_r42\R42_28_TEST_MANIFEST.json"
MANIFEST_SHA256 = "aaf20e86f733b2eaa7b09254bfaca86b4d23ca69ef4ebf6fc001e11b9db0219d"
PREFIX_FILE = RESEARCH + r"\2026-11-14_r40\sources\PROTOCOL_PREFIX.jsonl"
PREFIX_SHA256 = "88ad8c3a00de46a4b2da2eb96a036693771279bd8d4e975cf3f8a80de76ce063"
RECIPE_FILE = RESEARCH + r"\2026-11-14_r40\sources\CAPACITY_INPUT_RECIPE.json"
ORIGINAL_MANIFEST = RESEARCH + r"\2026-11-12_r33\R33_68_TEST_MANIFEST.json"
EVIDENCE_BYTES = 2097152
TEST_IDS = (
    "R40-PC-T01", "R40-PC-T02", "R40-PC-T03", "R40-PC-T04",
    "R40-PC-T05", "R40-PC-T06", "R40-PC-T07", "R40-PC-T08",
    "R40-PC-T09", "R40-PC-T10", "R40-PC-T11", "R40-PC-T12",
    "R40-PC-T13", "R40-PC-T14", "R40-PC-T15", "R40-PC-T16",
    "R40-PC-T17", "R40-PC-T18", "R40-PC-T19", "R40-PC-T20",
    "R40-PC-T21", "R40-PC-T22", "R40-PC-T23", "R40-PC-T24",
    "R40-PC-T25", "R40-PC-T26", "R40-PC-T27", "R40-PC-T28",
)
EVIDENCE_CAPS = {
    "RESULTS.json": 524288, "stdout.log": 65536, "stderr.log": 65536,
    "TEST_MANIFEST.json": 32768, "SOURCE_LOCK.json": 16384,
    "STATE_WITNESS.json": 131072, "RESOURCE_LEDGER.json": 32768,
    "EARLY_FAILURE.json": 65536, "physical_journal.jsonl": 65536,
}
REQUIRED_LIMITS = (
    "fault_arms", "observation_events", "model_api_calls", "native_api_calls",
    "fixture_total", "lock_total", "new_directories", "whole_process_rss_bytes",
    "cumulative_native_payload_bytes",
)


class FaultSchedule:
    """Independent observer and one-shot boundary fault plan, never a classifier."""

    def __init__(self, limits=None):
        self.limits = limits
        self.events = []
        self.arms = []
        self.fired = []
        self.counts = {}
        self.test_id, self.variant = None, None
        self.phase = "INITIALIZATION"
        self.fixtures = 0
        self.locks = 0
        self.rss_peak = None
        self._memory_query = None
        self.started = time.perf_counter()
        self.deadline = self.started + 120

    def check(self):
        if time.perf_counter() >= self.deadline:
            raise TimeoutError("HARNESS_REAL_WALL_DEADLINE")
        if self.limits is not None:
            self.measure_rss()

    def measure_rss(self):
        """Read OS lifetime peak working set; detection is not a hard memory cap."""
        if os.name != "nt":
            raise RuntimeError("WINDOWS_MEMORY_MONITOR_REQUIRED")
        native_count = sum(v for k, v in self.counts.items() if "/NATIVE/" in k)
        if native_count + 2 > self.limits["native_api_calls"]:
            raise RuntimeError("MEMORY_QUERY_API_BUDGET")
        if self._memory_query is None:
            class MemoryCounters(ctypes.Structure):
                _fields_ = [("cb", ctypes.c_ulong), ("faults", ctypes.c_ulong)] + [
                    (name, ctypes.c_size_t) for name in ("peak_working_set", "working_set",
                        "peak_paged", "paged", "peak_nonpaged", "nonpaged", "pagefile", "peak_pagefile", "private")]
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.GetCurrentProcess.restype = ctypes.c_void_p
            kernel.K32GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(MemoryCounters), ctypes.c_ulong]
            self._memory_query = kernel, MemoryCounters
        kernel, counter_type = self._memory_query
        value = counter_type()
        value.cb = ctypes.sizeof(value)
        for operation in ("GetCurrentProcess", "K32GetProcessMemoryInfo"):
            key = "HARNESS_IO/NATIVE/" + self.phase + "/" + operation
            self.counts[key] = self.counts.get(key, 0) + 1
        handle = kernel.GetCurrentProcess()  # pseudo-handle; no OpenProcess handle allocation
        if not kernel.K32GetProcessMemoryInfo(handle, ctypes.byref(value), value.cb):
            raise OSError(ctypes.get_last_error(), "PROCESS_MEMORY_QUERY_FAILED")
        self.rss_peak = max(self.rss_peak or 0, int(value.peak_working_set))
        if self.rss_peak > self.limits["whole_process_rss_bytes"]:
            raise RuntimeError("WHOLE_PROCESS_PEAK_BUDGET_EXCEEDED")

    def event(self, owner, op, realm="MODEL", requested=0):
        self.check()
        key = owner + "/" + realm + "/" + self.phase + "/" + op
        if self.limits is not None:
            if len(self.events) >= self.limits["observation_events"]:
                raise RuntimeError("OBSERVATION_BUDGET_EXCEEDED")
            api = sum(v for k, v in self.counts.items() if ("/" + realm + "/") in k)
            name = "model_api_calls" if realm == "MODEL" else "native_api_calls"
            if api >= self.limits[name]:
                raise RuntimeError("API_BUDGET_EXCEEDED")
        self.counts[key] = self.counts.get(key, 0) + 1
        row = {"owner": owner, "realm": realm, "phase": self.phase, "op": op,
               "test_id": self.test_id, "variant": self.variant,
               "requested": requested, "accepted": None, "outcome": "ENTERED"}
        self.events.append(row)
        return row

    def arm(self, point, action):
        if self.limits is not None and len(self.arms) >= self.limits["fault_arms"]:
            raise RuntimeError("FAULT_ARM_BUDGET_EXCEEDED")
        self.arms.append({"point": point, "action": action, "used": False,
                          "test_id": self.test_id, "variant": self.variant})

    def fire(self, point, ctx):
        for arm in self.arms:
            if not arm["used"] and arm["point"] == point:
                arm["used"] = True
                self.fired.append({"point": point, "test_id": self.test_id,
                                   "variant": self.variant, "action": arm["action"]})
                action = arm["action"]
                if action.startswith("clock:"):
                    ctx.clock = float(action.split(":", 1)[1])
                elif action == "owner_mismatch":
                    ctx.attempt["_owner"] = None
                elif action == "permission":
                    raise PermissionError(13, "SYNTHETIC_METADATA_PERMISSION")
                elif action == "raise":
                    raise OSError(22, "SYNTHETIC_BOUNDARY_FAULT")
                else:
                    raise AssertionError("UNKNOWN_FAULT_ACTION")

    def assert_consumed(self, start):
        assert_case_invariants(all(x["used"] for x in self.arms[start:]), "UNFIRED_FAULT")


class ObservedFileIO:
    def __init__(self, ctx, path, reader=False):
        self.ctx, self.path, self.reader = ctx, path, reader
        self.closed = False
        self.cursor = 0 if reader else len(ctx.files[str(path)])
        self.fd = len(ctx.handles) + 1
        ctx.handles[self.fd] = self
        self.mode = "normal"

    def write(self, data):
        assert_case_invariants(not self.closed and not self.reader, "INVALID_MODEL_WRITE")
        ev = self.ctx.audit.event("SUT_IO", "write", requested=len(data))
        self.ctx.audit.fire("write_enter", self.ctx)
        if self.mode == "raise_after_accept":
            self.ctx.files[str(self.path)].extend(data[:1])
            self.cursor += 1
            ev.update(accepted=1, outcome="RAISED_AFTER_ACCEPT")
            raise OSError(22, "SYNTHETIC_ACCEPT_THEN_ERROR")
        count = 0 if self.mode == "zero" else 1 if self.mode == "partial" else len(data)
        self.ctx.files[str(self.path)].extend(data[:count])
        self.cursor += count
        ev.update(accepted=count, outcome="RETURNED", returned=count)
        self.ctx.audit.fire("write_return", self.ctx)
        return count

    def flush(self):
        ev = self.ctx.audit.event("SUT_IO", "flush")
        self.ctx.audit.fire("flush_enter", self.ctx)
        ev["outcome"] = "RETURNED"
        self.ctx.audit.fire("flush_return", self.ctx)

    def fileno(self):
        self.ctx.audit.event("SUT_IO", "fileno")["outcome"] = "RETURNED"
        return self.fd

    def tell(self):
        ev = self.ctx.audit.event("SUT_IO", "tell")
        value = self.cursor + self.ctx.tell_delta
        ev["outcome"] = "RETURNED"
        self.ctx.audit.fire("tell_return", self.ctx)
        return value

    def read(self, size):
        ev = self.ctx.audit.event("SUT_IO", "read", requested=size)
        data = bytes(self.ctx.files[str(self.path)][self.cursor:self.cursor + size])
        self.cursor += len(data)
        ev.update(accepted=len(data), outcome="RETURNED")
        self.ctx.audit.fire("read_return", self.ctx)
        return data

    def close(self):
        ev = self.ctx.audit.event("SUT_IO", "close")
        self.ctx.audit.fire("close_enter", self.ctx)
        self.closed = True
        ev["outcome"] = "RETURNED"

    def contents(self):
        return bytes(self.ctx.files[str(self.path)])


class ObservedLedger(dict):
    def __init__(self, ctx, value):
        dict.__init__(self, value)
        self.ctx = ctx

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if key in {"SERIALIZED_BYTES", "charged_bytes", "state"}:
            self.ctx.audit.fire("ledger:" + key, self.ctx)
        if key == "state":
            self.ctx.audit.fire("ledger_state:" + value, self.ctx)


class PublicationProbeState:
    def __setattr__(self, name, value):
        context = self.__dict__.get("_probe_context")
        if context is not None and name == "journal_sequence":
            context.audit.fire("before_sequence", context)
        object.__setattr__(self, name, value)
        if context is not None and name in {"journal_sequence", "journal_head", "journal_bytes"}:
            context.audit.fire("after:" + name, context)


class SyntheticPath:
    """Filesystem boundary with stdlib path lexing and observed in-memory I/O."""

    def __init__(self, ctx, value):
        self.ctx = ctx
        self.p = value.p if isinstance(value, SyntheticPath) else PureWindowsPath(value)

    def __str__(self): return str(self.p)
    def __hash__(self): return hash(self.p)
    def __eq__(self, other): return isinstance(other, SyntheticPath) and self.p == other.p
    def __truediv__(self, part): return SyntheticPath(self.ctx, self.p / part)
    @property
    def name(self): return self.p.name
    @property
    def suffix(self): return self.p.suffix
    @property
    def parent(self): return SyntheticPath(self.ctx, self.p.parent)
    @property
    def parents(self): return tuple(SyntheticPath(self.ctx, x) for x in self.p.parents)
    def is_absolute(self): return self.p.is_absolute()
    def absolute(self): return self
    def is_relative_to(self, other): return self.p.is_relative_to(other.p)
    def relative_to(self, other): return SyntheticPath(self.ctx, self.p.relative_to(other.p))
    def as_posix(self): return self.p.as_posix()
    def resolve(self, strict=False): return self
    def samefile(self, other):
        self.ctx.audit.event("SUT_IO", "samefile")["outcome"] = "RETURNED"
        return self == other

    def _observe(self, op):
        ev = self.ctx.audit.event("SUT_IO", op)
        self.ctx.audit.fire("path_metadata", self.ctx)
        ev["outcome"] = "RETURNED"
        return str(self) in self.ctx.files

    def exists(self): return self._observe("exists") or str(self) in self.ctx.directories
    def is_file(self): return self._observe("is_file")
    def is_dir(self):
        self._observe("is_dir")
        return str(self) in self.ctx.directories
    def is_symlink(self):
        self._observe("is_symlink")
        return False
    def stat(self):
        self._observe("stat")
        inode, extent = self.ctx.inode_delta, self.ctx.extent_delta
        if getattr(self.ctx, "identity_fault", None) and hasattr(self.ctx, "state"):
            row = self.ctx.state.byte_ledger[self.ctx.target.RUN_ID + "/EARLY_FAILURE.json"]
            if row["charged_bytes"] > self.ctx.initial_charge and self.name == "EARLY_FAILURE.json":
                inode += int(self.ctx.identity_fault == "inode")
                extent += int(self.ctx.identity_fault == "extent")
        value = types.SimpleNamespace(st_dev=1, st_ino=100 + inode,
            st_size=len(self.ctx.files.get(str(self), b"")) + extent,
            st_nlink=1, st_file_attributes=0, st_mtime_ns=1)
        self.ctx.audit.fire("stat_return", self.ctx)
        return value
    def lstat(self): return self.stat()
    def open(self, mode, buffering=0):
        ev = self.ctx.audit.event("SUT_IO", "open/create" if mode == "xb" else "open/read")
        key = str(self)
        if mode == "xb":
            if key in self.ctx.files:
                ev["outcome"] = "REFUSED_EXISTS"
                raise FileExistsError("MODEL_EXCLUSIVE_OPEN")
            self.ctx.files[key] = bytearray()
        elif mode != "rb" or key not in self.ctx.files:
            ev["outcome"] = "REFUSED"
            raise PermissionError("MODEL_OPEN_SCOPE")
        ev["outcome"] = "RETURNED"
        return ObservedFileIO(self.ctx, self, reader=(mode == "rb"))
    def read_bytes(self):
        stream = self.open("rb", buffering=0)
        try: return stream.read(len(self.ctx.files[str(self)]))
        finally: stream.close()


class IsolatedTargetContext:
    def __init__(self, target, audit, inputs):
        self.target, self.audit, self.inputs = target, audit, inputs
        self.clock = 10.0
        self.inode_delta = self.extent_delta = self.tell_delta = 0
        self.files, self.handles = {}, {}
        self.saved = {}

    def enter(self):
        m = self.target
        self.audit.fixtures += 1
        self.audit.locks += 1
        if self.audit.limits is not None:
            assert_case_invariants(self.audit.fixtures <= self.audit.limits["fixture_total"], "FIXTURE_BUDGET")
            assert_case_invariants(self.audit.locks <= self.audit.limits["lock_total"], "LOCK_BUDGET")
        keys = ("OUTPUT", "RUN", "APPROVAL", "Path", "os", "time", "datetime", "ENTRY_STATE")
        self.saved = {k: getattr(m, k) for k in keys}
        self.core = {k: getattr(m.State, k) for k in ("checkpoint", "reserve_bytes", "io_write",
            "commit_case_record", "safe_checkpoint", "_checkpoint_rejection")}
        m.Path = lambda value: SyntheticPath(self, value)
        m.OUTPUT = SyntheticPath(self, r"V:\r43\evidence")
        m.RUN = m.OUTPUT / m.RUN_ID
        m.APPROVAL = m.OUTPUT / "RUN_APPROVAL_RECEIPT.json"
        self.directories = {str(x) for x in (m.RUN, m.OUTPUT, *m.OUTPUT.parents)}
        m.os = types.SimpleNamespace(fstat=self.fstat, fsync=self.fsync, listdir=self.listdir)
        m.time = types.SimpleNamespace(perf_counter=lambda: self.clock,
                                      perf_counter_ns=lambda: int(self.clock * 1000000000))
        fixed = datetime.datetime(2026, 11, 14, 0, 0, 10, 1, tzinfo=datetime.timezone.utc)
        m.datetime = types.SimpleNamespace(timezone=datetime.timezone,
            datetime=types.SimpleNamespace(now=lambda zone: fixed))
        self.state = construct_case_state(self)
        m.ENTRY_STATE = self.state
        self.path = m.RUN / "EARLY_FAILURE.json"
        self.stream = self.state.journal
        self.start = snapshot_observations(self)
        self.initial_charge = self.start["charged"]
        return self

    def exit(self):
        try:
            for key, value in getattr(self, "core", {}).items():
                assert_case_invariants(getattr(self.target.State, key) is value, "SUT_FUNCTION_REPLACED")
        finally:
            # Dispose SUT-created Sink objects while their own module facades exist.
            try:
                if hasattr(self, "state"):
                    for sink in list(self.state.streams): sink.close()
                    self.state.streams.clear()
            finally:
                for key, value in self.saved.items(): setattr(self.target, key, value)
                # Fixture destruction is HARNESS memory release, not a SUT close ACK.
                for stream in self.handles.values(): stream.closed = True
                self.files.clear()
                self.handles.clear()
                self.saved.clear()
                for name in ("state", "stream", "path"):
                    if hasattr(self, name): delattr(self, name)

    def fstat(self, fd):
        ev = self.audit.event("SUT_IO", "fstat")
        stream = self.handles[fd]
        ev["outcome"] = "RETURNED"
        return stream.path.stat()

    def fsync(self, fd):
        ev = self.audit.event("SUT_IO", "fsync")
        self.audit.fire("fsync_enter", self)
        ev["outcome"] = "RETURNED"
        self.audit.fire("fsync_return", self)

    def listdir(self, path):
        ev = self.audit.event("SUT_IO", "listdir")
        names = set()
        parent = str(path)
        for name in self.files:
            lexical = PureWindowsPath(name)
            if str(lexical.parent) == parent: names.add(lexical.name)
        if str(self.target.RUN.parent) == parent: names.add(self.target.RUN.name)
        ev["outcome"] = "RETURNED"
        return sorted(names)

    def refused(self, call, code=None):
        try:
            call()
        except self.target.Refusal as error:
            if code is not None:
                assert_case_invariants(error.args == (code,), "WRONG_REFUSAL_CODE")
            return error
        raise AssertionError("EXPECTED_REFUSAL_MISSING")


def construct_case_state(ctx):
    m = ctx.target
    cls = type("ObservedState", (PublicationProbeState, m.State), {})
    s = object.__new__(cls)
    s.started = 0.0
    s.started_utc = "SYNTHETIC_UNIT_INPUT"
    s.work_deadline, s.terminal_deadline, s.terminal_read_deadline, s.deadline = 90., 115., 115., 120.
    s.terminal = s.stop_requested = s.finalization_incomplete = s.finalization_started = False
    s.persistence_ok = s.evidence_complete = True
    s.phase, s.current = "A1", "A01"
    s.terminal_attempts, s.checkpoint_attempts = 0, 1
    s.evidence_issues, s.close_attempted, s.write_attempted_paths = set(), set(), set()
    s.errors, s.details, s.origins, s.origin_failures, s.projections = [], [], [], [], []
    s.streams, s.connections, s.read_handles = [], [], []
    s.rows, s.artifacts, s.detail_refs, s.detail_cursors, s.exec_files = {}, {}, {}, {}, set()
    s.origin_records = {}
    s.command = {"runner_sha256": SUT_SHA256, "control_pins": []}
    s.command_digest = s.approval_digest = "0" * 64
    s.build = {"source_digest": "0" * 64, "engineering_source": []}
    s.build_verified = s.tests_finished = s.journal_closed = s.d24_active = False
    s.manifest = ctx.inputs["original_manifest"]
    s.spec_by_id = {x["test_id"]: x for x in s.manifest["tests"]}
    s.case_lifecycle = {x: "NOT_RUN" for x in s.spec_by_id}
    s.case_statuses = {x: [None, None] for x in s.spec_by_id}
    s.case_callback_counts = {x: 0 for x in s.spec_by_id}
    s.case_overflow = {x: False for x in s.spec_by_id}
    s.work_audits = {"memory": {"status": "NOT_MEASURED"}, "integrity": False, "provenance": False}
    s.read_audit = {"denied_terminal_checks": 0, "admitted_terminal_checks": 0,
                   "last_denial": None, "late_return_observations": 0, "confirmed_closed_read_handles": 0}
    s.meter = {"memory_connections": {"A1": 0, "H1": 0, "D1A": 0}, "memory_active": 0,
        "memory_peak": 0, "execute_calls": 0, "rollback_calls": 0, "threads_created": 0,
        "threads_peak": 1, "subprocesses": 0, "network": 0, "file_SQLite": 0,
        "outside_writes": 0, "denials": []}
    s.secrets = set()
    s.codec = (binascii, zlib)
    s.io_lock = threading.RLock()
    s.owned_handles, s.byte_ledger = {}, {}
    s.opening_output = None
    path = m.RUN / "EARLY_FAILURE.json"
    seed = ctx.inputs["prefix"]
    ctx.files[str(path)] = bytearray(seed)
    s.journal = ObservedFileIO(ctx, path)
    s.owned_handles[path] = s.journal
    s.journal_identity = (1, 100)
    s.journal_sequence, s.journal_bytes = 1, len(seed)
    s.journal_head = json.loads(seed)["sha256"]
    p = len(seed)
    s.byte_ledger[m.RUN_ID + "/EARLY_FAILURE.json"] = ObservedLedger(ctx, {
        "RESERVED_BYTES": 1048576, "SERIALIZED_BYTES": p, "BUFFERED_BYTES": 0,
        "WRITE_ATTEMPTED_BYTES": p, "WRITE_RETURNED_BYTES": p, "CONFIRMED_PERSISTED_BYTES": p,
        "PERSISTENCE_UNCERTAIN_BYTES": 0, "charged_bytes": p, "write_attempts": 1,
        "close_attempts": 0, "closed_confirmed": False, "state": "PUBLISHED", "poisoned": False})
    s._probe_context = ctx
    return s


def snapshot_observations(ctx):
    s = ctx.state
    ledger = s.byte_ledger[ctx.target.RUN_ID + "/EARLY_FAILURE.json"]
    return {"seq": s.journal_sequence, "head": s.journal_head, "bytes": s.journal_bytes,
            "contents": ctx.stream.contents() if hasattr(ctx, "stream") else s.journal.contents(),
            "charged": ledger["charged_bytes"], "confirmed": ledger["CONFIRMED_PERSISTED_BYTES"],
            "attempted": ledger["WRITE_ATTEMPTED_BYTES"], "poisoned": ledger["poisoned"],
            "terminal_attempts": s.terminal_attempts, "event_index": len(ctx.audit.events)}


def verify_prefix_chain(data):
    previous = "0" * 64
    for index, line in enumerate(data.splitlines(), 1):
        row = json.loads(line)
        digest = row.pop("sha256")
        encoded = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                             allow_nan=False).encode()
        assert_case_invariants(row["seq"] == index and row["previous_sha256"] == previous,
                               "CHAIN_ORDER_OR_LINK")
        assert_case_invariants(hashlib.sha256(encoded).hexdigest() == digest, "CHAIN_DIGEST")
        raw = zlib.decompress(binascii.a2b_base64(row["value"]["data"]))
        assert_case_invariants(len(raw) == row["value"]["raw_bytes"] and
            hashlib.sha256(raw).hexdigest() == row["value"]["raw_sha256"], "PAYLOAD_DIGEST")
        previous = digest
    return index if data else 0, previous


def verify_fee_equations(ctx, before, expected_writes=None, healthy=None, charge_delta=None):
    after = snapshot_observations(ctx)
    events = ctx.audit.events[before["event_index"]:]
    writes = [x for x in events if x["owner"] == "SUT_IO" and x["op"] == "write"]
    if expected_writes is not None:
        assert_case_invariants(len(writes) == expected_writes, "OBSERVED_WRITE_COUNT")
    assert_case_invariants(after["charged"] >= before["charged"], "CHARGE_REFUNDED")
    if charge_delta is not None:
        assert_case_invariants(after["charged"] - before["charged"] == charge_delta, "CHARGE_DELTA")
    if healthy is not None:
        assert_case_invariants(after["poisoned"] is (not healthy), "JOURNAL_HEALTH")
    assert_case_invariants(after["contents"][:len(before["contents"])] == before["contents"], "OLD_PREFIX_BYTES")
    if not writes:
        assert_case_invariants(after["contents"] == before["contents"] and after["seq"] == before["seq"]
            and after["head"] == before["head"] and after["confirmed"] == before["confirmed"], "PREWRITE_PREFIX")
    return after


def assert_case_invariants(condition, code):
    if not condition:
        raise AssertionError(code)


class PoisonClassification28:
    def __init__(self, target, audit, inputs):
        self.target, self.audit, self.inputs = target, audit, inputs
        self.witnesses = []
        self.dense_cache = None

    def dense(self):
        if self.dense_cache is None:
            raw = b"".join(hashlib.sha256(b"R40-CAPACITY-v1:" + i.to_bytes(4, "big")).digest()
                           for i in range(24000))
            text = base64.b85encode(raw).decode("ascii")
            self.dense_cache = [text[i * 7800:(i + 1) * 7800] for i in range(118)]
        return self.dense_cache

    def prepare_observation(self, c):
        s = c.state
        spec = s.spec_by_id["A01"]
        s.case_lifecycle["A01"] = "RUNNING"
        s.rows["A01"] = {"id": "A01", "group": "A1", "status": "RUNNING", "executed": True,
            "source_hash": spec["source_hash"], "runner_sha256": SUT_SHA256,
            "original_expected": spec["original_expected"], "trusted_execution_phase": "A1",
            "events": [], "detail": None, "diagnostic_status": "NOT_APPLICABLE",
            "details_status": "NOT_CAPTURED", "detail_indices": [],
            "case_call_completed": False, "case_interrupted": False}

    def charged(self, c, amount):
        row = c.state.byte_ledger[c.target.RUN_ID + "/EARLY_FAILURE.json"]
        # Fixture premise: previously paid, certified no-write debit, never a refund.
        assert_case_invariants(amount >= row["charged_bytes"] and amount <= 1048576, "FIXTURE_DEBIT_MONOTONIC")
        dict.__setitem__(row, "charged_bytes", amount)
        dict.__setitem__(row, "SERIALIZED_BYTES", amount)

    def expect_os(self, call):
        fired_before, events_before = len(self.audit.fired), len(self.audit.events)
        try: call()
        except OSError as error:
            observed = len(self.audit.fired) > fired_before or any(
                x["outcome"] == "RAISED_AFTER_ACCEPT" for x in self.audit.events[events_before:])
            assert_case_invariants(error.errno == 22 and observed, "WRONG_OR_UNOBSERVED_OS_ERROR")
            return error
        raise AssertionError("EXPECTED_OS_ERROR_MISSING")

    def packet_size(self, c, value, stage="TEST_ASSERTION"):
        # Independent public wire-format reference, not a Poison/state classifier.
        canonical = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False).encode()
        raw = canonical(value)
        event = {"schema": "r35-checkpoint-jsonl/1", "seq": c.state.journal_sequence + 1,
            "previous_sha256": c.state.journal_head, "stage": stage, "phase": c.state.phase,
            "test_id": c.state.current, "utc": c.target.datetime.datetime.now(None).isoformat(),
            "value": {"encoding": "zlib-base64-canonical-json/1", "raw_bytes": len(raw),
                "raw_sha256": hashlib.sha256(raw).hexdigest(),
                "data": base64.b64encode(zlib.compress(raw, 9)).decode("ascii")}}
        return len(canonical({**event, "sha256": hashlib.sha256(canonical(event)).hexdigest()}) + b"\n")

    def execute(self, test_id):
        spec = next(x for x in self.inputs["manifest"]["rows"] if x["test_id"] == test_id)
        for variant in spec["variants"]:
            self.audit.test_id, self.audit.variant = test_id, variant["tag"]
            self.audit.phase = "SETUP"
            c = IsolatedTargetContext(self.target, self.audit, self.inputs)
            arm_start = len(self.audit.arms)
            entered = False
            try:
                c.enter()
                entered = True
                self.audit.phase = "PRIMARY"
                self.execute_variant(int(test_id[-2:]), variant["tag"], c)
                self.audit.assert_consumed(arm_start)
                after = snapshot_observations(c)
                self.witnesses.append({"test_id": test_id, "variant": variant["tag"],
                    "prefix_sha256": hashlib.sha256(after.pop("contents")).hexdigest(),
                    "state": after, "actual_measurement_scope": "MODEL_PYTHON_API_ONLY"})
            finally:
                self.audit.phase = "CLEANUP"
                if c.saved: c.exit()

    def execute_variant(self, number, tag, c):
        s, m, a = c.state, c.target, c.audit
        value = {"synthetic": "bounded packet"}
        checkpoint = lambda: s.checkpoint("TEST_ASSERTION", value)
        if number in (1, 2, 3, 17):
            before = snapshot_observations(c)
            assert_case_invariants(self.packet_size(c, self.dense()) == 998461, "R40_WIRE_BINDING")
            c.refused(lambda: s.checkpoint("TEST_ASSERTION", self.dense()), "EVIDENCE_BUDGET_INSUFFICIENT")
            verify_fee_equations(c, before, 0, True, 0)
            if number in (2, 17):
                a.phase = "RECOVERY"
                c.clock = 10.001
                s.begin_terminal()
                before = snapshot_observations(c)
                if number == 17:
                    a.arm("write_enter", "raise")
                    self.expect_os(lambda: s.checkpoint("FAILED", value))
                    verify_fee_equations(c, before, 1, False, self.packet_size(c, value, "FAILED"))
                else:
                    receipt = s.checkpoint("FAILED", value)
                    verify_fee_equations(c, before, 1, True)
                    count, head = verify_prefix_chain(c.stream.contents())
                    assert_case_invariants(count == 2 and receipt["sha256"] == head, "RECOVERY_CHAIN")
        elif number in (4, 13, 20):
            self.prepare_observation(c)
            if number == 13:
                c.clock = 89.9
                a.arm("path_metadata", "clock:90.001")
            elif number == 20 and tag == "unknown_result_terminal_refused":
                a.arm("ledger_state:WRITE_STARTED", "raise")
            else:
                self.charged(c, 983040)
            before = snapshot_observations(c)
            c.refused(lambda: s.observe_result("A01", "PASS", 1000000), "RESULT_CHECKPOINT_UNCONFIRMED")
            record = s.rows["A01"]["events"][0]
            unknown = number == 20 and tag == "unknown_result_terminal_refused"
            verify_fee_equations(c, before, 0, not unknown)
            assert_case_invariants(record["persistence_state"] ==
                ("RESULT_PERSISTENCE_UNKNOWN" if unknown else "RESULT_PERSISTENCE_FAILED"), "RESULT_KNOWLEDGE")
            assert_case_invariants(record["RESULT_DURABLE"] is not True and
                record["checkpoint_ref"] is None and s.case_statuses["A01"] == ["PASS", None], "ORIGINAL_RESULT_RETAINED")
            if number == 20:
                # Frozen0 applies only to the actual rejected observe_result call.
                primary = [x for x in a.events[before["event_index"]:] if x["op"] == "write"]
                assert_case_invariants(len(primary) == 0, "T20_PRIMARY_WRITES")
                a.phase = "RECOVERY"
                s.begin_terminal()
                s.safe_checkpoint("FAILED", {"original_result_ack": "UNCONFIRMED"})
                passed, counts = m.finalize_evidence(s, RuntimeError("SYNTHETIC_PRIMARY_REJECTION"))
                assert_case_invariants(passed is False, "T20_FALSE_FULL_ACCEPTANCE")
                assert_case_invariants(record["RESULT_DURABLE"] is not True and
                    "A01" not in s.case_partition()["durable_outcomes"], "T20_NO_ACK_RELABEL")
        elif number in (5, 6, 7, 8, 9, 10, 11):
            before = snapshot_observations(c)
            expected = self.packet_size(c, value)
            if number == 5:
                if tag == "write_accept_then_raise": c.stream.mode = "raise_after_accept"
                else: a.arm("write_enter", "raise")
            elif number == 6: c.stream.mode = "zero"
            elif number == 7: c.stream.mode = "partial"
            elif number == 8: a.arm("flush_enter", "raise")
            elif number == 9: a.arm("fsync_enter", "raise")
            elif number == 10:
                point = {"before_sequence_store": "before_sequence",
                    "after_sequence_store": "after:journal_sequence", "after_head_store": "after:journal_head"}[tag]
                a.arm(point, "raise")
            else: a.arm("after:journal_bytes", "raise")
            if number in (6, 7): c.refused(checkpoint, "EVIDENCE_SHORT_WRITE")
            else: self.expect_os(checkpoint)
            verify_fee_equations(c, before, 1, False, expected)
            assert_case_invariants(s.byte_ledger[m.RUN_ID + "/EARLY_FAILURE.json"]["CONFIRMED_PERSISTED_BYTES"]
                == (before["confirmed"] if number < 10 else before["confirmed"] + expected), "FSYNC_KNOWLEDGE")
            if number == 11:
                assert_case_invariants(s.journal_sequence == 2 and s.journal_bytes == len(c.stream.contents()),
                                       "COHERENT_HEAD_WITHOUT_ACK")
        elif number == 12:
            s.begin_terminal()
            self.charged(c, 1048566)
            before = snapshot_observations(c)
            if tag == "two_terminal_cap_refusals":
                for label in ("first", "second"):
                    c.refused(lambda: s.checkpoint("FAILED", {"request": label}), "EVIDENCE_BUDGET_INSUFFICIENT")
                assert_case_invariants(s.terminal_attempts == 2, "TERMINAL_ADMISSIONS_SPENT")
            else:
                record = {"observed": value, "persistence_state": "RESULT_OBSERVED_IN_MEMORY",
                          "RESULT_DURABLE": False, "checkpoint_ref": None}
                assert_case_invariants(s.commit_case_record(record, "TEST_ASSERTION") is False, "EXPECTED_FAILED_RECORD")
                used = s.checkpoint_attempts
                assert_case_invariants(s.commit_case_record(record, "TEST_ASSERTION") is False and
                    s.checkpoint_attempts == used, "RECORD_REENTRY_BUDGET")
            verify_fee_equations(c, before, 0, True, 0)
        elif number == 14:
            c.clock = 89.999
            before = snapshot_observations(c)
            expected = self.packet_size(c, value)
            a.arm("tell_return", "clock:90.001")
            c.refused(checkpoint, "FINALIZATION_INCOMPLETE")
            verify_fee_equations(c, before, 0, True, expected)
        elif number == 15:
            s.begin_terminal()
            before = snapshot_observations(c)
            if tag == "terminal_pre_reserve": c.clock = 115.
            else:
                a.arm("write_return" if tag == "terminal_after_write" else "flush_return", "clock:115")
            c.refused(checkpoint, "FINALIZATION_INCOMPLETE")
            verify_fee_equations(c, before, 0 if tag == "terminal_pre_reserve" else 1,
                                 tag == "terminal_pre_reserve")
        elif number == 16:
            path = m.OUTPUT / "TEST_RUNS.json"
            data = {"status": "FAILED", "FULL_CONTRACT_ACCEPTED": False, "data": self.dense()}
            before = snapshot_observations(c)
            c.refused(lambda: s.write(path, data))
            assert_case_invariants("TEST_RUNS.json" in s.write_attempted_paths, "RECEIPT_CLAIM_MISSING")
            c.refused(lambda: s.write(path, data), "EVIDENCE_RETRY_REFUSED")
            verify_fee_equations(c, before, 0, True, 0)
        elif number == 18:
            s.byte_ledger[m.RUN_ID + "/EARLY_FAILURE.json"]["poisoned"] = True
            before = snapshot_observations(c)
            c.refused(checkpoint, "EVIDENCE_STREAM_POISONED")
            verify_fee_equations(c, before, 0, False, 0)
        elif number == 19:
            before = snapshot_observations(c)
            receipts = [s.checkpoint("TEST_ASSERTION", {"item": i}) for i in range(2)]
            after = verify_fee_equations(c, before, 2, True)
            count, head = verify_prefix_chain(after["contents"])
            assert_case_invariants(count == 3 and [x["seq"] for x in receipts] == [2, 3]
                and head == receipts[-1]["sha256"], "HAPPY_CHAIN")
            assert_case_invariants(after["charged"] - before["charged"] == len(after["contents"]) - len(before["contents"]),
                                   "HAPPY_FULL_CHARGE")
        elif number == 21:
            reference = self.inputs["original_caps"]
            assert_case_invariants(m.EVIDENCE_CAPS == reference and sum(reference.values()) == 2000167
                and sum(reference.values()) <= EVIDENCE_BYTES, "ORIGINAL_CAPS_CHANGED")
            s.begin_terminal()
            before = snapshot_observations(c)
            for key, limit in reference.items():
                if key == "RUN_APPROVAL_RECEIPT.json": continue
                old = s.byte_ledger.get(key, {}).get("charged_bytes", 0)
                s.reserve_bytes(limit - old, m.OUTPUT / key)
            c.refused(lambda: s.reserve_bytes(1, c.path), "EVIDENCE_BUDGET_INSUFFICIENT")
            verify_fee_equations(c, before, 0, True)
            assert_case_invariants(sum(x["charged_bytes"] for x in s.byte_ledger.values()) + 8192 == 2000167,
                                   "CAP_SUM_DOUBLECOUNTED")
        elif number == 22:
            before = snapshot_observations(c)
            expected = self.packet_size(c, value)
            if tag == "tell_conflict": c.tell_delta = 1
            else: c.identity_fault = "inode" if tag == "inode_conflict" else "extent"
            c.refused(checkpoint)
            verify_fee_equations(c, before, 0, False, expected)
        elif number == 23:
            before = snapshot_observations(c)
            if tag == "missing_attempt_evidence":
                s.reserve_bytes(8, c.path)
                c.clock = 90.001
                c.refused(lambda: s.io_write(c.stream, c.path, b"12345678"), "FINALIZATION_INCOMPLETE")
            elif tag == "stale_nonempty_attempt":
                c.refused(lambda: s.checkpoint("FAILED", value, _attempt={"old": True}), "CHECKPOINT_ATTEMPT_STATE")
            elif tag == "owner_mismatch":
                self.charged(c, 983040)
                before = snapshot_observations(c)
                c.attempt = {}
                a.arm("path_metadata", "owner_mismatch")
                c.refused(lambda: s.checkpoint("TEST_ASSERTION", value, _attempt=c.attempt))
            else:
                a.arm("ledger_state:WRITE_STARTED", "raise")
                self.expect_os(checkpoint)
            verify_fee_equations(c, before, 0, False)
        elif number == 24:
            before = snapshot_observations(c)
            if tag == "global_guard_corrupt_ledger":
                s.byte_ledger["SYNTHETIC_CORRUPTION"] = {"charged_bytes": EVIDENCE_BYTES}
                c.refused(checkpoint, "RESOURCE_OUTPUT_BYTES")
            else:
                point = {"after_serialized": "ledger:SERIALIZED_BYTES", "after_charged": "ledger:charged_bytes",
                         "after_state_before_global": "ledger_state:SERIALIZED"}[tag]
                a.arm(point, "raise")
                self.expect_os(checkpoint)
            verify_fee_equations(c, before, 0, False)
        elif number == 25:
            a.phase = "SETUP"
            self.prepare_observation(c)
            record = s.observe_result("A01", "PASS", 1000000)
            receipt = dict(record["checkpoint_ref"])
            sink = m.Sink(s, m.RUN / "stdout.log")
            a.phase = "PRIMARY"
            before = snapshot_observations(c)
            if tag == "log_prewrite_refusal":
                s.byte_ledger[m.RUN_ID + "/stdout.log"]["charged_bytes"] = 65536
                c.refused(lambda: sink.write("unit"), "EVIDENCE_BUDGET_INSUFFICIENT")
            else:
                a.arm("write_enter", "raise")
                self.expect_os(lambda: sink.write("unit"))
            verify_fee_equations(c, before, 0 if tag == "log_prewrite_refusal" else 1, True, 0)
            assert_case_invariants(record["RESULT_DURABLE"] is True and record["checkpoint_ref"] == receipt,
                                   "ACK_CHANGED_BY_LOG")
        elif number == 26:
            before = snapshot_observations(c)
            if tag == "record_and_output_once":
                record = {"persistence_state": "RESULT_PERSISTENCE_FAILED"}
                assert_case_invariants(s.commit_case_record(record, "TEST_ASSERTION") is False, "REENTRY_FALSE")
                s.write_attempted_paths.add("TEST_RUNS.json")
                c.refused(lambda: s.write(m.OUTPUT / "TEST_RUNS.json", {}), "EVIDENCE_RETRY_REFUSED")
            elif tag == "attempt_limits":
                s.checkpoint_attempts = 8320
                c.refused(checkpoint, "CHECKPOINT_ATTEMPT_LIMIT")
                second = IsolatedTargetContext(m, a, self.inputs)
                nested = False
                try:
                    second.enter(); nested = True
                    second.state.begin_terminal()
                    second.state.terminal_attempts = 32
                    second.refused(lambda: second.state.checkpoint("FAILED", value), "TERMINAL_ATTEMPT_LIMIT")
                finally:
                    if second.saved: second.exit()
            else:
                sentinel = {"read_consumed": True, "grant_consumed": True, "epoch": 1}
                s.synthetic_business_sentinel = dict(sentinel)
                self.charged(c, 983040)
                before = snapshot_observations(c)
                c.refused(checkpoint, "EVIDENCE_BUDGET_INSUFFICIENT")
                assert_case_invariants(s.synthetic_business_sentinel == sentinel, "BUSINESS_SENTINEL_CHANGED")
            verify_fee_equations(c, before, 0, True)
        elif number == 27:
            before = snapshot_observations(c)
            if tag == "text_guard": c.refused(lambda: s.checkpoint("FAILED", {"text": "x" * 8193}))
            elif tag == "shape_guard": c.refused(lambda: s.checkpoint("FAILED", [0] * 4097))
            elif tag == "public_sink_guard":
                s.secrets = {"SYNTHETIC_PUBLIC_CANARY"}
                c.refused(lambda: s.checkpoint("FAILED", {"canary": "SYNTHETIC_PUBLIC_CANARY"}), "PUBLIC_SINK_REFUSED")
            elif tag == "path_permission_guard":
                a.arm("path_metadata", "permission")
                try: checkpoint()
                except PermissionError as error:
                    assert_case_invariants(error.errno == 13, "PERMISSION_FAULT_CODE")
                else: raise AssertionError("PERMISSION_FAULT_MISSING")
            elif tag == "phase_stop_guard":
                s.stop_requested = True
                c.refused(checkpoint, "WORK_DEADLINE_OR_STOP")
            else:
                path = m.RUN / "synthetic_source.py"
                c.files[str(path)] = bytearray(b"# synthetic source\n")
                module = types.ModuleType("r43_synthetic")
                module.__file__ = str(path)
                loader = importlib.machinery.SourceFileLoader(module.__name__, str(path))
                module.__spec__ = importlib.machinery.ModuleSpec(module.__name__, loader, origin=str(path))
                s.source_pins, s.runtime_code_pins, s.expected_names = {path: "0" * 64}, {}, {module.__name__: path}
                row = s.origin_observation(module.__name__, module)
                c.refused(lambda: s.verify_file_origin(row, module, path), "DEPENDENCY_CHANGED")
                assert_case_invariants(s.build_verified is False, "SOURCE_ADMISSION_CHANGED")
            verify_fee_equations(c, before, 0, tag != "path_permission_guard")
        elif number == 28:
            s.begin_terminal()
            before = snapshot_observations(c)
            if tag == "late_content_read":
                a.arm("read_return", "clock:115")
                c.refused(lambda: s.hash_owned_file(c.path), "TERMINAL_READ_DEADLINE")
            elif tag == "late_metadata_return":
                a.arm("stat_return", "clock:115")
                c.refused(lambda: m.metadata(c.path, "stat"), "TERMINAL_READ_DEADLINE")
            elif tag == "close_failure":
                a.arm("close_enter", "raise")
                self.expect_os(lambda: s.close_owned(c.stream, c.path))
                assert_case_invariants(not c.stream.closed, "FALSE_CLOSE_ACK")
            else:
                c.clock = 120.
                s.close_owned(c.stream, c.path)
                assert_case_invariants(not c.stream.closed and s.finalization_incomplete, "HARD_CLOSE_GATE")
            verify_fee_equations(c, before, 0)
        else:
            raise AssertionError("UNMAPPED_TEST_ID")

    def test_T01(self): return self.execute("R40-PC-T01")
    def test_T02(self): return self.execute("R40-PC-T02")
    def test_T03(self): return self.execute("R40-PC-T03")
    def test_T04(self): return self.execute("R40-PC-T04")
    def test_T05(self): return self.execute("R40-PC-T05")
    def test_T06(self): return self.execute("R40-PC-T06")
    def test_T07(self): return self.execute("R40-PC-T07")
    def test_T08(self): return self.execute("R40-PC-T08")
    def test_T09(self): return self.execute("R40-PC-T09")
    def test_T10(self): return self.execute("R40-PC-T10")
    def test_T11(self): return self.execute("R40-PC-T11")
    def test_T12(self): return self.execute("R40-PC-T12")
    def test_T13(self): return self.execute("R40-PC-T13")
    def test_T14(self): return self.execute("R40-PC-T14")
    def test_T15(self): return self.execute("R40-PC-T15")
    def test_T16(self): return self.execute("R40-PC-T16")
    def test_T17(self): return self.execute("R40-PC-T17")
    def test_T18(self): return self.execute("R40-PC-T18")
    def test_T19(self): return self.execute("R40-PC-T19")
    def test_T20(self): return self.execute("R40-PC-T20")
    def test_T21(self): return self.execute("R40-PC-T21")
    def test_T22(self): return self.execute("R40-PC-T22")
    def test_T23(self): return self.execute("R40-PC-T23")
    def test_T24(self): return self.execute("R40-PC-T24")
    def test_T25(self): return self.execute("R40-PC-T25")
    def test_T26(self): return self.execute("R40-PC-T26")
    def test_T27(self): return self.execute("R40-PC-T27")
    def test_T28(self): return self.execute("R40-PC-T28")


def verify_source_and_approval_inputs(packet_path, audit):
    """No SUT load/output allocation until a new complete grant passes this gate."""
    def read(path):
        path = Path(path)
        text = str(path).lower().replace("\\", "/")
        assert_case_invariants(path.is_absolute() and path.suffix.lower() not in
            {".db", ".sqlite", ".sqlite3", ".key", ".pem", ".pfx", ".aes"}
            and "/secure/" not in text and "/.runtime/" not in text, "READ_SCOPE")
        # Defensive control-size domain, not an approval of whole-process RAM.
        for part in reversed((path, *path.parents)):
            ev = audit.event("HARNESS_IO", "lstat", "NATIVE")
            info = part.lstat(); ev["outcome"] = "RETURNED"
            assert_case_invariants(not (getattr(info, "st_file_attributes", 0) & 0x400)
                and not part.is_symlink(), "CONTROL_REPARSE_REFUSED")
        ev = audit.event("HARNESS_IO", "stat", "NATIVE")
        stat = path.stat(); ev["outcome"] = "RETURNED"
        assert_case_invariants(stat.st_size <= EVIDENCE_BYTES and stat.st_nlink == 1, "CONTROL_FILE_SCOPE")
        ev = audit.event("HARNESS_IO", "open/read", "NATIVE")
        stream = path.open("rb", buffering=0); ev["outcome"] = "RETURNED"
        try:
            ev = audit.event("HARNESS_IO", "read", "NATIVE", requested=stat.st_size + 1)
            data = stream.read(stat.st_size + 1)
            ev.update(outcome="RETURNED", accepted=len(data))
            assert_case_invariants(len(data) == stat.st_size, "INPUT_CHANGED_DURING_READ")
            return data
        finally:
            ev = audit.event("HARNESS_IO", "close", "NATIVE")
            stream.close(); ev["outcome"] = "RETURNED"
    packet_path = Path(packet_path)
    assert_case_invariants(packet_path.is_absolute() and packet_path.is_relative_to(Path(RESEARCH)),
                           "EXECUTION_PACKET_SCOPE")
    packet = json.loads(read(packet_path))
    assert_case_invariants(packet.get("schema") == "r43-poison28-execution/1"
        and packet.get("approved") is True and packet.get("execution_authorized") is True,
        "INDEPENDENT_EXECUTION_APPROVAL_REQUIRED")
    assert_case_invariants(packet.get("eight_resource_budgets_closed") is True
        and packet.get("normal_and_failure_evidence_bound_proved") is True
        and packet.get("runtime_closure_approved") is True
        and packet.get("external_wall_supervision_approved") is True,
        "EXECUTION_PROOFS_REQUIRED")
    assert_case_invariants(packet.get("max_suite_runs") == 1 and packet.get("automatic_reruns") == 0
        and packet.get("wall_seconds") == 120 and packet.get("test_IDs") == list(TEST_IDS)
        and packet.get("t20_primary_call") == "State.observe_result(A01,PASS,1000000)", "EXECUTION_SCOPE")
    assert_case_invariants(sys.flags.isolated == 1 and sys.dont_write_bytecode
        and sys.flags.utf8_mode == 1 and Path(sys.executable) == Path(PYTHON_FILE), "PYTHON_FLAGS_OR_PATH")
    limits = packet["limits"]
    assert_case_invariants(all(type(limits.get(k)) is int and limits[k] > 0 for k in REQUIRED_LIMITS),
                           "RESOURCE_BUDGET_UNRESOLVED")
    assert_case_invariants(limits["cumulative_native_payload_bytes"] <= EVIDENCE_BYTES, "OUTPUT_BUDGET")
    audit.limits = limits
    assert_case_invariants(len(audit.events) <= limits["observation_events"], "BOOTSTRAP_COST_EXCEEDED")
    response_path = Path(packet["approval_response_path"])
    assert_case_invariants(response_path.suffix.lower() in {".txt", ".md", ".json"}, "APPROVAL_RESPONSE_SCOPE")
    assert_case_invariants(response_path.is_relative_to(Path(RESEARCH)) or response_path.is_relative_to(
        Path(r"C:\Users\a1887\.codex\attachments")), "APPROVAL_RESPONSE_ROOT")
    assert_case_invariants(hashlib.sha256(read(response_path)).hexdigest() == packet["approval_response_sha256"],
                           "APPROVAL_RESPONSE_CHANGED")
    paths = (str(Path(__file__).absolute()), SUT_FILE, PYTHON_FILE, MANIFEST_FILE,
             PREFIX_FILE, RECIPE_FILE, ORIGINAL_MANIFEST,
             RESEARCH + r"\2026-11-14_r41\R41_BUDGET_AND_POISON_CLASSIFICATION.json")
    assert_case_invariants(set(packet["input_pins"]) == set(paths), "INPUT_CATALOGUE_SCOPE")
    raw = {}
    for path in paths:
        value = read(path)
        assert_case_invariants(hashlib.sha256(value).hexdigest() == packet["input_pins"][path], "SOURCE_PIN_CHANGED")
        raw[path] = value
    assert_case_invariants(hashlib.sha256(raw[SUT_FILE]).hexdigest() == SUT_SHA256
        and hashlib.sha256(raw[MANIFEST_FILE]).hexdigest() == MANIFEST_SHA256
        and hashlib.sha256(raw[PREFIX_FILE]).hexdigest() == PREFIX_SHA256, "FROZEN_INPUT_CHANGED")
    manifest = json.loads(raw[MANIFEST_FILE])
    assert_case_invariants(tuple(x["test_id"] for x in manifest["rows"]) == TEST_IDS, "ORIGINAL28_ID_CHANGED")
    count, head = verify_prefix_chain(raw[PREFIX_FILE])
    assert_case_invariants(count == 1 and len(raw[PREFIX_FILE]) == 1062, "STATIC_SEED_DOMAIN")
    output = Path(packet["output_root"])
    expected = packet_path.parent / "verification_runs" / "poison28_001"
    successor = packet_path.parent.name.split("_")
    assert_case_invariants(packet_path.parent.parent == Path(RESEARCH) and len(successor) == 2
        and successor[1].startswith("r") and successor[1][1:].isdigit()
        and int(successor[1][1:]) > 43, "OUTPUT_SUCCESSOR_SCOPE")
    assert_case_invariants(datetime.date.fromisoformat(successor[0]) >= datetime.date(2026, 11, 16)
        and output == expected, "OUTPUT_HISTORY_SCOPE")
    assert_case_invariants(not output.exists() and not output.parent.exists(), "OUTPUT_ALREADY_EXISTS")
    return packet, {"manifest": manifest, "prefix": raw[PREFIX_FILE],
        "original_manifest": json.loads(raw[ORIGINAL_MANIFEST]),
        "original_caps": {x["file"]: x["bound"] for x in
            json.loads(raw[paths[-1]])["file_caps"]}, "output_root": output,
        "input_pins": packet["input_pins"], "approved_packet_path": str(packet_path),
        "sut_source": raw[SUT_FILE]}


def load_frozen_target(inputs):
    # Compile the verified source bytes; never substitute a project cache file.
    assert_case_invariants(hashlib.sha256(inputs["sut_source"]).hexdigest() == SUT_SHA256, "SUT_BYTES_CHANGED")
    module = types.ModuleType("r43_poison_sut")
    module.__file__, module.__package__ = SUT_FILE, ""
    exec(compile(inputs["sut_source"], SUT_FILE, "exec", dont_inherit=True), module.__dict__)
    return module


def build_ordered_suite(target, audit, inputs):
    suite = PoisonClassification28(target, audit, inputs)
    return suite, [(tid, getattr(suite, "test_T" + tid[-2:])) for tid in TEST_IDS]


def reserve_owned_output(inputs, audit):
    root = inputs["output_root"]
    assert_case_invariants(audit.limits["new_directories"] >= 2, "DIRECTORY_BUDGET")
    for path in (root.parent, root):
        assert_case_invariants(not path.exists() and not path.is_symlink(), "EXCLUSIVE_OUTPUT_SCOPE")
        ev = audit.event("EVIDENCE_IO", "mkdir", "NATIVE")
        path.mkdir(exist_ok=False); ev["outcome"] = "RETURNED"
    inputs["output_claims"], inputs["output_charged"], inputs["native_handles"] = set(), {}, []


def emit_owned_evidence(inputs, audit, name, value):
    assert_case_invariants(name in EVIDENCE_CAPS and name not in inputs["output_claims"], "OUTPUT_ONCE_SCOPE")
    inputs["output_claims"].add(name)
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8") + b"\n"
    assert_case_invariants(len(data) <= EVIDENCE_CAPS[name], "COMPLETE_ARTIFACT_DOES_NOT_FIT")
    total = sum(inputs["output_charged"].values()) + len(data)
    assert_case_invariants(total <= min(EVIDENCE_BYTES, audit.limits["cumulative_native_payload_bytes"]),
                           "EVIDENCE_BYTES_EXCEEDED")
    inputs["output_charged"][name] = len(data)  # no refund, including failed writes
    path = inputs["output_root"] / name
    ev = audit.event("EVIDENCE_IO", "open/create", "NATIVE")
    stream = path.open("xb", buffering=0); ev["outcome"] = "RETURNED"
    inputs["native_handles"].append({"stream": stream, "path": str(path), "close_attempted": False})
    try:
        ev = audit.event("EVIDENCE_IO", "write", "NATIVE", len(data))
        count = stream.write(data)
        ev.update(outcome="RETURNED", accepted=count)
        assert_case_invariants(count == len(data), "EVIDENCE_SHORT_WRITE")
        ev = audit.event("EVIDENCE_IO", "flush", "NATIVE")
        stream.flush(); ev["outcome"] = "RETURNED"
        ev = audit.event("EVIDENCE_IO", "fsync", "NATIVE")
        os.fsync(stream.fileno()); ev["outcome"] = "RETURNED"
    finally:
        close_owned_resources(inputs, audit)
    return hashlib.sha256(data).hexdigest()


def close_owned_resources(inputs, audit):
    for item in inputs.get("native_handles", []):
        if item["stream"].closed or item["close_attempted"]: continue
        # Native blocking/hard wall enforcement remains an external obligation.
        audit.check()
        item["close_attempted"] = True
        ev = audit.event("EVIDENCE_IO", "close", "NATIVE")
        item["stream"].close(); ev["outcome"] = "RETURNED"
        assert_case_invariants(item["stream"].closed, "OWNED_CLOSE_UNCONFIRMED")


def record_bounded_failure(error):
    # Full formatting is retained; cap refusal means incomplete evidence, never PASS.
    return {"type": type(error).__name__, "full_traceback": "".join(
        traceback.TracebackException.from_exception(error, capture_locals=False).format(chain=True)),
        "status": "ERROR", "retry": False}


def main():
    global json, hashlib, time, types, datetime, binascii, zlib, base64, threading
    global importlib, sys, os, traceback, ctypes, Path, PureWindowsPath
    import argparse
    import json, hashlib, time, types, datetime, binascii, zlib, base64, threading
    import importlib.util, importlib.machinery
    import sys, os, traceback, ctypes
    from pathlib import Path, PureWindowsPath
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--execution-lock", required=True)
    args = parser.parse_args()
    audit = FaultSchedule()
    # No target import, test fixture, directory or Journal exists before this gate.
    packet, inputs = verify_source_and_approval_inputs(Path(args.execution_lock), audit)
    reserve_owned_output(inputs, audit)
    results = [{"test_id": x, "status": "NOT_RUN"} for x in TEST_IDS]
    failure = None
    try:
        target = load_frozen_target(inputs)
        suite, ordered = build_ordered_suite(target, audit, inputs)
        for result, (test_id, call) in zip(results, ordered):
            result["status"] = "RUNNING"
            try:
                call()
            except Exception as error:
                result.update(status="ERROR", failure=record_bounded_failure(error))
                failure = result["failure"]
                break
            result["status"] = "PASS"
        audit.phase, audit.test_id, audit.variant = "EVIDENCE_OUTPUT", None, None
        emit_owned_evidence(inputs, audit, "STATE_WITNESS.json", {"variants": suite.witnesses})
        emit_owned_evidence(inputs, audit, "TEST_MANIFEST.json", {"test_IDs": list(TEST_IDS),
            "input_manifest_sha256": MANIFEST_SHA256, "source": SUT_SHA256})
        emit_owned_evidence(inputs, audit, "SOURCE_LOCK.json", {"input_pins": inputs["input_pins"],
            "approval_packet": inputs["approved_packet_path"]})
    except Exception as error:
        failure = record_bounded_failure(error)
    finally:
        close_owned_resources(inputs, audit)
    if failure is not None:
        emit_owned_evidence(inputs, audit, "EARLY_FAILURE.json", failure)
    ledger = {"observed_python_API_counts_before_ledger_write": dict(audit.counts),
        "fault_arms": len(audit.arms), "faults_fired": len(audit.fired),
        "fixture_total": audit.fixtures, "lock_total": audit.locks,
        "source_output_charges_before_ledger_write": dict(inputs["output_charged"]),
        "FULL_IO_COUNT_UNPROVEN": True, "system_calls": "UNKNOWN",
        "physical_disk_operations": "UNKNOWN", "whole_process_peak_working_set": audit.rss_peak,
        "peak_measurement_status": "NOT_MEASURED" if audit.rss_peak is None else "OS_REPORTED_PEAK",
        "unobserved_boundaries": ["bootstrap imports", "import loader native IO", "implicit native metadata", "interpreter shutdown"],
        "observation_scope": "owner/realm/phase; shared evidence counted once at suite level"}
    emit_owned_evidence(inputs, audit, "RESOURCE_LEDGER.json", ledger)
    emit_owned_evidence(inputs, audit, "stdout.log", {"counts": {
        key: sum(x["status"] == key for x in results) for key in ("PASS", "ERROR", "NOT_RUN")}})
    emit_owned_evidence(inputs, audit, "stderr.log", {"failure_present": failure is not None})
    passed = failure is None and all(x["status"] == "PASS" for x in results)
    emit_owned_evidence(inputs, audit, "RESULTS.json", {"cases": results, "passed": passed,
        "actual_exit_observed": "NOT_MEASURED", "required_exit": 0 if passed else 1,
        "complete_L0_capacity_proved": False, "native_durability_proved": False,
        "IO_count_scope": "primary/recovery traces, observed model/native Python APIs; syscall totalsUNKNOWN"})
    close_owned_resources(inputs, audit)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
