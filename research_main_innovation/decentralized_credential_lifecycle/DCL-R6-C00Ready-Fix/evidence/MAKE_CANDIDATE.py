"""Finite host-only startup integration; no native query or target import."""
from pathlib import Path

W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\cr01')
OLD=Path(r'D:\毕业设计\DCL-R6-isolated-verification\bc01')
def norm(s):return s.replace('bc01','cr01').replace('batch07','batch08').replace('BATCH07','BATCH08')
def once(s,a,b):
    assert s.count(a)==1,a[:100]
    return s.replace(a,b,1)

for f in (OLD/'src').glob('*.py'):
    if f.name not in ['guard.py','boot_continuity.py']:(W/'src'/f.name).write_bytes(f.read_bytes())
for name in ['root_ipc.py','c09_handoff.py','boot_continuity_regression.py']:
    (W/'src'/name).write_text(norm((OLD/'src'/name).read_text()),encoding='utf-8')
(W/'host/windows_entry.py').write_text(norm((OLD/'host/windows_entry.py').read_text()),encoding='utf-8')
g=norm((OLD/'src/guard.py').read_text(encoding='utf-8'))
g=once(g,"a['scope'] not in ('CALIBRATE_S1S9_THEN_F1_F4','CALIBRATE_S1S9_ONLY')", "a['scope'] not in ('CALIBRATE_S1S9_THEN_F1_F4','C00_DIAGNOSTIC_ONLY')")
g=once(g,"a.get('RootIPC_helpers_explicitly_approved') is not True", "(a['scope']!='C00_DIAGNOSTIC_ONLY' and a.get('RootIPC_helpers_explicitly_approved') is not True)")
g=once(g,"a.get('SameProcess_C09_resume_explicitly_approved') is not True", "(a['scope']!='C00_DIAGNOSTIC_ONLY' and a.get('SameProcess_C09_resume_explicitly_approved') is not True)")
g=once(g,"    if a['authorization_text_sha256'] != digest(ROOT/'inputs/BATCH08_AUTHORIZATION_TEXT.txt'):","""    if (a.get('readiness_profile')!='C00-READY/1' or a.get('readiness_contract_sha256')!=m.get('readiness_contract_sha256')):
        raise AdmissionBlocked('READINESS_SCOPE_MISSING')
    if a['scope']=='C00_DIAGNOSTIC_ONLY' and a.get('C00_diagnostic_explicitly_approved') is not True:
        raise AdmissionBlocked('C00_DIAGNOSTIC_NOT_APPROVED')
    if a['scope']=='CALIBRATE_S1S9_THEN_F1_F4' and a.get('Full_conditional_chain_explicitly_approved') is not True:
        raise AdmissionBlocked('FULL_CHAIN_NOT_APPROVED')
    if a['authorization_text_sha256'] != digest(ROOT/'inputs/BATCH08_AUTHORIZATION_TEXT.txt'):""")
old="""    _run(argv)
    unit='dclr6batch08-'+case.lower()+'.service'; until=now()+14
    info={}
    while now()<until:
        root_checkpoint()
        info=unit_show(unit); pid=int(info.get('MainPID','0'))
        if pid: break
        time.sleep(.02)
    else: raise AdmissionBlocked('NO_CONTROLLER_PID')
"""
new="""    activation_started=now()
    _run(argv)
    unit='dclr6batch08-'+case.lower()+'.service'; until=activation_started+14
    info={};ready_lease=None
    if case in ('C00','C10'):
        import service_readiness
        ready_lease=service_readiness.wait_native(sys.modules[__name__],case,unit,activation_started)
        pid=ready_lease.identity['pid'];info=ready_lease.info
    else:
        until=now()+14
        while now()<until:
            root_checkpoint()
            info=unit_show(unit); pid=int(info.get('MainPID','0'))
            if pid: break
            time.sleep(.02)
        else: raise AdmissionBlocked('NO_CONTROLLER_PID')
"""
g=once(g,old,new)
g=once(g,"t={'case':case,'unit':unit,'main_identity':identity(pid),'boot_id':boot_id(),", "t={'case':case,'unit':unit,'main_identity':(ready_lease.identity if ready_lease else identity(pid)),'boot_id':boot_id(),")
g=once(g,"    boot_continuity().service_confirmed(sys.modules[__name__],t)\n    _root_write(ROOT/('inputs/ticket_'+case+'.json'),t)","""    try:
        boot_continuity().service_confirmed(sys.modules[__name__],t,ready_lease)
        if ready_lease:
            root_checkpoint()
            if now()>=ready_lease.until:raise LimitReached('READINESS_TICKET_LATE')
            ready_lease.ticket_admit(sys.modules[__name__],t)
            t['readiness_sha256']=digest(ROOT/('inputs/'+case+'_READINESS.json'))
        _root_write(ROOT/('inputs/ticket_'+case+'.json'),t)
    finally:
        if ready_lease:ready_lease.close()""")
g=once(g,"            boot_continuity().formal_gate(sys.modules[__name__])", "            import service_readiness\n            service_readiness.formal_gate(sys.modules[__name__])\n            boot_continuity().formal_gate(sys.modules[__name__])")
g=once(g,"    expected_scope='CALIBRATE_S1S9_ONLY' if calibrate_only else 'CALIBRATE_S1S9_THEN_F1_F4'", "    expected_scope='C00_DIAGNOSTIC_ONLY' if a['scope']=='C00_DIAGNOSTIC_ONLY' else ('CALIBRATE_S1S9_ONLY' if calibrate_only else 'CALIBRATE_S1S9_THEN_F1_F4')")
g=once(g,"            if r['status']!='PASS': stop_tree('CALIBRATION_'+r['status']);return 65", """            if r['status']!='PASS': stop_tree('CALIBRATION_'+r['status']);return 65
            if c=='C00':
                import readiness_regression
                readiness_regression.run_suite(sys.modules[__name__])
                if a['scope']=='C00_DIAGNOSTIC_ONLY':
                    stop_tree('C00_DIAGNOSTIC_COMPLETE');seal();return 0""")
(W/'src/guard.py').write_text(g,encoding='utf-8')
b=norm((OLD/'src/boot_continuity.py').read_text(encoding='utf-8'))
b=once(b,"m['version']!='BootContinuity-static-1'","m['version']!='C00Ready-static-1'")
b=once(b,"'BOOT_CONTINUITY_QUALIFICATION.json'):raise Rejected('BC_PUBLIC_TARGET')", "'BOOT_CONTINUITY_QUALIFICATION.json','C00_READINESS.json','C10_READINESS.json','C00_READY_QUALIFICATION.json'):raise Rejected('BC_PUBLIC_TARGET')")
b=once(b,"auth.get('SameProcess_C09_resume_explicitly_approved') is not True", "(auth.get('scope')!='C00_DIAGNOSTIC_ONLY' and auth.get('SameProcess_C09_resume_explicitly_approved') is not True)")
b=once(b,"auth.get('RootIPC_helpers_explicitly_approved') is not True", "(auth.get('scope')!='C00_DIAGNOSTIC_ONLY' and auth.get('RootIPC_helpers_explicitly_approved') is not True)")
b=once(b,"auth.get('scope')!='CALIBRATE_S1S9_THEN_F1_F4'", "auth.get('scope') not in ('CALIBRATE_S1S9_THEN_F1_F4','C00_DIAGNOSTIC_ONLY')")
b=once(b,"    first=runtime_snapshot(m,lock,deadline,epoch)", """    if auth['scope']=='C00_DIAGNOSTIC_ONLY' and auth.get('C00_diagnostic_explicitly_approved') is not True:raise Rejected('BC_C00_SCOPE')
    if auth['scope']=='CALIBRATE_S1S9_THEN_F1_F4' and auth.get('Full_conditional_chain_explicitly_approved') is not True:raise Rejected('BC_FULL_SCOPE')
    if auth.get('readiness_contract_sha256')!=m.get('readiness_contract_sha256'):raise Rejected('BC_READINESS_BINDING')
    first=runtime_snapshot(m,lock,deadline,epoch)""")
a=b.index('def service_confirmed(G,t):');end=b.index("    service_policy(",a)
b=b[:a]+"""def service_confirmed(G,t,lease=None):
    if t['case'] not in ('C00','C10'):return
    if _SESSION is None:raise Rejected('BC_CHILD_SESSION_MISSING')
    import service_readiness
    certificate=service_readiness.require_lease(G,t,lease)
    info=lease.info;s=G.state();owner=_SESSION['ticket']['owner']
"""+b[end:]
b=once(b,"        if result==23:\n            verify_regression(G)", "        if result==23:\n            a,_=G.authorization()\n            if a['scope']!='CALIBRATE_S1S9_THEN_F1_F4' or a.get('SameProcess_C09_resume_explicitly_approved') is not True:raise Rejected('BC_RESUME_NOT_APPROVED')\n            verify_regression(G)")
(W/'src/boot_continuity.py').write_text(b,encoding='utf-8')
print('C00/C10 readiness wiring and explicitly separate diagnostic/full modes written; no WSL calls.')
