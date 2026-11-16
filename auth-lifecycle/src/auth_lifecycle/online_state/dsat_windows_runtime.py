"""Owned offline Windows primitives with R24 output and pipe-error policy.

The only admission factory requires the R21 receipt and its authorized output
tree. The confirmed D1-B2 root is never an execution target of these APIs.
"""
import ctypes as C
from ctypes import wintypes as W
import hashlib
import errno
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import weakref


OUTPUT = Path(r"D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs")
# Original bootstrap approval is read-only and keeps the R22 grant protocol.
RECORD = OUTPUT.parent.parent / "2026-11-11_r22"
RUN_RECORD = OUTPUT.parent
PROJECT = Path(r"D:\毕业设计\auth-lifecycle")
DEPLOYMENT = Path(r"D:\毕业设计\h2_test_runtime\h2-authority-synth-001")
_SCOPES, _FACTS, _LEASES, _EVENTS, _CHILDREN = (weakref.WeakKeyDictionary() for _ in range(5))
_RUN_COUNTS = {}
_COUNTER_LOCK = threading.RLock()
_CHILD_SLOTS = threading.BoundedSemaphore(2)


class SafetyError(ValueError):
    def __init__(self, code):
        codes = {"APPROVAL_REQUIRED", "OFFLINE_ONLY", "PATH_DENIED", "IDENTITY_MISMATCH", "SOURCE_MISMATCH",
            "SINGLE_ACTIVE_CONFLICT", "OWNERSHIP_UNPROVEN", "CONTEXT_REQUIRED", "RESOURCE_LIMIT",
            "NATIVE_UNAVAILABLE", "NATIVE_FAILURE", "STALE_EPOCH", "P2_NOT_AUTHORIZED", "REPLAY",
            "SCHEMA_MISMATCH", "INITIALIZATION_FAILED", "LIFECYCLE_ORDER", "PORT_CONFLICT", "DURABLE_CONSUMPTION_UNPROVEN",
            "CLEANUP_FAILED", "RECOVERY_REQUIRED", "UNSUPPORTED_ARGUMENTS", "DEPENDENCY_MISMATCH"}
        self.code = code if code in codes else "NATIVE_FAILURE"
        super().__init__(self.code)


def require(condition, code="CONTEXT_REQUIRED"):
    if not condition:
        raise SafetyError(code)


def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


class _Opaque:
    __slots__ = ("__weakref__",)

    def __init__(self, *args, **kwargs):
        raise SafetyError("CONTEXT_REQUIRED")

    def __reduce_ex__(self, protocol):
        raise TypeError("OWNED_CAPABILITY_NOT_SERIALIZABLE")

    def __repr__(self):
        return "<OwnedOfflineCapability redacted>"


class SECURITY_ATTRIBUTES(C.Structure):
    _fields_ = [("nLength", W.DWORD), ("lpSecurityDescriptor", C.c_void_p), ("bInheritHandle", W.BOOL)]


class FILE_INFORMATION(C.Structure):
    _fields_ = [("dwFileAttributes", W.DWORD), ("ftCreationTime", W.FILETIME), ("ftLastAccessTime", W.FILETIME),
        ("ftLastWriteTime", W.FILETIME), ("dwVolumeSerialNumber", W.DWORD), ("nFileSizeHigh", W.DWORD),
        ("nFileSizeLow", W.DWORD), ("nNumberOfLinks", W.DWORD), ("nFileIndexHigh", W.DWORD), ("nFileIndexLow", W.DWORD)]


class SID_AND_ATTRIBUTES(C.Structure):
    _fields_ = [("Sid", C.c_void_p), ("Attributes", W.DWORD)]


def _api():
    require(os.name == "nt", "NATIVE_UNAVAILABLE")
    kernel = C.WinDLL("kernel32", use_last_error=True)
    security = C.WinDLL("advapi32", use_last_error=True)
    kernel.GetCurrentProcess.restype = W.HANDLE
    kernel.GetCurrentProcessId.restype = W.DWORD
    kernel.CloseHandle.argtypes = [W.HANDLE]
    kernel.CloseHandle.restype = W.BOOL
    kernel.LocalFree.argtypes = [C.c_void_p]
    kernel.LocalFree.restype = C.c_void_p
    kernel.GetProcessId.argtypes = [W.HANDLE]
    kernel.GetProcessId.restype = W.DWORD
    kernel.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
    kernel.OpenProcess.restype = W.HANDLE
    kernel.GetProcessTimes.argtypes = [W.HANDLE] + [C.POINTER(W.FILETIME)] * 4
    kernel.GetProcessTimes.restype = W.BOOL
    kernel.QueryFullProcessImageNameW.argtypes = [W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD)]
    kernel.QueryFullProcessImageNameW.restype = W.BOOL
    kernel.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, C.POINTER(SECURITY_ATTRIBUTES), W.DWORD, W.DWORD, W.HANDLE]
    kernel.CreateFileW.restype = W.HANDLE
    kernel.GetFileInformationByHandle.argtypes = [W.HANDLE, C.POINTER(FILE_INFORMATION)]
    kernel.GetFileInformationByHandle.restype = W.BOOL
    kernel.GetFinalPathNameByHandleW.argtypes = [W.HANDLE, W.LPWSTR, W.DWORD, W.DWORD]
    kernel.GetFinalPathNameByHandleW.restype = W.DWORD
    kernel.CreateDirectoryW.argtypes = [W.LPCWSTR, C.POINTER(SECURITY_ATTRIBUTES)]
    kernel.CreateDirectoryW.restype = W.BOOL
    kernel.CreateEventW.argtypes = [C.POINTER(SECURITY_ATTRIBUTES), W.BOOL, W.BOOL, W.LPCWSTR]
    kernel.CreateEventW.restype = W.HANDLE
    kernel.OpenEventW.argtypes = [W.DWORD, W.BOOL, W.LPCWSTR]
    kernel.OpenEventW.restype = W.HANDLE
    kernel.SetEvent.argtypes = [W.HANDLE]
    kernel.SetEvent.restype = W.BOOL
    kernel.WaitForSingleObject.argtypes = [W.HANDLE, W.DWORD]
    kernel.WaitForSingleObject.restype = W.DWORD
    kernel.GetWindowsDirectoryW.argtypes = [W.LPWSTR, W.UINT]
    kernel.GetWindowsDirectoryW.restype = W.UINT
    security.OpenProcessToken.argtypes = [W.HANDLE, W.DWORD, C.POINTER(W.HANDLE)]
    security.OpenProcessToken.restype = W.BOOL
    security.GetTokenInformation.argtypes = [W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.POINTER(W.DWORD)]
    security.GetTokenInformation.restype = W.BOOL
    security.ConvertSidToStringSidW.argtypes = [C.c_void_p, C.POINTER(W.LPWSTR)]
    security.ConvertSidToStringSidW.restype = W.BOOL
    security.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [W.LPCWSTR, W.DWORD, C.POINTER(C.c_void_p), C.c_void_p]
    security.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = W.BOOL
    security.SetFileSecurityW.argtypes = [W.LPCWSTR, W.DWORD, C.c_void_p]
    security.SetFileSecurityW.restype = W.BOOL
    security.GetFileSecurityW.argtypes = [W.LPCWSTR, W.DWORD, C.c_void_p, W.DWORD, C.POINTER(W.DWORD)]
    security.GetFileSecurityW.restype = W.BOOL
    security.ConvertSecurityDescriptorToStringSecurityDescriptorW.argtypes = [C.c_void_p, W.DWORD, W.DWORD, C.POINTER(W.LPWSTR), C.c_void_p]
    security.ConvertSecurityDescriptorToStringSecurityDescriptorW.restype = W.BOOL
    return kernel, security


def _ok(value, code="NATIVE_FAILURE"):
    require(bool(value), code)


def _descriptor(sid):
    kernel, security = _api()
    descriptor = C.c_void_p()
    _ok(security.ConvertStringSecurityDescriptorToSecurityDescriptorW(
        "D:P(A;OICI;FA;;;" + sid + ")(A;OICI;FA;;;SY)", 1, C.byref(descriptor), None))
    return kernel, descriptor, SECURITY_ATTRIBUTES(C.sizeof(SECURITY_ATTRIBUTES), descriptor, False)


def _process_facts(handle):
    kernel, security = _api()
    times = [W.FILETIME() for _ in range(4)]
    _ok(kernel.GetProcessTimes(handle, *(C.byref(v) for v in times)))
    name, length = C.create_unicode_buffer(32768), W.DWORD(32768)
    _ok(kernel.QueryFullProcessImageNameW(handle, 0, name, C.byref(length)))
    token = W.HANDLE()
    _ok(security.OpenProcessToken(handle, 8, C.byref(token)))
    try:
        size = W.DWORD()
        security.GetTokenInformation(token, 1, None, 0, C.byref(size))
        require(0 < size.value <= 65536)
        buffer = C.create_string_buffer(size.value)
        _ok(security.GetTokenInformation(token, 1, buffer, size, C.byref(size)))
        sid = C.cast(buffer, C.POINTER(SID_AND_ATTRIBUTES)).contents.Sid
        output = W.LPWSTR()
        _ok(security.ConvertSidToStringSidW(sid, C.byref(output)))
        try:
            sid_text = output.value
        finally:
            kernel.LocalFree(output)
    finally:
        kernel.CloseHandle(token)
    return {"pid": int(kernel.GetProcessId(handle)), "created_filetime": times[0].dwLowDateTime | times[0].dwHighDateTime << 32,
            "image": name.value, "SID": sid_text, "source_kind": "OWNED_OFFLINE_WINDOWS_PROCESS"}


def _handle_file_facts(handle):
    kernel, _ = _api()
    info = FILE_INFORMATION()
    _ok(kernel.GetFileInformationByHandle(handle, C.byref(info)))
    name = C.create_unicode_buffer(32768)
    count = kernel.GetFinalPathNameByHandleW(handle, name, len(name), 0)
    require(0 < count < len(name))
    value = name.value
    if value.startswith("\\\\?\\"):
        value = value[4:]
    return {"volume": int(info.dwVolumeSerialNumber), "file_id": int(info.nFileIndexLow | info.nFileIndexHigh << 32),
            "links": int(info.nNumberOfLinks), "final_path": value, "reparse": bool(info.dwFileAttributes & 0x400)}


class TestScope(_Opaque):
    def _record(self):
        rec = _SCOPES.get(self)
        require(rec is not None)
        return rec

    @property
    def root(self):
        return self._record()["root"]

    @property
    def SID(self):
        return self._record()["process"]["SID"]

    @property
    def source_digest(self):
        return self._record()["source_digest"]

    def path(self, value):
        p = Path(value)
        require(p.is_absolute() and not str(p).startswith("\\\\") and ":" not in str(p)[2:], "PATH_DENIED")
        require(not any(x in {".", ".."} or x.endswith((".", " ")) for x in p.parts[1:]), "PATH_DENIED")
        p = p.absolute()
        require(p.is_relative_to(self.root), "PATH_DENIED")
        for part in (p, *p.parents):
            if part.exists():
                require(not part.is_symlink() and not (getattr(part.lstat(), "st_file_attributes", 0) & 0x400), "PATH_DENIED")
        if p.is_file():
            require(p.stat().st_nlink == 1, "PATH_DENIED")
        return p

    def count(self, key, limit, amount=1):
        rec = self._record()
        with _COUNTER_LOCK:
            value = rec["counts"].get(key, 0) + amount
            require(type(amount) is int and amount >= 0 and value <= limit, "RESOURCE_LIMIT")
            rec["counts"][key] = value
        return value

    def counts(self):
        return dict(self._record()["counts"])

    def directory(self, path):
        p = self.path(path)
        if p.exists():
            require(p.is_dir(), "PATH_DENIED")
            return p
        require(p.parent.exists(), "PATH_DENIED")
        self.count("private_directories", 64)
        kernel, descriptor, attributes = _descriptor(self.SID)
        try:
            _ok(kernel.CreateDirectoryW(str(p), C.byref(attributes)), "PATH_DENIED")
        finally:
            kernel.LocalFree(descriptor)
        return p

    def private_acl(self, path):
        p = self.path(path)
        kernel, descriptor, _ = _descriptor(self.SID)
        try:
            _, security = _api()
            _ok(security.SetFileSecurityW(str(p), 4 | 0x80000000, descriptor), "PATH_DENIED")
        finally:
            kernel.LocalFree(descriptor)
        return self.acl(p)

    def acl(self, path):
        p = self.path(path)
        kernel, security = _api()
        size = W.DWORD()
        security.GetFileSecurityW(str(p), 4, None, 0, C.byref(size))
        require(0 < size.value <= 65536, "PATH_DENIED")
        buffer = C.create_string_buffer(size.value)
        _ok(security.GetFileSecurityW(str(p), 4, buffer, size, C.byref(size)), "PATH_DENIED")
        text = W.LPWSTR()
        _ok(security.ConvertSecurityDescriptorToStringSecurityDescriptorW(buffer, 1, 4, C.byref(text), None))
        try:
            sddl = text.value
        finally:
            kernel.LocalFree(text)
        principals = set(re.findall(r";;;([^;)]+)\)", sddl))
        require(principals == {self.SID, "SY"} and "D:P" in sddl, "PATH_DENIED")
        return {"protected_DACL": True, "allowed_sids": sorted(principals)}

    def file_facts(self, path):
        p = self.path(path)
        kernel, _ = _api()
        handle = kernel.CreateFileW(str(p), 0x80, 7, None, 3, 0x02000000 | 0x00200000, None)
        require(handle not in (None, C.c_void_p(-1).value), "PATH_DENIED")
        try:
            facts = _handle_file_facts(handle)
            require(not facts["reparse"] and Path(facts["final_path"]) == p, "PATH_DENIED")
            require(p.is_dir() or facts["links"] == 1, "PATH_DENIED")
            return facts
        finally:
            kernel.CloseHandle(handle)

    def write_new(self, path, data):
        p = self.path(path)
        require(type(data) is bytes and len(data) <= 2 * 1024 * 1024 and p.parent.exists(), "RESOURCE_LIMIT")
        known = self._record().setdefault("created_paths", set())
        require(str(p).lower() in known or len(known) < 512, "RESOURCE_LIMIT")
        with p.open("xb") as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        known.add(str(p).lower())
        self.count("file_create_calls", 4096)
        self._record()["counts"]["unique_created_paths"] = len(known)
        return p

    def sources(self):
        rec = self._record()
        require(all(_hash(Path(x["path"])) == x["sha256"] for x in rec["sources"]), "SOURCE_MISMATCH")
        approved = {Path(x["path"]) for x in rec["sources"]}
        for name, module in list(sys.modules.items()):
            if name == "auth_lifecycle" or name == "auth_lifecycle.online_state" or name.startswith("auth_lifecycle.online_state."):
                package = hasattr(module, "__path__")
                expected = PROJECT / "src" / Path(*name.split("."))
                expected = expected / "__init__.py" if package else expected.with_suffix(".py")
                actual = getattr(module, "__file__", None)
                origin = getattr(getattr(module, "__spec__", None), "origin", None)
                require(actual is not None and origin is not None and Path(actual) == Path(origin) == expected
                        and expected in approved, "SOURCE_MISMATCH")
        return [dict(x) for x in rec["sources"]]


class HostEvidence(_Opaque):
    def facts(self):
        rec = _FACTS.get(self)
        require(rec is not None)
        return json.loads(json.dumps(rec["facts"]))


def authorize_test_scope(run_root):
    root = Path(run_root).absolute()
    require(root.is_relative_to(OUTPUT) and root != OUTPUT and root.is_dir(), "OFFLINE_ONLY")
    run_start_path = root / "RUN_START.json"
    require(run_start_path.is_file() and not (root / "RESULTS.json").exists(), "APPROVAL_REQUIRED")
    run_start = json.loads(run_start_path.read_text(encoding="utf-8"))
    require(run_start.get("suite") == "new54" and run_start.get("run_id") == root.name, "APPROVAL_REQUIRED")
    require(root == OUTPUT / "r24_new54_001" and run_start.get("output_root") == str(OUTPUT), "PATH_DENIED")
    # This receipt admits the future test job only; the separate synthetic
    # one-shot startup approvals keep their original R22 identity and journal.
    run_receipt = json.loads((RUN_RECORD / "RUN_APPROVAL_RECEIPT.json").read_text(encoding="utf-8"))
    require(run_receipt.get("schema") == "r24-run-approval/1" and run_receipt.get("approved") is True
        and run_receipt.get("suite") == "new54" and run_receipt.get("max_runs") == 1
        and run_receipt.get("automatic_reruns") == 0 and run_receipt.get("output_root") == str(OUTPUT)
        and run_receipt.get("run_id") == root.name
        and run_start.get("run_approval_sha256") == _hash(RUN_RECORD / "RUN_APPROVAL_RECEIPT.json")
        and run_start.get("admission_sha256") == run_receipt.get("admission_sha256")
        == _hash(RUN_RECORD / "R24_VERIFICATION_ADMISSION.json")
        and _hash(run_receipt["response_path"]) == run_receipt.get("response_sha256")
        and all(run_receipt.get(k) is False for k in ("D1B2", "P1", "P2", "S3B2", "S5")), "APPROVAL_REQUIRED")
    receipt = json.loads((RECORD / "APPROVAL_RECEIPT.json").read_text(encoding="utf-8"))
    require(receipt.get("approved") is True and receipt.get("scope") == "R22 six targets and122 offline tests only", "APPROVAL_REQUIRED")
    require(_hash(receipt["request_path"]) == receipt["request_sha256"] and receipt["D1B2"] is False, "APPROVAL_REQUIRED")
    require(Path(sys.executable) == Path(receipt["base_python"]), "IDENTITY_MISMATCH")
    require(sys.version_info[:3] == (3, 12, 14) and C.sizeof(C.c_void_p) == 8, "DEPENDENCY_MISMATCH")
    lock = json.loads((RECORD / "R22_SCOPE_LOCK.json").read_text(encoding="utf-8"))
    paths = sorted({Path(x["path"]) for x in lock["targets"] if Path(x["path"]).suffix == ".py"}
        | {p for p in (PROJECT / "src/auth_lifecycle/online_state").iterdir() if p.suffix in {".py", ".sql"}}
        | {PROJECT / "src/auth_lifecycle/__init__.py", PROJECT / "scripts/run_h2_authority_service.py"})
    require(len(paths) <= 64, "RESOURCE_LIMIT")
    sources = [{"path": str(p), "sha256": _hash(p)} for p in paths]
    kernel, _ = _api()
    process = _process_facts(kernel.GetCurrentProcess())
    require(Path(process["image"]) == Path(receipt["base_python"]), "IDENTITY_MISMATCH")
    frozen = json.loads((RUN_RECORD / "sources/R24_FILE_LOCK.json").read_text(encoding="utf-8"))
    require(all(_hash(x["path"]) == x["sha256"] for x in frozen["source_closure"]), "SOURCE_MISMATCH")
    obj = object.__new__(TestScope)
    counts = _RUN_COUNTS.setdefault(str(root), {})
    _SCOPES[obj] = {"root": root, "sources": sources, "source_digest": hashlib.sha256(_canonical(sources)).hexdigest(), "process": process,
                   "python_digest": _hash(receipt["base_python"]), "counts": counts}
    if process["pid"] != run_start["main_pid"]:
        deadline = time.monotonic() + 2
        confirmed = False
        while time.monotonic() < deadline:
            try:
                confirmed = recorded_owner(obj, process)["created_by_run"]
                if confirmed: break
            except SafetyError: pass
            time.sleep(.005)
        require(confirmed, "APPROVAL_REQUIRED")
    obj.path(root); obj.private_acl(root)
    return obj


def self_process_facts(scope):
    require(type(scope) is TestScope)
    kernel, _ = _api()
    current = _process_facts(kernel.GetCurrentProcess())
    require(current == scope._record()["process"], "IDENTITY_MISMATCH")
    obj = object.__new__(HostEvidence)
    _FACTS[obj] = {"scope": scope, "facts": current}
    return obj


def validate_host_evidence(evidence, scope):
    require(type(scope) is TestScope and type(evidence) is HostEvidence and evidence in _FACTS)
    require(_FACTS[evidence]["scope"] is scope, "IDENTITY_MISMATCH")
    scope.sources()
    return evidence.facts()


class InstanceLease(_Opaque):
    def facts(self):
        rec = _LEASES.get(self)
        require(rec is not None and not rec["closed"], "OWNERSHIP_UNPROVEN")
        require(_handle_file_facts(rec["handle"]) == rec["lock_facts"], "OWNERSHIP_UNPROVEN")
        require(rec["scope"].file_facts(rec["root"]) == rec["root_facts"], "OWNERSHIP_UNPROVEN")
        return {"root": str(rec["root"]), "root_facts": dict(rec["root_facts"]), "lock_facts": dict(rec["lock_facts"]), "owner_pid": rec["pid"]}

    def close(self):
        rec = _LEASES.get(self)
        require(rec is not None)
        if not rec["closed"]:
            _ok(_api()[0].CloseHandle(rec["handle"]))
            rec["closed"] = True

    def inherited_handle(self):
        self.facts()
        return int(_LEASES[self]["handle"])


def reserve_instance(scope, root, expected=None):
    require(type(scope) is TestScope)
    root = scope.path(root)
    require(root.is_dir(), "PATH_DENIED")
    facts = scope.file_facts(root)
    if expected is not None:
        require(facts == expected, "OWNERSHIP_UNPROVEN")
    path = root / "instance.lock"
    if not path.exists():
        scope.count("files_created", 512)
    kernel, descriptor, attributes = _descriptor(scope.SID)
    try:
        handle = kernel.CreateFileW(str(path), 0xC0000000 | 0x20000, 0, C.byref(attributes), 4, 0x80 | 0x00200000, None)
    finally:
        kernel.LocalFree(descriptor)
    require(handle not in (None, C.c_void_p(-1).value), "SINGLE_ACTIVE_CONFLICT")
    try:
        lock_facts = _handle_file_facts(handle)
        require(not lock_facts["reparse"] and lock_facts["links"] == 1, "PATH_DENIED")
        obj = object.__new__(InstanceLease)
        _LEASES[obj] = {"scope": scope, "root": root, "root_facts": facts, "lock_facts": lock_facts,
            "handle": handle, "closed": False, "pid": os.getpid()}
        scope.count("lock_acquisitions", 128)
        return obj
    except BaseException:
        kernel.CloseHandle(handle)
        raise


def validate_lease(lease, scope, root):
    require(type(lease) is InstanceLease and lease in _LEASES)
    require(_LEASES[lease]["scope"] is scope and _LEASES[lease]["root"] == scope.path(root), "OWNERSHIP_UNPROVEN")
    return lease.facts()


def open_owned_file(scope, path):
    require(type(scope) is TestScope)
    return scope.file_facts(path)


class StopEvent(_Opaque):
    def signaled(self):
        rec = _EVENTS.get(self)
        require(rec is not None and not rec["closed"])
        return _api()[0].WaitForSingleObject(rec["handle"], 0) == 0

    def close(self):
        rec = _EVENTS.get(self)
        require(rec is not None)
        if not rec["closed"]:
            _ok(_api()[0].CloseHandle(rec["handle"]))
            rec["closed"] = True

    @property
    def name(self):
        return _EVENTS[self]["name"]


def create_stop_event(scope, suffix):
    require(type(scope) is TestScope and type(suffix) is str and re.fullmatch(r"[a-f0-9]{32,64}", suffix))
    name = "Local\\auth_lifecycle_r22_" + suffix
    kernel, descriptor, attributes = _descriptor(scope.SID)
    try:
        C.set_last_error(0)
        handle = kernel.CreateEventW(C.byref(attributes), True, False, name)
        code = C.get_last_error()
    finally:
        kernel.LocalFree(descriptor)
    require(handle, "NATIVE_FAILURE")
    if code == 183:
        kernel.CloseHandle(handle)
        raise SafetyError("REPLAY")
    obj = object.__new__(StopEvent)
    _EVENTS[obj] = {"scope": scope, "name": name, "handle": handle, "closed": False}
    return obj


def signal_owned_stop(scope, event):
    require(type(event) is StopEvent and event in _EVENTS and _EVENTS[event]["scope"] is scope)
    require(not _EVENTS[event]["closed"])
    _ok(_api()[0].SetEvent(_EVENTS[event]["handle"]))


def verify_target_handle(scope, process, expected):
    require(type(scope) is TestScope and process in _CHILDREN, "OWNERSHIP_UNPROVEN")
    rec = _CHILDREN[process]
    require(rec["scope"] is scope, "OWNERSHIP_UNPROVEN")
    require(not rec.get("finished"), "OWNERSHIP_UNPROVEN")
    actual = _process_facts(int(process._handle))
    require(actual == rec["facts"] == expected, "IDENTITY_MISMATCH")
    return dict(actual)


def launch_owned_child(scope, manifest, *, inherit=()):
    """Only the reviewed runner's finite no-service worker protocol is launchable."""
    require(type(scope) is TestScope)
    require(os.getpid() == json.loads((scope.root / "RUN_START.json").read_text(encoding="utf-8"))["main_pid"], "APPROVAL_REQUIRED")
    scope.sources()
    require(sum(p.poll() is None for p, rec in list(_CHILDREN.items()) if rec["scope"] is scope) < 2, "RESOURCE_LIMIT")
    path = scope.path(manifest)
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data.get("source_kind") == "R22_OWNED_STUB" and data.get("mode") in {"race", "crash", "handoff", "event", "cross_first", "cross_replay"}, "OFFLINE_ONLY")
    require(Path(data["run_root"]) == scope.root, "PATH_DENIED")
    count = scope.count("child_launches", 8)
    runner = PROJECT / "scripts/run_dsat_authority_live_lifecycle_tests.py"
    startup = None
    values = tuple(int(x) for x in inherit)
    require(len(values) <= 1 and (not values or data["mode"] == "handoff"))
    if values:
        startup = subprocess.STARTUPINFO()
        startup.lpAttributeList = {"handle_list": list(values)}
    command = [sys.executable, "-B", str(runner), "--output-root", str(OUTPUT), "--worker", "--input", str(path)]
    kernel, _ = _api()
    windows = C.create_unicode_buffer(32768)
    require(0 < kernel.GetWindowsDirectoryW(windows, len(windows)) < len(windows), "NATIVE_FAILURE")
    environment = {"SystemRoot": windows.value, "WINDIR": windows.value,
        "PATH": str(Path(sys.executable).parent) + os.pathsep + str(Path(windows.value) / "System32"),
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    require(_CHILD_SLOTS.acquire(blocking=False), "RESOURCE_LIMIT")
    started = time.monotonic()
    try:
        for value in values:
            os.set_handle_inheritable(value, True)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            startupinfo=startup, close_fds=True, creationflags=subprocess.CREATE_NO_WINDOW, env=environment)
    except BaseException:
        _CHILD_SLOTS.release()
        raise
    finally:
        for value in values:
            os.set_handle_inheritable(value, False)
    try:
        facts = _process_facts(int(process._handle))
        require(facts["SID"] == scope.SID and Path(facts["image"]) == Path(sys.executable), "IDENTITY_MISMATCH")
        _CHILDREN[process] = {"scope": scope, "facts": facts, "start": started, "number": count,
            "created_command": list(command), "environment_keys": sorted(environment),
            "mode": data["mode"], "process_handle": process._handle,
            "pipes": {name:getattr(process,name) for name in ("stdin","stdout","stderr")},
            "pipe_fds": {name:getattr(process,name).fileno() for name in ("stdin","stdout","stderr")}}
        _record_child(scope, {"event": "CREATED", "facts": facts, "mode": data["mode"], "run_id": scope.root.name})
        return process, dict(facts)
    except BaseException:
        # It was just created and retained by this call; no PID/name lookup.
        try:
            process.terminate(); process.communicate(timeout=5)
        finally:
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None: stream.close()
            process._handle.Close()
            _CHILD_SLOTS.release()
        raise


def finish_owned_child(scope, process, *, data=b"stop\n"):
    """Collect one exact owned child, retaining primary and cleanup failures.

    EINVAL/CRT EPIPE are accepted only at original stdin write/flush/close
    after poll confirms this exact process exited. Native winerror variants
    and EBADF have no acceptance path in this review.
    """
    require(process in _CHILDREN and _CHILDREN[process]["scope"] is scope, "OWNERSHIP_UNPROVEN")
    rec = _CHILDREN[process]
    require(not rec.get("finish_started") and not rec.get("finished"), "REPLAY")
    require(process._handle is rec["process_handle"] and process.pid == rec["facts"]["pid"], "OWNERSHIP_UNPROVEN")
    require(all(getattr(process,name) is stream for name,stream in rec["pipes"].items()), "OWNERSHIP_UNPROVEN")
    require(data is None or (type(data) is bytes and len(data)<=16), "RESOURCE_LIMIT")
    rec["finish_started"] = True
    pipes = rec["pipes"]
    operations, failures, originals = [], [], []
    rec["exception_objects"] = originals  # Original exceptions stay available; never serialized as secrets.
    primary = None
    primary_tb = None
    timeout = max(.01, 10 - (time.monotonic() - rec["start"]))
    terminated = False

    def exception_record(operation, error, expected=False):
        originals.append(error)
        redactor = scope._record().get("pipe_error_redactor",lambda value:"[MESSAGE_WITHHELD]")
        return {"operation":operation,"exception_type":type(error).__module__+"."+type(error).__qualname__,
            "errno":getattr(error,"errno",None),"winerror":getattr(error,"winerror",None),
            "expected":expected,"original_exception_retained":True,
            "original_exception_repr_redacted":redactor(repr(error))[:1024],
            "pipe_identity_checked":True,"pipe_fds_at_creation":dict(rec["pipe_fds"]),
            "exit_code":process.returncode,"stdin_closed":pipes["stdin"].closed,
            "impact":"stdin control delivery unconfirmed" if operation.startswith("stdin.") else "cleanup/collection incomplete"}

    def failed(operation, error, row=None):
        nonlocal primary, primary_tb
        row = exception_record(operation,error) if row is None else row
        failures.append(row)
        if primary is None: primary, primary_tb = error, error.__traceback__
        return row

    def attempt(operation, action, *, stdin_race=False):
        try:
            value = action()
            operations.append({"operation":operation,"status":"OK"})
            return value
        except BaseException as error:
            row = exception_record(operation,error)
            # A live peer closing its pipe is deliberately insufficient.
            exited = False
            poll_failure = None
            if stdin_race:
                try:
                    exited = process.poll() is not None
                    operations.append({"operation":"poll_after_"+operation,"status":"OK","exit_code":process.returncode})
                except BaseException as poll_error:
                    poll_failure = poll_error
            allowed_code = isinstance(error,OSError) and getattr(error,"winerror",None) is None
            allowed_code = allowed_code and (getattr(error,"errno",None) == errno.EINVAL
                or (isinstance(error,BrokenPipeError) and error.errno == errno.EPIPE))
            row["exit_code"] = process.returncode
            row["expected"] = bool(stdin_race and exited and allowed_code)
            operations.append(row)
            if not row["expected"]: failed(operation,error,row)
            if poll_failure is not None: failed("poll_after_"+operation,poll_failure)
            return None

    # Each phase has its own exception decision and evidence. No blanket pass.
    if not pipes["stdin"].closed:
        if data is not None:
            written = attempt("stdin.write",lambda:pipes["stdin"].write(data),stdin_race=True)
            if written is not None and written != len(data):
                failed("stdin.write.short",SafetyError("CLEANUP_FAILED"))
            attempt("stdin.flush",pipes["stdin"].flush,stdin_race=True)
        attempt("stdin.close",pipes["stdin"].close,stdin_race=True)
    else:
        operations.append({"operation":"stdin.close","status":"ALREADY_CLOSED"})
    try:
        process.wait(timeout=timeout)
        operations.append({"operation":"wait","status":"OK","exit_code":process.returncode})
    except BaseException as error:
        failed("wait",error)
        if isinstance(error,subprocess.TimeoutExpired):
            try:
                verify_target_handle(scope,process,rec["facts"])
                process.terminate(); terminated = True
                process.wait(timeout=5)
            except BaseException as cleanup_error:
                failed("timeout_cleanup",cleanup_error)
    exit_code = attempt("poll_final",process.poll)
    exited = exit_code is not None
    output = attempt("stdout.read",lambda:pipes["stdout"].read(4097)) if exited else None
    error_output = attempt("stderr.read",lambda:pipes["stderr"].read(4097)) if exited else None
    complete_output = rec.get("read_stdout_prefix", b"") + (output or b"")
    if output is None or error_output is None:
        failed("output_incomplete",SafetyError("RECOVERY_REQUIRED"))
    if len(complete_output)>4096 or (error_output is not None and len(error_output)>4096):
        failed("output_limit",SafetyError("RESOURCE_LIMIT"))
    # A failed close may already have closed BufferedWriter. Reclose only an
    # original stream still open, with the same narrow stdin policy.
    for name, stream in pipes.items():
        if exited and not stream.closed:
            attempt(name+".close",stream.close,stdin_race=name=="stdin")
    if exited and not all(stream.closed for stream in pipes.values()):
        failed("pipes_not_closed",SafetyError("CLEANUP_FAILED"))
    handle_closed = False
    if exited:
        attempt("process_handle.close",process._handle.Close)
        handle_closed = bool(process._handle.closed)
        if not handle_closed: failed("process_handle_not_closed",SafetyError("CLEANUP_FAILED"))
        attempt("child_handles_account",lambda:scope.count("owned_child_handles_closed",8))
        _CHILD_SLOTS.release()
        rec["finished"] = True
        attempt("child_exit_journal",lambda:_record_child(scope,{"event":"EXITED","facts":rec["facts"],
            "exit_code":process.returncode,"run_id":scope.root.name}))
    elapsed = time.monotonic() - rec["start"]
    attempt("child_time_account",lambda:scope.count("child_total_milliseconds",60000,int(elapsed*1000)))
    prefix = "child_%02d" % rec["number"]
    stdout_path = attempt("stdout.persist",lambda:scope.write_new(scope.root/(prefix+"_stdout.log"),complete_output))
    stderr_path = attempt("stderr.persist",lambda:scope.write_new(scope.root/(prefix+"_stderr.log"),error_output or b""))
    result = {"pid":rec["facts"]["pid"],"created_filetime":rec["facts"]["created_filetime"],
        "identity":dict(rec["facts"]),"exit_code":process.returncode,"elapsed_seconds":elapsed,
        "terminated_owned_stub":terminated,"stdout":complete_output.decode("utf-8",errors="replace"),
        "stderr_bytes":None if error_output is None else len(error_output),
        "stdout_path":None if stdout_path is None else str(stdout_path),
        "stderr_path":None if stderr_path is None else str(stderr_path),
        "stdout_complete":output is not None and len(complete_output)<=4096,
        "stderr_complete":error_output is not None and len(error_output)<=4096,
        "stdin_bytes_requested":None if data is None else len(data),
        "stdin_delivery_confirmed":not any(x.get("exception_type") for x in operations if x.get("operation","").startswith("stdin.")),
        "created_command":list(rec["created_command"]),"environment_keys":list(rec["environment_keys"]),
        "pipes_closed":all(s.closed for s in pipes.values()),"process_handle_closed":handle_closed,
        "operations":operations,"primary_error":failures[0] if failures else None,
        "cleanup_errors":failures[1:],"cleanup_state":"COMPLETE" if exited and all(s.closed for s in pipes.values()) and handle_closed and not failures else "RECOVERY_REQUIRED"}
    rec["cleanup_result"] = result
    # Per-child immutable evidence also survives an exception raised to unittest.
    attempt("cleanup.persist",lambda:scope.write_new(scope.root/(prefix+"_cleanup.json"),
        json.dumps(result,ensure_ascii=True,indent=2).encode()))
    result["primary_error"] = failures[0] if failures else None
    result["cleanup_errors"] = failures[1:]
    if failures: result["cleanup_state"] = "RECOVERY_REQUIRED"
    if primary is not None:
        primary.add_note("Owned child cleanup evidence: "+str(scope.root/(prefix+"_cleanup.json")))
        raise primary.with_traceback(primary_tb)
    return result


def read_owned_child_line(scope, process, *, timeout=3):
    require(process in _CHILDREN and _CHILDREN[process]["scope"] is scope, "OWNERSHIP_UNPROVEN")
    import msvcrt
    kernel, _ = _api()
    kernel.PeekNamedPipe.argtypes = [W.HANDLE, C.c_void_p, W.DWORD, C.c_void_p, C.POINTER(W.DWORD), C.c_void_p]
    kernel.PeekNamedPipe.restype = W.BOOL
    handle = msvcrt.get_osfhandle(process.stdout.fileno())
    deadline, data = time.monotonic() + min(timeout, 3), bytearray()
    while time.monotonic() < deadline:
        available = W.DWORD()
        if not kernel.PeekNamedPipe(handle, None, 0, None, C.byref(available), None):
            break
        if available.value:
            data.extend(process.stdout.raw.read(min(available.value, 4096 - len(data))))
            if b"\n" in data:
                require(len(data) <= 4096, "RESOURCE_LIMIT")
                _CHILDREN[process]["read_stdout_prefix"] = _CHILDREN[process].get("read_stdout_prefix", b"") + bytes(data)
                return json.loads(data.split(b"\n", 1)[0].decode("utf-8"))
        require(len(data) < 4096, "RESOURCE_LIMIT")
        if process.poll() is not None and not available.value:
            break
        time.sleep(.005)
    raise SafetyError("RECOVERY_REQUIRED")


def self_peak_memory(scope):
    require(type(scope) is TestScope)
    class Memory(C.Structure):
        _fields_ = [("cb", W.DWORD), ("PageFaultCount", W.DWORD)] + [(n, C.c_size_t) for n in
            ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage",
             "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage", "PrivateUsage")]
    kernel, _ = _api()
    kernel.K32GetProcessMemoryInfo.argtypes = [W.HANDLE, C.POINTER(Memory), W.DWORD]
    kernel.K32GetProcessMemoryInfo.restype = W.BOOL
    memory = Memory(); memory.cb = C.sizeof(memory)
    _ok(kernel.K32GetProcessMemoryInfo(kernel.GetCurrentProcess(), C.byref(memory), memory.cb))
    return {"peak_working_set_bytes": int(memory.PeakWorkingSetSize), "working_set_bytes": int(memory.WorkingSetSize),
            "private_usage_bytes": int(memory.PrivateUsage), "basis": "current test process only; includes imports/harness"}


def _record_child(scope, body):
    require(type(scope) is TestScope)
    path = scope.path(scope.root / "owned_children.jsonl")
    row = {"payload": body, "digest": hashlib.sha256(_canonical(body)).hexdigest()}
    raw = _canonical(row) + b"\n"
    if not path.exists(): scope.write_new(path, raw)
    else:
        require(path.stat().st_size + len(raw) <= 32768, "RESOURCE_LIMIT")
        with path.open("ab") as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())


def recorded_owner(scope, facts):
    """Only a process whose creation was recorded by this owned test launcher."""
    require(type(scope) is TestScope and type(facts) is dict, "OWNERSHIP_UNPROVEN")
    path = scope.path(scope.root / "owned_children.jsonl")
    try:
        raw = path.read_bytes()
        require(0 < len(raw) <= 32768 and raw.endswith(b"\n"), "OWNERSHIP_UNPROVEN")
        created = False; exited = None
        for line in raw.splitlines():
            row = json.loads(line); body = row["payload"]
            require(row["digest"] == hashlib.sha256(_canonical(body)).hexdigest() and body["run_id"] == scope.root.name, "OWNERSHIP_UNPROVEN")
            if body["facts"] == facts:
                if body["event"] == "CREATED": created = True
                if body["event"] == "EXITED": exited = body["exit_code"]
        require(created and facts["SID"] == scope.SID, "OWNERSHIP_UNPROVEN")
        return {"created_by_run": True, "exit_recorded": exited is not None, "exit_code": exited}
    except SafetyError: raise
    except Exception: raise SafetyError("OWNERSHIP_UNPROVEN") from None


def verify_recorded_owner_live(scope, facts):
    info = recorded_owner(scope, facts)
    require(not info["exit_recorded"], "OWNERSHIP_UNPROVEN")
    kernel, _ = _api()
    handle = kernel.OpenProcess(0x1000 | 0x100000, False, facts["pid"])
    require(handle, "OWNERSHIP_UNPROVEN")
    try:
        require(_process_facts(handle) == facts, "IDENTITY_MISMATCH")
        require(kernel.WaitForSingleObject(handle, 0) == 258, "OWNERSHIP_UNPROVEN")
        return True
    finally: kernel.CloseHandle(handle)


def signal_recorded_event(scope, facts, event_name):
    verify_recorded_owner_live(scope, facts)
    require(type(event_name) is str and re.fullmatch(r"Local\\auth_lifecycle_r22_[a-f0-9]{32,64}", event_name) is not None, "OWNERSHIP_UNPROVEN")
    kernel, _ = _api()
    handle = kernel.OpenEventW(2, False, event_name)
    require(handle, "OWNERSHIP_UNPROVEN")
    try: _ok(kernel.SetEvent(handle))
    finally: kernel.CloseHandle(handle)
