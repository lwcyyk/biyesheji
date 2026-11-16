"""Append-only evidence summary; does not rewrite previous experiment outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', required=True)
    args = parser.parse_args(); out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated evidence path')
    out.mkdir(parents=True, exist_ok=False)
    old = json.loads((ROOT / 'delivery_manifest.json').read_text())
    historical = [{'path': name, 'unchanged': (ROOT / name).is_file() and sha(ROOT / name) == digest}
                  for name, digest in old['files'].items()]
    replay = []
    for path in sorted((ROOT / 'results/general_mask02').iterdir()):
        other = ROOT / 'results/general_mask03' / path.name
        replay.append({'file': path.name, 'sha256': sha(path),
                       'same_bytes': other.is_file() and path.read_bytes() == other.read_bytes()})
    paired = json.loads((ROOT / 'results/mpc_paired01/summary.json').read_text())
    averages = []
    for n in (8, 64):
        for mode in ('moments', 'coordinate'):
            rows = [r for r in paired['rows'] if r['n'] == n and r['mode'] == mode]
            averages.append({'n': n, 'mode': mode, 'runs': len(rows),
                             **{key: statistics.mean(r[key] for r in rows) for key in (
                                 'reported_seconds_including_preprocessing', 'online_seconds',
                                 'preprocessing_seconds', 'global_data_sent_MB', 'triples_consumed',
                                 'inverses_consumed')}})
    checks = []; run_hashes = {}
    for row in paired['rows']:
        directory = ROOT / row['run']; manifest = json.loads((directory / 'manifest.json').read_text())
        verify = json.loads((directory / 'verification.json').read_text())
        compile_log = (directory / 'compile.log').read_text()
        copied_source = directory / 'Programs/Source/locate2.mpc'
        ok = (manifest['success'] and verify['pass'] and 'WARNING' not in compile_log
              and sha(copied_source) == manifest['source_sha256'])
        checks.append({'run': row['run'], 'pass': ok,
                       'runtime_statistical_security_parameter': 40,
                       'source_sha256': manifest['source_sha256']})
        for path in directory.rglob('*'):
            if path.is_file() and (path.suffix in ('.log', '.json', '.mpc', '.bc', '.sch')):
                run_hashes[str(path.relative_to(ROOT))] = sha(path)
    finite_checks = []
    for directory_name in ('general_mask03', 'leakage_barrier01', 'simulation_barrier01', 'mds_barrier01'):
        directory = ROOT / 'results' / directory_name
        summary = json.loads((directory / 'summary.json').read_text())
        finite_checks.append({'run': 'results/' + directory_name, 'pass': summary['pass']})
        for path in directory.iterdir():
            if path.is_file(): run_hashes[str(path.relative_to(ROOT))] = sha(path)
    source_paths = [p for folder in ('mpc', 'construction') for p in (ROOT / folder).rglob('*')
                    if p.is_file() and p.suffix in ('.py', '.mpc')]
    source_paths += [ROOT / name for name in (
        'CONSTRUCTION_EXTENSION.md', 'TIGHT_LEAKAGE_BOUND.md', 'NOVELTY_REASSESSMENT.md',
        'MPC_VALIDATION.md', 'CURRENT_STATUS.md')]
    payload = {'status': 'CONDITIONAL_CONSTRUCTION_AND_DEVELOPMENT_EVIDENCE_NOT_NOVELTY_SUCCESS',
               'environment': {'python': sys.version, 'platform': platform.platform()},
               'historical_file_checks': historical, 'replay': replay, 'mpc_runs': checks,
               'finite_checks': finite_checks,
               'paired_arithmetic_means': averages,
               'source_hashes': {str(p.relative_to(ROOT)): sha(p) for p in source_paths},
               'raw_output_hashes': run_hashes,
               'known_failed_runs_preserved': {
                   'results/mpc_smoke01': 'incorrect compile flag -G 128; compile failed before MPC',
                   'results/mpc_locate_n8_02': 'runtime -S128 unsupported by an auxiliary field type'},
               'superseded_exploratory_run': {
                   'results/mpc_locate_n8_01': 'passed outputs but memory-order warning; final runs use --preserve-mem-order'},
               'development_pass': all(x['unchanged'] for x in historical)
                                   and all(x['same_bytes'] for x in replay)
                                   and all(x['pass'] for x in checks)
                                   and all(x['pass'] for x in finite_checks)}
    (out / 'manifest.json').write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps({'development_pass': payload['development_pass'],
                       'historical_files_unchanged': sum(x['unchanged'] for x in historical),
                       'replayed_files_equal': sum(x['same_bytes'] for x in replay),
                       'mpc_runs_pass': sum(x['pass'] for x in checks),
                       'averages': averages}), flush=True)
    if not payload['development_pass']: raise SystemExit(1)


if __name__ == '__main__': main()
