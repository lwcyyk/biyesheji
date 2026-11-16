# R13 key source excerpts (fixed text; no module execution)

## S01: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\storage.py
SHA-256: 2d17cf95d7d724d8debbeb47c2df28cfd537aa696bde47edb98908170a12de83

```text
   1 """SQLite authority. All approval mutations share one BEGIN IMMEDIATE order.
   2 
   3 The small prototype stores one encrypted application snapshot per commit. Its
   4 linear serialization cost is explicit; the SQL transaction and event are atomic.
   5 """
   6 
   7 import json
   8 import os
   9 from pathlib import Path
  10 import secrets
  11 import sqlite3
  12 import threading
  13 
  14 from cryptography.hazmat.primitives.ciphers.aead import AESGCM
  15 
  16 from .protocol import (EventLog, InvalidInput, canonical, digest, exact_fields,
  17                        identifier, normalized_request, write_json)
  18 from .materials import validate_material
  19 
  20 
  21 AAD = b"auth-lifecycle/online-state/schema-1"
  22 
  23 
  24 def request_projection(request):
  25     return {key: request[key] for key in
  26             ("rid", "digest", "origin", "phase", "attempt_id", "release_version")}
  27 
  28 
  29 def state_projection(state):
  30     approvals = []
  31     for grant in state["grants"].values():
  32         approvals.append({key: grant[key] for key in
  33                           ("grant_id", "caller", "task", "account", "audience",
  34                            "generation", "active", "limit", "reserved", "spent")})
  35     requests = [request_projection(req) for req in state["requests"].values()]
  36     obligations = [req["rid"] for req in requests
  37                    if req["phase"] in {"DISPATCHED_UNKNOWN", "QUARANTINED"}]
  38     for window in state.get("reconciliation_windows", {}).values():
  39         if window.get("receipt", {}).get("claim") != "CLOSED" and window["target_rid"] not in obligations:
  40             obligations.append(window["target_rid"])
  41     disposals = [{"disposal_op": key, **value} for key, value in state.get("disposals", {}).items()]
  42     return {"approvals": approvals, "requests": requests, "obligations": obligations,
  43             "disposals": disposals}
  44 
  45 
  46 class AuthorityStore:
  47     def __init__(self, directory, key_path, operation_limit=None):
  48         self.directory = Path(directory)
  49         self.directory.mkdir(parents=True, exist_ok=True)
  50         self.key_path = Path(key_path)
  51         self.lock = threading.RLock()
  52         self.metrics = EventLog(self.directory / "database_ops.jsonl")
  53         self.operation_limit = operation_limit
  54         self.operations = 0
  55         if self.metrics.path.exists():
  56             self.operations = len(self.metrics.path.read_bytes().splitlines())
  57         marker = self.directory / "initialized"
  58         if marker.exists() and not (self.directory / "authority.db").exists():
  59             raise ValueError("EXISTING_AUTHORITY_DATA_MISSING")
  60         self.connection = sqlite3.connect(self.directory / "authority.db",
  61                                           isolation_level=None, check_same_thread=False)
  62         self.connection.row_factory = sqlite3.Row
  63         journal_mode = self.execute("PRAGMA journal_mode=WAL").fetchone()[0]
  64         self.execute("PRAGMA synchronous=FULL")
  65         synchronous = self.execute("PRAGMA synchronous").fetchone()[0]
  66         self.execute("PRAGMA busy_timeout=5000")
  67         self.execute("PRAGMA wal_autocheckpoint=1000")
  68         if journal_mode != "wal" or synchronous != 2:
  69             raise ValueError("DURABILITY_CONFIGURATION_MISMATCH")
  70         schema_version = self.execute("PRAGMA user_version").fetchone()[0]
  71         if schema_version not in {0, 1, 2}:
  72             raise ValueError("UNSUPPORTED_SCHEMA_VERSION")
  73         if schema_version == 0:
  74             migration = (Path(__file__).with_name("migration.sql")).read_text()
  75             for statement in migration.split(";"):
  76                 if statement.strip():
  77                     self.execute(statement)
  78         if schema_version < 2:
  79             self.execute(Path(__file__).with_name("migration_2.sql").read_text())
  80         row = self.execute("SELECT version FROM authority_state WHERE id=1").fetchone()
  81         if row is None:
  82             if marker.exists():
  83                 raise ValueError("EXISTING_AUTHORITY_STATE_MISSING")
  84             state = {"grants": {}, "requests": {}, "grant_ops": {}, "revoke_ops": {}}
  85             self.execute("INSERT INTO authority_state VALUES(1,0,?)", (self.encrypt(state),))
  86         marker.touch(exist_ok=True)
  87         write_json(self.directory / "storage_configuration.json", {
  88             "sqlite_version": sqlite3.sqlite_version, "journal_mode": journal_mode,
  89             "synchronous": synchronous, "busy_timeout_ms": 5000,
  90             "wal_autocheckpoint_pages": 1000, "mutation_transaction": "BEGIN IMMEDIATE",
  91             "application_snapshot": "single AES-GCM encrypted row", "schema_version": 2})
  92 
  93     def execute(self, statement, parameters=()):
  94         if self.operation_limit is not None and self.operations >= self.operation_limit:
  95             raise RuntimeError("DATABASE_OPERATION_BUDGET")
  96         self.operations += 1
  97         kind = statement.strip().split()[0].upper()
  98         size = sum(len(x) if isinstance(x, (bytes, str)) else 8 for x in parameters)
  99         self.metrics.emit("sqlite_statement", number=self.operations, kind=kind,
 100                           bound_value_bytes=size)
 101         return self.connection.execute(statement, parameters)
 102 
 103     def cipher(self):
 104         # Reloading the external key makes a missing recovery key fail closed.
 105         key = self.key_path.read_bytes()
 106         if len(key) != 32:
 107             raise ValueError("KEY_UNAVAILABLE")
 108         return AESGCM(key)
 109 
 110     def encrypt(self, state):
 111         nonce = os.urandom(12)
 112         return nonce + self.cipher().encrypt(nonce, canonical(state), AAD)
 113 
 114     def read_state(self):
 115         row = self.execute("SELECT version,ciphertext FROM authority_state WHERE id=1").fetchone()
 116         if row is None:
 117             raise ValueError("STATE_UNAVAILABLE")
 118         raw = bytes(row["ciphertext"])
 119         state = json.loads(self.cipher().decrypt(raw[:12], raw[12:], AAD))
 120         return row["version"], state
 121 
 122     def call(self, operation, payload):
 123         if operation not in {"grant", "admit", "release", "record", "revoke", "recover",
 124                              "prepare_disposal", "record_disposal"}:
 125             if operation not in {"begin_reconciliation", "reconciliation_context", "save_reconciliation"}:
 126                 return {"status": "REJECTED", "reason": "INVALID_OPERATION"}
 127         with self.lock:
 128             try:
 129                 if operation == "recover":
 130                     if self.operation_limit is not None and self.operations >= self.operation_limit:
 131                         return {"status": "INCONCLUSIVE", "reason": "DATABASE_OPERATION_BUDGET"}
 132                     version, state = self.read_state()
 133                     return {"status": "RECOVERED", "version": version, **state_projection(state)}
 134                 if self.operation_limit is not None and self.operations + 6 > self.operation_limit:
 135                     return {"status": "INCONCLUSIVE", "reason": "DATABASE_OPERATION_BUDGET"}
 136                 self.execute("BEGIN IMMEDIATE")
 137                 version, state = self.read_state()
 138                 result = getattr(self, operation)(state, payload, version + 1)
 139                 public = {key: result[key] for key in
 140                           ("status", "reason", "rid", "grant_id", "phase", "send") if key in result}
 141                 event = {"result": public, "state": state_projection(state),
 142                          "logical_state_bytes": len(canonical(state))}
 143                 self.execute("UPDATE authority_state SET version=?,ciphertext=? WHERE id=1",
 144                              (version + 1, self.encrypt(state)))
 145                 self.execute("INSERT INTO authority_events VALUES(?,?,?)",
 146                              (version + 1, operation, canonical(event).decode()))
 147                 self.execute("COMMIT")
 148                 return {**result, "version": version + 1}
 149             except InvalidInput:
 150                 if self.connection.in_transaction:
 151                     self.execute("ROLLBACK")
 152                 return {"status": "REJECTED", "reason": "INVALID_INPUT"}
 153             except Exception:
 154                 if self.connection.in_transaction:
 155                     # A budget exhaustion must still release the DB transaction.
 156                     self.connection.rollback()
 157                     self.operations += 1
 158                     self.metrics.emit("sqlite_rollback_cleanup", kind="ROLLBACK")
 159                 return {"status": "UNKNOWN", "reason": "AUTHORITY_STATE_UNAVAILABLE"}
 160 
 161     def grant(self, state, payload, version):
 162         fields = ("approval_op", "caller", "task", "account", "audience",
 163                   "generation", "operations", "budget", "material")
 164         exact_fields(payload, fields)
 165         for key in fields:
 166             if key not in {"operations", "budget", "material"}:
 167                 identifier(payload[key])
 168         if (type(payload["budget"]) is not int or not 0 <= payload["budget"] <= 1000000
 169                 or not isinstance(payload["operations"], list) or not payload["operations"]
 170                 or len(payload["operations"]) != len(set(payload["operations"]))):
 171             raise InvalidInput("INVALID_APPROVAL")
 172         for operation in payload["operations"]:
 173             identifier(operation)
 174         validate_material(payload["material"], payload["account"], payload["audience"])
 175         if state.get("reconciliation_windows", {}).get(payload["account"], {}).get("active"):
 176             return {"status": "REJECTED", "reason": "RECONCILIATION_CREATION_PAUSED"}
 177         fingerprint = digest(payload)
 178         old = state["grant_ops"].get(payload["approval_op"])
 179         if old:
 180             if old["digest"] != fingerprint:
 181                 return {"status": "CONFLICT", "reason": "APPROVAL_OPERATION_CONFLICT"}
 182             grant = state["grants"][old["grant_id"]]
 183             return {"status": "GRANTED", "grant_id": grant["grant_id"], "handle": grant["handle"]}
 184         for grant in state["grants"].values():
 185             scope = ("caller", "task", "account", "audience", "generation")
 186             if all(grant[key] == payload[key] for key in scope):
 187                 return {"status": "CONFLICT", "reason": "GENERATION_ALREADY_EXISTS"}
 188         grant_id = "grant_" + secrets.token_hex(12)
 189         handle = "handle_" + secrets.token_hex(24)
 190         state["grants"][grant_id] = {
 191             **{key: payload[key] for key in ("caller", "task", "account", "audience", "generation", "operations", "material")},
 192             "grant_id": grant_id, "handle": handle, "active": True,
 193             "limit": payload["budget"], "reserved": 0, "spent": 0}
 194         state["grant_ops"][payload["approval_op"]] = {"digest": fingerprint, "grant_id": grant_id}
 195         return {"status": "GRANTED", "grant_id": grant_id, "handle": handle}
 196 
 197     def admit(self, state, payload, version):
 198         exact_fields(payload, ("caller", "request"))
 199         caller = identifier(payload["caller"])
 200         request = normalized_request(payload["request"])
 201         fingerprint = digest({"caller": caller, "request": request})
 202         existing = state["requests"].get(request["rid"])
 203         if existing:
 204             if existing["digest"] != fingerprint:
 205                 return {"status": "CONFLICT", "reason": "RID_BODY_CONFLICT"}
 206             return {"status": "DUPLICATE", **request_projection(existing)}
 207         grant = next((g for g in state["grants"].values() if g["handle"] == request["handle"]), None)
 208         if grant is None or grant["caller"] != caller:
 209             return {"status": "REJECTED", "reason": "BINDING_MISMATCH"}
 210         if any(grant[key] != request[key] for key in ("task", "account", "audience", "generation")):
 211             return {"status": "REJECTED", "reason": "BINDING_MISMATCH"}
 212         if not grant["active"] or request["operation"] not in grant["operations"]:
 213             return {"status": "REJECTED", "reason": "APPROVAL_INACTIVE_OR_OPERATION_DENIED"}
 214         if request["operation"] in {"issue", "refresh"} and state.get("reconciliation_windows", {}).get(request["account"], {}).get("active"):
 215             return {"status": "REJECTED", "reason": "RECONCILIATION_CREATION_PAUSED"}
 216         if grant["reserved"] + grant["spent"] >= grant["limit"]:
 217             return {"status": "REJECTED", "reason": "BUDGET_EXHAUSTED"}
 218         origin = {key: grant[key] for key in
 219                   ("grant_id", "caller", "task", "account", "audience", "generation")}
 220         saved = {"rid": request["rid"], "digest": fingerprint, "origin": origin,
 221                  "request": request, "phase": "QUEUED", "attempt_id": None,
 222                  "release_version": None, "result_digest": None, "result_material": None}
 223         state["requests"][request["rid"]] = saved
 224         grant["reserved"] += 1
 225         return {"status": "ADMITTED", **request_projection(saved)}
 226 
 227     def release(self, state, payload, version):
 228         exact_fields(payload, ("caller", "rid", "digest"))
 229         req = state["requests"].get(payload["rid"])
 230         if req is None or req["origin"]["caller"] != payload["caller"] or req["digest"] != payload["digest"]:
 231             return {"status": "REJECTED", "reason": "REQUEST_BINDING_MISMATCH", "send": False}
 232         grant = state["grants"][req["origin"]["grant_id"]]
 233         if req["phase"] != "QUEUED":
 234             return {"status": "RECORDED", "send": False, **request_projection(req)}
 235         if not grant["active"]:
 236             req["phase"] = "CANCELLED"
 237             grant["reserved"] -= 1
 238             return {"status": "REJECTED", "reason": "APPROVAL_REVOKED", "send": False}
 239         material = grant["material"]
 240         if req["request"]["operation"] in {"issue", "refresh"} and state.get("reconciliation_windows", {}).get(req["origin"]["account"], {}).get("active"):
 241             req["phase"] = "CANCELLED"
 242             grant["reserved"] -= 1
 243             return {"status": "REJECTED", "reason": "RECONCILIATION_CREATION_PAUSED", "send": False}
 244         if req["request"]["operation"] in {"refresh", "userinfo"}:
 245             source = state["requests"].get(req["request"]["payload"]["source_rid"])
 246             if (source is None or source["origin"] != req["origin"]
 247                     or source["phase"] != "RESULT_AVAILABLE" or not isinstance(source["result_material"], dict)):
 248                 req["phase"] = "CANCELLED"
 249                 grant["reserved"] -= 1
 250                 return {"status": "REJECTED", "reason": "SOURCE_MATERIAL_UNAVAILABLE", "send": False}
 251             material = source["result_material"]
 252         req["attempt_id"] = "attempt_" + secrets.token_hex(16)
 253         req["release_version"] = version
 254         req["phase"] = "DISPATCHED_UNKNOWN"
 255         grant["reserved"] -= 1
 256         grant["spent"] += 1
 257         return {"status": "RELEASED", "send": True, **request_projection(req),
 258                 "operation": req["request"]["operation"], "payload": req["request"]["payload"],
 259                 "material": material}
 260 
 261     def record(self, state, payload, version):
 262         fields = ("rid", "digest", "origin", "attempt_id", "release_version", "material", "outcome")
 263         exact_fields(payload, fields)
 264         req = state["requests"].get(payload["rid"])
 265         if req is None or any(req[key] != payload[key] for key in
 266                               ("digest", "origin", "attempt_id", "release_version")):
 267             return {"status": "CONFLICT", "reason": "RESULT_SOURCE_CONFLICT"}
 268         if payload["outcome"] != "OK":
 269             raise InvalidInput("INVALID_RESULT")
 270         validate_material(payload["material"], req["origin"]["account"], req["origin"]["audience"])
 271         result_digest = digest(payload)
 272         if req["result_digest"]:
 273             if req["result_digest"] != result_digest:
 274                 return {"status": "CONFLICT", "reason": "RESULT_BODY_CONFLICT"}
 275             return {"status": "RESULT_DUPLICATE", **request_projection(req)}
 276         if req["phase"] != "DISPATCHED_UNKNOWN" or not req["attempt_id"]:
 277             return {"status": "REJECTED", "reason": "RESULT_WITHOUT_RELEASE"}
 278         grant = state["grants"][req["origin"]["grant_id"]]
 279         req["result_digest"] = result_digest
 280         req["result_material"] = payload["material"]
 281         req["phase"] = "RESULT_AVAILABLE" if grant["active"] else "QUARANTINED"
 282         return {"status": req["phase"], **request_projection(req)}
 283 
 284     def revoke(self, state, payload, version):
 285         exact_fields(payload, ("revoke_op", "grant_id"))
 286         identifier(payload["revoke_op"])
 287         identifier(payload["grant_id"])
 288         old = state["revoke_ops"].get(payload["revoke_op"])
 289         if old:
 290             if old["grant_id"] != payload["grant_id"]:
 291                 return {"status": "CONFLICT", "reason": "REVOKE_OPERATION_CONFLICT"}
 292             return old
 293         grant = state["grants"].get(payload["grant_id"])
 294         if grant is None:
 295             return {"status": "REJECTED", "reason": "UNKNOWN_GRANT"}
 296         grant["active"] = False
 297         for req in state["requests"].values():
 298             if req["origin"]["grant_id"] != grant["grant_id"]:
 299                 continue
 300             if req["phase"] == "QUEUED":
 301                 req["phase"] = "CANCELLED"
 302                 grant["reserved"] -= 1
 303             elif req["phase"] == "RESULT_AVAILABLE":
 304                 req["phase"] = "QUARANTINED"
 305         receipt = {"status": "LOCAL_REVOKE_COMMITTED", "grant_id": grant["grant_id"],
 306                    "commit_version": version}
 307         state["revoke_ops"][payload["revoke_op"]] = receipt
 308         return receipt
 309 
 310     def prepare_disposal(self, state, payload, version):
 311         exact_fields(payload, ("disposal_op", "rid"))
 312         identifier(payload["disposal_op"])
 313         identifier(payload["rid"])
 314         disposals = state.setdefault("disposals", {})
 315         existing = disposals.get(payload["disposal_op"])
 316         if existing:
 317             if existing["rid"] != payload["rid"]:
 318                 return {"status": "CONFLICT", "reason": "DISPOSAL_ID_CONFLICT"}
 319             return {"status": existing["phase"], "send": False}
 320         req = state["requests"].get(payload["rid"])
 321         if (req is None or req["phase"] != "QUARANTINED"
 322                 or not isinstance(req["result_material"], dict)):
 323             return {"status": "UNKNOWN", "reason": "NO_KNOWN_QUARANTINED_MATERIAL", "send": False}
 324         disposals[payload["disposal_op"]] = {"rid": req["rid"], "phase": "DISPOSAL_UNKNOWN",
 325                                              "origin": req["origin"], "release_version": version}
 326         return {"status": "DISPOSAL_RELEASED", "send": True, "material": req["result_material"],
 327                 "rid": req["rid"], "disposal_op": payload["disposal_op"], "origin": req["origin"]}
 328 
 329     def record_disposal(self, state, payload, version):
 330         exact_fields(payload, ("disposal_op", "rid", "http", "userinfo_http", "userinfo_accepted", "introspection_active"))
 331         item = state.get("disposals", {}).get(payload["disposal_op"])
 332         if item is None or item["rid"] != payload["rid"]:
 333             return {"status": "CONFLICT", "reason": "DISPOSAL_SOURCE_CONFLICT"}
 334         if type(payload["http"]) is not int:
 335             raise InvalidInput("INVALID_HTTP_STATUS")
 336         item["phase"] = "NATIVE_REVOKE_RESPONDED"
 337         item["http"] = payload["http"]
 338         item["observations"] = {key: payload[key] for key in ("userinfo_http", "userinfo_accepted", "introspection_active")}
 339         item["completed_version"] = version
 340         if payload["http"] == 200 and payload["userinfo_accepted"] is False and payload["introspection_active"] is False:
 341             item["phase"] = "KNOWN_UNIT_INACTIVE"
 342             state["requests"][item["rid"]]["phase"] = "DISPOSED"
 343         return {"status": item["phase"], "rid": item["rid"], "http": item["http"],
 344                 "scope": "named_native_material_response_only"}
 345 
 346     def begin_reconciliation(self, state, payload, version):
 347         exact_fields(payload, ("rid", "window_id"))
 348         identifier(payload["window_id"])
 349         req = state["requests"].get(payload["rid"])
 350         if req is None:
 351             return {"status": "UNKNOWN", "reason": "UNKNOWN_ATTEMPT"}
 352         account = req["origin"]["account"]
 353         windows = state.setdefault("reconciliation_windows", {})
 354         old = windows.get(account)
 355         if old:
 356             if old["window_id"] != payload["window_id"] or old["target_rid"] != payload["rid"]:
 357                 return {"status": "CONFLICT", "reason": "WINDOW_CONFLICT"}
 358             return {"status": "WINDOW_OPEN", "window": old}
 359         if req["phase"] != "DISPATCHED_UNKNOWN" or req["request"]["operation"] != "refresh":
 360             return {"status": "UNKNOWN", "reason": "TARGET_NOT_UNKNOWN_REFRESH"}
 361         grant = state["grants"][req["origin"]["grant_id"]]
 362         if grant["active"]:
 363             return {"status": "REJECTED", "reason": "WITHDRAW_A_FIRST"}
 364         unknowns = [r["rid"] for r in state["requests"].values() if r["origin"]["account"] == account
 365                     and r["phase"] == "DISPATCHED_UNKNOWN" and r["request"]["operation"] in {"issue", "refresh"}]
 366         windows[account] = {"window_id": payload["window_id"], "target_rid": req["rid"],
 367                             "unknown_creators_at_open": unknowns, "active": True, "opened_version": version}
 368         return {"status": "WINDOW_OPEN", "window": windows[account]}
 369 
 370     def reconciliation_context(self, state, payload, version):
 371         exact_fields(payload, ("rid", "window_id", "B_rid"))
 372         req = state["requests"][payload["rid"]]
 373         window = state.get("reconciliation_windows", {}).get(req["origin"]["account"])
 374         if not window or window["window_id"] != payload["window_id"]:
 375             return {"status": "UNKNOWN", "reason": "WINDOW_UNAVAILABLE"}
 376         a_rows = [r for r in state["requests"].values() if r["origin"]["grant_id"] == req["origin"]["grant_id"] and r["result_material"]]
 377         disposals = [d for d in state.get("disposals", {}).values() if d["rid"] in {r["rid"] for r in a_rows}]
 378         last_disposal = max((d.get("completed_version", 0) for d in disposals), default=0)
 379         b = state["requests"].get(payload["B_rid"])
 380         b_ok = bool(b and b["origin"]["account"] == req["origin"]["account"] and b["origin"]["grant_id"] != req["origin"]["grant_id"]
 381                     and b["request"]["operation"] == "userinfo" and b["phase"] == "RESULT_AVAILABLE"
 382                     and b["release_version"] > last_disposal and last_disposal > 0
 383                     and state["grants"][b["origin"]["grant_id"]]["active"])
 384         account_grants = [g for g in state["grants"].values() if g["account"] == req["origin"]["account"]]
 385         known_ids = sorted({r["result_material"]["derived"]["verified_claims"]["jti"]
 386             for r in state["requests"].values() if r["origin"]["account"] == req["origin"]["account"]
 387             and isinstance(r["result_material"], dict) and r["result_material"].get("kind") == "casdoor_oauth"
 388             and r["result_material"].get("derived", {}).get("verified_claims", {}).get("jti")})
 389         return {"status": "RECONCILIATION_CONTEXT", "window": window, "target": request_projection(req),
 390                 "A_revoked": not state["grants"][req["origin"]["grant_id"]]["active"],
 391                 "known_A_rids": [r["rid"] for r in a_rows],
 392                 "known_A_units_inactive": bool(a_rows) and all(r["phase"] == "DISPOSED" for r in a_rows),
 393                 "B_preserved_after_disposal": b_ok, "disposition_versions": [d.get("completed_version") for d in disposals],
 394                 "known_unit_ids": known_ids, "account_grant_count": len(account_grants),
 395                 "account_budget_total": sum(g["limit"] for g in account_grants)}
 396 
 397     def save_reconciliation(self, state, payload, version):
 398         exact_fields(payload, ("rid", "window_id", "receipt", "query_evidence", "B_rid"))
 399         req = state["requests"][payload["rid"]]
 400         window = state.get("reconciliation_windows", {}).get(req["origin"]["account"])
 401         if not window or window["window_id"] != payload["window_id"]:
 402             return {"status": "CONFLICT", "reason": "WINDOW_MISMATCH"}
 403         receipt = payload["receipt"]
 404         if receipt["claim"] == "CLOSED":
 405             context = self.reconciliation_context(state, {"rid": payload["rid"], "window_id": payload["window_id"], "B_rid": payload["B_rid"]}, version)
 406             if (req["phase"] != "DISPOSED" or not window["active"] or not context["known_A_units_inactive"]
 407                     or not context["B_preserved_after_disposal"] or not context["A_revoked"]
 408                     or window["unknown_creators_at_open"] != [payload["rid"]]
 409                     or receipt["target"]["attempt_id"] != req["attempt_id"]
 410                     or receipt["target"]["request_digest"] != req["digest"]):
 411                 return {"status": "UNKNOWN", "reason": "CLOSE_STATE_MISMATCH"}
 412         window["receipt"] = receipt
 413         window["query_evidence"] = payload["query_evidence"]
 414         if receipt["claim"] == "CLOSED":window["active"] = False
 415         return {"status": receipt["claim"], "receipt": receipt, "receipt_ref": digest(receipt)}
```

## S02: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\services.py
SHA-256: d8ea05120fc8559a95050e4c71a094eefb73e29d22e1de66494d8c8e1975993a

```text
   1 """Authenticated local authority, controller, and synthetic provider processes."""
   2 
   3 import base64
   4 import hmac
   5 from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
   6 import json
   7 import os
   8 from pathlib import Path
   9 import secrets
  10 import ssl
  11 import threading
  12 import time
  13 
  14 from cryptography.hazmat.primitives.ciphers.aead import AESGCM
  15 
  16 from .protocol import (Client, EventLog, InvalidInput, canonical, digest,
  17                        exact_fields, identifier, normalized_request, strict_json, write_json)
  18 from .storage import AuthorityStore
  19 from .reconciliation import make_receipt
  20 
  21 
  22 class SingleActive:
  23     """OS-held lock outside the rollback cache. A process exit releases it."""
  24     def __init__(self, path):
  25         self.stream = open(path, "a+b")
  26         try:
  27             if os.fstat(self.stream.fileno()).st_size == 0:
  28                 self.stream.write(b"0")
  29                 self.stream.flush()
  30             self.stream.seek(0)
  31             if os.name == "nt":
  32                 import msvcrt
  33                 msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
  34             else:
  35                 import fcntl
  36                 fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
  37         except OSError:
  38             self.stream.close()
  39             raise
  40 
  41 
  42 class Controller:
  43     def __init__(self, root, config, fault=None):
  44         self.root = Path(root)
  45         self.config = config
  46         self.active_lock = SingleActive(self.root / "secure" / "controller.lock")
  47         self.log = EventLog(self.root / "controller" / "events.jsonl")
  48         self.authority = Client(config["authority_url"], config["authority_token"],
  49                                 config["certificate"], self.log)
  50         self.provider = Client(config["provider_url"], config["provider_token"],
  51                                config["certificate"], self.log)
  52         self.boot = secrets.token_hex(8)
  53         self.fault = fault
  54         self.fault_used = False
  55         self.ready = False
  56         self.recover()
  57 
  58     def barrier(self, point):
  59         if point != self.fault or self.fault_used:
  60             return
  61         self.fault_used = True
  62         folder = self.root / "controller" / "barriers"
  63         path = folder / (self.boot + "_" + point + ".json")
  64         write_json(path, {"point": point, "pid": os.getpid(), "boot": self.boot})
  65         self.log.emit("barrier", point=point, boot=self.boot)
  66         release = path.with_suffix(".release")
  67         while not release.exists():
  68             time.sleep(0.01)
  69 
  70     def recover(self):
  71         result = self.authority.call("recover", {})
  72         self.ready = result.get("status") == "RECOVERED"
  73         if self.ready:
  74             write_json(self.root / "cache" / "view.json", {
  75                 "authoritative_version": result["version"], "boot": self.boot,
  76                 "approval_count": len(result["approvals"]), "display_only": True})
  77         self.log.emit("recovery", status=result.get("status"),
  78                       version=result.get("version"), boot=self.boot)
  79         return result
  80 
  81     def call(self, operation, payload, identity):
  82         if operation == "recover":
  83             return self.recover()
  84         if not self.ready and self.recover().get("status") != "RECOVERED":
  85             return {"status": "UNKNOWN", "reason": "RECOVERY_INCOMPLETE"}
  86         if operation == "grant":
  87             return self.authority.call("grant", payload)
  88         if operation == "revoke":
  89             self.barrier("before_revoke")
  90             result = self.authority.call("revoke", payload)
  91             if result.get("status") == "LOCAL_REVOKE_COMMITTED":
  92                 self.barrier("after_revoke_commit")
  93             return result
  94         if operation == "status":
  95             result = self.authority.call("recover", {})
  96             if result.get("status") != "RECOVERED" or identity == "user":
  97                 return result
  98             result["approvals"] = [x for x in result["approvals"] if x["caller"] == identity]
  99             result["requests"] = [x for x in result["requests"] if x["origin"]["caller"] == identity]
 100             result["obligations"] = [x["rid"] for x in result["requests"]
 101                                      if x["phase"] in {"DISPATCHED_UNKNOWN", "QUARANTINED"}]
 102             return result
 103         if operation == "dispose":
 104             released = self.authority.call("prepare_disposal", payload)
 105             if not released.get("send"):
 106                 return {key: value for key, value in released.items() if key != "material"}
 107             response = self.provider.call("dispose", released)
 108             if response.get("status") != "DISPOSAL_RESPONSE":
 109                 return {"status": "UNKNOWN", "reason": "NATIVE_DISPOSAL_UNCERTAIN"}
 110             return self.authority.call("record_disposal", {
 111                 "disposal_op": payload["disposal_op"], "rid": payload["rid"], "http": response["http"],
 112                 "userinfo_http": response["userinfo_http"], "userinfo_accepted": response["userinfo_accepted"],
 113                 "introspection_active": response["introspection_active"]})
 114         if operation == "begin_reconciliation":
 115             return self.authority.call("begin_reconciliation", payload)
 116         if operation == "reconcile":
 117             return self.reconcile(payload)
 118         if operation == "deliver":
 119             exact_fields(payload, ("rid",))
 120             identifier(payload["rid"])
 121             known = self.authority.call("recover", {})
 122             if known.get("status") != "RECOVERED":
 123                 return known
 124             req = next((x for x in known["requests"] if x["rid"] == payload["rid"]), None)
 125             if req is None or req["attempt_id"] is None:
 126                 return {"status": "UNKNOWN", "reason": "NO_KNOWN_ATTEMPT"}
 127             lookup = {key: req[key] for key in
 128                       ("rid", "digest", "origin", "attempt_id", "release_version")}
 129             result = self.provider.call("lookup", lookup)
 130             return self.record_result(result)
 131         if operation != "call":
 132             return {"status": "REJECTED", "reason": "INVALID_OPERATION"}
 133         request = normalized_request(payload)
 134         self.barrier("before_admit")
 135         admitted = self.authority.call("admit", {"caller": identity, "request": request})
 136         if admitted.get("status") not in {"ADMITTED", "DUPLICATE"}:
 137             return admitted
 138         self.barrier("after_admit")
 139         if admitted["phase"] != "QUEUED":
 140             return admitted
 141         released = self.authority.call("release", {
 142             "caller": identity, "rid": request["rid"], "digest": admitted["digest"]})
 143         if not released.get("send"):
 144             return released
 145         self.barrier("after_release")
 146         provider_request = {key: released[key] for key in
 147                             ("rid", "digest", "origin", "attempt_id", "release_version",
 148                              "material", "operation", "payload")}
 149         result = self.provider.call("perform", provider_request)
 150         self.barrier("after_effect")
 151         return self.record_result(result)
 152 
 153     def record_result(self, result):
 154         if result.get("status") != "PROVIDER_RESULT":
 155             return {"status": "UNKNOWN", "reason": "EXTERNAL_RESULT_UNCERTAIN"}
 156         fields = ("rid", "digest", "origin", "attempt_id", "release_version", "material", "outcome")
 157         if not all(key in result for key in fields):
 158             return {"status": "UNKNOWN", "reason": "INVALID_PROVIDER_RESULT"}
 159         envelope = {key: result[key] for key in fields}
 160         return self.authority.call("record", envelope)
 161 
 162     def reconcile(self, payload):
 163         exact_fields(payload, ("rid", "window_id", "step", "B_rid"))
 164         context = self.authority.call("reconciliation_context", {
 165             "rid": payload["rid"], "window_id": payload["window_id"], "B_rid": payload["B_rid"]})
 166         if context.get("status") != "RECONCILIATION_CONTEXT":return context
 167         window = context["window"]
 168         if window.get("receipt", {}).get("claim") == "CLOSED":
 169             return {"status": "CLOSED", "receipt": window["receipt"]}
 170         query = window.get("query_evidence", {})
 171         if payload["step"] == "discover":
 172             target = context["target"]
 173             request = {key: target[key] for key in ("rid", "digest", "origin", "attempt_id", "release_version")}
 174             if self.config.get("reconciliation_model", {}).get("evidence_origin") == "AUTHORIZED_SCOPE_ENUMERATION":
 175                 request["enumeration_context"] = {"known_unit_ids": context["known_unit_ids"],
 176                     "account_grant_count": context["account_grant_count"], "account_budget_total": context["account_budget_total"],
 177                     "unknown_creators": window["unknown_creators_at_open"], "context_version": context["version"]}
 178             response = self.provider.call("reconcile_query", request)
 179             if response.get("status") == "SAFETY_FAILURE":
 180                 return response
 181             query = response.get("evidence", {})
 182             if (response.get("status") == "RECONCILED_MATERIAL" and window["unknown_creators_at_open"] == [payload["rid"]]
 183                     and query.get("actual_sends") == 1 and query.get("origin_bound") is True):
 184                 recorded = self.authority.call("record", response["result"])
 185                 if recorded.get("status") not in {"QUARANTINED", "RESULT_DUPLICATE"}:
 186                     return recorded
 187                 context = self.authority.call("reconciliation_context", {
 188                     "rid": payload["rid"], "window_id": payload["window_id"], "B_rid": payload["B_rid"]})
 189                 for rid in context["known_A_rids"]:
 190                     self.call("dispose", {"disposal_op": "reconcile_" + rid, "rid": rid}, "user")
 191                 context = self.authority.call("reconciliation_context", {
 192                     "rid": payload["rid"], "window_id": payload["window_id"], "B_rid": payload["B_rid"]})
 193         elif payload["step"] != "finish":
 194             return {"status": "REJECTED", "reason": "RECONCILIATION_STEP"}
 195         window = context["window"]
 196         model = self.config.get("reconciliation_model", {})
 197         facts = {key: query.get(key, False) for key in ("exact_authorized_read", "record_found", "origin_bound")}
 198         facts.update(single_unknown_creator=window["unknown_creators_at_open"] == [payload["rid"]],
 199             creation_paused=window["active"], A_revoked=context["A_revoked"],
 200             external_writers_excluded=model.get("external_writers_excluded") is True,
 201             future_retry_excluded=model.get("single_open_no_retry") is True,
 202             known_A_units_inactive=context["known_A_units_inactive"],
 203             B_preserved_after_disposal=context["B_preserved_after_disposal"],
 204             actual_sends=query.get("actual_sends", 0), per_send_effect_bound=model.get("per_send_effect_bound"),
 205             observed_distinct_effects=query.get("observed_distinct_effects", 0))
 206         target = context["target"]
 207         binding = {"rid": target["rid"], "attempt_id": target["attempt_id"], "request_digest": target["digest"], **target["origin"]}
 208         safe_context = {key: context[key] for key in ("target", "A_revoked", "known_A_rids", "known_A_units_inactive", "B_preserved_after_disposal", "disposition_versions")}
 209         safe_context["window"] = {key: window[key] for key in ("window_id", "target_rid", "active", "unknown_creators_at_open", "opened_version")}
 210         packet = {"context": safe_context, "query": query, "model": model}
 211         evidence = {"query_ref": query.get("query_ref"), "identifier_receipt_ref": query.get("identifier_receipt_ref"),
 212                     "source_lemma_ref": model.get("source_lemma_ref"), "packet": packet, "packet_ref": digest(packet),
 213                     "origin": model.get("evidence_origin", "IDENTIFIER_POINT_READ"),
 214                     "enumeration_ref": query.get("enumeration_ref"), "authorized_scope_ref": query.get("authorized_scope_ref")}
 215         receipt = make_receipt(binding, facts, evidence)
 216         return self.authority.call("save_reconciliation", {"rid": payload["rid"], "window_id": payload["window_id"],
 217                                    "receipt": receipt, "query_evidence": query, "B_rid": payload["B_rid"]})
 218 
 219 
 220 class FakeProvider:
 221     def __init__(self, root, config):
 222         self.root = Path(root)
 223         self.key = (self.root / "secure" / "provider.key").read_bytes()
 224         self.results_path = self.root / "provider" / "encrypted_results.jsonl"
 225         self.results_path.parent.mkdir(parents=True, exist_ok=True)
 226         self.truth = EventLog(self.root / "provider" / "truth.jsonl")
 227         self.lock = threading.Lock()
 228         self.hold = False
 229         self.results = {}
 230         if self.results_path.exists():
 231             for line in self.results_path.read_bytes().splitlines():
 232                 raw = base64.b64decode(line)
 233                 result = json.loads(AESGCM(self.key).decrypt(raw[:12], raw[12:], b"fake-provider-v1"))
 234                 self.results[result["attempt_id"]] = result
 235 
 236     def call(self, operation, payload, identity):
 237         with self.lock:
 238             if operation == "hold":
 239                 exact_fields(payload, ("enabled",))
 240                 if type(payload["enabled"]) is not bool:
 241                     raise InvalidInput("INVALID_HOLD")
 242                 self.hold = payload["enabled"]
 243                 return {"status": "CONFIGURED"}
 244             if operation == "lookup":
 245                 exact_fields(payload, ("rid", "digest", "origin", "attempt_id", "release_version"))
 246                 result = self.results.get(payload["attempt_id"])
 247                 if result is None:
 248                     return {"status": "UNKNOWN", "reason": "NO_RESULT_EVIDENCE"}
 249                 if any(result[key] != payload[key] for key in payload):
 250                     return {"status": "CONFLICT", "reason": "LOOKUP_BINDING_CONFLICT"}
 251                 return {"status": "PROVIDER_RESULT", **result}
 252             if operation != "perform":
 253                 return {"status": "REJECTED", "reason": "INVALID_OPERATION"}
 254             fields = ("rid", "digest", "origin", "attempt_id", "release_version", "material", "operation", "payload")
 255             exact_fields(payload, fields)
 256             if not isinstance(payload["material"], str) or not payload["material"].startswith("synthetic_"):
 257                 return {"status": "REJECTED", "reason": "SYNTHETIC_MATERIAL_REQUIRED"}
 258             # Each perform invocation records an effect, including accidental retries.
 259             result = {key: payload[key] for key in
 260                       ("rid", "digest", "origin", "attempt_id", "release_version")}
 261             result.update(material="synthetic_result_" + secrets.token_hex(24), outcome="OK")
 262             nonce = os.urandom(12)
 263             sealed = nonce + AESGCM(self.key).encrypt(nonce, canonical(result), b"fake-provider-v1")
 264             with self.results_path.open("ab") as stream:
 265                 stream.write(base64.b64encode(sealed) + b"\n")
 266                 stream.flush()
 267                 os.fsync(stream.fileno())
 268             self.results[payload["attempt_id"]] = result
 269             self.truth.emit("effect", **{key: result[key] for key in
 270                                         ("rid", "digest", "origin", "attempt_id", "release_version")})
 271             if self.hold:
 272                 return {"status": "PENDING"}
 273             return {"status": "PROVIDER_RESULT", **result,
 274                     "untrusted_extra": "synthetic_debug_secret_do_not_export"}
 275 
 276 
 277 def serve(role, root, fault=None):
 278     root = Path(root)
 279     config = json.loads((root / "secure" / (role + ".json")).read_text())
 280     log = EventLog(root / role / "transport.jsonl")
 281     if role == "authority":
 282         implementation = AuthorityStore(root / "authority", root / "secure" / "authority.key",
 283                                         config.get("operation_limit"))
 284     elif role == "provider":
 285         if config.get("native_profile"):
 286             from .native_provider import CasdoorProvider
 287             implementation = CasdoorProvider(root, config)
 288         else:
 289             implementation = FakeProvider(root, config)
 290     else:
 291         implementation = Controller(root, config, fault)
 292 
 293     class Handler(BaseHTTPRequestHandler):
 294         def log_message(self, *args):
 295             pass
 296 
 297         def do_POST(self):
 298             started = time.monotonic_ns()
 299             request_bytes = 0
 300             operation = self.path.removeprefix("/")
 301             identity = None
 302             supplied = self.headers.get("Authorization", "")
 303             for name, token in config["identities"].items():
 304                 if hmac.compare_digest(supplied, "Bearer " + token):
 305                     identity = name
 306             allowed = config["permissions"].get(identity, [])
 307             try:
 308                 if operation not in allowed:
 309                     result = {"status": "REJECTED", "reason": "IDENTITY_OR_OPERATION_DENIED"}
 310                 else:
 311                     length = int(self.headers.get("Content-Length", "0"))
 312                     if not 0 < length <= 65536:
 313                         raise InvalidInput("BODY_SIZE")
 314                     raw = self.rfile.read(length)
 315                     request_bytes = len(raw)
 316                     payload = strict_json(raw)
 317                     if role == "authority":
 318                         result = implementation.call(operation, payload)
 319                     else:
 320                         result = implementation.call(operation, payload, identity)
 321             except (ValueError, TypeError, KeyError, InvalidInput):
 322                 result = {"status": "REJECTED", "reason": "INVALID_INPUT"}
 323             except Exception:
 324                 result = {"status": "UNKNOWN", "reason": "SERVICE_UNAVAILABLE"}
 325             response = canonical(result)
 326             # The operation logged is selected from the configured whitelist.
 327             log.emit("request", operation=operation if operation in allowed else "denied",
 328                      identity=identity, request_json_bytes=request_bytes,
 329                      response_json_bytes=len(response), status=result.get("status"),
 330                      elapsed_ns=time.monotonic_ns() - started)
 331             try:
 332                 self.send_response(200)
 333                 self.send_header("Content-Type", "application/json")
 334                 self.send_header("Content-Length", str(len(response)))
 335                 self.end_headers()
 336                 self.wfile.write(response)
 337             except (OSError, ssl.SSLError):
 338                 pass
 339 
 340     server = ThreadingHTTPServer(("127.0.0.1", config["port"]), Handler)
 341     server.daemon_threads = True
 342     tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
 343     tls.minimum_version = ssl.TLSVersion.TLSv1_2
 344     tls.load_cert_chain(config["certificate"], config["tls_key"])
 345     server.socket = tls.wrap_socket(server.socket, server_side=True)
 346     write_json(root / "control" / (role + "_ready.json"),
 347                {"role": role, "pid": os.getpid(), "port": config["port"],
 348                 "boot": getattr(implementation, "boot", None)})
 349     server.serve_forever(poll_interval=0.05)
```

## S03: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\protocol.py
SHA-256: 1d74afd2d1c252e371fe0d2b619120e588eab27bb15072e27168b812253fed79

```text
   1 """Strict JSON, pinned loopback TLS, and secret-free event projections."""
   2 
   3 import hashlib
   4 import json
   5 import os
   6 from pathlib import Path
   7 import re
   8 import ssl
   9 import threading
  10 import time
  11 import urllib.error
  12 import urllib.request
  13 
  14 
  15 class InvalidInput(ValueError):
  16     pass
  17 
  18 
  19 def canonical(value):
  20     return json.dumps(value, sort_keys=True, separators=(",", ":"),
  21                       ensure_ascii=True, allow_nan=False).encode("utf-8")
  22 
  23 
  24 def digest(value):
  25     return hashlib.sha256(canonical(value)).hexdigest()
  26 
  27 
  28 def strict_json(raw):
  29     def pairs(items):
  30         result = {}
  31         for key, value in items:
  32             if key in result:
  33                 raise InvalidInput("DUPLICATE_JSON_KEY")
  34             result[key] = value
  35         return result
  36 
  37     def invalid_constant(value):
  38         raise InvalidInput("NONFINITE_JSON")
  39 
  40     return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
  41 
  42 
  43 def identifier(value):
  44     if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", value):
  45         raise InvalidInput("INVALID_IDENTIFIER")
  46     return value
  47 
  48 
  49 def exact_fields(value, fields):
  50     if not isinstance(value, dict) or set(value) != set(fields):
  51         raise InvalidInput("INVALID_FIELDS")
  52 
  53 
  54 def normalized_request(value):
  55     fields = ("rid", "handle", "task", "account", "audience", "generation",
  56               "operation", "payload")
  57     exact_fields(value, fields)
  58     result = {key: identifier(value[key]) for key in fields if key != "payload"}
  59     if result["operation"] == "issue":
  60         exact_fields(value["payload"], ())
  61         result["payload"] = {}
  62     elif result["operation"] in {"refresh", "userinfo"}:
  63         exact_fields(value["payload"], ("source_rid",))
  64         result["payload"] = {"source_rid": identifier(value["payload"]["source_rid"])}
  65     else:
  66         exact_fields(value["payload"], ("value",))
  67         number = value["payload"]["value"]
  68         if type(number) is not int or not -1000000 <= number <= 1000000:
  69             raise InvalidInput("INVALID_PAYLOAD")
  70         result["payload"] = {"value": number}
  71     return result
  72 
  73 
  74 def write_json(path, value):
  75     path = Path(path)
  76     path.parent.mkdir(parents=True, exist_ok=True)
  77     temporary = path.with_name(path.name + ".tmp")
  78     with temporary.open("wb") as stream:
  79         stream.write(canonical(value))
  80         stream.flush()
  81         os.fsync(stream.fileno())
  82     os.replace(temporary, path)
  83 
  84 
  85 class EventLog:
  86     def __init__(self, path):
  87         self.path = Path(path)
  88         self.path.parent.mkdir(parents=True, exist_ok=True)
  89         self.lock = threading.Lock()
  90 
  91     def emit(self, event, **fields):
  92         # Callers supply explicit projections; request bodies and exceptions stay out.
  93         row = {"event": event, "pid": os.getpid(), "monotonic_ns": time.monotonic_ns(), **fields}
  94         with self.lock, self.path.open("ab") as stream:
  95             stream.write(canonical(row) + b"\n")
  96             stream.flush()
  97             os.fsync(stream.fileno())
  98         return row
  99 
 100 
 101 class NoRedirect(urllib.request.HTTPRedirectHandler):
 102     def redirect_request(self, req, fp, code, msg, headers, newurl):
 103         return None
 104 
 105 
 106 class Client:
 107     def __init__(self, url, token, certificate, log=None, timeout=3):
 108         if not re.fullmatch(r"https://127\.0\.0\.1:[0-9]+", url):
 109             raise InvalidInput("LOOPBACK_TLS_REQUIRED")
 110         port = int(url.rsplit(":", 1)[1])
 111         if port in {18080, 18081, 8080}:
 112             raise InvalidInput("NATIVE_ENDPOINT_FORBIDDEN")
 113         self.url = url
 114         self.token = token
 115         self.log = log
 116         self.timeout = timeout
 117         context = ssl.create_default_context(cafile=str(certificate))
 118         self.opener = urllib.request.build_opener(
 119             urllib.request.ProxyHandler({}), NoRedirect(),
 120             urllib.request.HTTPSHandler(context=context))
 121 
 122     def call(self, operation, payload):
 123         identifier(operation)
 124         body = canonical(payload)
 125         request = urllib.request.Request(
 126             self.url + "/" + operation, data=body,
 127             headers={"Authorization": "Bearer " + self.token,
 128                      "Content-Type": "application/json"}, method="POST")
 129         started = time.monotonic_ns()
 130         try:
 131             with self.opener.open(request, timeout=self.timeout) as response:
 132                 raw = response.read(1024 * 1024)
 133                 result = strict_json(raw)
 134         except (urllib.error.URLError, TimeoutError, OSError):
 135             raw = b""
 136             result = {"status": "UNKNOWN", "reason": "TRANSPORT_UNAVAILABLE"}
 137         except (ValueError, InvalidInput):
 138             raw = b""
 139             result = {"status": "UNKNOWN", "reason": "INVALID_RESPONSE"}
 140         if self.log:
 141             self.log.emit("rpc", operation=operation, request_json_bytes=len(body),
 142                           response_json_bytes=len(raw), status=result.get("status"),
 143                           elapsed_ns=time.monotonic_ns() - started)
 144         return result
```

## S04: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\lab.py
SHA-256: ccf0c4ad6d21106fd1c0ef5aedcdad5b30bba49b2bf2f526ea69d79899409f26

```text
   1 """Isolated process fixture. Only synthetic credentials and loopback endpoints."""
   2 
   3 from concurrent.futures import ThreadPoolExecutor
   4 from datetime import datetime, timedelta, timezone
   5 import ipaddress
   6 import json
   7 import os
   8 from pathlib import Path
   9 import re
  10 import secrets
  11 import socket
  12 import subprocess
  13 import sys
  14 import time
  15 
  16 from cryptography import x509
  17 from cryptography.hazmat.primitives import hashes, serialization
  18 from cryptography.hazmat.primitives.asymmetric import rsa
  19 from cryptography.x509.oid import NameOID
  20 
  21 from .protocol import Client, EventLog, write_json
  22 
  23 
  24 def protect_directory(path):
  25     if os.name == "nt":
  26         output = subprocess.check_output(["whoami", "/user", "/fo", "csv", "/nh"])
  27         match = re.search(rb"S-\d+(?:-\d+)+", output)
  28         if match is None:
  29             raise RuntimeError("CURRENT_USER_SID_UNAVAILABLE")
  30         sid = match.group().decode("ascii")
  31         command = ["icacls", str(path), "/inheritance:r", "/grant:r",
  32                    "*" + sid + ":(OI)(CI)F", "/grant:r", "*S-1-5-18:(OI)(CI)F"]
  33         result = subprocess.run(command, capture_output=True)
  34         if result.returncode:
  35             raise RuntimeError("PRIVATE_DIRECTORY_ACL_FAILED")
  36         return {"mechanism": "Windows DACL", "allowed_sids": [sid, "S-1-5-18"]}
  37     os.chmod(path, 0o700)
  38     return {"mechanism": "POSIX", "mode": "0700"}
  39 
  40 
  41 def free_port():
  42     with socket.socket() as sock:
  43         sock.bind(("127.0.0.1", 0))
  44         return sock.getsockname()[1]
  45 
  46 
  47 def initialize(root, operation_limit=None):
  48     root = Path(root).resolve()
  49     root.mkdir(parents=True, exist_ok=False)
  50     secure = root / "secure"
  51     secure.mkdir()
  52     acl = protect_directory(secure)
  53     for directory in ("authority", "provider", "controller", "cache", "control", "runner", "scorer"):
  54         (root / directory).mkdir()
  55     private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
  56     name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "online-state-local-test")])
  57     now = datetime.now(timezone.utc)
  58     certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
  59                    .public_key(private_key.public_key()).serial_number(x509.random_serial_number())
  60                    .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=7))
  61                    .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), False)
  62                    .sign(private_key, hashes.SHA256()))
  63     cert_path = secure / "server.crt"
  64     key_path = secure / "server.key"
  65     cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
  66     key_path.write_bytes(private_key.private_bytes(serialization.Encoding.PEM,
  67                                                   serialization.PrivateFormat.PKCS8,
  68                                                   serialization.NoEncryption()))
  69     (secure / "authority.key").write_bytes(os.urandom(32))
  70     (secure / "provider.key").write_bytes(os.urandom(32))
  71     ports = {}
  72     while len(ports) < 3:
  73         port = free_port()
  74         if port not in ports.values() and port not in {18080, 18081, 8080}:
  75             ports[("authority", "provider", "controller")[len(ports)]] = port
  76     authority_token = secrets.token_urlsafe(32)
  77     provider_token = secrets.token_urlsafe(32)
  78     common = {"certificate": str(cert_path), "tls_key": str(key_path)}
  79     configs = {
  80         "authority": {**common, "port": ports["authority"], "operation_limit": operation_limit,
  81                       "identities": {"controller": authority_token},
  82                       "permissions": {"controller": ["grant", "admit", "release", "record", "revoke", "recover"]}},
  83         "provider": {**common, "port": ports["provider"],
  84                      "identities": {"adapter": provider_token, "fixture": secrets.token_urlsafe(32)},
  85                      "permissions": {"adapter": ["perform", "lookup"], "fixture": ["hold"]}},
  86         "controller": {**common, "port": ports["controller"],
  87                        "authority_url": "https://127.0.0.1:" + str(ports["authority"]),
  88                        "provider_url": "https://127.0.0.1:" + str(ports["provider"]),
  89                        "authority_token": authority_token, "provider_token": provider_token,
  90                        "identities": {name: secrets.token_urlsafe(32) for name in ("user", "agentA", "agentB")},
  91                        "permissions": {"user": ["grant", "revoke", "recover", "deliver", "status"],
  92                                        "agentA": ["call", "status"], "agentB": ["call", "status"]}}
  93     }
  94     for role, config in configs.items():
  95         write_json(secure / (role + ".json"), config)
  96     write_json(root / "control" / "environment.json", {
  97         "contract": "ONLINE_TRUSTED_STATE_V1", "ports": ports, "acl": acl,
  98         "operation_limit": operation_limit, "fault_domain": "controller process and cache/view.json",
  99         "independent_paths": ["authority", "provider", "secure"], "native_requests": 0,
 100         "identity_fixture": "Bearer capabilities provisioned outside agent input; trusted same-host test principal",
 101         "same_os_account_trust": "OS account and fixture are trusted; adversarial OS-user isolation untested"})
 102     return root
 103 
 104 
 105 class Laboratory:
 106     def __init__(self, root, operation_limit=None, create=True):
 107         self.root = initialize(root, operation_limit) if create else Path(root).resolve()
 108         self.processes = {}
 109         self.streams = []
 110         self.log = EventLog(self.root / "control" / "processes.jsonl")
 111         self.runner_log = EventLog(self.root / "runner" / "rpc.jsonl")
 112         self.executor = ThreadPoolExecutor(max_workers=12)
 113         self.configs = {role: json.loads((self.root / "secure" / (role + ".json")).read_text())
 114                         for role in ("authority", "provider", "controller")}
 115 
 116     def start(self, role, fault=None):
 117         if role in self.processes and self.processes[role].poll() is None:
 118             raise RuntimeError("PROCESS_ALREADY_RUNNING")
 119         ready = self.root / "control" / (role + "_ready.json")
 120         ready.unlink(missing_ok=True)
 121         env = dict(os.environ)
 122         env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])
 123         env["PYTHONDONTWRITEBYTECODE"] = "1"
 124         command = [sys.executable, "-B", "-m", "auth_lifecycle.online_state.cli", "serve",
 125                    "--root", str(self.root), "--role", role]
 126         if fault:
 127             command += ["--fault", fault]
 128         filename = role + "_" + secrets.token_hex(4) + ".stderr"
 129         stream = (self.root / "control" / filename).open("wb")
 130         self.streams.append(stream)
 131         flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
 132         process = subprocess.Popen(command, env=env, stdout=stream, stderr=stream, creationflags=flags)
 133         self.processes[role] = process
 134         deadline = time.monotonic() + 8
 135         while time.monotonic() < deadline:
 136             if process.poll() is not None:
 137                 raise RuntimeError("SERVICE_START_FAILED_" + role)
 138             if ready.exists():
 139                 data = json.loads(ready.read_text())
 140                 if data["pid"] == process.pid:
 141                     self.log.emit("started", role=role, child_pid=process.pid, boot=data.get("boot"))
 142                     return data
 143             time.sleep(0.02)
 144         raise TimeoutError("SERVICE_START_TIMEOUT_" + role)
 145 
 146     def start_all(self, fault=None):
 147         self.start("authority")
 148         self.start("provider")
 149         return self.start("controller", fault)
 150 
 151     def stop(self, role):
 152         process = self.processes.get(role)
 153         if process is not None and process.poll() is None:
 154             process.kill()
 155             code = process.wait(timeout=5)
 156             self.log.emit("terminated_and_waited", role=role, child_pid=process.pid, exit_code=code)
 157 
 158     def restart_controller(self, fault=None):
 159         self.stop("controller")
 160         return self.start("controller", fault)
 161 
 162     def client(self, identity="user", role="controller", timeout=3):
 163         config = self.configs[role]
 164         return Client("https://127.0.0.1:" + str(config["port"]),
 165                       config["identities"][identity], config["certificate"], self.runner_log, timeout)
 166 
 167     def async_call(self, identity, operation, payload):
 168         return self.executor.submit(self.client(identity, timeout=12).call, operation, payload)
 169 
 170     def wait_barrier(self, point):
```

## S05: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\dsat_authority_read.py
SHA-256: 3a6dbf67f4c9ee9df326607485ef78b995c27c1de18dfa5536b36705d27dfc83

```text
   1 """R11 internal read adapter: scoped, secret-free staging; no import-time I/O.
   2 
   3 The host authenticates and authorizes before binding a context. This library is
   4 not an authentication service. R12 exercises synthetic reader/lock doubles only.
   5 """
   6 from dataclasses import dataclass
   7 import hashlib
   8 import json
   9 import re
  10 import time
  11 
  12 from .protocol import canonical, digest, normalized_request
  13 
  14 
  15 SCHEMA = "dsat-authority-read/1"
  16 MODE = "AUTHORITY_READONLY_STAGING"
  17 MAX_REVISION = (1 << 63) - 1
  18 ORIGIN = ("grant_id", "caller", "task", "account", "audience", "generation")
  19 SCOPE_FIELDS = ("account", "audience", "tasks", "callers", "generations")
  20 PHASES = {"QUEUED", "CANCELLED", "DISPATCHED_UNKNOWN", "RESULT_AVAILABLE", "QUARANTINED", "DISPOSED"}
  21 BASE_GAPS = (
  22     "TYPED_O_NOT_IMPLEMENTED", "O_REVISION_NOT_IMPLEMENTED", "SOURCE_OR_REFINEMENT_GAP",
  23     "INSTANCE_UNBOUND", "SOURCE_COMPLETENESS_UNPROVEN", "SCOPE_UNIVERSE_INCOMPLETE",
  24     "CAPACITY_UNPROVEN", "BIRTH_OR_HISTORY_GAP", "SUSTAINED_INACTIVITY_UNPROVEN",
  25     "NATIVE_CURRENTNESS_UNPROVEN", "CURRENTNESS_UNPROVEN", "FRONTIER_UNPROVEN",
  26     "REAL_S1_ENTRY_UNAVAILABLE", "S1_V1_REDACTION_CONTRACT_GAP", "PROVIDER_HISTORY_EXPORT_REQUIRED",
  27     "LEGACY_SCOPE_INCOMPLETE",
  28 )
  29 ERRORS = {
  30     "READ_CONTEXT_REQUIRED", "READ_SCOPE_DENIED", "UNSUPPORTED_READ_REQUEST", "READ_SOURCE_UNAVAILABLE",
  31     "READ_BUDGET_DENIED", "SNAPSHOT_INCOMPLETE", "SOURCE_BINDING_CONFLICT", "INVALID_FIELD_TYPE",
  32     "RESOURCE_LIMIT", "BUDGET_SOURCE_CONFLICT", "UNSUPPORTED_SOURCE_SCHEMA",
  33 }
  34 PUBLIC_FIELDS = (
  35     "schema", "mode", "status", "source", "scope", "authority_revision", "obligation_revision",
  36     "grants", "requests", "disposals", "windows", "request_verifications", "legacy_obligations",
  37     "conservative_O_view", "typed_obligation_status", "missing_obligation_coverage", "open_frontiers",
  38     "partial_math", "field_provenance", "compatibility", "read_clock", "costs", "gap_codes",
  39     "math_input", "math_ready", "native_admission", "current_native_eligible", "global_complete",
  40     "authority_write_action", "snapshot_digest",
  41 )
  42 
  43 
  44 class ReadError(ValueError):
  45     """Only fixed codes may cross the read boundary."""
  46     def __init__(self, code):
  47         self.code = code if code in ERRORS else "SNAPSHOT_INCOMPLETE"
  48         super().__init__(self.code)
  49 
  50 
  51 def _id(value, maximum=80):
  52     if type(value) is not str or re.fullmatch(r"[A-Za-z0-9_.:-]{1,%d}" % maximum, value) is None:
  53         raise ReadError("INVALID_FIELD_TYPE")
  54     return value
  55 
  56 
  57 def _number(value, maximum=MAX_REVISION):
  58     if type(value) is not int or not 0 <= value <= maximum:
  59         raise ReadError("INVALID_FIELD_TYPE")
  60     return value
  61 
  62 
  63 def _bool(value):
  64     if type(value) is not bool:
  65         raise ReadError("INVALID_FIELD_TYPE")
  66     return value
  67 
  68 
  69 def _hash(domain, value):
  70     return hashlib.sha256(domain.encode("ascii") + b"\x00" + canonical(value)).hexdigest()
  71 
  72 
  73 def _copy(value):
  74     # Called only on newly built public values, never on the raw Authority state.
  75     return json.loads(canonical(value))
  76 
  77 
  78 @dataclass(frozen=True)
  79 class ReadLimits:
  80     output_bytes: int = 1048576
  81     scoped_records: int = 4096
  82     write_headroom: int = 6
  83 
  84     def __post_init__(self):
  85         if type(self.output_bytes) is not int or not 4096 <= self.output_bytes <= 1048576:
  86             raise ReadError("RESOURCE_LIMIT")
  87         if type(self.scoped_records) is not int or not 1 <= self.scoped_records <= 4096:
  88             raise ReadError("RESOURCE_LIMIT")
  89         if type(self.write_headroom) is not int or not 6 <= self.write_headroom <= 1000000:
  90             raise ReadError("RESOURCE_LIMIT")
  91 
  92 
  93 @dataclass(frozen=True)
  94 class ReadScope:
  95     account: str
  96     audience: str
  97     tasks: tuple
  98     callers: tuple
  99     generations: tuple
 100 
 101     def __post_init__(self):
 102         _id(self.account); _id(self.audience)
 103         for name in ("tasks", "callers", "generations"):
 104             items = getattr(self, name)
 105             if type(items) is not tuple or not 1 <= len(items) <= 4096 or len(set(items)) != len(items):
 106                 raise ReadError("UNSUPPORTED_READ_REQUEST")
 107             for value in items:
 108                 _id(value)
 109 
 110     def to_dict(self):
 111         return {"account": self.account, "audience": self.audience,
 112                 "tasks": list(self.tasks), "callers": list(self.callers), "generations": list(self.generations)}
 113 
 114     @classmethod
 115     def parse(cls, value):
 116         if type(value) is cls:
 117             return value
 118         if type(value) is not dict or set(value) != set(SCOPE_FIELDS):
 119             raise ReadError("UNSUPPORTED_READ_REQUEST")
 120         if any(type(value[k]) is not list for k in ("tasks", "callers", "generations")):
 121             raise ReadError("UNSUPPORTED_READ_REQUEST")
 122         return cls(value["account"], value["audience"], tuple(value["tasks"]), tuple(value["callers"]), tuple(value["generations"]))
 123 
 124     def contains(self, requested):
 125         return self.account == requested.account and self.audience == requested.audience and all(
 126             set(getattr(requested, k)) <= set(getattr(self, k)) for k in ("tasks", "callers", "generations"))
 127 
 128     def matches(self, origin):
 129         return (type(origin) is dict and origin.get("account") == self.account
 130                 and origin.get("audience") == self.audience and origin.get("task") in self.tasks
 131                 and origin.get("caller") in self.callers and origin.get("generation") in self.generations)
 132 
 133 
 134 class TrustedReadContext:
 135     """Host-only policy binding, outside serialized requests. Not a new credential.
 136 
 137     from_host requires a previously authorized host caller. Python code in that
 138     trusted process remains trusted; type tags do not authenticate a remote AI.
 139     """
 140     __slots__ = ("_reader", "_scope", "_principal", "_producer", "_locator", "_clock_epoch", "_source_kind")
 141 
 142     def __init__(self, *args, **kwargs):
 143         raise ReadError("READ_CONTEXT_REQUIRED")
 144 
 145     @classmethod
 146     def from_host(cls, reader, permitted_scope, *, principal_ref, producer_ref, authority_locator_ref,
 147                   clock_epoch_ref, source_kind):
 148         scope = ReadScope.parse(permitted_scope)
 149         for value in (principal_ref, producer_ref, authority_locator_ref, clock_epoch_ref):
 150             _id(value, 160)
 151         if source_kind not in {"SYNTHETIC_ONLY", "LOCAL_AUTHORITY_HOST"}:
 152             raise ReadError("READ_CONTEXT_REQUIRED")
 153         value = object.__new__(cls)
 154         value._reader = reader
 155         value._scope = scope
 156         value._principal, value._producer = principal_ref, producer_ref
 157         value._locator, value._clock_epoch = authority_locator_ref, clock_epoch_ref
 158         value._source_kind = source_kind
 159         return value
 160 
 161     def __repr__(self):
 162         return "<TrustedReadContext redacted>"
 163 
 164     def __reduce_ex__(self, protocol):
 165         raise TypeError("READ_CONTEXT_NOT_SERIALIZABLE")
 166 
 167 
 168 class StagingSnapshot:
 169     __slots__ = ("_public",)
 170 
 171     def __init__(self, public):
 172         if set(public) != set(PUBLIC_FIELDS) or public["schema"] != SCHEMA or public["mode"] != MODE:
 173             raise ReadError("UNSUPPORTED_SOURCE_SCHEMA")
 174         if (public["global_complete"] is not False or public["math_ready"] is not False
 175                 or public["current_native_eligible"] is not False or public["math_input"] is not None
 176                 or public["obligation_revision"] is not None or public["authority_write_action"] != "NONE"
 177                 or public["native_admission"] != "SOURCE_OR_REFINEMENT_GAP"):
 178             raise ReadError("UNSUPPORTED_READ_REQUEST")
 179         expected = _hash("dsat-authority-read/1:snapshot", {k: v for k, v in public.items() if k != "snapshot_digest"})
 180         if public["snapshot_digest"] != expected:
 181             raise ReadError("SOURCE_BINDING_CONFLICT")
 182         _validate_schema(public, staging_schema())
 183         self._public = _copy(public)
 184 
 185     def to_dict(self):
 186         return _copy(self._public)
 187 
 188     def to_json(self):
 189         return canonical(self._public)
 190 
 191     def __repr__(self):
 192         return "<StagingSnapshot schema=dsat-authority-read/1 status=" + self._public["status"] + ">"
 193 
 194 
 195 def _envelope(status, gaps, reads=0, read_ns=0, projection_ns=0):
 196     result = {k: None for k in PUBLIC_FIELDS}
 197     result.update(schema=SCHEMA, mode=MODE, status=status, obligation_revision=None,
 198                   typed_obligation_status="TYPED_O_NOT_IMPLEMENTED", gap_codes=sorted(set(gaps)),
 199                   missing_obligation_coverage=sorted(set(gaps)), math_input=None, math_ready=False,
 200                   native_admission="SOURCE_OR_REFINEMENT_GAP", current_native_eligible=False,
 201                   global_complete=False, authority_write_action="NONE",
 202                   costs={"source_reads": reads, "read_ns": read_ns, "projection_ns": projection_ns,
 203                          "source_operation_delta": None, "telemetry_may_change": True})
 204     return result
 205 
 206 
 207 def _finish(public):
 208     public["snapshot_digest"] = _hash("dsat-authority-read/1:snapshot", {k: v for k, v in public.items() if k != "snapshot_digest"})
 209     return StagingSnapshot(public)
 210 
 211 
 212 def _origin(value):
 213     if type(value) is not dict or set(value) != set(ORIGIN):
 214         raise ReadError("SOURCE_BINDING_CONFLICT")
 215     return {k: _id(value[k]) for k in ORIGIN}
 216 
 217 
 218 def _scope_origin(grant):
 219     return {k: grant[k] for k in ORIGIN}
 220 
 221 
 222 def _project(a, state, scope, context, limits):
 223     _number(a)
 224     if type(state) is not dict or any(type(state.get(k)) is not dict for k in ("grants", "requests")):
 225         raise ReadError("SNAPSHOT_INCOMPLETE")
 226     if "schema" in state and state["schema"] != "legacy-authority-state/1":
 227         raise ReadError("UNSUPPORTED_SOURCE_SCHEMA")
 228     gaps = set(BASE_GAPS)
 229     grants, raw_grants = [], {}
 230     for gid, value in state["grants"].items():
 231         if type(value) is not dict or not scope.matches(value):
 232             continue
 233         origin = _origin(_scope_origin(value))
 234         if _id(gid) != origin["grant_id"]:
 235             raise ReadError("SOURCE_BINDING_CONFLICT")
 236         ops = value["operations"]
 237         if type(ops) is not list or not ops or len(ops) > 4096 or len(set(ops)) != len(ops):
 238             raise ReadError("INVALID_FIELD_TYPE")
 239         operations = [_id(x) for x in ops]
 240         limit, reserved, spent = [_number(value[k], 1000000) for k in ("limit", "reserved", "spent")]
 241         if reserved + spent > limit:
 242             raise ReadError("BUDGET_SOURCE_CONFLICT")
 243         grants.append({"origin": origin, "active": _bool(value["active"]), "operations": operations,
 244                        "limit": limit, "reserved": reserved, "spent": spent})
 245         raw_grants[gid] = value
 246         if len(grants) > limits.scoped_records:
 247             raise ReadError("RESOURCE_LIMIT")
 248     requests, selected_raw, verifications = [], {}, []
 249     for rid, raw in state["requests"].items():
 250         if type(raw) is not dict or not scope.matches(raw.get("origin")):
 251             continue
 252         origin = _origin(raw["origin"])
 253         if _id(rid) != _id(raw["rid"]) or origin["grant_id"] not in raw_grants:
 254             raise ReadError("SOURCE_BINDING_CONFLICT")
 255         grant = raw_grants[origin["grant_id"]]
 256         if origin != _scope_origin(grant):
 257             raise ReadError("SOURCE_BINDING_CONFLICT")
 258         original = raw.get("request")
 259         if type(original) is not dict:
 260             raise ReadError("SNAPSHOT_INCOMPLETE")
 261         try:
 262             normalized = normalized_request(original)
 263         except Exception:
 264             raise ReadError("SOURCE_BINDING_CONFLICT") from None
 265         expected = digest({"caller": origin["caller"], "request": normalized})
 266         if (raw.get("digest") != expected or normalized["rid"] != rid
 267                 or normalized["handle"] != grant.get("handle")
 268                 or any(normalized[k] != origin[k] for k in ("task", "account", "audience", "generation"))):
 269             raise ReadError("SOURCE_BINDING_CONFLICT")
 270         phase = raw["phase"]
 271         if type(phase) is not str or phase not in PHASES:
 272             raise ReadError("INVALID_FIELD_TYPE")
 273         aid, release = raw["attempt_id"], raw["release_version"]
 274         if phase in {"QUEUED", "CANCELLED"}:
 275             if aid is not None or release is not None:
 276                 raise ReadError("SOURCE_BINDING_CONFLICT")
 277         else:
 278             if aid is None or release is None:
 279                 raise ReadError("SOURCE_BINDING_CONFLICT")
 280             _id(aid); _number(release)
 281             if release > a:
 282                 raise ReadError("SOURCE_BINDING_CONFLICT")
 283         source_rid = normalized["payload"].get("source_rid")
 284         source_status = "NOT_APPLICABLE"
 285         if normalized["operation"] in {"refresh", "userinfo"}:
 286             parent = state["requests"].get(source_rid)
 287             if type(parent) is dict and parent.get("origin") == origin and scope.matches(parent.get("origin")):
 288                 source_status = "BOUND_LOCAL_REFERENCE"
 289             else:
 290                 source_rid = None
 291                 source_status = "MISSING_OR_OUTSIDE_SCOPE"
 292                 gaps.add("SOURCE_REFERENCE_UNAVAILABLE")
 293         material = raw.get("result_material")
 294         material_present = material is not None
 295         kind = material.get("kind") if type(material) is dict else "legacy" if type(material) is str else None
 296         if kind not in {"casdoor_login", "casdoor_oauth", "legacy", None}:
 297             kind = "UNVERIFIED"
 298         binding = {"rid": rid, "request_digest": expected, "origin": origin,
 299                    "attempt_id": aid, "release_version": release}
 300         reference = _hash("dsat-authority-read/1:request-check", {"a": a, "locator": context._locator, **binding})
 301         requests.append({**binding, "operation": normalized["operation"], "source_rid": source_rid,
 302                          "source_link_status": source_status, "phase": phase,
 303                          "material_present": material_present, "material_kind": kind,
 304                          "result_ref": "result:" + _hash("dsat-authority-read/1:result", {"locator": context._locator, **binding}) if material_present else None,
 305                          "verification_ref": reference})
 306         verifications.append({"rid": rid, "authority_revision": a, "request_digest": expected,
 307                               "tuple_digest": _hash("dsat-authority-read/1:tuple", binding),
 308                               "verification_ref": reference, "outcome": "MATCHED_AT_TRUSTED_SOURCE",
 309                               "producer_ref": context._producer})
 310         selected_raw[rid] = raw
 311         if len(grants) + len(requests) > limits.scoped_records:
 312             raise ReadError("RESOURCE_LIMIT")
 313     if len(grants) + len(requests) > limits.scoped_records:
 314         raise ReadError("RESOURCE_LIMIT")
 315     observations, windows = [], []
 316     for did, item in state.get("disposals", {}).items():
 317         if type(item) is not dict or item.get("rid") not in selected_raw:
 318             continue
 319         raw = selected_raw[item["rid"]]
 320         if item.get("origin") != raw["origin"]:
 321             raise ReadError("SOURCE_BINDING_CONFLICT")
 322         phase = item["phase"]
 323         if phase not in {"DISPOSAL_UNKNOWN", "NATIVE_REVOKE_RESPONDED", "KNOWN_UNIT_INACTIVE"}:
 324             raise ReadError("INVALID_FIELD_TYPE")
 325         obs = item.get("observations", {})
 326         clean = {}
 327         for k in ("userinfo_http", "userinfo_accepted", "introspection_active"):
 328             v = obs.get(k)
 329             if v is not None:
 330                 if k.endswith("http"):
 331                     _number(v, 599)
 332                     if v < 100:
 333                         raise ReadError("INVALID_FIELD_TYPE")
 334                 else:
 335                     _bool(v)
 336             clean[k] = v
 337         done = item.get("completed_version")
 338         if done is not None and _number(done) > a:
 339             raise ReadError("SOURCE_BINDING_CONFLICT")
 340         observations.append({"disposal_ref": _id(did), "rid": item["rid"], "phase": phase,
 341                              "completed_version": done, "point_observations": clean,
 342                              "observation_guarantee": "POINT_ONLY_UNVERIFIED_FOR_NATIVE_FRAME"})
 343     for account, item in state.get("reconciliation_windows", {}).items():
 344         if account != scope.account or type(item) is not dict or item.get("target_rid") not in selected_raw:
 345             continue
 346         receipt = item.get("receipt", {})
 347         claim = receipt.get("claim") if type(receipt) is dict else None
 348         if claim not in {"CLOSED", "UNKNOWN", None}:
 349             claim = "UNVERIFIED"
 350         creators = item.get("unknown_creators_at_open", [])
 351         if type(creators) is not list:
 352             raise ReadError("INVALID_FIELD_TYPE")
 353         windows.append({"window_id": _id(item["window_id"]), "target_rid": item["target_rid"],
 354                         "active": _bool(item["active"]), "opened_version": _number(item["opened_version"]),
 355                         "scoped_creators": [_id(x) for x in creators if x in selected_raw],
 356                         "source_scope_complete": False,
 357                         "legacy_receipt_summary": {"schema": "native-attempt-closure/1" if receipt.get("schema") == "native-attempt-closure/1" else None,
 358                                                    "claim": claim, "scope": "ONE_ATTEMPT_HISTORY_ONLY"}})
 359     if len(grants) + len(requests) + len(observations) + len(windows) > limits.scoped_records:
 360         raise ReadError("RESOURCE_LIMIT")
 361     legacy = {x["rid"] for x in requests if x["phase"] in {"DISPATCHED_UNKNOWN", "QUARANTINED"}}
 362     for window in windows:
 363         if window["legacy_receipt_summary"]["claim"] != "CLOSED":
 364             legacy.add(window["target_rid"])
 365     view = {}
 366     def hold(kind, ref):
 367         oid = kind + ":" + ref
 368         view[oid] = {"id": oid, "kind": kind, "refs": [ref], "strict": True}
 369     hold("source_hold", scope.account)
 370     frontiers, attempts = [], []
 371     for grant in grants:
 372         if grant["active"] and set(grant["operations"]) & {"issue", "refresh"} and grant["limit"] > grant["spent"] + grant["reserved"]:
 373             ref = grant["origin"]["grant_id"]; hold("grant_frontier", ref); frontiers.append("grant_frontier:" + ref)
 374     for req in requests:
 375         if req["operation"] in {"issue", "refresh"}:
 376             if req["phase"] == "QUEUED":
 377                 hold("queued_creator", req["rid"]); frontiers.append("queued_creator:" + req["rid"])
 378                 gaps.add("QUEUED_CREATOR_FRONTIER")
 379             if req["attempt_id"] is not None:
 380                 attempts.append(req["attempt_id"]); hold("await_terminal", req["rid"])
 381             if req["phase"] == "DISPATCHED_UNKNOWN":
 382                 hold("settle", req["rid"])
 383         elif req["phase"] == "DISPATCHED_UNKNOWN":
 384             hold("exec", req["rid"])
 385         if req["material_present"]:
 386             hold("close", req["rid"])
 387     for window in windows:
 388         hold("window_review", window["target_rid"])
 389     result = _envelope("STAGING_READY_WITH_GAPS", gaps)
 390     result.update(source={"authority_locator_ref": context._locator, "producer_ref": context._producer,
 391                           "principal_ref": context._principal,
 392                           "authority_instance": None, "sql_schema_version": None,
 393                           "source_contract": "legacy-authority-state/1", "source_kind": context._source_kind,
 394                           "authentication_basis": "HOST_AUTHORIZED_CONTEXT_OUT_OF_BAND"},
 395                   scope=scope.to_dict(), authority_revision=a,
 396                   grants=sorted(grants, key=lambda x: x["origin"]["grant_id"]), requests=sorted(requests, key=lambda x: x["rid"]),
 397                   disposals=sorted(observations, key=lambda x: x["disposal_ref"]), windows=windows,
 398                   request_verifications=sorted(verifications, key=lambda x: x["rid"]),
 399                   legacy_obligations=sorted(legacy), conservative_O_view=[view[k] for k in sorted(view)],
 400                   open_frontiers=sorted(frontiers),
 401                   partial_math={"local_creator_attempts": sorted(attempts), "target_candidates": sorted(attempts),
 402                                 "c_known": {}, "capacity_unknown": sorted(attempts), "U": None, "E": None, "D_P": None,
 403                                 "interpretation": "LOCAL_METADATA_ONLY_NOT_D_FIN"},
 404                   field_provenance={"authority_revision": {"category": "DIRECT_FIELD", "source": "authority_state.version"},
 405                                     "request_metadata": {"category": "DERIVED_WITH_TRUSTED_BINDING", "source": "request_verifications"},
 406                                     "legacy_obligations": {"category": "LEGACY_PROJECTION", "source": "scoped_phase_and_window"},
 407                                     "test_source": {"category": "SYNTHETIC_ONLY" if context._source_kind == "SYNTHETIC_ONLY" else "UNVERIFIED", "source": "host_context"},
 408                                     "instance_o": {"category": "UNAVAILABLE", "source": "no_legacy_field"},
 409                                     "native_frame": {"category": "UNVERIFIED", "source": "external_evidence_required"}},
 410                   compatibility={"S1": {"direct_input": False, "reason": "S1_V1_REDACTION_CONTRACT_GAP"},
 411                                  "S2": {"direct_input": False, "reason": "FINITE_MATH_INPUT_UNAVAILABLE"},
 412                                  "S3A": {"direct_input": False, "reason": "SYNTHETIC_REGISTRY_AND_REAL_BASE_GAP"},
 413                                  "legacy": {"scope": "ONE_ATTEMPT_HISTORY_ONLY", "global_complete": False}})
 414     return result
 415 
 416 
 417 def read_dsat_authority_snapshot(reader, scope, trusted_read_context, limits=ReadLimits()):
 418     """Read once under the host lock, then return an immutable-owned public value.
 419 
 420     Existing read_state telemetry/quota effects are permitted by the source
 421     contract; world mutations, old call dispatch and source constructors are absent.
 422     """
 423     reads, read_ns, project_ns = 0, 0, 0
 424     try:
 425         if type(trusted_read_context) is not TrustedReadContext or trusted_read_context._reader is not reader:
 426             raise ReadError("READ_CONTEXT_REQUIRED")
 427         context = trusted_read_context
 428         requested = ReadScope.parse(scope)
 429         if not context._scope.contains(requested):
 430             raise ReadError("READ_SCOPE_DENIED")
 431         if type(limits) is not ReadLimits:
 432             raise ReadError("RESOURCE_LIMIT")
 433         with reader.lock:
 434             operation_limit = getattr(reader, "operation_limit", None)
 435             operations = getattr(reader, "operations", None)
 436             if operation_limit is not None:
 437                 _number(operation_limit); _number(operations)
 438                 if operations + 1 + limits.write_headroom > operation_limit:
 439                     raise ReadError("READ_BUDGET_DENIED")
 440             before = operations
 441             started = time.monotonic_ns(); read_started = time.perf_counter_ns(); reads = 1
 442             try:
 443                 a, state = reader.read_state()
 444             finally:
 445                 read_ns = time.perf_counter_ns() - read_started
 446                 observed = time.monotonic_ns()
 447             project_started = time.perf_counter_ns()
 448             try:
 449                 public = _project(a, state, requested, context, limits)
 450             finally:
 451                 project_ns = time.perf_counter_ns() - project_started
 452             after = getattr(reader, "operations", None)
 453             public["read_clock"] = {"domain": "monotonic_ns", "epoch_ref": context._clock_epoch,
 454                                     "lower": started, "upper": observed, "native_validity": "UNESTABLISHED"}
 455             public["costs"] = {"source_reads": 1, "read_ns": read_ns, "projection_ns": project_ns,
 456                                "source_operation_delta": after - before if type(after) is int and type(before) is int else None,
 457                                "telemetry_may_change": True}
 458             result = _finish(public)
 459             if len(result.to_json()) > limits.output_bytes:
 460                 raise ReadError("RESOURCE_LIMIT")
 461             return result
 462     except ReadError as exc:
 463         return _finish(_envelope(exc.code, (*BASE_GAPS, exc.code), reads, read_ns, project_ns))
 464     except (KeyError, TypeError, ValueError, AttributeError):
 465         return _finish(_envelope("SNAPSHOT_INCOMPLETE", (*BASE_GAPS, "SNAPSHOT_INCOMPLETE"), reads, read_ns, project_ns))
 466     except Exception:
 467         # Never include exception strings, locals, raw state, reader repr or causes.
 468         return _finish(_envelope("READ_SOURCE_UNAVAILABLE", (*BASE_GAPS, "READ_SOURCE_UNAVAILABLE"), reads, read_ns, project_ns))
 469 
 470 
 471 def staging_schema():
 472     """Machine-readable public contract; semantic checks stay in the adapter."""
 473     text = {"type": "string"}
 474     integer = {"type": "integer", "minimum": 0, "maximum": MAX_REVISION}
 475     boolean = {"type": "boolean"}
 476     def nullable(schema):
 477         return {**schema, "type": [schema["type"], "null"]}
 478     def obj(props):
 479         return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}
 480     def array(item):
 481         return {"type": "array", "items": item, "maxItems": 16384}
 482     origin = obj({k: text for k in ORIGIN})
 483     obligation_schema = obj({"id": text, "kind": text, "refs": array(text), "strict": {"const": True}})
 484     request = obj({"rid": text, "request_digest": text, "origin": origin,
 485                    "attempt_id": nullable(text), "release_version": nullable(integer),
 486                    "operation": text, "source_rid": nullable(text), "source_link_status": text,
 487                    "phase": {"enum": sorted(PHASES)}, "material_present": boolean,
 488                    "material_kind": nullable(text), "result_ref": nullable(text), "verification_ref": text})
 489     grant = obj({"origin": origin, "active": boolean, "operations": array(text),
 490                  "limit": integer, "reserved": integer, "spent": integer})
 491     provenance = obj({"category": {"enum": ["DIRECT_FIELD", "DERIVED_WITH_TRUSTED_BINDING", "LEGACY_PROJECTION",
 492                                             "SYNTHETIC_ONLY", "UNAVAILABLE", "UNVERIFIED"]}, "source": text})
 493     properties = {
 494         "source": nullable(obj({"authority_locator_ref": text, "producer_ref": text, "principal_ref": text,
 495                                 "authority_instance": {"type": "null"}, "sql_schema_version": {"type": "null"},
 496                                 "source_contract": {"const": "legacy-authority-state/1"}, "source_kind": text,
 497                                 "authentication_basis": {"const": "HOST_AUTHORIZED_CONTEXT_OUT_OF_BAND"}})),
 498         "scope": nullable(obj({"account": text, "audience": text, "tasks": array(text),
 499                                "callers": array(text), "generations": array(text)})),
 500         "grants": nullable(array(grant)), "requests": nullable(array(request)),
 501         "disposals": nullable(array(obj({"disposal_ref": text, "rid": text, "phase": text,
 502             "completed_version": nullable(integer), "observation_guarantee": text,
 503             "point_observations": obj({"userinfo_http": nullable(integer), "userinfo_accepted": nullable(boolean),
 504                                        "introspection_active": nullable(boolean)})}))),
 505         "windows": nullable(array(obj({"window_id": text, "target_rid": text, "active": boolean,
 506             "opened_version": integer, "scoped_creators": array(text), "source_scope_complete": {"const": False},
 507             "legacy_receipt_summary": obj({"schema": nullable(text), "claim": nullable(text),
 508                                             "scope": {"const": "ONE_ATTEMPT_HISTORY_ONLY"}})}))),
 509         "request_verifications": nullable(array(obj({"rid": text, "authority_revision": integer,
 510             "request_digest": text, "tuple_digest": text, "verification_ref": text,
 511             "outcome": {"const": "MATCHED_AT_TRUSTED_SOURCE"}, "producer_ref": text}))),
 512         "legacy_obligations": nullable(array(text)), "conservative_O_view": nullable(array(obligation_schema)),
 513         "missing_obligation_coverage": array(text), "gap_codes": array(text), "open_frontiers": nullable(array(text)),
 514         "partial_math": nullable(obj({"local_creator_attempts": array(text), "target_candidates": array(text),
 515             "c_known": obj({}), "capacity_unknown": array(text), "U": {"type": "null"}, "E": {"type": "null"},
 516             "D_P": {"type": "null"}, "interpretation": {"const": "LOCAL_METADATA_ONLY_NOT_D_FIN"}})),
 517         "field_provenance": nullable(obj({k: provenance for k in ("authority_revision", "request_metadata",
 518             "legacy_obligations", "test_source", "instance_o", "native_frame")})),
 519         "compatibility": nullable(obj({"S1": obj({"direct_input": {"const": False}, "reason": text}),
 520             "S2": obj({"direct_input": {"const": False}, "reason": text}),
 521             "S3A": obj({"direct_input": {"const": False}, "reason": text}),
 522             "legacy": obj({"scope": {"const": "ONE_ATTEMPT_HISTORY_ONLY"}, "global_complete": {"const": False}})})),
 523         "read_clock": nullable(obj({"domain": {"const": "monotonic_ns"}, "epoch_ref": text,
 524             "lower": integer, "upper": integer, "native_validity": {"const": "UNESTABLISHED"}})),
 525         "costs": obj({"source_reads": integer, "read_ns": integer, "projection_ns": integer,
 526                       "source_operation_delta": nullable(integer), "telemetry_may_change": {"const": True}}),
 527     }
 528     properties.update(schema={"const": SCHEMA}, mode={"const": MODE},
 529                       status={"enum": ["STAGING_READY_WITH_GAPS", *sorted(ERRORS)]},
 530                       authority_revision={"type": ["integer", "null"], "minimum": 0, "maximum": MAX_REVISION},
 531                       obligation_revision={"type": "null"}, math_input={"type": "null"},
 532                       math_ready={"const": False}, global_complete={"const": False},
 533                       current_native_eligible={"const": False}, authority_write_action={"const": "NONE"},
 534                       native_admission={"const": "SOURCE_OR_REFINEMENT_GAP"},
 535                       typed_obligation_status={"const": "TYPED_O_NOT_IMPLEMENTED"},
 536                       snapshot_digest={"type": "string", "pattern": "^[0-9a-f]{64}$"})
 537     return {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": SCHEMA,
 538             "type": "object", "additionalProperties": False, "required": list(PUBLIC_FIELDS),
 539             "properties": properties, "x-invariants": ["source-side original digest checked without exporting handle",
 540             "trusted host auth remains outside payload", "typed O and o absent, all native qualification unverified",
 541             "one source read under existing lock; no application writes; output deeply detached"]}
 542 
 543 
 544 def _validate_schema(value, schema, depth=0):
 545     """Small closed-schema validator for this fixed contract, not a general oracle."""
 546     if depth > 32:
 547         raise ReadError("RESOURCE_LIMIT")
 548     if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
 549         raise ReadError("INVALID_FIELD_TYPE")
 550     if "enum" in schema and value not in schema["enum"]:
 551         raise ReadError("INVALID_FIELD_TYPE")
 552     expected = schema.get("type")
 553     types = expected if type(expected) is list else [expected] if expected is not None else []
 554     actual = {dict: "object", list: "array", str: "string", int: "integer", bool: "boolean", type(None): "null"}.get(type(value))
 555     if types and actual not in types:
 556         raise ReadError("INVALID_FIELD_TYPE")
 557     if value is None:
 558         return
 559     if actual == "object":
 560         if not set(schema.get("required", [])) <= set(value):
 561             raise ReadError("INVALID_FIELD_TYPE")
 562         props = schema.get("properties", {})
 563         if schema.get("additionalProperties") is False and not set(value) <= set(props):
 564             raise ReadError("INVALID_FIELD_TYPE")
 565         for k, v in value.items():
 566             _validate_schema(v, props.get(k, {}), depth + 1)
 567     elif actual == "array":
 568         if len(value) > schema.get("maxItems", 16384):
 569             raise ReadError("RESOURCE_LIMIT")
 570         for item in value:
 571             _validate_schema(item, schema.get("items", {}), depth + 1)
 572     elif actual == "integer":
 573         if not schema.get("minimum", 0) <= value <= schema.get("maximum", MAX_REVISION):
 574             raise ReadError("INVALID_FIELD_TYPE")
 575     elif actual == "string":
 576         if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
 577             raise ReadError("INVALID_FIELD_TYPE")
 578         if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
 579             raise ReadError("INVALID_FIELD_TYPE")
```

## S06: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\cli.py
SHA-256: ae6b268c4e75abcb32bf37af9e554ee70a93bcb81df6c0b020df4b0050db1ba2

```text
   1 """Process entry points for the mature online-state baseline."""
   2 
   3 import argparse
   4 import json
   5 from pathlib import Path
   6 
   7 from .lab import Laboratory, initialize
   8 from .services import serve
   9 
  10 
  11 def main():
  12     parser = argparse.ArgumentParser()
  13     commands = parser.add_subparsers(dest="command", required=True)
  14     init = commands.add_parser("init")
  15     init.add_argument("--root", required=True)
  16     init.add_argument("--operation-limit", type=int)
  17     server = commands.add_parser("serve")
  18     server.add_argument("--root", required=True)
  19     server.add_argument("--role", choices=["authority", "provider", "controller"], required=True)
  20     server.add_argument("--fault", choices=["before_admit", "after_admit", "after_release", "after_effect",
  21                                          "before_revoke", "after_revoke_commit"])
  22     request = commands.add_parser("request")
  23     request.add_argument("--root", required=True)
  24     request.add_argument("--identity", choices=["user", "agentA", "agentB"], required=True)
  25     request.add_argument("--operation", required=True)
  26     request.add_argument("--input", required=True)
  27     m1 = commands.add_parser("m1")
  28     m1.add_argument("--out", required=True)
  29     m1.add_argument("--authorization-id", required=True)
  30     m1.add_argument("--continue-from", help="Execute only NOT_RUN slots from the same authorized plan")
  31     trace = commands.add_parser("trace")
  32     trace.add_argument("--root", required=True)
  33     trace.add_argument("--scenario", required=True)
  34     args = parser.parse_args()
  35     if args.command == "init":
  36         initialize(args.root, args.operation_limit)
  37         print(json.dumps({"status": "INITIALIZED", "root": str(Path(args.root).resolve())}))
  38     elif args.command == "serve":
  39         serve(args.role, args.root, args.fault)
  40     elif args.command == "request":
  41         lab = Laboratory(args.root, create=False)
  42         try:
  43             result = lab.client(args.identity).call(args.operation, json.loads(Path(args.input).read_text()))
  44             print(json.dumps(result, ensure_ascii=False))
  45         finally:
  46             lab.close()
  47     elif args.command == "m1":
  48         from .acceptance import run_acceptance
  49         run_acceptance(args.out, args.authorization_id, args.continue_from)
  50     elif args.command == "trace":
  51         from .acceptance import SCENARIOS, run_trace
  52         if args.scenario not in SCENARIOS:
  53             parser.error("unknown scenario")
  54         run_trace(args.root, args.scenario)
  55 
  56 
  57 if __name__ == "__main__":
  58     main()
```

## S07: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\migration.sql
SHA-256: cde954789b246d75b9f699e0e43a0d63ca199ee91470d76a7a1ca31b7d00420f

```text
   1 CREATE TABLE IF NOT EXISTS authority_state (
   2     id INTEGER PRIMARY KEY CHECK (id = 1),
   3     version INTEGER NOT NULL,
   4     ciphertext BLOB NOT NULL
   5 );
   6 CREATE TABLE IF NOT EXISTS authority_events (
   7     version INTEGER PRIMARY KEY,
   8     operation TEXT NOT NULL,
   9     projection TEXT NOT NULL
  10 );
  11 PRAGMA user_version = 1;
```

## S08: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\migration_2.sql
SHA-256: 7b0c25f990cc101b3b69d3598ed250732f5c975e1dcc30d4980ee0933dd97719

```text
   1 -- Schema 2 accepts typed material bundles. Legacy string values remain readable.
   2 -- The encrypted application-row format and AAD remain schema-1 for compatibility.
   3 PRAGMA user_version = 2;
```

## S09: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\isolation_service.py
SHA-256: 37bd7f085e202a1ae2df9150118556f82ae6b85d38e93c892fa781621ae66f0e

```text
   1 """Safe startup diagnostics for M5 services; no inherited output handles."""
   2 import argparse
   3 import json
   4 from pathlib import Path
   5 import traceback
   6 
   7 
   8 def main():
   9     parser = argparse.ArgumentParser()
  10     parser.add_argument("--root", required=True)
  11     parser.add_argument("--role", required=True)
  12     parser.add_argument("--fault")
  13     args = parser.parse_args()
  14     try:
  15         import os
  16         import sys
  17         import hashlib
  18         from .isolation_agent import token_information
  19         metadata = {"token": token_information(), "command_line": sys.argv,
  20                     "environment": {k: hashlib.sha256(v.encode()).hexdigest() for k,v in os.environ.items()}}
  21         (Path(args.root) / "control" / (args.role + "_" + str(os.getpid()) + "_isolation.json")).write_text(json.dumps(metadata))
  22         from .services import serve
  23         serve(args.role, args.root, args.fault)
  24     except Exception as error:
  25         # Class, numeric OS codes and frame locations, never exception text.
  26         record = {"exception": type(error).__name__, "winerror": getattr(error, "winerror", None),
  27                   "errno": getattr(error, "errno", None),
  28                   "frames": [{"file": f.filename, "function": f.name, "line": f.lineno}
  29                              for f in traceback.extract_tb(error.__traceback__)]}
  30         if isinstance(error, ImportError): record["loader_error"] = str(error)
  31         (Path(args.root) / "control" / (args.role + "_startup_error.json")).write_text(json.dumps(record))
  32         raise SystemExit(1)
  33 
  34 
  35 if __name__ == "__main__": main()
```

## S10: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_isolation_service.py
SHA-256: b2740390f2fb243378171ed182e64b8b72fa59f4a8fec7dace1a18e344257a34

```text
   1 """M6 service bootstrap, reusing M5 token diagnostics and startup handling."""
   2 import json
   3 from pathlib import Path
   4 import sys
   5 
   6 
   7 def main():
   8     args = sys.argv
   9     root = Path(args[args.index("--root") + 1])
  10     role = args[args.index("--role") + 1]
  11     config = json.loads((root / "secure" / (role + ".json")).read_text())
  12     if role == "provider" and config.get("synthetic_transport_fixture"):
  13         from .native_isolation_fixture import install
  14         install(config["synthetic_transport_fixture"])
  15     from .isolation_service import main as serve
  16     serve()
  17 
  18 
  19 if __name__ == "__main__": main()
```

## T01: D:\毕业设计\auth-lifecycle\tests\test_dsat_authority_read.py
SHA-256: a6d204f145a51c8a50599fa9096417e021e19e5844163c2c49a5e0e208db4ac9

```text
   1 """R11's 33 B1 cases. B15/B27/B28 remain outside this executable suite."""
   2 import ast
   3 from concurrent.futures import ThreadPoolExecutor
   4 import contextlib
   5 import copy
   6 import hashlib
   7 import io
   8 import json
   9 import logging
  10 from pathlib import Path
  11 import pickle
  12 import threading
  13 import time
  14 import unittest
  15 
  16 from auth_lifecycle.online_state.dsat_authority_read import (
  17     BASE_GAPS, MODE, PUBLIC_FIELDS, SCHEMA, ReadError, ReadLimits, ReadScope,
  18     StagingSnapshot, TrustedReadContext, read_dsat_authority_snapshot, staging_schema,
  19 )
  20 from auth_lifecycle.online_state.protocol import canonical, digest
  21 
  22 
  23 CONFIG = {}
  24 DETAILS = []
  25 
  26 
  27 def configure(plan, fixture_root):
  28     CONFIG.update(plan=plan, fixture_root=fixture_root)
  29 
  30 
  31 class LockSpy:
  32     def __init__(self):
  33         self._lock = threading.RLock()
  34         self.depth = 0
  35         self.entries = 0
  36         self.max_depth = 0
  37 
  38     def __enter__(self):
  39         self._lock.acquire()
  40         self.depth += 1; self.entries += 1
  41         self.max_depth = max(self.max_depth, self.depth)
  42         return self
  43 
  44     def __exit__(self, *args):
  45         self.depth -= 1; self._lock.release()
  46 
  47 
  48 class ReaderSpy:
  49     def __init__(self, state, version=120, operation_limit=None):
  50         self.state = state
  51         self.version = version
  52         self.lock = LockSpy()
  53         self.calls = 0
  54         self.operations = 0
  55         self.operation_limit = operation_limit
  56         self.forbidden_calls = 0
  57         self.fail_message = None
  58 
  59     def read_state(self):
  60         if self.lock.depth != 1:
  61             raise AssertionError("SOURCE_LOCK_REQUIRED")
  62         self.calls += 1; self.operations += 1
  63         if self.fail_message is not None:
  64             raise RuntimeError(self.fail_message)
  65         return self.version, self.state
  66 
  67     def call(self, *args):
  68         self.forbidden_calls += 1
  69         raise AssertionError("OLD_DISPATCH_FORBIDDEN")
  70 
  71     def execute(self, *args):
  72         self.forbidden_calls += 1
  73         raise AssertionError("SQL_FORBIDDEN")
  74 
  75     def __repr__(self):
  76         return "<SyntheticReaderSpy redacted>"
  77 
  78 
  79 class B1Cases(unittest.TestCase):
  80     def setUp(self):
  81         self.case_id = self._testMethodName.split("_")[1]
  82         self.spec = next(x for x in CONFIG["plan"]["cases"] if x["id"] == self.case_id)
  83         self.state = json.loads((CONFIG["fixture_root"]/"BASE_STATE.json").read_text(encoding="utf-8"))
  84         self.meta = json.loads((CONFIG["fixture_root"]/"METADATA.json").read_text(encoding="utf-8"))
  85         self.canaries = json.loads((CONFIG["fixture_root"]/"CANARIES.json").read_text(encoding="utf-8"))
  86         self.reader = ReaderSpy(self.state)
  87         self.observed = []
  88         self.checks = []
  89         self.started = time.perf_counter_ns()
  90 
  91     def tearDown(self):
  92         DETAILS.append({"id": self.case_id, "name": self.spec["name"], "checks": self.checks,
  93                         "calls": self.observed, "elapsed_ns": time.perf_counter_ns()-self.started})
  94 
  95     def check(self, condition, label):
  96         self.checks.append({"label": label, "satisfied": bool(condition)})
  97         if not condition:
  98             raise AssertionError(label)  # Fixed label only; no raw fixture repr in failures.
  99 
 100     def context(self, reader=None, scope=None, **overrides):
 101         data = dict(self.meta["host_context"]); data.update(overrides)
 102         return TrustedReadContext.from_host(reader or self.reader, scope or self.meta["scope_A"], **data)
 103 
 104     def read(self, *, reader=None, scope=None, context=None, limits=ReadLimits(), foreign=True):
 105         source = reader or self.reader
 106         ctx = self.context(source) if context is None else context
 107         requested = self.meta["scope_A"] if scope is None else scope
 108         before = canonical(source.state)
 109         version, calls = source.version, source.calls
 110         stdout, stderr, log = io.StringIO(), io.StringIO(), io.StringIO()
 111         handler = logging.StreamHandler(log); logger = logging.getLogger(); logger.addHandler(handler)
 112         started = time.perf_counter_ns()
 113         try:
 114             with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
 115                 result = read_dsat_authority_snapshot(source, requested, ctx, limits)
 116         finally:
 117             logger.removeHandler(handler)
 118         elapsed = time.perf_counter_ns()-started
 119         public = result.to_dict()
 120         self.check(before == canonical(source.state) and version == source.version, "AUTHORITY_WORLD_UNCHANGED")
 121         self.check(source.forbidden_calls == 0, "NO_OLD_DISPATCH_SQL_OR_WRITE")
 122         self.check(source.calls-calls <= 1, "AT_MOST_ONE_SOURCE_READ")
 123         self.check(public["global_complete"] is False and public["math_ready"] is False
 124                    and public["current_native_eligible"] is False, "NO_STRONG_QUALIFICATION")
 125         self.check(public["obligation_revision"] is None and public["authority_write_action"] == "NONE", "NO_O_REVISION_OR_COMMIT")
 126         rendered = result.to_json().decode()+repr(result)+json.dumps(public)+stdout.getvalue()+stderr.getvalue()+log.getvalue()
 127         self.no_secrets(rendered)
 128         if foreign:
 129             self.no_foreign(rendered)
 130         self.observed.append({"result": public, "total_ns": elapsed, "world_unchanged": True,
 131                               "source_reads": source.calls-calls, "log_bytes": len(log.getvalue()),
 132                               "stdout_bytes": len(stdout.getvalue()), "stderr_bytes": len(stderr.getvalue()),
 133                               "secret_scan": "CLEAN", "scope_scan": "CLEAN" if foreign else "EXPLICIT_WIDE_SCOPE"})
 134         return result
 135 
 136     def no_secrets(self, text):
 137         self.check(all(value not in text for value in self.canaries["sensitive_values"]), "SECRET_CANARIES_ABSENT")
 138 
 139     def no_foreign(self, text):
 140         self.check(all(value not in text for value in self.canaries["foreign_scope_A"]), "FOREIGN_SCOPE_METADATA_ABSENT")
 141 
 142     def ready(self, result):
 143         self.check(result.to_dict()["status"] == "STAGING_READY_WITH_GAPS", "STAGING_READY_WITH_EXPLICIT_GAPS")
 144 
 145     def request(self, public, rid):
 146         return next(x for x in public["requests"] if x["rid"] == rid)
 147 
 148     def resign(self, state, rid):
 149         raw = state["requests"][rid]
 150         raw["digest"] = digest({"caller": raw["origin"]["caller"], "request": raw["request"]})
 151 
 152     def test_B01_initialized_reader(self):
 153         result = self.read(); self.ready(result)
 154         self.check(self.reader.calls == 1 and self.reader.lock.entries == 1, "EXISTING_READER_ONCE_UNDER_LOCK")
 155         self.check(set(result.to_dict()) == set(PUBLIC_FIELDS), "VERSIONED_CLOSED_PUBLIC_SHAPE")
 156 
 157     def test_B02_revision(self):
 158         a=self.read().to_dict();self.check(a["authority_revision"]==120,"LOCAL_A_PRESERVED")
 159         self.reader.version=121;b=self.read().to_dict()
 160         self.check(b["authority_revision"]==121 and a["snapshot_digest"]!=b["snapshot_digest"],"READ_A_BOUND_IN_SNAPSHOT")
 161         self.check(all(v["authority_revision"]==121 for v in b["request_verifications"]),"REQUESTS_SAME_READ_VERSION")
 162 
 163     def test_B03_tuple(self):
 164         data=self.read().to_dict();row=self.request(data,"rF");raw=self.state["requests"]["rF"]
 165         self.check(all(row[k]==raw[k] for k in ["rid","origin","attempt_id","release_version"]),"SAVED_TUPLE_EXACT")
 166         self.check(row["request_digest"]==raw["digest"],"ORIGINAL_REQUEST_DIGEST_EXACT")
 167         for field in ["digest","origin","attempt_id","release_version"]:
 168             state=copy.deepcopy(self.state)
 169             if field=="digest":state["requests"]["rF"][field]="0"*64
 170             elif field=="origin":state["requests"]["rF"][field]["grant_id"]="gMissing"
 171             elif field=="attempt_id":state["requests"]["rF"][field]=None
 172             else:state["requests"]["rF"][field]=121
 173             pub=self.read(reader=ReaderSpy(state)).to_dict()
 174             self.check(pub["status"]=="SOURCE_BINDING_CONFLICT","TUPLE_TAMPER_REJECTED")
 175 
 176     def test_B04_original_operation_source(self):
 177         data=self.read().to_dict()
 178         self.check(self.request(data,"rP")["source_rid"] is None,"ISSUE_HAS_NO_PARENT")
 179         self.check(self.request(data,"rF")["operation"]=="refresh" and self.request(data,"rF")["source_rid"]=="rP","SOURCE_DERIVED_FROM_VERIFIED_ORIGINAL")
 180         state=copy.deepcopy(self.state);state["requests"]["rF"]["request"]["payload"]["source_rid"]="rX";self.resign(state,"rF")
 181         data=self.read(reader=ReaderSpy(state)).to_dict()
 182         self.check(self.request(data,"rF")["source_rid"] is None and "SOURCE_REFERENCE_UNAVAILABLE" in data["gap_codes"],"UNAUTHORIZED_PARENT_REMAINS_UNKNOWN")
 183 
 184     def test_B05_grants_and_scope(self):
 185         data=self.read().to_dict();g=data["grants"][0];old=self.state["grants"]["gA"]
 186         self.check(len(data["grants"])==1 and all(g[k]==old[k] for k in ["active","operations","limit","reserved","spent"]),"SCOPED_GRANT_METADATA_EXACT")
 187         scope=copy.deepcopy(self.meta["scope_A"]);scope["generations"]=["genB"]
 188         before=self.reader.calls;data=self.read(scope=scope).to_dict()
 189         self.check(data["status"]=="READ_SCOPE_DENIED" and self.reader.calls==before,"GENERATION_POLICY_CHECKED_BEFORE_READ")
 190 
 191     def test_B06_unknown_refresh(self):
 192         data=self.read().to_dict();ids={x["id"] for x in data["conservative_O_view"]}
 193         self.check("settle:rF" in ids and "await_terminal:rF" in ids,"UNKNOWN_REFRESH_DEBT_PRESERVED")
 194         self.check(data["partial_math"]["c_known"]=={} and "aF" in data["partial_math"]["capacity_unknown"],"NO_GUESSED_CAPACITY")
 195 
 196     def test_B07_unknown_issue(self):
 197         state=copy.deepcopy(self.state);raw=state["requests"]["rF"];raw["request"]["operation"]="issue";raw["request"]["payload"]={};self.resign(state,"rF")
 198         data=self.read(reader=ReaderSpy(state)).to_dict()
 199         self.check(self.request(data,"rF")["operation"]=="issue" and "settle:rF" in {x["id"] for x in data["conservative_O_view"]},"UNKNOWN_ISSUE_PRESERVED")
 200 
 201     def test_B08_double_unknown(self):
 202         state=copy.deepcopy(self.state);raw=state["requests"]["rU"];raw["request"]["operation"]="issue";raw["request"]["payload"]={};raw["phase"]="DISPATCHED_UNKNOWN";raw["result_material"]=None;self.resign(state,"rU")
 203         data=self.read(reader=ReaderSpy(state)).to_dict();ids={x["id"] for x in data["conservative_O_view"]}
 204         self.check({"settle:rF","settle:rU"}<=ids and data["partial_math"]["E"] is None,"ALL_UNKNOWN_SOURCES_HELD")
 205 
 206     def test_B09_third_grant(self):
 207         context=self.context(scope=self.meta["scope_wide"])
 208         data=self.read(scope=self.meta["scope_wide"],context=context,foreign=False).to_dict()
 209         self.check("grant_frontier:gV" in data["open_frontiers"],"AUTHORIZED_THIRD_GRANT_FRONTIER")
 210         data=self.read().to_dict()
 211         self.check("SCOPE_UNIVERSE_INCOMPLETE" in data["gap_codes"],"NARROW_SCOPE_NOT_PROMOTED_TO_GLOBAL")
 212 
 213     def test_B10_late(self):
 214         old=self.read().to_dict();state=copy.deepcopy(self.state);state["requests"]["rF"]["phase"]="QUARANTINED";state["requests"]["rF"]["result_material"]=copy.deepcopy(state["requests"]["rP"]["result_material"])
 215         new=self.read(reader=ReaderSpy(state,121)).to_dict();r=self.request(new,"rF")
 216         self.check(r["origin"]==self.request(old,"rF")["origin"] and r["result_ref"] is not None,"LATE_ORIGINAL_ORIGIN_AND_OPAQUE_RESULT")
 217         self.check("close:rF" in {x["id"] for x in new["conservative_O_view"]},"LATE_MATERIAL_DEBT_ADDED")
 218 
 219     def test_B11_quarantined(self):
 220         data=self.read().to_dict();row=self.request(data,"rU")
 221         self.check(row["phase"]=="QUARANTINED" and row["material_present"] and row["result_ref"].startswith("result:"),"QUARANTINED_METADATA_ONLY")
 222         self.check("close:rU" in {x["id"] for x in data["conservative_O_view"]},"QUARANTINED_HOLD")
 223 
 224     def test_B12_deleted_history(self):
 225         old=self.read().to_dict();self.state["external_AS_missing"]=["synthetic_missing_unit"]
 226         new=self.read().to_dict()
 227         self.check(self.request(old,"rP")["result_ref"]==self.request(new,"rP")["result_ref"],"POSITIVE_LOCAL_HISTORY_NOT_ERASED_BY_POINT_ABSENCE")
 228         self.check(new["partial_math"]["U"] is None and "BIRTH_OR_HISTORY_GAP" in new["gap_codes"],"NO_INVENTED_BIRTH_LEDGER")
 229 
 230     def test_B13_legacy_O(self):
 231         data=self.read().to_dict()
 232         self.check(data["legacy_obligations"]==["rF","rU"],"LEGACY_PHASE_WINDOW_VIEW_EXACT")
 233         self.check(data["typed_obligation_status"]=="TYPED_O_NOT_IMPLEMENTED" and data["obligation_revision"] is None,"NO_SYNTHETIC_PRODUCTION_O_DEFAULT")
 234         self.check("source_hold:account1" in {x["id"] for x in data["conservative_O_view"]},"DERIVED_VIEW_HAS_SOURCE_HOLD")
 235 
 236     def test_B14_projected_additions(self):
 237         state=copy.deepcopy(self.state);state["requests"]["rF"]["phase"]="QUARANTINED";state["requests"]["rF"]["result_material"]=copy.deepcopy(state["requests"]["rP"]["result_material"])
 238         data=self.read(reader=ReaderSpy(state)).to_dict();ids={x["id"] for x in data["conservative_O_view"]}
 239         self.check({"close:rF","await_terminal:rF"}<=ids,"MATERIAL_AND_AUDIT_EXTRAS_STAGED")
 240         self.check("close:rF" not in data["legacy_obligations"] and data["compatibility"]["S1"]["direct_input"] is False,"LEGACY_AND_PROJECTED_CONTEXT_DISTINCT")
 241 
 242     def test_B16_legacy_consumer(self):
 243         data=self.read().to_dict()
 244         self.check(data["schema"]==SCHEMA and data["mode"]==MODE and "approvals" not in data,"NO_IMPERSONATED_LEGACY_STATUS")
 245         self.check(data["compatibility"]["legacy"]["scope"]=="ONE_ATTEMPT_HISTORY_ONLY","OLD_SCOPE_LABEL_PRESERVED")
 246 
 247     def test_B17_expiry(self):
 248         self.state["certificate"]={"valid_until":0,"current_native_eligible":True,"H_T":0}
 249         data=self.read().to_dict()
 250         self.check(data["read_clock"]["native_validity"]=="UNESTABLISHED" and "CURRENTNESS_UNPROVEN" in data["gap_codes"],"OLD_POINT_OR_PROOF_NOT_CURRENT_PERMISSION")
 251 
 252     def test_B18_new_version(self):
 253         first=self.read().to_dict();state=copy.deepcopy(self.state);state["requests"]["rF"]["phase"]="QUARANTINED";state["requests"]["rF"]["result_material"]=copy.deepcopy(state["requests"]["rP"]["result_material"])
 254         second=self.read(reader=ReaderSpy(state,121)).to_dict()
 255         self.check(first["authority_revision"]==120 and second["authority_revision"]==121 and first["snapshot_digest"]!=second["snapshot_digest"],"OLD_SNAPSHOT_IDENTITY_NOT_REUSED")
 256 
 257     def test_B19_authentication_boundary(self):
 258         for bad in [{"actor":"manager","read_ok":True}, True, None]:
 259             context=bad if bad is not None else object()
 260             before=self.reader.calls;data=self.read(context=context).to_dict()
 261             self.check(data["status"]=="READ_CONTEXT_REQUIRED" and self.reader.calls==before,"PAYLOAD_AUTH_FLAGS_HAVE_NO_AUTHORITY")
 262         other=ReaderSpy(copy.deepcopy(self.state));ctx=self.context(self.reader)
 263         data=self.read(reader=other,context=ctx).to_dict()
 264         self.check(data["status"]=="READ_CONTEXT_REQUIRED" and other.calls==0,"CONTEXT_BOUND_TO_EXACT_READER")
 265 
 266     def test_B20_secret_sinks(self):
 267         result=self.read();ctx=self.context()
 268         self.no_secrets(repr(ctx)+repr(self.reader)+repr(result))
 269         for serialize in [lambda:json.dumps(ctx),lambda:pickle.dumps(ctx)]:
 270             try:serialize()
 271             except (TypeError,ReadError) as exc:self.no_secrets(str(exc)+repr(exc))
 272             else:self.check(False,"CONTEXT_SERIALIZATION_MUST_BE_DENIED")
 273         self.no_secrets(pickle.dumps(result).decode("latin1"))
 274         bad=ReaderSpy(copy.deepcopy(self.state));bad.fail_message=self.canaries["labels"]["exception_secret"]
 275         data=self.read(reader=bad).to_dict()
 276         self.check(data["status"]=="READ_SOURCE_UNAVAILABLE","EXCEPTION_TEXT_SANITIZED")
 277         state=copy.deepcopy(self.state);state["requests"]["rF"]["request"]["payload"]["password"]=self.canaries["labels"]["password"]
 278         data=self.read(reader=ReaderSpy(state)).to_dict()
 279         self.check(data["status"]=="SOURCE_BINDING_CONFLICT","UNKNOWN_SENSITIVE_ORIGINAL_FIELD_REJECTED")
 280         public=result.to_dict();public["requests"][0]["handle"]=self.canaries["labels"]["handle_A"]
 281         public["snapshot_digest"]=hashlib.sha256(b"dsat-authority-read/1:snapshot\0"+canonical({k:v for k,v in public.items() if k!="snapshot_digest"})).hexdigest()
 282         try:StagingSnapshot(public)
 283         except ReadError as exc:self.no_secrets(str(exc)+repr(exc))
 284         else:self.check(False,"NESTED_UNKNOWN_PUBLIC_FIELD_DENIED")
 285 
 286     def test_B21_no_source_upgrade(self):
 287         self.state["source_confirmed"]=True;self.state["contract"]={"source_complete":True,"capacity_complete":True,"frontier_complete":True};self.state["H_T"]=0
 288         data=self.read().to_dict()
 289         self.check("SOURCE_COMPLETENESS_UNPROVEN" in data["gap_codes"] and data["math_input"] is None,"SOURCE_FLAGS_NEVER_CREATE_D_FIN")
 290 
 291     def test_B22_point_not_frame(self):
 292         data=self.read().to_dict()
 293         self.check(data["disposals"][0]["point_observations"]["introspection_active"] is False,"POINT_FACT_PRESERVED")
 294         self.check(data["partial_math"]["D_P"] is None and "SUSTAINED_INACTIVITY_UNPROVEN" in data["gap_codes"],"NO_DISPOSED_TO_SUSTAINED_D")
 295 
 296     def test_B23_frontier(self):
 297         self.state["grants"]["gA"]["active"]=True
 298         data=self.read().to_dict()
 299         self.check("grant_frontier:gA" in data["open_frontiers"],"ACTIVE_CREATOR_FRONTIER_RETAINED")
 300         self.check(data["windows"][0]["active"] is True,"LOCAL_WINDOW_IS_POINT_LOCAL_FACT")
 301 
 302     def test_B24_external_change(self):
 303         first=self.read().to_dict();self.state["external_AS_generation"]=2;self.state["old_handler_may_create"]=True
 304         second=self.read().to_dict()
 305         self.check(first["authority_revision"]==second["authority_revision"]==120,"AS_CHANGE_NOT_FAKED_IN_LOCAL_A")
 306         self.check("NATIVE_CURRENTNESS_UNPROVEN" in second["gap_codes"],"LOCAL_A_NOT_NATIVE_FRAME")
 307 
 308     def test_B25_complete_request(self):
 309         for flag in ["global_complete","current_native_eligible","write_O"]:
 310             request=copy.deepcopy(self.meta["scope_A"]);request[flag]=True
 311             before=self.reader.calls;data=self.read(scope=request).to_dict()
 312             self.check(data["status"]=="UNSUPPORTED_READ_REQUEST" and self.reader.calls==before,"STRONG_OR_WRITE_REQUEST_DENIED_BEFORE_READ")
 313 
 314     def test_B26_old_closed(self):
 315         for rid in ["rF","rU"]:
 316             self.state["requests"][rid]["phase"]="DISPOSED"
 317             self.state["requests"][rid]["result_material"]=copy.deepcopy(self.state["requests"]["rP"]["result_material"])
 318         window=self.state["reconciliation_windows"]["account1"];window["active"]=False
 319         window["receipt"]={"schema":"native-attempt-closure/1","claim":"CLOSED","private_key":self.canaries["labels"]["private_key"]}
 320         data=self.read().to_dict()
 321         self.check(data["legacy_obligations"]==[] and len(data["conservative_O_view"])>0,"EMPTY_LEGACY_VIEW_NOT_GLOBAL_EMPTY")
 322         self.check(data["windows"][0]["legacy_receipt_summary"]["claim"]=="CLOSED","OLD_HISTORY_CLAIM_PRESERVED_WITH_SCOPE")
 323 
 324     def test_B29_handle_binding(self):
 325         first=self.read().to_dict();state=copy.deepcopy(self.state);state["grants"]["gA"]["handle"]=self.canaries["labels"]["handle_B"]
 326         self.check(self.read(reader=ReaderSpy(state)).to_dict()["status"]=="SOURCE_BINDING_CONFLICT","HANDLE_CHANGE_WITHOUT_VALID_ORIGINAL_DENIED")
 327         for rid,raw in state["requests"].items():
 328             if raw["origin"]["grant_id"]=="gA":raw["request"]["handle"]=state["grants"]["gA"]["handle"];self.resign(state,rid)
 329         second=self.read(reader=ReaderSpy(state)).to_dict()
 330         self.check(self.request(first,"rF")["request_digest"]!=self.request(second,"rF")["request_digest"],"ORIGINAL_WHOLE_BODY_DIGEST_STILL_BINDS_HANDLE")
 331         self.check("original_request" not in self.request(second,"rF") and "handle_digest" not in self.request(second,"rF"),"NO_HANDLE_OR_HANDLE_HASH_SUBSTITUTE")
 332 
 333     def test_B30_reserved_queue(self):
 334         state=copy.deepcopy(self.state);g=state["grants"]["gA"];g.update(active=True,limit=1,reserved=1,spent=0)
 335         raw=copy.deepcopy(state["requests"]["rP"]);raw.update(rid="rQ",phase="QUEUED",attempt_id=None,release_version=None,result_material=None,result_digest=None);raw["request"]["rid"]="rQ"
 336         state["grants"]={"gA":g};state["requests"]={"rQ":raw};state["disposals"]={};state["reconciliation_windows"]={};self.resign(state,"rQ")
 337         data=self.read(reader=ReaderSpy(state)).to_dict()
 338         self.check(data["legacy_obligations"]==[] and "queued_creator:rQ" in data["open_frontiers"],"ZERO_FREE_BUDGET_STILL_HAS_QUEUED_CREATOR")
 339 
 340     def test_B31_quota_and_parallel_read(self):
 341         reader=ReaderSpy(copy.deepcopy(self.state),operation_limit=7)
 342         self.ready(self.read(reader=reader));before=reader.calls
 343         data=self.read(reader=reader).to_dict()
 344         self.check(data["status"]=="READ_BUDGET_DENIED" and reader.calls==before,"WRITE_HEADROOM_RESERVED_WITH_NO_RETRY")
 345         context=self.context(self.reader);before=canonical(self.reader.state)
 346         barrier=threading.Barrier(4)
 347         def one(_):
 348             worker=threading.get_ident()
 349             barrier.wait(timeout=5)
 350             return worker,[read_dsat_authority_snapshot(self.reader,self.meta["scope_A"],context) for _ in range(3)]
 351         started=time.perf_counter_ns()
 352         with ThreadPoolExecutor(max_workers=4) as executor:batches=list(executor.map(one,range(4)))
 353         results=[result for _,batch in batches for result in batch]
 354         elapsed=time.perf_counter_ns()-started
 355         self.check(len({worker for worker,_ in batches})==4,"FOUR_LIVE_READ_THREADS_AT_START_BARRIER")
 356         self.check(all(r.to_dict()["authority_revision"]==120 for r in results) and self.reader.lock.max_depth==1,"PARALLEL_READS_SERIALIZED_UNDER_SOURCE_LOCK")
 357         self.check(canonical(self.reader.state)==before and self.reader.forbidden_calls==0,"PARALLEL_WORLD_AND_EVENTS_UNCHANGED")
 358         for result in results:self.no_secrets(result.to_json().decode());self.no_foreign(result.to_json().decode())
 359         self.observed.append({"operation":"parallel_reads","results":[x.to_dict() for x in results],
 360                               "source_reads":12,"world_unchanged":True,"total_ns":elapsed,"secret_scan":"CLEAN",
 361                               "thread_identifiers":sorted({worker for worker,_ in batches}),"start_barrier_parties":4})
 362         output=self.read().to_dict();output["requests"][0]["origin"]["task"]="client_mutated";output["grants"][0]["operations"].append("client_mutated")
 363         self.check(canonical(self.reader.state)==before,"NO_MUTABLE_ALIAS_TO_INPUT")
 364 
 365     def test_B32_downstream_gates(self):
 366         from auth_lifecycle.online_state.dsat_projection import project_evidence
 367         from auth_lifecycle.online_state.dsat_types import InputError, normalize_math
 368         from auth_lifecycle.online_state.dsat_commit_types import CommitError, Proposal, raw_obligation
 369         data=self.read().to_dict();failure=project_evidence(data,{})
 370         self.check(failure["math_ready"] is False and failure["native_admission"]=="SOURCE_OR_REFINEMENT_GAP","S1_REAL_STAGING_DIRECT_INPUT_DENIED")
 371         try:normalize_math(data["partial_math"])
 372         except InputError:pass
 373         else:self.check(False,"PARTIAL_UNKNOWN_NOT_COERCED_TO_FINITE_MATH")
 374         try:Proposal.parse(data)
 375         except CommitError:pass
 376         else:self.check(False,"STAGING_NOT_S3_COMMIT_PROPOSAL")
 377         for item in data["conservative_O_view"]:raw_obligation(item)
 378         self.check(all(v["direct_input"] is False for k,v in data["compatibility"].items() if k!="legacy"),"COMPATIBILITY_LIMITS_EXPLICIT")
 379 
 380     def test_B33_all_collections_scoped(self):
 381         window=self.state["reconciliation_windows"]["account1"];window["unknown_creators_at_open"].append("rB")
 382         data=self.read().to_dict()
 383         self.check(len(data["disposals"])==1 and data["disposals"][0]["rid"]=="rP","DISPOSALS_FILTERED_AS_WELL_AS_REQUESTS")
 384         self.check(data["windows"][0]["scoped_creators"]==["rF"] and data["windows"][0]["source_scope_complete"] is False,"FOREIGN_WINDOW_MEMBERS_NOT_EXPORTED_OR_COUNTED")
 385         window["target_rid"]="rB";data=self.read().to_dict()
 386         self.check(data["windows"]==[],"FOREIGN_TARGET_WINDOW_NOT_EXPORTED")
 387 
 388     def test_B34_locator_not_instance(self):
 389         first=self.read().to_dict();ctx=self.context(authority_locator_ref="authority:fixture2")
 390         second=self.read(context=ctx).to_dict()
 391         self.check(first["source"]["authority_instance"] is None and second["source"]["authority_instance"] is None,"STABLE_INSTANCE_NOT_FABRICATED")
 392         self.check(first["snapshot_digest"]!=second["snapshot_digest"] and self.request(first,"rP")["result_ref"]!=self.request(second,"rP")["result_ref"],"SOURCE_LOCATOR_NAMESPACES_METADATA_REFS")
 393 
 394     def test_B35_provider_history_gap(self):
 395         self.state["provider_last_result"]={"attempt_id":"aF","received":True,"access_token":self.canaries["labels"]["access_token"]}
 396         self.state["provider_receipt_count"]=2
 397         data=self.read().to_dict()
 398         self.check("PROVIDER_HISTORY_EXPORT_REQUIRED" in data["gap_codes"] and data["partial_math"]["U"] is None,"LAST_PROVIDER_RESULT_NOT_COMPLETE_MULTIEFFECT_HISTORY")
 399 
 400     def test_B36_resource_and_schema(self):
 401         for limits in [ReadLimits(scoped_records=1),ReadLimits(output_bytes=4096)]:
 402             data=self.read(limits=limits).to_dict()
 403             self.check(data["status"]=="RESOURCE_LIMIT" and data["conservative_O_view"] is None,"RESOURCE_FAILURE_NOT_CERTIFIED_EMPTY")
 404         for key in ["grants","requests"]:
 405             state=copy.deepcopy(self.state);del state[key];data=self.read(reader=ReaderSpy(state)).to_dict()
 406             self.check(data["status"]=="SNAPSHOT_INCOMPLETE" and data["legacy_obligations"] is None,"MISSING_STATE_NOT_EMPTY_LEDGER")
 407         self.state["authority_instance"]="forged_instance";self.state["dsat"]={"O":[],"obligation_revision":99}
 408         data=self.read().to_dict();self.check(data["source"]["authority_instance"] is None and data["obligation_revision"] is None,"UNKNOWN_NEW_FIELDS_DO_NOT_UPGRADE_LEGACY_CONTRACT")
 409         state=copy.deepcopy(self.state);state["schema"]="unreviewed-schema3"
 410         self.check(self.read(reader=ReaderSpy(state)).to_dict()["status"]=="UNSUPPORTED_SOURCE_SCHEMA","UNREVIEWED_SCHEMA_DENIED")
 411         module=Path(__file__).parents[1]/"src/auth_lifecycle/online_state/dsat_authority_read.py"
 412         tree=ast.parse(module.read_text(encoding="utf-8"))
 413         forbidden={"storage","services","native_provider","sqlite3","networkx"}
 414         imports=[n.module or "" for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]+[a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
 415         self.check(not any(set(name.split(".")) & forbidden for name in imports),"IMPORT_CLOSURE_EXCLUDES_RUNTIME_SERVICES")
 416         self.check(staging_schema()["additionalProperties"] is False,"PUBLIC_SCHEMA_CLOSED")
```

## T02: D:\毕业设计\auth-lifecycle\scripts\run_dsat_authority_read_tests.py
SHA-256: c8c2d6575449885e9b8ab9af567bcdc2d92e35577aa2b5a3ec6fa17cdbd3bb36

```text
   1 """R12 bounded B1-only runner; denies SQLite, network, native services and children."""
   2 import argparse
   3 import ast
   4 import _thread
   5 import datetime
   6 import hashlib
   7 import importlib.util
   8 import json
   9 import os
  10 from pathlib import Path
  11 import sys
  12 import threading
  13 import time
  14 import traceback
  15 import unittest
  16 
  17 
  18 PROJECT = Path(__file__).absolute().parent.parent
  19 R11 = PROJECT.parent/"research_g2_dsat_implementation/2026-11-10_r11"
  20 RECORD_ROOT = PROJECT.parent/"research_g2_dsat_implementation/2026-11-11_r12"
  21 ARTIFACT_ROOT = PROJECT.parent/"research_g2_dsat_implementation/2026-11-10_r12_b1"
  22 FIXTURES = PROJECT/"tests/fixtures/dsat_authority_read"
  23 sys.dont_write_bytecode = True
  24 AUDIT = {"sqlite_attempts":0,"network_attempts":0,"process_attempts":0,"forbidden_file_attempts":0,"violations":[]}
  25 SECRETS = []
  26 
  27 
  28 def sha(path):
  29     return hashlib.sha256(path.read_bytes()).hexdigest()
  30 
  31 
  32 def load(path):
  33     return json.loads(path.read_text(encoding="utf-8"))
  34 
  35 
  36 def checked_artifact(path):
  37     path=Path(path).absolute()
  38     if not path.is_relative_to(ARTIFACT_ROOT):
  39         raise RuntimeError("ARTIFACT_PATH_DENIED")
  40     for part in (path,*path.parents):
  41         if part.exists() and (part.is_symlink() or part.lstat().st_file_attributes & 0x400):
  42             raise RuntimeError("ARTIFACT_REPARSE_DENIED")
  43     if path.resolve()!=path:
  44         raise RuntimeError("ARTIFACT_PATH_DENIED")
  45     return path
  46 
  47 
  48 def audit(event,args):
  49     if event.startswith("sqlite3.connect"):
  50         AUDIT["sqlite_attempts"]+=1;AUDIT["violations"].append("SQLITE_DENIED")
  51         raise RuntimeError("SQLITE_DENIED")
  52     if event.startswith("socket."):
  53         AUDIT["network_attempts"]+=1;AUDIT["violations"].append("NETWORK_DENIED")
  54         raise RuntimeError("NETWORK_DENIED")
  55     if event in {"subprocess.Popen","os.system","os.startfile"}:
  56         AUDIT["process_attempts"]+=1;AUDIT["violations"].append("CHILD_PROCESS_DENIED")
  57         raise RuntimeError("CHILD_PROCESS_DENIED")
  58     if event=="open" and isinstance(args[0],(str,bytes,os.PathLike)):
  59         raw=os.fsdecode(args[0]);path=Path(raw).absolute();text=raw.replace("\\","/").lower()
  60         if "/.runtime/" in text or "/secure/" in text or path.suffix.lower() in {".db",".sqlite3",".sqlite",".key",".aes",".pem",".pfx"}:
  61             AUDIT["forbidden_file_attempts"]+=1;AUDIT["violations"].append("PRIVATE_OR_DATABASE_FILE_DENIED")
  62             raise RuntimeError("PRIVATE_OR_DATABASE_FILE_DENIED")
  63         mode,flags=args[1],args[2]
  64         writing=(type(mode)is str and any(c in mode for c in "wax+")) or (type(flags)is int and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
  65         if writing and not path.is_relative_to(ARTIFACT_ROOT):
  66             AUDIT["forbidden_file_attempts"]+=1;AUDIT["violations"].append("WRITE_OUTSIDE_ARTIFACT_ROOT")
  67             raise RuntimeError("WRITE_OUTSIDE_ARTIFACT_ROOT")
  68 
  69 
  70 def write(path,data):
  71     path=checked_artifact(path)
  72     path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  73 
  74 
  75 def preflight():
  76     approval=load(RECORD_ROOT/"APPROVAL_RECEIPT.json")
  77     if approval["approved"] is not True or approval["stage"]!="R11 frozen B1 development and offline doubles only":
  78         raise RuntimeError("B1_APPROVAL_REQUIRED")
  79     if sha(Path(approval["task_path"]))!=approval["task_sha256"]:
  80         raise RuntimeError("APPROVAL_SOURCE_CHANGED")
  81     baseline=load(RECORD_ROOT/"sources/PRECHECK_LOCK.json")
  82     for entry in baseline["checks"]:
  83         if sha(Path(entry["path"]))!=entry["expected"]:
  84             raise RuntimeError("OLD_SOURCE_OR_HISTORY_CHANGED")
  85     plan=load(R11/"S3B_TEST_PLAN.json")
  86     if len(plan["cases"])!=36 or sum(x["stage"]=="B1" for x in plan["cases"])!=33:
  87         raise RuntimeError("FROZEN_TEST_SCOPE_CHANGED")
  88     return plan,baseline
  89 
  90 
  91 class Result(unittest.TextTestResult):
  92     def __init__(self,*args,**kwargs):
  93         super().__init__(*args,**kwargs);self.rows=[];self.started=0;self.redactions=0
  94     def startTest(self,test):
  95         self.started=time.perf_counter_ns();super().startTest(test)
  96     def _exc_info_to_string(self,err,test):
  97         text=super()._exc_info_to_string(err,test)
  98         for value in SECRETS:
  99             if value in text:
 100                 text=text.replace(value,"[REDACTED_SYNTHETIC_CANARY]");self.redactions+=1
 101         return text
 102     def record(self,test,status,detail=None):
 103         row={"id":test._testMethodName.split("_")[1],"status":status,"executed":True,
 104              "elapsed_ns":time.perf_counter_ns()-self.started}
 105         if detail:row["detail"]=detail
 106         self.rows.append(row)
 107     def addSuccess(self,test):super().addSuccess(test);self.record(test,"PASS")
 108     def addFailure(self,test,err):
 109         super().addFailure(test,err);self.record(test,"FAIL",self._exc_info_to_string(err,test))
 110     def addError(self,test,err):
 111         super().addError(test,err);self.record(test,"ERROR",self._exc_info_to_string(err,test))
 112     def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,"SKIP",reason)
 113 
 114 
 115 def main():
 116     start=time.perf_counter_ns();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 117     plan,baseline=preflight()
 118     checked_artifact(ARTIFACT_ROOT).mkdir(exist_ok=True)
 119     index=1
 120     while (ARTIFACT_ROOT/("run_%03d"%index)).exists():index+=1
 121     run=checked_artifact(ARTIFACT_ROOT/("run_%03d"%index));run.mkdir()
 122     source_paths=[PROJECT/"src/auth_lifecycle/online_state/dsat_authority_read.py",
 123                   PROJECT/"tests/test_dsat_authority_read.py",Path(__file__).absolute()]
 124     code=[{"path":str(p),"sha256":sha(p)} for p in source_paths]
 125     inputs=[{"path":str(p),"sha256":sha(p)} for p in sorted(FIXTURES.glob("*.json"))]
 126     snapshot=run/"code_snapshot";snapshot.mkdir()
 127     for path in source_paths:(snapshot/(path.name+".txt")).write_bytes(path.read_bytes())
 128     write(run/"RUN_START.json",{"command":[sys.executable,"-B",str(Path(__file__).absolute())],
 129           "python":sys.version,"date_china":"2026-11-11","started_utc":started,"code":code,"inputs":inputs,
 130           "record_root":str(RECORD_ROOT),"artifact_root_frozen_R11":str(ARTIFACT_ROOT)})
 131     SECRETS.extend(load(FIXTURES/"CANARIES.json")["sensitive_values"])
 132     timer=threading.Timer(max(.01,120-(time.perf_counter_ns()-start)/1e9),_thread.interrupt_main)
 133     timer.daemon=True;timer.start()
 134     try:
 135         sys.path.insert(0,str(PROJECT/"src"))
 136         name="test_dsat_authority_read"
 137         spec=importlib.util.spec_from_file_location(name,PROJECT/"tests"/(name+".py"))
 138         module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 139         module.configure(plan,FIXTURES)
 140         suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.B1Cases)
 141         if suite.countTestCases()!=33:
 142             raise RuntimeError("B1_TEST_DENOMINATOR_CHANGED")
 143         with (run/"stdout.log").open("w",encoding="utf-8") as output:
 144             actual=unittest.TextTestRunner(stream=output,verbosity=2,resultclass=Result).run(suite)
 145         rows={x["id"]:x for x in actual.rows}
 146         final=[]
 147         for case in plan["cases"]:
 148             if case["stage"]=="B2":
 149                 row={"id":case["id"],"status":"BLOCKED","executed":False,"reason":"R11_B2_NOT_AUTHORIZED"}
 150             else:row=rows.get(case["id"],{"id":case["id"],"status":"NOT_RUN","executed":False})
 151             final.append({**row,"R11_original_case":case})
 152         counts={s:sum(x["status"]==s for x in final) for s in ["PASS","FAIL","ERROR","SKIP","BLOCKED","NOT_RUN"]}
 153         preflight()
 154         if any(sha(Path(x["path"]))!=x["sha256"] for x in code):raise RuntimeError("CODE_CHANGED_DURING_TEST")
 155         sink_text=(run/"stdout.log").read_text(encoding="utf-8")+json.dumps(module.DETAILS,ensure_ascii=True)
 156         clean=all(value not in sink_text for value in SECRETS)
 157         result={"schema":"r12-b1-actual-run/1","run":str(run),"started_utc":started,
 158                 "finished_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"date_china":"2026-11-11",
 159                 "python":sys.version,"command":[sys.executable,"-B",str(Path(__file__).absolute())],
 160                 "elapsed_ns":time.perf_counter_ns()-start,"frozen_denominator":36,"authorized_B1_denominator":33,
 161                 "executed":len(actual.rows),"counts":counts,"cases":final,"details":module.DETAILS,
 162                 "code_hashes":code,"input_hashes":inputs,"historical_hashes_checked":len(baseline["checks"]),
 163                 "scope_audit":AUDIT,"public_sink_scan":"CLEAN" if clean else "FAIL",
 164                 "failure_log_canary_redactions":actual.redactions,
 165                 "measurement_clocks":{name:{"implementation":time.get_clock_info(name).implementation,
 166                      "resolution_seconds":time.get_clock_info(name).resolution,
 167                      "monotonic":time.get_clock_info(name).monotonic} for name in ["perf_counter","monotonic"]},
 168                 "B2_cases_not_executed":["B15","B27","B28"],"S2_solver_or_checker_runs":0,
 169                 "real_authority_reads":0,"production_writes":0,"S3B2_operations":0,"S5_operations":0}
 170         result["passed_authorized_scope"]=counts=={"PASS":33,"FAIL":0,"ERROR":0,"SKIP":0,"BLOCKED":3,"NOT_RUN":0} and clean and not AUDIT["violations"]
 171         write(run/"RESULTS.json",result)
 172         from auth_lifecycle.online_state.dsat_authority_read import staging_schema
 173         write(run/"B1_STAGING_SCHEMA.json",staging_schema())
 174     except BaseException:
 175         text=traceback.format_exc()
 176         for value in SECRETS:text=text.replace(value,"[REDACTED_SYNTHETIC_CANARY]")
 177         write(run/"EARLY_FAILURE.json",{"status":"EARLY_FAILURE","traceback":text,"scope_audit":AUDIT})
 178         raise
 179     finally:timer.cancel()
 180     history_path=ARTIFACT_ROOT/"TEST_RUNS.json"
 181     history=load(history_path) if history_path.exists() else {"schema":"r12-b1-runs/1","runs":[]}
 182     history["runs"].append({"path":str(run/"RESULTS.json"),"sha256":sha(run/"RESULTS.json"),"counts":counts,"passed":result["passed_authorized_scope"]})
 183     write(history_path,history)
 184     print(json.dumps({"run":str(run),"counts":counts,"executed":len(actual.rows),"passed_authorized_scope":result["passed_authorized_scope"]}))
 185     return 0 if result["passed_authorized_scope"] else 1
 186 
 187 
 188 if __name__=="__main__":
 189     sys.addaudithook(audit)
 190     argparse.ArgumentParser(description=__doc__).parse_args()
 191     raise SystemExit(main())
```
