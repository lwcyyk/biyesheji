"""S1 offline projection for explicitly frozen SYNTHETIC_CONTRACT bundles.

No network, file access, runtime AuthorityStore/Provider or state mutation.
The caller owns the separately frozen manifest. Hash agreement binds fixture
bytes; it is not authentication of Casdoor or approval for native closure.
"""
from dataclasses import asdict
import json

from .dsat_types import (
    AuthoritySnapshot, CapacityContract, CostRecord, CreationAttempt,
    CreationWitness, EvidenceEnvelope, FrozenTrust, InputError, Limits,
    DEFAULT_LIMITS, MaterialObservation, OriginRelation, OutstandingObligation,
    boolean, canonical, digest, fields, ident, ids, integer, items, normalize_math,
)


def _failure(code):
    return {"schema": "readonly-lifecycle-projection/1", "mode": "SYNTHETIC_CONTRACT",
            "status": code, "issues": [{"code": code}], "math_input": None,
            "math_ready": False, "obligations_proposed": None,
            "obligation_action": "KEEP_EXISTING", "native_admission": "SOURCE_OR_REFINEMENT_GAP",
            "global_complete": False}


def project_evidence(bundle, trusted_manifest, limits=DEFAULT_LIMITS):
    """Return a proposal only. No existing obligation is discharged here."""
    try:
        return _project(bundle, trusted_manifest, limits)
    except InputError as error:
        return _failure(error.code)
    except (KeyError, TypeError, ValueError, RecursionError):
        return _failure("INVALID_INPUT")


def _project(bundle, trusted_manifest, limits):
    encoded = canonical(bundle)
    if len(encoded) > limits.input_bytes:
        raise InputError("UNKNOWN_RESOURCE_LIMIT")
    # Work on a detached JSON snapshot; output lists never alias caller input.
    bundle = json.loads(encoded)
    fields(bundle, ("mode", "authority", "attempts", "capacity_contracts", "envelopes", "history",
                    "contract", "scope", "obligations", "costs"))
    if bundle["mode"] != "SYNTHETIC_CONTRACT":
        raise InputError("REJECT_UNAUTHORIZED")
    trust = trusted_manifest if isinstance(trusted_manifest, FrozenTrust) else FrozenTrust.parse(trusted_manifest)
    contract_binding = {k: bundle[k] for k in ("contract", "scope", "attempts", "capacity_contracts")}
    for actual, expected in (
        (digest("snapshot", bundle["authority"]), trust.snapshot_digest),
        (digest("projection_contract", contract_binding), trust.contract_digest),
        (digest("O_before", bundle["obligations"]), trust.obligations_digest),
        (digest("cost_ledger", bundle["costs"]), trust.costs_digest),
    ):
        if actual != expected:
            raise InputError("REJECT_UNAUTHORIZED")
    authority = AuthoritySnapshot.parse(bundle["authority"], limits)
    attempts = tuple(CreationAttempt.parse(x) for x in items(bundle["attempts"], limits.attempts))
    capacities = tuple(CapacityContract.parse(x, limits) for x in items(bundle["capacity_contracts"], limits.attempts))
    obligations = tuple(OutstandingObligation.parse(x) for x in items(bundle["obligations"], limits.records))
    costs = tuple(CostRecord.parse(x, limits) for x in items(bundle["costs"], limits.records))
    for keys in ([x.id for x in attempts], [x.rid for x in attempts], [x.id for x in capacities],
                 [x.attempt_ref for x in capacities], [x.id for x in obligations], [x.id for x in costs]):
        if len(keys) != len(set(keys)):
            raise InputError()
    contract = fields(bundle["contract"], ("source_version", "source_complete", "capacity_complete",
                     "frontier_complete", "external_writers_excluded", "derivations_covered", "inactivity_frames"))
    ident(contract["source_version"])
    for key in ("source_complete", "capacity_complete", "frontier_complete", "external_writers_excluded", "derivations_covered"):
        boolean(contract[key])
    frames = ids(contract["inactivity_frames"])
    scope = fields(bundle["scope"], ("account", "audience", "paths", "target_attempts", "open_frontiers"))
    ident(scope["account"]); ident(scope["audience"])
    paths = ids(scope["paths"])
    targets = ids(scope["target_attempts"], limits.attempts)
    frontiers = set(ids(scope["open_frontiers"]))
    requests = {r.rid: r for r in authority.requests}
    grants = {g.origin["grant_id"]: g for g in authority.grants}
    amap = {a.id: a for a in attempts}
    by_rid = {a.rid: a for a in attempts}
    cmap = {c.id: c for c in capacities}
    if not set(targets) <= set(amap):
        raise InputError()
    issues = []

    def issue(code, ref=None):
        row = {"code": code}
        if ref is not None:
            row["ref"] = ref
        if row not in issues:
            issues.append(row)

    proposed = {o.id: asdict(o) for o in obligations}

    def add_obligation(oid, kind, refs):
        if oid not in proposed:
            proposed[oid] = {"id": oid, "kind": kind, "refs": list(refs), "strict": True}

    for key in ("source_complete", "capacity_complete", "external_writers_excluded", "derivations_covered"):
        if not contract[key]:
            issue("INSUFFICIENT_COVERAGE", key)
    if not contract["frontier_complete"]:
        frontiers.add("frontier:contract")
    if not paths:
        issue("INSUFFICIENT_COVERAGE", "paths")
    cvalues = {}
    structure_ready = True
    for attempt in attempts:
        req = requests.get(attempt.rid)
        cap = cmap.get(attempt.capacity_contract_ref)
        if (req is None or req.operation not in {"issue", "refresh"} or req.attempt_id is None
                or req.release_version is None or req.release_version > authority.version):
            issue("INSUFFICIENT_COVERAGE", attempt.id)
            structure_ready = False
        if cap is None or cap.attempt_ref != attempt.id or cap.capacity is None:
            issue("INSUFFICIENT_COVERAGE", "capacity:" + attempt.id)
            structure_ready = False
        else:
            cvalues[attempt.id] = cap.capacity
        if attempt.audit_required:
            add_obligation("await_terminal:" + attempt.id, "await_terminal", [attempt.id])
    for req in authority.requests:
        grant = grants.get(req.origin["grant_id"])
        if grant is None or grant.origin != req.origin:
            issue("EVIDENCE_CONFLICT", req.rid)
        if req.phase == "QUEUED" and (grant is None or not grant.active or req.operation not in grant.operations):
            issue("REJECT_UNAUTHORIZED", req.rid)
        if req.operation in {"refresh", "userinfo"}:
            source = requests.get(req.source_rid)
            if source is None or source.origin != req.origin:
                issue("REJECT_UNAUTHORIZED", req.rid)
        if req.attempt_id is not None and req.operation in {"issue", "refresh"}:
            a = by_rid.get(req.rid)
            if a is None:
                issue("INSUFFICIENT_COVERAGE", req.rid)
                structure_ready = False
            if req.phase == "DISPATCHED_UNKNOWN":
                key = a.id if a else req.attempt_id
                add_obligation("settle:" + key, "settle", [key])
        elif req.attempt_id is not None and req.operation == "userinfo" and req.phase == "DISPATCHED_UNKNOWN":
            add_obligation("exec:" + req.rid, "exec", [req.rid])
    for grant in authority.grants:
        if (grant.active and {"issue", "refresh"}.intersection(grant.operations)
                and grant.limit > grant.spent + grant.reserved and not authority.creation_paused):
            frontiers.add("frontier:" + grant.origin["grant_id"])
    if frontiers:
        issue("OPEN_FRONTIER")
        for ref in frontiers:
            add_obligation(ref, "frontier", [ref])
    raw_records = items(bundle["history"], limits.records) + items(bundle["envelopes"], limits.records)
    if len(raw_records) > limits.records:
        raise InputError("UNKNOWN_RESOURCE_LIMIT")
    valid_records = []
    seen_ids = {}
    for raw in raw_records:
        env = EvidenceEnvelope.parse(raw, limits)
        encoded_digest = digest("envelope", raw)
        if (trust.envelope_digests.get(env.id) != encoded_digest or env.source_ref not in trust.producers
                or env.scope.permit_ref not in trust.permits
                or env.scope.account != scope["account"] or env.scope.audience != scope["audience"]):
            issue("REJECT_UNAUTHORIZED", env.id)
            continue
        if env.id in seen_ids:
            if seen_ids[env.id] != encoded_digest:
                issue("EVIDENCE_CONFLICT", env.id)
            continue
        seen_ids[env.id] = encoded_digest
        if not env.scope.valid_from <= env.observed_at <= env.scope.valid_until:
            issue("STALE_EVIDENCE", env.id)
            continue
        if env.observed_at > env.received_at or env.received_at > authority.now:
            issue("STALE_EVIDENCE", env.id)
        if env.source_version != contract["source_version"]:
            issue("STALE_EVIDENCE", env.id)
        valid_records.append(env)
    groups = {}
    unit_keys = {}
    unknown_aliases = []
    quarantined = []
    for env in valid_records:
        if env.kind != "CREATION":
            continue
        w = env.payload
        if w.birth_ref is None:
            unknown_aliases.append({"unit_id": w.unit_id, "evidence_ref": env.id})
            issue("INSUFFICIENT_COVERAGE", "birth:" + w.unit_id)
            continue
        if w.unit_id in unit_keys and unit_keys[w.unit_id] != w.birth_key:
            issue("EVIDENCE_CONFLICT", w.unit_id)
            continue
        unit_keys[w.unit_id] = w.birth_key
        candidates = set(w.source_candidates) if w.source_candidates else set(amap)
        if not candidates <= set(amap):
            issue("INSUFFICIENT_COVERAGE", "origin:" + w.unit_id)
            structure_ready = False
            continue
        if w.request_binding is not None:
            binding = w.request_binding
            req = requests.get(binding["rid"])
            a = by_rid.get(binding["rid"])
            if (req is None or a is None or req.request_digest != binding["request_digest"]
                    or req.attempt_id != binding["attempt_id"] or req.release_version != binding["release_version"]
                    or req.origin != binding["origin"]):
                issue("EVIDENCE_CONFLICT", env.id)
                continue
            if a.id not in candidates:
                issue("EVIDENCE_CONFLICT", env.id)
            candidates &= {a.id}
            grant = grants.get(req.origin["grant_id"])
            if grant is not None and not grant.active:
                quarantined.append({"unit_id": w.unit_id, "grant_id": grant.origin["grant_id"], "evidence_ref": env.id})
        if w.birth_key not in groups:
            groups[w.birth_key] = {"aliases": set(), "sources": candidates, "refs": set(), "deleted": False}
        group = groups[w.birth_key]
        group["aliases"].add(w.unit_id)
        group["sources"] &= candidates
        group["refs"].add(env.id)
        group["deleted"] |= w.deleted
        if not group["sources"]:
            issue("EVIDENCE_CONFLICT", w.unit_id)
    if len(groups) > limits.witnesses:
        raise InputError("UNKNOWN_RESOURCE_LIMIT")
    units = []
    alias_to_unit = {}
    for key, group in groups.items():
        uid = min(group["aliases"])
        for alias in group["aliases"]:
            alias_to_unit[alias] = uid
        units.append({"unit_id": uid, "birth_key": list(key), "aliases": sorted(group["aliases"]),
                      "source_candidates": sorted(group["sources"]), "evidence_refs": sorted(group["refs"]),
                      "historically_deleted": group["deleted"], "state": "CONFIRMED_CREATION"})
    D = set()
    point_observations = []
    for env in valid_records:
        if env.kind != "MATERIAL":
            continue
        obs = env.payload
        uid = alias_to_unit.get(obs.unit_id)
        active = obs.active if obs.performed and obs.http == 200 else None
        accepted = obs.accepted if (obs.performed and obs.http in {200, 400, 401, 403}
                                    and (obs.accepted is not True or obs.http == 200)) else None
        point_observations.append({"unit_id": obs.unit_id, "status_kind": obs.status_kind,
                                   "performed": obs.performed, "http": obs.http,
                                   "active": active, "accepted": accepted,
                                   "reported_active": obs.active, "reported_accepted": obs.accepted,
                                   "evidence_ref": env.id})
        if ((obs.active is not None and active is None)
                or (obs.accepted is not None and accepted is None)):
            issue("INSUFFICIENT_COVERAGE", env.id)
        current = env.scope.valid_until >= authority.now and env.source_version == contract["source_version"]
        if not current:
            issue("STALE_EVIDENCE", env.id)
        if (uid is not None and obs.status_kind == "SUSTAINED_INACTIVITY" and obs.performed
                and obs.http == 200 and obs.active is False and obs.frame_ref in frames
                and set(paths) <= set(obs.paths) and set(paths) <= set(env.scope.paths) and current):
            D.add(uid)
    E = [[u["unit_id"], i] for u in units for i in u["source_candidates"]]
    if len(E) > limits.edges:
        raise InputError("UNKNOWN_RESOURCE_LIMIT")
    for unit in units:
        if set(unit["source_candidates"]).intersection(targets) and unit["unit_id"] not in D:
            add_obligation("close:" + unit["unit_id"], "close", [unit["unit_id"]])
    blocked = any(x["code"] in {"REJECT_UNAUTHORIZED", "EVIDENCE_CONFLICT"} for x in issues)
    math_input = None
    if structure_ready and not blocked:
        math_input = normalize_math({"I": list(amap), "T": list(targets), "c": cvalues,
                                     "U": [u["unit_id"] for u in units], "E": E, "D_P": list(D)}, limits)
    priority = ("EVIDENCE_CONFLICT", "REJECT_UNAUTHORIZED", "STALE_EVIDENCE", "OPEN_FRONTIER", "INSUFFICIENT_COVERAGE")
    codes = {i["code"] for i in issues}
    status = next((c for c in priority if c in codes), "UNKNOWN_PENDING")
    scope_ready = not issues and all(contract[k] for k in ("source_complete", "capacity_complete", "frontier_complete",
                                                          "external_writers_excluded", "derivations_covered"))
    return {"schema": "readonly-lifecycle-projection/1", "mode": "SYNTHETIC_CONTRACT",
            "status": status, "issues": issues, "math_input": math_input, "math_ready": math_input is not None,
            "partial_math": {"I": sorted(amap), "T": sorted(targets), "c_known": cvalues,
                             "capacity_unknown": sorted(set(amap) - set(cvalues)),
                             "U": sorted(u["unit_id"] for u in units), "E": sorted(E), "D_P": sorted(D)},
            "units": sorted(units, key=lambda u: u["unit_id"]), "unknown_aliases": unknown_aliases,
            "point_observations": point_observations, "quarantined": quarantined,
            "open_frontiers": sorted(frontiers), "source_scope_preconditions_declared": scope_ready,
            "creation_states": {a.id: "POSSIBLE_CREATION" for a in attempts},
            "origin_relations": [asdict(OriginRelation(u["unit_id"], tuple(u["source_candidates"]))) for u in units],
            "obligations_proposed": [proposed[k] for k in sorted(proposed)], "obligation_action": "PROPOSAL_ONLY_KEEP_EXISTING",
            "costs_retained": [asdict(c) for c in costs], "native_admission": "SOURCE_OR_REFINEMENT_GAP",
            "global_complete": False, "scope": dict(scope), "authority_version": authority.version,
            "work_counts": {"input_records": len(raw_records), "unique_evidence_ids": len(seen_ids), "births": len(units), "edges": len(E)}}
