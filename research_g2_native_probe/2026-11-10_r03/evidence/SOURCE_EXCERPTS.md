# G2-R03 selected source excerpts

Extracted source text, not executed. Original files remain unchanged.


## C01: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\storage.py
SHA-256: `2d17cf95d7d724d8debbeb47c2df28cfd537aa696bde47edb98908170a12de83`


### Lines 24–40
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
```


### Lines 161–259
```text
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
```


### Lines 264–395
```text
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
```


## C02: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\services.py
SHA-256: `d8ea05120fc8559a95050e4c71a094eefb73e29d22e1de66494d8c8e1975993a`


### Lines 80–217
```text
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


### Lines 297–312
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
```


## C03: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_provider.py
SHA-256: `5db41c26312960a668785f20b0c7988ab31030bebe92773cef46e5187f6df58f`


### Lines 1–224
```text
1: """Explicit Casdoor gateway, with an optional durable operational result inbox."""
2: 
3: import base64
4: import json
5: import os
6: from pathlib import Path
7: import threading
8: import time
9: import sqlite3
10: 
11: from cryptography.hazmat.primitives.ciphers.aead import AESGCM
12: 
13: from .materials import decode64, token_bundle, validate_material, verified_claims
14: from .native_http import NativeHTTP
15: from .protocol import EventLog, InvalidInput, canonical, digest, exact_fields, write_json
16: from .enumeration import analyze, ScopeViolation
17: 
18: 
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
53:         if operation == "dispose":
54:             material = validate_material(payload["material"], self.profile["actor"]["id"], self.profile["client_id"])
55:             access = material["native"]["access_token"]
56:             verified_claims(access, self.profile)
57:             header = json.loads(decode64(access.split(".")[0]))
58:             verified_claims(material["native"]["refresh_token"], self.profile, header.get("kid"))
59:             answer = self.http.call("revoke", actor=self.profile["actor"]["name"], form={
60:                 "client_id": self.profile["client_id"], "client_secret": self.profile["client_secret"],
61:                 "token": material["native"]["refresh_token"], "token_type_hint": "refresh_token"})
62:             if not answer["http"]:
63:                 return {"status": "UNKNOWN"}
64:             resource = self.http.call("userinfo", actor=self.profile["actor"]["name"],
65:                                       headers={"Authorization": "Bearer " + material["native"]["access_token"]})
66:             active = self.http.call("introspect", actor=self.profile["actor"]["name"], form={
67:                 "client_id": self.profile["client_id"], "client_secret": self.profile["client_secret"],
68:                 "token": material["native"]["access_token"], "token_type_hint": "access_token"})
69:             value = active["body"].get("active") if active["http"] == 200 else None
70:             return {"status": "DISPOSAL_RESPONSE", "http": answer["http"],
71:                     "userinfo_http": resource["http"],
72:                     "userinfo_accepted": (resource["http"] == 200 and resource["body"].get("sub") == self.profile["actor"]["id"])
73:                        if resource["http"] in {200, 400, 401, 403} else None,
74:                     "introspection_active": value if type(value) is bool else None}
75:         if operation != "perform":
76:             return {"status": "REJECTED", "reason": "UNSUPPORTED_NATIVE_OPERATION"}
77:         material = validate_material(payload["material"], self.profile["actor"]["id"], self.profile["client_id"])
78:         if material["kind"] == "casdoor_oauth":
79:             access = material["native"]["access_token"]
80:             verified_claims(access, self.profile)
81:             header = json.loads(decode64(access.split(".")[0]))
82:             verified_claims(material["native"]["refresh_token"], self.profile, header.get("kid"))
83:         if payload["origin"]["account"] != self.profile["actor"]["id"] or payload["origin"]["audience"] != self.profile["client_id"]:
84:             raise InvalidInput("NATIVE_ORIGIN_MISMATCH")
85:         kind = payload["operation"]
86:         context = {key: payload[key] for key in ("rid", "digest", "attempt_id")}
87:         if kind == "refresh" and self.profile.get("hold_before_native_refresh"):
88:             path = self.root / "provider" / "before_native_refresh.json"
89:             write_json(path, {**context, "position": "before NativeHTTP reservation and send"})
90:             while not path.with_suffix(".release").exists():
91:                 time.sleep(0.01)
92:         common = {"client_id": self.profile["client_id"], "client_secret": self.profile["client_secret"]}
93:         if kind == "issue" and material["kind"] == "casdoor_login":
94:             answer = self.http.call("issue", actor=self.profile["actor"]["name"], form={**common,
95:                 "grant_type": "password", "username": material["username"], "password": material["password"], "scope": "openid"}, context=context)
96:         elif kind == "refresh" and material["kind"] == "casdoor_oauth":
97:             answer = self.http.call("refresh", actor=self.profile["actor"]["name"], form={**common,
98:                 "grant_type": "refresh_token", "refresh_token": material["native"]["refresh_token"], "scope": "openid"}, context=context)
99:         elif kind == "userinfo" and material["kind"] == "casdoor_oauth":
100:             answer = self.http.call("userinfo", actor=self.profile["actor"]["name"],
101:                                     headers={"Authorization": "Bearer " + material["native"]["access_token"]}, context=context)
102:         else:
103:             raise InvalidInput("NATIVE_OPERATION_MATERIAL_MISMATCH")
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
150: 
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
191: 
192:     def reconcile_enumeration(self, payload):
193:         exact_fields(payload, ("rid", "digest", "origin", "attempt_id", "release_version", "enumeration_context"))
194:         known = payload["enumeration_context"]
195:         with sqlite3.connect("file:" + str(self.budget_path) + "?mode=ro", uri=True) as con:
196:             sends = con.execute("SELECT COUNT(*) FROM requests WHERE category='method' AND operation='refresh' AND attempt_id=? AND rid=? AND request_digest=? AND actor=?",
197:                 (payload["attempt_id"], payload["rid"], payload["digest"], self.profile["actor"]["name"])).fetchone()[0]
198:         basic = base64.b64encode((self.profile["client_id"] + ":" + self.profile["client_secret"]).encode()).decode()
199:         context = {key: payload[key] for key in ("rid", "digest", "attempt_id")}
200:         answer = self.http.call("get_tokens", actor=self.profile["actor"]["name"],
201:                                 headers={"Authorization": "Basic " + basic}, context=context)
202:         rows = answer["body"].get("data") if answer["http"] == 200 else None
203:         if not isinstance(rows, list) or answer["error_type"]:
204:             return {"status": "UNKNOWN", "reason": "AUTHORIZED_ENUMERATION_UNAVAILABLE", "evidence": {"actual_sends": sends}}
205:         try:
206:             evidence = analyze(rows, self.profile["organization"], self.profile["application_name"], self.profile["actor"]["name"],
207:                 self.http.policy["account_names"], known["known_unit_ids"], self.http.policy["page_size"], self.http.policy["record_upper_bound"],
208:                 known["unknown_creators"] == [payload["rid"]], known["account_grant_count"] == 2 and known["account_budget_total"] == 20, sends)
209:         except ScopeViolation:
210:             return {"status": "SAFETY_FAILURE", "reason": "QUERY_SCOPE_ESCAPED"}
211:         evidence.update(query_ref="native-http-" + str(answer["sequence"]), enumeration_ref=digest(rows),
212:             authorized_scope_ref=digest({"organization": self.profile["organization"], "scope": "ALL_TOKEN_RECORDS"}),
213:             input_context=known, input_context_ref=digest(known), query_evidence_schema="native-enumeration-observation/2",
214:             native_reported_count=answer["body"].get("data2"), returned_record_count=len(rows), native_reported_page_count=None)
215:         if not evidence["origin_bound"]:
216:             return {"status": "UNKNOWN", "reason": "COLLECTION_OR_ATTRIBUTION_UNRESOLVED", "evidence": evidence}
217:         selected = next(row for row in rows if row["owner"] + "/" + row["name"] == evidence["selected_unit_id"])
218:         body = {dst: selected.get(src) for dst, src in [("access_token", "accessToken"), ("refresh_token", "refreshToken"),
219:             ("id_token", "idToken"), ("token_type", "tokenType"), ("scope", "scope"), ("expires_in", "expiresIn")]}
220:         material = token_bundle(body, self.profile)
221:         if material["derived"]["verified_claims"]["jti"] != evidence["selected_unit_id"]:
222:             return {"status": "UNKNOWN", "reason": "ENUMERATED_UNIT_CLAIM_CONFLICT", "evidence": evidence}
223:         result = {key: payload[key] for key in ("rid", "digest", "origin", "attempt_id", "release_version")}
224:         return {"status": "RECONCILED_MATERIAL", "evidence": evidence, "result": {**result, "material": material, "outcome": "OK"}}
```


## C04: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_http.py
SHA-256: `7ccfa54e8982559fa1a16b519a3f0ab41ea237449ae45019d7f8140aec022bb4`


### Lines 22–44
```text
22: ROUTES = {
23:     "admin_login": ("POST", "/api/login"),
24:     "application": ("GET", "/api/get-application?id=admin/app-l1-0"),
25:     "discovery": ("GET", "/.well-known/openid-configuration"),
26:     "jwks": ("GET", "/.well-known/jwks"),
27:     "add_user": ("POST", "/api/add-user"),
28:     "get_user": ("GET", "/api/get-user"),
29:     "disable_user": ("POST", "/api/update-user"),
30:     "delete_user": ("POST", "/api/delete-user"),
31:     "issue": ("POST", "/api/login/oauth/access_token"),
32:     "refresh": ("POST", "/api/login/oauth/refresh_token"),
33:     "revoke": ("POST", "/api/login/oauth/revoke"),
34:     "userinfo": ("GET", "/api/userinfo"),
35:     "introspect": ("POST", "/api/login/oauth/introspect"),
36:     "get_token": ("GET", "/api/get-token"),
37:     "get_tokens": ("GET", "/api/get-tokens"),
38:     "owned_organization": ("GET", "/api/get-organization"),
39:     "add_organization": ("POST", "/api/add-organization"),
40:     "delete_organization": ("POST", "/api/delete-organization"),
41:     "owned_application": ("GET", "/api/get-application"),
42:     "add_application": ("POST", "/api/add-application"),
43:     "delete_application": ("POST", "/api/delete-application"),
44: }
```


### Lines 101–232
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
116: 
117:     def call(self, operation, *, actor=None, form=None, payload=None, headers=None, timeout=8, context=None):
118:         if operation not in ROUTES:
119:             raise InvalidInput("UNREGISTERED_NATIVE_OPERATION")
120:         actor_operations = {"add_user", "get_user", "disable_user", "delete_user", "issue", "refresh", "revoke", "userinfo", "introspect", "get_token"}
121:         if operation in actor_operations and actor not in self.policy["account_names"]:
122:             raise InvalidInput("NATIVE_ACCOUNT_OUT_OF_SCOPE")
123:         organization = self.policy.get("organization", "l1-study")
124:         client_id = self.policy.get("client_id", "l1-client-0")
125:         if self.category == "method" and operation not in {"issue", "refresh", "userinfo", "revoke", "introspect", "get_token", "get_tokens"}:
126:             raise InvalidInput("METHOD_INTERFACE_DENIED")
127:         if operation in {"issue", "refresh", "revoke", "introspect"}:
128:             fields = {
129:                 "issue": {"client_id", "client_secret", "grant_type", "username", "password", "scope"},
130:                 "refresh": {"client_id", "client_secret", "grant_type", "refresh_token", "scope"},
131:                 "revoke": {"client_id", "client_secret", "token", "token_type_hint"},
132:                 "introspect": {"client_id", "client_secret", "token", "token_type_hint"}}
133:             if not isinstance(form, dict) or set(form) != fields[operation]:
134:                 raise InvalidInput("NATIVE_FORM_FIELDS_DENIED")
135:             if form.get("client_id") != client_id:
136:                 raise InvalidInput("NATIVE_CLIENT_OUT_OF_SCOPE")
137:         if operation == "issue" and form["grant_type"] != "password":
138:             raise InvalidInput("NATIVE_GRANT_DENIED")
139:         if operation == "refresh" and form["grant_type"] != "refresh_token":
140:             raise InvalidInput("NATIVE_GRANT_DENIED")
141:         if operation == "issue" and form.get("username") != actor:
142:             raise InvalidInput("NATIVE_LOGIN_ACCOUNT_MISMATCH")
143:         if operation in {"add_user", "disable_user", "delete_user"}:
144:             if payload.get("owner") != organization or payload.get("name") != actor:
145:                 raise InvalidInput("NATIVE_MUTATION_ACCOUNT_MISMATCH")
146:         method, path = ROUTES[operation]
147:         object_kinds = {"owned_organization": "organization", "add_organization": "organization", "delete_organization": "organization",
148:                         "owned_application": "application_name", "add_application": "application_name", "delete_application": "application_name"}
149:         if operation in object_kinds:
150:             expected = self.policy.get(object_kinds[operation])
151:             if not self.policy.get("dedicated_scope") or self.category not in {"environment", "cleanup"} or not expected:
152:                 raise InvalidInput("OWNED_OBJECT_SCOPE_REQUIRED")
153:             if operation.startswith("owned_"):
154:                 path += "?" + urllib.parse.urlencode({"id": "admin/" + expected})
155:             elif not payload or payload.get("owner") != "admin" or payload.get("name") != expected:
156:                 raise InvalidInput("OWNED_OBJECT_MISMATCH")
157:             if operation == "add_application" and (payload.get("organization") != organization or payload.get("clientId") != client_id):
158:                 raise InvalidInput("OWNED_APPLICATION_BINDING")
159:             if operation == "delete_application" and payload.get("organization") != organization:
160:                 raise InvalidInput("OWNED_APPLICATION_DELETE_ORGANIZATION_REQUIRED")
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
182:             raise InvalidInput("UNAPPROVED_NATIVE_HEADER")
183:         if form is not None:
184:             data = urllib.parse.urlencode(form).encode()
185:             request_headers["Content-Type"] = "application/x-www-form-urlencoded"
186:         if payload is not None:
187:             data = canonical(payload)
188:             request_headers["Content-Type"] = "application/json"
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


## C05: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\enumeration.py
SHA-256: `cc5d688955e1606a8d3e15d8f6f5845a9da487343089a89cc52fc0c7d228516b`


### Lines 1–34
```text
1: """Authorized-scope snapshot and conservative difference attribution."""
2: 
3: 
4: class ScopeViolation(ValueError):
5:     pass
6: 
7: 
8: def analyze(rows, organization, application, target_user, allowed_users, known_ids,
9:             page_capacity, record_bound, unique_unknown, manifest_ok, actual_sends):
10:     if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
11:         raise ValueError("INVALID_COLLECTION")
12:     if any(row.get("organization") != organization for row in rows):
13:         raise ScopeViolation("UNAUTHORIZED_ORGANIZATION_RETURNED")
14:     projections = [{"unit_id": row.get("owner", "") + "/" + row.get("name", ""),
15:                     "user": row.get("user"), "application": row.get("application"),
16:                     "organization": row.get("organization")} for row in rows]
17:     ids = [row["unit_id"] for row in projections]
18:     universe_ok = all(row["user"] in allowed_users and row["application"] == application for row in projections)
19:     complete = (type(page_capacity) is int and type(record_bound) is int
20:                 and 0 < record_bound <= page_capacity and len(rows) <= record_bound
21:                 and len(ids) == len(set(ids)) and universe_ok and manifest_ok)
22:     target = [row["unit_id"] for row in projections if row["user"] == target_user and row["application"] == application]
23:     candidates = sorted(set(target) - set(known_ids))
24:     bound = complete and unique_unknown and actual_sends == 1 and len(candidates) == 1
25:     return {"evidence_origin": "AUTHORIZED_SCOPE_ENUMERATION", "query_kind": "organization_equal_single_page",
26:             "exact_authorized_read": True, "record_found": len(candidates) == 1, "origin_bound": bound,
27:             "actual_sends": actual_sends, "observed_distinct_effects": 1 if bound else 0,
28:             "organization": organization, "application": application, "target_user": target_user,
29:             "all_returned_rows_authorized": True, "registered_universe_complete": universe_ok,
30:             "collection_complete": complete, "page_capacity": page_capacity, "record_upper_bound": record_bound,
31:             "page_number": 1, "snapshot_scope": "single_find_statement", "organization_equal_filter": True,
32:             "returned_records": projections, "target_unit_ids": sorted(set(target)),
33:             "known_input_ids": sorted(set(known_ids)), "candidate_unit_ids": candidates,
34:             "selected_unit_id": candidates[0] if bound else None}
```


## C06: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\lab.py
SHA-256: `ccf0c4ad6d21106fd1c0ef5aedcdad5b30bba49b2bf2f526ea69d79899409f26`


### Lines 75–98
```text
75:             ports[("authority", "provider", "controller")[len(ports)]] = port
76:     authority_token = secrets.token_urlsafe(32)
77:     provider_token = secrets.token_urlsafe(32)
78:     common = {"certificate": str(cert_path), "tls_key": str(key_path)}
79:     configs = {
80:         "authority": {**common, "port": ports["authority"], "operation_limit": operation_limit,
81:                       "identities": {"controller": authority_token},
82:                       "permissions": {"controller": ["grant", "admit", "release", "record", "revoke", "recover"]}},
83:         "provider": {**common, "port": ports["provider"],
84:                      "identities": {"adapter": provider_token, "fixture": secrets.token_urlsafe(32)},
85:                      "permissions": {"adapter": ["perform", "lookup"], "fixture": ["hold"]}},
86:         "controller": {**common, "port": ports["controller"],
87:                        "authority_url": "https://127.0.0.1:" + str(ports["authority"]),
88:                        "provider_url": "https://127.0.0.1:" + str(ports["provider"]),
89:                        "authority_token": authority_token, "provider_token": provider_token,
90:                        "identities": {name: secrets.token_urlsafe(32) for name in ("user", "agentA", "agentB")},
91:                        "permissions": {"user": ["grant", "revoke", "recover", "deliver", "status"],
92:                                        "agentA": ["call", "status"], "agentB": ["call", "status"]}}
93:     }
94:     for role, config in configs.items():
95:         write_json(secure / (role + ".json"), config)
96:     write_json(root / "control" / "environment.json", {
97:         "contract": "ONLINE_TRUSTED_STATE_V1", "ports": ports, "acl": acl,
98:         "operation_limit": operation_limit, "fault_domain": "controller process and cache/view.json",
```


## C07: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\isolation_acceptance.py
SHA-256: `f161667ada4ddcf51b4bf4315a2134a49c3698199d75308713374b23c9d890fd`


### Lines 111–158
```text
111: class IsolationLab:
112:     def __init__(self, root):
113:         self.root = Path(root).resolve()
114:         self.root.mkdir(parents=True, exist_ok=False)
115:         self.owner = current_sid()
116:         set_acl(self.root, self.owner)
117:         seed = [secrets.randbelow(2**30) + 2**29 for _ in range(3)]
118:         prefix = "S-1-5-21-" + "-".join(map(str, seed))
119:         self.sids = {n: prefix + "-" + str(i) for n, i in [("A", 1001), ("B", 1002), ("R", 1003)]}
120:         self.owned, self.agent_objects, self.started = [], {}, time.monotonic()
121:         self.acls = {}
122:         # Allow traversal to separately ACL-protected children. No generic Users
123:         # or Everyone ACE is placed on any M5 resource.
124:         for name in ("assets", "agents"):
125:             path = self.root / name; path.mkdir()
126:             self.acls[name] = set_acl(path, self.owner, [(s, "GRGX") for s in self.sids.values()])
127:         self.assets = self.root / "assets"
128:         self.python = copy_runtime(self.assets / "python")
129:         self.code = self.assets / "source"
130:         package = Path(__file__).resolve().parents[1]
131:         destination = self.code / "auth_lifecycle" / "online_state"
132:         destination.mkdir(parents=True)
133:         shutil.copy2(package / "__init__.py", destination.parent / "__init__.py")
134:         for name in ("__init__.py", "protocol.py", "storage.py", "materials.py", "services.py", "lab.py",
135:                      "reconciliation.py", "isolation_agent.py", "isolation_service.py", "migration.sql", "migration_2.sql"):
136:             shutil.copy2(Path(__file__).with_name(name), destination / name)
137:         shutil.copy2(Path(__file__).with_name("isolation_agent.py"), self.assets / "isolation_agent.py")
138:         self.lab = Laboratory(self.root / "trusted")
139:         # Replace inherited user-only security on every precreated trusted item.
140:         for p in [self.lab.root, *self.lab.root.rglob("*")]:
141:             set_acl(p, self.owner, [(self.sids["R"], "FA")])
142:         self.scorer = self.root / "scorer_private"; self.scorer.mkdir()
143:         set_acl(self.scorer, self.owner)
144:         self.markers = {name: "M5_" + name + "_" + secrets.token_hex(24) for name in
145:                         ("AT", "RT", "APP_SECRET", "SCORER_PRIVATE", "INBOX")}
146:         (self.scorer / "private.key").write_text(self.markers["SCORER_PRIVATE"])
147:         self.lab.configs["controller"]["identities"]["recovery"] = secrets.token_urlsafe(32)
148:         permissions = self.lab.configs["controller"]["permissions"]
149:         permissions["user"] = ["grant", "revoke", "deliver", "status", "begin_reconciliation", "reconcile", "dispose"]
150:         permissions["recovery"] = ["recover"]
151:         self.lab.configs["provider"]["synthetic_application_secret"] = self.markers["APP_SECRET"]
152:         for role, config in self.lab.configs.items(): write_json(self.lab.root / "secure" / (role + ".json"), config)
153:         (self.lab.root / "secure" / "admin.cap").write_text(self.lab.configs["controller"]["identities"]["user"])
154:         (self.lab.root / "secure" / "approval_config.json").write_text('{"fixture":"M5"}')
155:         # An encrypted synthetic inbox is a file-access target, never an A input.
156:         from cryptography.hazmat.primitives.ciphers.aead import AESGCM
157:         nonce = os.urandom(12)
158:         (self.lab.root / "provider" / "operational_inbox.bin").write_bytes(nonce + AESGCM(
```


## C08: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_isolation.py
SHA-256: `07d6b0197dcf6ada58156deb2108a18d8dfefa53dfee6a43c6916edf8b41428d`


### Lines 1–28
```text
1: """M6 native profile wired to M5 restricted processes. Mature composition only."""
2: from concurrent.futures import ThreadPoolExecutor
3: import base64
4: from collections import Counter
5: import hashlib
6: import json
7: import os
8: from pathlib import Path
9: import secrets
10: import shutil
11: import sqlite3
12: import subprocess
13: import sys
14: import time
15: 
16: from cryptography.hazmat.primitives import hashes, serialization
17: from cryptography.hazmat.primitives.asymmetric import padding, rsa
18: 
19: from .isolation_acceptance import Agent, IsolationLab, source_lock, current_sid
20: from .lab import protect_directory
21: from .native_acceptance import preflight, create_actor, native_request, observe, cleanup_actor, require
22: from .native_http import NativeHTTP, create_budget, private_http_records, budget_path
23: from .protocol import canonical, write_json
24: from .reconciliation_acceptance import source_model
25: from .unidentified_acceptance import setup_scope, cleanup_scope
26: from .windows_isolation import set_acl, inspect_file_acl, inspect_process_acl
27: 
28: 
```


### Lines 64–86
```text
64:     def __init__(self, root, profile, model, fixture=None):
65:         super().__init__(root)
66:         self.profile, self.model = profile, model
67:         self.service_module = "auth_lifecycle.online_state.native_isolation_service"
68:         target = self.code / "auth_lifecycle" / "online_state"
69:         for name in ("native_http.py", "native_provider.py", "enumeration.py", "native_isolation_service.py", "native_isolation_fixture.py"):
70:             shutil.copy2(Path(__file__).with_name(name), target / name)
71:         self.lab.configs["provider"].pop("synthetic_application_secret", None)
72:         self.lab.configs["provider"]["native_profile"] = str(self.lab.root / "secure" / "native_profile.json")
73:         self.lab.configs["provider"]["permissions"]["adapter"] += ["dispose", "reconcile_query"]
74:         self.lab.configs["authority"]["permissions"]["controller"] += ["prepare_disposal", "record_disposal",
75:             "begin_reconciliation", "reconciliation_context", "save_reconciliation"]
76:         self.lab.configs["controller"]["reconciliation_model"] = model
77:         write_json(self.lab.root / "secure" / "native_profile.json", profile)
78:         if fixture:
79:             write_json(self.lab.root / "secure" / "synthetic_fixture.json", fixture)
80:             self.lab.configs["provider"]["synthetic_transport_fixture"] = str(self.lab.root / "secure" / "synthetic_fixture.json")
81:         for role, config in self.lab.configs.items(): write_json(self.lab.root / "secure" / (role + ".json"), config)
82:         (self.scorer/"private.key").unlink(missing_ok=True)
83:         write_json(self.scorer/"expected.json",{"purpose":"M6 scorer-only material evidence; actual values collected from private audit"})
84:         self.transport = Path(profile["batch"])
85:         # Shared budget and ciphertext output are writable. The batch parent and
86:         # scorer key stay outside the R writable directory.
```


## C09: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_isolation_service.py
SHA-256: `b2740390f2fb243378171ed182e64b8b72fa59f4a8fec7dace1a18e344257a34`


### Lines 1–19
```text
1: """M6 service bootstrap, reusing M5 token diagnostics and startup handling."""
2: import json
3: from pathlib import Path
4: import sys
5: 
6: 
7: def main():
8:     args = sys.argv
9:     root = Path(args[args.index("--root") + 1])
10:     role = args[args.index("--role") + 1]
11:     config = json.loads((root / "secure" / (role + ".json")).read_text())
12:     if role == "provider" and config.get("synthetic_transport_fixture"):
13:         from .native_isolation_fixture import install
14:         install(config["synthetic_transport_fixture"])
15:     from .isolation_service import main as serve
16:     serve()
17: 
18: 
19: if __name__ == "__main__": main()
```


## C10: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\materials.py
SHA-256: `5802380a8ff2058662685c8d2eb5963ec2821264f67e2dc97560db5e4fd2f218`


### Lines 14–99
```text
14:     if isinstance(material, str):
15:         if not 1 <= len(material) <= 4096:
16:             raise InvalidInput("INVALID_LEGACY_MATERIAL")
17:         return material
18:     if not isinstance(material, dict) or material.get("schema") != 2:
19:         raise InvalidInput("INVALID_MATERIAL_SCHEMA")
20:     kind = material.get("kind")
21:     if kind == "casdoor_login":
22:         exact_fields(material, ("schema", "kind", "issuer", "client", "expected_account", "username", "password"))
23:         identifier(material["username"])
24:         if not isinstance(material["password"], str) or not material["password"]:
25:             raise InvalidInput("MISSING_LOGIN_SECRET")
26:     elif kind == "casdoor_oauth":
27:         exact_fields(material, ("schema", "kind", "issuer", "client", "expected_account", "native", "derived"))
28:         native = material["native"]
29:         exact_fields(native, ("access_token", "refresh_token", "token_type", "scope", "expires_in", "id_token"))
30:         for field in ("access_token", "refresh_token"):
31:             if not isinstance(native[field], str) or not 1 <= len(native[field]) <= 32768:
32:                 raise InvalidInput("MISSING_TOKEN")
33:         if (not isinstance(native["token_type"], str) or native["token_type"].lower() != "bearer" or type(native["expires_in"]) is not int
34:                 or native["expires_in"] <= 0):
35:             raise InvalidInput("INVALID_TOKEN_METADATA")
36:         claims = material["derived"].get("verified_claims", {})
37:         audience = claims.get("aud", [])
38:         audience = [audience] if isinstance(audience, str) else audience
39:         if claims.get("sub") != material["expected_account"] or material["client"] not in audience:
40:             raise InvalidInput("CLAIM_BINDING_MISMATCH")
41:         if claims.get("iss") != material["issuer"]:
42:             raise InvalidInput("ISSUER_MISMATCH")
43:     else:
44:         raise InvalidInput("INVALID_MATERIAL_KIND")
45:     if material["issuer"] != "http://127.0.0.1:18081":
46:         raise InvalidInput("UNREGISTERED_ISSUER")
47:     identifier(material["client"])
48:     identifier(material["expected_account"])
49:     if account is not None and material["expected_account"] != account:
50:         raise InvalidInput("MATERIAL_ACCOUNT_MISMATCH")
51:     if client is not None and material["client"] != client:
52:         raise InvalidInput("MATERIAL_CLIENT_MISMATCH")
53:     return material
54: 
55: 
56: def decode64(value):
57:     return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
58: 
59: 
60: def verified_claims(token, profile, fallback_kid=None):
61:     try:
62:         head, body, signature = token.split(".")
63:         header = json.loads(decode64(head))
64:         claims = json.loads(decode64(body))
65:         if header.get("alg") != "RS256":
66:             raise ValueError("ALGORITHM")
67:         key_id = header.get("kid") or fallback_kid
68:         key = next(k for k in profile["jwks"]["keys"] if k.get("kid") == key_id and k.get("kty") == "RSA")
69:         public = rsa.RSAPublicNumbers(int.from_bytes(decode64(key["e"]), "big"),
70:                                      int.from_bytes(decode64(key["n"]), "big")).public_key()
71:         public.verify(decode64(signature), (head + "." + body).encode(), padding.PKCS1v15(), hashes.SHA256())
72:         aud = claims.get("aud", [])
73:         aud = [aud] if isinstance(aud, str) else aud
74:         if (claims.get("iss") != profile["base"] or claims.get("sub") != profile["actor"]["id"]
75:                 or profile["client_id"] not in aud or claims.get("exp", 0) <= time.time()
76:                 or claims.get("nbf", 0) > time.time()):
77:             raise ValueError("BINDING")
78:         return claims
79:     except Exception as error:
80:         raise InvalidInput("NATIVE_TOKEN_VERIFICATION_FAILED") from error
81: 
82: 
83: def token_bundle(body, profile):
84:     for name in ("access_token", "refresh_token", "token_type", "expires_in"):
85:         if name not in body:
86:             raise InvalidInput("NATIVE_RESPONSE_MISSING_FIELD")
87:     claims = verified_claims(body["access_token"], profile)
88:     access_header = json.loads(decode64(body["access_token"].split(".")[0]))
89:     refresh_claims = verified_claims(body["refresh_token"], profile, access_header.get("kid"))
90:     material = {"schema": 2, "kind": "casdoor_oauth", "issuer": profile["base"],
91:                 "client": profile["client_id"], "expected_account": profile["actor"]["id"],
92:                 "native": {key: body.get(key) for key in
93:                            ("access_token", "refresh_token", "token_type", "scope", "expires_in", "id_token")},
94:                 "derived": {"verified_claims": claims, "verified_refresh_claims": refresh_claims,
95:                             "access_ref": digest(body["access_token"]),
96:                             "refresh_ref": digest(body["refresh_token"]), "requested_scope": "openid",
97:                             "native_identifier_claim": claims.get("jti"),
98:                             "identifier_status": "JWT_CLAIM_REQUIRES_NATIVE_UNIT_MAPPING"}}
99:     return validate_material(material, profile["actor"]["id"], profile["client_id"])
```


## G01: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\controllers\token.go
SHA-256: `821ecbe055efcba0443e5a24b286fd3c7ceb17af791941194dd9262f438e7306`


### Lines 37–100
```text
37: func (c *ApiController) GetTokens() {
38: 	owner := c.Ctx.Input.Query("owner")
39: 	limit := c.Ctx.Input.Query("pageSize")
40: 	page := c.Ctx.Input.Query("p")
41: 	field := c.Ctx.Input.Query("field")
42: 	value := c.Ctx.Input.Query("value")
43: 	sortField := c.Ctx.Input.Query("sortField")
44: 	sortOrder := c.Ctx.Input.Query("sortOrder")
45: 	organization := c.Ctx.Input.Query("organization")
46: 	if limit == "" || page == "" {
47: 		token, err := object.GetTokens(owner, organization)
48: 		if err != nil {
49: 			c.ResponseError(err.Error())
50: 			return
51: 		}
52: 
53: 		c.ResponseOk(token)
54: 	} else {
55: 		limit := util.ParseInt(limit)
56: 		count, err := object.GetTokenCount(owner, organization, field, value)
57: 		if err != nil {
58: 			c.ResponseError(err.Error())
59: 			return
60: 		}
61: 
62: 		paginator := pagination.NewPaginator(c.Ctx.Request, limit, count)
63: 		tokens, err := object.GetPaginationTokens(owner, organization, paginator.Offset(), limit, field, value, sortField, sortOrder)
64: 		if err != nil {
65: 			c.ResponseError(err.Error())
66: 			return
67: 		}
68: 
69: 		c.ResponseOk(tokens, paginator.Nums())
70: 	}
71: }
72: 
73: // GetToken
74: // @Title GetToken
75: // @Tag Token API
76: // @Description get token
77: // @Param   id     query    string  true        "The token ID in format: organization/token-name (e.g., built-in/token-123456)"
78: // @Success 200 {object} object.Token The Response object
79: // @router /get-token [get]
80: func (c *ApiController) GetToken() {
81: 	id := c.Ctx.Input.Query("id")
82: 	organization := c.Ctx.Input.Query("organization")
83: 	token, err := object.GetToken(id)
84: 	if err != nil {
85: 		c.ResponseError(err.Error())
86: 		return
87: 	}
88: 
89: 	if token == nil {
90: 		c.ResponseError(fmt.Sprintf(c.T("general:The token: %s does not exist"), id))
91: 		return
92: 	}
93: 
94: 	isGlobalAdmin, _ := c.isGlobalAdmin()
95: 	if token.Organization != organization && !isGlobalAdmin {
96: 		c.ResponseError(c.T("auth:Unauthorized operation"))
97: 		return
98: 	}
99: 
100: 	c.ResponseOk(token)
```


### Lines 230–370
```text
230: 	scope := c.Ctx.Input.Query("scope")
231: 	nonce := c.Ctx.Input.Query("nonce")
232: 	username := c.Ctx.Input.Query("username")
233: 	password := c.Ctx.Input.Query("password")
234: 	countryCode := c.Ctx.Input.Query("country_code")
235: 	tag := c.Ctx.Input.Query("tag")
236: 	avatar := c.Ctx.Input.Query("avatar")
237: 	phoneCode := c.Ctx.Input.Query("phone_code")
238: 	phoneRequired := c.Ctx.Input.Query("phone_required") == "true"
239: 	refreshToken := c.Ctx.Input.Query("refresh_token")
240: 	deviceCode := c.Ctx.Input.Query("device_code")
241: 	subjectToken := c.Ctx.Input.Query("subject_token")
242: 	subjectTokenType := c.Ctx.Input.Query("subject_token_type")
243: 	requestedTokenType := c.Ctx.Input.Query("requested_token_type")
244: 	audience := c.Ctx.Input.Query("audience")
245: 	resource := c.Ctx.Input.Query("resource")
246: 
247: 	if clientId == "" && clientSecret == "" {
248: 		clientId, clientSecret, _ = c.getClientBasicAuth()
249: 	}
250: 
251: 	if len(c.Ctx.Input.RequestBody) != 0 && grantType != "urn:ietf:params:oauth:grant-type:device_code" {
252: 		// If clientId is empty, try to read data from RequestBody
253: 		var tokenRequest TokenRequest
254: 		err := json.Unmarshal(c.Ctx.Input.RequestBody, &tokenRequest)
255: 		if err == nil {
256: 			if clientId == "" {
257: 				clientId = tokenRequest.ClientId
258: 			}
259: 			if clientSecret == "" {
260: 				clientSecret = tokenRequest.ClientSecret
261: 			}
262: 			if clientAssertion == "" {
263: 				clientAssertion = tokenRequest.ClientAssertion
264: 			}
265: 			if clientAssertionType == "" {
266: 				clientAssertionType = tokenRequest.ClientAssertionType
267: 			}
268: 			if grantType == "" {
269: 				grantType = tokenRequest.GrantType
270: 			}
271: 			if code == "" {
272: 				code = tokenRequest.Code
273: 			}
274: 			if verifier == "" {
275: 				verifier = tokenRequest.Verifier
276: 			}
277: 			if scope == "" {
278: 				scope = tokenRequest.Scope
279: 			}
280: 			if nonce == "" {
281: 				nonce = tokenRequest.Nonce
282: 			}
283: 			if username == "" {
284: 				username = tokenRequest.Username
285: 			}
286: 			if password == "" {
287: 				password = tokenRequest.Password
288: 			}
289: 			if countryCode == "" {
290: 				countryCode = tokenRequest.CountryCode
291: 			}
292: 			if tag == "" {
293: 				tag = tokenRequest.Tag
294: 			}
295: 			if avatar == "" {
296: 				avatar = tokenRequest.Avatar
297: 			}
298: 			if phoneCode == "" {
299: 				phoneCode = tokenRequest.PhoneCode
300: 			}
301: 			if !phoneRequired {
302: 				phoneRequired = tokenRequest.PhoneRequired
303: 			}
304: 			if refreshToken == "" {
305: 				refreshToken = tokenRequest.RefreshToken
306: 			}
307: 			if subjectToken == "" {
308: 				subjectToken = tokenRequest.SubjectToken
309: 			}
310: 			if subjectTokenType == "" {
311: 				subjectTokenType = tokenRequest.SubjectTokenType
312: 			}
313: 			if requestedTokenType == "" {
314: 				requestedTokenType = tokenRequest.RequestedTokenType
315: 			}
316: 			if audience == "" {
317: 				audience = tokenRequest.Audience
318: 			}
319: 			if resource == "" {
320: 				resource = tokenRequest.Resource
321: 			}
322: 			if assertion == "" {
323: 				assertion = tokenRequest.Assertion
324: 			}
325: 		}
326: 	}
327: 
328: 	// Extract DPoP proof header (RFC 9449). Empty string when DPoP is not used.
329: 	dpopProof := c.Ctx.Request.Header.Get("DPoP")
330: 
331: 	host := c.Ctx.Request.Host
332: 	var pendingDeviceCode string
333: 	var pendingDeviceAuthCache object.DeviceAuthCache
334: 
335: 	if deviceCode != "" {
336: 		deviceAuthCache, ok := object.DeviceAuthMap.Load(deviceCode)
337: 		if !ok {
338: 			c.Data["json"] = &object.TokenError{
339: 				Error:            "expired_token",
340: 				ErrorDescription: "token is expired",
341: 			}
342: 			c.SetTokenErrorHttpStatus()
343: 			c.ServeJSON()
344: 			return
345: 		}
346: 
347: 		deviceAuthCacheCast := deviceAuthCache.(object.DeviceAuthCache)
348: 
349: 		if deviceAuthCacheCast.IsExpired() {
350: 			object.DeviceAuthMap.Delete(deviceCode)
351: 			c.Data["json"] = &object.TokenError{
352: 				Error:            "expired_token",
353: 				ErrorDescription: "token is expired",
354: 			}
355: 			c.SetTokenErrorHttpStatus()
356: 			c.ServeJSON()
357: 			return
358: 		}
359: 
360: 		if deviceAuthCacheCast.Status == object.DeviceAuthStatusDenied {
361: 			c.Data["json"] = &object.TokenError{
362: 				Error:            "access_denied",
363: 				ErrorDescription: "device login was denied",
364: 			}
365: 			c.SetTokenErrorHttpStatus()
366: 			c.ServeJSON()
367: 			return
368: 		}
369: 
370: 		if deviceAuthCacheCast.Status == object.DeviceAuthStatusTokenIssued {
```


### Lines 413–428
```text
413: 	token, err := object.GetOAuthToken(grantType, clientId, clientSecret, code, verifier, scope, nonce, username, password, countryCode, host, refreshToken, tag, avatar, phoneCode, phoneRequired, c.GetAcceptLanguage(), subjectToken, subjectTokenType, requestedTokenType, assertion, clientAssertion, clientAssertionType, audience, resource, dpopProof, util.GetClientIpFromRequest(c.Ctx.Request))
414: 	if err != nil {
415: 		c.ResponseError(err.Error())
416: 		return
417: 	}
418: 
419: 	if pendingDeviceCode != "" {
420: 		if _, isTokenError := token.(*object.TokenError); !isTokenError {
421: 			pendingDeviceAuthCache.Status = object.DeviceAuthStatusTokenIssued
422: 			object.DeviceAuthMap.Store(pendingDeviceCode, pendingDeviceAuthCache)
423: 		}
424: 	}
425: 
426: 	c.Data["json"] = token
427: 	c.SetTokenErrorHttpStatus()
428: 	c.ServeJSON()
```


### Lines 500–554
```text
500: func (c *ApiController) RevokeToken() {
501: 	c.Ctx.Output.Header("Cache-Control", "no-store")
502: 	c.Ctx.Output.Header("Pragma", "no-cache")
503: 
504: 	tokenValue := c.Ctx.Input.Query("token")
505: 	tokenTypeHint := c.Ctx.Input.Query("token_type_hint")
506: 	clientId := c.Ctx.Input.Query("client_id")
507: 	clientSecret := c.Ctx.Input.Query("client_secret")
508: 	if clientId == "" && clientSecret == "" {
509: 		clientId, clientSecret, _ = c.getClientBasicAuth()
510: 	}
511: 
512: 	if clientId == "" {
513: 		c.ResponseTokenError(object.InvalidClient, "client_id is required")
514: 		return
515: 	}
516: 
517: 	application, err := object.GetApplicationByClientId(clientId)
518: 	if err != nil {
519: 		c.ResponseTokenError(object.InvalidClient, err.Error())
520: 		return
521: 	}
522: 	if application == nil || (clientSecret != "" && application.ClientSecret != clientSecret) {
523: 		c.ResponseTokenError(object.InvalidClient, c.T("token:Invalid application or wrong clientSecret"))
524: 		return
525: 	}
526: 
527: 	if tokenValue == "" {
528: 		c.ResponseTokenError(object.InvalidRequest, "token is required")
529: 		return
530: 	}
531: 
532: 	tokenError, err := object.RevokeToken(application, clientSecret, tokenValue, tokenTypeHint)
533: 	if err != nil {
534: 		c.ResponseError(err.Error())
535: 		return
536: 	}
537: 	if tokenError != nil {
538: 		c.ResponseTokenError(tokenError.Error, tokenError.ErrorDescription)
539: 		return
540: 	}
541: 
542: 	c.Ctx.Output.SetStatus(http.StatusOK)
543: 	c.Ctx.Output.Body([]byte{})
544: }
545: 
546: func (c *ApiController) ResponseTokenError(errorMsg string, errorDescription string) {
547: 	c.Data["json"] = &object.TokenError{
548: 		Error:            errorMsg,
549: 		ErrorDescription: errorDescription,
550: 	}
551: 	c.SetTokenErrorHttpStatus()
552: 	c.ServeJSON()
553: }
554: 
```


### Lines 634–757
```text
634: func (c *ApiController) IntrospectToken() {
635: 	tokenValue := c.Ctx.Input.Query("token")
636: 
637: 	ok, application, _, _, err := c.ValidateOAuth(false)
638: 	if err != nil || !ok {
639: 		return
640: 	}
641: 
642: 	respondWithInactiveToken := func() {
643: 		c.Data["json"] = &object.IntrospectionResponse{Active: false}
644: 		c.ServeJSON()
645: 	}
646: 
647: 	tokenTypeHint := c.Ctx.Input.Query("token_type_hint")
648: 	var token *object.Token
649: 	if tokenTypeHint != "" {
650: 		token, err = object.GetTokenByTokenValue(tokenValue, tokenTypeHint)
651: 		if err != nil {
652: 			c.ResponseTokenError(object.InvalidRequest, err.Error())
653: 			return
654: 		}
655: 		if token == nil || token.ExpiresIn <= 0 {
656: 			respondWithInactiveToken()
657: 			return
658: 		}
659: 	}
660: 
661: 	var introspectionResponse object.IntrospectionResponse
662: 
663: 	if application.TokenFormat == "JWT-Standard" {
664: 		jwtToken, err := object.ParseStandardJwtTokenByApplication(tokenValue, application)
665: 		if err != nil {
666: 			respondWithInactiveToken()
667: 			return
668: 		}
669: 
670: 		introspectionResponse = object.IntrospectionResponse{
671: 			Active:    true,
672: 			Scope:     jwtToken.Scope,
673: 			Username:  jwtToken.Name,
674: 			TokenType: jwtToken.TokenType,
675: 			Exp:       jwtToken.ExpiresAt.Unix(),
676: 			Iat:       jwtToken.IssuedAt.Unix(),
677: 			Nbf:       jwtToken.NotBefore.Unix(),
678: 			Sub:       jwtToken.Subject,
679: 			Aud:       jwtToken.Audience,
680: 			Iss:       jwtToken.Issuer,
681: 			Jti:       jwtToken.ID,
682: 		}
683: 	} else {
684: 		jwtToken, err := object.ParseJwtTokenByApplication(tokenValue, application)
685: 		if err != nil {
686: 			respondWithInactiveToken()
687: 			return
688: 		}
689: 
690: 		introspectionResponse = object.IntrospectionResponse{
691: 			Active: true,
692: 			Exp:    jwtToken.ExpiresAt.Unix(),
693: 			Iat:    jwtToken.IssuedAt.Unix(),
694: 			Nbf:    jwtToken.NotBefore.Unix(),
695: 			Sub:    jwtToken.Subject,
696: 			Aud:    jwtToken.Audience,
697: 			Iss:    jwtToken.Issuer,
698: 			Jti:    jwtToken.ID,
699: 		}
700: 
701: 		if jwtToken.Scope != "" {
702: 			introspectionResponse.Scope = jwtToken.Scope
703: 		}
704: 		if jwtToken.Name != "" {
705: 			introspectionResponse.Username = jwtToken.Name
706: 		}
707: 		if jwtToken.TokenType != "" {
708: 			introspectionResponse.TokenType = jwtToken.TokenType
709: 		}
710: 	}
711: 
712: 	if tokenTypeHint == "" {
713: 		token, err = object.GetTokenByTokenValue(tokenValue, introspectionResponse.TokenType)
714: 		if err != nil {
715: 			c.ResponseTokenError(object.InvalidRequest, err.Error())
716: 			return
717: 		}
718: 		if token == nil || token.ExpiresIn <= 0 {
719: 			respondWithInactiveToken()
720: 			return
721: 		}
722: 	}
723: 
724: 	if token != nil {
725: 		// The token's user may have been forbidden or deleted after the token was issued
726: 		isUserActive, err := token.IsUserActive()
727: 		if err != nil {
728: 			c.ResponseTokenError(object.InvalidRequest, err.Error())
729: 			return
730: 		}
731: 		if !isUserActive {
732: 			respondWithInactiveToken()
733: 			return
734: 		}
735: 
736: 		application, err = object.GetApplication(fmt.Sprintf("%s/%s", token.Owner, token.Application))
737: 		if err != nil {
738: 			c.ResponseTokenError(object.InvalidClient, err.Error())
739: 			return
740: 		}
741: 		if application == nil {
742: 			c.ResponseError(fmt.Sprintf(c.T("auth:The application: %s does not exist"), token.Application))
743: 			return
744: 		}
745: 
746: 		introspectionResponse.TokenType = token.TokenType
747: 		introspectionResponse.ClientId = application.ClientId
748: 
749: 		// Expose DPoP key binding in the introspection response (RFC 9449 §8).
750: 		if token.DPoPJkt != "" {
751: 			introspectionResponse.Cnf = &object.DPoPConfirmation{JKT: token.DPoPJkt}
752: 		}
753: 	}
754: 
755: 	c.Data["json"] = introspectionResponse
756: 	c.ServeJSON()
757: }
```


## G02: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\object\token_oauth.go
SHA-256: `fc50eb89850dca17a15e8959d91c1951ce8caea00d2d2c2f1c33239dbb2e5758`


### Lines 27–165
```text
27: func GetOAuthToken(grantType string, clientId string, clientSecret string, code string, verifier string, scope string, nonce string, username string, password string, countryCode string, host string, refreshToken string, tag string, avatar string, phoneCode string, phoneRequired bool, lang string, subjectToken string, subjectTokenType string, requestedTokenType string, assertion string, clientAssertion string, clientAssertionType string, audience string, resource string, dpopProof string, clientIp string) (interface{}, error) {
28: 	var (
29: 		application *Application
30: 		err         error
31: 		ok          bool
32: 	)
33: 
34: 	if clientAssertionType == "urn:ietf:params:oauth:client-assertion-type:jwt-bearer" {
35: 		ok, application, err = ValidateClientAssertion(clientAssertion, clientId, host)
36: 		if err != nil {
37: 			return nil, err
38: 		}
39: 
40: 		if !ok || application == nil {
41: 			return &TokenError{
42: 				Error:            InvalidClient,
43: 				ErrorDescription: "client_assertion is invalid",
44: 			}, nil
45: 		}
46: 
47: 		clientSecret = application.ClientSecret
48: 		clientId = application.ClientId
49: 	} else {
50: 		application, err = GetApplicationByClientId(clientId)
51: 		if err != nil {
52: 			return nil, err
53: 		}
54: 	}
55: 
56: 	if application == nil {
57: 		return &TokenError{
58: 			Error:            InvalidClient,
59: 			ErrorDescription: "client_id is invalid",
60: 		}, nil
61: 	}
62: 
63: 	// Handle WeChat Mini Program flow separately — it does not use standard OAuth grant types
64: 	if tag == "wechat_miniprogram" {
65: 		token, tokenError, err := GetWechatMiniProgramToken(application, code, phoneCode, phoneRequired, host, username, avatar, lang)
66: 		if err != nil {
67: 			return nil, err
68: 		}
69: 		if tokenError != nil {
70: 			return tokenError, nil
71: 		}
72: 		return token, nil
73: 	}
74: 
75: 	// Check if grantType is allowed in the current application
76: 	if !IsGrantTypeValid(grantType, application.GrantTypes) {
77: 		return &TokenError{
78: 			Error:            UnsupportedGrantType,
79: 			ErrorDescription: fmt.Sprintf("grant_type: %s is not supported in this application", grantType),
80: 		}, nil
81: 	}
82: 
83: 	var token *Token
84: 	var tokenError *TokenError
85: 	switch grantType {
86: 	case "authorization_code": // Authorization Code Grant
87: 		token, tokenError, err = GetAuthorizationCodeToken(application, clientSecret, code, verifier, resource, lang)
88: 	case "password": // Resource Owner Password Credentials Grant
89: 		token, tokenError, err = GetPasswordToken(application, username, password, scope, host, clientIp, lang)
90: 	case "client_credentials": // Client Credentials Grant
91: 		token, tokenError, err = GetClientCredentialsToken(application, clientSecret, scope, host)
92: 	case VerificationCodeGrantType:
93: 		token, tokenError, err = GetVerificationCodeToken(application, username, countryCode, code, scope, host, clientIp, lang)
94: 	case MobileOneClickGrantType:
95: 		token, tokenError, err = GetMobileOneClickToken(application, code, scope, host, clientIp, lang)
96: 	case "token", "id_token": // Implicit Grant
97: 		token, tokenError, err = GetImplicitToken(application, username, password, scope, nonce, host, clientIp, lang)
98: 	case "urn:ietf:params:oauth:grant-type:jwt-bearer":
99: 		token, tokenError, err = GetJwtBearerToken(application, assertion, scope, nonce, host, clientIp, lang)
100: 	case "urn:ietf:params:oauth:grant-type:device_code":
101: 		// The user has already authenticated via browser in the device flow,
102: 		// so we skip password verification and mint a token directly.
103: 		token, tokenError, err = GetDeviceCodeToken(application, username, scope, nonce, host)
104: 	case "urn:ietf:params:oauth:grant-type:token-exchange": // Token Exchange Grant (RFC 8693)
105: 		if requestedTokenType == IdJagTokenType {
106: 			idJag, tokenError, err := GetIdJagToken(application, clientSecret, subjectToken, subjectTokenType, audience, resource, scope, host)
107: 			if err != nil {
108: 				return nil, err
109: 			}
110: 			if tokenError != nil {
111: 				return tokenError, nil
112: 			}
113: 			return idJag, nil
114: 		}
115: 		token, tokenError, err = GetTokenExchangeToken(application, clientSecret, subjectToken, subjectTokenType, audience, scope, host)
116: 	case "refresh_token":
117: 		refreshToken2, err := RefreshToken(application, grantType, refreshToken, scope, clientId, clientSecret, resource, host, dpopProof, "/api/login/oauth/access_token")
118: 		if err != nil {
119: 			return nil, err
120: 		}
121: 		return refreshToken2, nil
122: 	}
123: 
124: 	if err != nil {
125: 		return nil, err
126: 	}
127: 
128: 	if tokenError != nil {
129: 		return tokenError, nil
130: 	}
131: 
132: 	// Apply DPoP binding (RFC 9449) if a DPoP proof was supplied by the client.
133: 	if dpopProof != "" {
134: 		dpopHtu := GetDPoPHtu(host, "/api/login/oauth/access_token")
135: 		jkt, dpopErr := ValidateDPoPProof(dpopProof, "POST", dpopHtu, "")
136: 		if dpopErr != nil {
137: 			return &TokenError{
138: 				Error:            "invalid_dpop_proof",
139: 				ErrorDescription: dpopErr.Error(),
140: 			}, nil
141: 		}
142: 		token.TokenType = "DPoP"
143: 		token.DPoPJkt = jkt
144: 		if err = updateTokenDPoP(token); err != nil {
145: 			return nil, err
146: 		}
147: 	}
148: 
149: 	token.CodeIsUsed = true
150: 
151: 	_, err = updateUsedByCode(token)
152: 	if err != nil {
153: 		return nil, err
154: 	}
155: 
156: 	tokenWrapper := &TokenWrapper{
157: 		AccessToken:  token.AccessToken,
158: 		IdToken:      token.IdToken,
159: 		RefreshToken: token.RefreshToken,
160: 		TokenType:    token.TokenType,
161: 		ExpiresIn:    token.ExpiresIn,
162: 		Scope:        token.Scope,
163: 	}
164: 
165: 	return tokenWrapper, nil
```


### Lines 290–388
```text
290: func GetPasswordToken(application *Application, username string, password string, scope string, host string, clientIp string, lang string) (*Token, *TokenError, error) {
291: 	expandedScope, ok := IsScopeValidAndExpand(scope, application)
292: 	if !ok {
293: 		return nil, &TokenError{
294: 			Error:            InvalidScope,
295: 			ErrorDescription: "the requested scope is invalid or not defined in the application",
296: 		}, nil
297: 	}
298: 	scope = expandedScope
299: 
300: 	user, err := GetUserByFieldsForSharedApp(application, application.Organization, username)
301: 	if err != nil {
302: 		return nil, nil, err
303: 	}
304: 	if user == nil {
305: 		return nil, &TokenError{
306: 			Error:            InvalidGrant,
307: 			ErrorDescription: "the user does not exist",
308: 		}, nil
309: 	}
310: 
311: 	if user.Ldap != "" {
312: 		err = CheckLdapUserPassword(user, password, lang)
313: 	} else {
314: 		// For OAuth users who don't have a password set, they cannot use password grant type
315: 		if user.Password == "" {
316: 			return nil, &TokenError{
317: 				Error:            InvalidGrant,
318: 				ErrorDescription: "OAuth users cannot use password grant type, please use authorization code flow",
319: 			}, nil
320: 		}
321: 		err = CheckPassword(user, password, lang)
322: 	}
323: 	if err != nil {
324: 		return nil, &TokenError{
325: 			Error:            InvalidGrant,
326: 			ErrorDescription: fmt.Sprintf("invalid username or password: %s", err.Error()),
327: 		}, nil
328: 	}
329: 
330: 	if tokenError := getMfaUserTokenError(user); tokenError != nil {
331: 		return nil, tokenError, nil
332: 	}
333: 
334: 	if tokenError := getSigninPolicyTokenError(user, lang); tokenError != nil {
335: 		return nil, tokenError, nil
336: 	}
337: 
338: 	if tokenError := checkGrantUserSignin(application, user, clientIp, lang); tokenError != nil {
339: 		return nil, tokenError, nil
340: 	}
341: 
342: 	return getUserGrantToken(application, user, scope, host)
343: }
344: 
345: // getUserGrantToken issues the token of a grant whose user has been authenticated by the grant itself
346: func getUserGrantToken(application *Application, user *User, scope string, host string) (*Token, *TokenError, error) {
347: 	err := ExtendUserWithRolesAndPermissions(user)
348: 	if err != nil {
349: 		return nil, nil, err
350: 	}
351: 
352: 	accessToken, refreshToken, idToken, tokenName, err := generateJwtToken(application, user, "", "", "", scope, "", host)
353: 	if err != nil {
354: 		return nil, &TokenError{
355: 			Error:            EndpointError,
356: 			ErrorDescription: fmt.Sprintf("generate jwt token error: %s", err.Error()),
357: 		}, nil
358: 	}
359: 
360: 	// Record the signin after the token is generated, so that the "lastSigninTime"
361: 	// claim in the token means the previous signin instead of the current one.
362: 	err = RecordUserSignin(user, "")
363: 	if err != nil {
364: 		return nil, nil, err
365: 	}
366: 
367: 	token := &Token{
368: 		Owner:        application.Owner,
369: 		Name:         tokenName,
370: 		CreatedTime:  util.GetCurrentTime(),
371: 		Application:  application.Name,
372: 		Organization: user.Owner,
373: 		User:         user.Name,
374: 		Code:         util.GenerateAuthorizationCode(),
375: 		AccessToken:  accessToken,
376: 		RefreshToken: refreshToken,
377: 		IdToken:      idToken,
378: 		ExpiresIn:    int(application.ExpireInHours * float64(hourSeconds)),
379: 		Scope:        scope,
380: 		TokenType:    "Bearer",
381: 		CodeIsUsed:   true,
382: 	}
383: 	_, err = AddToken(token)
384: 	if err != nil {
385: 		return nil, nil, err
386: 	}
387: 
388: 	return token, nil, nil
```


### Lines 494–539
```text
494: func checkGrantUserSignin(application *Application, user *User, clientIp string, lang string) *TokenError {
495: 	err := CheckApplicationSignin(application, user, clientIp, lang)
496: 	if err != nil {
497: 		return &TokenError{
498: 			Error:            InvalidGrant,
499: 			ErrorDescription: err.Error(),
500: 		}
501: 	}
502: 	return nil
503: }
504: 
505: // getMfaUserTokenError refuses a password-only grant for an MFA-enabled user, the same as
506: // the password in the URL of AutoSigninFilter, or the password alone would skip the second factor
507: func getMfaUserTokenError(user *User) *TokenError {
508: 	if !user.IsMfaEnabled() {
509: 		return nil
510: 	}
511: 
512: 	return &TokenError{
513: 		Error:            InvalidGrant,
514: 		ErrorDescription: "the user has MFA enabled and cannot sign in with a password grant, please use the authorization code flow",
515: 	}
516: }
517: 
518: func getSigninPolicyTokenError(user *User, lang string) *TokenError {
519: 	err := CheckPasswordOnlySignin(user, "", lang)
520: 	if err == nil {
521: 		return nil
522: 	}
523: 
524: 	return &TokenError{
525: 		Error:            InvalidGrant,
526: 		ErrorDescription: err.Error(),
527: 	}
528: }
529: 
530: func getInactiveUserTokenError(user *User) *TokenError {
531: 	if !user.IsForbidden && !user.IsDeleted {
532: 		return nil
533: 	}
534: 
535: 	return &TokenError{
536: 		Error:            InvalidGrant,
537: 		ErrorDescription: "the user is forbidden to sign in, please contact the administrator",
538: 	}
539: }
```


## G03: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\object\token_oauth_util.go
SHA-256: `72d6bc4353aff5c0004729c7ae758f7fe731dd22961bbba9fc1ee5a94cfc4dc5`


### Lines 351–393
```text
351: func ExpireToken(token *Token) (bool, error) {
352: 	token.ExpiresIn = 0
353: 	affected, err := ormer.Engine.ID(core.PK{token.Owner, token.Name}).Cols("expires_in").Update(token)
354: 	if err != nil {
355: 		return false, err
356: 	}
357: 
358: 	// the tokens refreshed without rotation share the refresh token, it ends with all of them
359: 	if token.RefreshTokenHash != "" {
360: 		_, err = ormer.Engine.Where("refresh_token_hash = ? and expires_in > 0", token.RefreshTokenHash).Cols("expires_in").Update(&Token{ExpiresIn: 0})
361: 		if err != nil {
362: 			return false, err
363: 		}
364: 	}
365: 
366: 	return affected != 0, nil
367: }
368: 
369: // RevokeToken expires the client's access or refresh token (RFC 7009), an unknown token or one of another client is left alone
370: func RevokeToken(application *Application, clientSecret string, tokenValue string, tokenTypeHint string) (*TokenError, error) {
371: 	token, err := GetTokenByTokenValue(tokenValue, tokenTypeHint)
372: 	if err != nil {
373: 		return nil, err
374: 	}
375: 
376: 	if token == nil || token.Owner != application.Owner || token.Application != application.Name {
377: 		return nil, nil
378: 	}
379: 
380: 	isClientAuthenticated := util.InSlice(clientAuthenticatedGrantTypes, token.GrantType) || token.GrantType == "client_credentials"
381: 	if clientSecret == "" && isClientAuthenticated && token.CodeChallenge == "" {
382: 		return &TokenError{
383: 			Error:            InvalidClient,
384: 			ErrorDescription: "client_secret is required",
385: 		}, nil
386: 	}
387: 
388: 	if token.ExpiresIn <= 0 {
389: 		return nil, nil
390: 	}
391: 
392: 	_, err = ExpireToken(token)
393: 	return nil, err
```


### Lines 562–769
```text
562: func RefreshToken(application *Application, grantType string, refreshToken string, scope string, clientId string, clientSecret string, resource string, host string, dpopProof string, dpopPath string) (interface{}, error) {
563: 	if grantType != "refresh_token" {
564: 		return &TokenError{
565: 			Error:            UnsupportedGrantType,
566: 			ErrorDescription: "grant_type should be refresh_token",
567: 		}, nil
568: 	}
569: 
570: 	var err error
571: 	if application == nil {
572: 		application, err = GetApplicationByClientId(clientId)
573: 		if err != nil {
574: 			return nil, err
575: 		}
576: 
577: 		if application == nil {
578: 			return &TokenError{
579: 				Error:            InvalidClient,
580: 				ErrorDescription: "client_id is invalid",
581: 			}, nil
582: 		}
583: 	}
584: 
585: 	// check whether the refresh token is valid, and has not expired.
586: 	token, err := GetTokenByRefreshToken(refreshToken)
587: 	if err != nil || token == nil {
588: 		return &TokenError{
589: 			Error:            InvalidGrant,
590: 			ErrorDescription: "refresh token is invalid or revoked",
591: 		}, nil
592: 	}
593: 
594: 	if tokenError := checkRefreshClientSecret(application, token, clientSecret); tokenError != nil {
595: 		return tokenError, nil
596: 	}
597: 
598: 	// check if the token has been invalidated (e.g., by SSO logout)
599: 	if token.ExpiresIn <= 0 {
600: 		return &TokenError{
601: 			Error:            InvalidGrant,
602: 			ErrorDescription: "refresh token is expired",
603: 		}, nil
604: 	}
605: 
606: 	// The refresh token must belong to the authenticated client, exactly as the
607: 	// authorization_code exchange checks it. Without this a client may present a
608: 	// refresh token issued to a different application and, together with the
609: 	// audience restore below, mint a token carrying another grant's resource.
610: 	if application.Name != token.Application {
611: 		return &TokenError{
612: 			Error:            InvalidGrant,
613: 			ErrorDescription: fmt.Sprintf("the token is for wrong application (client_id), application.Name: [%s], token.Application: [%s]", application.Name, token.Application),
614: 		}, nil
615: 	}
616: 
617: 	// RFC 8707: the refreshed token must keep the audience of the original grant.
618: 	// The client MAY repeat the resource parameter; when it does, it has to match.
619: 	if resource != "" && resource != token.Resource {
620: 		return &TokenError{
621: 			Error:            InvalidGrant,
622: 			ErrorDescription: fmt.Sprintf("resource parameter does not match the original grant, expected: [%s], got: [%s]", token.Resource, resource),
623: 		}, nil
624: 	}
625: 	resource = token.Resource
626: 
627: 	dpopJkt, tokenError := getRefreshDPoPJkt(token, dpopProof, host, dpopPath)
628: 	if tokenError != nil {
629: 		return tokenError, nil
630: 	}
631: 
632: 	cert, err := getCertByApplication(application)
633: 	if err != nil {
634: 		return nil, err
635: 	}
636: 	if cert == nil {
637: 		return &TokenError{
638: 			Error:            InvalidGrant,
639: 			ErrorDescription: fmt.Sprintf("cert: %s cannot be found", application.Cert),
640: 		}, nil
641: 	}
642: 
643: 	var oldTokenScope string
644: 	var oldTokenSubject string
645: 	if application.TokenFormat == "JWT-Standard" {
646: 		oldToken, err := ParseStandardJwtToken(refreshToken, cert)
647: 		if err != nil {
648: 			return &TokenError{
649: 				Error:            InvalidGrant,
650: 				ErrorDescription: fmt.Sprintf("parse refresh token error: %s", err.Error()),
651: 			}, nil
652: 		}
653: 		oldTokenScope = oldToken.Scope
654: 		oldTokenSubject = oldToken.Subject
655: 	} else {
656: 		oldToken, err := ParseJwtToken(refreshToken, cert)
657: 		if err != nil {
658: 			return &TokenError{
659: 				Error:            InvalidGrant,
660: 				ErrorDescription: fmt.Sprintf("parse refresh token error: %s", err.Error()),
661: 			}, nil
662: 		}
663: 		oldTokenScope = oldToken.Scope
664: 		oldTokenSubject = oldToken.Subject
665: 	}
666: 
667: 	if scope == "" {
668: 		scope = oldTokenScope
669: 	} else if !isScopeSubset(scope, oldTokenScope) {
670: 		return &TokenError{
671: 			Error:            InvalidScope,
672: 			ErrorDescription: "the requested scope exceeds the scope of the original grant",
673: 		}, nil
674: 	}
675: 
676: 	// generate a new token
677: 	user, err := getUser(token.Organization, token.User)
678: 	if err != nil {
679: 		return nil, err
680: 	}
681: 	// a token issued before its user was renamed still has the old name, the
682: 	// subject is the user's ID, which a rename keeps
683: 	if user == nil && oldTokenSubject != "" {
684: 		user, err = GetUserByUserId(token.Organization, oldTokenSubject)
685: 		if err != nil {
686: 			return nil, err
687: 		}
688: 	}
689: 	if user == nil {
690: 		return &TokenError{
691: 			Error:            InvalidGrant,
692: 			ErrorDescription: fmt.Sprintf("the user: %s doesn't exist", util.GetId(token.Organization, token.User)),
693: 		}, nil
694: 	}
695: 
696: 	if tokenError := getInactiveUserTokenError(user); tokenError != nil {
697: 		return tokenError, nil
698: 	}
699: 
700: 	err = ExtendUserWithRolesAndPermissions(user)
701: 	if err != nil {
702: 		return nil, err
703: 	}
704: 
705: 	newAccessToken, newRefreshToken, newIdToken, tokenName, err := generateJwtTokenWithOptions(application, user, "", "", "", scope, resource, host, jwtTokenOptions{RefreshScope: oldTokenScope})
706: 	if err != nil {
707: 		return &TokenError{
708: 			Error:            EndpointError,
709: 			ErrorDescription: fmt.Sprintf("generate jwt token error: %s", err.Error()),
710: 		}, nil
711: 	}
712: 
713: 	// without rotation the refresh token is handed back as is and keeps its own expiry, so the
714: 	// processes sharing it (e.g. the parallel jobs of a CLI) don't revoke it for one another
715: 	if application.DisableRefreshRotation {
716: 		newRefreshToken = refreshToken
717: 	}
718: 
719: 	newToken := &Token{
720: 		Owner:        application.Owner,
721: 		Name:         tokenName,
722: 		CreatedTime:  util.GetCurrentTime(),
723: 		Application:  application.Name,
724: 		Organization: user.Owner,
725: 		User:         user.Name,
726: 		Code:         util.GenerateAuthorizationCode(),
727: 		AccessToken:  newAccessToken,
728: 		RefreshToken: newRefreshToken,
729: 		IdToken:      newIdToken,
730: 		ExpiresIn:    int(application.ExpireInHours * float64(hourSeconds)),
731: 		Scope:        scope,
732: 		TokenType:    "Bearer",
733: 		Resource:     resource,
734: 		GrantType:    token.GrantType,
735: 		// the refreshed token stays bound to the login session that minted the original one
736: 		SessionId: token.SessionId,
737: 	}
738: 	_, err = AddToken(newToken)
739: 	if err != nil {
740: 		return nil, err
741: 	}
742: 
743: 	// Apply DPoP binding to the refreshed token if a DPoP proof was provided.
744: 	if dpopJkt != "" {
745: 		newToken.TokenType = "DPoP"
746: 		newToken.DPoPJkt = dpopJkt
747: 		if err = updateTokenDPoP(newToken); err != nil {
748: 			return nil, err
749: 		}
750: 	}
751: 
752: 	// the access token of the earlier refresh may still be in use by another sharer of the
753: 	// refresh token, it expires on its own
754: 	if !application.DisableRefreshRotation {
755: 		_, err = DeleteToken(token)
756: 		if err != nil {
757: 			return nil, err
758: 		}
759: 	}
760: 
761: 	tokenWrapper := &TokenWrapper{
762: 		AccessToken:  newToken.AccessToken,
763: 		IdToken:      newToken.IdToken,
764: 		RefreshToken: newToken.RefreshToken,
765: 		TokenType:    newToken.TokenType,
766: 		ExpiresIn:    newToken.ExpiresIn,
767: 		Scope:        newToken.Scope,
768: 	}
769: 	return tokenWrapper, nil
```


## G04: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\object\token.go
SHA-256: `32f9fc3bc7c24aa77071cc9de9b63b83e26163329cee7ad396a0f18273e7aa5a`


### Lines 28–100
```text
28: type Token struct {
29: 	Owner       string `xorm:"varchar(100) notnull pk" json:"owner"`
30: 	Name        string `xorm:"varchar(100) notnull pk" json:"name"`
31: 	CreatedTime string `xorm:"varchar(100)" json:"createdTime"`
32: 
33: 	Application  string `xorm:"varchar(100)" json:"application"`
34: 	Organization string `xorm:"varchar(100) index(org_user)" json:"organization"`
35: 	User         string `xorm:"varchar(100) index(org_user)" json:"user"`
36: 
37: 	Code             string `xorm:"varchar(100) index" json:"code"`
38: 	AccessToken      string `xorm:"mediumtext" json:"accessToken"`
39: 	RefreshToken     string `xorm:"mediumtext" json:"refreshToken"`
40: 	IdToken          string `xorm:"mediumtext" json:"idToken"`
41: 	AccessTokenHash  string `xorm:"varchar(100) index" json:"accessTokenHash"`
42: 	RefreshTokenHash string `xorm:"varchar(100) index" json:"refreshTokenHash"`
43: 	IdTokenHash      string `xorm:"varchar(100) index" json:"idTokenHash"`
44: 	ExpiresIn        int    `json:"expiresIn"`
45: 	Scope            string `xorm:"varchar(300)" json:"scope"`
46: 	TokenType        string `xorm:"varchar(100)" json:"tokenType"`
47: 	GrantType        string `xorm:"varchar(100)" json:"grantType"`
48: 	CodeChallenge    string `xorm:"varchar(100)" json:"codeChallenge"`
49: 	CodeIsUsed       bool   `json:"codeIsUsed"`
50: 	CodeExpireIn     int64  `json:"codeExpireIn"`
51: 	Resource         string `xorm:"varchar(255)" json:"resource"`           // RFC 8707 Resource Indicator
52: 	DPoPJkt          string `xorm:"varchar(255) 'dpop_jkt'" json:"dPoPJkt"` // RFC 9449 DPoP JWK thumbprint binding
53: 	SessionId        string `xorm:"varchar(100) index" json:"sessionId"`    // the Beego session id that minted the token
54: }
55: 
56: func GetTokenCount(owner, organization, field, value string) (int64, error) {
57: 	session := GetSession(owner, -1, -1, field, value, "", "")
58: 	return session.Count(&Token{Organization: organization})
59: }
60: 
61: func GetTokens(owner string, organization string) ([]*Token, error) {
62: 	tokens := []*Token{}
63: 	err := ormer.Engine.Desc("created_time").Find(&tokens, &Token{Owner: owner, Organization: organization})
64: 	return tokens, err
65: }
66: 
67: func GetPaginationTokens(owner, organization string, offset, limit int, field, value, sortField, sortOrder string) ([]*Token, error) {
68: 	tokens := []*Token{}
69: 	session := GetSession(owner, offset, limit, field, value, sortField, sortOrder)
70: 	err := session.Find(&tokens, &Token{Organization: organization})
71: 	return tokens, err
72: }
73: 
74: func getToken(owner string, name string) (*Token, error) {
75: 	if owner == "" || name == "" {
76: 		return nil, nil
77: 	}
78: 
79: 	token := Token{Owner: owner, Name: name}
80: 	existed, err := ormer.Engine.Get(&token)
81: 	if err != nil {
82: 		return nil, err
83: 	}
84: 
85: 	if existed {
86: 		return &token, nil
87: 	}
88: 
89: 	return nil, nil
90: }
91: 
92: func getTokenByCode(code string) (*Token, error) {
93: 	token := Token{Code: code}
94: 	existed, err := ormer.Engine.Get(&token)
95: 	if err != nil {
96: 		return nil, err
97: 	}
98: 
99: 	if existed {
100: 		return &token, nil
```


### Lines 106–218
```text
106: func GetTokenByAccessToken(accessToken string) (*Token, error) {
107: 	token := Token{AccessTokenHash: getTokenHash(accessToken)}
108: 	existed, err := ormer.Engine.Get(&token)
109: 	if err != nil {
110: 		return nil, err
111: 	}
112: 
113: 	if !existed {
114: 		return nil, nil
115: 	}
116: 	return &token, nil
117: }
118: 
119: // IsUserActive checks whether the token's end user is still allowed to use it, a token issued to
120: // a forbidden, soft-deleted or removed user is treated as inactive. The tokens of the
121: // "client_credentials" grant are not bound to an end user, so they are always active.
122: // Refs: https://datatracker.ietf.org/doc/html/rfc7662
123: func (token *Token) IsUserActive() (bool, error) {
124: 	if token.GrantType == "client_credentials" || token.User == "" {
125: 		return true, nil
126: 	}
127: 
128: 	user, err := getUser(token.Organization, token.User)
129: 	if err != nil {
130: 		return false, err
131: 	}
132: 	if user == nil {
133: 		return false, nil
134: 	}
135: 
136: 	return !user.IsForbidden && !user.IsDeleted, nil
137: }
138: 
139: func GetTokenByRefreshToken(refreshToken string) (*Token, error) {
140: 	token := Token{RefreshTokenHash: getTokenHash(refreshToken)}
141: 	existed, err := ormer.Engine.Get(&token)
142: 	if err != nil {
143: 		return nil, err
144: 	}
145: 
146: 	if !existed {
147: 		return nil, nil
148: 	}
149: 	return &token, nil
150: }
151: 
152: func GetTokenByIdToken(idToken string) (*Token, error) {
153: 	token := Token{IdTokenHash: getTokenHash(idToken)}
154: 	existed, err := ormer.Engine.Get(&token)
155: 	if err != nil {
156: 		return nil, err
157: 	}
158: 
159: 	if !existed {
160: 		return nil, nil
161: 	}
162: 	return &token, nil
163: }
164: 
165: // GetTokenByTokenValue looks the token up as the hinted type first and then as the other type (RFC 7009 and RFC 7662 section 2.1)
166: func GetTokenByTokenValue(tokenValue, tokenTypeHint string) (*Token, error) {
167: 	getters := []func(string) (*Token, error){GetTokenByAccessToken, GetTokenByRefreshToken}
168: 	if tokenTypeHint == "refresh_token" || tokenTypeHint == "refresh-token" {
169: 		getters[0], getters[1] = getters[1], getters[0]
170: 	}
171: 
172: 	for _, getter := range getters {
173: 		token, err := getter(tokenValue)
174: 		if err != nil || token != nil {
175: 			return token, err
176: 		}
177: 	}
178: 
179: 	return nil, nil
180: }
181: 
182: func updateUsedByCode(token *Token) (bool, error) {
183: 	affected, err := ormer.Engine.Where("code=?", token.Code).Cols("code_is_used", "grant_type").Update(token)
184: 	if err != nil {
185: 		return false, err
186: 	}
187: 
188: 	return affected != 0, nil
189: }
190: 
191: func claimAuthorizationCode(code string) (bool, error) {
192: 	affected, err := ormer.Engine.Where("code = ? and code_is_used = ?", code, false).Cols("code_is_used").Update(&Token{CodeIsUsed: true})
193: 	if err != nil {
194: 		return false, err
195: 	}
196: 
197: 	return affected != 0, nil
198: }
199: 
200: func GetToken(id string) (*Token, error) {
201: 	owner, name, err := util.GetOwnerAndNameFromIdWithError(id)
202: 	if err != nil {
203: 		return nil, err
204: 	}
205: 	return getToken(owner, name)
206: }
207: 
208: func (token *Token) GetId() string {
209: 	return fmt.Sprintf("%s/%s", token.Owner, token.Name)
210: }
211: 
212: func getTokenHash(input string) string {
213: 	hash := sha256.Sum256([]byte(input))
214: 	res := hex.EncodeToString(hash[:])
215: 	if len(res) > 64 {
216: 		return res[:64]
217: 	}
218: 	return res
```


## G05: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\object\token_jwt.go
SHA-256: `ea32097e74ad7a89bf2f6db3a2f9c9586eec96c69bdff8f5257f2bef7f820eaa`


### Lines 630–780
```text
630: func generateJwtToken(application *Application, user *User, provider string, signinMethod string, nonce string, scope string, resource string, host string) (string, string, string, string, error) {
631: 	return generateJwtTokenWithOptions(application, user, provider, signinMethod, nonce, scope, resource, host, jwtTokenOptions{})
632: }
633: 
634: func generateJwtTokenWithOptions(application *Application, user *User, provider string, signinMethod string, nonce string, scope string, resource string, host string, options jwtTokenOptions) (string, string, string, string, error) {
635: 	nowTime := time.Now()
636: 	expireTime := nowTime.Add(time.Duration(application.ExpireInHours * float64(time.Hour)))
637: 	refreshExpireTime := nowTime.Add(time.Duration(application.RefreshExpireInHours * float64(time.Hour)))
638: 	if application.RefreshExpireInHours == 0 {
639: 		refreshExpireTime = expireTime
640: 	}
641: 
642: 	user, err := getTokenUser(application, user)
643: 	if err != nil {
644: 		return "", "", "", "", err
645: 	}
646: 
647: 	_, originBackend := getOriginFromHost(host)
648: 
649: 	name := util.GenerateId()
650: 	jti := util.GetId(application.Owner, name)
651: 
652: 	claims := Claims{
653: 		User:      user,
654: 		TokenType: "access-token",
655: 		Nonce:     nonce,
656: 		// FIXME: A workaround for custom claim by reusing `tag` in user info
657: 		Tag:          user.Tag,
658: 		Scope:        scope,
659: 		Azp:          application.ClientId,
660: 		Provider:     provider,
661: 		SigninMethod: signinMethod,
662: 		RegisteredClaims: jwt.RegisteredClaims{
663: 			Issuer:    originBackend,
664: 			Subject:   user.Id,
665: 			Audience:  []string{application.ClientId},
666: 			ExpiresAt: jwt.NewNumericDate(expireTime),
667: 			NotBefore: jwt.NewNumericDate(nowTime),
668: 			IssuedAt:  jwt.NewNumericDate(nowTime),
669: 			ID:        jti,
670: 		},
671: 	}
672: 
673: 	if options.AuthTime > 0 {
674: 		claims.AuthTime = jwt.NewNumericDate(time.Unix(options.AuthTime, 0))
675: 	}
676: 
677: 	if application.IsShared {
678: 		claims.Audience = []string{application.ClientId + "-org-" + user.Owner}
679: 	}
680: 
681: 	// the ID token is its own JWT so that it can't be replayed as the access token (RFC 8725 3.12),
682: 	// and its audience stays the client even when an RFC 8707 resource retargets the access token
683: 	idClaims := claims
684: 	idClaims.TokenType = "id-token"
685: 	idClaims.ID = util.GetId(application.Owner, util.GenerateId())
686: 
687: 	// RFC 8707: Use resource as audience when provided
688: 	if resource != "" {
689: 		claims.Audience = []string{resource}
690: 	}
691: 
692: 	// RFC 6749 section 6: the refresh token keeps the scope of the grant
693: 	refreshClaims := claims
694: 	refreshClaims.TokenType = "refresh-token"
695: 	refreshClaims.ExpiresAt = jwt.NewNumericDate(refreshExpireTime)
696: 	if options.RefreshScope != "" {
697: 		refreshClaims.Scope = options.RefreshScope
698: 	}
699: 
700: 	var token *jwt.Token
701: 	var refreshToken *jwt.Token
702: 	// the ID token is created once the access token is signed, its at_hash depends on it
703: 	var newIdToken func() *jwt.Token
704: 
705: 	if application.TokenFormat == "" {
706: 		application.TokenFormat = "JWT"
707: 	}
708: 
709: 	jwtMethod := getJwtSigningMethod(application)
710: 
711: 	// the JWT token length in "JWT-Empty" mode will be very short, as User object only has two properties: owner and name
712: 	if application.TokenFormat == "JWT" {
713: 		token = jwt.NewWithClaims(jwtMethod, getClaimsWithoutThirdIdp(claims))
714: 		newIdToken = func() *jwt.Token { return jwt.NewWithClaims(jwtMethod, getClaimsWithoutThirdIdp(idClaims)) }
715: 		refreshToken = jwt.NewWithClaims(jwtMethod, getClaimsWithoutThirdIdp(refreshClaims))
716: 	} else if application.TokenFormat == "JWT-Empty" {
717: 		token = jwt.NewWithClaims(jwtMethod, getShortClaims(claims))
718: 		newIdToken = func() *jwt.Token { return jwt.NewWithClaims(jwtMethod, getShortClaims(idClaims)) }
719: 		refreshToken = jwt.NewWithClaims(jwtMethod, getShortClaims(refreshClaims))
720: 	} else if application.TokenFormat == "JWT-Custom" {
721: 		token = jwt.NewWithClaims(jwtMethod, getClaimsCustom(claims, application.TokenFields, application.TokenAttributes))
722: 		newIdToken = func() *jwt.Token {
723: 			return jwt.NewWithClaims(jwtMethod, getClaimsCustom(idClaims, application.TokenFields, application.TokenAttributes))
724: 		}
725: 		refreshToken = jwt.NewWithClaims(jwtMethod, getRefreshClaimsCustom(refreshClaims, application.TokenFields, application.TokenAttributes, refreshExpireTime))
726: 	} else if application.TokenFormat == "JWT-Standard" {
727: 		token = jwt.NewWithClaims(jwtMethod, getStandardClaims(claims))
728: 		newIdToken = func() *jwt.Token { return jwt.NewWithClaims(jwtMethod, getStandardClaims(idClaims)) }
729: 		refreshToken = jwt.NewWithClaims(jwtMethod, getStandardClaims(refreshClaims))
730: 	} else {
731: 		return "", "", "", "", fmt.Errorf("unknown application TokenFormat: %s", application.TokenFormat)
732: 	}
733: 
734: 	cert, err := getCertByApplication(application)
735: 	if err != nil {
736: 		return "", "", "", "", err
737: 	}
738: 
739: 	if cert == nil {
740: 		if application.Cert == "" {
741: 			return "", "", "", "", fmt.Errorf("The cert field of the application \"%s\" should not be empty", application.GetId())
742: 		} else {
743: 			return "", "", "", "", fmt.Errorf("The cert \"%s\" does not exist", application.Cert)
744: 		}
745: 	}
746: 
747: 	var (
748: 		tokenString        string
749: 		refreshTokenString string
750: 		idTokenString      string
751: 		key                interface{}
752: 	)
753: 
754: 	if strings.Contains(application.TokenSigningMethod, "RS") || application.TokenSigningMethod == "" {
755: 		// RSA private key
756: 		key, err = jwt.ParseRSAPrivateKeyFromPEM([]byte(cert.PrivateKey))
757: 	} else if strings.Contains(application.TokenSigningMethod, "ES") {
758: 		// ES private key
759: 		key, err = jwt.ParseECPrivateKeyFromPEM([]byte(cert.PrivateKey))
760: 	} else if strings.Contains(application.TokenSigningMethod, "Ed") {
761: 		// Ed private key
762: 		key, err = jwt.ParseEdPrivateKeyFromPEM([]byte(cert.PrivateKey))
763: 	}
764: 	if err != nil {
765: 		return "", "", "", "", err
766: 	}
767: 
768: 	token.Header["kid"] = cert.Name
769: 	tokenString, err = token.SignedString(key)
770: 	if err != nil {
771: 		return "", "", "", "", err
772: 	}
773: 	refreshTokenString, err = refreshToken.SignedString(key)
774: 	if err != nil {
775: 		return "", "", "", "", err
776: 	}
777: 
778: 	if options.Code != "" {
779: 		idClaims.CHash = getOidcHash(options.Code, jwtMethod)
780: 	}
```


## G06: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\object\check.go
SHA-256: `3f63363e514e37ba825aad8037e63f2b3975b35778a2be2e2388005a9cf809ab`


### Lines 232–319
```text
232: func checkSigninErrorTimes(user *User, lang string) error {
233: 	failedSigninLimit, failedSigninFrozenTime, err := GetFailedSigninConfigByUser(user)
234: 	if err != nil {
235: 		return err
236: 	}
237: 
238: 	if user.SigninWrongTimes >= failedSigninLimit {
239: 		lastSignWrongTime, _ := time.Parse(time.RFC3339, user.LastSigninWrongTime)
240: 		passedTime := time.Now().UTC().Sub(lastSignWrongTime)
241: 		minutes := failedSigninFrozenTime - int(passedTime.Minutes())
242: 
243: 		// deny the login if the error times is greater than the limit and the last login time is less than the duration
244: 		if minutes > 0 {
245: 			return newSigninError(SigninReasonAccountFrozen, fmt.Sprintf(i18n.Translate(lang, "check:You have entered the wrong password or code too many times, please wait for %d minutes and try again"), minutes))
246: 		}
247: 
248: 		// reset the error times
249: 		user.SigninWrongTimes = 0
250: 
251: 		_, err := UpdateUser(user.GetId(), user, []string{"signin_wrong_times"}, false)
252: 		return err
253: 	}
254: 
255: 	return nil
256: }
257: 
258: func CheckPassword(user *User, password string, lang string, options ...bool) error {
259: 	if password == "" {
260: 		return errors.New(i18n.Translate(lang, "check:Password cannot be empty"))
261: 	}
262: 
263: 	enableCaptcha := false
264: 	if len(options) > 0 {
265: 		enableCaptcha = options[0]
266: 	}
267: 
268: 	// check the login error times
269: 	if !enableCaptcha {
270: 		err := checkSigninErrorTimes(user, lang)
271: 		if err != nil {
272: 			return err
273: 		}
274: 	}
275: 
276: 	organization, err := GetOrganizationByUser(user)
277: 	if err != nil {
278: 		return err
279: 	}
280: 	if organization == nil {
281: 		return errors.New(i18n.Translate(lang, "check:Organization does not exist"))
282: 	}
283: 
284: 	passwordType := user.PasswordType
285: 	if passwordType == "" {
286: 		passwordType = organization.PasswordType
287: 	}
288: 	// an organization without a password type stores the passwords as they are
289: 	if passwordType == "" {
290: 		passwordType = "plain"
291: 	}
292: 
293: 	credManager := cred.GetCredManager(passwordType)
294: 	if credManager == nil {
295: 		return fmt.Errorf(i18n.Translate(lang, "check:unsupported password type: %s"), passwordType)
296: 	}
297: 
298: 	if organization.MasterPassword != "" {
299: 		if password == organization.MasterPassword || credManager.IsPasswordCorrect(password, organization.MasterPassword, organization.PasswordSalt) {
300: 			return resetUserSigninErrorTimes(user)
301: 		}
302: 	}
303: 
304: 	if !credManager.IsPasswordCorrect(password, user.Password, organization.PasswordSalt) && !credManager.IsPasswordCorrect(password, user.Password, user.PasswordSalt) {
305: 		return recordSigninErrorInfo(user, lang, enableCaptcha)
306: 	}
307: 
308: 	isOutdated := organization.PasswordType != "" && passwordType != organization.PasswordType
309: 	if isOutdated {
310: 		user.Password = password
311: 		user.UpdateUserPassword(organization)
312: 		_, err = UpdateUser(user.GetId(), user, []string{"password", "password_type", "password_salt"}, true)
313: 		if err != nil {
314: 			return err
315: 		}
316: 	}
317: 
318: 	return resetUserSigninErrorTimes(user)
319: }
```


### Lines 646–742
```text
646: func CheckPasswordOnlySignin(user *User, clientIp string, lang string) error {
647: 	organization, err := GetOrganizationByUser(user)
648: 	if err != nil {
649: 		return err
650: 	}
651: 	if organization != nil && organization.DisableSignin {
652: 		return fmt.Errorf(i18n.Translate(lang, "auth:The organization: %s has disabled users to signin"), organization.Name)
653: 	}
654: 
655: 	if clientIp != "" {
656: 		err = CheckEntryIp(clientIp, user, nil, organization, lang)
657: 		if err != nil {
658: 			return err
659: 		}
660: 	}
661: 
662: 	if user.NeedUpdatePassword || IsNeedPromptMfa(organization, user) {
663: 		return fmt.Errorf("the user: %s must update the password or set up MFA on the login page first", user.GetId())
664: 	}
665: 	return nil
666: }
667: 
668: func CheckApplicationSignin(application *Application, user *User, clientIp string, lang string) error {
669: 	if user.IsForbidden {
670: 		return errors.New(i18n.Translate(lang, "check:The user is forbidden to sign in, please contact the administrator"))
671: 	}
672: 
673: 	if user.IsDeleted {
674: 		return errors.New(i18n.Translate(lang, "check:The user has been deleted and cannot be used to sign in, please contact the administrator"))
675: 	}
676: 
677: 	err := CheckEntryIp(clientIp, user, application, application.OrganizationObj, lang)
678: 	if err != nil {
679: 		return err
680: 	}
681: 
682: 	if application.DisableSignin {
683: 		return fmt.Errorf(i18n.Translate(lang, "auth:The application: %s has disabled users to signin"), application.Name)
684: 	}
685: 
686: 	if application.OrganizationObj != nil && application.OrganizationObj.DisableSignin {
687: 		return fmt.Errorf(i18n.Translate(lang, "auth:The organization: %s has disabled users to signin"), application.Organization)
688: 	}
689: 
690: 	err = checkUserOrganizationSignin(application, user, clientIp, lang)
691: 	if err != nil {
692: 		return err
693: 	}
694: 
695: 	allowed, err := CheckLoginPermission(user.GetId(), application)
696: 	if err != nil {
697: 		return err
698: 	}
699: 	if !allowed {
700: 		return errors.New(i18n.Translate(lang, "auth:Unauthorized operation"))
701: 	}
702: 
703: 	if !user.IsGlobalAdmin() && !user.IsAdmin && len(application.Tags) > 0 && !util.HasTagInSlice(application.Tags, user.Tag) {
704: 		return fmt.Errorf(i18n.Translate(lang, "auth:User's tag: %s is not listed in the application's tags"), user.Tag)
705: 	}
706: 
707: 	return nil
708: }
709: 
710: func checkUserOrganizationSignin(application *Application, user *User, clientIp string, lang string) error {
711: 	if application.OrganizationObj != nil && application.OrganizationObj.Name == user.Owner {
712: 		return nil
713: 	}
714: 
715: 	organization, err := GetOrganizationByUser(user)
716: 	if err != nil {
717: 		return err
718: 	}
719: 	if organization == nil {
720: 		return nil
721: 	}
722: 
723: 	if organization.DisableSignin {
724: 		return fmt.Errorf(i18n.Translate(lang, "auth:The organization: %s has disabled users to signin"), organization.Name)
725: 	}
726: 	return CheckEntryIp(clientIp, nil, nil, organization, lang)
727: }
728: 
729: func CheckLoginPermission(userId string, application *Application) (bool, error) {
730: 	owner, _, err := util.GetOwnerAndNameFromIdWithError(userId)
731: 	if err != nil {
732: 		return false, err
733: 	}
734: 	if owner == "built-in" {
735: 		return true, nil
736: 	}
737: 
738: 	user, err := GetUser(userId)
739: 	if err != nil {
740: 		return false, err
741: 	}
742: 	if user != nil && user.IsAdmin {
```


## G07: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\object\check_util.go
SHA-256: `f76aaf7be6e7b3ff6d18736de3f058e66708cf8704c2078807186f63a61e224e`


### Lines 41–125
```text
41: func resetUserSigninErrorTimes(user *User) error {
42: 	// if the password is correct and wrong times is not zero, reset the error times
43: 	if user.SigninWrongTimes == 0 {
44: 		return nil
45: 	}
46: 
47: 	user.SigninWrongTimes = 0
48: 	_, err := UpdateUser(user.GetId(), user, []string{"signin_wrong_times", "last_signin_wrong_time"}, false)
49: 	return err
50: }
51: 
52: // RecordUserSignin records the last successful signin time and IP of the user.
53: // It must be called after the token has been generated, so that the
54: // "last_signin_time" / "last_signin_ip" claims in the token still hold the
55: // previous signin rather than the current one (the current signin time is
56: // always available in the token's "iat" claim).
57: // See https://github.com/casdoor/casdoor/issues/5646 and
58: // https://github.com/casdoor/casdoor/issues/5651
59: func RecordUserSignin(user *User, clientIp string) error {
60: 	user.LastSigninTime = util.GetCurrentTime()
61: 	if clientIp != "" {
62: 		user.LastSigninIp = clientIp
63: 	}
64: 
65: 	_, err := UpdateUser(user.GetId(), user, []string{"last_signin_time", "last_signin_ip"}, false)
66: 	return err
67: }
68: 
69: func GetFailedSigninConfigByUser(user *User) (int, int, error) {
70: 	application, err := GetApplicationByUser(user)
71: 	if err != nil {
72: 		return 0, 0, err
73: 	}
74: 	if application == nil {
75: 		return 0, 0, fmt.Errorf("the application for user %s is not found", user.GetId())
76: 	}
77: 
78: 	failedSigninLimit := application.FailedSigninLimit
79: 	if failedSigninLimit == 0 {
80: 		failedSigninLimit = DefaultFailedSigninLimit
81: 	}
82: 
83: 	failedSigninFrozenTime := application.FailedSigninFrozenTime
84: 	if failedSigninFrozenTime == 0 {
85: 		failedSigninFrozenTime = DefaultFailedSigninFrozenTime
86: 	}
87: 
88: 	return failedSigninLimit, failedSigninFrozenTime, nil
89: }
90: 
91: func recordSigninErrorInfo(user *User, lang string, options ...bool) error {
92: 	enableCaptcha := false
93: 	if len(options) > 0 {
94: 		enableCaptcha = options[0]
95: 	}
96: 
97: 	failedSigninLimit, failedSigninFrozenTime, errSignin := GetFailedSigninConfigByUser(user)
98: 	if errSignin != nil {
99: 		return errSignin
100: 	}
101: 
102: 	// increase failed login count, and record the lockout time only when first reaching the limit
103: 	if user.SigninWrongTimes < failedSigninLimit {
104: 		user.SigninWrongTimes++
105: 		if user.SigninWrongTimes >= failedSigninLimit {
106: 			user.LastSigninWrongTime = time.Now().UTC().Format(time.RFC3339)
107: 		}
108: 	}
109: 
110: 	// update user
111: 	_, err := UpdateUser(user.GetId(), user, []string{"signin_wrong_times", "last_signin_wrong_time"}, false)
112: 	if err != nil {
113: 		return err
114: 	}
115: 
116: 	leftChances := failedSigninLimit - user.SigninWrongTimes
117: 	if leftChances == 0 && enableCaptcha {
118: 		return newSigninError(SigninReasonWrongPassword, i18n.Translate(lang, "check:password or code is incorrect"))
119: 	} else if leftChances >= 0 {
120: 		return newSigninError(SigninReasonWrongPassword, fmt.Sprintf(i18n.Translate(lang, "check:password or code is incorrect, you have %s remaining chances"), strconv.Itoa(leftChances)))
121: 	}
122: 
123: 	// don't show the chance error message if the user has no chance left
124: 	return newSigninError(SigninReasonAccountFrozen, fmt.Sprintf(i18n.Translate(lang, "check:You have entered the wrong password or code too many times, please wait for %d minutes and try again"), failedSigninFrozenTime))
125: }
```


## G08: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\object\user.go
SHA-256: `3cad53ca26b13a1d9da882bd24785d378bece15b542f6cd56a1353721c5e5237`


### Lines 936–1040
```text
936: func UpdateUser(id string, user *User, columns []string, isAdmin bool) (bool, error) {
937: 	var err error
938: 	owner, name := util.GetOwnerAndNameFromIdNoCheck(id)
939: 	oldUser, err := getUser(owner, name)
940: 	if err != nil {
941: 		return false, err
942: 	}
943: 	if oldUser == nil {
944: 		return false, fmt.Errorf("the user: %s is not found", id)
945: 	}
946: 
947: 	// Auto-upgrade guest users when they update their username or password
948: 	if oldUser.Tag == "guest-user" {
949: 		// Check if username is being changed from the generated guest username
950: 		usernameChanged := oldUser.Name != user.Name && !strings.HasPrefix(user.Name, "guest_")
951: 		// Check if password is being updated (not the placeholder ***)
952: 		passwordChanged := user.Password != "***" && user.Password != "" && user.Password != oldUser.Password
953: 
954: 		if usernameChanged || passwordChanged {
955: 			// Upgrade to normal user
956: 			user.Tag = "normal-user"
957: 			// Ensure tag is included in the update columns
958: 			if !util.InSlice(columns, "tag") && len(columns) > 0 {
959: 				columns = append(columns, "tag")
960: 			}
961: 		}
962: 	}
963: 
964: 	if name != user.Name {
965: 		err := userChangeTrigger(owner, name, user.Name)
966: 		if err != nil {
967: 			return false, err
968: 		}
969: 	}
970: 
971: 	if user.Password == "***" {
972: 		user.Password = oldUser.Password
973: 	}
974: 
975: 	if user.FaceIds == nil {
976: 		user.FaceIds = oldUser.FaceIds
977: 	}
978: 
979: 	if user.Id != oldUser.Id && user.Id == "" {
980: 		user.Id = oldUser.Id
981: 	}
982: 
983: 	if user.Avatar != oldUser.Avatar && user.Avatar != "" && user.PermanentAvatar != "*" {
984: 		user.PermanentAvatar, err = getPermanentAvatarUrl(user.Owner, user.Name, user.Avatar, false)
985: 		if err != nil {
986: 			return false, err
987: 		}
988: 	}
989: 
990: 	if len(columns) == 0 {
991: 		columns = GetDefaultUserUpdateColumns(isAdmin)
992: 	}
993: 
994: 	columns = append(columns, "updated_time")
995: 	user.UpdatedTime = util.GetCurrentTime()
996: 
997: 	if len(user.DeletedTime) > 0 {
998: 		columns = append(columns, "deleted_time")
999: 	}
1000: 
1001: 	if util.InSlice(columns, "groups") {
1002: 		_, err := userEnforcer.UpdateGroupsForUser(user.GetId(), user.Groups)
1003: 		if err != nil {
1004: 			return false, err
1005: 		}
1006: 	}
1007: 
1008: 	affected, err := updateUser(id, user, columns)
1009: 	if err != nil {
1010: 		return false, err
1011: 	}
1012: 
1013: 	if affected != 0 && isUserAccessRevoked(oldUser, user, columns) {
1014: 		// The tokens and sessions are keyed by the old user name, it may have just been renamed
1015: 		err = terminateUserAccess(oldUser)
1016: 		if err != nil {
1017: 			return true, fmt.Errorf("the user: %s is updated, but terminating its access failed: %w", id, err)
1018: 		}
1019: 	}
1020: 
1021: 	return affected != 0, nil
1022: }
1023: 
1024: func updateUser(id string, user *User, columns []string) (int64, error) {
1025: 	owner, name := util.GetOwnerAndNameFromIdNoCheck(id)
1026: 	err := user.UpdateUserHash()
1027: 	if err != nil {
1028: 		return 0, err
1029: 	}
1030: 
1031: 	// Ensure hash column is included in updates when columns are specified
1032: 	if len(columns) > 0 && !util.InSlice(columns, "hash") {
1033: 		columns = append(columns, "hash")
1034: 	}
1035: 
1036: 	affected, err := ormer.Engine.ID(core.PK{owner, name}).Cols(columns...).Update(user)
1037: 	if err != nil {
1038: 		return 0, err
1039: 	}
1040: 	return affected, nil
```


### Lines 1315–1378
```text
1315: // isUserAccessRevoked checks whether an update has just forbidden or soft-deleted the user, the
1316: // columns are the ones the update actually wrote, a nil value means that all of them were written
1317: func isUserAccessRevoked(oldUser *User, user *User, columns []string) bool {
1318: 	if oldUser.IsForbidden || oldUser.IsDeleted {
1319: 		return false
1320: 	}
1321: 
1322: 	if user.IsForbidden && (columns == nil || util.InSlice(columns, "is_forbidden")) {
1323: 		return true
1324: 	}
1325: 	if user.IsDeleted && (columns == nil || util.InSlice(columns, "is_deleted")) {
1326: 		return true
1327: 	}
1328: 
1329: 	return false
1330: }
1331: 
1332: // terminateUserAccess forces the user offline, it expires the user's tokens and drops all of its
1333: // sessions, in the same way as the "logout from all applications" flow. It does nothing when the
1334: // user has neither active tokens nor sessions, so it is safe to call it more than once
1335: func terminateUserAccess(user *User) error {
1336: 	tokens, err := GetActiveTokensByUser(user.Owner, user.Name)
1337: 	if err != nil {
1338: 		return err
1339: 	}
1340: 
1341: 	sessions, err := GetUserSessions(user.Owner, user.Name)
1342: 	if err != nil {
1343: 		return err
1344: 	}
1345: 
1346: 	if len(tokens) == 0 && len(sessions) == 0 {
1347: 		return nil
1348: 	}
1349: 
1350: 	// The ids are collected for the SSO logout notification below, the Beego sessions
1351: 	// themselves are destroyed by DeleteAllUserSessions()
1352: 	sessionIds := []string{}
1353: 	for _, session := range sessions {
1354: 		sessionIds = append(sessionIds, session.SessionId...)
1355: 	}
1356: 
1357: 	// The host is empty, so the issuer falls back to the configured origin
1358: 	sendBackchannelLogoutForTokens(user, tokens, "", "")
1359: 	SendSamlLogout(user.Owner, user.Name, nil, "")
1360: 
1361: 	_, err = ExpireTokenByUser(user.Owner, user.Name)
1362: 	if err != nil {
1363: 		return err
1364: 	}
1365: 
1366: 	// The sessions are stored under the applications used at login, so all of them have to be
1367: 	// dropped and not only the "app-built-in" one
1368: 	_, err = DeleteAllUserSessions(user.Owner, user.Name)
1369: 	if err != nil {
1370: 		return err
1371: 	}
1372: 
1373: 	// The notification is best-effort, the access has already been revoked at this point, so a
1374: 	// slow or failing notification provider must not block or undo it
1375: 	go func() {
1376: 		_ = SendSsoLogoutNotifications(user, sessionIds, tokens)
1377: 	}()
1378: 
```


## G09: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\routers\authz_filter.go
SHA-256: `29fb077e73ea72176e0f7be1bcdc178e94d5ca1159817f57c7ee4350df3ec165`


### Lines 36–58
```text
36: var orgOwnerObject = []string{
37: 	"-organization",
38: 	"-syncer",
39: 	"-webhook",
40: 	"-application",
41: 	"-token",
42: }
43: 
44: // organizationParamObject lists the APIs whose controllers scope the returned or
45: // modified objects by the "organization" query param, which makes that param the
46: // object to authorize against.
47: var organizationParamObject = []string{
48: 	"/api/get-applications",
49: 	"/api/get-organization-applications",
50: 	"/api/get-syncers",
51: 	"/api/get-syncer",
52: 	"/api/run-syncer",
53: 	"/api/get-tokens",
54: 	"/api/get-token",
55: 	"/api/get-webhooks",
56: 	"/api/get-webhook",
57: 	"/api/get-webhook-events",
58: }
```


## G10: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\object\ormer_session.go
SHA-256: `1ced309f0650198f43be63875c877ef4f2d80ee24bc876f02067a5377112fe38`


### Lines 32–53
```text
32: func GetSession(owner string, offset, limit int, field, value, sortField, sortOrder string) *xorm.Session {
33: 	session := ormer.Engine.Prepare()
34: 	if offset != -1 && limit != -1 {
35: 		session.Limit(limit, offset)
36: 	}
37: 	if owner != "" {
38: 		session = session.And("owner=?", owner)
39: 	}
40: 	if field != "" && value != "" {
41: 		if util.FilterField(field) {
42: 			session = session.And(fmt.Sprintf("%s like ?", util.CamelToSnakeCase(field)), fmt.Sprintf("%%%s%%", value))
43: 		}
44: 	}
45: 	if sortField == "" || sortOrder == "" || !util.FilterField(sortField) {
46: 		sortField = "created_time"
47: 	}
48: 	if sortOrder == "ascend" {
49: 		session = session.Asc(util.CamelToSnakeCase(sortField))
50: 	} else {
51: 		session = session.Desc(util.CamelToSnakeCase(sortField))
52: 	}
53: 	return session
```

## G11: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\controllers\account.go
SHA-256: `e7d647fcad7df1ab9c7beeee43d935d32996d2e8f0884870474fc52de44b5905`

### Lines 774–803
```text
774: // GetUserinfo
775: // UserInfo
776: // @Title UserInfo
777: // @Tag Account API
778: // @Description return user information according to OIDC standards
779: // @Success 200 {object} object.Userinfo The Response object
780: // @router /userinfo [get,post]
781: func (c *ApiController) GetUserinfo() {
782: 	if c.GetSessionUsername() == "" {
783: 		// RFC 6750 section 3.1: a request without an access token gets a challenge without an error code
784: 		c.Ctx.Output.Header("WWW-Authenticate", "Bearer")
785: 		c.Ctx.Output.SetStatus(http.StatusUnauthorized)
786: 	}
787: 
788: 	user, ok := c.RequireSignedInUser()
789: 	if !ok {
790: 		return
791: 	}
792: 
793: 	scope, aud := c.GetSessionOidc()
794: 	host := c.Ctx.Request.Host
795: 
796: 	userInfo, err := object.GetUserInfo(user, scope, aud, host)
797: 	if err != nil {
798: 		c.ResponseError(err.Error())
799: 		return
800: 	}
801: 
802: 	c.Data["json"] = userInfo
803: 	c.ServeJSON()
```

## G12: D:\毕业设计\research_main_innovation\ci01_contract_audit\sources\casdoor-v4.25.0\routers\auto_signin_filter.go
SHA-256: `474a1cf52684d48dd934c054cde3611392361d80e27afe725df7b6399eafe489`

### Lines 28–142
```text
28: func AutoSigninFilter(ctx *context.Context) {
29: 	urlPath := ctx.Request.URL.Path
30: 	if strings.HasPrefix(urlPath, "/api/login/oauth/access_token") {
31: 		return
32: 	}
33: 	// The RFC 7591/7592 DCR endpoints authenticate themselves: the bearer value is the
34: 	// application's "registration_access_token", which is not a row in the "token" table.
35: 	if strings.HasPrefix(urlPath, "/api/oauth/register") {
36: 		return
37: 	}
38: 	if urlPath == "/api/mcp" {
39: 		var req mcpself.McpRequest
40: 		if err := json.Unmarshal(ctx.Input.RequestBody, &req); err == nil {
41: 			if req.Method == "initialize" || req.Method == "notifications/initialized" || req.Method == "ping" || req.Method == "tools/list" {
42: 				return
43: 			}
44: 		}
45: 	}
46: 	//if getSessionUser(ctx) != "" {
47: 	//	return
48: 	//}
49: 
50: 	// GET parameter like "/page?access_token=123" or
51: 	// HTTP Bearer token like "Authorization: Bearer 123"
52: 	accessToken := ctx.Input.Query("accessToken")
53: 	if accessToken == "" {
54: 		accessToken = ctx.Input.Query("access_token")
55: 	}
56: 	if accessToken == "" {
57: 		accessToken = parseBearerToken(ctx)
58: 		if accessToken != "" {
59: 			skipSessionPersistence(ctx)
60: 		}
61: 	}
62: 
63: 	if accessToken != "" {
64: 		token, err := object.GetTokenByAccessToken(accessToken)
65: 		if err != nil {
66: 			responseError(ctx, err.Error())
67: 			return
68: 		}
69: 
70: 		// an ID-JAG is a grant to be redeemed at another authorization server, not an access token
71: 		if token == nil || token.TokenType == "ID-JAG" {
72: 			responseInvalidToken(ctx, nil, "invalid_token", "Access token doesn't exist in database")
73: 			return
74: 		}
75: 
76: 		isExpired, expireTime := util.IsTokenExpired(token.CreatedTime, token.ExpiresIn)
77: 		if isExpired {
78: 			responseInvalidToken(ctx, token, "invalid_token", fmt.Sprintf("Access token has expired, expireTime = %s", expireTime))
79: 			return
80: 		}
81: 
82: 		// The token's user may have been forbidden or deleted after the token was issued
83: 		isUserActive, err := token.IsUserActive()
84: 		if err != nil {
85: 			responseError(ctx, err.Error())
86: 			return
87: 		}
88: 		if !isUserActive {
89: 			responseInvalidToken(ctx, token, "invalid_token", "The user is forbidden to sign in, please contact the administrator")
90: 			return
91: 		}
92: 
93: 		// Validate DPoP proof for DPoP-bound tokens (RFC 9449).
94: 		if token.TokenType == "DPoP" {
95: 			dpopProof := ctx.Request.Header.Get("DPoP")
96: 			if dpopProof == "" {
97: 				responseInvalidToken(ctx, token, "invalid_dpop_proof", "DPoP proof header required for DPoP-bound access token")
98: 				return
99: 			}
100: 			htu := object.GetDPoPHtu(ctx.Request.Host, ctx.Request.URL.Path)
101: 			jkt, dpopErr := object.ValidateDPoPProof(dpopProof, ctx.Request.Method, htu, accessToken)
102: 			if dpopErr != nil {
103: 				responseInvalidToken(ctx, token, "invalid_dpop_proof", fmt.Sprintf("DPoP proof validation failed: %s", dpopErr.Error()))
104: 				return
105: 			}
106: 			if jkt != token.DPoPJkt {
107: 				responseInvalidToken(ctx, token, "invalid_token", "DPoP proof key binding mismatch")
108: 				return
109: 			}
110: 		}
111: 
112: 		application, err := object.GetApplicationByUserId(fmt.Sprintf("app/%s", token.Application))
113: 		if err != nil {
114: 			responseError(ctx, err.Error())
115: 			return
116: 		}
117: 		if application == nil {
118: 			responseError(ctx, fmt.Sprintf("No application is found for userId: app/%s", token.Application))
119: 			return
120: 		}
121: 
122: 		var userId string
123: 		if token.GrantType == "client_credentials" {
124: 			userId = object.GetAppUserId(application)
125: 		} else {
126: 			userId = util.GetId(token.Organization, token.User)
127: 		}
128: 		setSessionSigninToken(ctx, userId, token)
129: 		setSessionUser(ctx, userId)
130: 		setSessionOidc(ctx, token.Scope, application.ClientId)
131: 		return
132: 	}
133: 
134: 	err := clearSessionOfRevokedToken(ctx)
135: 	if err != nil {
136: 		responseError(ctx, err.Error())
137: 		return
138: 	}
139: 
140: 	// "/page?clientId=123&clientSecret=456"
141: 	userId, err := getUsernameByClientIdSecret(ctx)
142: 	if err != nil {
```
