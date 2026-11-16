"""P1a offline metadata validator. No OS/process/DB/key/RPC provider."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from auth_lifecycle.online_state.dsat_authority_runtime import (
    ROOT, RuntimeRefusal, inspect_offline_metadata, read_offline_json,
)
from auth_lifecycle.online_state.protocol import strict_json


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeRefusal("UNSUPPORTED_ARGUMENTS")


class OfflineRecordProvider:
    def __init__(self, record):
        self._record = record
        self.targets = []

    def read_one(self, pid):
        self.targets.append(pid)
        return self._record


def parse_args(argv):
    parser = Parser(add_help=False)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--mode", choices=["offline"], default="offline")
    return parser.parse_args(argv)


def main(argv=None):
    try:
        args = parse_args(argv)
        paths = [Path(args.metadata), Path(args.request)]
        if any(str(p).replace("/", "\\").lower().startswith(ROOT.lower()) for p in paths):
            raise RuntimeRefusal("P1_NOT_AUTHORIZED")
        value, request = (read_offline_json(p) for p in paths)
        result = inspect_offline_metadata(request, OfflineRecordProvider(value))
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except Exception:
        print(json.dumps({"status": "REFUSED", "reason": "OFFLINE_METADATA_ONLY_OR_INVALID_TARGET"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
