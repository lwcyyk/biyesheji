"""Independent bounded data oracle for future A evidence. Never signals roles."""
import hashlib,json

def verify(case,closure,budget_before,budget_after,exit_witness,admin,expected):
    errors=[]
    def require(ok,code):
        if not ok:errors.append(code)
    require(case.get('origin')=='NATIVE_RECORDED_EVENT','ORIGIN')
    require(case.get('binding')==expected.get('binding'),'BINDING')
    unit=case.get('unit');start=case.get('start',{});finish=case.get('finish',{})
    n=start.get('native',{});f=finish.get('native',{});ident=start.get('identity',{})
    require(isinstance(unit,str) and unit==expected['service_prefix']+'mr-native-fault.service','UNIT')
    require(n.get('Id')==unit and f.get('Id')==unit and n.get('ActiveState')=='active' and f.get('ActiveState')=='failed','STATE')
    require(bool(n.get('InvocationID')) and n.get('InvocationID')==f.get('InvocationID'),'INVOCATION')
    require(f.get('Result')=='exit-code' and f.get('ExecMainCode')=='1' and f.get('ExecMainStatus')=='79','REAL_EXIT')
    require(str(ident.get('pid'))==n.get('MainPID')==f.get('ExecMainPID') and ident.get('boot_id')==expected['boot_id'],'PID_BOOT')
    require(case.get('rejection')=='MR_UNREVIEWED_MANAGER_FAILURE:'+str(unit),'UNREVIEWED')
    require(set(case.get('failed_after',[]))==set(case.get('failed_before',[]))|{unit},'FAILED_SET')
    try:
        rows=[json.loads(s) for s in case['journal']['stdout'].splitlines()]
        require(case['journal']['exit_code']==0 and len(rows)<=32,'JOURNAL_QUERY')
        hits=[r for r in rows if r.get('_SYSTEMD_UNIT')==unit and r.get('_BOOT_ID')==expected['boot_id'].replace('-','') and r.get('_SYSTEMD_INVOCATION_ID')==n.get('InvocationID')]
        require(any(json.loads(r['MESSAGE']).get('event')=='MR_NATIVE_FAULT_READY' for r in hits),'JOURNAL_EVENT')
        require(int(f['ExecMainExitTimestampMonotonic'])>0 and start['sample']['boottime']<=finish['sample']['boottime'],'TIME')
    except (KeyError,TypeError,ValueError):errors.append('JOURNAL_OR_TIME')
    require(closure.get('stop_published') is True and closure.get('closed') is True,'AUTO_STOP')
    require(closure.get('roles_exited') is True and closure.get('group_empty') is True,'CLEANUP')
    require(closure.get('fallback') is False and closure.get('manual_stop') is False,'PRIMARY_PATH')
    require(closure.get('new_work_after_fault')==0,'DISPATCH')
    require(closure.get('window')==case.get('window'),'WINDOW')
    require(budget_before==budget_after and set(budget_before)=={'counter','intent','journal'},'BUDGET')
    require(all(isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v) for v in budget_before.values()),'BUDGET_HASH')
    require(exit_witness.get('exit_code')==78 and exit_witness.get('source')=='direct-parent waitpid','WAITPID')
    require(admin.get('native')=='NATIVE_SEAL_COMPLETED','NATIVE_SEAL')
    require(admin.get('administrative')=='ADMIN_EVIDENCE_SEALED','ADMIN_SEAL')
    return {'accepted':not errors,'errors':sorted(set(errors)),
        'status':'EXPECTED_NATIVE_FAILURE_CLOSED' if not errors else 'REJECT_NATIVE_ACCEPTANCE',
        'binding':expected.get('binding'),'promotes_other_batch':False}

def from_snapshot(root,admin,expected):
    """Parse immutable future exported originals; OS metadata is audited separately.

    `admin` must be a separately verified finalizer audit, with archive hashes
    and quiescence observations. This function cannot manufacture that audit.
    """
    from pathlib import Path
    import stat,struct
    root=Path(root)
    def load(rel):
        p=root/rel;s=p.lstat()
        if not stat.S_ISREG(s.st_mode) or p.is_symlink() or s.st_size>4194304:raise ValueError('RAW_METADATA')
        return json.loads(p.read_bytes())
    case=load('inputs/root_private/boot/mr_native_case.json')
    first=load('inputs/root_private/boot/mr_first_failure.json')
    close=load('inputs/root_private/boot/mr_close_state.json')
    closed=load('inputs/CLOSED.json');stop=load('out/STOP_REQUEST.json')
    reg=load('inputs/root_private/boot/mr_scheduler.json')
    wait=load('inputs/root_private/waitpid_%s.json'%reg['child']['pid'])
    if wait['raw_wait_status']!=78<<8 or wait['child']!=reg['child'] or wait['coordinator']!=reg['owner']:raise ValueError('RAW_WAITPID')
    if first['reason']!='MR_EXPECTED_DIAGNOSTIC_FAILURE' or first['expected_diagnostic'] is not True:raise ValueError('RAW_FIRST_FAILURE')
    if close['first_failure_sha256']!=hashlib.sha256((root/'inputs/root_private/boot/mr_first_failure.json').read_bytes()).hexdigest():raise ValueError('RAW_FIRST_DIGEST')
    if closed['boot_id']!=expected['boot_id'] or stop['boot_id']!=expected['boot_id']:raise ValueError('RAW_BOOT')
    if not(case['finish']['sample']['boottime']<=stop['boottime']<=closed['boottime'] and first['sample']['boottime']>=case['finish']['sample']['boottime']):raise ValueError('RAW_STOP_TIME')
    before={};after={}
    for role,name in [('counter','visits.bin'),('intent','visits.bin.intent.json'),('journal','visits.bin.journal.jsonl')]:
        before[role]=first['budget'][name]['sha256'];p=root/'out'/name
        if p.is_symlink() or not p.is_file() or p.stat().st_size>33554432:raise ValueError('RAW_BUDGET_BOUND')
        digest=hashlib.sha256()
        with p.open('rb') as stream:
            for chunk in iter(lambda:stream.read(65536),b''):digest.update(chunk)
        after[role]=digest.hexdigest()
    counter=(root/'out/visits.bin').read_bytes()
    if len(counter)!=24 or counter[:8]!=b'BRNGv001' or struct.unpack('<Q',counter[8:16])[0]!=case['counter_after_prepaid']:raise ValueError('RAW_COUNTER')
    if admin.get('binding')!=expected['binding'] or admin.get('independently_verified_archives') is not True:raise ValueError('RAW_ADMIN_TRUST')
    closure={'stop_published':True,'closed':True,'roles_exited':admin.get('roles_exited'),
        'group_empty':admin.get('group_empty'),'fallback':admin.get('fallback'),'manual_stop':admin.get('manual_stop'),
        'new_work_after_fault':admin.get('new_work_after_fault'),'window':first['window']}
    return verify(case,closure,before,after,{'exit_code':wait['exit_code'],'source':'direct-parent waitpid'},admin,expected)
