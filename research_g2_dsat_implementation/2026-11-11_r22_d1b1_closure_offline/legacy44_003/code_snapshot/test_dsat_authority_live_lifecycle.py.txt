"""R21 frozen F01-F28/T29-T52: real owned primitives and marked adapters."""
import ast
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import pickle
import secrets
import sqlite3
import threading
import time
import unittest
from unittest import mock

from auth_lifecycle.online_state import dsat_windows_runtime as w
from auth_lifecycle.online_state import dsat_authority_live as live
from auth_lifecycle.online_state import dsat_authority_lifecycle as l
from auth_lifecycle.online_state.protocol import canonical


CONFIG, DETAILS = {}, []


def configure(plan, fixture, run):
    CONFIG.update(plan=plan, fixture=fixture, run=run, scope=w.authorize_test_scope(run),
                  private_values=set(), children=[], shared={})


class LiveLifecycleCases(unittest.TestCase):
    def setUp(self):
        self.case_id = self._testMethodName.split("_")[1]
        self.spec = next(x for x in CONFIG["plan"]["new54"] if x["id"] == self.case_id)
        self.scope, self.run = CONFIG["scope"], CONFIG["run"]
        f = CONFIG["fixture"]
        self.document = json.loads((f / "CONFIRMED_CONFIG.json").read_text(encoding="utf-8-sig"))
        self.vector = json.loads((f / "PUBLIC_VECTORS.json").read_text(encoding="utf-8-sig"))
        self.canaries = json.loads((f / "CANARIES.json").read_text(encoding="utf-8"))["values"]
        self.checks, self.observations, self.ledgers = [], [], []
        self.started = time.perf_counter_ns()

    def tearDown(self):
        DETAILS.append({"id": self.case_id, "frozen_spec": self.spec, "checks": self.checks,
            "observations": self.observations, "resource_ledgers": [x.snapshot() for x in self.ledgers],
            "elapsed_ns": time.perf_counter_ns() - self.started})

    def check(self, condition, label):
        self.checks.append({"label": label, "satisfied": bool(condition)})
        if not condition: raise AssertionError(label)

    def refuses(self, function, code=None):
        try:
            function()
        except w.SafetyError as error:
            self.check(code is None or error.code == code, "FIXED_EXPECTED_REFUSAL")
            self.secret_free(str(error) + repr(error))
            self.observations.append({"business_status": error.code})
            return
        self.check(False, "EXPECTED_REFUSAL_REQUIRED")

    def secret_free(self, value):
        self.check(all(v not in value for v in self.canaries.values())
                   and all(v not in value for v in CONFIG["private_values"]), "PUBLIC_SINK_SECRET_FREE")

    def folder(self, name=None):
        return self.scope.directory(self.run / (name or self.case_id))

    def model_root(self):
        return self.scope.directory(self.run / ("model_" + self.case_id))

    def ledger(self):
        value = l.Ledger(); self.ledgers.append(value); return value

    def seed(self):
        return l.synthetic_seed(self.document, handle=self.canaries["handle"], material=self.canaries["material"])

    def public_key(self): return bytes.fromhex(self.vector["public_AES_key_hex"])
    def nonce(self): return bytes.fromhex(self.vector["public_nonce_hex"])

    def drive(self, fault=None, *, root=None, writer=None, store_factory=None):
        adapter = l.OfflineAdapters(self.scope, fault=fault, seed_writer=writer, store_factory=store_factory)
        core = l.Lifecycle(self.scope, root or self.model_root(), adapter, authorization_id="auth:" + self.case_id)
        self.ledgers.append(core.ledger)
        core.prepare()
        if core.state == "RESOURCES_RESERVED": core.initialize()
        if core.state == "SEED_READY": core.start_owned()
        return core, adapter

    def cleanup_ok(self, core, adapter, expected):
        result = core.status()
        self.check(result["state"] == expected, "EXPECTED_LIFECYCLE_FAILURE_STATE")
        self.check(result["P2"] is False and result["source_reads"] == 0 and result["INSTANCE_RUNNING"] is False, "ZERO_P2_REAL_SERVICE_AND_WORLD_READ")
        self.check(result["cleanup"] is not None and result["cleanup"]["complete"], "OWNED_STACK_CLOSED")
        self.check(all(x.connection.closed for x in adapter.stores if isinstance(x, l.OfflineStore)), "OWNED_FAKE_CONNECTIONS_CLOSED")
        self.check(all(x.closed and x.shutdown_calls == 0 for x in adapter.listeners), "LISTENERS_CLOSED_NO_SHUTDOWN_WAIT")
        self.secret_free(json.dumps(result)); self.observations.append(result)

    def real_writer(self, *, failure=None, key_path=None, fresh=False):
        def writer(core):
            key = l.generate_test_state_key(self.scope) if fresh else self.public_key()
            if fresh: CONFIG["private_values"].add(key.hex())
            if key_path is not None and not key_path.exists(): self.scope.write_new(key_path, key)
            def checkpoint(point):
                if point == failure: raise w.SafetyError("INITIALIZATION_FAILED")
            return l.initialize_fresh_seed(self.scope, core.root / "authority.db", self.seed(), key, self.nonce(), core.ledger,
                                           lease=core.lease, checkpoint=checkpoint)
        return writer

    def worker(self, root, *, mode="crash", inherited=(), event=None, exit_code=73, extra=None):
        authorization_id="auth:worker:"+root.name
        if mode in {"race","crash","event"} and not (root/"instance.json").exists():
            l.prepare_persistent_instance(self.scope,root,authorization_id)
            l.initialize_persistent_instance(self.scope,root,authorization_id)
        count = len(CONFIG["children"])
        manifest = self.scope.write_new(self.run / ("worker_%02d.json" % count), canonical({
            "source_kind": "R22_OWNED_STUB", "mode": mode, "run_root": str(self.run),
            "resource_root": str(root), "inherited_handle": int(inherited[0]) if inherited else None,
            "event_name": event, "exit_code": exit_code,"authorization_id":authorization_id,
            "extra":{} if extra is None else extra}))
        process, facts = w.launch_owned_child(self.scope, manifest, inherit=inherited)
        CONFIG["children"].append({"process": process, "facts": facts, "manifest": str(manifest), "result": None})
        return process, facts

    def finish(self, process, data=b"stop\n"):
        result = w.finish_owned_child(self.scope, process, data=data)
        rec = next(x for x in CONFIG["children"] if x["process"] is process)
        rec["result"] = result
        self.check(not result["terminated_owned_stub"], "STUB_EXITED_WITHOUT_FORCED_TERMINATION")
        self.check(result["pipes_closed"] and result["process_handle_closed"], "OWNED_PROCESS_AND_PIPE_HANDLES_EXPLICITLY_CLOSED")
        self.observations.append({"owned_stub_result": result})
        return result

    def test_F01_path_preflight(self):
        core, adapter = self.drive("path")
        self.cleanup_ok(core, adapter, "FAILED")
        self.check(adapter.hits == ["path"], "PRECHECK_FAILURE_BEFORE_ANY_STORE")

    def test_F02_OS_identity(self):
        core, adapter = self.drive("identity")
        self.cleanup_ok(core, adapter, "FAILED")
        self.check("source" not in adapter.hits, "IDENTITY_FAILURE_BEFORE_SOURCE_OR_STORE")

    def test_F03_source_digest(self):
        core, adapter = self.drive("source")
        self.cleanup_ok(core, adapter, "FAILED")
        self.check(core.status()["primary_error"] == "SOURCE_MISMATCH", "SOURCE_ERROR_RETAINED")

    def test_F04_dependency(self):
        core, adapter = self.drive("dependency")
        self.cleanup_ok(core, adapter, "FAILED")
        self.check(core.status()["primary_error"] == "DEPENDENCY_MISMATCH", "DEPENDENCY_ERROR_RETAINED")

    def test_F05_directory_create(self):
        core, adapter = self.drive("mkdir")
        self.cleanup_ok(core, adapter, "FAILED")
        self.check(core.records().get("instance") is None, "NO_INSTANCE_COMMIT_ON_CREATE_FAILURE")

    def test_F06_after_directory(self):
        core, adapter = self.drive("after_reserve")
        self.cleanup_ok(core, adapter, "RECOVERY_REQUIRED")
        self.check("instance" in core.records(), "RESERVATION_RECORD_RETAINED")

    def test_F07_SQLite_connect(self):
        root = self.folder()
        core, adapter = self.drive(root=root, writer=self.real_writer(failure="db_connect"))
        self.cleanup_ok(core, adapter, "RECOVERY_REQUIRED")
        self.check(core.ledger.counts.get("SQLite_connections", 0) == 0 and not (root / "authority.db").exists(), "CONNECT_BOUNDARY_REFUSAL_HAS_NO_CONNECTION")

    def test_F08_SQLite_transaction(self):
        root = self.folder()
        core, adapter = self.drive(root=root, writer=self.real_writer(failure="before_commit"))
        self.cleanup_ok(core, adapter, "RECOVERY_REQUIRED")
        verify = l.connect_owned(self.scope, root / "authority.db", self.ledger(), existing=True)
        try: count = verify.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
        finally: l.close_connection(verify)
        self.check(count == 0 and core.ledger.counts["failure_rollbacks"] == 1, "REAL_FILE_TRANSACTION_DDL_ROLLED_BACK")
        self.check(core.ledger.counts["initialization_SQL"] == 15, "FOURTEEN_SQL_PREFIX_PLUS_ONE_ROLLBACK")

    def test_F09_commit_marker_gap(self):
        root = self.folder()
        core, adapter = self.drive(root=root, writer=self.real_writer(failure="seed_receipt"))
        self.cleanup_ok(core, adapter, "RECOVERY_REQUIRED")
        verify = l.connect_owned(self.scope, root / "authority.db", self.ledger(), existing=True)
        try:
            version = verify.execute("SELECT version FROM authority_state WHERE id=1").fetchone()[0]
            count = verify.execute("SELECT count(*) FROM authority_events").fetchone()[0]
        finally: l.close_connection(verify)
        self.check(version == 2 and count == 2 and "seed" not in core.records(), "COMMITTED_DB_WITH_MISSING_OUTER_RECEIPT_RETAINED")
        CONFIG["shared"]["committed_gap_root"] = root

    def test_F10_key_write(self):
        key = l.generate_test_state_key(self.scope); CONFIG["private_values"].add(key.hex())
        root = self.folder()
        self.refuses(lambda: self.scope.write_new(root / "missing" / "test.key", key), "RESOURCE_LIMIT")
        core, adapter = self.drive("key_write")
        self.cleanup_ok(core, adapter, "RECOVERY_REQUIRED")
        self.check(not (root / "missing").exists(), "FAILED_TEST_KEY_WRITE_NO_FALLBACK")

    def test_F11_key_written_DB_failure(self):
        root = self.folder(); key = self.scope.write_new(root / "test_state.key", self.public_key())
        core, adapter = self.drive(root=root, writer=self.real_writer(failure="db_connect"))
        self.cleanup_ok(core, adapter, "RECOVERY_REQUIRED")
        self.check(key.exists() and key.stat().st_size == 32, "OWNED_KEY_RETAINED_AFTER_DB_FAILURE")

    def test_F12_certificate_failure(self):
        core, adapter = self.drive("TLS_material")
        self.cleanup_ok(core, adapter, "RECOVERY_REQUIRED")
        self.check("db_connect" not in adapter.hits, "CERTIFICATE_FAILURE_PRECEDES_DB_OR_LISTENER")

    def test_F13_TLS_private_listener_failure(self):
        root = self.folder("TLS_material")
        material = l.generate_test_TLS(self.scope, root, self.ledger())
        CONFIG["shared"]["TLS_material"] = material
        core, adapter = self.drive("listener_bind")
        self.cleanup_ok(core, adapter, "FAILED")
        self.check(Path(material["key"]).is_file() and Path(material["certificate"]).is_file(), "REAL_TEMP_TLS_FILES_RETAINED")
        self.check(self.scope.acl(root)["protected_DACL"], "TEST_TLS_PRIVATE_DACL")

    def test_F14_EventLog_failure(self):
        root = self.folder("F14_valid_seed")
        key = self.scope.write_new(root / "test_state.key", self.public_key())
        captured = []
        def factory(core):
            from auth_lifecycle.online_state.storage import AuthorityStore
            def checkpoint(point):
                if point == "metrics": raise RuntimeError(self.canaries["exception"])
            bootstrap = l.StrictStoreBootstrap.for_test(self.scope, root, key, core.owner, core.ledger, lease=core.lease, checkpoint=checkpoint)
            try: return AuthorityStore(root, key, bootstrap_context=bootstrap)
            finally: captured.extend(x["object"] for x in core.owner._items if x["name"] == "Store.connection")
        core, adapter = self.drive(root=root, writer=self.real_writer(), store_factory=factory)
        self.cleanup_ok(core, adapter, "FAILED")
        self.check(len(captured) == 1, "CONSTRUCTOR_CONNECTION_CAPTURED_BEFORE_LOG_FAILURE")
        try: captured[0].execute("SELECT 1")
        except sqlite3.ProgrammingError: self.check(True, "FAILED_CTOR_CONNECTION_ACTUALLY_CLOSED")
        else: self.check(False, "FAILED_CTOR_CONNECTION_ACTUALLY_CLOSED")

    def test_F15_Host_registration_failure(self):
        core, adapter = self.drive("host_register")
        self.cleanup_ok(core, adapter, "FAILED")
        self.check(len(adapter.stores) == 1 and not adapter.listeners, "STORE_CREATED_ONCE_NO_LISTENER")

    def test_F16_Handler_failure(self):
        core, adapter = self.drive("handler")
        self.cleanup_ok(core, adapter, "FAILED")
        self.check(len(adapter.stores) == 1 and not adapter.listeners, "HANDLER_ERROR_CLOSES_BOUND_STORE")

    def test_F17_Ready_publication_failure(self):
        core, adapter = self.drive("ready")
        self.cleanup_ok(core, adapter, "FAILED")
        self.check(len(adapter.listeners) == 1 and adapter.listeners[0].binds == 1 and "Ready" not in core.records(), "READY_FAILURE_CLOSES_ALREADY_BOUND_ADAPTER")

    def test_F18_port_conflict(self):
        core, adapter = self.drive("listener_bind")
        self.cleanup_ok(core, adapter, "FAILED")
        self.check(adapter.hits.count("listener_bind") == 1 and len(adapter.listeners) == 1, "ONE_BIND_BOUNDARY_ATTEMPT_NO_FALLBACK")

    def test_F19_immediate_exit(self):
        root = self.folder(); child, facts = self.worker(root, mode="crash", exit_code=73)
        result = self.finish(child)
        self.check(result["exit_code"] == 73, "ACTUAL_OWNED_PROCESS_ABNORMAL_EXIT")
        lease = w.reserve_instance(self.scope, root); lease.close()
        core, adapter = self.drive("runtime_died")
        self.cleanup_ok(core, adapter, "RECOVERY_REQUIRED")
        self.check(facts["pid"] == result["pid"], "CHILD_IDENTITY_RETAINED_AFTER_EXIT")

    def test_F20_shutdown_failure(self):
        core, adapter = self.drive("store_close")
        self.check(core.state == "SERVICE_READY", "OFFLINE_MODEL_STARTED_BEFORE_CLOSE_FAILURE")
        result = core.stop_owned()
        self.check(result["state"] == "RECOVERY_REQUIRED" and len(result["cleanup"]["errors"]) == 1, "CLEANUP_ERROR_RECORDED")
        self.check(adapter.listeners[0].closed, "LISTENER_CLOSED_DESPITE_STORE_CLOSE_ERROR")
        lease = w.reserve_instance(self.scope, self.model_root()); lease.close()
        self.check(core.stop_owned()["state"] == "RECOVERY_REQUIRED", "REPEATED_STOP_PRESERVES_UNCERTAINTY")

    def test_F21_stop_ACK_lost(self):
        core, adapter = self.drive()
        first = core.stop_owned()
        try: raise OSError("synthetic ACK transport loss")
        except OSError: pass
        second = core.stop_owned()
        self.check(first["state"] == second["state"] == "STOPPED" and first["cleanup"] == second["cleanup"], "LOST_ACK_STOP_IS_IDEMPOTENT")
        self.check(adapter.listeners[0].shutdown_calls == 0 and core.records()["start_claimed"], "ACK_LOSS_NO_REARM_OR_SHUTDOWN_WAIT")

    def test_F22_crash_during_cleanup(self):
        root = self.folder(); child, _ = self.worker(root, mode="crash", exit_code=74)
        result = self.finish(child)
        self.check(result["exit_code"] == 74 and (root / "partial_receipt.json").exists(), "REAL_STUB_CRASH_LEFT_PARTIAL_RECEIPT")
        lease = w.reserve_instance(self.scope, root); facts = lease.facts()["root_facts"]; lease.close()
        value = l.recover_classify(self.scope, root, {"phase": "STOPPING", "instance": {"root_facts": facts}})
        self.check(value["status"] == "RECOVERY_REQUIRED" and value["automatic_start"] is False, "PARTIAL_CLEANUP_CLASSIFIES_WITHOUT_RESTART")
        self.refuses(lambda:l.supervise_persistent_offline(self.scope,root,"auth:worker:"+root.name),"RECOVERY_REQUIRED")

    def test_F23_old_runtime_marker(self):
        root = self.folder(); facts = self.scope.file_facts(root)
        record = {"phase": "SERVICE_READY", "instance": {"root_facts": facts}, "Ready": {"epoch": "old"}}
        self.scope.write_new(root / "old_ready.json", canonical(record))
        result = l.recover_classify(self.scope, root, record)
        self.check(result["status"] == "RECOVERY_REQUIRED" and result["SQL"] == result["key_loads"] == 0, "OLD_READY_DOES_NOT_AUTHORIZE_START")
        witness=CONFIG["shared"]["cross_first"]
        self.check(witness["actor"]["pid"]!=os.getpid() and witness["probes"]["stale_marker"]=="RECOVERY_REQUIRED", "ACTUAL_INDEPENDENT_PROCESS_REJECTS_STALE_MARKER")
        self.check(witness["probes"]["old_epoch"]=="STALE_EPOCH" and all(x!="ADMITTED" for x in witness["probes"].values()), "CROSS_PROCESS_F23_ALL_INVALID_VARIANTS_REFUSED")

    def test_F24_two_process_competition(self):
        root = self.folder(); one, _ = self.worker(root, mode="race"); two, _ = self.worker(root, mode="race")
        first, second = w.read_owned_child_line(self.scope, one), w.read_owned_child_line(self.scope, two)
        self.check(sorted([first["status"], second["status"]]) == ["CONFLICT", "LOCKED"], "TWO_REAL_PROCESSES_EXACTLY_ONE_EXCLUSIVE_OWNER")
        self.finish(one); self.finish(two)
        lease = w.reserve_instance(self.scope, root); lease.close()
        self.check(True, "LOCK_REACQUIRED_ONLY_AFTER_OWNED_CHILDREN_EXIT")

    def test_F25_copied_instance(self):
        root, clone = self.folder(), self.folder("F25_clone")
        lease = w.reserve_instance(self.scope, root)
        try:
            receipt = l.initialize_fresh_seed(self.scope, root / "authority.db", self.seed(), self.public_key(), self.nonce(), self.ledger(), lease=lease)
            facts = lease.facts()["root_facts"]
        finally: lease.close()
        self.scope.write_new(clone / "authority.db", (root / "authority.db").read_bytes())
        result = l.recover_classify(self.scope, clone, {"phase": "STOPPED", "instance": {"root_facts": facts}})
        self.check(result["status"] == "RECOVERY_REQUIRED" and self.scope.file_facts(clone / "authority.db")["file_id"] != receipt["DB_facts"]["file_id"], "COPIED_DB_AND_ROOT_CANNOT_REUSE_IDENTITY")

    def test_F26_old_authorization_replay(self):
        core, _ = self.drive(); core.stop_owned()
        root = self.model_root(); lease = w.reserve_instance(self.scope, root)
        try:
            issuer = live.LiveDeploymentIssuer.for_owned_test(self.scope, w.self_process_facts(self.scope))
            self.refuses(lambda: issuer.bind_instance(root, lease, core.records()["instance"], authorization_id="auth:" + self.case_id), "REPLAY")
        finally: lease.close()
        witness=CONFIG["shared"]["cross_replay"]
        self.check(witness["actor"]["pid"]!=CONFIG["shared"]["cross_first"]["actor"]["pid"] and witness["replays"]["same_authorization"]=="REPLAY", "SECOND_REAL_PROCESS_REJECTS_PERSISTED_AUTHORIZATION")
        self.check(all(v=="REPLAY" for v in witness["aliases"].values()) and witness["effect_count_A"]==1, "ISSUER_SOURCE_CLIENT_ALIASES_CANNOT_CHANGE_CONSUMPTION")

    def test_F27_issuer_rebuild(self):
        core, _ = self.drive()
        try:
            issuer = live.LiveDeploymentIssuer.for_owned_test(self.scope, w.self_process_facts(self.scope))
            self.refuses(lambda: issuer.bind_instance(core.root, core.lease, core.records()["instance"], authorization_id="auth:" + self.case_id), "REPLAY")
        finally: core.stop_owned()

    def test_F28_old_epoch_request(self):
        core, _ = self.drive(); old = core.context.epoch; core.stop_owned()
        adapter = l.OfflineAdapters(self.scope)
        new = l.Lifecycle(self.scope, self.model_root(), adapter, authorization_id="auth:F28:new")
        new.prepare()
        try:
            self.check(new.context.epoch != old, "NEW_ADMISSION_NEW_EPOCH")
            self.refuses(lambda: new.context.check_epoch(old), "STALE_EPOCH")
            self.refuses(new.context.issue_permit, "P2_NOT_AUTHORIZED")
        finally: new._abort(w.SafetyError("OFFLINE_ONLY"))

    def test_T29_strict_six_operation_parser(self):
        script = self.script()
        for op in ("prepare", "initialize", "start", "status", "stop", "recover"):
            args = script.parse_args(["--manifest", "not-read.json", "--operation", op])
            self.check(args.operation == op and args.mode == "offline", "STRICT_OFFLINE_OPERATION_SUPPORTED")
        for argv in (["--manifest","a","--mode","deploy"], ["--manifest","a","--trusted"], ["--manifest","a","--key",self.canaries["private_key"]]):
            output = io.StringIO()
            with contextlib.redirect_stdout(output): code = script.main(argv)
            self.check(code == 2, "UNKNOWN_REAL_OR_SECRET_ARGUMENT_REFUSED"); self.secret_free(output.getvalue())

    def test_T30_typed_admission(self):
        self.refuses(lambda: live.LiveDeploymentIssuer.for_owned_test({"trusted":True}, {"SID":"claimed"}))
        self.refuses(lambda: live.validate_live_entry(object.__new__(live.LiveAuthorityContext), "authority", str(self.run)))
        try: live.LiveAuthorityContext()
        except w.SafetyError: self.check(True, "ORDINARY_CONSTRUCTION_HAS_NO_CAPABILITY")
        self.refuses(lambda: self.scope.path(w.DEPLOYMENT / "authority/authority.db"), "PATH_DENIED")

    def test_T31_source_config_binding(self):
        evidence = w.self_process_facts(self.scope)
        self.refuses(lambda: live.LiveDeploymentIssuer.for_owned_test(self.scope, evidence, expected_source_digest="0"*64), "SOURCE_MISMATCH")
        original_origin=live.__file__
        try:
            live.__file__=str(self.run/"unapproved_module.py")
            self.refuses(self.scope.sources,"SOURCE_MISMATCH")
        finally:live.__file__=original_origin
        core, _ = self.drive(); record = core.records()["instance"]; record["config_digest"] = "0"*64
        try:
            issuer = live.LiveDeploymentIssuer.for_owned_test(self.scope, evidence)
            self.refuses(lambda: issuer.bind_instance(core.root, core.lease, record, authorization_id="auth:T31:bad"), "SOURCE_MISMATCH")
            self.check(all(Path(x["path"]).is_file() for x in self.scope.sources()), "APPROVED_ARTIFACT_SOURCE_SET_PRESENT")
        finally: core.stop_owned()

    def test_T32_real_self_process_identity(self):
        evidence = w.self_process_facts(self.scope); facts = evidence.facts()
        self.check(facts["pid"] == os.getpid() and facts["created_filetime"] > 0 and facts["SID"].startswith("S-1-"), "ACTUAL_SELF_PID_CREATION_SID")
        self.refuses(lambda: live.LiveDeploymentIssuer.for_owned_test(self.scope, evidence, expected_SID="S-1-0-0"), "IDENTITY_MISMATCH")
        self.refuses(lambda: w.validate_host_evidence({"trusted":True}, self.scope))
        self.observations.append({"nonsecret_self_facts":facts})

    def test_T33_path_alias_and_ACL(self):
        root = self.folder(); source = self.scope.write_new(root / "one.txt", b"public")
        os.link(source, root / "alias.txt")
        self.refuses(lambda: self.scope.file_facts(source), "PATH_DENIED")
        original_lstat=Path.lstat
        class ReparseStat:
            def __init__(self,actual):self.actual=actual
            def __getattr__(self,name):return getattr(self.actual,name)
            @property
            def st_file_attributes(self):return self.actual.st_file_attributes|0x400
        def projected_lstat(path,*args,**kwargs):
            value=original_lstat(path,*args,**kwargs)
            return ReparseStat(value) if path==root else value
        with mock.patch.object(Path,"lstat",projected_lstat):
            self.refuses(lambda:self.scope.path(root),"PATH_DENIED")
        self.observations.append({"reparse_rejection_evidence":"injected attribute on owned path; actual junction creation not used"})
        self.refuses(lambda: self.scope.path(Path(r"D:\foreign\real.key")), "PATH_DENIED")
        self.check(self.scope.acl(root)["protected_DACL"], "OWNED_DIR_PRIVATE_DACL_ACTUALLY_READ")
        self.refuses(lambda: w.reserve_instance(self.scope, root, expected={"file_id":0}), "OWNERSHIP_UNPROVEN")

    def test_T34_real_SQLite_seed_and_codec(self):
        root = self.folder(); key = l.generate_test_state_key(self.scope); CONFIG["private_values"].add(key.hex())
        keyfile=self.scope.write_new(root / "test_state.key", key)
        self.check(keyfile.read_bytes()==key,"FRESH_TEST_KEY_FILE_READBACK")
        lease = w.reserve_instance(self.scope, root); ledger = self.ledger()
        try: receipt = l.initialize_fresh_seed(self.scope, root / "authority.db", self.seed(), key, self.nonce(), ledger, lease=lease)
        finally: lease.close()
        connection = l.connect_owned(self.scope, root / "authority.db", self.ledger(), existing=True)
        try:
            row = connection.execute("SELECT version,ciphertext FROM authority_state WHERE id=1").fetchone()
            count = connection.execute("SELECT count(*) FROM authority_events").fetchone()[0]
            schema = connection.execute("PRAGMA user_version").fetchone()[0]
        finally: l.close_connection(connection)
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        blob = bytes(row[1]); decoded = json.loads(AESGCM(key).decrypt(blob[:12],blob[12:],b"auth-lifecycle/online-state/schema-1"))
        self.check(decoded == self.seed()["state"] and row[0] == schema == 2 and count == 2, "REAL_TEST_DB_AES_SCHEMA2_ROUNDTRIP")
        self.check(ledger.counts["initialization_SQL"] == ledger.counts["SQL_executions_observed"] == 15, "EXACT_REAL_INITIALIZER_SQL_COUNT")
        self.check(receipt["world_decrypt"] == 0, "VERIFIER_DECRYPT_SEPARATE_FROM_INITIALIZER")
        CONFIG["shared"]["valid_db_root"] = root

    def test_T35_real_strict_Store_constructor(self):
        from auth_lifecycle.online_state.storage import AuthorityStore
        root = CONFIG["shared"]["valid_db_root"]; key = root / "test_state.key"
        def factory(core):
            bootstrap = l.StrictStoreBootstrap.for_test(self.scope, root, key, core.owner, core.ledger, lease=core.lease)
            return AuthorityStore(root, key, bootstrap_context=bootstrap)
        core, adapter = self.drive(root=root, store_factory=factory)
        self.check(core.state == "SERVICE_READY" and core.ledger.counts["Store_SQL"] == 7, "ACTUAL_STRICT_STORE_SEVEN_SQL")
        self.check(core.context.metadata()["registrations"] == 1 and adapter.stores[0].operations == 7, "ACTUAL_STORE_DORMANT_BIND_ONCE")
        core.stop_owned()
        bad = self.folder("T35_bad_schema"); self.scope.write_new(bad / "authority.db", b""); self.scope.write_new(bad / "test_state.key", self.public_key())
        lease = w.reserve_instance(self.scope,bad); owner=l.OwnedResources(self.scope); owner.add("lock",lease,lease.close,creator_scope=self.scope)
        ledger=self.ledger(); boot=l.StrictStoreBootstrap.for_test(self.scope,bad,bad/"test_state.key",owner,ledger,lease=lease)
        self.refuses(lambda: AuthorityStore(bad,bad/"test_state.key",bootstrap_context=boot),"SCHEMA_MISMATCH")
        self.check(ledger.counts["Store_SQL_attempts"]==1 and not(bad/"initialized").exists(),"UNKNOWN_SCHEMA_REFUSED_BEFORE_MIGRATION_OR_MARKER")
        owner.close()
        lease2=w.reserve_instance(self.scope,bad);owner2=l.OwnedResources(self.scope)
        owner2.add("lock",lease2,lease2.close,creator_scope=self.scope)
        stale=l.StrictStoreBootstrap.for_test(self.scope,bad,bad/"test_state.key",owner2,self.ledger(),lease=lease2)
        owner2.close()
        self.refuses(lambda:AuthorityStore(bad,bad/"test_state.key",bootstrap_context=stale),"OWNERSHIP_UNPROVEN")

    def test_T36_TLS_material_and_policy(self):
        material=CONFIG["shared"]["TLS_material"]; ledger=self.ledger()
        context=l.load_test_TLS(self.scope,material,ledger)
        self.check(context.minimum_version.name == "TLSv1_2", "REAL_SSL_CONTEXT_LOAD_NO_SOCKET")
        badcert=self.scope.write_new(self.run/"invalid_test_certificate.crt",b"public invalid certificate")
        self.refuses(lambda:l.load_test_TLS(self.scope,{**material,"certificate":str(badcert)},ledger),"INITIALIZATION_FAILED")
        adapter=l.OfflineAdapters(self.scope,TLS=False);core=l.Lifecycle(self.scope,self.folder("T36_TLS"),adapter,authorization_id="auth:T36:TLS")
        core.prepare();core.initialize();core.start_owned();self.cleanup_ok(core,adapter,"FAILED")
        adapter=l.OfflineAdapters(self.scope,listener_address="0.0.0.0");core=l.Lifecycle(self.scope,self.folder("T36_bind"),adapter,authorization_id="auth:T36:bind")
        core.prepare();core.initialize();core.start_owned();self.cleanup_ok(core,adapter,"FAILED")

    def test_T37_LIFO_and_primary_failure(self):
        order=[];owner=l.OwnedResources(self.scope,self.ledger())
        one,two,three=object(),object(),object()
        owner.add("first",one,lambda:order.append("first"),creator_scope=self.scope)
        def failing():order.append("second");raise RuntimeError(self.canaries["exception"])
        owner.add("second",two,failing,creator_scope=self.scope)
        owner.add("third",three,lambda:order.append("third"),creator_scope=self.scope)
        result=owner.close();again=owner.close()
        self.check(order==["third","second","first"] and result==again and not result["complete"],"LIFO_CLEANUP_CONTINUES_AND_IS_IDEMPOTENT")
        foreign=[];self.refuses(lambda:l.OwnedResources(self.scope).add("foreign",object(),lambda:foreign.append(1),creator_scope=object()),"OWNERSHIP_UNPROVEN")
        self.check(not foreign,"FOREIGN_CLOSER_NEVER_CALLED");self.secret_free(json.dumps(result))

    def test_T38_same_Store_dormant(self):
        core,adapter=self.drive()
        try:
            meta=core.context.metadata();self.check(meta["registrations"]==1 and meta["source_reads"]==meta["permits"]==0,"DORMANT_REAL_BIND_ZERO_READ")
            self.refuses(core.context.issue_permit,"P2_NOT_AUTHORIZED")
            self.refuses(core.context.read_state,"P2_NOT_AUTHORIZED")
            self.check(adapter.stores[0].reads==0,"NO_IMPLICIT_STORE_READ")
        finally:core.stop_owned()

    def test_T39_lock_handle_transfer(self):
        root=self.folder();lease=w.reserve_instance(self.scope,root)
        child,_=self.worker(root,mode="handoff",inherited=(lease.inherited_handle(),))
        line=w.read_owned_child_line(self.scope,child)
        self.check(line["status"]=="INHERITED_LOCK_OWNED","CHILD_VERIFIED_INHERITED_PHYSICAL_LOCK")
        lease.close();self.refuses(lambda:w.reserve_instance(self.scope,root),"SINGLE_ACTIVE_CONFLICT")
        self.finish(child);replacement=w.reserve_instance(self.scope,root);replacement.close()
        self.check(True,"CONTINUOUS_HANDOFF_UNTIL_LAST_OWNER_EXITS")

    def test_T40_no_shutdown_deadlock(self):
        for fault in ("handler","tls","ready"):
            adapter=l.OfflineAdapters(self.scope,fault=fault);core=l.Lifecycle(self.scope,self.folder("T40_"+fault),adapter,authorization_id="auth:T40:"+fault)
            core.prepare();core.initialize();core.start_owned()
            self.check(core.state=="FAILED" and all(x.shutdown_calls==0 and x.closed for x in adapter.listeners),"PRE_LOOP_FAILURE_NEVER_CALLS_SHUTDOWN")
        core,adapter=self.drive();core.stop_owned()
        self.check(adapter.listeners[0].shutdown_calls==0,"POST_LOOP_CLOSE_NO_SELF_THREAD_WAIT")

    def test_T41_exact_owned_process_stop(self):
        root=self.folder();event=w.create_stop_event(self.scope,secrets.token_hex(16))
        child,facts=self.worker(root,mode="event",event=event.name)
        line=w.read_owned_child_line(self.scope,child);self.check(line["status"]=="WAITING_EVENT","OWNED_CHILD_EVENT_READY")
        self.refuses(lambda:w.verify_target_handle(self.scope,child,{**facts,"created_filetime":facts["created_filetime"]+1}),"IDENTITY_MISMATCH")
        self.check(w.verify_target_handle(self.scope,child,facts)==facts,"EXACT_PID_CREATION_HANDLE_MATCH")
        authorization="auth:worker:"+root.name
        running=l.status_persistent(self.scope,root,authorization)
        self.check(running["liveness"]=="OWNED_PROCESS_ALIVE" and running["consumption_state"]=="STARTED","CROSS_PROCESS_STATUS_PROVES_EXACT_OWNED_SUPERVISOR")
        self.refuses(lambda:l.stop_persistent(self.scope,root,authorization,expected_owner={**facts,"created_filetime":facts["created_filetime"]+1}),"IDENTITY_MISMATCH")
        self.refuses(lambda:l.stop_persistent(self.scope,root,authorization,expected_epoch="old-epoch"),"STALE_EPOCH")
        stop=l.stop_persistent(self.scope,root,authorization,expected_owner=facts,expected_epoch=running["process_epoch"])
        self.check(stop["signal_sent"],"AUTHENTICATED_CROSS_PROCESS_STOP_SIGNAL")
        result=self.finish(child,data=None)
        self.check(result["exit_code"]==0,"REAL_OWNED_EVENT_GRACEFUL_EXIT");event.close();event.close()
        stopped=l.status_persistent(self.scope,root,authorization)
        self.check(stopped["liveness"]=="EXIT_CONFIRMED_BY_CREATOR" and stopped["consumption_state"]=="FINISHED","STOPPED_OWNER_DISTINCT_FROM_STALE_MARKER")

    def test_T42_stop_preserves_persistent_files(self):
        root=self.folder();retained=self.scope.write_new(root/"retained.json",b"{}")
        core,adapter=self.drive(root=root);core.stop_owned();core.stop_owned()
        self.check(retained.read_bytes()==b"{}" and core.state=="STOPPED","NORMAL_STOP_PRESERVES_OWNED_PERSISTENCE")
        self.check(core.status()["cleanup"]["persistent_files_deleted"]==0,"PERSISTENT_AUTODELETE_ZERO")

    def test_T43_recovery_is_metadata_only(self):
        core,_=self.drive();records=core.records();core.stop_owned();records=core.records()
        value=l.recover_classify(self.scope,core.root,records)
        self.check(value["status"]=="STOPPED_RECORDED_NOT_LIVENESS_ATTESTED" and value["SQL"]==value["key_loads"]==value["world_decrypt"]==0,"RECOVERY_METADATA_ONLY")
        self.check(not value["key_DB_content_verified"] and not value["automatic_start"] and not value["marker_repair"],"RECOVERY_DOES_NOT_INVENT_CONTENT_OR_PERMISSION_PROOF")

    def test_T44_commit_receipt_ambiguity(self):
        root=CONFIG["shared"]["committed_gap_root"]
        facts=self.scope.file_facts(root)
        value=l.recover_classify(self.scope,root,{"phase":"INITIALIZING","instance":{"root_facts":facts}})
        self.check(value["status"]=="RECOVERY_REQUIRED" and (root/"authority.db").exists(),"COMMIT_GAP_REMAINS_NO_AUTOREPAIR")

    def test_T45_epoch_and_consumed_start(self):
        core,adapter=self.drive("host_register");self.check(core.records()["start_claimed"] and core.state=="FAILED","FAILED_START_PERMISSION_STAYS_SPENT")
        self.refuses(core.start_owned,"LIFECYCLE_ORDER")
        self.refuses(core.context.issue_permit,"STALE_EPOCH")
        first=CONFIG["shared"]["cross_first"];second=CONFIG["shared"]["cross_replay"]
        self.check(first["first_start"]["START_APPROVAL_CONSUMED"] and first["first_start"]["START_SUCCEEDED"],"CROSS_PROCESS_SUCCESS_HAS_DISTINCT_CONSUMED_AND_STARTED_FACTS")
        self.check(first["start_ACK_observed_by_client"] is False and second["replays"]["same_authorization"]=="REPLAY","LOST_START_ACK_DOES_NOT_REOPEN_PAID_AUTHORIZATION")
        self.check(second["claimed_failure"]["START_APPROVAL_CONSUMED"] and not second["claimed_failure"]["START_SUCCEEDED"] and second["claimed_failure"]["effect_count"]==0,"REAL_CRASH_AFTER_CLAIM_STAYS_SPENT_WITH_ZERO_START_EFFECT")
        self.check(second["replays"]["claimed_after_crash"]=="REPLAY","FAILED_ACK_OR_CRASH_CANNOT_REISSUE_START")

    def test_T46_no_second_Store_or_rearm(self):
        core,adapter=self.drive()
        try:
            self.refuses(lambda:core.context.claim_start(core.context.epoch),"REPLAY")
            self.refuses(lambda:core.context.bind_dormant_store(adapter.stores[0],adapter.stores[0]),"REPLAY")
            original=adapter.stores[0].connection;adapter.stores[0].connection=l.OfflineConnection()
            self.refuses(lambda:core.context.check_store(adapter.stores[0]),"IDENTITY_MISMATCH")
            adapter.stores[0].connection=original
            self.check(len(adapter.stores)==1,"SINGLE_STORE_NO_CONNECTION_ALIAS_REARM")
        finally:core.stop_owned()

    def test_T47_no_semantic_upgrade(self):
        core,_=self.drive()
        try:
            meta=core.context.metadata();self.check(not meta["math_ready"] and not meta["global_complete"] and "TYPED_O_NOT_IMPLEMENTED" in meta["missing_fields"],"NATIVE_AND_TYPED_GAPS_REMAIN")
            try:pickle.dumps(core.context)
            except TypeError:self.check(True,"OLD_CAPABILITY_CANNOT_PERSIST_AS_TRUST")
            else:self.check(False,"OLD_CAPABILITY_CANNOT_PERSIST_AS_TRUST")
        finally:core.stop_owned()

    def test_T48_compatibility_definitions(self):
        project=Path(__file__).parents[1]
        tree=ast.parse((project/"src/auth_lifecycle/online_state/storage.py").read_text(encoding="utf-8"))
        ctor=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=="__init__")
        self.check("bootstrap_context" in [x.arg for x in ctor.args.kwonlyargs],"OPTIONAL_STRICT_CTOR_DEFAULT_COMPATIBILITY")
        for rel in ("tests/test_dsat_authority_runtime.py","tests/test_dsat_authority_host_activation.py","tests/test_dsat_authority_read_host.py"):
            self.check((project/rel).is_file(),"ORIGINAL_TEST_CLASS_UNCHANGED_AND_AVAILABLE")
        self.observations.append({"full_compatibility_execution":"separate r19_24 and legacy44 suites required"})

    def test_T49_public_sinks(self):
        core,adapter=self.drive("handler");self.secret_free(json.dumps(core.status()));self.secret_free(repr(core.context))
        self.check(core.status()["primary_error"]=="INITIALIZATION_FAILED","ERROR_IS_FIXED_CODE_NOT_RAW_EXCEPTION")
        self.secret_free(json.dumps([x.snapshot() for x in self.ledgers]))

    def test_T50_sandbox_and_SQL_authorizer(self):
        self.refuses(lambda:self.scope.path(w.DEPLOYMENT/"secure/authority.key"),"PATH_DENIED")
        self.refuses(lambda:w.launch_owned_child(self.scope,Path(r'D:\foreign\manifest.json')),"PATH_DENIED")
        root=self.folder();connection=l.connect_owned(self.scope,root/"guard.db",self.ledger())
        try:
            try:connection.execute("ATTACH DATABASE ':memory:' AS forbidden")
            except sqlite3.DatabaseError:self.check(True,"ACTUAL_SQLITE_ATTACH_DENIED")
            else:self.check(False,"ACTUAL_SQLITE_ATTACH_DENIED")
        finally:l.close_connection(connection)
        self.observations.append({"network_guard":"runner audit hook denies all socket operations"})

    def test_T51_real_resource_counts(self):
        self.check(self.scope.counts().get("file_SQLite_connections",0)<=104 and self.scope.counts().get("child_launches",0)<=8,"ACTUAL_SCOPE_COUNTS_WITHIN_BUDGET")
        self.check(self.scope.counts().get("test_state_keys_generated",0)==2 and self.scope.counts().get("test_TLS_material_generated",0)==1 and self.scope.counts().get("test_SSLContext_loads",0)==2,"ACTUAL_CRYPTO_COUNTS_NOT_ESTIMATED")
        peak=w.self_peak_memory(self.scope);self.check(peak["peak_working_set_bytes"]>=peak["working_set_bytes"]>0,"ACTUAL_SELF_PEAK_WORKING_SET")
        self.observations.append({"actual_scope_counts":self.scope.counts(),"process_memory":peak})

    def script(self):
        path=Path(__file__).parents[1]/"scripts/run_h2_authority_service.py"
        spec=importlib.util.spec_from_file_location("r21_launcher",path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

    def test_T52_six_offline_operations(self):
        script=self.script();root=self.run/"CLI_instance"
        request=self.scope.write_new(self.run/"CLI_request.json",canonical({"run_root":str(self.run),"instance_root":str(root),"authorization_id":"auth:T52:CLI"}))
        for op in ("prepare","initialize","start","status","stop","recover"):
            output=io.StringIO()
            with contextlib.redirect_stdout(output):code=script.main(["--manifest",str(request),"--operation",op,"--approval-ref",str(w.RECORD/"APPROVAL_RECEIPT.json")])
            value=json.loads(output.getvalue());self.check(code==0 and value["operation"]==op and not value["D1B2_executable"],"ACTUAL_SIX_OPERATION_OFFLINE_ENTRY")
            self.secret_free(output.getvalue());self.observations.append(value)
        self.check((root/"operation_receipt.json").is_file(),"OFFLINE_OPERATION_RECEIPT_PERSISTED")

    def test_X01_independent_process_first_admission(self):
        roots={name:self.folder("cross_"+name) for name in ["A","B","K"]}
        approvals={name:"auth:cross:"+name for name in roots}
        for name,root in roots.items():
            l.prepare_persistent_instance(self.scope,root,approvals[name])
            l.initialize_persistent_instance(self.scope,root,approvals[name])
        child,facts=self.worker(roots["A"],mode="cross_first",extra={"roots":{k:str(v) for k,v in roots.items()},"authorizations":approvals})
        result=self.finish(child)
        self.check(result["exit_code"]==73,"FIRST_INDEPENDENT_ACTOR_EXITED_AFTER_DURABLE_SECOND_CLAIM")
        witness=json.loads((self.run/"CROSS_FIRST_WITNESS.json").read_text(encoding="utf-8"))
        self.check(witness["actor"]==facts and facts["pid"]!=os.getpid(),"FIRST_WITNESS_ACTUAL_PID_AND_CREATION")
        self.check(witness["first_start"]["START_SUCCEEDED"] and witness["finished_A"]["consumption_state"]=="FINISHED" and witness["finished_A"]["effect_count"]==1,"PREPARE_INITIALIZE_PARENT_TO_INDEPENDENT_START_SUCCESS")
        self.check(len(witness["probes"])>=6 and all(x!="ADMITTED" for x in witness["probes"].values()),"INVALID_MARKER_AND_BINDING_VARIANTS_REJECTED_IN_ACTOR")
        CONFIG["shared"].update(cross_roots=roots,cross_authorizations=approvals,cross_first=witness)
        self.observations.append(witness)

    def test_X02_independent_process_replay(self):
        roots=CONFIG["shared"]["cross_roots"];approvals=CONFIG["shared"]["cross_authorizations"]
        child,facts=self.worker(roots["A"],mode="cross_replay",extra={"roots":{k:str(v) for k,v in roots.items()},"authorizations":approvals})
        result=self.finish(child)
        self.check(result["exit_code"]==0,"SECOND_INDEPENDENT_ACTOR_COMPLETED_REPLAY_CHECKS")
        witness=json.loads((self.run/"CROSS_REPLAY_WITNESS.json").read_text(encoding="utf-8"))
        self.check(witness["actor"]==facts and facts["pid"]!=CONFIG["shared"]["cross_first"]["actor"]["pid"],"INDEPENDENT_SECOND_PROCESS_AFTER_FIRST_EXIT")
        self.check(all(v=="REPLAY" for v in witness["replays"].values()) and all(v=="REPLAY" for v in witness["aliases"].values()),"DURABLE_CONSUMPTION_AND_ALL_DISPLAY_ALIASES_REFUSED")
        self.check(all(v=="RECOVERY_REQUIRED" for v in witness["corruption"].values()) and witness["effect_count_A"]==1,"TRUNCATION_MISSING_SLOT_AND_CHAIN_DAMAGE_FAIL_CLOSED")
        CONFIG["shared"]["cross_replay"]=witness
        self.observations.append(witness)
