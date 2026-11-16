"""Append-only source-binding evidence and honest closure status."""
import argparse
import hashlib
import json
from pathlib import Path
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
    historical_hashes = json.loads((ROOT / 'delivery_manifest.json').read_text())['files']
    for name in ('results/construction_mpc_delivery03/manifest.json', 'results/rowspace_delivery01/manifest.json'):
        previous = json.loads((ROOT / name).read_text())
        historical_hashes.update(previous['source_hashes'])
        historical_hashes.update(previous.get('raw_hashes', previous.get('raw_output_hashes', {})))
    history = [{'path': name, 'unchanged': (ROOT / name).is_file() and sha(ROOT / name) == digest}
               for name, digest in historical_hashes.items()]
    replay = [{'file': name, 'equal': (ROOT / 'results/source_aes_clear01' / name).read_bytes() ==
               (ROOT / 'results/source_aes_clear02' / name).read_bytes()}
              for name in ('parameters.json', 'vectors.jsonl')]
    # summary source inventories intentionally grew as build scripts were added;
    # arithmetic source hashes and deterministic vectors/parameters did not change.
    rows = []; raw_hashes = {}
    for name, method in [('source_binding_mpc01', 'rowspace'), ('source_binding_mpc02', 'rowspace'),
                         ('source_binding_moments01', 'moments'), ('source_binding_coordinate01', 'coordinate')]:
        directory = ROOT / 'results' / name
        run = json.loads((directory / 'manifest.json').read_text())
        checked = json.loads((directory / 'verification.json').read_text())
        copied = next((directory / 'Programs/Source').glob('*.mpc'))
        value = {'run': 'results/' + name, 'method': method,
                 'pass': run['success'] and checked['pass'] and sha(copied) == run['source_sha256']
                         and 'WARNING' not in (directory / 'compile.log').read_text(),
                 **metrics((directory / 'party0.log').read_text())}
        expected = {'rowspace': (16297, 95), 'moments': (16269, 109), 'coordinate': (16220, 116)}[method]
        value['pass'] &= (value['triples_consumed'], value['inverses_consumed']) == expected
        rows.append(value)
    negative = ROOT / 'results/source_binding_invalid01'
    failed = json.loads((negative / 'manifest.json').read_text())
    negative_pass = not failed['success'] and all(p.get('exit_code', 0) != 0 for p in failed['phases'] if 'party' in p)
    for party in (0, 1):
        log = (negative / f'party{party}.log').read_text()
        negative_pass &= 'INPUT_DOMAIN_INVALID' in log and 'RESULT batch=' not in log and 'PROTOCOL_DONE' not in log
    negative_result = {'expected': 'INPUT_DOMAIN_INVALID before AES/diagnostic output',
                       'run_success_expected': False, 'expected_rejection_verified': negative_pass}
    # Preserve the raw failed run; verification belongs to this new evidence folder.
    (out / 'domain_rejection.json').write_text(json.dumps(negative_result, indent=2))
    for name in ('source_aes_clear01', 'source_aes_clear02', 'source_binding_mpc01', 'source_binding_mpc02',
                 'source_binding_moments01', 'source_binding_coordinate01', 'source_binding_invalid01'):
        for path in (ROOT / 'results' / name).rglob('*'):
            if path.is_file() and path.suffix in ('.json', '.jsonl', '.log', '.mpc', '.bc', '.sch'):
                raw_hashes[str(path.relative_to(ROOT))] = sha(path)
    paths = [p for p in (ROOT / 'source_binding').rglob('*') if p.is_file() and p.suffix in ('.py', '.json', '.mpc')]
    paths += [ROOT / p for p in ('SOURCE_BINDING_2026-11-03.md', 'CLOSURE_REVIEW_2026-11-03.md',
                                 'CURRENT_STATUS_source_binding_2026-11-03.md')]
    hashes = {}
    for path in paths:
        name = path.relative_to(ROOT); hashes[str(name)] = sha(path)
        snapshot = out / 'source_snapshot' / name
        snapshot.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, snapshot)
    passed = all(x['unchanged'] for x in history) and all(x['equal'] for x in replay) and all(x['pass'] for x in rows) and negative_pass
    result = {'development_pass': passed, 'status': 'WORK_PACKAGE_COMPLETE_NOVELTY_GATE_UNRESOLVED',
              'user_requested_research_stop_condition_met': False,
              'workload_assessment': 'complete auxiliary implementation/validation package; not a university certification',
              'novelty_assessment': 'strong independent originality not yet confirmed',
              'pending_evidence': 'full-text comparison with ePrint 2026/946 / DOI 10.62056/ay4fvu7sf',
              'historical_files': history, 'deterministic_replay': replay,
              'positive_runs': rows, 'negative_run': negative_result,
              'source_hashes': hashes, 'raw_hashes': raw_hashes,
              'limits': ['trusted pre-established key/context', 'not full TLS', 'same-host honest MPC execution',
                         'backend statistical security 40', 'two one-block AES128-GCM records',
                         'synthetic test data', 'no formal H-A/H-B/H-AB statistical test']}
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'development_pass': passed, 'history_unchanged': sum(x['unchanged'] for x in history),
                       'positive_runs': len(rows), 'logical_cases': 8 * len(rows),
                       'expected_domain_abort_pass': negative_pass, 'metrics': rows}), flush=True)
    if not passed: raise SystemExit(1)


if __name__ == '__main__': main()
