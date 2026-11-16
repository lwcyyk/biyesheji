"""Generate a standalone alternative without changing the historical candidate."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    base = (ROOT / 'mpc/locate2.mpc').read_text()
    prefix = base.split('@for_range(batches)\ndef batch(batch_index):\n')[0]
    old = 'def moments(values):\n    r0, r1 = secret_uniform(), secret_uniform()'
    assert prefix.count(old) == 1
    prefix = prefix.replace(old, 'def moments(values, r0, r1):')
    driver = '''
@for_range(batches)
def batch(index):
    values = [sgf2n.get_input_from(0) + sgf2n.get_input_from(1) for _ in range(n)]
    check_point()
    determinants = []
    for repetition in range(2):
        xs = public_nonzero(3)
        determinants.append(det3([[polynomial(values, cgf2n(3) ** r * x) for x in xs] for r in range(3)]))
    gate = blind_open(norm(determinants[0], determinants[1]))
    status = MemValue(regint(3)); done = MemValue(regint(0)); attempts = MemValue(regint(0))
    sample_attempts = MemValue(regint(0))
    support = Array(n, regint); support.assign_all(0)
    @if_e(gate != cgf2n(0))
    def _(): status.write(2); done.write(1)
    @else_
    def _():
        for diagnosis_attempt in range(2):
            @if_(done.read() == 0)
            def _():
                ready = MemValue(regint(0)); seed = Array(2, sgf2n)
                for sampling_attempt in range(2):
                    @if_(ready.read() == 0)
                    def _():
                        sample_attempts.write(sample_attempts.read() + 1)
                        # Both independent coefficients and their product come
                        # from one real authenticated multiplication triple.
                        r0, r1, r01 = sgf2n.get_random_triple()
                        nonzero_norm = r0 * r0 + r01 + norm_c * (r1 * r1)
                        opening = blind_open(nonzero_norm)
                        @if_(opening != cgf2n(0))
                        def _():
                            seed[0] = r0; seed[1] = r1; ready.write(1)
                @if_e(ready.read())
                def _():
                    attempts.write(attempts.read() + 1)
                    u = moments(values, seed[0], seed[1])
                    selected, valid = decode_public(u)
                    @if_e(valid)
                    def _():
                        # Nonzero affine R has at most one root. Under the
                        # sparse promise, at most one error can remain, so this
                        # single fixed check is exact: no random challenge.
                        remaining = sum(values[i] * cgf2n(1 - selected[i]) for i in range(n))
                        verification = blind_open(remaining)
                        @if_(verification == cgf2n(0))
                        def _():
                            for i in range(n): support[i] = selected[i]
                            status.write(sum(selected[i] for i in range(n)) != 0)
                            done.write(1)
                    @else_
                    def _(): done.write(1)
                @else_
                def _(): done.write(1)
    check_point()
    print_ln('RESULT batch=%s status=%s attempts=%s', index, status.read(), attempts.read())
    print_ln('SAMPLING batch=%s attempts=%s', index, sample_attempts.read())
    for i in range(n):
        @if_(support[i])
        def _(): print_ln('SUPPORT batch=%s index=%s', index, i)
check_point()
print_ln('PROTOCOL_DONE')
'''
    source = '# Nonzero-seed exact sparse diagnosis; conditional, not novel primitives.\n' + prefix + driver
    destination = ROOT / 'mpc/nonzero_seed2.mpc'
    with destination.open('x') as f: f.write(source)
    metadata = {'base_sha256': hashlib.sha256(base.encode()).hexdigest(),
                'generated_sha256': hashlib.sha256(source.encode()).hexdigest(),
                'sampler_limit': 2, 'diagnosis_limit': 2,
                'profile': 'k=2 only; sparse gate unchanged'}
    with (ROOT / 'mpc/nonzero_seed2_build.json').open('x') as f: json.dump(metadata, f, indent=2)
    print(json.dumps(metadata))


if __name__ == '__main__': main()
