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
    for key in ("source_lemma_ref", "query_ref", "identifier_receipt_ref"):
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
            if facts.get("origin_bound") is True:
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
