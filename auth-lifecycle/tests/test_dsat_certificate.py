"""Bounded synthetic mathematical proof tests, independent of any optimizer."""
import ast
import copy
import hashlib
import json
from pathlib import Path
from time import perf_counter_ns
import tracemalloc
import unittest
from unittest.mock import patch

from auth_lifecycle.online_state.dsat_projection import project_evidence
from auth_lifecycle.online_state.dsat_types import canonical
from auth_lifecycle.online_state.dsat_flow import (
    assemble_optimum_packet, assemble_infeasible_packet, make_bindings, solve,
)
from dsat_test_support import (
    CHECKER, ROOT, load_case, rebind_fixture, proof_for, rehash_packet,
    CASE_RESULTS, CORE_PACKETS,
)


def _project(case):
    return project_evidence(case["bundle"], case["trusted_manifest"])


def _core_packet(case_id="A06", target="A"):
    case = load_case(case_id)
    return proof_for(case, _project(case), target)


class CoreProofTests(unittest.TestCase):
    def run_core(self, case_id):
        case = load_case(case_id)
        projected = _project(case)
        outcomes = {}
        assembly_ns = verify_ns = total_bytes = 0
        for target in case["manual_proofs"]:
            started = perf_counter_ns()
            packet = proof_for(case, projected, target)
            assembly_ns += perf_counter_ns() - started
            started = perf_counter_ns()
            checked = CHECKER.check_certificate(packet, expected_math_digest=packet["digests"]["math_input_digest"],
                                                expected_scope_digest=packet["digests"]["scope_digest"])
            verify_ns += perf_counter_ns() - started
            total_bytes += len(canonical(packet))
            CORE_PACKETS[case_id + "_" + target] = packet
            self.assertTrue(checked["mathematics_accepted"], checked)
            self.assertFalse(checked["solver_called"])
            self.assertEqual(checked["native_admission"], "SOURCE_OR_REFINEMENT_GAP")
            self.assertFalse(checked["global_complete"])
            if case_id == "A19":
                self.assertEqual(checked["result"], "EVIDENCE_CONFLICT")
                self.assertEqual(checked["cut_capacity"], 3)
                self.assertIsNone(checked["H_T"])
                self.assertTrue(checked["remaining_obligations"])
            else:
                self.assertEqual((checked["R_T"], checked["H_T"]), (0, 0))
                self.assertTrue(checked["conditional_material_closed"])
            if case_id == "A24":
                self.assertIn("await_terminal:i1", checked["remaining_obligations"])
            outcomes[target] = checked
        CASE_RESULTS.setdefault(case_id, {"case_id": case_id}).update(
            manual_certificate_results=outcomes, C_proof_assembly_ns=assembly_ns,
            C_verify_ns=verify_ns, certificate_bytes=total_bytes,
            proof_source="R05_HAND_SPECIFIED_VECTORS_NOT_OPTIMIZER_OUTPUT")

    def test_A01(self):
        self.run_core("A01")

    def test_A06(self):
        self.run_core("A06")

    def test_A19(self):
        self.run_core("A19")

    def test_A24(self):
        self.run_core("A24")


class CertificateVariants(unittest.TestCase):
    def test_missing_one_D_has_positive_H_in_both_targets(self):
        case = load_case("A06")
        case["bundle"]["envelopes"] = [e for e in case["bundle"]["envelopes"] if e["id"] != "syn:d:v1"]
        case["trusted_manifest"] = rebind_fixture(case["bundle"])
        projected = _project(case)
        cert = copy.deepcopy(case["manual_proofs"]["A"])
        cert["d"]["cost"] = 2
        cert["d"]["potentials"] = {"s": -1, "t": 0, "U:b": -1, "U:p": -1,
            "U:v1": 0, "U:v2": -1, "U:v3": -1, "I:i1": 0, "I:i2": 0,
            "I:i_p": 0, "I:i_b": -1, "I:j": -1}
        case["manual_proofs"]["A"] = cert
        packet = proof_for(case, projected, "A")
        checked = CHECKER.check_certificate(packet)
        self.assertTrue(checked["mathematics_accepted"], checked)
        self.assertEqual((checked["R_T"], checked["H_T"]), (0, 1))
        self.assertFalse(checked["conditional_material_closed"])
        CORE_PACKETS["VAR_MISSING_D_A"] = packet
        # For V, route the missing-D witness to j. All used d-costs are zero.
        flow = [["s", "U:b", 1], ["s", "U:p", 1], ["s", "U:v1", 1], ["s", "U:v2", 1], ["s", "U:v3", 1],
                ["U:b", "I:i_b", 1], ["U:p", "I:i_p", 1], ["U:v1", "I:j", 1],
                ["U:v2", "I:i1", 1], ["U:v3", "I:i2", 1], ["I:i1", "t", 1], ["I:i2", "t", 1],
                ["I:i_b", "t", 1], ["I:i_p", "t", 1], ["I:j", "t", 1]]
        cert = copy.deepcopy(case["manual_proofs"]["V"])
        cert["m"]["flow"] = flow
        cert["d"] = {"flow": flow, "potentials": {k: 0 for k in cert["m"]["potentials"]}, "cost": 0}
        case["manual_proofs"]["V"] = cert
        packet = proof_for(case, projected, "V")
        checked = CHECKER.check_certificate(packet)
        self.assertTrue(checked["mathematics_accepted"], checked)
        self.assertEqual((checked["R_T"], checked["H_T"]), (0, 1))
        self.assertFalse(checked["conditional_material_closed"])
        CORE_PACKETS["VAR_MISSING_D_V"] = packet

    def test_fourth_source_breaks_saturation(self):
        case = load_case("A06"); b = case["bundle"]
        origin = dict(b["authority"]["grants"][2]["origin"], grant_id="gZ", task="extra", generation="Z0")
        b["authority"]["grants"].append({"origin": origin, "active": False, "operations": ["issue"], "limit": 1, "reserved": 0, "spent": 1})
        req = copy.deepcopy(b["authority"]["requests"][-1])
        req.update(rid="rZ", attempt_id="aZ", release_version=24, origin=origin)
        req["original_request"].update(rid="rZ", handle="syn_handle_gZ", task="extra", generation="Z0")
        req["request_digest"] = hashlib.sha256(canonical({"caller": origin["caller"], "request": req["original_request"]})).hexdigest()
        b["authority"]["requests"].append(req)
        b["attempts"].append({"id": "z", "rid": "rZ", "capacity_contract_ref": "syn:cap:z", "audit_required": False})
        b["capacity_contracts"].append({"id": "syn:cap:z", "attempt_ref": "z", "capacity": 1, "source_ref": "syn:single_call_source"})
        for e in b["envelopes"]:
            if e["kind"] == "CREATION" and e["payload"]["unit_id"].startswith("v"):
                e["payload"]["source_candidates"].append("z")
        case["trusted_manifest"] = rebind_fixture(b); projected = _project(case)
        common = [["s", "U:b", 1], ["s", "U:p", 1], ["s", "U:v1", 1], ["s", "U:v2", 1], ["s", "U:v3", 1],
                  ["U:b", "I:i_b", 1], ["U:p", "I:i_p", 1], ["U:v1", "I:i1", 1], ["U:v3", "I:z", 1],
                  ["I:i1", "t", 1], ["I:i_b", "t", 1], ["I:i_p", "t", 1], ["I:z", "t", 1]]
        for target, middle, end, cost in [("A", "I:j", "I:j", 2), ("V", "I:i2", "I:i2", 0)]:
            cert = copy.deepcopy(case["manual_proofs"][target])
            flow = common + [["U:v2", middle, 1], [end, "t", 1]]
            pi = dict(cert["m"]["potentials"], **{"I:z": 0})
            cert["m"] = {"flow": flow, "potentials": pi, "cost": cost}
            cert["d"] = copy.deepcopy(cert["m"])
            case["manual_proofs"][target] = cert
            packet = proof_for(case, projected, target)
            checked = CHECKER.check_certificate(packet)
            self.assertTrue(checked["mathematics_accepted"], checked)
            self.assertEqual((checked["R_T"], checked["H_T"]), (1, 1))
            self.assertFalse(checked["conditional_material_closed"])
            CORE_PACKETS["VAR_FOURTH_SOURCE_" + target] = packet

    def test_open_grant_frontier_blocks_conditional_close_even_H_zero(self):
        for kind in ("grant", "derivative"):
            with self.subTest(kind=kind):
                case = load_case("A06")
                if kind == "grant":
                    case["bundle"]["authority"]["creation_paused"] = False
                    case["bundle"]["authority"]["grants"][2].update(active=True, limit=3)
                else:
                    case["bundle"]["contract"].update(frontier_complete=False, derivations_covered=False)
                    case["bundle"]["scope"]["open_frontiers"] = ["frontier:external"]
                case["trusted_manifest"] = rebind_fixture(case["bundle"])
                p = proof_for(case, _project(case), "A")
                r = CHECKER.check_certificate(p)
                self.assertTrue(r["mathematics_accepted"], r)
                self.assertEqual(r["H_T"], 0)
                self.assertFalse(r["conditional_material_closed"])
                self.assertFalse(r["global_complete"])

    def test_empty_witnesses_original_large_capacity_not_zero(self):
        case = load_case("A06"); bindings = make_bindings(case["bundle"], _project(case))
        m = {"I": ["s"], "T": ["s"], "c": {"s": 2 ** 80}, "U": [], "E": [], "D_P": []}
        bindings["scope"]["target_attempts"] = ["s"]
        cert = {"flow": [], "potentials": {"s": 0, "t": 0, "I:s": 0}, "cost": 0}
        r = CHECKER.check_certificate(assemble_optimum_packet(m, bindings, cert, cert))
        self.assertTrue(r["mathematics_accepted"], r)
        self.assertEqual(r["H_T"], 2 ** 80)
        self.assertFalse(r["conditional_material_closed"])

    def test_empty_target_is_only_empty_scope(self):
        p = _core_packet(); m = p["math_input"]; m["T"] = []
        p["bindings"]["scope"]["target_attempts"] = []
        flow = p["proof"]["m"]["flow"]
        cert = {"flow": flow, "potentials": {k: 0 for k in p["proof"]["m"]["potentials"]}, "cost": 0}
        q = assemble_optimum_packet(m, p["bindings"], cert, cert)
        r = CHECKER.check_certificate(q)
        self.assertTrue(r["mathematics_accepted"], r)
        self.assertEqual(r["C_T"], 0)
        self.assertFalse(r["global_complete"])
        self.assertEqual(r["native_admission"], "SOURCE_OR_REFINEMENT_GAP")


class TamperTests(unittest.TestCase):
    def reject(self, packet):
        r = CHECKER.check_certificate(packet)
        self.assertEqual(r["status"], "INVALID_CERTIFICATE", r)
        self.assertFalse(r["mathematics_accepted"])
        self.assertEqual(r["obligation_action"], "KEEP_EXISTING")

    def test_packet_hash_tampering(self):
        p = _core_packet(); p["claims"]["H_T"] = 1
        self.reject(p)

    def test_input_binding_tampering(self):
        p = _core_packet(); p["math_input"]["c"]["i1"] = 2
        self.reject(p)

    def test_rehashed_false_numeric_claim(self):
        p = _core_packet(); p["claims"]["R_T"] = 1
        self.reject(rehash_packet(p))

    def test_zero_flow_cannot_satisfy_nonzero_demand(self):
        p = _core_packet(); p["proof"]["m"]["flow"] = []
        self.reject(rehash_packet(p))

    def test_flow_capacity_tampering(self):
        p = _core_packet(); p["proof"]["d"]["flow"][0][2] = 2
        self.reject(rehash_packet(p))

    def test_illegal_flow_arc(self):
        p = _core_packet(); p["proof"]["d"]["flow"][0][0] = "I:nonexistent"
        self.reject(rehash_packet(p))

    def test_reverse_residual_violation(self):
        p = _core_packet(); p["proof"]["m"]["potentials"]["I:i1"] = 0
        self.reject(rehash_packet(p))

    def test_forward_residual_violation(self):
        p = _core_packet(); p["proof"]["m"]["potentials"].update({"s": -1, "U:v1": -1})
        self.reject(rehash_packet(p))

    def test_missing_potential_node(self):
        p = _core_packet(); del p["proof"]["m"]["potentials"]["U:v3"]
        self.reject(rehash_packet(p))

    def test_flow_and_potential_bool_float_rejected(self):
        for field, val in [("flow", True), ("flow", 1.0), ("potential", False), ("cost", 3.0)]:
            with self.subTest(field=field, val=val):
                p = _core_packet()
                if field == "flow":p["proof"]["m"]["flow"][0][2] = val
                elif field == "potential":p["proof"]["m"]["potentials"]["s"] = val
                else:p["proof"]["m"]["cost"] = val
                self.reject(rehash_packet(p))

    def test_duplicate_and_invalid_E(self):
        for edge in (["v1", "i1"], ["v1", "missing"]):
            p = _core_packet(); p["math_input"]["E"].append(edge)
            self.reject(rehash_packet(p))

    def test_bad_integer_capacity(self):
        for value in (True, 1.0, -1):
            p = _core_packet(); p["math_input"]["c"]["i1"] = value
            self.reject(rehash_packet(p))

    def test_cut_tampering(self):
        p = _core_packet("A19"); p["proof"]["cut"].remove("I:i1")
        self.reject(rehash_packet(p))

    def test_infeasible_flow_value_tampering(self):
        p = _core_packet("A19"); p["proof"]["value"] = 4
        self.reject(rehash_packet(p))

    def test_cut_requires_s_and_excludes_t(self):
        for change in ("remove_s", "include_t"):
            p = _core_packet("A19")
            if change == "remove_s":p["proof"]["cut"].remove("s")
            else:p["proof"]["cut"].append("t")
            self.reject(rehash_packet(p))

    def test_cannot_clear_obligations_or_promote_native(self):
        for field, val in [("remaining_obligations", []), ("global_complete", True), ("native_admission", "CLOSED")]:
            p = _core_packet("A24"); p["claims"][field] = val
            self.reject(rehash_packet(p))

    def test_scope_target_must_match_bound_T(self):
        p = _core_packet(); p["bindings"]["scope"]["target_attempts"] = ["j"]
        self.reject(rehash_packet(p))

    def test_external_pins_reject_self_rehashed_version_or_contract(self):
        for component, field in [("dependency", "dependency_digest"), ("contract", "contract_digest")]:
            p = _core_packet(); pinned = p["digests"][field]
            p["bindings"][component]["source_version"] = "changed_version"
            p["claims"]["conditional_material_closed"] = False
            rehash_packet(p)
            r = CHECKER.check_certificate(p, expected_digests={field: pinned})
            self.assertEqual(r["status"], "INVALID_CERTIFICATE")

    def test_resource_limits_are_unknown_not_infeasibility(self):
        p = _core_packet()
        for lim in ({"input_bytes": 1}, {"edges": 1}, {"witnesses": 1}):
            r = CHECKER.check_certificate(p, limits=lim)
            self.assertEqual(r["status"], "UNKNOWN_RESOURCE_LIMIT")
            self.assertFalse(r["mathematics_accepted"])
        p["math_input"]["c"]["i1"] = 2 ** 129
        r = CHECKER.check_certificate(rehash_packet(p))
        self.assertEqual(r["status"], "UNKNOWN_RESOURCE_LIMIT")

    def test_duplicate_JSON_keys_rejected(self):
        with self.assertRaises(CHECKER.Rejected):
            CHECKER._strict_load('{"a":1,"a":2}')

    def test_independent_checker_has_no_solver_or_runtime_import(self):
        tree = ast.parse((ROOT / "scripts" / "check_dsat_certificate.py").read_text(encoding="utf-8"))
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):names.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):names.append(node.module)
        self.assertTrue(set(names) <= {"argparse", "hashlib", "json", "pathlib", "re"})
        p = _core_packet()
        with patch("builtins.open", side_effect=AssertionError("I/O")), \
             patch.object(Path, "open", side_effect=AssertionError("I/O")):
            r = CHECKER.check_certificate(p)
        self.assertTrue(r["mathematics_accepted"])

    def test_optimizer_execution_not_run_without_dependency(self):
        # R06's exact test identity is retained; it now genuinely exercises S2.
        case = load_case("A06"); p = _project(case)
        r = solve(p["math_input"], bindings=make_bindings(case["bundle"], p))
        self.assertTrue(r["solved"], r)
        self.assertEqual(r["status"], "MATH_OPTIMAL")
        self.assertIn("network_simplex:m", r["metrics"]["backend_calls"])
        self.assertIn("network_simplex:d", r["metrics"]["backend_calls"])
        checked = CHECKER.check_certificate(r["proof_packet"])
        self.assertTrue(checked["mathematics_accepted"], checked)
        self.assertEqual((checked["R_T"], checked["H_T"]), (0, 0))


class AutomaticBackendCases(unittest.TestCase):
    pass


_EXPECTED_A = {"A01": (0, 0), "A02": (1, 1), "A03": (2, 2), "A04": (2, 2),
               "A05": (2, 2), "A06": (0, 0), "A07": (2, 2), "A08": (1, 2),
               "A09": (2, 2), "A10": (2, 2), "A14": (2, 2), "A15": (1, 2),
               "A16": (2, 3), "A17": (2, 3), "A18": (1, 1), "A20": (2, 2),
               "A21": (1, 2), "A22": (2, 2), "A24": (0, 0)}


def _automatic_case(case_id):
    def run(self):
        case = load_case(case_id); projected = _project(case)
        row = CASE_RESULTS.setdefault(case_id, {"case_id": case_id})
        if projected["math_input"] is None:
            self.assertEqual(projected["status"], "REJECT_UNAUTHORIZED")
            row["auto_solver_gate"] = "REJECTED_AT_PROJECTION_NO_SOLVER"
            return
        targets = list(case["manual_proofs"]) or ["A"]
        results = {}; timings = []
        for target in targets:
            mathematical = copy.deepcopy(projected["math_input"])
            if case["manual_proofs"]:
                mathematical["T"] = case["manual_proofs"][target]["T"]
            bindings = make_bindings(case["bundle"], projected)
            bindings["scope"]["target_attempts"] = list(mathematical["T"])
            tracemalloc.start()
            result = solve(mathematical, bindings=bindings)
            _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
            self.assertTrue(result["solved"], result)
            packet = result["proof_packet"]
            t = perf_counter_ns(); checked = CHECKER.check_certificate(packet,
                expected_math_digest=result["math_input_digest"], expected_scope_digest=packet["digests"]["scope_digest"])
            verify_ns = perf_counter_ns() - t
            self.assertTrue(checked["mathematics_accepted"], checked)
            self.assertEqual(checked["native_admission"], "SOURCE_OR_REFINEMENT_GAP")
            self.assertFalse(checked["global_complete"])
            self.assertTrue({o["id"] for o in case["bundle"]["obligations"]} <= set(checked["remaining_obligations"]))
            if case_id == "A19":
                self.assertEqual(checked["result"], "EVIDENCE_CONFLICT")
                self.assertEqual(checked["cut_capacity"], 3)
                self.assertIsNone(checked["H_T"])
            else:
                self.assertEqual((checked["R_T"], checked["H_T"]), _EXPECTED_A[case_id] if target == "A" else (0, 0))
            if case_id in {"A05", "A07", "A10", "A14", "A20", "A22"}:
                self.assertFalse(checked["conditional_material_closed"])
            if case_id == "A24":
                self.assertIn("await_terminal:i1", checked["remaining_obligations"])
            CORE_PACKETS["AUTO_" + case_id + "_" + target] = packet
            results[target] = checked
            timings.append({"target": target, **result["metrics"], "C_flow_ns": result["C_flow_ns"],
                            "C_verify_ns": verify_ns, "solver_traced_peak_bytes": peak,
                            "input_bytes": len(canonical(mathematical)), "certificate_bytes": len(canonical(packet)),
                            "network_nodes": result["network_nodes"], "network_arcs": result["network_arcs"]})
        row["automatic_certificate_results"] = results
        row["automatic_solver_metrics"] = timings
        row["automatic_backend"] = "NetworkX3.7_builtin"
    return run


for _case_id in [f"A{i:02d}" for i in range(1, 25)]:
    setattr(AutomaticBackendCases, "test_auto_" + _case_id, _automatic_case(_case_id))


class AutomaticBackendSpecific(unittest.TestCase):
    def verify_model(self, mathematical, expected_R_H=None, conflict=False, bindings=None):
        if bindings is None:
            case = load_case("A06"); bindings = make_bindings(case["bundle"], _project(case))
            bindings["scope"]["target_attempts"] = list(mathematical["T"])
            # Boundary-only models are mathematical, without a real native-source assertion.
            bindings["scope"]["coverage_complete"] = False
        r = solve(mathematical, bindings=bindings)
        self.assertTrue(r["solved"], r)
        checked = CHECKER.check_certificate(r["proof_packet"])
        self.assertTrue(checked["mathematics_accepted"], checked)
        if conflict:
            self.assertEqual(r["status"], "EVIDENCE_CONFLICT")
            self.assertLess(checked["cut_capacity"], checked["required_flow"])
        elif expected_R_H is not None:
            self.assertEqual((r["R_T"], r["H_T"]), expected_R_H)
        self.assertFalse(checked["global_complete"])
        return r

    def test_auto_empty_U_keeps_original_capacity(self):
        self.verify_model({"I": ["a"], "T": ["a"], "c": {"a": 2 ** 80}, "U": [], "E": [], "D_P": []}, (2 ** 80, 2 ** 80))

    def test_auto_empty_T(self):
        m = _project(load_case("A06"))["math_input"]; m["T"] = []
        self.verify_model(m, (0, 0))

    def test_auto_zero_capacity(self):
        self.verify_model({"I": ["a"], "T": ["a"], "c": {"a": 0}, "U": ["u"], "E": [["u", "a"]], "D_P": []}, conflict=True)

    def test_auto_capacity_above_h_is_not_used_for_C_T(self):
        self.verify_model({"I": ["a"], "T": ["a"], "c": {"a": 2 ** 80}, "U": ["u", "v"], "E": [["u", "a"], ["v", "a"]], "D_P": ["u", "v"]}, (2 ** 80 - 2, 2 ** 80 - 2))

    def test_auto_missing_E_yields_cut(self):
        self.verify_model({"I": ["a"], "T": ["a"], "c": {"a": 2}, "U": ["u", "v"], "E": [["u", "a"]], "D_P": []}, conflict=True)

    def test_auto_same_identifier_in_both_namespaces(self):
        self.verify_model({"I": ["s"], "T": ["s"], "c": {"s": 1}, "U": ["s"], "E": [["s", "s"]], "D_P": ["s"]}, (0, 0))

    def test_auto_missing_D_in_both_targets(self):
        case = load_case("A06"); case["bundle"]["envelopes"] = [e for e in case["bundle"]["envelopes"] if e["id"] != "syn:d:v1"]
        case["trusted_manifest"] = rebind_fixture(case["bundle"]); p = _project(case)
        for target in [["i1", "i2", "i_p"], ["j"]]:
            m = dict(p["math_input"], T=target); b = make_bindings(case["bundle"], p); b["scope"]["target_attempts"] = target
            r = self.verify_model(m, (0, 1), bindings=b)
            self.assertFalse(r["proof_packet"]["claims"]["conditional_material_closed"])

    def test_auto_fourth_source(self):
        m = copy.deepcopy(_project(load_case("A06"))["math_input"])
        m["I"].append("z"); m["c"]["z"] = 1
        for u in ["v1", "v2", "v3"]:m["E"].append([u, "z"])
        for target in [["i1", "i2", "i_p"], ["j"]]:
            self.verify_model(dict(m, T=target), (1, 1))

    def test_auto_open_frontier_even_saturated(self):
        for flag in ("frontier", "source", "derivative"):
            case = load_case("A06")
            if flag == "frontier":case["bundle"]["scope"]["open_frontiers"] = ["frontier:new_grant"]
            elif flag == "source":case["bundle"]["contract"]["source_complete"] = False
            else:case["bundle"]["contract"].update(derivations_covered=False, frontier_complete=False)
            case["trusted_manifest"] = rebind_fixture(case["bundle"]); p = _project(case)
            r = self.verify_model(p["math_input"], (0, 0), bindings=make_bindings(case["bundle"], p))
            self.assertFalse(r["proof_packet"]["claims"]["conditional_material_closed"])

    def test_auto_resource_and_bad_integer_rejection(self):
        from auth_lifecycle.online_state.dsat_types import Limits
        m = _project(load_case("A06"))["math_input"]
        self.assertEqual(solve(m, Limits(edges=1))["status"], "UNKNOWN_RESOURCE_LIMIT")
        for bad in (True, 1.0, -1):
            x = copy.deepcopy(m); x["c"]["i1"] = bad
            self.assertEqual(solve(x)["status"], "INVALID_INPUT")

    def test_auto_tamper_flows_potentials_and_pins(self):
        case = load_case("A06"); p = _project(case)
        original = self.verify_model(p["math_input"], (0, 0), bindings=make_bindings(case["bundle"], p))["proof_packet"]
        for change in ("flow", "potential", "hash", "obligations", "native", "dependency", "scope"):
            q = copy.deepcopy(original); pins = None
            if change == "flow":q["proof"]["m"]["flow"][0][2] = 2
            elif change == "potential":q["proof"]["d"]["potentials"]["t"] -= 100
            elif change == "hash":q["claims"]["m_T"] += 1
            elif change == "obligations":q["claims"]["remaining_obligations"] = []
            elif change == "native":q["claims"]["native_admission"] = "CLOSED"
            elif change == "dependency":
                pins = {"dependency_digest": original["digests"]["dependency_digest"]};q["bindings"]["dependency"]["authority_version"] += 1
            else:
                pins = {"scope_digest": original["digests"]["scope_digest"]};q["bindings"]["scope"]["paths"].append("new_path")
            rehash_packet(q)
            self.assertEqual(CHECKER.check_certificate(q, expected_digests=pins)["status"], "INVALID_CERTIFICATE", change)

    def test_auto_tampered_cut_rejected(self):
        case = load_case("A19"); p = _project(case)
        q = self.verify_model(p["math_input"], conflict=True, bindings=make_bindings(case["bundle"], p))["proof_packet"]
        q["proof"]["cut"].append("t"); rehash_packet(q)
        self.assertEqual(CHECKER.check_certificate(q)["status"], "INVALID_CERTIFICATE")

    def test_false_backend_infeasible_is_not_accepted_without_cut(self):
        from auth_lifecycle.online_state.dsat_flow import _load_backend
        nx = _load_backend(); m = _project(load_case("A06"))["math_input"]
        with patch.object(nx, "network_simplex", side_effect=nx.NetworkXUnfeasible()):
            r = solve(m)
        self.assertEqual(r["status"], "UNVERIFIED_INFEASIBILITY")
        self.assertFalse(r["solved"])

    def test_failed_or_invalid_potential_stops_proof(self):
        from auth_lifecycle.online_state.dsat_flow import _load_backend
        nx = _load_backend(); m = _project(load_case("A06"))["math_input"]
        with patch.object(nx, "single_source_bellman_ford_path_length", side_effect=nx.NetworkXUnbounded()):
            r = solve(m)
        self.assertEqual(r["status"], "INVALID_CERTIFICATE")
        self.assertFalse(r["solved"])
