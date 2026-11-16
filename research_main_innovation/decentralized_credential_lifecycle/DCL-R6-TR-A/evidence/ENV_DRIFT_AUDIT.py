"""Read-only diagnosis of actual preflight runtime hash drift. No retry/repair."""
from EXEC_ADMIN import call,dump,E
import json
CODE=r'''
from pathlib import Path
import hashlib,json,os,pwd,resource,signal,stat,subprocess,sys,time
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30));signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(30)
source=Path('/var/lib/dcl-r6/tr01');root=Path('/var/lib/dcl-r6/batch13')
m=json.loads((source/'inputs/static_manifest.json').read_bytes());tree=json.loads((source/'inputs/runtime_tree_lock.json').read_bytes())
expected=dict(m['runtime_files']);expected.update({p:r['sha256'] for p,r in tree['files'].items()})
runtime_differences=[];runtime_checked=0;started=time.clock_gettime(time.CLOCK_BOOTTIME)
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as stream:
  while True:
   b=stream.read(1048576)
   if not b:break
   h.update(b)
 return h.hexdigest()
for name,wanted in expected.items():
 try:
  p=Path(name);actual=digest(p);s=p.stat();runtime_checked+=1
  if actual!=wanted:runtime_differences.append({'path':name,'expected_sha256':wanted,'actual_sha256':actual,'bytes':s.st_size,
    'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'mtime_ns':s.st_mtime_ns,'resolved':str(p.resolve())})
 except OSError as exc:runtime_differences.append({'path':name,'expected_sha256':wanted,'error':repr(exc)})
src_errors=[]
for name,wanted in m['source_hashes'].items():
 if digest(source/'src'/name)!=wanted:src_errors.append('src/'+name)
for name,wanted in m['bound_inputs'].items():
 if digest(source/name)!=wanted:src_errors.append(name)
roles=[];payload=[]
for p in Path('/proc').glob('[0-9]*'):
 try:
  status=dict(x.split(':',1) for x in (p/'status').read_text().splitlines() if ':' in x);args=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  if 999 in map(int,status['Uid'].split()):payload.append(int(p.name))
  if '--batch-root' in args and str(root) in args and any(str(source/'src'/name) in args for name in ['guard.py','boot_continuity.py']):roles.append({'pid':int(p.name),'argv':args})
 except (OSError,ValueError,KeyError):pass
queries=[]
for argv in [['/usr/bin/dpkg-query','--show','--showformat=${Package}\t${Version}\n','libc6','libc-bin'],
 ['/usr/bin/dpkg-query','--search','/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2'],
 ['/usr/bin/systemctl','list-units','dclr6batch13*','--all','--no-pager','--no-legend']]:
 q=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
 queries.append({'argv':argv,'exit_code':q.returncode,'stdout':q.stdout.decode(errors='replace'),'stderr':q.stderr.decode(errors='replace')})
package_log=[]
log=Path('/var/log/dpkg.log')
if log.exists():
 for line in log.read_text(errors='replace').splitlines()[-500:]:
  if 'libc6:' in line or 'libc-bin:' in line:package_log.append(line)
print(json.dumps({'status':'READ_ONLY_RUNTIME_DRIFT_AUDIT','runtime_files_checked':runtime_checked,'differences':runtime_differences,
 'frozen_source_input_mismatches':src_errors,'queries':queries,'package_log_excerpt':package_log,
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'observation_boottime':time.clock_gettime(time.CLOCK_BOOTTIME),
 'root_roles':roles,'payload_pids':payload,'runtime_root_exists':root.exists(),'installed_slice_exists':Path('/etc/systemd/system/dclr6batch13.slice').exists(),
 'parent_cgroup_exists':Path('/sys/fs/cgroup/dclr6batch13.slice').exists(),'T0':None,'R':None,'elapsed_seconds':time.clock_gettime(time.CLOCK_BOOTTIME)-started,
 'actions':'Read/hash/package metadata only; no installs, reloads, resets, source or runtime writes'},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Read-only current pinned runtime differences, package metadata and no-batch/no-role audit after preflight rejection','READ_ONLY_RUNTIME_DRIFT_AUDIT')
assert r['exit_code']==0,r['stderr']
q=json.loads(r['stdout']);dump(E/'RUNTIME_DRIFT_AUDIT.json',q)
print(json.dumps({'status':q['status'],'checked':q['runtime_files_checked'],'differences':len(q['differences']),
 'changed_paths':[x['path'] for x in q['differences']],'source_mismatches':q['frozen_source_input_mismatches'],
 'roles_empty':not q['root_roles'] and not q['payload_pids'],'runtime_root_exists':q['runtime_root_exists']},ensure_ascii=False))
