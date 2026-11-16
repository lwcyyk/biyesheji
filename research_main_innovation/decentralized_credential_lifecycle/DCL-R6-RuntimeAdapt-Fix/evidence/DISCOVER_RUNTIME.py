"""Finite read-only native identity/package/toolchain discovery; no workload roles."""
from EXEC_ADMIN import call,dump,E
import json
CODE=r'''
from pathlib import Path
import hashlib,json,os,resource,signal,shutil,subprocess,sys,time
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30));signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(30)
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-RuntimeAdapt-Fix/evidence');out=e/'native_queries';out.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
commands=[['/usr/bin/getconf','GNU_LIBC_VERSION'],['/usr/bin/ldd','--version'],
 ['/usr/bin/dpkg-query','--show','--showformat=${binary:Package}\t${Version}\t${Architecture}\t${db:Status-Abbrev}\n','libc6','libc-bin','python3.12-minimal','python3.12','libpython3.12-stdlib','ubuntu-keyring'],
 ['/usr/bin/dpkg','--verify','libc6','libc-bin'],
 ['/usr/bin/dpkg-query','--search','/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2','/usr/lib/x86_64-linux-gnu/libc.so.6','/usr/lib/x86_64-linux-gnu/libm.so.6'],
 ['/usr/bin/apt-cache','policy','libc6','libc-bin']]
results=[]
for i,argv in enumerate(commands):
 before=time.clock_gettime(time.CLOCK_BOOTTIME)
 q=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=8)
 assert len(q.stdout)+len(q.stderr)<4194304
 for name,raw in [('stdout',q.stdout),('stderr',q.stderr)]:
  with (out/('%02d.'%(i+1)+name+'.raw')).open('xb') as f:f.write(raw)
 results.append({'number':i+1,'argv':argv,'exit_code':q.returncode,'stdout':q.stdout.decode(errors='replace'),'stderr':q.stderr.decode(errors='replace'),
  'before':before,'after':time.clock_gettime(time.CLOCK_BOOTTIME)})
tools={name:shutil.which(name) for name in ['readelf','gpgv','dpkg-deb','zstd','lz4','ar','tar','apt-cache','getconf','ldd']}
inventory={}
for name in ['/var/lib/apt/lists','/var/cache/apt/archives','/usr/share/keyrings','/etc/apt/sources.list.d']:
 p=Path(name);inventory[name]=[{'name':q.name,'bytes':q.stat().st_size,'is_file':q.is_file()} for q in sorted(p.iterdir())] if p.exists() else []
paths=['/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2','/usr/lib/x86_64-linux-gnu/libc.so.6','/usr/lib/x86_64-linux-gnu/libm.so.6','/usr/bin/python3.12']
artifacts=[]
for name in paths:
 p=Path(name);s=p.lstat();artifacts.append({'path':name,'is_symlink':p.is_symlink(),'readlink':os.readlink(p) if p.is_symlink() else None,
  'resolved':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size,'uid':s.st_uid,'gid':s.st_gid,'mode':s.st_mode&0o7777})
print(json.dumps({'status':'READ_ONLY_DISCOVERY','commands':results,'tools':tools,'inventory':inventory,'artifacts':artifacts,
 'os_release':Path('/etc/os-release').read_text(),'architecture':os.uname().machine,'kernel':os.uname().release,
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'actor_pid':os.getpid(),'observation_boottime':time.clock_gettime(time.CLOCK_BOOTTIME),
 'python_version':sys.version,'python_executable':sys.executable,'localtime_resolved':str(Path('/etc/localtime').resolve()),
 'loaded_relevant_mappings':[line for line in Path('/proc/self/maps').read_text().splitlines() if any(x in line for x in ['ld-linux','libc.so','libm.so','python3.12'])],
 'LD_environment':{name:os.environ.get(name) for name in ['LD_PRELOAD','LD_LIBRARY_PATH','LD_AUDIT']},
 'ld_so_preload':Path('/etc/ld.so.preload').read_text() if Path('/etc/ld.so.preload').exists() else None,
 'process_AS_query_envelope':resource.getrlimit(resource.RLIMIT_AS),'workload_or_test_runs':0},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Read-only glibc version/package integrity, actual paths, ELF tool and cached provenance inventory','READ_ONLY_RUNTIME_DISCOVERY')
assert r['exit_code']==0,r['stderr']
q=json.loads(r['stdout']);dump(E/'RUNTIME_DISCOVERY.json',q)
print(json.dumps({'status':q['status'],'boot_id':q['boot_id'],'tools':q['tools'],'package_verify_exit':q['commands'][3]['exit_code'],
 'package_verify_stdout':q['commands'][3]['stdout'],'apt_list_files':len(q['inventory']['/var/lib/apt/lists']),
 'cached_archives':len(q['inventory']['/var/cache/apt/archives'])},ensure_ascii=False))
