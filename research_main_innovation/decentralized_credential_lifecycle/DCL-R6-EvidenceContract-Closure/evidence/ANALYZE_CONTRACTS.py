"""Host-only source, contract graph and finite lifecycle model analysis.

No frozen program imports, archive checker execution, service or protocol run.
The scripts here calculate review artifacts; no admission/packaging mechanism.
"""
from pathlib import Path
import ast,hashlib,json,shutil,zipfile,collections
from datetime import datetime,timezone
P=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
I=Path(r'D:\毕业设计\DCL-R6-isolated-verification')
O=P/'DCL-R6-EvidenceContract-Closure';E=O/'evidence';E.mkdir(parents=True,exist_ok=True)
A=P/'DCL-R6-FullChain-AdmissionFix';S=I/'ra01'
NAV=['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']
def h(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,x):
 q=E/n;q.parent.mkdir(parents=True,exist_ok=True)
 with q.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def cp(p,q):
 q.parent.mkdir(parents=True,exist_ok=True)
 with p.open('rb') as r,q.open('xb') as w:shutil.copyfileobj(r,w)
cp(Path(r'C:\Users\a1887\.codex\attachments\07bbcc40-4eb8-40a4-8b4c-baa9bb9561b3\已粘贴的文本.txt'),E/'TASK_REQUEST.txt')
for n in NAV:cp(P/n,E/'NAV_ORIGINALS'/n)
history=[]
for root in [P,I]:
 for p in sorted(root.rglob('*')):
  if p.is_file() and not p.is_relative_to(O) and not(root==P and p.parent==P and p.name in NAV):history.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h(p)})
save('HISTORY_BASELINE.json',{'files':history})
old=read(A/'evidence/SOURCE_BASELINE_LOCK.json');sources=[]
for r in old['files']:
 p=S/r['relative'];assert h(p)==r['sha256'] and p.stat().st_size==r['bytes'];cp(p,E/'FROZEN_RA_ORIGINALS'/r['relative']);sources.append(r)
review=read(A/'evidence/STATIC_REVIEW_LOCK.json')
for r in review['files']:
 assert h(A/r['relative'])==r['sha256'];cp(A/r['relative'],E/'ADMISSIONFIX_REVIEW_ORIGINALS'/r['relative'])
save('SOURCE_AND_REVIEW_CHECK.json',{'frozen_runtime_files':sources,'review_files':review['files'],'runtime_source_changes':0,'review_source_changes':0,'imports':0})
refs=['DCL-R6-FullChain-AdmissionFix/FINAL_DECISION.md','DCL-R6-FullChain-AdmissionFix/EVIDENCE_COUNT_CONTRADICTION.md',
 'DCL-R6-FullChain-AdmissionFix/ADMIN_EVIDENCE_CONTRACT_AUDIT.md','DCL-R6-FullChain-AdmissionFix/NATIVE_ZIP_LIMIT_AUDIT.md',
 'DCL-R6-FullChain-AdmissionFix/EVIDENCE_PRESERVATION_PROOF.md','DCL-R6-FullChain-AdmissionFix/MR_NATIVE_CLOSURE_LIFECYCLE.md',
 'DCL-R6-FullChain-AdmissionFix/MR_NATIVE_CLOSURE_TEST_PLAN.md','DCL-R6-FullChain-AdmissionFix/evidence/ACTUAL_ADDITIONS.patch',
 'DCL-R6-FullChain-AdmissionFix/evidence/PROPOSED_MR_HOOK.patch','DCL-R6-FullChain-AdmissionFix/evidence/EVIDENCE_CATALOG.json',
 'DCL-R6-FullChain-AdmissionFix/evidence/EXPANDED_FULLCHAIN_LOWER_WITNESS.json','DCL-R6-FullChain-AdmissionFix/evidence/STATIC_REVIEW_LOCK.json',
 'DCL-R6-FullChain-AdmissionFix/evidence/FINAL_COMPONENT_CHECKS.json','DCL-R6-FullChain-B/FULLCHAIN_FINAL_DECISION.md',
 'DCL-R6-TR-A2/TRA2_FINAL_DECISION.md','DCL-R6-ManagerRecovery-Fix/FINAL_DECISION.md','DCL-R6-CalDiag/CALDIAG_FINAL_DECISION.md',
 'DCL-R6-FullChain-B/evidence/RESOURCE_BOUND_INDEPENDENT.json']
for rel in refs:cp(P/rel,E/'HISTORICAL_REFERENCES'/rel)
zp=A/'ADMISSIONFIX_EVIDENCE.zip'
with zipfile.ZipFile(zp) as z:
 mf=read(A/'ADMISSIONFIX_MANIFEST.json');assert z.testzip() is None
 for r in mf['files']:assert hashlib.sha256(z.read(r['relative'])).hexdigest()==r['sha256']
 assert len(z.namelist())==len(mf['files'])+1==280
assert h(zp)=='1833dac418b9cf35731192f9bfd04d2712bc7d1bc5de3d7665f7bb686816dcc8'
save('PREVIOUS_DELIVERY_RECHECK.json',{'files':279,'zip_members':280,'sha256':h(zp),'status':'PASS_ADMIN_HASH_STRUCTURE_ONLY'})

cfg={p.stem:read(p) for p in (S/'inputs').glob('*.json')}
src={p.name:p.read_text(encoding='utf-8-sig') for p in (S/'src').glob('*.py')}
trees={n:ast.parse(t) for n,t in src.items()}
# Disjoint pathname families. An upper bound is a union envelope, not the least
# realizable maximum, and creates no new runtime limit or file objects.
flat=set();boot=set();public=set()
for n in ast.walk(trees['root_ipc.py']):
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='allowed' for t in n.targets):flat.update(ast.literal_eval(n.value))
for t in trees.values():
 for n in ast.walk(t):
  if isinstance(n,ast.Call) and ast.unparse(n.func)=='store.put' and n.args:
   is_public=any(k.arg=='public' and isinstance(k.value,ast.Constant) and k.value.value for k in n.keywords)
   if isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str):(public if is_public else boot).add(n.args[0].value)
flat|=public|{'BATCH14_AUTHORIZATION_TEXT.txt','execution_authorization.json','BOOT_START.json','BOOT_RESUME.json',
 'C00_READINESS.json','C10_READINESS.json','c09_lifecycle.lock','launcher.lock'}
cases=[f'C{i:02}' for i in range(13)]+['C09H','RANGE','FORMAL']
flat|={f'{p}_{c}.json' for p in ['ticket','result'] for c in cases}
boot|={'activation.lock','pt_phase.lock','mr_credit.lock','mr_review.lock','mr_close.lock','mr_seal.lock',
 'pt_events.jsonl','mr_events.jsonl','mr_close_attempts.jsonl'}
boot|={f'entry_{p}.json' for p in ['initial','resume']}|{f'child_{p}.json' for p in ['initial','resume']}
boot|={f'mr_{p}_{c}.json' for p in ['start','review'] for c in ['C06','C07','C09']}
boot_jobs=312+len(cfg['boot_contract']['jobs'])+len(cfg['ledger_gate_contract']['jobs'])
ready_slots=2*(cfg['readiness_contract']['sample_cap']+1)
ipc=set()
for i,j in enumerate(cfg['root_ipc_contract']['jobs']):
 scenario=j['scenario'];mutant=j.get('mutant');base=f'inputs/root_private/wait_fixture_{i:03}'
 if j['kind']=='file':
  if scenario in ['receipt_read','receipt_write']:ipc.add(f'inputs/ipc_readable_fixture_{i:03}.json')
  elif scenario in ['private_read','private_write']:ipc.add('inputs/root_private/ipc_case_999.json')
  elif scenario in ['bad_batch','bad_boot','bad_lock','bad_digest','outside']:pass
  else:
   if scenario not in ['fault_after_create','fault_file_fsync','fault_rename']:ipc.add(f'out/ipc_fixture_{i:03}.json')
   if scenario in ['symlink','hardlink']:ipc.add(f'out/ipc_fixture_{i+100:03}.json')
   if scenario in ['historical','bad_metadata'] or mutant in ['root600','ignore_permissions']:ipc.add(f'out/ipc_fixture_{i:03}.json.historical')
 elif j['kind']=='wait':
  ipc.add(base+'/inputs/batch_state.json')
  if scenario not in ['timeout','closed_wait']:ipc.add(base+'/out/ready.json')
  if scenario in ['stop_before','repeat_stop','socket_cancel','fd_cancel','stop_after_ready','ack_stop','stale'] or mutant=='ignore_stop':ipc.add(base+'/out/STOP_REQUEST.json')
  if scenario in ['closed','late_ack','closed_wait'] or mutant=='ignore_closed':ipc.add(base+'/inputs/CLOSED.json')
  if mutant in ['ignore_stop','ignore_closed']:ipc.add(base+'/shadow/inputs/batch_state.json')
ipc|={f'inputs/root_private/ipc_case_{i:03}.json' for i in range(56)}
ipc|={'inputs/root_private/waitpid_<initial>.json','inputs/root_private/waitpid_<resume>.json','inputs/root_private/c09_events.jsonl'}
out_ipc=sum(p.startswith('out/') for p in ipc)

s_rows=[];s_count=0;s_meta=0;s_actors=0
for j in cfg['safety_contract']['jobs']:
 worker=j['kind'] in ['crash','concurrent'];actors=1+int(worker);facts=2 if j['kind']=='concurrent' else 1
 common=8;extra_worker=4*int(worker);snap=2*int(j['kind']=='crash');partial=int(j['kind']=='short_write');halt=int(j['kind'] in ['short_write','fsync_error']);barrier=6*int(j['kind']=='concurrent')
 count=common+extra_worker+facts+snap+partial+halt+barrier
 meta=3+2*int(worker)+halt # lifecycle/CLOSED/checker, worker_go/process, io_halted
 s_rows.append({'case_id':j['case_id'],'actors':actors,'named_regular_or_retained_slots':count,'common':common,'worker_extra':extra_worker,
 'registry':facts,'snapshots':snap,'partial_capture':partial,'halt_file':halt,'barriers':barrier,'G_atomic_metadata_targets':meta,
 'range_core_temp_slots':2*actors,'core_temp_proof':'One intent plus one task-fact target per actor; fixed PID/TID. Rename to mutant_retained preserves object count.'})
 s_count+=count;s_meta+=meta;s_actors+=actors
controllers=8*len(cases)
out_misc=3+3+1+4+2*3+1+3+4*3 # budget3,facts3,STOP,ready4,child pairs6,shared,local3,C11 mirrors12
models=195+1 # fixed F1/F4 input/results plus mutable summary
c09h=sum(len(j['events'])+1 for j in cfg['c09_contract']['jobs'])
ledger_raw=3*18-1
abort=2*3+2*4+2
seal_calls=1+2+2+1+1
stop_calls=abort+2*2+1+1+1
# Repeated atomic replacement uses fixed temp names for each file/writer.
# Per-actor core registry/intent temps are partitioned out, preventing overlap.
g_temp_targets=controllers+out_misc-3+models+c09h+out_ipc+s_meta
global_writers=len(cases)+14+1
t_payload=2*g_temp_targets+global_writers+2*3
t_core=2*s_actors
# BC temporary names are random, so bound invocation counts, not token values.
t_bc=(3+2+2+2+1+1+6+7+(256+4)+3*abort+seal_calls+2)
# Expected IPC fault3, ordinary first publication failure per Root role4,
# abort/fallback4 each, ordinary stop2, seal1, four seal-error publications.
t_publish=3+4+4*abort+2*(stop_calls-abort)+seal_calls+4
families=[
 {'id':'FLAT_INPUTS','count':len(flat),'paths':sorted('inputs/'+s for s in flat),'basis':'RootIPC allowed fixed names, public Store targets, auth2, lifecycle locks,16 ticket/result pairs'},
 {'id':'BOOT_FIXED','count':len(boot),'paths':sorted('inputs/root_private/boot/'+s for s in boot),'basis':'All fixed private Store.put targets, six locks/three append logs and phase/start/review names'},
 {'id':'BOOT_SUITE_ROWS','count':boot_jobs,'basis':'PT64/PF48/TR40/RA32/READY64/MR64 =312; BC40; ledger descriptor18'},
 {'id':'NATIVE_READINESS_SAMPLES','count':ready_slots,'basis':'C00/C10 each sample_cap300 plus one lease confirmation; 2*(300+1)'},
 {'id':'IPC_AND_WAITPID','count':len(ipc),'paths':sorted(ipc),'basis':'Scenario-specific IPC files/wait context/shadow,56 raw cases,2 scheduler waitpids,c09 append log. Nonregular link slot conservatively included.'},
 {'id':'C09H_RAW','count':c09h,'basis':'Sum actual frozen events204 plus34 per-job oracle files'},
 {'id':'LEDGER_NATIVE_SPECIMENS','count':ledger_raw,'basis':'18*3 minus one deliberately absent intent'},
 {'id':'CONTROLLER_FILES','count':controllers,'basis':'16 no-restart services times eight fixed suffixes'},
 {'id':'PROBES_AND_GLOBAL_BUDGET','count':out_misc,'basis':'global budget3/global facts3/STOP1/ready4/child pairs6/shared1/C05 local3/C11 mirrors12'},
 {'id':'S34_NAMED','count':s_count,'basis':'Per frozen scenario table, traces/ledger/registry/checker/worker/barrier/snapshot/partial files'},
 {'id':'MODEL_FILES','count':models,'basis':'F1 31 plus F4 164 plus mutable summary1'},
 {'id':'PAYLOAD_FIXED_TEMP','count':t_payload,'basis':f'2*{g_temp_targets} non-core atomic targets +{global_writers} shared global-intent writers +6 global fact owner/claim writers'},
 {'id':'S_CORE_TEMP','count':t_core,'basis':f'2*{s_actors} per-scenario actor intent/fact temp targets; retained moves keep count'},
 {'id':'BOOT_RANDOM_TEMP','count':t_bc,'basis':'3 prepare audits+2 activation updates+2 entry+2 child+1 before-seal+1 resume+6 scheduler+7 phases+256 credit updates+4 failed callers+3*abort16+seal7+2 public qualifiers'},
 {'id':'ROOT_RANDOM_TEMP','count':t_publish,'basis':'3 expected IPC staged faults+4 ordinary first Root failures+4*abort16+2*7 ordinary stop calls+7 seal manifest attempts+4 seal-error writes'},
 {'id':'DYNAMIC_STOP_FILES','count':2*stop_calls,'basis':f'stop_result/event at most2 per stop_tree call; C_stop={stop_calls}=abort16+coordinator4+external1+C09_1+normal1'},
]
K=sum(r['count'] for r in families)
normal_exclusions=3*abort+2*abort+4*abort # boot closing temps, dynamic abort stop files, root cleanup temps
formula={'schema':'EVIDENCE-CARDINALITY-CLOSURE/1','scope':'Frozen source-only closed-world namespace; complete input range or a first-failure prefix, bounded wrappers; no arbitrary external writers/restarts/reentry.',
 'status':'FINITE_SOURCE_DERIVED_COUNT_ENVELOPE_CONDITIONAL','raw_nonarchive_upper':K,'native_members_upper':K+1,'admin_originals_upper':K+2,'admin_zip_members_upper':K+17,
 'raw_lower_full_completed':1082,'native_lower_full_completed':1083,'admin_originals_lower_full_completed':1084,
 'C_abort':abort,'C_seal_attempts':seal_calls,'C_stop_tree':stop_calls,'exception_stop_unique_extra_upper':2*stop_calls+5,
 'exception_note':'5 named exception targets: STOP/CLOSED/mr_first_failure/mr_close_state/mr_external_closing; named targets already counted in families. Random failed staging additionally bounded in separate temp families.',
 'families':families,'S34_table':s_rows,'success_and_failure_union':True,'tight_least_maximum':False,
 'normal_only_deduction_not_used':normal_exclusions,'upper_bound_is_new_guard':False,'old_256_257_modified':False,
 'critical_assumptions':['Only fixed locked programs and frozen job lists write current ROOT','Restart=no; one activation; at most one C09 resume; no externally injected calls',
 'Payload actors/threads limited by frozen call graph, no additional helper restarts','First unexpected exception unwinds; Root abort/seal wrappers do not recurse',
 'Root namespace ownership and trusted kernel/TCB hold; no unrelated privileged/same-UID file injection'],
 'proof_limits':['Conservative disjoint family union, not a measured complete manifest or exact attainable maximum','Cardinality abstraction is manual-review source proof with AST evidence; not machine-verified semantic equivalence',
 'Counts do not prove per-file bytes or finite end-to-end IO work; C09 unmetered append remains a separate blocker']}
save('COUNT_CLOSURE_CALCULATION.json',formula)

# Every lower-witness leaf has a phase-correct dependency record. Hashes remain
# unknown for unrun outputs. Source/contract and observed historical hashes live
# in separate records and never masquerade as current output hashes.
lower=read(A/'evidence/EXPANDED_FULLCHAIN_LOWER_WITNESS.json')['rows']
nodes={};edges=[]
def node(i,kind,producer,path,required,dep=(),hash_value=None,retention='PRESERVE_ORIGINAL_BYTES',storage='Frozen namespace or separately sealed original'):
 assert i not in nodes
 nodes[i]={'evidence_id':i,'producer':producer,'source_path':path,'content_hash':hash_value,'evidence_type':kind,
 'required_by':required,'verification_rule':'Pinned identity/bytes plus the named source-specific oracle; current raw facts stay current',
 'storage_requirement':storage,'retention_requirement':retention,'dependency_ids':list(dep)}
 for d in dep:edges.append([d,i])
def macro(i,dep,kind='derived_verification',path=None):node(i,kind,i,path or '<phase>/'+i,'Frozen contract or explicitly pending proposal',dep)
macro('PROGRAM_BYTES',[],'test_input_and_identity',str(S/'src'))
macro('STATIC_INPUTS',[],'test_input_and_identity',str(S/'inputs'))
macro('STATIC_MANIFEST',['PROGRAM_BYTES','STATIC_INPUTS'],'manifest_integrity')
macro('EXECUTION_LOCK',['STATIC_MANIFEST','PROGRAM_BYTES'],'test_input_and_identity')
macro('AUTHORIZATION',['EXECUTION_LOCK','STATIC_MANIFEST'],'test_input_and_identity')
macro('ACTIVATION',['AUTHORIZATION'],'native_raw_fact')
macro('CURRENT_RUNTIME',['ACTIVATION'],'native_raw_fact')
macro('T0_AND_CAL_LEDGER_PREFIX',['CURRENT_RUNTIME'],'native_raw_fact')
macro('CURRENT_C00_C12_C09',['T0_AND_CAL_LEDGER_PREFIX'],'native_raw_fact')
pre=[];formal=[]
for k,r in enumerate(lower):
 i=f'E{k:04}';path=r['relative'];is_formal=path.startswith('out/generated_inputs/') or path.startswith('out/reports/')
 kind='test_input_and_identity' if 'generated_inputs/' in path else 'derived_verification' if '/oracle.json' in path or 'checker_observation' in path or '/reports/' in path else 'test_execution_raw_fact'
 dep=['FORMAL_ADMISSION','PROGRAM_BYTES','STATIC_INPUTS'] if is_formal else ['T0_AND_CAL_LEDGER_PREFIX','PROGRAM_BYTES','STATIC_INPUTS']
 node(i,kind,r['producer'],r['source_path'],r['required_by'],dep)
 (formal if is_formal else pre).append(i)
macro('RAW_CALIBRATION',['CURRENT_C00_C12_C09',*pre],'native_raw_fact')
macro('GATE18_AND_RANGE_Q',['RAW_CALIBRATION'])
macro('RESOURCE_QUALIFICATION',['GATE18_AND_RANGE_Q','EXECUTION_LOCK'])
macro('FORMAL_ADMISSION',['RESOURCE_QUALIFICATION','CURRENT_RUNTIME'])
macro('FORMAL_END',['FORMAL_ADMISSION',*formal],'native_raw_fact')
macro('TERMINAL_RAW',['FORMAL_END'],'native_raw_fact')
macro('PRE_NATIVE_REVIEW',['TERMINAL_RAW'])
macro('NATIVE_MANIFEST',['PRE_NATIVE_REVIEW','RAW_CALIBRATION','FORMAL_END'],'manifest_integrity')
macro('NATIVE_ZIP',['NATIVE_MANIFEST'],'archive_seal_metadata')
macro('POSTEXIT_NATIVE_AUDIT',['NATIVE_ZIP','TERMINAL_RAW'],'administrative_report')
macro('ADMIN_SNAPSHOT',['NATIVE_ZIP','NATIVE_MANIFEST','TERMINAL_RAW'],'archive_seal_metadata')
macro('ADMIN_MANIFEST',['ADMIN_SNAPSHOT','POSTEXIT_NATIVE_AUDIT','EXECUTION_LOCK'],'manifest_integrity')
macro('ADMIN_ZIP',['ADMIN_MANIFEST'],'archive_seal_metadata')
macro('FINALIZATION_RECEIPT',['ADMIN_ZIP','NATIVE_ZIP'],'archive_seal_metadata')
macro('POSTSEAL_MR_CERTIFICATE',['FINALIZATION_RECEIPT','ADMIN_ZIP','NATIVE_ZIP','TERMINAL_RAW'],'derived_verification','<outside-A-root>/certificate.pending.json')
macro('B_USE_SPEC',['POSTSEAL_MR_CERTIFICATE','EXECUTION_LOCK'],'test_input_and_identity')
macro('B_AUTH_RECEIPT',['B_USE_SPEC'],'test_input_and_identity')
macro('B_USE_REALIZATION',['B_AUTH_RECEIPT','B_USE_SPEC'],'native_raw_fact')
macro('B_CURRENT_QUALIFICATION',['B_USE_REALIZATION'],'native_raw_fact')

def topsort(ids,es):
 adj={i:[] for i in ids};degree={i:0 for i in ids}
 for a,b in es:assert a in adj and b in adj;adj[a].append(b);degree[b]+=1
 q=collections.deque(sorted(i for i,v in degree.items() if not v));order=[]
 while q:
  a=q.popleft();order.append(a)
  for b in adj[a]:
   degree[b]-=1
   if degree[b]==0:q.append(b)
 return order,[i for i,v in degree.items() if v]
order,cyclic=topsort(nodes,edges);assert not cyclic
cycles=[{'id':'MR_CERT_NATIVE_SELF_HASH','status':'HYPOTHETICAL_CONTRACT_CYCLE_NOT_PRESENT_IN_FROZEN_COLLECTOR',
 'cycle':['POSTSEAL_MR_CERTIFICATE','NATIVE_MANIFEST','NATIVE_ZIP','POSTSEAL_MR_CERTIFICATE'],
 'trigger':'Require post-seal certificate before creating native manifest and include it inside that same native preimage'},
 {'id':'ADMIN_FINAL_RECEIPT_SELF_HASH','status':'CUT_BY_EXISTING_MANIFEST_BOUNDARY',
 'cycle':['FINALIZATION_RECEIPT','ADMIN_MANIFEST','ADMIN_ZIP','FINALIZATION_RECEIPT'],
 'trigger':'Add finalization receipt with admin ZIP hash into that same admin ZIP'},
 {'id':'TARGET_USE_AUTH_SELF_HASH','status':'AVOID_IN_PENDING_RULE',
 'cycle':['B_AUTH_RECEIPT','B_USE_REALIZATION','B_AUTH_RECEIPT'],
 'trigger':'Authorization binds final use record hash while use record binds authorization hash; use independent use_spec then receipt then realized record instead'}]
save('EVIDENCE_DEPENDENCY_GRAPH.json',{'nodes':list(nodes.values()),'edges':edges,'topological_order':order,'acyclic':True,
 'graph_scope':'Stage/version-sensitive normative dependency graph; current source and pending cross-instance proposal are explicitly distinct; no current output bytes fabricated',
 'candidate_cycles':cycles,'raw_witness_leaf_count':len(lower),'family_schema_nodes':families})
save('FINITE_FIXED_POINT.json',{'operation':'Closure under finite typed predecessor rules, excluding collector output/receipt own preimages',
 'nodes':len(nodes),'edges':len(edges),'topological_rank_max':len(order),'closed':all(d in nodes for n in nodes.values() for d in n['dependency_ids']),
 'numeric_count_envelope':K,'bytes_fixed_point':'EVIDENCE_MAX_BOUND_UNRESOLVED_FOR_RAW_BYTES_AND_END_TO_END_WORK',
 'nonrecursive_archive_equations':{'raw':'K','native_members':'K+1','admin_originals':'K+2','admin_final_members':'K+17'},
 'original_guard_acceptance':'256/257 retained; full completed trace exceeds both; existing accepted full manifest set empty under these count guards',
 'unbounded_byte_rule':{'file':'src/c09_handoff.py','source_sha256':h(S/'src/c09_handoff.py'),'function':'Receiver.observe_exit -> event(EXIT_CLASSIFICATION_CHECK)',
 'caller':'guard._external_stop_impl ready pidfd branch while witness is PENDING','append_target':'inputs/root_private/c09_events.jsonl',
 'bound_present':'observe_until wall deadline; fsync; no visit debit or record/byte quota for repeated PENDING classifications',
 'parametric_trace':'For each n, delay coordinator witness while receiver logs n PENDING checks before fixed deadline, with per-step dt < handoff_seconds/(n+1); no minimum step-time axiom exists in frozen contract.',
 'consequence':'One filename, unclosed raw byte/record/work upper; finite file cardinality remains valid. Physical-machine finite throughput is not a frozen numerical proof.'}})

# Contract state model only: distinct symbolic windows, no native/model code.
def strict_model():
 initial=('WORK',False,False);seen={initial};queue=collections.deque([initial]);steps=[]
 while queue:
  s=queue.popleft();status,fault,formal_state=s
  nxt=[]
  if status=='WORK' and not fault:nxt.append(('native_fault_and_close',('CLOSED',True,False)))
  if status=='WORK' and fault:nxt.append(('gate_then_formal',('FORMAL',True,True)))
  for a,t in nxt:
   steps.append({'from':s,'action':a,'to':t})
   if t not in seen:seen.add(t);queue.append(t)
 return seen,steps
states,steps=strict_model();assert not any(s[2] for s in states)
cross_trace=[('A_WORK','B_OFF'),('A_FAULT','B_OFF'),('A_CLOSED','B_OFF'),('A_NATIVE_SEALED','B_OFF'),
 ('A_ADMIN_SEALED','B_OFF'),('A_POST_CERT_VALID','B_OFF'),('A_STAYS_CLOSED','B_WORK_CURRENT_CHECKS'),
 ('A_STAYS_CLOSED','B_QUALIFIED_CURRENT_PLUS_LIMITED_EVIDENCE'),('A_STAYS_CLOSED','B_F1'),('A_STAYS_CLOSED','B_F4'),('A_STAYS_CLOSED','B_CLOSED')]
save('LIFECYCLE_FORMAL_MODEL.json',{'category':'HOST_CONTRACT_STATE_EXPLORATION_NO_PROTOCOL_RUN','strict_status':'MR_LIFECYCLE_CONFLICT_PROVED_UNDER_SAME_INSTANCE_EXCEPTION_PREREQUISITE',
 'strict_states':list(states),'strict_transitions':steps,'strict_FORMAL_reachable':False,
 'minimal_inconsistent_conditions':['Native fault establishes CLOSED(B)','CLOSED(B) is absorbing','Gate(B) requires that fault already observed in B','FORMAL(B) requires WORK(B) after Gate(B)'],
 'code_only_status':'MR_LIFECYCLE_CONFLICT_NOT_ESTABLISHED_FOR_UNSTRENGTHENED_FROZEN_GATE',
 'reason':'Current M.formal_gate checks current MR64 and normal recovery, without mandatory native abnormal-closure certificate; strengthened same-instance condition is from task acceptance, not an existing executed gate.',
 'cross_trace_design_only':cross_trace,'cross_preconditions':['Policy explicitly approved','Actual A native raw/exit/STOP/CLOSED/native/admin/oracle verified','Exact reviewed artifact relation and same-boot TCB equivalence',
 'B own current qualification and resource windows','Unique B use_spec/nonce with no authority or budget transfer'],
 'windows':{'A':'symbolic T0_A/deadline_A/R_A','B':'symbolic T0_B/deadline_B/R_B'},'runtime_windows_created':0,
 'posthoc_testing_without_contract_change':'Does not discharge prerequisite gate before F1/F4','nested_fault_unit_without_parent_close':'Changes tested property; not an existing solution to strict main-batch obligation'})

# Source-line evidence and exact old/new boundary locks; no code edits.
spans={'guard.py':[(749,770),(774,808),(993,1027),(513,544)],'manager_recovery.py':[(317,400),(469,491)],
 'service_readiness.py':[(237,243),(250,267),(278,310)],'c09_handoff.py':[(75,91),(250,286)],
 'startup_lifecycle.py':[(452,519)]}
excerpts={}
for name,ss in spans.items():
 lines=src[name].splitlines();excerpts[name]={'sha256':h(S/'src'/name),'ranges':[{'start':a,'end':b,'lines':[f'{i}: {lines[i-1]}' for i in range(a,b+1)]} for a,b in ss]}
save('SOURCE_EXCERPTS.json',excerpts)
save('ANALYSIS_SUMMARY.json',{'utc':datetime.now(timezone.utc).isoformat(),'history_files':len(history),'source_files':64,'review_files':8,
 'dependency_nodes':len(nodes),'dependency_edges':len(edges),'DAG_acyclic':True,'raw_count_upper':K,'native_upper':K+1,'admin_raw_upper':K+2,'admin_zip_upper':K+17,
 'C_abort':abort,'C_stop':stop_calls,'C_seal':seal_calls,'new_guard_value_selected':False,'raw_byte_upper':'UNRESOLVED',
 'WSL_calls':0,'target_imports':0,'new_dynamic_tests':0,'T0':None,'R':None,'runtime_edits':0,'cross_gate_implementation':0})
print(json.dumps({'history_files':len(history),'DAG_nodes':len(nodes),'DAG_edges':len(edges),'raw_upper':K,'native_upper':K+1,
 'admin_originals_upper':K+2,'admin_zip_upper':K+17,'byte_bound':'UNRESOLVED','C_abort':abort,'C_stop':stop_calls,'C_seal':seal_calls}))
