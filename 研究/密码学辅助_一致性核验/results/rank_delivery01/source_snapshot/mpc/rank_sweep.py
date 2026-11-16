"""Same-input sanity comparison against strengthened, not historical weak, baselines."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from fixtures import verify
from sweep import metrics
ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False); rows = []
    methods = [('moments_paired', 'mpc/locate2_pair_random.mpc', 'moments'),
               ('rowspace_paired', 'mpc/rowspace2_pair_random.mpc', None),
               ('coordinate', 'mpc/locate2.mpc', 'coordinate'),
               ('nonzero_seed', 'mpc/nonzero_seed2.mpc', None)]
    for n in (8, 64):
        fixture_path = ROOT / f'results/rowspace_paired01/n{n}.json'
        fixture = json.loads(fixture_path.read_text())
        for name, source, mode in methods:
            run = out / f'n{n}_{name}'
            command = [sys.executable, 'mpc/run_backend.py', '--out', str(run), '--source', source,
                       '--fixture', str(fixture_path), '--compiler-arg', str(n),
                       '--compiler-arg', str(fixture['batches'])]
            if mode: command += ['--compiler-arg', mode]
            completed = subprocess.run(command, cwd=ROOT)
            if completed.returncode: raise RuntimeError(f'failed run preserved: {run}')
            verification = verify(run, fixture)
            (run / 'verification.json').write_text(json.dumps(verification, indent=2))
            if not verification['pass']: raise RuntimeError(f'wrong output preserved: {run}')
            row = {'n': n, 'method': name, 'batches': fixture['batches'], 'pass': True,
                   'run': str(run.relative_to(ROOT)), **metrics((run / 'party0.log').read_text())}
            rows.append(row)
            (out / 'summary.json').write_text(json.dumps({'status': 'DEVELOPMENT_ONLY', 'rows': rows,
                'limits': ['one run per configuration', 'same host two processes',
                           'statistical parameter 40', 'preprocessing padding included',
                           'counts are more informative here than timing differences']}, indent=2))
            print(json.dumps(row), flush=True)


if __name__ == '__main__': main()
