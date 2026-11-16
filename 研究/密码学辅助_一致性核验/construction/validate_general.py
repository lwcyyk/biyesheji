"""Repeatable finite checks for the general masking layer, not a security proof."""
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import sys
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from field import Field
from kernel import IdealArithmetic, middle_product_five, decode
import reference
from general_mask import middle_product, mask_moments, transforms


def direct(r, s, bits, modulus):
    result = []
    for j in range(2 * len(r)):
        value = 0
        for a in range(len(r)): value ^= reference.mul(r[a], s[j + a], bits, modulus)
        result.append(value)
    return result


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    rng = random.Random(21603); cases = []; failures = []
    for bits in (4, 8, 128):
        f = Field(bits)
        for k in range(1, 6):
            # Every bilinear basis tensor, then genuinely non-binary coefficients.
            vectors = []
            for i, j in product(range(k), range(3 * k - 1)):
                r = [0] * k; s = [0] * (3 * k - 1); r[i] = s[j] = 1
                vectors.append((r, s, 'complete_bilinear_basis'))
            for _ in range(24):
                vectors.append(([rng.randrange(f.q) for _ in range(k)],
                                [rng.randrange(f.q) for _ in range(3 * k - 1)], 'seeded'))
            for r, s, kind in vectors:
                ar = IdealArithmetic(f); actual = middle_product(ar, r, s)
                expected = direct(r, s, bits, f.modulus)
                record = {'bits': bits, 'k': k, 'kind': kind, 'r': r, 's': s,
                          'actual': actual, 'expected': expected, 'products': ar.products}
                record['pass'] = actual == expected and ar.products == 3 * k - 1
                if k == 2:
                    old_ar = IdealArithmetic(f)
                    record['matches_existing_five_product'] = actual == middle_product_five(old_ar, r, s)
                    record['pass'] &= record['matches_existing_five_product']
                cases.append(record)
                if not record['pass']: failures.append(record)
    privacy = []
    f = Field(4); labels = f.labels(5); k = 3; support = [0, 2, 4]
    # All 4096 mask coefficients for each of three same-support amplitudes.
    # Coordinate weights suffice: the public moment map is deterministic.
    distributions = []
    for amplitudes in ([1, 1, 1], [2, 7, 13], [15, 3, 10]):
        distribution = Counter()
        for mask in product(range(f.q), repeat=k):
            weights = tuple(f.mul(d, f.poly(mask, labels[i])) for i, d in zip(support, amplitudes))
            distribution[weights] += 1
        distributions.append(distribution)
        row = {'bits': 4, 'k': 3, 'support': support, 'amplitudes': amplitudes,
               'mask_tuples': f.q ** k, 'distinct_weight_vectors': len(distribution),
               'uniform': len(distribution) == f.q ** k and set(distribution.values()) == {1}}
        privacy.append(row)
        if not row['uniform']: failures.append(row)
    assert all(d == distributions[0] for d in distributions)
    # k=3 integrated masking + public decoder, including adversarially zeroing masks.
    decoded_cases = []
    d = [9, 0, 11, 0, 7]
    masks = [[0, 0, 0], [1, 0, 0], [labels[0], 1, 0]] + [
        [rng.randrange(16) for _ in range(k)] for _ in range(100)]
    for mask in masks:
        ar = IdealArithmetic(f); u = mask_moments(ar, d, labels, mask)
        weighted = []
        for value, label in zip(d, labels):
            r_at = 0
            for j, coefficient in enumerate(mask):
                r_at ^= reference.mul(coefficient, reference.power(label, j, 4, f.modulus), 4, f.modulus)
            weighted.append(reference.mul(value, r_at, 4, f.modulus))
        expected_u = reference.moments(weighted, labels, 6, 4, f.modulus)
        expected_support = [i for i, value in enumerate(weighted) if value]
        actual_support = decode(f, u, labels, k)
        record = {'d': d, 'mask': mask, 'actual_moments': u, 'expected_moments': expected_u,
                  'masked_support': expected_support, 'decoded': actual_support,
                  'full_support': support, 'requires_remainder_check': expected_support != support,
                  'pass': u == expected_u and expected_support == actual_support and ar.products == 8}
        decoded_cases.append(record)
        if not record['pass']: failures.append(record)
    for name, records in [('bilinear', cases), ('privacy', privacy), ('decoding', decoded_cases)]:
        (out / f'{name}.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in records))
    zero_free = []
    for threshold in (2, 3, 4):
        count = zeros = 0
        for mask in product(range(16), repeat=threshold):
            evaluations = [f.poly(mask, label) for label in labels[:threshold + 1]]
            if all(evaluations[:threshold]):
                count += 1; zeros += int(evaluations[threshold] == 0)
        expected_count = 15 ** threshold
        expected_zeros = (15 ** threshold + (-1) ** threshold * 15) // 16
        row = {'k': threshold, 'q': 16, 'mask_tuples': 16 ** threshold,
               'nonzero_at_first_k': count, 'zero_at_next': zeros,
               'conditional_probability': str(Fraction(zeros, count)),
               'expected_count': expected_count, 'expected_zeros': expected_zeros,
               'pass': count == expected_count and zeros == expected_zeros and zeros > 0}
        zero_free.append(row)
        if not row['pass']: failures.append(row)
    (out / 'zero_free_obstruction.json').write_text(json.dumps(zero_free, indent=2) + '\n')
    malformed = []
    for name, call in [
        ('empty', lambda: middle_product(IdealArithmetic(f), [], [])),
        ('wrong_length', lambda: middle_product(IdealArithmetic(f), [1, 2], [1, 2])),
        ('boolean_coefficient', lambda: middle_product(IdealArithmetic(f), [True], [1, 2])),
        ('boolean_cached_threshold', lambda: transforms(4, True)),
        ('insufficient_field', lambda: transforms(4, 6)),
        ('duplicate_labels', lambda: mask_moments(IdealArithmetic(f), [1, 2, 3], [1, 1, 2], [1, 2])),
    ]:
        try:
            call(); passed = False
        except ValueError:
            passed = True
        row = {'case': name, 'rejected': passed}; malformed.append(row)
        if not passed: failures.append(row)
    (out / 'malformed.json').write_text(json.dumps(malformed, indent=2) + '\n')
    # Tensor flattening has one nonzero disjoint anti-diagonal per s_l.
    flattening = [{'k': k, 'nonempty_disjoint_antidiagonals': 3 * k - 1,
                   'witness_pairs': [[max(0, l - (2 * k - 1)),
                                      l - max(0, l - (2 * k - 1))]
                                     for l in range(3 * k - 1)]} for k in range(1, 6)]
    summary = {'pass': not failures, 'failure_count': len(failures),
               'bilinear_cases': len(cases), 'decoding_cases': len(decoded_cases),
               'mask_weight_evaluations': 3 * 16 ** 3, 'flattening_witnesses': flattening,
               'zero_free_mask_tuples': sum(16 ** k for k in (2, 3, 4)),
               'malformed_rejections': sum(x['rejected'] for x in malformed),
               'scope': 'mask layer k=1..5, fields 4/8/128; k=3 privacy GF16; NOT full k>2 active MPC',
               'source_hashes': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in [Path(__file__), Path(__file__).with_name('general_mask.py'),
                                              ROOT / 'field.py', ROOT / 'kernel.py', ROOT / 'reference.py']}}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (out / 'failures.json').write_text(json.dumps(failures, indent=2) + '\n')
    print(json.dumps({key: value for key, value in summary.items() if key not in ('source_hashes', 'flattening_witnesses')}))
    if failures: raise SystemExit(1)


if __name__ == '__main__': main()
