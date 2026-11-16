"""RA/1 explicit runtime identity; never updates a lock, budget or service."""
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
import time
import batch_identity as N

def policy(f):
    if f['silent_relock']:return 'DENY_SILENT_RELOCK'
    if not all(f[k] for k in ('digests','paths','build_ids','packages','symbols','preload_absent','read_ok','fresh','batch_binding')):return 'DENY_RUNTIME_IDENTITY'
    if f['purpose']=='WORK' and f['closed']:return 'DENY_CLOSED_WORK'
    return 'IDENTITY_MATCH'

def _now():return time.clock_gettime(time.CLOCK_BOOTTIME)
def _bound(until,epoch):
    if _now()>=until or Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=epoch:raise RuntimeError('RA_BOOT_OR_READ_BOUND')

def _root_bytes(p,maximum):
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_uid!=0 or s.st_mode&0o022 or s.st_nlink!=1 or s.st_size>maximum:raise RuntimeError('RA_UNTRUSTED_FILE')
        raw=os.read(fd,maximum+1)
        if len(raw)!=s.st_size:raise RuntimeError('RA_FILE_READ_BOUND')
        return raw
    finally:os.close(fd)

def _build_id(raw):
    if raw[:6]!=b'\x7fELF\x02\x01':raise RuntimeError('RA_ELF64_LE_REQUIRED')
    h=struct.unpack_from('<16sHHIQQQIHHHHHH',raw)
    if h[2]!=62:raise RuntimeError('RA_ELF_MACHINE')
    for i in range(h[10]):
        kind,flags,offset,vaddr,paddr,filesz,memsz,align=struct.unpack_from('<IIQQQQQQ',raw,h[5]+i*h[9])
        if kind!=4:continue
        data=raw[offset:offset+filesz];pos=0
        while pos+12<=len(data):
            namesz,descsz,typeid=struct.unpack_from('<III',data,pos);name=data[pos+12:pos+12+namesz];start=pos+12+((namesz+3)//4)*4
            if typeid==3 and name.rstrip(b'\0')==b'GNU':return data[start:start+descsz].hex()
            pos=start+((descsz+3)//4)*4
    raise RuntimeError('RA_BUILD_ID_MISSING')

def _packages(spec):
    text=_root_bytes(Path('/var/lib/dpkg/status'),16777216).decode();found={}
    for stanza in text.split('\n\n'):
        fields={line.split(': ',1)[0]:line.split(': ',1)[1] for line in stanza.splitlines() if ': ' in line and not line[0].isspace()}
        if fields.get('Package') in spec['packages']:found[fields['Package']]={k:fields.get(k) for k in ['Package','Status','Version','Architecture']}
    for name,expected in spec['packages'].items():
        if found.get(name)!={'Package':name,'Status':'install ok installed','Version':expected['version'],'Architecture':expected['architecture']}:raise RuntimeError('RA_PACKAGE_IDENTITY:'+name)
    for row in spec['installed_catalogs']:
        if hashlib.sha256(_root_bytes(Path(row['path']),4194304)).hexdigest()!=row['sha256']:raise RuntimeError('RA_PACKAGE_CATALOG')
    return found

def verify(source,*,full=True,packages=True,deadline=None,epoch=None):
    source=Path(source).resolve();identity=N.load(source.parent)
    if source!=Path(__file__).resolve().parent or str(source)!=identity['source_root']+'/src':raise RuntimeError('RA_SOURCE_NAMESPACE')
    begun=_now();until=min(begun+5,deadline) if deadline is not None else begun+5
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip();epoch=boot if epoch is None else epoch;_bound(until,epoch)
    m=json.loads(_root_bytes(source.parent/'inputs/static_manifest.json',4194304));raw=_root_bytes(source.parent/'inputs/runtime_identity_contract.json',4194304)
    if hashlib.sha256(raw).hexdigest()!=m['runtime_identity_contract_sha256']:raise RuntimeError('RA_CONTRACT_DIGEST')
    spec=json.loads(raw)
    if spec['profile']!='GLIBC-UBU24-2.39-8.12/1' or spec['batch_id']!=identity['batch_id'] or spec['source_revision']!=identity['revision']:raise RuntimeError('RA_CONTRACT_IDENTITY')
    if any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LD_AUDIT']) or Path('/etc/ld.so.preload').exists():raise RuntimeError('RA_LOADER_OVERRIDE')
    for alias in spec['aliases']:
        p=Path(alias['path'])
        if str(p.resolve())!=alias['resolved'] or p.is_symlink()!=alias['is_symlink'] or (os.readlink(p) if p.is_symlink() else None)!=alias['link_text']:raise RuntimeError('RA_ALIAS_IDENTITY')
    components=[]
    for row in spec['components']:
        _bound(until,epoch);p=Path(row['path'])
        if p.is_symlink() or str(p.resolve())!=row['resolved']:raise RuntimeError('RA_COMPONENT_PATH')
        fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            s=os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_size)!=(0,0,row['mode'],row['bytes']):raise RuntimeError('RA_COMPONENT_METADATA')
            if full:
                raw=os.pread(fd,row['bytes']+1,0)
                if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256'] or _build_id(raw)!=row['build_id']:raise RuntimeError('RA_COMPONENT_DIGEST_OR_BUILD_ID')
            after=os.stat(p,follow_symlinks=False)
            if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns):raise RuntimeError('RA_COMPONENT_CHANGED_DURING_READ')
            components.append({'path':str(p),'sha256':row['sha256'],'build_id':row['build_id'],'device':s.st_dev,'inode':s.st_ino})
        finally:os.close(fd)
    found=_packages(spec) if packages else None
    if full or packages:
        for row in spec['loader_configuration']:
            if hashlib.sha256(_root_bytes(Path(row['path']),4194304)).hexdigest()!=row['sha256']:raise RuntimeError('RA_LOADER_CONFIGURATION')
    maps=Path('/proc/self/maps').read_text();matches=[]
    for row in components:
        lines=[line.split(maxsplit=5) for line in maps.splitlines() if len(line.split(maxsplit=5))==6 and Path(line.split(maxsplit=5)[5].removesuffix(' (deleted)')).name==Path(row['path']).name]
        if not lines:raise RuntimeError('RA_COMPONENT_NOT_LOADED')
        for parts in lines:
            major,minor=(int(x,16) for x in parts[3].split(':'))
            if parts[5].endswith(' (deleted)') or str(Path(parts[5]).resolve())!=row['path'] or int(parts[4])!=row['inode'] or (major,minor)!=(os.major(row['device']),os.minor(row['device'])):raise RuntimeError('RA_LOADED_OBJECT_MISMATCH')
        matches.append({'path':row['path'],'segments':len(lines),'disk_and_loaded_object_match':True})
    _bound(until,epoch)
    decision=policy({'silent_relock':False,'digests':True,'paths':True,'build_ids':True,'packages':True,'symbols':True,
        'preload_absent':True,'read_ok':True,'fresh':True,'batch_binding':True,'purpose':'IDENTITY_ONLY','closed':False})
    if decision!='IDENTITY_MATCH':raise RuntimeError('RA_IDENTITY_POLICY')
    return {'schema':'RUNTIME-IDENTITY/1','profile':spec['profile'],'package_revision':'2.39-0ubuntu8.12','components':components,'packages':found,
        'loaded_mapping_checks':matches,'boot_id':boot,'pid':os.getpid(),'sample_boottime':_now(),'elapsed_seconds':_now()-begun,
        'verification_scope':'full bytes/build-id/packages/maps' if full and packages else 'disk path/metadata and own mappings; caller separately verifies pinned bytes',
        'runtime_authority':'NONE','remaining_boundary':'No atomic filesystem-to-exec or protection from privileged updates after the final check'}
