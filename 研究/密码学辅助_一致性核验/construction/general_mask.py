"""General support-hiding moment layer; CLEAR algebra, not secure MPC.

Uses classical transposed polynomial multiplication. No claim that the
transposition principle or its bilinear complexity is newly invented here.
"""
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from field import Field


def inverse_matrix(field, matrix):
    size = len(matrix)
    if any(len(row) != size for row in matrix): raise ValueError('square matrix')
    rows = [list(row) + [int(i == j) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        if pivot is None: raise ValueError('singular matrix')
        rows[pivot], rows[column] = rows[column], rows[pivot]
        factor = field.inverse(rows[column][column])
        rows[column] = [field.mul(x, factor) for x in rows[column]]
        for i in range(size):
            if i == column: continue
            factor = rows[i][column]
            rows[i] = [x ^ field.mul(factor, y) for x, y in zip(rows[i], rows[column])]
    return [row[size:] for row in rows]


@lru_cache(maxsize=40, typed=True)
def transforms(bits, k):
    field = Field(bits)
    if type(k) is not int or not 1 <= k or 3 * k - 1 > field.q:
        raise ValueError('requires 1 <= k and 3k-1 <= field cardinality')
    size = 3 * k - 1
    points = list(range(size))
    evaluation = [[field.power(point, j) for j in range(size)] for point in points]
    inverse = inverse_matrix(field, evaluation)
    return tuple(points), tuple(tuple(row) for row in inverse)


def middle_product(arithmetic, mask, moments):
    """U_j = sum_a r_a s_(j+a), with exactly 3k-1 bilinear products.

    Input validation occurs outside the cached transform. Any 3k-1 distinct
    field points suffice; no roots of unity or characteristic restriction.
    """
    field = arithmetic.f; k = len(mask)
    if not k or len(moments) != 3 * k - 1: raise ValueError('shape')
    for value in list(mask) + list(moments): field.element(value)
    points, inverse = transforms(field.bits, k)
    r_eval = [field.poly(mask, point) for point in points]
    transposed = [field.total(field.mul(inverse[j][h], moments[j])
                               for j in range(len(moments))) for h in range(len(points))]
    products = [arithmetic.product(a, b) for a, b in zip(r_eval, transposed)]
    return [field.total(field.mul(products[h], field.power(points[h], j))
                        for h in range(len(points))) for j in range(2 * k)]


def mask_moments(arithmetic, residuals, labels, mask):
    field = arithmetic.f; k = len(mask)
    if len(residuals) != len(labels) or len(set(labels)) != len(labels):
        raise ValueError('distinct labels covering all residuals')
    if not 1 <= k < len(residuals): raise ValueError('threshold')
    for value in list(residuals) + list(labels) + list(mask): field.element(value)
    s = [field.total(field.mul(d, field.power(a, j)) for d, a in zip(residuals, labels))
         for j in range(3 * k - 1)]
    return middle_product(arithmetic, mask, s)
