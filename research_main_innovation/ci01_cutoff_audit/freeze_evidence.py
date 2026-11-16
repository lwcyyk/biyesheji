"""Copy and hash read-only evidence; no authentication mechanism or native calls."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'ci01_contract_audit'
SRC = OLD / 'sources/casdoor-v4.25.0'
PROJECT = Path(r'D:\毕业设计\auth-lifecycle')
COMMIT = '528a0213f01caf70b9f41009cbf7b2f67bdd67ec'

def digest(p):
    return sha256(p.read_bytes()).hexdigest()

def main():
    manifest_path = ROOT / 'HISTORICAL_INPUT_HASHES.json'
    if manifest_path.exists():
        raise RuntimeError('freeze already exists')
    files = [p for p in OLD.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
    files += [PROJECT / x for x in ['src/auth_lifecycle/experiment/providers.py',
        'src/auth_lifecycle/experiment/witness.py', 'docs/experiments/CAPABILITIES.md',
        'docs/experiments/RESULTS.md', 'experiments/l1/environment.lock.json',
        'experiments/l1/distributions.json']]
    papers = Path(r'D:\毕业设计\关键论文与可行性核查_2026-11-04\阅读记录')
    files += [papers / x for x in ['P03_全文.txt','P05_全文.txt','P08_全文.txt']]
    manifest = [{'path':str(p),'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(set(files))]
    manifest_path.write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'files':manifest}, ensure_ascii=False,indent=2),encoding='utf-8')
    selected = ['controllers/token.go','controllers/session.go','controllers/account.go',
        'controllers/auth.go','controllers/application.go','controllers/util.go',
        'object/token.go','object/token_oauth.go','object/token_oauth_util.go','object/token_jwt.go',
        'object/session.go','object/application.go','object/ormer_session.go','object/user.go',
        'routers/auto_signin_filter.go','routers/authz_filter.go','routers/base.go',
        'routers/session_provider.go','routers/router.go']
    copied=[]
    for rel in selected:
        p=SRC/rel
        if not p.exists():
            continue
        q=ROOT/'sources/casdoor-v4.25.0'/rel
        q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,q)
        copied.append({'path':str(q.relative_to(ROOT)),'origin':str(p),'sha256':digest(q),'commit':COMMIT})
    for rel in ['util/time.go','util/string.go','go.mod']:
        url=f'https://raw.githubusercontent.com/casdoor/casdoor/{COMMIT}/{rel}'
        q=ROOT/'sources/casdoor-v4.25.0'/rel
        q.parent.mkdir(parents=True,exist_ok=True)
        try:
            with urllib.request.urlopen(url,timeout=30) as r:
                data=r.read()
            q.write_bytes(data)
            copied.append({'path':str(q.relative_to(ROOT)),'url':url,'sha256':digest(q),'commit':COMMIT,'retrieval':'HTTPS fixed commit'})
        except Exception as e:
            copied.append({'url':url,'status':'UNAVAILABLE','exception_type':type(e).__name__})
    (ROOT/'SOURCE_MANIFEST.json').write_text(json.dumps(copied,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'historical_files':len(manifest),'source_entries':len(copied),'downloaded':sum('url' in x and 'sha256' in x for x in copied)}))

if __name__=='__main__':
    main()
