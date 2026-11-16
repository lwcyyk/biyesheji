"""Exact one-attempt old-protocol probabilities; no gate error for sparse inputs.

Tests sharpen the strong older comparator instead of using its loose union bound.
"""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import product
from math import gcd
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from field import Field


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    args = p.parse_args(); out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    f = Field(4); labels = f.labels(4)
    rows = []
    for residuals in ([1, 1, 0, 0], [1, 0, 0, 1], [1, 0, 0, 2], [0, 7, 0, 0]):
        support = [i for i, x in enumerate(residuals) if x]
        count = Counter(); total = 0
        for r0, r1 in product(range(16), repeat=2):
            omitted = [i for i in support if r0 ^ f.mul(r1, labels[i]) == 0]
            remaining = [x if i in omitted else 0 for i, x in enumerate(residuals)]
            for x0, x1 in product(range(1, 16), repeat=2):
                total += 1
                verified_zero = f.poly(remaining, x0) == f.poly(remaining, x1) == 0
                count['bad' if omitted and verified_zero else 'retry' if omitted else 'correct'] += 1
        root_count = sum(f.poly(residuals, x) == 0 for x in range(1, 16))
        p_bad = Fraction(root_count ** 2, 16 ** 2 * 15 ** 2) if len(support) == 2 else Fraction(0)
        p_correct = Fraction(15, 16) ** len(support)
        p_retry = 1 - p_bad - p_correct
        assert Fraction(count['bad'], total) == p_bad
        assert Fraction(count['correct'], total) == p_correct
        assert Fraction(count['retry'], total) == p_retry
        if len(support) == 2: assert root_count in (0, gcd(support[1] - support[0], 15))
        assert p_bad * (1 + p_retry) + p_correct * (1 + p_retry) + p_retry ** 2 == 1
        rows.append({'residuals': residuals, 'mask_and_challenge_tuples': total,
                     'counts': dict(count), 'nonzero_roots': root_count,
                     'single_attempt_bad': str(p_bad), 'single_attempt_correct': str(p_correct),
                     'single_attempt_retry': str(p_retry), 'two_attempt_bad': str(p_bad * (1 + p_retry)),
                     'two_attempt_inconclusive': str(p_retry ** 2), 'pass': True})
    summary = {'pass': True, 'cases': rows, 'tuples_enumerated': sum(x['mask_and_challenge_tuples'] for x in rows),
               'scope': 'sparse k=2 old diagnosis only, exact ideal arithmetic; gate/backend not included',
               'result': 'old sparse false acceptance is zero for s<=1, and O(q^-4) for fixed index gap at s=2'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__': main()
