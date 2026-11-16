"""Snapshot/verify historical bytes; no writes to historical directories."""
import bootstrap
import json, hashlib, argparse
from pathlib import Path
ROOT = bootstrap.ROOT
TARGETS = [bootstrap.ORIGINAL, bootstrap.OLD,
 bootstrap.WORKSPACE/'研究/主线与密码学机制融合_2026-11-03']
def collect():
    out={};skipped=[]
    for base in TARGETS:
        for p in sorted(base.rglob('*')):
            if p.is_file():
                try:out[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
                except OSError as e:skipped.append({'path':str(p),'reason':type(e).__name__})
    (ROOT/'historical_unreadable.json').write_text(json.dumps(skipped,ensure_ascii=False,indent=2),encoding='utf-8')
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--verify',action='store_true');a=ap.parse_args()
    current=collect();path=ROOT/'historical_sha256.json'
    if a.verify:
        old=json.loads(path.read_text(encoding='utf-8'))
        changes=[p for p,h in old.items() if current.get(p)!=h]
        result={'checked':len(old),'changed_or_missing':changes,'new_files':[p for p in current if p not in old],'pass':not changes}
        result['runtime_metadata_changes']=[p for p in changes if '/.runtime/' in p.replace('\\','/')]
        result['non_runtime_changes']=[p for p in changes if '/.runtime/' not in p.replace('\\','/')]
        result['non_runtime_pass']=not result['non_runtime_changes']
        result['attribution']='No task write to historical paths; runtime metadata change origin not established. All-readable pass remains false if any byte changed.'
        (ROOT/'historical_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False))
    else:
        if path.exists():raise SystemExit('baseline already exists; refusing overwrite')
        path.write_text(json.dumps(current,ensure_ascii=False,indent=2),encoding='utf-8');print('snapshot',len(current))
