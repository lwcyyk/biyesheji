"""Checks full-weight polynomial counts underlying the general tight bound.

The count is the classical full-weight MDS code enumerator. No originality
claim for that enumerator; our written derivation uses elementary inclusion-exclusion.
"""
import argparse
from fractions import Fraction
from itertools import product
import json
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from field import Field


def full_weight_count(q, n, k):
    return sum((-1) ** j * comb(n, j) * (q ** (k - j) - 1) for j in range(k))


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated path')
    out.mkdir(parents=True, exist_ok=False)
    field = Field(4); rows = []; tuples_checked = 0
    for k in range(1, 5):
        counts = {n: 0 for n in range(k, 17)}
        for mask in product(range(16), repeat=k):
            tuples_checked += 1
            prefix = 0
            for point in range(16):
                if field.poly(mask, point) == 0: break
                prefix += 1
            for n in range(k, prefix + 1): counts[n] += 1
        for n, actual in counts.items():
            expected = full_weight_count(16, n, k)
            assert actual == expected and 0 < expected <= 15 ** k
            epsilon = 1 - Fraction(expected, 15 ** k)
            if k == 2: assert epsilon == Fraction(n - 2, 15)
            rows.append({'q': 16, 'n': n, 'k': k, 'full_weight_polynomials': actual,
                         'inclusion_exclusion_count': expected,
                         'optimal_worst_case_simulator_error': str(epsilon), 'pass': True})
    (out / 'counts.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in rows))
    summary = {'pass': True, 'parameter_pairs': len(rows), 'mask_tuples': tuples_checked,
               'q': 16, 'k_range': [1, 4], 'n_range': 'k..16',
               'scope': 'full-weight counts enumerated; minimax over all mask/simulator distributions is proved analytically',
               'priority': 'CLASSICAL_ENUMERATOR_PLUS_PROJECT_DERIVATION_NOT_VERIFIED_NOVELTY'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__': main()
