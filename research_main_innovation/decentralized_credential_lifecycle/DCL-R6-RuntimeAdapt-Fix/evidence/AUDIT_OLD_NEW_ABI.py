"""Compare old cached-package ELF versions with current evidence, read-only."""
from EXEC_ADMIN import call,dump,E
import json
CODE=r'''
from pathlib import Path
import gzip,json,re,resource,signal,subprocess,time,hashlib
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30));signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(30)
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-RuntimeAdapt-Fix/evidence');out=e/'old_new_abi';out.mkdir()
export=json.loads((e/'PLATFORM_EXPORT.json').read_bytes());old=[]
for i,row in enumerate(export['old_members']):
 p=e/row['relative'];q=subprocess.run(['/usr/bin/readelf','-V',str(p)],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
 (out/('%02d.version.stdout.raw'%i)).write_bytes(q.stdout);(out/('%02d.version.stderr.raw'%i)).write_bytes(q.stderr)
 text=q.stdout.decode();mode=None;definitions=set();requirements=set()
 for line in text.splitlines():
  if line.startswith('Version definition section'):mode='definitions'
  elif line.startswith('Version needs section'):mode='needs'
  match=re.search(r'\bName:\s+(\S+)',line)
  if match and mode=='definitions':definitions.add(match[1])
  elif match and mode=='needs':requirements.add(match[1])
 old.append({'member':row['member'],'sha256':row['sha256'],'version_definitions':sorted(definitions),'version_requirements_union':sorted(requirements),'readelf_exit':q.returncode})
changelog=Path('/usr/share/doc/libc6/changelog.Debian.gz');entries=[]
if changelog.exists():
 text=gzip.decompress(changelog.read_bytes()).decode(errors='replace');chunks=re.split(r'(?=^glibc \()',text,flags=re.M)
 for chunk in chunks:
  if re.match(r'glibc \(2\.39-0ubuntu8\.(?:9|10|11|12)\)',chunk):entries.append(chunk)
 (out/'glibc-relevant-changelog.txt').write_text('\n'.join(entries),encoding='utf-8')
q=subprocess.run(['/usr/bin/dpkg','--verify','ubuntu-keyring'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
print(json.dumps({'status':'READ_ONLY_OLD_NEW_ABI','old_members':old,'relevant_changelog_entries':entries,
 'keyring_package_verify':{'argv':['/usr/bin/dpkg','--verify','ubuntu-keyring'],'exit_code':q.returncode,'stdout':q.stdout.decode(),'stderr':q.stderr.decode()},
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'observation_boottime':time.clock_gettime(time.CLOCK_BOOTTIME),'old_ELF_executions':0},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Readonly old cached8.9 symbol versions/changelog and keyring package verification; no old ELF execution','READ_ONLY_OLD_NEW_ABI')
assert r['exit_code']==0,r['stderr']
q=json.loads(r['stdout']);dump(E/'OLD_NEW_ABI_AUDIT.json',q)
print(json.dumps({'old_members':len(q['old_members']),'changelog_entries':len(q['relevant_changelog_entries']),'keyring_verify_exit':q['keyring_package_verify']['exit_code'],'keyring_verify_output':q['keyring_package_verify']['stdout'],'target_runs':0},ensure_ascii=False))
