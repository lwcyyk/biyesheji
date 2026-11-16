"""Conventional bounded ZIP/manifest checks. Review component; no runtime hook.

Capacity is supplied by an explicitly selected contract. This module never
raises a contract limit or extracts an archive to the filesystem.
"""
import hashlib
import json
from pathlib import PurePosixPath
import stat
import struct
import unicodedata
import zipfile

class Rejected(ValueError):pass

def path_key(name):
    if (not isinstance(name,str) or not name or len(name.encode('utf-8'))>1024 or
        '\\' in name or ':' in name or '\x00' in name or name.startswith('/') or
        any(x in ('','.','..') for x in name.split('/')) or
        unicodedata.normalize('NFC',name)!=name):raise Rejected('PATH')
    if PurePosixPath(name).is_absolute():raise Rejected('PATH')
    return name

def bounded_directory(path,max_members):
    """Reject oversized classic ZIP metadata before ZipFile allocates its index."""
    if type(max_members) is not int or not 1<=max_members<=65534:raise Rejected('CONTRACT_COUNT')
    with open(path,'rb') as f:
        f.seek(0,2);size=f.tell()
        if not 22<=size<=33554432:raise Rejected('COMPRESSED_BYTES')
        f.seek(size-22);raw=f.read(22)
        if raw[:4]!=b'PK\x05\x06':raise Rejected('PARTIAL_OR_COMMENTED_ZIP')
        _,disk,start,n_disk,n,size_cd,offset,comment=struct.unpack('<4s4H2LH',raw)
        if disk or start or n_disk!=n or comment or n>max_members:raise Rejected('MEMBER_COUNT')
        if n==65535 or size_cd==0xffffffff or offset==0xffffffff:raise Rejected('ZIP64')
        if size_cd>n*(46+1024+256+256) or offset+size_cd!=size-22:raise Rejected('CENTRAL_DIRECTORY_BOUND')
        return n

def verify(path,manifest_raw,max_members,manifest_name='out/EVIDENCE_MANIFEST.json',expected_binding=None):
    count=bounded_directory(path,max_members)
    if len(manifest_raw)>4194304:raise Rejected('MANIFEST_BYTES')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise Rejected('DUPLICATE_MANIFEST_KEY')
            result[k]=v
        return result
    m=json.loads(manifest_raw,object_pairs_hook=pairs)
    if expected_binding is not None and m.get('binding')!=expected_binding:raise Rejected('BINDING')
    declared=m['files']
    if isinstance(declared,list):
        names=[r['archive_path'] for r in declared]
        if len(names)!=len(set(names)):raise Rejected('DUPLICATE_MANIFEST_PATH')
        declared={r['archive_path']:{'bytes':r['bytes'],'sha256':r['sha256']} for r in declared}
    if not isinstance(declared,dict):raise Rejected('MANIFEST_SHAPE')
    path_key(manifest_name)
    for name,row in declared.items():
        path_key(name)
        if (not isinstance(row,dict) or type(row.get('bytes')) is not int or
            not 0<=row['bytes']<=33554432 or not isinstance(row.get('sha256'),str) or
            len(row['sha256'])!=64 or any(c not in '0123456789abcdef' for c in row['sha256'])):raise Rejected('MANIFEST_ROW')
    if manifest_name in declared:raise Rejected('MANIFEST_SELF_CYCLE')
    names=set(declared)|{manifest_name}
    if len(names)>max_members:raise Rejected('MEMBER_COUNT')
    total=len(manifest_raw)+sum(r['bytes'] for r in declared.values())
    if total>33554432:raise Rejected('UNCOMPRESSED_BYTES')
    with zipfile.ZipFile(path) as z:
        infos=z.infolist()
        if len(infos)!=count or len({i.filename for i in infos})!=len(infos):raise Rejected('DUPLICATE_MEMBER')
        if {i.filename for i in infos}!=names:raise Rejected('MEMBER_SET')
        actual_total=0
        for i in infos:
            path_key(i.filename)
            mode=i.external_attr>>16
            if (stat.S_IFMT(mode) not in (0,stat.S_IFREG) or i.is_dir() or
                i.flag_bits&1 or i.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED) or
                len(i.extra)>256 or len(i.comment)>256):raise Rejected('MEMBER_TYPE_OR_COMPRESSION')
            row=declared.get(i.filename)
            expected_size=len(manifest_raw) if row is None else row['bytes']
            if row is not None and 'mode' in row and stat.S_IMODE(mode)!=row['mode']:raise Rejected('MEMBER_PERMISSION')
            if i.file_size!=expected_size:raise Rejected('MEMBER_SIZE')
            digest=hashlib.sha256();size=0
            with z.open(i) as item:
                while True:
                    chunk=item.read(65536)
                    if not chunk:break
                    size+=len(chunk);actual_total+=len(chunk)
                    if size>expected_size or actual_total>33554432:raise Rejected('STREAM_BYTES')
                    digest.update(chunk)
            expected_hash=hashlib.sha256(manifest_raw).hexdigest() if row is None else row['sha256']
            if size!=expected_size or digest.hexdigest()!=expected_hash:raise Rejected('CONTENT_HASH')
    return {'members':count,'bytes':actual_total,'verified_files':len(declared),'status':'ACCEPT_ARCHIVE_ONLY'}
