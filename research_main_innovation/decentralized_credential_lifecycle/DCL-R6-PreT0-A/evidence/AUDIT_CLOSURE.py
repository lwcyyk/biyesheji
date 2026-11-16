"""Read-only audit after automatic entry/finalizer return; performs no cleanup."""
from EXEC_ADMIN import call,dump,E
import json
CODE=r'''
from pathlib import Path
import json,os,time,struct,subprocess,resource
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
root=Path('/var/lib/dcl-r6/batch11');source='/var/lib/dcl-r6/pt01/src/'
roles=[];payload=[]
for p in Path('/proc').glob('[0-9]*'):
 try:
  args=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  status=dict(x.split(':',1) for x in (p/'status').read_text().splitlines() if ':' in x)
  if 999 in map(int,status['Uid'].split()):payload.append(int(p.name))
  if '--batch-root' in args and str(root) in args and any(a in args for a in [source+'guard.py',source+'boot_continuity.py']):
   raw=(p/'stat').read_text().split(') ',1)[1].split();roles.append({'pid':int(p.name),'start_ticks':int(raw[19]),'args':args})
 except (OSError,ValueError,KeyError):pass
records={}
for name in ['inputs/batch_state.json','inputs/PT_RUNTIME_CHECKPOINT.json','inputs/STOP_ARMED.json','inputs/CLOSED.json','out/STOP_REQUEST.json',
 'inputs/root_private/boot/mr_first_failure.json','inputs/root_private/boot/mr_close_state.json','inputs/SEAL_ERROR.json','inputs/root_private/boot/pt_seal_disposition.json']:
 p=root/name
 if p.exists():records[name]=json.loads(p.read_bytes())
counter=root/'out/visits.bin';R=None
if counter.exists():
 raw=counter.read_bytes();R=struct.unpack('<Q',raw[8:16])[0] if len(raw)==24 else 'UNRESOLVED'
q=subprocess.run(['/usr/bin/systemctl','show','dclr6batch11.slice','dclr6batch11-stop.service','--property=Id','--property=ActiveState','--property=SubState','--property=MainPID','--property=Result','--property=ExecMainStatus','--property=ControlGroup'],capture_output=True,timeout=5)
print(json.dumps({'status':'READ_ONLY_CLOSURE_AUDIT','boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'observation_boottime':time.clock_gettime(time.CLOCK_BOOTTIME),'roles':roles,'payload':payload,
 'parent_cgroup_exists':Path('/sys/fs/cgroup/dclr6batch11.slice').exists(),'records':records,'R':R,'units':q.stdout.decode(),
 'native_zip_exists':(root/'out/EVIDENCE.zip').exists(),'runtime_files':sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file())},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Read-only current roles, group and automatic closure originals after first failure','READ_ONLY_CLOSURE_AUDIT')
assert r['exit_code']==0,r['stderr']
q=json.loads(r['stdout']);dump(E/'CLOSURE_AUDIT.json',q)
print(json.dumps({k:v for k,v in q.items() if k!='runtime_files'},ensure_ascii=False))
