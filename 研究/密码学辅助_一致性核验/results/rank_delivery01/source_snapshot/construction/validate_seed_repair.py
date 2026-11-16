"""Exhaustive small-field correctness, differential checks and joint-view privacy."""
from collections import Counter
from itertools import product
from pathlib import Path
import argparse
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from field import Field
import reference
from nonzero_seed_repair import diagnose


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    f = Field(4); labels = f.labels(4)
    table = reference.sparse_table(4, 2, labels, 4, f.modulus)
    vectors = [json.loads(line)['residuals'] for line in (ROOT / 'results/nonzero_seed_algebra01/vectors.jsonl').read_text().splitlines()]
    seeds = [(a, b) for a, b in product(range(16), repeat=2) if a or b]
    trials = differential = repairs = 0
    for d in vectors:
        expected = [i for i, value in enumerate(d) if value]
        s = reference.moments(d, labels, 5, 4, f.modulus)
        for seed_index, (r0, r1) in enumerate(seeds):
            u = [f.mul(r0, s[j]) ^ f.mul(r1, s[j + 1]) for j in range(4)]
            selected = [i for i, value in enumerate(table[tuple(u)]) if value]
            remaining = [x if i not in selected else 0 for i, x in enumerate(d)]
            e0 = f.total(remaining)
            if e0:
                e1 = f.total(f.mul(x, label) for x, label in zip(remaining, labels))
                position = labels.index(f.mul(e1, f.inverse(e0)))
                actual_support = sorted(selected + [position]); repairs += 1
            else: actual_support = selected
            assert actual_support == expected; trials += 1
            if seed_index % 17 == 0:
                got = diagnose(f, d, labels, [r0, r1], blind=7)
                got_support = got.get('support', got['candidate'])
                assert got['status'] == 'ACCEPT' and got_support == expected
                assert got['online_products'] == 6 + int(got['repaired'])
                differential += 1
    privacy = []
    def distribution(d):
        counter = Counter()
        for seed in seeds:
            for blind in range(1, 16):
                x = diagnose(f, d, labels, list(seed), blind)
                counter[(tuple(x['moments']), x['remainder_opening'], x['repair_opening'])] += 1
        return counter
    for left, right in [([1, 1, 0, 0], [7, 13, 0, 0]), ([0, 1, 0, 0], [0, 9, 0, 0])]:
        first, second = distribution(left), distribution(right)
        assert first == second
        privacy.append({'left': left, 'right': right, 'tapes_each': 3825, 'equal_joint_distribution': True})
    result = {'pass': True, 'exhaustive_vector_seed_pairs': trials, 'candidate_checks': differential,
               'repair_events': repairs, 'privacy_tapes': 15300, 'privacy_checks': privacy,
               'scope': 'sparse promise, fixed valid nonzero seed; sampler/gate/backend assessed separately'}
    (out / 'summary.json').write_text(json.dumps(result, indent=2)); print(json.dumps(result))


if __name__ == '__main__': main()
