"""Authenticated local authority, controller, and synthetic provider processes."""

import base64
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import ssl
import threading
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .protocol import (Client, EventLog, InvalidInput, canonical, digest,
                       exact_fields, identifier, normalized_request, strict_json, write_json)
from .storage import AuthorityStore


class SingleActive:
    """OS-held lock outside the rollback cache. A process exit releases it."""
    def __init__(self, path):
        self.stream = open(path, "a+b")
        try:
            if os.fstat(self.stream.fileno()).st_size == 0:
                self.stream.write(b"0")
                self.stream.flush()
            self.stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise


class Controller:
    def __init__(self, root, config, fault=None):
        self.root = Path(root)
        self.config = config
        self.active_lock = SingleActive(self.root / "secure" / "controller.lock")
        self.log = EventLog(self.root / "controller" / "events.jsonl")
        self.authority = Client(config["authority_url"], config["authority_token"],
                                config["certificate"], self.log)
        self.provider = Client(config["provider_url"], config["provider_token"],
                               config["certificate"], self.log)
        self.boot = secrets.token_hex(8)
        self.fault = fault
        self.fault_used = False
        self.ready = False
        self.recover()

    def barrier(self, point):
        if point != self.fault or self.fault_used:
            return
        self.fault_used = True
        folder = self.root / "controller" / "barriers"
        path = folder / (self.boot + "_" + point + ".json")
        write_json(path, {"point": point, "pid": os.getpid(), "boot": self.boot})
        self.log.emit("barrier", point=point, boot=self.boot)
        release = path.with_suffix(".release")
        while not release.exists():
            time.sleep(0.01)

    def recover(self):
        result = self.authority.call("recover", {})
        self.ready = result.get("status") == "RECOVERED"
        if self.ready:
            write_json(self.root / "cache" / "view.json", {
                "authoritative_version": result["version"], "boot": self.boot,
                "approval_count": len(result["approvals"]), "display_only": True})
        self.log.emit("recovery", status=result.get("status"),
                      version=result.get("version"), boot=self.boot)
        return result

    def call(self, operation, payload, identity):
        if operation == "recover":
            return self.recover()
        if not self.ready and self.recover().get("status") != "RECOVERED":
            return {"status": "UNKNOWN", "reason": "RECOVERY_INCOMPLETE"}
        if operation == "grant":
            return self.authority.call("grant", payload)
        if operation == "revoke":
            self.barrier("before_revoke")
            result = self.authority.call("revoke", payload)
            if result.get("status") == "LOCAL_REVOKE_COMMITTED":
                self.barrier("after_revoke_commit")
            return result
        if operation == "status":
            result = self.authority.call("recover", {})
            if result.get("status") != "RECOVERED" or identity == "user":
                return result
            result["approvals"] = [x for x in result["approvals"] if x["caller"] == identity]
            result["requests"] = [x for x in result["requests"] if x["origin"]["caller"] == identity]
            result["obligations"] = [x["rid"] for x in result["requests"]
                                     if x["phase"] in {"DISPATCHED_UNKNOWN", "QUARANTINED"}]
            return result
        if operation == "deliver":
            exact_fields(payload, ("rid",))
            identifier(payload["rid"])
            known = self.authority.call("recover", {})
            if known.get("status") != "RECOVERED":
                return known
            req = next((x for x in known["requests"] if x["rid"] == payload["rid"]), None)
            if req is None or req["attempt_id"] is None:
                return {"status": "UNKNOWN", "reason": "NO_KNOWN_ATTEMPT"}
            lookup = {key: req[key] for key in
                      ("rid", "digest", "origin", "attempt_id", "release_version")}
            result = self.provider.call("lookup", lookup)
            return self.record_result(result)
        if operation != "call":
            return {"status": "REJECTED", "reason": "INVALID_OPERATION"}
        request = normalized_request(payload)
        self.barrier("before_admit")
        admitted = self.authority.call("admit", {"caller": identity, "request": request})
        if admitted.get("status") not in {"ADMITTED", "DUPLICATE"}:
            return admitted
        self.barrier("after_admit")
        if admitted["phase"] != "QUEUED":
            return admitted
        released = self.authority.call("release", {
            "caller": identity, "rid": request["rid"], "digest": admitted["digest"]})
        if not released.get("send"):
            return released
        self.barrier("after_release")
        provider_request = {key: released[key] for key in
                            ("rid", "digest", "origin", "attempt_id", "release_version",
                             "material", "operation", "payload")}
        result = self.provider.call("perform", provider_request)
        self.barrier("after_effect")
        return self.record_result(result)

    def record_result(self, result):
        if result.get("status") != "PROVIDER_RESULT":
            return {"status": "UNKNOWN", "reason": "EXTERNAL_RESULT_UNCERTAIN"}
        fields = ("rid", "digest", "origin", "attempt_id", "release_version", "material", "outcome")
        if not all(key in result for key in fields):
            return {"status": "UNKNOWN", "reason": "INVALID_PROVIDER_RESULT"}
        envelope = {key: result[key] for key in fields}
        return self.authority.call("record", envelope)


class FakeProvider:
    def __init__(self, root, config):
        self.root = Path(root)
        self.key = (self.root / "secure" / "provider.key").read_bytes()
        self.results_path = self.root / "provider" / "encrypted_results.jsonl"
        self.results_path.parent.mkdir(parents=True, exist_ok=True)
        self.truth = EventLog(self.root / "provider" / "truth.jsonl")
        self.lock = threading.Lock()
        self.hold = False
        self.results = {}
        if self.results_path.exists():
            for line in self.results_path.read_bytes().splitlines():
                raw = base64.b64decode(line)
                result = json.loads(AESGCM(self.key).decrypt(raw[:12], raw[12:], b"fake-provider-v1"))
                self.results[result["attempt_id"]] = result

    def call(self, operation, payload, identity):
        with self.lock:
            if operation == "hold":
                exact_fields(payload, ("enabled",))
                if type(payload["enabled"]) is not bool:
                    raise InvalidInput("INVALID_HOLD")
                self.hold = payload["enabled"]
                return {"status": "CONFIGURED"}
            if operation == "lookup":
                exact_fields(payload, ("rid", "digest", "origin", "attempt_id", "release_version"))
                result = self.results.get(payload["attempt_id"])
                if result is None:
                    return {"status": "UNKNOWN", "reason": "NO_RESULT_EVIDENCE"}
                if any(result[key] != payload[key] for key in payload):
                    return {"status": "CONFLICT", "reason": "LOOKUP_BINDING_CONFLICT"}
                return {"status": "PROVIDER_RESULT", **result}
            if operation != "perform":
                return {"status": "REJECTED", "reason": "INVALID_OPERATION"}
            fields = ("rid", "digest", "origin", "attempt_id", "release_version", "material", "operation", "payload")
            exact_fields(payload, fields)
            if not isinstance(payload["material"], str) or not payload["material"].startswith("synthetic_"):
                return {"status": "REJECTED", "reason": "SYNTHETIC_MATERIAL_REQUIRED"}
            # Each perform invocation records an effect, including accidental retries.
            result = {key: payload[key] for key in
                      ("rid", "digest", "origin", "attempt_id", "release_version")}
            result.update(material="synthetic_result_" + secrets.token_hex(24), outcome="OK")
            nonce = os.urandom(12)
            sealed = nonce + AESGCM(self.key).encrypt(nonce, canonical(result), b"fake-provider-v1")
            with self.results_path.open("ab") as stream:
                stream.write(base64.b64encode(sealed) + b"\n")
                stream.flush()
                os.fsync(stream.fileno())
            self.results[payload["attempt_id"]] = result
            self.truth.emit("effect", **{key: result[key] for key in
                                        ("rid", "digest", "origin", "attempt_id", "release_version")})
            if self.hold:
                return {"status": "PENDING"}
            return {"status": "PROVIDER_RESULT", **result,
                    "untrusted_extra": "synthetic_debug_secret_do_not_export"}


def serve(role, root, fault=None):
    root = Path(root)
    config = json.loads((root / "secure" / (role + ".json")).read_text())
    log = EventLog(root / role / "transport.jsonl")
    if role == "authority":
        implementation = AuthorityStore(root / "authority", root / "secure" / "authority.key",
                                        config.get("operation_limit"))
    elif role == "provider":
        implementation = FakeProvider(root, config)
    else:
        implementation = Controller(root, config, fault)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            started = time.monotonic_ns()
            request_bytes = 0
            operation = self.path.removeprefix("/")
            identity = None
            supplied = self.headers.get("Authorization", "")
            for name, token in config["identities"].items():
                if hmac.compare_digest(supplied, "Bearer " + token):
                    identity = name
            allowed = config["permissions"].get(identity, [])
            try:
                if operation not in allowed:
                    result = {"status": "REJECTED", "reason": "IDENTITY_OR_OPERATION_DENIED"}
                else:
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 0 < length <= 65536:
                        raise InvalidInput("BODY_SIZE")
                    raw = self.rfile.read(length)
                    request_bytes = len(raw)
                    payload = strict_json(raw)
                    if role == "authority":
                        result = implementation.call(operation, payload)
                    else:
                        result = implementation.call(operation, payload, identity)
            except (ValueError, TypeError, KeyError, InvalidInput):
                result = {"status": "REJECTED", "reason": "INVALID_INPUT"}
            except Exception:
                result = {"status": "UNKNOWN", "reason": "SERVICE_UNAVAILABLE"}
            response = canonical(result)
            # The operation logged is selected from the configured whitelist.
            log.emit("request", operation=operation if operation in allowed else "denied",
                     identity=identity, request_json_bytes=request_bytes,
                     response_json_bytes=len(response), status=result.get("status"),
                     elapsed_ns=time.monotonic_ns() - started)
            try:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)
            except (OSError, ssl.SSLError):
                pass

    server = ThreadingHTTPServer(("127.0.0.1", config["port"]), Handler)
    server.daemon_threads = True
    tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls.minimum_version = ssl.TLSVersion.TLSv1_2
    tls.load_cert_chain(config["certificate"], config["tls_key"])
    server.socket = tls.wrap_socket(server.socket, server_side=True)
    write_json(root / "control" / (role + "_ready.json"),
               {"role": role, "pid": os.getpid(), "port": config["port"],
                "boot": getattr(implementation, "boot", None)})
    server.serve_forever(poll_interval=0.05)
