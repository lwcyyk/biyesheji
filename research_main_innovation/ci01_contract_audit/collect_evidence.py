"""Fixed native API schedules for CI-01 evidence collection.

This module records observations and delays delivery of one real refresh response.
It implements no authorization policy, revocation propagation, fence, or recovery.
Secrets stay in process memory. HTTP records use an explicit public-field projection.
"""

from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.metadata
import json
import re
import shutil
import sys
import time
import uuid
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PROJECT = Path(r"D:\毕业设计\auth-lifecycle")


def digest(value):
    return sha256(value.encode("utf-8")).hexdigest()


def file_hash(path):
    with path.open("rb") as stream:
        return sha256(stream.read()).hexdigest()


def public_response(response):
    """Only whitelisted fields enter logs, including error responses."""
    body = response.get("body", {})
    result = {"http": response.get("http"), "body_type": type(body).__name__}
    if not isinstance(body, dict):
        return result
    for name in ("active", "expires_in", "token_type", "scope", "status"):
        value = body.get(name)
        if isinstance(value, (bool, int, float, str)) and name in body:
            result[name] = value
    code = body.get("error")
    if isinstance(code, str) and re.fullmatch(r"[a-z_]{1,50}", code):
        result["oauth_error"] = code
    for name in ("access_token", "refresh_token", "id_token"):
        if isinstance(body.get(name), str):
            result[name + "_ref"] = digest(body[name])
    if isinstance(body.get("sub"), str):
        result["subject_ref"] = digest(body["sub"])
    if "data" in body:
        result["data_present"] = body["data"] is not None
    return result


class Recorder:
    def __init__(self, output):
        self.output = output
        self.stream = (output / "http_and_events.jsonl").open("x", encoding="utf-8")
        self.runner = (output / "runner_visible.jsonl").open("x", encoding="utf-8")
        self.sequence = 0
        self.previous = "0" * 64
        self.case = "environment"
        self.category = "setup"
        self.operation = "environment"
        self.visibility = "fixture"
        self.counts = Counter()
        self.local_counts = Counter()
        self.limits = {"method": 50, "measurement": 140, "setup": 30, "cleanup": 20}

    def emit(self, event, payload, *, runner_visible=False):
        self.sequence += 1
        row = {
            "seq": self.sequence,
            "utc": datetime.now(timezone.utc).isoformat(),
            "monotonic_ns": time.monotonic_ns(),
            "case": self.case,
            "category": self.category,
            "operation": self.operation,
            "visibility": self.visibility,
            "evidence_kind": "NEW_SAMPLE",
            "event": event,
            "payload": payload,
            "previous": self.previous,
        }
        canonical = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        row["sha256"] = digest(canonical)
        self.previous = row["sha256"]
        line = json.dumps(row, ensure_ascii=False) + "\n"
        self.stream.write(line)
        self.stream.flush()
        if runner_visible:
            self.runner.write(line)
            self.runner.flush()
        return row["seq"]

    @contextmanager
    def stage(self, category, operation, visibility):
        old = self.category, self.operation, self.visibility
        self.category, self.operation, self.visibility = category, operation, visibility
        try:
            yield
        finally:
            self.category, self.operation, self.visibility = old

    def instrument(self, http_class):
        original = http_class.call
        recorder = self

        def recorded(instance, method, url, **kwargs):
            from urllib.parse import urlsplit, parse_qs
            if recorder.counts[recorder.category] >= recorder.limits[recorder.category]:
                raise RuntimeError("registered request category budget exhausted")
            parsed = urlsplit(url)
            if parsed.hostname != "127.0.0.1" or parsed.port != 18081:
                raise RuntimeError("frozen Casdoor endpoint mismatch")
            recorder.counts[recorder.category] += 1
            request_id = sum(recorder.counts.values())
            recorder.emit("http_sent", {
                "request_id": request_id, "method": method, "path": parsed.path,
                "query_keys": sorted(parse_qs(parsed.query)),
                "form_keys": sorted((kwargs.get("form") or {}).keys()),
                "payload_keys": sorted((kwargs.get("payload") or {}).keys()),
                "header_names": sorted((kwargs.get("headers") or {}).keys()),
            })
            started = time.monotonic_ns()
            try:
                response = original(instance, method, url, **kwargs)
            except Exception as error:
                recorder.emit("http_unknown", {
                    "request_id": request_id, "exception_type": type(error).__name__,
                    "elapsed_ns": time.monotonic_ns() - started,
                })
                raise
            recorder.emit("http_received", {
                "request_id": request_id, "response": public_response(response),
                "elapsed_ns": time.monotonic_ns() - started,
            })
            return response

        http_class.call = recorded
        return original

    def close(self):
        self.stream.close()
        self.runner.close()


def snapshot_sources(output, dependency_root):
    files = [Path(__file__), ROOT / "MODEL_AND_CONTRACT.md"]
    files.extend(dependency_root / "auth_lifecycle" / name for name in [
        "__init__.py", "experiment/__init__.py", "experiment/providers.py",
        "experiment/witness.py", "experiment/journal.py",
    ])
    manifest = []
    for path in files:
        relative = path.relative_to(dependency_root) if path.is_relative_to(dependency_root) else Path(path.name)
        target = output / "source_snapshot" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        manifest.append({"path": str(path), "snapshot": str(target.relative_to(output)), "sha256": file_hash(path)})
    (output / "source_hashes.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def load_environment(provider, recorder, output, runtime, providers):
    with recorder.stage("setup", "admin_login", "fixture"):
        provider.admin_login()
    with recorder.stage("setup", "read_existing_application", "fixture"):
        body = providers.required(provider.admin("GET", "get-application?id=admin/app-l1-0"))
    app = body.get("data")
    if not isinstance(app, dict) or app.get("organization") != "l1-study":
        raise RuntimeError("frozen application unavailable")
    public_fields = ["name", "clientId", "organization", "grantTypes", "expireInHours",
                     "refreshExpireInHours", "tokenFormat", "cert", "disableRefreshRotation"]
    public_config = {key: app.get(key) for key in public_fields}
    public_config["disableRefreshRotation"] = bool(app.get("disableRefreshRotation", False))
    if app.get("tokenFormat") != "JWT" or app.get("expireInHours") != 1 or app.get("disableRefreshRotation", False):
        raise RuntimeError("frozen token/rotation profile changed")
    if not {"password", "refresh_token"}.issubset(set(app.get("grantTypes", []))):
        raise RuntimeError("frozen grant types unavailable")
    provider.clients = [{"id": app["clientId"], "secret": app["clientSecret"],
                         "native_id": app["name"], "configuration": app}]
    with recorder.stage("setup", "discovery", "fixture"):
        discovery = provider.discovery()
    if discovery.get("userinfo_endpoint") != provider.base + "/api/userinfo":
        raise RuntimeError("userinfo endpoint differs from frozen contract")
    artifact = runtime / "downloads/casdoor_Windows_x86_64.zip"
    binary = runtime / "dist/casdoor/casdoor.exe"
    with zipfile.ZipFile(artifact) as archive:
        entry = next(name for name in archive.namelist() if Path(name).name.lower() == "casdoor.exe")
        archive_binary_hash = sha256(archive.read(entry)).hexdigest()
    binary_hash = file_hash(binary)
    archive_hash = file_hash(artifact)
    if archive_hash != "24457f4383e33639d851514ddbb49fcaac85fca630f4736901c14d13a1114b32" or binary_hash != archive_binary_hash:
        raise RuntimeError("release artifact/binary binding mismatch")
    environment = {
        "utc": datetime.now(timezone.utc).isoformat(), "implementation": "Casdoor", "version": "4.25.0",
        "upstream_commit": "528a0213f01caf70b9f41009cbf7b2f67bdd67ec", "runtime_reference": str(runtime),
        "base": provider.base, "public_configuration": public_config,
        "discovery": {key: discovery.get(key) for key in ["issuer", "token_endpoint", "userinfo_endpoint", "jwks_uri", "revocation_endpoint", "introspection_endpoint"]},
        "distribution_sha256": archive_hash, "binary_sha256": binary_hash,
        "binary_matches_release_archive": True, "source_reproducible_build_proved": False,
        "python": sys.version, "cryptography": importlib.metadata.version("cryptography"),
        "selected_operation": "newly approved reauthorization via existing password grant",
        "resource_profile": "fresh cookie-free GET /api/userinfo with only bearer AT",
        "limits": recorder.limits,
    }
    (output / "environment.lock.json").write_text(json.dumps(environment, ensure_ascii=False, indent=2), encoding="utf-8")
    recorder.emit("environment_frozen", {"configuration": public_config, "binary_sha256": binary_hash})


def run_case(name, provider, recorder, witness, providers, output):
    recorder.case = name
    actor = None
    pairs = {}
    measurements = []
    cleanup = {"case": name, "actor_created": False, "actor_deleted": False}
    actor_name = "l1-ci01-" + uuid.uuid4().hex[:16]
    recorder.emit("fixture_account_intent", {"name": actor_name, "organization": "l1-study"})

    def remember(label, response, origin):
        body = providers.required(response)
        if not body.get("access_token") or not body.get("refresh_token"):
            raise RuntimeError("token pair response missing")
        pairs[label] = body
        recorder.emit("material_delivered", {
            "label": label, "origin": origin,
            "access_ref": digest(body["access_token"]), "refresh_ref": digest(body["refresh_token"]),
            "native_approval_generation_binding": False,
        }, runner_visible=True)
        return body

    def method(operation, call):
        with recorder.stage("method", operation, "runner"):
            response = call()
            recorder.emit("runner_response", public_response(response), runner_visible=True)
            return response

    def sample(point, material_map):
        # Results are emitted to the separate observer log and never returned.
        with recorder.stage("measurement", point, "observer_only"):
            for label, pair in material_map.items():
                at, rt = pair["access_token"], pair["refresh_token"]
                signed = witness.signed_access(at, subject=actor["id"])
                recorder.local_counts["signature_checks"] += 1
                access_active = witness.active(at)
                refresh_active = witness.active(rt, hint="refresh_token")
                userinfo = witness.http.call("GET", provider.base + "/api/userinfo", headers={"Authorization": "Bearer " + at})
                body = userinfo.get("body", {})
                subject_match = isinstance(body, dict) and body.get("sub") == actor["id"]
                row = {
                    "case": name, "point": point, "label": label,
                    "access_ref": digest(at), "refresh_ref": digest(rt),
                    "signature_account_audience_valid": signed,
                    "access_active": access_active, "refresh_active": refresh_active,
                    "userinfo_http": userinfo["http"], "userinfo_subject_matches": subject_match,
                    "userinfo_accepted": userinfo["http"] == 200 and subject_match,
                }
                row["event_seq"] = recorder.emit("independent_acceptance", row)
                measurements.append(row)

    def native_record(label, pair):
        with recorder.stage("measurement", "native_record_" + label, "observer_only"):
            unit = witness.native_unit(pair["access_token"], actor)
            recorder.local_counts["readonly_database_queries"] += 2
            recorder.emit("native_record_witness", {"label": label, "unit_ref": unit,
                                                    "access_ref": digest(pair["access_token"])})

    error_type = None
    try:
        with recorder.stage("setup", "create_new_actor", "fixture"):
            actor = provider.create_actor(actor_name)
        cleanup["actor_created"] = True
        cleanup["actor_name"] = actor_name
        cleanup["subject_ref"] = digest(actor["id"])
        recorder.emit("case_start", {"subject_ref": digest(actor["id"]), "schedule": name})
        recorder.emit("approved_schedule_entered", {"tasks": ["A.g0", "B.g0"], "authority": "preauthorized experiment fixture"}, runner_visible=True)
        a0 = remember("A0", method("issue_A0", lambda: provider.issue(actor)), "A.g0 initial password grant")
        b0 = remember("B0", method("issue_B0", lambda: provider.issue(actor)), "B.g0 initial password grant")
        native_record("A0", a0)
        native_record("B0", b0)
        sample("initial", {"A0": a0, "B0": b0})

        held = None
        if name == "W01_delayed_refresh":
            recorder.emit("runner_pending", {"attempt": "A-refresh-1", "origin": "A.g0"}, runner_visible=True)
            with recorder.stage("method", "refresh_A0_hold_response", "collector_only"):
                held = provider.refresh(a0["refresh_token"])
            recorder.emit("delivery_held", {"attempt": "A-refresh-1", "schedule_fact": "native HTTP returned before parent revoke dispatch", "response": public_response(held)})
            if held["body"].get("access_token"):
                native_record("A1_held", held["body"])

        method("revoke_A0", lambda: provider.revoke(a0["refresh_token"]))
        recorder.emit("parent_revoke_ack_boundary", {"completion_claim_issued": False}, runner_visible=True)
        at_ack = {"A0": a0, "B0": b0}
        if held and held["body"].get("access_token"):
            at_ack["A1_held"] = held["body"]
        sample("after_parent_ack", at_ack)

        recorder.emit("new_approval_fixture_entered", {"task": "B", "generation": "g1", "permits": "new password grant and userinfo use", "native_consent_ui_observed": False}, runner_visible=True)
        b1 = remember("B1", method("reauthorize_B1", lambda: provider.issue(actor)), "B.g1 fresh password grant")
        native_record("B1", b1)
        sample("after_B_reauthorization", {"B0": b0, "B1": b1})
        if held:
            recorder.emit("late_response_delivered", {"attempt": "A-refresh-1", "origin": "A.g0", "response": public_response(held)}, runner_visible=True)
            if held["body"].get("access_token"):
                remember("A1", held, "A.g0 refresh attempt A-refresh-1")
                sample("late_response_known", {"A1": pairs["A1"], "B1": b1})

        old_retry = method("retry_old_A0_RT", lambda: provider.refresh(a0["refresh_token"]))
        if old_retry["body"].get("access_token"):
            remember("A_unexpected_retry", old_retry, "old A0 RT retry")
        if "A1" in pairs:
            method("revoke_known_A1", lambda: provider.revoke(pairs["A1"]["refresh_token"]))
            child_retry = method("retry_revoked_A1_RT", lambda: provider.refresh(pairs["A1"]["refresh_token"]))
            if child_retry["body"].get("access_token"):
                remember("A_unexpected_child_retry", child_retry, "revoked A1 RT retry")
        sample("endpoint_check", pairs)
        recorder.emit("schedule_endpoint", {"all_registered_responses_delivered": True, "case_asserts_universal_completion": False}, runner_visible=True)
    except Exception as error:
        error_type = type(error).__name__
        recorder.emit("case_error", {"exception_type": error_type, "result": "UNKNOWN"})
    finally:
        # Only the freshly named actor can be recovered for fixture teardown.
        try:
            if actor is None:
                with recorder.stage("cleanup", "lookup_attempted_fixture_account", "fixture"):
                    found = providers.required(provider.admin("GET", "get-user?id=l1-study/" + actor_name)).get("data")
                if found and found.get("name") == actor_name and found.get("owner") == "l1-study":
                    actor = {"name": actor_name, "id": found["id"]}
                    provider.owned[actor_name] = actor["id"]
                    cleanup["actor_created"] = True
            if actor is not None:
                with recorder.stage("cleanup", "disable_test_account", "fixture"):
                    provider.root_stop(actor)
                with recorder.stage("cleanup", "delete_test_account", "fixture"):
                    provider.remove_actor(actor)
                with recorder.stage("cleanup", "verify_account_absent", "fixture"):
                    check = providers.required(provider.admin("GET", "get-user?id=l1-study/" + actor_name))
                cleanup["actor_deleted"] = check.get("data") is None
                sample("after_fixture_cleanup", pairs)
                recorder.emit("fixture_cleanup", cleanup)
        except Exception as error:
            cleanup["exception_type"] = type(error).__name__
            recorder.emit("cleanup_unresolved", cleanup)
        (output / (name + "_observations.json")).write_text(json.dumps(measurements, indent=2), encoding="utf-8")
        (output / (name + "_cleanup.json")).write_text(json.dumps(cleanup, indent=2), encoding="utf-8")
    return {"case": name, "status": "OBSERVED" if error_type is None else "UNKNOWN",
            "error_type": error_type, "cleanup": cleanup, "measurement_rows": len(measurements)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--dependency-root", type=Path, default=PROJECT / "src")
    parser.add_argument("--service-runtime", type=Path, default=PROJECT / ".runtime/l1")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.run_id):
        raise ValueError("run id must be a new simple name")
    output = ROOT / "raw" / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    snapshot_sources(output, args.dependency_root)
    sys.path.insert(0, str(args.dependency_root))
    from auth_lifecycle.experiment import providers
    from auth_lifecycle.experiment.witness import Witness
    providers.PRIVATE = args.service_runtime
    recorder = Recorder(output)
    original = recorder.instrument(providers.HTTP)
    provider = providers.Casdoor()
    result = {"phase": "CI01_NATIVE_EVIDENCE", "cases": [], "new_protection_mechanism": False}
    try:
        load_environment(provider, recorder, output, args.service_runtime, providers)
        with recorder.stage("measurement", "initialize_existing_witness", "observer_only"):
            witness = Witness(provider)
        for case in ["N01_normal", "W01_delayed_refresh"]:
            result["cases"].append(run_case(case, provider, recorder, witness, providers, output))
        with recorder.stage("setup", "verify_configuration_after", "fixture"):
            after = providers.required(provider.admin("GET", "get-application?id=admin/app-l1-0"))["data"]
        fields = ["name", "clientId", "organization", "grantTypes", "expireInHours",
                  "refreshExpireInHours", "tokenFormat", "cert", "disableRefreshRotation"]
        result["application_configuration_unchanged"] = all(
            after.get(key) == provider.clients[0]["configuration"].get(key) for key in fields
        )
    except Exception as error:
        result["environment_error_type"] = type(error).__name__
        recorder.emit("environment_error", {"exception_type": type(error).__name__})
    finally:
        if provider.logged_in:
            with recorder.stage("cleanup", "logout_fixture_admin_session", "fixture"):
                try:
                    response = provider.admin_http.call("POST", provider.base + "/api/logout")
                    result["admin_session_logout"] = public_response(response)
                except Exception as error:
                    result["admin_session_logout"] = {"exception_type": type(error).__name__}
        result["http_costs"] = dict(recorder.counts)
        result["local_measurement_costs"] = dict(recorder.local_counts)
        result["http_total"] = sum(recorder.counts.values())
        (output / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        recorder.close()
        providers.HTTP.call = original
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
