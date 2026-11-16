"""Append-only, hash-chained, secret-free experimental events."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import threading
import time

SECRET_KEYS = {"access_token", "refresh_token", "id_token", "password", "client_secret", "clientSecret", "authorization", "cookie", "set-cookie", "secret"}


def canonical(value):return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
def fingerprint(value):return sha256(str(value).encode()).hexdigest()


def redact(value):
    if isinstance(value, dict):return {k: {"sha256_ref": fingerprint(v)} if k.lower() in {s.lower() for s in SECRET_KEYS} else redact(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):return [redact(x) for x in value]
    if isinstance(value, str) and value.startswith("eyJ") and value.count(".") == 2:return {"jwt_ref": fingerprint(value)}
    return value


class Journal:
    def __init__(self, path, metadata):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open("x", encoding="utf-8"); self.metadata = metadata
        self.previous = "0" * 64; self.seq = 0; self.lock = threading.Lock()

    def emit(self, event, role="method", **payload):
        with self.lock:
            row = {"schema": "auth-study-event/1", "run_id": self.metadata["run_id"], "seq": self.seq,
                   "utc": datetime.now(timezone.utc).isoformat(), "monotonic_ns": time.monotonic_ns(),
                   "event": event, "role": role, "payload": redact(payload), "previous_sha256": self.previous}
            row["sha256"] = fingerprint(canonical(row)); self.previous = row["sha256"]; self.seq += 1
            self.stream.write(canonical(row) + "\n"); self.stream.flush()
            return row

    def close(self):self.stream.close()


def read_verified(path):
    previous = "0" * 64; result = []
    for seq, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines()):
        row = json.loads(line); claimed = row.pop("sha256")
        if (row.get("schema")!="auth-study-event/1" or type(row.get("seq")) is not int or type(row.get("monotonic_ns")) is not int
            or not isinstance(row.get("payload"),dict) or row.get("role") not in {"method","fixture","fault","transport","witness","resource","scorer","recovery"}):
            raise ValueError("event schema mismatch")
        if row["seq"] != seq or row["previous_sha256"] != previous or fingerprint(canonical(row)) != claimed:raise ValueError("event chain mismatch")
        row["sha256"] = claimed; previous = claimed; result.append(row)
    return result


class BudgetDenied(RuntimeError):pass
class ApprovalDenied(RuntimeError):pass
class ResponseLost(RuntimeError):pass


class Gate:
    """Same permission/budget gate for every method. Scorer never supplies decisions."""
    def __init__(self, journal, cap=64, approvals=8, fault="none"):
        self.journal = journal; self.cap = cap; self.approval_cap = approvals; self.sent = 0; self.charged_approvals = 0
        self.allowed = {"configure", "probe", "stop", "cleanup", "refresh"}; self.lock = threading.RLock()
        self.fault = fault; self.triggered = False; self.private_effects = []
        self.on_credential = None
        self.uncertain_creation_requests=0

    def call(self, operation, dispatch, *, approval_charge=0, endpoint_class="native_auth"):
        with self.lock:
            self.journal.emit("proposal", operation=operation)
            if self.fault == "approval_withdrawal" and operation == "stop" and not self.triggered:
                self.allowed.discard("stop"); self.triggered = True
                self.journal.emit("fault_triggered", "fault", fault=self.fault, point="before_final_approval_check")
            if operation not in self.allowed:
                self.journal.emit("approval_denied", operation=operation); raise ApprovalDenied(operation)
            if self.sent >= self.cap or self.charged_approvals + approval_charge > self.approval_cap:
                self.journal.emit("budget_denied", operation=operation); raise BudgetDenied(operation)
            self.charged_approvals += approval_charge; self.sent += 1; request_id = self.sent
            self.journal.emit("request_sent", operation=operation, request_id=request_id, counted=True, approval_charge=approval_charge,endpoint_class=endpoint_class)
        start = time.perf_counter()
        try:response = dispatch()
        except Exception as error:
            self.journal.emit("transport_unknown", operation=operation, request_id=request_id, error_type=type(error).__name__)
            if operation in {"configure","refresh"}:
                self.uncertain_creation_requests+=1
                self.journal.emit("obligation_created",kind="unresolved_inflight_creation",request_id=request_id)
            raise
        body = response.get("body", {})
        self.journal.emit("native_response" if endpoint_class=="native_auth" else "resource_response", "transport", operation=operation, request_id=request_id,endpoint_class=endpoint_class,
                          http_status=response["http"], elapsed_seconds=time.perf_counter()-start,
                          error=body.get("error"), active=body.get("active"))
        if body.get("access_token"):
            self.private_effects.append(body)  # scorer-only observer, never returned after loss
            native_unit=None
            if self.on_credential:
                try:native_unit=self.on_credential(body)
                except Exception as error:self.journal.emit("native_unit_witness_failed","witness",error_type=type(error).__name__,request_id=request_id)
            self.journal.emit("credential_created", "witness", request_id=request_id, credential_ref=fingerprint(body["access_token"]),native_unit_ref=native_unit)
        if self.fault == "response_loss" and operation == "configure" and response["http"] == 200 and body.get("access_token") and not self.triggered:
            self.triggered = True
            self.journal.emit("fault_triggered", "fault", fault=self.fault, point="native_response_received_before_method_receipt", request_id=request_id)
            self.journal.emit("obligation_created", kind="unknown_handle_after_loss", request_id=request_id)
            raise ResponseLost("native response withheld; outcome unknown to method")
        return response

    def transport(self, operation, dispatch):return self.call(operation, dispatch, approval_charge=int(operation == "configure"))
