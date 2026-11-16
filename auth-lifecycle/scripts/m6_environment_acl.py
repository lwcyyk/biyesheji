"""Review/apply the exact legacy lab ACL prerequisite, with separate approval.

Default is a read-only plan. --apply-authorization-id is meaningful only after
the researcher explicitly authorizes changing this existing directory's ACL.
"""
import argparse
import ctypes as C
from ctypes import wintypes as W
import json
from pathlib import Path

from auth_lifecycle.online_state.isolation_acceptance import current_sid
from auth_lifecycle.online_state.windows_isolation import inspect_file_acl, set_acl


TARGET = Path(r"D:\毕业设计\auth-lifecycle\.runtime\l1")


def plan():
    sid = current_sid()
    return {"target": str(TARGET), "current_root_sddl": inspect_file_acl(TARGET),
            "proposed_root_sddl": f"D:P(A;OICI;RC;;;OW)(A;OICI;FA;;;{sid})(A;OICI;FA;;;SY)",
            "change": "root DACL and its inherited ACE propagation only; contents unchanged",
            "retained_trusted_access": [sid, "S-1-5-18"],
            "reason": "legacy management credential and native DB inherit BUILTIN Users read access",
            "authorization_required": "M6 restricts existing objects to inspection; explicit additional ACL authorization required"}


def main():
    p = argparse.ArgumentParser(); p.add_argument("--out", required=True)
    p.add_argument("--apply-authorization-id")
    a = p.parse_args(); out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    record = plan()
    (out / "LEGACY_ACL_CHANGE_PLAN.json").write_text(json.dumps(record, indent=2))
    if a.apply_authorization_id:
        rows = [{"path": str(x), "sddl": inspect_file_acl(x)} for x in [TARGET, *TARGET.rglob("*")]]
        backup = out / "LEGACY_ACL_BEFORE.json"
        if backup.exists(): raise ValueError("ACL_BACKUP_ALREADY_EXISTS")
        backup.write_text(json.dumps({"authorization_id": a.apply_authorization_id, "objects": rows}, indent=2))
        # SetNamedSecurityInfo propagates inherited ACEs to existing children;
        # SetFileSecurity alone does not supply that propagation contract.
        api=C.WinDLL("advapi32",use_last_error=True);kernel=C.WinDLL("kernel32",use_last_error=True)
        api.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes=[W.LPCWSTR,W.DWORD,C.POINTER(C.c_void_p),C.c_void_p]
        api.GetSecurityDescriptorDacl.argtypes=[C.c_void_p,C.POINTER(W.BOOL),C.POINTER(C.c_void_p),C.POINTER(W.BOOL)]
        api.SetNamedSecurityInfoW.argtypes=[W.LPWSTR,C.c_int,W.DWORD,C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p]
        api.SetNamedSecurityInfoW.restype=W.DWORD;kernel.LocalFree.argtypes=[C.c_void_p]
        sd=C.c_void_p();acl=C.c_void_p();present=W.BOOL();defaulted=W.BOOL()
        if not api.ConvertStringSecurityDescriptorToSecurityDescriptorW(record["proposed_root_sddl"],1,C.byref(sd),None):
            raise OSError(C.get_last_error(),"ACL_DESCRIPTOR")
        try:
            if not api.GetSecurityDescriptorDacl(sd,C.byref(present),C.byref(acl),C.byref(defaulted)):
                raise OSError(C.get_last_error(),"ACL_EXTRACT")
            code=api.SetNamedSecurityInfoW(str(TARGET),1,4|0x80000000,None,None,acl,None)
            if code:raise OSError(code,"ACL_PROPAGATION")
        finally:kernel.LocalFree(sd)
        (out / "LEGACY_ACL_AFTER.json").write_text(json.dumps({"authorization_id": a.apply_authorization_id,
            "objects": [{"path": str(x), "sddl": inspect_file_acl(x)} for x in [TARGET, *TARGET.rglob("*")]]}, indent=2))
        record["applied"] = True
    print(json.dumps(record))


if __name__ == "__main__": main()
