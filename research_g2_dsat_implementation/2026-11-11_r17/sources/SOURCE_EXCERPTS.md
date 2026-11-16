# R17 static source excerpts, no runtime invocation

## C01: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\services.py
SHA-256 7cc2321e2623c06848e13d106680887a01bd5635bf417127942a5bac1647be41

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
 277 def serve(role, root, fault=None, *, authority_mount_ticket=None):
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
 293     # The default ticket is absent. Registration never constructs a second Store.
 294     from .dsat_authority_host_activation import (mount_authority_host,
 295         authenticate_authority_peer, dispatch_authority_read)
 296     authority_read_host = (mount_authority_host(implementation, authority_mount_ticket)
 297                            if role == "authority" else None)
 298 
 299     class Handler(BaseHTTPRequestHandler):
 300         def log_message(self, *args):
 301             pass
 302 
 303         def do_POST(self):
 304             started = time.monotonic_ns()
 305             request_bytes = 0
 306             operation = self.path.removeprefix("/")
 307             identity = None
 308             supplied = self.headers.get("Authorization", "")
 309             for name, token in config["identities"].items():
 310                 if hmac.compare_digest(supplied, "Bearer " + token):
 311                     identity = name
 312             allowed = config["permissions"].get(identity, [])
 313             try:
 314                 if operation not in allowed:
 315                     result = {"status": "REJECTED", "reason": "IDENTITY_OR_OPERATION_DENIED"}
 316                 else:
 317                     length = int(self.headers.get("Content-Length", "0"))
 318                     if not 0 < length <= 65536:
 319                         raise InvalidInput("BODY_SIZE")
 320                     raw = self.rfile.read(length)
 321                     request_bytes = len(raw)
 322                     payload = strict_json(raw)
 323                     if role == "authority":
 324                         if operation == "staging_read_metadata":
 325                             peer = authenticate_authority_peer(authority_read_host, supplied,
 326                                                                config["identities"], config["permissions"])
 327                             result = dispatch_authority_read(authority_read_host, peer, payload)
 328                         else:
 329                             result = implementation.call(operation, payload)
 330                     else:
 331                         result = implementation.call(operation, payload, identity)
 332             except (ValueError, TypeError, KeyError, InvalidInput):
 333                 result = {"status": "REJECTED", "reason": "INVALID_INPUT"}
 334             except Exception:
 335                 result = {"status": "UNKNOWN", "reason": "SERVICE_UNAVAILABLE"}
 336             response = canonical(result)
 337             # The operation logged is selected from the configured whitelist.
 338             try:
 339                 log.emit("request", operation=operation if operation in allowed else "denied",
 340                          identity=identity, request_json_bytes=request_bytes,
 341                          response_json_bytes=len(response), status=result.get("status"),
 342                          elapsed_ns=time.monotonic_ns() - started)
 343             except Exception:
 344                 if role != "authority" or operation != "staging_read_metadata":
 345                     raise
 346                 response = canonical({"status": "UNKNOWN", "reason": "READ_AUDIT_UNAVAILABLE"})
 347             try:
 348                 self.send_response(200)
 349                 self.send_header("Content-Type", "application/json")
 350                 self.send_header("Content-Length", str(len(response)))
 351                 self.end_headers()
 352                 self.wfile.write(response)
 353             except (OSError, ssl.SSLError):
 354                 pass
 355 
 356     server = ThreadingHTTPServer(("127.0.0.1", config["port"]), Handler)
 357     server.daemon_threads = True
 358     tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
 359     tls.minimum_version = ssl.TLSVersion.TLSv1_2
 360     tls.load_cert_chain(config["certificate"], config["tls_key"])
 361     server.socket = tls.wrap_socket(server.socket, server_side=True)
 362     write_json(root / "control" / (role + "_ready.json"),
 363                {"role": role, "pid": os.getpid(), "port": config["port"],
 364                 "boot": getattr(implementation, "boot", None)})
 365     server.serve_forever(poll_interval=0.05)
```

## C02: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\storage.py
SHA-256 2d17cf95d7d724d8debbeb47c2df28cfd537aa696bde47edb98908170a12de83

```text
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
```

## C03: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\dsat_authority_host_activation.py
SHA-256 edf9331d05ac10d3744481a1edb2c8a523869d0727db935a3dd0102ad8fbe3ff

```text
   1 """A1 offline mounting core. No storage/services/crypto imports or import I/O.
   2 
   3 All issuing APIs belong to the trusted process. Opaque objects bind local facts,
   4 not cryptographic identities. Live runtime admission remains a separate gate.
   5 """
   6 import hmac
   7 import json
   8 import threading
   9 import time
  10 import weakref
  11 
  12 from . import dsat_authority_read_host as h
  13 from .dsat_authority_read import ReadError
  14 
  15 
  16 BOUNDED_SELECT = (
  17     "SELECT version, length(ciphertext) AS state_bytes, CASE WHEN length(ciphertext) <= :ceiling "
  18     "THEN ciphertext ELSE NULL END AS ciphertext, (SELECT user_version FROM pragma_user_version) "
  19     "AS schema_version FROM authority_state WHERE id=1"
  20 )
  21 CEILING = 16777216
  22 _TICKETS = weakref.WeakKeyDictionary()
  23 _REGISTRATIONS = weakref.WeakKeyDictionary()
  24 _PEERS = weakref.WeakKeyDictionary()
  25 _SESSION_LOCK = threading.RLock()
  26 _SESSION_NAMESPACES = set()
  27 
  28 
  29 class _Capability:
  30     __slots__ = ("__weakref__",)
  31 
  32     def __init__(self, *args, **kwargs):
  33         raise h.HostReadError("HOST_SOURCE_MISMATCH")
  34 
  35     def __repr__(self):
  36         return "<AuthorityCapability redacted>"
  37 
  38     def __reduce_ex__(self, protocol):
  39         raise TypeError("AUTHORITY_CAPABILITY_NOT_SERIALIZABLE")
  40 
  41 
  42 class AuthorityMountTicket(_Capability):
  43     __slots__ = ()
  44 
  45 
  46 class AuthenticatedRpcContext(_Capability):
  47     __slots__ = ()
  48 
  49 
  50 class ActivationIssuer:
  51     """Host-only offline issuer; no live admission or secret-loading API."""
  52     def __init__(self, epoch_ref, *, clock=time.monotonic_ns):
  53         self.epoch_ref = h._id(epoch_ref)
  54         self.clock = clock
  55         self.active = True
  56         self._issued = set()
  57         self._lock = threading.RLock()
  58 
  59     def authorize_offline(self, *, authorization_id, scope, grant_ref, rid,
  60                           manager_identity, principal_ref, actor, transport_ref,
  61                           scope_ref, producer_ref, source_ref, expires_ns,
  62                           expected_store=None, ceiling=CEILING, audit_sink=None, permit_ref="permit:one",
  63                           limits=h.HostReadLimits(), aad=b"auth-lifecycle/online-state/schema-1"):
  64         with self._lock:
  65             authorization_id = h._id(authorization_id)
  66             if not self.active or authorization_id in self._issued:
  67                 raise h.HostReadError("HOST_PERMIT_REPLAY")
  68             if type(ceiling) is not int or not 1 <= ceiling <= CEILING or type(aad) is not bytes:
  69                 raise h.HostReadError("RESOURCE_LIMIT")
  70             refs = [grant_ref, rid, manager_identity, principal_ref, actor, transport_ref,
  71                     scope_ref, producer_ref, source_ref, permit_ref]
  72             for ref in refs:
  73                 h._id(ref)
  74             if manager_identity in {"controller", "agentA", "agentB"}:
  75                 raise h.HostReadError("HOST_PERMISSION_DENIED")
  76             ticket = object.__new__(AuthorityMountTicket)
  77             _TICKETS[ticket] = dict(issuer=self, authorization_id=authorization_id,
  78                 epoch=self.epoch_ref, scope=h._scope(scope), grant=grant_ref, rid=rid,
  79                 manager=manager_identity, principal=principal_ref, actor=actor,
  80                 transport=transport_ref, scope_ref=scope_ref, producer=producer_ref,
  81                 source=source_ref, expires=h._nat(expires_ns), expected_store=expected_store,
  82                 ceiling=ceiling, aad=aad, audit_sink=audit_sink, limits=limits,
  83                 enabled=True, version=1, mounted=False, permit_ref=permit_ref)
  84             self._issued.add(authorization_id)
  85             return ticket
  86 
  87     def revoke(self, ticket):
  88         rec = _TICKETS.get(ticket)
  89         if rec is None or rec["issuer"] is not self:
  90             raise h.HostReadError("HOST_SOURCE_MISMATCH")
  91         with self._lock:
  92             rec["enabled"] = False
  93             rec["version"] += 1
  94 
  95     def retire(self, new_epoch):
  96         with self._lock:
  97             self.active = False
  98             self.epoch_ref = h._id(new_epoch)
  99 
 100 
 101 class BoundedAuthorityReader:
 102     """Narrow existing-store view. No constructor, new connection, or key cache."""
 103     def __init__(self, registration):
 104         self._registration = registration
 105 
 106     @property
 107     def lock(self):
 108         return self._registration._record()["lock"]
 109 
 110     @property
 111     def connection(self):
 112         return self._registration._record()["connection"]
 113 
 114     @property
 115     def operations(self):
 116         return self._registration._record()["store"].operations
 117 
 118     @property
 119     def operation_limit(self):
 120         return self._registration._record()["store"].operation_limit
 121 
 122     def read_state(self):
 123         reg = self._registration
 124         rec = reg._record()
 125         reg._check_source()
 126         if (not rec["inflight"] or rec["owner"] != threading.get_ident()
 127                 or rec["reader_started"]):
 128             raise ReadError("SOURCE_BINDING_CONFLICT")
 129         rec["reader_started"] = True
 130         stats = rec["stats"]
 131         stats["source_read_attempts"] += 1
 132         stats["select_attempts"] += 1
 133         started = time.perf_counter_ns()
 134         cursor = None
 135         try:
 136             cursor = rec["store"].execute(BOUNDED_SELECT, {"ceiling": rec["ticket"]["ceiling"]})
 137             row = cursor.fetchone()
 138             stats["select_successes"] += 1
 139         finally:
 140             if cursor is not None:
 141                 cursor.close()
 142             stats["C_select_ns"] += time.perf_counter_ns() - started
 143         if row is None:
 144             raise ReadError("SNAPSHOT_INCOMPLETE")
 145         rec["observed_schema"] = row["schema_version"]
 146         if type(row["schema_version"]) is not int or row["schema_version"] != 2:
 147             raise ReadError("UNSUPPORTED_SOURCE_SCHEMA")
 148         size = row["state_bytes"]
 149         if type(size) is not int or size > rec["ticket"]["ceiling"]:
 150             raise ReadError("RESOURCE_LIMIT")
 151         if row["ciphertext"] is None or size < 28:
 152             raise ReadError("SNAPSHOT_INCOMPLETE")
 153         raw = bytes(row["ciphertext"])
 154         if len(raw) != size:
 155             raise ReadError("SOURCE_BINDING_CONFLICT")
 156         stats["key_calls"] += 1
 157         started = time.perf_counter_ns()
 158         try:
 159             cipher = rec["store"].cipher()
 160         finally:
 161             stats["C_key_ns"] += time.perf_counter_ns() - started
 162         stats["decode_calls"] += 1
 163         started = time.perf_counter_ns()
 164         try:
 165             state = json.loads(cipher.decrypt(raw[:12], raw[12:], rec["ticket"]["aad"]))
 166         finally:
 167             stats["C_decode_ns"] += time.perf_counter_ns() - started
 168         return row["version"], state
 169 
 170     def __repr__(self):
 171         return "<BoundedAuthorityReader redacted>"
 172 
 173 
 174 class AuthorityRegistration(_Capability):
 175     __slots__ = ()
 176 
 177     def _record(self):
 178         rec = _REGISTRATIONS.get(self)
 179         if rec is None:
 180             raise h.HostReadError("HOST_SOURCE_MISMATCH")
 181         return rec
 182 
 183     def _check_source(self):
 184         rec = self._record()
 185         ticket = rec["ticket"]
 186         issuer = ticket["issuer"]
 187         store = rec["store"]
 188         if (not issuer.active or issuer.epoch_ref != ticket["epoch"]
 189                 or store.connection is not rec["connection"] or store.lock is not rec["lock"]):
 190             raise h.HostReadError("HOST_SOURCE_MISMATCH")
 191         if not ticket["enabled"] or ticket["version"] != rec["ticket_version"]:
 192             raise h.HostReadError("HOST_PERMISSION_DENIED")
 193         if h._nat(issuer.clock()) >= ticket["expires"]:
 194             raise h.HostReadError("HOST_PERMIT_EXPIRED")
 195 
 196     def bind_host(self, host, reader, policy):
 197         rec = self._record()
 198         if (reader is not rec["reader"] or policy is not rec["policy"] or rec["host"] is not None
 199                 or host._epoch != rec["ticket"]["epoch"] or host._locator != rec["ticket"]["source"]
 200                 or host._producer != rec["ticket"]["producer"]):
 201             raise h.HostReadError("HOST_SOURCE_MISMATCH")
 202         rec["host"] = host
 203 
 204     def before_issue(self, host):
 205         self._check_source()
 206         rec = self._record()
 207         if rec["host"] is not host:
 208             raise h.HostReadError("HOST_SOURCE_MISMATCH")
 209         if rec["claimed"]:
 210             raise h.HostReadError("HOST_PERMIT_REPLAY")
 211 
 212     def note_permit(self):
 213         self._record()["stats"]["permits_issued"] += 1
 214 
 215     def claim(self, host, caller, scope):
 216         started = time.perf_counter_ns()
 217         self.before_issue(host)
 218         rec = self._record()
 219         if caller is not rec["caller"] or h._scope_key(scope) != h._scope_key(rec["ticket"]["scope"]):
 220             raise h.HostReadError("READ_SCOPE_DENIED")
 221         rec["stats"]["metadata_checks"] += 1
 222         changes_before = rec["connection"].total_changes
 223         rec["claimed"] = True
 224         rec["inflight"] = True
 225         rec["owner"] = threading.get_ident()
 226         rec["stats"]["session_claims"] += 1
 227         rec["stats"]["permits_consumed"] += 1
 228         rec["changes_before"] = changes_before
 229         rec["stats"]["C_session_gate_ns"] += time.perf_counter_ns() - started
 230 
 231     def note_output(self, elapsed):
 232         self._record()["stats"]["C_output_ns"] += elapsed
 233 
 234     def validate_stage(self, stage):
 235         rec = self._record()
 236         target = [row for row in stage["requests"] if row["rid"] == rec["ticket"]["rid"]]
 237         if len(target) != 1 or target[0]["origin"]["grant_id"] != rec["ticket"]["grant"]:
 238             raise h.HostReadError("SOURCE_BINDING_CONFLICT")
 239 
 240     def egress_check(self):
 241         self._record()["stats"]["metadata_checks"] += 1
 242         self._check_source()
 243 
 244     def finish(self):
 245         rec = self._record()
 246         if rec["inflight"] and rec["owner"] == threading.get_ident():
 247             try:
 248                 rec["changes_unchanged"] = rec["changes_before"] == rec["connection"].total_changes
 249                 return True
 250             except Exception:
 251                 rec["changes_unchanged"] = None
 252                 return False
 253             finally:
 254                 rec["inflight"] = False
 255         return True
 256 
 257     def public_audit(self):
 258         rec = self._record()
 259         return {"source_sql_count": rec["stats"]["select_attempts"],
 260                 "key_read_count": None, "key_count_basis": "PINNED_PATH_BOUND",
 261                 "observed_sql_schema_version": rec["observed_schema"],
 262                 "connection_total_changes_unchanged": rec["changes_unchanged"]}
 263 
 264     def counters(self):
 265         """Trusted test/management domain: counts only, no source or secrets."""
 266         rec = self._record()
 267         return {**rec["stats"], "slot_claimed": rec["claimed"],
 268                 "inflight": rec["inflight"], "changes_unchanged": rec["changes_unchanged"]}
 269 
 270 
 271 def mount_authority_host(store, ticket=None):
 272     """Default disabled. Called after Store creation and before Handler setup."""
 273     started = time.perf_counter_ns()
 274     if ticket is None:
 275         return None
 276     if type(ticket) is not AuthorityMountTicket or ticket not in _TICKETS:
 277         raise h.HostReadError("HOST_SOURCE_MISMATCH")
 278     tr = _TICKETS[ticket]
 279     issuer = tr["issuer"]
 280     with issuer._lock:
 281         if tr["mounted"] or not issuer.active or issuer.epoch_ref != tr["epoch"]:
 282             raise h.HostReadError("HOST_SOURCE_MISMATCH")
 283         if tr["expected_store"] is not None and tr["expected_store"] is not store:
 284             raise h.HostReadError("HOST_SOURCE_MISMATCH")
 285         if not tr["enabled"] or issuer.clock() >= tr["expires"]:
 286             raise h.HostReadError("HOST_PERMISSION_DENIED")
 287         # The namespace is process-wide, independent of issuer objects and
 288         # display aliases. Keep the connection object itself, avoiding id reuse.
 289         namespace = (store.connection, tr["authorization_id"], tr["epoch"],
 290                      h._scope_key(tr["scope"]))
 291         with _SESSION_LOCK:
 292             if namespace in _SESSION_NAMESPACES:
 293                 raise h.HostReadError("HOST_PERMIT_REPLAY")
 294             if len(_SESSION_NAMESPACES) >= 4096:
 295                 raise h.HostReadError("RESOURCE_LIMIT")
 296             _SESSION_NAMESPACES.add(namespace)
 297         policy = h.HostReadPolicy(tr["epoch"], clock=issuer.clock)
 298         caller = policy.bind_authenticated_caller(principal_ref=tr["principal"], actor=tr["actor"],
 299                     transport_ref=tr["transport"], expires_ns=tr["expires"])
 300         policy.allow(principal_ref=tr["principal"], actor=tr["actor"], transport_ref=tr["transport"],
 301                      scope=tr["scope"], grant_ref=tr["grant"], scope_ref=tr["scope_ref"], expires_ns=tr["expires"])
 302         registration = object.__new__(AuthorityRegistration)
 303         stats = {k: 0 for k in ("registrations", "permits_issued", "permits_consumed", "session_claims",
 304                  "source_read_attempts", "select_attempts", "select_successes", "key_calls", "decode_calls",
 305                  "metadata_checks", "C_registration_ns", "C_authorization_ns", "C_permit_ns",
 306                  "C_session_gate_ns", "C_select_ns", "C_key_ns", "C_decode_ns", "C_output_ns")}
 307         rec = dict(store=store, connection=store.connection, lock=store.lock, ticket=tr,
 308                    ticket_version=tr["version"], policy=policy, caller=caller, host=None,
 309                    reader=None, claimed=False, inflight=False, owner=None, reader_started=False,
 310                    stats=stats, observed_schema=None, changes_before=None, changes_unchanged=None)
 311         _REGISTRATIONS[registration] = rec
 312         reader = BoundedAuthorityReader(registration)
 313         rec["reader"] = reader
 314         host = h.AuthorityReadHost(reader, policy, producer_ref=tr["producer"], locator_ref=tr["source"],
 315                  epoch_ref=tr["epoch"], source_kind="LOCAL_AUTHORITY_HOST", limits=tr["limits"],
 316                  audit_sink=tr["audit_sink"], registration=registration)
 317         tr["mounted"] = True
 318         stats["registrations"] = 1
 319         stats["C_registration_ns"] = time.perf_counter_ns() - started
 320         return MountedAuthority(registration, host, caller, policy)
 321 
 322 
 323 class MountedAuthority:
 324     def __init__(self, registration, host, caller, policy):
 325         self.registration, self.host, self.caller, self.policy = registration, host, caller, policy
 326 
 327     def issue_permit(self):
 328         started = time.perf_counter_ns()
 329         try:
 330             return self.host.issue_permit(self.caller, self.registration._record()["ticket"]["scope"])
 331         finally:
 332             self.registration._record()["stats"]["C_permit_ns"] += time.perf_counter_ns() - started
 333 
 334     def refs(self, permit=None):
 335         tr = self.registration._record()["ticket"]
 336         reference = self.host.request_for(permit)["execution_ref"] if permit is not None else tr["permit_ref"]
 337         return {"authorization_ref": tr["authorization_id"], "permit_ref": reference,
 338                 "read_scope_ref": tr["scope_ref"]}
 339 
 340     def __repr__(self):
 341         return "<MountedAuthority redacted>"
 342 
 343     def __reduce_ex__(self, protocol):
 344         raise TypeError("MOUNT_NOT_SERIALIZABLE")
 345 
 346 
 347 def authenticate_authority_peer(mount, supplied, identities, permissions):
 348     """Called with already-private Handler configuration, never request body flags."""
 349     if type(mount) is not MountedAuthority or type(supplied) is not str:
 350         return None
 351     tr = mount.registration._record()["ticket"]
 352     matched = None
 353     for identity, token in identities.items():
 354         if type(token) is str and hmac.compare_digest(supplied, "Bearer " + token):
 355             matched = identity
 356     if matched != tr["manager"] or h.RIGHT not in permissions.get(matched, []):
 357         return None
 358     context = object.__new__(AuthenticatedRpcContext)
 359     _PEERS[context] = (mount, matched, tr["epoch"])
 360     return context
 361 
 362 
 363 def dispatch_authority_read(mount, context, payload, permit=None):
 364     if type(mount) is not MountedAuthority:
 365         return h.AuthorityReadHost._safe_refusal("READ_CONTEXT_REQUIRED", False, 0, 0, 0).to_dict()
 366     started = time.perf_counter_ns()
 367     rec = mount.registration._record()
 368     try:
 369         with mount.policy.lock:
 370             if (type(context) is not AuthenticatedRpcContext or context not in _PEERS
 371                     or _PEERS[context][0] is not mount or _PEERS[context][2] != rec["ticket"]["epoch"]):
 372                 raise h.HostReadError("HOST_IDENTITY_REQUIRED")
 373             mount.registration._check_source()
 374             if type(payload) is not dict or set(payload) != {"authorization_ref", "permit_ref", "read_scope_ref"}:
 375                 raise h.HostReadError("UNSUPPORTED_READ_REQUEST")
 376             tr = rec["ticket"]
 377             if payload["authorization_ref"] != tr["authorization_id"] or payload["read_scope_ref"] != tr["scope_ref"]:
 378                 raise h.HostReadError("READ_SCOPE_DENIED")
 379             if permit is None:
 380                 if payload["permit_ref"] != tr["permit_ref"]:
 381                     raise h.HostReadError("READ_SCOPE_DENIED")
 382                 permit = mount.issue_permit()
 383                 body = mount.host.request_for(permit)
 384             else:
 385                 body = mount.host.request_for(permit)
 386             if payload["permit_ref"] not in {tr["permit_ref"], body["execution_ref"]}:
 387                 raise h.HostReadError("READ_SCOPE_DENIED")
 388             rec["stats"]["C_authorization_ns"] += time.perf_counter_ns() - started
 389             return mount.host.read_summary(body, mount.caller, permit).to_dict()
 390     except h.HostReadError as error:
 391         return mount.host.refusal(error.code).to_dict()
 392     except Exception:
 393         return mount.host.refusal("READ_SOURCE_UNAVAILABLE").to_dict()
```

## C04: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\dsat_authority_read_host.py
SHA-256 8edcbb1aef62482a6bb3e1f7f993e33824bd6b060b7ddef479567645fdcdb9ad

```text
 289 class AuthorityReadHost:
 290     """Registered in-process reader and restricted metadata egress.
 291 
 292     H1 supports SYNTHETIC_ONLY registration. H2 source admission remains closed.
 293     SQL/key counts on the public summary refer to real access, not fake decoding.
 294     Synthetic counters are measured independently by the authorized test harness.
 295     """
 296     def __init__(self, reader, policy, *, producer_ref, locator_ref, epoch_ref,
 297                  source_contract="legacy-authority-state/1", source_kind="SYNTHETIC_ONLY",
 298                  limits=HostReadLimits(), audit_sink=None, registration=None):
 299         if type(policy) is not HostReadPolicy or type(limits) is not HostReadLimits:
 300             raise HostReadError("HOST_SOURCE_MISMATCH")
 301         self._reader, self._policy, self._limits = reader, policy, limits
 302         self._producer, self._locator, self._epoch = map(_id, (producer_ref, locator_ref, epoch_ref))
 303         self._contract, self._kind, self._audit_sink = source_contract, source_kind, audit_sink
 304         self._registration = registration
 305         if registration is not None:
 306             from .dsat_authority_host_activation import AuthorityRegistration
 307             if type(registration) is not AuthorityRegistration or source_kind != "LOCAL_AUTHORITY_HOST":
 308                 raise HostReadError("HOST_SOURCE_MISMATCH")
 309             registration.bind_host(self, reader, policy)
 310 
 311     def issue_permit(self, caller, scope):
 312         with self._policy.lock:
 313             if self._registration is not None:
 314                 self._registration.before_issue(self)
 315             scope = _scope(scope)
 316             principal, rule = self._policy._resolve(caller, scope)
 317             if len(self._policy._permits) >= 4096:
 318                 raise HostReadError("RESOURCE_LIMIT")
 319             self._policy._sequence += 1
 320             permit = object.__new__(HostReadPermit)
 321             self._policy._permits[permit] = {
 322                 "host": self, "reader": self._reader, "epoch": self._epoch,
 323                 "producer": self._producer, "locator": self._locator, "caller": caller,
 324                 "principal": principal, "scope": scope, "version": rule["version"],
 325                 "scope_ref": rule["scope_ref"], "grant": rule["grant"], "used": False,
 326                 "execution_ref": "exec:" + str(self._policy._sequence),
 327             }
 328             if self._registration is not None:
 329                 self._registration.note_permit()
 330             return permit
 331 
 332     def request_for(self, permit):
 333         """Trusted RPC wrapper constructs the exact body; no raw state access."""
 334         with self._policy.lock:
 335             rec = self._policy._permits.get(permit)
 336             if rec is None or rec["host"] is not self:
 337                 raise HostReadError("HOST_PERMIT_REPLAY")
 338             return {"execution_ref": rec["execution_ref"], "scope": rec["scope"].to_dict()}
 339 
 340     def read_summary(self, request, caller, permit):
 341         started = time.perf_counter_ns()
 342         status, stage, rec = "HOST_IDENTITY_REQUIRED", None, None
 343         consumed, operations_delta, source_reads = False, 0, 0
 344         try:
 345             with self._policy.lock:
 346                 if type(caller) is not VerifiedLocalCaller or caller not in self._policy._identities:
 347                     raise HostReadError("HOST_IDENTITY_REQUIRED")
 348                 if type(permit) is not HostReadPermit or permit not in self._policy._permits:
 349                     raise HostReadError("HOST_PERMIT_REPLAY")
 350                 rec = self._policy._permits[permit]
 351                 if (rec["host"] is not self or rec["reader"] is not self._reader
 352                         or rec["epoch"] != self._epoch or self._epoch != self._policy.epoch_ref
 353                         or rec["producer"] != self._producer or rec["locator"] != self._locator):
 354                     raise HostReadError("HOST_SOURCE_MISMATCH")
 355                 if rec["caller"] is not caller:
 356                     raise HostReadError("HOST_PERMISSION_DENIED")
 357                 if rec["used"]:
 358                     raise HostReadError("HOST_PERMIT_REPLAY")
 359                 if type(request) is not dict or set(request) != {"execution_ref", "scope"}:
 360                     raise HostReadError("UNSUPPORTED_READ_REQUEST")
 361                 if request["execution_ref"] != rec["execution_ref"]:
 362                     raise HostReadError("UNSUPPORTED_READ_REQUEST")
 363                 requested = _scope(request["scope"])
 364                 if _scope_key(requested) != _scope_key(rec["scope"]):
 365                     raise HostReadError("READ_SCOPE_DENIED")
 366                 principal, rule = self._policy._resolve(caller, requested)
 367                 if rule["version"] != rec["version"]:
 368                     raise HostReadError("HOST_PERMISSION_DENIED")
 369                 if (self._contract != "legacy-authority-state/1"
 370                         or (self._registration is None and self._kind != "SYNTHETIC_ONLY")):
 371                     raise HostReadError("UNSUPPORTED_SOURCE_SCHEMA")
 372                 with self._reader.lock:
 373                     if self._reader.connection.in_transaction is not False:
 374                         raise HostReadError("HOST_CONNECTION_NOT_IDLE")
 375                     if self._registration is not None:
 376                         self._registration.claim(self, caller, requested)
 377                     rec["used"] = True
 378                     consumed = True
 379                     before = self._reader.operations
 380                     context = TrustedReadContext.from_host(
 381                         self._reader, requested, principal_ref=principal, producer_ref=self._producer,
 382                         authority_locator_ref=self._locator, clock_epoch_ref=self._epoch,
 383                         source_kind="LOCAL_AUTHORITY_HOST" if self._registration is not None else "SYNTHETIC_ONLY")
 384                     try:
 385                         output = read_dsat_authority_snapshot(self._reader, requested, context,
 386                                                              ReadLimits(self._limits.staging_bytes,
 387                                                                         self._limits.scoped_records, 6))
 388                     finally:
 389                         # A failure after source I/O must retain its consumed quota.
 390                         operations_delta = self._reader.operations - before
 391                         # Under this locked, pinned one-read contract a positive
 392                         # operation delta witnesses a source read attempt, even
 393                         # if the adapter cannot return its normal cost envelope.
 394                         if operations_delta > 0:
 395                             source_reads = 1
 396                     if type(output) is not StagingSnapshot:
 397                         raise HostReadError("HOST_SUMMARY_REFUSED")
 398                     data = output.to_dict()
 399                     source_reads = data["costs"]["source_reads"]
 400                     status = data["status"]
 401                     if status == "STAGING_READY_WITH_GAPS":
 402                         if (data["scope"] != requested.to_dict() or not data["grants"]
 403                                 or any(g["origin"]["grant_id"] != rec["grant"] for g in data["grants"])
 404                                 or any(r["origin"]["grant_id"] != rec["grant"] for r in data["requests"])):
 405                             raise HostReadError("SOURCE_BINDING_CONFLICT")
 406                         stage = data
 407                         if self._registration is not None:
 408                             self._registration.validate_stage(stage)
 409                     if self._registration is not None:
 410                         self._registration.egress_check()
 411                     _, final_rule = self._policy._resolve(caller, requested)
 412                     if final_rule["version"] != rec["version"]:
 413                         raise HostReadError("HOST_PERMISSION_DENIED")
 414         except HostReadError as error:
 415             status, stage = error.code, None
 416         except Exception:
 417             status, stage = "READ_SOURCE_UNAVAILABLE", None
 418         finally:
 419             if self._registration is not None and consumed:
 420                 if not self._registration.finish():
 421                     status, stage = "READ_SOURCE_UNAVAILABLE", None
 422         if (self._registration is not None and consumed
 423                 and self._registration.public_audit()["connection_total_changes_unchanged"] is False):
 424             status, stage = "SOURCE_BINDING_CONFLICT", None
 425         elapsed = time.perf_counter_ns() - started
 426         if elapsed > self._limits.soft_deadline_ns:
 427             status, stage = "HOST_DEADLINE_EXCEEDED", None
 428         finish_started = time.perf_counter_ns()
 429         result = self._finish(status, stage, rec if consumed else None,
 430                              consumed, source_reads, operations_delta, elapsed,
 431                              self._registration.public_audit() if self._registration is not None and consumed else None)
 432         if self._registration is not None and consumed:
 433             self._registration.note_output(time.perf_counter_ns() - finish_started)
 434         return result
 435 
 436     def refusal(self, code):
 437         return self._finish(code if code in STATUSES else "HOST_SUMMARY_REFUSED", None,
 438                             None, False, 0, 0, 0)
 439 
 440     def _finish(self, status, stage, rec, consumed, reads, delta, elapsed, source_audit=None):
 441         # Every value below is fixed, host-issued, counted, or R12-sanitized.
 442         public = {
 443             "schema": SCHEMA, "execution_ref": rec["execution_ref"] if rec else "exec:unavailable",
 444             "status": status, "authority_revision": stage["authority_revision"] if stage else None,
 445             "authority_instance": None, "obligation_revision": None,
 446             "snapshot_digest": stage["snapshot_digest"] if stage else None,
 447             "read_scope_ref": rec["scope_ref"] if rec else "scope:unavailable",
 448             "observed_at": stage["read_clock"] if stage else None,
 449             "source_contract": stage["source"]["source_contract"] if stage else None,
 450             "source_binding_status": ("MATCHED" if stage["requests"] else "NOT_APPLICABLE_EMPTY_SCOPE") if stage else "UNAVAILABLE",
 451             "missing_fields": sorted(set(BASE_GAPS) | ({status} if status != "STAGING_READY_WITH_GAPS" else set())
 452                                      | (set(stage["gap_codes"]) if stage else set())),
 453             "native_currentness_status": "UNPROVEN", "math_ready": False,
 454             "current_native_eligible": False, "global_complete": False, "authority_write_action": "NONE",
 455             "audit": {"source_sql_count": 0, "source_read_count": reads,
 456                       "source_operations_delta": delta, "key_read_count": None,
 457                       "key_count_basis": "NOT_OBSERVED", "bound_request_count": len(stage["requests"]) if stage else None,
 458                       "world_row_unchanged": None, "authority_events_count_unchanged": None,
 459                       "authority_events_max_unchanged": None, "connection_total_changes_unchanged": None,
 460                       "observed_sql_schema_version": None, "secret_scan_status": "NOT_RUN",
 461                       "elapsed_ns": elapsed, "deadline_exceeded": status == "HOST_DEADLINE_EXCEEDED",
 462                       "permit_consumed": consumed},
 463         }
 464         if source_audit is not None:
 465             allowed = {"source_sql_count", "key_read_count", "key_count_basis",
 466                        "observed_sql_schema_version", "connection_total_changes_unchanged"}
 467             if set(source_audit) != allowed:
 468                 return self._safe_refusal("HOST_SUMMARY_REFUSED", consumed, reads, delta, elapsed)
 469             public["audit"].update(source_audit)
 470         if self._audit_sink is not None:
 471             try:
 472                 self._audit_sink({"event": "host_read", "status": status,
 473                                   "identity_basis": "HOST_REGISTRY" if rec else "UNVERIFIED",
 474                                   "source_reads": reads, "operation_delta": delta})
 475             except Exception:
 476                 return self._safe_refusal("READ_SOURCE_UNAVAILABLE", consumed, reads, delta, elapsed)
 477         try:
 478             return HostReadSummary(public, self._limits.summary_bytes)
 479         except Exception:
 480             return self._safe_refusal("HOST_SUMMARY_REFUSED", consumed, reads, delta, elapsed)
 481 
 482     @staticmethod
 483     def _safe_refusal(status, consumed, reads, delta, elapsed):
 484         # Fixed bounded fallback; it never recursively calls an audit sink.
 485         public = {
 486             "schema": SCHEMA, "execution_ref": "exec:unavailable", "status": status,
 487             "authority_revision": None, "authority_instance": None, "obligation_revision": None,
 488             "snapshot_digest": None, "read_scope_ref": "scope:unavailable", "observed_at": None,
 489             "source_contract": None, "source_binding_status": "UNAVAILABLE",
 490             "missing_fields": sorted(set(BASE_GAPS) | {status}),
 491             "native_currentness_status": "UNPROVEN", "math_ready": False,
 492             "current_native_eligible": False, "global_complete": False, "authority_write_action": "NONE",
 493             "audit": {"source_sql_count": 0, "source_read_count": reads if type(reads) is int and 0 <= reads <= 1 else 0,
 494                       "source_operations_delta": delta if type(delta) is int and 0 <= delta <= MAX_REVISION else None,
 495                       "key_read_count": None, "key_count_basis": "NOT_OBSERVED", "bound_request_count": None,
 496                       "world_row_unchanged": None, "authority_events_count_unchanged": None,
 497                       "authority_events_max_unchanged": None, "connection_total_changes_unchanged": None,
 498                       "observed_sql_schema_version": None, "secret_scan_status": "REFUSED",
 499                       "elapsed_ns": elapsed, "deadline_exceeded": status == "HOST_DEADLINE_EXCEEDED",
 500                       "permit_consumed": consumed},
 501         }
 502         return HostReadSummary(public, 4096)
 503 
 504     def __repr__(self):
 505         return "<AuthorityReadHost redacted>"
 506 
 507     def __reduce_ex__(self, protocol):
 508         raise TypeError("HOST_NOT_SERIALIZABLE")
```

## C05: D:\毕业设计\auth-lifecycle\scripts\read_dsat_authority_once.py
SHA-256 16f542aca76c566ab7f80ee166cb7c5983d259b9abb62cbab6f53a6f14653e58

```text
   1 """Minimal one-shot client. Live H2 is disabled; injected offline transport only."""
   2 import argparse
   3 import json
   4 from pathlib import Path
   5 
   6 from auth_lifecycle.online_state.dsat_authority_read_host import HostReadSummary, RIGHT
   7 from auth_lifecycle.online_state.protocol import canonical, strict_json
   8 
   9 
  10 class ClientRefusal(ValueError):
  11     pass
  12 
  13 
  14 class StrictParser(argparse.ArgumentParser):
  15     def error(self, message):
  16         raise ClientRefusal("UNSUPPORTED_CLIENT_ARGUMENTS")
  17 
  18 
  19 def parse_args(argv):
  20     parser = StrictParser(add_help=False)
  21     parser.add_argument("--mode", choices=["offline"], required=True)
  22     parser.add_argument("--manifest", required=True)
  23     return parser.parse_args(argv)
  24 
  25 
  26 class OfflineInvocation:
  27     def __init__(self, transport):
  28         self._transport = transport
  29         self.used = False
  30 
  31     def run(self, manifest):
  32         if self.used:
  33             raise ClientRefusal("CLIENT_ALREADY_USED")
  34         if (type(manifest) is not dict or set(manifest) != {"schema", "mode", "payload"}
  35                 or manifest["schema"] != "dsat-a1-offline-client/1" or manifest["mode"] != "OFFLINE_A1"):
  36             raise ClientRefusal("INVALID_OFFLINE_MANIFEST")
  37         body = manifest["payload"]
  38         if (type(body) is not dict or set(body) != {"authorization_ref", "permit_ref", "read_scope_ref"}
  39                 or any(type(x) is not str or not 1 <= len(x) <= 160 for x in body.values())):
  40             raise ClientRefusal("INVALID_OFFLINE_MANIFEST")
  41         self.used = True
  42         try:
  43             raw = self._transport.call(RIGHT, json.loads(canonical(body)))
  44             raw = canonical(raw) if type(raw) is dict else raw
  45             if type(raw) is not bytes or len(raw) > 4096:
  46                 raise ClientRefusal("INVALID_OFFLINE_RESPONSE")
  47             summary = HostReadSummary(strict_json(raw))
  48             return summary.to_json()
  49         except Exception:
  50             raise ClientRefusal("OFFLINE_CALL_FAILED") from None
  51 
  52 
  53 def main(argv=None, *, transport=None):
  54     try:
  55         args = parse_args(argv)
  56         # There is deliberately no live transport or credential/config loader.
  57         if transport is None:
  58             raise ClientRefusal("REAL_EXECUTION_DISABLED")
  59         path = Path(args.manifest)
  60         if path.suffix.lower() != ".json":
  61             raise ClientRefusal("INVALID_OFFLINE_MANIFEST")
  62         manifest = strict_json(path.read_bytes())
  63         raw = OfflineInvocation(transport).run(manifest)
  64         print(raw.decode("utf-8"))
  65         return 0
  66     except (ClientRefusal, ValueError, TypeError, KeyError, OSError):
  67         print(json.dumps({"status": "REFUSED", "reason": "OFFLINE_ONLY_OR_INVALID_REQUEST"}))
  68         return 2
  69 
  70 
  71 if __name__ == "__main__":
  72     raise SystemExit(main())
```

## C06: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\lab.py
SHA-256 ccf0c4ad6d21106fd1c0ef5aedcdad5b30bba49b2bf2f526ea69d79899409f26

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
 171         pid = self.processes["controller"].pid
 172         deadline = time.monotonic() + 8
 173         while time.monotonic() < deadline:
 174             for path in (self.root / "controller" / "barriers").glob("*_" + point + ".json"):
 175                 if json.loads(path.read_text())["pid"] == pid:
 176                     return path
 177             time.sleep(0.01)
 178         raise TimeoutError("BARRIER_TIMEOUT_" + point)
 179 
 180     def snapshot_cache(self):
 181         path = self.root / "cache" / "view.json"
 182         return path.read_bytes()
 183 
 184     def restore_cache(self, snapshot):
 185         process = self.processes.get("controller")
 186         if process is not None and process.poll() is None:
 187             raise RuntimeError("OLD_CONTROLLER_STILL_ACTIVE")
 188         path = (self.root / "cache" / "view.json").resolve()
 189         if not path.is_relative_to(self.root / "cache"):
 190             raise RuntimeError("RESTORE_PATH_OUTSIDE_CACHE")
 191         path.write_bytes(snapshot)
 192         self.log.emit("cache_restored", path="cache/view.json", restored_bytes=len(snapshot))
 193 
 194     def close(self):
 195         for role in ("controller", "provider", "authority"):
 196             self.stop(role)
 197         self.executor.shutdown(wait=True, cancel_futures=True)
 198         for stream in self.streams:
 199             stream.close()
```

## C07: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\cli.py
SHA-256 ae6b268c4e75abcb32bf37af9e554ee70a93bcb81df6c0b020df4b0050db1ba2

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

## C08: D:\毕业设计\auth-lifecycle\scripts\online_state.py
SHA-256 8e80d55ceade396cd1b231011185ae053a36b2690161ec3ecd4c05e343ae2d9d

```text
   1 """Run the isolated ONLINE_TRUSTED_STATE_V1 runtime from a source checkout."""
   2 from pathlib import Path
   3 import sys
   4 
   5 sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
   6 
   7 from auth_lifecycle.online_state.cli import main
   8 
   9 if __name__ == "__main__":
  10     main()
```

## C09: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\protocol.py
SHA-256 1d74afd2d1c252e371fe0d2b619120e588eab27bb15072e27168b812253fed79

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

## C10: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\migration.sql
SHA-256 cde954789b246d75b9f699e0e43a0d63ca199ee91470d76a7a1ca31b7d00420f

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

## C11: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\migration_2.sql
SHA-256 7b0c25f990cc101b3b69d3598ed250732f5c975e1dcc30d4980ee0933dd97719

```text
   1 -- Schema 2 accepts typed material bundles. Legacy string values remain readable.
   2 -- The encrypted application-row format and AAD remain schema-1 for compatibility.
   3 PRAGMA user_version = 2;
```

## C12: D:\毕业设计\auth-lifecycle\pyproject.toml
SHA-256 0d0a7fa9857a9aeca0882b21227544324ff5d6b46e32f31013dc8932382c67a9

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

## C13: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\isolation_service.py
SHA-256 37bd7f085e202a1ae2df9150118556f82ae6b85d38e93c892fa781621ae66f0e

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

## C14: D:\毕业设计\auth-lifecycle\src\auth_lifecycle\online_state\native_isolation_service.py
SHA-256 b2740390f2fb243378171ed182e64b8b72fa59f4a8fec7dace1a18e344257a34

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

## C15: D:\毕业设计\auth-lifecycle\scripts\m6_environment_acl.py
SHA-256 d367b5686d840854a8f221c2afdb980579192b6f675539971d7a8887271c8519

```text
   1 """Review/apply the exact legacy lab ACL prerequisite, with separate approval.
   2 
   3 Default is a read-only plan. --apply-authorization-id is meaningful only after
   4 the researcher explicitly authorizes changing this existing directory's ACL.
   5 """
   6 import argparse
   7 import ctypes as C
   8 from ctypes import wintypes as W
   9 import json
  10 from pathlib import Path
  11 
  12 from auth_lifecycle.online_state.isolation_acceptance import current_sid
  13 from auth_lifecycle.online_state.windows_isolation import inspect_file_acl, set_acl
  14 
  15 
  16 TARGET = Path(r"D:\毕业设计\auth-lifecycle\.runtime\l1")
  17 
  18 
  19 def plan():
  20     sid = current_sid()
  21     return {"target": str(TARGET), "current_root_sddl": inspect_file_acl(TARGET),
  22             "proposed_root_sddl": f"D:P(A;OICI;RC;;;OW)(A;OICI;FA;;;{sid})(A;OICI;FA;;;SY)",
  23             "change": "root DACL and its inherited ACE propagation only; contents unchanged",
  24             "retained_trusted_access": [sid, "S-1-5-18"],
  25             "reason": "legacy management credential and native DB inherit BUILTIN Users read access",
  26             "authorization_required": "M6 restricts existing objects to inspection; explicit additional ACL authorization required"}
  27 
  28 
  29 def main():
  30     p = argparse.ArgumentParser(); p.add_argument("--out", required=True)
  31     p.add_argument("--apply-authorization-id")
  32     a = p.parse_args(); out = Path(a.out).resolve()
  33     out.mkdir(parents=True, exist_ok=True)
  34     record = plan()
  35     (out / "LEGACY_ACL_CHANGE_PLAN.json").write_text(json.dumps(record, indent=2))
  36     if a.apply_authorization_id:
  37         rows = [{"path": str(x), "sddl": inspect_file_acl(x)} for x in [TARGET, *TARGET.rglob("*")]]
  38         backup = out / "LEGACY_ACL_BEFORE.json"
  39         if backup.exists(): raise ValueError("ACL_BACKUP_ALREADY_EXISTS")
  40         backup.write_text(json.dumps({"authorization_id": a.apply_authorization_id, "objects": rows}, indent=2))
  41         # SetNamedSecurityInfo propagates inherited ACEs to existing children;
  42         # SetFileSecurity alone does not supply that propagation contract.
  43         api=C.WinDLL("advapi32",use_last_error=True);kernel=C.WinDLL("kernel32",use_last_error=True)
  44         api.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes=[W.LPCWSTR,W.DWORD,C.POINTER(C.c_void_p),C.c_void_p]
  45         api.GetSecurityDescriptorDacl.argtypes=[C.c_void_p,C.POINTER(W.BOOL),C.POINTER(C.c_void_p),C.POINTER(W.BOOL)]
  46         api.SetNamedSecurityInfoW.argtypes=[W.LPWSTR,C.c_int,W.DWORD,C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p]
  47         api.SetNamedSecurityInfoW.restype=W.DWORD;kernel.LocalFree.argtypes=[C.c_void_p]
  48         sd=C.c_void_p();acl=C.c_void_p();present=W.BOOL();defaulted=W.BOOL()
  49         if not api.ConvertStringSecurityDescriptorToSecurityDescriptorW(record["proposed_root_sddl"],1,C.byref(sd),None):
  50             raise OSError(C.get_last_error(),"ACL_DESCRIPTOR")
  51         try:
  52             if not api.GetSecurityDescriptorDacl(sd,C.byref(present),C.byref(acl),C.byref(defaulted)):
  53                 raise OSError(C.get_last_error(),"ACL_EXTRACT")
  54             code=api.SetNamedSecurityInfoW(str(TARGET),1,4|0x80000000,None,None,acl,None)
  55             if code:raise OSError(code,"ACL_PROPAGATION")
  56         finally:kernel.LocalFree(sd)
  57         (out / "LEGACY_ACL_AFTER.json").write_text(json.dumps({"authorization_id": a.apply_authorization_id,
  58             "objects": [{"path": str(x), "sddl": inspect_file_acl(x)} for x in [TARGET, *TARGET.rglob("*")]]}, indent=2))
  59         record["applied"] = True
  60     print(json.dumps(record))
  61 
  62 
  63 if __name__ == "__main__": main()
```
