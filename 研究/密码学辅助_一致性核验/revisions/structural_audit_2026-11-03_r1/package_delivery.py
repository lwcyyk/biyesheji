"""Seal this isolated revision; hash-check protected evidence without rewriting it."""
import hashlib
import json
from pathlib import Path
import platform
import sys
import zipfile

REV = Path(__file__).resolve().parent
ROOT = REV.parents[1]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if (REV / 'delivery_manifest.json').exists(): raise FileExistsError('already sealed')
    receipt = json.loads((REV / 'input_receipt.json').read_text())
    inputs = []
    for item in receipt['inputs']:
        original = ROOT / item['path']; snapshot = REV / 'inputs' / item['path']
        row = {'path': item['path'], 'expected': item['sha256'], 'actual': sha(original), 'snapshot': sha(snapshot)}
        row['unchanged'] = row['expected'] == row['actual'] == row['snapshot']; assert row['unchanged'], row
        inputs.append(row)
    old_manifest = json.loads((ROOT / 'results/structural_delivery01/manifest.json').read_text())
    old_checks = []
    for section in ('source_hashes','raw_hashes'):
        for name, expected in old_manifest[section].items():
            actual = sha(ROOT / name); assert actual == expected, name
            old_checks.append({'path': name, 'expected': expected, 'actual': actual, 'pass': True})
    existence = [{'path': row['path'], 'exists': (ROOT / row['path']).exists()}
                 for row in old_manifest['historical_files']]
    replay = []
    for left, right in [('dev01','dev02'), ('algebra01','algebra02'), ('certificate_attacks01','certificate_attacks02')]:
        for path in sorted((REV / 'results' / left).iterdir()):
            if not path.is_file(): continue
            other = REV / 'results' / right / path.name
            match = sha(path) == sha(other); assert match, (path, other)
            replay.append({'left': str(path.relative_to(REV)), 'right': str(other.relative_to(REV)),
                           'sha256': sha(path), 'identical': match})
    deps = ['mpc/run_backend.py', 'vendor/backend_release.json',
            'source_binding/generated01/bind_gcm.mpc', 'source_binding/generated01/build.json',
            'results/source_binding_mpc01/verification.json']
    dependency_rows = []
    for name in deps:
        source = ROOT / name; destination = REV / 'inputs_extra_read_only' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream: stream.write(source.read_bytes())
        dependency_rows.append({'path': name, 'sha256': sha(source), 'scope': 'original read-only dependency snapshot, not new experiment'})
    source_files = sorted([p for p in REV.glob('*') if p.is_file() and p.suffix in ('.py','.md','.json')]
                          + [p for p in (REV / 'gate_mpc').rglob('*') if p.is_file()]
                          + [p for p in (REV / 'inputs_extra_read_only').rglob('*') if p.is_file()])
    snapshot = REV / 'source_snapshot.zip'
    with zipfile.ZipFile(snapshot, 'x', zipfile.ZIP_DEFLATED) as archive:
        for path in source_files:
            info = zipfile.ZipInfo(str(path.relative_to(REV)).replace('\\','/'), date_time=(2026,11,3,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    files = [{'path': str(path.relative_to(REV)), 'bytes': path.stat().st_size, 'sha256': sha(path)}
             for path in sorted(REV.rglob('*')) if path.is_file()]
    delivery = {'version': 'structural-audit-r1', 'environment': {'python': sys.version, 'platform': platform.platform(), 'git': 'NOT_A_GIT_REPOSITORY'},
                'protected_ten_inputs': inputs, 'old_manifest_explicit_hash_checks': old_checks,
                'old_historical_existence_only': existence,
                'warning': 'existence and historical unchanged flags do not prove original integrity without starting hashes',
                'dependencies': dependency_rows, 'deterministic_replay': replay,
                'tests': {name: json.loads((REV / path).read_text()) for name, path in [
                    ('finite_audit','results/dev02/summary.json'),('algebra','results/algebra02/summary.json'),
                    ('certificate_attacks','results/certificate_attacks02/summary.json'),('gate_logs','results/gate_log_verification02.json')]},
                'decision': json.loads((REV / 'decision.json').read_text()),
                'source_snapshot_sha256': sha(snapshot), 'files': files,
                'write_scope': str(REV), 'auth_lifecycle_writes': 'NONE_PERFORMED_NO_INITIAL_FULL_TREE_HASH',
                'no_external_peer_review': True}
    target = REV / 'delivery_manifest.json'
    with target.open('x') as stream: json.dump(delivery, stream, indent=2, ensure_ascii=False)
    with (REV / 'manifest_sha256.txt').open('x') as stream: stream.write(sha(target) + '  delivery_manifest.json\n')
    print(json.dumps({'pass': True, 'protected_inputs': len(inputs), 'explicit_old_hash_checks': len(old_checks),
                      'history_paths_checked_for_existence_only': len(existence), 'history_missing': sum(not x['exists'] for x in existence),
                      'replay_files_identical': len(replay), 'new_files_hashed': len(files),
                      'snapshot_sha256': sha(snapshot), 'manifest_sha256': sha(target)}))


if __name__ == '__main__': main()
