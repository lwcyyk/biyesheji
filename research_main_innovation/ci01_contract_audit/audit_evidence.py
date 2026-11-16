"""Read-only audit of captured evidence. It performs no native requests."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "raw/run01"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    rows = [json.loads(line) for line in (RUN / "http_and_events.jsonl").read_text(encoding="utf-8").splitlines()]
    previous = "0" * 64
    for number, row in enumerate(rows, 1):
        assert row["seq"] == number and row["previous"] == previous
        unsigned = {key: value for key, value in row.items() if key != "sha256"}
        actual = sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        assert actual == row["sha256"]
        previous = actual
    runner = [json.loads(line) for line in (RUN / "runner_visible.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all(row == rows[row["seq"] - 1] for row in runner)
    assert all(row["visibility"] != "observer_only" for row in runner)
    assert all(row["event"] not in {"independent_acceptance", "native_record_witness", "delivery_held"} for row in runner)
    late = next(row for row in rows if row["event"] == "late_response_delivered")
    held = next(row for row in rows if row["event"] == "delivery_held")
    assert held["payload"]["response"] == late["payload"]["response"]
    costs = Counter(row["category"] for row in rows if row["event"] == "http_sent")
    operations = Counter((row["category"], row["operation"]) for row in rows if row["event"] == "http_sent")
    result = read(RUN / "result.json")
    assert dict(costs) == result["http_costs"]
    assert sum(costs.values()) == result["http_total"]
    observations = [row for row in rows if row["event"] == "independent_acceptance"]
    by_key = {(row["case"], row["payload"]["point"], row["payload"]["label"]): row for row in observations}
    tests = []

    def expect(case, point, label, accepted):
        row = by_key[(case, point, label)]
        tests.append({"case": case, "point": point, "label": label, "expected_userinfo_acceptance": accepted,
                      "actual_userinfo_acceptance": row["payload"]["userinfo_accepted"], "event_seq": row["seq"],
                      "pass": row["payload"]["userinfo_accepted"] == accepted})

    for case in ["N01_normal", "W01_delayed_refresh"]:
        expect(case, "endpoint_check", "A0", False)
        expect(case, "endpoint_check", "B0", True)
        expect(case, "endpoint_check", "B1", True)
    expect("W01_delayed_refresh", "after_parent_ack", "A1_held", True)
    expect("W01_delayed_refresh", "endpoint_check", "A1", False)
    assert all(item["pass"] for item in tests)
    retries = [row for row in rows if row["event"] == "runner_response" and "retry" in row["operation"]]
    assert len(retries) == 3
    assert all(row["payload"].get("oauth_error") == "invalid_grant" and row["payload"]["http"] == 400 for row in retries)
    assert all(not row["payload"]["userinfo_accepted"] and row["payload"]["access_active"] is False
               and row["payload"]["refresh_active"] is False for row in observations
               if row["payload"]["point"] == "after_fixture_cleanup")
    assert all(case["cleanup"]["actor_deleted"] for case in result["cases"])
    assert result["application_configuration_unchanged"]
    assert all(case["status"] == "OBSERVED" for case in result["cases"])
    # The raw HTTP log omitted secret-bearing body values. Bindings below are
    # explicitly source-derived from the frozen fixed schedule, not wire proofs.
    material = {}
    for row in rows:
        if row["event"] == "material_delivered":
            material[(row["case"], row["payload"]["label"])] = row["payload"]
    method_aliases = {"revoke_A0": "A0", "retry_old_A0_RT": "A0", "refresh_A0_hold_response": "A0",
                      "revoke_known_A1": "A1", "retry_revoked_A1_RT": "A1"}
    bindings = []
    for row in rows:
        if row["event"] == "http_sent" and row["operation"] in method_aliases:
            label = method_aliases[row["operation"]]
            bindings.append({"request_event_seq": row["seq"], "case": row["case"], "operation": row["operation"],
                             "material_label": label, "refresh_ref": material[(row["case"], label)]["refresh_ref"],
                             "evidence_kind": "SOURCE_DERIVED", "basis": "frozen collect_evidence.py fixed schedule"})
    (ROOT / "REQUEST_BINDINGS_FROM_SOURCE.json").write_text(json.dumps(bindings, indent=2), encoding="utf-8")
    cost_record = {"scope": "all local native-service HTTP for this capture, not source-download traffic",
                   "by_category": dict(costs), "total": sum(costs.values()),
                   "by_operation": [{"category": key[0], "operation": key[1], "requests": value}
                                    for key, value in sorted(operations.items())],
                   "local_measurement_costs": result["local_measurement_costs"]}
    (ROOT / "COST_ACCOUNTING.json").write_text(json.dumps(cost_record, indent=2), encoding="utf-8")
    audit = {"scope": "capture integrity, expected observations and isolation projection; no general safety proof",
             "full_events": len(rows), "runner_visible_events": len(runner), "acceptance_rows": len(observations),
             "hash_chain_pass": True, "observer_results_absent_from_runner_log": True,
             "held_response_matches_delivered_response": True, "tests": tests,
             "old_refresh_rejections": len(retries), "all_test_accounts_deleted": True,
             "all_known_pairs_inactive_after_cleanup": True, "application_configuration_unchanged": True,
             "native_requests_by_auditor": 0}
    (ROOT / "EVIDENCE_AUDIT.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    selected = {"case_start", "approved_schedule_entered", "material_delivered", "runner_pending",
                "delivery_held", "parent_revoke_ack_boundary", "new_approval_fixture_entered",
                "late_response_delivered", "native_record_witness", "independent_acceptance",
                "runner_response", "schedule_endpoint", "fixture_cleanup"}
    source = str(RUN / "http_and_events.jsonl")
    source_hash = sha256((RUN / "http_and_events.jsonl").read_bytes()).hexdigest()
    with (ROOT / "EVENT_WITNESS.jsonl").open("w", encoding="utf-8") as stream:
        for row in rows:
            if row["case"] == "environment" or row["event"] not in selected:
                continue
            entry = {"evidence_kind": "NEW_SAMPLE", "source": source, "source_sha256": source_hash,
                     "source_seq": row["seq"], "event_hash": row["sha256"], "case": row["case"],
                     "utc": row["utc"], "monotonic_ns": row["monotonic_ns"], "event": row["event"],
                     "visibility": row["visibility"], "payload": row["payload"]}
            if "approval" in row["event"] or row["event"] == "approved_schedule_entered":
                entry["approval_evidence_limit"] = "preauthorized fixture stage, not a live user consent or native approval proof"
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(json.dumps({"pass": True, "events": len(rows), "observations": len(observations), "http_total": sum(costs.values())}))


def aggregate_supplements():
    root_audit = read(ROOT / "EVIDENCE_AUDIT.json")
    all_costs = Counter(read(RUN / "result.json")["http_costs"])
    local_costs = Counter(read(RUN / "result.json")["local_measurement_costs"])
    runs = [{"run": "run01", "http_total": sum(all_costs.values()),
             "events": root_audit["full_events"], "acceptance_rows": root_audit["acceptance_rows"]}]
    supplementary_events = []
    operations = Counter()
    for row in [json.loads(line) for line in (RUN / "http_and_events.jsonl").read_text(encoding="utf-8").splitlines()]:
        if row["event"] == "http_sent":
            operations[(row["category"], row["operation"])] += 1
    for name in ["run02_secretless", "run03_listing"]:
        directory = ROOT / "raw" / name
        path = directory / "http_and_events.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        previous = "0" * 64
        for number, row in enumerate(rows, 1):
            assert row["seq"] == number and row["previous"] == previous
            unsigned = {key: value for key, value in row.items() if key != "sha256"}
            calculated = sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
            assert calculated == row["sha256"]
            previous = calculated
        runner = [json.loads(line) for line in (directory / "runner_visible.jsonl").read_text(encoding="utf-8").splitlines()]
        assert all(row == rows[row["seq"] - 1] for row in runner)
        assert all(row["visibility"] != "observer_only" for row in runner)
        result = read(directory / "result.json")
        assert result["status"] == "OBSERVED" and result["actor_deleted"]
        assert result["application_configuration_unchanged"]
        counts = Counter(row["category"] for row in rows if row["event"] == "http_sent")
        assert dict(counts) == result["http_costs"]
        all_costs.update(counts)
        local_costs.update(result["local_measurement_costs"])
        obs = read(directory / "observations.json")
        assert all(row["signature_account_audience_valid"] for row in obs)
        assert all(not row["userinfo_accepted"] and row["access_active"] is False and row["refresh_active"] is False
                   for row in obs if row["point"] == "after_fixture_cleanup")
        if name == "run02_secretless":
            requests = [row for row in rows if row["event"] == "http_sent" and "without_client_secret" in row["operation"]]
            assert len(requests) == 3
            assert all("client_secret" not in row["payload"]["form_keys"] and not row["payload"]["header_names"] and not row["payload"]["query_keys"] for row in requests)
            answers = [row for row in rows if row["event"] == "runner_response" and "without_client_secret" in row["operation"]]
            assert [row["payload"]["http"] for row in answers] == [200, 200, 400]
            keyed = {(row["point"], row["label"]): row for row in obs}
            assert keyed[("after_parent_revoke", "A1")]["userinfo_accepted"]
            assert keyed[("after_second_parent_revoke", "A2")]["userinfo_accepted"]
            assert not keyed[("endpoint_check", "A2")]["userinfo_accepted"]
            assert keyed[("endpoint_check", "B0")]["userinfo_accepted"]
        else:
            permissions = {item["role"]: item for item in result["permission_observations"]}
            assert permissions["ordinary_user_bearer"]["status"] == "error"
            app = permissions["application_client_basic"]
            assert app["status"] == "ok" and app["rows_returned"] == 2
            assert all(item["access_handle_returned"] and item["refresh_handle_returned"] for item in app["current_source_refs"])
            material = {row["payload"]["label"]: row["payload"] for row in rows if row["event"] == "material_delivered"}
            assert {item["access_ref"] for item in app["current_source_refs"]} == {material[label]["access_ref"] for label in ["A1", "B0"]}
            assert {item["refresh_ref"] for item in app["current_source_refs"]} == {material[label]["refresh_ref"] for label in ["A1", "B0"]}
        runs.append({"run": name, "http_total": sum(counts.values()), "events": len(rows), "acceptance_rows": len(obs),
                     "capture_hash_chain_pass": True, "all_known_materials_inactive_after_cleanup": True})
        source_hash = sha256(path.read_bytes()).hexdigest()
        for row in rows:
            if row["event"] == "http_sent":
                operations[(row["category"], row["operation"])] += 1
            if row["case"] == "environment" or row["event"] not in {
                "material_delivered", "native_record_witness", "independent_acceptance", "runner_response", "scoped_listing_permission"
            }:
                continue
            supplementary_events.append({"evidence_kind": "NEW_SAMPLE", "source": str(path), "source_sha256": source_hash,
                                         "source_seq": row["seq"], "event_hash": row["sha256"], "case": row["case"],
                                         "utc": row["utc"], "monotonic_ns": row["monotonic_ns"], "event": row["event"],
                                         "visibility": row["visibility"], "payload": row["payload"],
                                         "scope": "registered supplementary native capability probe"})
    limits = read(RUN / "environment.lock.json")["limits"]
    assert all(all_costs[key] <= value for key, value in limits.items())
    root_audit["supplementary_runs"] = runs[1:]
    root_audit["combined_events"] = sum(row["events"] for row in runs)
    root_audit["combined_acceptance_rows"] = sum(row["acceptance_rows"] for row in runs)
    root_audit["combined_test_accounts_deleted"] = 4
    root_audit["original_budget_respected"] = True
    root_audit["secretless_rotation_confirmed_for_two_steps"] = True
    root_audit["ordinary_bearer_listing_denied_app_key_listing_succeeds"] = True
    posthoc_queries = 0
    posthoc_path = ROOT / "POST_CLEANUP_DB.json"
    if posthoc_path.exists():
        posthoc = read(posthoc_path)
        assert posthoc["sql_query_count"] == 4 and len(posthoc["rows"]) == 4
        assert all(item["rows_with_positive_expires_in"] == 0 for item in posthoc["rows"])
        assert all(item["rows_with_nonempty_session_id"] == 0 for item in posthoc["rows"])
        posthoc_queries = posthoc["sql_query_count"]
        root_audit["post_cleanup_retained_token_rows"] = sum(item["retained_token_rows"] for item in posthoc["rows"])
        root_audit["post_cleanup_positive_expiry_rows"] = 0
        root_audit["post_cleanup_nonempty_session_ids"] = 0
        source_hash = sha256(posthoc_path.read_bytes()).hexdigest()
        for index, item in enumerate(posthoc["rows"]):
            supplementary_events.append({"evidence_kind": "NEW_SAMPLE", "source": str(posthoc_path),
                                         "source_sha256": source_hash, "source_record_index": index,
                                         "utc": posthoc["utc"], "event": "post_cleanup_native_record_counts",
                                         "visibility": "observer_only", "payload": item})
    root_audit["posthoc_readonly_db_queries"] = posthoc_queries
    (ROOT / "EVIDENCE_AUDIT.json").write_text(json.dumps(root_audit, indent=2), encoding="utf-8")
    costs = {"scope": "all three native evidence captures; source acquisition is separate", "runs": runs,
             "by_category": dict(all_costs), "total": sum(all_costs.values()), "limits": limits,
             "local_measurement_costs": dict(local_costs), "posthoc_readonly_db_queries": posthoc_queries,
             "readonly_db_queries_total": local_costs.get("readonly_database_queries", 0) + posthoc_queries,
             "provider_internal_database_and_callback_costs": "NOT_MEASURED",
             "by_operation": [{"category": key[0], "operation": key[1], "requests": value} for key, value in sorted(operations.items())]}
    (ROOT / "COST_ACCOUNTING.json").write_text(json.dumps(costs, indent=2), encoding="utf-8")
    with (ROOT / "EVENT_WITNESS.jsonl").open("a", encoding="utf-8") as stream:
        for row in supplementary_events:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"supplements_pass": True, "http_total": costs["total"], "acceptance_rows": root_audit["combined_acceptance_rows"],
                      "four_test_accounts_deleted": True, "budget_respected": True}))


if __name__ == "__main__":
    main()
    aggregate_supplements()
