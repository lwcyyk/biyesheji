"""Independent Fraction checker. Imports neither the solver nor its model builder."""
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
from math import isqrt
import argparse
import copy
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fraction(value):
    require(isinstance(value, str), 'Rational values must be explicit strings')
    return Fraction(value)


def determinant(matrix):
    total = 0
    for permutation in permutations(range(len(matrix))):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(len(matrix)) for j in range(i+1, len(matrix)))
        term = (-1) ** inversions
        for i, j in enumerate(permutation):
            term *= matrix[i][j]
        total += term
    return total


def independent_counts(q, row_limit):
    Q = q-1
    sizes = {'R1': q**3-4*q*q+6*q-4}
    degrees = {'R1': {'S1': 5}}
    categories = {'S1': {'orbits': 1, 'size': Q**3, 'forbidden': q*q-3*q+3}}
    if row_limit >= 2:
        sizes.update({'R2_32': 10*(q-2), 'R2_311': 10*(q*q-3*q+3),
                      'R2_221': 15*(q-2)**2, 'R2_2111': 10*(q-2)*(q*q-4*q+5),
                      'R2_11111': (q-2)*(q**3-7*q*q+18*q-18)})
        degrees.update({'R2_32': {'S2_31': 2, 'S2_22': 3},
                        'R2_311': {'S2_31': 2, 'S2_211': 3},
                        'R2_221': {'S2_22': 1, 'S2_211': 4},
                        'R2_2111': {'S2_211': 3, 'S2_1111': 2},
                        'R2_11111': {'S2_1111': 5}})
        categories.update({'S2_31': {'orbits': 4, 'size': Q**2, 'forbidden': 0},
                           'S2_22': {'orbits': 3, 'size': Q**2, 'forbidden': 1},
                           'S2_211': {'orbits': 6, 'size': Q**3, 'forbidden': q-2},
                           'S2_1111': {'orbits': q-2, 'size': Q**3, 'forbidden': q-3}})
        require(sum(value for label, value in sizes.items() if label.startswith('R2')) ==
                q**4+q**3-3*q*q-4*q+6, 'Rank-two class count')
    if row_limit >= 3:
        sizes.update({'R3_32': 10, 'R3_311': 10*(q-2), 'R3_221': 15*(q-2),
                      'R3_2111': 10*(q-2)*(q-3), 'R3_11111': (q-2)*(q-3)*(q-4)})
        degrees.update({'R3_32': {'S3_2': 3, 'S3_3': 2},
                        'R3_311': {'S3_2': 3, 'S3_4': 2},
                        'R3_221': {'S3_3': 4, 'S3_4': 1},
                        'R3_2111': {'S3_3': 2, 'S3_4': 3},
                        'R3_11111': {'S3_4': 5}})
        categories.update({'S3_2': {'orbits': 6, 'size': Q, 'forbidden': 0},
                           'S3_3': {'orbits': 4, 'size': Q**2, 'forbidden': 0},
                           'S3_4': {'orbits': 1, 'size': Q**3, 'forbidden': 1}})
        require(sum(value for label, value in sizes.items() if label.startswith('R3')) ==
                q**3+q*q+q-4, 'Rank-three class count')
    edges = {}
    for label, neighbors in degrees.items():
        require(sum(neighbors.values()) == 5, 'Five bases must be represented')
        for category, degree in neighbors.items():
            count = Fraction(sizes[label]*degree, 5*categories[category]['orbits'])
            require(count.denominator == 1, 'Incidence count is not integral')
            edges[label, category] = (Fraction(degree, 5),
                                      count/categories[category]['size'], count.numerator, degree)
    for category, data in categories.items():
        require(sum(edge[2] for (label, c), edge in edges.items() if c == category) +
                data['forbidden'] == data['size'], 'Orbit partition is incomplete')
    return sizes, categories, edges


def verify(document):
    profile = {'observation': 'indexed MV_S diag(a)', 'input_independent_mask': True,
               'supports': 'all subsets of size at most k', 'amplitudes': 'arbitrary independent nonzero field entries',
               'no_erasure': 'all dictionary columns almost surely', 'rank_mixing': True,
               'simulator_given_support': True, 'entropy_budget': None, 'authorizes_execution': False}
    require(document.get('profile') == profile, 'Observation or input contract mismatch')
    require((document['q'], document['d'], document['k'], document['n']) == (4099, 4, 4, 5),
            'Unexpected input profile')
    q = document['q']
    require(all(q % divisor for divisor in range(2, isqrt(q)+1)), 'Modulus is not prime')
    dictionary = [[pow(i, power, q) for i in range(5)] for power in range(4)]
    require(document['dictionary'] == dictionary, 'Dictionary mismatch')
    for indices in combinations(range(5), 4):
        require(determinant([[row[i] for i in indices] for row in dictionary]) % q != 0,
                'Dictionary is not full spark')
    relation = document['circuit_relation']
    require(relation == [1, -4, 6, -4, 1], 'Circuit reference mismatch')
    require(all(sum(x*c for x, c in zip(row, relation)) % q == 0 for row in dictionary),
            'Circuit relation invalid')
    require(document['model_reduction_sha256'] == hashlib.sha256((ROOT/'MODEL_REDUCTION.md').read_bytes()).hexdigest(),
            'Model document binding mismatch')
    certificates = document['certificates']
    require([item['row_limit'] for item in certificates] == [2, 3], 'Both row budgets required')
    reports = []
    for certificate in certificates:
        sizes, categories, expected = independent_counts(q, certificate['row_limit'])
        require(certificate['left_sizes'] == sizes, 'Left state counts mismatch')
        require(certificate['right_categories'] == categories, 'Orbit counts mismatch')
        primal = certificate['primal']
        require(set(primal['x']) == set(sizes) and set(primal['y']) == set(categories), 'Missing probability variable')
        x = {name: fraction(value) for name, value in primal['x'].items()}
        y = {name: fraction(value) for name, value in primal['y'].items()}
        require(all(value >= 0 for value in [*x.values(), *y.values()]), 'Negative probability')
        require(sum(x.values()) == sum(y.values()) == 1, 'Probability normalization')
        require(set(primal['kernel_densities']) == set(sizes), 'Kernel density scope mismatch')
        require(set(primal['simulator_densities']) == set(categories), 'Simulator density scope mismatch')
        for name in sizes:
            require(fraction(primal['kernel_densities'][name]) == x[name]/sizes[name], 'Kernel density inconsistent')
        for name, data in categories.items():
            require(fraction(primal['simulator_densities'][name]) == y[name]/(data['orbits']*data['size']),
                    'Simulator density inconsistent')
        alpha = fraction(certificate['dual']['alpha'])
        beta = fraction(certificate['dual']['beta'])
        require(alpha >= 0 and beta >= 0, 'Negative dual normalization weight')
        records = certificate['edges']
        require(len(records) == len(expected), 'Missing or duplicated edge')
        supplied = {(edge['left'], edge['right']): edge for edge in records}
        require(set(supplied) == set(expected), 'Incidence set mismatch')
        left_dual = {name: Fraction(0) for name in sizes}
        right_dual = {name: Fraction(0) for name in categories}
        overlap = Fraction(0)
        residuals = []
        for (label, category), (f, g, count, degree) in expected.items():
            edge = supplied[label, category]
            require(fraction(edge['f']) == f and fraction(edge['g']) == g, 'LP coefficient mismatch')
            require(edge['per_orbit_count'] == count and edge['left_degree'] == degree, 'Combinatorial coefficient mismatch')
            h, u, v = (fraction(edge[name]) for name in ['h', 'u', 'v'])
            require(h >= 0 and u >= 0 and v >= 0, 'Negative primal or dual variable')
            left_slack = f*x[label]-h
            right_slack = g*y[category]-h
            dual_slack = u+v-1
            require(min(left_slack, right_slack, dual_slack) >= 0, 'Edge feasibility failure')
            products = [u*left_slack, v*right_slack, h*dual_slack]
            require(all(value == 0 for value in products), 'Edge complementary slackness failure')
            residuals.append({'edge': [label, category], 'primal_left_slack': str(left_slack),
                              'primal_right_slack': str(right_slack), 'dual_slack': str(dual_slack),
                              'complementarity_products': [str(value) for value in products]})
            left_dual[label] += f*u
            right_dual[category] += g*v
            overlap += h
        node_residuals = []
        for kind, probabilities, weights, normalizer in [('x', x, left_dual, alpha), ('y', y, right_dual, beta)]:
            for name, probability in probabilities.items():
                slack = normalizer-weights[name]
                require(slack >= 0, 'Node dual infeasibility')
                require(probability*slack == 0, 'Node complementary slackness failure')
                node_residuals.append({'kind': kind, 'node': name, 'dual_slack': str(slack),
                                       'complementarity_product': str(probability*slack)})
        require(overlap == alpha+beta, 'Primal-dual objective gap')
        require(fraction(certificate['primal_overlap']) == overlap, 'Recorded primal objective mismatch')
        require(fraction(certificate['dual_overlap']) == alpha+beta, 'Recorded dual objective mismatch')
        require(fraction(certificate['delta']) == 1-overlap, 'Recorded error mismatch')
        reports.append({'r': certificate['row_limit'], 'verified_delta': str(1-overlap),
                        'primal_dual_gap': '0', 'edge_residuals': residuals, 'node_residuals': node_residuals})
    return reports


def tamper_tests(document):
    def change_delta(item):
        item['certificates'][0]['delta'] = '0'
    def change_probability(item):
        item['certificates'][0]['primal']['x']['R1'] = '1'
    def change_dual(item):
        item['certificates'][1]['dual']['alpha'] = '0'
    def omit_edge(item):
        item['certificates'][0]['edges'].pop()
    def change_crossratio_count(item):
        item['certificates'][0]['right_categories']['S2_1111']['orbits'] -= 1
    def change_dictionary(item):
        item['dictionary'][0][0] = 0
    def change_amplitudes(item):
        item['profile']['amplitudes'] = 'equal nonzero amplitudes'
    def change_supports(item):
        item['profile']['supports'] = 'singletons only'
    results = []
    for mutate in [change_delta, change_probability, change_dual, omit_edge, change_crossratio_count,
                   change_dictionary, change_amplitudes, change_supports]:
        damaged = copy.deepcopy(document)
        mutate(damaged)
        try:
            verify(damaged)
        except (ValueError, KeyError) as error:
            results.append({'attack': mutate.__name__, 'rejected': True, 'reason': str(error)})
        else:
            raise ValueError('Tampered certificate was accepted: '+mutate.__name__)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('certificate', nargs='?', default=str(ROOT/'DUAL_CERTIFICATES.json'))
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    document = json.loads(Path(args.certificate).read_text(encoding='utf8'))
    reports = verify(document)
    attacks = tamper_tests(document) if args.self_test else []
    result = {'scope': 'Exact compressed LP certificate, conditional on the written exhaustive reduction proof',
              'arithmetic': 'Fraction', 'solver_imported': False, 'results': reports,
              'tamper_tests': attacks, 'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'VERIFICATION_RESULTS.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({'verified': [{'r': x['r'], 'delta': x['verified_delta'], 'gap': x['primal_dual_gap']} for x in reports],
                      'tamper_tests_rejected': len(attacks)}, ensure_ascii=False))
