"""Additional finite algebra/distribution checks, not a proof or priority test."""
import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
from algebra import Field, multiply, rank, left_inverse

REV = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); args = p.parse_args()
    out = (REV / args.out).resolve()
    if not out.is_relative_to(REV): raise ValueError('revision output only')
    out.mkdir(parents=True, exist_ok=False); cases = []
    def record(name, actual, expected):
        assert actual == expected, (name, actual, expected)
        cases.append({'case': name, 'actual': actual, 'expected': expected, 'pass': True})
    count = 0
    for q in (3, 4):
        f = Field(q)
        for d in (2, 3):
            identity = [[int(i == j) for j in range(d)] for i in range(d)]
            for w in product(range(q), repeat=d):
                for i in range(d):
                    if not w[i]: continue
                    t = [row[:] for row in identity]
                    for k in range(d): t[k][i] = w[k]
                    ti = left_inverse(f, t)
                    for lam in range(2, q):
                        di = [row[:] for row in identity]; di[i][i] = lam
                        di_inv = left_inverse(f, di)
                        k = multiply(f, multiply(f, multiply(f, t, di), ti), di_inv)
                        ki = left_inverse(f, k)
                        for j in range(d):
                            if j == i or not w[j]: continue
                            for mu in range(2, q):
                                dj = [row[:] for row in identity]; dj[j][j] = mu
                                actual = multiply(f, multiply(f, multiply(f, dj, k), left_inverse(f, dj)), ki)
                                expected = [row[:] for row in identity]
                                expected[j][i] = f.mul(f.add(mu, f.neg(1)), k[j][i])
                                assert actual == expected and expected[j][i] != 0
                                count += 1
        v = [[1,0,1],[0,1,1]]
        masks = []
        for values in product(range(q), repeat=4):
            matrix = [list(values[:2]), list(values[2:])]
            if rank(f, matrix) == 2: masks.append(matrix)
        for support in ((), (0,), (1,), (2,), (0,1), (0,2), (1,2)):
            laws = []
            for amps in product(range(1, q), repeat=len(support)):
                distribution = Counter()
                for matrix in masks:
                    y = multiply(f, matrix, [[row[i] for i in support] for row in v])
                    distribution[tuple(f.mul(y[r][c], amps[c]) for r in range(2) for c in range(len(support)))] += 1
                    assert all(any(y[r][c] for r in range(2)) for c in range(len(support)))
                laws.append(distribution)
            record(f'all_GL_frames_q{q}_support{support}', all(x == laws[0] for x in laws), True)
        record(f'GL2_size_q{q}', len(masks), (q*q-1)*(q*q-q))
    record('explicit_transvection_identities', count > 0, True)
    f = Field(3); b = [[1,1],[1,2]]; z = [[1,1]]
    wrong = multiply(f, z, b); correct_m = multiply(f, z, left_inverse(f, b))
    record('missing_pullback_erases_coordinate', wrong, [[2,0]])
    record('correct_pullback_preserves', multiply(f, correct_m, b), z)
    record('ambient_extension_not_invariant', Counter((x,x) for x in (1,2)) == Counter((f.mul(2,x),x) for x in (1,2)), False)
    single_laws = []
    for col in (1,1,2):
        single_laws.extend([Counter(f.mul(f.mul(rho,col),a) for rho in (1,2)) for a in (1,2)])
    record('singleton_triangle_one_row_privacy', all(x == single_laws[0] for x in single_laws), True)
    result = {'pass': True, 'identity_instances': count, 'assertion_records': len(cases),
              'fields': [3,4], 'identity_dimensions': [2,3],
              'distribution_scope': 'all GL2 masks, all independent triangle supports, all nonzero amplitudes',
              'proof_or_priority_claim': False}
    (out / 'checks.json').write_text(json.dumps(cases, indent=2))
    (out / 'summary.json').write_text(json.dumps(result, indent=2)); print(json.dumps(result))


if __name__ == '__main__': main()
