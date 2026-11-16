"""Offline cached Ubuntu signature/index and installed-package provenance audit."""
from EXEC_ADMIN import call,dump,E
import json
CODE=r'''
from pathlib import Path
import hashlib,json,os,resource,signal,subprocess,time,gzip
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30));signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(30)
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-RuntimeAdapt-Fix/evidence');out=e/'provenance';out.mkdir()
def h(p):
 d=hashlib.sha256()
 with Path(p).open('rb') as f:
  while True:
   b=f.read(1048576)
   if not b:break
   d.update(b)
 return d.hexdigest()
repos=[]
for prefix in ['archive.ubuntu.com_ubuntu_dists_noble-updates','security.ubuntu.com_ubuntu_dists_noble-security']:
 release=Path('/var/lib/apt/lists')/(prefix+'_InRelease');index=Path('/var/lib/apt/lists')/(prefix+'_main_binary-amd64_Packages')
 argv=['/usr/bin/gpgv','--status-fd=1','--keyring','/usr/share/keyrings/ubuntu-archive-keyring.gpg',str(release)]
 q=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=8)
 for name,raw in [('stdout',q.stdout),('stderr',q.stderr)]:
  with(out/(prefix+'.gpgv.'+name+'.raw')).open('xb') as f:f.write(raw)
 text=release.read_text();sha_rows={};section=False
 for line in text.splitlines():
  if line=='SHA256:':section=True;continue
  if section:
   if not line.startswith(' '):section=False;continue
   parts=line.split()
   if len(parts)==3:sha_rows[parts[2]]={'sha256':parts[0],'bytes':int(parts[1])}
 expected=sha_rows.get('main/binary-amd64/Packages');actual=h(index);size=index.stat().st_size
 package_stanzas=[]
 with index.open(encoding='utf-8') as stream:
  stanza=[]
  for line in stream:
   if line.strip():stanza.append(line)
   else:
    fields={}
    for row in stanza:
     if ': ' in row and not row[0].isspace():k,v=row.rstrip('\n').split(': ',1);fields[k]=v
    if fields.get('Package') in ['libc6','libc-bin'] and fields.get('Version')=='2.39-0ubuntu8.12':package_stanzas.append(fields)
    stanza=[]
 with(out/(prefix+'.InRelease')).open('xb') as f:f.write(release.read_bytes())
 # Preserve the small matching stanzas plus the full index identity, not a fabricated per-file package proof.
 with(out/(prefix+'.package-stanzas.json')).open('x',encoding='utf-8') as f:json.dump(package_stanzas,f,ensure_ascii=False,indent=2)
 repos.append({'release':str(release),'release_sha256':h(release),'gpgv_argv':argv,'gpgv_exit':q.returncode,'gpg_status':q.stdout.decode(),
  'gpg_stderr':q.stderr.decode(),'index':str(index),'index_sha256':actual,'index_bytes':size,'signed_expected':expected,
  'index_matches_signed_release':bool(expected and expected['sha256']==actual and expected['bytes']==size),'packages':package_stanzas,
  'release_fields':[line for line in text.splitlines() if line.startswith(('Origin:','Label:','Suite:','Codename:','Date:','Valid-Until:','Architectures:'))]})
catalog=[]
for name in ['libc6:amd64','libc-bin']:
 for suffix in ['md5sums','list']:
  p=Path('/var/lib/dpkg/info')/(name+'.'+suffix)
  if p.exists():
   raw=p.read_bytes();(out/p.name).write_bytes(raw);catalog.append({'path':str(p),'sha256':h(p),'bytes':len(raw)})
installed_members=[]
md5file=Path('/var/lib/dpkg/info/libc6:amd64.md5sums');expected_md5={line.split(None,1)[1].strip():line.split(None,1)[0] for line in md5file.read_text().splitlines()}
for name in ['/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2','/usr/lib/x86_64-linux-gnu/libc.so.6','/usr/lib/x86_64-linux-gnu/libm.so.6']:
 p=Path(name);md5=hashlib.md5(p.read_bytes()).hexdigest();installed_members.append({'path':name,'installed_catalog_md5':expected_md5.get(name.lstrip('/')),'actual_md5':md5,
  'matches_catalog':expected_md5.get(name.lstrip('/'))==md5,'sha256':h(p)})
logs=[]
for p in [Path('/var/log/dpkg.log'),Path('/var/log/apt/history.log'),Path('/var/log/apt/term.log')]:
 if p.exists():
  raw=p.read_bytes();selected=[line for line in raw.decode(errors='replace').splitlines() if any(x in line for x in ['libc6','libc-bin','Start-Date:','End-Date:','Commandline:'])][-120:]
  (out/(p.parent.name+'-'+p.name+'.excerpt.txt')).write_text('\n'.join(selected)+'\n',encoding='utf-8')
  logs.append({'path':str(p),'file_sha256':h(p),'excerpt':selected})
source_files=[]
for p in [Path('/etc/apt/sources.list'),*Path('/etc/apt/sources.list.d').glob('*.sources'),*Path('/etc/apt/sources.list.d').glob('*.list')]:
 if p.is_file():source_files.append({'path':str(p),'sha256':h(p),'text':p.read_text(errors='replace')})
local_candidates=[]
for folder in ['/var/cache/apt/archives','/var/cache/apt/archives/partial','/tmp','/var/tmp']:
 p=Path(folder)
 if p.exists():
  for q in p.glob('*libc*8.12*.deb'):local_candidates.append({'path':str(q),'bytes':q.stat().st_size,'sha256':h(q)})
keyring=Path('/usr/share/keyrings/ubuntu-archive-keyring.gpg');(out/keyring.name).write_bytes(keyring.read_bytes())
print(json.dumps({'status':'OFFLINE_PROVENANCE_AUDIT','repositories':repos,'installed_catalog':catalog,'installed_members':installed_members,
 'keyring':{'path':str(keyring),'sha256':h(keyring),'trust_anchor':'Existing installed ubuntu-keyring2023.11.28.1 under inherited trusted-Root/package-database assumption'},
 'logs':logs,'apt_sources':source_files,'matching_cached_new_debs':local_candidates,'network_queries':0,'downloads':0,'installations':0,
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'observation_boottime':time.clock_gettime(time.CLOCK_BOOTTIME)},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Offline cached Ubuntu InRelease/index and installed glibc member provenance; no downloads or installs','READ_ONLY_OFFLINE_PROVENANCE')
assert r['exit_code']==0,r['stderr']
q=json.loads(r['stdout']);dump(E/'PROVENANCE_AUDIT.json',q)
print(json.dumps({'status':q['status'],'repositories':[{'gpgv_exit':r['gpgv_exit'],'index_matches':r['index_matches_signed_release'],'package_stanzas':len(r['packages'])} for r in q['repositories']],
 'members_match_catalog':all(r['matches_catalog'] for r in q['installed_members']),'cached_new_debs':len(q['matching_cached_new_debs'])},ensure_ascii=False))
