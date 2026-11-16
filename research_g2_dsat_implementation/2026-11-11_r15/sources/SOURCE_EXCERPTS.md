# R15 source excerpts: static text only

## C01: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\storage.py
SHA-256: 2d17cf95d7d724d8debbeb47c2df28cfd537aa696bde47edb98908170a12de83

```text
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
```

## C02: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\services.py
SHA-256: d8ea05120fc8559a95050e4c71a094eefb73e29d22e1de66494d8c8e1975993a

```text
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

## C03: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\protocol.py
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

## C04: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\lab.py
SHA-256: ccf0c4ad6d21106fd1c0ef5aedcdad5b30bba49b2bf2f526ea69d79899409f26

```text
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
```

## C05: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\dsat_authority_read.py
SHA-256: 3a6dbf67f4c9ee9df326607485ef78b995c27c1de18dfa5536b36705d27dfc83

```text
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
```

## C06: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\dsat_authority_read_host.py
SHA-256: c19d81ff9cb69508a3c1a818366645d4ab5cb9a3616fdc58f096d04f55e1ea11

```text
   1 """H1 internal Authority host; offline integration, no import-time I/O.
   2 
   3 Authenticated facts are issued by trusted host code outside request bodies.
   4 The identity registry models that boundary; deployment authentication is H2 work.
   5 This module opens no storage, key, network, service, or database connection.
   6 """
   7 from dataclasses import dataclass
   8 import json
   9 import re
  10 import threading
  11 import time
  12 
  13 from .dsat_authority_read import (
  14     BASE_GAPS, ERRORS, MAX_REVISION, ReadLimits, ReadScope, StagingSnapshot,
  15     TrustedReadContext, read_dsat_authority_snapshot,
  16 )
  17 from .protocol import canonical
  18 
  19 
  20 SCHEMA = "dsat-host-read-summary/1"
  21 RIGHT = "staging_read_metadata"
  22 HOST_ERRORS = {
  23     "HOST_IDENTITY_REQUIRED", "HOST_PERMISSION_DENIED", "HOST_PERMIT_EXPIRED",
  24     "HOST_PERMIT_REPLAY", "HOST_SOURCE_MISMATCH", "HOST_CONNECTION_NOT_IDLE",
  25     "HOST_DEADLINE_EXCEEDED", "INCONCLUSIVE_CONCURRENT_CHANGE", "HOST_SUMMARY_REFUSED",
  26 }
  27 STATUSES = ERRORS | HOST_ERRORS | {"STAGING_READY_WITH_GAPS"}
  28 GAPS = set(BASE_GAPS) | STATUSES | {"SOURCE_REFERENCE_UNAVAILABLE", "QUEUED_CREATOR_FRONTIER"}
  29 
  30 
  31 class HostReadError(ValueError):
  32     def __init__(self, code):
  33         self.code = code if code in STATUSES else "HOST_SUMMARY_REFUSED"
  34         super().__init__(self.code)
  35 
  36 
  37 def _id(value):
  38     if type(value) is not str or re.fullmatch(r"[A-Za-z0-9_.:-]{1,160}", value) is None:
  39         raise HostReadError("UNSUPPORTED_READ_REQUEST")
  40     return value
  41 
  42 
  43 def _nat(value):
  44     if type(value) is not int or not 0 <= value <= MAX_REVISION:
  45         raise HostReadError("RESOURCE_LIMIT")
  46     return value
  47 
  48 
  49 def _scope(value):
  50     try:
  51         scope = ReadScope.parse(value)
  52     except Exception:
  53         raise HostReadError("READ_SCOPE_DENIED") from None
  54     if any(len(getattr(scope, k)) != 1 for k in ("tasks", "callers", "generations")):
  55         raise HostReadError("READ_SCOPE_DENIED")
  56     return scope
  57 
  58 
  59 def _scope_key(scope):
  60     return (scope.account, scope.audience, *scope.tasks, *scope.callers, *scope.generations)
  61 
  62 
  63 class _HostCapability:
  64     __slots__ = ()
  65 
  66     def __init__(self, *args, **kwargs):
  67         raise HostReadError("HOST_IDENTITY_REQUIRED")
  68 
  69     def __repr__(self):
  70         return "<HostCapability redacted>"
  71 
  72     def __reduce_ex__(self, protocol):
  73         raise TypeError("HOST_CAPABILITY_NOT_SERIALIZABLE")
  74 
  75 
  76 class VerifiedLocalCaller(_HostCapability):
  77     __slots__ = ()
  78 
  79 
  80 class HostReadPermit(_HostCapability):
  81     __slots__ = ()
  82 
  83 
  84 class HostReadPolicy:
  85     """Host-owned registry; all issuing/updating methods are trusted internal APIs.
  86 
  87     Possession of Python execution in this process remains a trust assumption.
  88     RPC authentication must happen before bind_authenticated_caller is called.
  89     """
  90     def __init__(self, epoch_ref, clock=time.monotonic_ns):
  91         self.epoch_ref = _id(epoch_ref)
  92         self.clock = clock
  93         self.lock = threading.RLock()
  94         self._identities, self._rules, self._permits = {}, {}, {}
  95         self._version = 0
  96         self._sequence = 0
  97 
  98     def bind_authenticated_caller(self, *, principal_ref, actor, transport_ref, expires_ns):
  99         with self.lock:
 100             if len(self._identities) >= 4096:
 101                 raise HostReadError("RESOURCE_LIMIT")
 102             fact = (_id(principal_ref), _id(actor), _id(transport_ref), _nat(expires_ns))
 103             caller = object.__new__(VerifiedLocalCaller)
 104             self._identities[caller] = fact
 105             return caller
 106 
 107     def allow(self, *, principal_ref, actor, transport_ref, scope, grant_ref,
 108               scope_ref, expires_ns, rights=(RIGHT,)):
 109         with self.lock:
 110             scope = _scope(scope)
 111             rights = tuple(rights)
 112             if any(type(x) is not str or x != RIGHT for x in rights):
 113                 raise HostReadError("HOST_PERMISSION_DENIED")
 114             self._version += 1
 115             self._rules[(_id(principal_ref), _scope_key(scope))] = {
 116                 "actor": _id(actor), "transport": _id(transport_ref), "scope": scope,
 117                 "grant": _id(grant_ref), "scope_ref": _id(scope_ref), "rights": rights,
 118                 "expires": _nat(expires_ns), "version": self._version,
 119             }
 120 
 121     def revoke(self, principal_ref, scope):
 122         with self.lock:
 123             self._rules.pop((principal_ref, _scope_key(_scope(scope))), None)
 124             self._version += 1
 125 
 126     def revoke_identity(self, caller):
 127         with self.lock:
 128             self._identities.pop(caller, None)
 129 
 130     def _resolve(self, caller, scope):
 131         if type(caller) is not VerifiedLocalCaller or caller not in self._identities:
 132             raise HostReadError("HOST_IDENTITY_REQUIRED")
 133         principal, actor, transport, expires = self._identities[caller]
 134         now = _nat(self.clock())
 135         if now >= expires:
 136             raise HostReadError("HOST_PERMIT_EXPIRED")
 137         rule = self._rules.get((principal, _scope_key(scope)))
 138         if rule is None or RIGHT not in rule["rights"]:
 139             raise HostReadError("HOST_PERMISSION_DENIED")
 140         if actor != rule["actor"] or transport != rule["transport"]:
 141             raise HostReadError("HOST_PERMISSION_DENIED")
 142         if now >= rule["expires"]:
 143             raise HostReadError("HOST_PERMIT_EXPIRED")
 144         return principal, rule
 145 
 146     def __repr__(self):
 147         return "<HostReadPolicy redacted>"
 148 
 149     def __reduce_ex__(self, protocol):
 150         raise TypeError("HOST_POLICY_NOT_SERIALIZABLE")
 151 
 152 
 153 @dataclass(frozen=True)
 154 class HostReadLimits:
 155     staging_bytes: int = 65536
 156     scoped_records: int = 32
 157     summary_bytes: int = 4096
 158     soft_deadline_ns: int = 10_000_000_000
 159 
 160     def __post_init__(self):
 161         ReadLimits(self.staging_bytes, self.scoped_records, 6)
 162         if (type(self.summary_bytes) is not int or not 2048 <= self.summary_bytes <= 4096
 163                 or type(self.scoped_records) is not int or not 1 <= self.scoped_records <= 32
 164                 or type(self.soft_deadline_ns) is not int or not 1 <= self.soft_deadline_ns <= 10_000_000_000):
 165             raise HostReadError("RESOURCE_LIMIT")
 166 
 167 
 168 def summary_schema():
 169     """Closed R13 shape; integer maxima are exact Python integers."""
 170     def obj(props):
 171         return {"type": "object", "additionalProperties": False,
 172                 "required": list(props), "properties": props}
 173     ident = {"type": "string", "minLength": 1, "maxLength": 160,
 174              "pattern": r"^[A-Za-z0-9_.:-]+$"}
 175     number = {"type": ["integer", "null"], "minimum": 0, "maximum": MAX_REVISION}
 176     boolean = {"type": ["boolean", "null"]}
 177     observed = obj({"domain": {"const": "monotonic_ns"}, "epoch_ref": ident,
 178                     "lower": number, "upper": number, "native_validity": {"const": "UNESTABLISHED"}})
 179     audit = obj({
 180         "source_sql_count": {"type": "integer", "minimum": 0, "maximum": 4},
 181         "source_read_count": {"type": "integer", "minimum": 0, "maximum": 1},
 182         "source_operations_delta": number,
 183         "key_read_count": {"type": ["integer", "null"], "minimum": 0, "maximum": 1},
 184         "key_count_basis": {"enum": ["PINNED_PATH_BOUND", "MEASURED_APPROVED_TELEMETRY", "NOT_OBSERVED"]},
 185         "bound_request_count": {"type": ["integer", "null"], "minimum": 0, "maximum": 32},
 186         "world_row_unchanged": boolean, "authority_events_count_unchanged": boolean,
 187         "authority_events_max_unchanged": boolean, "connection_total_changes_unchanged": boolean,
 188         "observed_sql_schema_version": {"type": ["integer", "null"], "minimum": 0, "maximum": 2147483647},
 189         "secret_scan_status": {"enum": ["CLEAN", "REFUSED", "NOT_RUN"]},
 190         "elapsed_ns": number, "deadline_exceeded": {"type": "boolean"}, "permit_consumed": {"type": "boolean"},
 191     })
 192     return obj({
 193         "schema": {"const": SCHEMA}, "execution_ref": ident, "status": {"enum": sorted(STATUSES)},
 194         "authority_revision": number, "authority_instance": {"type": "null"},
 195         "obligation_revision": {"type": "null"},
 196         "snapshot_digest": {"type": ["string", "null"], "pattern": "^[0-9a-f]{64}$"},
 197         "read_scope_ref": ident, "observed_at": {"anyOf": [{"type": "null"}, observed]},
 198         "source_contract": {"enum": ["legacy-authority-state/1", None]},
 199         "source_binding_status": {"enum": ["MATCHED", "NOT_APPLICABLE_EMPTY_SCOPE", "UNAVAILABLE"]},
 200         "missing_fields": {"type": "array", "uniqueItems": True, "maxItems": 64,
 201                            "items": {"enum": sorted(GAPS)}},
 202         "native_currentness_status": {"const": "UNPROVEN"}, "math_ready": {"const": False},
 203         "current_native_eligible": {"const": False}, "global_complete": {"const": False},
 204         "authority_write_action": {"const": "NONE"}, "audit": audit,
 205     })
 206 
 207 
 208 def _validate(value, schema, depth=0):
 209     if depth > 20:
 210         raise HostReadError("HOST_SUMMARY_REFUSED")
 211     if "anyOf" in schema:
 212         for option in schema["anyOf"]:
 213             try:
 214                 _validate(value, option, depth + 1)
 215                 return
 216             except HostReadError:
 217                 pass
 218         raise HostReadError("HOST_SUMMARY_REFUSED")
 219     if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
 220         raise HostReadError("HOST_SUMMARY_REFUSED")
 221     if "enum" in schema and not any(type(value) is type(x) and value == x for x in schema["enum"]):
 222         raise HostReadError("HOST_SUMMARY_REFUSED")
 223     actual = {dict: "object", list: "array", str: "string", int: "integer", bool: "boolean", type(None): "null"}.get(type(value))
 224     types = schema.get("type", [])
 225     types = [types] if type(types) is str else types
 226     if types and actual not in types:
 227         raise HostReadError("HOST_SUMMARY_REFUSED")
 228     if value is None:
 229         return
 230     if actual == "object":
 231         if set(value) != set(schema["properties"]):
 232             raise HostReadError("HOST_SUMMARY_REFUSED")
 233         for key in value:
 234             _validate(value[key], schema["properties"][key], depth + 1)
 235     elif actual == "array":
 236         if len(value) > schema.get("maxItems", 64) or (schema.get("uniqueItems") and len(value) != len(set(value))):
 237             raise HostReadError("HOST_SUMMARY_REFUSED")
 238         for item in value:
 239             _validate(item, schema["items"], depth + 1)
 240     elif actual == "integer":
 241         if not schema.get("minimum", 0) <= value <= schema.get("maximum", MAX_REVISION):
 242             raise HostReadError("HOST_SUMMARY_REFUSED")
 243     elif actual == "string":
 244         if not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", 4096):
 245             raise HostReadError("HOST_SUMMARY_REFUSED")
 246         if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
 247             raise HostReadError("HOST_SUMMARY_REFUSED")
 248 
 249 
 250 class HostReadSummary:
 251     __slots__ = ("_json",)
 252 
 253     def __init__(self, public, maximum=4096):
 254         _validate(public, summary_schema())
 255         if (public["source_binding_status"] == "MATCHED"
 256                 and (public["status"] != "STAGING_READY_WITH_GAPS" or not public["audit"]["bound_request_count"])):
 257             raise HostReadError("HOST_SUMMARY_REFUSED")
 258         raw = canonical(public)
 259         if type(maximum) is not int or not 2048 <= maximum <= 4096 or len(raw) > maximum:
 260             raise HostReadError("RESOURCE_LIMIT")
 261         self._json = raw
 262 
 263     def to_dict(self):
 264         return json.loads(self._json)
 265 
 266     def to_json(self):
 267         return self._json
 268 
 269     def __repr__(self):
 270         return "<HostReadSummary redacted>"
 271 
 272 
 273 def outcome_category(status):
 274     if status in {"HOST_IDENTITY_REQUIRED", "HOST_PERMISSION_DENIED", "READ_CONTEXT_REQUIRED"}:
 275         return "REJECT_UNAUTHORIZED"
 276     if status == "READ_SCOPE_DENIED":
 277         return "INSUFFICIENT_SCOPE"
 278     if status == "READ_BUDGET_DENIED":
 279         return "BUDGET_EXHAUSTED"
 280     if status in {"SOURCE_BINDING_CONFLICT", "HOST_SOURCE_MISMATCH"}:
 281         return "SOURCE_BINDING_FAILED"
 282     if status == "HOST_SUMMARY_REFUSED":
 283         return "SECRET_BOUNDARY_VIOLATION"
 284     if status == "STAGING_READY_WITH_GAPS":
 285         return "STAGING_READY_WITH_GAPS"
 286     return "UNKNOWN_PENDING"
 287 
 288 
 289 class AuthorityReadHost:
 290     """Registered in-process reader and restricted metadata egress.
 291 
 292     H1 supports SYNTHETIC_ONLY registration. H2 source admission remains closed.
 293     SQL/key counts on the public summary refer to real access, not fake decoding.
 294     Synthetic counters are measured independently by the authorized test harness.
 295     """
 296     def __init__(self, reader, policy, *, producer_ref, locator_ref, epoch_ref,
 297                  source_contract="legacy-authority-state/1", source_kind="SYNTHETIC_ONLY",
 298                  limits=HostReadLimits(), audit_sink=None):
 299         if type(policy) is not HostReadPolicy or type(limits) is not HostReadLimits:
 300             raise HostReadError("HOST_SOURCE_MISMATCH")
 301         self._reader, self._policy, self._limits = reader, policy, limits
 302         self._producer, self._locator, self._epoch = map(_id, (producer_ref, locator_ref, epoch_ref))
 303         self._contract, self._kind, self._audit_sink = source_contract, source_kind, audit_sink
 304 
 305     def issue_permit(self, caller, scope):
 306         with self._policy.lock:
 307             scope = _scope(scope)
 308             principal, rule = self._policy._resolve(caller, scope)
 309             if len(self._policy._permits) >= 4096:
 310                 raise HostReadError("RESOURCE_LIMIT")
 311             self._policy._sequence += 1
 312             permit = object.__new__(HostReadPermit)
 313             self._policy._permits[permit] = {
 314                 "host": self, "reader": self._reader, "epoch": self._epoch,
 315                 "producer": self._producer, "locator": self._locator, "caller": caller,
 316                 "principal": principal, "scope": scope, "version": rule["version"],
 317                 "scope_ref": rule["scope_ref"], "grant": rule["grant"], "used": False,
 318                 "execution_ref": "exec:" + str(self._policy._sequence),
 319             }
 320             return permit
 321 
 322     def request_for(self, permit):
 323         """Trusted RPC wrapper constructs the exact body; no raw state access."""
 324         with self._policy.lock:
 325             rec = self._policy._permits.get(permit)
 326             if rec is None or rec["host"] is not self:
 327                 raise HostReadError("HOST_PERMIT_REPLAY")
 328             return {"execution_ref": rec["execution_ref"], "scope": rec["scope"].to_dict()}
 329 
 330     def read_summary(self, request, caller, permit):
 331         started = time.perf_counter_ns()
 332         status, stage, rec = "HOST_IDENTITY_REQUIRED", None, None
 333         consumed, operations_delta, source_reads = False, 0, 0
 334         try:
 335             with self._policy.lock:
 336                 if type(caller) is not VerifiedLocalCaller or caller not in self._policy._identities:
 337                     raise HostReadError("HOST_IDENTITY_REQUIRED")
 338                 if type(permit) is not HostReadPermit or permit not in self._policy._permits:
 339                     raise HostReadError("HOST_PERMIT_REPLAY")
 340                 rec = self._policy._permits[permit]
 341                 if (rec["host"] is not self or rec["reader"] is not self._reader
 342                         or rec["epoch"] != self._epoch or self._epoch != self._policy.epoch_ref
 343                         or rec["producer"] != self._producer or rec["locator"] != self._locator):
 344                     raise HostReadError("HOST_SOURCE_MISMATCH")
 345                 if rec["caller"] is not caller:
 346                     raise HostReadError("HOST_PERMISSION_DENIED")
 347                 if rec["used"]:
 348                     raise HostReadError("HOST_PERMIT_REPLAY")
 349                 if type(request) is not dict or set(request) != {"execution_ref", "scope"}:
 350                     raise HostReadError("UNSUPPORTED_READ_REQUEST")
 351                 if request["execution_ref"] != rec["execution_ref"]:
 352                     raise HostReadError("UNSUPPORTED_READ_REQUEST")
 353                 requested = _scope(request["scope"])
 354                 if _scope_key(requested) != _scope_key(rec["scope"]):
 355                     raise HostReadError("READ_SCOPE_DENIED")
 356                 principal, rule = self._policy._resolve(caller, requested)
 357                 if rule["version"] != rec["version"]:
 358                     raise HostReadError("HOST_PERMISSION_DENIED")
 359                 if self._contract != "legacy-authority-state/1" or self._kind != "SYNTHETIC_ONLY":
 360                     raise HostReadError("UNSUPPORTED_SOURCE_SCHEMA")
 361                 with self._reader.lock:
 362                     if self._reader.connection.in_transaction is not False:
 363                         raise HostReadError("HOST_CONNECTION_NOT_IDLE")
 364                     rec["used"] = True
 365                     consumed = True
 366                     before = self._reader.operations
 367                     context = TrustedReadContext.from_host(
 368                         self._reader, requested, principal_ref=principal, producer_ref=self._producer,
 369                         authority_locator_ref=self._locator, clock_epoch_ref=self._epoch,
 370                         source_kind="SYNTHETIC_ONLY")
 371                     try:
 372                         output = read_dsat_authority_snapshot(self._reader, requested, context,
 373                                                              ReadLimits(self._limits.staging_bytes,
 374                                                                         self._limits.scoped_records, 6))
 375                     finally:
 376                         # A failure after source I/O must retain its consumed quota.
 377                         operations_delta = self._reader.operations - before
 378                         # Under this locked, pinned one-read contract a positive
 379                         # operation delta witnesses a source read attempt, even
 380                         # if the adapter cannot return its normal cost envelope.
 381                         if operations_delta > 0:
 382                             source_reads = 1
 383                     if type(output) is not StagingSnapshot:
 384                         raise HostReadError("HOST_SUMMARY_REFUSED")
 385                     data = output.to_dict()
 386                     source_reads = data["costs"]["source_reads"]
 387                     status = data["status"]
 388                     if status == "STAGING_READY_WITH_GAPS":
 389                         if (data["scope"] != requested.to_dict() or not data["grants"]
 390                                 or any(g["origin"]["grant_id"] != rec["grant"] for g in data["grants"])
 391                                 or any(r["origin"]["grant_id"] != rec["grant"] for r in data["requests"])):
 392                             raise HostReadError("SOURCE_BINDING_CONFLICT")
 393                         stage = data
 394                     _, final_rule = self._policy._resolve(caller, requested)
 395                     if final_rule["version"] != rec["version"]:
 396                         raise HostReadError("HOST_PERMISSION_DENIED")
 397         except HostReadError as error:
 398             status, stage = error.code, None
 399         except Exception:
 400             status, stage = "READ_SOURCE_UNAVAILABLE", None
 401         elapsed = time.perf_counter_ns() - started
 402         if elapsed > self._limits.soft_deadline_ns:
 403             status, stage = "HOST_DEADLINE_EXCEEDED", None
 404         return self._finish(status, stage, rec if consumed else None,
 405                             consumed, source_reads, operations_delta, elapsed)
 406 
 407     def refusal(self, code):
 408         return self._finish(code if code in STATUSES else "HOST_SUMMARY_REFUSED", None,
 409                             None, False, 0, 0, 0)
 410 
 411     def _finish(self, status, stage, rec, consumed, reads, delta, elapsed):
 412         # Every value below is fixed, host-issued, counted, or R12-sanitized.
 413         public = {
 414             "schema": SCHEMA, "execution_ref": rec["execution_ref"] if rec else "exec:unavailable",
 415             "status": status, "authority_revision": stage["authority_revision"] if stage else None,
 416             "authority_instance": None, "obligation_revision": None,
 417             "snapshot_digest": stage["snapshot_digest"] if stage else None,
 418             "read_scope_ref": rec["scope_ref"] if rec else "scope:unavailable",
 419             "observed_at": stage["read_clock"] if stage else None,
 420             "source_contract": stage["source"]["source_contract"] if stage else None,
 421             "source_binding_status": ("MATCHED" if stage["requests"] else "NOT_APPLICABLE_EMPTY_SCOPE") if stage else "UNAVAILABLE",
 422             "missing_fields": sorted(set(BASE_GAPS) | ({status} if status != "STAGING_READY_WITH_GAPS" else set())
 423                                      | (set(stage["gap_codes"]) if stage else set())),
 424             "native_currentness_status": "UNPROVEN", "math_ready": False,
 425             "current_native_eligible": False, "global_complete": False, "authority_write_action": "NONE",
 426             "audit": {"source_sql_count": 0, "source_read_count": reads,
 427                       "source_operations_delta": delta, "key_read_count": None,
 428                       "key_count_basis": "NOT_OBSERVED", "bound_request_count": len(stage["requests"]) if stage else None,
 429                       "world_row_unchanged": None, "authority_events_count_unchanged": None,
 430                       "authority_events_max_unchanged": None, "connection_total_changes_unchanged": None,
 431                       "observed_sql_schema_version": None, "secret_scan_status": "NOT_RUN",
 432                       "elapsed_ns": elapsed, "deadline_exceeded": status == "HOST_DEADLINE_EXCEEDED",
 433                       "permit_consumed": consumed},
 434         }
 435         if self._audit_sink is not None:
 436             try:
 437                 self._audit_sink({"event": "host_read", "status": status,
 438                                   "identity_basis": "HOST_REGISTRY" if rec else "UNVERIFIED",
 439                                   "source_reads": reads, "operation_delta": delta})
 440             except Exception:
 441                 return self._safe_refusal("READ_SOURCE_UNAVAILABLE", consumed, reads, delta, elapsed)
 442         try:
 443             return HostReadSummary(public, self._limits.summary_bytes)
 444         except Exception:
 445             return self._safe_refusal("HOST_SUMMARY_REFUSED", consumed, reads, delta, elapsed)
 446 
 447     @staticmethod
 448     def _safe_refusal(status, consumed, reads, delta, elapsed):
 449         # Fixed bounded fallback; it never recursively calls an audit sink.
 450         public = {
 451             "schema": SCHEMA, "execution_ref": "exec:unavailable", "status": status,
 452             "authority_revision": None, "authority_instance": None, "obligation_revision": None,
 453             "snapshot_digest": None, "read_scope_ref": "scope:unavailable", "observed_at": None,
 454             "source_contract": None, "source_binding_status": "UNAVAILABLE",
 455             "missing_fields": sorted(set(BASE_GAPS) | {status}),
 456             "native_currentness_status": "UNPROVEN", "math_ready": False,
 457             "current_native_eligible": False, "global_complete": False, "authority_write_action": "NONE",
 458             "audit": {"source_sql_count": 0, "source_read_count": reads if type(reads) is int and 0 <= reads <= 1 else 0,
 459                       "source_operations_delta": delta if type(delta) is int and 0 <= delta <= MAX_REVISION else None,
 460                       "key_read_count": None, "key_count_basis": "NOT_OBSERVED", "bound_request_count": None,
 461                       "world_row_unchanged": None, "authority_events_count_unchanged": None,
 462                       "authority_events_max_unchanged": None, "connection_total_changes_unchanged": None,
 463                       "observed_sql_schema_version": None, "secret_scan_status": "REFUSED",
 464                       "elapsed_ns": elapsed, "deadline_exceeded": status == "HOST_DEADLINE_EXCEEDED",
 465                       "permit_consumed": consumed},
 466         }
 467         return HostReadSummary(public, 4096)
 468 
 469     def __repr__(self):
 470         return "<AuthorityReadHost redacted>"
 471 
 472     def __reduce_ex__(self, protocol):
 473         raise TypeError("HOST_NOT_SERIALIZABLE")
```

## C07: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\cli.py
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

## C08: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\migration.sql
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

## C09: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\migration_2.sql
SHA-256: 7b0c25f990cc101b3b69d3598ed250732f5c975e1dcc30d4980ee0933dd97719

```text
   1 -- Schema 2 accepts typed material bundles. Legacy string values remain readable.
   2 -- The encrypted application-row format and AAD remain schema-1 for compatibility.
   3 PRAGMA user_version = 2;
```

## C12: D:\毕业设计\auth-lifecycle\pyproject.toml
SHA-256: 0d0a7fa9857a9aeca0882b21227544324ff5d6b46e32f31013dc8932382c67a9

```text
   1 [build-system]
   2 requires = ["setuptools>=68"]
   3 build-backend = "setuptools.build_meta"
   4 
   5 [project]
   6 name = "auth-lifecycle-l0"
   7 version = "0.16.0"
   8 description = "Finite bounded authentication lifecycle semantics and independent checks"
   9 requires-python = ">=3.11"
  10 dependencies = []
  11 
  12 [project.optional-dependencies]
  13 online-state = ["cryptography==50.0.2"]
  14 
  15 [tool.setuptools.packages.find]
  16 where = ["src"]
  17 
  18 [tool.setuptools.package-data]
  19 "auth_lifecycle.online_state" = ["migration.sql"]
```

## C13: D:\毕业设计\auth-lifecycle\.venv-dsat-r07-networkx-3.7\pyvenv.cfg
SHA-256: 67268bb56541de9781a4f290af0e57989448c51a7bb5941a38c96e5ca0aa7b67

```text
   1 home = C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python
   2 include-system-site-packages = false
   3 version = 3.12.14
   4 executable = C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
   5 command = C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m venv --without-pip D:\毕业设计\auth-lifecycle\.venv-dsat-r07-networkx-3.7
```

## C14: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\materials.py
SHA-256: 5802380a8ff2058662685c8d2eb5963ec2821264f67e2dc97560db5e4fd2f218

```text
   1 """Typed material bundles with legacy synthetic-string compatibility."""
   2 
   3 import base64
   4 import json
   5 import time
   6 
   7 from cryptography.hazmat.primitives import hashes
   8 from cryptography.hazmat.primitives.asymmetric import padding, rsa
   9 
  10 from .protocol import InvalidInput, digest, exact_fields, identifier
  11 
  12 
  13 def validate_material(material, account=None, client=None):
  14     if isinstance(material, str):
  15         if not 1 <= len(material) <= 4096:
  16             raise InvalidInput("INVALID_LEGACY_MATERIAL")
  17         return material
  18     if not isinstance(material, dict) or material.get("schema") != 2:
  19         raise InvalidInput("INVALID_MATERIAL_SCHEMA")
  20     kind = material.get("kind")
```

## D01: D:\毕业设计\research_g2_dsat_implementation\2026-11-11_r13\sources\sqlite_pragma.html
SHA-256: af75d7d7ab00c29e6eea98618cb1259a3919c308af60a6173215bf9798706034

```text
 304 <hr /><a name="pragfunc"></a>
 305 <h2>PRAGMA functions</h2>
 306 
 307 
 308 <p>
 309 PRAGMAs that return results and that have no side-effects can be 
 310 accessed from ordinary <a href="lang_select.html">SELECT</a> statements as <a href="vtab.html#tabfunc2">table-valued functions</a>.
 311 For each participating PRAGMA, the corresponding table-valued function
 312 has the same name as the PRAGMA with a 7-character "pragma_" prefix.
 313 The PRAGMA argument and schema, if any, are passed as arguments to the
 314 table-valued function, with the schema as an optional, last argument.
 315 
 316 <p>For example, information about the columns in an index can be
 317 read using the <a href="pragma.html#pragma_index_info">index_info pragma</a> as follows:
 318 
 319 <blockquote><pre>
 320 PRAGMA index_info('idx52');
 321 </pre></blockquote>
 322 
 323 <p>Or, the same content can be read using:
 324 
 325 <blockquote><pre>
 326 SELECT * FROM pragma_index_info('idx52');
 327 </pre></blockquote>
 328 
 329 <p>The advantage of the table-valued function format is that the query
 330 can return just a subset of the PRAGMA columns, can include a WHERE clause,
 331 can use aggregate functions, and the table-valued function can be just
 332 one of several data sources in a join.
 333 For example, to get a list of all indexed columns in a schema, one
 334 could query:
 335 
 336 <blockquote><pre>
 337 SELECT DISTINCT m.name || '.' || ii.name AS 'indexed-columns'
 338   FROM sqlite_schema AS m,
 339        pragma_index_list(m.name) AS il,
 340        pragma_index_info(il.name) AS ii
 341  WHERE m.type='table'
 342  ORDER BY 1;
 343 </pre></blockquote>
 344 
 345 <p>
 346 Additional notes:
 347 <ul>
 348 <li><p>
 349 Table-valued functions exist only for built-in PRAGMAs, not for PRAGMAs
 350 defined using the <a href="c3ref/c_fcntl_begin_atomic_write.html#sqlitefcntlpragma">SQLITE_FCNTL_PRAGMA</a> file control.
 351 <li><p>
 352 Table-valued functions exist only for PRAGMAs that return results and
 353 that have no side-effects.
 354 <li><p>
 355 This feature could be used to implement
 356 <a href="https://en.wikipedia.org/wiki/Information_schema">information schema</a>
 357 by first creating a separate schema using
 358 <blockquote><pre>
 359 <a href="lang_attach.html">ATTACH</a> ':memory:' AS 'information_schema';
 360 </pre></blockquote>
 361 Then creating
 362 <a href="lang_createview.html">VIEWs</a> in that schema that implement the official information schema
 363 tables using table-valued PRAGMA functions.
 364 <li><p>
 365 The table-valued functions for PRAGMA feature was added
 366 in SQLite version 3.16.0 (2017-01-02).  Prior versions of SQLite
 367 cannot use this feature.
2179 <a name="pragma_user_version"></a>
2180 <h _id=pragma_user_version style="display:none"> PRAGMA user_version</h><hr>
2181       <p><b>PRAGMA </b><i>schema.</i><b>user_version;
2182       <br>PRAGMA </b><i>schema.</i><b>user_version = </b><i>integer </i><b>;</b>
2183 
2184   
2185 <p>    The user_version pragma will get or set
2186        the value of the user-version integer at offset 60 in the
2187        <a href="fileformat2.html#database_header">database header</a>.  The user-version is an integer that is
2188        available to applications to use however they want.  SQLite
2189        makes no use of the user-version itself.
2190 
2191 <p>    See also the <a href="pragma.html#pragma_application_id">application_id pragma</a> and <a href="pragma.html#pragma_schema_version">schema_version pragma</a>.
```
