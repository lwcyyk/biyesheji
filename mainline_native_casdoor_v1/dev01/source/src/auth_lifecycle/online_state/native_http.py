"""Explicit Casdoor lab profile with persistent per-request accounting."""

import base64
import http.cookiejar
import json
import os
from pathlib import Path
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .protocol import InvalidInput, NoRedirect, canonical, digest, write_json


LIMITS = {"environment": 40, "method": 60, "measurement": 80, "cleanup": 60}
ROUTES = {
    "admin_login": ("POST", "/api/login"),
    "application": ("GET", "/api/get-application?id=admin/app-l1-0"),
    "discovery": ("GET", "/.well-known/openid-configuration"),
    "jwks": ("GET", "/.well-known/jwks"),
    "add_user": ("POST", "/api/add-user"),
    "get_user": ("GET", "/api/get-user"),
    "disable_user": ("POST", "/api/update-user"),
    "delete_user": ("POST", "/api/delete-user"),
    "issue": ("POST", "/api/login/oauth/access_token"),
    "refresh": ("POST", "/api/login/oauth/refresh_token"),
    "revoke": ("POST", "/api/login/oauth/revoke"),
    "userinfo": ("GET", "/api/userinfo"),
    "introspect": ("POST", "/api/login/oauth/introspect"),
}


def create_budget(batch, authorization_id, account_names):
    batch = Path(batch)
    write_json(batch / "BUDGET_AND_AUTHORIZATION.json", {
        "authorization_id": authorization_id, "total": 240, "categories": LIMITS,
        "cleanup_reserved": 60, "maximum_new_accounts": 4, "account_names": account_names,
        "base": "http://127.0.0.1:18081", "plan_denominator": 4,
        "wall_clock_seconds": 3600, "retries_charged_before_send": True})
    con = sqlite3.connect(batch / "native_budget.db")
    con.execute("CREATE TABLE requests(seq INTEGER PRIMARY KEY AUTOINCREMENT,category TEXT,operation TEXT,actor TEXT,started_ns INTEGER,http INTEGER,error_type TEXT,request_bytes INTEGER,response_bytes INTEGER)")
    con.commit()
    con.close()
    (batch / "secure" / "http.key").write_bytes(os.urandom(32))
    (batch / "secure" / "http").mkdir()


class NativeHTTP:
    def __init__(self, batch, category, cookies=False, enabled=False):
        if not enabled or category not in LIMITS:
            raise InvalidInput("NATIVE_PROFILE_EXPLICIT_ENABLE_REQUIRED")
        self.batch = Path(batch)
        self.category = category
        self.policy = json.loads((self.batch / "BUDGET_AND_AUTHORIZATION.json").read_text())
        self.key = (self.batch / "secure" / "http.key").read_bytes()
        handlers = [urllib.request.ProxyHandler({}), NoRedirect()]
        if cookies:
            handlers.append(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.opener = urllib.request.build_opener(*handlers)

    def reserve(self, operation, actor):
        con = sqlite3.connect(self.batch / "native_budget.db", timeout=5, isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE")
            used = con.execute("SELECT COUNT(*) FROM requests WHERE category=?", (self.category,)).fetchone()[0]
            total = con.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
            if used >= LIMITS[self.category] or total >= 240:
                raise RuntimeError("NATIVE_REQUEST_BUDGET_EXHAUSTED")
            cursor = con.execute("INSERT INTO requests(category,operation,actor,started_ns) VALUES(?,?,?,?)",
                                 (self.category, operation, actor, time.monotonic_ns()))
            con.execute("COMMIT")
            return cursor.lastrowid
        finally:
            con.close()

    def call(self, operation, *, actor=None, form=None, payload=None, headers=None, timeout=8):
        if operation not in ROUTES:
            raise InvalidInput("UNREGISTERED_NATIVE_OPERATION")
        actor_operations = {"add_user", "get_user", "disable_user", "delete_user", "issue", "refresh", "revoke", "userinfo", "introspect"}
        if operation in actor_operations and actor not in self.policy["account_names"]:
            raise InvalidInput("NATIVE_ACCOUNT_OUT_OF_SCOPE")
        if self.category == "method" and operation not in {"issue", "refresh", "userinfo", "revoke", "introspect"}:
            raise InvalidInput("METHOD_INTERFACE_DENIED")
        if operation in {"issue", "refresh", "revoke", "introspect"}:
            fields = {
                "issue": {"client_id", "client_secret", "grant_type", "username", "password", "scope"},
                "refresh": {"client_id", "client_secret", "grant_type", "refresh_token", "scope"},
                "revoke": {"client_id", "client_secret", "token", "token_type_hint"},
                "introspect": {"client_id", "client_secret", "token", "token_type_hint"}}
            if not isinstance(form, dict) or set(form) != fields[operation]:
                raise InvalidInput("NATIVE_FORM_FIELDS_DENIED")
            if form.get("client_id") != "l1-client-0":
                raise InvalidInput("NATIVE_CLIENT_OUT_OF_SCOPE")
        if operation == "issue" and form["grant_type"] != "password":
            raise InvalidInput("NATIVE_GRANT_DENIED")
        if operation == "refresh" and form["grant_type"] != "refresh_token":
            raise InvalidInput("NATIVE_GRANT_DENIED")
        if operation == "issue" and form.get("username") != actor:
            raise InvalidInput("NATIVE_LOGIN_ACCOUNT_MISMATCH")
        if operation in {"add_user", "disable_user", "delete_user"}:
            if payload.get("owner") != "l1-study" or payload.get("name") != actor:
                raise InvalidInput("NATIVE_MUTATION_ACCOUNT_MISMATCH")
        method, path = ROUTES[operation]
        if operation == "get_user":
            path += "?" + urllib.parse.urlencode({"id": "l1-study/" + actor})
        if operation == "disable_user":
            path += "?" + urllib.parse.urlencode({"id": "l1-study/" + actor, "columns": "isForbidden"})
        data = None
        request_headers = dict(headers or {})
        if any(key.lower() in {"cookie", "host"} for key in request_headers):
            raise InvalidInput("UNAPPROVED_NATIVE_HEADER")
        if form is not None:
            data = urllib.parse.urlencode(form).encode()
            request_headers["Content-Type"] = "application/x-www-form-urlencoded"
        if payload is not None:
            data = canonical(payload)
            request_headers["Content-Type"] = "application/json"
        sequence = self.reserve(operation, actor)
        started = time.monotonic_ns()
        response = {"http": 0, "body": {}}
        raw = b""
        error_type = None
        try:
            request = urllib.request.Request("http://127.0.0.1:18081" + path,
                                             data=data, headers=request_headers, method=method)
            try:
                answer = self.opener.open(request, timeout=timeout)
            except urllib.error.HTTPError as error:
                answer = error
            with answer:
                response["http"] = answer.status
                raw = answer.read(1024 * 1024)
            try:
                response["body"] = json.loads(raw) if raw else {}
            except (ValueError, UnicodeDecodeError):
                error_type = "ResponseParseFailure"
        except Exception as error:
            error_type = type(error).__name__
        finished = time.monotonic_ns()
        secret_record = {"sequence": sequence, "category": self.category, "operation": operation,
                         "actor": actor, "form": form, "payload": payload, "response": response,
                         "raw_response_base64": base64.b64encode(raw).decode(),
                         "error_type": error_type, "started_ns": started, "finished_ns": finished}
        nonce = os.urandom(12)
        encrypted = nonce + AESGCM(self.key).encrypt(nonce, canonical(secret_record), b"native-http-v1")
        path = self.batch / "secure" / "http" / (str(sequence) + ".aes")
        with path.open("wb") as stream:
            stream.write(encrypted)
            stream.flush()
            os.fsync(stream.fileno())
        con = sqlite3.connect(self.batch / "native_budget.db")
        con.execute("UPDATE requests SET http=?,error_type=?,request_bytes=?,response_bytes=? WHERE seq=?",
                    (response["http"], error_type, len(data or b""), len(raw), sequence))
        con.commit()
        con.close()
        return {**response, "error_type": error_type, "sequence": sequence}


def private_http_records(batch):
    batch = Path(batch)
    cipher = AESGCM((batch / "secure" / "http.key").read_bytes())
    result = []
    for path in sorted((batch / "secure" / "http").glob("*.aes"), key=lambda p: int(p.stem)):
        raw = path.read_bytes()
        result.append(json.loads(cipher.decrypt(raw[:12], raw[12:], b"native-http-v1")))
    return result
