"""Synthetic additive-share fixtures and independent output checks."""
import argparse
import json
from pathlib import Path
import random
import re

ROOT = Path(__file__).resolve().parents[1]


def generate(n, seed=216):
    rng = random.Random(seed)  # Lab fixture generation, NOT protocol randomness.
    examples = [[0] * n for _ in range(8)]
    examples[1][0] = 1
    examples[2][n - 1] = (1 << 127) + 7
    examples[3][1], examples[3][n - 2] = 27, 98
    examples[4][1], examples[4][n - 2] = 93, 12
    examples[5][0:3] = [1, 1, 1]
    examples[6] = [rng.randrange(1, 1 << 128) for _ in range(n)]
    examples[7][0], examples[7][n - 1] = 9, 9
    inputs = [[], []]
    expectations = []
    for values in examples:
        support = [i for i, value in enumerate(values) if value]
        expectations.append({'status': 2 if len(support) > 2 else int(bool(support)),
                             'support': [] if len(support) > 2 else support})
        for value in values:
            share = rng.getrandbits(128)
            inputs[0].append(share); inputs[1].append(share ^ value)
    return {'kind': 'SYNTHETIC_ADDITIVE_INPUTS_HARNESS_KNOWS_ALL',
            'n': n, 'batches': len(examples), 'seed': seed,
            'party_inputs': inputs, 'expected': expectations}


def verify(run, fixture):
    manifest = json.loads((run / 'manifest.json').read_text())
    party_results = []
    for party in (0, 1):
        log = (run / f'party{party}.log').read_text()
        observed = {}
        for b, status, attempts in re.findall(r'RESULT batch=(\d+) status=(\d+) attempts=(\d+)', log):
            if int(b) in observed: raise ValueError('duplicate result')
            observed[int(b)] = {'status': int(status), 'attempts': int(attempts), 'support': []}
        for b, index in re.findall(r'SUPPORT batch=(\d+) index=(\d+)', log):
            observed[int(b)]['support'].append(int(index))
        checks = [{'batch': i, 'expected': expected, 'actual': observed.get(i),
                   'pass': (i in observed and all(observed[i][k] == v for k, v in expected.items()))}
                  for i, expected in enumerate(fixture['expected'])]
        party_results.append({'party': party, 'checks': checks,
                              'pass': len(observed) == len(checks) and 'PROTOCOL_DONE' in log
                              and all(c['pass'] for c in checks)})
    return {'backend_exit_success': manifest.get('success', False),
            'parties': party_results,
            'pass': manifest.get('success', False) and all(x['pass'] for x in party_results),
            'scope': 'exact honest output on synthetic fixtures; not an adversarial security proof'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--n', type=int, default=8)
    p.add_argument('--out')
    p.add_argument('--verify')
    p.add_argument('--fixture')
    a = p.parse_args()
    if a.verify:
        run = ROOT / a.verify
        result = verify(run, json.loads((ROOT / a.fixture).read_text()))
        target = run / 'verification.json'
    else:
        result = generate(a.n); target = ROOT / a.out
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x') as f: json.dump(result, f, indent=2)
    print(json.dumps({'path': str(target), 'pass': result.get('pass')}))
    if a.verify and not result['pass']: raise SystemExit(1)
