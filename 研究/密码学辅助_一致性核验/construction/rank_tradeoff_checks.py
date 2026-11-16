"""Finite witnesses for a restricted mask-rank/privacy/erasure theorem.

Checks group generation, constructive elementary matrices, full-rank orbits,
exact erasure probabilities and a counterexample to too-short verification.
The arbitrary-field theorem is a written proof, not a consequence of sampling.
"""
from collections import deque
from fractions import Fraction
from itertools import product, combinations
from math import comb
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]


class SmallField:
    def __init__(self, q):
        if q not in (3, 4): raise ValueError('registered small field')
        self.q = q
    def add(self, a, b): return (a + b) % 3 if self.q == 3 else a ^ b
    def neg(self, a): return (-a) % 3 if self.q == 3 else a
    def mul(self, a, b):
        if self.q == 3: return a * b % 3
        result = 0
        while b:
            if b & 1: result ^= a
            b >>= 1; a <<= 1
            if a & 4: a ^= 7
        return result
    def power(self, a, exponent):
        value = 1
        for _ in range(exponent): value = self.mul(value, a)
        return value
    def inv(self, a):
        if not a: raise ValueError('zero inverse')
        return self.power(a, self.q - 2)
    def total(self, xs):
        value = 0
        for x in xs: value = self.add(value, x)
        return value


def identity(k): return [[int(i == j) for j in range(k)] for i in range(k)]
def mm(f, a, b):
    return [[f.total(f.mul(a[i][l], b[l][j]) for l in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]
def inverse(f, a):
    k = len(a); rows = [row[:] + eye for row, eye in zip(a, identity(k))]
    for c in range(k):
        p = next((i for i in range(c, k) if rows[i][c]), None)
        if p is None: raise ValueError('singular')
        rows[c], rows[p] = rows[p], rows[c]
        factor = f.inv(rows[c][c]); rows[c] = [f.mul(factor, x) for x in rows[c]]
        for i in range(k):
            if i == c: continue
            factor = rows[i][c]
            rows[i] = [f.add(x, f.neg(f.mul(factor, y))) for x, y in zip(rows[i], rows[c])]
    return [row[k:] for row in rows]
def diag(k, i, value):
    result = identity(k); result[i][i] = value; return result
def flat(matrix): return tuple(x for row in matrix for x in row)
def shaped(values, k): return [list(values[i:i + k]) for i in range(0, len(values), k)]


def omission_probability(q, k, r, s):
    result = Fraction(0)
    for j in range(1, min(s, k - r) + 1):
        intersection = Fraction(1)
        for h in range(j): intersection *= Fraction(q ** (k - r) - q ** h, q ** k - q ** h)
        result += (-1) ** (j + 1) * comb(s, j) * intersection
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True)
    args = parser.parse_args(); out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    rows = []; transvections = 0
    for q, k, ranks in ((3, 2, [1, 2]), (4, 2, [1, 2]), (4, 3, [1, 2])):
        f = SmallField(q); labels = list(range(k + 1))
        v = [[f.power(a, i) for a in labels] for i in range(k)]
        base = [row[:k] for row in v]; b_inv = inverse(f, base)
        normalized = mm(f, b_inv, v); c = [row[k] for row in normalized]
        assert all(c)
        generators = []
        for i in range(k):
            d = diag(k, i, 2); b = identity(k)
            for j in range(k): b[j][i] = c[j]
            a = mm(f, mm(f, b, d), inverse(f, b))
            generators += [('diagonal_' + str(i), d), ('support_switch_' + str(i), a)]
            u = mm(f, diag(k, i, f.inv(2)), a)
            for j in range(k):
                if j == i: continue
                dj = diag(k, j, 2)
                e0 = mm(f, mm(f, mm(f, dj, u), inverse(f, dj)), inverse(f, u))
                coefficient = f.mul(f.mul(f.add(2, f.neg(1)), f.add(2, f.neg(1))), f.mul(c[j], f.inv(c[i])))
                expected = identity(k); expected[j][i] = coefficient
                assert coefficient != 0 and e0 == expected
                for value in range(1, q):
                    scale = diag(k, j, f.mul(value, f.inv(coefficient)))
                    result = mm(f, mm(f, scale, e0), inverse(f, scale))
                    expected = identity(k); expected[j][i] = value
                    assert result == expected; transvections += 1
        for r in ranks:
            start = flat(identity(k)[:r]); visited = {start}; queue = deque([start])
            while queue:
                a = shaped(queue.popleft(), k)
                for _, generator in generators:
                    image = flat(mm(f, a, generator))
                    if image not in visited: visited.add(image); queue.append(image)
            expected_size = 1
            for i in range(r): expected_size *= q ** k - q ** i
            assert len(visited) == expected_size
            masks = [shaped(x, k) for x in sorted(visited)]
            erasures = []
            for mask in masks:
                evaluated = mm(f, mask, normalized)
                erased = {i for i in range(k + 1) if all(row[i] == 0 for row in evaluated)}
                assert len(erased) <= k - r
                erasures.append(erased)
            checks = []
            for s in range(1, k + 1):
                for support in combinations(range(k + 1), s):
                    actual = Fraction(sum(bool(set(support) & erased) for erased in erasures), len(masks))
                    expected = omission_probability(q, k, r, s)
                    assert actual == expected
                    checks.append({'support': support, 'probability': str(actual)})
            safe = {flat(m) for m, erased in zip(masks, erasures) if not erased}
            deviations = []
            if safe:
                for name, generator in generators:
                    moved = {flat(mm(f, shaped(x, k), generator)) for x in safe}
                    distance = 1 - Fraction(len(safe & moved), len(safe))
                    deviations.append({'generator': name, 'TV': str(distance)})
                if r < k: assert any(Fraction(x['TV']) > 0 for x in deviations)
                else: assert all(Fraction(x['TV']) == 0 for x in deviations)
            rows.append({'q': q, 'k': k, 'r': r, 'orbit_size': len(visited),
                         'expected_full_rank_matrices': expected_size, 'global_no_erasure_masks': len(safe),
                         'omission_checks': checks, 'conditioned_safe_distribution_deviations': deviations})
    # k=3,r=1: nonzero quadratic mask can erase two positions. One fixed
    # remainder sum is insufficient, whereas two Vandermonde moments detect it.
    f = SmallField(4); labels = [0, 1, 2, 3]; seed = [0, 1, 1]  # X(X-1), char 2
    values = [1, 1, 0, 0]
    masked = [f.mul(d, f.total(f.mul(c, f.power(a, j)) for j, c in enumerate(seed))) for d, a in zip(values, labels)]
    moments = [f.total(f.mul(d, f.power(a, j)) for d, a in zip(values, labels)) for j in range(2)]
    assert not any(masked) and moments[0] == 0 and moments[1] != 0
    counterexample = {'q': 4, 'k': 3, 'r': 1, 'labels': labels, 'seed': seed, 'values': values,
                      'masked': masked, 'remainder_moments': moments, 'one_moment_incorrectly_accepts': True}
    (out / 'orbits.json').write_text(json.dumps(rows, indent=2))
    (out / 'short_verifier_counterexample.json').write_text(json.dumps(counterexample, indent=2))
    summary = {'pass': True, 'parameter_profiles': len(rows), 'full_rank_matrices': sum(x['orbit_size'] for x in rows),
               'constructive_transvection_checks': transvections,
               'support_omission_checks': sum(len(x['omission_checks']) for x in rows),
               'scope': 'GF3/GF4 finite orbits; general-field necessity remains an analytic theorem',
               'priority': 'PROJECT_DERIVATION_NOT_YET_PRIORITY_VERIFIED'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2)); print(json.dumps(summary))


if __name__ == '__main__': main()
