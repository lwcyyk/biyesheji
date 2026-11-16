"""Finite attaining witnesses for the n-dependent minimax simulator bound.

For affine masks nonzero at n distinct points, two residual amplitudes,
and simulator told only support, optimal worst-case statistical error over
this class is (n-2)/(q-1). Mathematical minimax proof is in TIGHT_LEAKAGE_BOUND.md.
"""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import reference


def tv(first, second):
    n1, n2 = sum(first.values()), sum(second.values())
    return sum(abs(Fraction(first[x], n1) - Fraction(second[x], n2))
               for x in first.keys() | second.keys()) / 2


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated path')
    out.mkdir(parents=True, exist_ok=False)
    uniform = Counter({pair: 1 for pair in product(range(1, 16), repeat=2)})
    rows = []
    for n in range(2, 17):
        labels = list(range(n))  # Zero is a permitted evaluation point in this lemma.
        masks = []
        for r0, r1 in product(range(16), repeat=2):
            values = [r0 ^ reference.mul(r1, point, 4, 0x13) for point in labels]
            if all(values): masks.append(values)
        assert len(masks) == 15 * (17 - n)
        for amplitude in ((1, 1), (1, 2), (7, 12)):
            output = Counter((reference.mul(amplitude[0], z[0], 4, 0x13),
                              reference.mul(amplitude[1], z[1], 4, 0x13)) for z in masks)
            distance = tv(output, uniform); expected = Fraction(n - 2, 15)
            assert distance == expected
            rows.append({'q': 16, 'n': n, 'labels': labels, 'support': [0, 1],
                         'amplitudes': list(amplitude), 'legal_masks': len(masks),
                         'statistical_distance_to_uniform_simulator': str(distance),
                         'proven_minimax_formula': str(expected), 'pass': True})
    (out / 'attaining_instances.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    summary = {'pass': True, 'q': 16, 'n_range': [2, 16], 'distributions': len(rows),
               'coefficient_tuples_checked': 15 * 256,
               'result': 'attains (n-2)/(q-1)',
               'scope': 'uniform attaining distribution; arbitrary-distribution minimax relies on the written proof',
               'priority': 'UNVERIFIED_ORIGINALITY'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__': main()
