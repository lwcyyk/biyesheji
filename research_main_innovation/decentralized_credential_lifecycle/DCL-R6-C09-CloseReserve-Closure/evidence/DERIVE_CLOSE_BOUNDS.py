"""Static source census, JSON grammar arithmetic and abstract research tables.

No protocol implementation, imported target, failure injection or state replay.
"""
from AUDIT_INPUTS import ROOT, PREV, BOUND, OUT, E, RUNTIME, save, read, sha, row, cp
import ast
import json
from pathlib import Path

assert read(E/'INITIAL_INPUT_CHECK.json')['frozen_runtime_source_inputs']==64

# All actual frozen source is parsed as data. Save call ancestry, including loops.
calls=[];literal_hits=[]
interesting={'stop_tree','request_stop','halt_budget','abort','fail','seal','put','_root_write','write','print_exc','print','waitpid'}
class Scan(ast.NodeVisitor):
    def __init__(self,p,text):self.p=p;self.text=text;self.func=[];self.loops=[]
    def visit_FunctionDef(self,n):
        self.func.append(n.name);self.generic_visit(n);self.func.pop()
    visit_AsyncFunctionDef=visit_FunctionDef
    def visit_For(self,n):
        self.loops.append({'type':'for','line':n.lineno,'header':ast.get_source_segment(self.text,n.iter)})
        self.generic_visit(n);self.loops.pop()
    def visit_While(self,n):
        self.loops.append({'type':'while','line':n.lineno,'header':ast.get_source_segment(self.text,n.test)})
        self.generic_visit(n);self.loops.pop()
    def visit_Call(self,n):
        name=n.func.id if isinstance(n.func,ast.Name) else n.func.attr if isinstance(n.func,ast.Attribute) else None
        if name in interesting:
            calls.append({'file':str(self.p),'function':'.'.join(self.func),'line':n.lineno,'call':name,
                          'text':ast.get_source_segment(self.text,n),'enclosing_loops':list(self.loops)})
        self.generic_visit(n)
for base in [RUNTIME/'src',RUNTIME/'host']:
    for p in sorted(base.glob('*.py')):
        text=p.read_text(encoding='utf-8-sig');Scan(p,text).visit(ast.parse(text))
        for i,line in enumerate(text.splitlines(),1):
            if any(s in line for s in ('CLOSED','STOP_REQUEST','stop_event_','stop_result_','mr_close','SEAL_ERROR','final_before_seal','terminal_seal_review','EVIDENCE_MANIFEST','STARTUP_FINALIZATION','FRONTEND_ABORT')):
                literal_hits.append({'file':str(p),'line':i,'text':line})
save('SOURCE_CALL_CENSUS.json',{'all_relevant_calls':calls,'literal_hits':literal_hits,'target_imports':0})
excerpts={}
for file,ranges in {
 'src/guard.py':[(75,100),(109,164),(175,184),(545,546),(697,720),(749,841),(860,904),(993,1027),(1038,1074),(1130,1300)],
 'src/c09_handoff.py':[(18,34),(75,89),(252,310)],
 'src/manager_recovery.py':[(19,69),(82,116),(153,188),(244,430),(469,520)],
 'src/root_ipc.py':[(21,48),(91,155)],'src/boot_continuity.py':[(65,110),(406,446)],
 'src/startup_lifecycle.py':[(307,368),(370,524)],'src/terminal_evidence.py':[(18,35),(44,75),(121,186),(193,266)],
 'host/startup_finalize.py':[(10,121)],'host/windows_entry.py':[(13,78)],'src/admin_postexit.py':[(1,65)],'src/guard_probe.py':[(145,156)]}.items():
    text=(RUNTIME/file).read_text(encoding='utf-8-sig').splitlines()
    excerpts[file]=[{'start':a,'end':min(b,len(text)),'lines':[{'line':i,'text':text[i-1]} for i in range(a,min(b,len(text))+1)]} for a,b in ranges]
save('SOURCE_EXCERPTS.json',excerpts)

# Producer rows: actual filenames/records, logical record count and quota domain.
P=[]
def add(id,producer,process,site,path,trigger,phase,count,size,persistence,domain,required,after,fail):
    P.append(dict(zip(['producer_id','producer','process','source_site','record_or_path','trigger','phase',
      'maximum_count','maximum_encoded_bytes','persistence','quota_domain','required_for_close','after_closed','failure_behavior'],
      [id,producer,process,site,path,trigger,phase,count,size,persistence,domain,required,after,fail])))
add('C00','quota overflow refusal','proposed authenticated Receiver','c09_handoff.py:252-279; previous quota v2','no current quota-rejection producer',
    'attempt257','main exhausted','current no rejection; draft0 rejection rows','0 rejection-log bytes',
    'draft denies before classify; first failure separate','proposed main256/263, not effective','denial required; new row not required',False,'current may append another CHECK; future refusal proof missing')
add('C01','quota first summary','proposed one Root close owner','previous proposal only','new bounded failure summary',
    'first quota fault/exhaustion','transition to stop','draft1','draft334','compact ASCII JSON+LF, once, file+directory sync','proposed separate local reserve','draft summary supplements full raw facts',True,'UNKNOWN if persistence fails; no retry stream')
add('C02','guard.request_stop via M.abort','Root Receiver/scheduler/coordinator','manager_recovery.py:328; guard.py:545-546','out/STOP_REQUEST.json',
    'no existing STOP observed','abort entry','<=A writes; one pathname','189 only for reason ASCII<=43; otherwise L_stop(R)',
    'RootIPC pretty UTF-8, file+two-directory sync','current no close quota','cancellation marker',True,'notes STOP_PUBLISH:type; cleanup continues; race may overwrite')
add('C03','guard.halt_budget','Root prepay or UID999 payload budget actor','guard.py:82-85,688,709; range_core.py:163,192','same out/STOP_REQUEST.json',
    'budget persistence exception','any budget phase','H writes; same path as C02','error reason lacks explicit encoded width',
    'RootIPC or payload atomic; same target','budget safety, no independent close byte cap','budget denial marker when that path fires',True,'HALTED process flag remains even if marker write fails')
add('C04','M.abort first failure','Root roles','manager_recovery.py:355-361','inputs/root_private/boot/mr_first_failure.json',
    'first missing file under mr_close lock','abort entry','one retained object; <=A put attempts','L_first(R,T,B)',
    'BC.Store exclusive compact JSON, file+directory fsync','none','abnormal-path first failure evidence',True,'notes FAILURE_PERSIST; absence/corruption not repaired to success')
add('C05','M.abort external closing delegate','current external Receiver only','manager_recovery.py:363-365','inputs/root_private/boot/mr_external_closing.json',
    'STOP_ARMED.identity == caller','abort entry','<=A writes; one object','L_external fixed ABI conditional',
    'BC.Store replace, compact JSON','none','sealer delegation when matching role',True,'same failure persistence notes')
add('C06','M.abort ABORTING','Root roles','manager_recovery.py:366','same mr_close_state.json',
    'first failure loaded','abort intermediate','<=A writes; final uses same file','L_aborting fixed ABI conditional',
    'BC.Store replace, compact JSON','none','intermediate state; not an extra retained final file',True,'may leave ABORTING/partial staging; UNKNOWN')
add('C07','guard.stop_tree close marker','Root close caller','guard.py:754-760','inputs/CLOSED.json OR stop_event_<pid>_<ns>.json',
    'close=True; H lock; CLOSED already exists => new stop_event','stop attempt','<=S marker writes; CLOSED unique<=1; events<=S','L_stop(R)',
    'H lifecycle lock then RootIPC publish','none','CLOSED cancellation; extra stop events actual evidence',True,'close_error=repr; still attempts systemctl stop')
add('C08','M.abort fallback CLOSED','Root abort caller','manager_recovery.py:378-381','same inputs/CLOSED.json',
    'primary cleanup failed/insufficient window; marker absent','fallback','<=A attempts; one shared pathname','L_stop(R)',
    'H lock then RootIPC; presence dominates','none','fallback marker when primary failed',True,'notes CLOSED_FALLBACK; cleanup evidence remains UNKNOWN')
add('C09','guard.stop_tree result','Root close caller','guard.py:751,766-769','inputs/stop_result_<pid>_<ns>.json',
    'group empty confirmed; function reaches return publication','post-stop','<=S objects','L_result(E,V1..V12)',
    'RootIPC pretty JSON','none','result/observed charged snapshot; not proof every Root exited',True,'raises to caller; absence or error cannot be relabeled cleanup success')
add('C10','M.abort close attempt','Root abort caller','manager_recovery.py:390-397','inputs/root_private/boot/mr_close_attempts.jsonl',
    'cleanup result constructed','post-stop','<=A rows; one object','L_cleanup(T,B)+1 LF',
    'mr_close lock; O_APPEND/full write/fsync','none','all actual abnormal attempts preserved',True,'result UNKNOWN; FINAL_EVIDENCE added only to returned object if final persistence failed')
add('C11','M.abort final state','Root abort caller','manager_recovery.py:398-400','same mr_close_state.json as C06',
    'attempt append performed','post-stop','<=A writes; one shared object','L_cleanup(T,B)',
    'BC.Store replace, compact JSON','none','final internal status; absent can be UNKNOWN',True,'UNKNOWN return; existing raw attempt/partial staging preserved')
add('C12','coordinator waitpid normal','Root direct parent','guard.py:1222-1227','inputs/root_private/waitpid_<child>.json',
    'real child reaped','child exit','W<=2 phase objects, disjoint from fallback same-phase write','L_waitpid(state) fixed source schema/ABI conditional',
    'RootIPC pretty JSON, embeds state','none','required terminal native exit evidence',True,'child_reaped set before write; if it fails, no fake waitpid retry')
add('C13','coordinator waitpid fallback','Root direct parent','guard.py:1251-1259','same phase waitpid_<child>.json',
    'exception cleanup reaps previously unreaped child','child exit','mutually exclusive per phase with C12; combined W<=2','L_waitpid_fallback fixed ABI conditional',
    'RootIPC pretty JSON; failed write swallowed','none','real raw wait status if publication succeeds',True,'missing record remains UNKNOWN, not synthesized by Receiver')
add('C14','coordinator C09 witness','Root sender parent','c09_handoff.py:297-310','inputs/c09_exit_witness.json',
    'C09 child reaped while not stopped','handoff','<=1; preexisting/read-only during close','fixed identity/window schema; separately bounded width proof',
    'H lock + RootIPC; returns early when CLOSED','C09 other originals','for successful handoff; failure path may legitimately lack it',False,'cannot reconstruct parent waitpid after parent dies')
add('C15','M.budget_snapshot','Root abort caller','manager_recovery.py:266-280,330,392','embedded before/after hash+size maps',
    'abort entry/cleanup','before/after stop','<=2A scans; embedded in C04/C10/C11','B(T) encoded map; full journal only read',
    'read-only stream 64KiB','original global ledger retained separately','budget preservation evidence',True,'per-file UNKNOWN/error type; never initializes or charges budget')
add('C16','M.review_case/events','Root scheduler/coordinator','manager_recovery.py:153-188,51-60','mr_events.jsonl; mr_review_C09.json etc',
    'expected service exit review before resume','handoff/recovery','old review credit256; per event checks cap32768; full callers separate','32768 event write cap; stored proof fields need separate schema',
    'MR event lock append+file/dir fsync; private proof exclusive','MR native credit; not C09 quota','normal MR raw provenance; no generic close-event producer',True,'error unwinds into abort, no recursive review loop')
add('C17','BC.before_seal','eligible Root session owner','boot_continuity.py:406-412','inputs/root_private/boot/final_before_seal.json',
    'missing before-seal record','pre-seal','<=Q_s attempts; one object','embeds source state schema',
    'BC.Store compact JSON','none','native provenance when producer executes',True,'failure aborts sealing')
add('C18','G.seal terminal review','eligible native sealer','guard.py:1009-1018','inputs/root_private/boot/terminal_seal_review.json',
    'terminal reader native_ready','pre-seal','<=Q_s create attempts; exclusive, at most1 successful data publication','L_TR unclosed nested report',
    'BC.Store exclusive; existing blocks replay','none','native evidence prerequisite',True,'reject/UNKNOWN; no overwrite to make archive succeed')
add('C19','P.defer_startup_seal','Root sealer/caller','startup_lifecycle.py:348-354','inputs/root_private/boot/pt_seal_disposition.json',
    'native applicability unresolved/not applicable','seal decision','<=Q_s writes; one object','L_disposition(T), error text <=256 codepoints',
    'BC.Store replace','none','preserve native applicability UNKNOWN separately',True,'exception propagates to bounded wrappers')
add('C20','SEAL_ERROR writer','two scheduler/two coordinator finally paths','guard.py:1149,1275','inputs/SEAL_ERROR.json',
    'M.seal raises','seal failure','<=4 writes; one pathname','repr(exc) encoded field has no explicit cap',
    'RootIPC pretty JSON','none','actual seal error evidence',True,'failure may reach outer abort/traceback; no automatic infinite seal recursion')
add('C21','native manifest builder','eligible G.seal','guard.py:1019-1023','out/EVIDENCE_MANIFEST.json',
    'readiness and terminal review passed','native seal','<=Q_s attempts; one file','M_native(N,F,D) conditional grammar bound',
    'RootIPC pretty JSON; whole-file digest','native output; no new approved cap','all raw regular originals represented except two native output basenames',True,'partial manifest/zip stays unresolved; original raw retained')
add('C22','native ZIP builder','eligible G.seal','guard.py:1024-1027','out/EVIDENCE.zip',
    'manifest published','native seal','one x-create archive, not one per raw file','ZIP(R+M,names,codec); raw volume unresolved',
    'ZipFile x; close/CRC format; no full disk durability theorem','current acceptance257/32MiB remains','native archive when successful',True,'partial archive not equivalent to a complete seal')
add('C23','payload watchdog stop','watchdog UID999','guard.py:825-841','out/<case>.watchdog_stop.json',
    'expired/stale/dead/stopped','service exit','<=16 fixed-case writes; one per watchdog','fixed flags/stamp conditional',
    'payload atomic','case evidence; no C09 close reserve','all emitted originals retained; absence alone is not group-empty proof',True,'top-level error/stderr; no new watchdog restart')
add('C24','controller finally/monitor','UID999 payload main/monitor','guard.py:861-904','normal_stop/timing/monitor_failure/heartbeat/watchdog.stderr',
    'normal/abnormal controller exit','service exit','fixed file slots; timing/error bytes and monitor attempts separate','normal_stop ASCII16; timing repr/stdio volume unresolved',
    'payload atomic or raw file; join and wait bounded by existing deadlines','case domain, not main log','actual output preservation',True,'abrupt exit can lose telemetry; raw exit proof separately needed')
add('C25','P.post_exit_export audit','post-exit Root admin','startup_lifecycle.py:441-491','control/STARTUP_NATIVE_AUDIT.json',
    'up to128 quiescence samples; runtime/role audit','post-exit','one x-create audit','L_admin_audit: ambient role/process/error/member arrays need aggregate bound',
    'json dump UTF-8 indent2 +flush+fsync file','independent administrative30s/AS1GiB','admin cleanup/native/internal axes; no runtime grants',True,'UNKNOWN/defer; actual role exit cannot be assumed from CLOSED')
add('C26','post-exit raw stdout/stderr','admin child + host parent','host/startup_finalize.py:65-85','STARTUP_POSTEXIT.stdout.raw / stderr.raw',
    'automatic post-exit command','post-exit','2 x-create streams, one invocation','no streaming byte cap',
    'host raw output files','administrative outside ROOT','complete raw outputs preserved',True,'timeout result124; native/admin status independently retained')
add('C27','post-exit plan','host finalizer','host/startup_finalize.py:63-66','STARTUP_POSTEXIT_PLAN.json',
    'no valid prior finalization','admin entry','1 in once-invocation scope','fixed argv/host time/error scope; schema binding required',
    'host write_text pretty +LF, no fsync guarantee','admin outside ROOT','admin command provenance',True,'exception; no silent re-entry after unresolved final')
add('C28','snapshot exporter','post-exit Root admin','startup_lifecycle.py:493-510','control/startup_snapshot/<raw or native file>',
    'EXPORT_ALLOWED, fresh dest','admin export','old<=4452 conditional; current guard256','current total accepted<=32MiB; production raw not bounded by that check',
    '64KiB copy/hash; no per-copy fsync theorem','admin copy domain','raw + native manifest + native ZIP once per layer',True,'超限即fail; no raw deletion/summary replacement')
add('C29','admin manifest/ZIP','host finalizer','host/startup_finalize.py:109-118','STARTUP_ADMIN_MANIFEST.json / EVIDENCE.zip',
    'quiescent copy list and host/source inputs bound','admin seal','one each under once invocation','raw + native archive + host/source sidecars + manifest; byte closure unresolved',
    'host write_text; ZipFile x; z.read member hashes','admin outside ROOT','administrative archive when complete',True,'partial outputs retained; full success not promised')
add('C30','admin finalization/failure','host finalizer','host/startup_finalize.py:57-61,79-95,119-121','STARTUP_FINALIZATION.json / STARTUP_POSTEXIT_FAILURE.json',
    'post-exit code/audit result','admin final','one final state + at most1 failure under no re-entry','final embeds native_audit with arrays; full size unresolved',
    'host pretty write_text+LF; prior seal validated on reentry','admin outside ROOT','completion receipt; never RESOURCE_GATE_PASS',True,'ADMIN_EVIDENCE_UNRESOLVED and original errors')
add('C31','frontend_abort','host frontend only','host/startup_finalize.py:23-50','FRONTEND_ABORT + manifest + ZIP + receipt',
    'before native bootstrap','pre-native failure alternative','fixed4 outputs; disjoint attempt scope','error<=4096 codepoints, traceback.format_exc lacks aggregate bound',
    'host files; ZIP x','separate host attempt','evidence for that frontend attempt only',True,'no claim about previous runtime; not merged into C09-after-quota path')
add('C32','independent oracles','read-only native reader / unintegrated host reviewers','terminal_evidence.py:193-266; maintenance/archive_oracle.py:inspect',
    'returned review objects / separate research receipts','explicit verification call','read-only or external receipt','native no own persistent record; future extra oracle objects require delta','O(N+B) for admitted capped archive',
    'input streams only; sealer saves review under C18','read-only acceptance/review domain','independent completeness/hash/size/source checks',True,'failure never grants runtime or forces recursive archive')
add('C33','source/cursor/raw original reuse','read-only sealer','guard.py:1019-1026; prior quota proposal','existing C09 state/commit/witness/main/cursor/budget sources',
    'collect full raw set','native/admin reads','one raw pathname per layer; main already in old4450','345148 main conditional;350166 only declared local subset',
    'hash/copy, not regeneration','main / other raw / close sets distinct','preserve all original bytes including partial/staging',True,'missing/foreign/corrupt => UNKNOWN/reject')
add('C34','late native CHECK','Receiver already in observe_exit','c09_handoff.py:261-278','same main c09_events.jsonl',
    'STOP published after precheck; active observation finishes','stop race','current at most one in-flight Receiver call after marker under single-thread role; draft uses its prior slot','<=1322 conditional already main',
    'native append/fsync','main quota, not additional close allowance','raw observation preserved',True,'CLOSED H lock prevents new calls; STOP alone does not erase an in-flight write')
add('C35','Windows active-entry host evidence','Windows foreground parent','host/windows_entry.py:35-60',
    'WINDOWS_ENTRY_PLAN/EXIT, windows_entry.stdout/stderr.raw, STARTUP_FINALIZATION_ERROR.json',
    'active WSL client return and automatic finalizer exception','external TCB exit/admin boundary',
    '4 normal inputs; at most1 extra finalization-error file under once invocation','raw streams and repr/audit_error/embedded preserved audit need aggregate bounds',
    'host write_text; xb streams; finalization-error after failure outside admin ZIP preimage',
    'host_control outside ROOT; old4452 counts copied runtime originals only','host process/entry/error evidence; no runtime PASS',True,
    'native/admin unresolved axes preserved; process.wait itself has no host timeout in this function')
save('CLOSE_PRODUCER_MATRIX.json',{'rows':P,'domains':['main','local quota metadata','runtime close core','other runtime originals','native outputs','external/administrative','research oracle'],
 'no_invented_receiver_exit_file':True,'native_admin_exit_proof_distinct':True,'all_frozen_writers_assumed':True})

# Grammar expressions: constants count JSON syntax; symbols denote encoded tokens.
class N:
    def __init__(self,width):self.width=width
class V:
    def __init__(self,name,extra=0):self.name=name;self.extra=extra
def plus(*args):
    c=0;terms={}
    for a,b in args:
        c+=a
        for k,v in b.items():terms[k]=terms.get(k,0)+v
    return c,terms
def wire(x,pretty=False,depth=0):
    if isinstance(x,N):return x.width,{}
    if isinstance(x,V):return x.extra,{x.name:1}
    if isinstance(x,dict):
        n=len(x)
        if not n:return 2,{}
        key=sum(len(json.dumps(k).encode()) for k in x)
        syntax=2+max(0,n-1)+n+key
        if pretty:syntax+=1+n+2*n*(depth+1)+n+2*depth
        return plus((syntax,{}),*(wire(v,pretty,depth+1) for v in x.values()))
    if isinstance(x,list):
        n=len(x)
        if not n:return 2,{}
        syntax=2+n-1
        if pretty:syntax+=1+n+2*n*(depth+1)+2*depth
        return plus((syntax,{}),*(wire(v,pretty,depth+1) for v in x))
    if type(x)is bool:return 5,{} # conservative any Boolean
    return len(json.dumps(x,ensure_ascii=True).encode()),{}
def expr(x,pretty=False,lf=0):
    c,t=wire(x,pretty);return {'constant_bytes':c+lf,'encoded_token_coefficients':t,'LF':lf,'codec':'indent2 UTF8' if pretty else 'compact ensure_ascii=True'}
stamp={'boottime':N(25),'utc_ns':N(20),'boot_id':'b'*36}
ident={'pid':N(10),'start_ticks':N(20),'boot_id':'b'*36}
window={'T0':N(25),'deadline':N(25),'stop_at':N(25)}
Mprofile=None
for node in ast.parse((RUNTIME/'src/manager_recovery.py').read_text(encoding='utf-8-sig')).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROFILE' for t in node.targets):Mprofile=ast.literal_eval(node.value)
assert Mprofile
state={'status':'AWAIT_EXPECTED_RESUME','boot_id':'b'*36,**window,'launcher_identity':ident,'resume_count':1,
       'expected_launcher_exit':None,'execution_mode':'MR_RECOVERY_DIAGNOSTIC_ONLY','coordinator_identity':ident,'mr_stop_required':False}
normalwait={'schema':'ROOT-IPC-WAITPID/1','child':ident,'coordinator':ident,'raw_wait_status':N(11),'exit_code':N(11),'state':state,'sample':stamp}
fallbackwait={'schema':'ROOT-IPC-WAITPID/1','child':ident,'coordinator':ident,'raw_wait_status':N(11),'exit_code':N(11),'sample':stamp,'reason':'COORDINATOR_EXCEPTION'}
aborting={'phase':'ABORTING','first_failure_sha256':'a'*64,'sample':stamp}
external={'actor':ident,'batch_id':'batch14','sample':stamp}
budget_names=('visits.bin','visits.bin.intent.json','visits.bin.journal.jsonl')
good={'sha256':'a'*64,'bytes':N(20)};bad={'status':'UNKNOWN','error':V('T')}
budget_outer=wire({k:V('item') for k in budget_names})
notes_prefixes=['STOP_PUBLISH:','STATE_UNKNOWN:','FAILURE_PERSIST:','PRIMARY_CLEANUP:','CLOSED_FALLBACK:','EXTERNAL_STOP:']
note_prefix=max(map(len,notes_prefixes))
roles={'known_other_roles_exited':False,'delegated_to_owner':False,'owner_exit_pending':False,'local_child_reap_pending':False,
       'targets':[{'identity':ident,'exit_observed':False} for _ in range(2)],'error':V('T')}
cleanup={'schema':Mprofile,'phase':'CLEANUP','status':'CLOSED_CLEANUP_CONFIRMED','closed':False,'payload_empty':False,
  'other_roles':roles,'first_failure_sha256':'a'*64,'errors':[V('T',note_prefix) for _ in range(10)],
  'budget_after':V('B'),'sample':stamp,'caller_exit_pending':False}
first={'schema':Mprofile,'reason':V('R'),'error_type':V('T'),'error':N(24578),'expected_diagnostic':False,
  'sample':stamp,'batch_id':'batch14','actor':ident,'window':window,'budget':V('B')}
cg_values=('pids.current','pids.max','pids.events','memory.current','memory.peak','memory.max','memory.swap.max',
           'memory.events','memory.oom.group','cgroup.events','cgroup.procs','cgroup.threads')
cg={'path':'/sys/fs/cgroup/dclr6batch14.slice','filesystem_identity':{'device':N(20),'inode':N(20),'ctime_ns':N(29)},
 'values':{k:V('V'+str(i+1)) for i,k in enumerate(cg_values)},'sample':stamp,'metric':'cgroup charged memory; distinct from RSS'}
stopresult={'empty':False,'stop_exit':N(11),'closure_persistence_error':V('E'),'before_stop_charged_snapshot':cg,
 'peak_scope':'observed charge peak for this group generation; no exact RSS tree peak inferred',
 'after_stop_group_exists':False,'sample':stamp}
stopmarker={'reason':V('R'),'boottime':N(25),'utc_ns':N(20),'boot_id':'b'*36}
source_reason='MR_CRITICAL:C09_PENDING_ALLOWANCE_EXHAUSTED'
assert len(source_reason)==43
marker189=expr({**stopmarker,'reason':source_reason},True)['constant_bytes'];assert marker189==189
schema={
 'STOP_or_CLOSED':expr(stopmarker,True),'quota_marker_fixed43':marker189,
 'ABORTING':expr(aborting),'external_closing':expr(external),'first_failure':expr(first),
 'cleanup_state_upper_superset':expr(cleanup),'cleanup_attempt_line_upper_superset':expr(cleanup,lf=1),
 'stop_result':expr(stopresult,True),'waitpid_normal':expr(normalwait,True),'waitpid_fallback':expr(fallbackwait,True),
 'budget_map_outer':{'constant_bytes':budget_outer[0],'items':3},'budget_good_item':expr(good),'budget_error_item':expr(bad),
 'notes_upper':{'persisted_max_notes':10,'returned_after_failed_persistence_max_notes':11,'max_error_prefix_ascii':note_prefix,
    'mutually_exclusive_state_errors_counted_conservatively':True},
 'symbols':{'R':'encoded JSON reason token incl quotes; no general numeric cap chosen',
 'T':'encoded exception-class-name token incl quotes, at least4 to cover null/optional cases; needs closed TCB class proof or validator',
 'B':'encoded complete3-file budget hash/size/error map, B<=K_outer+3*max(K_good,K_error+T)',
 'E':'encoded repr closure error token incl quotes, at least4 to cover null; no cap in current source',
 'V1..V12':'encoded raw kernel cgroup value tokens incl quotes/null, need exact ABI/TasksMax/file-format bounds'},
 'single_marker_189_scope':'fixed43-byte ASCII reason only; not a bound for BUDGET_HALTED+arbitrary exception text',
 'MR_error_max_codepoints':2048,'MR_error_JSON_content_bytes':24576,'MR_error_token_bytes':24578,
 'numeric_profile':{'clock_JSON_binary64':25,'utc_ns_clock_signed64':20,'pid_positive_int32':10,'start_ticks_u64':20,
   'raw_wait_status_signed32':11,'budget_size_u64':20,'stat_device_inode_u64':20,
   'stat_ctime_ns':29,'stat_ctime_ns_basis':'signed64 time_t seconds multiplied by1e9 plus nanosecond remainder; do not inherit clock_ns20 blindly'},
 'full_close_numeric_bound':None,'status':'CLOSE_RESERVE_UNRESOLVED',
 'source_profiles':'Current closed-source shape, explicit numeric ABI widths and frozen namespace; no new limits implemented'}
save('CLOSE_SCHEMA_BYTE_ALGEBRA.json',schema)
compat=[T for T in range(4,2001) if 16*(998+11*T+69+3*max(106,29+T))<=131072]
assert max(compat)==502
save('MR_CLOSE_ORACLE_COMPATIBILITY.json',{'scope':'conditional A<=16 and the closed cleanup superset schema only',
 'reader':'manager_recovery_oracle.py:12,98','reader_total_bytes':131072,
 'budget_map_formula':'B(T)<=69+3*max(106,29+T)',
 'close_attempt_line_formula':'L(T)<=998+11*T+B(T)',
 'derived_threshold_T_encoded_token_bytes':502,'at502_total':16*(998+11*502+69+3*max(106,29+502)),
 'at503_coarse_total':16*(998+11*503+69+3*max(106,29+503)),
 'threshold_is_new_policy':False,'actual_T_bound_proved':False,
 'meaning':'If the applicable TCB exception-name profile independently proves T<=502, the16-row complete file fits this reader cap. It neither proves the pinned profile nor closes STOP/stop_result/terminal/admin bounds.'})
counts=read(BOUND/'evidence/COUNT_SCOPE_COVERAGE_REVIEW.json')
A=counts['C_abort'];S=counts['C_stop_tree'];Q=counts['C_seal_attempts'];W=2
assert (A,S,Q)==(16,23,7)
save('CLOSE_COUNT_DERIVATION.json',{
 'status':'CONDITIONAL_PROVED_FOR_FROZEN_CALL_GRAPH_COMPONENTS',
 'source_scope':counts['scope'],'assumptions':counts['critical_assumptions'],
 'abort_bound':{'scheduler_two_phases':2*3,'coordinator_two_phases':2*4,'external_two_wrappers':2,'sum':A,
  'note':'conservative wrapper obligations, including once-only outer boot entry; source callees do not recursively re-enter abort'},
 'stop_tree_bound':{'from_abort':A,'coordinator':4,'external':1,'expected_C09':1,'normal':1,'sum':S},
 'seal_attempts':Q,'waitpid_combined_two_phases':W,
 'core_production_attempts':{'expression':'7*A+2*S+W+H','at_A16_S23_W2_H0':7*A+2*S+W,
   'H':'additional budget-halt STOP writes; zero in the declared C09 idle/no-new-budget closing prefix, not a new full-scope workload theorem'},
 'seven_abort_non_stop_tree_slots':['STOP','first_failure','external_closing','ABORTING','fallback_CLOSED','close_attempt_append','final_close_state'],
 'stable_core_path_upper':{'expression':'5 fixed exception targets +2*S stop paths + close_attempts_file1 + waitpidW','value':5+2*S+1+W,
   'excludes':'failed staging, main/quota, MR review, payload exit telemetry, native/admin outputs'},
 'append_close_attempt_rows':A,'close_state_puts':2*A,'STOP_Root_puts':A,'SEAL_ERROR_puts':4,
 'no_source_numeric_close_quota':True,'arbitrary_repeat_API_calls_in_scope':False,
 'old_root_file_count':4450,'old_native_members':4451,'old_admin_originals':4452,'not_new_guard_values':True})

# Formula uses production-attempt sums to upper-bound both total generated bytes
# and retained stable/staging bytes; aliases are not separately counted as files.
save('CLOSE_TOTAL_FORMULA.json',{
 'core_write_bound': 'A*(L_stop(R_mr)+L_first(R,T,B)+L_external+L_aborting+L_stop(R_fallback)+L_cleanup(T,B)+1+L_cleanup(T,B)) + S*(L_stop(R_s)+L_result(E,V)) + W*max(L_waitpid_normal,L_waitpid_fallback) + sum_budget_halt_STOP',
 'retained_core_bytes':'<= generated_core_write_bytes under once/no-retry invocation envelope; partial staging is part of those writes, not a free new copy',
 'all_close_bytes':'core + native-preseal/SEAL_ERROR/disposition + relevant payload exit evidence + required raw external witnesses + independently scoped native/admin outputs',
 'C09_total':'345148 + B_close + B_other_disjoint',
 'previous_local_total':350166,'previous_local_scope':'main + cursor + quota first summary + two markers + declared staging, not full close',
 'partition_rule':'If full B_close includes STOP/CLOSED and quota summary/staging, remove them from B_other/PQ local before summing; budget maps are hash/size receipts, original ledger counted once',
 'N_close_max':None,'B_close_max':None,'B_C09_total':None,
 'blocking_symbols':['R_budget','T_exception_profile','E_close_repr','V_cgroup_profile','TR_terminal_report','payload_timing_and_stdio','native/admin full originals'],
 'conclusion':'CLOSE_RESERVE_UNRESOLVED; no larger close cap selected'})

families=[
 {'id':'A','initial':'same valid handoff, current budget fixed,256 normal missing-witness attempts allowed only by draft',
  'events':['256 full PENDING results retained','draft exhausts and denies new work','single existing abort path plus finite existing wrappers tries close/seal'],
  'state':'revision4 PENDING -> STOP/CLOSED or UNKNOWN','records':'256 PENDING +4 reached stages+ACK =261 main rows; no simultaneous six successful stages. One clean Receiver abort has8 data publications across7 core paths; real waitpid/seal/admin are additional.',
  'bytes':'main<=256*1322+4*948+1028=343252 conservative; full close uses symbolic source formula; local350166 not sufficient for whole chain',
  'budget':'R delta0 during idle observation/close; proposed256 prepay occurred before counter fixation',
  'terminal':'CLOSED only if marker+stop conditions succeed; cleanup/native/admin statuses separately observed',
  'premises':'proposed quota effective only hypothetically, healthy storage/TCB and explicit response bounds for numeric capacity; no native run'},
 {'id':'B','initial':'256 attempts consumed, same handoff','events':['request257','repeat request257 k times'],
  'state':'draft exhausted absorbing; current source may remain revision4 PENDING',
  'records':'draft0 new classifications/0 rejection logs; current source CHECK still possible on each admitted loop',
  'bytes':'draft0 main increment after exhausted; current k*positive row bytes subject to real environment/ABI/time; no newly executed k',
  'budget':'no global debit from original native observation loop','terminal':'draft stops; frozen source may continue until marker/deadline',
  'premises':'distinguish old runtime from proposed contract; no implicit activation'},
 {'id':'C','initial':'quota exhausts while manager/root failure begins; coordinator witness still unpublished',
  'events':['abort attempts first/STOP/ABORTING','primary stop errors or times out','fallback marker/systemctl stop+kill','Root role liveness/exit proof checked','native applicability re-evaluated'],
  'state':'CLOSED marker may coexist with UNKNOWN evidence; parent death may remove future waitpid publication',
  'records':'finite source wrapper envelope16 aborts/23 stops only under frozen no-reentry assumptions; missing parent evidence cannot be invented',
  'bytes':'L_result and SEAL_ERROR/stdio depend on response/error profiles; local main quota supplies none of these automatically',
  'budget':'existing ledger retained, snapshots hash it; no reset/new allowance',
  'terminal':'payload/group may be stopped while native seal stays UNRESOLVED',
  'premises':'fault/cancellation model includes failed manager or coordinator; storage may remain healthy; actual exits need external observation'},
 {'id':'D','initial':'one classification slot reserved near exhaustion','events':['short write or fsync EIO','burn credit','no replay','attempt bounded failure/STOP','use existing external stop/role proof'],
  'state':'deny new work; raw partial/uncertain state preserved','records':'one attempted main write per reserved slot; failed marker may add0 durable records; staging retained',
  'bytes':'logical reservation can be sufficient while durability fails; no numeric disk-success implication',
  'budget':'no refund or reinit; initial failed global prepay leaves existing intent/health semantics',
  'terminal':'process cleanup, internal completeness, native seal and admin seal are separate axes; UNKNOWN valid',
  'premises':'fault storage allowed; no promise of native seal for arbitrary EIO'},
 {'id':'E','initial':'CLOSED exists, native EVIDENCE.zip absent, enough deadline remains; current trusted Root caller',
  'events':['late existing role calls M.abort','writes ABORTING/close_attempt/final state, may write stop_event/result','another existing role repeats before seal'],
  'state':'CLOSED remains; internal status can be rewritten; file namespace still grows',
  'records':'under frozen entry append attempts<=16; in extended API input family E_n, n calls produce n close_attempt rows and up to n stop events/results',
  'bytes':'+sum encoded close_result lines, not suppressed by CLOSED alone; arbitrary E_n lies outside old one-entry count proof',
  'budget':'cleanup itself does not reserve new visits or reset T0',
  'terminal':'eventual native seal requires all writers quiescent; CLOSED+ZIP early return suppresses later abort writes',
  'premises':'extended API family explicitly outside fixed invocation scope; finite n only within storage/representation/deadline environment'}]
assert 256*1322+4*948+1028==343252
save('QUOTA_BOUNDARY_FAMILIES_A_E.json',{'type':'ABSTRACT_SOURCE_BOUND_TRAJECTORIES_NOT_DYNAMIC_REPLAY','families':families})
save('COUNTEREXAMPLE_REGISTER.json',{'rows':[
 {'id':'CE-257','scope':'frozen C09 state machine before quota implementation','family':'missing-witness stutter257','source':'c09_handoff.py:252-278; guard.py:799-805','conclusion':'current source does not enforce draft256; environment finite-prefix caveat retained'},
 {'id':'CE-CLOSED-REPEAT','scope':'general API closure domain; not old frozen invocation domain','family':'E_n with CLOSED but no ZIP','source':'manager_recovery.py:321,366,395; guard.py:759,769','conclusion':'CLOSED alone is not an append bound; old16-call premise still bounds frozen execution'},
 {'id':'CE-STOP-RACE','scope':'two existing aborting roles','family':'both test STOP absent before either publish','source':'manager_recovery.py:328 outside mr_close lock','conclusion':'same STOP pathname may be overwritten twice, not two distinct raw files'},
 {'id':'CE-CLOSE-IO','scope':'allowed storage failure','family':'last PENDING durable then STOP/CLOSED write or fsync returns EIO','source':'guard.py:760-765; manager_recovery.py:328-399','conclusion':'logical quota cannot guarantee durable evidence; no claim storage fault must defeat process stop'},
 {'id':'CE-EIO-NO-MARKER','scope':'existing process-local halt plus failed shared marker','family':'one actor sets its own _HALTED, STOP publication fails before a shared marker/ambiguous intent exists; another actor still sees an otherwise healthy ledger','source':'guard.py:52,82-87,288; manager_recovery.py:326-329','conclusion':'local HALTED alone is not a global cross-process stop proof; current supervision/marker/intent/role exits must be observed independently'},
 {'id':'CE-PARENT-WITNESS','scope':'coordinator/root failure during actual C09 handoff','family':'parent dies/gets killed before guard1225 waitpid publication; payload group stops','source':'guard.py:1225-1227; manager_recovery.py:291-313; terminal_evidence.py:129-141','conclusion':'exit/group empty may be true while required raw parent witness is missing; native readiness remains false/UNKNOWN'},
 {'id':'CE-SEAL-TEXT','scope':'interface fault-response model only; actual pinned systemctl output attainability unverified','family':'G._run nonzero stderr m ASCII bytes at G.seal STOP query; m=400000 illustrative','source':'guard.py:718-721,1006,1149,1275','conclusion':'unbounded diagnostic text is carried into exception/SEAL_ERROR; local350166 has no such field allocation; no new native reachability or physical infinity claim'},
 {'id':'CE-HASH-RACE','scope':'omitted quiescence premise','family':'hash file then late append then ZIP reads newer bytes','source':'guard.py:1022-1025','conclusion':'writer quiescence is necessary beyond count and CLOSED presence'}],
 'no_fault_injection':True,'finite_storage_and_off_t_caveat':True})

# Exact native manifest grammar with an explicit name/ABI envelope, not an approved cap.
def compact_native_manifest(n):
    return {'files':{chr(97+i):{'bytes':0,'sha256':'a'*64} for i in range(n)},'sample':{'boottime':0,'utc_ns':0,'boot_id':'b'*36}}
def plen(x):return len(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2).encode())
m1=plen(compact_native_manifest(1));m2=plen(compact_native_manifest(2));increment=m2-m1
K=4450;F=1535;D=19
manifest_upper=m1+(K-1)*increment+K*((F-1)+(D-1))+24+19
H=22+(K+1)*(92+2*F)
U=33554432
deflate_U=U+(U>>12)+(U>>14)+(U>>25)+13*(K+1)+H
save('MANIFEST_ZIP_BOUND_ARITHMETIC.json',{
 'profile':'current pretty manifest, closed ASCII names<=1535, file size signed64 off_t decimal<=19, fixed stamp widths25/20',
 'one_row_skeleton':m1,'per_additional_one_char_row':increment,'formula':'m1+(N-1)*increment+N*(F-1+D-1)+43',
 'N':K,'F':F,'D':D,'conditional_native_manifest_upper':manifest_upper,
 'manifest_accept_cap':4194304,'coarse_bound_above_cap_is_not_an_attainability_proof':True,
 'ZIP32_headers_at4451':H,'at_accepted_uncompressed_U32MiB_ZIP_STORED_upper':U+H,
 'at_accepted_U32MiB_deflate_conditional_upper':deflate_U,
 'deflate_condition':'pinned zlib default parameter compressBound-style proof required; compression not assumed reducing data',
 'generator_R_raw_upper':None,'current_accepted_zip_compressed_and_uncompressed_caps':33554432,
 'raw_off_t64_representation_upper':K*((1<<63)-1),'representation_is_resource_contract':False,
 'whole_memory_FD_IO_bound':'UNRESOLVED'})

save('ARCHIVE_RECURSION_REVIEW.json',{
 'native':'guard.seal excludes by basename EVIDENCE_MANIFEST.json/EVIDENCE.zip then adds current manifest once; fixed writers must avoid nested basename collision',
 'admin':'post_exit_export includes raw plus native manifest+nativeZIP once; control/startup_snapshot lies outside ROOT',
 'host':'host finalizer rows are snapshot entries +10 named host sidecars +4source locks; adds own admin manifest once; finalization receipt and windows_entry finalization-error output outside preimage',
 'oracle':'terminal reader is read-only; one saved terminal review before native list. Maintenance archive oracles unintegrated, no automatic recursive publication',
 'fault_reports':'SEAL_ERROR and disposition may be created before sealing/defer. Bounded wrappers do not auto-run until success; partial archive/defer remains UNKNOWN',
 'TCB':'once activation/resume, closed writers, stable namespace, trusted Root/kernel/storage; externally injected archive/report loops excluded',
 'conditional_DAG':'RAW -> native_manifest -> nativeZIP -> admin_copy -> admin_manifest -> adminZIP -> final_receipt; no current producer feeds admin outputs back into ROOT',
 'no_current_auto_recursive_archive':True,'cross_instance_certificate':'still external to A archive preimages and PROPOSED_NOT_EFFECTIVE'})
nodes=['main_raw','close_core','other_raw','terminal_review','native_manifest','native_ZIP','admin_snapshot',
       'host_entry_streams','admin_audit','postexit_stdout','postexit_stderr','source_locks','admin_manifest','admin_ZIP',
       'finalization_receipt','finalization_error','research_oracle_receipt','future_MR_certificate']
edges=[['main_raw','native_manifest'],['close_core','native_manifest'],['other_raw','native_manifest'],['terminal_review','native_manifest'],
       ['native_manifest','native_ZIP'],['main_raw','native_ZIP'],['close_core','native_ZIP'],['other_raw','native_ZIP'],['terminal_review','native_ZIP'],
       ['native_ZIP','admin_snapshot'],['native_manifest','admin_snapshot'],['main_raw','admin_snapshot'],['close_core','admin_snapshot'],
       ['other_raw','admin_snapshot'],['terminal_review','admin_snapshot'],['native_ZIP','admin_audit'],['admin_audit','postexit_stdout'],
       ['admin_snapshot','postexit_stdout'],['admin_snapshot','admin_manifest'],['host_entry_streams','admin_manifest'],
       ['admin_audit','admin_manifest'],['postexit_stdout','admin_manifest'],['postexit_stderr','admin_manifest'],['source_locks','admin_manifest'],
       ['admin_manifest','admin_ZIP'],['admin_snapshot','admin_ZIP'],['host_entry_streams','admin_ZIP'],['admin_audit','admin_ZIP'],
       ['postexit_stdout','admin_ZIP'],['postexit_stderr','admin_ZIP'],['source_locks','admin_ZIP'],['admin_ZIP','finalization_receipt'],
       ['postexit_stdout','finalization_receipt'],['admin_audit','finalization_error'],['admin_ZIP','research_oracle_receipt'],
       ['native_ZIP','future_MR_certificate'],['admin_ZIP','future_MR_certificate']]
indegree={n:0 for n in nodes}
for a,b in edges:indegree[b]+=1
order=[];queue=[n for n in nodes if indegree[n]==0]
while queue:
    a=queue.pop(0);order.append(a)
    for u,v in edges:
        if u==a:
            indegree[v]-=1
            if indegree[v]==0:queue.append(v)
assert len(order)==len(nodes)
save('EVIDENCE_LAYER_DAG.json',{'abstraction':'source-bound producer-family DAG, not a replay of the old1142-node graph or protocol execution',
  'nodes':nodes,'edges':edges,'topological_order':order,'acyclic':True,
  'conditional_cycle_examples':[['admin_ZIP','finalization_receipt','admin_ZIP'],['native_manifest','native_ZIP','native_manifest']],
  'cut':'outputs/receipts/certificates remain outside their own hash/archive preimages',
  'temporal_scope':'first successful quiescent native build then admin; reports created after failed/partial seal belong to a later raw/admin phase and do not retroactively enter the consumed native preimage',
  'failed_native_is_complete':False})
save('FULL_CAPACITY_GAP_TABLE.json',{'count_status':'COUNT_BOUND_PROVED_CONDITIONALLY_FOR_OLD_SCOPE',
 'byte_status':'UNRESOLVED_FOR_RESOURCE_COMPATIBLE_GENERATION','work_status':'PARTIAL_FOR_ADMITTED_INPUT_ONLY',
 'wall_status':'WALL_TIME_BOUND_UNRESOLVED',
 'gaps':[
 {'id':'G01','producer':'native C09 event','site':'c09_handoff.py:277','missing':'source observation quota and widths; draft not effective'},
 {'id':'G02','producer':'Root/payload budget halt STOP','site':'guard.py:84','missing':'encoded reason width, per-actor halt/write envelope and simultaneous active writers'},
 {'id':'G03','producer':'stop_result','site':'guard.py:766-769','missing':'E repr and12cgroup values/kernel ABI profiles; overall stop memory/FD/time'},
 {'id':'G04','producer':'MR first/cleanup','site':'manager_recovery.py:355,390','missing':'R/T exception profile, roles/error encoded bounds andB map; failure dissemination across roles'},
 {'id':'G05','producer':'SEAL_ERROR','site':'guard.py:1149,1275','missing':'repr width; helper stderr and parser/TCB exception response contracts'},
 {'id':'G06','producer':'terminal review','site':'terminal_evidence.py:259-263','missing':'nested returned evidence including read error records, waitpid state and hashes; output byte validator'},
 {'id':'G07','producer':'payload timing/stdout/stderr','site':'guard.py:62-76,902; startup_finalize.py:65-85','missing':'raw repr/traceback/capture/host streams byte aggregates'},
 {'id':'G08','producer':'readiness/RootIPC/MR/S1-S9','site':'service_readiness.py;root_ipc.py;range_fixtures.py','missing':'accepted per-record caps vs generated union/temporary aggregate'},
 {'id':'G09','producer':'global andlocal journals','site':'guard.py:624-628;range_core.py:80-85','missing':'generation byte ceiling matching32MiB accepting checker and required receipts'},
 {'id':'G10','producer':'F1/F4 serialization','site':'f1_model.py;f4_dp.py;run_batch.py','missing':'state/strategy/trace/report encoded bytes and peak allocations'},
 {'id':'G11','producer':'manifest/nativeZIP','site':'guard.py:1019-1027','missing':'resource-compatible R_raw; pinned compression expansion; raw hash materialization andcentral-directory memory'},
 {'id':'G12','producer':'admin audit/export/finalization','site':'startup_lifecycle.py:441-519;startup_finalize.py:87-121','missing':'ambient /proc roles, repeated native audit views, raw/copy/nested archive+host stream sums'},
 {'id':'G13','producer':'future quota integration/tests/oracles','site':'previous proposed quota only','missing':'file/byte/visit deltas, exact closing owner and preflight physical storage/cleanup assumptions'},
 {'id':'G14','producer':'all fsync/manager/scheduler','site':'multiple','missing':'worst syscall/scheduling/disk latency; finite work does not certify300s/5s/30s'},
 {'id':'G15','producer':'Windows finalization error','site':'host/windows_entry.py:50-60','missing':'after-archive receipt/error bytes, repr andembedded preserved audit; no folding into old4452 runtime-copy count'}],
 'old_guards_unchanged':[256,257],'capacity':'CAPACITY_CONTRACT_NOT_READY'})

# Versioned review drafts carry unresolved fields as null, never guessed caps.
(OUT/'proposals').mkdir(exist_ok=True)
fields=[
 ('raw_count','old4450 conditional scope; new integration/tests delta needed',4450,'CONDITIONAL_PROVED'),
 ('native_member_count','old4451; no new guard selected',4451,'CONDITIONAL_PROVED'),
 ('admin_export_count','old4452; nativeZIP duplicated only at admin layer',4452,'CONDITIONAL_PROVED'),
 ('uncompressed_total','resource-compatible generated raw/native/admin totals missing',None,'UNRESOLVED'),
 ('archive_total','R_raw and codec/metadata/nesting/host inputs missing',None,'UNRESOLVED'),
 ('single_file_bytes','only component widths and representation/accepted caps available',None,'PARTIAL'),
 ('main_PENDING','256 attempts/263rows/345148bytes, prior v2 not effective',345148,'CONDITIONAL_PROVED'),
 ('close_reserve','160+H core attempt model is not a full retained-byte quota',None,'UNRESOLVED'),
 ('manifest_index','native coarse profile7436121 vs4MiB accepted cap; no tight actual family sum',None,'PARTIAL'),
 ('verification_memory_work','accepted O(N+B); full builders/helpers/CPython peak and FD unresolved',None,'PARTIAL'),
 ('overflow','deny further work; preserve emitted raw; existing stop/UNKNOWN remains',None,'PARTIAL'),
 ('missing_unknown','no exit/durability/seal assertion from incomplete evidence',None,'PROVED'),
 ('independent_integrity','raw member set/hash/size/source/boot binding required; no new native check',None,'PARTIAL'),
 ('old_guard_isolation','256/257 unchanged; new approved version isolated',None,'PROVED'),
 ('effectiveness','explicit approval + precise isolated implementation/review + new execution authority',None,'BLOCKED')]
contract={'schema':'DCL-CLOSE-CAPACITY-REVIEW/1-DRAFT','version':'CloseReserve-Closure/review-1',
 'status':'CAPACITY_CONTRACT_NOT_READY','user_approved':False,'runtime_enabled':False,'effective':False,
 'scope':'source-bound review, no implementation, no guard expansion, no activation',
 'fields':[{'field':k,'basis':b,'candidate_component_or_old_value':v,'status':s} for k,b,v,s in fields],
 'new_total_raw_cap':None,'new_total_archive_cap':None,'new_close_reserve_cap':None,
 'unresolved_required_for_approval':[g['id'] for g in read(E/'FULL_CAPACITY_GAP_TABLE.json')['gaps']],
 'count_inheritance':'old fixed full scope only; future quota and tests produce explicit set/byte/visit deltas',
 'MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE','RESOURCE_GATE_PASS':'NOT_OBTAINED',
 'F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','IMPLEMENTATION_GATE':'CLOSED'}
(OUT/'proposals/CAPACITY_REVIEW_DRAFT.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
close_review={'schema':'DCL-CLOSE-RESERVE-REVIEW/1-DRAFT','status':'CLOSE_RESERVE_UNRESOLVED','version':'CloseReserve-Closure/review-1',
 'user_approved':False,'effective':False,'runtime_enabled':False,'source_core_attempts_H0':160,'source_core_path_bound_no_staging':54,
 'source_append_attempts_frozen':16,'close_reserved_bytes':None,
 'old_main_proposal_sha256':sha(PREV/'proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json'),
 'old_main_bound':345148,'old_local_subset':350166,
 'newly_calculated_components':{'ABORTING':schema['ABORTING'],'external_closing':schema['external_closing'],
   'waitpid_normal':schema['waitpid_normal'],'waitpid_fallback':schema['waitpid_fallback'],'stop_result':schema['stop_result']},
 'full_sufficiency':'not established; byte/io/exception/TCB/storage and exit-evidence obligations remain',
 'unchanged_contracts':['budget core','256/257','native seal','admin finalizer','MR cross-instance rule']}
(OUT/'proposals/CLOSE_RESERVE_REVIEW_DRAFT.json').write_text(json.dumps(close_review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save('GENERAL_G_COMPARISON.json',{'input_family':'one valid handoff with n missing-witness observations, finite close calls, concurrent fault or IO failure',
 'metric':['retained raw/close bytes','write/fsync work','at-most-once credits','evidence completeness under declared faults'],
 'strong_G':'bounded WAL/prepaid slots + serialized idempotent closure + independent reserved storage/emergency channel + standard manifest/archive',
 'predicted_strict_gap':0,'strict_more_cost_example_for_G':None,'status':'COVERED_BY_G','STRICT_SEPARATION_INSTANCES':0,
 'IMPLEMENTATION_GATE':'CLOSED','mechanism_code_written':0})
namespace_files=[]
for base in [RUNTIME/'src',RUNTIME/'host']:
    for p in sorted(base.glob('*.py')):
        if any(s in p.read_text(encoding='utf-8-sig') for s in ('ra01','batch14','dclr6batch14')):
            namespace_files.append(p.relative_to(RUNTIME).as_posix())
save('FUTURE_CHANGE_SCOPE.json',{
 'status':'REVIEW_REQUEST_MATERIAL_ONLY_NOT_AUTHORIZED','implementation_now':False,
 'minimum_behavioral_candidates':[
 {'file':'src/c09_handoff.py','functions':['event','publish','sender_prepare','Receiver.observe_exit'],
  'contract_change':'prior v2 predebit/completion/7 lifecycle bits/terminal latch, exact fields and bounded no-log rejection; no dynamic handoff'},
 {'file':'src/guard.py','functions':['request_stop','halt_budget','stop_tree','_run','seal error writer call sites'],
  'contract_change':'derive and explicitly approve response/encoded error/stop profiles and safe retained raw overflow behavior; no guessed cap or safety bypass'},
 {'file':'src/manager_recovery.py','functions':['abort','budget_snapshot','_stop_other_roots'],
  'contract_change':'bounded shared closing responsibility, finite per-role attempts, failure dissemination, fixed typed close schemas; no cross-instance admission changes'}],
 'conditional_full_capacity_consumers':[
 {'file':'src/terminal_evidence.py','reason':'only if approved close schema changes reader requirements; preserve terminal read-only/UNKNOWN and existing257 guard'},
 {'file':'src/startup_lifecycle.py','reason':'actual admin audit/report aggregate and ambient role scan bounds require separate derived contract'},
 {'file':'host/startup_finalize.py','reason':'raw streams/nested export/final receipt proof needs separate evidence and explicit authority; preserve256 guard until approved version'},
 {'file':'host/windows_entry.py','reason':'active-entry raw streams, post-finalizer exception receipt and host wait need separate source/byte/termination bounds'},
 {'file':'src/root_ipc.py','reason':'only if new targets cannot use existing Root-private BC.Store; permissions/durability semantics remain protected'}],
 'private_quota_target_option':'BC.Store private .json namespace may reuse existing helper; otherwise new path-policy delta explicitly reviewed. No helper is changed in this task.',
 'inputs_to_refreeze':['inputs/c09_contract.json','inputs/manager_contract.json','inputs/batch_identity.json',
  'inputs/static_manifest.json','inputs/execution_lock.json','inputs/runtime_tree_lock.json',
  'proposed new inputs/c09_quota_contract.json','proposed new inputs/close_reserve_contract.json',
  'affected startup/terminal/readiness/phase/runtime contracts only where dependency hashes/schema change'],
 'namespace_literal_files_requiring_exact_AST_review':namespace_files,
 'scope_exclusions':['budget reservation core semantics','old frozen directory bytes','old budget/T0/reopening',
   '256/257 guard expansion','MR cross-instance activation','WSL/native fault/model runs'],
 'prerequisites':['numeric missing profiles resolved from actual source/TCB, not invented limits','explicit next-stage maintenance authority and research-gate applicability',
 'new isolated identity/source/input/lock','all file/byte/visit/IO/test deltas and raw-oracle coverage'],
 'dynamic_authority':False})
save('PROPOSAL_BINDINGS.json',{'capacity':row(OUT/'proposals/CAPACITY_REVIEW_DRAFT.json'),
 'close':row(OUT/'proposals/CLOSE_RESERVE_REVIEW_DRAFT.json'),
 'MR_original_rule':row(BOUND/'proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json'),
 'PENDING_original_v2':row(PREV/'proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json'),
 'all_approval_or_activation':False})

print(json.dumps({'producer_rows':len(P),'call_sites':len(calls),'core_attempt_bound_H0':7*A+2*S+W,
 'core_path_bound':5+2*S+1+W,'manifest_upper':manifest_upper,'close_bytes':'UNRESOLVED','runtime_runs':0}))
