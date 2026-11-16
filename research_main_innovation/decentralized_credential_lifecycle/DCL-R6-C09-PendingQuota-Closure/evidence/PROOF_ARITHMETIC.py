"""Static source census, byte algebra and contract tables; no runtime imports.

All generated Python in this delivery is host research administration only.
No logger, quota allocator, budget transaction, fault or model is executed here.
"""
from RESEARCH_AUDIT import ROOT, OLD, OUT, E, RUNTIME, read, write, row, sha
import ast
import copy
import hashlib
import json
from pathlib import Path
import shutil
import struct
from collections import Counter

def enc(x): return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def pretty(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2).encode()

# Read every frozen source file as text/AST, never import it.
sites=[]; matches=[]; excerpts={}
for p in sorted((RUNTIME/'src').glob('*.py')):
    text=p.read_text(encoding='utf-8-sig'); tree=ast.parse(text,filename=str(p))
    rel=p.relative_to(RUNTIME).as_posix()
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('event','publish') and p.name=='c09_handoff.py':
            sites.append({'file':str(p),'source_line':node.lineno,'end_line':node.end_lineno,
                          'callee':node.func.id,'text':ast.get_source_segment(text,node)})
    for i,line in enumerate(text.splitlines(),1):
        if any(s in line for s in ('PENDING','c09_events','observe_exit','coordinator_witness')):
            matches.append({'file':str(p),'line':i,'text':line})
assert sum(r['callee']=='event' for r in sites)==3
assert sum(r['callee']=='publish' for r in sites)==6
write('STATIC_PRODUCER_CENSUS.json',{'native_event_sites':sites,'all_pending_related_source_matches':matches,
    'native_sink':'src/c09_handoff.py:75-84','native_pending_site':'src/c09_handoff.py:277',
    'closed_world':'64 frozen source/input objects; native callers only; no privileged source injection',
    'runtime_imports':0})
for name,ranges in {
 'c09_handoff.py':[(18,34),(36,134),(168,358)],
 'guard.py':[(109,164),(545,546),(568,595),(624,691),(718,725),(749,815),(993,1027),(1190,1240)],
 'root_ipc.py':[(91,155)],'manager_recovery.py':[(51,94),(251,315),(317,430),(453,468)],
 'terminal_evidence.py':[(143,186),(193,266)],'startup_lifecycle.py':[(412,524)],
 'c09_regression.py':[(1,74)],'range_core.py':[(100,225)]}.items():
    lines=(RUNTIME/'src'/name).read_text(encoding='utf-8-sig').splitlines()
    excerpts[name]=[{'start':a,'end':min(b,len(lines)), 'lines':[
        {'line':i,'text':lines[i-1]} for i in range(a,min(b,len(lines))+1)]} for a,b in ranges]
write('SOURCE_EXCERPTS.json',excerpts)

# Copy all eight historical raw objects, including nested inputs/out.
raw=OLD/'evidence/HISTORICAL_RAW'
for p in raw.rglob('*'):
    if p.is_file():
        q=E/'HISTORICAL_RAW'/p.relative_to(raw);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
native=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch09\final_snapshot')
names=['inputs/root_private/c09_events.jsonl','inputs/c09_handoff.json','inputs/c09_commit.json',
       'inputs/c09_exit_witness.json','inputs/CLOSED.json','out/visits.bin','out/visits.bin.intent.json','out/visits.bin.journal.jsonl']
lock=read(ROOT/'DCL-R6-CalDiag/evidence/FINAL_NATIVE_EXPORT_LOCK.json')
export_rows={r['relative']:r for r in lock['files']}
# Preserve and expose the original lock format; direct bytes additionally match the old raw copies.
historical=[]
for n in names:
    p=native/n
    q=E/'HISTORICAL_RAW'/('CALDIAG_c09_events.jsonl' if n.endswith('c09_events.jsonl') else n)
    assert sha(p)==sha(q)
    assert sha(p)==export_rows[n]['sha256'] and p.stat().st_size==export_rows[n]['bytes']
    historical.append({**row(p),'copy':str(q)})
log=(native/names[0]).read_bytes();rows=[json.loads(x) for x in log.splitlines()]
pending=[r for r in rows if r.get('verdict')=='PENDING'];assert len(pending)==17
jrows=[json.loads(x) for x in (native/names[-1]).read_bytes().splitlines()]
lo,hi=pending[0]['boottime'],pending[-1]['boottime']
assert not [r for r in jrows if lo<=r['boottime']<=hi]
for line in log.splitlines(keepends=True): assert line==enc(json.loads(line))
assert sha(RUNTIME/'src/c09_handoff.py')==sha(native.parent/'FROZEN_B09/src/c09_handoff.py')
write('HISTORICAL_RECHECK.json',{'originals':historical,'export_lock':row(ROOT/'DCL-R6-CalDiag/evidence/FINAL_NATIVE_EXPORT_LOCK.json'),
  'export_lock_contents':lock,'rows':len(rows),'bytes':len(log),'pending':len(pending),
  'events':dict(Counter(r['event'] for r in rows)), 'verdicts':dict(Counter(r.get('verdict') for r in rows if 'verdict'in r)),
  'same_handoff':len({r['handoff_id'] for r in pending})==1,'revisions':sorted({r['revision'] for r in pending}),
  'global_journal_rows_during_pending':0,'R':struct.unpack('<Q',(native/'out/visits.bin').read_bytes()[8:16])[0],
  'new_native_runs':0,'c09_source_sha256':sha(RUNTIME/'src/c09_handoff.py')})
cfg=read(RUNTIME/'inputs/c09_contract.json')
write('H34_STATIC_INPUT_REVIEW.json',{'contract':row(RUNTIME/'inputs/c09_contract.json'),
 'jobs':len(cfg['jobs']),'event_files':sum(len(j['events']) for j in cfg['jobs']),
 'max_events_in_actual_job':max(len(j['events']) for j in cfg['jobs']),
 'source':'src/c09_regression.py:59-72; src/c09_oracle.py:8-16,42-60',
 'event_file_accepted_bytes':65536,'native_pending_quota_inferred_from_synthetic':False,
 'new_synthetic_runs':0})

oldmath=read(OLD/'evidence/NATIVE_RECORD_BYTE_ALGEBRA.json')
t=oldmath['templates']; skeleton={k:len(enc(v)) for k,v in t.items()}
common=9+19+19+4*24
assert common==143
pending_null=skeleton['pending']+common+2*24
# Universal schema bound: thirteen Boolean fields; replacing every bool by false
# and witness by an eleven-character integer is a conservative envelope.
ct=copy.deepcopy(t['terminal']);ct['facts']={k:(False if type(v)is bool else v) for k,v in ct['facts'].items()}
schema_classification=len(enc(ct))+common+2*24+10
assert pending_null==1298 and schema_classification==1318
stages=['HANDOFF_PREPARING','HANDOFF_READY','HANDOFF_COMMITTED','LAUNCHER_EXIT_OBSERVED','HANDOFF_VERIFIED','RESUMED']
stage_bounds=[]
for name,line in zip(stages,[187,226,232,262,286,343]):
    v=copy.deepcopy(t['transition']);v['event']=name
    stage_bounds.append({'event':name,'line':line,'skeleton_bytes':len(enc(v)),'upper_bytes':len(enc(v))+common})
state_sum=sum(x['upper_bytes'] for x in stage_bounds)
line_max=1322;state_max=948;ack_max=1028
main=256*line_max+6*state_max+ack_max
assert main==345148
write('RECORD_BYTE_ALGEBRA.json',{
 'status':'CONDITIONAL_PROVED','codec':'CPython3.12 compact sorted JSON, ensure_ascii=True, UTF-8, LF1',
 'original_templates':t,'skeleton_bytes':skeleton,
 'common_adjustments':{'pid_1_to_10':9,'start_ticks_1_to_20':19,'utc_ns_1_to_20':19,'T0_deadline_stop_at_and_boottime_1_to_25':96},
 'classification_extra_floats':48,'classification_witness_1_to_11':10,
 'pending_missing_witness_and_durable_ACK_true_upper':pending_null,
 'all_schema_classifications_conservative_upper':schema_classification,'chosen_classification_slot':line_max,
 'chosen_slot_slack_above_schema_algebra':line_max-schema_classification,
 'state_rows':stage_bounds,'sum_of_actual_six_state_bounds':state_sum,
 'chosen_state_slot':state_max,'ACK_slot':ack_max,
 'main_reservation':{'classification':256*line_max,'lifecycle':6*state_max,'ACK':ack_max,'sum':main},
 'main_typed_upper_under_normal_ACK_stutter':255*1298+1322+6*948+1028,
 'general_contract_uses_1322_for_every_classification':True,
 'pending_1298_scope':'witness=None and durable_ack=True normal single-Receiver path; use1322 if the scalar facts differ',
 'schema_limits':oldmath['field_widths'],'source_enforced_row_cap':None,
 'source_shape_validation_required_before_encoding':True,'free_text_or_recursive_fields':'outside closed native schema'})

oldq=read(OLD/'proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json')
cursor=copy.deepcopy(oldq['quota_file_schema']);cursor['schema']='C09-LOG-QUOTA/2-DRAFT'
cursor.update(lifecycle_mask=127,terminal_latched=False,ordinal=263,
    prepay_before=1000000,prepay_after=1000000,prepay_journal_bytes=0,prepay_journal_sha256='a'*64)
C=len(enc(cursor))+3*24+19
failure=oldq['failure_record_schema'];F=len(enc(failure))+24+19
reason='MR_CRITICAL:C09_PENDING_ALLOWANCE_EXHAUSTED'
marker={'reason':reason,'boottime':0,'utc_ns':0,'boot_id':'b'*36}
M=len(pretty(marker))+24+19
assert (C,F,M)==(1198,334,189)
updates=1+1+263+256+1
local_retained=main+3*C+2*F+4*M
local_writes=main+updates*C+F+2*M
durability=263+updates*2+2+1+2*3
assert (updates,local_retained,local_writes,durability)==(522,350166,971216,1316)
write('QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json',{
 'status':'CONDITIONAL_PROVED_SUBCOMPONENT_ONLY','old_contract_sha256':sha(OLD/'proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json'),
 'main_bytes_unchanged':main,'cursor_schema_example_width_sentinel_not_instance':cursor,
 'cursor_skeleton':len(enc(cursor)),'cursor_float_adjustment':72,'cursor_journal_length_adjustment':19,'cursor_upper':C,
 'failure_schema':failure,'failure_upper':F,'marker_schema':marker,'marker_codec':'RootIPC pretty JSON indent2 ensure_ascii=False no LF',
 'marker_reason_max_ascii_bytes':43,'marker_skeleton':len(pretty(marker)),'one_marker_upper':M,
 'minimal_missing_STABLE_STOP_and_CLOSED_reservation':2*M,
 'minimal_missing_quota_stable_vs_main':C+F+2*M,
 'stable_subgroup_total':main+C+F+2*M,
 'staging':{'cursor_reservation_or_completion_and_poison':2*C,'failure':F,'STOP_and_CLOSED':2*M},
 'retained_subgroup_upper':local_retained,'extra_over_main_subgroup':local_retained-main,
 'cursor_updates':{'initialize':1,'bind_handoff':1,'predebit_all_slots':263,'classification_finalize':256,'poison_once':1,'sum':updates},
 'write_bytes_upper':local_writes,'durability_attempts_upper':durability,
 'old_values_remain_historical':{'cursor':956,'cursor_updates':266,'write_bytes':599778,'durability':798,'retained':348684},
 'source_staging_distinction':'RootIPC cross-directory STOP/CLOSED each may need file+destination+private sync; private cursor/failure file+one directory',
 'excluded_REQUIRED_objects':['existing c09_handoff state and commit resources','waitpid/witness/ACK provenance','stop_result / stop_event',
 'mr_first_failure / mr_close_state / mr_close_attempts','terminal_seal_review / SEAL_ERROR','native manifest/ZIP','admin audit/manifest/ZIP/raw host streams'],
 'whole_close_reserve_upper':None,'physical_disk_reservation':False,'whole_CLOSE_RESERVE_status':'CLOSE_RESERVE_BOUND_UNRESOLVED'})

contexts=[
 ('P01','initial PENDING / repeated observation','c09_handoff.py',252,277,'Receiver Root','witness missing after committed exit','COMMITTED/EXIT_OBSERVED','EXIT_OBSERVED/revision4',1,True,'lifecycle lock; same sole Receiver','O_APPEND + full write + fsync','ABSENT'),
 ('P02','six lifecycle publications','c09_handoff.py',85,88,'Sender / Receiver / resumed scheduler','each native stage call','previous stage','next stage',1,'crash gap requires no replay','same lifecycle lock','log fsync then state publish','ABSENT'),
 ('P03','sender ACK observation','c09_handoff.py',189,196,'initial sender Root','fresh committed reply checked','COMMITTED','COMMITTED',1,'no native ACK business retry','same lifecycle lock','append/fsync','ABSENT'),
 ('P04','duplicate PREPARE / repeated handoff id','c09_handoff.py',217,236,'Receiver Root','authenticated PREPARE','COMMITTED','COMMITTED',0,'same id reply only','lifecycle lock','reply; stage events only on PREPARING','not an observation quota'),
 ('P05','ACK connect/wait / error response','c09_handoff.py',138,155,'Sender/Receiver','RPC wait/error','unchanged','error/return',0,True,'RootIPC waits','socket; free error text may reach separate streams','separate bytes unresolved'),
 ('P06','parent waitpid / witness','c09_handoff.py',297,321,'Root coordinator','direct child reaped','EXIT_OBSERVED','witness published',0,'different stamp on repeated witness rejected','lifecycle lock','independent witness JSON','not main log'),
 ('P07','timeout/Launcher exit/error cleanup','guard.py',781,809,'external stop Root','deadline / supervisor failure','active','abort',0,False,'M.abort / H lock interplay','STOP / CLOSED / MR files','no native PENDING sink'),
 ('P08','Root recovery / resumed scheduler','c09_handoff.py',323,347,'new scheduler Root','verified once and old window','VERIFIED','RESUMED',0,False,'lifecycle lock','one RESUMED stage counted in P02','not a PENDING writer'),
 ('P09','ManagerRecovery supplementary logs','manager_recovery.py',51,60,'Root roles','review / abort / cleanup','reviewing','closure',0,'separate loops/abort bounds','mr locks','mr_events / close files','separate resource family'),
 ('P10','STOP / CLOSED race','guard.py',545,760,'multiple existing stop roles','critical error / stop request','active/inflight','stop/closed',0,'existing stop_event and stop_result paths possible','STOP write outside H lock; CLOSED inside','RootIPC writes','no native PENDING recursion'),
 ('P11','native seal / terminal read','guard.py',993,1027,'quiescent native sealer','writers/roles exit proof','closed','archive',0,False,'M.seal + terminal read + exit proof','hash/copy/ZIP','no native PENDING recursion'),
 ('P12','admin finalizer / post-exit export','startup_lifecycle.py',412,510,'post-exit admin','quiescence audited','closed','copied/archive',0,'bounded explicit admin calls only','read-only runtime originals','read/copy/admin artifacts','no native PENDING recursion'),
 ('P13','C09H34 synthetic PENDING','c09_regression.py',59,72,'UID999 payload','fixed204 synthetic steps','synthetic facts','synthetic facts',0,'fixed input events','per-test files','out/c09_tests event JSON; each charged','distinct synthetic path'),
]
keys=['producer_id','context','source_file','source_line','write_or_relevant_line','process','trigger','state_before','state_after',
      'native_main_append_count_per_trigger','retryable','concurrent','persistence','quota_checked']
write('PRODUCER_CONTEXT_MATRIX.json',{'rows':[dict(zip(keys,v)) for v in contexts],
 'distinct_objects':'native handoff_id vs frozen synthetic case_id/task_id; MR REVIEW_PENDING stays separate'})

crash=[
 ('I01','crash before quota reservation','no new grant; existing256 prepay may already be burned','none','no recreation; close on process failure'),
 ('I02','crash after durable predebit, before facts','one slot burned','zero emitted rows possible','INFLIGHT or process failure refuses replay'),
 ('I03','crash/short write during main append','slot stays burned','one raw prefix retained; no second append','UNKNOWN + stop; original bytes retained'),
 ('I04','full append before fsync, crash/EIO','slot stays burned','persistence unknown','no completion claim; no retry'),
 ('I05','append fsync succeeds, before completion/confirmation','slot stays burned','full row may exist despite lost return','INFLIGHT on disk closes; no duplicate re-append'),
 ('I06','COMMITTED debit / completed cursor then crash','global and local debit remain','no returned grant required','closed instance never reinitialized'),
 ('I07','same task/ordinal resubmitted','same prepay context; consumed ordinal never granted again','no duplicate row from replay','native API has no task_id; token=(binding,handoff,kind,ordinal)'),
 ('I08','two writers compete for last credit','one lock serializes fresh read + debit','at most one granted append','other sees256/terminal/stopping; zero extra error append'),
 ('I09','prepay global journal short write','existing budget core halts; no local cursor authority','raw journal prefix preserved','global intent unhealthy; no new quota initialization'),
 ('I10','cursor / log / stop / CLOSED EIO','credits burn, no further work','durable failure/close evidence may be absent','UNKNOWN; retain raw; storage-dependent cleanup remains unresolved'),
 ('I11','request during CLOSED / STOP / terminal cleanup','no new classification or main slot','no per-rejection main/emergency log','all roles enforce same absorbing state under lock'),
 ('I12','native seal while state changes','native seal waits writers + quiescence; else rejects','no immutable snapshot claim before exit','post-seal writes forbidden by process exit/provenance assumptions'),
]
write('CRASH_AND_CONCURRENCY_MATRIX.json',{'status':'CONDITIONAL_PROVED_LOG_SAFETY_CONTRACT_NOT_IMPLEMENTATION',
 'current_runtime_quota_proof':'ABSENT','cases':[dict(zip(['id','interleaving','quota_effect','record_effect','rule'],v)) for v in crash],
 'assumptions':['all writers share stable trusted lifecycle lock inode','storage honors completed file/directory fsync',
 'no privileged cursor rollback/reset or lock replacement','all role restarts close rather than resume an uncertain instance',
 'authorization/binding/schema checks precede grants; bounded lock acquisition retries must be specified separately'],
 'counterexamples':[
 {'id':'CE-LAST','schedule':'used255; A reads255; B reads255; A appends; B appends; both store256','violation':'two grants from one remaining credit without atomic fresh-read/debit'},
 {'id':'CE-TERMINAL','schedule':'A logs VERIFIED; releases lock for stop_tree; B logs VERIFIED before stage is HANDOFF_VERIFIED','violation':'single-thread terminal<=1 argument fails if generalized to concurrent observers'},
 {'id':'CE-REPLAY','schedule':'stage event fsync succeeds; crash before state publish; restarted writer sees old stage and republishes','violation':'stage count per logical transition alone does not bound replayed raw rows'},
 {'id':'CE-CLOSE-EIO','schedule':'quota exhausted; independent emergency/STOP/CLOSED write returns EIO','violation':'logical byte reservation alone cannot guarantee durable closing evidence'},
 {'id':'CE-SEAL','schedule':'hash old file then writer appends then ZIP reads new file','violation':'hash/package consistency requires true quiescence, not CLOSED presence alone'}]})

(OUT/'proposals').mkdir(exist_ok=True)
proposal={
 'schema':'C09-PENDING-QUOTA-CONTRACT/2-DRAFT','version':'PendingQuota-Closure/review-1',
 'status':'PROPOSED_NOT_EFFECTIVE','user_approved':False,'runtime_enabled':False,'actual_instance':None,
 'scope':'Reviewable engineering contract; whole close reserve and capacity still unresolved; no implementation authority',
 'main_limits':{'attempts':256,'all_outcome_PENDING':256,'successful_PENDING':255,'terminal_checks':1,
   'state_events':6,'ACK':1,'main_rows':263,'classification_slot_bytes':1322,'stage_slot_bytes':948,'ACK_slot_bytes':1028,'main_reserved_bytes':345148},
 'count_invariant':'emitted_rows<=debited_slots<=classification_debited+popcount(lifecycle_mask)<=256+7; no reappend of burned tokens',
 'observation_semantics':'An authenticated fresh call into native observe_exit consumes a credit before classification/check-base work; precheck/IO failures burn it; stopped/foreign/replayed calls obtain no grant. Polls and VERIFIED cached returns are not fresh classifications.',
 'classification_finalize':'Every computed classification first appends full raw facts and fsyncs; then one bounded cursor completion is persisted. Terminal latch is durable before releasing the lifecycle lock for stop_tree; failure at any barrier stops further calls.',
 'overflow':'The256th full PENDING is retained, then admission closes and a single bounded failure record is attempted. No257th classification or per-rejection append. On256th terminal the handshake may proceed only under all other unchanged checks.',
 'cursor_schema_width_example':cursor,'cursor_bytes':C,'cursor_updates_upper':updates,
 'cursor_semantics':'debited/reserved counts only; main raw bytes determine actual writes; lifecycle_mask has seven one-use category bits; ordinal never decreases; generation fixed1',
 'statuses':['INIT','BOUND','OPEN','INFLIGHT','TERMINAL_LATCHED','EXHAUSTED_FAIL_CLOSED','POISONED','CLOSED'],
 'terminal_status_distinction':'TERMINAL_LATCHED closes classification admission after VERIFIED but still permits the unused HANDOFF_VERIFIED and RESUMED category slots under their original guards. FAILED goes to POISONED; exhausted/stopped/poisoned/closed deny all new categories.',
 'bounded_invocation_condition':'522/1316/350166 require no retry of any failed slot write, globally at most one poison/summary attempt and no further staging on later rejected entries. Residual staging/INFLIGHT/process failure closes the instance. Enforcing this across all roles, including EIO with no marker, remains an explicit integration and close-proof obligation.',
 'prepay':'Call existing scalar durable reservation256 times in a separately authorized pre-C09 phase; record before/after and journal-prefix length/hash. Existing global core unchanged. Any interruption burns the prefix and closes; idempotence rejects a second initialization rather than issuing a new block.',
 'prepay_binding':'completed interval after-before=256; bounds before/after<=1000000; before C09 controller/ready/counter snapshot; no global debit during observation',
 'existing_exact_range_relation':'range_core production task contract currently covers C02/C03/C04; it is not an already authorized C09 block allocator. Reuse serialization/durable debit semantics; no new global budget core.',
 'concurrency':'one shared lifecycle lock, fresh cursor reads and durable predebit under lock; only current authenticated Receiver computes classifications; simultaneous entry requests serialize; terminal_latched closes the cleanup gap',
 'replay':'same(binding,handoff,kind,ordinal) never receives a second grant; newer ordinal is a new observation and consumes a new credit. No arbitrary task_id map or new handoff/window/credit generation.',
 'crash':'unknown commit/partial row/INFLIGHT on recovery => stop/UNKNOWN, no refund, no raw reappend, no business resume/reinitialization; finite poison/failure attempt only',
 'lock_order':'publish no-new-admission and bounded STOP attempt while serialized; release H lock before frozen stop_tree/abort; whole lock-order integration remains a required review',
 'schema':'exact current native keys; ASCII bounded strings; finite numeric ranges; no recursive/free text or extra keys; validate widths before serialization allocation; preserve original out-of-profile inputs separately and stop',
 'minimal_close_subgroup':{'failure_rows':1,'failure_bytes':334,'STOP_rows':1,'STOP_bytes':189,'CLOSED_rows':1,'CLOSED_bytes':189,
   'marker_reason_max_ascii_bytes':43,'marker_bytes_exclude_frozen_cleanup_artifacts':True,'cursor_bytes':C,
   'retained_bytes_with_failed_staging':local_retained,'write_bytes':local_writes,'durability_attempts':durability,
   'full_close_reserve':'CLOSE_RESERVE_BOUND_UNRESOLVED'},
 'persistence_failure':'No guarantee of durable STOP/CLOSED under EIO/ENOSPC. Deny work and attempt unchanged cleanup; exit/group-empty/seal remain actual evidence obligations, UNKNOWN if absent.',
 'seal':'all raw original bytes, including partial/staging/cursor/prepay linkage, must be manifested; quota summary cannot replace ACK/commit/witness/budget/exit evidence; writers quiescent before hashes',
 'full_capacity_status':'CAPACITY_CONTRACT_NOT_READY','MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE',
 'new_visits_pre_other_tests':256,'old_scope_visit_upper':68498,'conditional_scope_visits_pre_other_tests':68754,
 'full_new_count_bound':'4450 + new quota object set difference + close/integration/test deltas; unintegrated',
 'G_status':'COVERED_BY_G','strict_separation_instances':0,'implementation_gate':'CLOSED',
 'approval_meaning':'Approve/reject only this logical draft with named unresolved integration/closing/capacity obligations; separate exact static-maintenance authorization required'}
p=OUT/'proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json';p.write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write('FINAL_PROPOSAL_BINDING.json',{'proposal':row(p),'old_proposal':row(OLD/'proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json'),
 'effective':False,'approved':False,'separate_MR_rule':row(OLD/'proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json')})

write('WORK_BOUND_RECALCULATION.json',{
 'proposed_subgroup':{'main_appends':263,'main_write_bytes':345148,'cursor_updates':522,'cursor_bytes_per_update':1198,
   'failure_writes':1,'STOP_and_CLOSED_writes':2,'write_calls_max':788,'write_bytes_max':971216,'fsync_attempts_max':1316,
   'cursor_read_operations_max':522,'cursor_read_bytes_max':522*1198,
   'one_quiescent_subgroup_hash_pass_bytes':350166,'native_raw_subgroup_input_bytes':350166,
   'two_archive_oracles_subgroup_uncompressed_bytes':2*350166,
   'note':'522 bound is for declared state transitions/data reads, not an arbitrary retry-loop or hostile request bound'},
 'FD':'data1 + lifecycle1 simultaneous under same-dir cursor helper, plus directory descriptors and existing process/socket/pidfd/helper baselines; no complete numeric process FD proof',
 'memory':'bounded serialized scalar input buffers; CPython allocations/ambient systemctl captures and helper inputs still unresolved',
 'full_observation_reads':'C09 main quota does not bound global journal scans, full source hashing, check_base PIPE capture, /proc/systemd environment',
 'WORK_BOUND_status':'CONDITIONAL_PROVED_FOR_DECLARED_LOG_SUBGROUP',
 'VISIT_BOUND_status':'CONDITIONAL_PROVED_68754_BEFORE_NEW_TESTS',
 'MEMORY_BOUND_status':'PARTIAL','WALL_TIME_BOUND_status':'WALL_TIME_BOUND_UNRESOLVED',
 'lock_wait_retry_bound':None,'full_stop_seal_admin_work':None})

count=read(OLD/'evidence/COUNT_SCOPE_COVERAGE_REVIEW.json')
write('CAPACITY_RECALCULATION.json',{
 'old_scope':count['scope'],'old_raw_count':4450,'old_native_count':4451,'old_admin_original_count':4452,'old_admin_ZIP_count':4467,
 'C09_log_already_in_old_count':'one inputs/root_private/c09_events.jsonl object; its rows are not new files',
 'count_coverage_correction':count.get('coverage_correction'),
 'hypothetical_new_quota_objects':{'stable_new':2,'failed_staging_new_upper':3,'subsumed_existing_C09_log':1},
 'new_count_formula':'K_new<=4450+|Q_new minus old_file_families|+Delta_close_uncovered+Delta_integration_tests; local Q_new<=5, others unresolved',
 'old_raw_bytes':'B_C09_log_old + B_other_raw',
 'hypothetical_new_raw_bytes':'B_other_raw_without_existing_STOP_CLOSED + B_log + B_cursor_failure_staging + B_existing_STOP_CLOSED_and_close_staging + B_other_required_close + delta',
 'known_local_subgroup_upper':350166,'whole_raw_upper':None,
 'archive_equations':['U_native=R_raw+M_native','Z_native=ZIP(R_raw+M_native;names,codec)',
 'E_admin_originals=R_raw+M_native+Z_native','U_admin=E_admin_originals+H_host+S_source_locks+M_admin'],
 'single_C09_log_counted_once_per_layer':True,'nested_native_ZIP_is_additional_admin_bytes':True,
 'remaining_families':['C09 commit.resources and handoff cleanup','C00-C12 journals/output','RootIPC/boot/readiness aggregate',
 'ManagerRecovery close/snapshots/queries','S1-S9 registry/traces','Gate/report/model state and strategies',
 'stderr/traceback/SEAL_ERROR raw text','manifest/path/ZIP expansion/admin nested copies'],
 'accepted_oracle_work':'O(N+B) for accepted capped archives; generator whole-set memory/IO remains unresolved',
 'capacity_status':'CAPACITY_CONTRACT_NOT_READY','old_guards':'256/257_UNCHANGED'})

write('GENERAL_METHOD_COMPARISON.json',{'status':'COVERED_BY_G','input_family':'one valid handoff with n missing-witness observations plus delayed or failed persistence',
 'metrics':['retained raw bytes','durable write count','at-most-once grants','closing evidence completeness'],
 'strong_generic_G':'bounded append log + serialized durable prepaid slots + idempotent transaction tokens + independent close reservation + immutable manifest',
 'predicted_strict_gap':0,'necessary_more_cost_instance_for_G':None,'strict_separation_instances':0,
 'research_candidates_implemented':0,'implementation_gate':'CLOSED',
 'maintenance_application':'only a later explicit static engineering-maintenance task may propose integration; no architecture novelty claim'})
print(json.dumps({'main':main,'cursor':C,'minimal_marker':M,'local_retained':local_retained,'writes':local_writes,
 'fsync':durability,'historic_pending':len(pending),'runtime_runs':0,'status':'STATIC_ARITHMETIC_COMPLETE'}))
