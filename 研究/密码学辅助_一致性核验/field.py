"""Binary-field arithmetic for algebra experiments, NOT constant-time crypto."""
from functools import lru_cache


class Field:
    MODULI = {4: 0x13, 8: 0x11B, 128: (1 << 128) | 0x87}

    def __init__(self, bits):
        if type(bits) is not int or bits not in self.MODULI:
            raise ValueError("registered field required")
        self.bits = bits; self.q = 1 << bits; self.modulus = self.MODULI[bits]

    def element(self, value):
        if type(value) is not int or not 0 <= value < self.q:
            raise ValueError("invalid field element")
        return value

    @lru_cache(maxsize=65536, typed=True)
    def mul(self, a, b):
        self.element(a); self.element(b); result = 0
        while b:
            if b & 1: result ^= a
            b >>= 1; a <<= 1
            if a & self.q: a ^= self.modulus
        return result

    def power(self, value, exponent):
        self.element(value)
        if type(exponent) is not int or exponent < 0: raise ValueError("exponent")
        result = 1
        while exponent:
            if exponent & 1: result = self.mul(result, value)
            exponent >>= 1; value = self.mul(value, value)
        return result

    def inverse(self, value):
        if not value: raise ValueError("zero inverse")
        return self.power(value, self.q - 2)

    def total(self, values):
        result = 0
        for value in values: result ^= self.element(value)
        return result

    def poly(self, coefficients, point):
        result = 0
        for coefficient in reversed(coefficients):
            result = self.mul(result, point) ^ self.element(coefficient)
        return result

    def labels(self, count, base=3):
        values = [self.power(base, i) for i in range(count)]
        if len(set(values)) != count or 0 in values: raise ValueError("insufficient order of g")
        return values

    @lru_cache(maxsize=8)
    def fifth_root(self):
        if (self.q - 1) % 5: raise ValueError("field has no fifth roots")
        for value in range(2, min(self.q, 1000)):
            candidate = self.power(value, (self.q - 1) // 5)
            if candidate != 1 and self.power(candidate, 5) == 1: return candidate
        raise ValueError("root search failed")

    def trace(self, value):
        term = value; result = 0
        for _ in range(self.bits):
            result ^= term; term = self.mul(term, term)
        if result not in (0, 1): raise ArithmeticError("field/trace inconsistent")
        return result

    @lru_cache(maxsize=8)
    def norm_constant(self):
        # Tr(c)=1 makes X^2+X+c irreducible over this binary field.
        for i in range(self.bits):
            candidate = 1 << i
            if self.trace(candidate) == 1: return candidate
        raise ArithmeticError("trace-one element not found")
