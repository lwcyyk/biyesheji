"""Host-only evidence inventory and arithmetic. Never imports or runs runtime code.

This file is administrative research tooling, not a logger/quota implementation.
It reads frozen inputs and writes only this new delivery directory.
"""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from collections import Counter

ROOT = Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
OLD = ROOT / 'DCL-R6-C09-BoundClosure'
OUT = ROOT / 'DCL-R6-C09-PendingQuota-Closure'
E = OUT / 'evidence'
RUNTIME = Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01')

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name, obj):
    p = E / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def row(p): return {'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)}

def initialize():
    E.mkdir(parents=True, exist_ok=True)
    assert not (E/'INITIAL_INTEGRITY.json').exists(), 'Initialize once only'
    history = read(OLD/'evidence/HISTORY_BASELINE.json')['files']
    errors = [r['path'] for r in history if not Path(r['path']).is_file() or
              Path(r['path']).stat().st_size != r['bytes'] or sha(r['path']) != r['sha256']]
    assert len(history) == 9867 and not errors, errors
    shutil.copyfile(OLD/'evidence/HISTORY_BASELINE.json', E/'HISTORY_BASELINE_9867.json')
    oldrows = [row(p) for p in sorted(OLD.rglob('*')) if p.is_file()]
    write('PREVIOUS_DELIVERY_BASELINE.json', {'files': oldrows})
    lock = read(OLD/'evidence/SOURCE_AND_PRIOR_LOCK_CHECK.json')
    verified = []
    for r in lock['runtime_files']:
        p = RUNTIME/r['relative']
        assert sha(p) == r['sha256'] and p.stat().st_size == r['bytes'], str(p)
        q = E/'FROZEN_RUNTIME'/r['relative']; q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, q)
        verified.append({**r, 'path':str(p), 'copy':str(q)})
    write('FROZEN_SOURCE_LOCK.json', {'version':'RuntimeAdapt-static-1/r1', 'files':verified})
    prior = []
    for key, base in [('review_objects',ROOT/'DCL-R6-FullChain-AdmissionFix'),
                      ('previous_contract_review_files', ROOT/'DCL-R6-EvidenceContract-Closure')]:
        for r in lock[key]:
            p = base/r['relative']; assert sha(p)==r['sha256'], str(p)
            prior.append({**r,'path':str(p)})
    write('PRIOR_OBJECT_LOCK.json', {'files':prior})
    nav = []
    for name in ['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']:
        p=ROOT/name; q=E/'NAV_ORIGINALS'/name; q.parent.mkdir(exist_ok=True)
        shutil.copyfile(p,q); nav.append({**row(p),'copy':str(q)})
    write('NAV_BASELINE.json', {'files':nav})
    zpath=OLD/'C09BOUND_EVIDENCE.zip'
    assert sha(zpath)=='deced07f132a3ee0e0d724d1252fada234f56fd9fd2bc37e7b35d1fb7eb53cea'
    manifest=read(OLD/'C09BOUND_MANIFEST.json'); zchecks=[]
    with zipfile.ZipFile(zpath) as z:
        names=z.namelist(); assert len(names)==len(set(names))==157
        expected={r['relative'] for r in manifest['files']}|{'C09BOUND_MANIFEST.json'}
        assert set(names)==expected
        for r in manifest['files']:
            data=z.read(r['relative'])
            assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
            assert sha(OLD/r['relative'])==r['sha256']
            zchecks.append(r['relative'])
        assert z.read('C09BOUND_MANIFEST.json')==(OLD/'C09BOUND_MANIFEST.json').read_bytes()
    write('PREVIOUS_ZIP_FULL_VERIFICATION.json', {'zip':row(zpath),'manifest':row(OLD/'C09BOUND_MANIFEST.json'),
          'manifest_files':len(zchecks),'members':len(names),'all_members_read_crc_and_sha_checked':True,'errors':[]})
    rawbase=OLD/'evidence/HISTORICAL_RAW'
    for p in rawbase.iterdir():
        if p.is_file():
            q=E/'HISTORICAL_RAW'/p.name;q.parent.mkdir(exist_ok=True);shutil.copyfile(p,q)
    request=Path(r'C:\Users\a1887\.codex\attachments\7ed56acc-71cf-4599-a084-a1b150ad57e0\Pasted text.txt')
    shutil.copyfile(request,E/'TASK_REQUEST.txt')
    write('INITIAL_INTEGRITY.json', {'historical_files':len(history),'historical_errors':errors,
        'previous_delivery_files':len(oldrows),'runtime_files':len(verified),'prior_review_and_contract_objects':len(prior),
        'previous_zip_members_verified':len(names),'target_imports':0,'dynamic_runs':0,'runtime_edits':0})
    print(json.dumps(read(E/'INITIAL_INTEGRITY.json'),ensure_ascii=False))

if __name__=='__main__': initialize()
