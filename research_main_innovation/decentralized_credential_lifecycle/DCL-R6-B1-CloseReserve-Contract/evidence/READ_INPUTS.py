"""Verify frozen inputs for the B1 close-contract research delivery only."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
PREVIOUS = ROOT / 'DCL-R6-B1-ApprovalGate'
OUT = ROOT / 'DCL-R6-B1-CloseReserve-Contract'
E = OUT / 'evidence'
RUNTIME = Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01')
ISOLATED = RUNTIME.parent
NAV = ('CURRENT_VERDICT.md', 'NEXT_ACTION.md', 'README.md', 'DECISION_HISTORY.md')

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1048576), b''):
            result.update(data)
    return result.hexdigest()

def record(path):
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)}

def save(name, data):
    path = E / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)

def initialize():
    E.mkdir(parents=True, exist_ok=True)
    assert not (E / 'INITIAL_CHECK.json').exists()
    earlier = read(PREVIOUS / 'evidence/ALL_PRIOR_BASELINE.json')['files']
    latest = [record(path) for path in sorted(PREVIOUS.rglob('*')) if path.is_file()]
    assert len(earlier) == 10454 and len(latest) == 141
    baseline = earlier + latest
    assert len(baseline) == len({item['path'] for item in baseline}) == 10595
    errors = []
    for item in baseline:
        path = Path(item['path'])
        if not path.is_file() or path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            errors.append(str(path))
    assert not errors, errors
    current = {str(path) for base in (ROOT, ISOLATED) for path in base.rglob('*')
               if path.is_file() and not path.is_relative_to(OUT)
               and not (path.parent == ROOT and path.name in NAV)}
    assert current == {item['path'] for item in baseline}
    save('ALL_PRIOR_BASELINE.json', {'historical_files': 9867, 'previous_deliveries': 728, 'files': baseline})
    lock = read(PREVIOUS / 'evidence/FROZEN_SOURCE_LOCK.json')
    sources = []
    for item in lock['files']:
        source = Path(item['path'])
        assert sha(source) == item['sha256']
        destination = E / 'FROZEN_RUNTIME' / item['relative']
        copy(source, destination)
        sources.append({**item, 'copy': str(destination)})
    assert len(sources) == 64
    save('FROZEN_SOURCE_LOCK.json', {'version': lock['version'], 'files': sources})
    nav = []
    for name in NAV:
        source = ROOT / name
        destination = E / 'NAV_ORIGINALS' / name
        copy(source, destination)
        nav.append({**record(source), 'copy': str(destination)})
    save('NAV_BASELINE.json', {'files': nav})
    request = Path(r'C:\Users\a1887\.codex\attachments\7c46f65c-a714-432c-9e66-a1d52a7b2a15\Pasted text.txt')
    copy(request, E / 'TASK_REQUEST.txt')
    previous_bindings = read(PREVIOUS / 'evidence/APPROVAL_OBJECT_BINDINGS.json')
    for item in previous_bindings['files']:
        assert sha(item['path']) == item['sha256']
        data = read(item['path'])
        assert all(data[key] is False for key in ('approved', 'user_approved', 'effective', 'runtime_enabled'))
        assert data['user_decision'] is None
    save('PREVIOUS_APPROVAL_BINDINGS.json', previous_bindings)
    archive_path = PREVIOUS / 'B1AG_EVIDENCE.zip'
    manifest_path = PREVIOUS / 'B1AG_MANIFEST.json'
    assert sha(archive_path) == '7a626c8e9b213cc5a6e2a3c309a2b21b648219311469e8385e71f298ceba32e7'
    manifest = read(manifest_path)
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)) == 138
        assert set(names) == {item['relative'] for item in manifest['files']} | {manifest_path.name}
        for item in manifest['files']:
            data = archive.read(item['relative'])
            assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
            assert sha(PREVIOUS / item['relative']) == item['sha256']
        assert archive.read(manifest_path.name) == manifest_path.read_bytes()
    save('PREVIOUS_ARCHIVE_RECHECK.json', {'archive': record(archive_path), 'manifest': record(manifest_path),
                                          'members': 138, 'CRC_SHA_size_set_match': True})
    save('INITIAL_CHECK.json', {'historical_unchanged': 9867, 'previous_delivery_unchanged': 728,
                               'all_prior_unchanged': 10595, 'frozen_source_inputs': 64,
                               'mismatches': errors, 'runtime_imports': 0, 'source_edits': 0,
                               'WSL_calls': 0, 'dynamic_tests': 0, 'new_approval': False})
    print(json.dumps({'source64': 'MATCH', 'all_prior': 10595, 'archive_members': 138, 'source_edits': 0}))

if __name__ == '__main__':
    initialize()
