"""Read-only preservation of current/old ELF and signed cached metadata."""
from EXEC_ADMIN import call,dump,E
import json
CODE=r'''
from pathlib import Path
import hashlib,json,os,resource,signal,stat,subprocess,tarfile,time
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30));signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(45)
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-RuntimeAdapt-Fix/evidence');dest=e/'platform_snapshot';dest.mkdir()
discovery=json.loads((e/'RUNTIME_DISCOVERY.json').read_bytes());prov=json.loads((e/'PROVENANCE_AUDIT.json').read_bytes())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while True:
   b=f.read(1048576)
   if not b:break
   h.update(b)
 return h.hexdigest()
rows=[]
paths=[Path(r['path']) for r in discovery['artifacts'][:3]]+[Path(r['index']) for r in prov['repositories']]
for p in paths:
 q=dest/p.relative_to('/');q.parent.mkdir(parents=True,exist_ok=True)
 with p.open('rb') as source,q.open('xb') as target:
  while True:
   b=source.read(65536)
   if not b:break
   target.write(b)
 s=p.stat();rows.append({'linux_path':str(p),'relative':q.relative_to(e).as_posix(),'sha256':sha(p),'bytes':s.st_size,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'inode':s.st_ino,'device':s.st_dev})
aliases=[]
for name in ['/lib64','/lib64/ld-linux-x86-64.so.2','/usr/lib64/ld-linux-x86-64.so.2','/lib','/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2']:
 p=Path(name);aliases.append({'path':name,'is_symlink':p.is_symlink(),'link_text':os.readlink(p) if p.is_symlink() else None,'resolved':str(p.resolve())})
old=Path('/var/cache/apt/archives/libc6_2.39-0ubuntu8.9_amd64.deb');old_members=[]
old_info=subprocess.run(['/usr/bin/dpkg-deb','--field',str(old),'Package','Version','Architecture'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
(e/'provenance/old-libc6-control.stdout.raw').write_bytes(old_info.stdout)
proc=subprocess.Popen(['/usr/bin/dpkg-deb','--fsys-tarfile',str(old)],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
wanted={r['path'].lstrip('/') for r in discovery['artifacts'][:3]}
with tarfile.open(fileobj=proc.stdout,mode='r|') as archive:
 for member in archive:
  name=member.name.lstrip('./')
  if name in wanted and member.isfile():
   content=archive.extractfile(member).read();q=dest/'old-package-8.9'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(content)
   old_members.append({'member':name,'relative':q.relative_to(e).as_posix(),'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)})
proc.stdout.close();err=proc.stderr.read();code=proc.wait(timeout=5);(e/'provenance/old-libc6-extraction.stderr.raw').write_bytes(err)
config=[]
for p in [Path('/etc/ld.so.conf'),*Path('/etc/ld.so.conf.d').glob('*.conf')]:
 if p.exists():config.append({'path':str(p),'sha256':sha(p),'text':p.read_text()})
m=json.loads(Path('/var/lib/dcl-r6/tr01/inputs/static_manifest.json').read_bytes());tree=json.loads(Path('/var/lib/dcl-r6/tr01/inputs/runtime_tree_lock.json').read_bytes());expected=dict(m['runtime_files']);expected.update({p:r['sha256'] for p,r in tree['files'].items()})
differences=[]
for p,wanted_hash in expected.items():
 actual=sha(p)
 if actual!=wanted_hash:differences.append({'path':p,'expected_sha256':wanted_hash,'actual_sha256':actual})
status=Path('/var/lib/dpkg/status');catalogs=[Path('/var/lib/dpkg/info/libc6:amd64.md5sums'),Path('/var/lib/dpkg/info/libc-bin.md5sums')]
print(json.dumps({'status':'READ_ONLY_PROVENANCE_EXPORT','files':rows,'aliases':aliases,'old_package_control':old_info.stdout.decode(),
 'old_package_sha256':sha(old),'old_member_extraction_exit':code,'old_members':old_members,'loader_config':config,
 'runtime_files_checked':len(expected),'runtime_differences':differences,
 'catalogs':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'uid':p.stat().st_uid,'mode':stat.S_IMODE(p.stat().st_mode)} for p in catalogs],
 'status_database':{'path':str(status),'bytes':status.stat().st_size,'uid':status.stat().st_uid,'mode':stat.S_IMODE(status.stat().st_mode)},
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'observation_boottime':time.clock_gettime(time.CLOCK_BOOTTIME),
 'writes':'Only new evidence exports; source/system files unchanged','target_test_runs':0},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Readonly current3 ELF/signed index preservation, cached old8.9 member extraction and fresh full runtime comparison','READ_ONLY_PROVENANCE_EXPORT')
assert r['exit_code']==0,r['stderr']
q=json.loads(r['stdout']);dump(E/'PLATFORM_EXPORT.json',q)
print(json.dumps({'exported_files':len(q['files']),'old_members':len(q['old_members']),'old_extraction_exit':q['old_member_extraction_exit'],
 'runtime_checked':q['runtime_files_checked'],'current_differences':len(q['runtime_differences'])},ensure_ascii=False))
