"""Exact finite witnesses for a restricted, tight leakage lower bound.

For input-independent affine polynomial masks nonzero at three field points,
the minimum worst-case TV between two-amplitude inputs equals 1/(q-2).
This is an independently derived project lemma, NOT a priority claim.
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
from field import Field
import reference


def distance(a, b):
    assert sum(a.values()) == sum(b.values())
    return Fraction(sum(abs(a[x] - b[x]) for x in a.keys() | b.keys()), 2 * sum(a.values()))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True)
    args = parser.parse_args(); out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    f = Field(4); labels = f.labels(3)
    # There are (q-1)(q-2) valid affine masks. Use a direct independent evaluator.
    mask_evaluations = []
    for r0, r1 in product(range(16), repeat=2):
        z = [r0 ^ reference.mul(r1, x, 4, f.modulus) for x in labels]
        if all(z): mask_evaluations.append((r0, r1, z))
    assert len(mask_evaluations) == 15 * 14
    support_pairs = [(0, 1), (0, 2), (1, 2)]
    rows = []; maxima = []
    for first, second in support_pairs:
        base = Counter((z[first], z[second]) for _, _, z in mask_evaluations)
        maximum = Fraction(0)
        for d0, d1 in product(range(1, 16), repeat=2):
            changed = Counter((reference.mul(d0, z[first], 4, f.modulus),
                               reference.mul(d1, z[second], 4, f.modulus))
                              for _, _, z in mask_evaluations)
            tv = distance(base, changed); maximum = max(maximum, tv)
            rows.append({'support': [first, second], 'amplitudes': [d0, d1],
                         'tv_against_unit_amplitudes': str(tv)})
            assert tv in (Fraction(0), Fraction(1, 14))
        assert maximum == Fraction(1, 14)
        maxima.append({'support': [first, second], 'maximum_tv': str(maximum)})
    # Exhibit a concrete distinguishing event: the originally forbidden ratio.
    first, second = support_pairs[0]
    ratios = Counter(f.mul(z[second], f.inverse(z[first])) for _, _, z in mask_evaluations)
    forbidden = next(x for x in range(1, 16) if x not in ratios)
    d0, d1 = 1, 2
    event_count = sum(f.mul(f.mul(d1, z[second]), f.inverse(f.mul(d0, z[first]))) == forbidden
                      for _, _, z in mask_evaluations)
    assert Fraction(event_count, len(mask_evaluations)) == Fraction(1, 14)
    (out / 'scalings.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in rows))
    summary = {'pass': True, 'q': 16, 'labels': labels, 'valid_masks': len(mask_evaluations),
               'scaling_comparisons': len(rows), 'maxima': maxima,
               'lower_bound': '1/(q-2)', 'achieved_at_q16': '1/14',
               'distinguishing_event': {'support': [first, second], 'ratio': forbidden,
                   'input0': [1, 1], 'input1': [d0, d1], 'probability0': '0',
                   'probability1': str(Fraction(event_count, len(mask_evaluations)))},
               'scope': 'uniform attaining distribution checked exhaustively; general minimax lower bound is mathematical, not brute-forced over all distributions',
               'priority': 'UNVERIFIED_ORIGINALITY'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__': main()
