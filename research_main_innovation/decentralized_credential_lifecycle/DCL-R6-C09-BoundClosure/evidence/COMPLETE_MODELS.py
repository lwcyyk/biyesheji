"""Complete numerical contract drafts and work/memory review tables only."""
from pathlib import Path
import hashlib,json
O=Path(__file__).resolve().parent.parent;E=O/'evidence';P=O.parent
def j(n):return json.loads((E/n).read_bytes())
def save(n,x):
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def enc(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
a=j('NATIVE_RECORD_BYTE_ALGEBRA.json');q=j('C09_LOG_QUOTA_CONTRACT_DRAFT.json')
L=a['record_upper_bytes'];exact=255*L['pending']+L['all_classification']+6*L['state_transition']+L['ACK']
reserved=256*L['all_classification']+6*L['state_transition']+L['ACK']
assert exact==339028 and reserved==345148
window=a['templates']['pending']['window']
sidecar={'schema':'C09-LOG-QUOTA/1-DRAFT','binding':window,'policy_sha256':'a'*64,'handoff_id':'a'*64,
 'classification_debited':256,'pending_reserved':255,'records_reserved':263,'bytes_reserved':reserved,'byte_limit':reserved,
 'status':'EXHAUSTED_FAIL_CLOSED','generation':1}
Lm=len(enc(sidecar))+3*(25-1)
Lf=q['failure_record_max_bytes']
q.update(status='PROPOSED_NOT_EFFECTIVE',single_record_max_bytes=1322,
 main_log_actual_sharp_upper=exact,main_log_total_max_bytes=reserved,sidecar_max_bytes=Lm,
 total_quota_evidence_max_bytes=reserved+Lm+Lf,quota_file_schema=sidecar,
 cursor_semantics='Counts/bytes are reserved and may be burned, never claimed written. Actual written records are independently counted from raw log.',
 cursor_updates_upper=266,quota_total_write_upper=reserved+266*Lm+Lf,
 fsync_attempts_upper=266*2+263+2+1,
 byte_count_basis='256 classification slots each reserve1322; 6 state slots reserve948; 1 ACK slot reserves1028. Unused reserved bytes burn. Actual typed emitted max339028.',
 field_profile={'batch_id':'ASCII batch[0-9]{2}, maximum7 bytes; new namespace must be frozen before approval','hash_hex':64,'kernel_boot_uuid':36,
 'pid_max_decimal_chars':10,'start_ticks_max_decimal_chars':20,'utc_ns_max_decimal_chars':20,'binary64_encoded_chars':25,
 'mode_max_bytes':len(window['execution_mode']),'revision_range':[1,6],'extra_fields':'FORBIDDEN; ABI assumptions require explicit byte/range checks in a future implementation'},
 allowed_failure_codes=['Q_EXHAUSTED','Q_ROW_SIZE','Q_TOTAL_SIZE','Q_BINDING','Q_PERSIST','Q_APPEND','Q_RECOVERY'],
 long_errors='Existing first-failure/stdout/stderr originals remain separately preserved; fixed quota summary never replaces their bytes.',
 quota_persistence='One pre-debit cursor write per observation/event, no post-write credit refund; init+bind+263 reservations+at most one poison write gives266 updates.',
 observation_work_status='UNRESOLVED for full check_base/unit_show/uncapped pipe reads; finite log output/persistence work is conditional on validated fixed schema.',
 append_IO_time='WALL_TIME_BOUND_UNRESOLVED',
 joint_H_hard_context='Existing C09H+IPC+BC conservative3269; new256 prepay would be3525 below inherited5000 only if formally assigned to that same frozen charge context. No implicit sharing authorized.',
 separate_global_estimate=68754,
 whole_capacity_ready=False)
save('proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json',q)

# Conditional budget-journal producer schema sizes, no target logger execution.
base={'protocol':'EXACT-RANGE/1','status':'COMMITTED','before':1000000,'after':1000000,'amount':1000000,
 'cap':1000000,'request':None,'boot_id':'b'*36,'boottime':0,'utc_ns':0}
Lnone=len(enc(base))+(25-1)+(20-1)
request={'protocol':'EXACT-RANGE/1','batch_id':'batch14','boot_id':'b'*36,'T0':0,'task_id':'C04.fifth-task.v1',
 'N':32896,'case':'C04','source_manifest':'a'*64,'contract_sha256':'a'*64}
Lrequest=len(enc({**base,'request':request}))+(25-1)+(20-1)+(25-1)
Tfull=68498-(32896-1)-(4096-1)-(1-1)
Bcal=2*(Tfull-3)*Lnone+6*Lrequest
Tglobal=1000000-36990
Bfull=2*(Tglobal-3)*Lnone+6*Lrequest
save('evidence/GLOBAL_JOURNAL_BYTE_MODEL.json',{'status':'CONDITIONAL_CLOSED_SCHEMA_ABI_BOUND_NO_ACTUAL_LOGGER_RUN',
 'line_None_max':Lnone,'line_request_max':Lrequest,'bulk_transaction_saving':36990,'full_calibration_transactions_upper':Tfull,
 'full_calibration_journal_bound':Bcal,'full_1m_window_transactions_upper_if_three_bulk_jobs_completed':Tglobal,
 'full_1m_journal_conditional_bound':Bfull,'full_1m_over32MiB':Bfull>33554432,
 'conservative_validator_line_cap_product':2000000*16384,
 'preconditions':'Same fixed request schema/task IDs, all completed exact child reservations, compact codec, numeric/string width hypotheses as native model; incomplete prefixes need general2*V records envelope.',
 'different_read_acceptance_caps':{'range_checker_max_records':200000,'range_checker_max_line':16384,'terminal_reader_max_bytes':33554432,'terminal_reader_max_line':32768},
 'generated_bytes_vs_acceptance':'Source journal appender has no matching byte counter. Finite visit allowance permits more bytes/records than later validators admit; no assertion that every completed model domain actually reaches its quota.'})

work=[
 {'step':'C09 current PENDING classification loop','input':'N unbounded in contract, systemctl/raw reads separately unbounded','read':'UNRESOLVED','write':'sum L_i, current N unbounded',
 'memory':'Per-row encoding plus uncapped helper PIPE/copy buffers; AS ceiling may terminate, not prove completion','FD':'Event datafd1 + lifecycle lock1, plus helper/Root existing descriptors',
 'complexity':'O(N * check_base + sum L_i)','status':'UNRESOLVED'},
 {'step':'Proposed quota log encode/append/cursor','input':f'<=263 main slots, row<=1322; cursor<={Lm}; fail<={Lf}',
 'read':f'<=266 cursor reads plus schema/context inputs not included in this sub-bound','write':f'<=345148 +266*{Lm}+{Lf}={345148+266*Lm+Lf}',
 'memory':f'O(1322+{Lm}) validated scalar row buffers; serialization object overhead/native helper context separate',
 'FD':'Log append1, existing lifecycle lock1; cursor temp/update descriptors sequential; no new persistent process/thread',
 'complexity':'O(263*Lmax +266*Lcursor); <=798 durability attempts including2 failure-record syncs and1 first-log directory sync, before other stop work',
 'status':'WORK_BOUND_PROVED_FOR_PROPOSED_LOG_COMPONENT_UNDER_SCHEMA_ONLY','wall':'WALL_TIME_BOUND_UNRESOLVED'},
 {'step':'Quota complete observation','input':'check_base, counter, ticket/marker, checked_receiver/unit_show, current source/instance proofs',
 'read':'G.trusted caps selected JSON4MiB; G._run PIPE and G.read/digest inputs lack uniform caps','write':'Bounded log subgroup only',
 'memory':'UNRESOLVED until all helper response/schema bounds fixed','FD':'Bounded source call nesting; baseline/runtime-specific FD count separate',
 'complexity':'Finite256 observation calls under draft, total byte/work still conditional on helper input bounds','status':'PARTIAL'},
 {'step':'native build','input':'R_raw unbounded, N<=4450 under old scope','read':'One full hash pass R + one compression-read pass R+manifest; ZipFile library may add metadata reads',
 'write':'Z_native +M_native, unresolved until R and format bound fixed','memory':'sorted(rglob) O(N), manifest O(N), G.digest Path.read_bytes O(max file); no max raw file proof',
 'FD':'One input data file at a time plus archive output and pre-existing/lock/dir FDs','complexity':'O(N log N+R+compression work)','status':'UNRESOLVED'},
 {'step':'terminal independent native verification','input':'Only admitted zip<=32MiB, total uncompressed<=32MiB, manifest<=4MiB, currently members<=257',
 'read':'<=32MiB member streams plus metadata/manifest; duplicate/canonical checks; failed input inspected to fail boundary',
 'write':'Read-only verification; optional separate result excluded from earlier preimage','memory':'ZipFile central directory+JSON rows O(N+manifest), chunk64KiB; Python allocation constants not a complete1GiB proof',
 'FD':'Inside terminal reader: Root directories8 +boot1 +counter1 +phase-lock1 +ZIP open+dup2 =13 incremental source descriptors, plus baseline; transient operations separately reviewed',
 'complexity':'O(N+accepted uncompressed bytes); raw builder input not covered','status':'CONDITIONAL_PROVED_FOR_ACCEPTED_INPUT','wall':'5s unresolved'},
 {'step':'post-exit native audit','input':'native manifest and archive, host/native scope/hash bindings','read':'Existing z.read(member) materializes full member; lacks matching full-set and uniform per-member prelimit in that helper',
 'write':'STARTUP_NATIVE_AUDIT outside ROOT','memory':'O(largest member +manifest/JSON), presently not bounded for all source outputs','FD':'Zip source/active member plus audit temporary query descriptors','complexity':'O(total actual bytes), volume unresolved','status':'PARTIAL'},
 {'step':'admin export/finalizer','input':'R_raw + native manifest + Z_native <=32MiB required for export; host/source sidecars additional',
 'read':'Copy pass +host hash pass +ZIP creation pass +ZIP verify pass; each variable input must be counted','write':'Admin snapshot copy +admin ZIP+fixed metadata','memory':'Native export64KiB streaming; host digest/read ZIP may allocate full files; O(N) rows/index',
 'FD':'Sequential files plus ZIP output; environment baseline not a new approved NOFILE limit','complexity':'O(N log N+copies/hashes of actual byte volume)','status':'UNRESOLVED_FOR_TOTAL','wall':'30s unresolved'},
 {'step':'paired independent archive oracles','input':'Whole manifest/member set, validated path/type/hash/size/binding','read':'Two complete accepted archive streams plus original crosschecks, up to2*B+R under respective caps','write':'Separate immutable verification receipt only',
 'memory':'O(N+manifest+chunk), independent rule code shares zipfile/parser TCB in prior review components','FD':'Archive+one sequential member stream; actual wrappers/FD limits remain environmental','complexity':'O(N+B) for admitted inputs; hashing/CRC finite','status':'CONDITIONAL_PROVED','wall':'Unresolved scheduling/storage'},
]
save('evidence/WORK_MEMORY_FD_MODEL.json',{'steps':work,'resource_limits_unchanged':{'AS_bytes':1073741824,'parent_tasks':4,'global_visits':1000000,
 'calibration_visits':100000,'total_seconds':1800,'calibration_seconds':300,'preT0_TCB_seconds':120,'stop_relative':1740},
 'FD_note':'TasksMax does not limit FDs; no new RLIMIT_NOFILE contract inferred','hard_limit_not_completion':'AS/timeout/visit caps enforce refusal/termination boundaries, not successful sealing or completed300s',
 'current_total_work_status':'UNRESOLVED','new_timed_tests':0})

coverage=j('COUNT_SCOPE_COVERAGE_REVIEW.json')
capacity={'schema':'DCL-EVIDENCE-CAPACITY/2-APPROVAL-PREPARATION','status':'CAPACITY_CONTRACT_NOT_READY','user_approved':False,'effective':False,
 'old_guards':{'admin_files':256,'native_members':257},'corrected_old_full_scope_counts':{'preseal_raw':4450,'native_members':4451,'admin_raw':4452,'admin_zip':4467},
 'single_file_generation_max':None,'total_raw_generation_max':None,'total_native_uncompressed_generation_max':None,'total_native_zip_generation_max':None,
 'acceptance_limits_preserved':{'manifest':4194304,'native_compressed':33554432,'native_uncompressed':33554432,'admin_export':33554432},
 'pending_only_draft_limits':{'attempts':256,'pending_rows':255,'all_native_rows':263,'single_row':1322,'reserved_main_bytes':reserved,'sharp_typed_main_bytes':exact,
 'metadata_cursor':Lm,'fixed_failure':Lf,'retained_quota_objects_bytes':reserved+Lm+Lf},
 'blocking_obligations':['Current C09 producers have no effective quota; new draft not implemented/approved','Clock/proc integer width assumptions need explicit field validation or runtime ABI evidence',
 'Other log/schema/stdout/traceback/model outputs and total raw size not closed','Accepted-byte caps do not bound pre-acceptance native construction',
 'ZIP metadata+deflate overhead; do not assume compressed size<=uncompressed','Admin aggregate includes native ZIP as a nested file','New quota/cross-instance inputs/tests require delta counts/bytes/visits',
 'Full native verifier/exporter/host byte/type/set/partial-archive semantics and timing need integrated review'],
 'file_policy':['Regular files only in archive, retain nonregular fixture metadata and all existing raw originals','Canonical relative paths; no traversal/backslash/drive/collision',
 'Exact manifest-member bijection, duplicate/missing/extra reject','Full raw bytes and hashes preserved; no silent truncation or partial-set PASS','Same-batch/source/boot/lock binding','Quota exhaustion/partial seal accurately FAIL/UNKNOWN'],
 'contract_activation':'Specific explicit future user approval after complete proof/integration/lock; this file authorizes no count/byte/format change'}
save('proposals/EVIDENCE_CAPACITY_CONTRACT_PROPOSAL.json',capacity)

prior=json.loads((P/'DCL-R6-EvidenceContract-Closure/proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json').read_bytes())
mr={**prior,'schema':'MR-CROSS-INSTANCE-ADMISSION-FINAL-TEXT/1-DRAFT','version':'C09-BoundClosure/review-1',
 'predecessor_rule_sha256':hashlib.sha256((P/'DCL-R6-EvidenceContract-Closure/proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json').read_bytes()).hexdigest(),
 'MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE','user_approved':False,'runtime_enabled':False,'evidence_usable_now':False,
 'recommendation':'APPROVE_RECOMMENDED','recommendation_scope':'Only narrow rule text; explicit implementation and every actual A/B execution remain separately authorized',
 'capacity_separation':'Approval of MR principle does not approve capacity/quota changes or grant resource admission. Capacity proposal currently NOT_READY.',
 'reject_missing':['Native actual event','Raw source/boot/unit/InvocationID/PID/fault-class bindings','Primary automatic STOP/CLOSED/role exit/group empty',
 'Original budget/window preservation','Native/admin complete independent verification','Exact artifact pair and allowed namespace map review','Current B independent qualification',
 'Fresh target-specific use-spec/approval/nonce without hash cycles','Any mandatory UNKNOWN/missing file/substitution/old version or wrong boot'],
 'approval_receipt_generated':False,'approved_artifact_pairs':[],'A_identity':None,'B_identity':None}
save('proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json',mr)
gates={'BC-1':{'status':'COUNTEREXAMPLE','finding':'Reachable PENDING stutter schedule family, n arbitrary in contract timing model; historical17-PENDING original witness'},
 'BC-2':{'status':'CONDITIONAL_PROVED','finding':'Current closed native schemas pending1298/all-row1322 under ABI widths; total pending unbounded under present record contract; concrete quota draft only'},
 'BC-3':{'status':'UNRESOLVED','finding':'Complete raw/native/admin byte generation lacks aggregate bounds; several concrete sources remain outside matching caps'},
 'BC-4':{'status':'PARTIAL','finding':'Conditional finite proposed log persistence work and admitted archive verification; whole observation/build/host workload and wall bounds unresolved'},
 'BC-5':{'status':'BLOCKED','finding':'CAPACITY_CONTRACT_NOT_READY; old256/257 unchanged'},
 'BC-6':{'status':'CONDITIONAL_PROVED','finding':'Narrow final MR approval/rejection text prepared; PROPOSED_NOT_EFFECTIVE, material pairs/certificates absent'},
 'BC-7':{'status':'PROVED','finding':'All examined mechanisms covered by mature generic methods G; strict separation instances0, candidate implementation0'}}
save('evidence/BC_GATE_DECISIONS.json',gates)
save('evidence/FINAL_ANALYSIS_DECISION.json',{'date':'2026-11-15','overall':'C09_SOURCE_COUNTEREXAMPLE_QUOTA_DRAFT_CAPACITY_NOT_READY_MR_PROPOSED',
 'gates':gates,'C09_record_status':'C09_PENDING_RECORD_BOUND_UNPROVABLE_UNDER_CURRENT_CONTRACT','conditional_single_row_max':1322,
 'quota_policy':{'attempts':256,'pending':255,'all_native_rows':263,'reserved_main_bytes':reserved,'cursor_bytes':Lm,'failure_bytes':Lf,'write_upper':reserved+266*Lm+Lf},
 'quota_effective':False,'capacity':'CAPACITY_CONTRACT_NOT_READY','MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE',
 'source_files_unchanged':64,'prior_review_objects_unchanged':8,'producer_edits':0,'budget_core_edits':0,'sealer_edits':0,'count_guard_changes':0,'cross_gate_code':0,
 'WSL_calls':0,'dynamic_tests':0,'native_faults':0,'F1_F4_runs':0,'T0':None,'deadline':None,'R':None,'RESOURCE_GATE_PASS':'NOT_OBTAINED',
 'F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED'})
print(json.dumps({'sharp_log_bytes':exact,'reserved_log_bytes':reserved,'cursor_bytes':Lm,'retained_quota_bytes':reserved+Lm+Lf,
 'quota_write_bound':reserved+266*Lm+Lf,'GJ_calibration_bound':Bcal,'GJ_1m_bound':Bfull,'capacity':'NOT_READY','MR':'PROPOSED_NOT_EFFECTIVE'}))
