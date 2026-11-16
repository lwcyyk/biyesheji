"""Supplementary API observation prompted by checkRefreshClientSecret source audit.

The fixed schedule uses a newly created test account and existing endpoints only.
It adds no enforcement mechanism. Raw material is held only in memory.
"""
from pathlib import Path
import argparse
import json
import shutil
import sys
import uuid

import collect_evidence as evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not evidence.re.fullmatch(r"[a-zA-Z0-9_-]+", args.run_id):
        raise ValueError("invalid new run id")
    output = evidence.ROOT / "raw" / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    dependency_root = evidence.PROJECT / "src"
    evidence.snapshot_sources(output, dependency_root)
    for filename in ["collect_secretless_probe.py", "FROZEN_ADDENDUM.json"]:
        shutil.copyfile(evidence.ROOT / filename, output / "source_snapshot" / filename)
    manifest_path = output / "source_hashes.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for filename in ["collect_secretless_probe.py", "FROZEN_ADDENDUM.json"]:
        path = evidence.ROOT / filename
        manifest.append({"path": str(path), "snapshot": "source_snapshot/" + filename,
                         "sha256": evidence.file_hash(path)})
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    sys.path.insert(0, str(dependency_root))
    from auth_lifecycle.experiment import providers
    from auth_lifecycle.experiment.witness import Witness

    recorder = evidence.Recorder(output)
    prior = json.loads((evidence.ROOT / "raw/run01/result.json").read_text(encoding="utf-8"))
    recorder.limits = {key: value - prior["http_costs"].get(key, 0) for key, value in recorder.limits.items()}
    original = recorder.instrument(providers.HTTP)
    provider = providers.Casdoor()
    actor = None
    actor_name = "l1-ci01-" + uuid.uuid4().hex[:16]
    materials = {}
    observations = []
    result = {"case": "C01_secretless_rotation", "status": "UNKNOWN", "actor_deleted": False,
              "new_protection_mechanism": False}

    def call(operation, action):
        with recorder.stage("method", operation, "runner"):
            response = action()
            recorder.emit("runner_response", evidence.public_response(response), runner_visible=True)
            return response

    def remember(label, response, parent):
        body = providers.required(response)
        if not body.get("access_token") or not body.get("refresh_token"):
            raise RuntimeError("no token pair")
        materials[label] = body
        recorder.emit("material_delivered", {"label": label, "parent": parent,
                     "access_ref": evidence.digest(body["access_token"]),
                     "refresh_ref": evidence.digest(body["refresh_token"])}, runner_visible=True)
        with recorder.stage("measurement", "native_record_" + label, "observer_only"):
            unit = witness.native_unit(body["access_token"], actor)
            recorder.local_counts["readonly_database_queries"] += 2
            recorder.emit("native_record_witness", {"label": label, "unit_ref": unit})
        return body

    def secretless_refresh(pair):
        return provider.http.call("POST", provider.base + "/api/login/oauth/refresh_token", form={
            "grant_type": "refresh_token", "refresh_token": pair["refresh_token"],
            "client_id": provider.clients[0]["id"], "scope": "openid"})

    def sample(point, selected):
        with recorder.stage("measurement", point, "observer_only"):
            for label in selected:
                pair = materials[label]
                signed = witness.signed_access(pair["access_token"], subject=actor["id"])
                recorder.local_counts["signature_checks"] += 1
                at_active = witness.active(pair["access_token"])
                rt_active = witness.active(pair["refresh_token"], hint="refresh_token")
                response = witness.http.call("GET", provider.base + "/api/userinfo",
                                             headers={"Authorization": "Bearer " + pair["access_token"]})
                row = {"case": recorder.case, "point": point, "label": label,
                       "access_ref": evidence.digest(pair["access_token"]),
                       "refresh_ref": evidence.digest(pair["refresh_token"]),
                       "signature_account_audience_valid": signed, "access_active": at_active,
                       "refresh_active": rt_active, "userinfo_http": response["http"],
                       "userinfo_subject_matches": response["body"].get("sub") == actor["id"],
                       "userinfo_accepted": response["http"] == 200 and response["body"].get("sub") == actor["id"]}
                row["event_seq"] = recorder.emit("independent_acceptance", row)
                observations.append(row)

    try:
        evidence.load_environment(provider, recorder, output, providers.PRIVATE, providers)
        with recorder.stage("measurement", "initialize_existing_witness", "observer_only"):
            witness = Witness(provider)
        recorder.case = result["case"]
        recorder.emit("fixture_account_intent", {"name": actor_name})
        with recorder.stage("setup", "create_new_actor", "fixture"):
            actor = provider.create_actor(actor_name)
        result["actor_name"] = actor_name
        result["subject_ref"] = evidence.digest(actor["id"])
        a0 = remember("A0", call("issue_A0", lambda: provider.issue(actor)), "A.g0 password grant")
        remember("B0", call("issue_B0", lambda: provider.issue(actor)), "B.g0 password grant")
        a1 = remember("A1", call("refresh_A0_without_client_secret", lambda: secretless_refresh(a0)), "A0")
        call("revoke_consumed_A0", lambda: provider.revoke(a0["refresh_token"]))
        sample("after_parent_revoke", ["A1", "B0"])
        a2 = remember("A2", call("refresh_A1_without_client_secret", lambda: secretless_refresh(a1)), "A1")
        call("revoke_consumed_A1", lambda: provider.revoke(a1["refresh_token"]))
        sample("after_second_parent_revoke", ["A2", "B0"])
        call("revoke_current_A2", lambda: provider.revoke(a2["refresh_token"]))
        retry = call("retry_A2_without_client_secret", lambda: secretless_refresh(a2))
        if retry["body"].get("access_token"):
            remember("A_unexpected", retry, "A2 retry")
        sample("endpoint_check", ["A2", "B0"])
        result["status"] = "OBSERVED"
        with recorder.stage("setup", "verify_configuration_after", "fixture"):
            after = providers.required(provider.admin("GET", "get-application?id=admin/app-l1-0"))["data"]
        keys = ["clientId", "organization", "grantTypes", "expireInHours", "refreshExpireInHours", "tokenFormat", "disableRefreshRotation"]
        result["application_configuration_unchanged"] = all(after.get(k) == provider.clients[0]["configuration"].get(k) for k in keys)
    except Exception as error:
        result["error_type"] = type(error).__name__
        recorder.emit("case_error", {"exception_type": type(error).__name__})
    finally:
        try:
            if actor is None and provider.logged_in:
                with recorder.stage("cleanup", "lookup_attempted_fixture_account", "fixture"):
                    found = providers.required(provider.admin("GET", "get-user?id=l1-study/" + actor_name)).get("data")
                if found and found.get("name") == actor_name and found.get("owner") == "l1-study":
                    actor = {"name": actor_name, "id": found["id"]}
                    provider.owned[actor_name] = actor["id"]
            if actor:
                with recorder.stage("cleanup", "disable_test_account", "fixture"):
                    provider.root_stop(actor)
                with recorder.stage("cleanup", "delete_test_account", "fixture"):
                    provider.remove_actor(actor)
                with recorder.stage("cleanup", "verify_account_absent", "fixture"):
                    response = providers.required(provider.admin("GET", "get-user?id=l1-study/" + actor_name))
                result["actor_deleted"] = response.get("data") is None
                sample("after_fixture_cleanup", list(materials))
            if provider.logged_in:
                with recorder.stage("cleanup", "logout_fixture_admin_session", "fixture"):
                    result["admin_session_logout"] = evidence.public_response(provider.admin_http.call("POST", provider.base + "/api/logout"))
        except Exception as error:
            result["cleanup_error_type"] = type(error).__name__
        result["http_costs"] = dict(recorder.counts)
        result["http_total"] = sum(recorder.counts.values())
        result["local_measurement_costs"] = dict(recorder.local_counts)
        result["remaining_budget_at_start"] = recorder.limits
        (output / "observations.json").write_text(json.dumps(observations, indent=2), encoding="utf-8")
        (output / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        recorder.close()
        providers.HTTP.call = original
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
