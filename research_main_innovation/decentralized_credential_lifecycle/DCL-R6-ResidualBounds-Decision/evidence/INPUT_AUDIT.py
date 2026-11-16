"""Read-only evidence verification and research outputs. No DCL mechanisms run."""
from pathlib import Path
import hashlib,json,shutil,zipfile

ROOT=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
PREV=ROOT/'DCL-R6-C09-CloseReserve-Closure'
OUT=ROOT/'DCL-R6-ResidualBounds-Decision'
E=OUT/'evidence'
RUNTIME=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01')
ISO=RUNTIME.parent
NAV=('CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    d=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):d.update(b)
    return d.hexdigest()
def row(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def save(n,x):
    p=E/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def cp(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)

def initialize():
    E.mkdir(parents=True,exist_ok=True);assert not(E/'INITIAL_CHECK.json').exists()
    prior=read(PREV/'evidence/ALL_PRIOR_BASELINE.json')['files']
    latest=[row(p) for p in sorted(PREV.rglob('*')) if p.is_file()]
    assert len(prior)==10174 and len(latest)==143
    allrows=prior+latest;assert len({r['path'] for r in allrows})==len(allrows)==10317
    bad=[r['path'] for r in allrows if not Path(r['path']).is_file() or Path(r['path']).stat().st_size!=r['bytes'] or sha(r['path'])!=r['sha256']]
    assert not bad,bad
    actual={str(p) for base in [ROOT,ISO] for p in base.rglob('*') if p.is_file() and not p.is_relative_to(OUT) and not(p.parent==ROOT and p.name in NAV)}
    assert actual=={r['path'] for r in allrows}
    save('ALL_PRIOR_BASELINE.json',{'historical9867':9867,'earlier_deliveries450':450,'files':allrows})
    cp(PREV/'evidence/HISTORY_BASELINE_9867.json',E/'HISTORY_BASELINE_9867.json')
    src=read(PREV/'evidence/FROZEN_SOURCE_LOCK.json');new=[]
    for r in src['files']:
        p=Path(r['path']);assert sha(p)==r['sha256'];q=E/'FROZEN_RUNTIME'/r['relative'];cp(p,q)
        new.append({**r,'copy':str(q)})
    assert len(new)==64;save('FROZEN_SOURCE_LOCK.json',{'version':src['version'],'files':new})
    nav=[]
    for n in NAV:
        p=ROOT/n;q=E/'NAV_ORIGINALS'/n;cp(p,q);nav.append({**row(p),'copy':str(q)})
    save('NAV_BASELINE.json',{'files':nav})
    cp(Path(r'C:\Users\a1887\.codex\attachments\d45cc481-2706-4e03-b064-f7fe5c305fc5\Pasted text.txt'),E/'TASK_REQUEST.txt')
    m=read(PREV/'CRB_MANIFEST.json');zpath=PREV/'CRB_EVIDENCE.zip'
    assert sha(zpath)=='ae07ee35dcd3501011970d2ed83e32c686b695e0460b4535ae1eb4ba43dd3e8e'
    with zipfile.ZipFile(zpath) as z:
        names=z.namelist();assert len(names)==len(set(names))==140
        assert set(names)=={r['relative'] for r in m['files']}|{'CRB_MANIFEST.json'}
        for r in m['files']:
            b=z.read(r['relative']);assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
            assert sha(PREV/r['relative'])==r['sha256']
        assert z.read('CRB_MANIFEST.json')==(PREV/'CRB_MANIFEST.json').read_bytes()
    draft=[]
    for n,x in [('CLOSE_RESERVE_REVIEW_DRAFT.json','44980a113bda747f5e4e64ce47d6b782290a47e8bd3699f59623ecb0b045714a'),
      ('CAPACITY_REVIEW_DRAFT.json','44308e849c9ea2451cc1eb1443c00b88a874f523739d4129c202446132246d07')]:
        p=PREV/'proposals'/n;d=read(p);assert sha(p)==x
        assert d['user_approved']is False and d['effective']is False and d['runtime_enabled']is False
        draft.append({**row(p),'approved_field_present':'approved'in d,'user_approved':False,'effective':False,'runtime_enabled':False,
                      'top_level_nulls':[k for k,v in d.items() if v is None]})
    save('INITIAL_CHECK.json',{'source64':'MATCH','historical9867':'UNCHANGED','all_prior10317':'UNCHANGED',
      'drafts':draft,'approval_alias_note':'original files use user_approved=false; literal approved field absent; no approval receipt inferred',
      'previous_archive_members_verified':140,'runtime_edits':0,'dynamic_runs':0,'WSL_calls':0})
    print({'prior':10317,'source':64,'archive_members':140,'approval_or_activation':False})

if __name__=='__main__':initialize()
