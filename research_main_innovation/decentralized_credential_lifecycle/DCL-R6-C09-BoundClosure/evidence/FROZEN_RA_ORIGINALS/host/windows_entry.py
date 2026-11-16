"""Future authorized entry. One foreground WSL invocation; no diagnostics or retry."""
import argparse
from pathlib import Path
import hashlib
import json
import subprocess
from datetime import datetime,timezone
import time
import sys
_ACTIVE_CALL_STARTED=False


def main():
    global _ACTIVE_CALL_STARTED
    p=argparse.ArgumentParser();p.add_argument('--activate',action='store_true',required=True);p.parse_args()
    package=Path(__file__).resolve().parents[1]
    lock=json.loads((package/'inputs/execution_lock.json').read_text(encoding='utf-8'))
    sys.path.insert(0,str(package/'src'))
    import batch_identity as N
    identity=N.load(package)
    receipt_path=Path(identity['host_control'])/identity['authorization_filename']
    auth=json.loads(receipt_path.read_text(encoding='utf-8'))
    h=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
    text_path=receipt_path.parent/identity['operator_text_filename']
    if (auth.get('batch_id')!=identity['batch_id'] or auth.get('static_revision')!=identity['revision'] or
        auth.get('batch_identity_sha256')!=h(package/'inputs/batch_identity.json') or
        auth.get('scope') not in lock['allowed_scopes'] or auth.get('authorization_text_sha256')!=h(text_path)):
        raise SystemExit('MR_HOST_AUTHORIZATION_BINDING')
    if auth['execution_lock_sha256']!=h(package/'inputs/execution_lock.json') or auth['static_manifest_sha256']!=h(package/'inputs/static_manifest.json'):raise SystemExit('AUTHORIZATION_HASH_MISMATCH')
    if auth.get('SingleSession_exec_explicitly_approved') is not True or lock['windows_entry_sha256']!=h(Path(__file__)):raise SystemExit('ENTRY_NOT_APPROVED')
    if auth.get('phase_finalizer_contract_sha256')!=h(package/'inputs/phase_finalizer_contract.json'):raise SystemExit('PF_CONTRACT_BINDING')
    if auth['scope']=='PT_STARTUP_DIAGNOSTIC_ONLY' and auth.get('PhaseFinalizer_diagnostic_explicitly_approved') is not True:raise SystemExit('PF_SCOPE_NOT_APPROVED')
    for rel,expected in json.loads((package/'inputs/static_manifest.json').read_text())['source_hashes'].items():
        if h(package/'src'/rel)!=expected:raise SystemExit('SOURCE_DRIFT')
    out=receipt_path.parent/'windows_entry.stdout.raw';err=receipt_path.parent/'windows_entry.stderr.raw'
    begun=datetime.now(timezone.utc).isoformat();tick=time.perf_counter_ns()
    plan={'argv':lock['windows_single_call'],'status':'REQUESTED_ONLY','source_mode':'SOURCE_ONLY/1','start_utc':begun}
    (receipt_path.parent/'WINDOWS_ENTRY_PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
    with out.open('xb') as stdout,err.open('xb') as stderr:
        process=subprocess.Popen(lock['windows_single_call'],stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
        _ACTIVE_CALL_STARTED=True
        code=process.wait()
    # Exit status is process evidence; resource qualification still needs native receipts.
    (receipt_path.parent/'WINDOWS_ENTRY_EXIT.json').write_text(json.dumps({'exit_code':code,'wsl_client_pid':process.pid,
        'start_utc':begun,'end_utc':datetime.now(timezone.utc).isoformat(),'host_elapsed_ns':time.perf_counter_ns()-tick,
        'resource_gate':'REQUIRES_NATIVE_EVIDENCE'}),encoding='utf-8')
    try:
        sys.path.insert(0,str(package/'host'))
        from startup_finalize import finalize
        finalize(package,receipt_path.parent,code)
    except BaseException as exc:
        detail={'administrative_seal_status':'ADMIN_EVIDENCE_UNRESOLVED','error':repr(exc),'original_exit_code':code,'native_seal_status':'NATIVE_SEAL_UNRESOLVED'}
        try:
            from startup_finalize import preserved_native_audit
            audit=preserved_native_audit(package,receipt_path.parent)
            if audit is not None:detail.update(native_seal_status=audit['native_seal_status'],preserved_native_audit=audit)
        except BaseException as audit_error:detail['audit_error']=repr(audit_error)
        (receipt_path.parent/'STARTUP_FINALIZATION_ERROR.json').write_text(json.dumps(detail,ensure_ascii=False),encoding='utf-8')
        if code==0:code=125
    raise SystemExit(code)


if __name__=='__main__':
    try:main()
    except BaseException as exc:
        if not _ACTIVE_CALL_STARTED and not(isinstance(exc,SystemExit) and exc.code in (None,0)):
            try:
                from startup_finalize import frontend_abort
                frontend_abort(Path(__file__).resolve().parents[1],exc)
            except BaseException as sealing_error:print('PT_FRONTEND_ADMIN_UNRESOLVED',repr(sealing_error),file=sys.stderr)
        raise
