"""Closed minimal batch audit/export only. Never launches or replays a target case."""
from EXEC_ADMIN import call,dump,load,E
from pathlib import Path
import json
import shutil
import hashlib

assert (E/'WINDOWS_ENTRY_EXIT.json').exists()
code=r'''
from pathlib import Path
import hashlib,json,os,stat,subprocess
root=Path('/var/lib/dcl-r6/batch08');src=Path('/var/lib/dcl-r6/cr01')
host=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/batch08');assert not host.exists()
snapshot=host/'native_snapshot';frozen=host/'FROZEN_C00READY'
snapshot.mkdir(parents=True);frozen.mkdir()
state=json.loads((root/'inputs/batch_state.json').read_text());run_boot=state['boot_id']
def meta(p):
 s=p.lstat();return {'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino,
  'nlink':s.st_nlink,'ctime_ns':s.st_ctime_ns,'ACL':[a for a in os.listxattr(p,follow_symlinks=False) if a.startswith('system.posix_acl_')]}
def export(base,dest):
 files=[];dirs=[];other=[]
 for p in [base,*sorted(base.rglob('*'))]:
  s=p.lstat();rel=p.relative_to(base).as_posix()
  if stat.S_ISDIR(s.st_mode):dirs.append({'relative':rel,**meta(p)});continue
  if not stat.S_ISREG(s.st_mode):other.append({'relative':rel,'type':stat.S_IFMT(s.st_mode),**meta(p)});continue
  data=p.read_bytes();q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True)
  with q.open('xb') as f:f.write(data)
  files.append({'relative':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),**meta(p)})
 return files,dirs,other
files,dirs,other=export(root,snapshot);source,_,source_other=export(src,frozen)
payload=[];roles=[]
for p in Path('/proc').glob('[0-9]*'):
 try:
  s=dict(x.split(':',1) for x in (p/'status').read_text().splitlines() if ':'in x);uids=list(map(int,s['Uid'].split()))
  args=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  if 999 in uids:payload.append({'pid':int(p.name),'uids':uids,'argv':args})
  if '--role' in args and any(a.startswith('/var/lib/dcl-r6/') and a.endswith('/guard.py') for a in args):roles.append({'pid':int(p.name),'uids':uids,'argv':args})
  if '--activate' in args and '/var/lib/dcl-r6/cr01/src/boot_continuity.py' in args:roles.append({'pid':int(p.name),'uids':uids,'argv':args})
 except (OSError,KeyError,ValueError):pass
lock=json.loads((src/'inputs/execution_lock.json').read_text());argv=lock['journal_export_command'][:]
argv[argv.index('--boot')]='--boot='+run_boot.replace('-','')
j=subprocess.run(argv,capture_output=True,timeout=30)
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-batch08-Diag/evidence')
for name,data in [('stdout',j.stdout),('stderr',j.stderr)]:
 with (e/('RUN_BOOT_JOURNAL.'+name+'.raw')).open('xb') as f:f.write(data)
print(json.dumps({'schema':'D08-closed-export/1','observation_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'run_boot_id':run_boot,'native_files':files,'native_directories':dirs,'native_nonregular':other,'frozen_files':source,'frozen_nonregular':source_other,
 'payload_processes':payload,'root_role_processes':roles,'parent_cgroup_exists':Path('/sys/fs/cgroup/dclr6batch08.slice').exists(),
 'native_auto_seal':(root/'out/EVIDENCE.zip').exists(),'journal_argv':argv,'journal_exit':j.returncode,
 'journal_stdout_bytes':len(j.stdout),'journal_stderr_bytes':len(j.stderr),
 'journal_stdout_sha256':hashlib.sha256(j.stdout).hexdigest(),'journal_stderr_sha256':hashlib.sha256(j.stderr).hexdigest(),
 'ordinary_output':'Only file hashes/metadata; Root-private capability originals remain in private snapshot paths'},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',code],
 'Closed minimal batch: export native/diagnostic bytes and frozen sources, scoped run-boot journal, controlled-process audit','CLOSED_AUDIT_EXPORT_ONLY')
assert r['exit_code']==0
x=json.loads(r['stdout']);dump(E/'POSTRUN_AUDIT.json',x)
base=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch08');target=base/'FROZEN_C00READY'
entry=Path(r'D:\毕业设计\DCL-R6-isolated-verification\cr01/host/windows_entry.py');(target/'host').mkdir();shutil.copyfile(entry,target/'host/windows_entry.py')
x['frozen_files'].append({'relative':'host/windows_entry.py','bytes':entry.stat().st_size,'sha256':hashlib.sha256(entry.read_bytes()).hexdigest(),'origin':'host frozen entry','uid':None,'gid':None,'mode':None})
for name,rows,folder,other in [('NATIVE_EXPORT_LOCK.json',x['native_files'],'native_snapshot',x['native_nonregular']),('FROZEN_SOURCE_EXPORT_LOCK.json',x['frozen_files'],'FROZEN_C00READY',x['frozen_nonregular'])]:
 for row in rows:row['host']=str(base/folder/row['relative'])
 dump(E/name,{'schema':'D08-export-lock/1','files':rows,'nonregular':other,'run_boot':x['run_boot_id'],'native_auto_seal':x['native_auto_seal']})
assert not x['payload_processes'] and not x['root_role_processes'] and not x['parent_cgroup_exists']
call(['/usr/bin/systemctl','show','dclr6batch08.slice','dclr6batch08-c00.service','dclr6batch08-stop.service',
      '--property=Id','--property=LoadState','--property=ActiveState','--property=SubState','--property=MainPID','--property=Result','--property=ExecMainStatus',
      '--property=ControlGroup','--property=TasksMax','--property=MemoryMax'],
     'Postrun exact minimal parent/C00/stop manager state, not used as past runtime measurements','CLOSED_READ_ONLY')
print(json.dumps({'native_files':len(x['native_files']),'frozen_files':len(x['frozen_files']),'journal_exit':x['journal_exit'],'controlled_processes_empty':True},ensure_ascii=False))
