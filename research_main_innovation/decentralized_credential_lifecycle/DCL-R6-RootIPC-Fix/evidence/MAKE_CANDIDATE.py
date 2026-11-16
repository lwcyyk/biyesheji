"""Apply finite source edits in ri01 only; never execute a target module."""
from pathlib import Path

W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ri01')
OLD=Path(r'D:\毕业设计\DCL-R6-isolated-verification\c09f01')


def once(text,old,new):
    assert text.count(old)==1,old[:150]
    return text.replace(old,new,1)


g=(OLD/'src/guard.py').read_text(encoding='utf-8')
g=g.replace('c09f01','ri01').replace('batch05','batch06').replace('BATCH05','BATCH06')
g=once(g,"def atomic(path, data, root_record=False, timing_stage='metadata.atomic'):\n    _check_root()", """def root_ipc():
    if str(SOURCE) not in sys.path:sys.path.insert(0,str(SOURCE))
    import root_ipc as RI
    return RI
def root_checkpoint(allow_uninitialized=False):
    return root_ipc().checkpoint(sys.modules[__name__],allow_uninitialized)
def atomic(path, data, root_record=False, timing_stage='metadata.atomic'):
    _check_root()
    if os.geteuid()==0:
        return root_ipc().publish(sys.modules[__name__],path,data,root_record,timing_stage)""")
g=once(g,"    if a['authorization_text_sha256'] != digest(ROOT/'inputs/BATCH06_AUTHORIZATION_TEXT.txt'):","""    if (a.get('root_ipc_contract_sha256')!=m.get('root_ipc_contract_sha256') or
        a.get('root_ipc_profile')!='ROOT-IPC/1' or a.get('RootIPC_helpers_explicitly_approved') is not True):
        raise AdmissionBlocked('ROOT_IPC_SCOPE_MISSING')
    if a['authorization_text_sha256'] != digest(ROOT/'inputs/BATCH06_AUTHORIZATION_TEXT.txt'):""")
g=once(g,"def launch_one(case):\n    argv=service_argv(case)","def launch_one(case):\n    root_checkpoint()\n    argv=service_argv(case)")
g=once(g,"    while now()<until:\n        info=unit_show(unit); pid=int(info.get('MainPID','0'))", "    while now()<until:\n        root_checkpoint()\n        info=unit_show(unit); pid=int(info.get('MainPID','0'))")
g=once(g,"        while not (OUT/'C09.ready.json').exists() and now()<limit: time.sleep(.05)\n        if not (OUT/'C09.ready.json').exists(): raise AdmissionBlocked('C09_NOT_READY')\n        import c09_handoff as H", """        import c09_handoff as H
        def c09_live():
            return H.alive(sys.modules[__name__],t['main_identity']) and H.alive(
                sys.modules[__name__],trusted(ROOT/'inputs/STOP_ARMED.json')['identity'])
        root_ipc().wait_ready(sys.modules[__name__],OUT/'C09.ready.json',limit,c09_live)
        root_checkpoint()""")
g=once(g,"        H.sender_prepare(sys.modules[__name__],_COORDINATOR_ID)\n        os._exit(23)", "        H.sender_prepare(sys.modules[__name__],_COORDINATOR_ID)\n        root_checkpoint()\n        os._exit(23)")
g=once(g,"    while now()<limit+5:\n        info=unit_show(unit)", "    while now()<limit+5:\n        root_checkpoint()\n        info=unit_show(unit)")
# Seal runs in the final coordinator, after its raw waitpid observation is recorded.
g=once(g,"def seal():\n    # Wait for the independent writer", "def seal():\n    if _COORDINATOR_ID is not None and identity()!=_COORDINATOR_ID:return None\n    # Wait for the independent writer")
g=once(g,"            while not (ROOT/'inputs/STOP_ARMED.json').exists() and now()<until: time.sleep(.02)", "            root_ipc().wait_ready(sys.modules[__name__],ROOT/'inputs/STOP_ARMED.json',until)")
g=once(g,"        for c in remaining:\n            if c=='C09':", "        for c in remaining:\n            root_checkpoint()\n            if c=='C09':")
g=once(g,"                root_verify_c09h()\n            r=launch_one(c)", """                root_verify_c09h()
                root_checkpoint()
                import root_ipc_regression
                root_ipc_regression.run_suite(sys.modules[__name__])
                root_ipc().verify_qualification(sys.modules[__name__])
            r=launch_one(c)""")
g=once(g,"        s=state();s['status']='FORMAL';_root_write(ROOT/'inputs/batch_state.json',s)", """        import c09_handoff as H
        with H.lifecycle_lock(sys.modules[__name__]):
            root_checkpoint()
            s=state();s['status']='FORMAL';_root_write(ROOT/'inputs/batch_state.json',s)""")
g=once(g,"        if not select.select([ready_r],[],[],5)[0]:raise AdmissionBlocked('COORDINATOR_CHILD_HANDSHAKE')", "        root_ipc().wait_fd(sys.modules[__name__],ready_r,now()+5)")
g=once(g,"    fd=None\n    try:\n        root_ipc().wait_fd", "    fd=None;child_reaped=False\n    try:\n        root_ipc().wait_fd")
g=once(g,"            if ended:break\n            flags=root_ipc()", "            if ended:child_reaped=True;break\n            flags=root_ipc()") if '            if ended:break\n            flags=root_ipc()' in g else g
g=once(g,"        startup_until=now()+15\n        while True:", "        startup_until=now()+15;terminal_seen=None\n        while True:")
g=once(g,"            p=ROOT/'inputs/batch_state.json'\n            if p.exists():", """            flags=root_ipc().observe(sys.modules[__name__])
            if any(flags.values()):
                if terminal_seen is None:
                    terminal_seen=now()
                    if not flags['closed']:stop_tree('COORDINATOR_STOP_REQUEST')
                # Child observes cancellation, cleans and returns. Finite grace protects
                # against a scheduler that fails to cooperate; no new work is admitted.
                if now()>=terminal_seen+30:
                    signal.pidfd_send_signal(fd,signal.SIGKILL)
            p=ROOT/'inputs/batch_state.json'
            if p.exists():""")
g=once(g,"        code=os.waitstatus_to_exitcode(status)\n        if H.paths", """        code=os.waitstatus_to_exitcode(status)
        child_reaped=True
        raw_state=trusted(ROOT/'inputs/batch_state.json') if (ROOT/'inputs/batch_state.json').exists() else None
        _root_write(ROOT/('inputs/root_private/waitpid_%s.json'%child),{
            'schema':'ROOT-IPC-WAITPID/1','child':child_identity,'coordinator':coordinator,
            'raw_wait_status':status,'exit_code':code,'state':raw_state,'sample':stamp()})
        if H.paths""")
g=once(g,"        if fd is not None:os.close(fd)\ndef main():", """        if fd is not None:os.close(fd)
        if child_reaped and (ROOT/'inputs/CLOSED.json').exists() and _empty() and not (OUT/'EVIDENCE.zip').exists():
            try:seal()
            except BaseException as exc:
                _root_write(ROOT/'inputs/SEAL_ERROR.json',{'error':repr(exc),'sample':stamp()})
def main():""")
g=once(g,"        if (ROOT/'inputs/batch_state.json').exists():\n            try:stop_tree('COORDINATOR_FAILURE:'", """        if not child_reaped:
            if fd is None:
                try:os.kill(child,signal.SIGKILL)
                except ProcessLookupError:pass
            reap_until=now()+5
            while now()<reap_until:
                ended,cleanup_status=os.waitpid(child,os.WNOHANG)
                if ended:
                    child_reaped=True
                    try:_root_write(ROOT/('inputs/root_private/waitpid_%s.json'%child),{
                        'schema':'ROOT-IPC-WAITPID/1','child':child_identity if 'child_identity' in locals() else {'pid':child},
                        'coordinator':coordinator,'raw_wait_status':cleanup_status,
                        'exit_code':os.waitstatus_to_exitcode(cleanup_status),'sample':stamp(),'reason':'COORDINATOR_EXCEPTION'})
                    except BaseException:pass
                    break
                time.sleep(.02)
            if not child_reaped:
                try:stop_tree('COORDINATOR_REAP_UNCONFIRMED')
                finally:raise AdmissionBlocked('COORDINATOR_REAP_UNCONFIRMED')
        if (ROOT/'inputs/batch_state.json').exists():
            try:stop_tree('COORDINATOR_FAILURE:'""")
(W/'src/guard.py').write_text(g,encoding='utf-8')

h=(OLD/'src/c09_handoff.py').read_text(encoding='utf-8').replace('batch05','batch06')
h=once(h,"    if (G.ROOT/'inputs/CLOSED.json').exists():raise G.AdmissionBlocked('C09_CLOSED_ABSORBING')\n    h={", "    G.root_checkpoint()\n    h={")
h=once(h,"    p=G.ROOT/'inputs/c09_events.jsonl'", "    p=G.ROOT/'inputs/root_private/c09_events.jsonl'")
h=once(h,"os.O_APPEND|os.O_NOFOLLOW,0o640)","os.O_APPEND|os.O_NOFOLLOW,0o600)")
h=once(h,"        os.fchmod(fd,0o640);os.fchown(fd,0,G.pwd.getpwnam('dcl-r6').pw_gid)","        os.fchown(fd,0,0);os.fchmod(fd,0o600)")
h=once(h,"    remaining=min(12,until-G.now())", "    G.root_checkpoint()\n    remaining=min(12,until-G.now())")
h=once(h,"    c.settimeout(remaining)","    c.settimeout(min(.05,remaining))")
h=once(h,"        c.connect(str(paths(G)['socket']))", "        G.root_ipc().connect(G,c,paths(G)['socket'],until)")
h=once(h,"        c.sendall(raw);reply=c.recv(65537)","        G.root_ipc().send_packet(G,c,raw,until)\n        reply=G.root_ipc().receive(G,c,until)")
h=once(h,"    import c09_oracle\n    q=G.trusted", "    import c09_oracle\n    G.root_ipc().verify_qualification(G)\n    q=G.trusted")
h=once(h,"    if h['window']!=window(G,s) or h['id']!=sha(","    if not G.root_ipc().same_binding(h['window'],window(G,s)) or h['id']!=sha(")
h=once(h,"        try:c,_=self.sock.accept()", "        G.root_checkpoint()\n        try:c,_=self.sock.accept()")
h=once(h,"        c.settimeout(.5)","        c.settimeout(.05)")
h=once(h,"            raw=c.recv(65537)","            raw=G.root_ipc().receive(G,c,min(G.state()['deadline'],G.now()+.5))")
h=once(h,"            c.sendall(canonical(reply).encode())", "            with lifecycle_lock(G):\n                G.root_checkpoint()\n                G.root_ipc().send_packet(G,c,canonical(reply).encode(),min(h['observe_until'],G.now()+.5))")
(W/'src/c09_handoff.py').write_text(h,encoding='utf-8')
print('Wrote guard.py and c09_handoff.py in ri01; original source preserved.')
