"""Finite structure, distribution and independent-certificate checks."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import product, combinations
import json
from pathlib import Path
import hashlib
from structural_masks import SmallField, compile_dictionary, circuit_certificate, columns, rank, inverse, mm
from structural_checker import check_components, check_circuit
ROOT = Path(__file__).resolve().parents[1]


def tv(a, b):
    na, nb = sum(a.values()), sum(b.values())
    return sum(abs(Fraction(a[x], na) - Fraction(b[x], nb)) for x in a.keys() | b.keys()) / 2


def gl(f, b):
    result = []
    for entries in product(range(f.q), repeat=b * b):
        a = [list(entries[i * b:(i + 1) * b]) for i in range(b)]
        if rank(f, a) == b: result.append(a)
    return result


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    args = p.parse_args(); out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    profiles = [
        ('parallel_plus_coloop', [[1, 1, 0], [0, 0, 1]], 3, 1),
        ('triangle', [[1, 0, 1], [0, 1, 1]], 3, 2),
        ('connected_not_full_spark', [[1,0,0,1,0], [0,1,0,1,1], [0,0,1,0,1]], 3, 3),
        ('two_triangles', [[1,0,1,0,0,0], [0,1,1,0,0,0], [0,0,0,1,0,1], [0,0,0,0,1,1]], 3, 2),
        ('parallel_rank_one', [[1, 1, 2]], 3, 1),
        ('binary_extension_parallel', [[1, 1, 0], [0, 0, 1]], 4, 1),
        ('binary_extension_triangle', [[1, 0, 1], [0, 1, 1]], 4, 2)]
    records = []; certs = []; total_encodings = 0
    for name, v, q, expected_r in profiles:
        f = SmallField(q); cert = compile_dictionary(v, q)
        assert check_components(cert) and cert['minimum_mask_rows'] == expected_r
        k, n = len(v), len(v[0]); r = cert['minimum_mask_rows']
        inv_base = inverse(f, columns(v, cert['basis']))
        block_choices = [gl(f, block['rank']) for block in cert['components']]
        evaluations = []
        for choices in product(*block_choices):
            m = [[0] * k for _ in range(r)]
            for block, a in zip(cert['components'], choices):
                for i in range(block['rank']):
                    for j, axis in enumerate(block['basis_axes']): m[i][axis] = a[i][j]
            original_m = mm(f, m, inv_base); evaluated = mm(f, original_m, v)
            assert all(any(row[i] for row in evaluated) for i in range(n))
            evaluations.append(evaluated)
        assert len(evaluations) == cert['entropy_cardinality_lower_bound']
        bases = [s for s in combinations(range(n), k) if rank(f, columns(v, s)) == k]
        for basis in bases:
            first, second = Counter(), Counter()
            for ev in evaluations:
                first[tuple(ev[i][j] for i in range(r) for j in basis)] += 1
                second[tuple(f.mul(ev[i][j], 2 if j == basis[0] else 1) for i in range(r) for j in basis)] += 1
            assert first == second
            total_encodings += 2 * len(evaluations)
        bad = deepcopy(cert); bad['minimum_mask_rows'] = max(0, expected_r - 1)
        assert not check_components(bad)
        bad = deepcopy(cert); bad['basis'] = [cert['basis'][0]] * k
        if k > 1: assert not check_components(bad)
        bad = deepcopy(cert); bad['components'][0]['basis_axes'] = []
        assert not check_components(bad)
        certs.append({'profile': name, 'certificate': cert})
        records.append({'profile': name, 'q': q, 'rank': k, 'minimum_mask_rows': r,
                        'valid_masks_enumerated': len(evaluations), 'bases_checked': len(bases),
                        'all_columns_retained': True, 'same_support_amplitude_views_equal': True})
    # Parallel columns: a permitted dependent pair exposes its amplitude ratio
    # regardless of how many mask rows are added, when that column is retained.
    v = [[1, 1, 0], [0, 0, 1]]; q = 3; f = SmallField(q)
    policy = {'q': q, 'dictionary': v, 'admissible_supports': [[0, 1], [0, 2]],
              'policy_ref': 'synthetic-policy-01', 'world_ref': 'synthetic-world-01',
              'constraint_ref': 'amplitude-privacy-01',
              'amplitude_model': 'arbitrary_nonzero_per_position',
              'mask_model': 'input_independent_linear_observable'}
    conflict = circuit_certificate(v, q, [0, 1], [1, 2],
                **{k: policy[k] for k in ('policy_ref', 'world_ref', 'constraint_ref')})
    assert check_circuit(conflict, policy)
    mutations = []
    for key, value in [('coefficients', [1, 1]), ('support', [0, 2]),
                       ('world_ref', 'different-world'), ('constraint_ref', 'different-constraint')]:
        altered = deepcopy(conflict); altered[key] = value
        assert not check_circuit(altered, policy); mutations.append(key)
    strict = deepcopy(policy); strict['admissible_supports'] = [[0, 2], [1, 2]]
    assert not check_circuit(conflict, strict)
    correlated = deepcopy(policy); correlated['amplitude_model'] = 'equal_on_parallel_columns'
    assert not check_circuit(conflict, correlated)
    nonlinear = deepcopy(policy); nonlinear['mask_model'] = 'secret_nonlinear_postprocessing'
    assert not check_circuit(conflict, nonlinear)
    distributions = [Counter(), Counter()]
    masks = gl(f, 2)
    for m in masks:
        ev = mm(f, m, columns(v, [0, 1]))
        for version, d in enumerate(([1, 1], [1, 2])):
            output = tuple(f.mul(ev[i][j], d[j]) for i in range(2) for j in range(2))
            distributions[version][output] += 3
    for distribution in distributions: distribution[(0, 0, 0, 0)] += len(masks)
    distance = tv(*distributions)
    assert distance == Fraction(3, 4)
    (out / 'certificates.json').write_text(json.dumps(certs, indent=2))
    (out / 'profiles.json').write_text(json.dumps(records, indent=2))
    (out / 'conflict.json').write_text(json.dumps({'policy': policy, 'certificate': conflict,
        'mutations_rejected': mutations + ['inadmissible support', 'correlated amplitudes', 'different mask class'], 'exact_TV': str(distance),
        'erasure_probability': '1/4', 'tight_sum': '1'}, indent=2))
    summary = {'pass': True, 'profiles': len(profiles), 'distribution_encodings': total_encodings,
               'mask_matrices': sum(r['valid_masks_enumerated'] for r in records),
               'bases': sum(r['bases_checked'] for r in records),
               'scope': 'public geometry plus exact distributions; no runtime support-admissibility MPC implemented',
               'independent_checker_limits': 'GF3/GF4, rows<=4, columns<=8',
               'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                   [Path(__file__), Path(__file__).with_name('structural_masks.py'), Path(__file__).with_name('structural_checker.py')]}}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2)); print(json.dumps(summary))


if __name__ == '__main__': main()
