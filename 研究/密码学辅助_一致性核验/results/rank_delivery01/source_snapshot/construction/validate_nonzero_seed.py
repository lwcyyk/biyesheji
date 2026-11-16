"""Exhaustive promise-domain checks and exact full-opened-transcript distributions."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from field import Field
import reference
from kernel import decode
from nonzero_seed import attempt, sample


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    f = Field(4); labels = f.labels(4)
    table = reference.sparse_table(4, 2, labels, 4, f.modulus)
    seeds = [(a, b) for a, b in product(range(16), repeat=2) if a or b]
    vectors = []; exact_checks = candidate_checks = 0
    for size in range(3):
        for support in combinations(range(4), size):
            for nonzero_values in product(range(1, 16), repeat=size):
                d = [0] * 4
                for i, value in zip(support, nonzero_values): d[i] = value
                s = reference.moments(d, labels, 5, 4, f.modulus)
                counts = Counter()
                for seed_index, (r0, r1) in enumerate(seeds):
                    u = [f.mul(r0, s[j]) ^ f.mul(r1, s[j + 1]) for j in range(4)]
                    masked = table[tuple(u)]
                    proposed = [i for i, value in enumerate(masked) if value]
                    omitted = set(support) - set(proposed)
                    assert len(omitted) <= 1 and set(proposed) <= set(support)
                    remaining = f.total(value for i, value in enumerate(d) if i not in proposed)
                    accepted = remaining == 0
                    assert accepted == (proposed == list(support))
                    counts['accept' if accepted else 'retry'] += 1; exact_checks += 1
                    if seed_index % 17 == 0:
                        actual = attempt(f, d, labels, [r0, r1], blind=7)
                        assert actual['moments'] == u and actual['candidate'] == proposed
                        assert actual['status'] == ('ACCEPT' if accepted else 'RETRY')
                        assert actual['online_products'] == 6
                        candidate_checks += 1
                assert counts['retry'] == size * 15
                vectors.append({'residuals': d, 'support': list(support), 'counts': dict(counts),
                                'retry_probability': str(Fraction(counts['retry'], 255))})
    privacy = []
    def distribution(d):
        c = Counter()
        for seed in seeds:
            for blind in range(1, 16):
                actual = attempt(f, d, labels, list(seed), blind)
                c[(tuple(actual['moments']), actual['remainder_opening'])] += 1
        return c
    for left, right in [([1, 2, 0, 0], [7, 13, 0, 0]), ([0, 1, 0, 0], [0, 9, 0, 0])]:
        a, b = distribution(left), distribution(right)
        assert a == b
        privacy.append({'left': left, 'right': right, 'seed_and_blind_tapes_each': 3825,
                        'exact_full_opened_distribution_equal': True, 'distinct_transcripts': len(a),
                        'digest': hashlib.sha256(repr(sorted(a.items())).encode()).hexdigest()})
    # Rejection sampling uses a genuine uniform pair, including vectors where
    # exactly one coefficient is zero. Only the zero vector is excluded.
    chosen = sample(f, [(0, 0, 0), (0, 5, 0)], [3, 7])
    assert chosen['seed'] == [0, 5] and len(chosen['openings']) == 2
    assert chosen['online_products'] == 6 and chosen['random_triples'] == 2
    exhausted = sample(f, [(0, 0, 0), (0, 0, 0)], [3, 7])
    assert exhausted['seed'] is None
    for a, b in seeds:
        result = sample(f, [(a, b, f.mul(a, b))], [1])
        assert result['seed'] == [a, b] and result['online_products'] == 3
    # Without zero-seed rejection, two equal omitted errors cancel in E_0.
    bad = {'residuals': [1, 1, 0, 0], 'seed': [0, 0], 'public_moments': [0, 0, 0, 0],
           'candidate': [], 'remaining_sum': 0, 'unsafe_fixed_sum_accepts': True}
    try: attempt(f, bad['residuals'], labels, bad['seed'])
    except ValueError: bad['safe_candidate_rejects_seed'] = True
    else: raise AssertionError('zero seed allowed')
    (out / 'vectors.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in vectors))
    (out / 'privacy.json').write_text(json.dumps(privacy, indent=2))
    (out / 'counterexample.json').write_text(json.dumps(bad, indent=2))
    # Exact formula combines finite counts with independence; no claim to have
    # enumerated the enormous Cartesian product of two complete sampler tapes.
    budgets = []
    generation_fail = Fraction(1, 16 ** 4)
    for size in range(3):
        miss = Fraction(size, 17); continuation = (1 - generation_fail) * miss
        inconclusive = generation_fail * (1 + continuation) + continuation ** 2
        budgets.append({'support_size': size, 'T': 2, 'A': 2,
                        'generation_failure': str(generation_fail), 'mask_omission': str(miss),
                        'derived_inconclusive': str(inconclusive), 'wrong_acceptance': '0'})
    summary = {'pass': True, 'q': 16, 'n': 4, 'k': 2, 'sparse_vectors': len(vectors),
               'exhaustive_vector_seed_pairs': exact_checks, 'candidate_differential_checks': candidate_checks,
               'privacy_tapes': 4 * 3825, 'sampler_nonzero_pairs_checked': 255,
               'finite_budget_formulas': budgets,
               'scope': 'sparse promise only; global sparse gate and malicious backend errors remain',
               'source_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [Path(__file__), Path(__file__).with_name('nonzero_seed.py'), ROOT / 'kernel.py', ROOT / 'reference.py']}}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: v for k, v in summary.items() if k not in ('source_hashes', 'finite_budget_formulas')}))


if __name__ == '__main__': main()
