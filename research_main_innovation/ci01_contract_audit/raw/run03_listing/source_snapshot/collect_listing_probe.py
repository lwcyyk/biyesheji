"""Read-only token-list permission probe for one fresh fixture user.

The query is scoped to that new user's name and organization. Returned secrets
are represented only by fingerprints. No new protection mechanism is installed.
"""
import argparse
import base64
import json
import shutil
import sys
import uuid
from urllib.parse import urlencode

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
    manifest_path = output / "source_hashes.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for filename in ["collect_listing_probe.py", "FROZEN_LISTING_ADDENDUM.json"]:
        path = evidence.ROOT / filename
        shutil.copyfile(path, output / "source_snapshot" / filename)
        manifest.append({"path": str(path), "snapshot": "source_snapshot/" + filename, "sha256": evidence.file_hash(path)})
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    sys.path.insert(0, str(dependency_root))
    from auth_lifecycle.experiment import providers
    from auth_lifecycle.experiment.witness import Witness

    recorder = evidence.Recorder(output)
    for prior_name in ["run01", "run02_secretless"]:
        prior = json.loads((evidence.ROOT / "raw" / prior_name / "result.json").read_text(encoding="utf-8"))
        recorder.limits = {key: value - prior["http_costs"].get(key, 0) for key, value in recorder.limits.items()}
    original = recorder.instrument(providers.HTTP)
    provider = providers.Casdoor()
    actor = None
    actor_name = "l1-ci01-" + uuid.uuid4().hex[:16]
    materials = {}
    observations = []
    result = {"case": "C02_scoped_listing_permission", "status": "UNKNOWN", "actor_deleted": False,
              "new_protection_mechanism": False, "permission_observations": []}

    def remember(label, response):
        pair = providers.required(response)
        if not pair.get("access_token") or not pair.get("refresh_token"):
            raise RuntimeError("missing pair")
        materials[label] = pair
        recorder.emit("material_delivered", {"label": label, "access_ref": evidence.digest(pair["access_token"]),
                       "refresh_ref": evidence.digest(pair["refresh_token"])}, runner_visible=True)
        return pair

    def sample(point, labels):
        with recorder.stage("measurement", point, "observer_only"):
            for label in labels:
                pair = materials[label]
                signed = witness.signed_access(pair["access_token"], subject=actor["id"])
                recorder.local_counts["signature_checks"] += 1
                at = witness.active(pair["access_token"])
                rt = witness.active(pair["refresh_token"], hint="refresh_token")
                response = witness.http.call("GET", provider.base + "/api/userinfo",
                                             headers={"Authorization": "Bearer " + pair["access_token"]})
                row = {"case": recorder.case, "point": point, "label": label,
                       "signature_account_audience_valid": signed, "access_active": at, "refresh_active": rt,
                       "userinfo_http": response["http"], "userinfo_subject_matches": response["body"].get("sub") == actor["id"],
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
        with recorder.stage("method", "issue_A0", "runner"):
            a0 = remember("A0", provider.issue(actor))
        with recorder.stage("method", "issue_B0", "runner"):
            b0 = remember("B0", provider.issue(actor))
        with recorder.stage("method", "refresh_A0", "runner"):
            remember("A1", provider.refresh(a0["refresh_token"]))
        sample("before_listing", ["A1", "B0"])
        query = urlencode({"owner": "admin", "organization": "l1-study", "pageSize": 100,
                           "p": 1, "field": "user", "value": actor_name})
        client = provider.clients[0]
        basic = base64.b64encode((client["id"] + ":" + client["secret"]).encode()).decode()
        for role, authorization in [("ordinary_user_bearer", "Bearer " + b0["access_token"]),
                                    ("application_client_basic", "Basic " + basic)]:
            with recorder.stage("measurement", "list_own_fixture_tokens_" + role, "observer_only"):
                response = witness.http.call("GET", provider.base + "/api/get-tokens?" + query,
                                             headers={"Authorization": authorization})
            data = response["body"].get("data")
            summary = {"role": role, "http": response["http"], "status": response["body"].get("status"),
                       "query_scope": "new fixture user only", "rows_returned": len(data) if isinstance(data, list) else None,
                       "current_source_refs": []}
            if isinstance(data, list):
                if not all(row.get("user") == actor_name and row.get("organization") == "l1-study" for row in data):
                    raise RuntimeError("response escaped the requested fixture filter")
                for row in data:
                    entry = {"record_ref": evidence.digest(str(row.get("name"))),
                             "access_handle_returned": bool(row.get("accessToken")),
                             "refresh_handle_returned": bool(row.get("refreshToken"))}
                    if row.get("accessToken"):
                        entry["access_ref"] = evidence.digest(row["accessToken"])
                    if row.get("refreshToken"):
                        entry["refresh_ref"] = evidence.digest(row["refreshToken"])
                    summary["current_source_refs"].append(entry)
            recorder.emit("scoped_listing_permission", summary)
            result["permission_observations"].append(summary)
        result["status"] = "OBSERVED"
        with recorder.stage("setup", "verify_configuration_after", "fixture"):
            after = providers.required(provider.admin("GET", "get-application?id=admin/app-l1-0"))["data"]
        fields = ["clientId", "organization", "grantTypes", "expireInHours", "refreshExpireInHours", "tokenFormat", "disableRefreshRotation"]
        result["application_configuration_unchanged"] = all(after.get(k) == provider.clients[0]["configuration"].get(k) for k in fields)
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
                    found = providers.required(provider.admin("GET", "get-user?id=l1-study/" + actor_name))
                result["actor_deleted"] = found.get("data") is None
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
    print(json.dumps({k: v for k, v in result.items() if k != "permission_observations"}, ensure_ascii=False))
    print(json.dumps(result["permission_observations"], ensure_ascii=False))


if __name__ == "__main__":
    main()
