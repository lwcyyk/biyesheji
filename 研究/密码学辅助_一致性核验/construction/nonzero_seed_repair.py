"""Exact one-erasure repair after the rank-one nonzero-seed diagnosis."""
from nonzero_seed import attempt


def diagnose(field, residuals, labels, seed, blind=1):
    first = attempt(field, residuals, labels, seed, blind)
    if first['status'] != 'RETRY':
        return {**first, 'repair_opening': None, 'repaired': False}
    selected = first['candidate']
    e1 = field.total(field.mul(d, labels[i]) for i, d in enumerate(residuals) if i not in selected)
    z1 = field.mul(blind, e1)
    location = field.mul(z1, field.inverse(first['remainder_opening']))
    matches = [i for i, label in enumerate(labels) if label == location and i not in selected]
    if len(matches) != 1 or len(selected) + 1 > 2:
        return {**first, 'status': 'INCONCLUSIVE', 'repair_opening': z1, 'repaired': False,
                'online_products': first['online_products'] + 1}
    return {**first, 'status': 'ACCEPT', 'support': sorted(selected + matches),
            'repair_opening': z1, 'repaired': True, 'online_products': first['online_products'] + 1}
