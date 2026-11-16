"""Source-bound close evidence, algebra and declarative test specifications.

No target imports, business/model execution, allocator, patch or fault replay.
"""
from pathlib import Path
import ast
import json
from READ_INPUTS import ROOT, PREVIOUS, OUT, E, RUNTIME, read, sha, record, save

assert read(E/'INITIAL_CHECK.json')['frozen_source_inputs'] == 64
spec = {
    'src/c09_handoff.py': [(18,53),(75,89),(115,134),(252,347)],
    'src/guard.py': [(52,100),(121,124),(280,288),(597,691),(749,824),(993,1027),(1198,1281)],
    'src/manager_recovery.py': [(32,60),(79,82),(266,430)],
    'src/root_ipc.py': [(21,48),(71,155)],
    'src/boot_continuity.py': [(65,110),(406,446)],
    'src/terminal_evidence.py': [(121,186),(193,266)],
    'src/startup_lifecycle.py': [(327,368),(386,519)],
    'host/startup_finalize.py': [(52,121)],
    'host/windows_entry.py': [(35,66)]}
excerpts = {}
for relative, intervals in spec.items():
    lines = (RUNTIME/relative).read_text(encoding='utf-8-sig').splitlines()
    excerpts[relative] = [{'start':first,'end':min(last,len(lines)),
                          'lines':[{'line':number,'text':lines[number-1]} for number in range(first,min(last,len(lines))+1)]}
                         for first,last in intervals]
save('CURRENT_SOURCE_EXCERPTS.json', excerpts)

nodes = []
def node(key, function, caller, result, conditions, locks, records, budget, failure):
    nodes.append(dict(zip(['id','function','caller','return_or_result','preconditions','lock_state',
                           'possible_records','budget_effect','failure_exit'],
                          [key,function,caller,result,conditions,locks,records,budget,failure])))
node('CG01','guard.main:1283 / external_stop:813','frozen external-stop role entry','normal exit code or exception',
     'Root current source/identity/authorization','none','existing stderr and final sealer outcome','no initialization by close path','top-level traceback/exit status')
node('CG02','guard._external_stop_impl:771,799-800','external_stop','observe_exit result',
     'STOP_ARMED role, valid coordinator/sender identity, sender pidfd readable','no H lock at call site','STOP_ARMED already exists','no observe-loop global debit','except806 calls first abort')
node('CG03','Receiver.observe_exit:252,254-261','guard800','CLOSED/VERIFIED/PENDING or exception',
     'current state and binding; quota gate is proposed','H exclusive lock','optional first EXIT_OBSERVED stage','proposed local debit only','context unwinds before caller except')
node('CG04','proposed quota gate before facts/classify','observe_exit proposed layer','new slot or denied/exhausted',
     'identity, current stop state, cursor binding/remaining token','H held','cursor predebit, raw input references','burn slot on uncertain outcome','fixed AdmissionBlocked proposal, no classified257')
node('CG05','classify:18 / observe_exit276 / event277','admitted observe_exit','PENDING/VERIFIED/FAILED',
     'one admitted classification','H held','full CHECK with raw facts, main LF/fsync','local allowance already reserved','write/fsync errors preserve partial bytes and leave uncertainty')
node('CG06','lifecycle_lock:40-53 context exit','observe_exit return/raise','unlock then close fd under normal syscall semantics',
     'valid acquired fd and trusted kernel flock','H released before outer caller catches','none','none','unlock/close error or death handled as distinct failure responsibility')
node('CG07','guard808 M.abort first layer','except806','cleanup result or propagated error',
     'H context already exited','MR close lock in record stages; H re-acquired only by stop path','STOP, first, delegate, ABORTING, marker/result, attempts/final','ledger read snapshots, no new visit','original exception re-raised809 or abort error propagates')
node('CG08','guard817 M.abort second layer','external_stop815','cleanup result or propagated error',
     'first layer returns/raises into outer exception','same finite MR/H lock pattern','may append/rewrite while CLOSED and noZIP','no close-path global visit','raise818 then finally sealer branch')
node('CG09','M.abort328 / guard.request_stop545','both abort layers','shared cancellation file when persistence succeeds',
     'STOP absent check occurs before mr_close lock','RootIPC file publication, not H serialization here','out/STOP_REQUEST.json, random private staging','no debit','STOP_PUBLISH note, shared marker may remain absent')
node('CG10','M.abort355-366','valid Root abort','first/delegate/intermediate data',
     'current boot/window or terminal fallback authority','mr_close.lock; first exclusive O_EXCL','mr_first_failure, mr_external_closing, mr_close_state ABORTING','budget_before hash/size map embedded','FAILURE_PERSIST note, no guarantee record saved')
node('CG11','M.abort372 / guard.stop_tree749','primary cleanup','group empty result if confirmed',
     'enough remaining existing window','H lock around CLOSED/event publication, then released','CLOSED or new stop_event; stop_result','none','marker errors recorded, manager fallback/UNKNOWN')
node('CG12','M._stop_other_roots291-313','abort385','known_other_roles_exited and target facts',
     'protected registry and exact pidfd identity','no H lock while waiting/signalling','facts embedded in attempt/final state','none','ROLE_EXIT_UNKNOWN or targets not exited')
node('CG13','guard1225 or1255 waitpid publication','actual direct parent','raw wait status / code or missing witness',
     'parent alive and child genuinely reaped','RootIPC publication','waitpid_<child>.json; C09 witness only before stopped','none','parent loss/missing storage => UNKNOWN, no fabricated status')
node('CG14','M.abort390-400','post-cleanup','CLOSED_CLEANUP_CONFIRMED or UNKNOWN','marker/group/role observations',
     'mr_close.lock','mr_close_attempts line, replacement final state; caller_exit_pending=true','budget_after snapshot','FINAL_EVIDENCE note may only reach returned object')
node('CG15','external_stop819-823 / M.seal414 / G.seal993','outer finally','native digest or defer/error',
     'CLOSED/group empty/other-role exits, read-ready evidence','mr_seal lock; terminal reader locks','terminal review/disposition/manifest/ZIP as applicable','read-only budget','native UNRESOLVED/partial; MR_SEAL_UNKNOWN stderr')
node('CG16','P.post_exit_export412 / host.finalize52','host after active client exit','admin/cleanup/native axes',
     'new admin command authorized by prior run; actual quiescence','read-only runtime inputs','audit/copy/host streams/admin manifest/ZIP/final receipt','no T0 or budget creation','DEFERRED/UNKNOWN or failed admin archive')
node('CG17','observe_exit281-295 / resume_admission323-347','VERIFIED branch and admitted resumed scheduler',
     'VERIFIED then optional source-approved RESUMED progression',
     'genuine witness/ACK/resource checks and original once-resume predicates',
     'H released before stop_tree(close=False), reacquired for verified/resumed publication',
     'stop_result; handoff state; result_C09; batch_state; two stage rows already inmain',
     'handoff counter conserved until admitted resume; later legitimate work belongs its own budget',
     'existing exception wrappers, incomplete handoff/UNKNOWN if cleanup or publication fails')
node('CG18','guard803-804 existing CLOSED result','observe_exit stopped return','stop_tree(close=False), exit125',
     'genuine STOP/CLOSED absorption observed at255','H released before cleanup',
     'stop_result if generated, no CLOSED publication at this specific close=False call',
     'no grant','existing wrappers/finally; a fabricated CLOSED return lacks this precondition')
save('B1_CLOSE_CALL_GRAPH.json', {'nodes':nodes,'edges':[
    ['CG01','CG02'],['CG02','CG03'],['CG03','CG04'],['CG04','CG05'],['CG05','CG06'],
    ['CG06','CG07'],['CG07','CG08'],['CG07','CG09'],['CG08','CG09'],['CG07','CG10'],
    ['CG08','CG10'],['CG10','CG11'],['CG11','CG12'],['CG12','CG14'],['CG08','CG15'],['CG15','CG16'],
    ['CG06','CG17'],['CG06','CG18'],['CG18','CG15']],
    'edge_conditions':{'CG06->CG07':'only exception branch','CG06->CG17':'only VERIFIED branch',
                       'CG06->CG18':'only genuine stopped/CLOSED branch',
                       'CG06->CG02':'ordinary PENDING returns to polling; proposed exhaustion must end this repetition'},
    'parent_side_node':'CG13 is independent of Receiver ordering and may never publish if parent lost',
    'selected_semantics':'fixed existing AdmissionBlocked after last completePENDING and proposed cursor finalization, H unwinds, then existing808/817 exception chain',
    'alternatives':{
        'A_return_EXHAUSTED':'Current801-805 leaves this value unconsumed. Same ready pidfd can re-enter, with no quota-local iteration bound before other deadlines/exceptions. Actual extra classify/event behavior depends on the proposed gate.',
        'B_map_to_CLOSED':'close=False still attempts payload stop/empty confirmation but creates no CLOSED in that call and does not run the MR root/first-failure/shared-marker chain at this site.',
        'C_fixed_exception':'Ends current observation while; lock context exit precedes first abort; at most two Receiver abort entries; storage/exits/evidence still separately proved'},
    'statuses':{'VERIFIED':'existing successful handoff state','CLOSED':'existing stopped marker absorption, may be STOP or CLOSED',
                'EXHAUSTED':'proposed resource state, no native return branch currently','exception':'existing error control flow','UNKNOWN':'evidence/cleanup uncertainty, no handoff success'},
    'lock_release_condition':'Normal valid-fd flock unlock/close semantics. Failure of these calls or delayed kernel process exit does not mint a released-lock fact.'})

required = []
def req(key, fact, tier, carrier, producer, timing, persistence, repeat, main, external, loss, reason):
    required.append(dict(zip(['id','fact','tier','existing_or_proposed_carrier','producer','when','persistence',
                              'repeat_rule','main_log','independent_source','on_loss','necessity'],
                             [key,fact,tier,carrier,producer,timing,persistence,repeat,main,external,loss,reason])))
req('RE01','batch/boot/handoff/source/input/authorization identity','B1_SAFETY',
    'c09_handoff.json/window, STOP_ARMED, protected namespace and proposed cursor','existing Root roles and proposed B1 cursor','before admission',
    'retain originals and exact digest links','one current binding, no fresh generation on recovery','main references same binding',
    'trusted source/input lock + kernel boot/PID tuple','reject/UNKNOWN','prevents foreign quota/exit/marker reuse')
req('RE02','quota exhaustion and last raw observation','B1_SAFETY',
    'existing c09_events.jsonl plus proposed cursor','Receiver','full256th PENDING then exhaustion latch',
    'append/fsync and cursor completion under declared model','one reserved token per actual observation','already part of345148',
    'raw independent re-count and source provenance','UNKNOWN if partial/unproven','ties resource stop to actual consumed work and facts')
req('RE03','first failure cause/actor/window/budget_before','B1_SAFETY',
    'mr_first_failure.json','M.abort355-361','first eligible close caller',
    'Root600 exclusive under mr_close lock','first successfully published file; errors may prevent success','independent file',
    'captured original input/exception plus protected source','UNKNOWN','immutable first incident cause')
req('RE04','shared cancellation','B1_SAFETY','out/STOP_REQUEST.json','M.abort328/guard546','before cleanup',
    'RootIPC metadata, file/directory fsync when successful','path can be overwritten by racing calls','independent file',
    'equivalent approved shared source currently uninstantiated','no shared cancellation proof','stops other actors without relying on process-local_HALTED')
req('RE05','ABORTING transition','B1_SAFETY_WRITE_COST',
    'mr_close_state.json intermediate version','M.abort366','before cleanup',
    'source writes an intermediate version, later replacement allowed','same pathname as final state','independent file alias',
    'source-order proof plus failure staging if retained','intermediate history unknown if overwritten','must budget actual write while avoiding a fictitious separate stable record')
req('RE06','CLOSED and repeat close events','B1_SAFETY','CLOSED.json / stop_event_<pid>_<ns>.json','stop_tree/fallback','under H lock before/while stop',
    'Root protected metadata and completed barriers','CLOSED one path, additional events finite by call graph','independent files',
    'approved equivalent cancellation/terminal carrier absent','UNKNOWN','absorbing stop identity and close reason')
req('RE07','payload stop and group-empty confirmation','B1_SAFETY',
    'stop_result files and final MR payload_empty','Root stop_tree and M.abort','after manager stop and observed cgroup empty',
    'retain source raw result and scope/generation identity','one per actual stop call, unique-path upper','independent files',
    'fresh trusted cgroup/systemd proof may supply equivalent observation','resource cleanup UNKNOWN','CLOSED marker alone is insufficient for actual reclamation')
req('RE08','other controlled Root role exits','B1_SAFETY',
    'MR other_roles target facts, registry, last main exit_observed','Receiver/Root via pidfd and exact identity','during cleanup',
    'stored attempt/final facts linked to originals','at most protected child/owner set for each call','facts embedded in MR records',
    'fresh trusted pidfd/systemd identity-bound raw observations','other-role cleanup UNKNOWN','records kernel-observed target exit rather than return-code inference')
req('RE09','closing Receiver own exit','B1_SAFETY_EXTERNAL',
    'no dedicated guaranteed pre-arranged external receipt in current B1; postexit audit may observe later','independent trusted guardian/systemd/host source to be bound',
    'after Receiver exits','external channel/retention must be explicitly guaranteed','one identity-bound final outcome, bounded provider attempts','outside main',
    'external provider currently null','caller-exit UNKNOWN','caller cannot write a durable post-mortem self-exit receipt before it exits')
req('RE10','direct waitpid or equivalent exit outcome','B1_SAFETY_AND_NATIVE',
    'waitpid_<child>.json / C09 exit_witness when available','actual direct parent','real waitpid before parent loss',
    'RootIPC raw status and identities','one per phase, exhaustion phase<=1','outside main',
    'pidfd can prove process gone for resource-close; exact23 handoff status still needs its source','exact code/native readiness UNKNOWN','resource-close and successful expected handoff use distinct evidence obligations')
req('RE11','final budget conservation','B1_SAFETY',
    'original visits.bin/intent/journal plus before/after hash-size maps','existing global ledger and M.budget_snapshot','before/after cleanup',
    'original bytes retained, no reset/refund/new initialization','three originals once, maps embedded in actual records','outside main',
    'independent hash/counter/intent re-read of retained originals','budget UNKNOWN if torn/missing','cleanup must not create a free window or refund charged work')
req('RE12','all actual close attempts and final internal status','B1_SAFETY',
    'mr_close_attempts.jsonl and final mr_close_state.json','M.abort390-400','after cleanup observations',
    'append/file fsync and BC replacement when successful','two Receiver calls locally, scoped parent calls separately bounded','outside main',
    'raw independent recomputation','internal completeness UNKNOWN','repeated wrappers and persistence failures remain visible')
req('RE13','lock and publication objects','B1_PHYSICAL_METADATA',
    'c09_lifecycle.lock, mr_close.lock, directory/staging objects','existing H/MR/RootIPC/BC helpers','before/during publication',
    'trusted inode/type/mode and stable locking relation','empty lock file still needs inode/metadata; temp names counted by call','outside main',
    'trusted storage-domain/inode reservation evidence currently null','admission/retention UNKNOWN','zero data bytes do not imply zero physical storage need')
req('RE14','normal VERIFIED cleanup continuation','B1_NORMAL_HANDOFF',
    'stop_result, updated handoff with cleanup, result_C09, batch_state and later RESUMED','Receiver281-294 and admitted resumed scheduler',
    'successful verification, payload cleanup, then state progression','raw replacements/new result preserved','cleanup appears in three real carriers, each path charged once','stage event only is in main',
    'existing commit/witness/ACK inputs','normal handoff incomplete/UNKNOWN','preserves the actual successful C09 path without forcing terminal batch closure')
req('RE15','native prerequisite originals','NATIVE_INPUT_REFERENCES',
    'activation/state/checkpoint/phase/runtime_intent/budget/scheduler/STOP_ARMED/markers/waitpid','existing protected producers',
    'already present or genuinely produced before native readiness','refer to original paths/hash/size; no forced duplicate copies in close pool','one raw pathname per original layer','outside main',
    'independent raw oracle and current exit facts','native readiness false/UNKNOWN','retains minimum source inputs required by terminal reader')
req('RE16','native output/defer information','NATIVE_LATER_LAYER',
    'terminal review / pt_seal_disposition / native manifest/ZIP / applicable error','existing sealer',
    'after actual close/quiescence checks','own later byte/work contract','at most scoped sealer calls; one x-created archive','outside main',
    'native output can be absent under failure','native UNKNOWN/FAILED','later complete sealing is a separate capacity obligation')
req('RE17','minimal administrative reference index','ADMIN_REFERENCE_SPEC',
    'proposed minimal index of original paths/hashes/sizes/roles/outcome axes; current compact writer absent','trusted evidence owner to be identified',
    'reference safety evidence captured before archive work','index preserves availability references, not a replacement for originals','one bounded index profile currently null','outside main',
    'guaranteed independent retention provider currently null','admin UNKNOWN, core facts cannot be deferred to index generation','allows later audit to find already saved safety evidence')
req('RE18','v2 fixed quota failure summary','PROPOSED_SUPPLEMENT',
    'prior v2 bounded summary334','future B1 writer if adopted','first resource failure',
    'declared local write/staging retained','one global summary only if its role is adopted','outside main',
    'exhaustion facts already linked by main/cursor and MR first cause','summary missing => profile-dependent UNKNOWN','a duplicate carrier is budgeted if selected, not silently promoted to a new mandatory source')
save('B1_CLOSE_REQUIRED_EVIDENCE.json', {'items':required,
    'definition':'B1_CLOSE_REQUIRED_EVIDENCE is a fact/provenance and actual-carrier contract, with safety, normal-handoff, native and admin layers explicitly identified',
    'all4450_required_in_close_pool':False,'safety_capture_before_admin_archive_required':True,
    'external_receiver_exit_provider':None,'minimal_index_bytes':None})

save('SCOPED_CLOSE_COUNT_PROOF.json', {
    'verdict':'CONDITIONAL_PROVED',
    'scope_E':'One fresh256th-PENDING exhaustion incident in initial C09 phase, sender exited, noVERIFIED/no resume, H=0, existing once/no-restart role graph, proposed exception absorption honored',
    'receiver':{'first_abort_max':1,'second_abort_max':1,'abort_entries_max':2,'stop_tree_from_abort_max':2,
                'core_production_attempts_max':18,'plus_parent_waitpid_max':19,
                'clean_serialized_prefix':{'first_data_writes':8,'second_data_writes':6,'total':14,
                   'stable_core_paths':9,'close_attempt_rows':2,
                   'conditions':'Receiver first-failure win, ordinary persistence succeeds, shared first/STOP then exist, both primary cleanup calls complete, no parent close writes interleaved'}},
    'whole_incident_E':{'active_coordinator_phase_max':1,'coordinator_abort_bound':4,'receiver_abort_bound':2,
        'A_abort':6,'S_stop_tree':8,'S_basis':'at most one primary per abort plus at most2 direct coordinator stop sites',
        'W_waitpid':1,'Q_seal_attempts':3,'Q_basis':'coordinator finally1 + outer boot failure1 + Receiver external tail1',
        'SEAL_ERROR_publications_max':1,'H':0,
        'core_production_attempts':59,'core_production_formula':'7*6+2*8+1',
        'stable_core_paths_no_staging':23,'path_formula':'5 fixed exception targets +2*8 stop paths +1close_attempts file +1waitpid',
        'BC_staging_create_attempts_max':18,'RootIPC_staging_create_attempts_max':29,
        'failed_staging_path_upper':47,'stable_plus_failed_staging_path_upper':70,
        'staging_basis':'BC external/ABORTING/final each<=A; RootIPC STOP/fallback each<=A, marker/result each<=S, waitpid<=W. Exclusive first-failure file has no separate staging.'},
    'scope_N':'Successful handoff uses stop_tree(close=False) once before HANDOFF_VERIFIED; publish state/result/batch_state add3 real publication calls, first parent witness inputs retained. Full batch shutdown remains later scope.',
    'scope_F':'Prepay/bind/ACK/resume or other failures outside E keep inherited whole frozen envelope A16/S23/Q7/W2/H52/core212/path54; it does not create a212-unique-record quota',
    'identities_not_reset':True,
    'idempotence':{'first_failure':'one existing exclusive first file under mr_close lock',
        'STOP':'absence check outside lock permits racing overwrite on one path',
        'CLOSED':'H lock serializes first marker; later stop_event paths permitted',
        'attempts':'each non-announce abort may append once while ZIP absent; current source has no close-request debit ledger',
        'late_calls':'actual fixed wrappers bounded; arbitrary API E_n lies outside original role-count scope',
        'recovery':'current Root graph Restart=no; proposed quota recovery must reject replenishment/uncertain state'}})
assert 7*6+2*8+1 == 59
assert 5+2*8+1+1 == 23
assert 3*6 == 18 and 2*6+2*8+1 == 29

# The existing source schemas are reused as declarative byte expressions.
old = read(ROOT/'DCL-R6-C09-CloseReserve-Closure/evidence/CLOSE_SCHEMA_BYTE_ALGEBRA.json')
role_identity = {'pid':0,'start_ticks':0,'boot_id':'b'*36}
stamp = {'boottime':0,'utc_ns':0,'boot_id':'b'*36}
budget = {name:{'sha256':'a'*64,'bytes':0} for name in ('visits.bin','visits.bin.intent.json','visits.bin.journal.jsonl')}
healthy_cleanup = {'schema':'MANAGER-RECOVERY/1','phase':'CLEANUP','status':'CLOSED_CLEANUP_CONFIRMED',
    'closed':False,'payload_empty':False,'other_roles':{'known_other_roles_exited':False,
       'targets':[{'identity':role_identity,'exit_observed':False} for _ in range(2)]},
    'first_failure_sha256':'a'*64,'errors':[],'budget_after':budget,'sample':stamp,'caller_exit_pending':False}
healthy_cleanup_bound = len(json.dumps(healthy_cleanup,sort_keys=True,separators=(',',':')).encode())+2*(9+19)+24+19+3*19
assert healthy_cleanup_bound == 1119
save('B1_CLOSE_BYTE_ALGEBRA.json', {
    'status':'PARTIAL','rechecked_prior_schema':old,
    'inherited_conditionals':{'ABORTING':237,'external_closing':260,'waitpid_normal':1223,'waitpid_fallback':565,
       'marker':'144+R','fixed43_reason_marker':189,'Root_generic_marker':194,
       'first':'25092+T+B with R_MR<=38','cleanup_state':'997+11T+B','cleanup_line':'998+11T+B',
       'stop_result':'1151+E+sumV','B':'69+3max(106,29+T)','healthy_B':387},
    'symbols':{'R':'encoded JSON reason token including quotes, distinguish fixedMR and R_budget',
       'T':'encoded exception class-name token; local source-owned18 does not instantiate complete importedTCB profile',
       'B':'three original budget-file hash/size or UNKNOWN/error maps',
       'E':'encoded repr of marker publication/lock failure in stop_tree close try, excludes later systemctl stderr',
       'V':'12 selected raw kernel cgroup file tokens; source list fixed, complete wire/list/churn profile uninstantiated',
       'R_budget':'BUDGET_HALTED:str(error) STOP token, H=0 in E but general source scope retains52'},
    'generated_core_E':'179815 +138*T +18*B +8*E +8*sumV',
    'stable_unique_core_E':'44708 +78*T +8*B +8*E +8*sumV',
    'failed_staging_union_E':'23275 +66*T +6*B +8*E +8*sumV',
    'stable_plus_staging_union_E':'67983 +144*T +14*B +16*E +16*sumV',
    'union_caveat':'These count distinct path classes once. Separate maxima need not be simultaneously attainable. Generated production sum is another conservative upper; choose the minimum of valid bounds only after profiles are fixed.',
    'healthy_receiver_example':{'first_bound':941,'marker_bound':183,'cleanup_state_bound':1119,
       'data_writes':14,'generated_bytes':'9272+2*sumV','fsync_calls':31,'budget_file_scans':12,
       'notes':'source fixed quota error31 ASCII/AdmissionBlocked16, first receiver reason25 ASCII, healthy budget map387, no cleanup errors, source normal-role branches, still no completeV profile'},
    'B_B1_close_formula':'sum unique required core originals + actual failed staging + selected quota supplement + trusted external witness/index + physical allocation overhead in a separately measured unit',
    'B_B1_close_encoded_bytes':None,'B_B1_close_physical_bytes':None,'B_external_witness':None,'B_min_index':None,
    'normal_handoff_other_bytes':None,
    'minimal_missing':['quantitativeT/E/V and applicable error/profile evidence','guaranteed independent caller-exit witness/index wire source','physical data/inode/directory/journal/temporary reserve and writer isolation'],
    'no_invented_numeric_caps':True})
assert 6*27972 + 8*1345 + 1223 == 179815
assert 194+25092+260+997+6*998+194+8*194+8*1151+1223 == 44708
assert 6*(260+237+997)+12*194+8*194+8*1151+1223 == 23275
assert 44708+23275 == 67983
assert 4796+4*1119 == 9272

storage_calls = []
for filename in ('c09_handoff.py','guard.py','manager_recovery.py','root_ipc.py','boot_continuity.py'):
    path = RUNTIME/'src'/filename
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    for call in ast.walk(tree):
        if isinstance(call,ast.Call):
            name = call.func.id if isinstance(call.func,ast.Name) else call.func.attr if isinstance(call.func,ast.Attribute) else ''
            if name in ('posix_fallocate','fallocate','ftruncate','statvfs','disk_usage'):
                storage_calls.append({'file':str(path),'line':call.lineno,'function':name})
assert not storage_calls
save('PHYSICAL_STORAGE_AUDIT.json', {
    'current_main_quota':'PROPOSED_NOT_EFFECTIVE','LOGICAL_QUOTA_RESERVED':'NOT_ESTABLISHED_FOR_B1_CLOSE',
    'PHYSICAL_STORAGE_RESERVED':'NOT_OBTAINED','source_allocation_or_free_space_calls_in_close_modules':storage_calls,
    'RootIPC':'private/out st_dev equality enforced84-85; random new private temp106; data write113; file+directory sync115,121,122',
    'BCStore':'boot directory Root-metadata checked, replacement uses new .bc inode100, file+directory barriers102,108; no close reservation provider',
    'backend_mapping':'each required target and staging directory must bind actual filesystem/device/generation before a physical guarantee; current live map not queried',
    'physical_requirements':['data extents','free reserved inodes','directory entries/rename capacity','filesystem journal/COW/metadata requirements','old+new version temporary overlap','ordinary and outside-writer exclusion from protected minimum'],
    'encoded_to_physical_formula':'sum ceil(size_i/allocation_unit)*allocation_unit + inode/directory/FS-journal/COW/temporary overhead, with provider guarantees for all required domains',
    'allocation_unit':None,'reserved_data_bytes':None,'reserved_inodes':None,'reserved_metadata_bytes':None,
    'trusted_provider':None,'provider_receipt':None,'ordinary_writers_cannot_consume_close_space':None,
    'memory_page_size_is_disk_allocation_unit':False,'arbitraryEIO_persistence_success_claim':False})

save('MINIMAL_STORAGE_COUNTEREXAMPLE.json', {
    'status':'COUNTEREXAMPLE','admission_status':'B1_CLOSE_RESERVE_COUNTEREXAMPLE',
    'target_claim':'Logical main/local reservation alone guarantees necessary durable close information remains writable after the final admitted PENDING',
    'scope':'source-bound proposed B1 exception composition with existing RootIPC/BC.Store, not an executed quota trace',
    'initial':['fresh valid handoff/boot/owner, sender dead and witness delayed','no STOP/CLOSED yet',
               'quota logical slots and remaining close credits are declared','no physical data/inode/metadata reservation or exclusion exists'],
    'steps':['last admitted PENDING append and fsync succeed','completion cursor publication succeeds, exhaustion is latched',
             'H context exits and existing fixed error reaches guard808','permitted volume allocation pressure leaves no inode or allocatable metadata for a new close temp',
             'STOP RootIPC staging creation returnsENOSPC; current code records only process-local note if possible',
             'first/ABORTING/CLOSED staging may also fail; first or second abort still attempts existing kernel/manager cleanup'],
    'result':['logical allowance can remain positive','durable shared STOP/CLOSED/required first evidence not guaranteed',
              'actual process cleanup may succeed or remain unconfirmed','budget is not refunded or reinitialized','native/admin completeness remainsUNKNOWN'],
    'healthy_media_capacity_case':'Allocation exhaustion requires no disk corruption. Other allowed volume consumers or unreserved ordinary records can exhaust capacity; namespace permissions supply no protected floor.',
    'counterexample_does_not_require':'unlimited API calls, domain-external stderr_m, a newDCL writer or a physical-infinite storage model',
    'minimum_exclusion_condition':'bind a trusted provider ensuring the measured closing subset data/inode/metadata/temp floor survives all approved ordinary/concurrent writes, with explicit fault outcomes',
    'new_tests':0,'root_files_mutated':0})

failure_specs = [
    ('F01','short write','one raw prefix retained, no reappend grant','existing abort/manager and external guardian attempt close','actual pidfd/group facts needed','no refund; counter/intent preserved','partial evidence UNKNOWN','native incomplete/UNKNOWN','admin independent/UNKNOWN'),
    ('F02','ENOSPC','deny new observations; local notes may lack persistence','manager stop can operate independently of application file creation','actual empty/exit facts independent','no new budget','shared marker may be missing','seal not guaranteed','retention/index needs independent source'),
    ('F03','EIO','burn uncertain slot and stop current flow','existing fallback/root manager responsibility','persistence error not equivalent to process-live/dead','ambiguous health remains','UNKNOWN','UNKNOWN/FAILED','UNKNOWN'),
    ('F04','fsync failure','written bytes may exist but durability uncertain','do not mint a completed marker from write return','fresh exit facts required','charged credit burned','UNKNOWN at failed barrier','no guaranteed complete seal','separate raw export result'),
    ('F05','Root Receiver death','kernel closes owned descriptors on actual exit','owner/manager guardian must be named and fresh','own death receipt needs independent producer','old state/ledger retained','unpublished data UNKNOWN','native may remain unsealed','later audit cannot be assumed available'),
    ('F06','BC.Store unavailable','cursor/first/final private state cannot be trusted as newly saved','existing RootIPC/manager attempts may still run','actual role/group proof required','prepay or quota state not rebuilt','UNKNOWN','defer/error','independent source required'),
    ('F07','direct parent lost','original raw waitpid may be unavailable','Receiver can observe gone targets using trusted identity/pidfd source','exit status23 remains unknown absent genuine parent witness','no reset','code/parent evidence UNKNOWN','native ready false if requiredwaitpid absent','admin cannot invent parent status'),
    ('F08','shared marker absent','local_HALTED is process scoped','supervision/deadline/manager can attempt remaining duty','global stop must be observed','existing intent health may separately block','UNKNOWN cancellation visibility','depends on genuine CLOSED/exit proofs','keep independent outcome axes'),
    ('F09','unlock or close-fd error','normal __exit__ ordering is known; released=true cannot be fabricated','stop_treeH reacquisition has bounded attempt deadline but kernel completion separate','actual process death eventually closes owned lock fds under kernel model','no fresh credit','lock/cleanup UNKNOWN','native requires actual preconditions','independent raw failure report'),
    ('F10','external guardian/store lost','caller has no guaranteed post-mortem self record','remaining independent sources only if actually available','final own-exit completeness UNKNOWN','no new windows','UNKNOWN','no universal seal promise','UNKNOWN')]
save('PERSISTENCE_FAILURE_MATRIX.json', {'rows':[dict(zip(['id','failure','local_behavior','external_stop_behavior','exit_evidence','budget_state','internal_state','native_seal','administrative_result'],row)) for row in failure_specs],
    'four_axes':['admission stopped','payload/roles actually reclaimed','minimum evidence complete/durable','native/admin completeness'],
    'arbitrary_storage_fault_all_persistence_guaranteed':False})

properties = [
    ('CR-1','MainQuotaExhaustion','PARTIAL','proposed256 quota; caller exception route must be implemented and checked'),
    ('CR-2','CloseReserveAvailability','COUNTEREXAMPLE','ENOSPC after last main/cursor commit with no protected physical floor'),
    ('CR-3','CloseReserveIsolation','UNRESOLVED','no current independent closing ledger/provider isolation'),
    ('CR-4','CloseAttemptBound','CONDITIONAL_PROVED','E branch A6/S8/W1/Q3/H0; global fallback A16/S23/W2/Q7/H52'),
    ('CR-5','NoAbortLoop','CONDITIONAL_PROVED','fixed exception leaves while, two Receiver wrappers; arbitrary API repeated calls excluded'),
    ('CR-6','NoFalseClosed','CONDITIONAL_PROVED','current CLOSED absorption depends on existing stop marker; proposed EXHAUSTED uses distinct fixed exception'),
    ('CR-7','LockReleaseBeforeAbort','CONDITIONAL_PROVED','valid-fd normal context exit unlock/close before caller except; syscall/death uncertainty explicit'),
    ('CR-8','CloseIdempotence','PARTIAL','first-file exclusivity and finite source wrappers; current attempts may append and no close debit ledger exists'),
    ('CR-9','BudgetConservation','CONDITIONAL_PROVED','close functions read budget, no reset/refund/debit; newB1 cursor rule remains proposed'),
    ('CR-10','FailureResponsibility','PARTIAL','existing manager/Root actions explicit; guaranteed independent own-exit provider unbound'),
    ('CR-11','UnknownPreservation','CONDITIONAL_PROVED','source returns/retainsUNKNOWN when evidence or exits fail, no newPASS'),
    ('CR-12','EvidencePreservation','PARTIAL','minimal required facts/carriers identified; physical/provider guarantee unavailable')]
save('SECURITY_PROPERTIES.json', {'properties':[{'id':key,'name':name,'verdict':verdict,'basis':basis} for key,name,verdict,basis in properties],
    'proposal_activated':False})
test_rows = []
for key,name,verdict,basis in properties:
    test_rows.append({'id':key,'name':name,'normal_input':'current binding, valid committed cursor/raw and healthy stop sources within declared profile',
       'failure_input':basis,'concurrent_input':'two eligible existing roles race last slot, STOP/first/CLOSED or close debit',
       'crash_interleaving':'before/after predebit, raw write/fsync, completion, STOP/CLOSED rename+directoryfsync and caller death',
       'expected_state':'specified axis only if original observation and persistence evidence suffice; otherwiseUNKNOWN/reject',
       'expected_bytes':'main unchanged345148 profile; unique closing paths/staging use scoped formulas; null maxima produce UNSUPPORTED_BOUND',
       'independent_oracle':'parse original evidence without importing target classifier/logger/Store or using supplied PASS; reconstruct role/lock/token/time/budget/bytes and compare actual vs reserved separately',
       'mutation_target':{'CR-1':'skip quota gate','CR-2':'claim logical equals physical','CR-3':'ordinary writer spends close allowance',
           'CR-4':'ignore wrapper/role count','CR-5':'returnEXHAUSTED without caller consumption','CR-6':'mapEXHAUSTED toCLOSED without marker',
           'CR-7':'abort whileH held','CR-8':'reissue close reservation or reinit missing ledger','CR-9':'refund/resetR orT0',
           'CR-10':'trust localHALTED as shared stop or self as own-exit witness','CR-11':'replaceUNKNOWN withPASS','CR-12':'omit required raw/staging/exit source'}[key]})
save('REGRESSION_ORACLE_SPEC.json', {'artifact_type':'DECLARATIVE_SPECIFICATION_ONLY','cases':test_rows,'executed':0,
    'future_paths_inherited':read(PREVIOUS/'evidence/FUTURE_FILE_SLOTS.json'),
    'oracle_rejection_rules':['missing/foreign/duplicate/extra raw path','hash/size/type/mode/binding mismatch','budget reset or recycledtoken',
        'unsubstantiated physical reservation','snapshot labelled as live current exit proof','null bound presented as a numericPASS'],
    'current_oracle_or_harness_code_written':False})

fields = [
    ('scope','fresh single B1 initial-handoff E incident and declared normal path; other failures use stated global fallback'),
    ('main_quota',{'attempts':256,'rows':263,'bytes':345148,'effective':False}),
    ('close_record_types',[item['id'] for item in required]),
    ('record_count',{'Receiver_abort':2,'core_E_attempts':59,'core_stable_E_paths':23,'failed_core_staging_E':47,'scope_conditions_required':True}),
    ('per_record_bytes',read(E/'B1_CLOSE_BYTE_ALGEBRA.json')['inherited_conditionals']),
    ('total_close_bytes',None),('logical_reservation',{'close_limit':None,'request_binding':'same source/batch/boot/handoff/generation, one initial reservation, no refund/regrant','state':'PROPOSED_NOT_EFFECTIVE'}),
    ('physical_reservation',{'provider':None,'domain_map':None,'data_bytes':None,'inode_count':None,'metadata_bytes':None,'exclusion_guarantee':None}),
    ('access_control','existing RootIPC/BC owner/type/mode/no-link/ACL checks plus provider identity binding'),
    ('concurrency_idempotence','ordinary observations and new reservation issuance freeze at stop; already reserved finite cleanup operations may complete afterCLOSED'),
    ('durability_order','pre-admission provider proof and logical reservation, local slot debit, full lastRaw/fsync, completion/exhaustion, H exit, existing abort path, actual exit evidence'),
    ('fault_responsibility',read(E/'PERSISTENCE_FAILURE_MATRIX.json')['rows']),
    ('overflow','deny new admission, keep actual raw/partial/staging and trigger existing bounded cleanup; incomplete evidence staysUNKNOWN'),
    ('unknown','never infer own exit, exact wait status, complete native/admin seal or shared cancellation from missing raw facts'),
    ('native_inputs','minimum retained original identity/state/checkpoint/budget/role/marker/waitpid references; native output remains later layer'),
    ('admin_inputs','minimum index is a reference to already captured safety raw; cannot serve as deferred-only capture of those facts'),
    ('failed_close_path','source808/817+fallback and bounded Root coordinator paths; no new API retries or role restart'),
    ('resource_consumption',{'healthy_prepay_write_bytes':266752,'healthy_prepay_journal_part':122112,'healthy_prepay_fsync':2304,'close_full_IO_memory_FD_time':None}),
    ('effectiveness','all numeric/profile/provider/exit-source obligations and exact version proof plus independent user source/run approvals'),
    ('version_binding',{'source_lock':'RuntimeAdapt-static-1/r1 current digest set','future_contract_hash':None,'approval_receipt':None,'execution_identity':None})]
assert len(fields) == 20
OUT.joinpath('proposals').mkdir(exist_ok=True)
contract = {'schema':'DCL-B1-MINIMAL-CLOSE-RESERVE/1-DRAFT','version':'B1-CloseReserve-Contract/review-1',
    'status':'B1_CLOSE_RESERVE_COUNTEREXAMPLE','approved':False,'user_approved':False,'effective':False,'runtime_enabled':False,
    'fields':[{'number':number,'field':name,'value':value} for number,(name,value) in enumerate(fields,1)],
    'B_B1_close':None,'physical_storage_reserved':False,'trusted_external_exit_retention_provider':None,
    'admission':'B1_BLOCKED_BY_CLOSE_RESERVE','source_implementation_request':'SUSPENDED',
    'full_capacity':'CAPACITY_CONTRACT_NOT_READY','four_permissions_independent':True,
    'minimal_missing':['quantitative required close wire profile','trusted physical/data/inode/metadata/temp guarantee and ordinary-writer exclusion',
                       'independent durable caller-exit witness source','current source/candidate finite ownership/recovery mapping'],
    'no_current_execution_or_patch':True}
path = OUT/'proposals/B1_MINIMAL_CLOSE_RESERVE_DRAFT.json'
path.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save('IMPLEMENTATION_ADMISSION.json', {'current':'B1_BLOCKED_BY_CLOSE_RESERVE','close_verdict':'B1_CLOSE_RESERVE_COUNTEREXAMPLE',
    'scope_plan_inherited':read(PREVIOUS/'proposals/B1_MAINTENANCE_REQUEST_DRAFT.json'),
    'implementation_application_submission':'SUSPENDED_UNTIL_MINIMAL_CONTRACT_SUFFICIENT',
    'authorized_source_changes':False,'manager_recovery_role':'read-only interface dependency','runtime_tree_lock_role':'read-only TCB dependency',
    'permission_states':{'CAPACITY_CONTRACT_APPROVAL':'logical decision only, actual user decision absent','MR_CROSS_INSTANCE_APPROVAL':'PROPOSED_NOT_EFFECTIVE',
         'NATIVE_IMPLEMENTATION_AUTHORIZATION':'NOT_GRANTED','FULLCHAIN_DYNAMIC_AUTHORIZATION':'NOT_GRANTED'},
    'conditional_future_request_required_fields':['currentSHA','function/line','semanticdiff','invariants','tests','negativecases','mutations',
        'resources','rollback','historicalprotection','newversionmanifest','independentnativevalidationrequest'],
    'new_source_patch_created':False,'new_dynamic_batch_created':False})
save('CONTRACT_BINDING.json', {'contract':record(path),
    'prior_logical':record(PREVIOUS/'proposals/CAPACITY_LOGICAL_CLAUSES_DRAFT.json'),
    'prior_maintenance':record(PREVIOUS/'proposals/B1_MAINTENANCE_REQUEST_DRAFT.json'),
    'MR_rule':record(ROOT/'DCL-R6-C09-BoundClosure/proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json'),
    'all_new_user_decisions':None})
save('GENERAL_G_COMPARISON.json', {'input_family':'single handoff main exhaustion and normal/faulty close on finite writers',
    'metrics':['required raw bytes','production/staging attempts','isolated allocation','budget/exit/evidence safety'],
    'G':'standard bounded append log, physical preallocation/guaranteed reserve, idempotent close identity, finite typedtoken and atomic allowance',
    'status':'COVERED_BY_G','predicted_strict_gap':0,'strict_more_cost_instance_for_G':None,
    'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED','mechanism_implementation':0})
print(json.dumps({'call_nodes':len(nodes),'evidence_items':len(required),'core_E_attempts':59,'stable_E_paths':23,
    'Receiver_clean_writes':14,'Receiver_clean_paths':9,'contract_fields':20,
    'verdict':'B1_CLOSE_RESERVE_COUNTEREXAMPLE','admission':'B1_BLOCKED_BY_CLOSE_RESERVE'}))
