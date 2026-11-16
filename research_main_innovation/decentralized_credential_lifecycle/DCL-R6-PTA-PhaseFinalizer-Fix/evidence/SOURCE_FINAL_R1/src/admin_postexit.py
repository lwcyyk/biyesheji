"""PF administrative entry: stdlib-only bootstrap, fixed source, no runtime grants."""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import stat
import sys

def checked_source():
    source=Path(__file__).resolve().parent
    if sys.platform!='linux' or os.geteuid()!=0 or source!=Path('/var/lib/dcl-r6/pf01/src'):
        raise RuntimeError('PF_ADMIN_FIXED_ROOT_SOURCE')
    if not (sys.version_info[:3]==(3,12,3) and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
        raise RuntimeError('PF_ADMIN_INTERPRETER')
    for p in [source.parent,source,source.parent/'inputs']:
        s=p.lstat()
        if not stat.S_ISDIR(s.st_mode) or s.st_uid!=0 or s.st_mode&0o022 or any(k.startswith('system.posix_acl_') for k in os.listxattr(p,follow_symlinks=False)):
            raise RuntimeError('PF_ADMIN_SOURCE_DIRECTORY')
    def read(p):
        fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            s=os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_uid!=0 or s.st_mode&0o022 or s.st_nlink!=1 or s.st_size>4194304:
                raise RuntimeError('PF_ADMIN_SOURCE_FILE')
            raw=os.read(fd,s.st_size+1)
            if len(raw)!=s.st_size:raise RuntimeError('PF_ADMIN_SHORT_READ')
            return raw
        finally:os.close(fd)
    manifest_raw=read(source.parent/'inputs/static_manifest.json');manifest=json.loads(manifest_raw)
    lock=json.loads(read(source.parent/'inputs/execution_lock.json'))
    if hashlib.sha256(manifest_raw).hexdigest()!=lock['static_manifest_sha256']:raise RuntimeError('PF_ADMIN_MANIFEST_BINDING')
    for name,expected in manifest['source_hashes'].items():
        if Path(name).name!=name or hashlib.sha256(read(source/name)).hexdigest()!=expected:raise RuntimeError('PF_ADMIN_SOURCE_DIGEST')
    return source

def load_target(source):
    # No environment/PYTHONPATH/cwd lookup can precede the checked fixed source.
    sys.path.insert(0,str(source))
    target=importlib.import_module('startup_lifecycle')
    if Path(target.__file__).resolve()!=source/'startup_lifecycle.py':raise RuntimeError('PF_ADMIN_MODULE_ORIGIN')
    return target

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--post-exit-export',action='store_true',required=True);parser.parse_args()
    source=checked_source()
    load_target(source).post_exit_export()

if __name__=='__main__':main()
