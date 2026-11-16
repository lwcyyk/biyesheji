"""Execute frozen batch06 preparation and its single approved launcher; no repair path."""
from pathlib import Path
import hashlib
import json
from EXEC_NATIVE import call,dump,load,E

W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ri01')
P=E.parent
lock=load(E/'execution_lock.json')
base=load(E/'PREFLIGHT_RESULT.json')
assert base['status']=='PREFLIGHT_BASE_PASS'
assert not any(r['classification']=='B06_FROZEN_LAUNCHER' for r in load(E/'COMMAND_PLAN.json')['commands'])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=load(E.parent.parent/'DCL-R6-RootIPC-Fix/evidence/BATCH06_AUTHORIZATION_TEMPLATE.json')
receipt.update(schema='B06-EXECUTION-AUTHORIZATION/1',authorization_status='EXPLICIT_USER_APPROVED_DYNAMIC',
 authorization_text_sha256=sha(E/'TASK_REQUEST.txt'),Root_coordinator_explicitly_approved=True,
 RootIPC_helpers_explicitly_approved=True,Root_coordinator_scope='Current batch06 supervision/handoff/stop/evidence only',
 no_budget_or_deadline_reset=True,source_version='RootIPC-static-1',freeze_revision='r4')
assert receipt['static_manifest_sha256']==sha(E/'static_manifest.json')
assert receipt['execution_lock_sha256']==sha(E/'execution_lock.json')
dump(E/'execution_authorization.json',receipt)
dump(E/'AUTHORIZATION_RECEIPT.json',{'schema':'B06-authorization-review/1','batch_id':'batch06',
 'source_version':'RootIPC-static-1/r4','user_text_sha256':receipt['authorization_text_sha256'],
 'scope':receipt['scope'],'extra_sequential_probe_approved':True,'T0':None,'counter':None,
 'RootTCB_probe':lock['root_ipc_helper_contract'],'dynamic_source_changes':0})

for i,argv in enumerate(lock['preparation_commands'],1):
    result=call(argv,f'Frozen batch06 preparation{i}: exact execution_lock argv','B06_FROZEN_PREPARATION')
    if result['exit_code']:
        dump(E/'PREFLIGHT_FINAL.json',{'status':'PREFLIGHT_FAILED','reason':'PREPARATION_COMMAND_FAILED','command':result['order'],'T0':None,'counter':None})
        raise SystemExit(0)
for name,target in [('TASK_REQUEST.txt','BATCH06_AUTHORIZATION_TEXT.txt'),('execution_authorization.json','execution_authorization.json')]:
    src='/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-batch06/evidence/'+name
    result=call(['/usr/bin/install','-m','0640','-o','root','-g','dcl-r6',src,'/var/lib/dcl-r6/batch06/inputs/'+target],
                'Install current explicit batch06 '+target,'B06_AUTHORIZATION_INSTALL')
    if result['exit_code']:
        dump(E/'PREFLIGHT_FINAL.json',{'status':'PREFLIGHT_FAILED','reason':'AUTHORIZATION_INSTALL_FAILED','command':result['order'],'T0':None,'counter':None})
        raise SystemExit(0)
show=call(['/usr/bin/systemctl','show','dclr6batch06.slice','--property=LoadState','--property=ActiveState',
           '--property=SubState','--property=TasksMax','--property=MemoryMax','--property=ControlGroup'],
          'Read installed frozen parent limits; require inactive before T0','PREFLIGHT_READ_ONLY')
properties=dict(line.split('=',1) for line in show['stdout'].splitlines() if '=' in line)

code=r'''
import hashlib,json,os
from pathlib import Path
root=Path('/var/lib/dcl-r6/batch06');rows=[]
for p in [root,root/'inputs',root/'out',root/'inputs/root_private',root/'inputs/BATCH06_AUTHORIZATION_TEXT.txt',root/'inputs/execution_authorization.json']:
 s=p.stat();rows.append({'path':str(p),'uid':s.st_uid,'gid':s.st_gid,'mode':s.st_mode&0o777,'device':s.st_dev,
  'symlink':p.is_symlink(),'ACL':[a for a in os.listxattr(p) if a.startswith('system.posix_acl_')]})
print(json.dumps({'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'metadata':rows,
 'out_entries':[p.name for p in (root/'out').iterdir()],
 'state_exists':(root/'inputs/batch_state.json').exists(),'counter_exists':(root/'out/visits.bin').exists(),
 'closed_exists':(root/'inputs/CLOSED.json').exists(),
 'authorization_text_sha256':hashlib.sha256((root/'inputs/BATCH06_AUTHORIZATION_TEXT.txt').read_bytes()).hexdigest(),
 'authorization_receipt_sha256':hashlib.sha256((root/'inputs/execution_authorization.json').read_bytes()).hexdigest(),
 'unit_sha256':hashlib.sha256(Path('/etc/systemd/system/dclr6batch06.slice').read_bytes()).hexdigest()}))
'''
meta=call(['/usr/bin/python3.12','-I','-S','-B','-c',code],
          'Final boot, metadata/ACL, authorization and no-window/no-counter checks','PREFLIGHT_READ_ONLY')
actual=json.loads(meta['stdout'])
expected=[(0,989,0o750),(0,989,0o750),(999,989,0o700),(0,0,0o700),(0,989,0o640),(0,989,0o640)]
checks={'base':True,'same_boot':actual['boot_id']==base['boot_id'],
 'parent_limits':show['exit_code']==0 and properties.get('LoadState')=='loaded' and properties.get('ActiveState')=='inactive' and properties.get('TasksMax')=='4' and properties.get('MemoryMax')=='4294967296',
 'metadata':all((r['uid'],r['gid'],r['mode'])==want and not r['symlink'] and not r['ACL'] for r,want in zip(actual['metadata'],expected)),
 'same_device':len({r['device'] for r in actual['metadata']})==1,
 'fresh_window':not actual['out_entries'] and not actual['state_exists'] and not actual['counter_exists'] and not actual['closed_exists'],
 'authorization':actual['authorization_text_sha256']==sha(E/'TASK_REQUEST.txt') and actual['authorization_receipt_sha256']==sha(E/'execution_authorization.json'),
 'slice_hash':actual['unit_sha256']==lock['unit_slice_sha256']}
final={'schema':'B06-final-preflight/1','status':'PREFLIGHT_PASS' if all(checks.values()) else 'PREFLIGHT_FAILED',
       'checks':checks,'boot_id':actual['boot_id'],'parent_properties':properties,'metadata':actual,
       'T0':None,'counter':None}
dump(E/'PREFLIGHT_FINAL.json',final)
print(json.dumps({'final_preflight':final['status'],'checks':checks},ensure_ascii=False),flush=True)
if not all(checks.values()):raise SystemExit(0)
launch=call(lock['launch_command'],'Single approved RootIPC-static-1/r4 batch06 launcher; conditional full chain; stop first critical failure','B06_FROZEN_LAUNCHER')
dump(E/'LAUNCHER_COMPLETION.json',launch)
