"""Administrative deployment/evidence calls only. Active entry uses frozen windows_entry.py."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import subprocess

E=Path(__file__).resolve().parent
P=E.parent
PREFIX=[r'C:\Windows\System32\wsl.exe','--distribution','Ubuntu-24.04','--user','root','--exec']
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def call(argv,purpose,kind):
    plan=load(E/'ADMIN_COMMAND_PLAN.json') if (E/'ADMIN_COMMAND_PLAN.json').exists() else {'schema':'D08-admin-plan/1','commands':[]}
    i=len(plan['commands'])+1;exact=PREFIX+argv
    row={'order':i,'argv':exact,'purpose':purpose,'classification':kind,'start_utc':datetime.now(timezone.utc).isoformat(),'retry':False}
    plan['commands'].append(row.copy());dump(E/'ADMIN_COMMAND_PLAN.json',plan)
    base=E/'commands'/f'{i:02}'
    with Path(str(base)+'.stdout.raw').open('xb') as out,Path(str(base)+'.stderr.raw').open('xb') as err:
        p=subprocess.Popen(exact,stdin=subprocess.DEVNULL,stdout=out,stderr=err);row['wsl_client_pid']=p.pid;row['exit_code']=p.wait()
    row['end_utc']=datetime.now(timezone.utc).isoformat()
    for name in ['stdout','stderr']:
        q=Path(str(base)+'.'+name+'.raw');raw=q.read_bytes();row[name]=raw.decode('utf-8',errors='replace')
        row[name+'_sha256']=hashlib.sha256(raw).hexdigest();row[name+'_file']=q.relative_to(P).as_posix()
    dump(str(base)+'.result.json',row)
    print(json.dumps({'order':i,'exit_code':row['exit_code'],'purpose':purpose,'stdout':row['stdout']},ensure_ascii=False),flush=True)
    return row
