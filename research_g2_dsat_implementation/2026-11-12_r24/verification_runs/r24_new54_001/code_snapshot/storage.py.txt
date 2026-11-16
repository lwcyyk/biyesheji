"""SQLite authority. All approval mutations share one BEGIN IMMEDIATE order.

The small prototype stores one encrypted application snapshot per commit. Its
linear serialization cost is explicit; the SQL transaction and event are atomic.
"""

import json
import os
from pathlib import Path
import secrets
import sqlite3
import threading

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .protocol import (EventLog, InvalidInput, canonical, digest, exact_fields,
                       identifier, normalized_request, write_json)
from .materials import validate_material


AAD = b"auth-lifecycle/online-state/schema-1"


def request_projection(request):
    return {key: request[key] for key in
            ("rid", "digest", "origin", "phase", "attempt_id", "release_version")}


def state_projection(state):
    approvals = []
    for grant in state["grants"].values():
        approvals.append({key: grant[key] for key in
                          ("grant_id", "caller", "task", "account", "audience",
                           "generation", "active", "limit", "reserved", "spent")})
    requests = [request_projection(req) for req in state["requests"].values()]
    obligations = [req["rid"] for req in requests
                   if req["phase"] in {"DISPATCHED_UNKNOWN", "QUARANTINED"}]
    for window in state.get("reconciliation_windows", {}).values():
        if window.get("receipt", {}).get("claim") != "CLOSED" and window["target_rid"] not in obligations:
            obligations.append(window["target_rid"])
    disposals = [{"disposal_op": key, **value} for key, value in state.get("disposals", {}).items()]
    return {"approvals": approvals, "requests": requests, "obligations": obligations,
            "disposals": disposals}


class AuthorityStore:
    def __init__(self, directory, key_path, operation_limit=None, *, bootstrap_context=None):
        if bootstrap_context is not None:
            from .dsat_authority_lifecycle import construct_preseeded_store
            construct_preseeded_store(self, bootstrap_context, directory, key_path, operation_limit)
            return
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.key_path = Path(key_path)
        self.lock = threading.RLock()
        self.metrics = EventLog(self.directory / "database_ops.jsonl")
        self.operation_limit = operation_limit
        self.operations = 0
        if self.metrics.path.exists():
            self.operations = len(self.metrics.path.read_bytes().splitlines())
        marker = self.directory / "initialized"
        if marker.exists() and not (self.directory / "authority.db").exists():
            raise ValueError("EXISTING_AUTHORITY_DATA_MISSING")
        self.connection = sqlite3.connect(self.directory / "authority.db",
                                          isolation_level=None, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        journal_mode = self.execute("PRAGMA journal_mode=WAL").fetchone()[0]
        self.execute("PRAGMA synchronous=FULL")
        synchronous = self.execute("PRAGMA synchronous").fetchone()[0]
        self.execute("PRAGMA busy_timeout=5000")
        self.execute("PRAGMA wal_autocheckpoint=1000")
        if journal_mode != "wal" or synchronous != 2:
            raise ValueError("DURABILITY_CONFIGURATION_MISMATCH")
        schema_version = self.execute("PRAGMA user_version").fetchone()[0]
        if schema_version not in {0, 1, 2}:
            raise ValueError("UNSUPPORTED_SCHEMA_VERSION")
        if schema_version == 0:
            migration = (Path(__file__).with_name("migration.sql")).read_text()
            for statement in migration.split(";"):
                if statement.strip():
                    self.execute(statement)
        if schema_version < 2:
            self.execute(Path(__file__).with_name("migration_2.sql").read_text())
        row = self.execute("SELECT version FROM authority_state WHERE id=1").fetchone()
        if row is None:
            if marker.exists():
                raise ValueError("EXISTING_AUTHORITY_STATE_MISSING")
            state = {"grants": {}, "requests": {}, "grant_ops": {}, "revoke_ops": {}}
            self.execute("INSERT INTO authority_state VALUES(1,0,?)", (self.encrypt(state),))
        marker.touch(exist_ok=True)
        write_json(self.directory / "storage_configuration.json", {
            "sqlite_version": sqlite3.sqlite_version, "journal_mode": journal_mode,
            "synchronous": synchronous, "busy_timeout_ms": 5000,
            "wal_autocheckpoint_pages": 1000, "mutation_transaction": "BEGIN IMMEDIATE",
            "application_snapshot": "single AES-GCM encrypted row", "schema_version": 2})

    def execute(self, statement, parameters=()):
        if self.operation_limit is not None and self.operations >= self.operation_limit:
            raise RuntimeError("DATABASE_OPERATION_BUDGET")
        self.operations += 1
        kind = statement.strip().split()[0].upper()
        size = sum(len(x) if isinstance(x, (bytes, str)) else 8 for x in parameters)
        self.metrics.emit("sqlite_statement", number=self.operations, kind=kind,
                          bound_value_bytes=size)
        return self.connection.execute(statement, parameters)

    def cipher(self):
        # Reloading the external key makes a missing recovery key fail closed.
        key = self.key_path.read_bytes()
        if len(key) != 32:
            raise ValueError("KEY_UNAVAILABLE")
        return AESGCM(key)

    def encrypt(self, state):
        nonce = os.urandom(12)
        return nonce + self.cipher().encrypt(nonce, canonical(state), AAD)

    def read_state(self):
        row = self.execute("SELECT version,ciphertext FROM authority_state WHERE id=1").fetchone()
        if row is None:
            raise ValueError("STATE_UNAVAILABLE")
        raw = bytes(row["ciphertext"])
        state = json.loads(self.cipher().decrypt(raw[:12], raw[12:], AAD))
        return row["version"], state

    def call(self, operation, payload):
        if operation not in {"grant", "admit", "release", "record", "revoke", "recover",
                             "prepare_disposal", "record_disposal"}:
            if operation not in {"begin_reconciliation", "reconciliation_context", "save_reconciliation"}:
                return {"status": "REJECTED", "reason": "INVALID_OPERATION"}
        with self.lock:
            try:
                if operation == "recover":
                    if self.operation_limit is not None and self.operations >= self.operation_limit:
                        return {"status": "INCONCLUSIVE", "reason": "DATABASE_OPERATION_BUDGET"}
                    version, state = self.read_state()
                    return {"status": "RECOVERED", "version": version, **state_projection(state)}
                if self.operation_limit is not None and self.operations + 6 > self.operation_limit:
                    return {"status": "INCONCLUSIVE", "reason": "DATABASE_OPERATION_BUDGET"}
                self.execute("BEGIN IMMEDIATE")
                version, state = self.read_state()
                result = getattr(self, operation)(state, payload, version + 1)
                public = {key: result[key] for key in
                          ("status", "reason", "rid", "grant_id", "phase", "send") if key in result}
                event = {"result": public, "state": state_projection(state),
                         "logical_state_bytes": len(canonical(state))}
                self.execute("UPDATE authority_state SET version=?,ciphertext=? WHERE id=1",
                             (version + 1, self.encrypt(state)))
                self.execute("INSERT INTO authority_events VALUES(?,?,?)",
                             (version + 1, operation, canonical(event).decode()))
                self.execute("COMMIT")
                return {**result, "version": version + 1}
            except InvalidInput:
                if self.connection.in_transaction:
                    self.execute("ROLLBACK")
                return {"status": "REJECTED", "reason": "INVALID_INPUT"}
            except Exception:
                if self.connection.in_transaction:
                    # A budget exhaustion must still release the DB transaction.
                    self.connection.rollback()
                    self.operations += 1
                    self.metrics.emit("sqlite_rollback_cleanup", kind="ROLLBACK")
                return {"status": "UNKNOWN", "reason": "AUTHORITY_STATE_UNAVAILABLE"}

    def grant(self, state, payload, version):
        fields = ("approval_op", "caller", "task", "account", "audience",
                  "generation", "operations", "budget", "material")
        exact_fields(payload, fields)
        for key in fields:
            if key not in {"operations", "budget", "material"}:
                identifier(payload[key])
        if (type(payload["budget"]) is not int or not 0 <= payload["budget"] <= 1000000
                or not isinstance(payload["operations"], list) or not payload["operations"]
                or len(payload["operations"]) != len(set(payload["operations"]))):
            raise InvalidInput("INVALID_APPROVAL")
        for operation in payload["operations"]:
            identifier(operation)
        validate_material(payload["material"], payload["account"], payload["audience"])
        if state.get("reconciliation_windows", {}).get(payload["account"], {}).get("active"):
            return {"status": "REJECTED", "reason": "RECONCILIATION_CREATION_PAUSED"}
        fingerprint = digest(payload)
        old = state["grant_ops"].get(payload["approval_op"])
        if old:
            if old["digest"] != fingerprint:
                return {"status": "CONFLICT", "reason": "APPROVAL_OPERATION_CONFLICT"}
            grant = state["grants"][old["grant_id"]]
            return {"status": "GRANTED", "grant_id": grant["grant_id"], "handle": grant["handle"]}
        for grant in state["grants"].values():
            scope = ("caller", "task", "account", "audience", "generation")
            if all(grant[key] == payload[key] for key in scope):
                return {"status": "CONFLICT", "reason": "GENERATION_ALREADY_EXISTS"}
        grant_id = "grant_" + secrets.token_hex(12)
        handle = "handle_" + secrets.token_hex(24)
        state["grants"][grant_id] = {
            **{key: payload[key] for key in ("caller", "task", "account", "audience", "generation", "operations", "material")},
            "grant_id": grant_id, "handle": handle, "active": True,
            "limit": payload["budget"], "reserved": 0, "spent": 0}
        state["grant_ops"][payload["approval_op"]] = {"digest": fingerprint, "grant_id": grant_id}
        return {"status": "GRANTED", "grant_id": grant_id, "handle": handle}

    def admit(self, state, payload, version):
        exact_fields(payload, ("caller", "request"))
        caller = identifier(payload["caller"])
        request = normalized_request(payload["request"])
        fingerprint = digest({"caller": caller, "request": request})
        existing = state["requests"].get(request["rid"])
        if existing:
            if existing["digest"] != fingerprint:
                return {"status": "CONFLICT", "reason": "RID_BODY_CONFLICT"}
            return {"status": "DUPLICATE", **request_projection(existing)}
        grant = next((g for g in state["grants"].values() if g["handle"] == request["handle"]), None)
        if grant is None or grant["caller"] != caller:
            return {"status": "REJECTED", "reason": "BINDING_MISMATCH"}
        if any(grant[key] != request[key] for key in ("task", "account", "audience", "generation")):
            return {"status": "REJECTED", "reason": "BINDING_MISMATCH"}
        if not grant["active"] or request["operation"] not in grant["operations"]:
            return {"status": "REJECTED", "reason": "APPROVAL_INACTIVE_OR_OPERATION_DENIED"}
        if request["operation"] in {"issue", "refresh"} and state.get("reconciliation_windows", {}).get(request["account"], {}).get("active"):
            return {"status": "REJECTED", "reason": "RECONCILIATION_CREATION_PAUSED"}
        if grant["reserved"] + grant["spent"] >= grant["limit"]:
            return {"status": "REJECTED", "reason": "BUDGET_EXHAUSTED"}
        origin = {key: grant[key] for key in
                  ("grant_id", "caller", "task", "account", "audience", "generation")}
        saved = {"rid": request["rid"], "digest": fingerprint, "origin": origin,
                 "request": request, "phase": "QUEUED", "attempt_id": None,
                 "release_version": None, "result_digest": None, "result_material": None}
        state["requests"][request["rid"]] = saved
        grant["reserved"] += 1
        return {"status": "ADMITTED", **request_projection(saved)}

    def release(self, state, payload, version):
        exact_fields(payload, ("caller", "rid", "digest"))
        req = state["requests"].get(payload["rid"])
        if req is None or req["origin"]["caller"] != payload["caller"] or req["digest"] != payload["digest"]:
            return {"status": "REJECTED", "reason": "REQUEST_BINDING_MISMATCH", "send": False}
        grant = state["grants"][req["origin"]["grant_id"]]
        if req["phase"] != "QUEUED":
            return {"status": "RECORDED", "send": False, **request_projection(req)}
        if not grant["active"]:
            req["phase"] = "CANCELLED"
            grant["reserved"] -= 1
            return {"status": "REJECTED", "reason": "APPROVAL_REVOKED", "send": False}
        material = grant["material"]
        if req["request"]["operation"] in {"issue", "refresh"} and state.get("reconciliation_windows", {}).get(req["origin"]["account"], {}).get("active"):
            req["phase"] = "CANCELLED"
            grant["reserved"] -= 1
            return {"status": "REJECTED", "reason": "RECONCILIATION_CREATION_PAUSED", "send": False}
        if req["request"]["operation"] in {"refresh", "userinfo"}:
            source = state["requests"].get(req["request"]["payload"]["source_rid"])
            if (source is None or source["origin"] != req["origin"]
                    or source["phase"] != "RESULT_AVAILABLE" or not isinstance(source["result_material"], dict)):
                req["phase"] = "CANCELLED"
                grant["reserved"] -= 1
                return {"status": "REJECTED", "reason": "SOURCE_MATERIAL_UNAVAILABLE", "send": False}
            material = source["result_material"]
        req["attempt_id"] = "attempt_" + secrets.token_hex(16)
        req["release_version"] = version
        req["phase"] = "DISPATCHED_UNKNOWN"
        grant["reserved"] -= 1
        grant["spent"] += 1
        return {"status": "RELEASED", "send": True, **request_projection(req),
                "operation": req["request"]["operation"], "payload": req["request"]["payload"],
                "material": material}

    def record(self, state, payload, version):
        fields = ("rid", "digest", "origin", "attempt_id", "release_version", "material", "outcome")
        exact_fields(payload, fields)
        req = state["requests"].get(payload["rid"])
        if req is None or any(req[key] != payload[key] for key in
                              ("digest", "origin", "attempt_id", "release_version")):
            return {"status": "CONFLICT", "reason": "RESULT_SOURCE_CONFLICT"}
        if payload["outcome"] != "OK":
            raise InvalidInput("INVALID_RESULT")
        validate_material(payload["material"], req["origin"]["account"], req["origin"]["audience"])
        result_digest = digest(payload)
        if req["result_digest"]:
            if req["result_digest"] != result_digest:
                return {"status": "CONFLICT", "reason": "RESULT_BODY_CONFLICT"}
            return {"status": "RESULT_DUPLICATE", **request_projection(req)}
        if req["phase"] != "DISPATCHED_UNKNOWN" or not req["attempt_id"]:
            return {"status": "REJECTED", "reason": "RESULT_WITHOUT_RELEASE"}
        grant = state["grants"][req["origin"]["grant_id"]]
        req["result_digest"] = result_digest
        req["result_material"] = payload["material"]
        req["phase"] = "RESULT_AVAILABLE" if grant["active"] else "QUARANTINED"
        return {"status": req["phase"], **request_projection(req)}

    def revoke(self, state, payload, version):
        exact_fields(payload, ("revoke_op", "grant_id"))
        identifier(payload["revoke_op"])
        identifier(payload["grant_id"])
        old = state["revoke_ops"].get(payload["revoke_op"])
        if old:
            if old["grant_id"] != payload["grant_id"]:
                return {"status": "CONFLICT", "reason": "REVOKE_OPERATION_CONFLICT"}
            return old
        grant = state["grants"].get(payload["grant_id"])
        if grant is None:
            return {"status": "REJECTED", "reason": "UNKNOWN_GRANT"}
        grant["active"] = False
        for req in state["requests"].values():
            if req["origin"]["grant_id"] != grant["grant_id"]:
                continue
            if req["phase"] == "QUEUED":
                req["phase"] = "CANCELLED"
                grant["reserved"] -= 1
            elif req["phase"] == "RESULT_AVAILABLE":
                req["phase"] = "QUARANTINED"
        receipt = {"status": "LOCAL_REVOKE_COMMITTED", "grant_id": grant["grant_id"],
                   "commit_version": version}
        state["revoke_ops"][payload["revoke_op"]] = receipt
        return receipt

    def prepare_disposal(self, state, payload, version):
        exact_fields(payload, ("disposal_op", "rid"))
        identifier(payload["disposal_op"])
        identifier(payload["rid"])
        disposals = state.setdefault("disposals", {})
        existing = disposals.get(payload["disposal_op"])
        if existing:
            if existing["rid"] != payload["rid"]:
                return {"status": "CONFLICT", "reason": "DISPOSAL_ID_CONFLICT"}
            return {"status": existing["phase"], "send": False}
        req = state["requests"].get(payload["rid"])
        if (req is None or req["phase"] != "QUARANTINED"
                or not isinstance(req["result_material"], dict)):
            return {"status": "UNKNOWN", "reason": "NO_KNOWN_QUARANTINED_MATERIAL", "send": False}
        disposals[payload["disposal_op"]] = {"rid": req["rid"], "phase": "DISPOSAL_UNKNOWN",
                                             "origin": req["origin"], "release_version": version}
        return {"status": "DISPOSAL_RELEASED", "send": True, "material": req["result_material"],
                "rid": req["rid"], "disposal_op": payload["disposal_op"], "origin": req["origin"]}

    def record_disposal(self, state, payload, version):
        exact_fields(payload, ("disposal_op", "rid", "http", "userinfo_http", "userinfo_accepted", "introspection_active"))
        item = state.get("disposals", {}).get(payload["disposal_op"])
        if item is None or item["rid"] != payload["rid"]:
            return {"status": "CONFLICT", "reason": "DISPOSAL_SOURCE_CONFLICT"}
        if type(payload["http"]) is not int:
            raise InvalidInput("INVALID_HTTP_STATUS")
        item["phase"] = "NATIVE_REVOKE_RESPONDED"
        item["http"] = payload["http"]
        item["observations"] = {key: payload[key] for key in ("userinfo_http", "userinfo_accepted", "introspection_active")}
        item["completed_version"] = version
        if payload["http"] == 200 and payload["userinfo_accepted"] is False and payload["introspection_active"] is False:
            item["phase"] = "KNOWN_UNIT_INACTIVE"
            state["requests"][item["rid"]]["phase"] = "DISPOSED"
        return {"status": item["phase"], "rid": item["rid"], "http": item["http"],
                "scope": "named_native_material_response_only"}

    def begin_reconciliation(self, state, payload, version):
        exact_fields(payload, ("rid", "window_id"))
        identifier(payload["window_id"])
        req = state["requests"].get(payload["rid"])
        if req is None:
            return {"status": "UNKNOWN", "reason": "UNKNOWN_ATTEMPT"}
        account = req["origin"]["account"]
        windows = state.setdefault("reconciliation_windows", {})
        old = windows.get(account)
        if old:
            if old["window_id"] != payload["window_id"] or old["target_rid"] != payload["rid"]:
                return {"status": "CONFLICT", "reason": "WINDOW_CONFLICT"}
            return {"status": "WINDOW_OPEN", "window": old}
        if req["phase"] != "DISPATCHED_UNKNOWN" or req["request"]["operation"] != "refresh":
            return {"status": "UNKNOWN", "reason": "TARGET_NOT_UNKNOWN_REFRESH"}
        grant = state["grants"][req["origin"]["grant_id"]]
        if grant["active"]:
            return {"status": "REJECTED", "reason": "WITHDRAW_A_FIRST"}
        unknowns = [r["rid"] for r in state["requests"].values() if r["origin"]["account"] == account
                    and r["phase"] == "DISPATCHED_UNKNOWN" and r["request"]["operation"] in {"issue", "refresh"}]
        windows[account] = {"window_id": payload["window_id"], "target_rid": req["rid"],
                            "unknown_creators_at_open": unknowns, "active": True, "opened_version": version}
        return {"status": "WINDOW_OPEN", "window": windows[account]}

    def reconciliation_context(self, state, payload, version):
        exact_fields(payload, ("rid", "window_id", "B_rid"))
        req = state["requests"][payload["rid"]]
        window = state.get("reconciliation_windows", {}).get(req["origin"]["account"])
        if not window or window["window_id"] != payload["window_id"]:
            return {"status": "UNKNOWN", "reason": "WINDOW_UNAVAILABLE"}
        a_rows = [r for r in state["requests"].values() if r["origin"]["grant_id"] == req["origin"]["grant_id"] and r["result_material"]]
        disposals = [d for d in state.get("disposals", {}).values() if d["rid"] in {r["rid"] for r in a_rows}]
        last_disposal = max((d.get("completed_version", 0) for d in disposals), default=0)
        b = state["requests"].get(payload["B_rid"])
        b_ok = bool(b and b["origin"]["account"] == req["origin"]["account"] and b["origin"]["grant_id"] != req["origin"]["grant_id"]
                    and b["request"]["operation"] == "userinfo" and b["phase"] == "RESULT_AVAILABLE"
                    and b["release_version"] > last_disposal and last_disposal > 0
                    and state["grants"][b["origin"]["grant_id"]]["active"])
        account_grants = [g for g in state["grants"].values() if g["account"] == req["origin"]["account"]]
        known_ids = sorted({r["result_material"]["derived"]["verified_claims"]["jti"]
            for r in state["requests"].values() if r["origin"]["account"] == req["origin"]["account"]
            and isinstance(r["result_material"], dict) and r["result_material"].get("kind") == "casdoor_oauth"
            and r["result_material"].get("derived", {}).get("verified_claims", {}).get("jti")})
        return {"status": "RECONCILIATION_CONTEXT", "window": window, "target": request_projection(req),
                "A_revoked": not state["grants"][req["origin"]["grant_id"]]["active"],
                "known_A_rids": [r["rid"] for r in a_rows],
                "known_A_units_inactive": bool(a_rows) and all(r["phase"] == "DISPOSED" for r in a_rows),
                "B_preserved_after_disposal": b_ok, "disposition_versions": [d.get("completed_version") for d in disposals],
                "known_unit_ids": known_ids, "account_grant_count": len(account_grants),
                "account_budget_total": sum(g["limit"] for g in account_grants)}

    def save_reconciliation(self, state, payload, version):
        exact_fields(payload, ("rid", "window_id", "receipt", "query_evidence", "B_rid"))
        req = state["requests"][payload["rid"]]
        window = state.get("reconciliation_windows", {}).get(req["origin"]["account"])
        if not window or window["window_id"] != payload["window_id"]:
            return {"status": "CONFLICT", "reason": "WINDOW_MISMATCH"}
        receipt = payload["receipt"]
        if receipt["claim"] == "CLOSED":
            context = self.reconciliation_context(state, {"rid": payload["rid"], "window_id": payload["window_id"], "B_rid": payload["B_rid"]}, version)
            if (req["phase"] != "DISPOSED" or not window["active"] or not context["known_A_units_inactive"]
                    or not context["B_preserved_after_disposal"] or not context["A_revoked"]
                    or window["unknown_creators_at_open"] != [payload["rid"]]
                    or receipt["target"]["attempt_id"] != req["attempt_id"]
                    or receipt["target"]["request_digest"] != req["digest"]):
                return {"status": "UNKNOWN", "reason": "CLOSE_STATE_MISMATCH"}
        window["receipt"] = receipt
        window["query_evidence"] = payload["query_evidence"]
        if receipt["claim"] == "CLOSED":window["active"] = False
        return {"status": receipt["claim"], "receipt": receipt, "receipt_ref": digest(receipt)}
