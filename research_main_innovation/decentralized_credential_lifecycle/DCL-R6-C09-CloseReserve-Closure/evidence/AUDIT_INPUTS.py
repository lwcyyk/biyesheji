"""Host evidence collection and hash arithmetic only; no runtime/mechanism code.

Reads frozen inputs and writes this research delivery. No target imports,
protocol replay, WSL/service calls, quota allocation or model execution.
"""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
PREV=ROOT/'DCL-R6-C09-PendingQuota-Closure'
BOUND=ROOT/'DCL-R6-C09-BoundClosure'
OUT=ROOT/'DCL-R6-C09-CloseReserve-Closure'
E=OUT/'evidence'
RUNTIME=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01')
ISOLATED=RUNTIME.parent
NAV=('CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md')

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(name,x):
    p=E/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def row(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def cp(p,q):
    q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)

def main():
    E.mkdir(parents=True,exist_ok=True)
    assert not (E/'INITIAL_INPUT_CHECK.json').exists()
    hbase=read(PREV/'evidence/HISTORY_BASELINE_9867.json')['files']
    assert len(hbase)==9867
    old=read(PREV/'evidence/PREVIOUS_DELIVERY_BASELINE.json')['files']
    assert len(old)==160
    latest=[row(p) for p in sorted(PREV.rglob('*')) if p.is_file()]
    assert len(latest)==147
    allrows=hbase+old+latest
    assert len(allrows)==len({r['path'] for r in allrows})==10174
    bad=[r['path'] for r in allrows if not Path(r['path']).is_file() or Path(r['path']).stat().st_size!=r['bytes'] or sha(r['path'])!=r['sha256']]
    assert not bad,bad
    current={str(p) for base in [ROOT,ISOLATED] for p in base.rglob('*') if p.is_file() and not p.is_relative_to(OUT) and not(p.parent==ROOT and p.name in NAV)}
    assert current=={r['path'] for r in allrows}
    save('ALL_PRIOR_BASELINE.json',{'historical9867':len(hbase),'BoundClosure160':len(old),'PendingQuota147':len(latest),'files':allrows})
    cp(PREV/'evidence/HISTORY_BASELINE_9867.json',E/'HISTORY_BASELINE_9867.json')
    source=read(PREV/'evidence/FROZEN_SOURCE_LOCK.json');source_rows=[]
    for r in source['files']:
        p=Path(r['path']);assert sha(p)==r['sha256']
        q=E/'FROZEN_RUNTIME'/r['relative'];cp(p,q)
        source_rows.append({**r,'copy':str(q)})
    assert len(source_rows)==64
    save('FROZEN_SOURCE_LOCK.json',{'version':source['version'],'files':source_rows,'runtime_edits':0})
    nav=[]
    for n in NAV:
        p=ROOT/n;q=E/'NAV_ORIGINALS'/n;cp(p,q);nav.append({**row(p),'copy':str(q)})
    save('NAV_BASELINE.json',{'files':nav})
    cp(Path(r'C:\Users\a1887\.codex\attachments\2c2c52ab-e95a-4d2c-8e43-4aaaf4a680e7\Pasted text.txt'),E/'TASK_REQUEST.txt')
    zip_checks=[]
    for base,mname,zname,expected in [
      (PREV,'PQUOTA_MANIFEST.json','PQUOTA_EVIDENCE.zip','96760e5dccb441f4420abbb7b4db59ba50790ddda161ea9334e7076a575c8f94'),
      (BOUND,'C09BOUND_MANIFEST.json','C09BOUND_EVIDENCE.zip','deced07f132a3ee0e0d724d1252fada234f56fd9fd2bc37e7b35d1fb7eb53cea')]:
        manifest=read(base/mname);assert sha(base/zname)==expected
        with zipfile.ZipFile(base/zname) as z:
            names=z.namelist();assert len(names)==len(set(names))==len(manifest['files'])+1
            assert set(names)=={r['relative'] for r in manifest['files']}|{mname}
            for r in manifest['files']:
                b=z.read(r['relative']);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
                assert sha(base/r['relative'])==r['sha256']
            assert z.read(mname)==(base/mname).read_bytes()
        zip_checks.append({'archive':row(base/zname),'manifest':row(base/mname),'files':len(manifest['files']),'members':len(names),'full_CRC_SHA_match':True})
    save('PRIOR_ARCHIVE_CHECK.json',{'archives':zip_checks})
    save('INITIAL_INPUT_CHECK.json',{'historical9867_unchanged':9867,'all_prior_unchanged':10174,
         'frozen_runtime_source_inputs':64,'source_mismatches':[],'prior_delivery_objects':307,
         'prior_archive_members_read':sum(r['members'] for r in zip_checks),'runtime_imports':0,
         'runtime_changes':0,'dynamic_calls':0,'WSL_calls':0})
    print(json.dumps(read(E/'INITIAL_INPUT_CHECK.json')))

if __name__=='__main__':main()
