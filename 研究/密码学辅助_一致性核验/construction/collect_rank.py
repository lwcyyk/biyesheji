"""Snapshot the rank/repair research without rewriting prior evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'mpc'))
from sweep import metrics


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    old_hashes = json.loads((ROOT / 'delivery_manifest.json').read_text())['files']
    for filename in ('results/construction_mpc_delivery03/manifest.json', 'results/rowspace_delivery01/manifest.json',
                     'results/source_binding_delivery01/manifest.json'):
        record = json.loads((ROOT / filename).read_text())
        old_hashes.update(record['source_hashes'])
        old_hashes.update(record.get('raw_hashes', record.get('raw_output_hashes', {})))
    historical = [{'path': name, 'unchanged': (ROOT / name).is_file() and sha(ROOT / name) == digest}
                  for name, digest in old_hashes.items()]
    replays = []
    for first, second in (('rank_tradeoff01', 'rank_tradeoff02'),
                          ('nonzero_seed_algebra01', 'nonzero_seed_algebra02'),
                          ('seed_repair_algebra01', 'seed_repair_algebra02')):
        for path in sorted((ROOT / 'results' / first).iterdir()):
            if path.is_file():
                other = ROOT / 'results' / second / path.name
                replays.append({'first': str(path.relative_to(ROOT)), 'same_bytes': path.read_bytes() == other.read_bytes()})
    finite = []
    raw_hashes = {}
    for name in ('rank_tradeoff02', 'rank_boundaries01', 'nonzero_seed_algebra02', 'seed_repair_algebra02'):
        directory = ROOT / 'results' / name
        result = json.loads((directory / 'summary.json').read_text())
        finite.append({'run': name, 'pass': result['pass']})
        for path in directory.iterdir():
            if path.is_file(): raw_hashes[str(path.relative_to(ROOT))] = sha(path)
    comparison = json.loads((ROOT / 'results/rank_paired01/summary.json').read_text())
    paths = [ROOT / row['run'] for row in comparison['rows']]
    paths += [ROOT / 'results' / name for name in ('nonzero_seed_pilot01', 'nonzero_seed_n64_01', 'seed_repair_secure01')]
    runs = []
    for directory in paths:
        run = json.loads((directory / 'manifest.json').read_text())
        verified = json.loads((directory / 'verification.json').read_text())
        source = next((directory / 'Programs/Source').glob('*.mpc'))
        logs = [(directory / f'party{i}.log').read_text() for i in (0, 1)]
        ok = run['success'] and verified['pass'] and sha(source) == run['source_sha256']
        ok &= 'WARNING' not in (directory / 'compile.log').read_text() and all('LAB_FIXED_SEED' not in log for log in logs)
        runs.append({'run': str(directory.relative_to(ROOT)), 'pass': ok, **metrics(logs[0])})
    lab = ROOT / 'results/seed_repair_lab01'
    lab_verified = json.loads((lab / 'verification.json').read_text())['pass']
    repair_counts = []
    for party in (0, 1):
        log = (lab / f'party{party}.log').read_text()
        count = len(re.findall(r'REPAIR batch=\d+ used=1', log))
        repair_counts.append(count)
        lab_verified &= 'LAB_FIXED_SEED_NOT_PRIVATE' in log and count == 2
    for directory in paths + [lab]:
        for path in directory.rglob('*'):
            if path.is_file() and path.suffix in ('.log', '.json', '.mpc', '.bc', '.sch'):
                raw_hashes[str(path.relative_to(ROOT))] = sha(path)
    raw_hashes['results/rank_paired01/summary.json'] = sha(ROOT / 'results/rank_paired01/summary.json')
    files = ['RANK_PRIVACY_TRADEOFF_2026-11-03.md', 'NONZERO_SEED_2026-11-03.md',
             'SEED_REPAIR_2026-11-03.md', 'NOVELTY_RANK_PACKAGE_2026-11-03.md', 'CURRENT_STATUS_rank_tradeoff_2026-11-03.md']
    files += ['construction/' + name for name in (
        'nonzero_seed.py', 'build_nonzero_seed_mpc.py', 'rank_tradeoff_checks.py',
        'validate_nonzero_seed.py', 'build_paired_random_baselines.py', 'rank_tradeoff_boundaries.py',
        'nonzero_seed_repair.py', 'build_seed_repair_mpc.py', 'validate_seed_repair.py', 'collect_rank.py')]
    files += ['mpc/' + name for name in (
        'nonzero_seed2.mpc', 'nonzero_seed2_build.json', 'locate2_pair_random.mpc', 'rowspace2_pair_random.mpc',
        'paired_random_build.json', 'rank_sweep.py', 'seed_repair2.mpc', 'seed_repair2_lab.mpc',
        'seed_repair2_lab_last.mpc', 'seed_repair_build.json', 'seed_repair_lab_last_build.json')]
    hashes = {}
    for name in files:
        source = ROOT / name; hashes[name] = sha(source)
        target = out / 'source_snapshot' / name
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
    passed = (all(x['unchanged'] for x in historical) and all(x['same_bytes'] for x in replays)
              and all(x['pass'] for x in finite + runs) and lab_verified)
    result = {'status': 'THEOREM_AND_CONSTRUCTION_CANDIDATES_NOT_PRIORITY_CERTIFIED',
              'development_pass': passed, 'general_proofs_independently_reviewed': False,
              'novelty_priority_confirmed': False, 'historical_files': historical,
              'deterministic_replays': replays, 'finite_checks': finite,
              'normal_random_mpc_runs': runs, 'normal_logical_batches': len(runs) * 9,
              'non_private_lab': {'pass': lab_verified, 'repair_branches_by_party': repair_counts,
                  'purpose': 'functional branch coverage only, explicitly NOT privacy evidence'},
              'source_hashes': hashes, 'raw_hashes': raw_hashes,
              'unrun': ['general k real MPC', 'new repair integrated with AES/GCM frontend',
                        'full malicious implementation audit', 'formal H-A/H-B/H-AB statistical tests'],
              'limits': ['fixed input-independent linear mask class', 'same-host execution',
                         'backend statistical parameter 40', 'no global runtime superiority claim']}
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'development_pass': passed, 'history_unchanged': sum(x['unchanged'] for x in historical),
                       'replayed_files': len(replays), 'normal_mpc_runs': len(runs),
                       'normal_batches': len(runs) * 9, 'separate_lab_pass': lab_verified,
                       'source_snapshots': len(files)}), flush=True)
    if not passed: raise SystemExit(1)


if __name__ == '__main__': main()
