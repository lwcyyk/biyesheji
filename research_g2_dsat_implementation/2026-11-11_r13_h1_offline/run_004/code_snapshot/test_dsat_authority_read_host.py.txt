"""R13 frozen H01-H24. All services, storage, keys, and transport are doubles."""
import ast
from concurrent.futures import ThreadPoolExecutor
import contextlib
import copy
import hashlib
import hmac
import io
import json
import logging
from pathlib import Path
import pickle
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from auth_lifecycle.online_state import dsat_authority_read_host as hostmod
from auth_lifecycle.online_state.dsat_authority_read import BASE_GAPS
from auth_lifecycle.online_state.protocol import canonical, digest


CONFIG, DETAILS = {}, []
ORIGINAL_READ = hostmod.read_dsat_authority_snapshot


def configure(plan, fixture_root):
    CONFIG.update(plan=plan, fixture_root=fixture_root)


class TracedRLock:
    def __init__(self, name, trace):
        self.real = threading.RLock()
        self.name, self.trace = name, trace
        self.depth, self.maximum = 0, 0

    def __enter__(self):
        self.real.acquire()
        self.depth += 1
        self.maximum = max(self.maximum, self.depth)
        self.trace.append(self.name + "+")
        return self

    def __exit__(self, *args):
        self.trace.append(self.name + "-")
        self.depth -= 1
        self.real.release()


class FakeConnection:
    def __init__(self):
        self.in_transaction = False
        self.total_changes = 0
        self.forbidden = 0

    def execute(self, *args):
        self.forbidden += 1
        raise AssertionError("REAL_SQL_PATH_FORBIDDEN")

    commit = rollback = execute


class FakeCodec:
    """Opaque catalog stand-in, with no cryptographic security claim."""
    def __init__(self, state, key, exception):
        self.key, self.exception = key, exception
        self._plain = canonical(state)
        self.sealed = b"H1-SYNTHETIC-SEALED-CATALOG-ENTRY"

    def decode(self, blob, key, fail=False):
        if blob != self.sealed or key != self.key or fail:
            raise RuntimeError(self.exception)
        return json.loads(self._plain)

    def world_bytes(self):
        return self._plain

    def __repr__(self):
        return "<SyntheticCodec redacted>"


class SyntheticReader:
    """Mirrors storage.execute -> telemetry -> SELECT -> key -> decode ordering."""
    def __init__(self, state, version, canaries, trace):
        self.codec = FakeCodec(state, canaries["codec_key"], canaries["exception"])
        self.version, self.trace = version, trace
        self.lock = TracedRLock("reader", trace)
        self.connection = FakeConnection()
        self.operations, self.operation_limit = 0, None
        self.reads, self.telemetry_attempts, self.selects = 0, 0, 0
        self.key_reads, self.decode_attempts, self.forbidden = 0, 0, 0
        self.metrics, self.read_threads = [], []
        self.failure, self.entered, self.release_gate = None, None, None

    def read_state(self):
        if self.lock.depth != 2:
            raise AssertionError("OUTER_HOST_AND_INNER_R12_LOCK_REQUIRED")
        self.read_threads.append(threading.get_ident())
        self.reads += 1
        self.trace.append("read_state")
        if self.operation_limit is not None and self.operations >= self.operation_limit:
            raise RuntimeError("DATABASE_OPERATION_BUDGET")
        self.operations += 1
        self.trace.append("operation_increment")
        self.telemetry_attempts += 1
        self.trace.append("source_telemetry_attempt")
        if self.failure == "telemetry":
            raise RuntimeError(self.codec.exception)
        self.metrics.append({"event": "sqlite_statement", "number": self.operations,
                             "kind": "SELECT", "bound_value_bytes": 0})
        self.trace.append("source_telemetry_committed")
        self.selects += 1
        self.trace.append("synthetic_select")
        if self.entered is not None:
            self.entered.set()
            if not self.release_gate.wait(3):
                raise RuntimeError("SYNTHETIC_GATE_TIMEOUT")
        self.key_reads += 1
        self.trace.append("synthetic_key_read")
        if self.failure == "key":
            raise RuntimeError(self.codec.exception)
        self.decode_attempts += 1
        self.trace.append("synthetic_decode")
        return self.version, self.codec.decode(self.codec.sealed, self.codec.key, self.failure == "decode")

    def counters(self):
        return {"read_attempts": self.reads, "operations": self.operations,
                "telemetry_attempts": self.telemetry_attempts, "telemetry_rows": len(self.metrics),
                "simulated_selects": self.selects, "simulated_key_reads": self.key_reads,
                "simulated_decode_attempts": self.decode_attempts}

    def world_hash(self):
        return hashlib.sha256(canonical({"version": self.version,
                                        "world_bytes": self.codec.world_bytes().decode()})).hexdigest()

    def call(self, *args):
        self.forbidden += 1
        raise AssertionError("OLD_DISPATCH_FORBIDDEN")

    execute = call

    def __repr__(self):
        return "<SyntheticAuthorityReader redacted>"


class HostAudit:
    def __init__(self, secret):
        self.rows, self.attempts, self.failure, self.secret = [], 0, False, secret

    def __call__(self, row):
        self.attempts += 1
        if self.failure:
            raise RuntimeError(self.secret)
        self.rows.append(copy.deepcopy(row))


class OfflineAuthorityRPC:
    """Trusted synthetic transport verifier; it returns serialized summary only."""
    def __init__(self, host, identity, token):
        self.host, self.identity, self.token = host, identity, token
        self.responses = []

    def call(self, operation, body, token):
        if type(token) is not str or not hmac.compare_digest(token, self.token):
            summary = self.host.refusal("HOST_IDENTITY_REQUIRED")
        elif operation != hostmod.RIGHT or type(body) is not dict or set(body) != {"scope"}:
            summary = self.host.refusal("UNSUPPORTED_READ_REQUEST")
        else:
            try:
                permit = self.host.issue_permit(self.identity, body["scope"])
                summary = self.host.read_summary(self.host.request_for(permit), self.identity, permit)
            except hostmod.HostReadError as error:
                summary = self.host.refusal(error.code)
        wire = summary.to_json()
        self.responses.append(wire)
        return wire


class OfflineController:
    def __init__(self, rpc, token):
        self._rpc, self._token = rpc, token
        self.received = []

    def request(self, body, operation=hostmod.RIGHT, token=None):
        wire = self._rpc.call(operation, body, self._token if token is None else token)
        self.received.append(wire)
        return wire


class H1Cases(unittest.TestCase):
    def setUp(self):
        self.case_id = self._testMethodName.split("_")[1]
        self.spec = next(x for x in CONFIG["plan"]["H1"]["cases"] if x["id"] == self.case_id)
        root = CONFIG["fixture_root"]
        self.seed = json.loads((root / "STATE_SEED.json").read_text(encoding="utf-8-sig"))
        self.canaries = json.loads((root / "CANARIES.json").read_text(encoding="utf-8-sig"))["values"]
        self.meta = json.loads((root / "HOST_METADATA.json").read_text(encoding="utf-8-sig"))
        self.schema = json.loads((root / "R13_SUMMARY_SCHEMA.json").read_text(encoding="utf-8"))
        self.checks, self.calls, self.batches, self.stages = [], [], [], []
        self.started = time.perf_counter_ns()
        self.env = self.environment()

    def tearDown(self):
        DETAILS.append({"id": self.case_id, "name": self.spec["name"], "checks": self.checks,
                        "calls": self.calls, "batches": self.batches,
                        "elapsed_ns": time.perf_counter_ns() - self.started})

    def check(self, condition, label):
        self.checks.append({"label": label, "satisfied": bool(condition)})
        if not condition:
            raise AssertionError(label)

    def resign(self, state):
        for raw in state["requests"].values():
            raw["digest"] = digest({"caller": raw["origin"]["caller"], "request": raw["request"]})

    def environment(self, state=None, limits=None, **host_overrides):
        state = copy.deepcopy(self.seed["state"] if state is None else state)
        self.resign(state)
        trace, clock = [], SimpleNamespace(now=self.meta["clock_start"])
        policy = hostmod.HostReadPolicy(self.meta["epoch"], lambda: clock.now)
        policy.lock = TracedRLock("policy", trace)
        reader = SyntheticReader(state, self.seed["version"], self.canaries, trace)
        identity = policy.bind_authenticated_caller(principal_ref=self.meta["principal"], actor=self.meta["actor"],
                    transport_ref=self.meta["transport"], expires_ns=self.meta["expiry"])
        policy.allow(principal_ref=self.meta["principal"], actor=self.meta["actor"], transport_ref=self.meta["transport"],
                     scope=self.seed["scope_A"], grant_ref="gA", scope_ref=self.meta["scope_ref"], expires_ns=self.meta["expiry"])
        audit = HostAudit(self.canaries["exception"])
        args = dict(producer_ref=self.meta["producer"], locator_ref=self.meta["locator"], epoch_ref=self.meta["epoch"],
                    limits=limits or hostmod.HostReadLimits(), audit_sink=audit)
        args.update(host_overrides)
        host = hostmod.AuthorityReadHost(reader, policy, **args)
        rpc = OfflineAuthorityRPC(host, identity, self.canaries["rpc_token"])
        controller = OfflineController(rpc, self.canaries["rpc_token"])
        return SimpleNamespace(state=state, reader=reader, policy=policy, identity=identity,
                               host=host, rpc=rpc, controller=controller, audit=audit, clock=clock, trace=trace)

    def secrets_absent(self, rendered):
        self.check(all(value not in rendered for value in self.canaries.values()), "ALL_SENSITIVE_CANARIES_ABSENT")

    def verify_public(self, public, rendered):
        self.check(set(public) == set(self.schema["required"]), "R13_ROOT_WHITELIST_EXACT")
        self.check(set(public["audit"]) == set(self.schema["properties"]["audit"]["required"]), "R13_AUDIT_WHITELIST_EXACT")
        self.check(len(canonical(public)) <= 4096, "PUBLIC_OUTPUT_AT_MOST_4096")
        self.check(public["authority_instance"] is None and public["obligation_revision"] is None, "INSTANCE_AND_O_REMAIN_UNKNOWN")
        self.check(all(public[k] is False for k in ("math_ready", "current_native_eligible", "global_complete")), "NO_MATH_NATIVE_OR_COMPLETE_QUALIFICATION")
        self.check(public["authority_write_action"] == "NONE" and public["native_currentness_status"] == "UNPROVEN", "READ_ONLY_STAGING_QUALIFICATION")
        self.check(set(BASE_GAPS) <= set(public["missing_fields"]), "ALL_BASE_GAPS_PRESERVED")
        self.check(public["audit"]["source_sql_count"] == 0 and public["audit"]["key_read_count"] is None,
                   "REAL_SQL_ZERO_AND_REAL_KEY_MEASUREMENT_UNKNOWN")
        self.secrets_absent(rendered)
        self.check(all(marker not in rendered for marker in ("gB", "rB", "taskB", "agentB", "genB")), "FOREIGN_ROW_METADATA_ABSENT")

    def exercise(self, env=None, *, body=None, operation=hostmod.RIGHT, token=None, direct=None, stage_hook=None):
        env = env or self.env
        before, counters = env.reader.world_hash(), env.reader.counters()
        trace_start, stages = len(env.trace), []
        stdout, stderr, logs = io.StringIO(), io.StringIO(), io.StringIO()
        handler = logging.StreamHandler(logs)
        logger = logging.getLogger()
        logger.addHandler(handler)
        def observe(*args, **kwargs):
            output = ORIGINAL_READ(*args, **kwargs)
            stages.append(output.to_dict())
            if stage_hook is not None:
                stage_hook(output)
            return output
        start = time.perf_counter_ns()
        try:
            with patch.object(hostmod, "read_dsat_authority_snapshot", observe), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                if direct:
                    summary = direct()
                    wire = summary.to_json()
                else:
                    wire = env.controller.request(body if body is not None else {"scope": self.seed["scope_A"]}, operation, token)
                    summary = hostmod.HostReadSummary(json.loads(wire))
        finally:
            logger.removeHandler(handler)
        elapsed = time.perf_counter_ns() - start
        public = json.loads(wire)
        after = env.reader.world_hash()
        delta = {k: env.reader.counters()[k] - value for k, value in counters.items()}
        self.check(before == after, "WORLD_VERSION_EVENTS_BUDGET_PHASE_AND_STATE_UNCHANGED")
        self.check(env.reader.connection.forbidden == 0 and env.reader.forbidden == 0, "NO_DANGEROUS_SOURCE_ENTRY")
        self.check(delta["read_attempts"] <= 1 and delta["operations"] <= 1, "ONE_SOURCE_ATTEMPT_NO_AUTOMATIC_RETRY")
        self.check(public["audit"]["source_operations_delta"] == delta["operations"], "OPERATION_DELTA_EXACT_SEPARATE_FROM_WORLD")
        self.check(public["audit"]["source_read_count"] == delta["read_attempts"], "SOURCE_READ_ATTEMPTS_ACCOUNTED_ON_ALL_RETURNS")
        rendered = wire.decode() + repr(summary) + stdout.getvalue() + stderr.getvalue() + logs.getvalue() + json.dumps(env.audit.rows)
        self.verify_public(public, rendered)
        self.check(stdout.getvalue() == stderr.getvalue() == logs.getvalue() == "", "NO_RAW_OUTPUT_OR_LOGGING")
        self.stages.extend(stages)
        self.calls.append({"status": public["status"], "business_category": hostmod.outcome_category(public["status"]),
                           "summary": public, "world_before": before, "world_after": after,
                           "simulation_effect_delta": delta, "source_trace": env.trace[trace_start:],
                           "source_telemetry": copy.deepcopy(env.reader.metrics), "host_audit": copy.deepcopy(env.audit.rows),
                           "source_stage_count": len(stages), "total_ns": elapsed,
                           "sink_scan": "CLEAN", "world_unchanged": before == after})
        return public

    def permit(self, env=None):
        env = env or self.env
        p = env.host.issue_permit(env.identity, self.seed["scope_A"])
        return p, env.host.request_for(p)

    def rejected_without_read(self, public, expected):
        self.check(public["status"] == expected and self.calls[-1]["simulation_effect_delta"]["read_attempts"] == 0,
                   "EXPECTED_DENIAL_BEFORE_SOURCE_READ")

    def test_H01_registration(self):
        p = self.exercise()
        self.check(p["status"] == "STAGING_READY_WITH_GAPS" and p["source_binding_status"] == "MATCHED", "REGISTERED_HOST_WORKS_END_TO_END")
        source = self.stages[-1]["source"]
        self.check(source["producer_ref"] == self.meta["producer"] and source["authority_locator_ref"] == self.meta["locator"]
                   and source["principal_ref"] == self.meta["principal"], "TRUSTED_HOST_PROVENANCE_BOUND")

    def test_H02_identity(self):
        self.rejected_without_read(self.exercise(token="invalid"), "HOST_IDENTITY_REQUIRED")
        permit, request = self.permit()
        fake = object.__new__(hostmod.VerifiedLocalCaller)
        self.rejected_without_read(self.exercise(direct=lambda: self.env.host.read_summary(request, fake, permit)), "HOST_IDENTITY_REQUIRED")

    def test_H03_body_flags(self):
        for key in ("trusted", "is_admin", "source_confirmed", "actor", "origin"):
            body = {"scope": self.seed["scope_A"], key: True}
            self.rejected_without_read(self.exercise(body=body), "UNSUPPORTED_READ_REQUEST")

    def test_H04_expiry_withdrawal(self):
        permit, request = self.permit()
        self.env.clock.now = self.meta["expiry"]
        self.rejected_without_read(self.exercise(direct=lambda: self.env.host.read_summary(request, self.env.identity, permit)), "HOST_PERMIT_EXPIRED")
        env = self.environment()
        permit, request = self.permit(env)
        env.policy.revoke(self.meta["principal"], self.seed["scope_A"])
        self.rejected_without_read(self.exercise(env, direct=lambda: env.host.read_summary(request, env.identity, permit)), "HOST_PERMISSION_DENIED")
        env = self.environment()
        env.policy.revoke_identity(env.identity)
        self.rejected_without_read(self.exercise(env), "HOST_IDENTITY_REQUIRED")

    def test_H05_exact_tuple(self):
        self.exercise()
        stage = self.stages[-1]
        self.check(stage["scope"] == self.seed["scope_A"] and len(stage["grants"]) == 1, "SINGLETON_SCOPE_AND_GRANT")
        expected = self.env.state["requests"]
        for row in stage["requests"]:
            raw = expected[row["rid"]]
            self.check(row["origin"] == raw["origin"] and row["request_digest"] == raw["digest"], "ORIGINAL_ORIGIN_AND_FULL_DIGEST_MATCH")
            self.check(row["operation"] == raw["request"]["operation"] and row["phase"] == raw["phase"], "OPERATION_PHASE_EXACT")
        self.check(stage["legacy_obligations"] == ["rF", "rU"] and len(stage["disposals"]) == 1, "SCOPED_LEGACY_AND_DISPOSAL_PROJECTION")

    def test_H06_account_audience(self):
        permit, base = self.permit()
        for key in ("account", "audience"):
            request = copy.deepcopy(base)
            request["scope"][key] = "foreign"
            self.rejected_without_read(self.exercise(direct=lambda: self.env.host.read_summary(request, self.env.identity, permit)), "READ_SCOPE_DENIED")

    def test_H07_task_caller_generation(self):
        permit, base = self.permit()
        for key in ("tasks", "callers", "generations"):
            request = copy.deepcopy(base)
            request["scope"][key] = ["foreign"]
            self.rejected_without_read(self.exercise(direct=lambda: self.env.host.read_summary(request, self.env.identity, permit)), "READ_SCOPE_DENIED")
        other = self.env.policy.bind_authenticated_caller(principal_ref="manager1", actor="agentA", transport_ref="rpc:agent", expires_ns=self.meta["expiry"])
        self.rejected_without_read(self.exercise(direct=lambda: self.env.host.read_summary(base, other, permit)), "HOST_PERMISSION_DENIED")

    def test_H08_cartesian_scope(self):
        self.env.policy.allow(principal_ref="manager1", actor="user", transport_ref="rpc:controller", scope=self.seed["scope_B"],
                              grant_ref="gB", scope_ref="scope:h1B", expires_ns=self.meta["expiry"])
        permit, request = self.permit()
        mixed = copy.deepcopy(request)
        mixed["scope"]["callers"] = ["agentB"]
        self.rejected_without_read(self.exercise(direct=lambda: self.env.host.read_summary(mixed, self.env.identity, permit)), "READ_SCOPE_DENIED")
        wide = copy.deepcopy(request)
        for key in ("tasks", "callers", "generations"):
            wide["scope"][key] += self.seed["scope_B"][key]
        self.rejected_without_read(self.exercise(direct=lambda: self.env.host.read_summary(wide, self.env.identity, permit)), "READ_SCOPE_DENIED")

    def test_H09_selectors(self):
        for key in ("grant", "grant_id", "rid", "fields", "path", "reader", "key_path", "authority_revision"):
            body = {"scope": self.seed["scope_A"], key: "foreign"}
            self.rejected_without_read(self.exercise(body=body), "UNSUPPORTED_READ_REQUEST")
        state = copy.deepcopy(self.seed["state"])
        state["grants"]["gExtra"] = copy.deepcopy(state["grants"]["gA"])
        state["grants"]["gExtra"]["grant_id"] = "gExtra"
        self.check(self.exercise(self.environment(state))["status"] == "SOURCE_BINDING_CONFLICT", "UNEXPECTED_SAME_TUPLE_GRANT_NOT_ENUMERATED")

    def test_H10_lock_parallel(self):
        before = self.env.reader.world_hash()
        barrier = threading.Barrier(4)
        def one(_):
            thread = threading.get_ident()
            barrier.wait(3)
            wire = self.env.controller.request({"scope": self.seed["scope_A"]})
            return thread, json.loads(wire)
        start = time.perf_counter_ns()
        with ThreadPoolExecutor(max_workers=4) as pool:
            batches = list(pool.map(one, range(4)))
        self.check(len({x[0] for x in batches}) == 4 and len(set(self.env.reader.read_threads)) == 4, "FOUR_REAL_THREADS_THROUGH_SOURCE")
        self.check(self.env.reader.reads == self.env.reader.operations == 4 and self.env.reader.lock.maximum == 2, "FOUR_SERIALIZED_SINGLE_READS_WITH_REENTRANT_LOCK")
        self.check(before == self.env.reader.world_hash(), "PARALLEL_WORLD_UNCHANGED")
        trace = self.env.trace
        for index, event in enumerate(trace):
            if event == "read_state":
                self.check(trace[index - 2:index] == ["reader+", "reader+"], "HOST_OUTER_THEN_R12_INNER_LOCK")
        for _, public in batches:
            self.verify_public(public, json.dumps(public))
            self.check(public["status"] == "STAGING_READY_WITH_GAPS" and public["authority_revision"] == 120, "PARALLEL_REVISIONS_MATCH")
        self.batches.append({"kind": "four_thread_reads", "thread_count": 4, "barrier_parties": 4,
                             "thread_identifiers": sorted({x[0] for x in batches}),
                             "source_thread_identifiers": sorted(set(self.env.reader.read_threads)),
                             "effects": self.env.reader.counters(), "world_before": before,
                             "world_after": self.env.reader.world_hash(), "results": [x[1] for x in batches],
                             "elapsed_ns": time.perf_counter_ns() - start})

    def test_H11_isolation_traps(self):
        self.exercise()
        tree = ast.parse((Path(__file__).parents[1] / "src/auth_lifecycle/online_state/dsat_authority_read_host.py").read_text())
        imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        forbidden = {"storage", "services", "sqlite3", "native_provider", "native_http", "lab", "networkx"}
        self.check(not any(set(x.split(".")) & forbidden for x in imports), "NO_RUNTIME_SERVICE_OR_DATABASE_IMPORT")
        self.check(self.env.reader.forbidden == self.env.reader.connection.forbidden == 0, "SOURCE_SQL_OLD_CALL_COMMIT_TRAPS_NOT_HIT")

    def test_H12_quota(self):
        self.env.reader.operation_limit = 7
        self.check(self.exercise()["status"] == "STAGING_READY_WITH_GAPS", "EXACT_ONE_PLUS_SIX_HEADROOM_ACCEPTS")
        self.rejected_without_read(self.exercise(), "READ_BUDGET_DENIED")
        self.check(self.env.reader.operations == len(self.env.reader.metrics) == 1, "BUDGET_DENIAL_NO_EXTRA_CHARGE")
        env = self.environment()
        env.reader.operation_limit = 6
        self.rejected_without_read(self.exercise(env), "READ_BUDGET_DENIED")

    def test_H13_failure_ordering(self):
        for failure, counts in [("telemetry", (0, 0, 0)), ("key", (1, 1, 0)), ("decode", (1, 1, 1))]:
            env = self.environment()
            env.reader.failure = failure
            public = self.exercise(env)
            effect = self.calls[-1]["simulation_effect_delta"]
            self.check(public["status"] == "READ_SOURCE_UNAVAILABLE", "SOURCE_FAILURE_FIXED_CODE")
            self.check(effect["operations"] == effect["telemetry_attempts"] == 1, "FAILED_READ_CHARGES_BEFORE_TELEMETRY")
            self.check((effect["simulated_selects"], effect["simulated_key_reads"], effect["simulated_decode_attempts"]) == counts, "SOURCE_FAILURE_STAGE_ORDER_EXACT")
        env = self.environment()
        env.audit.failure = True
        public = self.exercise(env)
        self.check(public["status"] == "READ_SOURCE_UNAVAILABLE" and public["snapshot_digest"] is None,
                   "HOST_AUDIT_FAILURE_DISCARDS_DATA_WITHOUT_RETRY")
        self.check(env.reader.reads == 1 and env.audit.attempts == 1, "HOST_AUDIT_FAILURE_COST_RETAINED")
        env = self.environment()
        def fail_at_return(_):
            raise RuntimeError(self.canaries["exception"])
        public = self.exercise(env, stage_hook=fail_at_return)
        self.check(public["status"] == "READ_SOURCE_UNAVAILABLE" and public["snapshot_digest"] is None,
                   "ADAPTER_RETURN_FAILURE_RETAINS_CHARGE_AND_DISCARDS_DATA")

    def test_H14_active_transaction(self):
        self.env.reader.connection.in_transaction = True
        self.rejected_without_read(self.exercise(), "HOST_CONNECTION_NOT_IDLE")
        self.check(self.env.reader.connection.in_transaction is True and self.env.reader.connection.forbidden == 0,
                   "FOREIGN_TRANSACTION_NEVER_COMMITTED_OR_ROLLED_BACK")

    def test_H15_schema(self):
        self.exercise()
        self.rejected_without_read(self.exercise(self.environment(source_contract="unknown")), "UNSUPPORTED_SOURCE_SCHEMA")
        self.rejected_without_read(self.exercise(self.environment(source_kind="LOCAL_AUTHORITY_HOST")), "UNSUPPORTED_SOURCE_SCHEMA")
        state = copy.deepcopy(self.seed["state"])
        state["schema"] = "unknown3"
        self.check(self.exercise(self.environment(state))["status"] == "UNSUPPORTED_SOURCE_SCHEMA", "UNREVIEWED_STATE_SCHEMA_REFUSED_NO_MIGRATION")

    def test_H16_private_decode(self):
        public = self.exercise()
        self.check(self.env.reader.key_reads == self.env.reader.decode_attempts == 1, "SYNTHETIC_DECODE_ONLY_IN_AUTHORITY_DOMAIN")
        self.check(all(k not in public for k in ("grants", "requests", "disposals", "partial_math", "request_verifications", "state", "key")), "CONTROLLER_ONLY_RECEIVES_MINIMAL_SUMMARY")
        self.check(len(self.env.controller.received) == 1 and self.env.controller.received == self.env.rpc.responses, "SERIALIZED_RPC_RESPONSE_ONLY")
        self.check(self.stages[-1]["requests"][0]["rid"] in {"rF", "rP", "rU"}, "B1_INTERNAL_MAPPING_AVAILABLE_IN_TRUSTED_TEST_PROBE")

    def test_H17_sinks(self):
        public = self.exercise()
        permit, request = self.permit()
        for value in (self.env.host, self.env.policy, self.env.identity, permit):
            self.secrets_absent(repr(value))
            try:
                pickle.dumps(value)
            except (TypeError, hostmod.HostReadError) as error:
                self.secrets_absent(str(error))
            else:
                self.check(False, "HOST_CONTROL_OBJECT_SERIALIZATION_REFUSED")
        summary = hostmod.HostReadSummary(public)
        self.secrets_absent(pickle.dumps(summary).decode("latin1"))
        for target in ("root", "audit"):
            forged = copy.deepcopy(public)
            if target == "root":
                forged["handle"] = self.canaries["handle"]
            else:
                forged["audit"]["refresh_token"] = self.canaries["refresh_token"]
            try:
                hostmod.HostReadSummary(forged)
            except hostmod.HostReadError:
                pass
            else:
                self.check(False, "NESTED_SECRET_EXTENSION_MUST_BE_REFUSED")
        state = copy.deepcopy(self.seed["state"])
        state["requests"]["rF"]["request"]["payload"]["password"] = self.canaries["password"]
        self.check(self.exercise(self.environment(state))["status"] == "SOURCE_BINDING_CONFLICT", "UNKNOWN_SENSITIVE_ORIGINAL_FIELD_REFUSED")

    def test_H18_world_effects(self):
        public = self.exercise()
        effect = self.calls[-1]["simulation_effect_delta"]
        self.check(all(effect[k] == 1 for k in effect), "ONE_READ_OPERATION_TELEMETRY_SELECT_KEY_DECODE")
        expected = ["read_state", "operation_increment", "source_telemetry_attempt", "source_telemetry_committed",
                    "synthetic_select", "synthetic_key_read", "synthetic_decode"]
        self.check([x for x in self.calls[-1]["source_trace"] if not x.startswith(("reader", "policy"))] == expected, "PINNED_STORAGE_ORDER_MIRRORED")
        self.check(public["audit"]["permit_consumed"] is True and len(self.env.audit.rows) == 1, "HOST_CONTROL_EFFECTS_SEPARATE")
        summary = hostmod.HostReadSummary(public)
        modified = summary.to_dict()
        modified["missing_fields"].clear()
        modified["audit"]["source_read_count"] = 0
        self.check(summary.to_dict() == public and self.env.reader.world_hash() == self.calls[-1]["world_before"], "OUTPUT_DEEPLY_DETACHED")

    def test_H19_revoke_order(self):
        env = self.env
        env.reader.entered, env.reader.release_gate = threading.Event(), threading.Event()
        revoke_attempt, revoke_done = threading.Event(), threading.Event()
        before = env.reader.world_hash()
        def revoke():
            revoke_attempt.set()
            env.policy.revoke(self.meta["principal"], self.seed["scope_A"])
            revoke_done.set()
        with ThreadPoolExecutor(max_workers=2) as pool:
            pending = pool.submit(env.controller.request, {"scope": self.seed["scope_A"]})
            try:
                self.check(env.reader.entered.wait(3), "READ_REACHED_LOCKED_SOURCE")
                withdrawal = pool.submit(revoke)
                self.check(revoke_attempt.wait(3) and not revoke_done.wait(.02), "WITHDRAWAL_WAITS_FOR_AUTHORIZED_READ_LOCK")
            finally:
                env.reader.release_gate.set()
            public = json.loads(pending.result(3))
            withdrawal.result(3)
        self.verify_public(public, json.dumps(public))
        self.check(public["status"] == "STAGING_READY_WITH_GAPS" and revoke_done.is_set(), "READ_LINEARIZES_BEFORE_POLICY_REVOCATION")
        self.rejected_without_read(self.exercise(env), "HOST_PERMISSION_DENIED")
        self.check(before == env.reader.world_hash(), "REVOCATION_CHANGES_ONLY_HOST_POLICY")
        self.batches.append({"kind": "read_then_revoke", "read_status": public["status"],
                             "world_before": before, "world_after": env.reader.world_hash(),
                             "effects": env.reader.counters(), "revoke_completed": revoke_done.is_set()})

    def test_H20_replay(self):
        permit, request = self.permit()
        barrier = threading.Barrier(2)
        def one(_):
            barrier.wait(3)
            return self.env.host.read_summary(request, self.env.identity, permit).to_dict()
        before = self.env.reader.world_hash()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(one, range(2)))
        self.check(sorted(x["status"] for x in results) == ["HOST_PERMIT_REPLAY", "STAGING_READY_WITH_GAPS"], "CONCURRENT_SAME_PERMIT_EXACTLY_ONE_READ")
        self.check(self.env.reader.reads == self.env.reader.operations == 1, "REPLAY_NO_DOUBLE_CHARGE")
        for public in results:
            self.verify_public(public, json.dumps(public))
        self.rejected_without_read(self.exercise(direct=lambda: self.env.host.read_summary(request, self.env.identity, permit)), "HOST_PERMIT_REPLAY")
        self.batches.append({"kind": "same_permit_race", "results": results, "effects": self.env.reader.counters(),
                             "world_before": before, "world_after": self.env.reader.world_hash()})

    def test_H21_source_substitution(self):
        for attribute, replacement in (("_epoch", "epoch:other"), ("_producer", "producer:other"), ("_locator", "authority:other")):
            env = self.environment()
            permit, request = self.permit(env)
            setattr(env.host, attribute, replacement)
            self.rejected_without_read(self.exercise(env, direct=lambda: env.host.read_summary(request, env.identity, permit)), "HOST_SOURCE_MISMATCH")
        env = self.environment()
        permit, request = self.permit(env)
        env.host._reader = self.environment().reader
        self.rejected_without_read(self.exercise(env, direct=lambda: env.host.read_summary(request, env.identity, permit)), "HOST_SOURCE_MISMATCH")
        self.check(env.host._reader.reads == 0, "SUBSTITUTED_READER_NEVER_READ")

    def test_H22_limits(self):
        for limits in (hostmod.HostReadLimits(scoped_records=1), hostmod.HostReadLimits(staging_bytes=4096)):
            public = self.exercise(self.environment(limits=limits))
            self.check(public["status"] == "RESOURCE_LIMIT" and public["snapshot_digest"] is None, "RESOURCE_FAILURE_NO_PARTIAL_STAGING")
        public = self.exercise()
        public["read_scope_ref"] = "x" * 5000
        try:
            hostmod.HostReadSummary(public)
        except hostmod.HostReadError:
            pass
        else:
            self.check(False, "OVERSIZED_PUBLIC_FIELD_DENIED")

    def test_H23_separate_rights(self):
        self.check(self.exercise()["status"] == "STAGING_READY_WITH_GAPS", "INACTIVE_BUSINESS_GRANT_WITH_SEPARATE_AUDIT_RIGHT")
        state = copy.deepcopy(self.seed["state"])
        state["grants"]["gA"]["active"] = True
        env = self.environment(state)
        env.policy.allow(principal_ref="manager1", actor="user", transport_ref="rpc:controller", scope=self.seed["scope_A"],
                         grant_ref="gA", scope_ref="scope:h1A", expires_ns=self.meta["expiry"], rights=())
        self.rejected_without_read(self.exercise(env), "HOST_PERMISSION_DENIED")

    def test_H24_qualification_and_binding(self):
        first = self.exercise()
        env = self.environment()
        env.reader.version = 121
        second = self.exercise(env)
        self.check(first["authority_revision"] == 120 and second["authority_revision"] == 121
                   and first["snapshot_digest"] != second["snapshot_digest"], "REVISION_AND_SNAPSHOT_BINDING")
        stage = self.stages[-1]
        self.check(stage["obligation_revision"] is None and stage["typed_obligation_status"] == "TYPED_O_NOT_IMPLEMENTED", "NO_DEFAULT_TYPED_O_OR_ZERO_REVISION")
        self.check(stage["partial_math"]["U"] is None and stage["partial_math"]["E"] is None
                   and stage["partial_math"]["D_P"] is None, "UNKNOWN_MATH_DOMAIN_PRESERVED")
        refresh = next(x for x in stage["requests"] if x["rid"] == "rF")
        self.check(refresh["source_rid"] == "rP" and refresh["operation"] == "refresh", "SOURCE_FROM_VERIFIED_ORIGINAL")
        state = copy.deepcopy(self.seed["state"])
        state["requests"]["rF"]["request"]["payload"]["source_rid"] = "rB"
        self.exercise(self.environment(state))
        refresh = next(x for x in self.stages[-1]["requests"] if x["rid"] == "rF")
        self.check(refresh["source_rid"] is None and "SOURCE_REFERENCE_UNAVAILABLE" in self.stages[-1]["gap_codes"], "CROSS_ORIGIN_PARENT_REMAINS_UNKNOWN")
        for field in ("origin", "handle", "digest"):
            env = self.environment()
            tampered = copy.deepcopy(env.state)
            if field == "origin":
                tampered["requests"]["rF"]["origin"]["grant_id"] = "missing"
            elif field == "handle":
                tampered["requests"]["rF"]["request"]["handle"] = self.canaries["foreign_handle"]
            else:
                tampered["requests"]["rF"]["digest"] = "0" * 64
            env.reader.codec._plain = canonical(tampered)
            self.check(self.exercise(env)["status"] == "SOURCE_BINDING_CONFLICT", "FORGED_ORIGINAL_ORIGIN_HANDLE_DIGEST_REFUSED")
        state = copy.deepcopy(self.seed["state"])
        state["reconciliation_windows"]["account1"]["receipt"] = {"schema": "native-attempt-closure/1", "claim": "CLOSED"}
        state["reconciliation_windows"]["account1"]["active"] = False
        self.exercise(self.environment(state))
        self.check(self.stages[-1]["windows"][0]["legacy_receipt_summary"]["scope"] == "ONE_ATTEMPT_HISTORY_ONLY", "OLD_CLOSED_REMAINS_HISTORY_ONLY")
        for operation in ("grant", "issue", "refresh", "revoke", "commit", "native-close", "COMPLETE"):
            self.rejected_without_read(self.exercise(operation=operation), "UNSUPPORTED_READ_REQUEST")
        deadline_env = self.environment(limits=hostmod.HostReadLimits(soft_deadline_ns=1))
        self.check(self.exercise(deadline_env)["status"] == "HOST_DEADLINE_EXCEEDED", "SOFT_DEADLINE_DISCARDS_RESULT_WITHOUT_RETRY")
