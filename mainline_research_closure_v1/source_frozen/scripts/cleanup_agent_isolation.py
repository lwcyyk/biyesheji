"""Cleanup only recorded M5 processes, checking creation time and exact image."""
import argparse
import ctypes as C
from ctypes import wintypes as W
import json
from pathlib import Path
import shutil

from auth_lifecycle.online_state.windows_isolation import process_facts


def cleanup(root, remove_runtime=False):
    root = Path(root).resolve()
    owned = json.loads((root / "OWNED_PROCESSES.json").read_text())
    if Path(owned["root"]).resolve() != root: raise ValueError("OWNERSHIP_ROOT_MISMATCH")
    kernel = C.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]; kernel.OpenProcess.restype = W.HANDLE
    kernel.TerminateProcess.argtypes = [W.HANDLE, W.UINT]
    kernel.WaitForSingleObject.argtypes = [W.HANDLE, W.DWORD]
    kernel.CloseHandle.argtypes = [W.HANDLE]
    rows = []
    expected_image = (root / "assets" / "python" / "python.exe").resolve()
    for r in owned["processes"]:
        handle = kernel.OpenProcess(0x1000 | 0x1 | 0x100000, False, r["pid"])
        if not handle:
            rows.append({"pid": r["pid"], "action": "NO_OPEN_HANDLE", "winerror": C.get_last_error()}); continue
        try:
            facts = process_facts(handle)
            if facts["created_filetime"] != r["created_filetime"] or Path(facts["image"]).resolve() != expected_image:
                rows.append({"pid": r["pid"], "action": "PID_REUSED_OR_IDENTITY_MISMATCH_SKIPPED"}); continue
            ok = kernel.TerminateProcess(handle, 137)
            waited = kernel.WaitForSingleObject(handle, 5000) == 0 if ok else False
            rows.append({"pid": r["pid"], "action": "OWNED_PROCESS_TERMINATED", "success": bool(ok and waited)})
        finally: kernel.CloseHandle(handle)
    removed = False
    if remove_runtime:
        target = (root / "assets" / "python").resolve()
        if target == root or not target.is_relative_to(root): raise ValueError("REMOVE_OUTSIDE_OWNED_ROOT")
        if target.exists(): shutil.rmtree(target); removed = True
    result = {"root": str(root), "processes": rows, "runtime_copy_removed": removed,
              "sam_users_created": 0, "outside_acl_changes": 0, "audit_and_scoped_acl": "retained"}
    (root / "CLEANUP_RECHECK.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--root", required=True); p.add_argument("--remove-runtime", action="store_true")
    a = p.parse_args(); print(json.dumps(cleanup(a.root, a.remove_runtime)))
