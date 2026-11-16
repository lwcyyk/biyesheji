"""Synthetic tests. NativeHTTP network sends are always mocked here."""

import base64
import hashlib
import io
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
import subprocess
import sys
import time
import unittest
from unittest.mock import Mock

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from auth_lifecycle.online_state.lab import initialize
from auth_lifecycle.online_state.materials import token_bundle, validate_material
from auth_lifecycle.online_state.native_http import NativeHTTP, create_budget
from auth_lifecycle.online_state.native_provider import CasdoorProvider
from auth_lifecycle.online_state.protocol import InvalidInput, canonical, normalized_request, write_json
from auth_lifecycle.online_state.storage import AuthorityStore


def b64(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


class NativeAdapterTests(unittest.TestCase):
    def setUp(self):
        parent = Path(os.environ.get("NATIVE_TEST_ROOT", Path(__file__).resolve().parents[2] / "mainline_native_casdoor_v1/dev_work"))
        parent.mkdir(parents=True, exist_ok=True)
        self.root = initialize(parent / (self._testMethodName + "_" + secrets.token_hex(4)))
        self.name = "l1-m2-synthetic-1"
        create_budget(self.root, "synthetic-development-only", [self.name])
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.signing_key = key
        numbers = key.public_key().public_numbers()
        self.profile = {"enabled": True, "version": "4.25.0", "base": "http://127.0.0.1:18081",
            "client_id": "l1-client-0", "client_secret": "synthetic_client_secret",
            "actor": {"id": "synthetic_account", "name": self.name, "password": "synthetic_password"}, "batch": str(self.root), "durable_inbox": True,
            "jwks": {"keys": [{"kid": "fixture", "kty": "RSA", "n": b64(numbers.n.to_bytes(256, "big")),
                                 "e": b64(numbers.e.to_bytes(3, "big"))}]}}
        self.body = {"access_token": self.jwt(True), "refresh_token": self.jwt(False),
                     "token_type": "Bearer", "scope": "openid", "expires_in": 3600}
        write_json(self.root / "secure/native_profile.json", self.profile)

    def jwt(self, kid=True, subject="synthetic_account", client="l1-client-0"):
        header = {"alg": "RS256", "typ": "JWT"}
        if kid:header["kid"] = "fixture"
        claims = {"iss": "http://127.0.0.1:18081", "sub": subject, "aud": [client],
                  "exp": int(time.time()) + 3600, "iat": int(time.time()), "jti": secrets.token_hex(5)}
        signed = b64(canonical(header)) + "." + b64(canonical(claims))
        return signed + "." + b64(self.signing_key.sign(signed.encode(), padding.PKCS1v15(), hashes.SHA256()))

    def store(self, folder="authority_test"):
        store = AuthorityStore(self.root / folder, self.root / "secure/authority.key")
        self.addCleanup(store.connection.close)
        return store

    def test_bundle_signature_binding_missing_fields_and_refresh_kid(self):
        material = token_bundle(self.body, self.profile)
        self.assertEqual(material["derived"]["verified_refresh_claims"]["sub"], "synthetic_account")
        for field in ("access_token", "refresh_token", "token_type", "expires_in"):
            damaged = dict(self.body);damaged.pop(field)
            with self.assertRaises(InvalidInput):token_bundle(damaged, self.profile)
        for body in [{**self.body, "access_token": self.jwt(subject="other")},
                     {**self.body, "access_token": self.jwt(client="other")},
                     {**self.body, "refresh_token": self.jwt(False, subject="other")}]:
            with self.assertRaises(InvalidInput):token_bundle(body, self.profile)
        with self.assertRaises(InvalidInput):validate_material(material, "wrong_account", "l1-client-0")

    def test_bundle_encrypted_state_and_recovery(self):
        store = self.store()
        material = token_bundle(self.body, self.profile)
        payload = {"approval_op": "approve", "caller": "agentA", "task": "A", "account": "synthetic_account",
                   "audience": "l1-client-0", "generation": "g0", "operations": ["issue"], "budget": 2, "material": material}
        self.assertEqual(store.call("grant", payload)["status"], "GRANTED")
        _, state = store.read_state()
        self.assertEqual(next(iter(state["grants"].values()))["material"], material)
        projection = canonical(store.call("recover", {}))
        self.assertNotIn(self.body["access_token"].encode(), projection)
        for file in (self.root / "authority_test").glob("authority.db*"):
            self.assertNotIn(self.body["refresh_token"].encode(), file.read_bytes())

    def test_schema_one_copy_preserves_original_and_legacy_material(self):
        original = self.store("old")
        payload = {"approval_op": "old", "caller": "agentA", "task": "A", "account": "account1", "audience": "fake_rp",
                   "generation": "g0", "operations": ["use"], "budget": 1, "material": "synthetic_legacy"}
        original.call("grant", payload)
        original.connection.execute("PRAGMA user_version=1")
        copy_dir = self.root / "copy";copy_dir.mkdir()
        backup = sqlite3.connect(copy_dir / "authority.db")
        original.connection.backup(backup);backup.close()
        before = original.call("recover", {})
        migrated = self.store("copy")
        self.assertEqual(migrated.connection.execute("PRAGMA user_version").fetchone()[0], 2)
        self.assertEqual(migrated.call("recover", {}), before)
        self.assertEqual(original.connection.execute("PRAGMA user_version").fetchone()[0], 1)

    def test_profile_denies_wrong_endpoints_account_client_and_extra_fields(self):
        with self.assertRaises(InvalidInput):NativeHTTP(self.root, "method")
        client = NativeHTTP(self.root, "method", enabled=True)
        client.opener.open = Mock(side_effect=AssertionError("network must remain unused"))
        for operation, kwargs in [("https://example.com", {}), ("userinfo", {"actor": "other"}),
            ("refresh", {"actor": self.name, "form": {"client_id": "wrong"}}),
            ("userinfo", {"actor": self.name, "headers": {"Cookie": "synthetic_cookie"}})]:
            with self.assertRaises(InvalidInput):client.call(operation, **kwargs)
        self.assertFalse(client.opener.open.called)

    def test_transport_errors_and_parse_failure_are_charged_without_retry(self):
        client = NativeHTTP(self.root, "method", enabled=True)
        for error in (TimeoutError(), ConnectionResetError()):
            client.opener.open = Mock(side_effect=error)
            result = client.call("userinfo", actor=self.name)
            self.assertEqual(result["http"], 0)
            self.assertEqual(client.opener.open.call_count, 1)
        answer = io.BytesIO(b"not-json");answer.status = 200
        client.opener.open = Mock(return_value=answer)
        result = client.call("userinfo", actor=self.name)
        self.assertEqual(result["error_type"], "ResponseParseFailure")
        with sqlite3.connect(self.root / "native_budget.db") as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM requests").fetchone()[0], 3)

    def test_gateway_inbox_binding_and_no_inbox_unknown(self):
        for enabled in (False, True):
            self.profile["durable_inbox"] = enabled
            write_json(self.root / "secure/native_profile.json", self.profile)
            gateway = CasdoorProvider(self.root, {"native_profile": str(self.root / "secure/native_profile.json")})
            gateway.http = Mock()
            gateway.http.call.return_value = {"http": 200, "body": self.body, "error_type": None, "sequence": 1}
            source = {"rid": "A0", "digest": "d", "attempt_id": "attempt", "release_version": 3,
                      "origin": {"account": "synthetic_account", "audience": "l1-client-0", "task": "A", "generation": "g0"}}
            login = {"schema": 2, "kind": "casdoor_login", "issuer": self.profile["base"], "client": "l1-client-0",
                     "expected_account": "synthetic_account", "username": self.name, "password": "synthetic_password"}
            result = gateway.call("perform", {**source, "operation": "issue", "payload": {}, "material": login}, "adapter")
            self.assertEqual(result["status"], "PROVIDER_RESULT")
            queried = gateway.call("lookup", source, "adapter")
            self.assertEqual(queried["status"], "PROVIDER_RESULT" if enabled else "UNKNOWN")
            if enabled:
                altered = {**source, "origin": {**source["origin"], "generation": "g1"}}
                self.assertEqual(gateway.call("lookup", altered, "adapter")["status"], "CONFLICT")

    def test_native_payload_references_and_disposal_only_after_revoke(self):
        request = {"rid": "A0", "handle": "h", "task": "A", "account": "synthetic_account", "audience": "l1-client-0",
                   "generation": "g0", "operation": "issue", "payload": {}}
        self.assertEqual(normalized_request(request)["payload"], {})
        with self.assertRaises(InvalidInput):normalized_request({**request, "payload": {"url": "http://example.com"}})
        store = self.store()
        self.assertEqual(store.call("prepare_disposal", {"disposal_op": "d", "rid": "unknown"})["status"], "UNKNOWN")

    def test_synthetic_native_scorer_positive_and_bad_acceptance_negative(self):
        store = self.store("authority")
        gateway = CasdoorProvider(self.root, {"native_profile": str(self.root / "secure/native_profile.json")})
        gateway.http = Mock()
        grants = {}
        for task, generation in (("A", "g0"), ("B", "g1")):
            login = {"schema": 2, "kind": "casdoor_login", "issuer": self.profile["base"], "client": "l1-client-0",
                     "expected_account": "synthetic_account", "username": self.name, "password": "synthetic_password"}
            grants[task] = store.call("grant", {"approval_op": task, "caller": "agent" + task, "task": task,
                "account": "synthetic_account", "audience": "l1-client-0", "generation": generation,
                "operations": ["issue"], "budget": 2, "material": login})
            req = {"rid": task + "0", "handle": grants[task]["handle"], "task": task, "account": "synthetic_account",
                   "audience": "l1-client-0", "generation": generation, "operation": "issue", "payload": {}}
            admitted = store.call("admit", {"caller": "agent" + task, "request": req})
            released = store.call("release", {"caller": "agent" + task, "rid": task + "0", "digest": admitted["digest"]})
            body = {**self.body, "access_token": self.jwt(), "refresh_token": self.jwt(False)}
            gateway.http.call.return_value = {"http": 200, "body": body, "error_type": None, "sequence": 1 if task == "A" else 2}
            result = gateway.call("perform", {k: released[k] for k in
                ("rid", "digest", "origin", "attempt_id", "release_version", "material", "operation", "payload")}, "adapter")
            recorded = store.call("record", {k: result[k] for k in
                ("rid", "digest", "origin", "attempt_id", "release_version", "material", "outcome")})
            self.assertEqual(recorded["status"], "RESULT_AVAILABLE")
        store.call("revoke", {"revoke_op": "r", "grant_id": grants["A"]["grant_id"]})
        store.call("prepare_disposal", {"disposal_op": "d", "rid": "A0"})
        store.call("record_disposal", {"disposal_op": "d", "rid": "A0", "http": 200,
                   "userinfo_http": 401, "userinfo_accepted": False, "introspection_active": False})
        initial = {"rows": [{"rid": "A0", "accepted": True}, {"rid": "B0", "accepted": True}], "native_units": []}
        final = {"rows": [{"rid": "A0", "accepted": False, "runner_has_result": True, "refresh_rejected": True},
                          {"rid": "B0", "accepted": True, "runner_has_result": True}], "native_units": []}
        for obj in (initial, final):
            for row in obj["rows"]:row.update(access_ref=row["rid"] + "at", refresh_ref=row["rid"] + "rt")
        write_json(self.root / "scorer/initial_native.json", initial)
        write_json(self.root / "scorer/final_native.json", final)
        write_json(self.root / "runner/outcome.json", {"status": "OBSERVED", "scenario": "M2-01",
                   "A_after_ack": {"status": "REJECTED"}, "B_continue": {"status": "RESULT_AVAILABLE"}})
        (self.root / "control/processes.jsonl").write_text('\n'.join(json.dumps(x) for x in
            [{"event": "started", "child_pid": 1}, {"event": "terminated_and_waited", "child_pid": 1}]) + '\n')
        script = Path(__file__).resolve().parents[1] / "scripts/score_native_casdoor.py"
        result = subprocess.run([sys.executable, "-B", str(script), "--case", str(self.root)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        final["rows"][0]["accepted"] = True
        write_json(self.root / "scorer/final_native.json", final)
        result = subprocess.run([sys.executable, "-B", str(script), "--case", str(self.root)], capture_output=True)
        self.assertEqual(result.returncode, 1)
        verdict = json.loads((self.root / "scorer/result.json").read_text())
        self.assertEqual(verdict["status"], "SAFETY_FAILURE")

    def test_recovery_scorer_accepts_config_restart_and_requires_fault_exit(self):
        script = Path(__file__).resolve().parents[1] / "scripts/score_native_casdoor.py"
        spec = importlib.util.spec_from_file_location("independent_native_scorer", script)
        scorer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scorer)
        events = []
        for pid in (10, 20, 30):
            events += [{"event": "started", "role": "controller", "child_pid": pid},
                       {"event": "terminated_and_waited", "role": "controller", "child_pid": pid}]
        self.assertTrue(scorer.recovery_evidence(events, "M2-03", 20))
        self.assertFalse(scorer.recovery_evidence(events, "M2-03", 99))
        self.assertFalse(scorer.recovery_evidence(events[2:4], "M2-03", 20))
        overlap = [events[0], events[2], events[1], events[3]]
        self.assertFalse(scorer.recovery_evidence(overlap, "M2-03", 10))


if __name__ == "__main__":unittest.main()
