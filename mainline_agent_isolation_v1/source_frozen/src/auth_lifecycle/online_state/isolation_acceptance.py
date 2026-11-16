"""M5: mature Windows restricted-token + ACL deployment fixture, synthetic only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import subprocess
import sys
import time

from .lab import Laboratory, approval, request_for
from .protocol import canonical, write_json
from .windows_isolation import IsolationUnavailable, launch_restricted, set_acl, inspect_file_acl


SCENARIOS = [f"M5-{i:02d}" for i in range(1, 13)]
SUPPORT_SIDS = ["S-1-5-32-545", "S-1-1-0", "S-1-5-12"]


def current_sid():
    return re.search(rb"S-\d+(?:-\d+)+", subprocess.check_output(
        ["whoami.exe", "/user", "/fo", "csv", "/nh"])).group().decode("ascii")


def scoped(root, path):
    root, path = Path(root).resolve(), Path(path).resolve()
    if path == root or path.is_relative_to(root): return path
    raise ValueError("M5_PATH_OUTSIDE_OWNED_ROOT")


def source_lock():
    repo = Path(__file__).resolve().parents[3]
    paths = []
    for directory in ("src", "scripts", "tests"):
        for p in (repo / directory).rglob("*"):
            if p.is_file() and p.suffix in {".py", ".sql", ".ps1"}:
                paths.append({"path": p.relative_to(repo).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    paths.append({"path": "pyproject.toml", "sha256": hashlib.sha256((repo / "pyproject.toml").read_bytes()).hexdigest()})
    return {"files": sorted(paths, key=lambda x: x["path"]), "native_requests": 0}


def copy_runtime(target):
    target = Path(target)
    source = Path(sys.executable).parent
    target.mkdir()
    for p in source.iterdir():
        if p.is_file() and p.suffix in {".exe", ".dll"}: shutil.copy2(p, target / p.name)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "site-packages", "test", "tests", "idlelib", "tkinter", "ensurepip")
    shutil.copytree(source / "Lib", target / "Lib", ignore=ignore)
    shutil.copytree(source / "DLLs", target / "DLLs", ignore=shutil.ignore_patterns("*_tkinter*"))
    site = target / "Lib" / "site-packages"
    site.mkdir()
    for name in ("cryptography", "cffi", "pycparser"):
        p = source / "Lib" / "site-packages" / name
        if p.exists(): shutil.copytree(p, site / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for p in (source / "Lib" / "site-packages").glob("_cffi_backend*"):
        shutil.copy2(p, site / p.name)
    return target / "python.exe"


class Agent:
    def __init__(self, env, name, domain=None, integrity=4096):
        self.env, self.name, self.sequence = env, name, 0
        self.work = env.root / "agents" / name
        self.work.mkdir()
        set_acl(self.work, env.owner, [(domain or env.sids[name], "FA")], low=integrity == 4096)
        for part in ("in", "out"): (self.work / part).mkdir()
        cfg = {"work": str(self.work), "capability": env.lab.configs["controller"]["identities"].get("agent" + name, ""),
               "urls": {role: "https://127.0.0.1:" + str(c["port"]) for role, c in env.lab.configs.items()},
               "certificate": str(env.assets / "server.crt")}
        write_json(self.work / "config.json", cfg)
        command = [str(env.python), "-I", "-S", "-B", str(env.assets / "isolation_agent.py"),
                   "--config", str(self.work / "config.json")]
        self.command = command
        self.process = launch_restricted(command, self.work, domain or env.sids[name],
                                         env.clean_environment(self.work), integrity_rid=integrity)
        env.owned.append(self.process)
        env.save_owned_processes()
        deadline = time.monotonic() + 12
        while not (self.work / "ready.json").exists():
            if self.process.poll() is not None:
                raise IsolationUnavailable("AGENT_BOOT_EXIT", self.process.poll())
            if time.monotonic() > deadline: raise IsolationUnavailable("AGENT_BOOT_TIMEOUT", 1460)
            time.sleep(.02)
        self.identity = json.loads((self.work / "ready.json").read_text())

    def ask(self, action, **fields):
        self.sequence += 1
        filename = f"{self.sequence:04d}.json"
        write_json(self.work / "in" / filename, {"action": action, **fields})
        path = self.work / "out" / filename
        deadline = time.monotonic() + 15
        while not path.exists():
            if self.process.poll() is not None: raise RuntimeError("AGENT_EXITED")
            if time.monotonic() > deadline: raise TimeoutError("AGENT_COMMAND_TIMEOUT")
            time.sleep(.02)
        result = json.loads(path.read_text())
        return result

    def rpc(self, operation, payload=None, **fields):
        return self.ask("rpc", operation=operation, payload=payload or {}, **fields)


class IsolationLab:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=False)
        self.owner = current_sid()
        set_acl(self.root, self.owner)
        seed = [secrets.randbelow(2**30) + 2**29 for _ in range(3)]
        prefix = "S-1-5-21-" + "-".join(map(str, seed))
        self.sids = {n: prefix + "-" + str(i) for n, i in [("A", 1001), ("B", 1002), ("R", 1003)]}
        self.owned, self.agent_objects, self.started = [], {}, time.monotonic()
        self.acls = {}
        # Allow traversal to separately ACL-protected children. No generic Users
        # or Everyone ACE is placed on any M5 resource.
        for name in ("assets", "agents"):
            path = self.root / name; path.mkdir()
            self.acls[name] = set_acl(path, self.owner, [(s, "GRGX") for s in self.sids.values()])
        self.assets = self.root / "assets"
        self.python = copy_runtime(self.assets / "python")
        self.code = self.assets / "source"
        package = Path(__file__).resolve().parents[1]
        destination = self.code / "auth_lifecycle" / "online_state"
        destination.mkdir(parents=True)
        shutil.copy2(package / "__init__.py", destination.parent / "__init__.py")
        for name in ("__init__.py", "protocol.py", "storage.py", "materials.py", "services.py", "lab.py",
                     "reconciliation.py", "isolation_agent.py", "isolation_service.py", "migration.sql", "migration_2.sql"):
            shutil.copy2(Path(__file__).with_name(name), destination / name)
        shutil.copy2(Path(__file__).with_name("isolation_agent.py"), self.assets / "isolation_agent.py")
        self.lab = Laboratory(self.root / "trusted")
        # Replace inherited user-only security on every precreated trusted item.
        for p in [self.lab.root, *self.lab.root.rglob("*")]:
            set_acl(p, self.owner, [(self.sids["R"], "FA")])
        self.scorer = self.root / "scorer_private"; self.scorer.mkdir()
        set_acl(self.scorer, self.owner)
        self.markers = {name: "M5_" + name + "_" + secrets.token_hex(24) for name in
                        ("AT", "RT", "APP_SECRET", "SCORER_PRIVATE", "INBOX")}
        (self.scorer / "private.key").write_text(self.markers["SCORER_PRIVATE"])
        self.lab.configs["controller"]["identities"]["recovery"] = secrets.token_urlsafe(32)
        permissions = self.lab.configs["controller"]["permissions"]
        permissions["user"] = ["grant", "revoke", "deliver", "status", "begin_reconciliation", "reconcile", "dispose"]
        permissions["recovery"] = ["recover"]
        self.lab.configs["provider"]["synthetic_application_secret"] = self.markers["APP_SECRET"]
        for role, config in self.lab.configs.items(): write_json(self.lab.root / "secure" / (role + ".json"), config)
        (self.lab.root / "secure" / "admin.cap").write_text(self.lab.configs["controller"]["identities"]["user"])
        (self.lab.root / "secure" / "approval_config.json").write_text('{"fixture":"M5"}')
        # An encrypted synthetic inbox is a file-access target, never an A input.
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        nonce = os.urandom(12)
        (self.lab.root / "provider" / "operational_inbox.bin").write_bytes(nonce + AESGCM(
            (self.lab.root / "secure" / "provider.key").read_bytes()).encrypt(nonce, self.markers["INBOX"].encode(), b"M5"))
        shutil.copy2(self.lab.root / "secure" / "server.crt", self.assets / "server.crt")
        # Explicitly inheritable canary remains excluded by bInheritHandles=False.
        self.canary = (self.lab.root / "secure" / "handle_canary.bin").open("w+b")
        self.canary.write(os.urandom(32)); self.canary.flush()
        import msvcrt
        self.canary_handle = msvcrt.get_osfhandle(self.canary.fileno())
        os.set_handle_inheritable(self.canary_handle, True)
        write_json(self.scorer / "expected.json", {"markers": self.markers,
            "capabilities": {r: c["identities"] for r, c in self.lab.configs.items()}})
        self.lab.start = self.start_service
        self.targets = []
        self.audit = []

    def clean_environment(self, work, service=False):
        env = {"SystemRoot": os.environ.get("SystemRoot", r"C:\Windows"), "TEMP": str(work),
               "TMP": str(work), "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}
        if service: env["PYTHONPATH"] = str(self.code)
        return env

    def save_owned_processes(self):
        write_json(self.root / "OWNED_PROCESSES.json", {"root": str(self.root), "processes": [
            {"pid": p.pid, **p.facts} for p in self.owned]})

    def start_service(self, role, fault=None):
        previous = self.lab.processes.get(role)
        if previous and previous.poll() is None: raise RuntimeError("OLD_INSTANCE_STILL_RUNNING")
        ready = self.lab.root / "control" / (role + "_ready.json"); ready.unlink(missing_ok=True)
        command = [str(self.python), "-B", "-m", "auth_lifecycle.online_state.isolation_service", "--root", str(self.lab.root), "--role", role]
        if fault: command += ["--fault", fault]
        p = launch_restricted(command, self.lab.root, self.sids["R"],
                              self.clean_environment(self.lab.root / "control", True), integrity_rid=8192)
        self.lab.processes[role] = p; self.owned.append(p)
        self.save_owned_processes()
        deadline = time.monotonic() + 12
        while not ready.exists():
            if p.poll() is not None: raise IsolationUnavailable("SERVICE_BOOT_" + role, p.poll())
            if time.monotonic() > deadline: raise IsolationUnavailable("SERVICE_BOOT_TIMEOUT_" + role, 1460)
            time.sleep(.02)
        data = json.loads(ready.read_text())
        if data["pid"] != p.pid: raise RuntimeError("STALE_READY_FILE")
        self.lab.log.emit("started_restricted", role=role, child_pid=p.pid,
                          restricting_sid=self.sids["R"], integrity="Medium", boot=data.get("boot"))
        return data

    def start(self):
        if any(config.get("native_profile") for config in self.lab.configs.values()):
            raise ValueError("M5_NATIVE_PROFILE_FORBIDDEN")
        self.lab.start_all()
        self.user = self.lab.client("user")
        self.recovery = self.lab.client("recovery")
        self.grants = {}
        for task, gen in [("A", "g0"), ("B", "g1")]:
            a = approval(task, gen, 100)
            a["material"] = "synthetic_" + self.markers["AT"] + "_" + self.markers["RT"] + "_" + task
            self.grants[task] = self.user.call("grant", a)
            if self.grants[task].get("status") != "GRANTED": raise RuntimeError("GRANT_SETUP_FAILED")
        self.old_cache = self.lab.snapshot_cache()
        for task in ("A", "B"):
            self.agent_objects[task] = Agent(self, task)
        rprobe = Agent(self, "R_probe", self.sids["R"], 8192)
        self.rprobe = rprobe
        self.runtime_scorer_probe = rprobe.ask("read", targets=[{"object": "scorer_private_key", "path": str(self.scorer / "private.key")}])
        self.setup_identity = {task: obj.ask("identity") for task, obj in self.agent_objects.items()}
        self.setup_identity["R_probe"] = rprobe.ask("identity")
        self.read_targets = [
            ("authority_key", self.lab.root / "secure" / "authority.key"),
            ("adapter_configuration", self.lab.root / "secure" / "provider.json"),
            ("management_capability", self.lab.root / "secure" / "admin.cap"),
            ("operational_inbox", self.lab.root / "provider" / "operational_inbox.bin"),
            ("scorer_private_key", self.scorer / "private.key"),
            ("B_configuration", self.agent_objects["B"].work / "config.json"),
            ("controller_configuration", self.lab.root / "secure" / "controller.json"),
            ("material_database", self.lab.root / "authority" / "authority.db"),
            ("audit_evidence", self.scorer / "expected.json")]
        self.write_targets = [
            ("authority_database", self.lab.root / "authority" / "authority.db"),
            ("approval_configuration", self.lab.root / "secure" / "approval_config.json"),
            ("security_log", self.lab.root / "authority" / "database_ops.jsonl"),
            ("recovery_cache", self.lab.root / "cache" / "view.json")]
        self.target_manifest = {label: {"path": str(p), "exists": p.exists(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                                for label, p in self.read_targets + self.write_targets}
        if not all(v["exists"] for v in self.target_manifest.values()): raise RuntimeError("TARGET_MISSING")
        self.pids = {role: p.pid for role, p in self.lab.processes.items()}
        self.actual_acls = {str(p.relative_to(self.root)): inspect_file_acl(p) for p in
            [self.lab.root, self.scorer, self.assets, self.agent_objects["A"].work,
             self.agent_objects["B"].work, *[p for _,p in self.read_targets + self.write_targets]]}
        self.lock = {"contract": "ONLINE_TRUSTED_STATE_V1", "crypto": "FROZEN", "native_requests": 0,
                     "owner_sid": self.owner, "restricting_sids": self.sids, "support_restricting_sids": SUPPORT_SIDS,
                     "agent_integrity": "S-1-16-4096", "trusted_runtime_integrity": "S-1-16-8192",
                     "token_user": self.owner, "identities_are": "distinct restricted primary token access domains",
                     "new_sam_users": 0, "inherit_handles": False, "environment_allowlist": list(self.clean_environment(self.root)),
                     "ports": {r: c["port"] for r, c in self.lab.configs.items()}, "registered_pids": self.pids,
                     "runtime": str(self.python), "python_version": sys.version, "sqlite_version": sqlite3.sqlite_version,
                     "windows_version": platform.platform(), "machine": platform.machine(),
                     "acl_sddl": self.acls, "actual_acl_readback": self.actual_acls, "targets": self.target_manifest,
                     "runtime_executable_sha256": hashlib.sha256(self.python.read_bytes()).hexdigest(),
                     "fault_scope": ["trusted/cache/view.json", "registered controller/authority/provider process"],
                     "secret_locations": ["trusted/secure", "trusted/authority", "trusted/provider", "scorer_private"],
                     "outbound_network": "not OS-filtered; tests use registered loopback services only"}
        write_json(self.root / "ENVIRONMENT_LOCK.json", self.lock)
        write_json(self.root / "SOURCE_LOCK.json", source_lock())
        write_json(self.root / "SETUP_CONTROLS.json", {"identities": self.setup_identity,
            "runtime_scorer_probe": self.runtime_scorer_probe, "targets": self.target_manifest})

    def request(self, task, rid, **changes):
        r = request_for(self.grants[task]["handle"], task, "g0" if task == "A" else "g1", rid)
        r.update(changes); return r

    def snapshot(self):
        return self.user.call("status", {})

    def close(self):
        # Never enumerate/kill other processes or alter original account objects.
        results = []
        for process in reversed(self.owned):
            try:
                process.kill(); code = process.wait(5); process.close()
                results.append({"pid": process.pid, "terminated_and_waited": True, "exit_code": code})
            except Exception as error: results.append({"pid": process.pid, "error": type(error).__name__})
        if hasattr(self, "canary"): self.canary.close()
        if hasattr(self, "lab"):
            self.lab.executor.shutdown(wait=True, cancel_futures=True)
        if hasattr(self, "root") and self.root.exists():
            write_json(self.root / "CLEANUP.json", {"processes": results, "sam_users_created": 0,
                "native_requests": 0, "retained": "protected audit, synthetic state, copied runtime and scoped ACLs",
                "external_acl_changes": 0})


def run_scene(env, number):
    A, B = env.agent_objects["A"], env.agent_objects["B"]
    row = {"scenario": f"M5-{number:02d}", "A_pid": A.process.pid, "B_pid": B.process.pid,
           "before": env.snapshot(), "started_monotonic_ns": time.monotonic_ns()}
    if number in {1, 2}:
        who = "A" if number == 1 else "B"
        agent = env.agent_objects[who]
        row["positive"] = agent.ask("identity")
        row["call"] = agent.rpc("call", env.request(who, "legal_" + who))
    elif number == 3:
        row["attacks"] = A.ask("read", targets=[{"object": n, "path": str(p)} for n, p in env.read_targets])
    elif number == 4:
        targets = [{"object": n, "path": str(p)} for n, p in env.write_targets]
        row["attacks"] = A.ask("write", targets=targets)
        if all(not x.get("allowed") for x in row["attacks"]): row["acl_attacks"] = A.ask("acl", targets=targets)
    elif number == 5:
        row["attacks"] = A.ask("process", pids=env.pids, canary_handle=env.canary_handle)
        row["agent_environment"] = A.ask("identity")
    elif number == 6:
        tests = [("controller", "grant", approval("B", "evil")),
                 ("controller", "revoke", {"revoke_op": "evil_B", "grant_id": env.grants["B"]["grant_id"]}),
                 ("controller", "begin_reconciliation", {}), ("controller", "reconcile", {}),
                 ("controller", "deliver", {"rid": "legal_B"}), ("controller", "dispose", {}),
                 ("controller", "recover", {}), ("authority", "recover", {}),
                 ("authority", "grant", {}), ("provider", "lookup", {}), ("provider", "hold", {})]
        row["attacks"] = [{"role": role, "operation": op, **A.rpc(op, p, role=role)} for role, op, p in tests]
        row["wrong_capability"] = A.rpc("status", {}, token="invalid")
        row["status"] = A.rpc("status", {})
        row["recovery_positive"] = env.recovery.call("recover", {})
        row["management_cannot_recover"] = env.user.call("recover", {})
        row["recovery_cannot_grant"] = env.recovery.call("grant", approval("B", "evil2"))
    elif number == 7:
        req = env.request("B", "stolen_B_handle")
        tests = [("B_handle", req), ("caller", {**req, "caller": "agentB"})]
        for field in ("task", "account", "audience", "generation"):
            tests.append((field, {**env.request("A", "tamper_" + field), field: "wrong"}))
        row["attacks"] = [{"field": field, **A.rpc("call", body)} for field, body in tests]
        row["B_positive"] = B.rpc("call", env.request("B", "B_after_handle_attack"))
    elif number == 8:
        req = env.request("A", "own_replay")
        row["initial"] = A.rpc("call", req)
        row["duplicate"] = A.rpc("call", req)
        row["conflict"] = A.rpc("call", {**req, "payload": {"value": 2}})
    elif number == 9:
        row["parse"] = [A.ask("rpc", operation="call", raw=s) for s in
                        ('{"rid":"a","rid":"b"}', '{', '{"payload":NaN}', '[]')]
        row["permission"] = A.rpc("recover", {})
        # Real provider process unavailability exercises the safe exception path.
        env.lab.stop("provider")
        row["provider_error"] = A.rpc("call", env.request("A", "A_provider_unknown"))
        env.lab.start("provider")
        env.pids["provider"] = env.lab.processes["provider"].pid
        row["provider_positive"] = B.rpc("call", env.request("B", "B_after_provider_error"))
    elif number == 10:
        row["ack"] = env.user.call("revoke", {"revoke_op": "withdraw_A", "grant_id": env.grants["A"]["grant_id"]})
        row["attack"] = A.rpc("call", env.request("A", "A_after_revoke"))
        row["B_positive"] = B.rpc("call", env.request("B", "B_after_A_revoke"))
    elif number == 11:
        old = env.lab.processes["controller"].pid
        env.lab.stop("controller"); env.lab.restore_cache(env.old_cache)
        row["restored_cache_sha256"] = hashlib.sha256(env.old_cache).hexdigest()
        env.lab.start("controller")
        row["old_controller_pid"], row["new_controller_pid"] = old, env.lab.processes["controller"].pid
        row["A_still_alive"] = A.process.poll() is None
        row["attack"] = A.rpc("call", env.request("A", "A_after_old_cache"))
        row["B_positive"] = B.rpc("call", env.request("B", "B_after_old_cache"))
    elif number == 12:
        env.lab.stop("authority")
        row["A_during_outage"] = A.rpc("call", env.request("A", "A_authority_outage"))
        row["B_during_outage"] = B.rpc("call", env.request("B", "B_authority_outage"))
        env.lab.start("authority")
        row["recovery_positive"] = env.recovery.call("recover", {})
        row["after_outage_before_resume"] = env.snapshot()
        row["B_positive"] = B.rpc("call", env.request("B", "B_after_authority_outage"))
    row["after"] = env.snapshot()
    row["elapsed_seconds"] = (time.monotonic_ns() - row["started_monotonic_ns"]) / 1e9
    return row


def run(out, authorization_id, development=False):
    out = Path(out).resolve()
    if out.exists(): raise ValueError("NEW_BATCH_DIRECTORY_REQUIRED")
    env = None
    rows = []
    started = time.monotonic()
    try:
        env = IsolationLab(out)
        write_json(out / "PLAN.json", {"authorization_id": authorization_id, "scenarios": SCENARIOS,
            "scope": "DEVELOPMENT_SMOKE" if development else "M5_ACCEPTANCE", "max_scene_seconds": 60,
            "max_batch_seconds": 1800, "native_request_budget": 0,
            "stop_on": ["unauthorized_read", "unauthorized_write", "wrong_dispatch", "secret_delivery"]})
        env.start()
        if development:
            # Test access before entering the acceptance denominator.
            controls = {"identity": env.setup_identity, "R_scorer": env.runtime_scorer_probe,
                "read": env.agent_objects["A"].ask("read", targets=[{"object": n, "path": str(p)} for n,p in env.read_targets]),
                "write": env.agent_objects["A"].ask("write", targets=[{"object": n, "path": str(p)} for n,p in env.write_targets]),
                "acl": env.agent_objects["A"].ask("acl", targets=[{"object": n, "path": str(p)} for n,p in env.write_targets]),
                "process": env.agent_objects["A"].ask("process", pids=env.pids, canary_handle=env.canary_handle),
                "A_call": env.agent_objects["A"].rpc("call", env.request("A", "dev_A")),
                "B_call": env.agent_objects["B"].rpc("call", env.request("B", "dev_B"))}
            write_json(out / "DEVELOPMENT_CONTROLS.json", controls)
            return {"status": "DEVELOPMENT_COMPLETE", "root": str(out)}
        # Independent scorer is frozen with the source and never imported by the
        # service/agent. Invoke it after each scene for immediate stop decisions.
        scorer = Path(__file__).resolve().parents[3] / "scripts" / "score_agent_isolation.py"
        for number in range(1, 13):
            if time.monotonic() - started > 1800: break
            row = run_scene(env, number)
            path = out / (f"M5-{number:02d}.json"); write_json(path, row)
            rows.append(row)
            result = subprocess.run([sys.executable, "-B", str(scorer), "--root", str(out), "--scene", path.name],
                                    capture_output=True, timeout=20)
            if result.returncode not in {0, 2}: raise RuntimeError("SCORER_EXECUTION_FAILED")
            score = json.loads(result.stdout)
            write_json(out / (f"M5-{number:02d}.score.json"), score)
            if score["status"] == "FAIL_SECURITY" or row["elapsed_seconds"] > 60: break
        return {"status": "BATCH_COMPLETE", "executed": len(rows), "root": str(out)}
    except IsolationUnavailable as error:
        out.mkdir(parents=True, exist_ok=True)
        r = {"status": "BLOCKED_ENVIRONMENT", "operation": error.operation, "win32_error": error.code,
             "executed": len(rows), "native_requests": 0}
        write_json(out / "BLOCKED_ENVIRONMENT.json", r)
        return r
    except Exception as error:
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "ABORTED.json", {"status": "ABORTED", "exception": type(error).__name__,
            "executed": len(rows), "native_requests": 0})
        raise
    finally:
        if env is not None: env.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--authorization-id", required=True)
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.out, args.authorization_id, args.development)))


if __name__ == "__main__": main()
