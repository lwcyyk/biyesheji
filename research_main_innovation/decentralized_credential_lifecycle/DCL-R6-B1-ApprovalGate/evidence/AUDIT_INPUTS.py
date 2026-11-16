"""Collect immutable inputs for the authorized B1 contract review.

This administrative script hashes and copies research inputs. It does not
import target modules, create a runtime instance or implement the proposed diff.
"""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
PREVIOUS = ROOT / 'DCL-R6-ResidualBounds-Decision'
OUT = ROOT / 'DCL-R6-B1-ApprovalGate'
EVIDENCE = OUT / 'evidence'
RUNTIME = Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01')
ISOLATED = RUNTIME.parent
NAVIGATION = ('CURRENT_VERDICT.md', 'NEXT_ACTION.md', 'README.md', 'DECISION_HISTORY.md')

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            result.update(block)
    return result.hexdigest()

def file_record(path):
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)}

def save(name, value):
    target = EVIDENCE / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def copy_file(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)

def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    assert not (EVIDENCE / 'INITIAL_INTEGRITY.json').exists()
    earlier = read_json(PREVIOUS / 'evidence/ALL_PRIOR_BASELINE.json')['files']
    latest = [file_record(path) for path in sorted(PREVIOUS.rglob('*')) if path.is_file()]
    assert len(earlier) == 10317 and len(latest) == 137
    baseline = earlier + latest
    assert len(baseline) == len({item['path'] for item in baseline}) == 10454
    mismatches = []
    for item in baseline:
        path = Path(item['path'])
        if not path.is_file() or path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            mismatches.append(str(path))
    assert not mismatches, mismatches
    actual = {str(path) for base in (ROOT, ISOLATED) for path in base.rglob('*')
              if path.is_file() and not path.is_relative_to(OUT)
              and not (path.parent == ROOT and path.name in NAVIGATION)}
    assert actual == {item['path'] for item in baseline}
    save('ALL_PRIOR_BASELINE.json', {'historical_files': 9867, 'prior_delivery_files': 587, 'files': baseline})
    source_lock = read_json(PREVIOUS / 'evidence/FROZEN_SOURCE_LOCK.json')
    copied = []
    for item in source_lock['files']:
        path = Path(item['path'])
        assert digest(path) == item['sha256']
        destination = EVIDENCE / 'FROZEN_RUNTIME' / item['relative']
        copy_file(path, destination)
        copied.append({**item, 'copy': str(destination)})
    assert len(copied) == 64
    save('FROZEN_SOURCE_LOCK.json', {'version': source_lock['version'], 'files': copied})
    nav = []
    for name in NAVIGATION:
        path = ROOT / name
        destination = EVIDENCE / 'NAV_ORIGINALS' / name
        copy_file(path, destination)
        nav.append({**file_record(path), 'copy': str(destination)})
    save('NAVIGATION_BASELINE.json', {'files': nav})
    request = Path(r'C:\Users\a1887\.codex\attachments\704dbf73-dbec-4e59-89f5-92f94b40045f\Pasted text.txt')
    copy_file(request, EVIDENCE / 'TASK_REQUEST.txt')

    bindings = read_json(PREVIOUS / 'evidence/DECISION_BINDINGS.json')
    checks = []
    for label, item in bindings.items():
        path = Path(item['path'])
        assert digest(path) == item['sha256']
        data = read_json(path)
        flags = {key: {'present': key in data, 'value': data.get(key)}
                 for key in ('approved', 'user_approved', 'effective', 'runtime_enabled')}
        assert data['user_approved'] is False and data['runtime_enabled'] is False
        assert all(entry['value'] is False for entry in flags.values() if entry['present'])
        checks.append({'label': label, **file_record(path), 'flags': flags,
                       'null_fields': [key for key, value in data.items() if value is None]})
        copy_file(path, EVIDENCE / 'PRIOR_PROPOSALS' / path.parent.parent.name / path.name)
    quota = ROOT / 'DCL-R6-C09-PendingQuota-Closure/proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json'
    assert digest(quota) == '7effe4e39e1eae665153bae4e16f7d2a20513a574fc26a4873ded5a81ef680ae'
    quota_data = read_json(quota)
    copy_file(quota, EVIDENCE / 'PRIOR_PROPOSALS' / quota.parent.parent.name / quota.name)
    aliases = []
    for name, key in [('CAPACITY_REVIEW_DRAFT.json', 'prior_capacity_draft'),
                      ('CLOSE_RESERVE_REVIEW_DRAFT.json', 'prior_close_draft')]:
        requested = PREVIOUS / 'proposals' / name
        assert not requested.exists()
        aliases.append({'requested_path': str(requested), 'actual_path': bindings[key]['path'],
                        'resolution': 'ResidualBounds DECISION_BINDINGS points to frozen CloseReserve draft'})
    save('DRAFT_HASH_AND_STATUS_CHECK.json', {
        'objects': checks, 'requested_path_resolution': aliases,
        'quota_v2': file_record(quota),
        'quota_v2_schema_field_observed': quota_data['schema'],
        'quota_v2_format_note': 'The top-level schema field contains a field-profile sentence. Bind review to exact file digest, version and main_limits. A future version needs a unique schema identifier.',
        'historical_source_files_modified': False, 'approval_received': False})

    manifest_path = PREVIOUS / 'RBD_MANIFEST.json'
    archive_path = PREVIOUS / 'RBD_EVIDENCE.zip'
    assert digest(archive_path) == '08abd5ff14d0445389b6d632a67f023efeaaefb110f461ef39636ce3ead93f12'
    manifest = read_json(manifest_path)
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)) == 134
        assert set(names) == {item['relative'] for item in manifest['files']} | {manifest_path.name}
        for item in manifest['files']:
            data = archive.read(item['relative'])
            assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
            assert digest(PREVIOUS / item['relative']) == item['sha256']
        assert archive.read(manifest_path.name) == manifest_path.read_bytes()
    save('PRIOR_ARCHIVE_RECHECK.json', {'archive': file_record(archive_path), 'manifest': file_record(manifest_path),
                                       'members_verified': 134, 'CRC_SHA_size_set_match': True})
    save('INITIAL_INTEGRITY.json', {'historical_files_unchanged': 9867, 'prior_delivery_files_unchanged': 587,
                                   'all_prior_files_unchanged': 10454, 'runtime_objects': 64,
                                   'mismatches': mismatches, 'runtime_imports': 0, 'dynamic_runs': 0,
                                   'WSL_calls': 0, 'approval_received': False})
    print(json.dumps({'prior': 10454, 'runtime_objects': 64, 'drafts': len(checks),
                      'requested_draft_aliases_resolved': 2, 'archive_members': 134}))

if __name__ == '__main__':
    main()
