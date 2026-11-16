"""Bounded, secret-free dsat-commit/1 data. Standard library; no import I/O."""
from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path
import re


PROJECT = Path(r"D:\毕业设计\auth-lifecycle")
RUN_ROOT = Path(r"D:\毕业设计\research_g2_dsat_implementation\2026-11-10_r09_s3a")
DB_ROOT = RUN_ROOT / "synthetic_db"
SCOPE_PATH = Path(r"D:\毕业设计\research_g2_dsat_implementation\2026-11-10_r09\S3A_SCOPE_LOCK.json")
MODE = "SYNTHETIC_CONTRACT"
MAX_REVISION = (1 << 63) - 1
NATIVE_GAP = "SOURCE_OR_REFINEMENT_GAP"
LEVELS = ("MATH_ARCHIVE", "CONDITIONAL_ARCHIVE", "COVER_PRESERVING_MODEL_TRANSFORM")


class CommitError(ValueError):
    def __init__(self, code="INVALID_INPUT"):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class Limits:
    proof_bytes: int = 4194304
    world_bytes: int = 8388608
    proposal_bytes: int = 8388608
    objects_bytes: int = 8388608
    receipt_bytes: int = 262144
    event_bytes: int = 1048576
    O_items: int = 1024
    risk_components: int = 4096
    proposal_ids: int = 256
    db_pages: int = 16384
    wal_bytes: int = 67108864
    shm_bytes: int = 4194304
    run_bytes: int = 268435456
    busy_ms: int = 1000

    def __post_init__(self):
        for f in fields(self):
            maximum = f.default
            value = getattr(self, f.name)
            if type(value) is not int or not 1 <= value <= maximum:
                raise CommitError("UNKNOWN_RESOURCE_LIMIT")


def integer(value, maximum=MAX_REVISION):
    if type(value) is not int or not 0 <= value <= maximum:
        raise CommitError()
    return value


def ident(value):
    if type(value) is not str or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value) is None:
        raise CommitError()
    return value


def keys(value, names):
    if type(value) is not dict or set(value) != set(names):
        raise CommitError()


def _json_value(value, depth=0):
    if depth > 32:
        raise CommitError("UNKNOWN_RESOURCE_LIMIT")
    if type(value) is dict:
        for k, v in value.items():
            if type(k) is not str:
                raise CommitError()
            _json_value(k, depth + 1)
            _json_value(v, depth + 1)
    elif type(value) is list:
        for v in value:
            _json_value(v, depth + 1)
    elif type(value) is str:
        if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
            raise CommitError()
    elif type(value) is int:
        if abs(value) > (1 << 128) - 1:
            raise CommitError()
    elif value is not None and type(value) is not bool:
        raise CommitError()


def canonical(value):
    _json_value(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


def strict_load(data, maximum=8388608):
    if isinstance(data, str):
        try:
            data = data.encode("utf-8")
        except UnicodeError as exc:
            raise CommitError() from exc
    if type(data) is not bytes or len(data) > maximum:
        raise CommitError("UNKNOWN_RESOURCE_LIMIT")

    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise CommitError()
            result[k] = v
        return result

    def invalid(_):
        raise CommitError()

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
                           parse_float=invalid, parse_constant=invalid)
        _json_value(value)
        return value
    except (UnicodeError, RecursionError, json.JSONDecodeError) as exc:
        raise CommitError() from exc


def clone(value):
    return strict_load(canonical(value))


def digest(domain, value):
    return hashlib.sha256(domain.encode("ascii") + b"\x00" + canonical(value)).hexdigest()


def legacy_digest(component, value):
    return hashlib.sha256(canonical({"schema": "dsat-proof-binding/1", "component": component,
                                     "payload": value})).hexdigest()


def packet_digest(packet):
    return hashlib.sha256(canonical({"schema": "dsat-packet/1", "packet": {
        k: v for k, v in packet.items() if k != "packet_digest"}})).hexdigest()


def object_digest(kind, value):
    return digest("dsat-s3a-object/1:" + kind, value)


def O_digest(obligations):
    return digest("dsat-s3a/1:typed-O", obligations)


def proposal_digest(body):
    return digest("dsat-commit/1:proposal", {k: v for k, v in body.items() if k != "proposal_digest"})


def seal(body):
    value = clone(body)
    value["proposal_digest"] = proposal_digest(value)
    return value


def raw_obligation(value):
    keys(value, ("id", "kind", "refs", "strict"))
    ident(value["id"]); ident(value["kind"])
    if type(value["refs"]) is not list or len(value["refs"]) > 4096 or type(value["strict"]) is not bool:
        raise CommitError()
    for ref in value["refs"]:
        ident(ref)
    return clone(value)


def obligation(raw, scope):
    raw = raw_obligation(raw)
    # An opaque hold covers the whole old descriptor, including unobserved risks.
    return {**raw, "scope": scope, "origin": {"refs": list(raw["refs"])},
            "descriptor": raw, "holds": [digest("dsat-s3a/1:risk", raw)], "retained": None,
            "dependency_epoch": 0}


def pending_source(old):
    result = clone(old)
    result.update(id="pending_source:" + old["id"], kind="pending_source",
                  retained=clone(old))
    return result


@dataclass(frozen=True)
class Actor:
    """Identity supplied by the trusted offline caller, independent of the body."""
    name: str

    def __post_init__(self):
        ident(self.name)


@dataclass(frozen=True)
class AuthorityRevision:
    a: int
    o: int

    def __post_init__(self):
        integer(self.a); integer(self.o)


@dataclass(frozen=True)
class CertificateReference:
    packet_digest: str
    checker_source_digest: str
    math_input_digest: str


@dataclass(frozen=True)
class ObligationDelta:
    add: list
    replace: list


@dataclass(frozen=True)
class WorkRecord:
    id: str
    body: dict


@dataclass(frozen=True)
class Receipt:
    value: dict


PROPOSAL_FIELDS = (
    "schema", "mode", "authority_instance", "proposal_id", "actor",
    "base_authority_revision", "base_obligation_revision", "base_O_digest",
    "source_snapshot_digest", "request_scope_digest", "current_grant_digest", "policy_epoch",
    "proof", "packet_digest", "math_input_digest", "checker_source_digest",
    "projection_digest", "projection_O_digest", "proof_context_O_digest",
    "obligations_delta", "dependency_policy", "cost_delta", "requested_level", "proposal_digest")


@dataclass(frozen=True)
class Proposal:
    body: dict

    @classmethod
    def parse(cls, data, limits=Limits()):
        encoded = data if type(data) in (bytes, str) else canonical(data)
        value = strict_load(encoded, limits.proposal_bytes)
        keys(value, PROPOSAL_FIELDS)
        if value["schema"] != "dsat-commit/1" or value["mode"] != MODE or value["requested_level"] not in LEVELS:
            raise CommitError()
        for k in ("authority_instance", "proposal_id", "actor"):
            ident(value[k])
        for k in ("base_authority_revision", "base_obligation_revision", "policy_epoch"):
            integer(value[k])
        for k in ("base_O_digest", "source_snapshot_digest", "request_scope_digest", "current_grant_digest",
                  "packet_digest", "math_input_digest", "checker_source_digest", "projection_digest",
                  "projection_O_digest", "proof_context_O_digest", "proposal_digest"):
            if type(value[k]) is not str or re.fullmatch("[0-9a-f]{64}", value[k]) is None:
                raise CommitError()
        if len(canonical(value["proof"])) > limits.proof_bytes:
            raise CommitError("UNKNOWN_RESOURCE_LIMIT")
        keys(value["obligations_delta"], ("add", "replace"))
        if any(type(value["obligations_delta"][k]) is not list for k in ("add", "replace")):
            raise CommitError()
        keys(value["dependency_policy"], ("require_current", "allow_history"))
        if any(type(x) is not bool for x in value["dependency_policy"].values()):
            raise CommitError()
        if type(value["cost_delta"]) is not list or len(value["cost_delta"]) > 4096:
            raise CommitError()
        seen = set()
        for work in value["cost_delta"]:
            keys(work, ("id", "body")); ident(work["id"])
            keys(work["body"], ("amount", "unit", "math_input_digest"))
            integer(work["body"]["amount"], (1 << 128) - 1); ident(work["body"]["unit"])
            if work["id"] in seen:
                raise CommitError()
            seen.add(work["id"])
        if value["proposal_digest"] != proposal_digest(value):
            raise CommitError()
        return cls(value)


def validate_world(world, limits=Limits()):
    if world.get("schema") != "dsat-s3a-world/1":
        raise CommitError("UNSUPPORTED_SCHEMA")
    if world.get("mode") != MODE or world.get("codec") != "SyntheticJsonCodec/1":
        raise CommitError("UNSUPPORTED_MODE")
    if world.get("NO_NATIVE") is not True or world.get("NO_GLOBAL_COMPLETE") is not True:
        raise CommitError("UNSUPPORTED_MODE")
    ident(world["authority_instance"])
    integer(world["genesis_revision"])
    dsat = world.get("dsat", {})
    if "O" not in dsat or type(dsat["O"]) is not list:
        raise CommitError("DB_IDENTITY_MISMATCH")
    integer(dsat["obligation_revision"])
    if len(dsat["O"]) > limits.O_items or sum(len(x["holds"]) for x in dsat["O"]) > limits.risk_components:
        raise CommitError("UNKNOWN_RESOURCE_LIMIT")
    ids = set()
    for item in dsat["O"]:
        ident(item["id"])
        if item["id"] in ids:
            raise CommitError("DB_IDENTITY_MISMATCH")
        ids.add(item["id"])
        raw_obligation(item["descriptor"])
    if len(canonical(world)) > limits.world_bytes:
        raise CommitError("UNKNOWN_RESOURCE_LIMIT")
