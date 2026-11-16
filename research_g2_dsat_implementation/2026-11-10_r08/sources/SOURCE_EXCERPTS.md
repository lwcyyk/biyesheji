# R08 source excerpts

Read/extract/AST only, not imported or executed. Prior full same-conversation reading retained.


## C01: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\storage.py
SHA256 `2d17cf95d7d724d8debbeb47c2df28cfd537aa696bde47edb98908170a12de83`

```text
1: """SQLite authority. All approval mutations share one BEGIN IMMEDIATE order.
2: 
3: The small prototype stores one encrypted application snapshot per commit. Its
4: linear serialization cost is explicit; the SQL transaction and event are atomic.
5: """
6: 
7: import json
8: import os
9: from pathlib import Path
10: import secrets
11: import sqlite3
12: import threading
13: 
14: from cryptography.hazmat.primitives.ciphers.aead import AESGCM
15: 
16: from .protocol import (EventLog, InvalidInput, canonical, digest, exact_fields,
17:                        identifier, normalized_request, write_json)
18: from .materials import validate_material
19: 
20: 
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
44: 
45: 
46: class AuthorityStore:
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
160: 
161:     def grant(self, state, payload, version):
162:         fields = ("approval_op", "caller", "task", "account", "audience",
163:                   "generation", "operations", "budget", "material")
164:         exact_fields(payload, fields)
165:         for key in fields:
166:             if key not in {"operations", "budget", "material"}:
167:                 identifier(payload[key])
168:         if (type(payload["budget"]) is not int or not 0 <= payload["budget"] <= 1000000
169:                 or not isinstance(payload["operations"], list) or not payload["operations"]
170:                 or len(payload["operations"]) != len(set(payload["operations"]))):
171:             raise InvalidInput("INVALID_APPROVAL")
172:         for operation in payload["operations"]:
173:             identifier(operation)
174:         validate_material(payload["material"], payload["account"], payload["audience"])
175:         if state.get("reconciliation_windows", {}).get(payload["account"], {}).get("active"):
176:             return {"status": "REJECTED", "reason": "RECONCILIATION_CREATION_PAUSED"}
177:         fingerprint = digest(payload)
178:         old = state["grant_ops"].get(payload["approval_op"])
179:         if old:
180:             if old["digest"] != fingerprint:
181:                 return {"status": "CONFLICT", "reason": "APPROVAL_OPERATION_CONFLICT"}
182:             grant = state["grants"][old["grant_id"]]
183:             return {"status": "GRANTED", "grant_id": grant["grant_id"], "handle": grant["handle"]}
184:         for grant in state["grants"].values():
185:             scope = ("caller", "task", "account", "audience", "generation")
186:             if all(grant[key] == payload[key] for key in scope):
187:                 return {"status": "CONFLICT", "reason": "GENERATION_ALREADY_EXISTS"}
188:         grant_id = "grant_" + secrets.token_hex(12)
189:         handle = "handle_" + secrets.token_hex(24)
190:         state["grants"][grant_id] = {
191:             **{key: payload[key] for key in ("caller", "task", "account", "audience", "generation", "operations", "material")},
192:             "grant_id": grant_id, "handle": handle, "active": True,
193:             "limit": payload["budget"], "reserved": 0, "spent": 0}
194:         state["grant_ops"][payload["approval_op"]] = {"digest": fingerprint, "grant_id": grant_id}
195:         return {"status": "GRANTED", "grant_id": grant_id, "handle": handle}
196: 
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
226: 
227:     def release(self, state, payload, version):
228:         exact_fields(payload, ("caller", "rid", "digest"))
229:         req = state["requests"].get(payload["rid"])
230:         if req is None or req["origin"]["caller"] != payload["caller"] or req["digest"] != payload["digest"]:
231:             return {"status": "REJECTED", "reason": "REQUEST_BINDING_MISMATCH", "send": False}
232:         grant = state["grants"][req["origin"]["grant_id"]]
233:         if req["phase"] != "QUEUED":
234:             return {"status": "RECORDED", "send": False, **request_projection(req)}
235:         if not grant["active"]:
236:             req["phase"] = "CANCELLED"
237:             grant["reserved"] -= 1
238:             return {"status": "REJECTED", "reason": "APPROVAL_REVOKED", "send": False}
239:         material = grant["material"]
240:         if req["request"]["operation"] in {"issue", "refresh"} and state.get("reconciliation_windows", {}).get(req["origin"]["account"], {}).get("active"):
241:             req["phase"] = "CANCELLED"
242:             grant["reserved"] -= 1
243:             return {"status": "REJECTED", "reason": "RECONCILIATION_CREATION_PAUSED", "send": False}
244:         if req["request"]["operation"] in {"refresh", "userinfo"}:
245:             source = state["requests"].get(req["request"]["payload"]["source_rid"])
246:             if (source is None or source["origin"] != req["origin"]
247:                     or source["phase"] != "RESULT_AVAILABLE" or not isinstance(source["result_material"], dict)):
248:                 req["phase"] = "CANCELLED"
249:                 grant["reserved"] -= 1
250:                 return {"status": "REJECTED", "reason": "SOURCE_MATERIAL_UNAVAILABLE", "send": False}
251:             material = source["result_material"]
252:         req["attempt_id"] = "attempt_" + secrets.token_hex(16)
253:         req["release_version"] = version
254:         req["phase"] = "DISPATCHED_UNKNOWN"
255:         grant["reserved"] -= 1
256:         grant["spent"] += 1
257:         return {"status": "RELEASED", "send": True, **request_projection(req),
258:                 "operation": req["request"]["operation"], "payload": req["request"]["payload"],
259:                 "material": material}
260: 
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
283: 
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
309: 
310:     def prepare_disposal(self, state, payload, version):
311:         exact_fields(payload, ("disposal_op", "rid"))
312:         identifier(payload["disposal_op"])
313:         identifier(payload["rid"])
314:         disposals = state.setdefault("disposals", {})
315:         existing = disposals.get(payload["disposal_op"])
316:         if existing:
317:             if existing["rid"] != payload["rid"]:
318:                 return {"status": "CONFLICT", "reason": "DISPOSAL_ID_CONFLICT"}
319:             return {"status": existing["phase"], "send": False}
320:         req = state["requests"].get(payload["rid"])
321:         if (req is None or req["phase"] != "QUARANTINED"
322:                 or not isinstance(req["result_material"], dict)):
323:             return {"status": "UNKNOWN", "reason": "NO_KNOWN_QUARANTINED_MATERIAL", "send": False}
324:         disposals[payload["disposal_op"]] = {"rid": req["rid"], "phase": "DISPOSAL_UNKNOWN",
325:                                              "origin": req["origin"], "release_version": version}
326:         return {"status": "DISPOSAL_RELEASED", "send": True, "material": req["result_material"],
327:                 "rid": req["rid"], "disposal_op": payload["disposal_op"], "origin": req["origin"]}
328: 
329:     def record_disposal(self, state, payload, version):
330:         exact_fields(payload, ("disposal_op", "rid", "http", "userinfo_http", "userinfo_accepted", "introspection_active"))
331:         item = state.get("disposals", {}).get(payload["disposal_op"])
332:         if item is None or item["rid"] != payload["rid"]:
333:             return {"status": "CONFLICT", "reason": "DISPOSAL_SOURCE_CONFLICT"}
334:         if type(payload["http"]) is not int:
335:             raise InvalidInput("INVALID_HTTP_STATUS")
336:         item["phase"] = "NATIVE_REVOKE_RESPONDED"
337:         item["http"] = payload["http"]
338:         item["observations"] = {key: payload[key] for key in ("userinfo_http", "userinfo_accepted", "introspection_active")}
339:         item["completed_version"] = version
340:         if payload["http"] == 200 and payload["userinfo_accepted"] is False and payload["introspection_active"] is False:
341:             item["phase"] = "KNOWN_UNIT_INACTIVE"
342:             state["requests"][item["rid"]]["phase"] = "DISPOSED"
343:         return {"status": item["phase"], "rid": item["rid"], "http": item["http"],
344:                 "scope": "named_native_material_response_only"}
345: 
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


## C02: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\services.py
SHA256 `d8ea05120fc8559a95050e4c71a094eefb73e29d22e1de66494d8c8e1975993a`

```text
22: class SingleActive:
23:     """OS-held lock outside the rollback cache. A process exit releases it."""
24:     def __init__(self, path):
25:         self.stream = open(path, "a+b")
26:         try:
27:             if os.fstat(self.stream.fileno()).st_size == 0:
28:                 self.stream.write(b"0")
29:                 self.stream.flush()
30:             self.stream.seek(0)
31:             if os.name == "nt":
32:                 import msvcrt
33:                 msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
34:             else:
35:                 import fcntl
36:                 fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
37:         except OSError:
38:             self.stream.close()
39:             raise
40: 
41: 
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

```text
277: def serve(role, root, fault=None):
278:     root = Path(root)
279:     config = json.loads((root / "secure" / (role + ".json")).read_text())
280:     log = EventLog(root / role / "transport.jsonl")
281:     if role == "authority":
282:         implementation = AuthorityStore(root / "authority", root / "secure" / "authority.key",
283:                                         config.get("operation_limit"))
284:     elif role == "provider":
285:         if config.get("native_profile"):
286:             from .native_provider import CasdoorProvider
287:             implementation = CasdoorProvider(root, config)
288:         else:
289:             implementation = FakeProvider(root, config)
290:     else:
291:         implementation = Controller(root, config, fault)
292: 
293:     class Handler(BaseHTTPRequestHandler):
294:         def log_message(self, *args):
295:             pass
296: 
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
325:             response = canonical(result)
326:             # The operation logged is selected from the configured whitelist.
327:             log.emit("request", operation=operation if operation in allowed else "denied",
328:                      identity=identity, request_json_bytes=request_bytes,
329:                      response_json_bytes=len(response), status=result.get("status"),
330:                      elapsed_ns=time.monotonic_ns() - started)
331:             try:
332:                 self.send_response(200)
333:                 self.send_header("Content-Type", "application/json")
334:                 self.send_header("Content-Length", str(len(response)))
335:                 self.end_headers()
336:                 self.wfile.write(response)
337:             except (OSError, ssl.SSLError):
338:                 pass
339: 
340:     server = ThreadingHTTPServer(("127.0.0.1", config["port"]), Handler)
341:     server.daemon_threads = True
342:     tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
343:     tls.minimum_version = ssl.TLSVersion.TLSv1_2
344:     tls.load_cert_chain(config["certificate"], config["tls_key"])
345:     server.socket = tls.wrap_socket(server.socket, server_side=True)
346:     write_json(root / "control" / (role + "_ready.json"),
347:                {"role": role, "pid": os.getpid(), "port": config["port"],
348:                 "boot": getattr(implementation, "boot", None)})
349:     server.serve_forever(poll_interval=0.05)
```


## C03: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\protocol.py
SHA256 `1d74afd2d1c252e371fe0d2b619120e588eab27bb15072e27168b812253fed79`

```text
1: """Strict JSON, pinned loopback TLS, and secret-free event projections."""
2: 
3: import hashlib
4: import json
5: import os
6: from pathlib import Path
7: import re
8: import ssl
9: import threading
10: import time
11: import urllib.error
12: import urllib.request
13: 
14: 
15: class InvalidInput(ValueError):
16:     pass
17: 
18: 
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
99: 
100: 
101: class NoRedirect(urllib.request.HTTPRedirectHandler):
102:     def redirect_request(self, req, fp, code, msg, headers, newurl):
103:         return None
104: 
105: 
106: class Client:
107:     def __init__(self, url, token, certificate, log=None, timeout=3):
108:         if not re.fullmatch(r"https://127\.0\.0\.1:[0-9]+", url):
109:             raise InvalidInput("LOOPBACK_TLS_REQUIRED")
110:         port = int(url.rsplit(":", 1)[1])
111:         if port in {18080, 18081, 8080}:
112:             raise InvalidInput("NATIVE_ENDPOINT_FORBIDDEN")
113:         self.url = url
114:         self.token = token
115:         self.log = log
116:         self.timeout = timeout
117:         context = ssl.create_default_context(cafile=str(certificate))
118:         self.opener = urllib.request.build_opener(
119:             urllib.request.ProxyHandler({}), NoRedirect(),
120:             urllib.request.HTTPSHandler(context=context))
121: 
122:     def call(self, operation, payload):
123:         identifier(operation)
124:         body = canonical(payload)
125:         request = urllib.request.Request(
126:             self.url + "/" + operation, data=body,
127:             headers={"Authorization": "Bearer " + self.token,
128:                      "Content-Type": "application/json"}, method="POST")
129:         started = time.monotonic_ns()
130:         try:
131:             with self.opener.open(request, timeout=self.timeout) as response:
132:                 raw = response.read(1024 * 1024)
133:                 result = strict_json(raw)
134:         except (urllib.error.URLError, TimeoutError, OSError):
135:             raw = b""
136:             result = {"status": "UNKNOWN", "reason": "TRANSPORT_UNAVAILABLE"}
137:         except (ValueError, InvalidInput):
138:             raw = b""
139:             result = {"status": "UNKNOWN", "reason": "INVALID_RESPONSE"}
140:         if self.log:
141:             self.log.emit("rpc", operation=operation, request_json_bytes=len(body),
142:                           response_json_bytes=len(raw), status=result.get("status"),
143:                           elapsed_ns=time.monotonic_ns() - started)
144:         return result
```


## C04: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\reconciliation.py
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


## C05: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\evidence_semantics.py
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


## C06: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_provider.py
SHA256 `5db41c26312960a668785f20b0c7988ab31030bebe92773cef46e5187f6df58f`

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


## C07: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\migration.sql
SHA256 `cde954789b246d75b9f699e0e43a0d63ca199ee91470d76a7a1ca31b7d00420f`

```text
1: CREATE TABLE IF NOT EXISTS authority_state (
2:     id INTEGER PRIMARY KEY CHECK (id = 1),
3:     version INTEGER NOT NULL,
4:     ciphertext BLOB NOT NULL
5: );
6: CREATE TABLE IF NOT EXISTS authority_events (
7:     version INTEGER PRIMARY KEY,
8:     operation TEXT NOT NULL,
9:     projection TEXT NOT NULL
10: );
11: PRAGMA user_version = 1;
```


## C08: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\migration_2.sql
SHA256 `7b0c25f990cc101b3b69d3598ed250732f5c975e1dcc30d4980ee0933dd97719`

```text
1: -- Schema 2 accepts typed material bundles. Legacy string values remain readable.
2: -- The encrypted application-row format and AAD remain schema-1 for compatibility.
3: PRAGMA user_version = 2;
```


## C09: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\dsat_flow.py
SHA256 `03565208c2ee301f8060a8aa4426deb23ce604fe79dcc02317afe343e2d82d60`

```text
246: def make_bindings(bundle, projection):
247:     """Redacted synthetic context only; no evidence payload, handle or token is exported."""
248:     if bundle.get("mode") != "SYNTHETIC_CONTRACT" or projection.get("math_input") is None:
249:         raise InputError()
250:     scope = projection["scope"]
251:     return {
252:         "evidence_bundle": sorted(digest("envelope", e) for e in bundle["history"] + bundle["envelopes"]),
253:         "contract": dict(bundle["contract"]),
254:         "scope": {"target_attempts": list(projection["math_input"]["T"]), "paths": list(scope["paths"]),
255:                   "open_frontiers": list(projection["open_frontiers"]),
256:                   "coverage_complete": projection["source_scope_preconditions_declared"], "material_scope_only": True},
257:         "dependency": {"authority_version": projection["authority_version"],
258:                        "source_version": bundle["contract"]["source_version"],
259:                        "evidence_version": 1, "now": bundle["authority"]["now"],
260:                        "valid_until": bundle["authority"]["now"]},
261:         "cost_ledger": list(projection["costs_retained"]),
262:         "O_before": list(projection["obligations_proposed"]),
263:     }
264: 
265: 
266: _BINDINGS = {"evidence_bundle": "evidence_bundle_digest", "contract": "contract_digest",
267:              "scope": "scope_digest", "dependency": "dependency_digest",
268:              "cost_ledger": "cost_ledger_digest", "O_before": "O_before_digest"}
269: 
270: 
271: def _base_packet(math_input, bindings):
272:     value = normalize_math(math_input)
273:     fields(bindings, _BINDINGS)
274:     # Copy via JSON-equivalent serialization to prevent caller mutation of a bound packet.
275:     import json
276:     bindings = json.loads(canonical(bindings))
277:     return {"schema": "dsat-proof/1", "mode": "SYNTHETIC_CONTRACT", "math_input": value,
278:             "bindings": bindings, "digests": {"math_input_digest": math_digest(value),
279:                 **{field: digest(key, bindings[key]) for key, field in _BINDINGS.items()}}}
280: 
281: 
282: def assemble_optimum_packet(math_input, bindings, m_certificate, d_certificate):
283:     """Serialize supplied vectors; this function neither solves nor verifies them."""
284:     packet = _base_packet(math_input, bindings)
285:     value = packet["math_input"]
286:     total = sum(value["c"][i] for i in value["T"])
287:     m = integer(m_certificate["cost"])
288:     d = integer(d_certificate["cost"])
289:     context = packet["bindings"]
290:     contract, scope, dep = context["contract"], context["scope"], context["dependency"]
291:     source_ready = (scope["coverage_complete"] and bool(scope["paths"]) and not scope["open_frontiers"]
292:                     and all(contract[k] for k in ("source_complete", "capacity_complete", "frontier_complete",
293:                                                   "external_writers_excluded", "derivations_covered"))
294:                     and dep["now"] <= dep["valid_until"] and dep["source_version"] == contract["source_version"])
295:     packet["proof"] = {"kind": "OPTIMUM", "m": m_certificate, "d": d_certificate}
296:     packet["claims"] = {"C_T": total, "m_T": m, "d_T": d, "R_T": total - m, "H_T": total - d,
297:                         "conditional_material_closed": bool(total == d and source_ready),
298:                         "native_admission": "SOURCE_OR_REFINEMENT_GAP", "global_complete": False,
299:                         "remaining_obligations": [o["id"] for o in context["O_before"]]}
300:     packet["packet_digest"] = packet_digest(packet)
301:     return packet
302: 
303: 
304: def assemble_infeasible_packet(math_input, bindings, flow, cut, value):
305:     packet = _base_packet(math_input, bindings)
306:     packet["proof"] = {"kind": "INFEASIBLE", "flow": flow, "cut": cut, "value": value}
307:     packet["claims"] = {"result": "EVIDENCE_CONFLICT", "conditional_material_closed": False,
308:                         "native_admission": "SOURCE_OR_REFINEMENT_GAP", "global_complete": False,
309:                         "remaining_obligations": [o["id"] for o in packet["bindings"]["O_before"]]}
310:     packet["packet_digest"] = packet_digest(packet)
```


## C12: D:\毕业设计\auth-lifecycle\tests\test_online_state.py
SHA256 `f66018c8bbca7e218a6c2cdb0b0aad03956d1fe1cfaa1f37d8019fe1e819f37b`

```text
1: """Development regressions through the authenticated controller entry point."""
2: 
3: from concurrent.futures import ThreadPoolExecutor
4: import json
5: import os
6: from pathlib import Path
7: import secrets
8: import shutil
9: import subprocess
10: import sys
11: import unittest
12: from unittest.mock import patch
13: 
14: from auth_lifecycle.online_state.lab import Laboratory, approval, request_for, protect_directory
15: from auth_lifecycle.online_state.protocol import Client
16: from auth_lifecycle.online_state.storage import AuthorityStore
17: from auth_lifecycle.online_state.services import SingleActive
18: from auth_lifecycle.online_state.acceptance import SCENARIOS, continuation_plan
19: 
20: 
21: class OnlineStateTests(unittest.TestCase):
22:     def setUp(self):
23:         default = Path(__file__).resolve().parents[2] / "mainline_online_state_v1" / "dev_work"
24:         self.parent = Path(os.environ.get("ONLINE_STATE_TEST_ROOT", default))
25:         self.parent.mkdir(parents=True, exist_ok=True)
26:         self.lab = Laboratory(self.parent / (self._testMethodName + "_" + secrets.token_hex(4)))
27:         self.addCleanup(self.lab.close)
28:         self.lab.start_all()
29:         self.user = self.lab.client()
30:         self.a = self.user.call("grant", approval("A", "g0", 3))
31:         self.b = self.user.call("grant", approval("B", "g1", 3))
32:         self.assertEqual(self.a["status"], "GRANTED")
33:         self.assertEqual(self.b["status"], "GRANTED")
34: 
35:     def request_a(self, rid="A1"):
36:         return request_for(self.a["handle"], "A", "g0", rid)
37: 
38:     def request_b(self, rid="B1"):
39:         return request_for(self.b["handle"], "B", "g1", rid)
40: 
41:     def revoke_a(self, operation="revokeA"):
42:         return self.user.call("revoke", {"revoke_op": operation, "grant_id": self.a["grant_id"]})
43: 
44:     def status(self):
45:         result = self.user.call("status", {})
46:         self.assertEqual(result["status"], "RECOVERED")
47:         return result
48: 
49:     def test_normal_entry_and_secret_projection(self):
50:         result = self.lab.client("agentA").call("call", self.request_a())
51:         self.assertEqual(result["status"], "RESULT_AVAILABLE")
52:         public = json.dumps([self.a, self.b, result, self.status()])
53:         self.assertNotIn("synthetic_initial", public)
54:         self.assertNotIn("synthetic_result", public)
55:         self.assertNotIn("synthetic_debug", public)
56:         self.assertEqual(self.revoke_a()["status"], "LOCAL_REVOKE_COMMITTED")
57:         self.assertEqual(self.lab.client("agentA").call("call", self.request_a("A2"))["status"], "REJECTED")
58:         self.assertEqual(self.lab.client("agentB").call("call", self.request_b())["status"], "RESULT_AVAILABLE")
59: 
60:     def test_binding_caller_task_account_audience_generation_operation(self):
61:         request = self.request_a()
62:         self.assertEqual(self.lab.client("agentB").call("call", request)["status"], "REJECTED")
63:         for field in ("task", "account", "audience", "generation", "operation"):
64:             with self.subTest(field=field):
65:                 altered = {**self.request_a(field), field: "wrong"}
66:                 self.assertEqual(self.lab.client("agentA").call("call", altered)["status"], "REJECTED")
67:         extra = {**self.request_a("caller_field"), "caller": "agentB"}
68:         self.assertEqual(self.lab.client("agentA").call("call", extra)["status"], "REJECTED")
69:         config = self.lab.configs["controller"]
70:         denied = Client("https://127.0.0.1:" + str(config["port"]), "wrong", config["certificate"])
71:         self.assertEqual(denied.call("status", {})["status"], "REJECTED")
72:         self.assertEqual(self.lab.client("agentA").call("grant", approval("A", "g2"))["status"], "REJECTED")
73: 
74:     def test_rid_duplicate_and_body_conflict(self):
75:         request = self.request_a()
76:         with ThreadPoolExecutor(max_workers=5) as pool:
77:             results = list(pool.map(lambda _: self.lab.client("agentA").call("call", request), range(5)))
78:         self.assertTrue(any(r.get("phase") == "RESULT_AVAILABLE" for r in results))
79:         conflict = {**request, "payload": {"value": 2}}
80:         self.assertEqual(self.lab.client("agentA").call("call", conflict)["status"], "CONFLICT")
81:         state = self.status()
82:         self.assertEqual(len(state["requests"]), 1)
83:         grant = next(g for g in state["approvals"] if g["task"] == "A")
84:         self.assertEqual((grant["reserved"], grant["spent"]), (0, 1))
85:         truth = (self.lab.root / "provider" / "truth.jsonl").read_text().splitlines()
86:         self.assertEqual(len(truth), 1)
87: 
88:     def test_concurrent_budget(self):
89:         with ThreadPoolExecutor(max_workers=8) as pool:
90:             results = list(pool.map(lambda i: self.lab.client("agentA").call("call", self.request_a("r" + str(i))), range(8)))
91:         self.assertEqual(sum(r["status"] == "RESULT_AVAILABLE" for r in results), 3)
92:         grant = next(g for g in self.status()["approvals"] if g["task"] == "A")
93:         self.assertEqual((grant["reserved"], grant["spent"]), (0, 3))
94: 
95:     def test_admission_revoke_compete_at_queue_boundary(self):
96:         self.lab.restart_controller("after_admit")
97:         pending = self.lab.async_call("agentA", "call", self.request_a())
98:         barrier = self.lab.wait_barrier("after_admit")
99:         ack = self.revoke_a()
100:         self.assertEqual(ack["status"], "LOCAL_REVOKE_COMMITTED")
101:         barrier.with_suffix(".release").touch()
102:         self.assertFalse(pending.result(timeout=5).get("send", False))
103:         state = self.status()
104:         self.assertEqual(state["requests"][0]["phase"], "CANCELLED")
105:         grant = next(g for g in state["approvals"] if g["task"] == "A")
106:         self.assertEqual((grant["reserved"], grant["spent"]), (0, 0))
107: 
108:     def test_release_before_revoke_is_pending_then_quarantined(self):
109:         self.lab.restart_controller("after_release")
110:         pending = self.lab.async_call("agentA", "call", self.request_a())
111:         barrier = self.lab.wait_barrier("after_release")
112:         ack = self.revoke_a()
113:         self.assertEqual(ack["status"], "LOCAL_REVOKE_COMMITTED")
114:         self.assertEqual(self.status()["requests"][0]["phase"], "DISPATCHED_UNKNOWN")
115:         barrier.with_suffix(".release").touch()
116:         result = pending.result(timeout=5)
117:         self.assertEqual(result["status"], "QUARANTINED")
118:         self.assertLess(result["release_version"], ack["commit_version"])
119: 
120:     def test_revocation_ack_loss_and_idempotent_recovery(self):
121:         self.lab.restart_controller("after_revoke_commit")
122:         pending = self.lab.async_call("user", "revoke", {"revoke_op": "lost_ack", "grant_id": self.a["grant_id"]})
123:         self.lab.wait_barrier("after_revoke_commit")
124:         self.lab.restart_controller()
125:         self.assertEqual(pending.result(timeout=5)["status"], "UNKNOWN")
126:         first = self.revoke_a("lost_ack")
127:         second = self.revoke_a("lost_ack")
128:         self.assertEqual(first["commit_version"], second["commit_version"])
129:         self.assertEqual(self.lab.client("agentA").call("call", self.request_a())["status"], "REJECTED")
130: 
131:     def test_release_crash_never_automatically_resends_and_B_recovers(self):
132:         self.lab.restart_controller("after_release")
133:         pending = self.lab.async_call("agentA", "call", self.request_a())
134:         self.lab.wait_barrier("after_release")
135:         self.lab.restart_controller()
136:         pending.result(timeout=5)
137:         self.assertEqual(self.revoke_a()["status"], "LOCAL_REVOKE_COMMITTED")
138:         repeat = self.lab.client("agentA").call("call", self.request_a())
139:         self.assertEqual(repeat["phase"], "DISPATCHED_UNKNOWN")
140:         self.assertFalse((self.lab.root / "provider" / "truth.jsonl").exists())
141:         self.assertEqual(self.lab.client("agentB").call("call", self.request_b())["status"], "RESULT_AVAILABLE")
142:         self.assertIn("A1", self.status()["obligations"])
143: 
144:     def test_effect_crash_late_and_duplicate_result_binding(self):
145:         self.lab.restart_controller("after_effect")
146:         pending = self.lab.async_call("agentA", "call", self.request_a())
147:         self.lab.wait_barrier("after_effect")
148:         self.lab.restart_controller()
149:         pending.result(timeout=5)
150:         self.revoke_a()
151:         first = self.user.call("deliver", {"rid": "A1"})
152:         second = self.user.call("deliver", {"rid": "A1"})
153:         self.assertEqual(first["status"], "QUARANTINED")
154:         self.assertEqual(second["status"], "RESULT_DUPLICATE")
155:         self.assertEqual(first["origin"]["generation"], "g0")
156:         new_grant = self.user.call("grant", approval("A", "g2"))
157:         self.assertNotEqual(new_grant["grant_id"], self.a["grant_id"])
158:         self.assertEqual(self.user.call("deliver", {"rid": "A1"})["origin"]["generation"], "g0")
159: 
160:     def test_old_cache_restore_authority_outage_and_key_unavailability(self):
161:         snapshot = self.lab.snapshot_cache()
162:         self.revoke_a()
163:         self.lab.stop("controller")
164:         self.lab.restore_cache(snapshot)
165:         self.lab.stop("authority")
166:         self.lab.start("controller")
167:         self.assertEqual(self.user.call("recover", {})["status"], "UNKNOWN")
168:         self.assertEqual(self.lab.client("agentB").call("call", self.request_b())["status"], "UNKNOWN")
169:         self.lab.start("authority")
170:         self.assertEqual(self.user.call("recover", {})["status"], "RECOVERED")
171:         self.assertEqual(self.lab.client("agentA").call("call", self.request_a())["status"], "REJECTED")
172:         key = self.lab.root / "secure" / "authority.key"
173:         saved = key.with_suffix(".saved")
174:         key.rename(saved)
175:         try:
176:             self.assertEqual(self.user.call("recover", {})["status"], "UNKNOWN")
177:         finally:
178:             saved.rename(key)
179:         self.assertEqual(self.user.call("recover", {})["status"], "RECOVERED")
180:         self.assertEqual(self.lab.client("agentB").call("call", self.request_b())["status"], "RESULT_AVAILABLE")
181: 
182:     def test_conflicting_provider_result_and_transaction_rollback(self):
183:         self.lab.client("fixture", "provider").call("hold", {"enabled": True})
184:         self.lab.client("agentA").call("call", self.request_a())
185:         req = self.status()["requests"][0]
186:         envelope = {key: req[key] for key in ("rid", "digest", "origin", "attempt_id", "release_version")}
187:         envelope.update(material="synthetic_bad", outcome="OK")
188:         envelope["origin"] = {**envelope["origin"], "generation": "g1"}
189:         config = self.lab.configs["authority"]
190:         authority = Client("https://127.0.0.1:" + str(config["port"]), config["identities"]["controller"], config["certificate"])
191:         self.assertEqual(authority.call("record", envelope)["status"], "CONFLICT")
192:         self.assertEqual(self.user.call("deliver", {"rid": "A1"})["status"], "RESULT_AVAILABLE")
193:         unit = self.lab.root / "transaction_regression"
194:         store = AuthorityStore(unit, self.lab.root / "secure" / "authority.key")
195:         original = store.execute
196:         def fail_before_event(statement, parameters=()):
197:             if statement.startswith("INSERT INTO authority_events"):
198:                 raise RuntimeError("synthetic secret must stay out of errors")
199:             return original(statement, parameters)
200:         store.execute = fail_before_event
201:         self.assertEqual(store.call("grant", approval("A", "g0"))["status"], "UNKNOWN")
202:         store.execute = original
203:         self.assertEqual(store.call("recover", {})["approvals"], [])
204:         store.connection.close()
205: 
206:     def test_single_active_lock_is_held_by_running_controller(self):
207:         with self.assertRaises(OSError):
208:             SingleActive(self.lab.root / "secure" / "controller.lock")
209: 
210:     @unittest.skipUnless(os.name == "nt", "Windows SID encoding regression")
```


## C13: D:\毕业设计\auth-lifecycle\tests\test_reconciliation.py
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

```text
88: class WindowTests(unittest.TestCase):
89:     def test_window_pauses_B_creating_but_allows_B_resource_admission(self):
90:         parent = Path(os.environ.get("RECONCILIATION_TEST_ROOT", Path(__file__).resolve().parents[2] / "mainline_native_reconciliation_v1/dev_work"))
91:         root = parent / secrets.token_hex(8);root.mkdir(parents=True)
92:         key = root / "key";key.write_bytes(os.urandom(32))
93:         store = AuthorityStore(root / "authority", key);self.addCleanup(store.connection.close)
94:         grants = {}
95:         for task, generation in [("A", "g0"), ("B", "g1")]:
96:             grants[task] = store.call("grant", {"approval_op": task, "caller": "agent" + task, "task": task,
97:                 "account": "account1", "audience": "l1-client-0", "generation": generation,
98:                 "operations": ["issue", "refresh", "userinfo"], "budget": 4, "material": "synthetic_legacy"})
99:         version, state = store.read_state()
100:         origin = {k: state["grants"][grants["A"]["grant_id"]][k] for k in ("grant_id", "caller", "task", "account", "audience", "generation")}
101:         state["requests"]["A1"] = {"rid": "A1", "digest": "d", "origin": origin,
102:             "request": {"operation": "refresh"}, "phase": "DISPATCHED_UNKNOWN", "attempt_id": "attempt1",
103:             "release_version": 2, "result_digest": None, "result_material": None}
104:         store.execute("UPDATE authority_state SET ciphertext=? WHERE id=1", (store.encrypt(state),))
105:         store.call("revoke", {"revoke_op": "r", "grant_id": origin["grant_id"]})
106:         self.assertEqual(store.call("begin_reconciliation", {"rid": "A1", "window_id": "w"})["status"], "WINDOW_OPEN")
107:         base = {"handle": grants["B"]["handle"], "task": "B", "account": "account1", "audience": "l1-client-0", "generation": "g1"}
108:         blocked = store.call("admit", {"caller": "agentB", "request": {**base, "rid": "B_create", "operation": "issue", "payload": {}}})
109:         allowed = store.call("admit", {"caller": "agentB", "request": {**base, "rid": "B_read", "operation": "userinfo", "payload": {"source_rid": "B0"}}})
110:         self.assertEqual(blocked["status"], "REJECTED")
111:         self.assertEqual(allowed["status"], "ADMITTED")
112:         self.assertIn("A1", store.call("recover", {})["obligations"])
113: 
114:     def test_complete_controller_reconciliation_with_synthetic_native_responses(self):
115:         import test_native_casdoor as native_fixtures
116:         fixture = native_fixtures.NativeAdapterTests()
117:         fixture.setUp()
118:         root = fixture.root
119:         fixture.profile.update(identifier_journal=True, durable_inbox=False)
120:         from auth_lifecycle.online_state.protocol import write_json
121:         write_json(root / "secure/native_profile.json", fixture.profile)
122:         authority = AuthorityStore(root / "authority", root / "secure/authority.key")
123:         self.addCleanup(authority.connection.close)
124:         gateway = CasdoorProvider(root, {"native_profile": str(root / "secure/native_profile.json")})
125:         ledger = NativeHTTP(root, "method", enabled=True)
126:         records = {}
127:         def synthetic_native(operation, **kwargs):
128:             seq = ledger.reserve(operation, fixture.name, kwargs.get("context"))
129:             if operation in {"issue", "refresh"}:
130:                 body = {**fixture.body, "access_token": fixture.jwt(), "refresh_token": fixture.jwt(False)}
131:                 claims = json.loads(native_fixtures.base64.urlsafe_b64decode(body["access_token"].split('.')[1]+'=='))
132:                 # Synthetic JWT fixture uses a bare jti; point lookup still binds it.
133:                 records[claims["jti"]] = {"body": body, "active": True}
134:                 return {"http":200,"body":body,"error_type":None,"sequence":seq}
135:             if operation == "get_token":
136:                 unit = kwargs["payload"]["id"];item=records[unit];body=item["body"]
137:                 row={"owner":"", "name":unit, "organization":"l1-study", "user":fixture.name,"application":"app-l1-0"}
138:                 # The actual gateway requires owner/name equality. Use the same
139:                 # admin/name mapping as the native signed identifier.
140:                 owner,name=unit.split('/',1);row.update(owner=owner,name=name)
141:                 row.update(accessToken=body["access_token"],refreshToken=body["refresh_token"],idToken=body.get("id_token"),
142:                            tokenType=body["token_type"],scope=body["scope"],expiresIn=body["expires_in"])
143:                 return {"http":200,"body":{"data":row},"error_type":None,"sequence":seq}
144:             token = kwargs.get("form",{}).get("token")
145:             if operation == "revoke":
146:                 for item in records.values():
147:                     if item["body"]["refresh_token"]==token:item["active"]=False
148:                 return {"http":200,"body":{},"error_type":None,"sequence":seq}
149:             if operation == "userinfo":
150:                 access=kwargs["headers"]["Authorization"].removeprefix('Bearer ')
151:                 active=any(x["body"]["access_token"]==access and x["active"] for x in records.values())
152:                 return {"http":200 if active else 401,"body":{"sub":"synthetic_account"} if active else {},"error_type":None,"sequence":seq}
153:             active=any(x["body"]["access_token"]==token and x["active"] for x in records.values())
154:             return {"http":200,"body":{"active":active},"error_type":None,"sequence":seq}
155:         # Make fixture jti reflect the native owner's exact key format.
156:         original_jwt=fixture.jwt
157:         def native_jwt(*args,**kwargs):
158:             token=original_jwt(*args,**kwargs)
159:             head,body,_=token.split('.')
160:             claims=json.loads(native_fixtures.base64.urlsafe_b64decode(body+'=='));claims['jti']='admin/'+claims['jti']
161:             text=head+'.'+native_fixtures.b64(canonical(claims))
162:             return text+'.'+native_fixtures.b64(fixture.signing_key.sign(text.encode(),native_fixtures.padding.PKCS1v15(),native_fixtures.hashes.SHA256()))
163:         fixture.jwt=native_jwt
164:         gateway.http=Mock();gateway.http.call.side_effect=synthetic_native
165:         class AuthorityAdapter:
166:             drop=True
167:             def call(self,operation,payload):
168:                 if operation=='record' and payload['rid']=='A1' and self.drop:
169:                     self.drop=False;return {'status':'UNKNOWN'}
170:                 return authority.call(operation,payload)
171:         controller=Controller(root,json.loads((root/'secure/controller.json').read_text()))
172:         self.addCleanup(controller.active_lock.stream.close)
173:         controller.authority=AuthorityAdapter()
174:         controller.provider=Mock();controller.provider.call.side_effect=lambda op,data:gateway.call(op,data,'adapter')
175:         controller.ready=True
176:         controller.config['reconciliation_model']={'per_send_effect_bound':1,'single_open_no_retry':True,'external_writers_excluded':True,'source_lemma_ref':'synthetic-bound','source_files':[]}
177:         grants={}
178:         def request(task,rid,operation,source=None):
179:             return {'rid':rid,'handle':grants[task]['handle'],'task':task,'account':'synthetic_account','audience':'l1-client-0',
180:                     'generation':'g0' if task=='A' else 'g1','operation':operation,'payload':{} if operation=='issue' else {'source_rid':source}}
181:         for task in ['A','B']:
182:             login={'schema':2,'kind':'casdoor_login','issuer':fixture.profile['base'],'client':'l1-client-0','expected_account':'synthetic_account','username':fixture.name,'password':'synthetic_password'}
183:             grants[task]=controller.call('grant',{'approval_op':task,'caller':'agent'+task,'task':task,'account':'synthetic_account','audience':'l1-client-0','generation':'g0' if task=='A' else 'g1','operations':['issue','refresh','userinfo'],'budget':5,'material':login},'user')
184:             self.assertEqual(controller.call('call',request(task,task+'0','issue'),'agent'+task)['status'],'RESULT_AVAILABLE')
185:         self.assertEqual(controller.call('call',request('A','A1','refresh','A0'),'agentA')['status'],'UNKNOWN')
186:         controller.call('revoke',{'revoke_op':'withdraw','grant_id':grants['A']['grant_id']},'user')
187:         controller.call('begin_reconciliation',{'rid':'A1','window_id':'w'},'user')
188:         found=controller.call('reconcile',{'rid':'A1','window_id':'w','step':'discover','B_rid':''},'user')
189:         self.assertEqual(found['status'],'UNKNOWN')
190:         self.assertEqual(found['receipt']['remaining_creation_bound'],0)
191:         self.assertEqual(controller.call('call',request('B','B_after','userinfo','B0'),'agentB')['status'],'RESULT_AVAILABLE')
192:         closed=controller.call('reconcile',{'rid':'A1','window_id':'w','step':'finish','B_rid':'B_after'},'user')
193:         self.assertEqual(closed['status'],'CLOSED')
194:         self.assertEqual(CHECKER.check(closed['receipt'])['status'],'VALID_CONDITIONAL_CLOSED')
195:         self.assertEqual(authority.call('recover',{})['obligations'],[])
```


## C14: D:\毕业设计\auth-lifecycle\scripts\score_agent_isolation.py
SHA256 `4590c9256f49bae3d45376261d9c840e3a46d9ab05ec3fa26a8677054d099404`

```text
170:         if isinstance(value, dict):
171:             if "reached" in value and "result" in value: yield value["result"]
172:             for child in value.values(): yield from responses(child)
173:         elif isinstance(value, list):
174:             for child in value: yield from responses(child)
175:     allowed = {"status", "reason", "version", "rid", "digest", "origin", "phase", "attempt_id", "release_version",
176:                "approvals", "requests", "obligations", "disposals"}
177:     check("agent_response_top_level_whitelist", all(set(r) <= allowed for r in responses(scene)))
178:     failures = [c for c in checks if not c["pass"]]
179:     status = "FAIL_SECURITY" if any(c["security"] for c in failures) else "INCONCLUSIVE" if failures else "PASS"
180:     return {"scenario": scene["scenario"], "status": status, "checks": checks, "leaks": leaks,
181:             "scorer_access_log": accesses, "authority_version": version, "effects": len(effects)}
```
