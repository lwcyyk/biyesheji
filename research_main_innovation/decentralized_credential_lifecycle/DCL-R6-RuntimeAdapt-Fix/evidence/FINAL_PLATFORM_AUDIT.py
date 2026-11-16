"""Final read-only platform/config freshness before static baseline freeze."""
from EXEC_ADMIN import call,dump,E
import json
CODE=r'''
from pathlib import Path
import hashlib,json,os,pwd,resource,signal,stat,subprocess,time
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30));signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(30)
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-RuntimeAdapt-Fix/evidence')
d=json.loads((e/'RUNTIME_DISCOVERY.json').read_bytes());stable=[]
for row in d['artifacts']:
 actual=h(row['path']);stable.append({'path':row['path'],'sha256':actual,'unchanged_since_first_query':actual==row['sha256']})
configs=[]
for p in [Path('/etc/ld.so.cache'),Path('/etc/ld.so.conf'),*Path('/etc/ld.so.conf.d').glob('*.conf')]:
 if p.exists():
  s=p.stat();configs.append({'path':str(p),'sha256':h(p),'bytes':s.st_size,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode)})
q=subprocess.run(['/usr/bin/systemctl','show','--property=Version','--value'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
user=pwd.getpwuid(999)
print(json.dumps({'status':'READ_ONLY_FINAL_PLATFORM','stable_components_and_python':stable,'loader_configuration':configs,
 'systemd':q.stdout.decode().strip(),'systemd_exit':q.returncode,'kernel':os.uname().release,'architecture':os.uname().machine,
 'uid':999,'gid':user.pw_gid,'groups':os.getgrouplist(user.pw_name,user.pw_gid),
 'cgroup_v2':any(x.split()[4]=='/sys/fs/cgroup' and ' - cgroup2 ' in x for x in Path('/proc/self/mountinfo').read_text().splitlines()),
 'future_runtime_exists':Path('/var/lib/dcl-r6/batch14').exists(),'future_source_exists':Path('/var/lib/dcl-r6/ra01').exists(),
 'future_slice_exists':Path('/etc/systemd/system/dclr6batch14.slice').exists(),
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'observation_boottime':time.clock_gettime(time.CLOCK_BOOTTIME),'T0':None,'R':None,'workload_runs':0},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Final readonly runtime/config/hash freshness, kernel/systemd/UID/cgroup and absence of future instance','READ_ONLY_FINAL_PLATFORM')
assert r['exit_code']==0,r['stderr']
q=json.loads(r['stdout']);dump(E/'FINAL_PLATFORM_AUDIT.json',q)
print(json.dumps({'status':q['status'],'stable':all(x['unchanged_since_first_query'] for x in q['stable_components_and_python']),
 'systemd':q['systemd'],'kernel':q['kernel'],'loader_config_files':len(q['loader_configuration']),
 'future_instance_exists':q['future_runtime_exists'],'future_source_exists':q['future_source_exists']},ensure_ascii=False))
