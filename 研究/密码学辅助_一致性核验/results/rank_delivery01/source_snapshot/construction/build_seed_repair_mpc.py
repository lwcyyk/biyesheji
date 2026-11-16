"""Build secure and explicitly non-private lab-only repair branch variants."""
from pathlib import Path
import hashlib
import json
ROOT = Path(__file__).resolve().parents[1]


def main():
    base = (ROOT / 'mpc/nonzero_seed2.mpc').read_text()
    prefix = base.split('@for_range(batches)\ndef batch(index):\n')[0]
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
    status = MemValue(regint(3)); attempts = MemValue(regint(0)); repaired = MemValue(regint(0))
    support = Array(n, regint); support.assign_all(0)
    @if_e(gate != cgf2n(0))
    def _(): status.write(2)
    @else_
    def _():
        ready = MemValue(regint(0)); seed = Array(2, sgf2n)
        for sampling_attempt in range(2):
            @if_(ready.read() == 0)
            def _():
                attempts.write(attempts.read() + 1)
                r0, r1, r01 = sgf2n.get_random_triple()
                opening = blind_open(r0 * r0 + r01 + norm_c * (r1 * r1))
                @if_(opening != cgf2n(0))
                def _(): seed[0] = r0; seed[1] = r1; ready.write(1)
        @if_(ready.read())
        def _():
            u = moments(values, seed[0], seed[1])
            selected, valid = decode_public(u)
            @if_(valid)
            def _():
                remaining = [values[i] * cgf2n(1 - selected[i]) for i in range(n)]
                sigma = sgf2n.get_random_inverse()[0]
                z0 = (sigma * sum(remaining)).reveal()
                check_point()
                @if_e(z0 == cgf2n(0))
                def _():
                    for i in range(n): support[i] = selected[i]
                    status.write(sum(selected[i] for i in range(n)) != 0)
                @else_
                def _():
                    # Safe linked reuse of sigma ONLY because the rank argument
                    # certifies one remaining nonzero entry under the promise.
                    z1 = (sigma * sum(d * label for d, label in zip(remaining, labels))).reveal()
                    check_point()
                    location = z1 / z0
                    matches = [(location == labels[i]) * (1 - selected[i]) for i in range(n)]
                    @if_((sum(matches) == 1) * (sum(selected[i] for i in range(n)) <= 1))
                    def _():
                        for i in range(n): support[i] = selected[i] + matches[i]
                        status.write(1); repaired.write(1)
    check_point()
    print_ln('RESULT batch=%s status=%s attempts=%s', index, status.read(), attempts.read())
    print_ln('REPAIR batch=%s used=%s', index, repaired.read())
    for i in range(n):
        @if_(support[i])
        def _(): print_ln('SUPPORT batch=%s index=%s', index, i)
check_point()
print_ln('PROTOCOL_DONE')
'''
    secure = prefix + driver
    lab = secure.replace('r0, r1, r01 = sgf2n.get_random_triple()',
                         'r0, r1, r01 = sgf2n(1), sgf2n(1), sgf2n(1)')
    assert secure != lab
    lab = "# UNSAFE LAB FIXED SEED. NO AMPLITUDE PRIVACY. SYNTHETIC INPUTS ONLY.\n" + lab
    lab = lab.replace("print_ln('PROTOCOL_DONE')", "print_ln('LAB_FIXED_SEED_NOT_PRIVATE')\nprint_ln('PROTOCOL_DONE')")
    entries = []
    for name, text, mode in [('seed_repair2.mpc', secure, 'SECURE_SAMPLING'),
                             ('seed_repair2_lab.mpc', lab, 'FUNCTIONAL_BRANCH_TEST_NO_PRIVACY')]:
        with (ROOT / 'mpc' / name).open('x') as f: f.write(text)
        entries.append({'file': name, 'mode': mode, 'sha256': hashlib.sha256(text.encode()).hexdigest()})
    with (ROOT / 'mpc/seed_repair_build.json').open('x') as f: json.dump(entries, f, indent=2)
    print(json.dumps(entries))


if __name__ == '__main__': main()
