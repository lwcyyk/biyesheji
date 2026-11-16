"""Independent bounded certificate checker, with no generator/algebra imports.

VERIFIED concerns a public mathematical profile only. It never authorizes an
action, attests a service fact, or certifies actual secret support membership.
"""
import hashlib
import json
from itertools import combinations


class CheckFailure(Exception):
    def __init__(self, status, reason): self.status, self.reason = status, reason


def fail(status, reason): raise CheckFailure(status, reason)
def encoded(profile): return json.dumps(profile, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
def outcome(status, reason, conclusion='NONE', **data):
    return {'verification_status': status, 'reason': reason, 'mathematical_conclusion': conclusion,
            'scope': 'PUBLIC_MODEL_ONLY', 'runtime_support_verified': False,
            'authorizes_execution': False, **data}


def profile_check(p):
    if not isinstance(p, dict): fail('INVALID_INPUT', 'PROFILE_NOT_OBJECT')
    required = {'version', 'profile_id', 'field', 'n', 'dictionary', 'support_policy',
                'amplitude_model', 'mask_model', 'observation_model', 'retention_scope',
                'policy_ref', 'world_ref', 'constraint_refs', 'approval_ref', 'budget_ref', 'source_refs'}
    if set(p) != required: fail('INVALID_INPUT', 'PROFILE_FIELDS_MISSING_OR_UNKNOWN')
    if type(p['version']) is not int or p['version'] != 1: fail('INVALID_INPUT', 'PROFILE_VERSION')
    for key in ('profile_id', 'policy_ref', 'world_ref', 'approval_ref', 'budget_ref'):
        if not isinstance(p[key], str) or not p[key]: fail('INVALID_INPUT', 'MISSING_REFERENCE:' + key)
    for key in ('constraint_refs', 'source_refs'):
        if (not isinstance(p[key], list) or not p[key] or any(not isinstance(x, str) or not x for x in p[key])
            or len(set(p[key])) != len(p[key])): fail('INVALID_INPUT', 'REFERENCE_LIST:' + key)
    f = p['field']
    if not isinstance(f, dict) or set(f) != {'q', 'representation'} or type(f['q']) is not int:
        fail('INVALID_INPUT', 'FIELD_DESCRIPTOR')
    q = f['q']
    if q <= 2: fail('MODEL_NOT_APPLICABLE', 'THEOREMS_REQUIRE_Q_GREATER_THAN_TWO')
    if q not in (3, 4): fail('OUT_OF_SCOPE', 'CHECKER_FIELDS_GF3_GF4_ONLY')
    if f['representation'] != {3: 'prime_mod_3', 4: 'poly_x2_x_1'}[q]: fail('INVALID_INPUT', 'FIELD_REPRESENTATION')
    n = p['n']
    if type(n) is not int or n < 0: fail('INVALID_INPUT', 'N_TYPE_OR_SIGN')
    if n > 8: fail('OUT_OF_SCOPE', 'CHECKER_N_LE_8')
    v = p['dictionary']
    if not isinstance(v, list) or not v: fail('INVALID_INPUT', 'AMBIENT_ROWS_REQUIRED')
    if len(v) > 4: fail('OUT_OF_SCOPE', 'CHECKER_AMBIENT_ROWS_LE_4')
    if any(not isinstance(row, list) or len(row) != n for row in v): fail('INVALID_INPUT', 'DICTIONARY_SHAPE')
    if any(type(x) is not int or not 0 <= x < q for row in v for x in row): fail('INVALID_INPUT', 'DICTIONARY_ELEMENT')
    expected = {'amplitude_model': 'arbitrary_nonzero_per_position',
                'mask_model': 'input_independent_linear',
                'observation_model': 'indexed_masked_columns', 'retention_scope': 'active_only'}
    for key, value in expected.items():
        if p[key] != value: fail('MODEL_NOT_APPLICABLE', 'UNSUPPORTED_MODEL:' + key)
    policy = p['support_policy']
    if not isinstance(policy, dict): fail('INVALID_INPUT', 'POLICY_NOT_OBJECT')
    if policy.get('representation') != 'explicit_list': fail('INCONCLUSIVE', 'SUPPORT_FAMILY_NOT_ENUMERATED')
    if set(policy) != {'representation', 'coverage', 'supports'}: fail('INVALID_INPUT', 'POLICY_FIELDS')
    if policy['coverage'] not in ('exact', 'known_subset'): fail('INVALID_INPUT', 'COVERAGE_MODE')
    supports = policy['supports']
    if not isinstance(supports, list): fail('INVALID_INPUT', 'SUPPORTS_NOT_LIST')
    if len(supports) > 2 ** n: fail('OUT_OF_SCOPE', 'FAMILY_LIST_TOO_LARGE')
    canonical = set()
    for support in supports:
        if (not isinstance(support, list) or any(type(i) is not int or not 0 <= i < n for i in support)
            or len(set(support)) != len(support)): fail('INVALID_INPUT', 'SUPPORT_ELEMENT_OR_DUPLICATE')
        value = tuple(sorted(support))
        if value in canonical: fail('INVALID_INPUT', 'DUPLICATE_SUPPORT')
        canonical.add(value)
    return q, n, v, canonical


class LinearReference:
    def __init__(self, q, budget): self.q, self.budget, self.used = q, budget, 0
    def add(self, a, b): return (a + b) % 3 if self.q == 3 else a ^ b
    def neg(self, a): return (-a) % 3 if self.q == 3 else a
    def mul(self, a, b):
        if self.q == 3: return a * b % 3
        # Independent full GF4 multiplication table.
        return ((0,0,0,0), (0,1,2,3), (0,2,3,1), (0,3,1,2))[a][b]
    def rank(self, v):
        self.used += 1
        if self.used > self.budget: fail('INCONCLUSIVE', 'CHECK_WORK_BUDGET_EXHAUSTED')
        rows = [row[:] for row in v]; lead = 0
        if not rows: return 0
        for c in range(len(rows[0])):
            pivot = next((i for i in range(lead, len(rows)) if rows[i][c]), None)
            if pivot is None: continue
            rows[lead], rows[pivot] = rows[pivot], rows[lead]
            inv = next(x for x in range(1, self.q) if self.mul(x, rows[lead][c]) == 1)
            rows[lead] = [self.mul(inv, x) for x in rows[lead]]
            for i in range(len(rows)):
                if i == lead: continue
                t = rows[i][c]
                rows[i] = [self.add(x, self.neg(self.mul(t, y))) for x, y in zip(rows[i], rows[lead])]
            lead += 1
            if lead == len(rows): break
        return lead
    def product(self, a, b):
        if not b: return [[] for _ in a]
        out = []
        for row in a:
            target = []
            for j in range(len(b[0])):
                value = 0
                for l, x in enumerate(row): value = self.add(value, self.mul(x, b[l][j]))
                target.append(value)
            out.append(target)
        return out


def check(cert, profile, max_rank_checks=10000):
    try:
        q, n, v, family = profile_check(profile)
        if type(max_rank_checks) is not int or max_rank_checks < 0: fail('INVALID_INPUT', 'CHECK_BUDGET')
        ref = LinearReference(q, max_rank_checks)
        if not isinstance(cert, dict): fail('INVALID_CERTIFICATE', 'CERTIFICATE_NOT_OBJECT')
        if cert.get('version') != 1 or type(cert.get('version')) is not int: fail('INVALID_CERTIFICATE', 'CERTIFICATE_VERSION')
        if cert.get('profile_digest') != hashlib.sha256(encoded(profile)).hexdigest(): fail('INVALID_CERTIFICATE', 'PROFILE_BINDING_MISMATCH')
        if cert.get('scope') != 'PUBLIC_MODEL_ONLY' or cert.get('authorizes_execution') is not False:
            fail('INVALID_CERTIFICATE', 'AUTHORITY_OVERCLAIM')
        common = {'version', 'kind', 'profile_digest', 'scope', 'authorizes_execution'}
        payloads = {'CIRCUIT_CONFLICT': {'support', 'coefficients', 'allowed_support_witness', 'conclusion'},
                    'COMPONENT_RESOURCES': {'active_columns', 'basis', 'left_inverse', 'components',
                                            'minimum_rows', 'entropy_orbit_size', 'premise'}}
        if cert.get('kind') not in payloads or set(cert) != common | payloads[cert['kind']]:
            fail('INVALID_CERTIFICATE', 'CERTIFICATE_FIELDS_MISSING_OR_UNKNOWN')
        sub = lambda s: [[row[i] for i in s] for row in v]
        def indices(value, allow_empty=True):
            if (not isinstance(value, list) or (not allow_empty and not value)
                or any(type(i) is not int or not 0 <= i < n for i in value)
                or len(set(value)) != len(value)): fail('INVALID_CERTIFICATE', 'INDEX_LIST')
            return value
        if cert.get('kind') == 'CIRCUIT_CONFLICT':
            if cert.get('conclusion') != 'NO_PERFECT_NONERASING_MASK_IN_DECLARED_CLASS': fail('INVALID_CERTIFICATE', 'CONCLUSION')
            s = indices(cert.get('support'), False); c = cert.get('coefficients')
            witness = indices(cert.get('allowed_support_witness'))
            if tuple(sorted(witness)) not in family or not set(s) <= set(witness): fail('INVALID_CERTIFICATE', 'WITNESS_NOT_DECLARED_ADMISSIBLE')
            if not isinstance(c, list) or len(c) != len(s) or any(type(x) is not int or not 0 < x < q for x in c):
                fail('INVALID_CERTIFICATE', 'CIRCUIT_COEFFICIENTS')
            for row in v:
                value = 0
                for i, a in zip(s, c): value = ref.add(value, ref.mul(row[i], a))
                if value: fail('INVALID_CERTIFICATE', 'RELATION_FALSE')
            if ref.rank(sub(s)) != len(s) - 1: fail('INVALID_CERTIFICATE', 'NOT_MINIMAL_CIRCUIT')
            if any(ref.rank(sub([i for i in s if i != removed])) != len(s) - 1 for removed in s):
                fail('INVALID_CERTIFICATE', 'NOT_MINIMAL_CIRCUIT')
            return outcome('VERIFIED', 'DEPENDENT_ADMISSIBLE_SUPPORT_WITNESS', 'INFEASIBLE_IN_DECLARED_MASK_CLASS',
                           rank_checks=ref.used, affected_positions=s, family_complete=profile['support_policy']['coverage'] == 'exact')
        if cert.get('kind') != 'COMPONENT_RESOURCES': fail('INVALID_CERTIFICATE', 'UNSUPPORTED_CERTIFICATE_KIND')
        if cert.get('premise') != 'support_policy_equals_all_independent_sets': fail('INVALID_CERTIFICATE', 'PREMISE_MISSING')
        if profile['support_policy']['coverage'] != 'exact': fail('INCONCLUSIVE', 'C3_REQUIRES_COMPLETE_FAMILY')
        active = sorted({i for s in family for i in s})
        independent = set()
        for size in range(len(active) + 1):
            for s in combinations(active, size):
                if ref.rank(sub(s)) == size: independent.add(tuple(s))
        if family != independent: fail('MODEL_NOT_APPLICABLE', 'C3_FAMILY_NOT_ALL_INDEPENDENT_SETS_ON_ACTIVE_UNIVERSE')
        if indices(cert.get('active_columns')) != active: fail('INVALID_CERTIFICATE', 'ACTIVE_UNIVERSE')
        basis = indices(cert.get('basis')); d = ref.rank(sub(active))
        if not set(basis) <= set(active) or len(basis) != d or ref.rank(sub(basis)) != d:
            fail('INVALID_CERTIFICATE', 'BASIS')
        ell = cert.get('left_inverse')
        if (not isinstance(ell, list) or len(ell) != d
            or any(not isinstance(row, list) or len(row) != len(v) for row in ell)
            or any(type(x) is not int or not 0 <= x < q for row in ell for x in row)):
            fail('INVALID_CERTIFICATE', 'LEFT_INVERSE_SHAPE')
        if d and ref.product(ell, sub(basis)) != [[int(i == j) for j in range(d)] for i in range(d)]:
            fail('INVALID_CERTIFICATE', 'LEFT_INVERSE_FALSE')
        if d and ref.product(sub(basis), ref.product(ell, sub(active))) != sub(active):
            fail('INVALID_CERTIFICATE', 'BASIS_DOES_NOT_SPAN_ACTIVE_COLUMNS')
        # Independent of producer's fundamental-circuit graph: enumerate all circuits.
        parent = {i: i for i in active}
        def root(i):
            while parent[i] != i: i = parent[i]
            return i
        for size in range(1, min(d + 1, len(active)) + 1):
            for s in combinations(active, size):
                if ref.rank(sub(s)) != size - 1: continue
                if not all(ref.rank(sub([i for i in s if i != removed])) == size - 1 for removed in s): continue
                for i in s[1:]: parent[root(i)] = root(s[0])
        groups = sorted([[i for i in active if root(i) == r] for r in sorted({root(i) for i in active})])
        blocks = cert.get('components')
        if not isinstance(blocks, list) or any(not isinstance(b, dict) for b in blocks): fail('INVALID_CERTIFICATE', 'COMPONENT_SHAPE')
        for b in blocks: indices(b.get('columns'), False)
        if sorted([b['columns'] for b in blocks]) != groups: fail('INVALID_CERTIFICATE', 'COMPONENT_PARTITION')
        entropy_size = 1; ranks = []
        for b in blocks:
            if set(b) != {'columns', 'basis_axes', 'rank', 'GL_size'}: fail('INVALID_CERTIFICATE', 'COMPONENT_FIELDS')
            if not isinstance(b.get('basis_axes'), list) or any(type(i) is not int for i in b['basis_axes']):
                fail('INVALID_CERTIFICATE', 'BASIS_AXES_TYPE')
            size = ref.rank(sub(b['columns'])); ranks.append(size)
            if b.get('basis_axes') != [j for j, i in enumerate(basis) if i in b['columns']]: fail('INVALID_CERTIFICATE', 'BASIS_AXES')
            gl_size = 1
            for h in range(size): gl_size *= q ** size - q ** h
            if type(b.get('rank')) is not int or b['rank'] != size or type(b.get('GL_size')) is not int or b['GL_size'] != gl_size:
                fail('INVALID_CERTIFICATE', 'COMPONENT_RESOURCE')
            entropy_size *= gl_size
        if type(cert.get('minimum_rows')) is not int or cert['minimum_rows'] != max(ranks, default=0): fail('INVALID_CERTIFICATE', 'ROW_BOUND')
        if type(cert.get('entropy_orbit_size')) is not int or cert['entropy_orbit_size'] != entropy_size: fail('INVALID_CERTIFICATE', 'ENTROPY_BOUND')
        return outcome('VERIFIED', 'EXACT_PUBLIC_FAMILY_AND_COMPONENTS_CHECKED', 'CONDITIONAL_COMPONENT_OPTIMALITY',
                       rank_checks=ref.used, minimum_rows=max(ranks, default=0),
                       entropy_orbit_size=entropy_size, empty_active_universe=not active)
    except CheckFailure as error:
        return outcome(error.status, error.reason)
    except (KeyError, TypeError, ValueError, IndexError, StopIteration):
        return outcome('INVALID_CERTIFICATE', 'MALFORMED_CERTIFICATE_DATA')
