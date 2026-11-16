"""Exact symbolic check of the n=5 closed-form extrapolation. No optimization calls."""
from pathlib import Path
import json
import sympy as sp

ROOT = Path(__file__).resolve().parent
q = sp.Symbol('q')
x = sp.Symbol('x')
Q = q-1
A = q*q-3*q+3
B = q*q-4*q+5
C = q**3-7*q*q+18*q-18
T = q*q+q-3
Z2 = 3*q**4+3*q**3-4*q*q-7*q+3
Z3 = 2*q**3+2*q*q+2*q-3

sizes = {'R1': q**3-4*q*q+6*q-4,
         'R2_32': 10*(q-2), 'R2_311': 10*A, 'R2_221': 15*(q-2)**2,
         'R2_2111': 10*(q-2)*B, 'R2_11111': (q-2)*C,
         'R3_32': 10, 'R3_311': 10*(q-2), 'R3_221': 15*(q-2),
         'R3_2111': 10*(q-2)*(q-3), 'R3_11111': (q-2)*(q-3)*(q-4)}
right = {'S1': (1, Q**3), 'S2_31': (4, Q**2), 'S2_22': (3, Q**2),
         'S2_211': (6, Q**3), 'S2_1111': (q-2, Q**3),
         'S3_2': (6, Q), 'S3_3': (4, Q**2), 'S3_4': (1, Q**3)}
degrees = {'R1': {'S1': 5}, 'R2_32': {'S2_31': 2, 'S2_22': 3},
           'R2_311': {'S2_31': 2, 'S2_211': 3},
           'R2_221': {'S2_22': 1, 'S2_211': 4},
           'R2_2111': {'S2_211': 3, 'S2_1111': 2}, 'R2_11111': {'S2_1111': 5},
           'R3_32': {'S3_2': 3, 'S3_3': 2}, 'R3_311': {'S3_2': 3, 'S3_4': 2},
           'R3_221': {'S3_3': 4, 'S3_4': 1},
           'R3_2111': {'S3_3': 2, 'S3_4': 3}, 'R3_11111': {'S3_4': 5}}


def rank(label):
    return int(label[1])


def sign_certificate(label, value):
    value = sp.cancel(value)
    assert not value.atoms(sp.Float), 'Floating-point atom detected'
    numerator, denominator = value.as_numer_denom()
    top = [int(c) for c in sp.Poly(sp.expand(numerator.subs(q, x+400)), x).all_coeffs()]
    bottom = [int(c) for c in sp.Poly(sp.expand(denominator.subs(q, x+400)), x).all_coeffs()]
    assert all(c >= 0 for c in top), (label, 'numerator', sp.factor(numerator))
    assert all(c >= 0 for c in bottom) and bottom[-1] > 0, (label, 'denominator')
    return {'label': label, 'expression': str(sp.factor(value)),
            'numerator_at_q_equals_x_plus_400': top,
            'denominator_at_q_equals_x_plus_400': bottom}


def check(row_limit):
    left = {key: value for key, value in sizes.items() if rank(key) <= row_limit}
    categories = {key: value for key, value in right.items() if rank(key) <= row_limit}
    if row_limit == 2:
        low = 3/Z2
        high = low*(1+T/(6*Q**2))
        alpha, beta, delta = 2*T/Z2, 1-5*T/Z2, 3*T/Z2
        u22 = (5*T*Q**2-Z2)/(Z2*(q-2)**2)
        u211 = (10*T/Z2-u22)/4
        u_new = (5*T*Q**3-Z2*(q-2)-2*(q-2)**2*Z2*u211)/(Z2*(q-2)*B)
        u_generic = (10*T/Z2-3*u_new)/2
        u = {('R2_32', 'S2_31'): 5*T/Z2, ('R2_311', 'S2_31'): 5*T/Z2,
             ('R2_221', 'S2_22'): u22, ('R2_221', 'S2_211'): u211,
             ('R2_2111', 'S2_211'): u_new, ('R2_2111', 'S2_1111'): u_generic,
             ('R2_11111', 'S2_1111'): alpha}
        high_category = 'S2_31'
    else:
        low = 2/Z3
        high = low*(1+1/(4*Q))
        alpha, beta, delta = 3/Z3, 1-5/Z3, 2/Z3
        u_new = 5*(4*q*q-17*q+22)/(4*Z3*(q-2)*(q-3))
        u_generic = 5*(2*q*q-13*q+14)/(6*Z3*(q-2)*(q-3))
        u = {('R2_32', 'S2_31'): 5/Z3, ('R2_311', 'S2_31'): 5/Z3,
             ('R3_32', 'S3_2'): 5/Z3, ('R3_311', 'S3_2'): 5/Z3,
             ('R3_221', 'S3_3'): 15/(4*Z3), ('R3_2111', 'S3_3'): u_new,
             ('R3_2111', 'S3_4'): u_generic, ('R3_11111', 'S3_4'): alpha}
        high_category = 'S3_2'
    high_types = {f'R{row_limit}_32', f'R{row_limit}_311'}
    p = {label: high if label in high_types else low if rank(label) == row_limit else sp.Integer(0)
         for label in left}
    z = {label: high if label == high_category else low if rank(label) == row_limit else sp.Integer(0)
         for label in categories}
    mass_x = {label: left[label]*p[label] for label in left}
    mass_y = {label: categories[label][0]*categories[label][1]*z[label] for label in categories}
    assert sp.cancel(sum(mass_x.values())-1) == 0
    assert sp.cancel(sum(mass_y.values())-1) == 0
    signs = [sign_certificate('alpha', alpha), sign_certificate('beta', beta)]
    left_sums = {label: sp.Integer(0) for label in left}
    right_sums = {label: sp.Integer(0) for label in categories}
    overlap = sp.Integer(0)
    for label in left:
        signs.append(sign_certificate('mass_'+label, mass_x[label]))
        for category, degree in degrees[label].items():
            f = sp.Rational(degree, 5)
            orbit_count, orbit_size = categories[category]
            g = left[label]*f/(orbit_count*orbit_size)
            edge_u = u.get((label, category), sp.Integer(0))
            edge_v = 1-edge_u
            density = high if label in high_types and category == high_category else low
            h = left[label]*f*density if rank(label) == row_limit else sp.Integer(0)
            left_slack = f*mass_x[label]-h
            right_slack = g*mass_y[category]-h
            for tag, expression in [('u', edge_u), ('v', edge_v), ('left_slack', left_slack), ('right_slack', right_slack)]:
                signs.append(sign_certificate(label+'/'+category+'/'+tag, expression))
            signs.append(sign_certificate(label+'/'+category+'/h', h))
            assert sp.cancel(edge_u*left_slack) == 0
            assert sp.cancel(edge_v*right_slack) == 0
            left_sums[label] += f*edge_u
            right_sums[category] += g*edge_v
            overlap += h
    for label in left:
        slack = sp.cancel(alpha-left_sums[label])
        signs.append(sign_certificate('dual_left_'+label, slack))
        assert sp.cancel(mass_x[label]*slack) == 0
    for category in categories:
        signs.append(sign_certificate('mass_'+category, mass_y[category]))
        slack = sp.cancel(beta-right_sums[category])
        signs.append(sign_certificate('dual_right_'+category, slack))
        assert sp.cancel(mass_y[category]*slack) == 0
    assert sp.cancel(overlap-(1-delta)) == 0
    assert sp.cancel(alpha+beta-overlap) == 0
    instance = json.loads((ROOT/'DUAL_CERTIFICATES.json').read_text(encoding='utf8'))['certificates'][row_limit-2]
    assert str(sp.cancel(delta.subs(q,4099))) == instance['delta']
    for label in left:
        assert str(sp.cancel(p[label].subs(q,4099))) == instance['primal']['kernel_densities'][label]
    return {'r': row_limit, 'delta': str(sp.factor(delta)), 'low': str(sp.factor(low)),
            'high': str(sp.factor(high)), 'alpha': str(sp.factor(alpha)), 'beta': str(sp.factor(beta)),
            'u_nonzero': {label+'/'+category: str(sp.factor(value)) for (label, category), value in u.items()},
            'sign_certificates': signs, 'identities_verified': True, 'instance_matches': True}


if __name__ == '__main__':
    results = [check(2), check(3)]
    delta1 = 1-(q**4-5*q**3+10*q*q-10*q+4)/Q**4
    order_checks = [sign_certificate('delta1_minus_delta2', delta1-3*T/Z2),
                    sign_certificate('delta2_minus_delta3', 3*T/Z2-2/Z3),
                    sign_certificate('delta3_positive', 2/Z3)]
    assert all(item['numerator_at_q_equals_x_plus_400'][-1] > 0 for item in order_checks)
    output = {'scope': 'Exact symbolic identities and coefficient-wise nonnegativity for q>=400',
              'assumption': 'The finite-field combinatorial reduction in MODEL_REDUCTION.md',
              'sympy_version': sp.__version__, 'floating_point_used': False, 'solver_imported': False,
              'results': results, 'strict_order_checks': order_checks}
    (ROOT/'SYMBOLIC_PROOF_CHECKS.json').write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps([{'r': item['r'], 'delta': item['delta'], 'sign_checks': len(item['sign_certificates'])} for item in results]))
