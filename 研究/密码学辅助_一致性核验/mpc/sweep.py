"""Small descriptive paired sweep, no H-B/H-A statistical hypothesis tests."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from fixtures import generate, verify

ROOT = Path(__file__).resolve().parents[1]


def metrics(log):
    result = {}
    for name, pattern in {
        'reported_seconds_including_preprocessing': r'^Time = ([\d.e+-]+) seconds',
        'global_data_sent_MB': r'^Global data sent = ([\d.e+-]+) MB',
        'online_seconds': r'Spent ([\d.e+-]+) seconds',
        'preprocessing_seconds': r'on the online phase and ([\d.e+-]+) seconds',
        'triples_consumed': r'^\s+(\d+)\s+Triples$',
        'inverses_consumed': r'^\s+(\d+)\s+Inverses$',
    }.items():
        found = re.search(pattern, log, re.M)
        if found: result[name] = float(found.group(1))
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--sizes', nargs='+', type=int, default=[8, 64])
    p.add_argument('--repeats', type=int, default=2)
    a = p.parse_args()
    out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated directory required')
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    for n in a.sizes:
        fixture = generate(n)
        fixture_path = out / f'n{n}.json'
        fixture_path.write_text(json.dumps(fixture, indent=2))
        for repeat in range(a.repeats):
            # Swap order between repeats to reduce simple order confounding.
            modes = ['moments', 'coordinate'][::1 if repeat % 2 == 0 else -1]
            for mode in modes:
                run = out / f'n{n}_{mode}_{repeat}'
                cmd = [sys.executable, 'mpc/run_backend.py', '--out', str(run),
                       '--source', 'mpc/locate2.mpc', '--fixture', str(fixture_path),
                       '--compiler-arg', str(n), '--compiler-arg', str(fixture['batches']),
                       '--compiler-arg', mode]
                completed = subprocess.run(cmd, cwd=ROOT)
                if completed.returncode: raise RuntimeError(f'failed run retained: {run}')
                verification = verify(run, fixture)
                (run / 'verification.json').write_text(json.dumps(verification, indent=2))
                if not verification['pass']: raise RuntimeError(f'output mismatch retained: {run}')
                row = {'n': n, 'mode': mode, 'repeat': repeat, 'batches': fixture['batches'],
                       'outputs_pass': verification['pass'], 'run': str(run.relative_to(ROOT)),
                       **metrics((run / 'party0.log').read_text())}
                rows.append(row)
                (out / 'summary.json').write_text(json.dumps({
                    'status': 'DEVELOPMENT_ONLY_NOT_STATISTICAL_SUPPORT', 'rows': rows,
                    'limits': ['two local parties', 'statistical parameter 40',
                               'eight fixed synthetic batches per run',
                               'compilation, SSL generation and process setup excluded from backend Time',
                               'preprocessing batch padding included',
                               'no independent backend security audit']}, indent=2))
                print(json.dumps(row), flush=True)


if __name__ == '__main__': main()
