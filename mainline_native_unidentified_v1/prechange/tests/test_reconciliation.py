"""Finite receipt counterexamples and authoritative creation-pause regressions."""

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import unittest
from unittest.mock import Mock

from auth_lifecycle.online_state.protocol import canonical, digest
from auth_lifecycle.online_state.reconciliation import make_receipt
from auth_lifecycle.online_state.storage import AuthorityStore
from auth_lifecycle.online_state.services import Controller
from auth_lifecycle.online_state.native_provider import CasdoorProvider
from auth_lifecycle.online_state.native_http import NativeHTTP


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_reconciliation_receipt.py"
SPEC = importlib.util.spec_from_file_location("independent_receipt_checker", SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def fixture():
    origin = {"grant_id": "grantA", "generation": "g0", "account": "account1", "audience": "l1-client-0", "caller": "agentA", "task": "A"}
    target = {"rid": "A1", "attempt_id": "attempt1", "request_digest": "requesthash", **origin}
    metadata = {"rid": "A1", "attempt_id": "attempt1", "digest": "requesthash", "origin": origin, "native_unit_id": "admin/unit1"}
    query = {"exact_authorized_read": True, "record_found": True, "origin_bound": True,
             "actual_sends": 1, "observed_distinct_effects": 1, "query_ref": "native-http-1",
             "identifier_receipt_ref": digest(metadata), "identifier_receipt": metadata, "native_unit_id": "admin/unit1"}
    context = {"target": {"rid": "A1", "attempt_id": "attempt1", "digest": "requesthash", "origin": origin},
        "window": {"unknown_creators_at_open": ["A1"], "active": True}, "A_revoked": True,
        "known_A_units_inactive": True, "B_preserved_after_disposal": True}
    model = {"external_writers_excluded": True, "single_open_no_retry": True, "per_send_effect_bound": 1}
    packet = {"context": context, "query": query, "model": model}
    facts = {key: True for key in ("exact_authorized_read", "record_found", "origin_bound", "single_unknown_creator",
             "creation_paused", "A_revoked", "external_writers_excluded", "future_retry_excluded",
             "known_A_units_inactive", "B_preserved_after_disposal")}
    facts.update(actual_sends=1, per_send_effect_bound=1, observed_distinct_effects=1)
    evidence = {"source_lemma_ref": "synthetic-reviewed-bound", "query_ref": "native-http-1",
                "identifier_receipt_ref": digest(metadata), "packet": packet, "packet_ref": digest(packet)}
    return target, facts, evidence


class ReceiptTests(unittest.TestCase):
    def test_unique_bound_source_positive_and_independent_checker(self):
        receipt = make_receipt(*fixture())
        self.assertEqual(receipt["claim"], "CLOSED")
        self.assertEqual(CHECKER.check(receipt)["status"], "VALID_CONDITIONAL_CLOSED")
        self.assertFalse(receipt["handler_termination_claimed"])

    def test_unsafe_closure_matrix(self):
        cases = {
            "empty_query_request_can_commit_later": {"record_found": False, "observed_distinct_effects": 0},
            "two_same_queries_then_new_material": {"record_found": False, "observed_distinct_effects": 0},
            "pagination_insert_or_delete_omission": {"exact_authorized_read": False, "origin_bound": False},
            "A_B_unknown_sources_ambiguous": {"single_unknown_creator": False},
            "same_account_other_approval": {"origin_bound": False},
            "one_attempt_multiple_effects": {"per_send_effect_bound": 2},
            "transport_actual_retry": {"actual_sends": 2},
            "known_revoke_but_open_creation_frontier": {"creation_paused": False},
            "query_timeout": {"record_found": False},
            "disposal_timeout": {"known_A_units_inactive": False},
            "unknown_A_independent_B_works": {"record_found": False, "B_preserved_after_disposal": True},
            "future_retries_not_excluded": {"future_retry_excluded": False},
            "missing_writer_manifest": {"external_writers_excluded": False}}
        for name, changes in cases.items():
            with self.subTest(name=name):
                target, facts, evidence = fixture();facts.update(changes)
                receipt = make_receipt(target, facts, evidence)
                self.assertEqual(receipt["claim"], "UNKNOWN")
                forged = copy.deepcopy(receipt)
                forged.update(claim="CLOSED", remaining_creation_bound=0, remaining_obligations=[])
                self.assertEqual(CHECKER.check(forged)["status"], "INVALID")

    def test_metadata_source_and_packet_tampering(self):
        receipt = make_receipt(*fixture())
        receipt["evidence"]["packet"]["query"]["identifier_receipt"]["origin"]["grant_id"] = "grantB"
        self.assertEqual(CHECKER.check(receipt)["status"], "INVALID")
        missing = make_receipt(*fixture())
        missing["evidence"].pop("packet")
        self.assertEqual(CHECKER.check(missing)["status"], "INVALID")


class WindowTests(unittest.TestCase):
    def test_window_pauses_B_creating_but_allows_B_resource_admission(self):
        parent = Path(os.environ.get("RECONCILIATION_TEST_ROOT", Path(__file__).resolve().parents[2] / "mainline_native_reconciliation_v1/dev_work"))
        root = parent / secrets.token_hex(8);root.mkdir(parents=True)
        key = root / "key";key.write_bytes(os.urandom(32))
        store = AuthorityStore(root / "authority", key);self.addCleanup(store.connection.close)
        grants = {}
        for task, generation in [("A", "g0"), ("B", "g1")]:
            grants[task] = store.call("grant", {"approval_op": task, "caller": "agent" + task, "task": task,
                "account": "account1", "audience": "l1-client-0", "generation": generation,
                "operations": ["issue", "refresh", "userinfo"], "budget": 4, "material": "synthetic_legacy"})
        version, state = store.read_state()
        origin = {k: state["grants"][grants["A"]["grant_id"]][k] for k in ("grant_id", "caller", "task", "account", "audience", "generation")}
        state["requests"]["A1"] = {"rid": "A1", "digest": "d", "origin": origin,
            "request": {"operation": "refresh"}, "phase": "DISPATCHED_UNKNOWN", "attempt_id": "attempt1",
            "release_version": 2, "result_digest": None, "result_material": None}
        store.execute("UPDATE authority_state SET ciphertext=? WHERE id=1", (store.encrypt(state),))
        store.call("revoke", {"revoke_op": "r", "grant_id": origin["grant_id"]})
        self.assertEqual(store.call("begin_reconciliation", {"rid": "A1", "window_id": "w"})["status"], "WINDOW_OPEN")
        base = {"handle": grants["B"]["handle"], "task": "B", "account": "account1", "audience": "l1-client-0", "generation": "g1"}
        blocked = store.call("admit", {"caller": "agentB", "request": {**base, "rid": "B_create", "operation": "issue", "payload": {}}})
        allowed = store.call("admit", {"caller": "agentB", "request": {**base, "rid": "B_read", "operation": "userinfo", "payload": {"source_rid": "B0"}}})
        self.assertEqual(blocked["status"], "REJECTED")
        self.assertEqual(allowed["status"], "ADMITTED")
        self.assertIn("A1", store.call("recover", {})["obligations"])

    def test_complete_controller_reconciliation_with_synthetic_native_responses(self):
        import test_native_casdoor as native_fixtures
        fixture = native_fixtures.NativeAdapterTests()
        fixture.setUp()
        root = fixture.root
        fixture.profile.update(identifier_journal=True, durable_inbox=False)
        from auth_lifecycle.online_state.protocol import write_json
        write_json(root / "secure/native_profile.json", fixture.profile)
        authority = AuthorityStore(root / "authority", root / "secure/authority.key")
        self.addCleanup(authority.connection.close)
        gateway = CasdoorProvider(root, {"native_profile": str(root / "secure/native_profile.json")})
        ledger = NativeHTTP(root, "method", enabled=True)
        records = {}
        def synthetic_native(operation, **kwargs):
            seq = ledger.reserve(operation, fixture.name, kwargs.get("context"))
            if operation in {"issue", "refresh"}:
                body = {**fixture.body, "access_token": fixture.jwt(), "refresh_token": fixture.jwt(False)}
                claims = json.loads(native_fixtures.base64.urlsafe_b64decode(body["access_token"].split('.')[1]+'=='))
                # Synthetic JWT fixture uses a bare jti; point lookup still binds it.
                records[claims["jti"]] = {"body": body, "active": True}
                return {"http":200,"body":body,"error_type":None,"sequence":seq}
            if operation == "get_token":
                unit = kwargs["payload"]["id"];item=records[unit];body=item["body"]
                row={"owner":"", "name":unit, "organization":"l1-study", "user":fixture.name,"application":"app-l1-0"}
                # The actual gateway requires owner/name equality. Use the same
                # admin/name mapping as the native signed identifier.
                owner,name=unit.split('/',1);row.update(owner=owner,name=name)
                row.update(accessToken=body["access_token"],refreshToken=body["refresh_token"],idToken=body.get("id_token"),
                           tokenType=body["token_type"],scope=body["scope"],expiresIn=body["expires_in"])
                return {"http":200,"body":{"data":row},"error_type":None,"sequence":seq}
            token = kwargs.get("form",{}).get("token")
            if operation == "revoke":
                for item in records.values():
                    if item["body"]["refresh_token"]==token:item["active"]=False
                return {"http":200,"body":{},"error_type":None,"sequence":seq}
            if operation == "userinfo":
                access=kwargs["headers"]["Authorization"].removeprefix('Bearer ')
                active=any(x["body"]["access_token"]==access and x["active"] for x in records.values())
                return {"http":200 if active else 401,"body":{"sub":"synthetic_account"} if active else {},"error_type":None,"sequence":seq}
            active=any(x["body"]["access_token"]==token and x["active"] for x in records.values())
            return {"http":200,"body":{"active":active},"error_type":None,"sequence":seq}
        # Make fixture jti reflect the native owner's exact key format.
        original_jwt=fixture.jwt
        def native_jwt(*args,**kwargs):
            token=original_jwt(*args,**kwargs)
            head,body,_=token.split('.')
            claims=json.loads(native_fixtures.base64.urlsafe_b64decode(body+'=='));claims['jti']='admin/'+claims['jti']
            text=head+'.'+native_fixtures.b64(canonical(claims))
            return text+'.'+native_fixtures.b64(fixture.signing_key.sign(text.encode(),native_fixtures.padding.PKCS1v15(),native_fixtures.hashes.SHA256()))
        fixture.jwt=native_jwt
        gateway.http=Mock();gateway.http.call.side_effect=synthetic_native
        class AuthorityAdapter:
            drop=True
            def call(self,operation,payload):
                if operation=='record' and payload['rid']=='A1' and self.drop:
                    self.drop=False;return {'status':'UNKNOWN'}
                return authority.call(operation,payload)
        controller=Controller(root,json.loads((root/'secure/controller.json').read_text()))
        self.addCleanup(controller.active_lock.stream.close)
        controller.authority=AuthorityAdapter()
        controller.provider=Mock();controller.provider.call.side_effect=lambda op,data:gateway.call(op,data,'adapter')
        controller.ready=True
        controller.config['reconciliation_model']={'per_send_effect_bound':1,'single_open_no_retry':True,'external_writers_excluded':True,'source_lemma_ref':'synthetic-bound','source_files':[]}
        grants={}
        def request(task,rid,operation,source=None):
            return {'rid':rid,'handle':grants[task]['handle'],'task':task,'account':'synthetic_account','audience':'l1-client-0',
                    'generation':'g0' if task=='A' else 'g1','operation':operation,'payload':{} if operation=='issue' else {'source_rid':source}}
        for task in ['A','B']:
            login={'schema':2,'kind':'casdoor_login','issuer':fixture.profile['base'],'client':'l1-client-0','expected_account':'synthetic_account','username':fixture.name,'password':'synthetic_password'}
            grants[task]=controller.call('grant',{'approval_op':task,'caller':'agent'+task,'task':task,'account':'synthetic_account','audience':'l1-client-0','generation':'g0' if task=='A' else 'g1','operations':['issue','refresh','userinfo'],'budget':5,'material':login},'user')
            self.assertEqual(controller.call('call',request(task,task+'0','issue'),'agent'+task)['status'],'RESULT_AVAILABLE')
        self.assertEqual(controller.call('call',request('A','A1','refresh','A0'),'agentA')['status'],'UNKNOWN')
        controller.call('revoke',{'revoke_op':'withdraw','grant_id':grants['A']['grant_id']},'user')
        controller.call('begin_reconciliation',{'rid':'A1','window_id':'w'},'user')
        found=controller.call('reconcile',{'rid':'A1','window_id':'w','step':'discover','B_rid':''},'user')
        self.assertEqual(found['status'],'UNKNOWN')
        self.assertEqual(found['receipt']['remaining_creation_bound'],0)
        self.assertEqual(controller.call('call',request('B','B_after','userinfo','B0'),'agentB')['status'],'RESULT_AVAILABLE')
        closed=controller.call('reconcile',{'rid':'A1','window_id':'w','step':'finish','B_rid':'B_after'},'user')
        self.assertEqual(closed['status'],'CLOSED')
        self.assertEqual(CHECKER.check(closed['receipt'])['status'],'VALID_CONDITIONAL_CLOSED')
        self.assertEqual(authority.call('recover',{})['obligations'],[])
