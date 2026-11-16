"""Stage-5 generic gate reference only. No structural optimized protocol runs."""
from pathlib import Path
import hashlib
import json
import random
from profiles import record_profiles

REV = Path(__file__).resolve().parent


def main():
    target = REV / 'gate_mpc'; target.mkdir(exist_ok=False)
    original, restricted = record_profiles()
    families = {'original': original['support_policy']['supports'],
                'restricted': restricted['support_policy']['supports']}
    supports = [[], [0], [1], [0,1], [1,3], [0,1], [2], [0,1,2]]
    rng = random.Random(216110301); inputs = [[], []]; cases = []
    for i, support in enumerate(supports):
        values = [rng.randrange(1, 1 << 128) if j in support else 0 for j in range(4)]
        for value in values:
            share = rng.getrandbits(128); inputs[0].append(share); inputs[1].append(share ^ value)
        cases.append({'case': i, 'support': support, 'values': values,
                      'expected': {key: support in family for key, family in families.items()}})
    fixture = {'kind': 'GENERIC_GATE_REFERENCE_SYNTHETIC_RESIDUALS_NOT_SOURCE_BOUND',
               'party_inputs': inputs, 'cases': cases,
               'source_case_relation': 'support patterns match prior AES/GCM eight scenarios; residual values regenerated, not a new AES run'}
    (target / 'fixture.json').write_text(json.dumps(fixture, indent=2))
    source = '''from Compiler.types import sgf2n, cgf2n, regint
from Compiler.library import print_ln, check_point, for_range, runtime_error_if

families = FAMILIES_PLACEHOLDER
profile = program.args[1]
assert profile in families
family = families[profile]
cases = 8

def nonzero_bit(x):
    # x^(2^128-1), fixed binary addition chain. Simple reference, not optimized.
    result = x
    for _ in range(127): result = result * result * x
    return result

@for_range(cases)
def gate_case(index):
    d = [sgf2n.get_input_from(0) + sgf2n.get_input_from(1) for _ in range(4)]
    check_point()  # Inputs fixed and authenticated before any result is exposed.
    bits = [nonzero_bit(x) for x in d]
    accepted = sgf2n(0)
    for support in family:
        term = sgf2n(1)
        for i in range(4): term *= bits[i] if i in support else (1 - bits[i])
        accepted += term
    public = accepted.reveal()
    check_point()
    runtime_error_if((public != cgf2n(0)) * (public != cgf2n(1)), 'NOT_A_BOOLEAN_RESULT')
    print_ln('GATE case=%s accepted=%s', index, regint(public))
check_point()
print_ln('SCOPE GENERIC_SUPPORT_GATE_REFERENCE_ONLY')
print_ln('PROTOCOL_DONE')
'''.replace('FAMILIES_PLACEHOLDER', repr(families))
    (target / 'support_gate.mpc').write_text(source)
    meta = {'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'data_field': 'GF(2^128), x^128+x^7+x^2+x+1', 'backend_statistical_parameter': 40,
            'profiles_are_separate_functions': True, 'certificate_checker_GF3_GF4_not_claimed_to_check_this_runtime_field': True,
            'one_public_membership_bit_per_call': True, 'native_source_binding': False,
            'purpose': 'required stage-5 general reference; not stage-7 optimized construction or statistical comparison'}
    (target / 'build.json').write_text(json.dumps(meta, indent=2)); print(json.dumps(meta))


if __name__ == '__main__': main()
