# R04 targeted supplemental excerpts

Text extraction only; no source execution. R03 selected excerpts retained at the bound prior location.


## C11 D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\protocol.py
SHA256 `1d74afd2d1c252e371fe0d2b619120e588eab27bb15072e27168b812253fed79`

```text
19: def canonical(value):
20:     return json.dumps(value, sort_keys=True, separators=(",", ":"),
21:                       ensure_ascii=True, allow_nan=False).encode("utf-8")
22: 
23: 
24: def digest(value):
25:     return hashlib.sha256(canonical(value)).hexdigest()
26: 
27: 
28: def strict_json(raw):
29:     def pairs(items):
30:         result = {}
31:         for key, value in items:
32:             if key in result:
33:                 raise InvalidInput("DUPLICATE_JSON_KEY")
34:             result[key] = value
35:         return result
36: 
37:     def invalid_constant(value):
38:         raise InvalidInput("NONFINITE_JSON")
39: 
40:     return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
41: 
42: 
43: def identifier(value):
44:     if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", value):
45:         raise InvalidInput("INVALID_IDENTIFIER")
46:     return value
47: 
48: 
49: def exact_fields(value, fields):
50:     if not isinstance(value, dict) or set(value) != set(fields):
51:         raise InvalidInput("INVALID_FIELDS")
52: 
53: 
54: def normalized_request(value):
55:     fields = ("rid", "handle", "task", "account", "audience", "generation",
56:               "operation", "payload")
57:     exact_fields(value, fields)
58:     result = {key: identifier(value[key]) for key in fields if key != "payload"}
59:     if result["operation"] == "issue":
60:         exact_fields(value["payload"], ())
61:         result["payload"] = {}
62:     elif result["operation"] in {"refresh", "userinfo"}:
63:         exact_fields(value["payload"], ("source_rid",))
64:         result["payload"] = {"source_rid": identifier(value["payload"]["source_rid"])}
65:     else:
66:         exact_fields(value["payload"], ("value",))
67:         number = value["payload"]["value"]
68:         if type(number) is not int or not -1000000 <= number <= 1000000:
69:             raise InvalidInput("INVALID_PAYLOAD")
70:         result["payload"] = {"value": number}
71:     return result
72: 
73: 
74: def write_json(path, value):
75:     path = Path(path)
76:     path.parent.mkdir(parents=True, exist_ok=True)
77:     temporary = path.with_name(path.name + ".tmp")
78:     with temporary.open("wb") as stream:
79:         stream.write(canonical(value))
80:         stream.flush()
81:         os.fsync(stream.fileno())
82:     os.replace(temporary, path)
83: 
84: 
85: class EventLog:
86:     def __init__(self, path):
87:         self.path = Path(path)
88:         self.path.parent.mkdir(parents=True, exist_ok=True)
89:         self.lock = threading.Lock()
90: 
91:     def emit(self, event, **fields):
92:         # Callers supply explicit projections; request bodies and exceptions stay out.
93:         row = {"event": event, "pid": os.getpid(), "monotonic_ns": time.monotonic_ns(), **fields}
94:         with self.lock, self.path.open("ab") as stream:
95:             stream.write(canonical(row) + b"\n")
96:             stream.flush()
97:             os.fsync(stream.fileno())
98:         return row
```


## C12 D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\reconciliation.py
SHA256 `22f1eba0a80371d2e647b535089c348beaeac3eda4594de547fd66d401d81047`

```text
1: """Conditional G0/G9 closure receipts. No new cryptographic mechanism."""
2: 
3: 
4: REQUIRED = (
5:     "exact_authorized_read", "record_found", "origin_bound", "single_unknown_creator",
6:     "creation_paused", "A_revoked", "external_writers_excluded",
7:     "future_retry_excluded", "known_A_units_inactive", "B_preserved_after_disposal")
8: 
9: 
10: def make_receipt(target, facts, evidence):
11:     missing = [key for key in REQUIRED if facts.get(key) is not True]
12:     for key in ("actual_sends", "per_send_effect_bound", "observed_distinct_effects"):
13:         if type(facts.get(key)) is not int or facts[key] != 1:
14:             missing.append(key)
15:     if not evidence.get("source_lemma_ref"):
16:         missing.append("source_lemma_ref")
17:     if not evidence.get("query_ref"):
18:         missing.append("query_ref")
19:     origin = evidence.get("origin", "IDENTIFIER_POINT_READ")
20:     if origin == "AUTHORIZED_SCOPE_ENUMERATION":
21:         query = evidence.get("packet", {}).get("query", {})
22:         if not evidence.get("enumeration_ref") or not evidence.get("authorized_scope_ref"):
23:             missing.append("enumeration_scope_reference")
24:         if query.get("collection_complete") is not True:
25:             missing.append("authorized_collection_complete")
26:     elif not evidence.get("identifier_receipt_ref"):
27:         missing.append("identifier_receipt_ref")
28:     remaining = None
29:     if facts.get("per_send_effect_bound") == 1 and facts.get("future_retry_excluded") is True and evidence.get("source_lemma_ref"):
30:         if facts.get("observed_distinct_effects") == 0 and facts.get("actual_sends") in {0, 1}:
31:             remaining = 1
32:         elif (facts.get("observed_distinct_effects") == facts.get("actual_sends") == 1
33:               and facts.get("record_found") is True and facts.get("origin_bound") is True):
34:             remaining = 0
35:     return {"schema": "native-attempt-closure/1", "target": target,
36:             "evidence_origin": origin,
37:             "claim": "CLOSED" if not missing else "UNKNOWN", "facts": facts,
38:             "evidence": evidence, "missing": missing,
39:             "remaining_creation_bound": remaining,
40:             "completeness_scope": "one attempt, bounded effect saturation",
41:             "whole_account_enumeration_claimed": False,
42:             "handler_termination_claimed": False,
43:             "conditional_assumptions": ["source-faithful fixed Casdoor profile", "trusted registered creators and custody", "no other fixture/admin writers"],
44:             "remaining_obligations": [] if not missing else [target["rid"]]}
```


## C13 D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\evidence_semantics.py
SHA256 `0e58693429fbddebd46f03fc8716744a7e6167f0373d632acf45095d039532aa`

```text
1: """Pure, versioned evidence views. No network, state changes, or token inputs.
2: 
3: Legacy booleans remain observations with their original scope. Introspection
4: never implies that a refresh was sent or that future creation is impossible.
5: """
6: from copy import deepcopy
7: 
8: MATERIAL_SCHEMA = "native-material-observation/2"
9: QUERY_SCHEMA = "native-enumeration-observation/2"
10: 
11: 
12: def boolean(value):
13:     return value if type(value) is bool else None
14: 
15: 
16: def normalize_material(row, provenance=None):
17:     """Normalize a secret-free measurement row, preserving missing evidence."""
18:     mode = row.get("refresh_check_kind")
19:     rt_active = row.get("rt_introspection_active", row.get("refresh_introspection_active"))
20:     rt_performed = row.get("rt_introspection_performed") is True or mode == "READ_ONLY_INTROSPECTION"
21:     rt_http = row.get("rt_introspection_http")
22:     rt_http_valid = rt_http is None or rt_http == 200
23:     at_http = row.get("at_introspection_http", row.get("introspection_http"))
24:     at_http_valid = at_http is None or at_http == 200
25:     refresh_performed = row.get("refresh_request_performed") is True or (
26:         mode != "READ_ONLY_INTROSPECTION" and "refresh_http" in row)
27:     refresh_http = row.get("refresh_request_http", row.get("refresh_http")) if refresh_performed else None
28:     material = boolean(row.get("refresh_response_has_new_material"))
29:     # Old active-probe producer set refresh_rejected only after a 4xx response
30:     # with no access token. It did not record all returned material fields.
31:     legacy_rejected = row.get("refresh_rejected") is True
32:     old_active_rejection = refresh_performed and refresh_http in {400, 401, 403} and legacy_rejected and material is None
33:     response_rejected = refresh_performed and refresh_http in {400, 401, 403} and (
34:         material is False or old_active_rejection) and not row.get("refresh_transport_error_type")
35:     ambiguous = "refresh_rejected" in row and not rt_performed and not refresh_performed
36:     return {"schema": MATERIAL_SCHEMA, "rid": row.get("rid"),
37:         "userinfo": {"http": row.get("userinfo_http"), "accepted": boolean(row.get("accepted")),
38:                      "scope": "configured cookie-free UserInfo and expected account"},
39:         "access_token_introspection": {"performed": "at_introspection_active" in row or "introspection_active" in row,
40:             "http": at_http,
41:             "active": boolean(row.get("at_introspection_active", row.get("introspection_active"))) if at_http_valid else None},
42:         "refresh_token_introspection": {"performed": rt_performed,
43:             "http": rt_http, "active": boolean(rt_active) if rt_performed and rt_http_valid else None,
44:             "inconsistent_http_active": rt_performed and not rt_http_valid and type(rt_active) is bool,
45:             "native_sequence": row.get("rt_introspection_native_sequence"),
46:             "http_not_explicitly_recorded": rt_performed and "rt_introspection_http" not in row},
47:         "refresh_attempt": {"performed": refresh_performed, "http": refresh_http,
48:             "response_rejects_request": bool(response_rejected), "new_material_in_response": material,
49:             "legacy_only_no_access_token": old_active_rejection,
50:             "response_error_present": boolean(row.get("refresh_response_error_present")),
51:             "transport_error_type": row.get("refresh_transport_error_type"),
52:             "native_sequence": row.get("refresh_native_sequence"),
53:             "creation_effect_excluded": None},
54:         "legacy_ambiguous_boolean": ambiguous, "provenance": deepcopy(provenance or {}),
55:         "does_not_establish": ["arbitrary RP rejection", "future creation cutoff", "all descendants closed"]}
56: 
57: 
58: def rt_inactive_or_refresh_response_rejected(row):
59:     view = normalize_material(row)
60:     intro = view["refresh_token_introspection"]
61:     return ((intro["performed"] and intro["active"] is False)
62:             or view["refresh_attempt"]["response_rejects_request"])
63: 
64: 
65: def normalize_query(query, provenance=None):
66:     records = query.get("returned_records")
67:     new_count = query.get("native_reported_count")
68:     old_count = query.get("reported_pages")
69:     count = new_count if "native_reported_count" in query else old_count
70:     return {"schema": QUERY_SCHEMA, "native_reported_count": count if type(count) is int else None,
71:         "returned_record_count": len(records) if isinstance(records, list) else query.get("returned_record_count"),
72:         "requested_page_capacity": query.get("page_capacity"), "requested_page_number": query.get("page_number"),
73:         "native_reported_page_count": None,
74:         "count_and_rows_share_snapshot": False,
75:         "complete_at_find_snapshot": boolean(query.get("collection_complete")),
76:         "completeness_basis": {"snapshot_scope": query.get("snapshot_scope"),
77:                                "lifetime_record_upper_bound": query.get("record_upper_bound")},
78:         "future_creation_cutoff_established_by_count": False,
79:         "legacy_field_mapping": "reported_pages -> native_reported_count (Casdoor data2)",
80:         "conflicting_count_fields": "native_reported_count" in query and "reported_pages" in query and new_count != old_count,
81:         "provenance": deepcopy(provenance or {})}
```


## C01 R04 additional read D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\storage.py

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
93:     def execute(self, statement, parameters=()):
94:         if self.operation_limit is not None and self.operations >= self.operation_limit:
95:             raise RuntimeError("DATABASE_OPERATION_BUDGET")
96:         self.operations += 1
97:         kind = statement.strip().split()[0].upper()
98:         size = sum(len(x) if isinstance(x, (bytes, str)) else 8 for x in parameters)
99:         self.metrics.emit("sqlite_statement", number=self.operations, kind=kind,
100:                           bound_value_bytes=size)
101:         return self.connection.execute(statement, parameters)
102: 
103:     def cipher(self):
104:         # Reloading the external key makes a missing recovery key fail closed.
105:         key = self.key_path.read_bytes()
106:         if len(key) != 32:
107:             raise ValueError("KEY_UNAVAILABLE")
108:         return AESGCM(key)
109: 
110:     def encrypt(self, state):
111:         nonce = os.urandom(12)
112:         return nonce + self.cipher().encrypt(nonce, canonical(state), AAD)
113: 
114:     def read_state(self):
115:         row = self.execute("SELECT version,ciphertext FROM authority_state WHERE id=1").fetchone()
116:         if row is None:
117:             raise ValueError("STATE_UNAVAILABLE")
118:         raw = bytes(row["ciphertext"])
119:         state = json.loads(self.cipher().decrypt(raw[:12], raw[12:], AAD))
120:         return row["version"], state
121: 
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


## C02 R04 additional read D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\services.py

```text
42: class Controller:
43:     def __init__(self, root, config, fault=None):
44:         self.root = Path(root)
45:         self.config = config
46:         self.active_lock = SingleActive(self.root / "secure" / "controller.lock")
47:         self.log = EventLog(self.root / "controller" / "events.jsonl")
48:         self.authority = Client(config["authority_url"], config["authority_token"],
49:                                 config["certificate"], self.log)
50:         self.provider = Client(config["provider_url"], config["provider_token"],
51:                                config["certificate"], self.log)
52:         self.boot = secrets.token_hex(8)
53:         self.fault = fault
54:         self.fault_used = False
55:         self.ready = False
56:         self.recover()
57: 
58:     def barrier(self, point):
59:         if point != self.fault or self.fault_used:
60:             return
61:         self.fault_used = True
62:         folder = self.root / "controller" / "barriers"
63:         path = folder / (self.boot + "_" + point + ".json")
64:         write_json(path, {"point": point, "pid": os.getpid(), "boot": self.boot})
65:         self.log.emit("barrier", point=point, boot=self.boot)
66:         release = path.with_suffix(".release")
67:         while not release.exists():
68:             time.sleep(0.01)
69: 
70:     def recover(self):
71:         result = self.authority.call("recover", {})
72:         self.ready = result.get("status") == "RECOVERED"
73:         if self.ready:
74:             write_json(self.root / "cache" / "view.json", {
75:                 "authoritative_version": result["version"], "boot": self.boot,
76:                 "approval_count": len(result["approvals"]), "display_only": True})
77:         self.log.emit("recovery", status=result.get("status"),
78:                       version=result.get("version"), boot=self.boot)
79:         return result
80: 
81:     def call(self, operation, payload, identity):
```

```text
153:     def record_result(self, result):
154:         if result.get("status") != "PROVIDER_RESULT":
155:             return {"status": "UNKNOWN", "reason": "EXTERNAL_RESULT_UNCERTAIN"}
156:         fields = ("rid", "digest", "origin", "attempt_id", "release_version", "material", "outcome")
157:         if not all(key in result for key in fields):
158:             return {"status": "UNKNOWN", "reason": "INVALID_PROVIDER_RESULT"}
159:         envelope = {key: result[key] for key in fields}
160:         return self.authority.call("record", envelope)
161: 
162:     def reconcile(self, payload):
163:         exact_fields(payload, ("rid", "window_id", "step", "B_rid"))
164:         context = self.authority.call("reconciliation_context", {
165:             "rid": payload["rid"], "window_id": payload["window_id"], "B_rid": payload["B_rid"]})
166:         if context.get("status") != "RECONCILIATION_CONTEXT":return context
167:         window = context["window"]
168:         if window.get("receipt", {}).get("claim") == "CLOSED":
169:             return {"status": "CLOSED", "receipt": window["receipt"]}
170:         query = window.get("query_evidence", {})
171:         if payload["step"] == "discover":
172:             target = context["target"]
173:             request = {key: target[key] for key in ("rid", "digest", "origin", "attempt_id", "release_version")}
174:             if self.config.get("reconciliation_model", {}).get("evidence_origin") == "AUTHORIZED_SCOPE_ENUMERATION":
175:                 request["enumeration_context"] = {"known_unit_ids": context["known_unit_ids"],
176:                     "account_grant_count": context["account_grant_count"], "account_budget_total": context["account_budget_total"],
177:                     "unknown_creators": window["unknown_creators_at_open"], "context_version": context["version"]}
178:             response = self.provider.call("reconcile_query", request)
179:             if response.get("status") == "SAFETY_FAILURE":
180:                 return response
181:             query = response.get("evidence", {})
182:             if (response.get("status") == "RECONCILED_MATERIAL" and window["unknown_creators_at_open"] == [payload["rid"]]
183:                     and query.get("actual_sends") == 1 and query.get("origin_bound") is True):
184:                 recorded = self.authority.call("record", response["result"])
185:                 if recorded.get("status") not in {"QUARANTINED", "RESULT_DUPLICATE"}:
186:                     return recorded
187:                 context = self.authority.call("reconciliation_context", {
188:                     "rid": payload["rid"], "window_id": payload["window_id"], "B_rid": payload["B_rid"]})
189:                 for rid in context["known_A_rids"]:
190:                     self.call("dispose", {"disposal_op": "reconcile_" + rid, "rid": rid}, "user")
191:                 context = self.authority.call("reconciliation_context", {
192:                     "rid": payload["rid"], "window_id": payload["window_id"], "B_rid": payload["B_rid"]})
193:         elif payload["step"] != "finish":
194:             return {"status": "REJECTED", "reason": "RECONCILIATION_STEP"}
195:         window = context["window"]
196:         model = self.config.get("reconciliation_model", {})
197:         facts = {key: query.get(key, False) for key in ("exact_authorized_read", "record_found", "origin_bound")}
198:         facts.update(single_unknown_creator=window["unknown_creators_at_open"] == [payload["rid"]],
199:             creation_paused=window["active"], A_revoked=context["A_revoked"],
200:             external_writers_excluded=model.get("external_writers_excluded") is True,
201:             future_retry_excluded=model.get("single_open_no_retry") is True,
202:             known_A_units_inactive=context["known_A_units_inactive"],
203:             B_preserved_after_disposal=context["B_preserved_after_disposal"],
204:             actual_sends=query.get("actual_sends", 0), per_send_effect_bound=model.get("per_send_effect_bound"),
205:             observed_distinct_effects=query.get("observed_distinct_effects", 0))
206:         target = context["target"]
207:         binding = {"rid": target["rid"], "attempt_id": target["attempt_id"], "request_digest": target["digest"], **target["origin"]}
208:         safe_context = {key: context[key] for key in ("target", "A_revoked", "known_A_rids", "known_A_units_inactive", "B_preserved_after_disposal", "disposition_versions")}
209:         safe_context["window"] = {key: window[key] for key in ("window_id", "target_rid", "active", "unknown_creators_at_open", "opened_version")}
210:         packet = {"context": safe_context, "query": query, "model": model}
211:         evidence = {"query_ref": query.get("query_ref"), "identifier_receipt_ref": query.get("identifier_receipt_ref"),
212:                     "source_lemma_ref": model.get("source_lemma_ref"), "packet": packet, "packet_ref": digest(packet),
213:                     "origin": model.get("evidence_origin", "IDENTIFIER_POINT_READ"),
214:                     "enumeration_ref": query.get("enumeration_ref"), "authorized_scope_ref": query.get("authorized_scope_ref")}
215:         receipt = make_receipt(binding, facts, evidence)
216:         return self.authority.call("save_reconciliation", {"rid": payload["rid"], "window_id": payload["window_id"],
217:                                    "receipt": receipt, "query_evidence": query, "B_rid": payload["B_rid"]})
```


## C03 R04 additional read D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_provider.py

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
```

```text
114:         result = {key: payload[key] for key in ("rid", "digest", "origin", "attempt_id", "release_version")}
115:         result.update(material=result_material, outcome="OK")
116:         if kind in {"issue", "refresh"} and self.profile.get("identifier_journal"):
117:             self.identifier_log.emit("verified_native_identifier", **{key: result[key] for key in
118:                 ("rid", "digest", "origin", "attempt_id", "release_version")},
119:                 native_unit_id=result_material["derived"]["verified_claims"]["jti"],
120:                 verified_account=result_material["expected_account"], verified_client=result_material["client"],
121:                 native_sequence=answer["sequence"])
122:             if kind == "refresh" and self.profile.get("hold_after_identifier"):
123:                 path = self.root / "provider" / "identifier_ready.json"
124:                 write_json(path, {**context, "position": "identifier durable, response delivery held"})
125:                 while not path.with_suffix(".release").exists():
126:                     time.sleep(0.01)
127:         if kind == "refresh" and self.profile.get("hold_response_without_identifiers"):
128:             path = self.root / "provider" / "response_ready_without_identifiers.json"
129:             write_json(path, {**context, "position": "response withheld; no operational body or identifier retained"})
130:             while not path.with_suffix(".release").exists():
131:                 time.sleep(0.01)
132:         if self.profile.get("durable_inbox", True):
133:             with self.lock:
134:                 nonce = os.urandom(12)
135:                 raw = nonce + AESGCM(self.key).encrypt(nonce, canonical(result), b"native-inbox-v1")
136:                 with self.inbox.open("ab") as stream:
137:                     stream.write(base64.b64encode(raw) + b"\n")
138:                     stream.flush()
139:                     os.fsync(stream.fileno())
140:                 self.results[result["attempt_id"]] = result
141:             self.log.emit("operational_result_durable", rid=payload["rid"], attempt_id=payload["attempt_id"])
142:         if kind == "refresh" and self.profile.get("hold_refresh"):
143:             barrier = self.root / "provider" / "refresh_received.json"
144:             write_json(barrier, {"rid": payload["rid"], "attempt_id": payload["attempt_id"],
145:                                  "native_sequence": answer["sequence"], "durable_inbox": bool(self.profile.get("durable_inbox"))})
146:             while not barrier.with_suffix(".release").exists():
147:                 time.sleep(0.01)
148:         self.log.emit("result_delivered_to_controller", rid=payload["rid"], attempt_id=payload["attempt_id"])
149:         return {"status": "PROVIDER_RESULT", **result}
```


## C04 R04 additional read D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_http.py

```text
161:         if operation == "get_tokens":
162:             if not self.policy.get("organization_scope_read_enabled") or not self.policy.get("dedicated_scope"):
163:                 raise InvalidInput("EXPLICIT_ORGANIZATION_READ_REQUIRED")
164:             if form is not None or payload is not None:
165:                 raise InvalidInput("FIXED_SCOPE_QUERY_FIELDS")
166:             path += "?" + urllib.parse.urlencode({"owner": "admin", "organization": organization,
167:                 "pageSize": self.policy["page_size"], "p": 1, "field": "", "value": "", "sortField": "name", "sortOrder": "ascend"})
168:         if operation == "get_token":
169:             if (not self.policy.get("exact_point_reads_enabled") or not isinstance(payload, dict)
170:                     or set(payload) != {"id"} or not payload["id"].startswith("admin/")
171:                     or not context or context.get("verified_unit_id") != payload["id"]):
172:                 raise InvalidInput("EXACT_OWNED_RECORD_BINDING_REQUIRED")
173:             path += "?" + urllib.parse.urlencode({"id": payload["id"], "organization": organization})
174:             payload = None
175:         if operation == "get_user":
176:             path += "?" + urllib.parse.urlencode({"id": organization + "/" + actor})
177:         if operation == "disable_user":
178:             path += "?" + urllib.parse.urlencode({"id": organization + "/" + actor, "columns": "isForbidden"})
179:         data = None
180:         request_headers = dict(headers or {})
181:         if any(key.lower() in {"cookie", "host"} for key in request_headers):
```
