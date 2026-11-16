"""Clear k=2 exact-with-abort diagnosis using a nonzero coefficient vector.

Precondition for the layer: at most two nonzero residuals. The existing
private sparse gate remains mandatory when the promise is not trusted.
No claim of novel finite-field primitives is made.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kernel import IdealArithmetic, masked_moments, decode


def sample(field, triples, blinds):
    if not triples or len(triples) != len(blinds): raise ValueError('sampler tape')
    ar = IdealArithmetic(field); openings = []
    for triple, blind in zip(triples, blinds):
        if len(triple) != 3: raise ValueError('triple shape')
        for x in triple: field.element(x)
        if not field.element(blind): raise ValueError('nonzero blind')
        a, b, ab = triple
        if field.mul(a, b) != ab: raise ValueError('invalid ideal triple')
        norm = ar.product(a, a) ^ ab ^ field.mul(field.norm_constant(), ar.product(b, b))
        opened = ar.product(norm, blind); openings.append(opened)
        if opened:
            return {'seed': [a, b], 'openings': openings,
                    'online_products': ar.products, 'random_triples': len(openings)}
    return {'seed': None, 'openings': openings, 'online_products': ar.products,
            'random_triples': len(openings)}


def attempt(field, residuals, labels, seed, blind=1):
    if len(seed) != 2 or not any(seed): raise ValueError('nonzero 2-vector required')
    if len(labels) != len(residuals) or len(set(labels)) != len(labels): raise ValueError('distinct labels')
    for x in list(seed) + list(residuals) + list(labels): field.element(x)
    if not field.element(blind): raise ValueError('nonzero verification blind')
    ar = IdealArithmetic(field)
    moments = masked_moments(ar, residuals, labels, seed)
    proposed = decode(field, moments, labels, 2)
    if proposed is None:
        return {'status': 'INCONCLUSIVE', 'reason': 'decoder_reject', 'moments': moments,
                'candidate': None, 'online_products': ar.products}
    remaining_sum = field.total(d for i, d in enumerate(residuals) if i not in proposed)
    opening = ar.product(remaining_sum, blind)
    return {'status': 'ACCEPT' if opening == 0 else 'RETRY', 'candidate': proposed,
            'moments': moments, 'remainder_opening': opening, 'online_products': ar.products}
