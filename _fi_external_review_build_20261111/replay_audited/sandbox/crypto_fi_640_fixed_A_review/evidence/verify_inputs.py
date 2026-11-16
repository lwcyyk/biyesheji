"""Read-only source fingerprints and immutable review input snapshot."""
from pathlib import Path
import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo

BASE = Path(r'D:\毕业设计')
OUT = BASE / 'crypto_fi_640_fixed_A_review'
SRC = BASE / 'crypto_fi_640_fixed_A_correctness'

def record(path):
    b = path.read_bytes()
    return {'path': str(path), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def hash_nodes(obj, locator='$'):
    if isinstance(obj, dict):
        if isinstance(obj.get('path'), str) and isinstance(obj.get('sha256'), str):
            yield locator, obj
        for k, v in obj.items():
            yield from hash_nodes(v, locator + '.' + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from hash_nodes(v, locator + '[' + str(i) + ']')

def main():
    snapshot = OUT / 'evidence' / 'INPUT_SNAPSHOT.json'
    if snapshot.exists():
        old = json.loads(snapshot.read_text(encoding='utf-8'))
        changes = []
        all_records = {item['path']: item for item in old['files']}
        refs = json.loads((OUT / 'evidence' / 'EMBEDDED_FINGERPRINT_CHECK.json').read_text(encoding='utf-8'))
        for item in refs['records']:
            value = item['target']
            all_records[value['path']] = value
        for item in all_records.values():
            now = record(Path(item['path']))
            if now != item:
                changes.append({'before': item, 'after': now})
        result = {'schema': 'fi640-fixed-A-review/input-recheck/1',
                  'direct_historical_files_rechecked': len(old['files']),
                  'historical_files_rechecked_including_references': len(all_records),
                  'historical_inputs_unchanged': not changes, 'changes': changes}
        (OUT / 'evidence' / 'INPUT_RECHECK.json').write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        assert not changes, changes
        print(json.dumps(result, ensure_ascii=False))
        return
    paths = {p.resolve() for p in SRC.rglob('*') if p.is_file()}
    lock = json.loads((SRC / 'evidence' / 'INPUT_LOCK.json').read_text(encoding='utf-8-sig'))
    paths.update(Path(x['path']).resolve() for x in lock['files'])
    checked = []
    for source in sorted(paths):
        if source.suffix.lower() != '.json':
            continue
        data = json.loads(source.read_text(encoding='utf-8-sig'))
        for locator, item in hash_nodes(data):
            p = Path(item['path'])
            if not p.is_absolute():
                p = source.parent / p
            got = record(p)
            match = got['sha256'].lower() == item['sha256'].lower()
            if 'bytes' in item:
                match = match and got['bytes'] == item['bytes']
            checked.append({'source': str(source), 'locator': locator,
                            'target': got, 'matched': match})
            assert match, checked[-1]
    result = {'schema': 'fi640-fixed-A-review/input-snapshot/1',
              'date_asia_shanghai': '2026-11-11',
              'snapshot_scope': 'All 10 submitted-package files plus 84 historical lock entries; hashes do not attest semantic reading',
              'files': [record(p) for p in sorted(paths)]}
    snapshot.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    refs = {'schema': 'fi640-fixed-A-review/embedded-fingerprint-check/1',
            'records_checked': len(checked), 'all_matched': True, 'records': checked}
    (OUT / 'evidence' / 'EMBEDDED_FINGERPRINT_CHECK.json').write_text(
        json.dumps(refs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'historical_files_snapshotted': len(paths),
                      'embedded_fingerprints_checked': len(checked), 'all_matched': True}))

if __name__ == '__main__':
    main()
