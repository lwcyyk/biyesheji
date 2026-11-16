"""Read-only frozen-source/historical evidence analysis and mathematical models.

No frozen program imports or execution. No logger/quota/packaging/gate code.
Only this turn's research reports, schemas and archive artifacts are written.
"""
from pathlib import Path
import ast,collections,copy,hashlib,json,shutil,zipfile
from datetime import datetime,timezone
P=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
I=Path(r'D:\毕业设计\DCL-R6-isolated-verification')
PREV=P/'DCL-R6-EvidenceContract-Closure';O=P/'DCL-R6-C09-BoundClosure';E=O/'evidence';E.mkdir(parents=True,exist_ok=True)
NAV=['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']
def h(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,x):
 p=E/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def cp(p,q):
 q.parent.mkdir(parents=True,exist_ok=True)
 with p.open('rb') as r,q.open('xb') as w:shutil.copyfileobj(r,w)
cp(Path(r'C:\Users\a1887\.codex\attachments\37a9a61d-9ed2-4b15-86bb-d2dfe2e4e006\已粘贴的文本.txt'),E/'TASK_REQUEST.txt')
for n in NAV:cp(P/n,E/'NAV_ORIGINALS'/n)
history=[]
for root in [P,I]:
 for p in sorted(root.rglob('*')):
  if p.is_file() and not p.is_relative_to(O) and not(root==P and p.parent==P and p.name in NAV):history.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h(p)})
save('HISTORY_BASELINE.json',{'files':history})
source_lock=read(P/'DCL-R6-FullChain-AdmissionFix/evidence/SOURCE_BASELINE_LOCK.json')
for r in source_lock['files']:
 p=I/'ra01'/r['relative'];assert h(p)==r['sha256'];cp(p,E/'FROZEN_RA_ORIGINALS'/r['relative'])
review=read(P/'DCL-R6-FullChain-AdmissionFix/evidence/STATIC_REVIEW_LOCK.json')
for r in review['files']:
 p=P/'DCL-R6-FullChain-AdmissionFix'/r['relative'];assert h(p)==r['sha256'];cp(p,E/'PRIOR_REVIEW_ORIGINALS'/r['relative'])
prev_lock=read(PREV/'evidence/FINAL_CONTRACT_REVIEW_LOCK.json')
for r in prev_lock['files']:assert h(PREV/r['relative'])==r['sha256']
save('SOURCE_AND_PRIOR_LOCK_CHECK.json',{'runtime_version':'RuntimeAdapt-static-1/r1','runtime_files':source_lock['files'],
 'review_objects':review['files'],'previous_contract_review_files':prev_lock['files'],'source_edits':0,'target_imports':0})
refs=['DCL-R6-EvidenceContract-Closure/FINAL_DECISION.md','DCL-R6-EvidenceContract-Closure/EVIDENCE_DEPENDENCY_GRAPH.md',
 'DCL-R6-EvidenceContract-Closure/EVIDENCE_RECURSION_AUDIT.md','DCL-R6-EvidenceContract-Closure/EVIDENCE_COUNT_CLOSURE_PROOF.md',
 'DCL-R6-EvidenceContract-Closure/ADMIN_NATIVE_CAPACITY_CONTRACT.md','DCL-R6-EvidenceContract-Closure/MR_LIFECYCLE_CONFLICT_PROOF.md',
 'DCL-R6-EvidenceContract-Closure/MR_CROSS_INSTANCE_ADMISSION_PROPOSAL.md','DCL-R6-EvidenceContract-Closure/MR_CROSS_INSTANCE_ADMISSION_APPROVAL.md',
 'DCL-R6-EvidenceContract-Closure/evidence/FINAL_COUNT_CLOSURE_CALCULATION.json','DCL-R6-EvidenceContract-Closure/proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json',
 'DCL-R6-FullChain-AdmissionFix/FINAL_DECISION.md','DCL-R6-FullChain-B/FULLCHAIN_FINAL_DECISION.md',
 'DCL-R6-CalDiag/CALDIAG_FINAL_DECISION.md','DCL-R6-CalDiag/evidence/C09_ACTUAL_HANDOFF.json','DCL-R6-CalDiag/evidence/FINAL_NATIVE_EXPORT_LOCK.json',
 'DCL-R6-TR-A2/evidence/DELIVERY_CHECK.json','DCL-R6-CalDiag/evidence/RESOURCE_ACCOUNTING.json']
for n in refs:cp(P/n,E/'HISTORICAL_REFERENCES'/n)
with zipfile.ZipFile(PREV/'EVIDENCECONTRACT_EVIDENCE.zip') as z:
 m=read(PREV/'EVIDENCECONTRACT_MANIFEST.json');assert len(z.namelist())==len(m['files'])+1==142 and z.testzip() is None
 for r in m['files']:assert hashlib.sha256(z.read(r['relative'])).hexdigest()==r['sha256']
assert h(PREV/'EVIDENCECONTRACT_EVIDENCE.zip')=='aada1b672ca91c731f97263ae21f4bacb03f501692eb25d0d464d6b9163e4346'
save('PREVIOUS_ZIP_RECHECK.json',{'members':142,'sha256':h(PREV/'EVIDENCECONTRACT_EVIDENCE.zip'),'status':'PASS_ADMIN_HASH_STRUCTURE'})
S=I/'ra01';src={p.name:p.read_text(encoding='utf-8-sig') for p in (S/'src').glob('*.py')};trees={n:ast.parse(t) for n,t in src.items()}
c09=trees['c09_handoff.py'];sites=[]
for n in ast.walk(c09):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='event':
  sites.append({'file':'src/c09_handoff.py','line':n.lineno,'expression':ast.unparse(n),
   'event_kind':ast.literal_eval(n.args[2]) if isinstance(n.args[2],ast.Constant) else '<publish stage>',
   'source_sha256':h(S/'src/c09_handoff.py')})
assert len(sites)==3
publish=[]
for n in ast.walk(c09):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='publish':publish.append({'line':n.lineno,'stage':ast.literal_eval(n.args[2])})
assert {r['stage'] for r in publish}=={'HANDOFF_PREPARING','HANDOFF_READY','HANDOFF_COMMITTED','LAUNCHER_EXIT_OBSERVED','HANDOFF_VERIFIED','RESUMED'}
native_producers=[
 {'id':'NATIVE-PUBLISH','site':sites[0] if sites[0]['event_kind']=='<publish stage>' else next(s for s in sites if s['event_kind']=='<publish stage>'),
 'process':'initial Root scheduler / Receiver / resume scheduler by stage','trigger':'Six actual publish call sites','repeat':'Each progress stage at most once under frozen writers/once handoff',
 'lifecycle':'PREPARING..RESUMED','max_records':6,'variable_fields':'Closed native schema: identity, window, timestamps, bounded stage/revision/hash',
 'external_lengths':'Trusted kernel/Root values; no raw systemctl/error/traceback field','fsync':True,'dedup':'single handoff state, stage conditions, classification_count/resume_count',
 'recovery':'Only RESUMED one additional stage','identity_guard':'Root-owned state, window/counter/case/receiver binding; no per-record size check'},
 {'id':'NATIVE-ACK','site':next(s for s in sites if s['event_kind']=='SENDER_ACK_OBSERVED'),'process':'initial Root scheduler',
 'trigger':'Authenticated durable PREPARE reply and fresh commit','repeat':'One frozen sender_prepare call; no automatic PREPARE retry',
 'lifecycle':'after COMMITTED while sender live','max_records':1,'variable_fields':'Base plus64hex commit digest','external_lengths':'No raw ACK/error payload copied',
 'fsync':True,'dedup':'fresh initial state + single sender call','recovery':'No re-ACK event in resume','identity_guard':'check_base(require_sender_live=True), sender peer/commit/window checks'},
 {'id':'NATIVE-CHECK','site':next(s for s in sites if s['event_kind']=='EXIT_CLASSIFICATION_CHECK'),'process':'Receiver independent external-stop Root',
 'trigger':'Persistent ready pidfd for exited scheduler; no waitpid witness yet yields PENDING','repeat':'PENDING self-loop arbitrary finite n in contract scheduling model',
 'lifecycle':'LAUNCHER_EXIT_OBSERVED,revision4,classification_count0','max_records':None,'variable_fields':'Base plus fixed facts map and verdict',
 'external_lengths':'witness integer/null; no unbounded error text, task_id or systemd output in native check row',
 'fsync':True,'dedup':'No PENDING counter/dedup; classification_count constrains successful transition only',
 'recovery':'HANDOFF_VERIFIED returns early; no PENDING after verified/resumed path','identity_guard':'check_base(...False), live Receiver/coordinator, stable budget/ticket/ready hashes'}]
save('C09_NATIVE_PRODUCERS.json',{'sink':{'file':'src/c09_handoff.py','line':75,'path':'inputs/root_private/c09_events.jsonl',
 'write_line':83,'encoding':'json.dumps(sort_keys=True,separators=(comma,colon),ensure_ascii=True) -> UTF-8 plusLF','per_call_fsync':True,'append_bytes_cap':None},
 'producers':native_producers,'publish_sites':publish,'declared_but_unproduced_native_stage':'HANDOFF_FAILED',
 'all_native_logging_call_sites':3,'no_c09_pending_producer_in_stop_native_seal_or_admin':True})

# History is parsed once as original bytes. No handoff/model/checker execution.
H=I/'batch09/final_snapshot';p=H/'inputs/root_private/c09_events.jsonl';raw=p.read_bytes();lines=raw.splitlines(keepends=True);rows=[json.loads(b) for b in lines]
assert h(I/'batch09/FROZEN_B09/src/c09_handoff.py')==h(S/'src/c09_handoff.py')
cp(p,E/'HISTORICAL_RAW/CALDIAG_c09_events.jsonl')
for n in ['inputs/c09_handoff.json','inputs/c09_commit.json','inputs/c09_exit_witness.json','inputs/CLOSED.json','out/visits.bin','out/visits.bin.intent.json','out/visits.bin.journal.jsonl']:
 cp(H/n,E/'HISTORICAL_RAW'/n)
pend=[r for r in rows if r.get('verdict')=='PENDING'];assert len(pend)==17
jrows=[json.loads(b) for b in (H/'out/visits.bin.journal.jsonl').read_bytes().splitlines()]
begin=pend[0]['boottime'];end=pend[-1]['boottime'];charges=[r for r in jrows if begin<=r['boottime']<=end]
assert not charges
save('HISTORICAL_NATIVE_LOG_ACCOUNTING.json',{'source_C09_same_bytes':True,'c09_sha256':h(S/'src/c09_handoff.py'),
 'batch':'batch09','status':'HISTORICAL_OBSERVATION_ONLY','file_sha256':h(p),'bytes':len(raw),'rows':len(rows),
 'events':dict(collections.Counter(r['event'] for r in rows)),'verdicts':dict(collections.Counter(r.get('verdict') for r in rows if r['event']=='EXIT_CLASSIFICATION_CHECK')),
 'line_min':min(map(len,lines)),'line_max':max(map(len,lines)),'pending_span_boottime':[begin,end],
 'pending_revisions':sorted(set(r['revision'] for r in pend)),'pending_handoff_ids':len(set(r['handoff_id'] for r in pend)),
 'budget_journal_appends_in_pending_span':len(charges),'R':38729,'transactions':1739,'journal_records':len(jrows),
 'no_RESUMED_reason':'Historical ManagerRecovery admission failed after real handoff; do not relabel as full-chain pass',
 'new_runtime_execution':0})

# Reachability evidence is a source-bound schedule family, not a logger copy.
family={'schema':'C09-CONTRACT-SCHEDULE-COUNTEREXAMPLE/1','status':'C09_PENDING_RECORD_BOUND_UNPROVABLE_UNDER_CURRENT_CONTRACT',
 'category':'STATIC_SOURCE_REACHABILITY_ARGUMENT_NOT_NATIVE_RUN',
 'initial':['One fresh handoff, PREPARING->READY->COMMITTED and durable ACK done','Receiver pidfd already acquired while sender was alive',
 'Sender executes os._exit(23)','Receiver/coordinator/payload/watchdog remain alive; Root coordinator temporarily descheduled before waitpid publication',
 'No STOP/CLOSED, deadline slack tau>0, current counter/ticket/ready/window bindings valid'],
 'parameter':'Any positive integer n; scheduling family sigma_n delays coordinator witness for tau<handoff_remaining, allowing n Receiver iterations',
 'first_iteration':['check_base(require_sender_live=False)','publish LAUNCHER_EXIT_OBSERVED once (revision3->4)','witness=None; all other facts valid','classify returns PENDING',
 'event(EXIT_CLASSIFICATION_CHECK,facts,verdict=PENDING) appends and fsyncs','return PENDING; external-stop caller neither closes nor resets ready pidfd'],
 'self_loop':['guard._external_stop_impl:781->787(no socket peer ready)->791->799(ready immediately)->800',
 'observe_exit:254->261->264(None)->276->277->278 -> repeat'],
 'invariant':{'stage':'LAUNCHER_EXIT_OBSERVED','revision':4,'classification_count':0,'resume_count':0,'model_budget_delta':0,
 'handoff_id':'one fixed id','counter':'same Root/ACK snapshot','log_records_delta_per_iteration':1,'log_fsync_delta_per_iteration':1},
 'growth':'N_PENDING(n)=n; B_PENDING(n)=sum encoded row lengths >=n bytes; actual fixed schema has a much larger positive minimum',
 'completion':'After finite n schedule coordinator waitpid/witness; next valid check can verify and close once. Later MR failure does not invalidate earlier repeated prefix.',
 'time_model':'No frozen lower bound for an immediate ready select/JSON/write/fsync operation. Arbitrary finite n is source/contract-model admissibility, not a physical fixed-hardware infinite-throughput claim.',
 'blocks_outside_family':['Pidfd not installed before sender exit -> identity acquisition can fail','Bad ACK/binding/counter -> reject','Wrong witness exit -> FAILED','CLOSED -> return CLOSED before append',
 'Deadline before check_base -> reject before append; crossing inside classifier may append one FAILED then close'],
 'runtime_instances_created':0,'replay_method':'Read these exact source branches and original17-PENDING witness; no executable protocol replay is authorized'}
save('COUNTEREXAMPLE_FAMILY.json',family)
save('NATIVE_STATE_RECORD_PROOF.json',{'normal_published_stages':6,'sender_ACK_records':1,'successful_check_terminal_records':1,
 'full_native_log_formula':'N_PENDING+8 on completed resume; prefixes have no more than this','pending_count_upper_current':None,
 'historical_prefix_check':'17+7=24 because no RESUMED event','no_PROGRESS_uniqueness_bound_on_stuttering':True,
 'CLOSED_race':'Entry/check_base reject markers; STOP can race after check, allowing an in-flight record. The raw event sink has no terminal guard. Frozen callers do not invoke it recursively from seal/admin.',
 'STOP_new_work_rule':'Do not strengthen safe stop dominance into a zero-post-marker-write promise that current event() does not implement.'})

# Byte algebra: native event templates plus explicit ABI width hypotheses.
mode=max((s for s in read(S/'inputs/execution_lock.json')['allowed_scopes'] if s!='PT_STARTUP_DIAGNOSTIC_ONLY'),key=len)
window={'batch_id':'batch14','boot_id':'b'*36,'T0':0,'deadline':0,'stop_at':0,'execution_mode':mode,
 'source_manifest_sha256':'a'*64,'execution_lock_sha256':'a'*64,'contract_sha256':'a'*64,'authorization_sha256':'a'*64}
base={'event':'EXIT_CLASSIFICATION_CHECK','handoff_id':'a'*64,'revision':4,'identity':{'pid':0,'start_ticks':0,'boot_id':'b'*36},
 'window':window,'boottime':0,'utc_ns':0,'boot_id':'b'*36}
facts={'closed':False,'binding_ok':True,'sender_ok':True,'version_ok':True,'window_ok':True,'budget_ok':True,'receiver_ready':True,'receiver_alive':True,'stop_alive':True,
 'witness':None,'now':0,'expires':0,'prepared':True,'commit':True,'durable_ack':True,'exit_observed':True}
def enc(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
pending={**base,'facts':facts,'verdict':'PENDING'}
common_delta=(10-1)+(20-1)+(20-1)+4*(25-1) # pid/ticks/utc and3window+boottime floats
Lp=len(enc(pending))+common_delta+2*(25-1)
terminal={**base,'facts':{**facts,'witness':0},'verdict':'VERIFIED'}
Lx=len(enc(terminal))+common_delta+2*(25-1)+(11-1)+16 # every boolean may use false(5) instead of true(4); conservative16 fields
transition={**base,'event':'LAUNCHER_EXIT_OBSERVED'}
Lstate=len(enc(transition))+common_delta
ack={**base,'event':'SENDER_ACK_OBSERVED','commit_sha256':'a'*64}
Lack=len(enc(ack))+common_delta
Lmax=max(Lp,Lx,Lstate,Lack)
save('NATIVE_RECORD_BYTE_ALGEBRA.json',{'status':'CONDITIONAL_PROVED_CLOSED_NATIVE_CALLERS_AND_ABI_WIDTHS','source_enforced_row_cap':None,
 'codec':'CPython3.12 json compact sorted keys,ensure_ascii=True,UTF-8,1 LF included','field_widths':{
 'batch_id':7,'boot_UUID':36,'hash_hex':64,'mode':len(mode),'revision':1,'pid_decimal':10,'proc_start_ticks_decimal':20,'utc_ns_signed_decimal':20,
 'binary64_JSON_number':25,'witness_signed_exit_decimal':11},'templates':{'pending':pending,'terminal':terminal,'transition':transition,'ack':ack},
 'encoded_skeleton_bytes':{'pending':len(enc(pending)),'terminal':len(enc(terminal)),'transition':len(enc(transition)),'ack':len(enc(ack))},
 'record_upper_bytes':{'pending':Lp,'all_classification':Lx,'state_transition':Lstate,'ACK':Lack,'common_all_native':Lmax},
 'ABI_hypotheses':['pid_t signed32','proc start_ticks unsigned64 representation','CPython time_ns representable in signed64','Python binary64 repr uses <=25 JSON characters',
 'Kernel boot UUID36; fixed native fields and frozen ASCII namespace; no arbitrary Root caller injection'],
 'source_width_enforcement':'No explicit digit/byte validators in event(); ABI/kernel representation assumptions are separate from actual source caps.',
 'absent_native_fields':['task_id','raw exception string','traceback','raw systemd stdout/stderr','full resources map'],
 'general_event_API':'kind/**data untyped; arbitrary extra callers outside closed-world scope have no such bound',
 'future_namespace':'Recompute exact batch/mode lengths from each future frozen identity; no automatic cross-version bound inheritance',
 'total_current':'UNRESOLVED because N_PENDING lacks a contract maximum'})

# Quota is a numerical normative proposal only, without an implementation.
Q=256;Pmax=Q-1;total_rows=Q+6+1
sidecar={'schema':'C09-LOG-QUOTA/1-DRAFT','binding':window,'policy_sha256':'a'*64,'handoff_id':'a'*64,'used':256,'pending_written':255,
 'total_written':263,'status':'EXHAUSTED_FAIL_CLOSED','generation':1}
Lmeta=len(enc(sidecar))+3*(25-1)
failure={'schema':'C09-LOG-QUOTA-FAIL/1-DRAFT','handoff_id':'a'*64,'batch_id':'batch14','boot_id':'b'*36,
 'reason':'C09_PENDING_ALLOWANCE_EXHAUSTED','used':256,'pending_written':255,'boottime':0,'utc_ns':0}
Lfail=len(enc(failure))+(25-1)+(20-1)
quota={'schema':'C09-PENDING-QUOTA-CONTRACT/1-DRAFT','status':'PROPOSED_NOT_EFFECTIVE','runtime_enabled':False,'user_approved':False,
 'count_basis':'256 is an explicit review policy using the established native-review block size; it is a new separate allowance, not a bound implied by current state machine or a transfer of existing MR credits.',
 'classification_attempts':Q,'pending_record_max':Pmax,'terminal_check_reserved_slots':1,'state_transition_max':6,'ACK_max':1,'all_C09_native_rows_max':total_rows,
 'single_record_max_bytes':Lmax,'main_log_total_max_bytes':total_rows*Lmax,'sidecar_max_bytes':Lmeta,'failure_record_max_bytes':Lfail,
 'total_quota_evidence_max_bytes':total_rows*Lmax+Lmeta+Lfail,'record_codec_profile':'Exact native schema/closed callers plus explicit field-width validation proposed',
 'producers':'One shared handoff binding and aggregate log envelope; only authenticated current Receiver spends classification credits; fixed Sender/resume stage/ACK categories retain their own maxima.',
 'prepay':'If approved, a separate256 visit block is charged before launching C09 controller/ready marker/counter fixation; after handoff counter snapshot only protected local log allowance is spent.',
 'append_order':['Check source identity, binding, stop/deadline and available allowance under existing lifecycle serialization',
 'Persist reservation/used cursor before logging; count full encoded UTF-8+LF bytes before append','Append exact raw event bytes and fsync; uncertain write/fsync => stop/poison, no refund or continuation'],
 'last_attempt':'Attempt256 may log a terminal verdict. If it is still PENDING after255 pending rows, emit only the bounded fixed failure receipt then request safe close; no further polling.',
 'crash_rule':'Reserved-but-unwritten credit is burned; missing/corrupt/foreign quota data refuses resume/reinitialization. No reset of T0/global R/log quota.',
 'failure_evidence':'Preserve all existing raw log bytes and ACK/commit/witness/state/counter. One fixed bounded reason summary, no truncating/replacing originals. Fallback or missing emergency persistence stays UNKNOWN.',
 'liveness_cost':'Any finite quota can be exhausted by a legal fast Receiver schedule before coordinator gets CPU. Safety-preserving early close does not prove successful C09 liveness.',
 'future_files':'At most2 new fixed quota/failure objects plus at most2 failed staging leftovers is a proposed normative envelope; actual code/extra tests/MR rule need recount.',
 'new_visits_estimate':256,'old_calibration_bound':68498,'conditional_bound_before_other_new_tests':68754,
 'full_capacity_approval_ready':False,'new_mechanism':False,'G_status':'COVERED_BY_G_BOUNDED_LOG_COUNTER_PREPAID_ALLOWANCE'}
save('C09_LOG_QUOTA_CONTRACT_DRAFT.json',quota)

# Aggregate bytes: accepted-input limits and generation bounds remain distinct.
byte_families=[
 {'id':'C09_NATIVE','producer_bound':None,'conditional_row_max':Lmax,'history':len(raw),'needs':'quota count/row/total with persistent fail-closed accounting'},
 {'id':'GLOBAL_BUDGET_JOURNAL','producer_bound':None,'healthy_transactions_upper':1000000,'healthy_records_upper':2000000,
 'gate_accept_limits':{'records':200000,'line':16384},'terminal_accept_limits':{'line':32768,'total':33554432},
 'coarse_if_all_generated_lines_16384':2000000*16384,'needs':'Source-bound row size and aggregate generation/preservation workload; acceptance cap does not limit append production'},
 {'id':'C03_SHARED','producer_bound':16777216,'type':'SOURCE_FTRUNCATE_FIXED'},
 {'id':'BINARY_COUNTER','producer_bound':24,'type':'SOURCE_FIXED_STRUCT'},
 {'id':'READINESS_ROWS','per_row_cap':131072,'row_count_cap':602,'cap_product':602*131072,'type':'WRITE_SIZE_CHECK_AND_BOUNDED_SAMPLE_LOOP'},
 {'id':'S34_TRACE','per_row_cap':4096,'actors':48,'events_per_actor_cap':256,'cap_product':48*256*4096,'type':'WRITE_CAP_PRODUCT_NOT_TIGHT_SOURCE_SIZE'},
 {'id':'S34_ATOMIC_METADATA','per_object_write_cap':16384,'type':'WRITE_CAP'},
 {'id':'C09H34','event_files':204,'reader_file_cap':65536,'reader_event_product':204*65536,'type':'READ_ACCEPT_CAP; writer has no identical row-size guard'},
 {'id':'BOOT_IPC_MR_PT_PF_TR_RA','producer_bound':None,'read_caps':['Root trusted JSON4MiB','BC private reader128KiB','MR event write32KiB'],
 'needs':'Per-schema serialization/record-count/aggregate proof; untouched read caps alone are insufficient'},
 {'id':'STDOUT_STDERR_SYSTEMD_JOURNAL','producer_bound':None,'type':'EXTERNAL_CAPTURE_AND_TRACEBACK','needs':'G._run captures PIPEs without a byte cap; full journal export is not source-volume bounded'},
 {'id':'F1_F4_OUTPUTS','producer_bound':None,'file_count_plan':196,'needs':'Per-state/strategy/trace/report serialization size, generated successors/witness trees and aggregate bound'},
 {'id':'EXIT_EXCEPTION_RAW','producer_bound':None,'type':'MIXED_FIXED_COUNTS_VARIABLE_BYTES','needs':'SEAL_ERROR repr has no length guard; bounded MR event/first_error fields do not bound all stderr/tracebacks'},
 {'id':'NATIVE_MANIFEST_ZIP_ADMIN','producer_bound':None,'accepted_caps':{'manifest':4194304,'native_zip':33554432,'native_uncompressed':33554432,'admin_export_bytes':33554432},
 'needs':'Bound all input bytes before native builder G.digest(read_bytes)/ZipFile.write and preserve aggregate including nested native ZIP'}]
save('TOTAL_BYTE_FAMILY_AUDIT.json',{'families':byte_families,'B_raw_total':None,'B_pending_current':None,'B_total_archive_current':None,
 'equation':'U_native=R_raw+M_native; Z_native=sum D(s_i)+H_native; admin_export=R_raw+M_native+Z_native; U_admin=admin_export+host_streams+source_locks+M_admin',
 'capacity_status':'CAPACITY_CONTRACT_NOT_READY','historical_sizes_are_not_worst_case':True})
N=4451;D=6;F=D*255+(D-1);B=33554432
header=22+N*(92+2*F) # conservative16-byte descriptors; source32-bit members/seekable format
compress=B+(B>>12)+(B>>14)+(B>>25)+13*N
save('ZIP_BOUND_ALGEBRA.json',{'category':'CONDITIONAL_FORMAT_AND_LIBRARY_BOUND_NO_ARCHIVE_BUILT',
 'scope':'Admitted ZIP32 input profile only; generated raw bytes still unresolved','N':N,'component_bytes_assumption':255,'native_relative_components_max_source_profile':6,'F':F,
 'header_formula':'H <=22+sum(30+f_i+46+f_i+16), empty extra/comments, conservative descriptor allowance; ZIP64 not needed for bounded32MiB data/profile',
 'header_upper':header,'decompression_input_limit':B,
 'deflate_assumption':'Exact default zlib compressBound-compatible bound for pinned runtime/default parameters; raw-DEFLATE output bounded conservatively by wrapper bound. Requires library/parameter proof before adoption.',
 'deflate_sum_formula':'sum D(s_i) <= U+(U>>12)+(U>>14)+(U>>25)+13*N','conditional_compressed_data_upper':compress,
 'conditional_zip_upper_at_U32MiB':compress+header,'ZIP_STORED_upper':B+header,'compressed_bound_fits_current32MiB':compress+header<=B,
 'filename_scope_note':'Closed frozen paths/shadow fixture depth and Linux NAME_MAX255; future namespaces/schema require review. Generic ZIP format permits larger names/extras/comments and cannot use this profile without checks.',
 'archive_total_ready':False,'no_assumed_compression_savings':True})

# Exact source audit and corrected family coverage without changing its sum.
count=read(PREV/'evidence/FINAL_COUNT_CLOSURE_CALCULATION.json');boot=next(r for r in count['families'] if r['id']=='BOOT_FIXED')
assert 'inputs/root_private/boot/pt_expected_abort.json' in boot['paths']
assert 'inputs/root_private/boot/mr_events.lock' not in boot['paths']
boot['paths'].remove('inputs/root_private/boot/pt_expected_abort.json');boot['paths'].append('inputs/root_private/boot/mr_events.lock');boot['paths'].sort()
boot['basis']='Full formal scope only: include mr_events.lock; exclude pt_expected_abort.json guarded by PT_STARTUP_DIAGNOSTIC_ONLY. Other fixed-family cardinalities retained.'
count['scope']='CALIBRATE_S1S9_THEN_F1_F4 with unchanged frozen source/input, closed-world writers, once activation/resume/first-failure assumptions; separate PT/MR schemes require their own scope proof.'
count['coverage_correction']={'historical_omission':'mr_events.lock opened by manager_recovery.event at source55 via locked()',
 'unreachable_old_slot':'pt_expected_abort.json is only produced by expected_prewindow_abort, called only under PT_STARTUP_DIAGNOSTIC_ONLY, excluded in full formal scope',
 'no_physical_files_deleted':True,'old_file_table_preserved':True,'numeric_delta':0,'scope_must_be_explicit':True}
assert sum(r['count'] for r in count['families'])==4450
save('COUNT_SCOPE_COVERAGE_REVIEW.json',count)
actual_manifest=read(I/'batch14/native_snapshot/out/EVIDENCE_MANIFEST.json')
lock_name='inputs/root_private/boot/mr_events.lock';assert lock_name in actual_manifest['files']
save('COUNT_COVERAGE_FINDING.json',{'status':'SOURCE_TABLE_COVERAGE_CORRECTED_FULL_SCOPE_ONLY','missing_prior_path':lock_name,
 'historical_native_manifest_row':actual_manifest['files'][lock_name],'omission_is_historical_not_new_runtime_file':True,
 'compensating_unreachable_path':'inputs/root_private/boot/pt_expected_abort.json','guard_source':'guard.py:1042 scope==PT_STARTUP_DIAGNOSTIC_ONLY',
 'full_scope_count_upper':[4450,4451,4452],'numbers_are_source_conditional_envelope':True,
 'new_quota_or_MR_impl_applied':False,'future_delta':'4450 + delta_quota_objects/staging + delta_quota_tests + delta_cross_instance_inputs/records + any changed cleanup rules'})

# Precise producer/source ranges include the surrounding logs and consumers.
spans={'c09_handoff.py':[(14,34),(75,90),(115,134),(138,156),(168,197),(199,251),(252,295),(297,346)],
 'guard.py':[(624,628),(718,726),(749,770),(771,823),(950,960),(993,1027),(1219,1243)],
 'manager_recovery.py':[(51,69),(317,400)],'terminal_evidence.py':[(99,120),(143,186)],
 'startup_lifecycle.py':[(452,519)],'c09_regression.py':[(52,75)],'range_evidence.py':[(307,351)]}
excerpts={}
for name,ranges in spans.items():
 lines=src[name].splitlines();excerpts[name]={'sha256':h(S/'src'/name),'ranges':[{'start':a,'end':min(b,len(lines)),'lines':[f'{i}: {lines[i-1]}' for i in range(a,min(b,len(lines))+1)]} for a,b in ranges]}
save('SOURCE_EXCERPTS.json',excerpts)
save('ANALYSIS_SUMMARY.json',{'date':'2026-11-15','history_files':len(history),'frozen_files':64,'prior_review_files':8,
 'native_pending_producer_sites':1,'native_logging_sites':3,'historical_pending_rows':17,'historical_native_rows':24,'historical_bytes':27144,
 'pending_record_status':'C09_PENDING_RECORD_BOUND_UNPROVABLE_UNDER_CURRENT_CONTRACT','conditional_native_record_max':Lmax,
 'proposed_pending_max':255,'proposed_all_native_rows_max':263,'proposed_main_log_bytes':263*Lmax,
 'total_bytes':'UNRESOLVED','capacity_status':'CAPACITY_CONTRACT_NOT_READY','MR_rule':'PROPOSED_NOT_EFFECTIVE',
 'WSL_calls':0,'target_imports':0,'dynamic_tests':0,'runtime_edits':0,'T0':None,'deadline':None,'R':None})
print(json.dumps({'history_files':len(history),'historical_pending':17,'historical_rows':24,'L_native_conditional':Lmax,
 'quota_pending':255,'quota_log_rows':263,'quota_log_bytes':263*Lmax,'capacity':'NOT_READY','runtime_changes':0}))
