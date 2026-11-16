"""Finite tree/label checks only; no candidate protocol implementation.

Prints actual inputs, expected values and observed values as JSON.
Reuses the frozen R2 mathematical audit through a separate subprocess.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

R2_SCRIPT = Path(r"D:\毕业设计\crypto_expiring_ue_proof_r2\mathematical_audit.py")


def preorder(depth):
    result = []

    def visit(word):
        result.append(word)
        if len(word) < depth:
            visit(word + "1")
            visit(word + "2")

    visit("")
    return result


def gamma(word):
    return {word} | {word[:i] + "2" for i, b in enumerate(word) if b == "1"}


def epoch(word, lam):
    return 1 + sum(1 + (2 ** (lam - i) - 1) * (int(b) - 1)
                   for i, b in enumerate(word, 1))


lam = 4
nodes = preorder(lam - 1)
labels = {i + 1: node for i, node in enumerate(nodes)}


def coverage(frontier):
    return {i for i, node in labels.items()
            if any(node.startswith(root) for root in frontier)}


def index_set(e, tau):
    return gamma(labels[e]) - gamma(labels[tau + 1])


checks = []


def check(name, inputs, expected, actual):
    checks.append({"id": name, "input": inputs, "expected": expected,
                   "actual": actual, "pass": expected == actual})


expected_labels = ["", "1", "11", "111", "112", "12", "121", "122",
                   "2", "21", "211", "212", "22", "221", "222"]
check("preorder", {"lambda": lam}, expected_labels, nodes)
check("inverse_encoding_all_nodes", {"lambda": lam, "nodes": nodes},
      list(range(1, 16)), [epoch(node, lam) for node in nodes])
check("I_2_2", {"e": 2, "tau": 2}, ["1"], sorted(index_set(2, 2)))
check("I_2_3", {"e": 2, "tau": 3}, ["1"], sorted(index_set(2, 3)))
check("range_difference_2_2", {"left": "Gamma_1", "right": "Gamma_11"},
      [2], sorted(coverage(gamma("1")) - coverage(gamma("11"))))
check("range_difference_2_3", {"left": "Gamma_1", "right": "Gamma_111"},
      [2, 3], sorted(coverage(gamma("1")) - coverage(gamma("111"))))
check("literal_node_coverage", {"frontier": ["1"]},
      list(range(2, 9)), sorted(coverage({"1"})))
check("root_children_indices", {"parent": "", "lambda": lam},
      [2, 9], [epoch("1", lam), epoch("2", lam)])
check("root_printed_right_label_mismatch", {"e": 1, "printed_index": 3},
      {"actual_right": "2", "printed_label": "11", "equal": False},
      {"actual_right": "2", "printed_label": labels[3], "equal": "2" == labels[3]})
check("node1_children_indices", {"parent": "1", "lambda": lam},
      [3, 6], [epoch("11", lam), epoch("12", lam)])
check("node11_e_plus_2_special_case", {"parent": "11", "lambda": lam},
      5, epoch("112", lam))
check("update_target_3_3", {"e": 3, "tau": 3},
      ["11"], sorted(index_set(3, 3)))
check("printed_full_return_extra_nodes", {"source_return": "Gamma_11", "target": "I(3,3)"},
      ["12", "2"], sorted(gamma("11") - index_set(3, 3)))
check("aligned_long_window_2_8", {"e": 2, "tau": 8},
      list(range(2, 9)), sorted(coverage(index_set(2, 8))))
check("aligned_long_window_3_8", {"e": 3, "tau": 8},
      ["11", "12"], sorted(index_set(3, 8)))
check("empty_window_guess", {"e_star": 2, "tau": 2, "L": 15},
      [], [i for i in range(1, 16) if 2 < i <= 2])
check("incoming_token_matches_challenge", {"Delta2_label": labels[2], "I_2_3": sorted(index_set(2, 3))},
      True, labels[2] in index_set(2, 3))

result = subprocess.run([sys.executable, str(R2_SCRIPT)],
                        capture_output=True, check=False)
prior = json.loads(result.stdout.decode("utf-8"))
all_ok = all(c["pass"] for c in checks) and result.returncode == 0 and prior["all_pass"]
print(json.dumps({
    "kind": "FINITE_MATH_AUDIT_NOT_CRYPTO_IMPLEMENTATION",
    "lambda": lam,
    "new_checks": checks,
    "R2_reuse": {"script": str(R2_SCRIPT),
                 "sha256": hashlib.sha256(R2_SCRIPT.read_bytes()).hexdigest(),
                 "process_exit_code": result.returncode,
                 "stderr": result.stderr.decode("utf-8", errors="replace"),
                 "raw_result": prior},
    "counts": {"new": len(checks), "new_pass": sum(c["pass"] for c in checks),
               "inherited": len(prior["checks"]),
               "inherited_pass": sum(c["pass"] for c in prior["checks"])},
    "all_pass": all_ok,
    "proof_scope": "Finite tree and set equalities; general R3-RANGE and pairing calculations are paper proofs",
    "cryptographic_security_proved_by_program": False,
}, ensure_ascii=False, indent=2))
