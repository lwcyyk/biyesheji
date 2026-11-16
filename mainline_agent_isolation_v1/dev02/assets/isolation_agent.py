"""Untrusted M5 test program. Runs in a restricted primary token, stdlib only."""
import argparse
import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
import os
from pathlib import Path
import ssl
import time
import urllib.request


def token_information():
    api = C.WinDLL("advapi32", use_last_error=True)
    kernel = C.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = W.HANDLE
    api.OpenProcessToken.argtypes = [W.HANDLE, W.DWORD, C.POINTER(W.HANDLE)]
    api.GetTokenInformation.argtypes = [W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.POINTER(W.DWORD)]
    api.ConvertSidToStringSidW.argtypes = [C.c_void_p, C.POINTER(W.LPWSTR)]
    kernel.CloseHandle.argtypes = [W.HANDLE]
    kernel.LocalFree.argtypes = [C.c_void_p]
    token = W.HANDLE()
    if not api.OpenProcessToken(kernel.GetCurrentProcess(), 8, C.byref(token)):
        return {"error": C.get_last_error()}

    class SID_ATTRIBUTES(C.Structure):
        _fields_ = [("Sid", C.c_void_p), ("Attributes", W.DWORD)]
    class GROUPS(C.Structure):
        _fields_ = [("Count", W.DWORD), ("Groups", SID_ATTRIBUTES * 1)]

    def query(kind):
        size = W.DWORD()
        api.GetTokenInformation(token, kind, None, 0, C.byref(size))
        buffer = C.create_string_buffer(size.value)
        if not api.GetTokenInformation(token, kind, buffer, size, C.byref(size)):
            raise OSError(C.get_last_error(), "TOKEN_QUERY")
        return buffer

    def sid(ptr):
        text = W.LPWSTR()
        if not api.ConvertSidToStringSidW(ptr, C.byref(text)):
            return "INVALID_SID"
        value = text.value
        kernel.LocalFree(text)
        return value

    def groups(kind):
        buffer = query(kind)
        count = W.DWORD.from_buffer(buffer).value
        values = (SID_ATTRIBUTES * count).from_buffer(buffer, GROUPS.Groups.offset)
        return [{"sid": sid(g.Sid), "attributes": g.Attributes} for g in values]

    try:
        info = {"user": sid(SID_ATTRIBUTES.from_buffer(query(1)).Sid),
                "groups": groups(2), "restricting_sids": groups(11),
                "integrity": sid(SID_ATTRIBUTES.from_buffer(query(25)).Sid),
                "elevated": W.DWORD.from_buffer(query(20)).value,
                "token_type": W.DWORD.from_buffer(query(8)).value,
                "pid": os.getpid()}
        # Record enabled privilege LUIDs without reading arbitrary host state.
        raw = query(3)
        count = W.DWORD.from_buffer(raw).value
        info["privilege_count"] = count
        info["privileges_raw_hex"] = raw.raw.hex()
        return info
    finally:
        kernel.CloseHandle(token)


def file_probe(targets, mode):
    results = []
    for item in targets:
        path = Path(item["path"])
        row = {"object": item["object"], "path": str(path), "operation": mode}
        try:
            if mode == "read":
                data = path.read_bytes()
                row.update(allowed=True, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            elif mode == "write":
                with path.open("r+b") as stream:
                    byte = stream.read(1)
                    stream.seek(0)
                    stream.write(byte)  # permission exercise, preserves bytes
                row.update(allowed=True, bytes_written=len(byte))
            elif mode == "acl":
                api = C.WinDLL("advapi32", use_last_error=True)
                kernel = C.WinDLL("kernel32", use_last_error=True)
                api.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [
                    W.LPCWSTR, W.DWORD, C.POINTER(C.c_void_p), C.c_void_p]
                api.SetFileSecurityW.argtypes = [W.LPCWSTR, W.DWORD, C.c_void_p]
                kernel.LocalFree.argtypes = [C.c_void_p]
                desc = C.c_void_p()
                if not api.ConvertStringSecurityDescriptorToSecurityDescriptorW(
                        "D:P(A;;FA;;;WD)", 1, C.byref(desc), None):
                    raise OSError(C.get_last_error(), "DESCRIPTOR")
                try:
                    allowed = bool(api.SetFileSecurityW(str(path), 4 | 0x80000000, desc))
                    row.update(allowed=allowed, winerror=0 if allowed else C.get_last_error())
                finally:
                    kernel.LocalFree(desc)
        except OSError as error:
            row.update(allowed=False, winerror=getattr(error, "winerror", None), errno=error.errno,
                       classification="NOT_FOUND" if isinstance(error, FileNotFoundError) else "ACCESS_ERROR")
        results.append(row)
        if row.get("allowed"):
            break  # preserve first counterexample, no further target accesses
    return results


def process_probe(pids, inherited_handle):
    kernel = C.WinDLL("kernel32", use_last_error=True)
    api = C.WinDLL("advapi32", use_last_error=True)
    kernel.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
    kernel.OpenProcess.restype = W.HANDLE
    kernel.CloseHandle.argtypes = [W.HANDLE]
    api.OpenProcessToken.argtypes = [W.HANDLE, W.DWORD, C.POINTER(W.HANDLE)]
    rows = []
    for role, pid in pids.items():
        for label, mask in [("VM_READ", 0x10), ("VM_WRITE_OPERATION", 0x28), ("DUP_HANDLE", 0x40),
                            ("CREATE_THREAD", 2), ("TERMINATE", 1), ("WRITE_DAC", 0x40000),
                            ("QUERY_LIMITED", 0x1000)]:
            handle = kernel.OpenProcess(mask, False, pid)
            row = {"role": role, "pid": pid, "operation": label, "mask": mask,
                   "allowed": bool(handle), "winerror": 0 if handle else C.get_last_error()}
            if handle:
                if label == "QUERY_LIMITED":
                    token = W.HANDLE()
                    ok = api.OpenProcessToken(handle, 0x2 | 0x1, C.byref(token))
                    row["token_duplicate_assign"] = {"allowed": bool(ok),
                        "winerror": 0 if ok else C.get_last_error()}
                    if token: kernel.CloseHandle(token)
                kernel.CloseHandle(handle)
            rows.append(row)
            if row["allowed"] and label != "QUERY_LIMITED":
                return {"processes": rows, "stopped_on_sensitive_access": True}
    kernel.GetHandleInformation.argtypes = [W.HANDLE, C.POINTER(W.DWORD)]
    flags = W.DWORD()
    ok = kernel.GetHandleInformation(inherited_handle, C.byref(flags))
    # If numeric value was reused, resolve its object path; a coincidental handle
    # does not establish inheritance of the parent's canary file.
    kernel.GetFinalPathNameByHandleW.argtypes = [W.HANDLE, W.LPWSTR, W.DWORD, W.DWORD]
    path = C.create_unicode_buffer(32768)
    length = kernel.GetFinalPathNameByHandleW(inherited_handle, path, len(path), 0) if ok else 0
    return {"processes": rows, "canary_handle": {"valid": bool(ok),
            "winerror": 0 if ok else C.get_last_error(), "resolved_path": path.value if length else None}}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args): return None


def rpc(config, request):
    role = request.get("role", "controller")
    url = config["urls"][role]
    # Provisioned fixture endpoints only. Never accept request-provided URLs.
    context = ssl.create_default_context(cafile=config["certificate"])
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect(),
                                        urllib.request.HTTPSHandler(context=context))
    body = request.get("raw")
    body = body.encode() if body is not None else json.dumps(request.get("payload", {})).encode()
    token = config["capability"] if request.get("token", "own") == "own" else "M5_INVALID_CAPABILITY"
    message = urllib.request.Request(url + "/" + request["operation"], data=body,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"}, method="POST")
    try:
        with opener.open(message, timeout=4) as response:
            raw = response.read(1 << 20)
            return {"reached": True, "http": response.status, "result": json.loads(raw),
                    "response_bytes": len(raw)}
    except Exception as error:
        return {"reached": False, "error_type": type(error).__name__}  # no exception text/URLs/secrets


def act(config, command):
    action = command["action"]
    if action == "identity":
        own = Path(config["work"]) / "positive.txt"
        own.write_text("M5_OWN_WORKSPACE_POSITIVE", encoding="ascii")
        return {"token": token_information(), "own_read_write": own.read_text() == "M5_OWN_WORKSPACE_POSITIVE",
                "environment": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in os.environ.items()},
                "command_line": __import__("sys").argv}
    if action == "rpc": return rpc(config, command)
    if action in {"read", "write", "acl"}: return file_probe(command["targets"], action)
    if action == "process": return process_probe(command["pids"], command["canary_handle"])
    raise ValueError("UNKNOWN_TEST_ACTION")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    work = Path(config["work"])
    (work / "ready.json").write_text(json.dumps({"pid": os.getpid(), "token": token_information()}))
    seen = set()
    while not (work / "stop").exists():
        for path in sorted((work / "in").glob("*.json")):
            if path.name in seen: continue
            try:
                command = json.loads(path.read_text())
                result = act(config, command)
            except Exception as error:
                result = {"probe_error": type(error).__name__}
            (work / "out" / path.name).write_text(json.dumps(result), encoding="utf-8")
            seen.add(path.name)
        time.sleep(.01)


if __name__ == "__main__": main()
