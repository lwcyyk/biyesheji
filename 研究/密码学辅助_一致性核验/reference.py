"""Independent small-field reference; shared syntax only, no candidate imports."""
from itertools import combinations, permutations, product


def mul(a, b, bits, modulus):
    value = 0
    for i in range(bits):
        if (b >> i) & 1: value ^= a << i
    while value.bit_length() > bits:
        value ^= modulus << (value.bit_length() - modulus.bit_length())
    return value


def power(a, e, bits, modulus):
    value = 1
    for bit in bin(e)[2:]:
        value = mul(value, value, bits, modulus)
        if bit == "1": value = mul(value, a, bits, modulus)
    return value


def determinant(matrix, bits, modulus):
    """Leibniz formula; signs disappear in characteristic two."""
    value = 0
    for permutation in permutations(range(len(matrix))):
        term = 1
        for i, j in enumerate(permutation): term = mul(term, matrix[i][j], bits, modulus)
        value ^= term
    return value


def moments(vector, labels, size, bits, modulus):
    out = []
    for j in range(size):
        value = 0
        for x, label in zip(vector, labels):
            value ^= mul(x, power(label, j, bits, modulus), bits, modulus)
        out.append(value)
    return out


def sparse_table(n, k, labels, bits, modulus):
    """Finite exact decoder table, used only for small exhaustive tests."""
    table = {}
    for size in range(k + 1):
        for indices in combinations(range(n), size):
            for values in product(range(1, 1 << bits), repeat=size):
                vector = [0] * n
                for i, value in zip(indices, values): vector[i] = value
                fingerprint = tuple(moments(vector, labels, 2 * k, bits, modulus))
                if fingerprint in table and table[fingerprint] != vector:
                    raise AssertionError("sparse moment map is not injective")
                table[fingerprint] = vector
    return table


def decode_prony(sequence, labels, bits, modulus):
    """Independent explicit Prony solver, up to two nonzero coordinates."""
    q = 1 << bits
    def mm(a, b): return mul(a, b, bits, modulus)
    def inv(a):
        if not a: raise ValueError("zero")
        return power(a, q - 2, bits, modulus)
    def check(indices, weights):
        if any(w == 0 for w in weights): return False
        v = [0] * len(labels)
        for i, w in zip(indices, weights): v[i] = w
        return moments(v, labels, len(sequence), bits, modulus) == sequence
    if not any(sequence): return []
    a, b = sequence[:2]
    if a:
        alpha = mm(b, inv(a))
        if alpha in labels:
            index = labels.index(alpha)
            if check([index], [a]): return [index]
    if len(sequence) != 4: return None
    c, d = sequence[2:]
    determinant = mm(b, b) ^ mm(a, c)
    if not determinant: return None
    denominator = inv(determinant)
    c1 = mm(mm(c, b) ^ mm(a, d), denominator)
    c2 = mm(mm(b, d) ^ mm(c, c), denominator)
    roots = [i for i, x in enumerate(labels) if mm(x, x) ^ mm(c1, x) ^ c2 == 0]
    if len(roots) != 2: return None
    x, y = [labels[i] for i in roots]
    first = mm(b ^ mm(y, a), inv(x ^ y)); second = a ^ first
    return roots if check(roots, [first, second]) else None


def simulate(residuals, *, bits, modulus, norm_constant, gate_challenges, gate_blind, attempts, g=3, amplified=True):
    """Independent clear algebra reference for the full k=2 execution."""
    def mm(a, b): return mul(a, b, bits, modulus)
    def pp(a, e): return power(a, e, bits, modulus)
    def total(values):
        z = 0
        for v in values: z ^= v
        return z
    def polynomial(v, x): return total(mm(a, pp(x, i)) for i, a in enumerate(v))
    def norm(a, b): return mm(a, a) ^ mm(a, b) ^ mm(norm_constant, mm(b, b))
    labels = [pp(g, i) for i in range(len(residuals))]
    determinants = [determinant([[polynomial(residuals, mm(pp(g, r), x)) for x in row] for r in range(3)], bits, modulus)
                    for row in gate_challenges]
    opening = mm(gate_blind, norm(*determinants) if amplified else determinants[0])
    answer = {"gate_opening": opening, "attempts": []}
    if opening: return dict(answer, status="MANY", support=None)
    for attempt in attempts:
        weighted = [mm(value, polynomial(attempt["mask"], label)) for value, label in zip(residuals, labels)]
        observed = moments(weighted, labels, 4, bits, modulus)
        candidate = decode_prony(observed, labels, bits, modulus)
        row = {"masked_moments": observed, "candidate": candidate}; answer["attempts"].append(row)
        if candidate is None: return dict(answer, status="INCONCLUSIVE", support=None)
        tail = [0 if i in candidate else value for i, value in enumerate(residuals)]
        remainders = [polynomial(tail, challenge) for challenge in attempt["challenges"]]
        checked = mm(attempt["blind"], norm(*remainders) if amplified else remainders[0])
        row.update(verification_challenges=attempt["challenges"], verification_opening=checked)
        if checked == 0: return dict(answer, status="LOCATED" if candidate else "ALL_VALID", support=candidate)
    return dict(answer, status="INCONCLUSIVE", support=None)
