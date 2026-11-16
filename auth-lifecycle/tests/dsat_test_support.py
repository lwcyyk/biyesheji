"""Synthetic-only fixtures and independently loaded pure checker for R06 tests."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

from auth_lifecycle.online_state.dsat_types import canonical, digest, math_digest, packet_digest
from auth_lifecycle.online_state.dsat_flow import make_bindings, assemble_optimum_packet, assemble_infeasible_packet


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "dsat"
spec = importlib.util.spec_from_file_location("dsat_independent_checker", ROOT / "scripts" / "check_dsat_certificate.py")
CHECKER = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CHECKER)
CASE_RESULTS = {}
CORE_PACKETS = {}


def load_case(case_id):
    return json.loads((FIXTURES / (case_id + ".json")).read_text(encoding="utf-8"))


def rebind_fixture(bundle):
    """Explicit synthetic test authority, never called by the projection on payloads."""
    return {"mode": "SYNTHETIC_CONTRACT", "snapshot_digest": digest("snapshot", bundle["authority"]),
            "contract_digest": digest("projection_contract", {k: bundle[k] for k in
                  ("contract", "scope", "attempts", "capacity_contracts")}),
            "obligations_digest": digest("O_before", bundle["obligations"]),
            "costs_digest": digest("cost_ledger", bundle["costs"]),
            "envelope_digests": {e["id"]: digest("envelope", e) for e in bundle["history"] + bundle["envelopes"]},
            "producers": ["syn:collector"], "permits": ["syn:permit"]}


def proof_for(case, projection, target="A"):
    supplied = case["manual_proofs"][target]
    math_input = copy.deepcopy(projection["math_input"])
    math_input["T"] = supplied["T"]
    bindings = make_bindings(case["bundle"], projection)
    bindings["scope"]["target_attempts"] = list(supplied["T"])
    if supplied["kind"] == "INFEASIBLE":
        return assemble_infeasible_packet(math_input, bindings, supplied["flow"], supplied["cut"], supplied["value"])
    return assemble_optimum_packet(math_input, bindings, supplied["m"], supplied["d"])


def rehash_packet(packet):
    """Test attack helper: update hashes so semantic checks, not only hashes, run."""
    packet["digests"]["math_input_digest"] = math_digest(packet["math_input"])
    for component, field in {"evidence_bundle": "evidence_bundle_digest", "contract": "contract_digest",
                             "scope": "scope_digest", "dependency": "dependency_digest",
                             "cost_ledger": "cost_ledger_digest", "O_before": "O_before_digest"}.items():
        packet["digests"][field] = digest(component, packet["bindings"][component])
    packet["packet_digest"] = packet_digest(packet)
    return packet
