"""Explicit Casdoor gateway, with an optional durable operational result inbox."""

import base64
import json
import os
from pathlib import Path
import threading
import time
import sqlite3

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .materials import decode64, token_bundle, validate_material, verified_claims
from .native_http import NativeHTTP
from .protocol import EventLog, InvalidInput, canonical, digest, exact_fields, write_json
from .enumeration import analyze, ScopeViolation


class CasdoorProvider:
    def __init__(self, root, config):
        self.root = Path(root)
        self.profile = json.loads(Path(config["native_profile"]).read_text())
        if self.profile.get("enabled") is not True or self.profile.get("version") != "4.25.0":
            raise InvalidInput("NATIVE_PROFILE_NOT_ENABLED")
        self.http = NativeHTTP(self.profile["batch"], "method", enabled=True)
        self.budget_path = self.http.budget_path
        self.key = (self.root / "secure" / "provider.key").read_bytes()
        self.log = EventLog(self.root / "provider" / "native_events.jsonl")
        self.inbox = self.root / "provider" / "native_inbox.jsonl"
        self.lock = threading.Lock()
        self.results = {}
        self.identifier_log = EventLog(self.root / "provider" / "identifier_receipts.jsonl")
        if self.profile.get("identifier_journal"):
            self.log.emit("identifier_journal_enabled", scope="responses received after this process start")
        if self.inbox.exists():
            for line in self.inbox.read_bytes().splitlines():
                raw = base64.b64decode(line)
                result = json.loads(AESGCM(self.key).decrypt(raw[:12], raw[12:], b"native-inbox-v1"))
                self.results[result["attempt_id"]] = result

    def call(self, operation, payload, identity):
        if operation == "reconcile_query":
            return self.reconcile_query(payload)
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
                    "userinfo_accepted": (resource["http"] == 200 and resource["body"].get("sub") == self.profile["actor"]["id"])
                       if resource["http"] in {200, 400, 401, 403} else None,
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
        context = {key: payload[key] for key in ("rid", "digest", "attempt_id")}
        if kind == "refresh" and self.profile.get("hold_before_native_refresh"):
            path = self.root / "provider" / "before_native_refresh.json"
            write_json(path, {**context, "position": "before NativeHTTP reservation and send"})
            while not path.with_suffix(".release").exists():
                time.sleep(0.01)
        common = {"client_id": self.profile["client_id"], "client_secret": self.profile["client_secret"]}
        if kind == "issue" and material["kind"] == "casdoor_login":
            answer = self.http.call("issue", actor=self.profile["actor"]["name"], form={**common,
                "grant_type": "password", "username": material["username"], "password": material["password"], "scope": "openid"}, context=context)
        elif kind == "refresh" and material["kind"] == "casdoor_oauth":
            answer = self.http.call("refresh", actor=self.profile["actor"]["name"], form={**common,
                "grant_type": "refresh_token", "refresh_token": material["native"]["refresh_token"], "scope": "openid"}, context=context)
        elif kind == "userinfo" and material["kind"] == "casdoor_oauth":
            answer = self.http.call("userinfo", actor=self.profile["actor"]["name"],
                                    headers={"Authorization": "Bearer " + material["native"]["access_token"]}, context=context)
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
        if kind in {"issue", "refresh"} and self.profile.get("identifier_journal"):
            self.identifier_log.emit("verified_native_identifier", **{key: result[key] for key in
                ("rid", "digest", "origin", "attempt_id", "release_version")},
                native_unit_id=result_material["derived"]["verified_claims"]["jti"],
                verified_account=result_material["expected_account"], verified_client=result_material["client"],
                native_sequence=answer["sequence"])
            if kind == "refresh" and self.profile.get("hold_after_identifier"):
                path = self.root / "provider" / "identifier_ready.json"
                write_json(path, {**context, "position": "identifier durable, response delivery held"})
                while not path.with_suffix(".release").exists():
                    time.sleep(0.01)
        if kind == "refresh" and self.profile.get("hold_response_without_identifiers"):
            path = self.root / "provider" / "response_ready_without_identifiers.json"
            write_json(path, {**context, "position": "response withheld; no operational body or identifier retained"})
            while not path.with_suffix(".release").exists():
                time.sleep(0.01)
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

    def reconcile_query(self, payload):
        if self.profile.get("query_mode") == "AUTHORIZED_SCOPE_ENUMERATION":
            return self.reconcile_enumeration(payload)
        exact_fields(payload, ("rid", "digest", "origin", "attempt_id", "release_version"))
        with sqlite3.connect("file:" + str(self.budget_path) + "?mode=ro", uri=True) as con:
            sends = con.execute("SELECT COUNT(*) FROM requests WHERE category='method' AND operation='refresh' AND attempt_id=? AND rid=? AND request_digest=? AND actor=?",
                                (payload["attempt_id"], payload["rid"], payload["digest"], self.profile["actor"]["name"])).fetchone()[0]
        evidence = {"actual_sends": sends, "query_kind": "none", "record_found": False,
                    "exact_authorized_read": False, "origin_bound": False, "observed_distinct_effects": 0}
        path = self.identifier_log.path
        entries = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
        matches = [row for row in entries if all(row.get(key) == payload[key] for key in payload)]
        if sends != 1 or len(matches) != 1:
            return {"status": "UNKNOWN", "reason": "NO_UNIQUE_TRUSTED_IDENTIFIER_OR_SEND", "evidence": evidence,
                    "unsafe_account_listing_sent": False}
        metadata = matches[0]
        unit = metadata["native_unit_id"]
        if metadata["verified_account"] != self.profile["actor"]["id"] or metadata["verified_client"] != self.profile["client_id"]:
            return {"status": "UNKNOWN", "reason": "IDENTIFIER_SCOPE_MISMATCH", "evidence": evidence}
        basic = base64.b64encode((self.profile["client_id"] + ":" + self.profile["client_secret"]).encode()).decode()
        response = self.http.call("get_token", actor=self.profile["actor"]["name"], payload={"id": unit},
                                  headers={"Authorization": "Basic " + basic}, context={**payload, "verified_unit_id": unit})
        evidence.update(query_kind="exact_primary_key", exact_authorized_read=True,
                        identifier_receipt_ref=digest(metadata), native_unit_id=unit,
                        identifier_receipt=metadata, query_ref="native-http-" + str(response["sequence"]))
        row = response["body"].get("data") if response["http"] == 200 else None
        if not isinstance(row, dict):
            return {"status": "UNKNOWN", "reason": "EXACT_POINT_READ_UNAVAILABLE", "evidence": evidence}
        if (row.get("owner", "") + "/" + row.get("name", "") != unit
                or row.get("organization") != "l1-study" or row.get("user") != self.profile["actor"]["name"]
                or row.get("application") != "app-l1-0"):
            return {"status": "UNKNOWN", "reason": "NATIVE_ROW_SCOPE_CONFLICT", "evidence": evidence}
        body = {dst: row.get(src) for dst, src in [("access_token", "accessToken"), ("refresh_token", "refreshToken"),
                ("id_token", "idToken"), ("token_type", "tokenType"), ("scope", "scope"), ("expires_in", "expiresIn")]}
        material = token_bundle(body, self.profile)
        if material["derived"]["verified_claims"]["jti"] != unit:
            return {"status": "UNKNOWN", "reason": "POINT_ID_CLAIM_CONFLICT", "evidence": evidence}
        evidence.update(record_found=True, origin_bound=True, observed_distinct_effects=1)
        return {"status": "RECONCILED_MATERIAL", "evidence": evidence,
                "result": {**payload, "material": material, "outcome": "OK"}}

    def reconcile_enumeration(self, payload):
        exact_fields(payload, ("rid", "digest", "origin", "attempt_id", "release_version", "enumeration_context"))
        known = payload["enumeration_context"]
        with sqlite3.connect("file:" + str(self.budget_path) + "?mode=ro", uri=True) as con:
            sends = con.execute("SELECT COUNT(*) FROM requests WHERE category='method' AND operation='refresh' AND attempt_id=? AND rid=? AND request_digest=? AND actor=?",
                (payload["attempt_id"], payload["rid"], payload["digest"], self.profile["actor"]["name"])).fetchone()[0]
        basic = base64.b64encode((self.profile["client_id"] + ":" + self.profile["client_secret"]).encode()).decode()
        context = {key: payload[key] for key in ("rid", "digest", "attempt_id")}
        answer = self.http.call("get_tokens", actor=self.profile["actor"]["name"],
                                headers={"Authorization": "Basic " + basic}, context=context)
        rows = answer["body"].get("data") if answer["http"] == 200 else None
        if not isinstance(rows, list) or answer["error_type"]:
            return {"status": "UNKNOWN", "reason": "AUTHORIZED_ENUMERATION_UNAVAILABLE", "evidence": {"actual_sends": sends}}
        try:
            evidence = analyze(rows, self.profile["organization"], self.profile["application_name"], self.profile["actor"]["name"],
                self.http.policy["account_names"], known["known_unit_ids"], self.http.policy["page_size"], self.http.policy["record_upper_bound"],
                known["unknown_creators"] == [payload["rid"]], known["account_grant_count"] == 2 and known["account_budget_total"] == 20, sends)
        except ScopeViolation:
            return {"status": "SAFETY_FAILURE", "reason": "QUERY_SCOPE_ESCAPED"}
        evidence.update(query_ref="native-http-" + str(answer["sequence"]), enumeration_ref=digest(rows),
            authorized_scope_ref=digest({"organization": self.profile["organization"], "scope": "ALL_TOKEN_RECORDS"}),
            input_context=known, input_context_ref=digest(known), query_evidence_schema="native-enumeration-observation/2",
            native_reported_count=answer["body"].get("data2"), returned_record_count=len(rows), native_reported_page_count=None)
        if not evidence["origin_bound"]:
            return {"status": "UNKNOWN", "reason": "COLLECTION_OR_ATTRIBUTION_UNRESOLVED", "evidence": evidence}
        selected = next(row for row in rows if row["owner"] + "/" + row["name"] == evidence["selected_unit_id"])
        body = {dst: selected.get(src) for dst, src in [("access_token", "accessToken"), ("refresh_token", "refreshToken"),
            ("id_token", "idToken"), ("token_type", "tokenType"), ("scope", "scope"), ("expires_in", "expiresIn")]}
        material = token_bundle(body, self.profile)
        if material["derived"]["verified_claims"]["jti"] != evidence["selected_unit_id"]:
            return {"status": "UNKNOWN", "reason": "ENUMERATED_UNIT_CLAIM_CONFLICT", "evidence": evidence}
        result = {key: payload[key] for key in ("rid", "digest", "origin", "attempt_id", "release_version")}
        return {"status": "RECONCILED_MATERIAL", "evidence": evidence, "result": {**result, "material": material, "outcome": "OK"}}
