"""Read-only source/runtime snapshot after preflight rejection; no native batch exists."""
from EXEC_ADMIN import call,dump,load,E
from pathlib import Path
import hashlib,json,shutil
control=Path(load(E/'AUTHORIZATION_RECEIPT_LOCK.json')['control_directory'])
for p in control.iterdir():
    if p.is_file():shutil.copyfile(p,E/p.name)
CODE=r'''
from pathlib import Path
import hashlib,json,os,resource,signal,stat
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30));signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(30)
src=Path('/var/lib/dcl-r6/tr01');base=Path('/mnt/d/毕业设计/DCL-R6-isolated-verification/batch13')
assert not Path('/var/lib/dcl-r6/batch13').exists() and not base.exists()
frozen=base/'FROZEN_TR';runtime=base/'preflight_runtime_snapshot';frozen.mkdir(parents=True);runtime.mkdir()
def export(p,q,relative):
 s=p.lstat();assert stat.S_ISREG(s.st_mode)
 q.parent.mkdir(parents=True,exist_ok=True);digest=hashlib.sha256();size=0
 with p.open('rb') as source,q.open('xb') as target:
  while True:
   b=source.read(65536)
   if not b:break
   target.write(b);digest.update(b);size+=len(b)
 assert size==s.st_size
 return {'relative':relative,'bytes':size,'sha256':digest.hexdigest(),'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),
  'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'ACL':[n for n in os.listxattr(p,follow_symlinks=False) if n.startswith('system.posix_acl_')]}
source_rows=[]
for p in sorted(src.rglob('*')):
 if p.is_file():source_rows.append(export(p,frozen/p.relative_to(src),p.relative_to(src).as_posix()))
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-TR-A/evidence')
audit=json.loads((e/'RUNTIME_DRIFT_AUDIT.json').read_bytes());runtime_rows=[]
for row in audit['differences']:
 p=Path(row['path']);rel=p.relative_to('/').as_posix();record=export(p,runtime/rel,rel)
 assert record['sha256']==row['actual_sha256'];record['original_linux_path']=row['path'];record['frozen_expected_sha256']=row['expected_sha256'];runtime_rows.append(record)
print(json.dumps({'status':'READ_ONLY_PREFLIGHT_SOURCE_AND_RUNTIME_EXPORT','source_files':source_rows,'changed_runtime_files':runtime_rows,
 'source_path':str(src),'runtime_root_exists':False,'new_runtime_objects_created':False,'observation_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'administrative_export_only':True},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Read-only export of57 frozen Linux files and3 changed runtime originals after preflight rejection','POST_PREFLIGHT_READ_ONLY_EXPORT')
assert r['exit_code']==0,r['stderr']
q=json.loads(r['stdout']);base=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch13');frozen=base/'FROZEN_TR';(frozen/'host').mkdir()
for name in ['windows_entry.py','startup_finalize.py']:
    p=Path(r'D:\毕业设计\DCL-R6-isolated-verification\tr01\host')/name;shutil.copyfile(p,frozen/'host'/name)
    q['source_files'].append({'relative':'host/'+name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'origin':'host frozen program'})
for row in q['source_files']:row['host']=str(frozen/row['relative'])
for row in q['changed_runtime_files']:row['host']=str(base/'preflight_runtime_snapshot'/row['relative'])
dump(E/'FROZEN_SOURCE_EXPORT_LOCK.json',{'files':q['source_files'],'observation_boot_id':q['observation_boot_id']})
dump(E/'DRIFTED_RUNTIME_EXPORT_LOCK.json',{'files':q['changed_runtime_files'],'observation_boot_id':q['observation_boot_id']})
dump(E/'POST_PREFLIGHT_EXPORT.json',q)
print(json.dumps({'source_files':len(q['source_files']),'drifted_runtime_files':len(q['changed_runtime_files']),'native_batch_created':False,'source_changes':0},ensure_ascii=False))
