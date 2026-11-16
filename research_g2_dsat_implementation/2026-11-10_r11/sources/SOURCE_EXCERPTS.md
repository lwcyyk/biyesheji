# R11 关键源码定位
仅已有源码摘录，未执行。

## C01 D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\storage.py
SHA256 2d17cf95d7d724d8debbeb47c2df28cfd537aa696bde47edb98908170a12de83

```text
21: AAD = b"auth-lifecycle/online-state/schema-1"
22: 
23: 
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
```

```text
47:     def __init__(self, directory, key_path, operation_limit=None):
48:         self.directory = Path(directory)
49:         self.directory.mkdir(parents=True, exist_ok=True)
50:         self.key_path = Path(key_path)
51:         self.lock = threading.RLock()
52:         self.metrics = EventLog(self.directory / "database_ops.jsonl")
53:         self.operation_limit = operation_limit
54:         self.operations = 0
55:         if self.metrics.path.exists():
56:             self.operations = len(self.metrics.path.read_bytes().splitlines())
57:         marker = self.directory / "initialized"
58:         if marker.exists() and not (self.directory / "authority.db").exists():
59:             raise ValueError("EXISTING_AUTHORITY_DATA_MISSING")
60:         self.connection = sqlite3.connect(self.directory / "authority.db",
61:                                           isolation_level=None, check_same_thread=False)
62:         self.connection.row_factory = sqlite3.Row
63:         journal_mode = self.execute("PRAGMA journal_mode=WAL").fetchone()[0]
64:         self.execute("PRAGMA synchronous=FULL")
65:         synchronous = self.execute("PRAGMA synchronous").fetchone()[0]
66:         self.execute("PRAGMA busy_timeout=5000")
67:         self.execute("PRAGMA wal_autocheckpoint=1000")
68:         if journal_mode != "wal" or synchronous != 2:
69:             raise ValueError("DURABILITY_CONFIGURATION_MISMATCH")
70:         schema_version = self.execute("PRAGMA user_version").fetchone()[0]
71:         if schema_version not in {0, 1, 2}:
72:             raise ValueError("UNSUPPORTED_SCHEMA_VERSION")
73:         if schema_version == 0:
74:             migration = (Path(__file__).with_name("migration.sql")).read_text()
75:             for statement in migration.split(";"):
76:                 if statement.strip():
77:                     self.execute(statement)
78:         if schema_version < 2:
79:             self.execute(Path(__file__).with_name("migration_2.sql").read_text())
80:         row = self.execute("SELECT version FROM authority_state WHERE id=1").fetchone()
81:         if row is None:
82:             if marker.exists():
83:                 raise ValueError("EXISTING_AUTHORITY_STATE_MISSING")
84:             state = {"grants": {}, "requests": {}, "grant_ops": {}, "revoke_ops": {}}
85:             self.execute("INSERT INTO authority_state VALUES(1,0,?)", (self.encrypt(state),))
86:         marker.touch(exist_ok=True)
87:         write_json(self.directory / "storage_configuration.json", {
88:             "sqlite_version": sqlite3.sqlite_version, "journal_mode": journal_mode,
89:             "synchronous": synchronous, "busy_timeout_ms": 5000,
90:             "wal_autocheckpoint_pages": 1000, "mutation_transaction": "BEGIN IMMEDIATE",
91:             "application_snapshot": "single AES-GCM encrypted row", "schema_version": 2})
92: 
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
197:     def admit(self, state, payload, version):
198:         exact_fields(payload, ("caller", "request"))
199:         caller = identifier(payload["caller"])
200:         request = normalized_request(payload["request"])
201:         fingerprint = digest({"caller": caller, "request": request})
202:         existing = state["requests"].get(request["rid"])
203:         if existing:
204:             if existing["digest"] != fingerprint:
205:                 return {"status": "CONFLICT", "reason": "RID_BODY_CONFLICT"}
206:             return {"status": "DUPLICATE", **request_projection(existing)}
207:         grant = next((g for g in state["grants"].values() if g["handle"] == request["handle"]), None)
208:         if grant is None or grant["caller"] != caller:
209:             return {"status": "REJECTED", "reason": "BINDING_MISMATCH"}
210:         if any(grant[key] != request[key] for key in ("task", "account", "audience", "generation")):
211:             return {"status": "REJECTED", "reason": "BINDING_MISMATCH"}
212:         if not grant["active"] or request["operation"] not in grant["operations"]:
213:             return {"status": "REJECTED", "reason": "APPROVAL_INACTIVE_OR_OPERATION_DENIED"}
214:         if request["operation"] in {"issue", "refresh"} and state.get("reconciliation_windows", {}).get(request["account"], {}).get("active"):
215:             return {"status": "REJECTED", "reason": "RECONCILIATION_CREATION_PAUSED"}
216:         if grant["reserved"] + grant["spent"] >= grant["limit"]:
217:             return {"status": "REJECTED", "reason": "BUDGET_EXHAUSTED"}
218:         origin = {key: grant[key] for key in
219:                   ("grant_id", "caller", "task", "account", "audience", "generation")}
220:         saved = {"rid": request["rid"], "digest": fingerprint, "origin": origin,
221:                  "request": request, "phase": "QUEUED", "attempt_id": None,
222:                  "release_version": None, "result_digest": None, "result_material": None}
223:         state["requests"][request["rid"]] = saved
224:         grant["reserved"] += 1
225:         return {"status": "ADMITTED", **request_projection(saved)}
```

```text
261:     def record(self, state, payload, version):
262:         fields = ("rid", "digest", "origin", "attempt_id", "release_version", "material", "outcome")
263:         exact_fields(payload, fields)
264:         req = state["requests"].get(payload["rid"])
265:         if req is None or any(req[key] != payload[key] for key in
266:                               ("digest", "origin", "attempt_id", "release_version")):
267:             return {"status": "CONFLICT", "reason": "RESULT_SOURCE_CONFLICT"}
268:         if payload["outcome"] != "OK":
269:             raise InvalidInput("INVALID_RESULT")
270:         validate_material(payload["material"], req["origin"]["account"], req["origin"]["audience"])
271:         result_digest = digest(payload)
272:         if req["result_digest"]:
273:             if req["result_digest"] != result_digest:
274:                 return {"status": "CONFLICT", "reason": "RESULT_BODY_CONFLICT"}
275:             return {"status": "RESULT_DUPLICATE", **request_projection(req)}
276:         if req["phase"] != "DISPATCHED_UNKNOWN" or not req["attempt_id"]:
277:             return {"status": "REJECTED", "reason": "RESULT_WITHOUT_RELEASE"}
278:         grant = state["grants"][req["origin"]["grant_id"]]
279:         req["result_digest"] = result_digest
280:         req["result_material"] = payload["material"]
281:         req["phase"] = "RESULT_AVAILABLE" if grant["active"] else "QUARANTINED"
282:         return {"status": req["phase"], **request_projection(req)}
```

```text
284:     def revoke(self, state, payload, version):
285:         exact_fields(payload, ("revoke_op", "grant_id"))
286:         identifier(payload["revoke_op"])
287:         identifier(payload["grant_id"])
288:         old = state["revoke_ops"].get(payload["revoke_op"])
289:         if old:
290:             if old["grant_id"] != payload["grant_id"]:
291:                 return {"status": "CONFLICT", "reason": "REVOKE_OPERATION_CONFLICT"}
292:             return old
293:         grant = state["grants"].get(payload["grant_id"])
294:         if grant is None:
295:             return {"status": "REJECTED", "reason": "UNKNOWN_GRANT"}
296:         grant["active"] = False
297:         for req in state["requests"].values():
298:             if req["origin"]["grant_id"] != grant["grant_id"]:
299:                 continue
300:             if req["phase"] == "QUEUED":
301:                 req["phase"] = "CANCELLED"
302:                 grant["reserved"] -= 1
303:             elif req["phase"] == "RESULT_AVAILABLE":
304:                 req["phase"] = "QUARANTINED"
305:         receipt = {"status": "LOCAL_REVOKE_COMMITTED", "grant_id": grant["grant_id"],
306:                    "commit_version": version}
307:         state["revoke_ops"][payload["revoke_op"]] = receipt
308:         return receipt
```

```text
346:     def begin_reconciliation(self, state, payload, version):
347:         exact_fields(payload, ("rid", "window_id"))
348:         identifier(payload["window_id"])
349:         req = state["requests"].get(payload["rid"])
350:         if req is None:
351:             return {"status": "UNKNOWN", "reason": "UNKNOWN_ATTEMPT"}
352:         account = req["origin"]["account"]
353:         windows = state.setdefault("reconciliation_windows", {})
354:         old = windows.get(account)
355:         if old:
356:             if old["window_id"] != payload["window_id"] or old["target_rid"] != payload["rid"]:
357:                 return {"status": "CONFLICT", "reason": "WINDOW_CONFLICT"}
358:             return {"status": "WINDOW_OPEN", "window": old}
359:         if req["phase"] != "DISPATCHED_UNKNOWN" or req["request"]["operation"] != "refresh":
360:             return {"status": "UNKNOWN", "reason": "TARGET_NOT_UNKNOWN_REFRESH"}
361:         grant = state["grants"][req["origin"]["grant_id"]]
362:         if grant["active"]:
363:             return {"status": "REJECTED", "reason": "WITHDRAW_A_FIRST"}
364:         unknowns = [r["rid"] for r in state["requests"].values() if r["origin"]["account"] == account
365:                     and r["phase"] == "DISPATCHED_UNKNOWN" and r["request"]["operation"] in {"issue", "refresh"}]
366:         windows[account] = {"window_id": payload["window_id"], "target_rid": req["rid"],
367:                             "unknown_creators_at_open": unknowns, "active": True, "opened_version": version}
368:         return {"status": "WINDOW_OPEN", "window": windows[account]}
369: 
370:     def reconciliation_context(self, state, payload, version):
371:         exact_fields(payload, ("rid", "window_id", "B_rid"))
372:         req = state["requests"][payload["rid"]]
373:         window = state.get("reconciliation_windows", {}).get(req["origin"]["account"])
374:         if not window or window["window_id"] != payload["window_id"]:
375:             return {"status": "UNKNOWN", "reason": "WINDOW_UNAVAILABLE"}
376:         a_rows = [r for r in state["requests"].values() if r["origin"]["grant_id"] == req["origin"]["grant_id"] and r["result_material"]]
377:         disposals = [d for d in state.get("disposals", {}).values() if d["rid"] in {r["rid"] for r in a_rows}]
378:         last_disposal = max((d.get("completed_version", 0) for d in disposals), default=0)
379:         b = state["requests"].get(payload["B_rid"])
380:         b_ok = bool(b and b["origin"]["account"] == req["origin"]["account"] and b["origin"]["grant_id"] != req["origin"]["grant_id"]
381:                     and b["request"]["operation"] == "userinfo" and b["phase"] == "RESULT_AVAILABLE"
382:                     and b["release_version"] > last_disposal and last_disposal > 0
383:                     and state["grants"][b["origin"]["grant_id"]]["active"])
384:         account_grants = [g for g in state["grants"].values() if g["account"] == req["origin"]["account"]]
385:         known_ids = sorted({r["result_material"]["derived"]["verified_claims"]["jti"]
386:             for r in state["requests"].values() if r["origin"]["account"] == req["origin"]["account"]
387:             and isinstance(r["result_material"], dict) and r["result_material"].get("kind") == "casdoor_oauth"
388:             and r["result_material"].get("derived", {}).get("verified_claims", {}).get("jti")})
389:         return {"status": "RECONCILIATION_CONTEXT", "window": window, "target": request_projection(req),
390:                 "A_revoked": not state["grants"][req["origin"]["grant_id"]]["active"],
391:                 "known_A_rids": [r["rid"] for r in a_rows],
392:                 "known_A_units_inactive": bool(a_rows) and all(r["phase"] == "DISPOSED" for r in a_rows),
393:                 "B_preserved_after_disposal": b_ok, "disposition_versions": [d.get("completed_version") for d in disposals],
394:                 "known_unit_ids": known_ids, "account_grant_count": len(account_grants),
395:                 "account_budget_total": sum(g["limit"] for g in account_grants)}
396: 
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

## C02 D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\services.py
SHA256 d8ea05120fc8559a95050e4c71a094eefb73e29d22e1de66494d8c8e1975993a

```text
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
82:         if operation == "recover":
83:             return self.recover()
84:         if not self.ready and self.recover().get("status") != "RECOVERED":
85:             return {"status": "UNKNOWN", "reason": "RECOVERY_INCOMPLETE"}
86:         if operation == "grant":
87:             return self.authority.call("grant", payload)
88:         if operation == "revoke":
89:             self.barrier("before_revoke")
90:             result = self.authority.call("revoke", payload)
91:             if result.get("status") == "LOCAL_REVOKE_COMMITTED":
92:                 self.barrier("after_revoke_commit")
93:             return result
94:         if operation == "status":
95:             result = self.authority.call("recover", {})
96:             if result.get("status") != "RECOVERED" or identity == "user":
97:                 return result
98:             result["approvals"] = [x for x in result["approvals"] if x["caller"] == identity]
99:             result["requests"] = [x for x in result["requests"] if x["origin"]["caller"] == identity]
100:             result["obligations"] = [x["rid"] for x in result["requests"]
101:                                      if x["phase"] in {"DISPATCHED_UNKNOWN", "QUARANTINED"}]
102:             return result
103:         if operation == "dispose":
104:             released = self.authority.call("prepare_disposal", payload)
105:             if not released.get("send"):
106:                 return {key: value for key, value in released.items() if key != "material"}
107:             response = self.provider.call("dispose", released)
108:             if response.get("status") != "DISPOSAL_RESPONSE":
109:                 return {"status": "UNKNOWN", "reason": "NATIVE_DISPOSAL_UNCERTAIN"}
110:             return self.authority.call("record_disposal", {
111:                 "disposal_op": payload["disposal_op"], "rid": payload["rid"], "http": response["http"],
112:                 "userinfo_http": response["userinfo_http"], "userinfo_accepted": response["userinfo_accepted"],
113:                 "introspection_active": response["introspection_active"]})
114:         if operation == "begin_reconciliation":
115:             return self.authority.call("begin_reconciliation", payload)
116:         if operation == "reconcile":
117:             return self.reconcile(payload)
118:         if operation == "deliver":
119:             exact_fields(payload, ("rid",))
120:             identifier(payload["rid"])
121:             known = self.authority.call("recover", {})
122:             if known.get("status") != "RECOVERED":
123:                 return known
124:             req = next((x for x in known["requests"] if x["rid"] == payload["rid"]), None)
125:             if req is None or req["attempt_id"] is None:
126:                 return {"status": "UNKNOWN", "reason": "NO_KNOWN_ATTEMPT"}
127:             lookup = {key: req[key] for key in
128:                       ("rid", "digest", "origin", "attempt_id", "release_version")}
129:             result = self.provider.call("lookup", lookup)
130:             return self.record_result(result)
131:         if operation != "call":
132:             return {"status": "REJECTED", "reason": "INVALID_OPERATION"}
133:         request = normalized_request(payload)
134:         self.barrier("before_admit")
135:         admitted = self.authority.call("admit", {"caller": identity, "request": request})
136:         if admitted.get("status") not in {"ADMITTED", "DUPLICATE"}:
137:             return admitted
138:         self.barrier("after_admit")
139:         if admitted["phase"] != "QUEUED":
140:             return admitted
141:         released = self.authority.call("release", {
142:             "caller": identity, "rid": request["rid"], "digest": admitted["digest"]})
143:         if not released.get("send"):
144:             return released
145:         self.barrier("after_release")
146:         provider_request = {key: released[key] for key in
147:                             ("rid", "digest", "origin", "attempt_id", "release_version",
148:                              "material", "operation", "payload")}
149:         result = self.provider.call("perform", provider_request)
150:         self.barrier("after_effect")
151:         return self.record_result(result)
152: 
153:     def record_result(self, result):
154:         if result.get("status") != "PROVIDER_RESULT":
155:             return {"status": "UNKNOWN", "reason": "EXTERNAL_RESULT_UNCERTAIN"}
156:         fields = ("rid", "digest", "origin", "attempt_id", "release_version", "material", "outcome")
157:         if not all(key in result for key in fields):
158:             return {"status": "UNKNOWN", "reason": "INVALID_PROVIDER_RESULT"}
159:         envelope = {key: result[key] for key in fields}
160:         return self.authority.call("record", envelope)
```

```text
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

```text
297:         def do_POST(self):
298:             started = time.monotonic_ns()
299:             request_bytes = 0
300:             operation = self.path.removeprefix("/")
301:             identity = None
302:             supplied = self.headers.get("Authorization", "")
303:             for name, token in config["identities"].items():
304:                 if hmac.compare_digest(supplied, "Bearer " + token):
305:                     identity = name
306:             allowed = config["permissions"].get(identity, [])
307:             try:
308:                 if operation not in allowed:
309:                     result = {"status": "REJECTED", "reason": "IDENTITY_OR_OPERATION_DENIED"}
310:                 else:
311:                     length = int(self.headers.get("Content-Length", "0"))
312:                     if not 0 < length <= 65536:
313:                         raise InvalidInput("BODY_SIZE")
314:                     raw = self.rfile.read(length)
315:                     request_bytes = len(raw)
316:                     payload = strict_json(raw)
317:                     if role == "authority":
318:                         result = implementation.call(operation, payload)
319:                     else:
320:                         result = implementation.call(operation, payload, identity)
321:             except (ValueError, TypeError, KeyError, InvalidInput):
322:                 result = {"status": "REJECTED", "reason": "INVALID_INPUT"}
323:             except Exception:
324:                 result = {"status": "UNKNOWN", "reason": "SERVICE_UNAVAILABLE"}
```

## C04 D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_provider.py
SHA256 5db41c26312960a668785f20b0c7988ab31030bebe92773cef46e5187f6df58f

```text
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
104:         self.log.emit("native_response_received", rid=payload["rid"], attempt_id=payload["attempt_id"],
105:                       native_sequence=answer["sequence"], http=answer["http"])
106:         if answer["http"] != 200 or answer["error_type"]:
107:             return {"status": "UNKNOWN", "reason": "NATIVE_RESULT_UNCERTAIN"}
108:         if kind == "userinfo":
109:             if answer["body"].get("sub") != self.profile["actor"]["id"]:
110:                 raise InvalidInput("USERINFO_ACCOUNT_MISMATCH")
111:             result_material = material
112:         else:
113:             result_material = token_bundle(answer["body"], self.profile)
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

## C05 D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_http.py
SHA256 7ccfa54e8982559fa1a16b519a3f0ab41ea237449ae45019d7f8140aec022bb4

```text
101:     def reserve(self, operation, actor, context=None):
102:         con = sqlite3.connect(self.budget_path, timeout=5, isolation_level=None)
103:         try:
104:             con.execute("BEGIN IMMEDIATE")
105:             used = con.execute("SELECT COUNT(*) FROM requests WHERE category=?", (self.category,)).fetchone()[0]
106:             total = con.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
107:             if used >= self.policy["categories"][self.category] or total >= self.policy["total"]:
108:                 raise RuntimeError("NATIVE_REQUEST_BUDGET_EXHAUSTED")
109:             context = context or {}
110:             cursor = con.execute("INSERT INTO requests(category,operation,actor,started_ns,attempt_id,rid,request_digest) VALUES(?,?,?,?,?,?,?)",
111:                                  (self.category, operation, actor, time.monotonic_ns(), context.get("attempt_id"), context.get("rid"), context.get("digest")))
112:             con.execute("COMMIT")
113:             return cursor.lastrowid
114:         finally:
115:             con.close()
```

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
```

```text
189:         sequence = self.reserve(operation, actor, context)
190:         started = time.monotonic_ns()
191:         response = {"http": 0, "body": {}}
192:         raw = b""
193:         error_type = None
194:         try:
195:             request = urllib.request.Request("http://127.0.0.1:18081" + path,
196:                                              data=data, headers=request_headers, method=method)
197:             try:
198:                 answer = self.opener.open(request, timeout=timeout)
199:             except urllib.error.HTTPError as error:
200:                 answer = error
201:             with answer:
202:                 response["http"] = answer.status
203:                 raw = answer.read(1024 * 1024)
204:             try:
205:                 response["body"] = json.loads(raw) if raw else {}
206:             except (ValueError, UnicodeDecodeError):
207:                 error_type = "ResponseParseFailure"
208:         except Exception as error:
209:             error_type = type(error).__name__
210:         finished = time.monotonic_ns()
211:         secret_record = {"sequence": sequence, "category": self.category, "operation": operation,
212:                          "actor": actor, "form": form, "payload": payload, "response": response,
213:                          "raw_response_base64": base64.b64encode(raw).decode(),
214:                          "error_type": error_type, "started_ns": started, "finished_ns": finished}
215:         nonce = os.urandom(12)
216:         if self.audit_public is not None:
217:             audit_key = AESGCM.generate_key(bit_length=256)
218:             capsule = self.audit_public.encrypt(audit_key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
219:             encrypted = b"M4AE" + len(capsule).to_bytes(2, "big") + capsule + nonce + AESGCM(audit_key).encrypt(nonce, canonical(secret_record), b"native-http-v2")
220:         else:
221:             encrypted = nonce + AESGCM(self.key).encrypt(nonce, canonical(secret_record), b"native-http-v1")
222:         path = self.batch / "secure" / "http" / (str(sequence) + ".aes")
223:         with path.open("wb") as stream:
224:             stream.write(encrypted)
225:             stream.flush()
226:             os.fsync(stream.fileno())
227:         con = sqlite3.connect(self.budget_path)
228:         con.execute("UPDATE requests SET http=?,error_type=?,request_bytes=?,response_bytes=? WHERE seq=?",
229:                     (response["http"], error_type, len(data or b""), len(raw), sequence))
230:         con.commit()
231:         con.close()
232:         return {**response, "error_type": error_type, "sequence": sequence}
```

## C08 D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\dsat_types.py
SHA256 0962d19d5ea5b684cc8c8611dc1d6351950235ec82aadf592475c9dadb645b03

```text
139:     @classmethod
140:     def parse(cls, value, limits):
141:         fields(value, ("rid", "attempt_id", "release_version", "request_digest", "origin",
142:                        "operation", "source_rid", "phase", "original_request"))
143:         o = origin(value["origin"])
144:         body = value["original_request"]
145:         fields(body, ("rid", "handle", "task", "account", "audience", "generation", "operation", "payload"))
146:         for key in set(body) - {"payload"}:
147:             if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", ident(body[key])):
148:                 raise InputError()
149:         operation = ident(value["operation"])
150:         if operation not in {"issue", "refresh", "userinfo"}:
151:             raise InputError()
152:         fields(body["payload"], () if operation == "issue" else ("source_rid",))
153:         source = None if operation == "issue" else ident(body["payload"]["source_rid"])
154:         if (body["rid"] != value["rid"] or body["operation"] != operation
155:                 or source != value["source_rid"]
156:                 or any(body[k] != o[k] for k in ("task", "account", "audience", "generation"))):
157:             raise InputError()
158:         expected = hashlib.sha256(canonical({"caller": o["caller"], "request": body})).hexdigest()
159:         if sha(value["request_digest"]) != expected:
160:             raise InputError("REJECT_UNAUTHORIZED")
161:         phase = ident(value["phase"])
162:         if phase not in {"QUEUED", "CANCELLED", "DISPATCHED_UNKNOWN", "RESULT_AVAILABLE", "QUARANTINED", "DISPOSED"}:
163:             raise InputError()
164:         aid = None if value["attempt_id"] is None else ident(value["attempt_id"])
165:         ver = None if value["release_version"] is None else integer(value["release_version"], limits)
166:         if (phase in {"QUEUED", "CANCELLED"}) != (aid is None and ver is None):
167:             raise InputError()
168:         if phase not in {"QUEUED", "CANCELLED"} and (aid is None or ver is None):
169:             raise InputError()
170:         return cls(ident(value["rid"]), aid, ver, expected, o, operation, source, phase)
```

```text
358: class FrozenTrust:
359:     """Caller-supplied frozen manifest, kept outside the untrusted evidence bundle."""
360:     snapshot_digest: str
361:     contract_digest: str
362:     obligations_digest: str
363:     costs_digest: str
364:     envelope_digests: dict
365:     producers: tuple
366:     permits: tuple
367: 
368:     @classmethod
369:     def parse(cls, value):
370:         fields(value, ("mode", "snapshot_digest", "contract_digest", "obligations_digest", "costs_digest",
371:                        "envelope_digests", "producers", "permits"))
372:         if value["mode"] != "SYNTHETIC_CONTRACT" or type(value["envelope_digests"]) is not dict:
373:             raise InputError("REJECT_UNAUTHORIZED")
374:         return cls(sha(value["snapshot_digest"]), sha(value["contract_digest"]),
375:                    sha(value["obligations_digest"]), sha(value["costs_digest"]),
376:                    {ident(k): sha(v) for k, v in value["envelope_digests"].items()},
377:                    ids(value["producers"]), ids(value["permits"]))
```

## C09 D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\dsat_projection.py
SHA256 63b9ba5efe8565868047510a1bbaa477f485d6903a0dc279c27c979106d98946

```text
36: def _project(bundle, trusted_manifest, limits):
37:     encoded = canonical(bundle)
38:     if len(encoded) > limits.input_bytes:
39:         raise InputError("UNKNOWN_RESOURCE_LIMIT")
40:     # Work on a detached JSON snapshot; output lists never alias caller input.
41:     bundle = json.loads(encoded)
42:     fields(bundle, ("mode", "authority", "attempts", "capacity_contracts", "envelopes", "history",
43:                     "contract", "scope", "obligations", "costs"))
44:     if bundle["mode"] != "SYNTHETIC_CONTRACT":
45:         raise InputError("REJECT_UNAUTHORIZED")
46:     trust = trusted_manifest if isinstance(trusted_manifest, FrozenTrust) else FrozenTrust.parse(trusted_manifest)
47:     contract_binding = {k: bundle[k] for k in ("contract", "scope", "attempts", "capacity_contracts")}
48:     for actual, expected in (
49:         (digest("snapshot", bundle["authority"]), trust.snapshot_digest),
50:         (digest("projection_contract", contract_binding), trust.contract_digest),
51:         (digest("O_before", bundle["obligations"]), trust.obligations_digest),
52:         (digest("cost_ledger", bundle["costs"]), trust.costs_digest),
53:     ):
54:         if actual != expected:
55:             raise InputError("REJECT_UNAUTHORIZED")
```

```text
107:     for attempt in attempts:
108:         req = requests.get(attempt.rid)
109:         cap = cmap.get(attempt.capacity_contract_ref)
110:         if (req is None or req.operation not in {"issue", "refresh"} or req.attempt_id is None
111:                 or req.release_version is None or req.release_version > authority.version):
112:             issue("INSUFFICIENT_COVERAGE", attempt.id)
113:             structure_ready = False
114:         if cap is None or cap.attempt_ref != attempt.id or cap.capacity is None:
115:             issue("INSUFFICIENT_COVERAGE", "capacity:" + attempt.id)
116:             structure_ready = False
117:         else:
118:             cvalues[attempt.id] = cap.capacity
119:         if attempt.audit_required:
120:             add_obligation("await_terminal:" + attempt.id, "await_terminal", [attempt.id])
121:     for req in authority.requests:
122:         grant = grants.get(req.origin["grant_id"])
123:         if grant is None or grant.origin != req.origin:
124:             issue("EVIDENCE_CONFLICT", req.rid)
125:         if req.phase == "QUEUED" and (grant is None or not grant.active or req.operation not in grant.operations):
126:             issue("REJECT_UNAUTHORIZED", req.rid)
127:         if req.operation in {"refresh", "userinfo"}:
128:             source = requests.get(req.source_rid)
129:             if source is None or source.origin != req.origin:
130:                 issue("REJECT_UNAUTHORIZED", req.rid)
131:         if req.attempt_id is not None and req.operation in {"issue", "refresh"}:
132:             a = by_rid.get(req.rid)
133:             if a is None:
134:                 issue("INSUFFICIENT_COVERAGE", req.rid)
135:                 structure_ready = False
136:             if req.phase == "DISPATCHED_UNKNOWN":
137:                 key = a.id if a else req.attempt_id
138:                 add_obligation("settle:" + key, "settle", [key])
139:         elif req.attempt_id is not None and req.operation == "userinfo" and req.phase == "DISPATCHED_UNKNOWN":
140:             add_obligation("exec:" + req.rid, "exec", [req.rid])
141:     for grant in authority.grants:
142:         if (grant.active and {"issue", "refresh"}.intersection(grant.operations)
143:                 and grant.limit > grant.spent + grant.reserved and not authority.creation_paused):
144:             frontiers.add("frontier:" + grant.origin["grant_id"])
145:     if frontiers:
146:         issue("OPEN_FRONTIER")
147:         for ref in frontiers:
148:             add_obligation(ref, "frontier", [ref])
```

```text
179:     for env in valid_records:
180:         if env.kind != "CREATION":
181:             continue
182:         w = env.payload
183:         if w.birth_ref is None:
184:             unknown_aliases.append({"unit_id": w.unit_id, "evidence_ref": env.id})
185:             issue("INSUFFICIENT_COVERAGE", "birth:" + w.unit_id)
186:             continue
187:         if w.unit_id in unit_keys and unit_keys[w.unit_id] != w.birth_key:
188:             issue("EVIDENCE_CONFLICT", w.unit_id)
189:             continue
190:         unit_keys[w.unit_id] = w.birth_key
191:         candidates = set(w.source_candidates) if w.source_candidates else set(amap)
192:         if not candidates <= set(amap):
193:             issue("INSUFFICIENT_COVERAGE", "origin:" + w.unit_id)
194:             structure_ready = False
195:             continue
196:         if w.request_binding is not None:
197:             binding = w.request_binding
198:             req = requests.get(binding["rid"])
199:             a = by_rid.get(binding["rid"])
200:             if (req is None or a is None or req.request_digest != binding["request_digest"]
201:                     or req.attempt_id != binding["attempt_id"] or req.release_version != binding["release_version"]
202:                     or req.origin != binding["origin"]):
203:                 issue("EVIDENCE_CONFLICT", env.id)
204:                 continue
205:             if a.id not in candidates:
206:                 issue("EVIDENCE_CONFLICT", env.id)
207:             candidates &= {a.id}
208:             grant = grants.get(req.origin["grant_id"])
209:             if grant is not None and not grant.active:
210:                 quarantined.append({"unit_id": w.unit_id, "grant_id": grant.origin["grant_id"], "evidence_ref": env.id})
211:         if w.birth_key not in groups:
212:             groups[w.birth_key] = {"aliases": set(), "sources": candidates, "refs": set(), "deleted": False}
213:         group = groups[w.birth_key]
214:         group["aliases"].add(w.unit_id)
215:         group["sources"] &= candidates
216:         group["refs"].add(env.id)
217:         group["deleted"] |= w.deleted
218:         if not group["sources"]:
219:             issue("EVIDENCE_CONFLICT", w.unit_id)
```

```text
249:         current = env.scope.valid_until >= authority.now and env.source_version == contract["source_version"]
250:         if not current:
251:             issue("STALE_EVIDENCE", env.id)
252:         if (uid is not None and obs.status_kind == "SUSTAINED_INACTIVITY" and obs.performed
253:                 and obs.http == 200 and obs.active is False and obs.frame_ref in frames
254:                 and set(paths) <= set(obs.paths) and set(paths) <= set(env.scope.paths) and current):
255:             D.add(uid)
256:     E = [[u["unit_id"], i] for u in units for i in u["source_candidates"]]
257:     if len(E) > limits.edges:
258:         raise InputError("UNKNOWN_RESOURCE_LIMIT")
259:     for unit in units:
260:         if set(unit["source_candidates"]).intersection(targets) and unit["unit_id"] not in D:
261:             add_obligation("close:" + unit["unit_id"], "close", [unit["unit_id"]])
262:     blocked = any(x["code"] in {"REJECT_UNAUTHORIZED", "EVIDENCE_CONFLICT"} for x in issues)
263:     math_input = None
264:     if structure_ready and not blocked:
265:         math_input = normalize_math({"I": list(amap), "T": list(targets), "c": cvalues,
266:                                      "U": [u["unit_id"] for u in units], "E": E, "D_P": list(D)}, limits)
267:     priority = ("EVIDENCE_CONFLICT", "REJECT_UNAUTHORIZED", "STALE_EVIDENCE", "OPEN_FRONTIER", "INSUFFICIENT_COVERAGE")
268:     codes = {i["code"] for i in issues}
269:     status = next((c for c in priority if c in codes), "UNKNOWN_PENDING")
270:     scope_ready = not issues and all(contract[k] for k in ("source_complete", "capacity_complete", "frontier_complete",
271:                                                           "external_writers_excluded", "derivations_covered"))
272:     return {"schema": "readonly-lifecycle-projection/1", "mode": "SYNTHETIC_CONTRACT",
273:             "status": status, "issues": issues, "math_input": math_input, "math_ready": math_input is not None,
274:             "partial_math": {"I": sorted(amap), "T": sorted(targets), "c_known": cvalues,
275:                              "capacity_unknown": sorted(set(amap) - set(cvalues)),
276:                              "U": sorted(u["unit_id"] for u in units), "E": sorted(E), "D_P": sorted(D)},
277:             "units": sorted(units, key=lambda u: u["unit_id"]), "unknown_aliases": unknown_aliases,
278:             "point_observations": point_observations, "quarantined": quarantined,
279:             "open_frontiers": sorted(frontiers), "source_scope_preconditions_declared": scope_ready,
280:             "creation_states": {a.id: "POSSIBLE_CREATION" for a in attempts},
281:             "origin_relations": [asdict(OriginRelation(u["unit_id"], tuple(u["source_candidates"]))) for u in units],
282:             "obligations_proposed": [proposed[k] for k in sorted(proposed)], "obligation_action": "PROPOSAL_ONLY_KEEP_EXISTING",
283:             "costs_retained": [asdict(c) for c in costs], "native_admission": "SOURCE_OR_REFINEMENT_GAP",
284:             "global_complete": False, "scope": dict(scope), "authority_version": authority.version,
285:             "work_counts": {"input_records": len(raw_records), "unique_evidence_ids": len(seen_ids), "births": len(units), "edges": len(E)}}
```

## C12 D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\dsat_commit.py
SHA256 82055a554fe5d15e7640fb14ea53064064cd91409d0ad41fc8983fbfaca0a778

```text
18: def artifact_path(path):
19:     path = Path(path).absolute()
20:     try:
21:         path.relative_to(RUN_ROOT)
22:     except ValueError as exc:
23:         raise CommitError("DB_PATH_DENIED") from exc
24:     for node in (path, *path.parents):
25:         if node.exists() and (node.is_symlink() or node.lstat().st_file_attributes & 0x400):
26:             raise CommitError("DB_PATH_DENIED")
27:     if path.resolve() != path:
28:         raise CommitError("DB_PATH_DENIED")
29:     return path
30: 
31: 
32: class FrozenRegistry:
33:     """Trusted offline configuration. A proposal cannot supply this registry."""
34:     def __init__(self, evidence_directory):
35:         self.directory = artifact_path(evidence_directory)
36:         self.directory.mkdir(parents=True, exist_ok=True)
37:         self.scope = strict_load(SCOPE_PATH.read_bytes())
38:         self.checker = self.scope["frozen_inputs"]["checker"]
39:         self.packets = {}
40:         self.sources = {}
41:         self.verified = {}
42:         self.checks = []
43:         fixtures = {}
44:         for ref in self.scope["frozen_inputs"]["fixtures"]:
45:             path = Path(ref["path"])
46:             copied = PROJECT/"tests/fixtures/dsat_commit"/path.name
47:             if copied.is_file():
48:                 path = copied
49:             data = path.read_bytes()
50:             if hashlib.sha256(data).hexdigest() != ref["sha256"]:
51:                 raise CommitError("REJECTED_PROOF_BINDING")
52:             fixtures[path.stem] = (strict_load(data), ref["sha256"])
53:         for ref in self.scope["frozen_inputs"]["proofs"]:
54:             path = Path(ref["path"]); data = path.read_bytes()
55:             copied = PROJECT/"tests/fixtures/dsat_commit"/path.name
56:             if copied.is_file():
57:                 data = copied.read_bytes()
58:             if hashlib.sha256(data).hexdigest() != ref["sha256"]:
59:                 raise CommitError("REJECTED_PROOF_BINDING")
60:             name = path.stem
61:             case_name = "A06" if name == "VAR_MISSING_D_A" else name.split("_")[1]
62:             case, fixture_hash = fixtures[case_name]
63:             bundle = clone(case["bundle"])
64:             if name == "VAR_MISSING_D_A":
65:                 bundle["envelopes"] = [x for x in bundle["envelopes"] if x["id"] != "syn:d:v1"]
66:             self.packets[name] = strict_load(data)
67:             self.sources[name] = {"fixture_ref": fixture_hash, "bundle": bundle}
```

```text
148: def base_digests(world):
149:     return {"base_O_digest": O_digest(world["dsat"]["O"]),
150:             "source_snapshot_digest": digest("source", world["source"]),
151:             "request_scope_digest": digest("scope", world["scope"]),
152:             "current_grant_digest": digest("grant", world["simulation"])}
153: 
154: 
155: def PrepareDSatCommit(snapshot, registry, proposal_id, actor=Actor("syn:manager"),
156:                      level="MATH_ARCHIVE", name=None):
157:     a, world = snapshot["a"], snapshot["world"]
158:     name = name or world["source"]["fixture_key"]
159:     packet = clone(registry.packets[name])
160:     oh = digest("scope", world["scope"])
161:     old_ids = {x["id"] for x in world["dsat"]["O"]}
162:     additions = [obligation(x, oh) for x in packet["bindings"]["O_before"] if x["id"] not in old_ids]
163:     for added in additions:
164:         added["dependency_epoch"] = world["source"]["epoch"]
165:     return seal({"schema": "dsat-commit/1", "mode": MODE,
166:         "authority_instance": world["authority_instance"], "proposal_id": proposal_id, "actor": actor.name,
167:         "base_authority_revision": a, "base_obligation_revision": world["dsat"]["obligation_revision"],
168:         **base_digests(world), "policy_epoch": world["policy_epoch"],
169:         "proof": packet, "packet_digest": packet["packet_digest"],
170:         "math_input_digest": packet["digests"]["math_input_digest"],
171:         "checker_source_digest": registry.checker["sha256"],
172:         "projection_digest": registry.binding(name),
173:         "projection_O_digest": legacy_digest("O_before", packet["bindings"]["O_before"]),
174:         "proof_context_O_digest": packet["digests"]["O_before_digest"],
175:         "obligations_delta": {"add": additions, "replace": []},
176:         "dependency_policy": {"require_current": False, "allow_history": True},
177:         "cost_delta": [{"id": "work:" + packet["packet_digest"][:24],
178:                         "body": {"amount": 1, "unit": "synthetic-work", "math_input_digest": packet["digests"]["math_input_digest"]}}],
179:         "requested_level": level})
180: 
181: 
182: def ValidateDSatCommit(body, snapshot, registry, now=100, limits=Limits()):
183:     """A pure plan over a trusted current snapshot and a trusted checked registry."""
184:     started = time.perf_counter_ns()
185:     world = snapshot["world"]
186:     name = world["source"]["fixture_key"]
187:     expected = registry.packets.get(name)
188:     record = registry.verified.get(name)
189:     packet = body["proof"]
190:     if expected is None or record is None or not record["accepted"] or canonical(packet) != canonical(expected):
191:         raise CommitError("REJECTED_PROOF_BINDING")
192:     if hashlib.sha256(Path(registry.checker["path"]).read_bytes()).hexdigest() != registry.checker["sha256"]:
193:         raise CommitError("REJECTED_PROOF_BINDING")
194:     wanted = {"packet_digest": expected["packet_digest"], "math_input_digest": expected["digests"]["math_input_digest"],
195:               "checker_source_digest": registry.checker["sha256"], "projection_digest": registry.binding(name),
196:               "projection_O_digest": legacy_digest("O_before", expected["bindings"]["O_before"]),
197:               "proof_context_O_digest": expected["digests"]["O_before_digest"]}
198:     if any(body[k] != v for k, v in wanted.items()) or packet_digest(packet) != packet["packet_digest"]:
199:         raise CommitError("REJECTED_PROOF_BINDING")
200:     if world["source"]["fixture_ref"] != registry.sources[name]["fixture_ref"] or world["source"]["bundle"] != registry.sources[name]["bundle"]:
201:         raise CommitError("REJECTED_ORIGIN_SCOPE")
202:     policy = body["dependency_policy"]
203:     integer(now)
```

## C24 D:\毕业设计\auth-lifecycle\scripts\check_dsat_certificate.py
SHA256 c4e5027a2f11ae867f8c87210f9148aa5b65a466280ba9b7ccce3be8b34033e2

```text
240: def _check(packet, expected_math, expected_scope, lim, expected_digests):
241:     if len(_encoded(packet)) > lim["input_bytes"]:
242:         raise Rejected("UNKNOWN_RESOURCE_LIMIT")
243:     _keys(packet, ("schema", "mode", "math_input", "bindings", "digests", "proof", "claims", "packet_digest"))
244:     if packet["schema"] != "dsat-proof/1" or packet["mode"] != "SYNTHETIC_CONTRACT":
245:         raise Rejected()
246:     expected_packet = hashlib.sha256(_encoded({"schema": "dsat-packet/1", "packet": {
247:         k: v for k, v in packet.items() if k != "packet_digest"}})).hexdigest()
248:     if _sha(packet["packet_digest"]) != expected_packet:
249:         raise Rejected()
250:     value = _math(packet["math_input"], lim)
251:     math_hash = hashlib.sha256(_encoded({"schema": "dsat-math-input/1", "input": value})).hexdigest()
252:     names, O_ids, ready = _bindings(packet["bindings"], value, lim)
253:     ds = packet["digests"]
254:     _keys(ds, ["math_input_digest"] + list(names.values()))
255:     if _sha(ds["math_input_digest"]) != math_hash:
256:         raise Rejected()
257:     if expected_math is not None and _sha(expected_math) != math_hash:
258:         raise Rejected()
259:     for component, field in names.items():
260:         if _sha(ds[field]) != _hash(component, packet["bindings"][component]):
261:             raise Rejected()
262:     if expected_scope is not None and _sha(expected_scope) != ds["scope_digest"]:
263:         raise Rejected()
264:     if expected_digests is not None:
265:         if type(expected_digests) is not dict or not set(expected_digests) <= set(ds):
266:             raise Rejected()
267:         for field, pinned in expected_digests.items():
268:             if _sha(pinned) != ds[field]:
269:                 raise Rejected()
270:     proof, claims = packet["proof"], packet["claims"]
271:     if type(proof) is not dict or type(claims) is not dict:
272:         raise Rejected()
273:     if (claims.get("native_admission") != "SOURCE_OR_REFINEMENT_GAP"
274:             or claims.get("global_complete") is not False):
275:         raise Rejected()
```

```text
315:     closed = bool(expected["H_T"] == 0 and ready)
316:     if _bool(claims["conditional_material_closed"]) != closed:
317:         raise Rejected()
318:     return {"status": "VALID_MATH_OPTIMUM", "mathematics_accepted": True, "F_nonempty": True,
319:             **expected, "conditional_material_closed": closed,
320:             "native_admission": "SOURCE_OR_REFINEMENT_GAP", "global_complete": False,
321:             "remaining_obligations": sorted(remaining), "math_input_digest": math_hash,
322:             "residual_arcs_checked": residual_m + residual_d, "solver_called": False,
323:             "source_authentication_performed": False}
```
