"""Resource-gate ledger snapshot checks. No producer or budget mutation API."""
import hashlib
import os
from pathlib import Path
import stat
import range_evidence as R

NAMES={'counter':'visits.bin','intent':'visits.bin.intent.json','journal':'visits.bin.journal.jsonl'}
MAX_BYTES={'counter':24,'intent':65536,'journal':200000*16384}
PROFILE='GATE-LEDGER-SNAPSHOT/1'

class LedgerRejected(RuntimeError):pass

def metadata(path,role):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size>MAX_BYTES[role]:
            raise LedgerRejected('GATE_LEDGER_FILE_BOUND')
        digest=hashlib.sha256();size=0
        while True:
            block=os.read(fd,65536)
            if not block:break
            digest.update(block);size+=len(block)
        after=os.fstat(fd)
        if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns) or size!=after.st_size:
            raise LedgerRejected('GATE_LEDGER_SNAPSHOT_CHANGED')
        return {'name':NAMES[role],'bytes':size,'sha256':digest.hexdigest()}
    finally:os.close(fd)

def capture(base,cap,binding):
    base=Path(base)
    return {'schema':PROFILE,'binding':dict(binding),'cap':cap,
            'files':{role:metadata(base/name,role) for role,name in NAMES.items()}}

def evaluate(base,descriptor,cap,binding):
    """Identical real-gate and synthetic-subject acceptance predicate."""
    try:
        base=Path(base)
        if base.is_symlink():raise LedgerRejected('GATE_LEDGER_BASE_SYMLINK')
        if descriptor.get('schema')!=PROFILE or descriptor.get('binding')!=binding or descriptor.get('cap')!=cap:
            raise LedgerRejected('GATE_LEDGER_BINDING')
        if set(descriptor.get('files',{}))!=set(NAMES):raise LedgerRejected('GATE_LEDGER_FILE_SET')
        for role,name in NAMES.items():
            expected=descriptor['files'][role]
            if set(expected)!={'name','bytes','sha256'} or expected['name']!=name:
                raise LedgerRejected('GATE_LEDGER_FOREIGN_PATH')
            if metadata(base/name,role)!=expected:raise LedgerRejected('GATE_LEDGER_DIGEST')
        health=R.check_global_ledger(base/NAMES['counter'],cap,binding)
        for role,name in NAMES.items():
            if metadata(base/name,role)!=descriptor['files'][role]:raise LedgerRejected('GATE_LEDGER_SNAPSHOT_CHANGED')
        return {'decision':'ACCEPT_LEDGER_HEALTHY','reason':None,'health':health,'descriptor':descriptor}
    except (LedgerRejected,R.EvidenceError,OSError,ValueError,KeyError,TypeError) as exc:
        return {'decision':'REJECT_LEDGER_ANOMALY','reason':str(exc),'exception_type':type(exc).__name__}

def require_current(G,binding):
    G.root_checkpoint();G.execution_deadline('FORMAL' if G._TICKET and G._TICKET['case']=='FORMAL' else 'RANGE')
    base=G.OUT
    if base != G.ROOT/'out' or G.ROOT.name!='batch10':raise G.AdmissionBlocked('GATE_LEDGER_CURRENT_ROOT')
    try:descriptor=capture(base,G.VISIT_CAP,binding)
    except (LedgerRejected,R.EvidenceError,OSError,ValueError,KeyError,TypeError) as exc:
        raise G.AdmissionBlocked('REJECT_LEDGER_ANOMALY:'+str(exc)) from exc
    result=evaluate(base,descriptor,G.VISIT_CAP,binding)
    if result['decision']!='ACCEPT_LEDGER_HEALTHY':raise G.AdmissionBlocked('REJECT_LEDGER_ANOMALY:'+result['reason'])
    return {**result['health'],'snapshot':descriptor}
