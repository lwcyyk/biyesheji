"""Same-input, same-gate descriptive comparison including the new rowspace layer."""
import argparse
import json
from pathlib import Path
import random
import subprocess
import sys
from fixtures import generate, verify
from sweep import metrics
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from field import Field


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    p.add_argument('--sizes', type=int, nargs='+', default=[8, 64])
    p.add_argument('--repeats', type=int, default=2)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False); rows = []
    for n in a.sizes:
        fixture = generate(n); f = Field(128); labels = f.labels(n)
        locator = [f.mul(labels[0], labels[1]), labels[0] ^ labels[1], 1]
        b, c, e = labels[2:5]
        vector = [0, 0] + [f.mul(z, f.inverse(f.poly(locator, x)))
                            for z, x in zip([c ^ e, e ^ b, b ^ c], labels[2:5])] + [0] * (n - 5)
        rng = random.Random(2161103 + n)
        for d in vector:
            s = rng.getrandbits(128)
            fixture['party_inputs'][0].append(s); fixture['party_inputs'][1].append(s ^ d)
        fixture['expected'].append({'status': 2, 'support': []}); fixture['batches'] += 1
        fixture['extra_case'] = {'residuals': vector, 'true_support': [2, 3, 4],
                                'forged_rowspace_support_without_gate': [0, 1]}
        fixture_path = out / f'n{n}.json'; fixture_path.write_text(json.dumps(fixture, indent=2))
        for repeat in range(a.repeats):
            modes = ['moments', 'coordinate', 'rowspace']
            if repeat % 2: modes.reverse()
            for mode in modes:
                directory = out / f'n{n}_{mode}_{repeat}'
                source = 'mpc/rowspace2.mpc' if mode == 'rowspace' else 'mpc/locate2.mpc'
                command = [sys.executable, 'mpc/run_backend.py', '--out', str(directory),
                           '--source', source, '--fixture', str(fixture_path),
                           '--compiler-arg', str(n), '--compiler-arg', str(fixture['batches'])]
                if mode != 'rowspace': command += ['--compiler-arg', mode]
                completed = subprocess.run(command, cwd=ROOT)
                if completed.returncode: raise RuntimeError(f'failed run retained: {directory}')
                checked = verify(directory, fixture)
                (directory / 'verification.json').write_text(json.dumps(checked, indent=2))
                if not checked['pass']: raise RuntimeError(f'wrong output retained: {directory}')
                row = {'n': n, 'mode': mode, 'repeat': repeat, 'batches': fixture['batches'],
                       'run': str(directory.relative_to(ROOT)), 'pass': checked['pass'],
                       **metrics((directory / 'party0.log').read_text())}
                rows.append(row)
                (out / 'summary.json').write_text(json.dumps({
                    'status': 'DESCRIPTIVE_DEVELOPMENT_ONLY', 'rows': rows,
                    'limits': ['one host, two processes', 'backend statistical parameter 40',
                               'timings are not a formal statistical claim',
                               'rowspace sampler cost included, not relabeled offline',
                               'the ninth case requires the gate; rowspace alone is unsafe']}, indent=2))
                print(json.dumps(row), flush=True)


if __name__ == '__main__': main()
