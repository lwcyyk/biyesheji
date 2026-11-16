"""Produces public-model certificates, never runtime authorization."""
import hashlib
import json
from itertools import combinations
from algebra import Field, columns, rank, rref, left_inverse, multiply, independent_sets


def digest(profile):
    return hashlib.sha256(json.dumps(profile, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def envelope(profile, kind):
    return {'version': 1, 'kind': kind, 'profile_digest': digest(profile),
            'scope': 'PUBLIC_MODEL_ONLY', 'authorizes_execution': False}


def components(profile, basis=None):
    v, q = profile['dictionary'], profile['field']['q']; f = Field(q); n = profile['n']
    active = sorted({i for s in profile['support_policy']['supports'] for i in s})
    selected = []
    if basis is None:
        for i in active:
            if rank(f, columns(v, selected + [i])) > len(selected): selected.append(i)
    else: selected = list(basis)
    d = len(selected)
    if d:
        b = columns(v, selected); ell = left_inverse(f, b); coords = multiply(f, ell, v)
    else: b, ell, coords = [[] for _ in v], [], []
    parent = list(range(d))
    def root(i):
        while parent[i] != i: i = parent[i]
        return i
    for col in active:
        axes = [j for j in range(d) if coords[j][col]]
        for j in axes[1:]: parent[root(j)] = root(axes[0])
    blocks = []
    for representative in sorted({root(i) for i in range(d)}):
        axes = [i for i in range(d) if root(i) == representative]
        items = [i for i in active if any(coords[j][i] for j in axes)]
        size = len(axes); cardinality = 1
        for h in range(size): cardinality *= q ** size - q ** h
        blocks.append({'columns': items, 'basis_axes': axes, 'rank': size, 'GL_size': cardinality})
    blocks.sort(key=lambda x: x['columns'])
    cardinality = 1
    for block in blocks: cardinality *= block['GL_size']
    return {**envelope(profile, 'COMPONENT_RESOURCES'), 'active_columns': active,
            'basis': selected, 'left_inverse': ell, 'components': blocks,
            'minimum_rows': max([x['rank'] for x in blocks], default=0),
            'entropy_orbit_size': cardinality,
            'premise': 'support_policy_equals_all_independent_sets'}


def find_conflict(profile):
    f = Field(profile['field']['q']); v = profile['dictionary']
    for allowed in profile['support_policy']['supports']:
        for size in range(1, len(allowed) + 1):
            for s in combinations(allowed, size):
                a = columns(v, s)
                if rank(f, a) == size: continue
                reduced, pivots = rref(f, a)
                free = next(i for i in range(size) if i not in pivots)
                c = [0] * size; c[free] = 1
                for row, pivot in zip(reduced, pivots): c[pivot] = f.neg(row[free])
                if not all(c): continue
                return {**envelope(profile, 'CIRCUIT_CONFLICT'), 'support': list(s), 'coefficients': c,
                        'allowed_support_witness': allowed,
                        'conclusion': 'NO_PERFECT_NONERASING_MASK_IN_DECLARED_CLASS'}
    return {**envelope(profile, 'SEARCH_RESULT'),
            'status': 'NO_WITNESS_FOUND', 'conclusion': 'NO_FEASIBILITY_CERTIFICATE'}
