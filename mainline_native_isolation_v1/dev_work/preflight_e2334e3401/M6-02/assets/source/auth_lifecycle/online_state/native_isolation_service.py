"""M6 service bootstrap, reusing M5 token diagnostics and startup handling."""
import json
from pathlib import Path
import sys


def main():
    args = sys.argv
    root = Path(args[args.index("--root") + 1])
    role = args[args.index("--role") + 1]
    config = json.loads((root / "secure" / (role + ".json")).read_text())
    if role == "provider" and config.get("synthetic_transport_fixture"):
        from .native_isolation_fixture import install
        install(config["synthetic_transport_fixture"])
    from .isolation_service import main as serve
    serve()


if __name__ == "__main__": main()
