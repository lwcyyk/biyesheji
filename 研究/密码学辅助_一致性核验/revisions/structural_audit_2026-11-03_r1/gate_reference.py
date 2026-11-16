"""A fixed arithmetic circuit for exact membership in an explicit support family.

Interpreter values are CLEAR. This is an L0 circuit reference, not secure MPC.
The circuit has exactly one public opening and no data-dependent address/branch.
"""
from algebra import Field
from checker import profile_check, CheckFailure
import hashlib
import json


def build(profile):
    profile = json.loads(json.dumps(profile))
    q, n, _, family = profile_check(profile)
    if profile['support_policy']['coverage'] != 'exact':
        raise CheckFailure('INCONCLUSIVE', 'GATE_REQUIRES_EXACT_FAMILY')
    f = Field(q); nodes = []; secret = []; depth = []; constants = {}
    def emit(op, *args):
        if op == 'const' and args[0] in constants: return constants[args[0]]
        index = len(nodes); nodes.append((op, *args))
        secret.append(op == 'input' or op in ('add', 'mul') and any(secret[a] for a in args))
        depth.append(0 if op in ('const', 'input') else max(depth[a] for a in args) + int(op == 'mul' and all(secret[a] for a in args)))
        if op == 'const': constants[args[0]] = index
        return index
    zero, one = emit('const', 0), emit('const', 1)
    def mul(a, b): return emit('mul', a, b)
    def add(a, b): return emit('add', a, b)
    def power(a, e):
        result = one
        while e:
            if e & 1: result = mul(result, a)
            e >>= 1
            if e: a = mul(a, a)
        return result
    bits = [power(emit('input', i), q - 1) for i in range(n)]
    complements = [add(one, mul(emit('const', f.neg(1)), bit)) for bit in bits]
    accepted = zero
    for support in sorted(family):
        term = one
        for i in range(n): term = mul(term, bits[i] if i in support else complements[i])
        accepted = add(accepted, term)
    output = emit('open', accepted)
    return {'q': q, 'n': n, 'nodes': nodes, 'output': output,
            'profile_digest': hashlib.sha256(json.dumps(profile, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest(),
            'metrics': {'nodes': len(nodes), 'openings': 1,
                        'secret_multiplications': sum(node[0] == 'mul' and secret[node[1]] and secret[node[2]] for node in nodes),
                        'multiplicative_depth': depth[output], 'wire_memory_upper_bound': len(nodes),
                        'data_dependent_branches': 0, 'data_dependent_addresses': 0},
            'leakage': 'only the final support-membership bit; public profile and fixed dimensions'}


def evaluate(circuit, values):
    values = tuple(values)
    f = Field(circuit['q'])
    if len(values) != circuit['n'] or any(type(x) is not int or not 0 <= x < f.q for x in values):
        raise ValueError('invalid field input')
    wires = []; opened = []
    for node in circuit['nodes']:
        op, args = node[0], node[1:]
        if op == 'const': value = args[0]
        elif op == 'input': value = values[args[0]]
        elif op == 'add': value = f.add(wires[args[0]], wires[args[1]])
        elif op == 'mul': value = f.mul(wires[args[0]], wires[args[1]])
        elif op == 'open': value = wires[args[0]]; opened.append(value)
        else: raise ValueError('unknown circuit operation')
        wires.append(value)
    if len(opened) != 1 or opened[0] not in (0, 1): raise AssertionError('invalid gate output')
    return {'accepted': bool(opened[0]), 'public_transcript': opened, 'executed_nodes': len(wires)}


def direct_membership(profile, values):
    """Independent non-arithmetic truth table for testing."""
    support = tuple(i for i, value in enumerate(values) if value != 0)
    return support in {tuple(sorted(s)) for s in profile['support_policy']['supports']}
