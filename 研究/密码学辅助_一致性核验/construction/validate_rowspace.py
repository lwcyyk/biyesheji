"""Finite exhaustive, distributional, differential and negative tests."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import random
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from field import Field
from kernel import IdealArithmetic
import reference
import rowspace as candidate
import rowspace_reference as independent


def tv(a, b):
    total_a, total_b = sum(a.values()), sum(b.values())
    return sum(abs(Fraction(a[x], total_a) - Fraction(b[x], total_b))
               for x in a.keys() | b.keys()) / 2


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    args = p.parse_args(); out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    f = Field(4); labels = f.labels(5); rng = random.Random(2161103)
    gl = []; sl = []
    for a, b, c, d in product(range(16), repeat=4):
        determinant = f.mul(a, d) ^ f.mul(b, c)
        if determinant:
            gl.append([[a, b], [c, d]])
            if determinant == 1: sl.append([[a, b], [c, d]])
    assert len(gl) == (256 - 1) * (256 - 16) == 61200 and len(sl) == 4080
    # Public-rank-one and rank-two distributions over ALL legal GL2 matrices.
    def distribution(values, matrices):
        s = reference.moments(values, labels, 4, 4, f.modulus)
        counts = Counter()
        for matrix in matrices:
            result = tuple(f.mul(row[0], s[j]) ^ f.mul(row[1], s[j + 1])
                           for row in matrix for j in range(3))
            counts[result] += 1
        return counts
    privacy = []
    for left, right, rank in [([1, 0, 0, 2, 0], [7, 0, 0, 13, 0], 2),
                               ([0, 1, 0, 0, 0], [0, 11, 0, 0, 0], 1)]:
        a, b = distribution(left, gl), distribution(right, gl)
        distance = tv(a, b)
        assert distance == 0
        expected_distinct = {1: 255, 2: 61200}[rank]
        assert len(a) == expected_distinct and len(set(a.values())) == 1
        privacy.append({'left': left, 'right': right, 'rank': rank,
                        'matrices_each': len(gl), 'distinct_outputs': len(a),
                        'each_output_count': next(iter(a.values())), 'TV': str(distance),
                        'distribution_sha256': hashlib.sha256(json.dumps(sorted(a.items())).encode()).hexdigest()})
    # Every <=2-sparse GF16 vector on four positions, six independent mask choices.
    sparse_checks = []; actual_trials = 0
    for size in range(3):
        for support in combinations(range(4), size):
            for values in product(range(1, 16), repeat=size):
                vector = [0] * 4
                for i, value in zip(support, values): vector[i] = value
                for matrix in [gl[0], gl[-1], [[1, 0], [0, 1]]] + [rng.choice(gl) for _ in range(3)]:
                    ar = IdealArithmetic(f)
                    c = candidate.encode(ar, vector, labels[:4], matrix)
                    ref_c = independent.encode(vector, labels[:4], matrix, 4, f.modulus)
                    got = candidate.decode(f, c, labels[:4])
                    ref_got = independent.decode2(c, labels[:4], 4, f.modulus)
                    assert c == ref_c and got == ref_got == list(support) and ar.products == 8
                    actual_trials += 1
                sparse_checks.append({'vector': vector, 'support': list(support), 'six_masks_pass': True})
    # k=1..4, including GF128. Not a full k>2 MPC implementation.
    general = []
    for bits in (4, 8, 128):
        field = Field(bits)
        for k in range(1, 5):
            points = field.labels(k + 2)
            for _ in range(16):
                while True:
                    m = [[rng.randrange(field.q) for j in range(k)] for i in range(k)]
                    if len(candidate.rref(field, m)[0]) == k: break
                support = sorted(rng.sample(range(k + 2), rng.randrange(k + 1)))
                values = [rng.randrange(1, field.q) if i in support else 0 for i in range(k + 2)]
                ar = IdealArithmetic(field); c = candidate.encode(ar, values, points, m)
                expected = independent.encode(values, points, m, bits, field.modulus)
                assert c == expected and candidate.decode(field, c, points) == support and ar.products == 2 * k * k
                general.append({'bits': bits, 'k': k, 'residuals': values, 'matrix': m,
                                'public_matrix': c, 'support': support, 'products': ar.products})
    # Arbitrary malformed public matrices, checked by an algebraically different decoder.
    decoder_cases = 0
    for x in product(range(4), repeat=6):
        matrix = [list(x[:3]), list(x[3:])]
        assert candidate.decode(f, matrix, labels) == independent.decode2(matrix, labels, 4, f.modulus)
        decoder_cases += 1
    # Security counterexamples, preserved rather than excluded from test inputs.
    counterexamples = []
    x, y = [1, 0, 0, 2, 0], [7, 0, 0, 13, 0]
    sl_tv = tv(distribution(x, sl), distribution(y, sl))
    assert sl_tv == 1
    counterexamples.append({'kind': 'SL2_NOT_GL2', 'inputs': [x, y], 'exact_TV': str(sl_tv),
                            'reason': 'fixed determinant exposes product of nonzero amplitudes'})
    singular = [[labels[0], 1], [0, 0]]
    c = candidate.encode(IdealArithmetic(f), [1, 0, 0, 0, 0], labels, singular, check_invertible=False)
    assert candidate.decode(f, c, labels) == []
    try:
        candidate.encode(IdealArithmetic(f), [1, 0, 0, 0, 0], labels, singular)
        raise AssertionError('singular mask accepted')
    except ValueError: pass
    counterexamples.append({'kind': 'SINGULAR_MASK_ERASES_FAILURE', 'mask': singular, 'public_matrix': c})
    # Dense vector deliberately has the same row space as a different sparse support.
    dense = [0, 0, 12, 5, 6]
    c = candidate.encode(IdealArithmetic(f), dense, labels, [[1, 0], [0, 1]])
    assert candidate.decode(f, c, labels) == [0, 1]
    gate_matrix = [[f.poly(dense, f.mul(f.power(3, r), 1)) for _ in range(3)] for r in range(3)]
    assert reference.determinant(gate_matrix, 4, f.modulus) == 0
    counterexamples.append({'kind': 'GATE_STILL_NEEDED_AND_HAS_RARE_ERRORS', 'residuals': dense,
        'gate_challenge_sets': [[1, 1, 1], [1, 1, 1]], 'true_support': [2, 3, 4],
        'incorrect_decoding_if_gate_passes': [0, 1], 'public_matrix_with_identity_mask': c})
    m = gl[113]
    c0 = candidate.encode(IdealArithmetic(f), [0, 1, 0, 0, 0], labels, m)
    c1 = candidate.encode(IdealArithmetic(f), [0, 9, 0, 0, 0], labels, m)
    recovered = next(f.mul(v1, f.inverse(v0)) for r0, r1 in zip(c0, c1)
                     for v0, v1 in zip(r0, r1) if v0)
    assert recovered == 9
    counterexamples.append({'kind': 'MATRIX_REUSE_LEAKS_RATIO', 'recovered_ratio': recovered})
    # Finite sampler failure, retry, and blinded-open distribution.
    valid, openings = candidate.choose_mask2(f, [singular, [[1, 0], [0, 1]]], [2, 7])
    assert valid == [[1, 0], [0, 1]] and openings == [0, 7]
    none, openings = candidate.choose_mask2(f, [singular, singular], [2, 7])
    assert none is None and openings == [0, 0]
    for determinant in range(1, 16):
        assert sorted(f.mul(determinant, rho) for rho in range(1, 16)) == list(range(1, 16))
    for name, records in [('privacy', privacy), ('sparse', sparse_checks), ('general', general), ('counterexamples', counterexamples)]:
        (out / f'{name}.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in records))
    summary = {'pass': True, 'sparse_vectors': len(sparse_checks), 'sparse_trials': actual_trials,
               'general_trials': len(general), 'decoder_matrices': decoder_cases,
               'privacy_GL2_matrix_evaluations': 4 * len(gl), 'counterexamples_retained': len(counterexamples),
               'GL2_size': len(gl), 'sampler_failure_single': str(1 - Fraction(len(gl), 16 ** 4)),
               'scope': 'finite clear algebra and exact distributions, not full malicious security',
               'source_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [Path(__file__), Path(__file__).with_name('rowspace.py'),
                             Path(__file__).with_name('rowspace_reference.py'), ROOT / 'field.py', ROOT / 'reference.py']}}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'source_hashes'}), flush=True)


if __name__ == '__main__': main()
