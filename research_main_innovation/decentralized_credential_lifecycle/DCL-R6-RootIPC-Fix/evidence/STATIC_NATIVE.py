"""Recorded static-only WSL commands: environment reads, compilation and static source copy."""
from pathlib import Path
import hashlib
import json
import subprocess
from datetime import datetime,timezone

E=Path(__file__).resolve().parent
W='/mnt/d/毕业设计/DCL-R6-isolated-verification/ri01'
READ=r'''
import hashlib,json,os,platform,pwd,sys
from pathlib import Path
print(json.dumps({'python':sys.version,'python_path':sys.executable,
 'python_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
 'kernel':platform.release(),'machine':platform.machine(),
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'uid999':list(pwd.getpwuid(999))[:4], 'uid65534':list(pwd.getpwuid(65534))[:4],
 'root_euid':os.geteuid(),'batch06_exists':Path('/var/lib/dcl-r6/batch06').exists(),
 'ri01_exists':Path('/var/lib/dcl-r6/ri01').exists(),
 'api_dir_fd':{f.__name__: f in os.supports_dir_fd for f in [os.open,os.stat,os.rename]},
 'replace_signature':__import__('inspect').signature(os.replace).__str__()},ensure_ascii=False))
base=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/ri01/inputs')
m=json.loads((base/'static_manifest.json').read_text());tree=json.loads((base/'runtime_tree_lock.json').read_text())
errors=[]
for name,digest in m['runtime_files'].items():
 if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:errors.append(name)
for name,row in tree['files'].items():
 if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=row['sha256']:errors.append(name)
dev=os.stat('/var/lib/dcl-r6').st_dev;device=str(os.major(dev))+':'+str(os.minor(dev))
mounts=[s for s in Path('/proc/self/mountinfo').read_text().splitlines() if s.split()[2]==device]
print(json.dumps({'runtime_critical_checked':len(m['runtime_files']),'runtime_tree_checked':len(tree['files']),
 'hash_errors':errors,'filesystem_device':device,'matching_mountinfo':mounts},ensure_ascii=False))
assert not errors
'''
COMPILE=r'''
import json,py_compile,sys
from pathlib import Path
base=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/ri01/src');rows=[]
assert sys.version_info[:3]==(3,12,3)
for p in sorted(base.glob('*.py')):
 out=base/'__pycache__'/(p.stem+'.cpython-312.pyc')
 py_compile.compile(str(p),cfile=str(out),dfile='/var/lib/dcl-r6/ri01/src/'+p.name,
                    doraise=True,invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH)
 rows.append({'file':p.name,'cache':out.name,'status':'SYNTAX_OK'})
print(json.dumps({'schema':'RI-syntax/1','modules':rows,'target_body_executed':0}))
'''
COPY=r'''
import hashlib,json,os,shutil
from pathlib import Path
src=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/ri01');dst=Path('/var/lib/dcl-r6/ri01')
assert not Path('/var/lib/dcl-r6/batch06').exists()
if not dst.exists():dst.mkdir(mode=0o755)
assert dst.resolve()==dst and dst.stat().st_uid==0
rows=[]
for p in sorted(src.rglob('*')):
 if p.is_file():
  q=dst/p.relative_to(src);q.parent.mkdir(parents=True,exist_ok=True)
  assert q.resolve().is_relative_to(dst) and not q.is_symlink()
  shutil.copyfile(p,q);os.chown(q,0,0);os.chmod(q,0o644)
  rows.append({'relative':p.relative_to(src).as_posix(),'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),
               'uid':q.stat().st_uid,'gid':q.stat().st_gid,'mode':oct(q.stat().st_mode&0o777)})
for q in [dst,*[x for x in dst.rglob('*') if x.is_dir()]]:os.chown(q,0,0);os.chmod(q,0o755)
print(json.dumps({'schema':'RI-static-deployment/1','files':rows,'batch06_created':False}))
'''
VERIFY=r'''
import hashlib,json,os
from pathlib import Path
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-RootIPC-Fix/evidence')
lock=json.loads((e/'STATIC_WORKSPACE_LOCK.json').read_text());errors=[]
for row in lock['files']:
 p=Path(row['linux'])
 if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append(row['linux'])
meta=[]
for name in ['/var','/var/lib','/var/lib/dcl-r6','/var/lib/dcl-r6/ri01','/var/lib/dcl-r6/ri01/src','/var/lib/dcl-r6/ri01/inputs']:
 p=Path(name);s=p.stat();meta.append({'path':name,'uid':s.st_uid,'gid':s.st_gid,'mode':oct(s.st_mode&0o777),
                                  'posix_acl':[a for a in os.listxattr(p) if a.startswith('system.posix_acl_')]})
print(json.dumps({'schema':'RI-final-native-static-check/1','revision':lock['freeze_revision'],
 'files_checked':len(lock['files']),'hash_errors':errors,'directory_metadata':meta,
 'batch06_exists':Path('/var/lib/dcl-r6/batch06').exists(),'runtime_T0_created':False,
 'target_body_executed':0},ensure_ascii=False))
assert not errors and not Path('/var/lib/dcl-r6/batch06').exists()
assert all(not x['posix_acl'] for x in meta)
'''


def call(purpose,code):
    out=E/'commands';out.mkdir(exist_ok=True)
    i=len(list(out.glob('*.result.json')))+1
    argv=['C:\\Windows\\System32\\wsl.exe','--distribution','Ubuntu-24.04','--exec',
          '/usr/bin/python3.12','-I','-S','-B','-c',code]
    start=datetime.now(timezone.utc).isoformat()
    (out/f'{i:02}.plan.json').write_text(json.dumps({'argv':argv,'purpose':purpose,'start_utc':start},ensure_ascii=False,indent=2),encoding='utf-8')
    r=subprocess.run(argv,capture_output=True,timeout=60)
    for name,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
        (out/f'{i:02}.{name}.raw').write_bytes(raw)
    row={'argv':argv,'purpose':purpose,'start_utc':start,'end_utc':datetime.now(timezone.utc).isoformat(),
         'exit_code':r.returncode,'stdout':r.stdout.decode('utf-8',errors='replace'),
         'stderr':r.stderr.decode('utf-8',errors='replace'),
         'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest(),
         'target_module_body_executed':0,'dynamic_tests':0,'systemd_mutations':0}
    (out/f'{i:02}.result.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'order':i,'purpose':purpose,'exit':r.returncode,'stdout':row['stdout']},ensure_ascii=False))
    if r.returncode:raise SystemExit(r.returncode)


if __name__=='__main__':
    import sys
    option=sys.argv[1]
    if option=='read':call('Readonly current interpreter/API/environment identities; no target code',READ)
    elif option=='compile':call('CPython3.12 py_compile17; no target import or role body',COMPILE)
    elif option=='copy':call('Deploy ri01 static files only; batch06 absent; no services or runtime',COPY)
    elif option=='verify':call('Readonly final44 Linux hashes, source directory ACL/metadata, batch06 absence',VERIFY)
    else:raise SystemExit('unknown static operation')
