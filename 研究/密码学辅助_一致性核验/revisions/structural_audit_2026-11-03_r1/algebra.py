"""Producer/reference arithmetic. Checker has a separate implementation."""
from itertools import combinations


class Field:
    def __init__(self, q):
        if type(q) is not int or q not in (3, 4): raise ValueError('supported fields: GF3/GF4')
        self.q = q
    def add(self, a, b): return (a + b) % 3 if self.q == 3 else a ^ b
    def neg(self, a): return (-a) % 3 if self.q == 3 else a
    def mul(self, a, b):
        if self.q == 3: return a * b % 3
        z = 0
        while b:
            if b & 1: z ^= a
            b >>= 1; a <<= 1
            if a & 4: a ^= 7
        return z
    def power(self, a, n):
        z = 1
        for _ in range(n): z = self.mul(z, a)
        return z
    def inv(self, a):
        if not a: raise ValueError('zero inverse')
        return self.power(a, self.q - 2)
    def total(self, xs):
        z = 0
        for x in xs: z = self.add(z, x)
        return z


def rref(f, matrix):
    a = [row[:] for row in matrix]; pivots = []; lead = 0
    if not a: return [], []
    for col in range(len(a[0])):
        pivot = next((i for i in range(lead, len(a)) if a[i][col]), None)
        if pivot is None: continue
        a[lead], a[pivot] = a[pivot], a[lead]
        s = f.inv(a[lead][col]); a[lead] = [f.mul(s, x) for x in a[lead]]
        for i in range(len(a)):
            if i == lead: continue
            s = a[i][col]; a[i] = [f.add(x, f.neg(f.mul(s, y))) for x, y in zip(a[i], a[lead])]
        pivots.append(col); lead += 1
        if lead == len(a): break
    return a, pivots


def rank(f, a): return len(rref(f, a)[1])
def columns(v, s): return [[row[i] for i in s] for row in v]
def identity(n): return [[int(i == j) for j in range(n)] for i in range(n)]
def inverse(f, a):
    n = len(a); reduced, pivots = rref(f, [row[:] + eye for row, eye in zip(a, identity(n))])
    if pivots[:n] != list(range(n)): raise ValueError('singular')
    return [row[n:] for row in reduced]
def multiply(f, a, b):
    if not b: return [[] for _ in a]
    return [[f.total(f.mul(a[i][l], b[l][j]) for l in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
def all_subsets(n):
    return [list(s) for size in range(n + 1) for s in combinations(range(n), size)]
def independent_sets(v, q):
    f = Field(q)
    return [s for s in all_subsets(len(v[0])) if rank(f, columns(v, s)) == len(s)]


def left_inverse(f, b):
    """B has full column rank, even if the ambient row dimension is larger."""
    d = len(b[0]) if b else 0
    if d == 0: return []
    for rows in combinations(range(len(b)), d):
        square = [b[i] for i in rows]
        if rank(f, square) == d:
            inv = inverse(f, square); result = [[0] * len(b) for _ in range(d)]
            for i in range(d):
                for j, original in enumerate(rows): result[i][original] = inv[i][j]
            return result
    raise ValueError('columns not independent')
