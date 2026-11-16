"""One post-exit read-only export, including a pre-T0 failure; no target import."""
from EXEC_ADMIN import call,dump,load,E
from pathlib import Path
import json
import hashlib
import shutil

assert load(E/'ACTIVE_ENTRY_RETURN.json')['exit_code']==0
control=Path(load(E/'AUTHORIZATION_RECEIPT_LOCK.json')['control_directory'])
for name in [p.name for p in control.iterdir() if p.is_file()]:
    shutil.copyfile(control/name,E/name)
CODE=r'''
from pathlib import Path
import hashlib,json,os,resource,stat,subprocess
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
root=Path('/var/lib/dcl-r6/batch12');src=Path('/var/lib/dcl-r6/pf01');host=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/batch12')
assert root.exists() and not host.exists()
snapshot=host/'native_snapshot';frozen=host/'FROZEN_PF';snapshot.mkdir(parents=True);frozen.mkdir()
def meta(p):
 s=p.lstat();return {'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'ACL':[x for x in os.listxattr(p,follow_symlinks=False) if x.startswith('system.posix_acl_')]}
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
entry=json.loads((root/'inputs/root_private/boot/entry_initial.json').read_text());run_boot=entry['owner']['boot_id']
payload=[];roles=[]
for p in Path('/proc').glob('[0-9]*'):
 try:
  status=dict(v.split(':',1) for v in (p/'status').read_text().splitlines() if ':' in v);uids=list(map(int,status['Uid'].split()));argv=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  if 999 in uids:payload.append({'pid':int(p.name),'argv':argv})
  if '--role' in argv and any(a.startswith('/var/lib/dcl-r6/') and a.endswith('/guard.py') for a in argv):roles.append({'pid':int(p.name),'argv':argv})
  if '--activate' in argv and str(src/'src/boot_continuity.py') in argv:roles.append({'pid':int(p.name),'argv':argv})
 except (OSError,ValueError,KeyError):pass
lock=json.loads((src/'inputs/execution_lock.json').read_text());argv=lock['journal_export_command'][:];argv[argv.index('--boot')]='--boot='+run_boot.replace('-','')
j=subprocess.run(argv,capture_output=True,timeout=30);e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-PTA-PF-A/evidence')
for stream,raw in [('stdout',j.stdout),('stderr',j.stderr)]:
 with(e/('RUN_BOOT_JOURNAL.'+stream+'.raw')).open('xb') as f:f.write(raw)
queries={
 'FAILED_UNITS':['/usr/bin/systemctl','list-units','--state=failed','--all','--no-pager','--no-legend'],
 'BATCH12_UNITS':['/usr/bin/systemctl','show',*[a.split('=',1)[1] for a in lock['journal_export_command'] if a.startswith('--unit=')],
  '--property=Id','--property=LoadState','--property=ActiveState','--property=SubState','--property=MainPID','--property=Result','--property=ExecMainStatus','--property=ControlGroup','--property=TasksMax','--property=MemoryMax']}
query_results=[]
for name,cmd in queries.items():
 q=subprocess.run(cmd,capture_output=True,timeout=20)
 for stream,raw in [('stdout',q.stdout),('stderr',q.stderr)]:
  with(e/(name+'.'+stream+'.raw')).open('xb') as f:f.write(raw)
 query_results.append({'name':name,'argv':cmd,'exit_code':q.returncode,'stdout_sha256':hashlib.sha256(q.stdout).hexdigest()})
print(json.dumps({'status':'POST_EXIT_READ_ONLY_EXPORT','run_boot_id':run_boot,'observation_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'observation_boottime':__import__('time').clock_gettime(__import__('time').CLOCK_BOOTTIME),'files':files,'directories':dirs,'nonregular':other,'source_files':source,'source_directories':source_dirs,'source_nonregular':source_other,'payload_processes':payload,'root_role_processes':roles,'parent_cgroup_exists':Path('/sys/fs/cgroup/dclr6batch12.slice').exists(),'batch_state_exists':(root/'inputs/batch_state.json').exists(),'budget_counter_exists':(root/'out/visits.bin').exists(),'budget_journal_exists':(root/'out/visits.bin.journal.jsonl').exists(),'closed_marker_exists':(root/'inputs/CLOSED.json').exists(),'STOP_REQUEST_exists':(root/'out/STOP_REQUEST.json').exists(),'native_seal_exists':(root/'out/EVIDENCE.zip').exists(),'journal_argv':argv,'journal_exit':j.returncode,'queries':query_results,'private_originals':'Capability nonce preserved in private snapshot only'},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Post-exit pre-T0-aware read-only snapshot/export, current failed units and controlled-role audit','POST_EXIT_READ_ONLY_EXPORT')
assert r['exit_code']==0,r['stderr']
x=json.loads(r['stdout']);dump(E/'POSTRUN_AUDIT.json',x)
base=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch12');frozen=base/'FROZEN_PF';(frozen/'host').mkdir()
for name in ['windows_entry.py','startup_finalize.py']:
 entry=Path(r'D:\毕业设计\DCL-R6-isolated-verification\pf01\host')/name;shutil.copyfile(entry,frozen/'host'/name)
 x['source_files'].append({'relative':'host/'+name,'bytes':entry.stat().st_size,'sha256':hashlib.sha256(entry.read_bytes()).hexdigest(),'origin':'host frozen program'})
for name,rows,folder,other in [('NATIVE_EXPORT_LOCK.json',x['files'],'native_snapshot',x['nonregular']),('FROZEN_SOURCE_EXPORT_LOCK.json',x['source_files'],'FROZEN_PF',x['source_nonregular'])]:
 for row in rows:row['host']=str(base/folder/row['relative'])
 dump(E/name,{'files':rows,'nonregular':other,'run_boot_id':x['run_boot_id']})
print(json.dumps({'native_files':len(x['files']),'source_files':len(x['source_files']),'T0_exists':x['batch_state_exists'],'counter_exists':x['budget_counter_exists'],'closed':x['closed_marker_exists'],'STOP':x['STOP_REQUEST_exists'],'native_seal':x['native_seal_exists'],'controlled_roles_empty':not x['payload_processes'] and not x['root_role_processes'],'roles':x['root_role_processes'],'parent_cgroup_exists':x['parent_cgroup_exists']},ensure_ascii=False))
