"""Authorized fail-closed cleanup through frozen functions; no new case/window."""
from EXEC_ADMIN import call,dump,E
import json

CODE=r'''
from pathlib import Path
import hashlib,json,os,resource,sys,time
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
root=Path('/var/lib/dcl-r6/batch09');src=Path('/var/lib/dcl-r6/cr09/src')
lock=json.loads((src.parent/'inputs/execution_lock.json').read_text());m=json.loads((src.parent/'inputs/static_manifest.json').read_text())
assert hashlib.sha256((src.parent/'inputs/static_manifest.json').read_bytes()).hexdigest()==lock['static_manifest_sha256']
for name,expected in m['source_hashes'].items():assert hashlib.sha256((src/name).read_bytes()).hexdigest()==expected
state=json.loads((root/'inputs/batch_state.json').read_text());epoch=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
assert state['boot_id']==epoch and state['execution_mode']=='CALIBRATE_S1S9_ONLY'
assert state['status']=='AWAIT_EXPECTED_RESUME' and not(root/'inputs/CLOSED.json').exists()
budget=root/'out/visits.bin';journal=budget.with_suffix('.bin.journal.jsonl');intent=budget.with_suffix('.bin.intent.json')
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [budget,journal,intent]}
window={k:state[k] for k in ['T0','deadline','stop_at']};started=time.clock_gettime(time.CLOCK_BOOTTIME)
sys.argv=[str(src/'guard.py'),'--batch-root',str(root)]
sys.path.insert(0,str(src));import guard as G
cleanup=G.stop_tree('CALDIAG_ABORT_AFTER_RESUME_MANAGER_FAILURE',True)
G.seal()
until=time.clock_gettime(time.CLOCK_BOOTTIME)+10;roles=[]
while True:
 roles=[]
 for p in Path('/proc').glob('[0-9]*'):
  try:
   argv=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
   if '--role' in argv and str(src/'guard.py') in argv:roles.append({'pid':int(p.name),'argv':argv})
  except (OSError,ValueError):pass
 if not roles or time.clock_gettime(time.CLOCK_BOOTTIME)>=until:break
 time.sleep(.05)
after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [budget,journal,intent]}
final=json.loads((root/'inputs/batch_state.json').read_text())
assert before==after and all(final[k]==v for k,v in window.items())
print(json.dumps({'status':'FROZEN_FAIL_CLOSED_CLEANUP','run_boot_id':epoch,'cleanup_started':started,'cleanup_finished':time.clock_gettime(time.CLOCK_BOOTTIME),'reason':'CALDIAG_ABORT_AFTER_RESUME_MANAGER_FAILURE','original_window':window,'budget_before_sha256':before,'budget_after_sha256':after,'budget_unchanged':before==after,'closed':(root/'inputs/CLOSED.json').exists(),'final_state_status':final['status'],'group_cleanup':cleanup,'remaining_role_processes':roles,'native_seal_exists':(root/'out/EVIDENCE.zip').exists(),'target_cases_started':0,'new_window_created':False},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'After preserving initial snapshot, close failed batch09 through frozen guard.stop_tree/seal; unchanged T0 and counter; no case/restart/resume','AUTHORIZED_FAILURE_CLEANUP_ONLY')
assert r['exit_code']==0,r['stderr']
x=json.loads(r['stdout']);dump(E/'FROZEN_FAILURE_CLEANUP.json',x)
print(json.dumps({'status':x['status'],'closed':x['closed'],'budget_unchanged':x['budget_unchanged'],'remaining_roles':len(x['remaining_role_processes']),'native_seal':x['native_seal_exists']},ensure_ascii=False))
