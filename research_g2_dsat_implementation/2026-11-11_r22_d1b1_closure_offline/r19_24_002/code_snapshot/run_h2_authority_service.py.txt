"""D1-A strict offline planner. No live deployment issuer or init/serve call."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from auth_lifecycle.online_state.dsat_authority_runtime import ROOT, RuntimeConfig, RuntimeRefusal, read_offline_json
from auth_lifecycle.online_state.protocol import strict_json


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeRefusal("UNSUPPORTED_ARGUMENTS")


def parse_args(argv):
    parser = Parser(add_help=False)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--mode", choices=["offline"], default="offline")
    parser.add_argument("--operation", choices=["prepare", "initialize", "start", "status", "stop", "recover"])
    parser.add_argument("--approval-ref")
    parser.add_argument("--result")
    return parser.parse_args(argv)


def offline_plan(document):
    return RuntimeConfig.from_confirmed(document).plan()


def main(argv=None):
    try:
        args = parse_args(argv)
        if args.operation is not None:
            from auth_lifecycle.online_state.dsat_authority_lifecycle import dispatch_offline_operation
            result = dispatch_offline_operation(args.operation, args.manifest, args.approval_ref, args.result)
            print(json.dumps(result, ensure_ascii=True))
            return 0 if result.get("status") != "REFUSED" else 2
        path = Path(args.manifest)
        if str(path).replace("/", "\\").lower().startswith(ROOT.lower()):
            raise RuntimeRefusal("D1B_NOT_AUTHORIZED")
        document = read_offline_json(path)
        result = offline_plan(document)
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except Exception:
        print(json.dumps({"status": "REFUSED", "reason": "OFFLINE_ONLY_OR_INVALID_CONFIG"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
