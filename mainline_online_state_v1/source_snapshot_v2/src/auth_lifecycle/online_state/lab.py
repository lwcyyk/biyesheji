"""Isolated process fixture. Only synthetic credentials and loopback endpoints."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import ipaddress
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import sys
import time

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from .protocol import Client, EventLog, write_json


def protect_directory(path):
    if os.name == "nt":
        output = subprocess.check_output(["whoami", "/user", "/fo", "csv", "/nh"])
        match = re.search(rb"S-\d+(?:-\d+)+", output)
        if match is None:
            raise RuntimeError("CURRENT_USER_SID_UNAVAILABLE")
        sid = match.group().decode("ascii")
        command = ["icacls", str(path), "/inheritance:r", "/grant:r",
                   "*" + sid + ":(OI)(CI)F", "/grant:r", "*S-1-5-18:(OI)(CI)F"]
        result = subprocess.run(command, capture_output=True)
        if result.returncode:
            raise RuntimeError("PRIVATE_DIRECTORY_ACL_FAILED")
        return {"mechanism": "Windows DACL", "allowed_sids": [sid, "S-1-5-18"]}
    os.chmod(path, 0o700)
    return {"mechanism": "POSIX", "mode": "0700"}


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def initialize(root, operation_limit=None):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=False)
    secure = root / "secure"
    secure.mkdir()
    acl = protect_directory(secure)
    for directory in ("authority", "provider", "controller", "cache", "control", "runner", "scorer"):
        (root / directory).mkdir()
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "online-state-local-test")])
    now = datetime.now(timezone.utc)
    certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                   .public_key(private_key.public_key()).serial_number(x509.random_serial_number())
                   .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=7))
                   .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), False)
                   .sign(private_key, hashes.SHA256()))
    cert_path = secure / "server.crt"
    key_path = secure / "server.key"
    cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(private_key.private_bytes(serialization.Encoding.PEM,
                                                  serialization.PrivateFormat.PKCS8,
                                                  serialization.NoEncryption()))
    (secure / "authority.key").write_bytes(os.urandom(32))
    (secure / "provider.key").write_bytes(os.urandom(32))
    ports = {}
    while len(ports) < 3:
        port = free_port()
        if port not in ports.values() and port not in {18080, 18081, 8080}:
            ports[("authority", "provider", "controller")[len(ports)]] = port
    authority_token = secrets.token_urlsafe(32)
    provider_token = secrets.token_urlsafe(32)
    common = {"certificate": str(cert_path), "tls_key": str(key_path)}
    configs = {
        "authority": {**common, "port": ports["authority"], "operation_limit": operation_limit,
                      "identities": {"controller": authority_token},
                      "permissions": {"controller": ["grant", "admit", "release", "record", "revoke", "recover"]}},
        "provider": {**common, "port": ports["provider"],
                     "identities": {"adapter": provider_token, "fixture": secrets.token_urlsafe(32)},
                     "permissions": {"adapter": ["perform", "lookup"], "fixture": ["hold"]}},
        "controller": {**common, "port": ports["controller"],
                       "authority_url": "https://127.0.0.1:" + str(ports["authority"]),
                       "provider_url": "https://127.0.0.1:" + str(ports["provider"]),
                       "authority_token": authority_token, "provider_token": provider_token,
                       "identities": {name: secrets.token_urlsafe(32) for name in ("user", "agentA", "agentB")},
                       "permissions": {"user": ["grant", "revoke", "recover", "deliver", "status"],
                                       "agentA": ["call", "status"], "agentB": ["call", "status"]}}
    }
    for role, config in configs.items():
        write_json(secure / (role + ".json"), config)
    write_json(root / "control" / "environment.json", {
        "contract": "ONLINE_TRUSTED_STATE_V1", "ports": ports, "acl": acl,
        "operation_limit": operation_limit, "fault_domain": "controller process and cache/view.json",
        "independent_paths": ["authority", "provider", "secure"], "native_requests": 0,
        "identity_fixture": "Bearer capabilities provisioned outside agent input; trusted same-host test principal",
        "same_os_account_trust": "OS account and fixture are trusted; adversarial OS-user isolation untested"})
    return root


class Laboratory:
    def __init__(self, root, operation_limit=None, create=True):
        self.root = initialize(root, operation_limit) if create else Path(root).resolve()
        self.processes = {}
        self.streams = []
        self.log = EventLog(self.root / "control" / "processes.jsonl")
        self.runner_log = EventLog(self.root / "runner" / "rpc.jsonl")
        self.executor = ThreadPoolExecutor(max_workers=12)
        self.configs = {role: json.loads((self.root / "secure" / (role + ".json")).read_text())
                        for role in ("authority", "provider", "controller")}

    def start(self, role, fault=None):
        if role in self.processes and self.processes[role].poll() is None:
            raise RuntimeError("PROCESS_ALREADY_RUNNING")
        ready = self.root / "control" / (role + "_ready.json")
        ready.unlink(missing_ok=True)
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        command = [sys.executable, "-B", "-m", "auth_lifecycle.online_state.cli", "serve",
                   "--root", str(self.root), "--role", role]
        if fault:
            command += ["--fault", fault]
        filename = role + "_" + secrets.token_hex(4) + ".stderr"
        stream = (self.root / "control" / filename).open("wb")
        self.streams.append(stream)
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        process = subprocess.Popen(command, env=env, stdout=stream, stderr=stream, creationflags=flags)
        self.processes[role] = process
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("SERVICE_START_FAILED_" + role)
            if ready.exists():
                data = json.loads(ready.read_text())
                if data["pid"] == process.pid:
                    self.log.emit("started", role=role, child_pid=process.pid, boot=data.get("boot"))
                    return data
            time.sleep(0.02)
        raise TimeoutError("SERVICE_START_TIMEOUT_" + role)

    def start_all(self, fault=None):
        self.start("authority")
        self.start("provider")
        return self.start("controller", fault)

    def stop(self, role):
        process = self.processes.get(role)
        if process is not None and process.poll() is None:
            process.kill()
            code = process.wait(timeout=5)
            self.log.emit("terminated_and_waited", role=role, child_pid=process.pid, exit_code=code)

    def restart_controller(self, fault=None):
        self.stop("controller")
        return self.start("controller", fault)

    def client(self, identity="user", role="controller", timeout=3):
        config = self.configs[role]
        return Client("https://127.0.0.1:" + str(config["port"]),
                      config["identities"][identity], config["certificate"], self.runner_log, timeout)

    def async_call(self, identity, operation, payload):
        return self.executor.submit(self.client(identity, timeout=12).call, operation, payload)

    def wait_barrier(self, point):
        pid = self.processes["controller"].pid
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            for path in (self.root / "controller" / "barriers").glob("*_" + point + ".json"):
                if json.loads(path.read_text())["pid"] == pid:
                    return path
            time.sleep(0.01)
        raise TimeoutError("BARRIER_TIMEOUT_" + point)

    def snapshot_cache(self):
        path = self.root / "cache" / "view.json"
        return path.read_bytes()

    def restore_cache(self, snapshot):
        process = self.processes.get("controller")
        if process is not None and process.poll() is None:
            raise RuntimeError("OLD_CONTROLLER_STILL_ACTIVE")
        path = (self.root / "cache" / "view.json").resolve()
        if not path.is_relative_to(self.root / "cache"):
            raise RuntimeError("RESTORE_PATH_OUTSIDE_CACHE")
        path.write_bytes(snapshot)
        self.log.emit("cache_restored", path="cache/view.json", restored_bytes=len(snapshot))

    def close(self):
        for role in ("controller", "provider", "authority"):
            self.stop(role)
        self.executor.shutdown(wait=True, cancel_futures=True)
        for stream in self.streams:
            stream.close()


def approval(task, generation, budget=4):
    return {"approval_op": "approve_" + task + "_" + generation,
            "caller": "agent" + task, "task": task, "account": "account1",
            "audience": "fake_rp", "generation": generation, "operations": ["use"],
            "budget": budget, "material": "synthetic_initial_" + task + "_" + generation}


def request_for(handle, task, generation, rid, value=1):
    return {"rid": rid, "handle": handle, "task": task, "account": "account1",
            "audience": "fake_rp", "generation": generation, "operation": "use",
            "payload": {"value": value}}
