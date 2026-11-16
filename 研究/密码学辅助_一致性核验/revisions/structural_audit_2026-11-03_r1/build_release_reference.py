"""Negative-control reference: reuse the exact gate, then release accepted support.

No structural masks; this is not a candidate-MPC expansion. Public acceptance
controls output, so rejected inputs never release their zero flags.
"""
from pathlib import Path
import hashlib
import json

REV = Path(__file__).resolve().parent


def main():
    source = (REV / 'gate_mpc/support_gate.mpc').read_text()
    marker = "    print_ln('GATE case=%s accepted=%s', index, regint(public))\n"
    assert source.count(marker) == 1
    addition = """    @if_(regint(public) == 1)
    def release():
        packed = sum(bits[i] * cgf2n(1 << i) for i in range(4))
        opened_support = packed.reveal()
        check_point()
        print_ln('SUPPORT case=%s packed=%s', index, regint(opened_support))
"""
    modified = source.replace('for_range, runtime_error_if', 'for_range, runtime_error_if, if_')
    modified = modified.replace(marker, marker + addition)
    modified = modified.replace('SCOPE GENERIC_SUPPORT_GATE_REFERENCE_ONLY', 'SCOPE GATE_THEN_SUPPORT_REFERENCE_ONLY')
    target = REV / 'gate_mpc/gate_release.mpc'
    with target.open('x') as stream: stream.write(modified)
    meta = {'source_sha256': hashlib.sha256(modified.encode()).hexdigest(),
            'gate_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'gate_arithmetic_unchanged': True, 'extra_secret_multiplications_for_release': 0,
            'rejected_leakage': 'membership_bit_only', 'accepted_leakage': 'membership_bit_and_support',
            'independent_of_structural_mask_construction': True,
            'purpose': 'stage-5 generic reference and negative control, not stage-7 optimized candidate'}
    with (REV / 'gate_mpc/release_build.json').open('x') as stream: json.dump(meta, stream, indent=2)
    print(json.dumps(meta))


if __name__ == '__main__': main()
