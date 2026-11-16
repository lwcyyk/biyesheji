"""SQLite authority. All approval mutations share one BEGIN IMMEDIATE order.

The small prototype stores one encrypted application snapshot per commit. Its
linear serialization cost is explicit; the SQL transaction and event are atomic.
"""

import base64
import json
import os
from pathlib import Path
import secrets
import sqlite3
import threading

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .protocol import (EventLog, InvalidInput, canonical, digest, exact_fields,
                       identifier, normalized_request)


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
    return {"approvals": approvals, "requests": requests, "obligations": obligations}


class AuthorityStore:
    def __init__(self, directory, key_path, operation_limit=None):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.key_path = Path(key_path)
        self.lock = threading.RLock()
        self.metrics = EventLog(self.directory / "database_ops.jsonl")
        self.operation_limit = operation_limit
        self.operations = 0
        if self.metrics.path.exists():
            self.operations = len(self.metrics.path.read_bytes().splitlines())
        self.connection = sqlite3.connect(self.directory / "authority.db",
                                          isolation_level=None, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.execute("PRAGMA journal_mode=WAL")
        self.execute("PRAGMA synchronous=FULL")
        self.execute("PRAGMA busy_timeout=5000")
        migration = (Path(__file__).with_name("migration.sql")).read_text()
        for statement in migration.split(";"):
            if statement.strip():
                self.execute(statement)
        row = self.execute("SELECT version FROM authority_state WHERE id=1").fetchone()
        if row is None:
            state = {"grants": {}, "requests": {}, "grant_ops": {}, "revoke_ops": {}}
            self.execute("INSERT INTO authority_state VALUES(1,0,?)", (self.encrypt(state),))

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
        if operation not in {"grant", "admit", "release", "record", "revoke", "recover"}:
            return {"status": "REJECTED", "reason": "INVALID_OPERATION"}
        with self.lock:
            try:
                if operation == "recover":
                    version, state = self.read_state()
                    return {"status": "RECOVERED", "version": version, **state_projection(state)}
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
        if not isinstance(payload["material"], str) or not 1 <= len(payload["material"]) <= 4096:
            raise InvalidInput("INVALID_MATERIAL")
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
        req["attempt_id"] = "attempt_" + secrets.token_hex(16)
        req["release_version"] = version
        req["phase"] = "DISPATCHED_UNKNOWN"
        grant["reserved"] -= 1
        grant["spent"] += 1
        return {"status": "RELEASED", "send": True, **request_projection(req),
                "operation": req["request"]["operation"], "payload": req["request"]["payload"],
                "material": grant["material"]}

    def record(self, state, payload, version):
        fields = ("rid", "digest", "origin", "attempt_id", "release_version", "material", "outcome")
        exact_fields(payload, fields)
        req = state["requests"].get(payload["rid"])
        if req is None or any(req[key] != payload[key] for key in
                              ("digest", "origin", "attempt_id", "release_version")):
            return {"status": "CONFLICT", "reason": "RESULT_SOURCE_CONFLICT"}
        if payload["outcome"] != "OK" or not isinstance(payload["material"], str) or not 1 <= len(payload["material"]) <= 4096:
            raise InvalidInput("INVALID_RESULT")
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
