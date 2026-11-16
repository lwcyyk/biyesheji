"""Automatic host post-exit startup evidence seal; never grants runtime authority."""
import hashlib
import json
from pathlib import Path,PurePosixPath
import subprocess
import time
import zipfile
from datetime import datetime,timezone

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def preserved_native_audit(package,control):
    p=control/'STARTUP_NATIVE_AUDIT.json'
    if not p.exists():return None
    audit=json.loads(p.read_bytes());identity=json.loads((package/'inputs/batch_identity.json').read_bytes())
    if (audit.get('batch_id')!=identity['batch_id'] or audit.get('source_revision')!=identity['revision'] or
        audit.get('source_manifest_sha256')!=digest(package/'inputs/static_manifest.json') or
        audit.get('execution_lock_sha256')!=digest(package/'inputs/execution_lock.json') or
        audit.get('authorization_receipt_sha256')!=digest(control/'execution_authorization.json')):raise RuntimeError('PF_ADMIN_AUDIT_BINDING')
    return audit

def frontend_abort(package,error):
    """Host-only failed attempt: never assumes anything about a prior native run."""
    import sys
    import traceback
    package=Path(package);sys.path.insert(0,str(package/'src'))
    import batch_identity as N
    if package.resolve().as_posix()!=N.SPEC['host_package']:raise RuntimeError('PT_FRONTEND_PACKAGE')
    control=Path(N.SPEC['host_control']);control.mkdir(parents=True,exist_ok=True)
    record=control/'FRONTEND_ABORT.json'
    if record.exists():return json.loads(record.read_bytes())
    result={'schema':'PT-FRONTEND-ABORT/1','status':'STARTUP_ABORTED_PRE_BOOTSTRAP','exception':type(error).__name__,
        'error':str(error)[:4096],'native_active_call_started':False,'native_seal_status':'NATIVE_SEAL_NOT_APPLICABLE',
        'process_scope':'This frontend attempt only; no claim about earlier native processes',
        'T0':None,'R':None,'traceback':traceback.format_exc(),'sample_utc':datetime.now(timezone.utc).isoformat()}
    write(record,result);rows=[]
    for p in [record,package/'inputs/static_manifest.json',package/'inputs/execution_lock.json']:
        if p.is_file():rows.append({'host':str(p),'archive_path':p.name,'bytes':p.stat().st_size,'sha256':digest(p)})
    manifest=control/'FRONTEND_ADMIN_MANIFEST.json';write(manifest,{'scope':'Host-only pre-bootstrap failure evidence','files':rows})
    archive=control/'FRONTEND_ADMIN_EVIDENCE.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for row in rows:z.write(row['host'],row['archive_path'])
        z.write(manifest,'FRONTEND_ADMIN_MANIFEST.json')
    with zipfile.ZipFile(archive) as z:
        for row in rows:
            if hashlib.sha256(z.read(row['archive_path'])).hexdigest()!=row['sha256']:raise RuntimeError('PT_FRONTEND_ARCHIVE_HASH')
    receipt={'administrative_seal_status':'ADMIN_EVIDENCE_SEALED','completeness':'Host-only; native not started by this attempt',
        'manifest_sha256':digest(manifest),'ZIP_sha256':digest(archive),'native_seal_status':'NATIVE_SEAL_NOT_APPLICABLE'}
    write(control/'FRONTEND_SEAL_RECEIPT.json',receipt);return receipt

def finalize(package,control,active_exit):
    package=Path(package);control=Path(control);lock=json.loads((package/'inputs/execution_lock.json').read_bytes())
    if digest(__file__)!=lock['startup_host_finalizer_sha256']:raise RuntimeError('PT_HOST_FINALIZER_DRIFT')
    final=control/'STARTUP_FINALIZATION.json'
    if final.exists():
        previous=json.loads(final.read_bytes())
        if (previous.get('administrative_seal_status')=='ADMIN_EVIDENCE_SEALED' and digest(control/'STARTUP_ADMIN_EVIDENCE.zip')==previous['ZIP_sha256'] and
            digest(control/'STARTUP_ADMIN_MANIFEST.json')==previous['manifest_sha256']):
            return previous
        if previous.get('administrative_seal_status')=='NOT_REQUIRED_RUNTIME_NATIVE_SEAL':return previous
        raise RuntimeError('PT_FINALIZATION_EXISTING_UNRESOLVED')
    plan={'argv':lock['startup_post_exit_command'],'active_exit':active_exit,'start_utc':datetime.now(timezone.utc).isoformat(),
          'scope':'Post-exit read-only audit/export; no test, resume, budget or T0 creation'}
    write(control/'STARTUP_POSTEXIT_PLAN.json',plan);tick=time.perf_counter()
    with (control/'STARTUP_POSTEXIT.stdout.raw').open('xb') as out,(control/'STARTUP_POSTEXIT.stderr.raw').open('xb') as err:
        proc=subprocess.Popen(plan['argv'],stdin=subprocess.DEVNULL,stdout=out,stderr=err)
        try:code=proc.wait(timeout=32)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:proc.wait(timeout=max(.001,35-(time.perf_counter()-tick)))
            except subprocess.TimeoutExpired:pass
            code=124
    result={'schema':'PT-HOST-FINALIZATION/1','post_exit_code':code,'active_exit':active_exit,'elapsed_seconds':time.perf_counter()-tick,
            'administrative_seal_status':'ADMIN_EVIDENCE_UNRESOLVED','native_seal_status':'NATIVE_SEAL_UNRESOLVED'}
    if code!=0:
        audit=preserved_native_audit(package,control)
        if audit is not None:result.update(native_seal_status=audit['native_seal_status'],preserved_native_audit=audit)
        error={'schema':'PF-POSTEXIT-FAILURE/1','post_exit_code':code,'active_exit':active_exit,'sample_utc':datetime.now(timezone.utc).isoformat(),
            'stdout_sha256':digest(control/'STARTUP_POSTEXIT.stdout.raw'),'stderr_sha256':digest(control/'STARTUP_POSTEXIT.stderr.raw'),
            'native_seal_status':result['native_seal_status'],'runtime_originals_modified':False,'administrative_seal_status':'ADMIN_EVIDENCE_UNRESOLVED'}
        write(control/'STARTUP_POSTEXIT_FAILURE.json',error)
        write(final,result);return result
    native=json.loads((control/'STARTUP_POSTEXIT.stdout.raw').read_bytes());result['native_audit']=native
    saved=preserved_native_audit(package,control)
    if saved is None or any(saved[k]!=native[k] for k in ('batch_id','source_revision','source_manifest_sha256','execution_lock_sha256','native_seal_status')):
        raise RuntimeError('PF_POSTEXIT_AUDIT_MISMATCH')
    result['native_seal_status']=native['native_seal_status'];result['process_cleanup_status']=native['process_cleanup_status']
    if native['administrative_export_status']!='EXPORTED_QUIESCENT_STARTUP_EVIDENCE':
        write(control/'STARTUP_POSTEXIT_FAILURE.json',{'post_exit_code':code,'reason':native['administrative_export_status'],
            'native_seal_status':native['native_seal_status'],'administrative_seal_status':'ADMIN_EVIDENCE_UNRESOLVED'})
        write(final,result);return result
    rows=[];folder=control/'startup_snapshot'
    cfg=json.loads((package/'inputs/startup_contract.json').read_bytes())
    if len(native['files'])>cfg['admin_max_files'] or sum(row['bytes'] for row in native['files'])>cfg['admin_max_bytes']:raise RuntimeError('PF_HOST_ADMIN_BOUND')
    for row in native['files']:
        rel=PurePosixPath(row['relative'])
        if rel.is_absolute() or '..' in rel.parts or '\\' in row['relative'] or ':' in row['relative']:raise RuntimeError('PF_ADMIN_EXPORT_PATH')
        p=folder/row['relative']
        if digest(p)!=row['sha256']:raise RuntimeError('PT_ADMIN_COPY_HASH')
        rows.append({'host':str(p),'archive_path':'startup/'+row['relative'],'bytes':p.stat().st_size,'sha256':digest(p)})
    for name in ['TASK_REQUEST.txt','execution_authorization.json','WINDOWS_ENTRY_PLAN.json','WINDOWS_ENTRY_EXIT.json',
                 'windows_entry.stdout.raw','windows_entry.stderr.raw','STARTUP_POSTEXIT_PLAN.json','STARTUP_POSTEXIT.stdout.raw','STARTUP_POSTEXIT.stderr.raw','STARTUP_NATIVE_AUDIT.json']:
        p=control/name
        if p.is_file():rows.append({'host':str(p),'archive_path':'host/'+name,'bytes':p.stat().st_size,'sha256':digest(p)})
    for name in ['static_manifest.json','execution_lock.json','batch_identity.json','startup_contract.json']:
        p=package/'inputs'/name;rows.append({'host':str(p),'archive_path':'source_locks/'+name,'bytes':p.stat().st_size,'sha256':digest(p)})
    manifest=control/'STARTUP_ADMIN_MANIFEST.json';write(manifest,{'schema':'PT-ADMIN-MANIFEST/1','files':rows,
        'scope':'Quiescent startup originals plus complete post-exit host streams; no synthetic runtime objects',
        'native_seal_status':native['native_seal_status'],'process_cleanup_status':native['process_cleanup_status']})
    archive=control/'STARTUP_ADMIN_EVIDENCE.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for row in rows:z.write(row['host'],row['archive_path'])
        z.write(manifest,'STARTUP_ADMIN_MANIFEST.json')
    with zipfile.ZipFile(archive) as z:
        for row in rows:
            if hashlib.sha256(z.read(row['archive_path'])).hexdigest()!=row['sha256']:raise RuntimeError('PT_ADMIN_ZIP_HASH')
    result.update(administrative_seal_status='ADMIN_EVIDENCE_SEALED',manifest_sha256=digest(manifest),ZIP_sha256=digest(archive),
        ZIP_bytes=archive.stat().st_size,files=len(rows),sealed_utc=datetime.now(timezone.utc).isoformat())
    write(final,result);return result
