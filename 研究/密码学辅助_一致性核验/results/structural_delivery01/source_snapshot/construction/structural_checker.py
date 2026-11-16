"""Independent bounded checker. Never calls structural_masks or its compiler."""
from itertools import combinations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import reference


def checked_rank(v, q):
    a = [row[:] for row in v]
    if not a or not a[0]: return 0
    def add(x, y): return x ^ y if q == 4 else (x + y) % 3
    def neg(x): return x if q == 4 else (-x) % 3
    def mul(x, y): return reference.mul(x, y, 2, 7) if q == 4 else (x * y) % 3
    lead = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(lead, len(a)) if a[i][col]), None)
        if pivot is None: continue
        a[pivot], a[lead] = a[lead], a[pivot]
        inverse = next(x for x in range(1, q) if mul(x, a[lead][col]) == 1)
        a[lead] = [mul(inverse, x) for x in a[lead]]
        for i in range(len(a)):
            if i == lead: continue
            factor = a[i][col]
            a[i] = [add(x, neg(mul(factor, y))) for x, y in zip(a[i], a[lead])]
        lead += 1
        if lead == len(a): break
    return lead


def valid_dictionary(v, q):
    return (q in (3, 4) and isinstance(v, list) and 1 <= len(v) <= 4 and isinstance(v[0], list)
            and 1 <= len(v[0]) <= 8 and all(isinstance(row, list) and len(row) == len(v[0]) for row in v)
            and all(type(x) is int and 0 <= x < q for row in v for x in row))


def check_components(cert):
    v, q = cert.get('dictionary'), cert.get('q')
    if not valid_dictionary(v, q) or cert.get('kind') != 'INDEPENDENT_SUPPORT_MODEL_ONLY': return False
    k, n = len(v), len(v[0])
    if checked_rank(v, q) != k: return False
    if any(not any(row[i] for row in v) for i in range(n)): return False
    basis = cert.get('basis', [])
    if (len(basis) != k or len(set(basis)) != k
        or any(type(i) is not int or not 0 <= i < n for i in basis)
        or checked_rank([[row[i] for i in basis] for row in v], q) != k): return False
    # Independent reference: enumerate all minimal circuits and connect their
    # elements, rather than using the producer's fundamental-circuit graph.
    parent = list(range(n))
    def root(i):
        while parent[i] != i: i = parent[i]
        return i
    def sub(indices): return [[row[i] for i in indices] for row in v]
    for size in range(2, k + 2):
        for indices in combinations(range(n), size):
            if checked_rank(sub(indices), q) != size - 1: continue
            if not all(checked_rank(sub([i for i in indices if i != omit]), q) == size - 1 for omit in indices): continue
            for i in indices[1:]: parent[root(i)] = root(indices[0])
    groups = sorted([[i for i in range(n) if root(i) == r] for r in sorted({root(i) for i in range(n)})])
    provided = cert.get('components', [])
    if sorted([g.get('columns', []) for g in provided]) != groups: return False
    factors = []
    for group in provided:
        b = checked_rank(sub(group['columns']), q)
        if group.get('basis_axes') != [j for j, item in enumerate(basis) if item in group['columns']]: return False
        gl = 1
        for h in range(b): gl *= q ** b - q ** h
        if group.get('rank') != b or group.get('GL_size') != gl: return False
        factors.append(gl)
    if cert.get('minimum_mask_rows') != max(g['rank'] for g in provided): return False
    product_value = 1
    for x in factors: product_value *= x
    return cert.get('entropy_cardinality_lower_bound') == product_value


def check_circuit(cert, policy):
    v, q = cert.get('dictionary'), cert.get('q')
    if not valid_dictionary(v, q) or cert.get('kind') != 'DEPENDENT_SUPPORT_PRIVACY_CONFLICT': return False
    for key, required in [('amplitude_model', 'arbitrary_nonzero_per_position'),
                          ('mask_model', 'input_independent_linear_observable')]:
        if cert.get(key) != required or policy.get(key) != required: return False
    if any(not isinstance(cert.get(key), str) or not cert.get(key) for key in ('policy_ref', 'world_ref', 'constraint_ref')): return False
    if any(cert.get(key) != policy.get(key) for key in ('policy_ref', 'world_ref', 'constraint_ref')): return False
    if v != policy.get('dictionary') or q != policy.get('q'): return False
    support, coefficients = cert.get('support', []), cert.get('coefficients', [])
    n = len(v[0])
    if (not support or len(support) != len(coefficients) or len(set(support)) != len(support)
        or any(type(i) is not int or not 0 <= i < n for i in support)
        or any(type(x) is not int or not 0 < x < q for x in coefficients)): return False
    if not any(set(support) <= set(s) for s in policy.get('admissible_supports', [])): return False
    for row in v:
        value = 0
        for i, c in zip(support, coefficients):
            term = reference.mul(row[i], c, 2, 7) if q == 4 else row[i] * c % 3
            value = value ^ term if q == 4 else (value + term) % 3
        if value: return False
    sub = [[row[i] for i in support] for row in v]
    if checked_rank(sub, q) != len(support) - 1: return False
    for removed in support:
        if checked_rank([[row[i] for i in support if i != removed] for row in v], q) != len(support) - 1: return False
    return True
