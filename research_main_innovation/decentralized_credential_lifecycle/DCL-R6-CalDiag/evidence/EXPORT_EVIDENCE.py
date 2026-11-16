"""Post-exit read-only export and current process audit; no target import/replay."""
from EXEC_ADMIN import call,dump,load,E
from pathlib import Path
import hashlib
import json
import shutil

active=load(E/'ACTIVE_ENTRY_RETURN.json')
control=Path(load(E/'AUTHORIZATION_RECEIPT_LOCK.json')['control_directory'])
for name in ['WINDOWS_ENTRY_PLAN.json','WINDOWS_ENTRY_EXIT.json','windows_entry.stdout.raw','windows_entry.stderr.raw']:
    assert (control/name).exists();shutil.copyfile(control/name,E/name)
CODE=r'''
from pathlib import Path
import hashlib,json,os,resource,stat,subprocess
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
root=Path('/var/lib/dcl-r6/batch09');src=Path('/var/lib/dcl-r6/cr09')
host=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/batch09');assert not host.exists()
snapshot=host/'native_snapshot';frozen=host/'FROZEN_B09';snapshot.mkdir(parents=True);frozen.mkdir()
state=json.loads((root/'inputs/batch_state.json').read_text());run_boot=state['boot_id']
def meta(p):
 s=p.lstat();return {'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'ctime_ns':s.st_ctime_ns,'ACL':[a for a in os.listxattr(p,follow_symlinks=False) if a.startswith('system.posix_acl_')]}
def export(base,dst):
 files=[];dirs=[];other=[]
 for p in [base,*sorted(base.rglob('*'))]:
  s=p.lstat();rel=p.relative_to(base).as_posix()
  if stat.S_ISDIR(s.st_mode):dirs.append({'relative':rel,**meta(p)});continue
  if not stat.S_ISREG(s.st_mode):other.append({'relative':rel,'type':stat.S_IFMT(s.st_mode),**meta(p)});continue
  raw=p.read_bytes();q=dst/rel;q.parent.mkdir(parents=True,exist_ok=True)
  with q.open('xb') as f:f.write(raw)
  files.append({'relative':rel,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),**meta(p)})
 return files,dirs,other
files,dirs,other=export(root,snapshot);source,source_dirs,source_other=export(src,frozen)
payload=[];roles=[]
for p in Path('/proc').glob('[0-9]*'):
 try:
  s=dict(v.split(':',1) for v in (p/'status').read_text().splitlines() if ':' in v);uids=list(map(int,s['Uid'].split()))
  argv=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  if 999 in uids:payload.append({'pid':int(p.name),'uids':uids,'argv':argv})
  if '--role' in argv and any(a.startswith('/var/lib/dcl-r6/') and a.endswith('/guard.py') for a in argv):roles.append({'pid':int(p.name),'uids':uids,'argv':argv})
  if '--activate' in argv and '/var/lib/dcl-r6/cr09/src/boot_continuity.py' in argv:roles.append({'pid':int(p.name),'uids':uids,'argv':argv})
 except (OSError,ValueError,KeyError):pass
lock=json.loads((src/'inputs/execution_lock.json').read_text());argv=lock['journal_export_command'][:]
argv[argv.index('--boot')]='--boot='+run_boot.replace('-','')
j=subprocess.run(argv,capture_output=True,timeout=30)
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-CalDiag/evidence')
for name,raw in [('stdout',j.stdout),('stderr',j.stderr)]:
 with (e/('RUN_BOOT_JOURNAL.'+name+'.raw')).open('xb') as f:f.write(raw)
queries={
 'POSTRUN_FAILED_UNITS':['/usr/bin/systemctl','list-units','--state=failed','--all','--no-pager','--no-legend'],
 'POSTRUN_BATCH09_UNITS':['/usr/bin/systemctl','show',*[a.split('=',1)[1] for a in lock['journal_export_command'] if a.startswith('--unit=')],
  '--property=Id','--property=LoadState','--property=ActiveState','--property=SubState','--property=MainPID','--property=Result','--property=ExecMainStatus','--property=ControlGroup','--property=TasksMax','--property=MemoryMax']}
query_results=[]
for name,command in queries.items():
 r=subprocess.run(command,capture_output=True,timeout=20)
 for stream,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
  with (e/(name+'.'+stream+'.raw')).open('xb') as f:f.write(raw)
 query_results.append({'name':name,'argv':command,'exit_code':r.returncode,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr).hexdigest()})
print(json.dumps({'status':'POST_EXIT_READ_ONLY_EXPORT','observation_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'run_boot_id':run_boot,'native_files':files,'native_directories':dirs,'native_nonregular':other,'frozen_files':source,'frozen_directories':source_dirs,'frozen_nonregular':source_other,'payload_processes':payload,'root_role_processes':roles,'parent_cgroup_exists':Path('/sys/fs/cgroup/dclr6batch09.slice').exists(),'closed_file_exists':(root/'inputs/CLOSED.json').exists(),'native_auto_seal':(root/'out/EVIDENCE.zip').exists(),'journal_argv':argv,'journal_exit':j.returncode,'journal_stdout_sha256':hashlib.sha256(j.stdout).hexdigest(),'journal_stderr_sha256':hashlib.sha256(j.stderr).hexdigest(),'queries':query_results,'private_originals':'Preserved only in native_snapshot and sealed archive; no capability nonce printed'},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Post-exit batch09 source/runtime byte export, scoped run-boot journal, current controlled-process and failed-unit read-only audit','POST_EXIT_READ_ONLY_EXPORT')
assert r['exit_code']==0,r['stderr']
x=json.loads(r['stdout']);dump(E/'POSTRUN_AUDIT.json',x)
base=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch09');target=base/'FROZEN_B09';(target/'host').mkdir()
entry=Path(r'D:\毕业设计\DCL-R6-isolated-verification\cr09\host\windows_entry.py');shutil.copyfile(entry,target/'host/windows_entry.py')
x['frozen_files'].append({'relative':'host/windows_entry.py','bytes':entry.stat().st_size,'sha256':hashlib.sha256(entry.read_bytes()).hexdigest(),'origin':'host frozen Windows entry'})
for name,rows,folder,other in [('NATIVE_EXPORT_LOCK.json',x['native_files'],'native_snapshot',x['native_nonregular']),('FROZEN_SOURCE_EXPORT_LOCK.json',x['frozen_files'],'FROZEN_B09',x['frozen_nonregular'])]:
    for row in rows:row['host']=str(base/folder/row['relative'])
    dump(E/name,{'schema':'CalDiag-export/1','files':rows,'nonregular':other,'run_boot_id':x['run_boot_id']})
dump(E/'EXPORT_COMPLETION.json',{'native_files':len(x['native_files']),'frozen_files':len(x['frozen_files']),'closed':x['closed_file_exists'],'native_auto_seal':x['native_auto_seal'],'controlled_processes_empty':not x['payload_processes'] and not x['root_role_processes'],'parent_cgroup_exists':x['parent_cgroup_exists']})
print(json.dumps({'native_files':len(x['native_files']),'frozen_files':len(x['frozen_files']),'closed':x['closed_file_exists'],'native_auto_seal':x['native_auto_seal'],'controlled_processes_empty':not x['payload_processes'] and not x['root_role_processes'],'parent_cgroup_exists':x['parent_cgroup_exists'],'journal_exit':x['journal_exit']},ensure_ascii=False))
