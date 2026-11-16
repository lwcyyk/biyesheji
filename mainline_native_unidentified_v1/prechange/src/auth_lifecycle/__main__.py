from dataclasses import asdict
from pathlib import Path
import argparse, json
from . import __version__
from .schema import canonical


def main(argv=None):
    ap = argparse.ArgumentParser(description="v2.16 finite L0; no network calls")
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="command", required=True)
    solve_p = sub.add_parser("solve"); solve_p.add_argument("model")
    solve_p.add_argument("--engine", choices=["candidate", "reference"], default="candidate")
    solve_p.add_argument("--horizon", type=int); solve_p.add_argument("--limit", type=int, default=100000)
    cert_p = sub.add_parser("certificate"); cert_p.add_argument("model")
    cert_p.add_argument("--scope", choices=["bounded_policy_impossible", "no_common_immediate_completion"], default="bounded_policy_impossible")
    cert_p.add_argument("--horizon", type=int); cert_p.add_argument("--limit", type=int, default=100000)
    check_p = sub.add_parser("check"); check_p.add_argument("model"); check_p.add_argument("artifact")
    check_p.add_argument("--kind", choices=["policy", "impossibility"], required=True)
    check_p.add_argument("--horizon", type=int); check_p.add_argument("--limit", type=int, default=100000)
    for parser in [solve_p, cert_p, check_p]:parser.add_argument("--out", help="new file only; never overwrite")
    args = ap.parse_args(argv)
    spec = json.loads(Path(args.model).read_text(encoding="utf-8"))
    if args.command == "solve":
        from . import candidate, reference
        result = asdict((candidate if args.engine == "candidate" else reference).solve(spec, horizon=args.horizon, node_limit=args.limit))
    elif args.command == "certificate":
        from .certificates import produce
        status, certificate, reason = produce(spec, scope=args.scope, horizon=args.horizon, node_limit=args.limit)
        result = {"status": status, "reason": reason, "certificate": certificate}
    else:
        from .checker import check_policy, check_impossibility
        artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
        if args.kind == "policy":result = asdict(check_policy(spec, artifact.get("policy", artifact), horizon=args.horizon, node_limit=args.limit))
        else:result = asdict(check_impossibility(spec, artifact.get("certificate", artifact), horizon=args.horizon, node_limit=args.limit))
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with Path(args.out).open("x", encoding="utf-8") as f:f.write(output+"\n")
    else:print(output)
    return 0


if __name__ == "__main__":raise SystemExit(main())
