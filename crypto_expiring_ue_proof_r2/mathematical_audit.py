"""Offline finite checks of paper equations; no encryption/protocol implementation.

Usage: python mathematical_audit.py
Only prints JSON. The analytic proofs remain in the Markdown reports.
"""
import json
from fractions import Fraction


def frontier(word):
    return {word} | {
        word[:index] + "2"
        for index, digit in enumerate(word)
        if digit == "1"
    }


def label(epoch, depth=3):
    nodes = []

    def preorder(word):
        nodes.append(word)
        if len(word) < depth:
            preorder(word + "1")
            preorder(word + "2")

    preorder("")
    return nodes[epoch - 1]


labels = {e: label(e) for e in range(1, 5)}
sets = {e: frontier(labels[e]) for e in labels}
index_22 = sets[2] - sets[3]
index_23 = sets[2] - sets[4]
tests = [
    {"id": "a1_to_a4", "pass": list(labels.values()) == ["", "1", "11", "111"]},
    {"id": "frontier_1", "pass": sets[2] == {"1", "2"}},
    {"id": "frontier_11", "pass": sets[3] == {"11", "12", "2"}},
    {"id": "frontier_111", "pass": sets[4] == {"111", "112", "12", "2"}},
    {"id": "I_2_2", "pass": index_22 == {"1"}},
    {"id": "I_2_3_same", "pass": index_23 == index_22},
    {"id": "incoming_token_prefix_counterexample", "pass": labels[2] in index_23},
]
p = 7
unit = list(range(1, p))
shifted = {x: Fraction(sum((1 + y) % p == x for y in unit), p - 1) for x in range(p)}
fresh = {x: Fraction(int(x != 0), p - 1) for x in range(p)}
tv = sum(abs(shifted[x] - fresh[x]) for x in range(p)) / 2
tests.append({"id": "unit_sampler_shift_TV_p7", "pass": tv == Fraction(1, p - 1)})
print(json.dumps({
    "kind": "FINITE_COMBINATORIAL_AUDIT_ONLY",
    "protocol_implementation": False,
    "labels": labels,
    "frontiers": {e: sorted(v) for e, v in sets.items()},
    "I_2_2": sorted(index_22), "I_2_3": sorted(index_23),
    "scalar_TV_p7": str(tv),
    "checks": tests,
    "all_pass": all(test["pass"] for test in tests),
    "security_theorem_verified_by_program": False,
}, ensure_ascii=False, indent=2))
