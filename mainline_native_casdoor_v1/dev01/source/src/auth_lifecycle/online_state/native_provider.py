"""Explicit Casdoor gateway, with an optional durable operational result inbox."""

import base64
import json
import os
from pathlib import Path
import threading
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .materials import decode64, token_bundle, validate_material, verified_claims
from .native_http import NativeHTTP
from .protocol import EventLog, InvalidInput, canonical, exact_fields, write_json


class CasdoorProvider:
    def __init__(self, root, config):
        self.root = Path(root)
        self.profile = json.loads(Path(config["native_profile"]).read_text())
        if self.profile.get("enabled") is not True or self.profile.get("version") != "4.25.0":
            raise InvalidInput("NATIVE_PROFILE_NOT_ENABLED")
        self.http = NativeHTTP(self.profile["batch"], "method", enabled=True)
        self.key = (self.root / "secure" / "provider.key").read_bytes()
        self.log = EventLog(self.root / "provider" / "native_events.jsonl")
        self.inbox = self.root / "provider" / "native_inbox.jsonl"
        self.lock = threading.Lock()
        self.results = {}
        if self.inbox.exists():
            for line in self.inbox.read_bytes().splitlines():
                raw = base64.b64decode(line)
                result = json.loads(AESGCM(self.key).decrypt(raw[:12], raw[12:], b"native-inbox-v1"))
                self.results[result["attempt_id"]] = result

    def call(self, operation, payload, identity):
        if operation == "lookup":
            exact_fields(payload, ("rid", "digest", "origin", "attempt_id", "release_version"))
            result = self.results.get(payload["attempt_id"])
            if result is None:
                return {"status": "UNKNOWN", "reason": "NO_DURABLE_OPERATIONAL_RESULT"}
            if any(result[key] != payload[key] for key in payload):
                return {"status": "CONFLICT", "reason": "LOOKUP_SOURCE_CONFLICT"}
            self.log.emit("operational_lookup", rid=result["rid"], attempt_id=result["attempt_id"])
            return {"status": "PROVIDER_RESULT", **result}
        if operation == "dispose":
            material = validate_material(payload["material"], self.profile["actor"]["id"], self.profile["client_id"])
            access = material["native"]["access_token"]
            verified_claims(access, self.profile)
            header = json.loads(decode64(access.split(".")[0]))
            verified_claims(material["native"]["refresh_token"], self.profile, header.get("kid"))
            answer = self.http.call("revoke", actor=self.profile["actor"]["name"], form={
                "client_id": self.profile["client_id"], "client_secret": self.profile["client_secret"],
                "token": material["native"]["refresh_token"], "token_type_hint": "refresh_token"})
            if not answer["http"]:
                return {"status": "UNKNOWN"}
            resource = self.http.call("userinfo", actor=self.profile["actor"]["name"],
                                      headers={"Authorization": "Bearer " + material["native"]["access_token"]})
            active = self.http.call("introspect", actor=self.profile["actor"]["name"], form={
                "client_id": self.profile["client_id"], "client_secret": self.profile["client_secret"],
                "token": material["native"]["access_token"], "token_type_hint": "access_token"})
            value = active["body"].get("active") if active["http"] == 200 else None
            return {"status": "DISPOSAL_RESPONSE", "http": answer["http"],
                    "userinfo_http": resource["http"],
                    "userinfo_accepted": resource["http"] == 200 if resource["http"] in {200, 400, 401, 403} else None,
                    "introspection_active": value if type(value) is bool else None}
        if operation != "perform":
            return {"status": "REJECTED", "reason": "UNSUPPORTED_NATIVE_OPERATION"}
        material = validate_material(payload["material"], self.profile["actor"]["id"], self.profile["client_id"])
        if material["kind"] == "casdoor_oauth":
            access = material["native"]["access_token"]
            verified_claims(access, self.profile)
            header = json.loads(decode64(access.split(".")[0]))
            verified_claims(material["native"]["refresh_token"], self.profile, header.get("kid"))
        if payload["origin"]["account"] != self.profile["actor"]["id"] or payload["origin"]["audience"] != self.profile["client_id"]:
            raise InvalidInput("NATIVE_ORIGIN_MISMATCH")
        kind = payload["operation"]
        common = {"client_id": self.profile["client_id"], "client_secret": self.profile["client_secret"]}
        if kind == "issue" and material["kind"] == "casdoor_login":
            answer = self.http.call("issue", actor=self.profile["actor"]["name"], form={**common,
                "grant_type": "password", "username": material["username"], "password": material["password"], "scope": "openid"})
        elif kind == "refresh" and material["kind"] == "casdoor_oauth":
            answer = self.http.call("refresh", actor=self.profile["actor"]["name"], form={**common,
                "grant_type": "refresh_token", "refresh_token": material["native"]["refresh_token"], "scope": "openid"})
        elif kind == "userinfo" and material["kind"] == "casdoor_oauth":
            answer = self.http.call("userinfo", actor=self.profile["actor"]["name"],
                                    headers={"Authorization": "Bearer " + material["native"]["access_token"]})
        else:
            raise InvalidInput("NATIVE_OPERATION_MATERIAL_MISMATCH")
        self.log.emit("native_response_received", rid=payload["rid"], attempt_id=payload["attempt_id"],
                      native_sequence=answer["sequence"], http=answer["http"])
        if answer["http"] != 200 or answer["error_type"]:
            return {"status": "UNKNOWN", "reason": "NATIVE_RESULT_UNCERTAIN"}
        if kind == "userinfo":
            if answer["body"].get("sub") != self.profile["actor"]["id"]:
                raise InvalidInput("USERINFO_ACCOUNT_MISMATCH")
            result_material = material
        else:
            result_material = token_bundle(answer["body"], self.profile)
        result = {key: payload[key] for key in ("rid", "digest", "origin", "attempt_id", "release_version")}
        result.update(material=result_material, outcome="OK")
        if self.profile.get("durable_inbox", True):
            with self.lock:
                nonce = os.urandom(12)
                raw = nonce + AESGCM(self.key).encrypt(nonce, canonical(result), b"native-inbox-v1")
                with self.inbox.open("ab") as stream:
                    stream.write(base64.b64encode(raw) + b"\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                self.results[result["attempt_id"]] = result
            self.log.emit("operational_result_durable", rid=payload["rid"], attempt_id=payload["attempt_id"])
        if kind == "refresh" and self.profile.get("hold_refresh"):
            barrier = self.root / "provider" / "refresh_received.json"
            write_json(barrier, {"rid": payload["rid"], "attempt_id": payload["attempt_id"],
                                 "native_sequence": answer["sequence"], "durable_inbox": bool(self.profile.get("durable_inbox"))})
            while not barrier.with_suffix(".release").exists():
                time.sleep(0.01)
        self.log.emit("result_delivered_to_controller", rid=payload["rid"], attempt_id=payload["attempt_id"])
        return {"status": "PROVIDER_RESULT", **result}
