"""Safe startup diagnostics for M5 services; no inherited output handles."""
import argparse
import json
from pathlib import Path
import traceback


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--fault")
    args = parser.parse_args()
    try:
        from .services import serve
        serve(args.role, args.root, args.fault)
    except Exception as error:
        # Class, numeric OS codes and frame locations, never exception text.
        record = {"exception": type(error).__name__, "winerror": getattr(error, "winerror", None),
                  "errno": getattr(error, "errno", None),
                  "frames": [{"file": f.filename, "function": f.name, "line": f.lineno}
                             for f in traceback.extract_tb(error.__traceback__)]}
        if isinstance(error, ImportError): record["loader_error"] = str(error)
        (Path(args.root) / "control" / (args.role + "_startup_error.json")).write_text(json.dumps(record))
        raise SystemExit(1)


if __name__ == "__main__": main()
