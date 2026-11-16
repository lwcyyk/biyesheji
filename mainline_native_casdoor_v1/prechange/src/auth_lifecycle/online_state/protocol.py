"""Strict JSON, pinned loopback TLS, and secret-free event projections."""

import hashlib
import json
import os
from pathlib import Path
import re
import ssl
import threading
import time
import urllib.error
import urllib.request


class InvalidInput(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise InvalidInput("DUPLICATE_JSON_KEY")
            result[key] = value
        return result

    def invalid_constant(value):
        raise InvalidInput("NONFINITE_JSON")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", value):
        raise InvalidInput("INVALID_IDENTIFIER")
    return value


def exact_fields(value, fields):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise InvalidInput("INVALID_FIELDS")


def normalized_request(value):
    fields = ("rid", "handle", "task", "account", "audience", "generation",
              "operation", "payload")
    exact_fields(value, fields)
    result = {key: identifier(value[key]) for key in fields if key != "payload"}
    exact_fields(value["payload"], ("value",))
    number = value["payload"]["value"]
    if type(number) is not int or not -1000000 <= number <= 1000000:
        raise InvalidInput("INVALID_PAYLOAD")
    result["payload"] = {"value": number}
    return result


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(canonical(value))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


class EventLog:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def emit(self, event, **fields):
        # Callers supply explicit projections; request bodies and exceptions stay out.
        row = {"event": event, "pid": os.getpid(), "monotonic_ns": time.monotonic_ns(), **fields}
        with self.lock, self.path.open("ab") as stream:
            stream.write(canonical(row) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self, url, token, certificate, log=None, timeout=3):
        if not re.fullmatch(r"https://127\.0\.0\.1:[0-9]+", url):
            raise InvalidInput("LOOPBACK_TLS_REQUIRED")
        port = int(url.rsplit(":", 1)[1])
        if port in {18080, 18081, 8080}:
            raise InvalidInput("NATIVE_ENDPOINT_FORBIDDEN")
        self.url = url
        self.token = token
        self.log = log
        self.timeout = timeout
        context = ssl.create_default_context(cafile=str(certificate))
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect(),
            urllib.request.HTTPSHandler(context=context))

    def call(self, operation, payload):
        identifier(operation)
        body = canonical(payload)
        request = urllib.request.Request(
            self.url + "/" + operation, data=body,
            headers={"Authorization": "Bearer " + self.token,
                     "Content-Type": "application/json"}, method="POST")
        started = time.monotonic_ns()
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                raw = response.read(1024 * 1024)
                result = strict_json(raw)
        except (urllib.error.URLError, TimeoutError, OSError):
            raw = b""
            result = {"status": "UNKNOWN", "reason": "TRANSPORT_UNAVAILABLE"}
        except (ValueError, InvalidInput):
            raw = b""
            result = {"status": "UNKNOWN", "reason": "INVALID_RESPONSE"}
        if self.log:
            self.log.emit("rpc", operation=operation, request_json_bytes=len(body),
                          response_json_bytes=len(raw), status=result.get("status"),
                          elapsed_ns=time.monotonic_ns() - started)
        return result
