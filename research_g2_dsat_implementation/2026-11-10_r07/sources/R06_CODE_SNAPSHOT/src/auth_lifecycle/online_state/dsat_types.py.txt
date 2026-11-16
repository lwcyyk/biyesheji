"""Strict, secret-free offline DSAT data. No runtime/provider imports or I/O.

This module does not authenticate a service. FrozenTrust is a separate, explicit
synthetic-fixture trust boundary, never a source_confirmed flag in a payload.
"""
from dataclasses import dataclass
import hashlib
import json
import re


class InputError(ValueError):
    def __init__(self, code="INVALID_INPUT"):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class Limits:
    attempts: int = 256
    witnesses: int = 256
    edges: int = 16384
    records: int = 4096
    integer_bits: int = 128
    input_bytes: int = 1048576


DEFAULT_LIMITS = Limits()


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, OverflowError, RecursionError):
        raise InputError() from None


def digest(component, value):
    return hashlib.sha256(canonical({"schema": "dsat-proof-binding/1",
                                    "component": component, "payload": value})).hexdigest()


def math_digest(value):
    return hashlib.sha256(canonical({"schema": "dsat-math-input/1", "input": value})).hexdigest()


def packet_digest(value):
    body = {k: v for k, v in value.items() if k != "packet_digest"}
    return hashlib.sha256(canonical({"schema": "dsat-packet/1", "packet": body})).hexdigest()


def fields(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise InputError()
    return value


def ident(value):
    if type(value) is not str or not re.fullmatch(r"[A-Za-z0-9_.:/-]{1,160}", value):
        raise InputError()
    return value


def integer(value, limits=DEFAULT_LIMITS, nonnegative=True):
    if type(value) is not int or (nonnegative and value < 0):
        raise InputError()
    if value.bit_length() > limits.integer_bits:
        raise InputError("UNKNOWN_RESOURCE_LIMIT")
    return value


def boolean(value):
    if type(value) is not bool:
        raise InputError()
    return value


def items(value, limit):
    if type(value) is not list:
        raise InputError()
    if len(value) > limit:
        raise InputError("UNKNOWN_RESOURCE_LIMIT")
    return value


def ids(value, limit=4096):
    result = tuple(ident(x) for x in items(value, limit))
    if len(set(result)) != len(result):
        raise InputError()
    return result


def sha(value):
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise InputError()
    return value


ORIGIN_FIELDS = ("grant_id", "caller", "task", "account", "audience", "generation")


def origin(value):
    fields(value, ORIGIN_FIELDS)
    return {k: ident(value[k]) for k in ORIGIN_FIELDS}


@dataclass(frozen=True)
class GrantSnapshot:
    origin: dict
    active: bool
    operations: tuple
    limit: int
    reserved: int
    spent: int

    @classmethod
    def parse(cls, value, limits):
        fields(value, ("origin", "active", "operations", "limit", "reserved", "spent"))
        result = cls(origin(value["origin"]), boolean(value["active"]), ids(value["operations"]),
                     integer(value["limit"], limits), integer(value["reserved"], limits),
                     integer(value["spent"], limits))
        if result.reserved + result.spent > result.limit:
            raise InputError()
        return result


@dataclass(frozen=True)
class RequestSnapshot:
    rid: str
    attempt_id: str | None
    release_version: int | None
    request_digest: str
    origin: dict
    operation: str
    source_rid: str | None
    phase: str

    @classmethod
    def parse(cls, value, limits):
        fields(value, ("rid", "attempt_id", "release_version", "request_digest", "origin",
                       "operation", "source_rid", "phase", "original_request"))
        o = origin(value["origin"])
        body = value["original_request"]
        fields(body, ("rid", "handle", "task", "account", "audience", "generation", "operation", "payload"))
        for key in set(body) - {"payload"}:
            if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", ident(body[key])):
                raise InputError()
        operation = ident(value["operation"])
        if operation not in {"issue", "refresh", "userinfo"}:
            raise InputError()
        fields(body["payload"], () if operation == "issue" else ("source_rid",))
        source = None if operation == "issue" else ident(body["payload"]["source_rid"])
        if (body["rid"] != value["rid"] or body["operation"] != operation
                or source != value["source_rid"]
                or any(body[k] != o[k] for k in ("task", "account", "audience", "generation"))):
            raise InputError()
        expected = hashlib.sha256(canonical({"caller": o["caller"], "request": body})).hexdigest()
        if sha(value["request_digest"]) != expected:
            raise InputError("REJECT_UNAUTHORIZED")
        phase = ident(value["phase"])
        if phase not in {"QUEUED", "CANCELLED", "DISPATCHED_UNKNOWN", "RESULT_AVAILABLE", "QUARANTINED", "DISPOSED"}:
            raise InputError()
        aid = None if value["attempt_id"] is None else ident(value["attempt_id"])
        ver = None if value["release_version"] is None else integer(value["release_version"], limits)
        if (phase in {"QUEUED", "CANCELLED"}) != (aid is None and ver is None):
            raise InputError()
        if phase not in {"QUEUED", "CANCELLED"} and (aid is None or ver is None):
            raise InputError()
        return cls(ident(value["rid"]), aid, ver, expected, o, operation, source, phase)


@dataclass(frozen=True)
class AuthoritySnapshot:
    instance_ref: str
    version: int
    now: int
    creation_paused: bool
    grants: tuple
    requests: tuple

    @classmethod
    def parse(cls, value, limits):
        fields(value, ("instance_ref", "version", "now", "creation_paused", "grants", "requests"))
        gs = tuple(GrantSnapshot.parse(x, limits) for x in items(value["grants"], limits.records))
        rs = tuple(RequestSnapshot.parse(x, limits) for x in items(value["requests"], limits.records))
        for keys in ([g.origin["grant_id"] for g in gs], [r.rid for r in rs], [r.attempt_id for r in rs if r.attempt_id is not None]):
            if len(keys) != len(set(keys)):
                raise InputError()
        return cls(ident(value["instance_ref"]), integer(value["version"], limits),
                   integer(value["now"], limits), boolean(value["creation_paused"]), gs, rs)


@dataclass(frozen=True)
class CreationAttempt:
    id: str
    rid: str
    capacity_contract_ref: str
    audit_required: bool

    @classmethod
    def parse(cls, value):
        fields(value, ("id", "rid", "capacity_contract_ref", "audit_required"))
        return cls(ident(value["id"]), ident(value["rid"]), ident(value["capacity_contract_ref"]),
                   boolean(value["audit_required"]))


@dataclass(frozen=True)
class CapacityContract:
    id: str
    attempt_ref: str
    capacity: int | None
    source_ref: str

    @classmethod
    def parse(cls, value, limits):
        fields(value, ("id", "attempt_ref", "capacity", "source_ref"))
        c = None if value["capacity"] is None else integer(value["capacity"], limits)
        return cls(ident(value["id"]), ident(value["attempt_ref"]), c, ident(value["source_ref"]))


@dataclass(frozen=True)
class EvidenceScope:
    account: str
    audience: str
    paths: tuple
    permit_ref: str
    valid_from: int
    valid_until: int

    @classmethod
    def parse(cls, value, limits):
        fields(value, ("account", "audience", "paths", "permit_ref", "valid_from", "valid_until"))
        result = cls(ident(value["account"]), ident(value["audience"]), ids(value["paths"]),
                     ident(value["permit_ref"]), integer(value["valid_from"], limits),
                     integer(value["valid_until"], limits))
        if result.valid_from > result.valid_until:
            raise InputError()
        return result


@dataclass(frozen=True)
class CreationWitness:
    unit_id: str
    native_ref: str
    birth_ref: str | None
    service_ref: str
    database_ref: str
    source_candidates: tuple
    request_binding: dict | None
    deleted: bool

    @classmethod
    def parse(cls, value):
        fields(value, ("unit_id", "native_ref", "birth_ref", "service_ref", "database_ref",
                       "source_candidates", "request_binding", "deleted"))
        b = value["request_binding"]
        if b is not None:
            fields(b, ("rid", "request_digest", "origin", "attempt_id", "release_version"))
            ident(b["rid"]); sha(b["request_digest"]); origin(b["origin"])
            ident(b["attempt_id"]); integer(b["release_version"])
        return cls(ident(value["unit_id"]), ident(value["native_ref"]),
                   None if value["birth_ref"] is None else ident(value["birth_ref"]),
                   ident(value["service_ref"]), ident(value["database_ref"]),
                   ids(value["source_candidates"]), b, boolean(value["deleted"]))

    @property
    def birth_key(self):
        return (self.service_ref, self.database_ref, self.native_ref, self.birth_ref)


@dataclass(frozen=True)
class OriginRelation:
    unit_id: str
    attempts: tuple


@dataclass(frozen=True)
class MaterialObservation:
    unit_id: str
    status_kind: str
    performed: bool
    http: int | None
    active: bool | None
    accepted: bool | None
    paths: tuple
    frame_ref: str | None

    @classmethod
    def parse(cls, value, limits):
        fields(value, ("unit_id", "status_kind", "performed", "http", "active", "accepted", "paths", "frame_ref"))
        for k in ("active", "accepted"):
            if value[k] is not None:
                boolean(value[k])
        http = None if value["http"] is None else integer(value["http"], limits)
        if http is not None and not 100 <= http <= 599:
            raise InputError()
        kind = ident(value["status_kind"])
        if kind not in {"AT_USERINFO", "AT_INTROSPECTION", "RT_INTROSPECTION", "NAMED_STATE", "SUSTAINED_INACTIVITY"}:
            raise InputError()
        return cls(ident(value["unit_id"]), kind, boolean(value["performed"]), http,
                   value["active"], value["accepted"], ids(value["paths"]),
                   None if value["frame_ref"] is None else ident(value["frame_ref"]))


@dataclass(frozen=True)
class EvidenceEnvelope:
    id: str
    kind: str
    source_ref: str
    source_version: str
    observed_at: int
    received_at: int
    scope: EvidenceScope
    payload: CreationWitness | MaterialObservation

    @classmethod
    def parse(cls, value, limits):
        fields(value, ("id", "kind", "source_ref", "source_version", "observed_at", "received_at", "scope", "payload"))
        kind = value["kind"]
        if kind not in {"CREATION", "MATERIAL"}:
            raise InputError()
        payload = CreationWitness.parse(value["payload"]) if kind == "CREATION" else MaterialObservation.parse(value["payload"], limits)
        return cls(ident(value["id"]), kind, ident(value["source_ref"]), ident(value["source_version"]),
                   integer(value["observed_at"], limits), integer(value["received_at"], limits),
                   EvidenceScope.parse(value["scope"], limits), payload)


@dataclass(frozen=True)
class OutstandingObligation:
    id: str
    kind: str
    refs: tuple
    strict: bool

    @classmethod
    def parse(cls, value):
        fields(value, ("id", "kind", "refs", "strict"))
        return cls(ident(value["id"]), ident(value["kind"]), ids(value["refs"]), boolean(value["strict"]))


@dataclass(frozen=True)
class CostRecord:
    id: str
    category: str
    amount: int
    unit: str
    historical: bool

    @classmethod
    def parse(cls, value, limits):
        fields(value, ("id", "category", "amount", "unit", "historical"))
        return cls(ident(value["id"]), ident(value["category"]), integer(value["amount"], limits),
                   ident(value["unit"]), boolean(value["historical"]))


@dataclass(frozen=True)
class FrozenTrust:
    """Caller-supplied frozen manifest, kept outside the untrusted evidence bundle."""
    snapshot_digest: str
    contract_digest: str
    obligations_digest: str
    costs_digest: str
    envelope_digests: dict
    producers: tuple
    permits: tuple

    @classmethod
    def parse(cls, value):
        fields(value, ("mode", "snapshot_digest", "contract_digest", "obligations_digest", "costs_digest",
                       "envelope_digests", "producers", "permits"))
        if value["mode"] != "SYNTHETIC_CONTRACT" or type(value["envelope_digests"]) is not dict:
            raise InputError("REJECT_UNAUTHORIZED")
        return cls(sha(value["snapshot_digest"]), sha(value["contract_digest"]),
                   sha(value["obligations_digest"]), sha(value["costs_digest"]),
                   {ident(k): sha(v) for k, v in value["envelope_digests"].items()},
                   ids(value["producers"]), ids(value["permits"]))


def normalize_math(value, limits=DEFAULT_LIMITS):
    if len(canonical(value)) > limits.input_bytes:
        raise InputError("UNKNOWN_RESOURCE_LIMIT")
    fields(value, ("I", "T", "c", "U", "E", "D_P"))
    I = ids(value["I"], limits.attempts)
    U = ids(value["U"], limits.witnesses)
    T = ids(value["T"], limits.attempts)
    D = ids(value["D_P"], limits.witnesses)
    if not set(T) <= set(I) or not set(D) <= set(U) or type(value["c"]) is not dict or set(value["c"]) != set(I):
        raise InputError()
    c = {i: integer(value["c"][i], limits) for i in I}
    edges = []
    for edge in items(value["E"], limits.edges):
        if type(edge) is not list or len(edge) != 2 or edge[0] not in U or edge[1] not in I:
            raise InputError()
        edges.append((ident(edge[0]), ident(edge[1])))
    if len(set(edges)) != len(edges):
        raise InputError()
    return {"I": sorted(I), "T": sorted(T), "c": {i: c[i] for i in sorted(I)},
            "U": sorted(U), "E": [list(e) for e in sorted(edges)], "D_P": sorted(D)}
