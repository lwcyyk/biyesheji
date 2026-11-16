"""Independent checker for the bounded receipt predicates. Standard library only."""

import argparse
import hashlib
import json
from pathlib import Path


def check(receipt):
    if receipt.get("schema") != "native-attempt-closure/1":
        return {"status": "INVALID", "reason": "SCHEMA"}
    facts = receipt.get("facts", {})
    evidence = receipt.get("evidence", {})
    failures = []
    for key in ("exact_authorized_read", "record_found", "origin_bound", "single_unknown_creator",
                "creation_paused", "A_revoked", "external_writers_excluded", "future_retry_excluded",
                "known_A_units_inactive", "B_preserved_after_disposal"):
        if facts.get(key) is not True:failures.append(key)
    for key in ("actual_sends", "per_send_effect_bound", "observed_distinct_effects"):
        if type(facts.get(key)) is not int or facts[key] != 1:failures.append(key)
    origin = receipt.get("evidence_origin", "IDENTIFIER_POINT_READ")
    refs = ("source_lemma_ref", "query_ref", "enumeration_ref", "authorized_scope_ref") if origin == "AUTHORIZED_SCOPE_ENUMERATION" else ("source_lemma_ref", "query_ref", "identifier_receipt_ref")
    for key in refs:
        if not evidence.get(key):failures.append(key)
    target = receipt.get("target", {})
    if not all(target.get(k) for k in ("rid", "attempt_id", "grant_id", "generation", "account", "request_digest")):
        failures.append("TARGET_BINDING")
    if receipt.get("whole_account_enumeration_claimed") is not False:
        failures.append("EXCESS_SCOPE")
    if receipt.get("handler_termination_claimed") is not False:
        failures.append("UNSUPPORTED_HANDLER_TERMINATION")
    packet = evidence.get("packet")
    if receipt.get("claim") == "CLOSED" and not isinstance(packet, dict):
        failures.append("EVIDENCE_PACKET_REQUIRED")
    if packet is not None:
        raw = json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()
        if hashlib.sha256(raw).hexdigest() != evidence.get("packet_ref"):
            failures.append("PACKET_HASH")
        try:
            context, query, model = packet["context"], packet["query"], packet["model"]
            original = context["target"]
            if (target["attempt_id"] != original["attempt_id"] or target["request_digest"] != original["digest"]
                    or any(target[k] != original["origin"][k] for k in original["origin"])):
                failures.append("PACKET_TARGET")
            expected = {key: query.get(key, False) for key in ("exact_authorized_read", "record_found", "origin_bound")}
            expected.update(single_unknown_creator=context["window"]["unknown_creators_at_open"] == [target["rid"]],
                creation_paused=context["window"]["active"], A_revoked=context["A_revoked"],
                external_writers_excluded=model.get("external_writers_excluded") is True,
                future_retry_excluded=model.get("single_open_no_retry") is True,
                known_A_units_inactive=context["known_A_units_inactive"],
                B_preserved_after_disposal=context["B_preserved_after_disposal"], actual_sends=query.get("actual_sends", 0),
                per_send_effect_bound=model.get("per_send_effect_bound"), observed_distinct_effects=query.get("observed_distinct_effects", 0))
            if facts != expected:failures.append("PACKET_FACT_MISMATCH")
            metadata = query.get("identifier_receipt")
            if facts.get("origin_bound") is True and origin == "IDENTIFIER_POINT_READ":
                if not isinstance(metadata, dict):
                    failures.append("IDENTIFIER_RECEIPT_MISSING")
                else:
                    encoded = json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
                    if hashlib.sha256(encoded).hexdigest() != evidence.get("identifier_receipt_ref"):
                        failures.append("IDENTIFIER_HASH")
                    if (metadata.get("attempt_id") != target["attempt_id"] or metadata.get("digest") != target["request_digest"]
                            or metadata.get("origin") != original["origin"] or metadata.get("rid") != target["rid"]
                            or metadata.get("native_unit_id") != query.get("native_unit_id")):
                        failures.append("IDENTIFIER_SOURCE")
            if origin == "AUTHORIZED_SCOPE_ENUMERATION":
                for flag in ("collection_complete", "all_returned_rows_authorized", "registered_universe_complete", "organization_equal_filter"):
                    if query.get(flag) is not True:failures.append(flag)
                bound = query.get("record_upper_bound")
                capacity = query.get("page_capacity")
                budgets = model.get("approved_scope_budgets", [])
                if (type(bound) is not int or type(capacity) is not int or not 0 < bound <= capacity
                        or not budgets or any(type(n) is not int or n < 0 for n in budgets) or sum(budgets) != bound):
                    failures.append("ENUMERATION_BOUND")
                if query.get("page_number") != 1 or query.get("snapshot_scope") != "single_find_statement":
                    failures.append("ENUMERATION_SNAPSHOT")
                rows = query.get("returned_records", [])
                if query.get("organization") != model.get("organization") or any(r.get("organization") != model.get("organization") for r in rows):
                    failures.append("ENUMERATION_ORGANIZATION")
                if (any(r.get("application") != model.get("application_name") or r.get("user") not in model.get("account_names", []) for r in rows)
                        or model.get("account_id_by_name", {}).get(query.get("target_user")) != target["account"]
                        or model.get("client_id") != target.get("audience")):
                    failures.append("ENUMERATION_UNIVERSE")
                selected = sorted({r["unit_id"] for r in rows if r.get("user") == query.get("target_user") and r.get("application") == model.get("application_name")})
                candidates = sorted(set(selected) - set(query.get("known_input_ids", [])))
                if (selected != query.get("target_unit_ids") or candidates != query.get("candidate_unit_ids")
                        or len(candidates) != 1 or candidates[0] != query.get("selected_unit_id")):
                    failures.append("ENUMERATION_SELECTION")
                input_context = query.get("input_context", {})
                encoded = json.dumps(input_context, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
                if (hashlib.sha256(encoded).hexdigest() != query.get("input_context_ref")
                        or input_context.get("known_unit_ids") != query.get("known_input_ids")
                        or input_context.get("unknown_creators") != [target["rid"]]
                        or input_context.get("account_grant_count") != 2 or input_context.get("account_budget_total") != 20):
                    failures.append("ENUMERATION_SOURCE_CONTEXT")
            for item in model.get("source_files", []):
                if hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() != item["sha256"]:
                    failures.append("SOURCE_HASH")
        except (KeyError, OSError, TypeError):
            failures.append("PACKET_INPUT")
    if receipt.get("claim") == "CLOSED":
        if receipt.get("remaining_creation_bound") != 0 or receipt.get("remaining_obligations"):
            failures.append("INCONSISTENT_CLOSED_RESULT")
        return {"status": "VALID_CONDITIONAL_CLOSED" if not failures else "INVALID", "failures": failures,
                "scope": "registered facts and stated model assumptions; source lemma and deployment remain premises"}
    if receipt.get("claim") == "UNKNOWN":
        return {"status": "VALID_CONSERVATIVE_UNKNOWN", "unmet": failures}
    return {"status": "INVALID", "reason": "CLAIM"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt")
    parser.add_argument("--out")
    args = parser.parse_args()
    result = check(json.loads(Path(args.receipt).read_text()))
    if args.out:Path(args.out).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    raise SystemExit(1 if result["status"] == "INVALID" else 0)
