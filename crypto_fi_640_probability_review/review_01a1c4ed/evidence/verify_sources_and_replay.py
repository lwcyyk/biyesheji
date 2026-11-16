from pathlib import Path
import os, sys, json, hashlib, subprocess

BASE=Path(r'D:\毕业设计')
OUT=Path(__file__).resolve().parents[1]
EV=OUT/'evidence'
sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)

def verify(rec):
    p=Path(rec['path'])
    if not p.is_file(): return dict(path=str(p),exists=False,pass_check=False)
    raw=p.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    return dict(path=str(p),bytes=len(raw),sha256=digest,pass_check=(digest.lower()==rec['sha256'].lower() and len(raw)==rec.get('bytes',len(raw))))

snap=json.loads((EV/'INPUT_SNAPSHOT.json').read_text(encoding='utf-8'))
snapshot_checks=[verify(r) for r in snap['records']]
assert all(x['pass_check'] for x in snapshot_checks)
manifest_checks=[]
def walk(v,source):
    if isinstance(v,dict):
        if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str) and len(v['sha256'])==64:
            item=verify(v); item['record_source']=source
            manifest_checks.append(item)
        for val in v.values(): walk(val,source)
    elif isinstance(v,list):
        for val in v:walk(val,source)
for dirname in ('crypto_fi_640_correctness_audit','crypto_fi_640_joint_correctness'):
    for p in sorted((BASE/dirname).rglob('*.json')):
        walk(json.loads(p.read_text(encoding='utf-8')),str(p))
assert all(x['pass_check'] for x in manifest_checks)
(EV/'INPUT_HASH_VERIFICATION.json').write_text(json.dumps(dict(snapshot_count=len(snapshot_checks),snapshot_checks=snapshot_checks,referenced_record_count=len(manifest_checks),referenced_record_checks=manifest_checks,all_match=True),ensure_ascii=False,indent=2),encoding='utf-8')

runtime=Path(r'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
preflight=Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\scripts\pdf_read_preflight.py')
env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
preflight_results=[]
for filename,sidecar in [('FI_journal_20261110.pdf','FI_PREFLIGHT.json'),('official_frodo_2021.pdf','FRODO_PREFLIGHT.json')]:
    p=BASE/'crypto_fi_640_correctness_audit'/'sources'/filename
    r=subprocess.run([str(runtime),str(preflight),str(p)],capture_output=True,encoding='utf-8',env=env,check=True)
    data=json.loads(r.stdout)
    assert data['verdict']=='PASS' and data['file']==str(p)
    assert data['sha256']==hashlib.sha256(p.read_bytes()).hexdigest()
    (EV/sidecar).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    preflight_results.append(data)

replay=[]
for folder,script,cert,ignored in [
    ('crypto_fi_640_correctness_audit','compute_scalar_certificates.py','SCALAR_CERTIFICATES.json',['elapsed_seconds_display_only']),
    ('crypto_fi_640_joint_correctness','compute_joint_certificates.py','JOINT_SCALAR_CERTIFICATES.json',[])]:
    src=BASE/folder/'evidence'
    dst=EV/'author_replay'/folder/'evidence'
    dst.mkdir(parents=True,exist_ok=True)
    raw=(src/script).read_bytes();(dst/script).write_bytes(raw)
    r=subprocess.run([sys.executable,str(dst/script)],capture_output=True,encoding='utf-8',env=env,check=True)
    (dst/'STDOUT.txt').write_text(r.stdout,encoding='utf-8')
    got=json.loads((dst/cert).read_text(encoding='utf-8'))
    ref=json.loads((src/cert).read_text(encoding='utf-8'))
    for key in ignored:got.pop(key,None);ref.pop(key,None)
    assert got==ref
    replay.append(dict(source_script=str(src/script),script_sha256=hashlib.sha256(raw).hexdigest(),isolated_script=str(dst/script),result_file=str(dst/cert),all_certifying_fields_equal=True,ignored_display_fields=ignored))
(EV/'SOURCE_AND_REPLAY_VERIFICATION.json').write_text(json.dumps(dict(preflight=preflight_results,preflight_recovery='Windows --output mode requires POSIX dirfd; legacy stdout captured with explicit UTF-8 and saved without changing result.',author_replays=replay,all_passed=True),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(historical_snapshot_records=len(snapshot_checks),referenced_hash_records=len(manifest_checks),preflight_pass=len(preflight_results),author_replays_equal=len(replay)),ensure_ascii=False))
