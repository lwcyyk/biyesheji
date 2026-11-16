"""Typed R21 offline admission, stable source binding and dormant host ownership.

Deployment admission and H2 activation remain separate closed gates. The
capabilities below only exist after actual owned Windows test facts are checked.
"""
import hashlib
import json
from pathlib import Path
import secrets
import threading
import weakref
import os
import re

from .dsat_windows_runtime import (SafetyError, require, TestScope, validate_host_evidence,
                                  validate_lease)
from . import dsat_windows_runtime as win
from .protocol import strict_json, canonical


_ISSUERS, _CONTEXTS = weakref.WeakKeyDictionary(), weakref.WeakKeyDictionary()
_START_APPROVALS = weakref.WeakKeyDictionary()
_NAMESPACE_LOCK = threading.RLock()
_LIFECYCLE_NAMESPACES = {}
ENVIRONMENT = "h2-authority-synth-001"
SCOPE = {"account": "h2_account_001", "audience": "h2_audience_001", "tasks": ["h2_task_001"],
         "callers": ["h2_agent_001"], "generations": ["h2_gen_001"]}
GAPS = ["SOURCE_OR_REFINEMENT_GAP", "TYPED_O_NOT_IMPLEMENTED", "O_REVISION_NOT_IMPLEMENTED",
        "P1_NOT_AUTHORIZED", "P2_NOT_AUTHORIZED", "REAL_DEPLOYMENT_NOT_RUN"]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def effective_config_digest(scope, root):
    require(type(scope) is TestScope)
    return digest({"environment_id": ENVIRONMENT, "root": str(scope.path(root)), "source": scope.source_digest,
                   "scope": SCOPE, "P2": False, "port": 27443, "TLS": True})


class _Capability:
    __slots__ = ("__weakref__",)

    def __init__(self, *args, **kwargs):
        raise SafetyError("CONTEXT_REQUIRED")

    def __repr__(self):
        return "<DormantAuthorityCapability redacted>"

    def __reduce_ex__(self, protocol):
        raise TypeError("LIVE_CAPABILITY_NOT_SERIALIZABLE")


class LiveDeploymentIssuer(_Capability):
    @classmethod
    def for_owned_test(cls, scope, evidence, *, expected_source_digest=None, expected_SID=None):
        require(type(scope) is TestScope)
        facts = validate_host_evidence(evidence, scope)
        if expected_source_digest is not None:
            require(expected_source_digest == scope.source_digest, "SOURCE_MISMATCH")
        if expected_SID is not None:
            require(expected_SID == facts["SID"], "IDENTITY_MISMATCH")
        obj = object.__new__(cls)
        _ISSUERS[obj] = {"scope": scope, "facts": facts, "retired": False}
        return obj

    def bind_instance(self, root, lease, instance_record, *, authorization_id):
        rec = _ISSUERS.get(self)
        require(rec is not None and not rec["retired"])
        require(type(authorization_id) is str and 1 <= len(authorization_id) <= 160)
        scope = rec["scope"]
        facts = validate_lease(lease, scope, root)
        require(type(instance_record) is dict and set(instance_record) == {"schema", "environment_id", "instance_id", "root_facts", "source_digest", "config_digest", "approved_scope"}, "IDENTITY_MISMATCH")
        require(instance_record["schema"] == "r21-owned-instance/1" and instance_record["environment_id"] == ENVIRONMENT
            and instance_record["root_facts"] == facts["root_facts"] and instance_record["source_digest"] == scope.source_digest
            and instance_record["approved_scope"] == SCOPE, "IDENTITY_MISMATCH")
        require(type(instance_record["instance_id"]) is str and len(instance_record["instance_id"]) == 64
            and type(instance_record["config_digest"]) is str and len(instance_record["config_digest"]) == 64, "IDENTITY_MISMATCH")
        require(instance_record["config_digest"] == effective_config_digest(scope, root), "SOURCE_MISMATCH")
        approval = load_start_approval(scope, root, instance_record, authorization_id, lease)
        history = read_consumption(approval, lease)
        require(history[-1]["state"] == "UNCLAIMED", "REPLAY")
        validate_marker(scope, root, instance_record, {"PREPARED", "SEED_READY", "STOPPED"})
        # Keep physical root identity and authorization identity, independent of
        # issuer objects and display/source aliases. A closed namespace stays used.
        key = (facts["root_facts"]["volume"], facts["root_facts"]["file_id"], authorization_id)
        with _NAMESPACE_LOCK:
            require(key not in _LIFECYCLE_NAMESPACES, "REPLAY")
            require(len(_LIFECYCLE_NAMESPACES) < 4096, "RESOURCE_LIMIT")
            obj = object.__new__(LiveAuthorityContext)
            epoch = _START_APPROVALS[approval]["body"]["process_epoch"]
            _CONTEXTS[obj] = {"issuer": self, "scope": scope, "root": Path(root), "lease": lease,
                "lease_facts": facts, "instance": json.loads(json.dumps(instance_record)), "authorization_id": authorization_id,
                "epoch": epoch, "facts": dict(rec["facts"]), "store": None, "connection": None, "lock": None,
                "DB_facts": None, "closed": False, "bound": False, "registrations": 0,
                "source_reads": 0, "permits": 0, "start_claimed": False, "approval": approval}
            _LIFECYCLE_NAMESPACES[key] = obj
            return obj

    def retire(self):
        rec = _ISSUERS.get(self)
        require(rec is not None)
        rec["retired"] = True


class LiveAuthorityContext(_Capability):
    def _record(self):
        rec = _CONTEXTS.get(self)
        require(rec is not None)
        require(not rec["closed"], "STALE_EPOCH")
        require(not _ISSUERS[rec["issuer"]]["retired"], "STALE_EPOCH")
        rec["scope"].sources()
        require(validate_lease(rec["lease"], rec["scope"], rec["root"]) == rec["lease_facts"], "OWNERSHIP_UNPROVEN")
        return rec

    @property
    def epoch(self):
        return self._record()["epoch"]

    @property
    def scope(self):
        return self._record()["scope"]

    @property
    def root(self):
        return self._record()["root"]

    def claim_start(self, expected_epoch):
        rec = self._record()
        with _NAMESPACE_LOCK:
            require(expected_epoch == rec["epoch"], "STALE_EPOCH")
            require(not rec["start_claimed"], "REPLAY")
            consume_start_approval(rec["approval"], rec["lease"], expected_epoch)
            rec["start_claimed"] = True

    def note_started(self, control_name=None):
        rec = self._record()
        transition_consumption(rec["approval"], rec["lease"], "STARTED")
        write_marker(rec["scope"], rec["root"], rec["instance"], "SERVICE_READY",
            authorization_id=rec["authorization_id"], epoch=rec["epoch"], owner=rec["facts"], control_name=control_name)

    def finish_approval(self, *, successful):
        rec = _CONTEXTS.get(self)
        require(rec is not None)
        if rec["start_claimed"]:
            finish_start_approval(rec["approval"], rec["lease"], successful=successful)
            write_marker(rec["scope"], rec["root"], rec["instance"], "STOPPED" if successful else "RECOVERY_REQUIRED",
                authorization_id=rec["authorization_id"], epoch=rec["epoch"], owner=rec["facts"])

    def bind_dormant_store(self, store, expected_store, DB_path=None):
        rec = self._record()
        require(rec["start_claimed"] and not rec["bound"], "REPLAY")
        require(store is expected_store and hasattr(store, "connection") and hasattr(store, "lock"), "IDENTITY_MISMATCH")
        if DB_path is not None:
            rec["DB_facts"] = rec["scope"].file_facts(DB_path)
        rec.update(store=store, connection=store.connection, lock=store.lock, bound=True, registrations=1)

    def check_store(self, store):
        rec = self._record()
        require(rec["bound"] and store is rec["store"] and store.connection is rec["connection"]
                and store.lock is rec["lock"], "IDENTITY_MISMATCH")
        return True

    def check_epoch(self, epoch):
        require(epoch == self._record()["epoch"], "STALE_EPOCH")

    def validate_service_entry(self, role, root):
        self._record()
        # No D1-B2 issuer or production process admission is shipped in R21.
        raise SafetyError("OFFLINE_ONLY")

    def issue_permit(self):
        self._record()
        raise SafetyError("P2_NOT_AUTHORIZED")

    read_state = issue_permit

    def retire(self):
        rec = _CONTEXTS.get(self)
        require(rec is not None)
        rec["closed"] = True

    def metadata(self):
        rec = self._record()
        if rec["bound"]:
            self.check_store(rec["store"])
        return {"schema": "r21-dormant-context/1", "source_kind": "OWNED_OFFLINE_TEST",
            "environment_id": ENVIRONMENT, "instance_id": rec["instance"]["instance_id"],
            "source_digest": rec["scope"].source_digest, "config_digest": rec["instance"]["config_digest"],
            "process": dict(rec["facts"]), "process_epoch": rec["epoch"], "authorization_id": rec["authorization_id"],
            "scope": json.loads(json.dumps(SCOPE)), "registrations": rec["registrations"], "start_claimed": rec["start_claimed"],
            "P2_enabled": False, "source_reads": 0, "permits": 0, "MAX_SESSION_TOTAL_READS": 1,
            "INSTANCE_RUNNING": False, "math_ready": False, "global_complete": False, "missing_fields": list(GAPS)}


def validate_live_entry(context, role, root):
    require(type(context) is LiveAuthorityContext and context in _CONTEXTS)
    return context.validate_service_entry(role, root)


def bind_dormant_store(context, store, expected_store, DB_path=None):
    require(type(context) is LiveAuthorityContext and context in _CONTEXTS)
    return context.bind_dormant_store(store, expected_store, DB_path)


def _id(value):
    require(type(value) is str and re.fullmatch(r"[A-Za-z0-9_.:-]{1,160}", value) is not None, "APPROVAL_REQUIRED")
    return value


def read_bound_document(scope, path):
    p = scope.path(path)
    try:
        require(p.is_file() and p.stat().st_size <= 16384, "RECOVERY_REQUIRED")
        value = strict_json(p.read_bytes())
        require(type(value) is dict and set(value) == {"payload", "digest"}
                and type(value["payload"]) is dict and value["digest"] == digest(value["payload"]), "RECOVERY_REQUIRED")
        return value["payload"]
    except SafetyError:
        raise
    except Exception:
        raise SafetyError("RECOVERY_REQUIRED") from None


def write_bound_document(scope, path, body, *, replace=False):
    p = scope.path(path)
    data = canonical({"payload": body, "digest": digest(body)})
    require(len(data) <= 16384, "RESOURCE_LIMIT")
    if p.exists():
        require(replace, "REPLAY")
        temporary = scope.write_new(p.with_name(p.name + ".tmp"), data)
        os.replace(temporary, p)
    else:
        scope.write_new(p, data)


def write_marker(scope, root, instance, phase, *, authorization_id=None, epoch=None, owner=None, control_name=None):
    body = {"schema": "r22-instance-marker/1", "environment_id": ENVIRONMENT, "run_id": scope.root.name,
        "instance_id": instance["instance_id"], "root_facts": scope.file_facts(root), "source_digest": scope.source_digest,
        "config_digest": instance["config_digest"], "SID": scope.SID, "phase": phase,
        "authorization_id": authorization_id, "process_epoch": epoch, "owner": owner,
        "control_name": control_name, "resources_owned": True, "P2": False}
    write_bound_document(scope, Path(root) / "instance_marker.json", body, replace=True)


def validate_marker(scope, root, instance, phases=None):
    body = read_bound_document(scope, Path(root) / "instance_marker.json")
    keys = {"schema", "environment_id", "run_id", "instance_id", "root_facts", "source_digest", "config_digest",
            "SID", "phase", "authorization_id", "process_epoch", "owner", "control_name", "resources_owned", "P2"}
    require(set(body) == keys and body["schema"] == "r22-instance-marker/1" and body["environment_id"] == ENVIRONMENT
        and body["run_id"] == scope.root.name and body["instance_id"] == instance["instance_id"]
        and body["root_facts"] == scope.file_facts(root) and body["source_digest"] == scope.source_digest
        and body["config_digest"] == instance["config_digest"] and body["SID"] == scope.SID
        and body["resources_owned"] is True and body["P2"] is False
        and body["phase"] in {"PREPARED", "SEED_READY", "CLAIMED", "SERVICE_READY", "STOPPING", "STOPPED", "RECOVERY_REQUIRED"}, "RECOVERY_REQUIRED")
    if phases is not None: require(body["phase"] in phases, "RECOVERY_REQUIRED")
    return body


def approval_paths(root, authorization_id):
    key = digest(_id(authorization_id))[:32]
    return Path(root) / ("start_approval_" + key + ".json"), Path(root) / ("start_consumption_" + key + ".jsonl"), Path(root) / ("start_effect_" + key + ".json")


class StartApproval(_Capability):
    def body(self):
        require(self in _START_APPROVALS)
        return json.loads(json.dumps(_START_APPROVALS[self]["body"]))


def issue_start_approval(scope, root, instance, authorization_id, lease, *, allow_new):
    """Trusted authorized test preparation, distinct from the job capability.

    The persistent action approval is immutable. Existing or partially published
    artifacts are loaded/refused, never reset to an unused state.
    """
    require(type(scope) is TestScope)
    validate_lease(lease, scope, root)
    grant_path, slot_path, effect = approval_paths(root, authorization_id)
    if grant_path.exists(): return load_start_approval(scope, root, instance, authorization_id, lease)
    require(allow_new is True and not slot_path.exists() and not effect.exists(), "RECOVERY_REQUIRED")
    receipt = strict_json((win.RECORD / "APPROVAL_RECEIPT.json").read_bytes())
    require(receipt.get("approved") is True and receipt.get("scope") == "R22 six targets and122 offline tests only", "APPROVAL_REQUIRED")
    body = {"schema": "r22-one-shot-start/1", "authorization_id": _id(authorization_id), "approved_action": "START_OFFLINE_SUPERVISOR",
        "environment_id": ENVIRONMENT, "run_id": scope.root.name, "deployment_root": str(scope.path(root)),
        "root_facts": scope.file_facts(root), "instance_id": instance["instance_id"], "source_digest": scope.source_digest,
        "config_digest": instance["config_digest"], "executor_SID": scope.SID,
        "Python_image": receipt["base_python"], "Python_version": "3.12.14", "Python_digest": win._SCOPES[scope]["python_digest"], "approved_scope": SCOPE,
        "issuer_identity": "R22_AUTHORIZED_SYNTHETIC_BOOTSTRAP", "approval_receipt_digest": win._hash(win.RECORD / "APPROVAL_RECEIPT.json"),
        "process_epoch": secrets.token_hex(32), "maximum_start_admissions": 1, "P2": False}
    write_bound_document(scope, grant_path, body)
    scope.private_acl(grant_path)
    first = {"seq": 0, "state": "UNCLAIMED", "grant_digest": digest(body), "process_epoch": body["process_epoch"],
        "owner": None, "previous": digest(body), "effect_count": 0}
    record = {"payload": first, "digest": digest(first)}
    scope.write_new(slot_path, canonical(record) + b"\n")
    scope.private_acl(slot_path)
    return load_start_approval(scope, root, instance, authorization_id, lease)


def load_start_approval(scope, root, instance, authorization_id, lease=None):
    require(type(scope) is TestScope)
    if lease is not None: validate_lease(lease, scope, root)
    path, slot, effect = approval_paths(root, authorization_id)
    require(path.exists(), "APPROVAL_REQUIRED")
    body = read_bound_document(scope, path)
    scope.acl(path)
    expected = {"schema", "authorization_id", "approved_action", "environment_id", "run_id", "deployment_root", "root_facts", "instance_id",
        "source_digest", "config_digest", "executor_SID", "Python_image", "Python_version", "Python_digest", "approved_scope", "issuer_identity",
        "approval_receipt_digest", "process_epoch", "maximum_start_admissions", "P2"}
    require(set(body) == expected and body["schema"] == "r22-one-shot-start/1" and body["authorization_id"] == authorization_id
        and body["approved_action"] == "START_OFFLINE_SUPERVISOR" and body["environment_id"] == ENVIRONMENT
        and body["run_id"] == scope.root.name and Path(body["deployment_root"]) == scope.path(root)
        and body["root_facts"] == scope.file_facts(root) and body["instance_id"] == instance["instance_id"]
        and body["source_digest"] == scope.source_digest and body["config_digest"] == effective_config_digest(scope, root)
        and body["executor_SID"] == scope.SID and Path(body["Python_image"]) == Path(win._SCOPES[scope]["process"]["image"])
        and body["Python_version"] == "3.12.14" and body["Python_digest"] == win._SCOPES[scope]["python_digest"] and body["approved_scope"] == SCOPE
        and body["issuer_identity"] == "R22_AUTHORIZED_SYNTHETIC_BOOTSTRAP"
        and body["approval_receipt_digest"] == win._hash(win.RECORD / "APPROVAL_RECEIPT.json")
        and type(body["maximum_start_admissions"]) is int and body["maximum_start_admissions"] == 1
        and body["P2"] is False and type(body["process_epoch"]) is str
        and re.fullmatch(r"[a-f0-9]{64}", body["process_epoch"]) is not None, "IDENTITY_MISMATCH")
    obj = object.__new__(StartApproval)
    _START_APPROVALS[obj] = {"scope": scope, "root": Path(root), "instance": instance, "body": body,
        "slot": slot, "effect": effect, "grant_facts": scope.file_facts(path)}
    # Missing/truncated slot is uncertainty even before the caller has a lease.
    read_consumption(obj, lease)
    return obj


def read_consumption(approval, lease=None):
    require(type(approval) is StartApproval and approval in _START_APPROVALS)
    rec = _START_APPROVALS[approval]; scope, body = rec["scope"], rec["body"]
    if lease is not None: validate_lease(lease, scope, rec["root"])
    path = scope.path(rec["slot"])
    try:
        require(path.is_file() and 0 < path.stat().st_size <= 16384, "RECOVERY_REQUIRED")
        raw = path.read_bytes(); require(raw.endswith(b"\n"), "RECOVERY_REQUIRED")
        parts = raw.splitlines(); require(1 <= len(parts) <= 5, "RECOVERY_REQUIRED")
        rows, previous = [], digest(body)
        allowed = {"UNCLAIMED": {"CLAIMED"}, "CLAIMED": {"STARTED", "UNCERTAIN", "FINISHED"},
                   "STARTED": {"FINISHED", "UNCERTAIN"}, "FINISHED": set(), "UNCERTAIN": set()}
        for index, part in enumerate(parts):
            value = strict_json(part)
            require(type(value) is dict and set(value) == {"payload", "digest"}, "RECOVERY_REQUIRED")
            row = value["payload"]
            require(type(row) is dict and set(row) == {"seq", "state", "grant_digest", "process_epoch", "owner", "previous", "effect_count"}
                and type(row["seq"]) is int and row["seq"] == index and row["grant_digest"] == digest(body)
                and row["process_epoch"] == body["process_epoch"] and row["previous"] == previous
                and value["digest"] == digest(row) and type(row["effect_count"]) is int
                and row["effect_count"] in {0, 1}, "RECOVERY_REQUIRED")
            if index == 0: require(row["state"] == "UNCLAIMED" and row["owner"] is None and row["effect_count"] == 0, "RECOVERY_REQUIRED")
            else:
                require(row["state"] in allowed[rows[-1]["state"]] and type(row["owner"]) is dict
                    and row["owner"]["SID"] == scope.SID and type(row["owner"]["pid"]) is int
                    and row["owner"]["created_filetime"] > 0, "RECOVERY_REQUIRED")
                if index > 1: require(row["owner"] == rows[-1]["owner"], "RECOVERY_REQUIRED")
                require(row["effect_count"] >= rows[-1]["effect_count"], "RECOVERY_REQUIRED")
            rows.append(row); previous = value["digest"]
        return rows
    except SafetyError: raise
    except Exception: raise SafetyError("RECOVERY_REQUIRED") from None


def _append_state(approval, lease, state, owner, effect_count):
    rec = _START_APPROVALS[approval]; scope = rec["scope"]
    rows = read_consumption(approval, lease); last = rows[-1]
    permitted = {"UNCLAIMED": {"CLAIMED"}, "CLAIMED": {"STARTED", "UNCERTAIN", "FINISHED"},
                 "STARTED": {"FINISHED", "UNCERTAIN"}}
    require(state in permitted.get(last["state"], set()), "REPLAY")
    row = {"seq": len(rows), "state": state, "grant_digest": digest(rec["body"]), "process_epoch": rec["body"]["process_epoch"],
        "owner": owner, "previous": digest(last), "effect_count": effect_count}
    payload = canonical({"payload": row, "digest": digest(row)}) + b"\n"
    facts = scope.file_facts(rec["slot"])
    try:
        with scope.path(rec["slot"]).open("ab") as stream:
            require(stream.write(payload) == len(payload), "RECOVERY_REQUIRED")
            stream.flush(); os.fsync(stream.fileno())
    except Exception:
        raise SafetyError("RECOVERY_REQUIRED") from None
    require(scope.file_facts(rec["slot"]) == facts, "RECOVERY_REQUIRED")
    require(read_consumption(approval, lease)[-1] == row, "RECOVERY_REQUIRED")
    return row


def consume_start_approval(approval, lease, expected_epoch):
    rec = _START_APPROVALS.get(approval); require(rec is not None)
    require(expected_epoch == rec["body"]["process_epoch"], "STALE_EPOCH")
    rows = read_consumption(approval, lease)
    require(rows[-1]["state"] == "UNCLAIMED", "REPLAY")
    require(not rec["effect"].exists(), "RECOVERY_REQUIRED")
    validate_marker(rec["scope"], rec["root"], rec["instance"], {"SEED_READY", "STOPPED"})
    owner = win.self_process_facts(rec["scope"]).facts()
    result = _append_state(approval, lease, "CLAIMED", owner, 0)
    write_marker(rec["scope"], rec["root"], rec["instance"], "CLAIMED", authorization_id=rec["body"]["authorization_id"],
                 epoch=expected_epoch, owner=owner)
    return result


def transition_consumption(approval, lease, state):
    rec = _START_APPROVALS.get(approval); require(rec is not None)
    rows = read_consumption(approval, lease); last = rows[-1]
    effect_count = last["effect_count"]
    if state == "STARTED":
        require(last["state"] == "CLAIMED" and not rec["effect"].exists(), "REPLAY")
        write_bound_document(rec["scope"], rec["effect"], {"schema": "r22-offline-start-effect/1", "grant_digest": digest(rec["body"]),
            "process_epoch": rec["body"]["process_epoch"], "owner": last["owner"], "effect_count": 1, "P2": False})
        effect_count = 1
    return _append_state(approval, lease, state, last["owner"], effect_count)


def finish_start_approval(approval, lease, *, successful):
    rec = _START_APPROVALS.get(approval); require(rec is not None)
    last = read_consumption(approval, lease)[-1]
    if last["state"] in {"FINISHED", "UNCERTAIN"}: return last
    require(last["state"] in {"CLAIMED", "STARTED"}, "RECOVERY_REQUIRED")
    return transition_consumption(approval, lease, "FINISHED" if successful else "UNCERTAIN")
