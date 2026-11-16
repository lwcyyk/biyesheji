"""R21 bounded initialization and owned offline Authority lifecycle.

Files, SQLite and test cryptography are real when explicitly selected by the
test owner. Listener/Handler/runtime actions are sealed offline adapters. No
production initializer, network admission or H2 activation is exposed here.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import ssl
import threading
import time
import weakref

from . import dsat_windows_runtime as win
from .dsat_authority_live import (LiveDeploymentIssuer, LiveAuthorityContext, SCOPE, ENVIRONMENT, digest, effective_config_digest,
    issue_start_approval, load_start_approval, read_consumption, consume_start_approval, finish_start_approval,
    read_bound_document, write_bound_document, write_marker, validate_marker, approval_paths)
from .dsat_authority_runtime import RuntimeConfig, build_synthetic_seed, probe_offline_dependencies
from .protocol import canonical


SafetyError, require = win.SafetyError, win.require
_BOOTSTRAPS = weakref.WeakKeyDictionary()
_LIFECYCLES = weakref.WeakKeyDictionary()
_ADAPTERS = weakref.WeakKeyDictionary()
_SQL_CONNECTIONS = {}
_CLI_LOOPS = {}
_SUPERVISORS = weakref.WeakKeyDictionary()
STATES = ("NEW", "PREFLIGHTED", "RESOURCES_RESERVED", "INITIALIZING", "SEED_READY", "STORE_READY",
          "HOST_DORMANT", "LISTENER_READY", "SERVICE_READY", "STOPPING", "STOPPED")
_NEXT = dict(zip(STATES, STATES[1:]))


class Ledger:
    def __init__(self):
        self.counts, self.cost_ns, self.events, self.files = {}, {}, [], []

    def count(self, key, limit, amount=1):
        value = self.counts.get(key, 0) + amount
        require(type(amount) is int and 0 <= amount and value <= limit, "RESOURCE_LIMIT")
        self.counts[key] = value
        return value

    def note(self, event, **fields):
        started = time.perf_counter_ns()
        require(type(event) is str and len(self.events) < 256, "RESOURCE_LIMIT")
        row = {"event": event, **fields}
        require(len(canonical(row)) <= 2048, "RESOURCE_LIMIT")
        self.events.append(row)
        self.cost_ns["C_logging"] = self.cost_ns.get("C_logging", 0) + time.perf_counter_ns() - started

    def snapshot(self):
        return {"counts": dict(self.counts), "cost_ns": dict(self.cost_ns), "events": list(self.events),
                "physical_VFS_IO": "NOT_MEASURED", "real_D1B2_cost": "NOT_MEASURED"}

    def timed(self, category, function, *args, **kwargs):
        started = time.perf_counter_ns()
        try:
            return function(*args, **kwargs)
        finally:
            self.cost_ns[category] = self.cost_ns.get(category, 0) + time.perf_counter_ns() - started


class OwnedResources:
    def __init__(self, scope, ledger=None):
        require(type(scope) is win.TestScope)
        self.scope, self.ledger = scope, ledger or Ledger()
        self._items, self._result, self._closed, self._errors = [], None, [], []

    def add(self, name, obj, closer, *, creator_scope):
        require(creator_scope is self.scope and callable(closer), "OWNERSHIP_UNPROVEN")
        require(self._result is None and len(self._items) < 128, "RESOURCE_LIMIT")
        found = next((x for x in self._items if x["object"] is obj), None)
        if found is not None:
            return obj
        self._items.append({"name": name, "object": obj, "closer": closer, "closed": False, "attempted": False})
        self.ledger.note("owned_acquired", name=name)
        return obj

    def close(self):
        if self._result is not None:
            return json.loads(json.dumps(self._result))
        return self._close_items(set(), final=True)

    def close_without(self, names):
        require(self._result is None, "LIFECYCLE_ORDER")
        return self._close_items(set(names), final=False)

    def _close_items(self, skip, *, final):
        for row in reversed(self._items):
            if row["attempted"] or row["name"] in skip: continue
            row["attempted"] = True
            try:
                row["closer"]()
                row["closed"] = True
                self._closed.append(row["name"])
            except Exception:
                self._errors.append({"resource": row["name"], "category": "CLEANUP_FAILED"})
        result = {"closed": list(self._closed), "errors": list(self._errors), "complete": not self._errors,
                        "persistent_files_deleted": 0, "foreign_resources_closed": 0}
        if not final: return result
        self._result = result
        try:
            self.ledger.note("owned_cleanup", complete=not self._errors, errors=len(self._errors))
        except Exception:
            self._result["complete"] = False
            self._result["errors"].append({"resource": "cleanup_audit", "category": "CLEANUP_FAILED"})
        return json.loads(json.dumps(self._result))


def _guard_SQL(action, arg1, arg2, database, trigger):
    if action in {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH} or (action == sqlite3.SQLITE_FUNCTION and str(arg2).lower() == "load_extension"):
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def connect_owned(scope, path, ledger, *, existing=False):
    require(type(scope) is win.TestScope)
    path = scope.path(path)
    require(path.parent.is_dir(), "PATH_DENIED")
    if existing:
        require(path.is_file(), "PATH_DENIED")
    else:
        require(not path.exists(), "PATH_DENIED")
        scope.write_new(path, b"")
    scope.count("file_SQLite_connections", 104)
    ledger.count("SQLite_connection_attempts", 2)
    connection = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, isolation_level=None, check_same_thread=False)
    _SQL_CONNECTIONS[connection] = {"scope": scope, "path": path, "closed": False}
    try:
        connection.row_factory = sqlite3.Row
        connection.set_authorizer(_guard_SQL)
        def trace(statement):
            ledger.count("SQL_executions_observed", 128)
            ledger.note("SQL_observed", kind=statement.strip().split()[0].upper())
        connection.set_trace_callback(trace)
        ledger.count("SQLite_connections", 2)
        return connection
    except BaseException:
        close_connection(connection)
        raise


def close_connection(connection):
    rec = _SQL_CONNECTIONS.get(connection)
    require(rec is not None, "OWNERSHIP_UNPROVEN")
    if not rec["closed"]:
        connection.close()
        rec["closed"] = True


def synthetic_seed(config_document, *, handle, material, grant_id="h2_grant_instance_001"):
    return build_synthetic_seed(RuntimeConfig.from_confirmed(config_document), grant_id=grant_id, handle=handle, material=material)


def generate_test_state_key(scope):
    require(type(scope) is win.TestScope)
    scope.count("test_state_keys_generated", 2)
    return secrets.token_bytes(32)


def initialize_fresh_seed(scope, path, seed, key, nonce, ledger, *, lease, checkpoint=lambda point: None):
    """Exactly15 normal SQL wrappers, at most one failure rollback. Owned files only."""
    require(type(scope) is win.TestScope and type(key) is bytes and len(key) == 32 and type(nonce) is bytes and len(nonce) == 12)
    win.validate_lease(lease, scope, Path(path).parent)
    require(seed["version"] == 2 and len(seed["history"]) == 2, "INITIALIZATION_FAILED")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    plaintext = canonical(seed["state"])
    blob = nonce + ledger.timed("C_key", AESGCM(key).encrypt, nonce, plaintext, b"auth-lifecycle/online-state/schema-1")
    require(len(blob) <= 16384, "RESOURCE_LIMIT")
    ledger.count("AES_encryptions", 1)
    connection = None
    committed = False
    def execute(sql, parameters=()):
        ledger.count("initialization_SQL", 16)
        return ledger.timed("C_database", connection.execute, sql, parameters)
    try:
        checkpoint("db_connect")
        connection = connect_owned(scope, path, ledger)
        execute("PRAGMA page_size=4096")
        require(execute("PRAGMA page_size").fetchone()[0] == 4096, "SCHEMA_MISMATCH")
        require(execute("PRAGMA max_page_count=2048").fetchone()[0] == 2048, "SCHEMA_MISMATCH")
        require(execute("PRAGMA journal_mode=DELETE").fetchone()[0] == "delete", "SCHEMA_MISMATCH")
        execute("PRAGMA synchronous=FULL")
        require(execute("PRAGMA synchronous").fetchone()[0] == 2, "SCHEMA_MISMATCH")
        execute("PRAGMA busy_timeout=0")
        execute("BEGIN IMMEDIATE")
        execute("CREATE TABLE authority_state(id INTEGER PRIMARY KEY CHECK(id=1),version INTEGER NOT NULL,ciphertext BLOB NOT NULL)")
        execute("CREATE TABLE authority_events(version INTEGER PRIMARY KEY,operation TEXT NOT NULL,projection TEXT NOT NULL)")
        execute("PRAGMA user_version=2")
        execute("INSERT INTO authority_state VALUES(1,?,?)", (2, blob))
        for row in seed["history"]:
            execute("INSERT INTO authority_events VALUES(?,?,?)", (row["version"], row["operation"], canonical({"provenance": seed["provenance"]}).decode()))
        checkpoint("before_commit")
        execute("COMMIT")
        committed = True
        checkpoint("seed_receipt")
        ledger.note("seed_committed", schema=2, version=2, rows=3, ciphertext_bytes=len(blob))
        receipt = {"schema": "r21-seed-receipt/1", "schema_version": 2, "state_version": 2,
            "history_count": 2, "DB_facts": scope.file_facts(path), "provenance": seed["provenance"],
            "world_read_state": 0, "world_decrypt": 0, "committed": True}
        publish_seed_descriptor(scope, Path(path).parent, receipt)
        return receipt
    except Exception:
        if connection is not None and connection.in_transaction:
            ledger.count("failure_rollbacks", 1)
            connection.rollback()
            ledger.count("initialization_SQL", 16)
        ledger.note("seed_failed", commit_known=committed)
        raise
    finally:
        if connection is not None:
            close_connection(connection)


def generate_test_TLS(scope, folder, ledger):
    """Real temporary test RSA/certificate only; no sockets, no system trust edits."""
    require(type(scope) is win.TestScope)
    scope.count("test_TLS_material_generated", 2)
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
    import ipaddress
    folder = scope.path(folder)
    require(folder.is_dir(), "PATH_DENIED")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.datetime.now(datetime.timezone.utc)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "h2-offline-test-001")])
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
        .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(hours=23))
        .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), False)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), False)
        .sign(key, hashes.SHA256()))
    keypath = scope.write_new(folder / "test_server.key", key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    certpath = scope.write_new(folder / "test_server.crt", cert.public_bytes(serialization.Encoding.PEM))
    ledger.count("test_TLS_key_generation", 2)
    return {"key": str(keypath), "certificate": str(certpath), "scope": "TEMPORARY_TEST_ONLY", "minimum": "TLS1.2", "IP_SAN": "127.0.0.1"}


def load_test_TLS(scope, material, ledger):
    require(type(scope) is win.TestScope and material.get("scope") == "TEMPORARY_TEST_ONLY", "OFFLINE_ONLY")
    key, cert = scope.path(material["key"]), scope.path(material["certificate"])
    scope.count("test_SSLContext_loads", 2)
    ledger.count("test_SSLContext_loads", 2)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    try:
        context.load_cert_chain(str(cert), str(key))
    except Exception:
        raise SafetyError("INITIALIZATION_FAILED") from None
    return context


class BoundedMetrics:
    def __init__(self, scope, path, ledger, checkpoint):
        self.scope, self.path, self.ledger, self.checkpoint = scope, scope.path(path), ledger, checkpoint

    def emit(self, event, **fields):
        self.ledger.count("Store_SQL_attempts", 8)
        self.checkpoint("metrics")
        self.ledger.count("database_log_events", 8)
        row = {"event": event, **fields}
        require(set(row) <= {"event", "number", "kind", "bound_value_bytes"} and len(canonical(row)) <= 2048, "RESOURCE_LIMIT")
        with self.path.open("ab") as stream:
            stream.write(canonical(row) + b"\n"); stream.flush(); os.fsync(stream.fileno())
        return row


class StrictStoreBootstrap:
    __slots__ = ("__weakref__",)

    def __init__(self, *args, **kwargs):
        raise SafetyError("CONTEXT_REQUIRED")

    @classmethod
    def for_test(cls, scope, directory, key_path, owner, ledger, *, lease, checkpoint=lambda point: None):
        require(type(scope) is win.TestScope and type(owner) is OwnedResources and owner.scope is scope)
        directory, key = scope.path(directory), scope.path(key_path)
        win.validate_lease(lease, scope, directory)
        require(directory.is_dir() and (directory / "authority.db").is_file() and key.is_file(), "PATH_DENIED")
        obj = object.__new__(cls)
        _BOOTSTRAPS[obj] = {"scope": scope, "directory": directory, "key": key, "owner": owner,
            "ledger": ledger, "checkpoint": checkpoint, "constructed": False, "lease": lease}
        return obj


def construct_preseeded_store(store, context, directory, key_path, operation_limit):
    require(type(context) is StrictStoreBootstrap and context in _BOOTSTRAPS)
    rec = _BOOTSTRAPS[context]
    require(not rec["constructed"], "REPLAY")
    rec["constructed"] = True
    win.validate_lease(rec["lease"], rec["scope"], rec["directory"])
    require(Path(directory) == rec["directory"] and Path(key_path) == rec["key"], "PATH_DENIED")
    scope, owner, ledger, checkpoint = (rec[k] for k in ("scope", "owner", "ledger", "checkpoint"))
    connection = None
    try:
        store.directory, store.key_path = rec["directory"], rec["key"]
        store.lock = threading.RLock()
        store.metrics = BoundedMetrics(scope, store.directory / "database_ops.jsonl", ledger, checkpoint)
        store.operation_limit, store.operations = 7, 0
        require(operation_limit is None or operation_limit == 7, "RESOURCE_LIMIT")
        connection = connect_owned(scope, store.directory / "authority.db", ledger, existing=True)
        # Capture before row-factory, schema, logging, marker or config failures.
        owner.add("Store.connection", connection, lambda: close_connection(connection), creator_scope=scope)
        store.connection = connection
        checkpoint("connection_registered")
        require(store.execute("PRAGMA user_version").fetchone()[0] == 2, "SCHEMA_MISMATCH")
        require(store.execute("PRAGMA journal_mode=WAL").fetchone()[0] == "wal", "SCHEMA_MISMATCH")
        store.execute("PRAGMA synchronous=FULL")
        require(store.execute("PRAGMA synchronous").fetchone()[0] == 2, "SCHEMA_MISMATCH")
        store.execute("PRAGMA busy_timeout=5000")
        store.execute("PRAGMA wal_autocheckpoint=1000")
        row = store.execute("SELECT version FROM authority_state WHERE id=1").fetchone()
        require(row is not None and row[0] == 2, "SCHEMA_MISMATCH")
        checkpoint("store_marker")
        marker = store.directory / "initialized"
        if not marker.exists():
            scope.write_new(marker, b"")
        config = {"schema_version": 2, "journal_mode": "wal", "synchronous": 2, "strict_preseeded": True}
        scope.write_new(store.directory / "storage_configuration.json", canonical(config))
        ledger.count("Store_constructions", 1)
        ledger.count("Store_SQL", store.operations, store.operations)
        return None
    except Exception:
        if connection is not None:
            close_connection(connection)
        raise


class OfflineConnection:
    def __init__(self, fail_close=False):
        self.closed, self.fail_close, self.total_changes, self.in_transaction = False, fail_close, 0, False

    def close(self):
        if self.fail_close:
            raise SafetyError("CLEANUP_FAILED")
        self.closed = True


class OfflineStore:
    def __init__(self, fail_close=False):
        self.connection = OfflineConnection(fail_close)
        self.lock, self.operations, self.reads = threading.RLock(), 0, 0

    def read_state(self):
        self.reads += 1
        raise SafetyError("P2_NOT_AUTHORIZED")


class OfflineListener:
    def __init__(self, scope, *, port=27443, address="127.0.0.1", TLS=True):
        self.scope, self.server_address, self.TLS_REQUIRED = scope, (address, port), TLS
        self.allow_reuse_address, self.exclusive_address_use = False, True
        self.binds, self.listens, self.closed, self.shutdown_calls = 0, 0, False, 0

    def bind_once(self):
        require(self.binds == 0, "REPLAY")
        self.binds += 1

    def listen_once(self):
        require(self.listens == 0, "REPLAY")
        self.listens += 1

    def server_close(self):
        self.closed = True

    def shutdown(self):
        self.shutdown_calls += 1
        raise AssertionError("NO_SHUTDOWN_WAIT_IN_OFFLINE_OR_SAME_THREAD")


class OfflineAdapters:
    def __init__(self, scope, *, fault=None, seed_writer=None, store_factory=None, listener_address="127.0.0.1", TLS=True):
        require(type(scope) is win.TestScope)
        self.scope, self.fault, self.seed_writer, self.store_factory = scope, fault, seed_writer, store_factory
        self.hits, self.stores, self.listeners = [], [], []
        self.listener_address, self.TLS, self.primary_secret = listener_address, TLS, ""
        _ADAPTERS[self] = scope

    def step(self, point):
        self.hits.append(point)
        if self.fault == point:
            codes = {"path": "PATH_DENIED", "identity": "IDENTITY_MISMATCH", "source": "SOURCE_MISMATCH", "dependency": "DEPENDENCY_MISMATCH", "listener_bind": "PORT_CONFLICT"}
            raise SafetyError(codes.get(point, "INITIALIZATION_FAILED"))

    def initialize(self, lifecycle):
        if self.seed_writer is not None:
            return self.seed_writer(lifecycle)
        # This is explicitly a simulated SQL adapter; actual file SQLite is
        # verified separately by the same public initialize_fresh_seed routine.
        self.step("db_connect")
        lifecycle.ledger.count("simulated_initialization_SQL", 16, 14)
        self.step("before_commit")
        lifecycle.ledger.count("simulated_initialization_SQL", 16)
        self.step("seed_receipt")
        return {"schema": "r21-seed-receipt/1", "schema_version": 2, "state_version": 2,
            "history_count": 2, "provenance": "SIMULATED_ADAPTER_ONLY", "committed": True}

    def construct_store(self, lifecycle):
        self.step("store_constructor")
        if self.store_factory is not None:
            store = self.store_factory(lifecycle)
        else:
            store = OfflineStore(fail_close=self.fault == "store_close")
            lifecycle.owner.add("Store.connection", store.connection, store.connection.close, creator_scope=self.scope)
        self.stores.append(store)
        return store


def build_bounded_test_listener(context, adapter, owner):
    require(type(context) is LiveAuthorityContext and type(adapter) is OfflineAdapters and _ADAPTERS.get(adapter) is context.scope)
    require(type(owner) is OwnedResources and owner.scope is context.scope)
    # TLS preparation precedes even the simulated bind; no socket exists here.
    adapter.step("handler")
    adapter.step("tls")
    require(adapter.TLS is True, "OFFLINE_ONLY")
    listener = OfflineListener(context.scope, address=adapter.listener_address, TLS=adapter.TLS)
    owner.add("listener", listener, listener.server_close, creator_scope=context.scope)
    adapter.listeners.append(listener)
    require(listener.server_address == ("127.0.0.1", 27443) and listener.TLS_REQUIRED is True
        and listener.allow_reuse_address is False and listener.exclusive_address_use is True, "PORT_CONFLICT")
    adapter.step("listener_bind")
    listener.bind_once(); listener.listen_once()
    return listener


def _instance_record(scope, root):
    return {"schema": "r21-owned-instance/1", "environment_id": ENVIRONMENT, "instance_id": secrets.token_hex(32),
        "root_facts": scope.file_facts(root), "source_digest": scope.source_digest,
        "config_digest": effective_config_digest(scope, root), "approved_scope": json.loads(json.dumps(SCOPE))}


class Lifecycle:
    __slots__ = ("__weakref__",)

    def __init__(self, scope, root, adapters, *, authorization_id, records=None):
        require(type(scope) is win.TestScope and type(adapters) is OfflineAdapters and _ADAPTERS.get(adapters) is scope)
        root = scope.path(root)
        ledger = Ledger()
        _LIFECYCLES[self] = {"scope": scope, "root": root, "adapter": adapters, "authorization": authorization_id,
            "records": {} if records is None else records, "state": "NEW", "ledger": ledger,
            "owner": OwnedResources(scope, ledger), "context": None, "store": None, "listener": None,
            "lease": None, "primary": None, "cleanup": None, "persistent_prepared": False}

    def _record(self):
        rec = _LIFECYCLES.get(self)
        require(rec is not None)
        return rec

    @property
    def state(self): return self._record()["state"]
    @property
    def ledger(self): return self._record()["ledger"]
    @property
    def owner(self): return self._record()["owner"]
    @property
    def context(self): return self._record()["context"]
    @property
    def root(self): return self._record()["root"]
    @property
    def lease(self): return self._record()["lease"]

    def _advance(self, target):
        rec = self._record()
        require(_NEXT.get(rec["state"]) == target, "LIFECYCLE_ORDER")
        facts = {
            "PREFLIGHTED": rec.get("preflight_complete", False),
            "RESOURCES_RESERVED": rec["lease"] is not None and rec["context"] is not None,
            "INITIALIZING": rec["persistent_prepared"],
            "SEED_READY": rec["records"].get("seed", {}).get("committed") is True,
            "STORE_READY": rec["store"] is not None and rec["records"].get("start_claimed") is True,
            "HOST_DORMANT": rec["context"] is not None and rec["context"].metadata()["registrations"] == 1 if target == "HOST_DORMANT" else True,
            "LISTENER_READY": rec["listener"] is not None,
            "SERVICE_READY": "Ready" in rec["records"],
            "STOPPING": True,
            "STOPPED": rec["cleanup"] is not None and rec["cleanup"]["complete"] is True,
        }
        require(facts.get(target) is True, "LIFECYCLE_ORDER")
        rec["state"] = target
        rec["records"]["phase"] = target
        self.ledger.note("transition", state=target)
        if rec["lease"] is not None and target not in {"STOPPED"}:
            self._journal("transition")

    def _journal(self, event):
        rec = self._record()
        if rec["lease"] is None:
            return
        win.validate_lease(rec["lease"], rec["scope"], rec["root"])
        name = "lifecycle_" + digest(rec["authorization"])[:16] + ".jsonl"
        path = rec["scope"].path(rec["root"] / name)
        self.ledger.count("lifecycle_journal_records", 32)
        payload = canonical({"event": event, "phase": rec["state"], "start_claimed": bool(rec["records"].get("start_claimed")),
            "instance_id": rec["records"].get("instance", {}).get("instance_id"),
            "source_digest": rec["scope"].source_digest, "source_kind": "OWNED_OFFLINE_TEST"}) + b"\n"
        if not path.exists(): rec["scope"].write_new(path, payload)
        else:
            with path.open("ab") as stream:
                stream.write(payload); stream.flush(); os.fsync(stream.fileno())

    def _abort(self, error, *, uncertain=False):
        rec = self._record()
        rec["primary"] = error.code if type(error) is SafetyError else "INITIALIZATION_FAILED"
        if rec["context"] is not None:
            try:
                rec["context"].finish_approval(successful=False)
            except Exception:
                uncertain = True
            rec["context"].retire()
        if rec["lease"] is not None and "instance" in rec["records"]:
            try: write_marker(rec["scope"], rec["root"], rec["records"]["instance"], "RECOVERY_REQUIRED", authorization_id=rec["authorization"])
            except Exception: uncertain = True
        rec["cleanup"] = self.ledger.timed("C_cleanup", self.owner.close)
        rec["state"] = "RECOVERY_REQUIRED" if uncertain or not rec["cleanup"]["complete"] else "FAILED"
        rec["records"]["phase"] = rec["state"]
        self.ledger.note("safe_failure", primary=rec["primary"], state=rec["state"])
        return self.status()

    def prepare(self):
        rec = self._record(); adapter, scope = rec["adapter"], rec["scope"]
        require(self.state == "NEW", "LIFECYCLE_ORDER")
        try:
            for point in ("path", "identity", "source", "dependency"):
                self.ledger.timed("C_" + ("source_validation" if point == "source" else "identity"), adapter.step, point)
            self.ledger.timed("C_source_validation", scope.sources); scope.path(self.root)
            evidence = self.ledger.timed("C_identity", win.self_process_facts, scope)
            self.ledger.timed("C_dependency_check", probe_offline_dependencies)
            rec["preflight_complete"] = True
            self._advance("PREFLIGHTED")
            adapter.step("mkdir")
            if not self.root.exists(): scope.directory(self.root)
            lease = win.reserve_instance(scope, self.root)
            rec["lease"] = self.owner.add("instance.lock", lease, lease.close, creator_scope=scope)
            instance, approval = prepare_resources_with_lease(scope, self.root, rec["authorization"], lease)
            issuer = LiveDeploymentIssuer.for_owned_test(scope, evidence)
            rec["context"] = issuer.bind_instance(self.root, lease, instance, authorization_id=rec["authorization"])
            rec["records"]["instance"] = instance
            self._advance("RESOURCES_RESERVED")
            rec["persistent_prepared"] = True
            adapter.step("after_reserve")
            return self.status()
        except Exception as error:
            return self._abort(error, uncertain=rec["persistent_prepared"])

    def initialize(self):
        rec = self._record(); adapter = rec["adapter"]
        require(self.state == "RESOURCES_RESERVED", "LIFECYCLE_ORDER")
        try:
            adapter.step("key_generate"); adapter.step("key_write"); adapter.step("TLS_material")
            self._advance("INITIALIZING")
            receipt = self.ledger.timed("C_initialization", adapter.initialize, self)
            require(receipt["committed"] is True and receipt["schema_version"] == 2, "INITIALIZATION_FAILED")
            rec["records"]["seed"] = receipt
            if not (self.root / "seed_descriptor.json").exists(): publish_seed_descriptor(rec["scope"], self.root, receipt)
            write_marker(rec["scope"], self.root, rec["records"]["instance"], "SEED_READY", authorization_id=rec["authorization"])
            self._advance("SEED_READY")
            return self.status()
        except Exception as error:
            return self._abort(error, uncertain=True)

    def start_owned(self):
        rec = self._record(); adapter = rec["adapter"]
        require(self.state == "SEED_READY", "LIFECYCLE_ORDER")
        try:
            rec["context"].claim_start(rec["context"].epoch)
            rec["records"]["start_claimed"] = True
            self._journal("start_claim_before_Store")
            adapter.step("start_claim")
            store = self.ledger.timed("C_database", adapter.construct_store, self)
            rec["store"] = store
            self.ledger.count("lifecycle_Store_count", 1)
            self._advance("STORE_READY")
            adapter.step("host_register")
            DB_path = None
            if hasattr(store, "directory"):
                require(Path(store.directory) == self.root, "IDENTITY_MISMATCH")
                DB_path = self.root / "authority.db"
                rec["records"]["DB_reference"] = {"path": str(DB_path), "facts": rec["scope"].file_facts(DB_path)}
                rec["records"]["key_reference"] = {"path": str(store.key_path), "facts": rec["scope"].file_facts(store.key_path)}
            self.ledger.timed("C_host", rec["context"].bind_dormant_store, store, store, DB_path)
            self._advance("HOST_DORMANT")
            # Import only in the new52 domain; legacy/R19 suites use no service.
            from .services import bounded_authority_listener
            listener = self.ledger.timed("C_listener", bounded_authority_listener, rec["context"], adapter, self.owner)
            rec["listener"] = listener
            self._advance("LISTENER_READY")
            adapter.step("ready")
            rec["records"]["Ready"] = {"epoch": rec["context"].epoch, "P2": False, "source_kind": "OFFLINE_LISTENER_ADAPTER"}
            self._advance("SERVICE_READY")
            rec["context"].note_started()
            adapter.step("runtime_died")
            return self.status()
        except Exception as error:
            return self._abort(error, uncertain=self.state == "SERVICE_READY")

    def stop_owned(self):
        rec = self._record()
        if self.state in {"STOPPED", "FAILED", "RECOVERY_REQUIRED"}:
            return self.status()
        require(self.state == "SERVICE_READY", "LIFECYCLE_ORDER")
        try:
            self._advance("STOPPING")
        except Exception as error:
            return self._abort(error, uncertain=True)
        rec["context"].retire()
        interim = self.owner.close_without({"instance.lock"})
        try:
            rec["context"].finish_approval(successful=interim["complete"])
        except Exception:
            self.owner._errors.append({"resource": "durable_finish", "category": "CLEANUP_FAILED"})
        rec["cleanup"] = self.ledger.timed("C_shutdown", self.owner.close)
        if rec["cleanup"]["complete"]:
            self._advance("STOPPED")
        else:
            rec["state"] = "RECOVERY_REQUIRED"; rec["records"]["phase"] = rec["state"]
        return self.status()

    def status(self):
        rec = self._record()
        return {"schema": "r21-lifecycle-status/1", "state": rec["state"], "primary_error": rec["primary"],
            "cleanup": rec["cleanup"], "observed_at_monotonic_ns": time.monotonic_ns(),
            "source_kind": "OFFLINE_ONLY", "INSTANCE_RUNNING": False, "P2": False,
            "source_reads": 0, "start_claimed": bool(rec["records"].get("start_claimed")),
            "live_service_qualification": False}

    def records(self):
        return json.loads(json.dumps(self._record()["records"]))


def recover_classify(scope, root, records, *, expected_root_facts=None):
    """Metadata/provenance only. No SQL, key loading, decrypt, repair or restart."""
    require(type(scope) is win.TestScope and type(records) is dict)
    root = scope.path(root)
    if not root.exists():
        result = "NEW"
    else:
        facts = scope.file_facts(root)
        expected = expected_root_facts or records.get("instance", {}).get("root_facts")
        if expected is None or expected != facts:
            result = "RECOVERY_REQUIRED"
        elif records.get("phase") == "STOPPED":
            result = "STOPPED_RECORDED_NOT_LIVENESS_ATTESTED"
        else:
            result = "RECOVERY_REQUIRED"
        for kind in ("DB_reference", "key_reference"):
            ref = records.get(kind)
            if ref is not None:
                try:
                    if scope.file_facts(ref["path"]) != ref["facts"]:
                        result = "RECOVERY_REQUIRED"
                except Exception:
                    result = "RECOVERY_REQUIRED"
    return {"status": result, "SQL": 0, "key_loads": 0, "world_decrypt": 0, "automatic_start": False,
            "marker_repair": False, "key_DB_content_verified": False, "P2": False}


def prepare(lifecycle): return lifecycle.prepare()
def start_owned(lifecycle): return lifecycle.start_owned()
def status_record(lifecycle): return lifecycle.status()
def stop_owned(lifecycle): return lifecycle.stop_owned()


def dispatch_offline_operation(operation, manifest, approval_ref, result_path=None):
    """Six strict offline operations. A vanished process context is never restored.

    In-process driver calls share their registered context. A new CLI process
    can classify stored receipts, but cannot resume an old ephemeral authority.
    D1-B2 admission remains absent and is explicitly reported by the interface.
    """
    require(operation in {"prepare", "initialize", "start", "status", "stop", "recover"}, "UNSUPPORTED_ARGUMENTS")
    require(Path(approval_ref or "") == win.RECORD / "APPROVAL_RECEIPT.json", "APPROVAL_REQUIRED")
    path = Path(manifest)
    require(path.is_absolute() and path.is_relative_to(win.OUTPUT) and path.suffix == ".json", "PATH_DENIED")
    for parent in (path, *path.parents):
        if parent.exists():
            require(not parent.is_symlink() and not (getattr(parent.lstat(), "st_file_attributes", 0) & 0x400), "PATH_DENIED")
    require(path.stat().st_size <= 16384, "RESOURCE_LIMIT")
    from .protocol import strict_json
    request = strict_json(path.read_bytes())
    require(type(request) is dict and set(request) == {"run_root", "instance_root", "authorization_id"}, "UNSUPPORTED_ARGUMENTS")
    scope = win.authorize_test_scope(request["run_root"])
    root = scope.path(request["instance_root"])
    key = (str(root), os.getpid())
    if operation == "prepare":
        require(key not in _CLI_LOOPS, "REPLAY")
        value = prepare_persistent_instance(scope, root, request["authorization_id"])
    elif operation == "initialize":
        value = initialize_persistent_instance(scope, root, request["authorization_id"])
    elif operation == "start":
        # The shell is not a daemon launcher in this authorization. Independent
        # starts run in the registered owned worker/supervisor entry. The main
        # test driver may keep an inline supervisor for the six-operation check.
        require(os.getpid() == json.loads((scope.root / "RUN_START.json").read_text(encoding="utf-8"))["main_pid"], "OFFLINE_ONLY")
        require(key not in _CLI_LOOPS, "REPLAY")
        manager = supervise_persistent_offline(scope, root, request["authorization_id"])
        _CLI_LOOPS[key] = manager
        value = manager.snapshot()
    elif operation == "recover":
        value = recover_persistent(scope, root, request["authorization_id"])
    elif operation == "status":
        manager = _CLI_LOOPS.get(key)
        value = manager.snapshot() if manager is not None else status_persistent(scope, root, request["authorization_id"])
    else:
        manager = _CLI_LOOPS.get(key)
        value = manager.stop() if manager is not None else stop_persistent(scope, root, request["authorization_id"])
    result = {"status": "OFFLINE_OPERATION_COMPLETED", "operation": operation, "result": value,
              "source_kind": "SIMULATED_SQL_AND_LISTENER_ADAPTER", "D1B2_executable": False,
              "cross_process_resume": "DURABLE_RESOURCE_AND_ACTION_REVALIDATION", "P2": False}
    write_bound_document(scope, root / "operation_receipt.json", result, replace=True)
    if result_path is not None:
        scope.write_new(result_path, canonical(result))
    return result


def load_persistent_instance(scope, root):
    root = scope.path(root)
    path = root / "instance.json"
    try:
        require(path.is_file() and path.stat().st_size <= 16384, "RECOVERY_REQUIRED")
        instance = json.loads(path.read_text(encoding="utf-8"))
        require(type(instance) is dict and set(instance) == {"schema", "environment_id", "instance_id", "root_facts", "source_digest", "config_digest", "approved_scope"}
            and instance["schema"] == "r21-owned-instance/1" and instance["environment_id"] == ENVIRONMENT
            and instance["root_facts"] == scope.file_facts(root) and instance["source_digest"] == scope.source_digest
            and instance["config_digest"] == effective_config_digest(scope, root) and instance["approved_scope"] == SCOPE,
            "IDENTITY_MISMATCH")
        return instance
    except SafetyError: raise
    except Exception: raise SafetyError("RECOVERY_REQUIRED") from None


def publish_seed_descriptor(scope, root, receipt):
    body = {"schema": "r22-seed-resource/1", "run_id": scope.root.name, "root_facts": scope.file_facts(root),
        "source_digest": scope.source_digest, "SID": scope.SID, "schema_version": 2, "state_version": 2,
        "grant_count": 1, "queued_count": 1, "P2": False,
        "kind": "REAL_OWNED_TEST_SQLITE" if "DB_facts" in receipt else "SIMULATED_PERSISTENT_SEED_DESCRIPTOR",
        "DB_facts": receipt.get("DB_facts"), "provenance": receipt.get("provenance", "SIMULATED_ADAPTER_ONLY")}
    path = Path(root) / "seed_descriptor.json"
    if path.exists():
        existing = read_seed_descriptor(scope, root)
        require(existing["root_facts"] == body["root_facts"], "RECOVERY_REQUIRED")
        return existing
    write_bound_document(scope, path, body)
    return body


def read_seed_descriptor(scope, root):
    body = read_bound_document(scope, Path(root) / "seed_descriptor.json")
    require(body.get("schema") == "r22-seed-resource/1" and body.get("run_id") == scope.root.name
        and body.get("root_facts") == scope.file_facts(root) and body.get("source_digest") == scope.source_digest
        and body.get("SID") == scope.SID and body.get("schema_version") == body.get("state_version") == 2
        and body.get("grant_count") == body.get("queued_count") == 1 and body.get("P2") is False, "RECOVERY_REQUIRED")
    if body.get("DB_facts") is not None:
        require(body["DB_facts"] == scope.file_facts(Path(root) / "authority.db"), "RECOVERY_REQUIRED")
    return body


def prepare_resources_with_lease(scope, root, authorization_id, lease):
    win.validate_lease(lease, scope, root)
    root = scope.path(root)
    if (root / "instance.json").exists():
        instance = load_persistent_instance(scope, root)
        marker = validate_marker(scope, root, instance, {"PREPARED", "SEED_READY", "STOPPED"})
    else:
        # A preseeded DB may only be adopted with the owned initializer's full
        # descriptor. An unlabelled existing database is an unknown resource.
        seeded = (root / "seed_descriptor.json").exists()
        if (root / "authority.db").exists(): read_seed_descriptor(scope, root)
        if seeded: read_seed_descriptor(scope, root)
        instance = _instance_record(scope, root)
        scope.write_new(root / "instance.json", canonical(instance))
        write_marker(scope, root, instance, "SEED_READY" if seeded else "PREPARED", authorization_id=authorization_id)
        marker = validate_marker(scope, root, instance)
    grant = issue_start_approval(scope, root, instance, authorization_id, lease, allow_new=True)
    require(read_consumption(grant, lease)[-1]["state"] == "UNCLAIMED", "REPLAY")
    require(marker["phase"] in {"PREPARED", "SEED_READY", "STOPPED"}, "RECOVERY_REQUIRED")
    return instance, grant


def prepare_persistent_instance(scope, root, authorization_id):
    require(type(scope) is win.TestScope)
    root = scope.path(root)
    if not root.exists(): scope.directory(root)
    lease = win.reserve_instance(scope, root)
    try:
        instance, grant = prepare_resources_with_lease(scope, root, authorization_id, lease)
        return {"status": "PREPARED", "instance": instance, "approval": grant.body(), "P2": False}
    finally: lease.close()


def initialize_persistent_instance(scope, root, authorization_id):
    lease = win.reserve_instance(scope, root)
    try:
        instance = load_persistent_instance(scope, root)
        grant = load_start_approval(scope, root, instance, authorization_id, lease)
        require(read_consumption(grant, lease)[-1]["state"] == "UNCLAIMED", "REPLAY")
        validate_marker(scope, root, instance, {"PREPARED", "SEED_READY", "STOPPED"})
        if not (Path(root) / "seed_descriptor.json").exists():
            publish_seed_descriptor(scope, root, {"provenance": "SIMULATED_PERSISTENT_SEED_DESCRIPTOR"})
        seed = read_seed_descriptor(scope, root)
        write_marker(scope, root, instance, "SEED_READY", authorization_id=authorization_id,
            epoch=grant.body()["process_epoch"])
        return {"status": "SEED_READY", "kind": seed["kind"], "P2": False, "SQLite_calls": 0}
    finally: lease.close()


class OfflineSupervisor:
    __slots__ = ("__weakref__",)
    def __init__(self, *args, **kwargs): raise SafetyError("CONTEXT_REQUIRED")

    def snapshot(self):
        rec = _SUPERVISORS.get(self); require(rec is not None)
        value = status_persistent(rec["scope"], rec["root"], rec["authorization"])
        value["owned_supervisor_current_process"] = not rec["closed"]
        return value

    def stop(self):
        rec = _SUPERVISORS.get(self); require(rec is not None)
        if rec["closed"]: return self.snapshot()
        rec["context"].retire()
        cleanup = rec["owner"].close()
        try:
            rec["context"].finish_approval(successful=cleanup["complete"])
        finally:
            rec["lease"].close(); rec["closed"] = True
        return self.snapshot()


def supervise_persistent_offline(scope, root, authorization_id, *, expected_epoch=None, control_name=None, request_context=None):
    """Real independent-process admission; all Store/Handler/listener objects are offline adapters."""
    require(type(scope) is win.TestScope)
    request_context = {} if request_context is None else request_context
    require(type(request_context) is dict and set(request_context) <= {"issuer_alias", "source_alias", "client_alias", "display"}, "UNSUPPORTED_ARGUMENTS")
    root = scope.path(root)
    lease = win.reserve_instance(scope, root)
    owner = OwnedResources(scope); context = None
    try:
        instance = load_persistent_instance(scope, root)
        grant = load_start_approval(scope, root, instance, authorization_id, lease)
        require(expected_epoch is None or expected_epoch == grant.body()["process_epoch"], "STALE_EPOCH")
        require(read_consumption(grant, lease)[-1]["state"] == "UNCLAIMED", "REPLAY")
        read_seed_descriptor(scope, root)
        validate_marker(scope, root, instance, {"SEED_READY", "STOPPED"})
        issuer = LiveDeploymentIssuer.for_owned_test(scope, win.self_process_facts(scope))
        context = issuer.bind_instance(root, lease, instance, authorization_id=authorization_id)
        context.claim_start(context.epoch)
        store = OfflineStore()
        owner.add("Store.connection", store.connection, store.connection.close, creator_scope=scope)
        context.bind_dormant_store(store, store)
        adapter = OfflineAdapters(scope)
        from .services import bounded_authority_listener
        listener = bounded_authority_listener(context, adapter, owner)
        context.note_started(control_name)
        obj = object.__new__(OfflineSupervisor)
        _SUPERVISORS[obj] = {"scope": scope, "root": root, "authorization": authorization_id,
            "context": context, "store": store, "listener": listener, "owner": owner, "lease": lease, "closed": False}
        return obj
    except Exception:
        if context is not None:
            try: context.finish_approval(successful=False)
            except Exception: pass
            context.retire()
        owner.close(); lease.close()
        raise


def status_persistent(scope, root, authorization_id):
    instance = load_persistent_instance(scope, root)
    grant = load_start_approval(scope, root, instance, authorization_id)
    rows = read_consumption(grant); marker = validate_marker(scope, root, instance)
    last = rows[-1]; owner = last["owner"]
    liveness = "HISTORICAL_ONLY"
    if owner is not None:
        try:
            recorded = win.recorded_owner(scope, owner)
            if recorded["exit_recorded"]: liveness = "EXIT_CONFIRMED_BY_CREATOR"
            else:
                win.verify_recorded_owner_live(scope, owner); liveness = "OWNED_PROCESS_ALIVE"
        except SafetyError: liveness = "UNKNOWN_OWNER_LIVENESS"
    return {"status": "PERSISTENT_STATUS", "instance_id": instance["instance_id"],
        "authorization_id": authorization_id, "process_epoch": grant.body()["process_epoch"],
        "consumption_state": last["state"], "START_APPROVAL_CONSUMED": last["state"] != "UNCLAIMED",
        "START_SUCCEEDED": last["effect_count"] == 1, "effect_count": last["effect_count"],
        "marker_phase": marker["phase"], "owner": owner, "liveness": liveness, "P2": False,
        "actual_Authority_service": False, "current_native_eligible": False}


def stop_persistent(scope, root, authorization_id, *, expected_epoch=None, expected_owner=None):
    instance = load_persistent_instance(scope, root)
    grant = load_start_approval(scope, root, instance, authorization_id)
    require(expected_epoch is None or expected_epoch == grant.body()["process_epoch"], "STALE_EPOCH")
    rows = read_consumption(grant); marker = validate_marker(scope, root, instance)
    owner = rows[-1]["owner"]
    require(expected_owner is None or expected_owner == owner, "IDENTITY_MISMATCH")
    if rows[-1]["state"] == "FINISHED":
        return {"status": "STOPPED_HISTORICAL", "P2": False, "signal_sent": False}
    require(rows[-1]["state"] == "STARTED" and marker["owner"] == owner
        and marker["process_epoch"] == grant.body()["process_epoch"] and marker["control_name"] is not None, "RECOVERY_REQUIRED")
    win.signal_recorded_event(scope, owner, marker["control_name"])
    return {"status": "STOP_REQUEST_SENT", "P2": False, "signal_sent": True, "owner": owner}


def recover_persistent(scope, root, authorization_id):
    try:
        value = status_persistent(scope, root, authorization_id)
        state = "STOPPED_RECORDED" if value["consumption_state"] == "FINISHED" else "RECOVERY_REQUIRED"
        return {"status": state, "history": value, "SQL": 0, "key_loads": 0, "world_decrypt": 0,
            "automatic_start": False, "old_approval_reopened": False, "P2": False}
    except SafetyError as error:
        return {"status": "RECOVERY_REQUIRED", "reason": error.code, "consumption": "UNPROVEN_ASSUME_UNAVAILABLE",
            "SQL": 0, "key_loads": 0, "world_decrypt": 0, "automatic_start": False, "P2": False}
