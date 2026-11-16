"""Public dictionary audit for structure-restricted private masking.

Research prototype. The declared admissible supports must be enforced elsewhere;
this public compiler does not certify a secret residual's support at runtime.
"""
from itertools import combinations
from rank_tradeoff_checks import SmallField, inverse, mm


def rank(f, a):
    if not a: return 0
    rows = [r[:] for r in a]; lead = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(lead, len(rows)) if rows[i][col]), None)
        if pivot is None: continue
        rows[pivot], rows[lead] = rows[lead], rows[pivot]
        scale = f.inv(rows[lead][col]); rows[lead] = [f.mul(scale, x) for x in rows[lead]]
        for i in range(lead + 1, len(rows)):
            scale = rows[i][col]
            rows[i] = [f.add(x, f.neg(f.mul(scale, y))) for x, y in zip(rows[i], rows[lead])]
        lead += 1
        if lead == len(rows): break
    return lead


def columns(v, indices): return [[row[i] for i in indices] for row in v]


def compile_dictionary(v, q):
    f = SmallField(q); k = len(v)
    if not k or not v[0] or any(len(row) != len(v[0]) for row in v): raise ValueError('rectangular dictionary')
    if any(type(x) is not int or not 0 <= x < q for row in v for x in row): raise ValueError('field values')
    n = len(v[0])
    if any(not any(v[j][i] for j in range(k)) for i in range(n)): raise ValueError('loop/zero column')
    basis = []
    for i in range(n):
        if rank(f, columns(v, basis + [i])) > len(basis): basis.append(i)
    if len(basis) != k: raise ValueError('full row rank required')
    coordinate = mm(f, inverse(f, columns(v, basis)), v)
    parent = list(range(k))
    def find(i):
        while parent[i] != i: i = parent[i]
        return i
    for i in range(n):
        support = [j for j in range(k) if coordinate[j][i]]
        for j in support[1:]: parent[find(j)] = find(support[0])
    blocks = []
    for root in sorted({find(j) for j in range(k)}):
        axes = [j for j in range(k) if find(j) == root]
        items = [i for i in range(n) if any(coordinate[j][i] for j in axes)]
        assert all(not coordinate[j][i] for i in items for j in range(k) if j not in axes)
        b = len(axes); gl = 1
        for h in range(b): gl *= q ** b - q ** h
        blocks.append({'basis_axes': axes, 'columns': items, 'rank': b, 'GL_size': gl})
    blocks.sort(key=lambda x: x['columns'])
    return {'kind': 'INDEPENDENT_SUPPORT_MODEL_ONLY', 'q': q, 'dictionary': v, 'basis': basis,
            'components': blocks, 'minimum_mask_rows': max(x['rank'] for x in blocks),
            'entropy_cardinality_lower_bound': __import__('math').prod(x['GL_size'] for x in blocks),
            'requires': 'secret support is an independent set of this column matroid'}


def circuit_certificate(v, q, support, coefficients, *, policy_ref, world_ref, constraint_ref):
    # Merely constructs a certificate; the separate checker must validate it.
    return {'kind': 'DEPENDENT_SUPPORT_PRIVACY_CONFLICT', 'q': q,
            'dictionary': v, 'support': list(support), 'coefficients': list(coefficients),
            'policy_ref': policy_ref, 'world_ref': world_ref, 'constraint_ref': constraint_ref,
            'amplitude_model': 'arbitrary_nonzero_per_position',
            'mask_model': 'input_independent_linear_observable',
            'claim': 'pairwise privacy distance >= 1 - erasure probability at each circuit index'}
