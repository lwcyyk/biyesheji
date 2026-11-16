"""Process entry points for the mature online-state baseline."""

import argparse
import json
from pathlib import Path

from .lab import Laboratory, initialize
from .services import serve


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--root", required=True)
    init.add_argument("--operation-limit", type=int)
    server = commands.add_parser("serve")
    server.add_argument("--root", required=True)
    server.add_argument("--role", choices=["authority", "provider", "controller"], required=True)
    server.add_argument("--fault", choices=["before_admit", "after_admit", "after_release", "after_effect",
                                         "before_revoke", "after_revoke_commit"])
    request = commands.add_parser("request")
    request.add_argument("--root", required=True)
    request.add_argument("--identity", choices=["user", "agentA", "agentB"], required=True)
    request.add_argument("--operation", required=True)
    request.add_argument("--input", required=True)
    m1 = commands.add_parser("m1")
    m1.add_argument("--out", required=True)
    m1.add_argument("--authorization-id", required=True)
    trace = commands.add_parser("trace")
    trace.add_argument("--root", required=True)
    trace.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if args.command == "init":
        initialize(args.root, args.operation_limit)
        print(json.dumps({"status": "INITIALIZED", "root": str(Path(args.root).resolve())}))
    elif args.command == "serve":
        serve(args.role, args.root, args.fault)
    elif args.command == "request":
        lab = Laboratory(args.root, create=False)
        try:
            result = lab.client(args.identity).call(args.operation, json.loads(Path(args.input).read_text()))
            print(json.dumps(result, ensure_ascii=False))
        finally:
            lab.close()
    elif args.command == "m1":
        from .acceptance import run_acceptance
        run_acceptance(args.out, args.authorization_id)
    elif args.command == "trace":
        from .acceptance import SCENARIOS, run_trace
        if args.scenario not in SCENARIOS:
            parser.error("unknown scenario")
        run_trace(args.root, args.scenario)


if __name__ == "__main__":
    main()
