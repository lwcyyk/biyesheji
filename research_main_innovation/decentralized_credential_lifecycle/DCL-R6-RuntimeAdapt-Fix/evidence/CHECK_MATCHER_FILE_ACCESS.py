"""Read-only metadata/access check for exact files the matcher will consume."""
from EXEC_ADMIN import call,dump,E
import json
CODE=r'''
from pathlib import Path
import hashlib,json,os,resource,signal,stat,time
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30));signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(20)
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-RuntimeAdapt-Fix/evidence')
a=json.loads((e/'FINAL_PLATFORM_AUDIT.json').read_bytes());paths=[r['path'] for r in a['loader_configuration']]+['/var/lib/dpkg/status','/var/lib/dpkg/info/libc6:amd64.md5sums','/var/lib/dpkg/info/libc-bin.md5sums'];rows=[]
for name in paths:
 p=Path(name);s=p.lstat();row={'path':name,'is_symlink':p.is_symlink(),'link_text':os.readlink(p) if p.is_symlink() else None,'resolved':str(p.resolve()),'lstat_mode':stat.S_IMODE(s.st_mode)}
 try:
  fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:
   q=os.fstat(fd);row.update(nofollow_read_ok=True,uid=q.st_uid,gid=q.st_gid,mode=stat.S_IMODE(q.st_mode),nlink=q.st_nlink,bytes=q.st_size)
  finally:os.close(fd)
 except OSError as exc:row.update(nofollow_read_ok=False,error=repr(exc))
 rows.append(row)
print(json.dumps({'status':'READ_ONLY_MATCHER_FILE_ACCESS','files':rows,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'observation_boottime':time.clock_gettime(time.CLOCK_BOOTTIME),'business_runs':0},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Readonly exact O_NOFOLLOW metadata/access conditions for loader configuration and package records','READ_ONLY_MATCHER_FILE_ACCESS')
assert r['exit_code']==0,r['stderr'];q=json.loads(r['stdout']);dump(E/'MATCHER_FILE_ACCESS.json',q)
print(json.dumps({'files':len(q['files']),'symlinks':[x for x in q['files'] if x['is_symlink']],'read_failures':[x['path'] for x in q['files'] if not x['nofollow_read_ok']]},ensure_ascii=False))
