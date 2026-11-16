"""Acquire public frozen source and official Go toolchain; no service calls."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,urllib.request,zipfile,shutil

ROOT=Path(__file__).resolve().parent
COMMIT='528a0213f01caf70b9f41009cbf7b2f67bdd67ec'
def fetch(url,path):
    if path.exists():return path.read_bytes()
    path.parent.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(url,headers={'User-Agent':'local-offline-policy-regression'})
    with urllib.request.urlopen(req,timeout=45) as resp, path.open('xb') as f:
        while True:
            chunk=resp.read(1024*1024)
            if not chunk:break
            f.write(chunk)
    return path.read_bytes()
def main():
    history=[]
    previous=ROOT.parent/'ci01_policy_consistency_review'
    for p in previous.rglob('*'):
        if p.is_file() and not any(x in {'.gocache','.gotmp','.gopath','__pycache__'} for x in p.relative_to(previous).parts):
            history.append({'path':str(p),'sha256':sha256(p.read_bytes()).hexdigest()})
    (ROOT/'HISTORICAL_HASHES.json').write_text(json.dumps(history,ensure_ascii=False,indent=2),encoding='utf-8')
    log=[]
    tasks=[('source',f'https://codeload.github.com/casdoor/casdoor/zip/{COMMIT}','casdoor.zip'),
           ('go_index','https://go.dev/dl/?mode=json&include=all','go_releases.json')]
    for kind,url,name in tasks:
        try:
            data=fetch(url,ROOT/'downloads'/name)
            log.append({'kind':kind,'url':url,'sha256':sha256(data).hexdigest(),'bytes':len(data),'status':'ACQUIRED'})
            print(kind,len(data),flush=True)
        except Exception as e:log.append({'kind':kind,'url':url,'status':'UNAVAILABLE','error':type(e).__name__,'http':getattr(e,'code',None)})
    index=ROOT/'downloads/go_releases.json'
    if index.exists():
        versions=json.loads(index.read_text(encoding='utf-8'))
        entry=next((f for v in versions if v['version']=='go1.26.10' for f in v['files'] if f['filename']=='go1.26.10.windows-amd64.zip'),None)
        if entry:
            url='https://go.dev/dl/'+entry['filename']
            try:
                data=fetch(url,ROOT/'downloads'/entry['filename']);digest=sha256(data).hexdigest()
                if digest!=entry['sha256']:raise RuntimeError('official Go checksum mismatch')
                log.append({'kind':'go_toolchain','url':url,'sha256':digest,'official_sha256':entry['sha256'],'bytes':len(data),'status':'VERIFIED'})
                print('Go checksum verified',flush=True)
            except Exception as e:log.append({'kind':'go_toolchain','url':url,'status':'UNAVAILABLE','error':type(e).__name__,'http':getattr(e,'code',None)})
        else:log.append({'kind':'go_toolchain','status':'REQUIRED_VERSION_NOT_IN_OFFICIAL_INDEX'})
    for archive,dest,strip in [(ROOT/'downloads/casdoor.zip',ROOT/'baseline',True),(ROOT/'downloads/go1.26.10.windows-amd64.zip',ROOT/'toolchain',False)]:
        if not archive.exists():continue
        if dest.exists():continue
        try:
            with zipfile.ZipFile(archive) as z:
                for member in z.infolist():
                    if member.is_dir():continue
                    rel=Path(*Path(member.filename).parts[1:]) if strip else Path(member.filename)
                    target=(dest/rel).resolve()
                    if not target.is_relative_to(dest.resolve()):raise RuntimeError('unsafe archive path')
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with z.open(member) as a,target.open('xb') as b:shutil.copyfileobj(a,b)
            print('extracted',dest.name,flush=True)
        except Exception as e:log.append({'archive':str(archive),'status':'EXTRACTION_ERROR','error':type(e).__name__})
    (ROOT/'BOOTSTRAP.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),'events':log},indent=2),encoding='utf-8')
    print(json.dumps(log,indent=2),flush=True)
if __name__=='__main__':main()
