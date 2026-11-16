"""Read actual M5 file ACLs; exact equality with frozen readback, no mutation."""
import argparse
import json
from pathlib import Path

from auth_lifecycle.online_state.windows_isolation import inspect_file_acl


def verify(root):
    root = Path(root).resolve()
    lock = json.loads((root / "ENVIRONMENT_LOCK.json").read_text())
    rows = []
    for name, expected in lock["actual_acl_readback"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root): raise ValueError("ACL_TARGET_OUTSIDE_ROOT")
        actual = inspect_file_acl(path)
        rows.append({"object": name, "matches_frozen_acl": actual == expected, "actual_sddl": actual})
    return {"status": "PASS" if all(r["matches_frozen_acl"] for r in rows) else "CONFIGURATION_CHANGED", "objects": rows}


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--root", required=True); a = p.parse_args()
    print(json.dumps(verify(a.root)))
