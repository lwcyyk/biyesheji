# R05 supplemental read-only source excerpts

No source imported/executed. Existing R03/R04 excerpts remain bound at their original locations.


## C14: D:\毕业设计\auth-lifecycle\pyproject.toml
SHA256 `0d0a7fa9857a9aeca0882b21227544324ff5d6b46e32f31013dc8932382c67a9`

```text
1: [build-system]
2: requires = ["setuptools>=68"]
3: build-backend = "setuptools.build_meta"
4: 
5: [project]
6: name = "auth-lifecycle-l0"
7: version = "0.16.0"
8: description = "Finite bounded authentication lifecycle semantics and independent checks"
9: requires-python = ">=3.11"
10: dependencies = []
11: 
12: [project.optional-dependencies]
13: online-state = ["cryptography==50.0.2"]
14: 
15: [tool.setuptools.packages.find]
16: where = ["src"]
17: 
18: [tool.setuptools.package-data]
19: "auth_lifecycle.online_state" = ["migration.sql"]
```


## C15: D:\毕业设计\auth-lifecycle\scripts\check_reconciliation_receipt.py
SHA256 `8e23f92ae0e3144106e9bfd11c49af64dd704fdeeac47033f141104677ff0a5e`

```text
1: """Independent checker for the bounded receipt predicates. Standard library only."""
2: 
3: import argparse
4: import hashlib
5: import json
6: from pathlib import Path
7: 
8: 
9: def check(receipt):
10:     if receipt.get("schema") != "native-attempt-closure/1":
11:         return {"status": "INVALID", "reason": "SCHEMA"}
12:     facts = receipt.get("facts", {})
13:     evidence = receipt.get("evidence", {})
14:     failures = []
15:     for key in ("exact_authorized_read", "record_found", "origin_bound", "single_unknown_creator",
16:                 "creation_paused", "A_revoked", "external_writers_excluded", "future_retry_excluded",
17:                 "known_A_units_inactive", "B_preserved_after_disposal"):
18:         if facts.get(key) is not True:failures.append(key)
19:     for key in ("actual_sends", "per_send_effect_bound", "observed_distinct_effects"):
20:         if type(facts.get(key)) is not int or facts[key] != 1:failures.append(key)
21:     origin = receipt.get("evidence_origin", "IDENTIFIER_POINT_READ")
22:     refs = ("source_lemma_ref", "query_ref", "enumeration_ref", "authorized_scope_ref") if origin == "AUTHORIZED_SCOPE_ENUMERATION" else ("source_lemma_ref", "query_ref", "identifier_receipt_ref")
23:     for key in refs:
24:         if not evidence.get(key):failures.append(key)
25:     target = receipt.get("target", {})
26:     if not all(target.get(k) for k in ("rid", "attempt_id", "grant_id", "generation", "account", "request_digest")):
27:         failures.append("TARGET_BINDING")
28:     if receipt.get("whole_account_enumeration_claimed") is not False:
29:         failures.append("EXCESS_SCOPE")
30:     if receipt.get("handler_termination_claimed") is not False:
31:         failures.append("UNSUPPORTED_HANDLER_TERMINATION")
32:     packet = evidence.get("packet")
33:     if receipt.get("claim") == "CLOSED" and not isinstance(packet, dict):
34:         failures.append("EVIDENCE_PACKET_REQUIRED")
35:     if packet is not None:
36:         raw = json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()
37:         if hashlib.sha256(raw).hexdigest() != evidence.get("packet_ref"):
38:             failures.append("PACKET_HASH")
39:         try:
40:             context, query, model = packet["context"], packet["query"], packet["model"]
41:             original = context["target"]
42:             if (target["attempt_id"] != original["attempt_id"] or target["request_digest"] != original["digest"]
43:                     or any(target[k] != original["origin"][k] for k in original["origin"])):
44:                 failures.append("PACKET_TARGET")
45:             expected = {key: query.get(key, False) for key in ("exact_authorized_read", "record_found", "origin_bound")}
46:             expected.update(single_unknown_creator=context["window"]["unknown_creators_at_open"] == [target["rid"]],
47:                 creation_paused=context["window"]["active"], A_revoked=context["A_revoked"],
48:                 external_writers_excluded=model.get("external_writers_excluded") is True,
49:                 future_retry_excluded=model.get("single_open_no_retry") is True,
50:                 known_A_units_inactive=context["known_A_units_inactive"],
51:                 B_preserved_after_disposal=context["B_preserved_after_disposal"], actual_sends=query.get("actual_sends", 0),
52:                 per_send_effect_bound=model.get("per_send_effect_bound"), observed_distinct_effects=query.get("observed_distinct_effects", 0))
53:             if facts != expected:failures.append("PACKET_FACT_MISMATCH")
54:             metadata = query.get("identifier_receipt")
55:             if facts.get("origin_bound") is True and origin == "IDENTIFIER_POINT_READ":
56:                 if not isinstance(metadata, dict):
57:                     failures.append("IDENTIFIER_RECEIPT_MISSING")
58:                 else:
59:                     encoded = json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
60:                     if hashlib.sha256(encoded).hexdigest() != evidence.get("identifier_receipt_ref"):
61:                         failures.append("IDENTIFIER_HASH")
62:                     if (metadata.get("attempt_id") != target["attempt_id"] or metadata.get("digest") != target["request_digest"]
63:                             or metadata.get("origin") != original["origin"] or metadata.get("rid") != target["rid"]
64:                             or metadata.get("native_unit_id") != query.get("native_unit_id")):
65:                         failures.append("IDENTIFIER_SOURCE")
66:             if origin == "AUTHORIZED_SCOPE_ENUMERATION":
67:                 for flag in ("collection_complete", "all_returned_rows_authorized", "registered_universe_complete", "organization_equal_filter"):
68:                     if query.get(flag) is not True:failures.append(flag)
69:                 bound = query.get("record_upper_bound")
70:                 capacity = query.get("page_capacity")
71:                 budgets = model.get("approved_scope_budgets", [])
72:                 if (type(bound) is not int or type(capacity) is not int or not 0 < bound <= capacity
73:                         or not budgets or any(type(n) is not int or n < 0 for n in budgets) or sum(budgets) != bound):
74:                     failures.append("ENUMERATION_BOUND")
75:                 if query.get("page_number") != 1 or query.get("snapshot_scope") != "single_find_statement":
76:                     failures.append("ENUMERATION_SNAPSHOT")
77:                 rows = query.get("returned_records", [])
78:                 if query.get("organization") != model.get("organization") or any(r.get("organization") != model.get("organization") for r in rows):
79:                     failures.append("ENUMERATION_ORGANIZATION")
80:                 if (any(r.get("application") != model.get("application_name") or r.get("user") not in model.get("account_names", []) for r in rows)
81:                         or model.get("account_id_by_name", {}).get(query.get("target_user")) != target["account"]
82:                         or model.get("client_id") != target.get("audience")):
83:                     failures.append("ENUMERATION_UNIVERSE")
84:                 selected = sorted({r["unit_id"] for r in rows if r.get("user") == query.get("target_user") and r.get("application") == model.get("application_name")})
85:                 candidates = sorted(set(selected) - set(query.get("known_input_ids", [])))
86:                 if (selected != query.get("target_unit_ids") or candidates != query.get("candidate_unit_ids")
87:                         or len(candidates) != 1 or candidates[0] != query.get("selected_unit_id")):
88:                     failures.append("ENUMERATION_SELECTION")
89:                 input_context = query.get("input_context", {})
90:                 encoded = json.dumps(input_context, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
91:                 if (hashlib.sha256(encoded).hexdigest() != query.get("input_context_ref")
92:                         or input_context.get("known_unit_ids") != query.get("known_input_ids")
93:                         or input_context.get("unknown_creators") != [target["rid"]]
94:                         or input_context.get("account_grant_count") != 2 or input_context.get("account_budget_total") != 20):
95:                     failures.append("ENUMERATION_SOURCE_CONTEXT")
96:             for item in model.get("source_files", []):
97:                 if hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() != item["sha256"]:
98:                     failures.append("SOURCE_HASH")
99:         except (KeyError, OSError, TypeError):
100:             failures.append("PACKET_INPUT")
101:     if receipt.get("claim") == "CLOSED":
102:         if receipt.get("remaining_creation_bound") != 0 or receipt.get("remaining_obligations"):
103:             failures.append("INCONSISTENT_CLOSED_RESULT")
104:         return {"status": "VALID_CONDITIONAL_CLOSED" if not failures else "INVALID", "failures": failures,
105:                 "scope": "registered facts and stated model assumptions; source lemma and deployment remain premises"}
106:     if receipt.get("claim") == "UNKNOWN":
107:         return {"status": "VALID_CONSERVATIVE_UNKNOWN", "unmet": failures}
108:     return {"status": "INVALID", "reason": "CLAIM"}
109: 
110: 
111: if __name__ == "__main__":
112:     parser = argparse.ArgumentParser()
113:     parser.add_argument("receipt")
114:     parser.add_argument("--out")
115:     args = parser.parse_args()
116:     result = check(json.loads(Path(args.receipt).read_text()))
117:     if args.out:Path(args.out).write_text(json.dumps(result, indent=2) + "\n")
118:     print(json.dumps(result))
119:     raise SystemExit(1 if result["status"] == "INVALID" else 0)
```


## C16: D:\毕业设计\auth-lifecycle\tests\test_reconciliation.py
SHA256 `97d633552eb2062d785a20f558407a7b1eb9bc3c86cae8361ebddd162fab12b6`

```text
1: """Finite receipt counterexamples and authoritative creation-pause regressions."""
2: 
3: import copy
4: import hashlib
5: import importlib.util
6: import json
7: import os
8: from pathlib import Path
9: import secrets
10: import unittest
11: from unittest.mock import Mock
12: 
13: from auth_lifecycle.online_state.protocol import canonical, digest
14: from auth_lifecycle.online_state.reconciliation import make_receipt
15: from auth_lifecycle.online_state.storage import AuthorityStore
16: from auth_lifecycle.online_state.services import Controller
17: from auth_lifecycle.online_state.native_provider import CasdoorProvider
18: from auth_lifecycle.online_state.native_http import NativeHTTP
19: 
20: 
21: SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_reconciliation_receipt.py"
22: SPEC = importlib.util.spec_from_file_location("independent_receipt_checker", SCRIPT)
23: CHECKER = importlib.util.module_from_spec(SPEC)
24: SPEC.loader.exec_module(CHECKER)
25: 
26: 
27: def fixture():
28:     origin = {"grant_id": "grantA", "generation": "g0", "account": "account1", "audience": "l1-client-0", "caller": "agentA", "task": "A"}
29:     target = {"rid": "A1", "attempt_id": "attempt1", "request_digest": "requesthash", **origin}
30:     metadata = {"rid": "A1", "attempt_id": "attempt1", "digest": "requesthash", "origin": origin, "native_unit_id": "admin/unit1"}
31:     query = {"exact_authorized_read": True, "record_found": True, "origin_bound": True,
32:              "actual_sends": 1, "observed_distinct_effects": 1, "query_ref": "native-http-1",
33:              "identifier_receipt_ref": digest(metadata), "identifier_receipt": metadata, "native_unit_id": "admin/unit1"}
34:     context = {"target": {"rid": "A1", "attempt_id": "attempt1", "digest": "requesthash", "origin": origin},
35:         "window": {"unknown_creators_at_open": ["A1"], "active": True}, "A_revoked": True,
36:         "known_A_units_inactive": True, "B_preserved_after_disposal": True}
37:     model = {"external_writers_excluded": True, "single_open_no_retry": True, "per_send_effect_bound": 1}
38:     packet = {"context": context, "query": query, "model": model}
39:     facts = {key: True for key in ("exact_authorized_read", "record_found", "origin_bound", "single_unknown_creator",
40:              "creation_paused", "A_revoked", "external_writers_excluded", "future_retry_excluded",
41:              "known_A_units_inactive", "B_preserved_after_disposal")}
42:     facts.update(actual_sends=1, per_send_effect_bound=1, observed_distinct_effects=1)
43:     evidence = {"source_lemma_ref": "synthetic-reviewed-bound", "query_ref": "native-http-1",
44:                 "identifier_receipt_ref": digest(metadata), "packet": packet, "packet_ref": digest(packet)}
45:     return target, facts, evidence
46: 
47: 
48: class ReceiptTests(unittest.TestCase):
49:     def test_unique_bound_source_positive_and_independent_checker(self):
50:         receipt = make_receipt(*fixture())
51:         self.assertEqual(receipt["claim"], "CLOSED")
52:         self.assertEqual(CHECKER.check(receipt)["status"], "VALID_CONDITIONAL_CLOSED")
53:         self.assertFalse(receipt["handler_termination_claimed"])
54: 
55:     def test_unsafe_closure_matrix(self):
56:         cases = {
57:             "empty_query_request_can_commit_later": {"record_found": False, "observed_distinct_effects": 0},
58:             "two_same_queries_then_new_material": {"record_found": False, "observed_distinct_effects": 0},
59:             "pagination_insert_or_delete_omission": {"exact_authorized_read": False, "origin_bound": False},
60:             "A_B_unknown_sources_ambiguous": {"single_unknown_creator": False},
61:             "same_account_other_approval": {"origin_bound": False},
62:             "one_attempt_multiple_effects": {"per_send_effect_bound": 2},
63:             "transport_actual_retry": {"actual_sends": 2},
64:             "known_revoke_but_open_creation_frontier": {"creation_paused": False},
65:             "query_timeout": {"record_found": False},
```


## C17: D:\毕业设计\auth-lifecycle\tests\test_evidence_semantics.py
SHA256 `5993084832b9571e67111da662351c8615d8bd76439f588747aeabce0f1efa0c`

```text
1: """Offline evidence meaning and non-promotion regressions."""
2: from copy import deepcopy
3: import unittest
4: from auth_lifecycle.online_state.evidence_semantics import (
5:     normalize_material, normalize_query, rt_inactive_or_refresh_response_rejected)
6: 
7: 
8: class EvidenceSemanticsTests(unittest.TestCase):
9:     def test_legacy_introspection_does_not_become_refresh_attempt(self):
10:         row={"refresh_rejected":True,"refresh_check_kind":"READ_ONLY_INTROSPECTION","refresh_introspection_active":False}
11:         value=normalize_material(row)
12:         self.assertFalse(value['refresh_attempt']['performed'])
13:         self.assertIsNone(value['refresh_attempt']['creation_effect_excluded'])
14:         self.assertFalse(value['refresh_token_introspection']['active'])
15:         self.assertTrue(rt_inactive_or_refresh_response_rejected(row))
16: 
17:     def test_untyped_legacy_boolean_stays_ambiguous(self):
18:         value=normalize_material({'refresh_rejected':True})
19:         self.assertTrue(value['legacy_ambiguous_boolean'])
20:         self.assertFalse(rt_inactive_or_refresh_response_rejected({'refresh_rejected':True}))
21: 
22:     def test_actual_refresh_response_scope(self):
23:         row={'refresh_request_performed':True,'refresh_request_http':400,'refresh_response_has_new_material':False}
24:         value=normalize_material(row)
25:         self.assertTrue(value['refresh_attempt']['response_rejects_request'])
26:         self.assertIsNone(value['refresh_attempt']['creation_effect_excluded'])
27: 
28:     def test_response_with_material_or_parse_error_is_not_clean_rejection(self):
29:         for update in [{'refresh_response_has_new_material':True},{'refresh_transport_error_type':'ResponseParseFailure'}]:
30:             row={'refresh_request_performed':True,'refresh_request_http':400,'refresh_response_has_new_material':False,**update}
31:             self.assertFalse(rt_inactive_or_refresh_response_rejected(row))
32: 
33:     def test_http_error_does_not_become_inactive(self):
34:         row={'rt_introspection_performed':True,'rt_introspection_http':500,'rt_introspection_active':False}
35:         value=normalize_material(row)
36:         self.assertIsNone(value['refresh_token_introspection']['active'])
37:         self.assertTrue(value['refresh_token_introspection']['inconsistent_http_active'])
38:         self.assertFalse(rt_inactive_or_refresh_response_rejected(row))
39:         at=normalize_material({'at_introspection_http':500,'at_introspection_active':False})
40:         self.assertIsNone(at['access_token_introspection']['active'])
41: 
42:     def test_nonboolean_active_is_unknown(self):
43:         row={'rt_introspection_performed':True,'rt_introspection_http':200,'rt_introspection_active':'false'}
44:         self.assertIsNone(normalize_material(row)['refresh_token_introspection']['active'])
45: 
46:     def test_resource_and_token_statement_are_separate(self):
47:         row={'accepted':True,'userinfo_http':200,'rt_introspection_performed':True,'rt_introspection_active':False}
48:         value=normalize_material(row)
49:         self.assertTrue(value['userinfo']['accepted'])
50:         self.assertFalse(value['refresh_token_introspection']['active'])
51: 
52:     def test_count_is_not_page_count_or_completeness(self):
53:         q={'reported_pages':4,'returned_records':[{},{}],'page_capacity':100,'page_number':1,'collection_complete':False}
54:         value=normalize_query(q)
55:         self.assertEqual(value['native_reported_count'],4)
56:         self.assertEqual(value['returned_record_count'],2)
57:         self.assertIsNone(value['native_reported_page_count'])
58:         self.assertFalse(value['complete_at_find_snapshot'])
59:         self.assertFalse(value['future_creation_cutoff_established_by_count'])
60: 
```


## C01 R05 re-read: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\storage.py

```text
24: def request_projection(request):
25:     return {key: request[key] for key in
26:             ("rid", "digest", "origin", "phase", "attempt_id", "release_version")}
27: 
28: 
29: def state_projection(state):
30:     approvals = []
31:     for grant in state["grants"].values():
32:         approvals.append({key: grant[key] for key in
33:                           ("grant_id", "caller", "task", "account", "audience",
34:                            "generation", "active", "limit", "reserved", "spent")})
35:     requests = [request_projection(req) for req in state["requests"].values()]
36:     obligations = [req["rid"] for req in requests
37:                    if req["phase"] in {"DISPATCHED_UNKNOWN", "QUARANTINED"}]
38:     for window in state.get("reconciliation_windows", {}).values():
39:         if window.get("receipt", {}).get("claim") != "CLOSED" and window["target_rid"] not in obligations:
40:             obligations.append(window["target_rid"])
41:     disposals = [{"disposal_op": key, **value} for key, value in state.get("disposals", {}).items()]
42:     return {"approvals": approvals, "requests": requests, "obligations": obligations,
43:             "disposals": disposals}
44: 
45: 
```

```text
122:     def call(self, operation, payload):
123:         if operation not in {"grant", "admit", "release", "record", "revoke", "recover",
124:                              "prepare_disposal", "record_disposal"}:
125:             if operation not in {"begin_reconciliation", "reconciliation_context", "save_reconciliation"}:
126:                 return {"status": "REJECTED", "reason": "INVALID_OPERATION"}
127:         with self.lock:
128:             try:
129:                 if operation == "recover":
130:                     if self.operation_limit is not None and self.operations >= self.operation_limit:
131:                         return {"status": "INCONCLUSIVE", "reason": "DATABASE_OPERATION_BUDGET"}
132:                     version, state = self.read_state()
133:                     return {"status": "RECOVERED", "version": version, **state_projection(state)}
134:                 if self.operation_limit is not None and self.operations + 6 > self.operation_limit:
135:                     return {"status": "INCONCLUSIVE", "reason": "DATABASE_OPERATION_BUDGET"}
136:                 self.execute("BEGIN IMMEDIATE")
137:                 version, state = self.read_state()
138:                 result = getattr(self, operation)(state, payload, version + 1)
139:                 public = {key: result[key] for key in
140:                           ("status", "reason", "rid", "grant_id", "phase", "send") if key in result}
141:                 event = {"result": public, "state": state_projection(state),
142:                          "logical_state_bytes": len(canonical(state))}
143:                 self.execute("UPDATE authority_state SET version=?,ciphertext=? WHERE id=1",
144:                              (version + 1, self.encrypt(state)))
145:                 self.execute("INSERT INTO authority_events VALUES(?,?,?)",
146:                              (version + 1, operation, canonical(event).decode()))
147:                 self.execute("COMMIT")
148:                 return {**result, "version": version + 1}
149:             except InvalidInput:
150:                 if self.connection.in_transaction:
151:                     self.execute("ROLLBACK")
152:                 return {"status": "REJECTED", "reason": "INVALID_INPUT"}
153:             except Exception:
154:                 if self.connection.in_transaction:
155:                     # A budget exhaustion must still release the DB transaction.
156:                     self.connection.rollback()
157:                     self.operations += 1
158:                     self.metrics.emit("sqlite_rollback_cleanup", kind="ROLLBACK")
159:                 return {"status": "UNKNOWN", "reason": "AUTHORITY_STATE_UNAVAILABLE"}
```

```text
397:     def save_reconciliation(self, state, payload, version):
398:         exact_fields(payload, ("rid", "window_id", "receipt", "query_evidence", "B_rid"))
399:         req = state["requests"][payload["rid"]]
400:         window = state.get("reconciliation_windows", {}).get(req["origin"]["account"])
401:         if not window or window["window_id"] != payload["window_id"]:
402:             return {"status": "CONFLICT", "reason": "WINDOW_MISMATCH"}
403:         receipt = payload["receipt"]
404:         if receipt["claim"] == "CLOSED":
405:             context = self.reconciliation_context(state, {"rid": payload["rid"], "window_id": payload["window_id"], "B_rid": payload["B_rid"]}, version)
406:             if (req["phase"] != "DISPOSED" or not window["active"] or not context["known_A_units_inactive"]
407:                     or not context["B_preserved_after_disposal"] or not context["A_revoked"]
408:                     or window["unknown_creators_at_open"] != [payload["rid"]]
409:                     or receipt["target"]["attempt_id"] != req["attempt_id"]
410:                     or receipt["target"]["request_digest"] != req["digest"]):
411:                 return {"status": "UNKNOWN", "reason": "CLOSE_STATE_MISMATCH"}
412:         window["receipt"] = receipt
413:         window["query_evidence"] = payload["query_evidence"]
414:         if receipt["claim"] == "CLOSED":window["active"] = False
415:         return {"status": receipt["claim"], "receipt": receipt, "receipt_ref": digest(receipt)}
```


## C03 R05 re-read: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_provider.py

```text
19: class CasdoorProvider:
20:     def __init__(self, root, config):
21:         self.root = Path(root)
22:         self.profile = json.loads(Path(config["native_profile"]).read_text())
23:         if self.profile.get("enabled") is not True or self.profile.get("version") != "4.25.0":
24:             raise InvalidInput("NATIVE_PROFILE_NOT_ENABLED")
25:         self.http = NativeHTTP(self.profile["batch"], "method", enabled=True)
26:         self.budget_path = self.http.budget_path
27:         self.key = (self.root / "secure" / "provider.key").read_bytes()
28:         self.log = EventLog(self.root / "provider" / "native_events.jsonl")
29:         self.inbox = self.root / "provider" / "native_inbox.jsonl"
30:         self.lock = threading.Lock()
31:         self.results = {}
32:         self.identifier_log = EventLog(self.root / "provider" / "identifier_receipts.jsonl")
33:         if self.profile.get("identifier_journal"):
34:             self.log.emit("identifier_journal_enabled", scope="responses received after this process start")
35:         if self.inbox.exists():
36:             for line in self.inbox.read_bytes().splitlines():
37:                 raw = base64.b64decode(line)
38:                 result = json.loads(AESGCM(self.key).decrypt(raw[:12], raw[12:], b"native-inbox-v1"))
39:                 self.results[result["attempt_id"]] = result
40: 
41:     def call(self, operation, payload, identity):
42:         if operation == "reconcile_query":
43:             return self.reconcile_query(payload)
44:         if operation == "lookup":
45:             exact_fields(payload, ("rid", "digest", "origin", "attempt_id", "release_version"))
46:             result = self.results.get(payload["attempt_id"])
47:             if result is None:
48:                 return {"status": "UNKNOWN", "reason": "NO_DURABLE_OPERATIONAL_RESULT"}
49:             if any(result[key] != payload[key] for key in payload):
50:                 return {"status": "CONFLICT", "reason": "LOOKUP_SOURCE_CONFLICT"}
51:             self.log.emit("operational_lookup", rid=result["rid"], attempt_id=result["attempt_id"])
52:             return {"status": "PROVIDER_RESULT", **result}
```

```text
151:     def reconcile_query(self, payload):
152:         if self.profile.get("query_mode") == "AUTHORIZED_SCOPE_ENUMERATION":
153:             return self.reconcile_enumeration(payload)
154:         exact_fields(payload, ("rid", "digest", "origin", "attempt_id", "release_version"))
155:         with sqlite3.connect("file:" + str(self.budget_path) + "?mode=ro", uri=True) as con:
156:             sends = con.execute("SELECT COUNT(*) FROM requests WHERE category='method' AND operation='refresh' AND attempt_id=? AND rid=? AND request_digest=? AND actor=?",
157:                                 (payload["attempt_id"], payload["rid"], payload["digest"], self.profile["actor"]["name"])).fetchone()[0]
158:         evidence = {"actual_sends": sends, "query_kind": "none", "record_found": False,
159:                     "exact_authorized_read": False, "origin_bound": False, "observed_distinct_effects": 0}
160:         path = self.identifier_log.path
161:         entries = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
162:         matches = [row for row in entries if all(row.get(key) == payload[key] for key in payload)]
163:         if sends != 1 or len(matches) != 1:
164:             return {"status": "UNKNOWN", "reason": "NO_UNIQUE_TRUSTED_IDENTIFIER_OR_SEND", "evidence": evidence,
165:                     "unsafe_account_listing_sent": False}
166:         metadata = matches[0]
167:         unit = metadata["native_unit_id"]
168:         if metadata["verified_account"] != self.profile["actor"]["id"] or metadata["verified_client"] != self.profile["client_id"]:
169:             return {"status": "UNKNOWN", "reason": "IDENTIFIER_SCOPE_MISMATCH", "evidence": evidence}
170:         basic = base64.b64encode((self.profile["client_id"] + ":" + self.profile["client_secret"]).encode()).decode()
171:         response = self.http.call("get_token", actor=self.profile["actor"]["name"], payload={"id": unit},
172:                                   headers={"Authorization": "Basic " + basic}, context={**payload, "verified_unit_id": unit})
173:         evidence.update(query_kind="exact_primary_key", exact_authorized_read=True,
174:                         identifier_receipt_ref=digest(metadata), native_unit_id=unit,
175:                         identifier_receipt=metadata, query_ref="native-http-" + str(response["sequence"]))
176:         row = response["body"].get("data") if response["http"] == 200 else None
177:         if not isinstance(row, dict):
178:             return {"status": "UNKNOWN", "reason": "EXACT_POINT_READ_UNAVAILABLE", "evidence": evidence}
179:         if (row.get("owner", "") + "/" + row.get("name", "") != unit
180:                 or row.get("organization") != "l1-study" or row.get("user") != self.profile["actor"]["name"]
181:                 or row.get("application") != "app-l1-0"):
182:             return {"status": "UNKNOWN", "reason": "NATIVE_ROW_SCOPE_CONFLICT", "evidence": evidence}
183:         body = {dst: row.get(src) for dst, src in [("access_token", "accessToken"), ("refresh_token", "refreshToken"),
184:                 ("id_token", "idToken"), ("token_type", "tokenType"), ("scope", "scope"), ("expires_in", "expiresIn")]}
185:         material = token_bundle(body, self.profile)
186:         if material["derived"]["verified_claims"]["jti"] != unit:
187:             return {"status": "UNKNOWN", "reason": "POINT_ID_CLAIM_CONFLICT", "evidence": evidence}
188:         evidence.update(record_found=True, origin_bound=True, observed_distinct_effects=1)
189:         return {"status": "RECONCILED_MATERIAL", "evidence": evidence,
190:                 "result": {**payload, "material": material, "outcome": "OK"}}
```
