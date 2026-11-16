"""Concrete witnesses for restricted column/sketch-size claims."""
from collections import Counter
import argparse
from itertools import product
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from field import Field
import reference


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True)
    args = parser.parse_args(); out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    f = Field(4); labels = f.labels(4)
    distributions = []
    for vector in ([1, 2, 0, 0], [0, 0, 3, 4]):
        s = reference.moments(vector, labels, 3, 4, f.modulus)
        distribution = Counter()
        for a, b, c, d in product(range(16), repeat=4):
            if f.mul(a, d) ^ f.mul(b, c):
                output = tuple(f.mul(x, s[j]) ^ f.mul(y, s[j + 1])
                               for x, y in ((a, b), (c, d)) for j in range(2))
                distribution[output] += 1
        assert len(distribution) == 61200 and set(distribution.values()) == {1}
        distributions.append(distribution)
    assert distributions[0] == distributions[1]
    weights = []
    for i, a in enumerate(labels):
        denominator = 1
        for j, b in enumerate(labels):
            if i != j: denominator = f.mul(denominator, a ^ b)
        weights.append(f.inverse(denominator))
    left, right = weights[:2] + [0, 0], [0, 0] + weights[2:]
    l = reference.moments(left, labels, 3, 4, f.modulus)
    r = reference.moments(right, labels, 3, 4, f.modulus)
    assert l == r and reference.moments(left, labels, 4, 4, f.modulus) != reference.moments(right, labels, 4, 4, f.modulus)
    result = {'pass': True, 'restricted_column_witness': {
        'q': 16, 'k': 2, 'columns': 2, 'inputs': [[1, 2, 0, 0], [0, 0, 3, 4]],
        'different_supports_identical_distributions': True, 'GL_matrices_per_input': 61200},
        'three_moment_collision': {'labels': labels, 'left': left, 'right': right, 'equal_first_three_moments': l},
        'scope': 'two explicit limited-model witnesses, not general protocol lower bounds'}
    (out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__': main()
