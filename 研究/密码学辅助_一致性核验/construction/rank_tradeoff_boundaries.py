"""Concrete necessity checks for the theorem's field/support assumptions."""
from itertools import product, combinations
from collections import Counter
from pathlib import Path
import argparse
import json
from rank_tradeoff_checks import SmallField
ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    # n=k: only one full-support basis, so diagonal invariance need not imply GL invariance.
    f = SmallField(4); seeds = [(z0, f.add(z0, z1)) for z0, z1 in product(range(1, 4), repeat=2)]
    baseline = Counter((x, f.add(x, y)) for x, y in seeds)
    for d0, d1 in product(range(1, 4), repeat=2):
        distribution = Counter((f.mul(d0, x), f.mul(d1, f.add(x, y))) for x, y in seeds)
        assert distribution == baseline and all(a and b for a, b in distribution)
    # q=2: for a general full-spark dictionary (not polynomial evaluation at
    # distinct F2 points), nonzero amplitudes have no variability.
    columns = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]
    for selected in combinations(columns, 3):
        for coefficients in product((0, 1), repeat=3):
            if any(coefficients):
                assert any(sum(c * v[j] for c, v in zip(coefficients, selected)) % 2 for j in range(3))
    evaluations = [sum(v) % 2 for v in columns]
    assert evaluations == [1] * 4
    result = {'pass': True,
              'n_equals_k': {'q': 4, 'n': 2, 'k': 2, 'r': 1, 'mask_count': len(seeds),
                             'perfect_amplitude_hiding': True, 'erasure_probability': 0,
                             'violates_rank_lower_bound_if_n_ge_k_plus_1_is_dropped': True},
              'q_equals_2': {'k': 3, 'n': 4, 'r': 1, 'dictionary': columns, 'mask': [1, 1, 1],
                            'all_columns_retained': True, 'amplitude_privacy_vacuous': True,
                            'note': 'general full-spark dictionary, not four distinct F2 evaluation points'},
              'scope': 'assumption counterexamples only'}
    (out / 'summary.json').write_text(json.dumps(result, indent=2)); print(json.dumps(result))


if __name__ == '__main__': main()
