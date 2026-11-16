"""Deterministic finite audit. All output paths stay in this revision."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import product, combinations
import importlib.util
import json
from pathlib import Path
import sys
from algebra import Field, columns, rank, multiply, all_subsets
from compiler import components, find_conflict, digest
from checker import check
from gate_reference import build, evaluate, direct_membership
from profiles import make, record_profiles

REV = Path(__file__).resolve().parent
ROOT = REV.parents[1]


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True)
    args = parser.parse_args(); out = (REV / args.out).resolve()
    if not out.is_relative_to(REV): raise ValueError('revision output only')
    out.mkdir(parents=True, exist_ok=False)
    records = []
    def expect(name, actual, expected):
        passed = actual == expected
        records.append({'case': name, 'expected': expected, 'actual': actual, 'pass': passed})
        if not passed: raise AssertionError((name, actual, expected))
    dictionaries = [
        [[1,1,0],[0,0,1]], [[1,0,1],[0,1,1]],
        [[1,0,0,1,0],[0,1,0,1,1],[0,0,1,0,1]],
        [[1,0,1,0,0,0],[0,1,1,0,0,0],[0,0,0,1,0,1],[0,0,0,0,1,1]],
        [[1,1,2]], [[1,0],[0,0],[1,0]], [[0,0]], [[]]]
    base_counts = 0; base_certificates = []
    for q in (3, 4):
        f = Field(q)
        for index, v in enumerate(dictionaries):
            profile = make(f'p{q}_{index}', v, q)
            cert = components(profile); result = check(cert, profile)
            expect(f'component_{q}_{index}', result['verification_status'], 'VERIFIED')
            expect(f'no_runtime_authority_{q}_{index}',
                   [result['authorizes_execution'], result['runtime_support_verified']], [False, False])
            base_certificates.append({'profile': profile, 'certificate': cert, 'result': result})
            active = cert['active_columns']; d = len(cert['basis'])
            bases = [list(s) for s in combinations(active, d) if rank(f, columns(v, s)) == d]
            if d > 1: bases += [list(reversed(bases[0]))]
            if d == 4: bases.append([0,3,1,4])
            for basis in bases:
                alternative = components(profile, basis=basis)
                expect(f'alternate_basis_{q}_{index}_{base_counts}', check(alternative, profile)['verification_status'], 'VERIFIED')
                expect(f'invariant_resources_{base_counts}',
                       [alternative['minimum_rows'], alternative['entropy_orbit_size'],
                        [b['columns'] for b in alternative['components']]],
                       [cert['minimum_rows'], cert['entropy_orbit_size'], [b['columns'] for b in cert['components']]])
                base_counts += 1
    profile = make('triangle', [[1,0,1],[0,1,1]], 3); cert = components(profile)
    for key in ('premise', 'left_inverse', 'components', 'profile_digest'):
        altered = deepcopy(cert); del altered[key]
        expect('missing_cert_' + key, check(altered, profile)['verification_status'], 'INVALID_CERTIFICATE')
    for key in ('constraint_refs', 'world_ref', 'observation_model', 'approval_ref', 'budget_ref'):
        altered = deepcopy(profile); del altered[key]
        expect('missing_profile_' + key, check(cert, altered)['verification_status'], 'INVALID_INPUT')
    for key in ('world_ref', 'policy_ref', 'approval_ref', 'budget_ref'):
        altered = deepcopy(profile); altered[key] += ':changed'
        expect('changed_scope_' + key, check(cert, altered)['verification_status'], 'INVALID_CERTIFICATE')
    for key in ('amplitude_model', 'mask_model', 'observation_model', 'retention_scope'):
        altered = deepcopy(profile); altered[key] = 'different-model'
        forged = deepcopy(cert); forged['profile_digest'] = digest(altered)
        expect('changed_model_' + key, check(forged, altered)['verification_status'], 'MODEL_NOT_APPLICABLE')
    for key, value in [('minimum_rows', 1), ('entropy_orbit_size', 1), ('active_columns', [False,1,2]),
                       ('left_inverse', [[0,0],[0,0]]), ('authorizes_execution', True)]:
        altered = deepcopy(cert); altered[key] = value
        expect('tamper_' + key, check(altered, profile)['verification_status'], 'INVALID_CERTIFICATE')
    altered = deepcopy(cert); altered['components'][0]['basis_axes'] = [False, True]
    expect('bool_axes', check(altered, profile)['verification_status'], 'INVALID_CERTIFICATE')
    altered = deepcopy(cert); altered['world_ref'] = 'ignored-if-not-strict'
    expect('unknown_cert_field', check(altered, profile)['verification_status'], 'INVALID_CERTIFICATE')
    expect('null_certificate', check(None, profile)['verification_status'], 'INVALID_CERTIFICATE')
    expect('null_profile', check(cert, None)['verification_status'], 'INVALID_INPUT')
    for q, status in [(3.0, 'INVALID_INPUT'), (2, 'MODEL_NOT_APPLICABLE'), (5, 'OUT_OF_SCOPE')]:
        altered = deepcopy(profile); altered['field']['q'] = q
        expect('field_' + str(q), check(cert, altered)['verification_status'], status)
    altered = deepcopy(profile); altered['n'] = 9
    expect('n_bound', check(cert, altered)['verification_status'], 'OUT_OF_SCOPE')
    altered = deepcopy(profile); altered['dictionary'] += [[0,0,0]] * 3
    expect('row_bound', check(cert, altered)['verification_status'], 'OUT_OF_SCOPE')
    expect('check_budget', check(cert, profile, max_rank_checks=0)['verification_status'], 'INCONCLUSIVE')
    partial = deepcopy(profile); partial['support_policy']['coverage'] = 'known_subset'
    partial_cert = deepcopy(cert); partial_cert['profile_digest'] = digest(partial)
    expect('partial_C3', check(partial_cert, partial)['verification_status'], 'INCONCLUSIVE')
    singletons = deepcopy(profile); singletons['support_policy']['supports'] = [[],[0],[1],[2]]
    single_cert = deepcopy(cert); single_cert['profile_digest'] = digest(singletons)
    expect('general_family_not_C3', check(single_cert, singletons)['verification_status'], 'MODEL_NOT_APPLICABLE')
    empty = deepcopy(profile); empty['support_policy']['supports'] = []
    empty_cert = deepcopy(cert); empty_cert['profile_digest'] = digest(empty)
    expect('empty_family_not_all_independent', check(empty_cert, empty)['verification_status'], 'MODEL_NOT_APPLICABLE')
    bad_policy = deepcopy(profile); bad_policy['support_policy']['supports'] = [[False, True]]
    expect('bool_policy_indices', check(cert, bad_policy)['verification_status'], 'INVALID_INPUT')
    bad_policy = deepcopy(profile); bad_policy['support_policy']['supports'].append([])
    expect('duplicate_policy_support', check(cert, bad_policy)['verification_status'], 'INVALID_INPUT')
    # Conflict and model-binding checks, including a witness in a known subset.
    original, restricted = record_profiles()
    conflict = find_conflict(original)
    expect('conflict_verified', check(conflict, original)['mathematical_conclusion'], 'INFEASIBLE_IN_DECLARED_MASK_CLASS')
    partial = deepcopy(original); partial['support_policy']['coverage'] = 'known_subset'
    partial_conflict = deepcopy(conflict); partial_conflict['profile_digest'] = digest(partial)
    expect('partial_positive_witness_valid', check(partial_conflict, partial)['verification_status'], 'VERIFIED')
    for key, value in [('coefficients', [1,2]), ('allowed_support_witness', [0,2]), ('support', [0,2])]:
        altered = deepcopy(conflict); altered[key] = value
        expect('conflict_tamper_' + key, check(altered, original)['verification_status'], 'INVALID_CERTIFICATE')
    expect('no_witness_not_certificate', check(find_conflict(restricted), restricted)['verification_status'], 'INVALID_CERTIFICATE')
    loop_profile = make('active_loop', [[0]], 3, supports=[[],[0]])
    expect('active_loop_impossible', check(find_conflict(loop_profile), loop_profile)['mathematical_conclusion'], 'INFEASIBLE_IN_DECLARED_MASK_CLASS')
    # Row changes must change bindings but preserve the proven resources.
    changes = 0
    for q in (3, 4):
        f = Field(q); v = [[1,1,0],[0,0,1]]; p0 = make('row-change', v, q); c0 = components(p0)
        for entries in product(range(q), repeat=4):
            a = [list(entries[:2]), list(entries[2:])]
            if rank(f, a) != 2: continue
            changed_v = multiply(f, a, v); p1 = make('row-change', changed_v, q); c1 = components(p1)
            expect('row_change_' + str(changes), check(c1, p1)['verification_status'], 'VERIFIED')
            expect('row_invariant_' + str(changes), [c1['minimum_rows'], c1['entropy_orbit_size']], [c0['minimum_rows'], c0['entropy_orbit_size']])
            expect('pullback_' + str(changes), multiply(f, c1['left_inverse'], changed_v), multiply(f, c0['left_inverse'], v))
            changes += 1
    # Entire support need not disappear: only the coordinates in a relation.
    f = Field(3); laws = []
    for amplitudes in product((1,2), repeat=3):
        laws.append(Counter((0,0,f.mul(rho, amplitudes[2])) for rho in (1,2)))
    expect('circuit_plus_coloop_privacy', all(x == laws[0] for x in laws), True)
    # Correlated block column spaces are allowed; frames conditional on them must
    # be independent. Shared scalar coefficients instead would leak a ratio.
    lines = [(1,0),(1,1),(1,2),(0,1)]
    frame_laws = []
    for a, b in product((1,2), repeat=2):
        frame_laws.append(Counter(tuple(f.mul(c, scale) for scale in (f.mul(a,x), f.mul(b,y)) for c in line)
                                  for line in lines for x,y in product((1,2), repeat=2)))
    expect('correlated_spaces_are_allowed', all(x == frame_laws[0] for x in frame_laws), True)
    shared0 = Counter((rho,rho) for rho in (1,2)); shared1 = Counter((rho,f.mul(2,rho)) for rho in (1,2))
    expect('correlated_frames_fail', set(shared0).isdisjoint(shared1), True)
    # Generic gate: complete finite domain, one-bit output, fixed node count.
    gate_rows = []; total_inputs = 0
    gate_profiles = [original, restricted, make('empty-family', [[1,0]], 4, supports=[]),
                     make('only-empty', [[0,0]], 3, supports=[[]]), make('no-coordinates', [[]], 4, supports=[[]])]
    original_true = restricted_true = lost = 0
    for p in gate_profiles:
        circuit = build(p); counts = Counter(); transcripts = set()
        for values in product(range(p['field']['q']), repeat=p['n']):
            result = evaluate(circuit, values); truth = direct_membership(p, values)
            if result['accepted'] != truth: raise AssertionError(('gate', p['profile_id'], values))
            if result['executed_nodes'] != len(circuit['nodes']): raise AssertionError('data-dependent schedule')
            counts[str(truth)] += 1; transcripts.add(tuple(result['public_transcript'])); total_inputs += 1
        gate_rows.append({'profile_id': p['profile_id'], 'profile': p, 'metrics': circuit['metrics'],
                          'counts': dict(counts), 'public_transcripts': sorted(transcripts)})
    for values in product(range(4), repeat=4):
        a, b = direct_membership(original, values), direct_membership(restricted, values)
        original_true += a; restricted_true += b; lost += a and not b
    expect('original_accepts', original_true, 67); expect('restricted_accepts', restricted_true, 49)
    expect('silently_lost_original_inputs', lost, 18)
    # Reproduce legacy issues by read-only import (python -B avoids old pycache writes).
    saved = sys.path[:]
    sys.path.insert(0, str(ROOT / 'construction'))
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
    legacy_gen = load('legacy_structural_masks', ROOT / 'construction/structural_masks.py')
    legacy_check = load('legacy_structural_checker', ROOT / 'construction/structural_checker.py')
    legacy = legacy_gen.compile_dictionary([[1,0,1],[0,1,1]], 3)
    removed = deepcopy(legacy); removed.pop('requires'); removed['world_ref'] = 'unbound-world'; removed['amplitude_model'] = 'different'
    legacy_findings = [{'case': 'component_missing_premise_and_added_wrong_context',
                        'actual': legacy_check.check_components(removed),
                        'impact': 'conditional dictionary check only; no external profile binding'}]
    float_q = deepcopy(legacy); float_q['q'] = 3.0
    for name, obj in [('float_q', float_q), ('null_cert', None)]:
        try: value = legacy_check.check_components(obj)
        except Exception as e: value = {'exception': type(e).__name__, 'message': str(e)}
        legacy_findings.append({'case': name, 'actual': value})
    sys.path[:] = saved
    (out / 'checks.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in records))
    (out / 'certificates.json').write_text(json.dumps(base_certificates, indent=2))
    (out / 'gate_reference.json').write_text(json.dumps({'profiles': gate_rows, 'inputs': total_inputs,
        'function_change': {'original_accepted': 67, 'restricted_accepted': 49, 'lost': 18,
                            'explicit_counterexample': [1,1,0,0]}}, indent=2))
    (out / 'legacy_findings.json').write_text(json.dumps(legacy_findings, indent=2))
    summary = {'pass': all(x['pass'] for x in records), 'assertion_records': len(records),
               'alternate_bases': base_counts, 'invertible_row_changes': changes,
               'gate_inputs_exhausted': total_inputs, 'new_mpc_protocols_executed': 0,
               'scope': 'finite certificate/contract and exact circuit checks; not a general proof or security audit'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2)); print(json.dumps(summary))


if __name__ == '__main__': main()
