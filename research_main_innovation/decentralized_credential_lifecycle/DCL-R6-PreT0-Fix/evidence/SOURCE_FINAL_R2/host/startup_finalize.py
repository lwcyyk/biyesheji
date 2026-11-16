"""Automatic host post-exit startup evidence seal; never grants runtime authority."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
import zipfile
from datetime import datetime,timezone

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def finalize(package,control,active_exit):
    package=Path(package);control=Path(control);lock=json.loads((package/'inputs/execution_lock.json').read_bytes())
    if digest(__file__)!=lock['startup_host_finalizer_sha256']:raise RuntimeError('PT_HOST_FINALIZER_DRIFT')
    final=control/'STARTUP_FINALIZATION.json'
    if final.exists():
        previous=json.loads(final.read_bytes())
        if previous.get('administrative_seal_status')=='ADMIN_EVIDENCE_SEALED' and digest(control/'STARTUP_ADMIN_EVIDENCE.zip')==previous['ZIP_sha256']:
            return previous
        if previous.get('administrative_seal_status')=='NOT_REQUIRED_RUNTIME_NATIVE_SEAL':return previous
        raise RuntimeError('PT_FINALIZATION_EXISTING_UNRESOLVED')
    plan={'argv':lock['startup_post_exit_command'],'active_exit':active_exit,'start_utc':datetime.now(timezone.utc).isoformat(),
          'scope':'Post-exit read-only audit/export; no test, resume, budget or T0 creation'}
    write(control/'STARTUP_POSTEXIT_PLAN.json',plan);tick=time.perf_counter()
    with (control/'STARTUP_POSTEXIT.stdout.raw').open('xb') as out,(control/'STARTUP_POSTEXIT.stderr.raw').open('xb') as err:
        proc=subprocess.Popen(plan['argv'],stdin=subprocess.DEVNULL,stdout=out,stderr=err)
        try:code=proc.wait(timeout=35)
        except subprocess.TimeoutExpired:
            proc.terminate();code=124
    result={'schema':'PT-HOST-FINALIZATION/1','post_exit_code':code,'active_exit':active_exit,'elapsed_seconds':time.perf_counter()-tick,
            'administrative_seal_status':'ADMIN_EVIDENCE_UNRESOLVED','native_seal_status':'NATIVE_SEAL_UNRESOLVED'}
    if code!=0:
        write(final,result);return result
    native=json.loads((control/'STARTUP_POSTEXIT.stdout.raw').read_bytes());result['native_audit']=native
    result['native_seal_status']=native['native_seal_status'];result['process_cleanup_status']=native['process_cleanup_status']
    if native['administrative_export_status']=='NOT_REQUIRED_RUNTIME_NATIVE_SEAL':
        result['administrative_seal_status']='NOT_REQUIRED_RUNTIME_NATIVE_SEAL';write(final,result);return result
    if native['administrative_export_status']!='EXPORTED_QUIESCENT_STARTUP_EVIDENCE':write(final,result);return result
    rows=[];folder=control/'startup_snapshot'
    for row in native['files']:
        p=folder/row['relative']
        if digest(p)!=row['sha256']:raise RuntimeError('PT_ADMIN_COPY_HASH')
        rows.append({'host':str(p),'archive_path':'startup/'+row['relative'],'bytes':p.stat().st_size,'sha256':digest(p)})
    for name in ['TASK_REQUEST.txt','execution_authorization.json','WINDOWS_ENTRY_PLAN.json','WINDOWS_ENTRY_EXIT.json',
                 'windows_entry.stdout.raw','windows_entry.stderr.raw','STARTUP_POSTEXIT_PLAN.json','STARTUP_POSTEXIT.stdout.raw','STARTUP_POSTEXIT.stderr.raw']:
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
