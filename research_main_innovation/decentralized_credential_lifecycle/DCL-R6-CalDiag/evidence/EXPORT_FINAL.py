"""Export the terminal snapshot separately; initial failure snapshot stays intact."""
from EXEC_ADMIN import call,dump,E
from pathlib import Path
import hashlib
import json

CODE=r'''
from pathlib import Path
import hashlib,json,os,resource,stat,subprocess
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
root=Path('/var/lib/dcl-r6/batch09');dst=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/batch09/final_snapshot')
assert (root/'inputs/CLOSED.json').exists() and (root/'out/EVIDENCE.zip').exists() and not dst.exists()
dst.mkdir();files=[];dirs=[];other=[]
for p in [root,*sorted(root.rglob('*'))]:
 s=p.lstat();rel=p.relative_to(root).as_posix();meta={'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink}
 if stat.S_ISDIR(s.st_mode):dirs.append({'relative':rel,**meta});continue
 if not stat.S_ISREG(s.st_mode):other.append({'relative':rel,'type':stat.S_IFMT(s.st_mode),**meta});continue
 raw=p.read_bytes();q=dst/rel;q.parent.mkdir(parents=True,exist_ok=True)
 with q.open('xb') as f:f.write(raw)
 files.append({'relative':rel,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),**meta})
payload=[];roles=[]
for p in Path('/proc').glob('[0-9]*'):
 try:
  status=dict(v.split(':',1) for v in (p/'status').read_text().splitlines() if ':' in v);uids=list(map(int,status['Uid'].split()));argv=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  if 999 in uids:payload.append({'pid':int(p.name),'argv':argv})
  if '--role' in argv and any(a.startswith('/var/lib/dcl-r6/') and a.endswith('/guard.py') for a in argv):roles.append({'pid':int(p.name),'argv':argv})
 except (OSError,ValueError,KeyError):pass
s=json.loads((root/'inputs/batch_state.json').read_text());lock=json.loads(Path('/var/lib/dcl-r6/cr09/inputs/execution_lock.json').read_text())
argv=lock['journal_export_command'][:];argv[argv.index('--boot')]='--boot='+s['boot_id'].replace('-','');j=subprocess.run(argv,capture_output=True,timeout=30)
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-CalDiag/evidence')
for stream,raw in [('stdout',j.stdout),('stderr',j.stderr)]:
 with (e/('FINAL_RUN_BOOT_JOURNAL.'+stream+'.raw')).open('xb') as f:f.write(raw)
print(json.dumps({'run_boot_id':s['boot_id'],'observation_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'files':files,'directories':dirs,'nonregular':other,'payload_processes':payload,'root_role_processes':roles,'parent_cgroup_exists':Path('/sys/fs/cgroup/dclr6batch09.slice').exists(),'closed_marker':True,'state_document_status':s['status'],'native_seal_exists':True,'journal_argv':argv,'journal_exit':j.returncode,'controlled_roles_empty':not payload and not roles},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Export terminal CLOSED/sealed snapshot without overwriting initial failure evidence; verify all controlled processes empty','TERMINAL_READ_ONLY_EXPORT')
assert r['exit_code']==0,r['stderr']
x=json.loads(r['stdout']);dump(E/'FINAL_POSTRUN_AUDIT.json',x)
base=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch09\final_snapshot')
for row in x['files']:row['host']=str(base/row['relative'])
dump(E/'FINAL_NATIVE_EXPORT_LOCK.json',{'files':x['files'],'nonregular':x['nonregular'],'run_boot_id':x['run_boot_id']})
assert x['controlled_roles_empty'] and not x['parent_cgroup_exists'] and x['journal_exit']==0
print(json.dumps({'final_native_files':len(x['files']),'closed_marker':True,'state_document_status':x['state_document_status'],'all_controlled_roles_empty':True,'parent_cgroup_exists':False,'native_seal':True,'journal_exit':x['journal_exit']},ensure_ascii=False))
