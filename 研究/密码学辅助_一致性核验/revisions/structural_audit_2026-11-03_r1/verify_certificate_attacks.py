"""Symmetric context/omission attacks on both certificate types."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
from compiler import components, find_conflict, digest
from checker import check
from profiles import record_profiles

REV = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True); args = parser.parse_args()
    target = (REV / args.out).resolve()
    if not target.is_relative_to(REV): raise ValueError('revision output only')
    target.mkdir(parents=True, exist_ok=False); records = []
    original, restricted = record_profiles()
    for name, profile, cert in [('conflict', original, find_conflict(original)), ('components', restricted, components(restricted))]:
        def test(case, actual, expected):
            assert actual == expected, (case, actual, expected)
            records.append({'kind': name, 'case': case, 'actual': actual, 'expected': expected, 'pass': True})
        for key in profile:
            changed = deepcopy(profile); del changed[key]
            test('missing_profile_' + key, check(cert, changed)['verification_status'], 'INVALID_INPUT')
        for key in cert:
            changed = deepcopy(cert); del changed[key]
            test('missing_certificate_' + key, check(changed, profile)['verification_status'], 'INVALID_CERTIFICATE')
        for key in ('source_refs', 'constraint_refs'):
            changed = deepcopy(profile); changed[key] = ['attacker-substitution']
            test('substituted_' + key, check(cert, changed)['verification_status'], 'INVALID_CERTIFICATE')
        for key in ('amplitude_model', 'observation_model', 'mask_model'):
            changed = deepcopy(profile); changed[key] = 'wrong-model'; rebound = deepcopy(cert); rebound['profile_digest'] = digest(changed)
            test('rebound_wrong_' + key, check(rebound, changed)['verification_status'], 'MODEL_NOT_APPLICABLE')
        for key in ('world_ref', 'approval_ref', 'budget_ref'):
            changed = deepcopy(profile); changed[key] += ':stale'
            test('stale_' + key, check(cert, changed)['verification_status'], 'INVALID_CERTIFICATE')
    changed = deepcopy(original); changed['support_policy']['supports'] = [[],[0],[1],[2],[3]]
    c = find_conflict(original); c['profile_digest'] = digest(changed)
    actual = check(c, changed)['verification_status']; assert actual == 'INVALID_CERTIFICATE'
    records.append({'kind': 'conflict', 'case': 'removed_allowed_witness_rebound', 'actual': actual, 'expected': 'INVALID_CERTIFICATE', 'pass': True})
    (target / 'checks.json').write_text(json.dumps(records, indent=2))
    result = {'pass': True, 'assertion_records': len(records), 'scope': 'public certificate boundary tests only'}
    (target / 'summary.json').write_text(json.dumps(result, indent=2)); print(json.dumps(result))


if __name__ == '__main__': main()
