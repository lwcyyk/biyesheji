"""Minimal one-shot client. Live H2 is disabled; injected offline transport only."""
import argparse
import json
from pathlib import Path

from auth_lifecycle.online_state.dsat_authority_read_host import HostReadSummary, RIGHT
from auth_lifecycle.online_state.protocol import canonical, strict_json


class ClientRefusal(ValueError):
    pass


class StrictParser(argparse.ArgumentParser):
    def error(self, message):
        raise ClientRefusal("UNSUPPORTED_CLIENT_ARGUMENTS")


def parse_args(argv):
    parser = StrictParser(add_help=False)
    parser.add_argument("--mode", choices=["offline"], required=True)
    parser.add_argument("--manifest", required=True)
    return parser.parse_args(argv)


class OfflineInvocation:
    def __init__(self, transport):
        self._transport = transport
        self.used = False

    def run(self, manifest):
        if self.used:
            raise ClientRefusal("CLIENT_ALREADY_USED")
        if (type(manifest) is not dict or set(manifest) != {"schema", "mode", "payload"}
                or manifest["schema"] != "dsat-a1-offline-client/1" or manifest["mode"] != "OFFLINE_A1"):
            raise ClientRefusal("INVALID_OFFLINE_MANIFEST")
        body = manifest["payload"]
        if (type(body) is not dict or set(body) != {"authorization_ref", "permit_ref", "read_scope_ref"}
                or any(type(x) is not str or not 1 <= len(x) <= 160 for x in body.values())):
            raise ClientRefusal("INVALID_OFFLINE_MANIFEST")
        self.used = True
        try:
            raw = self._transport.call(RIGHT, json.loads(canonical(body)))
            raw = canonical(raw) if type(raw) is dict else raw
            if type(raw) is not bytes or len(raw) > 4096:
                raise ClientRefusal("INVALID_OFFLINE_RESPONSE")
            summary = HostReadSummary(strict_json(raw))
            return summary.to_json()
        except Exception:
            raise ClientRefusal("OFFLINE_CALL_FAILED") from None


def main(argv=None, *, transport=None):
    try:
        args = parse_args(argv)
        # There is deliberately no live transport or credential/config loader.
        if transport is None:
            raise ClientRefusal("REAL_EXECUTION_DISABLED")
        path = Path(args.manifest)
        if path.suffix.lower() != ".json":
            raise ClientRefusal("INVALID_OFFLINE_MANIFEST")
        manifest = strict_json(path.read_bytes())
        raw = OfflineInvocation(transport).run(manifest)
        print(raw.decode("utf-8"))
        return 0
    except (ClientRefusal, ValueError, TypeError, KeyError, OSError):
        print(json.dumps({"status": "REFUSED", "reason": "OFFLINE_ONLY_OR_INVALID_REQUEST"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
