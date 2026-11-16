"""Read-only ELF parsing and dependency/version resolution; never executes target ELF."""
from EXEC_ADMIN import call,dump,E
import json
CODE=r'''
from pathlib import Path
import hashlib,json,os,re,resource,signal,struct,subprocess,sys,time
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30));signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(45)
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-RuntimeAdapt-Fix/evidence');out=e/'elf_raw';out.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def elf(p):
 raw=Path(p).read_bytes()
 if raw[:6]!=b'\x7fELF\x02\x01':raise ValueError('ELF64_LE_REQUIRED:'+str(p))
 header=struct.unpack_from('<16sHHIQQQIHHHHHH',raw);shoff=header[6];entsize=header[11];count=header[12];strings=header[13]
 sections=[struct.unpack_from('<IIQQQQIIQQ',raw,shoff+i*entsize) for i in range(count)]
 def section(i):s=sections[i];return raw[s[4]:s[4]+s[5]]
 def word(blob,offset):return blob[offset:blob.index(b'\0',offset)].decode(errors='strict')
 names=section(strings);table={word(names,s[0]):(i,s) for i,s in enumerate(sections)}
 needed=[];runpath=[];rpath=[];soname=None;requirements={};definitions=set();buildid=None;interpreter=None
 if '.dynamic' in table:
  i,s=table['.dynamic'];data=section(i);ds=section(s[6])
  for j in range(0,len(data),16):
   tag,value=struct.unpack_from('<qQ',data,j)
   if tag==1:needed.append(word(ds,value))
   elif tag==14:soname=word(ds,value)
   elif tag==15:rpath=word(ds,value).split(':')
   elif tag==29:runpath=word(ds,value).split(':')
 if '.gnu.version_r' in table:
  i,s=table['.gnu.version_r'];data=section(i);ds=section(s[6]);offset=0
  while offset<len(data):
   version,num,file,aux,nxt=struct.unpack_from('<HHIII',data,offset);name=word(ds,file);a=offset+aux;required=[]
   for j in range(num):
    _,flags,other,text,nextaux=struct.unpack_from('<IHHII',data,a);required.append(word(ds,text))
    if not nextaux:break
    a+=nextaux
   requirements[name]=required
   if not nxt:break
   offset+=nxt
 if '.gnu.version_d' in table:
  i,s=table['.gnu.version_d'];data=section(i);ds=section(s[6]);offset=0
  while offset<len(data):
   version,flags,index,num,h,aux,nxt=struct.unpack_from('<HHHHIII',data,offset);name,_=struct.unpack_from('<II',data,offset+aux);definitions.add(word(ds,name))
   if not nxt:break
   offset+=nxt
 if '.note.gnu.build-id' in table:
  i,_=table['.note.gnu.build-id'];data=section(i);namesz,descsz,typeid=struct.unpack_from('<III',data);start=12+((namesz+3)//4)*4;buildid=data[start:start+descsz].hex()
 for i,s in enumerate(sections):
  if s[1]==7 and buildid is None:
   data=section(i);pos=0
   while pos+12<=len(data):
    ns,ds,ty=struct.unpack_from('<III',data,pos);name=data[pos+12:pos+12+ns];start=pos+12+((ns+3)//4)*4
    if ty==3 and name.rstrip(b'\0')==b'GNU':buildid=data[start:start+ds].hex()
    pos=start+((ds+3)//4)*4
 phoff=header[5];phsize=header[9];phnum=header[10]
 for i in range(phnum):
  kind,flags,off,vaddr,paddr,filesz,memsz,align=struct.unpack_from('<IIQQQQQQ',raw,phoff+i*phsize)
  if kind==3:interpreter=raw[off:off+filesz].rstrip(b'\0').decode()
 return {'path':str(Path(p).resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'ELF_Class':'ELF64','Machine':header[2],
  'build_id':buildid,'soname':soname,'interpreter':interpreter,'needed':needed,'rpath':rpath,'runpath':runpath,
  'version_requirements':requirements,'version_definitions':sorted(definitions)}
m=json.loads(Path('/var/lib/dcl-r6/tr01/inputs/static_manifest.json').read_bytes());tree=json.loads(Path('/var/lib/dcl-r6/tr01/inputs/runtime_tree_lock.json').read_bytes())
frozen=set(m['runtime_files'])|set(tree['files']);seeds=[]
for name in sorted(frozen):
 with Path(name).open('rb') as f:magic=f.read(4)
 if magic==b'\x7fELF':seeds.append(str(Path(name).resolve()))
q=subprocess.run(['/usr/sbin/ldconfig','-p'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
(out/'ldconfig-cache.stdout.raw').write_bytes(q.stdout);(out/'ldconfig-cache.stderr.raw').write_bytes(q.stderr)
cache={}
for line in q.stdout.decode().splitlines():
 match=re.match(r'\s*(\S+)\s+\(([^)]+)\)\s+=>\s+(\S+)',line)
 if match and 'x86-64' in match[2]:cache.setdefault(match[1],[]).append(match[3])
objects={};queue=list(seeds);edges=[];unresolved=[]
while queue:
 name=queue.pop();name=str(Path(name).resolve())
 if name in objects:continue
 obj=elf(name);objects[name]=obj
 search=[s.replace('${ORIGIN}',str(Path(name).parent)).replace('$ORIGIN',str(Path(name).parent)) for s in (obj['runpath'] or obj['rpath'])]
 for needed in obj['needed']:
  choices=[str(Path(folder)/needed) for folder in search if folder]+cache.get(needed,[])
  path=next((str(Path(x).resolve()) for x in choices if Path(x).is_file()),None)
  edges.append({'consumer':name,'needed':needed,'provider':path,'resolution':'static RPATH/RUNPATH then native cache; LD env/preload absent in observed query'})
  if path:queue.append(path)
  else:unresolved.append({'consumer':name,'needed':needed})
version_missing=[];version_checks=[]
for name,obj in objects.items():
 for library,required in obj['version_requirements'].items():
  edge=next((x for x in edges if x['consumer']==name and x['needed']==library),None)
  provider=edge['provider'] if edge else next((p for p,o in objects.items() if o['soname']==library),None)
  defined=set(objects[provider]['version_definitions']) if provider in objects else set();missing=sorted(set(required)-defined)
  row={'consumer':name,'library':library,'provider':provider,'required':required,'missing':missing};version_checks.append(row)
  if missing:version_missing.append(row)
three=['/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2','/usr/lib/x86_64-linux-gnu/libc.so.6','/usr/lib/x86_64-linux-gnu/libm.so.6']
raw_queries=[]
for i,path in enumerate(three+['/usr/bin/python3.12']):
 for flag in ['-h','-n','-d','-V','-l']:
  argv=['/usr/bin/readelf',flag,path];r=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
  filename='%02d-%s'%(i,flag.lstrip('-'));(out/(filename+'.stdout.raw')).write_bytes(r.stdout);(out/(filename+'.stderr.raw')).write_bytes(r.stderr)
  raw_queries.append({'argv':argv,'exit_code':r.returncode,'stdout_file':'elf_raw/'+filename+'.stdout.raw','stderr_file':'elf_raw/'+filename+'.stderr.raw'})
maps=[]
for line in Path('/proc/self/maps').read_text().splitlines():
 parts=line.split(maxsplit=5)
 if len(parts)==6 and any(Path(parts[5]).name==Path(p).name for p in three):
  p=Path(parts[5]);s=p.stat();major,minor=map(lambda x:int(x,16),parts[3].split(':'))
  maps.append({'raw':line,'resolved':str(p.resolve()),'map_inode':int(parts[4]),'disk_inode':s.st_ino,'map_device':[major,minor],
   'disk_device':[os.major(s.st_dev),os.minor(s.st_dev)],'same_live_object':int(parts[4])==s.st_ino and (major,minor)==(os.major(s.st_dev),os.minor(s.st_dev))})
resource_symbols=['setrlimit','getrlimit','prlimit','prlimit64','clock_gettime','flock','fsync','open','pread64','pwrite64','waitpid','syscall']
r=subprocess.run(['/usr/bin/readelf','--dyn-syms','--wide',three[1]],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
(out/'libc-dynamic-symbols.stdout.raw').write_bytes(r.stdout)
symbols=r.stdout.decode();symbol_presence={name:bool(re.search(r'\b'+re.escape(name)+r'(?:@|\s|$)',symbols)) for name in resource_symbols}
print(json.dumps({'status':'READ_ONLY_STATIC_ELF_ABI','frozen_ELF_seed_count':len(set(seeds)),'resolved_ELF_objects':len(objects),'dependency_edges':edges,
 'objects':objects,'unresolved_needed':unresolved,'version_checks':version_checks,'missing_versions':version_missing,
 'three_components':{p:objects[str(Path(p).resolve())] for p in three},'python':objects[str(Path('/usr/bin/python3.12').resolve())],
 'raw_queries':raw_queries,'observed_python_mappings':maps,'resource_symbol_presence':symbol_presence,
 'static_resolution_caveat':'No target ELF executed; environment/cache/path and exported version sets establish static necessary conditions, not relocation/runtime behavior or race-free future mapping identity',
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'observation_boottime':time.clock_gettime(time.CLOCK_BOOTTIME),'business_test_runs':0},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Read-only ELF headers/build IDs/needed-version closure for all frozen ELF seeds and current providers','READ_ONLY_STATIC_ELF_ABI')
assert r['exit_code']==0,r['stderr']
q=json.loads(r['stdout']);dump(E/'ELF_ABI_AUDIT.json',q)
print(json.dumps({'status':q['status'],'seed_ELFs':q['frozen_ELF_seed_count'],'resolved_objects':q['resolved_ELF_objects'],
 'unresolved_needed':len(q['unresolved_needed']),'missing_version_groups':len(q['missing_versions']),
 'python_interpreter':q['python']['interpreter'],'resource_symbols':q['resource_symbol_presence'],'live_mapping_objects_match':all(x['same_live_object'] for x in q['observed_python_mappings'])},ensure_ascii=False))
