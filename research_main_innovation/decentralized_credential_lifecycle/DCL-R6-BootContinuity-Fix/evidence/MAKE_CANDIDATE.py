"""Host-only finite startup edits; retains r4 original files and semantics."""
from pathlib import Path

W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\bc01')
OLD=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ri01')


def once(s,old,new):
    assert s.count(old)==1,old
    return s.replace(old,new,1)


g=(OLD/'src/guard.py').read_text(encoding='utf-8').replace('ri01','bc01').replace('batch06','batch07').replace('BATCH06','BATCH07')
g=once(g,"def root_checkpoint(allow_uninitialized=False):", """def boot_continuity():
    if str(SOURCE) not in sys.path:sys.path.insert(0,str(SOURCE))
    import boot_continuity as BC
    return BC
def root_checkpoint(allow_uninitialized=False):""")
g=once(g,"    if a['authorization_text_sha256'] != digest(ROOT/'inputs/BATCH07_AUTHORIZATION_TEXT.txt'):","""    if (a.get('boot_continuity_profile')!='BC-SINGLE-SESSION/1' or
        a.get('boot_contract_sha256')!=m.get('boot_contract_sha256') or a.get('source_mode')!='SOURCE_ONLY/1' or
        a.get('SingleSession_exec_explicitly_approved') is not True or a.get('SameProcess_C09_resume_explicitly_approved') is not True):
        raise AdmissionBlocked('BOOT_CONTINUITY_SCOPE_MISSING')
    if a['authorization_text_sha256'] != digest(ROOT/'inputs/BATCH07_AUTHORIZATION_TEXT.txt'):""")
g=once(g,"        if case=='FORMAL':\n            require_formal_admission()", "        if case=='FORMAL':\n            boot_continuity().formal_gate(sys.modules[__name__])\n            require_formal_admission()")
g=once(g,"    _root_write(ROOT/('inputs/ticket_'+case+'.json'),t)\n    if case=='C09':", "    boot_continuity().service_confirmed(sys.modules[__name__],t)\n    _root_write(ROOT/('inputs/ticket_'+case+'.json'),t)\n    if case=='C09':")
g=once(g,"    if _COORDINATOR_ID is not None and identity()!=_COORDINATOR_ID:return None\n    # Wait", "    if _COORDINATOR_ID is not None and identity()!=_COORDINATOR_ID:return None\n    boot_continuity().before_seal(sys.modules[__name__])\n    # Wait")
g=once(g,"def _launcher_body(resume=False,calibrate_only=False):\n    if os.geteuid()!=0: raise AdmissionBlocked('TRUSTED_ROOT_LAUNCHER_REQUIRED')\n    a,m=authorization()", """def _launcher_body(resume=False,calibrate_only=False):
    if os.geteuid()!=0: raise AdmissionBlocked('TRUSTED_ROOT_LAUNCHER_REQUIRED')
    a,m=authorization()
    boot_continuity().child_admission(sys.modules[__name__],resume)""")
g=once(g,"                root_ipc().verify_qualification(sys.modules[__name__])\n            r=launch_one(c)", """                root_ipc().verify_qualification(sys.modules[__name__])
                import boot_continuity_regression
                boot_continuity_regression.run_suite(sys.modules[__name__])
            r=launch_one(c)""")
g=once(g,"    if os.geteuid()!=0:raise AdmissionBlocked('TRUSTED_ROOT_COORDINATOR_REQUIRED')\n    authorization()", "    if os.geteuid()!=0:raise AdmissionBlocked('TRUSTED_ROOT_COORDINATOR_REQUIRED')\n    authorization()\n    boot_continuity().guard_admission(sys.modules[__name__],resume)")
g=once(g,"    if args.role=='launcher': return launcher(args.resume,args.calibrate_only)", "    if args.role=='launcher': return boot_continuity().entry(sys.modules[__name__],args.resume,args.calibrate_only)")
(W/'src/guard.py').write_text(g,encoding='utf-8')
for name in ['c09_handoff.py','root_ipc.py']:
    s=(OLD/'src'/name).read_text(encoding='utf-8').replace('batch06','batch07')
    (W/'src'/name).write_text(s,encoding='utf-8')
print('Applied startup hooks and namespace-only adaptations in bc01. No WSL calls.')
