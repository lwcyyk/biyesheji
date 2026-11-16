"""Solve only the authorized q=4099, d=k=4, n=5 LPs using Fraction arithmetic."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import platform
import time

ROOT = Path(__file__).resolve().parent


def build_model(q, row_limit):
    Q = q - 1
    a = q*q - 3*q + 3
    b = q*q - 4*q + 5
    c = q**3 - 7*q*q + 18*q - 18
    right = {'S1': {'orbits': 1, 'size': Q**3, 'forbidden': a}}
    incidence = {'R1': {'S1': (q**3 - 4*q*q + 6*q - 4, 5)}}
    if row_limit >= 2:
        right.update({
            'S2_31': {'orbits': 4, 'size': Q**2, 'forbidden': 0},
            'S2_22': {'orbits': 3, 'size': Q**2, 'forbidden': 1},
            'S2_211': {'orbits': 6, 'size': Q**3, 'forbidden': q-2},
            'S2_1111': {'orbits': q-2, 'size': Q**3, 'forbidden': q-3}})
        incidence.update({
            'R2_32': {'S2_31': (q-2, 2), 'S2_22': (2*(q-2), 3)},
            'R2_311': {'S2_31': (a, 2), 'S2_211': (a, 3)},
            'R2_221': {'S2_22': ((q-2)**2, 1), 'S2_211': (2*(q-2)**2, 4)},
            'R2_2111': {'S2_211': ((q-2)*b, 3), 'S2_1111': (4*b, 2)},
            'R2_11111': {'S2_1111': (c, 5)}})
    if row_limit >= 3:
        right.update({
            'S3_2': {'orbits': 6, 'size': Q, 'forbidden': 0},
            'S3_3': {'orbits': 4, 'size': Q**2, 'forbidden': 0},
            'S3_4': {'orbits': 1, 'size': Q**3, 'forbidden': 1}})
        incidence.update({
            'R3_32': {'S3_2': (1, 3), 'S3_3': (1, 2)},
            'R3_311': {'S3_2': (q-2, 3), 'S3_4': (4*(q-2), 2)},
            'R3_221': {'S3_3': (3*(q-2), 4), 'S3_4': (3*(q-2), 1)},
            'R3_2111': {'S3_3': ((q-2)*(q-3), 2), 'S3_4': (6*(q-2)*(q-3), 3)},
            'R3_11111': {'S3_4': ((q-2)*(q-3)*(q-4), 5)}})
    left = {}
    edges = []
    for label, neighbors in incidence.items():
        sizes = {Fraction(5 * right[category]['orbits'] * count, degree)
                 for category, (count, degree) in neighbors.items()}
        assert len(sizes) == 1
        size = sizes.pop()
        assert size.denominator == 1
        left[label] = size.numerator
        for category, (count, degree) in neighbors.items():
            edges.append({'left': label, 'right': category,
                          'per_orbit_count': count, 'left_degree': degree,
                          'f': Fraction(degree, 5),
                          'g': Fraction(count, right[category]['size'])})
    for category, data in right.items():
        assert sum(e['per_orbit_count'] for e in edges if e['right'] == category) + data['forbidden'] == data['size']
    return left, right, edges


def exact_simplex(matrix, bound, objective):
    """Maximize c*x with A*x<=b, x>=0 and b>=0. Bland pivoting, exact rationals."""
    n = len(objective)
    m = len(bound)
    assert all(value >= 0 for value in bound)
    tableau = []
    for i, (row, rhs) in enumerate(zip(matrix, bound)):
        tableau.append([Fraction(value) for value in row] +
                       [Fraction(int(i == j)) for j in range(m)] + [Fraction(rhs)])
    tableau.append([-Fraction(value) for value in objective] + [Fraction(0)] * (m+1))
    basis = [n+i for i in range(m)]
    trace = []
    while True:
        entering = next((j for j in range(n+m) if tableau[-1][j] < 0), None)
        if entering is None:
            break
        choices = [(tableau[i][-1] / tableau[i][entering], basis[i], i)
                   for i in range(m) if tableau[i][entering] > 0]
        if not choices:
            raise RuntimeError('Unexpected unbounded LP')
        ratio, leaving, pivot_row = min(choices)
        pivot = tableau[pivot_row][entering]
        normalized = [value / pivot for value in tableau[pivot_row]]
        for i in range(m+1):
            if i == pivot_row:
                continue
            factor = tableau[i][entering]
            if factor:
                tableau[i] = [value - factor*other if other else value
                              for value, other in zip(tableau[i], normalized)]
        tableau[pivot_row] = normalized
        basis[pivot_row] = entering
        trace.append({'entering': entering, 'leaving': leaving, 'step': str(ratio),
                      'objective': str(tableau[-1][-1])})
        if len(trace) > 10000:
            raise RuntimeError('Exact Bland iteration guard reached')
    solution = [Fraction(0)] * n
    for i, variable in enumerate(basis):
        if variable < n:
            solution[variable] = tableau[i][-1]
    shadow_prices = tableau[-1][n:n+m]
    return tableau[-1][-1], solution, shadow_prices, trace


def solve(q, row_limit):
    left, right, edges = build_model(q, row_limit)
    left_names = list(left)
    right_names = list(right)
    names = [('x', x) for x in left_names[1:]] + [('y', y) for y in right_names[1:]]
    names += [('h', i) for i in range(len(edges))]
    index = {name: i for i, name in enumerate(names)}
    count = len(names)
    matrix = []
    bound = []
    for kind, labels in [('x', left_names), ('y', right_names)]:
        row = [Fraction(0)] * count
        for label in labels[1:]:
            row[index[kind, label]] = 1
        matrix.append(row)
        bound.append(Fraction(1))
    for number, edge in enumerate(edges):
        for kind, label, coefficient, labels in [
                ('x', edge['left'], edge['f'], left_names),
                ('y', edge['right'], edge['g'], right_names)]:
            row = [Fraction(0)] * count
            row[index['h', number]] = 1
            rhs = Fraction(0)
            if label == labels[0]:
                for other in labels[1:]:
                    row[index[kind, other]] = coefficient
                rhs = coefficient
            else:
                row[index[kind, label]] = -coefficient
            matrix.append(row)
            bound.append(rhs)
    objective = [Fraction(int(kind == 'h')) for kind, label in names]
    started = time.monotonic_ns()
    overlap, solution, shadows, trace = exact_simplex(matrix, bound, objective)
    elapsed = time.monotonic_ns() - started
    x = {label: solution[index['x', label]] for label in left_names[1:]}
    x[left_names[0]] = 1 - sum(x.values())
    y = {label: solution[index['y', label]] for label in right_names[1:]}
    y[right_names[0]] = 1 - sum(y.values())
    u = [shadows[2 + 2*i] for i in range(len(edges))]
    v = [shadows[3 + 2*i] for i in range(len(edges))]
    alpha = shadows[0] + sum(edge['f']*u[i] for i, edge in enumerate(edges) if edge['left'] == left_names[0])
    beta = shadows[1] + sum(edge['g']*v[i] for i, edge in enumerate(edges) if edge['right'] == right_names[0])
    assert alpha + beta == overlap
    certificate = {'row_limit': row_limit, 'delta': str(1-overlap),
                   'primal_overlap': str(overlap), 'dual_overlap': str(alpha+beta),
                   'left_sizes': left, 'right_categories': right,
                   'primal': {'x': {k: str(z) for k, z in x.items()},
                              'y': {k: str(z) for k, z in y.items()},
                              'kernel_densities': {k: str(x[k]/left[k]) for k in left},
                              'simulator_densities': {k: str(y[k]/(right[k]['orbits']*right[k]['size'])) for k in right}},
                   'dual': {'alpha': str(alpha), 'beta': str(beta)},
                   'edges': [],
                   'run': {'variables_after_elimination': count, 'inequalities': len(bound),
                           'pivots': len(trace), 'elapsed_ns': elapsed}}
    for i, edge in enumerate(edges):
        certificate['edges'].append({**{k: str(z) if isinstance(z, Fraction) else z for k, z in edge.items()},
                                     'h': str(solution[index['h', i]]), 'u': str(u[i]), 'v': str(v[i])})
    return certificate, trace


if __name__ == '__main__':
    q = 4099
    solutions = []
    traces = {}
    for row_limit in [2, 3]:
        solution, trace = solve(q, row_limit)
        solutions.append(solution)
        traces[str(row_limit)] = trace
        print(json.dumps({'r': row_limit, 'delta': solution['delta'], 'run': solution['run']}, ensure_ascii=False), flush=True)
    result = {'schema': 'paired_exact_lp_certificate/1', 'q': q, 'd': 4, 'k': 4, 'n': 5,
              'profile': {'observation': 'indexed MV_S diag(a)', 'input_independent_mask': True,
                          'supports': 'all subsets of size at most k', 'amplitudes': 'arbitrary independent nonzero field entries',
                          'no_erasure': 'all dictionary columns almost surely', 'rank_mixing': True,
                          'simulator_given_support': True, 'entropy_budget': None, 'authorizes_execution': False},
              'dictionary': [[pow(i, power, q) for i in range(5)] for power in range(4)],
              'circuit_relation': [1, -4, 6, -4, 1],
              'arithmetic': 'Python fractions.Fraction, no floating point',
              'model_reduction': 'MODEL_REDUCTION.md, hand proof plus independent integer checks',
              'model_reduction_sha256': hashlib.sha256((ROOT/'MODEL_REDUCTION.md').read_bytes()).hexdigest(),
              'python_version': platform.python_version(),
              'solver_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'certificates': solutions}
    (ROOT/'DUAL_CERTIFICATES.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    (ROOT/'EXACT_SIMPLEX_TRACE.json').write_text(json.dumps(traces, indent=2), encoding='utf8')
