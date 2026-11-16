"""Read-only Linux audit and host evidence export after the preflight stop."""
from EXEC_NATIVE import call,dump,load,E
import json

assert load(E/'PREFLIGHT_FINAL.json')['status']=='PREFLIGHT_FAILED'
assert not any(r['classification']=='B06_FROZEN_LAUNCHER' for r in load(E/'COMMAND_PLAN.json')['commands'])
code=r'''
from pathlib import Path
import hashlib,json,os,stat
root=Path('/var/lib/dcl-r6/batch06');dest=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/batch06')
assert not dest.exists()
snapshot=dest/'native_snapshot';frozen=dest/'FROZEN_ROOTIPC'
snapshot.mkdir(parents=True);frozen.mkdir()
files=[];directories=[];nonregular=[]
def meta(p):
 s=p.lstat()
 return {'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,
         'inode':s.st_ino,'nlink':s.st_nlink,'ctime_ns':s.st_ctime_ns,
         'ACL':[a for a in os.listxattr(p,follow_symlinks=False) if a.startswith('system.posix_acl_')]}
for p in [root,*sorted(root.rglob('*'))]:
 rel=p.relative_to(root).as_posix();s=p.lstat()
 if stat.S_ISDIR(s.st_mode):directories.append({'relative':rel,**meta(p)});continue
 if not stat.S_ISREG(s.st_mode):nonregular.append({'relative':rel,'type':stat.S_IFMT(s.st_mode),**meta(p)});continue
 data=p.read_bytes();q=snapshot/rel;q.parent.mkdir(parents=True,exist_ok=True)
 with q.open('xb') as f:f.write(data)
 files.append({'relative':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),**meta(p)})
source=[];src=Path('/var/lib/dcl-r6/ri01')
for p in sorted(src.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(src).as_posix();data=p.read_bytes();q=frozen/rel;q.parent.mkdir(parents=True,exist_ok=True)
 with q.open('xb') as f:f.write(data)
 source.append({'relative':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),**meta(p)})
payload=[];roles=[]
for p in Path('/proc').glob('[0-9]*'):
 try:
  fields=dict(s.split(':',1) for s in (p/'status').read_text().splitlines() if ':' in s)
  ids=list(map(int,fields['Uid'].split()));args=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  if 999 in ids:payload.append({'pid':int(p.name),'uids':ids,'argv':args})
  if '--role' in args and any(s.startswith('/var/lib/dcl-r6/') and s.endswith('/guard.py') for s in args):roles.append({'pid':int(p.name),'uids':ids,'argv':args})
 except (OSError,ValueError,KeyError):pass
print(json.dumps({'schema':'B06-postfailure-export/1','boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'native_files':files,'native_directories':directories,'native_nonregular':nonregular,'source_files':source,
 'payload_processes':payload,'root_role_processes':roles,
 'parent_cgroup_exists':Path('/sys/fs/cgroup/dclr6batch06.slice').exists(),
 'state_exists':(root/'inputs/batch_state.json').exists(),'counter_exists':(root/'out/visits.bin').exists(),
 'CLOSED_exists':(root/'inputs/CLOSED.json').exists(),'STOP_REQUEST_exists':(root/'out/STOP_REQUEST.json').exists(),
 'native_auto_seal_exists':(root/'out/EVIDENCE.zip').exists(),
 'out_entries':[p.name for p in (root/'out').iterdir()],'private_entries':[p.name for p in (root/'inputs/root_private').iterdir()]},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',code],
       'After preflight failure: read-only Linux metadata/process audit and byte export to approved host workspace','POSTFAIL_READ_EXPORT_ONLY')
assert r['exit_code']==0
actual=json.loads(r['stdout']);dump(E/'POSTFAIL_AUDIT.json',actual)
for key in ['state_exists','counter_exists','CLOSED_exists','STOP_REQUEST_exists','native_auto_seal_exists','parent_cgroup_exists']:assert not actual[key],key
assert not actual['payload_processes'] and not actual['root_role_processes']
host='D:\\毕业设计\\DCL-R6-isolated-verification\\batch06\\'
for name,rows,folder in [('NATIVE_EXPORT_LOCK.json',actual['native_files'],'native_snapshot'),('FROZEN_SOURCE_EXPORT_LOCK.json',actual['source_files'],'FROZEN_ROOTIPC')]:
    for row in rows:row['host']=host+folder+'\\'+row['relative'].replace('/','\\')
    dump(E/name,{'schema':'B06-byte-export/1','files':rows,'phase':'PREFLIGHT_FAILED; target execution0','nonregular':actual['native_nonregular'] if folder=='native_snapshot' else []})
for argv,purpose in [
 (['/usr/bin/systemctl','show','dclr6batch06.slice','--property=ActiveState','--property=SubState','--property=ControlGroup','--property=TasksCurrent','--property=TasksMax','--property=MemoryCurrent','--property=MemoryMax'], 'Postfailure parent unit state; no stop/start action'),
 (['/usr/bin/systemctl','list-units','dclr6batch06*','--all','--no-pager','--no-legend'],'Postfailure exact batch06 unit listing'),
 (load(E/'execution_lock.json')['journal_export_command'],'Frozen exact17-unit current-boot journal after preflight stop; no runtime case started')]:
    row=call(argv,purpose,'POSTFAIL_READ_ONLY')
    assert row['exit_code']==0
