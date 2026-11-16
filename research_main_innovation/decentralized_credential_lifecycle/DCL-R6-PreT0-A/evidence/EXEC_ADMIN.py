"""Administrative deploy/export calls. Actual run uses the frozen Windows entry."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import subprocess
import time

E=Path(__file__).resolve().parent
PREFIX=[r'C:\Windows\System32\wsl.exe','--distribution','Ubuntu-24.04','--user','root','--exec']
def load(p):return json.loads(Path(p).read_bytes())
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def call(argv,purpose,kind):
    path=E/'ADMIN_COMMAND_PLAN.json';plan=load(path) if path.exists() else {'commands':[]}
    i=len(plan['commands'])+1;exact=PREFIX+argv;tick=time.perf_counter()
    row={'order':i,'argv':exact,'purpose':purpose,'classification':kind,'start_utc':datetime.now(timezone.utc).isoformat(),'retry':False}
    plan['commands'].append(dict(row));dump(path,plan);base=E/'commands'/('%02d'%i)
    with Path(str(base)+'.stdout.raw').open('xb') as out,Path(str(base)+'.stderr.raw').open('xb') as err:
        p=subprocess.Popen(exact,stdin=subprocess.DEVNULL,stdout=out,stderr=err);row['wsl_client_pid']=p.pid;row['exit_code']=p.wait()
    row['end_utc']=datetime.now(timezone.utc).isoformat();row['host_elapsed_seconds']=time.perf_counter()-tick
    for name in ['stdout','stderr']:
        q=Path(str(base)+'.'+name+'.raw');raw=q.read_bytes();row[name]=raw.decode('utf-8',errors='replace')
        row[name+'_sha256']=hashlib.sha256(raw).hexdigest();row[name+'_file']=q.relative_to(E.parent).as_posix()
    dump(str(base)+'.result.json',row)
    print(json.dumps({'order':i,'exit_code':row['exit_code'],'purpose':purpose,'host_elapsed_seconds':row['host_elapsed_seconds']},ensure_ascii=False),flush=True)
    return row
