"""Integer and rational arithmetic checks only. No masking protocol or LP solver."""
from pathlib import Path
from fractions import Fraction
from math import comb, isqrt
import json

ROOT = Path(__file__).resolve().parent


def rational(value):
    return {'numerator': value.numerator, 'denominator': value.denominator,
            'decimal': float(value)}


primes = {}
for value in [401, 1031, 4099, 8191]:
    remainders = [[divisor, value % divisor] for divisor in range(2, isqrt(value) + 1)]
    primes[str(value)] = {'max_divisor': isqrt(value), 'remainders': remainders,
                          'prime': all(remainder for divisor, remainder in remainders)}

gaps = []
for q in [4096, 4099]:
    n = 8
    lower_two = Fraction(1, 400 * (q * q + 1))
    upper_three = Fraction(n, (q + 1) * (q * q + 1))
    gap_formula = Fraction(q + 1 - 400 * n, 400 * (q + 1) * (q * q + 1))
    gaps.append({'q': q, 'n': n, 'd': 4, 'k': 4,
                 'lower_two': rational(lower_two), 'upper_three': rational(upper_three),
                 'gap': rational(lower_two - upper_three),
                 'midpoint_tolerance': rational((lower_two + upper_three) / 2),
                 'large_field_condition': q >= 16 * n * n,
                 'strict_gap': lower_two > upper_three,
                 'gap_identity': lower_two - upper_three == gap_formula})

counts = []
for q, n in [(4096, 5), (1031, 3)]:
    d = n - 1
    inclusion_exclusion = sum((-1) ** j * comb(n, j) * q ** max(d - j, 0)
                              for j in range(n + 1))
    parity_count = Fraction((q - 1) ** n + (-1) ** n * (q - 1), q)
    counts.append({'q': q, 'n': n, 'd': d, 'inclusion_exclusion': inclusion_exclusion,
                   'parity_count': rational(parity_count),
                   'equal': inclusion_exclusion == parity_count,
                   'delta_full_support': rational(1 - Fraction(inclusion_exclusion, (q - 1) ** n))})

result = {'scope': 'Finite integer/formula checks only. General proofs remain handwritten.',
          'primes': primes, 'strict_rank_gaps': gaps, 'full_weight_counts': counts,
          'not_run': ['finite-field mask enumeration', 'LP optimization', 'MPC', 'machine theorem proof']}
(ROOT / 'ARITHMETIC_CHECKS.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
assert all(item['prime'] for item in primes.values())
assert all(item['strict_gap'] and item['gap_identity'] and item['large_field_condition'] for item in gaps)
assert all(item['equal'] for item in counts)
print(json.dumps({'prime_checks': len(primes), 'strict_gap_checks': len(gaps),
                  'count_identity_checks': len(counts), 'failures': 0}, ensure_ascii=False))
