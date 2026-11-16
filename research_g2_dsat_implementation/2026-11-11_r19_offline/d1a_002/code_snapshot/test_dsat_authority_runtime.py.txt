"""R19 new D01-D24. Public crypto vectors, owned memory SQL, lifecycle stubs."""
import ast
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import pickle
import threading
import time
from types import SimpleNamespace
import unittest

from auth_lifecycle.online_state import dsat_authority_runtime as r
from auth_lifecycle.online_state.protocol import canonical, digest, normalized_request

CONFIG, DETAILS = {}, []


def configure(plan, fixture_root, connect_memory, output):
    CONFIG.update(plan=plan, fixture=fixture_root, connect=connect_memory, output=output)


class ConnectionStub:
    def __init__(self):
        self.closed = 0
        self.in_transaction = False
        self.total_changes = 0

    def close(self):
        self.closed += 1

    def execute(self, *args):
        raise AssertionError("DORMANT_SQL_FORBIDDEN")


class StoreStub:
    def __init__(self, secret):
        self.connection = ConnectionStub()
        self.lock = threading.RLock()
        self.world = {"private": {"handle": secret}, "version": 2}
        self.operations = self.key_calls = self.read_calls = 0

    def read_state(self):
        self.read_calls += 1
        raise AssertionError("DORMANT_READ_FORBIDDEN")

    def cipher(self):
        self.key_calls += 1
        raise AssertionError("DORMANT_KEY_FORBIDDEN")


class ServerStub:
    def __init__(self, fail_close=False, secret=""):
        self.server_address = ("127.0.0.1", 27443)
        self.TLS_REQUIRED = True
        self.shutdown_calls = self.close_calls = 0
        self.fail_close, self.secret = fail_close, secret

    def shutdown(self):
        self.shutdown_calls += 1
        if self.fail_close:
            raise RuntimeError(self.secret)

    def server_close(self):
        self.close_calls += 1


class Adapters:
    def __init__(self, secret, conflict=False, fail_close=False):
        self.secret, self.conflict = secret, conflict
        self.constructs = self.bind_attempts = 0
        self.store = StoreStub(secret)
        self.server = ServerStub(fail_close, secret)

    def path_facts(self, config):
        return {"root": config.deployment_root, "root_exists": False, "ancestor_reparse": False,
                "source_isolation": True, "producer": "OFFLINE_PATH_PROVIDER"}

    def dependency_facts(self):
        return {"python": "3.12.14", "architecture": "AMD64", "crypto": "50.0.2", "sqlite": "3.53.1", "imported": False}

    def schema_facts(self):
        return {"user_version": 2, "state_present": True, "producer": "OFFLINE_SCHEMA_PROVIDER"}

    def construct_store(self, config):
        self.constructs += 1
        return self.store

    def prepare_listener(self, address, port, *, TLS_REQUIRED):
        self.bind_attempts += 1
        if self.conflict:
            raise RuntimeError(self.secret)
        if (address, port, TLS_REQUIRED) != ("127.0.0.1", 27443, True):
            raise AssertionError("NETWORK_POLICY_MISMATCH")
        return self.server


class Provider:
    def __init__(self, record, secret=None):
        self.record, self.secret, self.targets = record, secret, []

    def read_one(self, pid):
        self.targets.append(pid)
        if self.secret:
            raise RuntimeError(self.secret)
        return copy.deepcopy(self.record)


class D1ACases(unittest.TestCase):
    def setUp(self):
        self.case_id = self._testMethodName.split("_")[1]
        self.spec = next(x for x in CONFIG["plan"]["new_cases"] if x["id"] == self.case_id)
        f = CONFIG["fixture"]
        self.doc = json.loads((f / "CONFIRMED_CONFIG.json").read_text(encoding="utf-8-sig"))
        self.vector = json.loads((f / "PUBLIC_VECTORS.json").read_text(encoding="utf-8-sig"))
        self.canaries = json.loads((f / "CANARIES.json").read_text(encoding="utf-8-sig"))["values"]
        self.checks, self.observations = [], []
        self.started = time.perf_counter_ns()

    def tearDown(self):
        DETAILS.append({"id": self.case_id, "original_spec": self.spec, "checks": self.checks,
                        "observations": self.observations, "elapsed_ns": time.perf_counter_ns() - self.started})

    def check(self, condition, label):
        self.checks.append({"label": label, "satisfied": bool(condition)})
        if not condition:
            raise AssertionError(label)

    def refused(self, function, code=None):
        try:
            function()
        except r.RuntimeRefusal as error:
            self.check(code is None or error.code == code, "EXPECTED_FIXED_REFUSAL")
            self.secret_free(str(error) + repr(error))
            self.observations.append({"business_status": error.code})
            return
        self.check(False, "EXPECTED_REFUSAL_NOT_SUCCESS")

    def secret_free(self, text):
        self.check(all(v not in text for v in self.canaries.values()), "ALL_SECRET_CANARIES_ABSENT")

    def config(self, doc=None):
        return r.RuntimeConfig.from_confirmed(self.doc if doc is None else doc)

    def context(self, config=None):
        return r.RuntimeContext.from_offline_host(config or self.config(), process=self.vector["process"], source_digest="1" * 64)

    def bound_metadata(self):
        context = self.context()
        adapters = Adapters(self.canaries["handle"])
        context.bind_store(adapters.store)
        context.on_listener_ready(adapters.server, adapters.store)
        return context, adapters, context.metadata()

    def request(self, value):
        p = value["process"]
        return {"environment_id": value["environment_id"], "pid": p["pid"], "created_at": p["created_at"],
                "epoch": p["epoch"], "source_digest": value["source_digest"], "config_digest": value["config_digest"]}

    def script(self, name):
        path = Path(__file__).parents[1] / "scripts" / name
        spec = importlib.util.spec_from_file_location("d1a_" + name.replace(".", "_"), path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_D01_confirmed_config(self):
        c = self.config()
        self.check(c.deployment_root == r.ROOT and c.python_executable == r.PYTHON, "CONFIRMED_ROOT_AND_PYTHON")
        self.check(c.plan()["P2_authorized"] is False and not c.plan()["INSTANCE_RUNNING"], "PARAMETERS_NOT_LIVE_DEPLOYMENT")
        self.observations.append(c.plan())

    def test_D02_closed_types(self):
        for key in ("deployment_root", "port_policy", "parameter_confirmation"):
            doc = copy.deepcopy(self.doc); del doc[key]
            self.refused(lambda: self.config(doc))
        doc = copy.deepcopy(self.doc); doc["trusted"] = True
        self.refused(lambda: self.config(doc))
        doc = copy.deepcopy(self.doc); doc["synthetic_data_scope"]["approved_value"]["password"] = self.canaries["password"]
        self.refused(lambda: self.config(doc))
        doc = copy.deepcopy(self.doc); doc["synthetic_data_scope"]["approved_value"]["counts"]["grants"] = True
        self.refused(lambda: self.config(doc))
        doc = copy.deepcopy(self.doc); doc["p2_authorization"]["approved"] = 0
        self.refused(lambda: self.config(doc))

    def test_D03_path_boundary(self):
        for value in (r"relative\root", r"D:\毕业设计\auth-lifecycle\.runtime\real", r.ROOT + r"\..", r.ROOT + ":ads", r"\\server\share\root"):
            doc = copy.deepcopy(self.doc); doc["deployment_root"]["approved_value"] = value
            self.refused(lambda: self.config(doc), "PATH_DENIED")

    def test_D04_source_and_derived(self):
        doc = copy.deepcopy(self.doc); doc["all_candidate_paths"]["state_key_path"] = r"D:\foreign\real.key"
        self.refused(lambda: self.config(doc), "PATH_DENIED")
        doc = copy.deepcopy(self.doc); doc["source_digest"]["current_static_basis_sha256"] = "2" * 64
        self.refused(lambda: self.config(doc), "SOURCE_MISMATCH")
        doc = copy.deepcopy(self.doc); doc["python_executable"]["approved_value"] = r"D:\foreign\python.exe"
        self.refused(lambda: self.config(doc), "PATH_DENIED")

    def test_D05_reparse_and_existing(self):
        adapters = Adapters("")
        for key, value in (("root_exists", True), ("ancestor_reparse", True), ("source_isolation", False)):
            facts = adapters.path_facts(self.config()); facts[key] = value
            self.refused(lambda: r.validate_path_facts(self.config(), facts), "PATH_DENIED")
        self.refused(lambda: r.read_offline_json(r.ROOT + r"\secure\authority.json"), "PATH_DENIED")

    def test_D06_dependency_import(self):
        facts = r.probe_offline_dependencies()
        self.check(facts["status"] == "PACKAGE_IMPORTABLE" and facts["crypto"] == "50.0.2", "APPROVED_BASE_PACKAGES_ACTUALLY_IMPORT")
        self.check(facts["Authority_runtime_compatible"] is False, "IMPORT_NOT_AUTHORITY_RUNNING")
        self.observations.append({"dependency_import_facts": facts})
        for key, value in (("crypto", "missing"), ("architecture", "OTHER"), ("sqlite", "3.15.0")):
            bad = Adapters("").dependency_facts(); bad[key] = value
            self.refused(lambda: r.check_dependency_facts(bad), "DEPENDENCY_RUNTIME_GAP")

    def seed(self):
        return r.build_synthetic_seed(self.config(), grant_id=self.vector["grant_id"],
                handle=self.canaries["handle"], material=self.canaries["material"])

    def test_D07_seed_contract(self):
        seed = self.seed(); state = seed["state"]
        self.check(seed["version"] == 2 and len(state["grants"]) == len(state["requests"]) == 1, "ONE_GRANT_ONE_REQUEST_COHERENT_VERSION")
        grant = next(iter(state["grants"].values())); req = next(iter(state["requests"].values()))
        self.check(grant["limit"] == grant["reserved"] == 1 and grant["spent"] == 0 and req["phase"] == "QUEUED", "QUEUED_BUDGET_CORRECT")
        self.check(req["digest"] == digest({"caller": r.SCOPE["caller"], "request": normalized_request(req["request"])}), "ORIGINAL_DIGEST_EXACT")
        self.check(req["origin"]["grant_id"] == grant["grant_id"] and req["request"]["handle"] == grant["handle"], "HANDLE_AND_ORIGIN_BOUND")
        self.check(req["attempt_id"] is None and req["release_version"] is None and not state["disposals"] and not state["reconciliation_windows"], "NO_DISPATCH_OR_NATIVE_HISTORY")
        self.observations.append({"state_hash": digest(state), "history_versions": [x["version"] for x in seed["history"]]})

    def test_D08_AES_memory(self):
        seed = self.seed(); key = bytes.fromhex(self.vector["public_AES_key_hex"]); nonce = bytes.fromhex(self.vector["public_nonce_hex"])
        blob = r.encrypt_public_test_seed(seed, key, nonce)
        conn = CONFIG["connect"]()
        prepared = r.prepare_public_memory_database(conn, seed, blob)
        self.check(prepared["schema_version"] == conn.execute("PRAGMA user_version").fetchone()[0] == 2, "ACTUAL_SCHEMA2_PREPARATION")
        self.check(conn.execute("SELECT count(*) FROM authority_events").fetchone()[0] == 2, "COHERENT_SYNTHETIC_HISTORY_ROWS")
        row = conn.execute("SELECT version,ciphertext FROM authority_state WHERE id=1").fetchone()
        self.check(row[0] == 2 and r.public_test_seed_roundtrip(bytes(row[1]), key) == seed["state"], "REAL_AES_PUBLIC_VECTOR_MEMORY_SQLITE_ROUNDTRIP")
        self.observations.append({"public_test_ciphertext_bytes": len(blob), "persistent_key_files": 0, "production_AES_cost": "NOT_MEASURED"})

    def test_D09_crypto_refusal(self):
        seed = self.seed()
        self.refused(lambda: r.encrypt_public_test_seed(seed, b"bad", b"bad"))
        key = bytes.fromhex(self.vector["public_AES_key_hex"]); nonce = bytes.fromhex(self.vector["public_nonce_hex"])
        blob = r.encrypt_public_test_seed(seed, key, nonce)
        self.refused(lambda: r.public_test_seed_roundtrip(blob[:-1] + bytes([blob[-1] ^ 1]), key))

    def test_D10_default_offline(self):
        launch = self.script("run_h2_authority_service.py")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = launch.main(["--manifest", str(CONFIG["fixture"] / "CONFIRMED_CONFIG.json")])
        value = json.loads(output.getvalue())
        self.check(code == 0 and value["status"] == "DEPLOYMENT_PREPARED_OFFLINE" and value["dormant"], "DEFAULT_CLI_ONLY_OFFLINE_PLAN")
        self.secret_free(output.getvalue())

    def test_D11_bootstrap_order(self):
        config = self.config(); context = self.context(config); adapters = Adapters(self.canaries["handle"])
        before = digest(adapters.store.world)
        value = r.simulate_bootstrap(config, context, adapters)
        self.check(context.counters()["events"] == ["config_preflight", "dependency_preflight", "schema_preflight", "store_constructed", "dormant_bind", "listener_simulated"], "EXACT_BOOTSTRAP_ORDER")
        self.check(adapters.constructs == adapters.bind_attempts == 1, "ONE_STORE_AND_ONE_SIMULATED_BIND")
        self.check(before == digest(adapters.store.world) and adapters.store.operations == adapters.store.key_calls == adapters.store.read_calls == 0, "DORMANT_WORLD_AND_IO_UNCHANGED")
        self.check(adapters.store.connection.closed == adapters.server.close_calls == adapters.server.shutdown_calls == 1, "OWNED_RESOURCES_CLOSED")
        self.secret_free(json.dumps(value)); self.observations.append(value)

    def test_D12_dormant_zero_read(self):
        context, adapters, meta = self.bound_metadata()
        self.refused(context.issue_permit, "P2_NOT_AUTHORIZED"); self.refused(context.read_state, "P2_NOT_AUTHORIZED")
        self.check(meta["P2_read_enabled"] is False and meta["permits_issued"] == meta["session_reads"] == 0, "NO_DORMANT_PERMIT_OR_READ")
        context.close_owned()

    def test_D13_source_binding(self):
        self.refused(lambda: r.validate_runtime_context({"trusted": True}, "authority", r.ROOT), "CONTEXT_REQUIRED")
        forged = object.__new__(r.RuntimeContext)
        self.refused(forged.metadata, "CONTEXT_REQUIRED")
        context, adapters, _ = self.bound_metadata()
        self.refused(lambda: context.bind_store(adapters.store), "CONTEXT_ALREADY_BOUND")
        adapters.store.lock = threading.RLock()
        self.refused(context.metadata, "SOURCE_MISMATCH")
        context.close_owned()

    def test_D14_epoch_config(self):
        process = dict(self.vector["process"]); process["source_kind"] = "REAL"
        self.refused(lambda: r.RuntimeContext.from_offline_host(self.config(), process=process, source_digest="1" * 64))
        context = self.context()
        self.refused(lambda: r.simulate_bootstrap(SimpleNamespace(), context, Adapters("")), "CONTEXT_REQUIRED")

    def test_D15_closed_context(self):
        context, _, _ = self.bound_metadata(); context.close_owned()
        self.refused(context.metadata, "CONTEXT_CLOSED"); self.refused(context.issue_permit, "CONTEXT_CLOSED")
        context.close_owned(); self.check(context.counters()["closed"], "CLOSE_IDEMPOTENT_NO_REARM")

    def test_D16_metadata_closed(self):
        context, _, meta = self.bound_metadata()
        value = r.validate_metadata(meta); value["process"]["epoch"] = "client:changed"
        self.check(context.metadata()["process"]["epoch"] != "client:changed", "METADATA_DETACHED")
        for target in ("root", "process"):
            bad = copy.deepcopy(meta)
            (bad if target == "root" else bad["process"])["token"] = self.canaries["token"]
            self.refused(lambda: r.validate_metadata(bad), "METADATA_INVALID")
        self.secret_free(repr(context))
        try: pickle.dumps(context)
        except TypeError as error: self.secret_free(str(error))
        else: self.check(False, "CONTEXT_SERIALIZATION_DENIED")
        context.close_owned()

    def test_D17_one_target(self):
        context, _, meta = self.bound_metadata(); provider = Provider(meta)
        value = r.inspect_offline_metadata(self.request(meta), provider)
        self.check(provider.targets == [self.vector["process"]["pid"]] and value == meta, "ONLY_ONE_SPECIFIED_TARGET")
        request = self.request(meta); request["epoch"] = "old:epoch"
        self.refused(lambda: r.inspect_offline_metadata(request, provider), "TARGET_MISMATCH")
        context.close_owned()

    def test_D18_P1_boundaries(self):
        context, _, meta = self.bound_metadata(); request = self.request(meta); request["all_processes"] = True
        self.refused(lambda: r.inspect_offline_metadata(request, Provider(meta)), "TARGET_MISMATCH")
        self.refused(lambda: r.inspect_offline_metadata(self.request(meta), Provider(meta, self.canaries["exception"])), "METADATA_INVALID")
        spec = r.p1b_static_contract()
        self.check(spec["statements"] == ["PRAGMA user_version", "PRAGMA journal_mode"] and not spec["authorized"] and spec["world_SELECT"] == spec["key"] == spec["decrypt"] == 0, "P1B_STATIC_ONLY_SEPARATE_PERMISSION")
        context.close_owned()

    def test_D19_network_policy(self):
        for key, val in (("address", "0.0.0.0"), ("port", 0), ("policy", "AUTO_FALLBACK")):
            doc = copy.deepcopy(self.doc); doc["port_policy"]["approved_value"][key] = val
            self.refused(lambda: self.config(doc))
        context, adapters, _ = self.bound_metadata(); adapters.server.TLS_REQUIRED = False
        self.refused(lambda: context.on_listener_ready(adapters.server, adapters.store), "PORT_CONFLICT")
        context.close_owned()

    def test_D20_conflict_stop(self):
        adapters = Adapters(self.canaries["exception"], conflict=True); context = self.context()
        self.refused(lambda: r.simulate_bootstrap(self.config(), context, adapters), "PORT_CONFLICT")
        self.check(adapters.bind_attempts == 1 and adapters.constructs == 1 and adapters.store.connection.closed == 1, "NO_PORT_RETRY_AND_OWNED_CLOSE")
        adapters = Adapters(""); adapters.server.server_address = ("0.0.0.0", 27443); context = self.context()
        self.refused(lambda: r.simulate_bootstrap(self.config(), context, adapters), "PORT_CONFLICT")
        self.check(adapters.server.close_calls == adapters.store.connection.closed == 1, "POLICY_REJECTED_OWNED_LISTENER_CLEANED")

    def test_D21_cleanup_fault(self):
        adapters = Adapters(self.canaries["exception"], fail_close=True); context = self.context()
        self.refused(lambda: r.simulate_bootstrap(self.config(), context, adapters), "OFFLINE_ADAPTER_FAILED")
        self.check(adapters.store.connection.closed == adapters.server.close_calls == 1 and context.counters()["closed"], "CLEANUP_CONTINUES_AFTER_SHUTDOWN_FAILURE")

    def test_D22_phase_gates(self):
        context = self.context()
        self.refused(lambda: r.validate_runtime_context(context, "authority", r.ROOT), "D1B_NOT_AUTHORIZED")
        doc = copy.deepcopy(self.doc); doc["deployment_authorization"]["D1_B"] = True
        self.refused(lambda: self.config(doc))
        self.check(self.config().plan()["approved_reads"] == 0, "PARAMETER_CONFIRMATION_GIVES_NO_EXECUTION")

    def test_D23_services_AST(self):
        path = Path(__file__).parents[1] / "src/auth_lifecycle/online_state/services.py"
        tree = ast.parse(path.read_text(encoding="utf-8")); serve = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "serve")
        text = ast.unparse(serve)
        self.check("authority_runtime_context" in [n.arg for n in serve.args.kwonlyargs], "OPTIONAL_RUNTIME_CONTEXT_KEYWORD")
        self.check(text.index("validate_runtime_context") < text.index("read_text"), "LIVE_GATE_BEFORE_CONFIG_IO")
        self.check(text.index("AuthorityStore(") < text.index("bind_store") < text.index("class Handler"), "POST_STORE_PRE_HANDLER_DORMANT_HOOK")
        self.check("authority_runtime_context.close_owned()" in text and "finally:" in text, "OWNED_CLEANUP_HOOK_PRESENT")
        import sys
        self.check(not any(n in sys.modules for n in ("auth_lifecycle.online_state.services", "auth_lifecycle.online_state.storage", "auth_lifecycle.online_state.materials")), "NO_REAL_SERVICE_MODULE_IMPORTED")

    def test_D24_CLI_sinks(self):
        launch = self.script("run_h2_authority_service.py")
        inspect = self.script("inspect_h2_authority_metadata.py")
        for module in (launch, inspect):
            output = io.StringIO()
            with contextlib.redirect_stdout(output): code = module.main(["--mode", "deploy", "--key", self.canaries["private_key"]])
            self.check(code == 2, "REAL_OR_UNKNOWN_ARGV_REFUSED"); self.secret_free(output.getvalue())
        context, _, meta = self.bound_metadata()
        md = CONFIG["output"] / "test_metadata.json"; req = CONFIG["output"] / "test_request.json"
        md.write_bytes(canonical(meta)); req.write_bytes(canonical(self.request(meta)))
        output = io.StringIO()
        with contextlib.redirect_stdout(output): code = inspect.main(["--metadata", str(md), "--request", str(req)])
        self.check(code == 0 and json.loads(output.getvalue()) == meta, "P1A_OFFLINE_CLI_VALID_RECORD")
        self.secret_free(output.getvalue()); context.close_owned()
