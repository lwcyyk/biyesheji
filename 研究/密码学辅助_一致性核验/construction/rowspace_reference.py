"""Independent GF2n and k=2 public decoder; no candidate imports."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import reference


def encode(values, labels, matrix, bits, modulus):
    k = len(matrix); s = reference.moments(values, labels, 2 * k, bits, modulus)
    result = []
    for row in matrix:
        output = []
        for j in range(k + 1):
            value = 0
            for a, coefficient in enumerate(row):
                value ^= reference.mul(coefficient, s[a + j], bits, modulus)
            output.append(value)
        result.append(output)
    return result


def decode2(matrix, labels, bits, modulus):
    a, b = matrix
    def mm(x, y): return reference.mul(x, y, bits, modulus)
    def inv(x): return reference.power(x, (1 << bits) - 2, bits, modulus)
    cross = [mm(a[1], b[2]) ^ mm(a[2], b[1]),
             mm(a[2], b[0]) ^ mm(a[0], b[2]),
             mm(a[0], b[1]) ^ mm(a[1], b[0])]
    if any(cross):
        found = [i for i, x in enumerate(labels) if cross[0] ^ mm(cross[1], x) ^ mm(cross[2], mm(x, x)) == 0]
        return found if len(found) == 2 else None
    row = a if any(a) else b
    if not any(row): return []
    if row[0] == 0: return None
    label = mm(row[1], inv(row[0]))
    if label not in labels or row[2] != mm(row[0], mm(label, label)): return None
    return [labels.index(label)]
