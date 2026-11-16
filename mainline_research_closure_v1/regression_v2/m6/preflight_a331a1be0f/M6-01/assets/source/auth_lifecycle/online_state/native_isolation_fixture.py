"""Synthetic AS transport for zero-native M6 preflight. Never opens a socket."""
import io
import json
from pathlib import Path
import urllib.parse


class Response(io.BytesIO):
    def __init__(self, body, status=200):
        super().__init__(json.dumps(body).encode()); self.status = status


class FixtureOpener:
    def __init__(self, fixture):
        self.fixture = json.loads(Path(fixture).read_text())
        self.issued = 0
        self.rows, self.pairs = {}, {}

    def open(self, request, timeout=None):
        path = urllib.parse.urlsplit(request.full_url).path
        if not request.full_url.startswith("http://127.0.0.1:18081/"):
            raise AssertionError("SYNTHETIC_TRANSPORT_URL_DENIED")
        values = {k:v[0] for k,v in urllib.parse.parse_qs((request.data or b"").decode()).items()}
        if path.endswith("/access_token") or path.endswith("/refresh_token"):
            if path.endswith("/refresh_token"):
                parent = next((k for k,b in self.pairs.items() if b["refresh_token"] == values.get("refresh_token")), None)
                if parent is None or parent not in self.rows or self.rows[parent]["expiresIn"] <= 0:
                    return Response({"error":"invalid_grant"}, 400)
                del self.rows[parent]
            entry = self.fixture["entries"][self.issued]; self.issued += 1
            body, row = entry["body"], dict(entry["row"])
            unit = row["owner"] + "/" + row["name"]
            self.pairs[unit] = body; self.rows[unit] = row
            return Response(body)
        if path == "/api/userinfo":
            access = request.get_header("Authorization", "").removeprefix("Bearer ")
            ok = any(b["access_token"] == access and unit in self.rows and self.rows[unit]["expiresIn"] > 0
                     for unit,b in self.pairs.items())
            return Response({"sub":self.fixture["account_id"]} if ok else {"error":"inactive"}, 200 if ok else 401)
        if path.endswith("/revoke"):
            for unit,b in self.pairs.items():
                if b["refresh_token"] == values.get("token") and unit in self.rows: self.rows[unit]["expiresIn"] = 0
            return Response({})
        if path.endswith("/introspect"):
            token = values.get("token")
            active = any(token in (b["access_token"], b["refresh_token"]) and unit in self.rows
                         and self.rows[unit]["expiresIn"] > 0 for unit,b in self.pairs.items())
            return Response({"active":active})
        if path == "/api/get-tokens": return Response({"status":"ok", "data":list(self.rows.values()), "data2":1})
        raise AssertionError("SYNTHETIC_TRANSPORT_OPERATION_DENIED")


def install(fixture):
    from .native_http import NativeHTTP
    original = NativeHTTP.__init__
    def initialize(self, *args, **kwargs):
        original(self, *args, **kwargs)
        if self.policy.get("execution_domain") != "SYNTHETIC_ZERO_NATIVE_PREFLIGHT":
            raise RuntimeError("FIXTURE_CANNOT_REPLACE_NATIVE_BATCH")
        self.opener = FixtureOpener(fixture)
    NativeHTTP.__init__ = initialize
