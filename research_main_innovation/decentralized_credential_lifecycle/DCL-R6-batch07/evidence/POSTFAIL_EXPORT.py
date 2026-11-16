"""After the single failed activation, only audit/byte export and scoped journal reads."""
from EXEC_ADMIN import call,dump,load,E
import json
from pathlib import Path
import shutil
assert load(E/'WINDOWS_ENTRY_EXIT.json')['exit_code']!=0
code=r'''
from pathlib import Path
import hashlib,json,os,stat,subprocess
root=Path('/var/lib/dcl-r6/batch07');src=Path('/var/lib/dcl-r6/bc01')
host=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/batch07');assert not host.exists()
snapshot=host/'native_snapshot';frozen=host/'FROZEN_BOOTCONTINUITY'
snapshot.mkdir(parents=True);frozen.mkdir()
def metadata(p):
 s=p.lstat()
 return {'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino,
         'nlink':s.st_nlink,'ctime_ns':s.st_ctime_ns,'ACL':[a for a in os.listxattr(p,follow_symlinks=False) if a.startswith('system.posix_acl_')]}
def copytree(base,dest):
 files=[];dirs=[];other=[]
 for p in [base,*sorted(base.rglob('*'))]:
  s=p.lstat();rel=p.relative_to(base).as_posix()
  if stat.S_ISDIR(s.st_mode):dirs.append({'relative':rel,**metadata(p)});continue
  if not stat.S_ISREG(s.st_mode):other.append({'relative':rel,'type':stat.S_IFMT(s.st_mode),**metadata(p)});continue
  raw=p.read_bytes();q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True)
  with q.open('xb') as f:f.write(raw)
  files.append({'relative':rel,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),**metadata(p)})
 return files,dirs,other
files,dirs,other=copytree(root,snapshot);source,source_dirs,source_other=copytree(src,frozen)
payload=[];roles=[]
for p in Path('/proc').glob('[0-9]*'):
 try:
  fields=dict(s.split(':',1) for s in (p/'status').read_text().splitlines() if ':'in s)
  ids=list(map(int,fields['Uid'].split()));argv=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  if 999 in ids:payload.append({'pid':int(p.name),'uids':ids,'argv':argv})
  if '--role' in argv and any(a.startswith('/var/lib/dcl-r6/') and a.endswith('/guard.py') for a in argv):roles.append({'pid':int(p.name),'uids':ids,'argv':argv})
  if '--activate' in argv and '/var/lib/dcl-r6/bc01/src/boot_continuity.py' in argv:roles.append({'pid':int(p.name),'uids':ids,'argv':argv})
 except (OSError,ValueError,KeyError):pass
lock=json.loads((src/'inputs/execution_lock.json').read_text());argv=lock['journal_export_command'][:]
argv[argv.index('--boot')]='--boot=060a08fc-fceb-48ff-a264-50c34312f97a'
r=subprocess.run(argv,capture_output=True,timeout=30)
journal_dir=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-batch07/evidence')
for name,data in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (journal_dir/('RUN_BOOT_JOURNAL.'+name+'.raw')).open('xb') as f:f.write(data)
print(json.dumps({'schema':'B07-postfailure/1','observation_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'native_files':files,'native_directories':dirs,'native_nonregular':other,'frozen_files':source,'frozen_nonregular':source_other,
 'payload_processes':payload,'root_role_processes':roles,'parent_cgroup_exists':Path('/sys/fs/cgroup/dclr6batch07.slice').exists(),
 'native_auto_seal_exists':(root/'out/EVIDENCE.zip').exists(),
 'journal_argv':argv,'journal_exit':r.returncode,'journal_stdout_bytes':len(r.stdout),'journal_stderr_bytes':len(r.stderr),
 'journal_stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'journal_stderr_sha256':hashlib.sha256(r.stderr).hexdigest(),
 'secret_scope':'Raw private records copied only to native_snapshot/inputs/root_private; ordinary output contains hashes/metadata only'},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',code],
       'First failure: audit controlled processes, preserve native/private bytes and31 source files, export exact17-unit RUN-BOOT journal','POSTFAIL_READ_EXPORT_ONLY')
assert r['exit_code']==0
actual=json.loads(r['stdout']);dump(E/'POSTFAIL_AUDIT.json',actual)
prefix=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch07')
frozen=prefix/'FROZEN_BOOTCONTINUITY'
entry=Path(r'D:\毕业设计\DCL-R6-isolated-verification\bc01\host\windows_entry.py')
(frozen/'host').mkdir();shutil.copyfile(entry,frozen/'host/windows_entry.py')
import hashlib
actual['frozen_files'].append({'relative':'host/windows_entry.py','bytes':entry.stat().st_size,
 'sha256':hashlib.sha256(entry.read_bytes()).hexdigest(),'origin':'host frozen Windows entry','uid':None,'gid':None,'mode':None})
for name,rows,folder in [('NATIVE_EXPORT_LOCK.json',actual['native_files'],'native_snapshot'),('FROZEN_SOURCE_EXPORT_LOCK.json',actual['frozen_files'],'FROZEN_BOOTCONTINUITY')]:
 for row in rows:row['host']=str(prefix/folder/row['relative'])
 dump(E/name,{'schema':'B07-export/1','files':rows,'nonregular':actual['native_nonregular'] if folder=='native_snapshot' else actual['frozen_nonregular'],
   'native_auto_seal':actual['native_auto_seal_exists'] if folder=='native_snapshot' else None,'run_boot_id':'060a08fc-fceb-48ff-a264-50c34312f97a'})
assert not actual['payload_processes'] and not actual['root_role_processes'] and not actual['parent_cgroup_exists']
for argv,purpose in [
 (['/usr/bin/systemctl','show','dclr6batch07.slice','dclr6batch07-c00.service','dclr6batch07-stop.service',
   '--property=Id','--property=LoadState','--property=ActiveState','--property=SubState','--property=MainPID','--property=Result',
   '--property=ExecMainStatus','--property=User','--property=Group','--property=LimitAS','--property=LimitASSoft',
   '--property=ControlGroup','--property=NoNewPrivileges','--property=TasksMax','--property=MemoryMax'],
  'Postfailure manager properties for exact current batch parent/C00/stop; temporal scope after failure'),
 (['/usr/bin/systemctl','list-units','dclr6batch07*','--all','--no-pager','--no-legend'],'Postfailure exact batch07 unit list')]:
 result=call(argv,purpose,'POSTFAIL_READ_ONLY');assert result['exit_code']==0
