"""Ideal arithmetic model for value-hiding, at-most-k fault localization.

All values are CLEAR in this file. Arithmetic gate counters are not real MPC
benchmarks. Input fixation, authenticated shares and secure random sampling are
ASSUMED ideal services, not implemented cryptographic protections.
"""
from dataclasses import dataclass
from field import Field


@dataclass(frozen=True)
class FrozenBatch:
    batch_id: str
    context: tuple
    residuals: tuple

    def __post_init__(self):
        if not isinstance(self.batch_id, str) or not self.batch_id:
            raise ValueError("batch id")
        if not isinstance(self.context, tuple) or not isinstance(self.residuals, tuple):
            raise ValueError("immutable batch/context required")


class IdealArithmetic:
    def __init__(self, field):
        self.f = field; self.products = 0

    def product(self, a, b):
        self.products += 1
        return self.f.mul(a, b)


def det_circuit(matrix, arithmetic):
    """Division-free circuits. No data-dependent pivoting on private values."""
    f = arithmetic.f; mm = arithmetic.product; n = len(matrix)
    if n == 1: return matrix[0][0]
    if n == 2: return mm(matrix[0][0], matrix[1][1]) ^ mm(matrix[0][1], matrix[1][0])
    if n == 3:
        a, b, c = matrix[0]; d, e, z = matrix[1]; h, i, j = matrix[2]
        return mm(a, mm(e, j) ^ mm(z, i)) ^ mm(b, mm(d, j) ^ mm(z, h)) ^ mm(c, mm(d, i) ^ mm(e, h))
    raise ValueError("prototype implements k=1 or k=2 only")


def rank_matrix(f, residuals, g, challenges):
    return [[f.poly(residuals, f.mul(f.power(g, row), x))
             for x in challenges] for row in range(len(challenges))]


def moments_naive(f, residuals, labels, coefficients, k):
    """Independent algebra expression, not a multiplication-efficient circuit."""
    masked = [f.mul(x, f.poly(coefficients, label)) for x, label in zip(residuals, labels)]
    return [f.total(f.mul(value, f.power(label, j)) for value, label in zip(masked, labels)) for j in range(2 * k)]


def middle_product_five(arithmetic, coefficients, s):
    if len(coefficients) != 2 or len(s) != 5: raise ValueError("2-by-5 middle product")
    f = arithmetic.f; root = f.fifth_root(); points = [f.power(root, j) for j in range(5)]
    products = [arithmetic.product(f.poly([coefficients[1], coefficients[0]], x), f.poly(s, x)) for x in points]
    return [f.total(f.mul(value, f.power(x, (5 - degree) % 5)) for value, x in zip(products, points)) for degree in range(1, 5)]


def private_norm(arithmetic, a, b):
    f = arithmetic.f
    # Conservative count: squares are charged; not every authenticated backend
    # provides free Frobenius conversion under the same MAC key.
    return arithmetic.product(a, a) ^ arithmetic.product(a, b) ^ f.mul(f.norm_constant(), arithmetic.product(b, b))


def masked_moments(arithmetic, residuals, labels, coefficients, *, fast=True):
    f = arithmetic.f; k = len(coefficients)
    s = [f.total(f.mul(value, f.power(label, j)) for value, label in zip(residuals, labels))
         for j in range(3 * k - 1)]
    if k == 2 and fast:
        # A(X)=r1+r0*X; B(X)=s0+...+s4*X^4. Product modulo X^5-1.
        # Degree-5 wrap affects only coefficient 0; coefficients 1..4 are wanted.
        return middle_product_five(arithmetic, coefficients, s)
    return [f.total(arithmetic.product(coefficients[a], s[j + a]) for a in range(k)) for j in range(2 * k)]


def berlekamp_massey(f, sequence):
    c = [1]; b = [1]; length = 0; shift = 1; old = 1
    for position, value in enumerate(sequence):
        discrepancy = value
        for j in range(1, length + 1):
            if j < len(c): discrepancy ^= f.mul(c[j], sequence[position - j])
        if discrepancy == 0: shift += 1; continue
        previous = c[:]; factor = f.mul(discrepancy, f.inverse(old))
        needed = len(b) + shift
        c += [0] * max(0, needed - len(c))
        for j, coefficient in enumerate(b): c[j + shift] ^= f.mul(factor, coefficient)
        if 2 * length <= position:
            length = position + 1 - length; b = previous; old = discrepancy; shift = 1
        else: shift += 1
    return c[:length + 1], length


def solve_public_linear(f, matrix, target):
    # These are PUBLIC masked moments and PUBLIC labels, not secret state.
    n = len(target); rows = [row[:] + [value] for row, value in zip(matrix, target)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if rows[r][col]), None)
        if pivot is None: return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        inverse = f.inverse(rows[col][col]); rows[col] = [f.mul(x, inverse) for x in rows[col]]
        for r in range(n):
            if r == col: continue
            factor = rows[r][col]
            if factor: rows[r] = [a ^ f.mul(factor, b) for a, b in zip(rows[r], rows[col])]
    return [row[-1] for row in rows]


def decode(f, moments, labels, k):
    recurrence, length = berlekamp_massey(f, moments)
    if length > k: return None
    if length == 0: return [] if all(x == 0 for x in moments) else None
    roots = [i for i, label in enumerate(labels) if f.poly(list(reversed(recurrence)), label) == 0]
    if len(roots) != length: return None
    matrix = [[f.power(labels[i], j) for i in roots] for j in range(length)]
    weights = solve_public_linear(f, matrix, moments[:length])
    if weights is None or any(w == 0 for w in weights): return None
    recomputed = [f.total(f.mul(w, f.power(labels[i], j)) for i, w in zip(roots, weights)) for j in range(len(moments))]
    return roots if recomputed == moments else None


class Session:
    """Ideal single-use state machine; NOT a tamper-resistant implementation."""
    def __init__(self, field, batch, k, *, g=3, max_attempts=2, amplified=True):
        if type(k) is not int or k not in (1, 2) or not k < len(batch.residuals): raise ValueError("k/profile")
        if type(max_attempts) is not int or not 1 <= max_attempts <= 4: raise ValueError("attempt bound")
        if any(type(x) is not int for x in batch.residuals): raise ValueError("residual types")
        for value in batch.residuals: field.element(value)
        self.f = field; self.batch = batch; self.k = k; self.g = g
        self._binding = (batch.batch_id, batch.context, batch.residuals)
        if type(amplified) is not bool: raise ValueError("amplification flag")
        self.amplified = amplified
        self.labels = field.labels(len(batch.residuals), g); self.limit = max_attempts
        self.phase = "FROZEN"; self.used = 0; self.arithmetic = IdealArithmetic(field)
        self.transcript = {"model": "IDEAL_ARITHMETIC_ONLY", "batch_id": batch.batch_id,
                           "context": list(batch.context), "k": k, "amplified": amplified, "attempts": []}
        self.result = None

    def check_context(self, batch_id, context):
        self.assert_frozen()
        if batch_id != self.batch.batch_id or tuple(context) != self.batch.context: raise ValueError("bound context changed")

    def assert_frozen(self):
        if (self.batch.batch_id, self.batch.context, self.batch.residuals) != self._binding:
            raise ValueError("ideal input binding violated")

    def gate(self, challenge_sets, blind, *, batch_id, context):
        self.check_context(batch_id, context)
        if self.phase != "FROZEN": raise ValueError("gate replay/reuse")
        if len(challenge_sets) != (2 if self.amplified else 1): raise ValueError("gate repetition count")
        for challenges in challenge_sets:
            if len(challenges) != self.k + 1 or any(not self.f.element(x) for x in challenges): raise ValueError("gate challenges")
        if not self.f.element(blind): raise ValueError("nonzero private gate blind required")
        values = [det_circuit(rank_matrix(self.f, self.batch.residuals, self.g, challenges), self.arithmetic) for challenges in challenge_sets]
        value = private_norm(self.arithmetic, *values) if self.amplified else values[0]
        opening = self.arithmetic.product(blind, value)
        self.transcript.update(gate_challenges=[list(x) for x in challenge_sets], gate_opening=opening)
        if opening:
            self.phase = "CLOSED"; self.result = {"status": "MANY", "support": None}
        else: self.phase = "READY"
        return opening

    def propose(self, coefficients):
        self.assert_frozen()
        if self.phase != "READY": raise ValueError("candidate before gate/after close")
        if len(coefficients) != self.k: raise ValueError("mask coefficient count")
        for x in coefficients: self.f.element(x)
        if self.used >= self.limit: raise ValueError("attempt limit")
        self.used += 1
        moments = masked_moments(self.arithmetic, self.batch.residuals, self.labels, coefficients)
        found = decode(self.f, moments, self.labels, self.k)
        event = {"masked_moments": moments, "candidate": found}
        self.transcript["attempts"].append(event)
        if found is None:
            self.phase = "CLOSED"; self.result = {"status": "INCONCLUSIVE", "support": None, "reason": "public decoder rejects"}
        else:
            self.phase = "VERIFY"; self.pending = found
        return found

    def verify(self, challenges, blind):
        self.assert_frozen()
        if self.phase != "VERIFY": raise ValueError("no committed candidate")
        if len(challenges) != (2 if self.amplified else 1): raise ValueError("verification repetitions")
        if any(not self.f.element(x) for x in challenges) or not self.f.element(blind): raise ValueError("nonzero verification randomness")
        remaining = [0 if i in self.pending else x for i, x in enumerate(self.batch.residuals)]
        values = [self.f.poly(remaining, x) for x in challenges]
        value = private_norm(self.arithmetic, *values) if self.amplified else values[0]
        opening = self.arithmetic.product(blind, value)
        self.transcript["attempts"][-1].update(verification_challenges=list(challenges), verification_opening=opening)
        if not opening:
            self.phase = "CLOSED"; self.result = {"status": "ALL_VALID" if not self.pending else "LOCATED", "support": self.pending[:]}
        elif self.used == self.limit:
            self.phase = "CLOSED"; self.result = {"status": "INCONCLUSIVE", "support": None, "reason": "mask retry budget exhausted"}
        else: self.phase = "READY"
        return opening

    def finish(self):
        self.assert_frozen()
        if self.result is None: return {"status": "INCONCLUSIVE", "reason": "unfinished ideal execution"}
        return {**self.result, "transcript": self.transcript, "secret_products": self.arithmetic.products,
                "not_implemented": ["real MPC", "cryptographic input fixation", "secure random preprocessing", "TLS binding"]}


def run(field, residuals, *, gate_challenges, gate_blind, attempts, k=2, g=3, context=("synthetic", 0), batch_id="toy", amplified=True):
    if not attempts: raise ValueError("explicit harness randomness required")
    session = Session(field, FrozenBatch(batch_id, tuple(context), tuple(residuals)), k, g=g, max_attempts=len(attempts), amplified=amplified)
    session.gate(gate_challenges, gate_blind, batch_id=batch_id, context=context)
    for a in attempts:
        if session.phase == "CLOSED": break
        session.propose(a["mask"])
        if session.phase == "VERIFY": session.verify(a["challenges"], a["blind"])
    return session.finish()
