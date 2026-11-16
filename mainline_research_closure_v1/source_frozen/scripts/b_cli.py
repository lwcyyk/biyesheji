"""Standard-library CLI for finite B synthesis and independent checks."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from auth_lifecycle.b import search, baselines, reference, certificates, checker


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["solve", "conflict", "check", "audit-g"])
    parser.add_argument("model"); parser.add_argument("artifact", nargs="?")
    parser.add_argument("--engine", choices=["B", "B-B", "reference"], default="B")
    parser.add_argument("--kind", choices=["delivery", "conflict"], default="delivery")
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--out")
    args = parser.parse_args(); spec = json.loads(Path(args.model).read_text(encoding="utf-8"))
    if args.command == "solve":
        result = asdict({"B": search, "B-B": baselines, "reference": reference}[args.engine].solve(spec, limit=args.limit))
    elif args.command == "conflict":result = certificates.produce(spec, limit=args.limit)
    else:
        if not args.artifact:parser.error("check/audit-g requires artifact JSON")
        artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
        if args.command == "audit-g":result = checker.audit_G(spec, (artifact.get("delivery") or artifact).get("configuration"))
        elif args.kind == "delivery":result = checker.check_delivery(spec, artifact.get("delivery", artifact), limit=args.limit)
        else:result = checker.check_conflict(spec, artifact.get("certificate", artifact), limit=args.limit)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with Path(args.out).open("x", encoding="utf-8") as f:f.write(output + "\n")
    else:print(output)
    return 0


if __name__ == "__main__":raise SystemExit(main())
