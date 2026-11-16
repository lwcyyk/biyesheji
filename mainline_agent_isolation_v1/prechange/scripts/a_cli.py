"""Finite A/AB CLI. No live provider dispatch; B sources remain unchanged."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from auth_lifecycle.a import compiler, candidate, joint_reference, audit, runtime
from auth_lifecycle.checker import check_policy


def main():
    p = argparse.ArgumentParser(); p.add_argument("command", choices=["solve", "compile", "check"])
    p.add_argument("source"); p.add_argument("artifact", nargs="?")
    p.add_argument("--method", choices=["A1", "AB1", "B-A", "B-AB", "R-J"], default="AB1")
    p.add_argument("--node-limit", type=int, default=100_000); p.add_argument("--compile-limit", type=int, default=20_000)
    p.add_argument("--out"); args = p.parse_args()
    source = json.loads(Path(args.source).read_text(encoding="utf-8"))
    built = compiler.compile_model(source, node_limit=args.compile_limit)
    if built.status != "COMPILED":output = asdict(built)
    else:
        checked = audit.check_compilation(built.bundle)
        if checked["verdict"] != "ACCEPTED":output = {"status": "REJECTED_COMPILATION", "audit": checked}
        elif args.command == "compile":output = asdict(built)
        elif args.command == "check":
            if not args.artifact:p.error("check requires artifact")
            artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
            output = asdict(check_policy(built.bundle["l0"], artifact.get("result", artifact).get("policy"), node_limit=args.node_limit))
        else:
            result = joint_reference.solve(built.bundle, node_limit=args.node_limit) if args.method == "R-J" else candidate.solve(
                built.bundle, method="B-A" if args.method == "B-A" else "A1", feedback=args.method == "AB1", node_limit=args.node_limit)
            output = {"method": args.method, "source_digest": built.bundle["source_digest"], "compilation_nodes": built.nodes,
                      "audit": checked, "result": asdict(result), "evaluation": runtime.evaluate(built.bundle, result)}
    content = json.dumps(output, ensure_ascii=False, indent=2)
    if args.out:
        with Path(args.out).open("x", encoding="utf-8") as f:f.write(content + "\n")
    else:print(content)
    return 0


if __name__ == "__main__":raise SystemExit(main())
