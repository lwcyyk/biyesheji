"""Reused standard AES arithmetic functions. Source provenance in aes_reuse.json."""

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
