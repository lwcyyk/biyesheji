"""Deploy57 exact locked Linux files. No runtime root, unit, or budget creation."""
from EXEC_ADMIN import call,dump,E
import json

CODE=r'''
from pathlib import Path
import hashlib,json,os,resource,stat,sys
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-TR-A/evidence')
admission=json.loads((e/'SOURCE_AND_SCOPE_ADMISSION.json').read_text());rows=[r for r in admission['files'] if not r['relative'].startswith('host/')]
m=json.loads((e/'FROZEN_SOURCE_REFERENCE/inputs/static_manifest.json').read_text())
assert len(rows)==57
assert sys.version_info[:3]==(3,12,3) and str(Path(sys.executable).resolve())=='/usr/bin/python3.12'
assert hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()==m['runtime_files']['/usr/bin/python3.12']
assert not Path('/var/lib/dcl-r6/batch13').exists()
assert not Path('/etc/systemd/system/dclr6batch13.slice').exists()
assert not Path('/sys/fs/cgroup/dclr6batch13.slice').exists()
for name in ['/var','/var/lib','/var/lib/dcl-r6']:
 p=Path(name);s=p.lstat()
 assert stat.S_ISDIR(s.st_mode) and s.st_uid==0 and not s.st_mode&0o022
 assert not [n for n in os.listxattr(p,follow_symlinks=False) if n.startswith('system.posix_acl_')]
src=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/tr01');dst=Path('/var/lib/dcl-r6/tr01');existed=dst.exists()
if existed:
 assert {p.relative_to(dst).as_posix() for p in dst.rglob('*') if p.is_file()}=={r['relative'] for r in rows}
 for r in rows:
  p=dst/r['relative'];s=p.lstat()
  assert stat.S_ISREG(s.st_mode) and (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o644)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
else:
 dst.mkdir(mode=0o755);os.chown(dst,0,0);os.chmod(dst,0o755)
 for r in rows:
  raw=(src/r['relative']).read_bytes();assert hashlib.sha256(raw).hexdigest()==r['sha256']
  p=dst/r['relative'];p.parent.mkdir(parents=True,exist_ok=True)
  fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644)
  try:
   os.fchown(fd,0,0);os.fchmod(fd,0o644)
   assert os.write(fd,raw)==len(raw);os.fsync(fd)
  finally:os.close(fd)
 for p in [dst,*[p for p in dst.rglob('*') if p.is_dir()]]:os.chown(p,0,0);os.chmod(p,0o755)
results=[]
for r in rows:
 p=dst/r['relative'];s=p.lstat();actual=hashlib.sha256(p.read_bytes()).hexdigest()
 assert actual==r['sha256'] and stat.S_ISREG(s.st_mode) and (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o644)
 assert not [n for n in os.listxattr(p,follow_symlinks=False) if n.startswith('system.posix_acl_')]
 results.append({'relative':r['relative'],'bytes':s.st_size,'sha256':actual,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode)})
for p in [dst,*[p for p in dst.rglob('*') if p.is_dir()]]:
 s=p.lstat();assert stat.S_ISDIR(s.st_mode) and (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o755)
 assert not [n for n in os.listxattr(p,follow_symlinks=False) if n.startswith('system.posix_acl_')]
assert not list(dst.rglob('*.pyc'))
for p in (dst/'src').glob('*.py'):compile(p.read_bytes(),str(p),'exec')
print(json.dumps({'status':'PASS_STATIC_DEPLOYMENT_ONLY','files':results,'existed':existed,'python':list(sys.version_info[:3]),'python_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),'observation_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'boot_scope':'Deployment observation only; activation must bind its own current boot','target_module_imports':0,'runtime_root_created':False,'units_created':0},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Deploy and hash57 exact TerminalRead-r1 Linux source/input files; native syntax only','STATIC_DEPLOYMENT_ONLY')
if r['exit_code']==0:
    parsed=json.loads(r['stdout']);dump(E/'DEPLOYMENT_RESULT.json',parsed)
    print(json.dumps({'deployment_status':parsed['status'],'files':len(parsed['files']),'python':parsed['python'],'observation_boot_id':parsed['observation_boot_id'],'target_imports':0},ensure_ascii=False))
else:
    dump(E/'DEPLOYMENT_RESULT.json',{'status':'PREFLIGHT_FAILED','phase':'STATIC_DEPLOYMENT','command_order':r['order'],'T0':None,'R':None})
    print(r['stderr'][-3000:])
    raise SystemExit(r['exit_code'])
