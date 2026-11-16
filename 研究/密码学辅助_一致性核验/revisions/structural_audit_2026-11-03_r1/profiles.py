"""Explicit mathematical contracts. References are identifiers, not attestations."""
from algebra import independent_sets, all_subsets


def make(profile_id, v, q=4, supports=None, coverage='exact'):
    n = len(v[0])
    if supports is None: supports = independent_sets(v, q)
    return {'version': 1, 'profile_id': profile_id,
            'field': {'q': q, 'representation': {3: 'prime_mod_3', 4: 'poly_x2_x_1'}[q]},
            'n': n, 'dictionary': v,
            'support_policy': {'representation': 'explicit_list', 'coverage': coverage, 'supports': supports},
            'amplitude_model': 'arbitrary_nonzero_per_position',
            'mask_model': 'input_independent_linear', 'observation_model': 'indexed_masked_columns',
            'retention_scope': 'active_only', 'policy_ref': profile_id + ':policy-v1',
            'world_ref': 'SYNTHETIC_PUBLIC_MODEL_ONLY',
            'constraint_refs': ['C1-C3:declared-model', 'no-runtime-authority'],
            'approval_ref': 'LAB_ONLY_NO_EXTERNAL_ACTION_APPROVAL',
            'budget_ref': 'FINITE_CHECK_N8_D4', 'source_refs': ['NOT_A_SERVICE_ATTESTATION']}


def record_profiles():
    # A deliberately proposed compression of two checks per record, not a claim
    # that the checks have a common native revocation unit or correlated errors.
    v = [[1, 1, 0, 0], [0, 0, 1, 1]]
    original = make('ORIGINAL_ALL_AT_MOST_TWO', v, supports=[s for s in all_subsets(4) if len(s) <= 2])
    restricted = make('RESTRICTED_ONE_PER_RECORD', v)
    return original, restricted
