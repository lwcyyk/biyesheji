"""Own portable test processes only. No system service, Docker or production DB."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / ".runtime/l1"


def settings():
    path = RUN / "secrets.json"
    if not path.exists():
        data = {"keycloak_admin": "l1-admin", "keycloak_password": secrets.token_urlsafe(30),
                "casdoor_admin": "admin", "casdoor_password": secrets.token_urlsafe(30)}
        with path.open("x", encoding="utf-8") as f:json.dump(data, f)
    return json.loads(path.read_text(encoding="utf-8"))


def prepare():
    credentials = settings(); base = RUN / "dist/casdoor"
    original = (base / "conf/app.conf").read_text(encoding="utf-8")
    overrides = {"httpport": "18081", "httpaddr": "127.0.0.1", "runmode": "prod", "driverName": "sqlite",
                 "dataSourceName": "file:" + (RUN / "casdoor-l1.db").as_posix() + "?cache=shared", "dbName": "casdoor_l1",
                 "origin": "http://127.0.0.1:18081", "originFrontend": "http://127.0.0.1:18081",
                 "frontendBaseDir": str(base).replace("\\", "/"), "socks5Proxy": "", "ldapServerPort": "0",
                 "ldapsServerPort": "0", "radiusServerPort": "-1", "radiusSecret": secrets.token_urlsafe(24),
                 "initAdminPassword": credentials["casdoor_password"], "showSql": "false", "isDemoMode": "false"}
    lines = []
    for line in original.splitlines():
        name = line.split("=", 1)[0].strip()
        if name not in overrides:lines.append(line)
    lines += [f"{key} = {value}" for key, value in overrides.items()]
    (RUN / "casdoor.conf").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return credentials


def available(port):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", port))


def serve():
    for port in [18080, 18081, 18082]:available(port)
    stop_file=RUN/"STOP"
    if not stop_file.resolve().is_relative_to(RUN.resolve()):raise RuntimeError("stop marker escaped runtime")
    stop_file.unlink(missing_ok=True)
    credentials = prepare(); java_home = next((RUN/"dist/java").glob("jdk*"))
    kc = RUN / "dist/keycloak/keycloak-26.8.1"
    java = java_home / "bin/java.exe"
    opts = [str(java), "-Xms64m", "-Xmx512m", "-Djava.util.logging.manager=org.jboss.logmanager.LogManager",
            "-Dkc.home.dir=" + str(kc), "-Djboss.server.config.dir=" + str(kc/"conf"), "-Dkeycloak.theme.dir=" + str(kc/"themes")]
    tail = ["-cp", str(kc/"lib/quarkus-run.jar"), "io.quarkus.bootstrap.runner.QuarkusEntryPoint", "start-dev",
            "--http-host=127.0.0.1", "--http-port=18080", "--hostname=http://127.0.0.1:18080",
            "--health-enabled=true", "--http-management-host=127.0.0.1", "--http-management-port=18082"]
    env = os.environ.copy(); env.update(KC_BOOTSTRAP_ADMIN_USERNAME=credentials["keycloak_admin"], KC_BOOTSTRAP_ADMIN_PASSWORD=credentials["keycloak_password"], JAVA_HOME=str(java_home))
    logs = [open(RUN/"keycloak-private.log", "ab"), open(RUN/"casdoor-private.log", "ab")]
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    procs = []
    try:
        procs.append(subprocess.Popen(opts + tail, cwd=kc, env=env, stdout=logs[0], stderr=subprocess.STDOUT, creationflags=flags))
        procs.append(subprocess.Popen([str(RUN/"dist/casdoor/casdoor.exe"), "--config", str(RUN/"casdoor.conf")],
                                     cwd=RUN/"dist/casdoor", stdout=logs[1], stderr=subprocess.STDOUT, creationflags=flags))
        rebuilt = False
        while True:
            if procs[0].poll() == 10 and not rebuilt:
                procs[0] = subprocess.Popen(opts + ["-Dkc.config.built=true"] + tail, cwd=kc, env=env,
                                           stdout=logs[0], stderr=subprocess.STDOUT, creationflags=flags); rebuilt = True
            status = {"owner_pid": os.getpid(), "keycloak_pid": procs[0].pid, "casdoor_pid": procs[1].pid,
                      "keycloak_exit": procs[0].poll(), "casdoor_exit": procs[1].poll(),
                      "updated_utc": datetime.now(timezone.utc).isoformat(), "ports": [18080, 18081, 18082]}
            (RUN/"processes.json").write_text(json.dumps(status), encoding="utf-8")
            if any(p.poll() is not None for p in procs):
                print(json.dumps(status), flush=True); raise RuntimeError("native provider exited; inspect private local log")
            if (RUN/"STOP").exists():break
            time.sleep(1)
    finally:
        for proc in procs:
            if proc.poll() is None:proc.terminate()
        for proc in procs:
            try:proc.wait(timeout=15)
            except subprocess.TimeoutExpired:proc.kill()
        for f in logs:f.close()
        (RUN/"processes.json").write_text(json.dumps({"state":"STOPPED","owner_pid":os.getpid(),"updated_utc":datetime.now(timezone.utc).isoformat(),
            "keycloak_exit":procs[0].poll() if procs else None,"casdoor_exit":procs[1].poll() if len(procs)>1 else None}),encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=["serve", "stop"]); args = parser.parse_args()
    if args.command == "serve":serve()
    else:(RUN/"STOP").write_text("stop owned L1 processes", encoding="utf-8")
