"""Strengthen historical baselines with the same authenticated triple interface.

Both a and b of a uniform triple (a,b,ab) are independent uniform randomness.
Do not credit the candidate for an avoidable extra randomness tuple in a baseline.
"""
from pathlib import Path
import hashlib
import json
ROOT = Path(__file__).resolve().parents[1]


def main():
    modifications = []
    source = (ROOT / 'mpc/locate2.mpc').read_text()
    old = 'r0, r1 = secret_uniform(), secret_uniform()'
    assert source.count(old) == 1
    transformed = source.replace(old, 'r0, r1, unused_product = sgf2n.get_random_triple()')
    modifications.append(('mpc/locate2_pair_random.mpc', transformed, source))
    source = (ROOT / 'mpc/rowspace2.mpc').read_text()
    old = '''proposal = [sgf2n.get_random_triple()[0] for _ in range(4)]
                opening = blind_open(proposal[0] * proposal[3] + proposal[1] * proposal[2])'''
    new = '''a, d, ad = sgf2n.get_random_triple()
                b, c, bc = sgf2n.get_random_triple()
                proposal = [a, b, c, d]
                opening = blind_open(ad + bc)'''
    assert source.count(old) == 1
    modifications.append(('mpc/rowspace2_pair_random.mpc', source.replace(old, new), source))
    manifest = []
    for filename, transformed, base in modifications:
        with (ROOT / filename).open('x') as f: f.write(transformed)
        manifest.append({'path': filename, 'base_sha256': hashlib.sha256(base.encode()).hexdigest(),
                         'sha256': hashlib.sha256(transformed.encode()).hexdigest()})
    with (ROOT / 'mpc/paired_random_build.json').open('x') as f: json.dump(manifest, f, indent=2)
    print(json.dumps(manifest))


if __name__ == '__main__': main()
