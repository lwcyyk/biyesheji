"""Conditional G0/G9 closure receipts. No new cryptographic mechanism."""


REQUIRED = (
    "exact_authorized_read", "record_found", "origin_bound", "single_unknown_creator",
    "creation_paused", "A_revoked", "external_writers_excluded",
    "future_retry_excluded", "known_A_units_inactive", "B_preserved_after_disposal")


def make_receipt(target, facts, evidence):
    missing = [key for key in REQUIRED if facts.get(key) is not True]
    for key in ("actual_sends", "per_send_effect_bound", "observed_distinct_effects"):
        if type(facts.get(key)) is not int or facts[key] != 1:
            missing.append(key)
    if not evidence.get("source_lemma_ref"):
        missing.append("source_lemma_ref")
    if not evidence.get("query_ref"):
        missing.append("query_ref")
    if not evidence.get("identifier_receipt_ref"):
        missing.append("identifier_receipt_ref")
    remaining = None
    if facts.get("per_send_effect_bound") == 1 and facts.get("future_retry_excluded") is True and evidence.get("source_lemma_ref"):
        if facts.get("observed_distinct_effects") == 0 and facts.get("actual_sends") in {0, 1}:
            remaining = 1
        elif (facts.get("observed_distinct_effects") == facts.get("actual_sends") == 1
              and facts.get("record_found") is True and facts.get("origin_bound") is True):
            remaining = 0
    return {"schema": "native-attempt-closure/1", "target": target,
            "claim": "CLOSED" if not missing else "UNKNOWN", "facts": facts,
            "evidence": evidence, "missing": missing,
            "remaining_creation_bound": remaining,
            "completeness_scope": "one attempt, bounded effect saturation",
            "whole_account_enumeration_claimed": False,
            "handler_termination_claimed": False,
            "conditional_assumptions": ["source-faithful fixed Casdoor profile", "trusted registered creators and custody", "no other fixture/admin writers"],
            "remaining_obligations": [] if not missing else [target["rid"]]}
