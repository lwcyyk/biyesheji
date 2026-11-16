"""CLEAR reference candidate for invertible row-space sparse diagnosis.

Uniform GL(k) sampling and authenticated arithmetic are assumptions here.
The executable MPC version is separate. No originality claim is made by code.
"""
from functools import lru_cache
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from field import Field
from general_mask import inverse_matrix


def rref(field, matrix):
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError('nonempty rectangular matrix')
    for row in matrix:
        for x in row: field.element(x)
    rows = [list(row) for row in matrix]; pivots = []; lead = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(lead, len(rows)) if rows[i][col]), None)
        if pivot is None: continue
        rows[lead], rows[pivot] = rows[pivot], rows[lead]
        scale = field.inverse(rows[lead][col])
        rows[lead] = [field.mul(scale, x) for x in rows[lead]]
        for i in range(len(rows)):
            if i == lead: continue
            scale = rows[i][col]
            rows[i] = [x ^ field.mul(scale, y) for x, y in zip(rows[i], rows[lead])]
        pivots.append(col); lead += 1
        if lead == len(rows): break
    return rows[:lead], pivots


@lru_cache(maxsize=32, typed=True)
def transforms(bits, k):
    field = Field(bits)
    if type(k) is not int or k < 1 or 2 * k > field.q: raise ValueError('threshold/field')
    points = tuple(range(2 * k))
    matrix = [[field.power(x, j) for j in range(2 * k)] for x in points]
    return points, tuple(tuple(row) for row in inverse_matrix(field, matrix))


def encode(arithmetic, residuals, labels, matrix, *, check_invertible=True):
    f = arithmetic.f; k = len(matrix)
    if not 1 <= k < len(residuals) or len(residuals) != len(labels): raise ValueError('sizes')
    if len(set(labels)) != len(labels) or any(len(row) != k for row in matrix): raise ValueError('labels/matrix')
    for x in list(residuals) + list(labels) + [x for row in matrix for x in row]: f.element(x)
    if check_invertible and len(rref(f, matrix)[0]) != k: raise ValueError('singular mask')
    s = [f.total(f.mul(d, f.power(a, j)) for d, a in zip(residuals, labels))
         for j in range(2 * k)]
    points, inverse = transforms(f.bits, k)
    transposed = [f.total(f.mul(inverse[j][h], s[j]) for j in range(2 * k))
                  for h in range(2 * k)]
    result = []
    for row in matrix:
        products = [arithmetic.product(f.poly(row, point), value)
                    for point, value in zip(points, transposed)]
        result.append([f.total(f.mul(z, f.power(point, j)) for z, point in zip(products, points))
                       for j in range(k + 1)])
    return result


def decode(field, public_matrix, labels):
    k = len(public_matrix)
    if not k or any(len(row) != k + 1 for row in public_matrix): raise ValueError('k by k+1')
    if len(set(labels)) != len(labels): raise ValueError('distinct labels')
    for x in labels: field.element(x)
    basis, pivots = rref(field, public_matrix)
    support = []
    for i, label in enumerate(labels):
        row = [field.power(label, j) for j in range(k + 1)]
        for b, pivot in zip(basis, pivots):
            scale = row[pivot]
            row = [x ^ field.mul(scale, y) for x, y in zip(row, b)]
        if not any(row): support.append(i)
    # Any <=k+1 distinct Vandermonde rows are independent. Count equality
    # therefore also certifies that the decoded rows span the whole row space.
    return support if len(support) == len(basis) else None


def choose_mask2(field, candidates, blinds):
    """Finite ideal sampler tape; only blinded determinant openings are public.

    Caller must supply iid uniform candidate entries and iid uniform nonzero
    blinds for security. Test tapes intentionally violate this for counterexamples.
    """
    if not candidates or len(candidates) != len(blinds): raise ValueError('random tape')
    openings = []
    for matrix, blind in zip(candidates, blinds):
        if len(matrix) != 2 or any(len(row) != 2 for row in matrix): raise ValueError('2 by 2')
        if field.element(blind) == 0: raise ValueError('nonzero sampler blind')
        for row in matrix:
            for x in row: field.element(x)
        a, b = matrix[0]; c, d = matrix[1]
        determinant = field.mul(a, d) ^ field.mul(b, c)
        openings.append(field.mul(blind, determinant))
        if determinant: return matrix, openings
    return None, openings
