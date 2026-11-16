"""Check and snapshot this additive delivery; historical artifacts stay untouched."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import statistics

ROOT = Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    before_path = ROOT / 'results/construction_mpc_delivery03/manifest.json'
    before = json.loads(before_path.read_text())
    hashes = {**json.loads((ROOT / 'delivery_manifest.json').read_text())['files'],
              **before['source_hashes'], **before['raw_output_hashes']}
    history = [{'path': name, 'unchanged': (ROOT / name).is_file() and sha(ROOT / name) == digest}
               for name, digest in hashes.items()]
    replay = [{'file': path.name, 'same_bytes': path.read_bytes() ==
               (ROOT / 'results/rowspace_algebra02' / path.name).read_bytes()}
              for path in sorted((ROOT / 'results/rowspace_algebra01').iterdir()) if path.is_file()]
    finite = []
    raw_hashes = {}
    for name in ('rowspace_algebra02', 'rowspace_limits01', 'old_bound_refinement01'):
        directory = ROOT / 'results' / name
        result = json.loads((directory / 'summary.json').read_text())
        finite.append({'run': 'results/' + name, 'pass': result['pass']})
        for path in directory.iterdir():
            if path.is_file(): raw_hashes[str(path.relative_to(ROOT))] = sha(path)
    rows = json.loads((ROOT / 'results/rowspace_paired01/summary.json').read_text())['rows']
    runs = []
    for row in rows:
        directory = ROOT / row['run']; manifest = json.loads((directory / 'manifest.json').read_text())
        checked = json.loads((directory / 'verification.json').read_text())
        source = next((directory / 'Programs/Source').glob('*.mpc'))
        compile_text = (directory / 'compile.log').read_text()
        ok = manifest['success'] and checked['pass'] and 'WARNING' not in compile_text and sha(source) == manifest['source_sha256']
        # The actual triples and inverse tuples include generation of secret masks.
        expected = {'moments': (264, 81), 'rowspace': (288, 69),
                    'coordinate': (198 + 6 * row['n'], 63 + 6 * row['n'])}[row['mode']]
        ok &= (row['triples_consumed'], row['inverses_consumed']) == expected
        runs.append({'run': row['run'], 'pass': ok, 'source_sha256': manifest['source_sha256']})
        for path in directory.rglob('*'):
            if path.is_file() and path.suffix in ('.log', '.json', '.mpc', '.bc', '.sch'):
                raw_hashes[str(path.relative_to(ROOT))] = sha(path)
    for path in (ROOT / 'results/rowspace_paired01').glob('*.json'):
        raw_hashes[str(path.relative_to(ROOT))] = sha(path)
    means = []
    for n in (8, 64):
        for mode in ('moments', 'coordinate', 'rowspace'):
            selected = [r for r in rows if r['n'] == n and r['mode'] == mode]
            means.append({'n': n, 'mode': mode, 'repeats': len(selected),
                          **{key: statistics.mean(r[key] for r in selected) for key in (
                              'reported_seconds_including_preprocessing', 'online_seconds',
                              'global_data_sent_MB', 'triples_consumed', 'inverses_consumed')}})
    own_files = [
        'construction/rowspace.py', 'construction/rowspace_reference.py',
        'construction/validate_rowspace.py', 'construction/rowspace_limits.py',
        'construction/old_bound_refinement.py', 'mpc/rowspace2.mpc', 'mpc/rowspace_sweep.py',
        'mpc/collect_rowspace.py', 'ROWSPACE_2026-11-03.md', 'ROWSPACE_VALIDATION_2026-11-03.md',
        'LITERATURE_2026-11-03.md', 'CURRENT_STATUS_2026-11-03.md']
    source_hashes = {}
    for name in own_files:
        path = ROOT / name; source_hashes[name] = sha(path)
        snapshot = out / 'source_snapshot' / name
        snapshot.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, snapshot)
    all_pass = (len(rows) == 12 and all(x['unchanged'] for x in history)
                and all(x['same_bytes'] for x in replay) and all(x['pass'] for x in finite + runs))
    result = {'status': 'CONDITIONAL_CONSTRUCTION_VERIFIED_IN_FINITE_SCOPE_NOT_NOVELTY_PROVEN',
              'date': '2026-11-03', 'development_pass': all_pass,
              'previous_manifest_sha256': sha(before_path), 'historical_files': history,
              'deterministic_replay': replay, 'finite_checks': finite, 'mpc_checks': runs,
              'logical_mpc_batches': sum(r['batches'] for r in rows),
              'descriptive_means': means, 'source_hashes': source_hashes, 'raw_hashes': raw_hashes,
              'limits': ['same-host honest executions of an active-security backend',
                         'backend statistical parameter 40', 'real MPC k=2 only',
                         'native source binding absent', 'no formal H-A/H-B/H-AB test',
                         'no full novelty/priority verification']}
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'development_pass': all_pass, 'historical_files_unchanged': sum(x['unchanged'] for x in history),
                       'replayed_files': len(replay), 'mpc_runs': len(runs),
                       'logical_batches': result['logical_mpc_batches'], 'snapshot_files': len(own_files)}), flush=True)
    if not all_pass: raise SystemExit(1)


if __name__ == '__main__': main()
