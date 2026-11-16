"""Snapshot exploration evidence, including explicitly rejected novelty routes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    hashes = json.loads((ROOT / 'delivery_manifest.json').read_text())['files']
    for name in ('construction_mpc_delivery03', 'rowspace_delivery01', 'source_binding_delivery01', 'rank_delivery01'):
        old = json.loads((ROOT / 'results' / name / 'manifest.json').read_text())
        hashes.update(old['source_hashes']); hashes.update(old.get('raw_hashes', old.get('raw_output_hashes', {})))
    history = [{'path': name, 'unchanged': (ROOT / name).is_file() and sha(ROOT / name) == digest} for name, digest in hashes.items()]
    replay = []
    for path in sorted((ROOT / 'results/structural_masks02').iterdir()):
        other = ROOT / 'results/structural_masks03' / path.name
        replay.append({'path': path.name, 'identical': path.read_bytes() == other.read_bytes()})
    tests = []; raw = {}
    for name in ('structural_masks03', 'hankel_scope01'):
        directory = ROOT / 'results' / name
        result = json.loads((directory / 'summary.json').read_text())
        tests.append({'run': name, 'pass': result['pass']})
        for path in directory.iterdir():
            if path.is_file(): raw[str(path.relative_to(ROOT))] = sha(path)
    paper = ROOT / 'papers/HKZ16.pdf'
    provenance = {'title': 'Numerical Sparsity Determination and Early Termination',
                  'year': 2016, 'doi': '10.1145/2930889.2930924',
                  'url': 'https://users.cs.duke.edu/~elk27/bibliography/16/HKZ16.pdf',
                  'sha256': sha(paper), 'pages': 8,
                  'verified_scope': 'section 4 discussion and appendix 6 characteristic-two counterexamples',
                  'effect_on_claims': 'same Hankel cancellation/shift idea excluded from originality claims'}
    assert provenance['sha256'] == '2229f5fc82fc3cb68308a04c848d4193b5e37e2c325cd77055a14a48968593cb'
    (out / 'paper_provenance.json').write_text(json.dumps(provenance, indent=2))
    files = ['construction/structural_masks.py', 'construction/structural_checker.py',
             'construction/validate_structural.py', 'construction/check_hankel_scope.py',
             'construction/collect_structural.py', 'STRUCTURAL_PRIVACY_2026-11-03.md',
             'EXPLORATION_SCREEN_2026-11-03.md', 'CURRENT_STATUS_structural_exploration_2026-11-03.md']
    source_hashes = {}
    for name in files:
        source_hashes[name] = sha(ROOT / name)
        target = out / 'source_snapshot' / name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    ok = all(x['unchanged'] for x in history) and all(x['identical'] for x in replay) and all(x['pass'] for x in tests)
    result = {'status': 'EXPLORATORY_STRUCTURAL_THEOREMS_NOT_NOVELTY_CERTIFICATION',
              'development_pass': ok, 'strong_independent_originality_established': False,
              'historical_files': history, 'deterministic_replay': replay, 'tests': tests,
              'source_hashes': source_hashes, 'raw_hashes': raw, 'paper_provenance': provenance,
              'unresolved': ['general proof independent review', 'priority comparison',
                             'private runtime support-admissibility enforcement',
                             'native semantics justification for admissible support/amplitude models'],
              'negative_controls': ['direct-sum construction equals simple correct block composition',
                                    'Hankel characteristic-two pathology already known in 2016'],
              'not_run': ['new secret-support MPC', 'formal H-A/H-B/H-AB experiments'],
              'superseded_exploration': 'structural_masks01 predates explicit amplitude/mask-class bindings; retained unchanged'}
    (out / 'manifest.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({'development_pass': ok, 'unchanged_historical_files': sum(x['unchanged'] for x in history),
                       'replayed_files': len(replay), 'source_snapshots': len(files), 'new_real_mpc_runs': 0}))
    if not ok: raise SystemExit(1)


if __name__ == '__main__': main()
