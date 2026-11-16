"""AES-128 and GCM field maps for a bounded record-binding experiment.

Classical AES, not a new cipher. Clear execution uses Field; generated MPC uses
the same straight-line functions with secret arithmetic and public coefficients.
Independent cryptography-library vectors test the transformation and byte order.
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'construction'))
from field import Field
from general_mask import inverse_matrix


def derive_parameters():
    f = Field(128)
    for seed in range(2, 100):
        generator = f.power(seed, (f.q - 1) // 255)
        elements = {f.power(generator, i) for i in range(255)}
        if len(elements) == 255: break
    else: raise ArithmeticError('subfield generator')
    theta = next(x for x in sorted(elements) if f.poly([1, 1, 0, 1, 1, 0, 0, 0, 1], x) == 0)
    basis = [f.power(theta, i) for i in range(8)]
    def embed(byte): return f.total(basis[i] for i in range(8) if byte >> i & 1)
    moore = [[f.power(x, 1 << j) for j in range(8)] for x in basis]
    inverse = inverse_matrix(f, moore)
    def coefficients(targets):
        return [f.total(f.mul(a, b) for a, b in zip(row, targets)) for row in inverse]
    def affine(byte):
        return byte ^ ((byte << 1 | byte >> 7) & 255) ^ ((byte << 2 | byte >> 6) & 255) ^ ((byte << 3 | byte >> 5) & 255) ^ ((byte << 4 | byte >> 4) & 255)
    return {'theta': theta, 'embed': [embed(x) for x in range(256)],
            'sbox_linear': coefficients([embed(affine(1 << i)) for i in range(8)]),
            'reverse_linear': coefficients([1 << (7 - i) for i in range(8)]),
            'modulus': f.modulus}


class ClearOps:
    def __init__(self, params): self.f = Field(128); self.params = params; self.products = 0
    def add(self, a, b): return a ^ b
    def total(self, values): return self.f.total(values)
    def mul(self, a, b): self.products += 1; return self.f.mul(a, b)
    def public(self, a, b): return self.f.mul(a, b)
    def const(self, byte): return self.params['embed'][byte]


def linearized(value, coefficients, ops):
    powers = [value]
    for _ in range(7): powers.append(ops.mul(powers[-1], powers[-1]))
    return ops.total(ops.public(c, x) for c, x in zip(coefficients, powers))


def sbox(value, ops):
    x2 = ops.mul(value, value); x3 = ops.mul(x2, value)
    x6 = ops.mul(x3, x3); x12 = ops.mul(x6, x6)
    x15 = ops.mul(x12, x3); x30 = ops.mul(x15, x15)
    x60 = ops.mul(x30, x30); x120 = ops.mul(x60, x60)
    x240 = ops.mul(x120, x120); x252 = ops.mul(x240, x12)
    inverse = ops.mul(x252, x2)
    return ops.add(linearized(inverse, ops.params['sbox_linear'], ops), ops.const(0x63))


def expand_key(key, ops):
    assert len(key) == 16
    words = [list(key[4 * i:4 * i + 4]) for i in range(4)]
    rcon = 1
    for i in range(4, 44):
        temp = words[-1][:]
        if i % 4 == 0:
            temp = [sbox(x, ops) for x in temp[1:] + temp[:1]]
            temp[0] = ops.add(temp[0], ops.const(rcon))
            rcon = (rcon << 1) ^ (0x11b if rcon & 128 else 0)
        words.append([ops.add(a, b) for a, b in zip(words[i - 4], temp)])
    return [sum(words[4 * r:4 * r + 4], []) for r in range(11)]


def encrypt_block(block, keys, ops):
    state = [ops.add(a, b) for a, b in zip(block, keys[0])]
    for round_number in range(1, 11):
        state = [sbox(x, ops) for x in state]
        state = [state[4 * ((c + r) % 4) + r] for c in range(4) for r in range(4)]
        if round_number < 10:
            mixed = []
            for c in range(4):
                column = state[4 * c:4 * c + 4]
                doubled = [ops.public(ops.const(2), x) for x in column]
                mixed += [ops.total([doubled[i], doubled[(i + 1) % 4], column[(i + 1) % 4],
                                     column[(i + 2) % 4], column[(i + 3) % 4]]) for i in range(4)]
            state = mixed
        state = [ops.add(a, b) for a, b in zip(state, keys[round_number])]
    return state


def pack_embedded(block, ops):
    if len(block) != 16: raise ValueError('full block only')
    return ops.total(ops.public(1 << (8 * i), linearized(x, ops.params['reverse_linear'], ops))
                     for i, x in enumerate(block))


def pack_public(block):
    if len(block) != 16: raise ValueError('full block only')
    return int(f'{int.from_bytes(block, "big"):0128b}'[::-1], 2)


def unpack_public(value):
    return int(f'{value:0128b}'[::-1], 2).to_bytes(16, 'big')


def ghash(h, aad, ciphertext, ops):
    value = 0
    for data in (aad, ciphertext):
        for i in range(0, len(data), 16):
            block = data[i:i + 16].ljust(16, b'\0')
            value = ops.mul(ops.add(value, pack_public(block)), h)
    length = (len(aad) * 8).to_bytes(8, 'big') + (len(ciphertext) * 8).to_bytes(8, 'big')
    return ops.mul(ops.add(value, pack_public(length)), h)
