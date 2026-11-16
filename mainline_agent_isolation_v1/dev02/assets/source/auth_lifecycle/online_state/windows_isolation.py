"""Windows restricted-primary-token primitives for the synthetic M5 fixture.

No impersonation is used: arbitrary child code runs under the restricted primary
token. This module deliberately has no native-provider or account-management API.
"""
from __future__ import annotations

import ctypes as C
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import subprocess
import time
import re


class IsolationUnavailable(RuntimeError):
    def __init__(self, operation, code):
        self.operation, self.code = operation, code
        super().__init__(f"{operation}: Win32 {code}")


def _windows():
    if os.name != "nt":
        raise IsolationUnavailable("WINDOWS_REQUIRED", 50)
    return C.WinDLL("advapi32", use_last_error=True), C.WinDLL("kernel32", use_last_error=True)


class SID_AND_ATTRIBUTES(C.Structure):
    _fields_ = [("Sid", C.c_void_p), ("Attributes", W.DWORD)]


class STARTUPINFO(C.Structure):
    _fields_ = [("cb", W.DWORD), ("lpReserved", W.LPWSTR), ("lpDesktop", W.LPWSTR),
                ("lpTitle", W.LPWSTR), ("dwX", W.DWORD), ("dwY", W.DWORD),
                ("dwXSize", W.DWORD), ("dwYSize", W.DWORD), ("dwXCountChars", W.DWORD),
                ("dwYCountChars", W.DWORD), ("dwFillAttribute", W.DWORD),
                ("dwFlags", W.DWORD), ("wShowWindow", W.WORD), ("cbReserved2", W.WORD),
                ("lpReserved2", C.c_void_p), ("hStdInput", W.HANDLE),
                ("hStdOutput", W.HANDLE), ("hStdError", W.HANDLE)]


class PROCESS_INFORMATION(C.Structure):
    _fields_ = [("hProcess", W.HANDLE), ("hThread", W.HANDLE),
                ("dwProcessId", W.DWORD), ("dwThreadId", W.DWORD)]


class SECURITY_ATTRIBUTES(C.Structure):
    _fields_ = [("nLength", W.DWORD), ("lpSecurityDescriptor", C.c_void_p),
                ("bInheritHandle", W.BOOL)]


def _check(ok, name):
    if not ok:
        raise IsolationUnavailable(name, C.get_last_error())


def _sid(api, value):
    result = C.c_void_p()
    api.ConvertStringSidToSidW.argtypes = [W.LPCWSTR, C.POINTER(C.c_void_p)]
    api.ConvertStringSidToSidW.restype = W.BOOL
    _check(api.ConvertStringSidToSidW(value, C.byref(result)), "ConvertStringSidToSidW")
    return result


def set_acl(path, owner_sid, grants=(), low=False):
    """Replace DACL only on caller-owned M5 objects; owner implicit rights limited.

    grants is a sequence of (SID, SDDL rights), e.g. (agent_sid, 'GRGX').
    The caller must scope path to the M5 root before invoking this low-level API.
    """
    api, kernel = _windows()
    api.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [
        W.LPCWSTR, W.DWORD, C.POINTER(C.c_void_p), C.POINTER(W.DWORD)]
    api.SetFileSecurityW.argtypes = [W.LPCWSTR, W.DWORD, C.c_void_p]
    kernel.LocalFree.argtypes = [C.c_void_p]
    # OWNER RIGHTS suppresses implicit owner WRITE_DAC. Explicit trusted SID
    # remains able to administer; restricted SID check still has to succeed.
    dacl = f"D:P(A;OICI;RC;;;OW)(A;OICI;FA;;;{owner_sid})(A;OICI;FA;;;SY)"
    for sid, rights in grants:
        dacl += f"(A;OICI;{rights};;;{sid})"
    descriptor = C.c_void_p()
    _check(api.ConvertStringSecurityDescriptorToSecurityDescriptorW(dacl, 1, C.byref(descriptor), None),
           "ConvertStringSecurityDescriptorToSecurityDescriptorW")
    try:
        flags = 4 | 0x80000000
        _check(api.SetFileSecurityW(str(Path(path).resolve()), flags, descriptor), "SetFileSecurityW")
    finally:
        kernel.LocalFree(descriptor)
    if low:
        result = subprocess.run(["icacls.exe", str(Path(path).resolve()),
                                 "/setintegritylevel", "(OI)(CI)L"], capture_output=True)
        if result.returncode:
            raise IsolationUnavailable("icacls_setintegritylevel", result.returncode)
    return dacl


class RestrictedProcess:
    def __init__(self, handle, pid):
        self.handle, self.pid = handle, pid

    def poll(self):
        _, kernel = _windows()
        kernel.GetExitCodeProcess.argtypes = [W.HANDLE, C.POINTER(W.DWORD)]
        code = W.DWORD()
        _check(kernel.GetExitCodeProcess(self.handle, C.byref(code)), "GetExitCodeProcess")
        return None if code.value == 259 else code.value

    def wait(self, timeout=10):
        deadline = time.monotonic() + timeout
        while self.poll() is None:
            if time.monotonic() >= deadline:
                raise TimeoutError("RESTRICTED_PROCESS_TIMEOUT")
            time.sleep(.02)
        return self.poll()

    def kill(self):
        _, kernel = _windows()
        kernel.TerminateProcess.argtypes = [W.HANDLE, W.UINT]
        if self.poll() is None:
            _check(kernel.TerminateProcess(self.handle, 137), "TerminateProcess")

    def close(self):
        _, kernel = _windows()
        kernel.CloseHandle.argtypes = [W.HANDLE]
        kernel.CloseHandle(self.handle)


def launch_restricted(command, cwd, restricting_sid, environment, support_sids=("S-1-1-0",), integrity_rid=4096):
    """Create a low-IL primary token with disabled privileges and unique SID.

    BUILTIN Users is an additional restricting SID to read OS executable files.
    Protected M5 resources must therefore never grant BUILTIN Users access.
    No handles are inherited; the environment is an explicit caller allowlist.
    """
    api, kernel = _windows()
    kernel.GetCurrentProcess.restype = W.HANDLE
    kernel.CloseHandle.argtypes = [W.HANDLE]
    kernel.LocalFree.argtypes = [C.c_void_p]
    api.OpenProcessToken.argtypes = [W.HANDLE, W.DWORD, C.POINTER(W.HANDLE)]
    api.CreateRestrictedToken.argtypes = [W.HANDLE, W.DWORD, W.DWORD, C.c_void_p,
                                         W.DWORD, C.c_void_p, W.DWORD,
                                         C.POINTER(SID_AND_ATTRIBUTES), C.POINTER(W.HANDLE)]
    api.SetTokenInformation.argtypes = [W.HANDLE, C.c_int, C.c_void_p, W.DWORD]
    api.GetLengthSid.argtypes = [C.c_void_p]
    api.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [
        W.LPCWSTR, W.DWORD, C.POINTER(C.c_void_p), C.POINTER(W.DWORD)]
    api.GetSecurityDescriptorDacl.argtypes = [C.c_void_p, C.POINTER(W.BOOL),
                                             C.POINTER(C.c_void_p), C.POINTER(W.BOOL)]
    api.CreateProcessAsUserW.argtypes = [W.HANDLE, W.LPCWSTR, W.LPWSTR,
        C.c_void_p, C.c_void_p, W.BOOL, W.DWORD, C.c_void_p, W.LPCWSTR,
        C.POINTER(STARTUPINFO), C.POINTER(PROCESS_INFORMATION)]
    original, restricted = W.HANDLE(), W.HANDLE()
    allocated = []
    descriptor = C.c_void_p()
    try:
        _check(api.OpenProcessToken(kernel.GetCurrentProcess(), 0x0002 | 0x0008 | 0x0001 | 0x0080, C.byref(original)),
               "OpenProcessToken")
        restricting_values = (restricting_sid, "S-1-5-32-545", *support_sids)
        if integrity_rid not in {4096, 8192}:
            raise ValueError("UNREGISTERED_INTEGRITY_LEVEL")
        for value in (*restricting_values, f"S-1-16-{integrity_rid}"):
            allocated.append(_sid(api, value))
        sids = (SID_AND_ATTRIBUTES * len(restricting_values))(
            *(SID_AND_ATTRIBUTES(p, 0) for p in allocated[:-1]))
        _check(api.CreateRestrictedToken(original, 1, 0, None, 0, None, len(sids), sids, C.byref(restricted)),
               "CreateRestrictedToken")
        label = SID_AND_ATTRIBUTES(allocated[-1], 0x20)
        _check(api.SetTokenInformation(restricted, 25, C.byref(label),
                                      C.sizeof(label) + api.GetLengthSid(allocated[-1])), "SetTokenIntegrityLevel")
        owner = re.search(rb"S-\d+(?:-\d+)+", subprocess.check_output(
            ["whoami.exe", "/user", "/fo", "csv", "/nh"])).group().decode("ascii")
        label_name = "LW" if integrity_rid == 4096 else "ME"
        sddl = f"D:P(A;;RC;;;OW)(A;;GA;;;{owner})(A;;GA;;;SY)(A;;GA;;;{restricting_sid})S:(ML;;NW;;;{label_name})"
        _check(api.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, C.byref(descriptor), None),
               "ProcessSecurityDescriptor")
        present, defaulted, acl = W.BOOL(), W.BOOL(), C.c_void_p()
        _check(api.GetSecurityDescriptorDacl(descriptor, C.byref(present), C.byref(acl), C.byref(defaulted)),
               "GetSecurityDescriptorDacl")
        _check(api.SetTokenInformation(restricted, 6, C.byref(acl), C.sizeof(acl)), "SetTokenDefaultDacl")
        attributes = SECURITY_ATTRIBUTES(C.sizeof(SECURITY_ATTRIBUTES), descriptor, False)
        startup, process = STARTUPINFO(), PROCESS_INFORMATION()
        startup.cb = C.sizeof(startup)
        env = "\0".join(f"{k}={v}" for k, v in sorted(environment.items(), key=lambda x: x[0].upper())) + "\0\0"
        envbuf = C.create_unicode_buffer(env)
        cmd = C.create_unicode_buffer(subprocess.list2cmdline([str(x) for x in command]))
        _check(api.CreateProcessAsUserW(restricted, str(command[0]), cmd, C.byref(attributes), C.byref(attributes), False,
                                      0x08000000 | 0x400, envbuf, str(cwd),
                                      C.byref(startup), C.byref(process)), "CreateProcessAsUserW")
        kernel.CloseHandle(process.hThread)
        return RestrictedProcess(process.hProcess, process.dwProcessId)
    finally:
        if descriptor:
            kernel.LocalFree(descriptor)
        for ptr in allocated:
            kernel.LocalFree(ptr)
        for handle in (restricted, original):
            if handle:
                kernel.CloseHandle(handle)
