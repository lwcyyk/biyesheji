"""Development regressions through the authenticated controller entry point."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import unittest

from auth_lifecycle.online_state.lab import Laboratory, approval, request_for
from auth_lifecycle.online_state.protocol import Client
from auth_lifecycle.online_state.storage import AuthorityStore
from auth_lifecycle.online_state.services import SingleActive


class OnlineStateTests(unittest.TestCase):
    def setUp(self):
        default = Path(__file__).resolve().parents[2] / "mainline_online_state_v1" / "dev_work"
        self.parent = Path(os.environ.get("ONLINE_STATE_TEST_ROOT", default))
        self.parent.mkdir(parents=True, exist_ok=True)
        self.lab = Laboratory(self.parent / (self._testMethodName + "_" + secrets.token_hex(4)))
        self.addCleanup(self.lab.close)
        self.lab.start_all()
        self.user = self.lab.client()
        self.a = self.user.call("grant", approval("A", "g0", 3))
        self.b = self.user.call("grant", approval("B", "g1", 3))
        self.assertEqual(self.a["status"], "GRANTED")
        self.assertEqual(self.b["status"], "GRANTED")

    def request_a(self, rid="A1"):
        return request_for(self.a["handle"], "A", "g0", rid)

    def request_b(self, rid="B1"):
        return request_for(self.b["handle"], "B", "g1", rid)

    def revoke_a(self, operation="revokeA"):
        return self.user.call("revoke", {"revoke_op": operation, "grant_id": self.a["grant_id"]})

    def status(self):
        result = self.user.call("status", {})
        self.assertEqual(result["status"], "RECOVERED")
        return result

    def test_normal_entry_and_secret_projection(self):
        result = self.lab.client("agentA").call("call", self.request_a())
        self.assertEqual(result["status"], "RESULT_AVAILABLE")
        public = json.dumps([self.a, self.b, result, self.status()])
        self.assertNotIn("synthetic_initial", public)
        self.assertNotIn("synthetic_result", public)
        self.assertNotIn("synthetic_debug", public)
        self.assertEqual(self.revoke_a()["status"], "LOCAL_REVOKE_COMMITTED")
        self.assertEqual(self.lab.client("agentA").call("call", self.request_a("A2"))["status"], "REJECTED")
        self.assertEqual(self.lab.client("agentB").call("call", self.request_b())["status"], "RESULT_AVAILABLE")

    def test_binding_caller_task_account_audience_generation_operation(self):
        request = self.request_a()
        self.assertEqual(self.lab.client("agentB").call("call", request)["status"], "REJECTED")
        for field in ("task", "account", "audience", "generation", "operation"):
            with self.subTest(field=field):
                altered = {**self.request_a(field), field: "wrong"}
                self.assertEqual(self.lab.client("agentA").call("call", altered)["status"], "REJECTED")
        extra = {**self.request_a("caller_field"), "caller": "agentB"}
        self.assertEqual(self.lab.client("agentA").call("call", extra)["status"], "REJECTED")
        config = self.lab.configs["controller"]
        denied = Client("https://127.0.0.1:" + str(config["port"]), "wrong", config["certificate"])
        self.assertEqual(denied.call("status", {})["status"], "REJECTED")
        self.assertEqual(self.lab.client("agentA").call("grant", approval("A", "g2"))["status"], "REJECTED")

    def test_rid_duplicate_and_body_conflict(self):
        request = self.request_a()
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(lambda _: self.lab.client("agentA").call("call", request), range(5)))
        self.assertTrue(any(r.get("phase") == "RESULT_AVAILABLE" for r in results))
        conflict = {**request, "payload": {"value": 2}}
        self.assertEqual(self.lab.client("agentA").call("call", conflict)["status"], "CONFLICT")
        state = self.status()
        self.assertEqual(len(state["requests"]), 1)
        grant = next(g for g in state["approvals"] if g["task"] == "A")
        self.assertEqual((grant["reserved"], grant["spent"]), (0, 1))
        truth = (self.lab.root / "provider" / "truth.jsonl").read_text().splitlines()
        self.assertEqual(len(truth), 1)

    def test_concurrent_budget(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda i: self.lab.client("agentA").call("call", self.request_a("r" + str(i))), range(8)))
        self.assertEqual(sum(r["status"] == "RESULT_AVAILABLE" for r in results), 3)
        grant = next(g for g in self.status()["approvals"] if g["task"] == "A")
        self.assertEqual((grant["reserved"], grant["spent"]), (0, 3))

    def test_admission_revoke_compete_at_queue_boundary(self):
        self.lab.restart_controller("after_admit")
        pending = self.lab.async_call("agentA", "call", self.request_a())
        barrier = self.lab.wait_barrier("after_admit")
        ack = self.revoke_a()
        self.assertEqual(ack["status"], "LOCAL_REVOKE_COMMITTED")
        barrier.with_suffix(".release").touch()
        self.assertFalse(pending.result(timeout=5).get("send", False))
        state = self.status()
        self.assertEqual(state["requests"][0]["phase"], "CANCELLED")
        grant = next(g for g in state["approvals"] if g["task"] == "A")
        self.assertEqual((grant["reserved"], grant["spent"]), (0, 0))

    def test_release_before_revoke_is_pending_then_quarantined(self):
        self.lab.restart_controller("after_release")
        pending = self.lab.async_call("agentA", "call", self.request_a())
        barrier = self.lab.wait_barrier("after_release")
        ack = self.revoke_a()
        self.assertEqual(ack["status"], "LOCAL_REVOKE_COMMITTED")
        self.assertEqual(self.status()["requests"][0]["phase"], "DISPATCHED_UNKNOWN")
        barrier.with_suffix(".release").touch()
        result = pending.result(timeout=5)
        self.assertEqual(result["status"], "QUARANTINED")
        self.assertLess(result["release_version"], ack["commit_version"])

    def test_revocation_ack_loss_and_idempotent_recovery(self):
        self.lab.restart_controller("after_revoke_commit")
        pending = self.lab.async_call("user", "revoke", {"revoke_op": "lost_ack", "grant_id": self.a["grant_id"]})
        self.lab.wait_barrier("after_revoke_commit")
        self.lab.restart_controller()
        self.assertEqual(pending.result(timeout=5)["status"], "UNKNOWN")
        first = self.revoke_a("lost_ack")
        second = self.revoke_a("lost_ack")
        self.assertEqual(first["commit_version"], second["commit_version"])
        self.assertEqual(self.lab.client("agentA").call("call", self.request_a())["status"], "REJECTED")

    def test_release_crash_never_automatically_resends_and_B_recovers(self):
        self.lab.restart_controller("after_release")
        pending = self.lab.async_call("agentA", "call", self.request_a())
        self.lab.wait_barrier("after_release")
        self.lab.restart_controller()
        pending.result(timeout=5)
        self.assertEqual(self.revoke_a()["status"], "LOCAL_REVOKE_COMMITTED")
        repeat = self.lab.client("agentA").call("call", self.request_a())
        self.assertEqual(repeat["phase"], "DISPATCHED_UNKNOWN")
        self.assertFalse((self.lab.root / "provider" / "truth.jsonl").exists())
        self.assertEqual(self.lab.client("agentB").call("call", self.request_b())["status"], "RESULT_AVAILABLE")
        self.assertIn("A1", self.status()["obligations"])

    def test_effect_crash_late_and_duplicate_result_binding(self):
        self.lab.restart_controller("after_effect")
        pending = self.lab.async_call("agentA", "call", self.request_a())
        self.lab.wait_barrier("after_effect")
        self.lab.restart_controller()
        pending.result(timeout=5)
        self.revoke_a()
        first = self.user.call("deliver", {"rid": "A1"})
        second = self.user.call("deliver", {"rid": "A1"})
        self.assertEqual(first["status"], "QUARANTINED")
        self.assertEqual(second["status"], "RESULT_DUPLICATE")
        self.assertEqual(first["origin"]["generation"], "g0")
        new_grant = self.user.call("grant", approval("A", "g2"))
        self.assertNotEqual(new_grant["grant_id"], self.a["grant_id"])
        self.assertEqual(self.user.call("deliver", {"rid": "A1"})["origin"]["generation"], "g0")

    def test_old_cache_restore_authority_outage_and_key_unavailability(self):
        snapshot = self.lab.snapshot_cache()
        self.revoke_a()
        self.lab.stop("controller")
        self.lab.restore_cache(snapshot)
        self.lab.stop("authority")
        self.lab.start("controller")
        self.assertEqual(self.user.call("recover", {})["status"], "UNKNOWN")
        self.assertEqual(self.lab.client("agentB").call("call", self.request_b())["status"], "UNKNOWN")
        self.lab.start("authority")
        self.assertEqual(self.user.call("recover", {})["status"], "RECOVERED")
        self.assertEqual(self.lab.client("agentA").call("call", self.request_a())["status"], "REJECTED")
        key = self.lab.root / "secure" / "authority.key"
        saved = key.with_suffix(".saved")
        key.rename(saved)
        try:
            self.assertEqual(self.user.call("recover", {})["status"], "UNKNOWN")
        finally:
            saved.rename(key)
        self.assertEqual(self.user.call("recover", {})["status"], "RECOVERED")
        self.assertEqual(self.lab.client("agentB").call("call", self.request_b())["status"], "RESULT_AVAILABLE")

    def test_conflicting_provider_result_and_transaction_rollback(self):
        self.lab.client("fixture", "provider").call("hold", {"enabled": True})
        self.lab.client("agentA").call("call", self.request_a())
        req = self.status()["requests"][0]
        envelope = {key: req[key] for key in ("rid", "digest", "origin", "attempt_id", "release_version")}
        envelope.update(material="synthetic_bad", outcome="OK")
        envelope["origin"] = {**envelope["origin"], "generation": "g1"}
        config = self.lab.configs["authority"]
        authority = Client("https://127.0.0.1:" + str(config["port"]), config["identities"]["controller"], config["certificate"])
        self.assertEqual(authority.call("record", envelope)["status"], "CONFLICT")
        self.assertEqual(self.user.call("deliver", {"rid": "A1"})["status"], "RESULT_AVAILABLE")
        unit = self.lab.root / "transaction_regression"
        store = AuthorityStore(unit, self.lab.root / "secure" / "authority.key")
        original = store.execute
        def fail_before_event(statement, parameters=()):
            if statement.startswith("INSERT INTO authority_events"):
                raise RuntimeError("synthetic secret must stay out of errors")
            return original(statement, parameters)
        store.execute = fail_before_event
        self.assertEqual(store.call("grant", approval("A", "g0"))["status"], "UNKNOWN")
        store.execute = original
        self.assertEqual(store.call("recover", {})["approvals"], [])
        store.connection.close()

    def test_single_active_lock_is_held_by_running_controller(self):
        with self.assertRaises(OSError):
            SingleActive(self.lab.root / "secure" / "controller.lock")

    def test_independent_scorer_detects_wrong_source(self):
        self.lab.client("agentA").call("call", self.request_a())
        self.revoke_a()
        rejected = self.lab.client("agentA").call("call", self.request_a("A_after_ack"))
        b = self.lab.client("agentB").call("call", self.request_b())
        self.lab.close()
        outcome = {"scenario": "normal", "post_ack_A": rejected, "B_result": b,
                   "elapsed_seconds": 1, "B_after_recovery_seconds": 0.1}
        (self.lab.root / "runner" / "outcome.json").write_text(json.dumps(outcome))
        scorer = Path(__file__).resolve().parents[1] / "scripts" / "score_online_state.py"
        command = [sys.executable, "-B", str(scorer), "--root", str(self.lab.root)]
        result = subprocess.run(command, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        altered_root = self.parent / ("tampered_" + secrets.token_hex(6))
        shutil.copytree(self.lab.root, altered_root)
        truth = altered_root / "provider" / "truth.jsonl"
        events = [json.loads(line) for line in truth.read_text().splitlines()]
        events[0]["origin"]["generation"] = "g1"
        truth.write_text("\n".join(json.dumps(row) for row in events) + "\n")
        result = subprocess.run([sys.executable, "-B", str(scorer), "--root", str(altered_root)], capture_output=True)
        scored = json.loads((altered_root / "scorer" / "result.json").read_text())
        self.assertEqual(result.returncode, 1)
        self.assertEqual(scored["status"], "SAFETY_FAILURE")
        self.assertIn("every_provider_effect_has_matching_durable_release",
                      [row["name"] for row in scored["checks"] if not row["pass"]])


if __name__ == "__main__":
    unittest.main()
