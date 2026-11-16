"""Final targeted static proof/decision tables. No DCL program is imported/run."""
from INPUT_AUDIT import ROOT,PREV,OUT,E,RUNTIME,read,save,sha,row
import ast,json,re

assert read(E/'INITIAL_CHECK.json')['source64']=='MATCH'
sources={p.name:p.read_text(encoding='utf-8-sig') for p in (RUNTIME/'src').glob('*.py')}
cfg=read(RUNTIME/'inputs/safety_contract.json')
workers=[j['case_id'] for j in cfg['jobs'] if j['kind'] in ('crash','concurrent')]
cases=read(RUNTIME/'inputs/batch_identity.json')['cases'];controllers=[c for c in cases if c!='STOP']
assert len(controllers)==16 and len(workers)==14

# H is bounded by admitted execution contexts, not by successful visit charges.
hrows=[
 {'role':'Root initial/resume scheduler','count':2,'halts_per_context':1,'why':'scalar reserve only; before next reserve budget_health refuses; coordinator has no global-reservation caller'},
 {'role':'C00-C12 controller main threads','count':13,'halts_per_context':2,'why':'inner global _reserve catch then outer Budget.visit catch; later entry checks _HALTED before try'},
 {'role':'C05 additional budget worker thread','count':1,'halts_per_context':2,'why':'one fixed extra thread; same process flag, at most one admitted in-flight failure body per thread'},
 {'role':'C09H controller main','count':1,'halts_per_context':2,'why':'c09h_charge with Budget; same nested two catches'},
 {'role':'FORMAL controller main','count':1,'halts_per_context':2,'why':'Budget.visit; direct admission scalar uses same guard flag and does not add an independent failure episode'},
 {'role':'RANGE controller main','count':1,'halts_per_context':1,'why':'safety_charge direct scalar; synthetic Store mode never calls production halt catch'},
 {'role':'RANGE worker processes','count':len(workers),'halts_per_context':1,'why':'one process per frozen crash/concurrent job, no respawn; safety_charge direct scalar'},
 {'role':'C02/C03/C04 prepaid child claimers','count':3,'halts_per_context':1,'why':'claim.valid before try; production claim catch once; Credits.visit has no halt_budget caller'}]
H=sum(r['count']*r['halts_per_context'] for r in hrows)
assert H==52
assert '_HALTED.clear' not in sources['guard.py']
halts=[]
for filename,text in sources.items():
    for n in ast.walk(ast.parse(text)):
        if isinstance(n,ast.Call):
            name=n.func.id if isinstance(n.func,ast.Name) else n.func.attr if isinstance(n.func,ast.Attribute) else ''
            if name=='halt_budget':halts.append({'file':filename,'line':n.lineno,'call':ast.get_source_segment(text,n)})
assert len(halts)==4
save('H_FULL_SCOPE_PROOF.json',{
 'verdict':'PROVED_IN_FROZEN_SCOPE','scope':'fixed CALIBRATE_S1S9_THEN_F1_F4 source/job/once-role envelope; failed prefixes included',
 'H_definition':'budget-origin halt_budget invocations / at most one STOP publish attempt each; excludes M.abort STOP already in160',
 'H_max':H,'core_attempt_max':160+H,'stable_core_paths_unchanged':54,
 'roles':hrows,'eligible_contexts':sum(r['count'] for r in hrows),'worker_ids':workers,'halt_sites':halts,
 'proof_obligations':[
 'guard._reserve budget_health at630 precedes its try642',
 'Budget.visit execution_deadline at703 precedes try704; failure may halt inside688 and709 only',
 'Store.reserve.valid at116 and Store.claim.valid at168 precede their try blocks; further calls after HALTED stop before catch',
 'one synchronous in-flight operation per listed budget thread; controller monitor/watchdog never call halt_budget',
 'synthetic Store mode non-None at S1-S9, so production163/192 halt disabled there; global scalar charge still counted',
 'controller844 aliases sys.modules guard to current module; helper processes import one fresh guard; no flag reset/reload',
 'closed fixed role graph, Restart=no, three prepaid child spawns and14 frozen safety workers; no arbitrary API calls'],
 'failure_credit':'a failure before counter pwrite can addH with zero R increment; global visit cap alone does not proveH',
 'after_CLOSED':'already admitted calls may fail late; a direct scalar call with a fresh local flag can also enter its try and halt when _counter_lock.execution_deadline seesCLOSED. No grant is issued; subsequent calls in that guard instance stop before try.52 covers these late first failures.',
 'idle_prefix_H':0,'no_global_halt_claim':'process-local flag does not broadcast stop; actual cleanup obligations unchanged',
 'dynamic_tests':0,'source_edits':0})

# Bound production MR reasons from actual call-site provenance. Use inherited
# signed32 decimal width11 for code; no attempt to claim an exact tight maximum.
reason_rows=[]
def string_bound(node):
    if isinstance(node,ast.Constant) and isinstance(node.value,str):return len(node.value), 'ASCII_LITERAL'
    if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Add):
        left,_=string_bound(node.left)
        if isinstance(node.right,ast.Subscript):return left+4,'launch_one.status in PASS/FAIL, each<=4 ASCII'
        if isinstance(node.right,ast.Call) and isinstance(node.right.func,ast.Name) and node.right.func.id=='str':
            return left+11,'native wait exit code conservative signed32 decimal<=11'
    raise ValueError(ast.dump(node))
for file in ('guard.py','boot_continuity.py','startup_lifecycle.py','manager_recovery.py'):
    text=sources[file]
    for n in ast.walk(ast.parse(text)):
        if not isinstance(n,ast.Call):continue
        f=n.func
        external=isinstance(f,ast.Attribute) and isinstance(f.value,ast.Name) and f.value.id=='M' and f.attr in ('abort','fail')
        local=file=='manager_recovery.py' and isinstance(f,ast.Name) and f.id=='fail'
        if (external or local) and len(n.args)>=2:
            size,basis=string_bound(n.args[1]);reason_rows.append({'file':file,'line':n.lineno,'call':ast.get_source_segment(text,n),
                'reason_ASCII_upper':size,'basis':basis})
reason_max=max(r['reason_ASCII_upper'] for r in reason_rows)
assert reason_max==36
save('REASON_AND_VARIABLE_DECISION.json',{
 'R_MR':{'meaning':'encoded JSON token including quotes for M.abort first.reason / direct role reasons',
   'verdict':'PROVED_IN_FROZEN_SCOPE','ASCII_content_max':36,'token_max':38,'sites':reason_rows,
   'MR_prefix_content_max':48,'root_marker_token_max':50,'root_marker_bytes_max':194,
   'constant_quota43_marker_189_unchanged':True,
   'scope':'fixed callers plus inherited code integer ABI; union includes unreachable diagnostics conservatively; general external abort(reason=x_n) excluded'},
 'R_budget':{'meaning':'BUDGET_HALTED:+str(exception) after budget failure, same STOP pathname',
   'verdict':'CONDITIONAL_ON_EXISTING_TCB','numeric_max':None,
   'provenance':'local file/counter/JSON/clock/serialization error path; no systemctl stderr call inside reserve transaction',
   'exact_missing':'pinned Python/libc filesystem/JSON diagnostic wire catalogue; no source byte check or complete catalogue receipt',
   'family':'halt_budget(reason=x_n) yields >=n but direct arbitrary reason injection is OUTSIDE_FROZEN_SCOPE'},
 'T':{'meaning':'JSON-escaped type(exception).__name__ token, covers optional null with T>=4',
   'verdict':'CONDITIONAL_ON_EXISTING_TCB','numeric_max':None,'source_owned_class_max':18,
   'exact_missing':'complete reachable builtin/stdlib/loader/native-error class-name catalogue for pinned3.12.3/libc; source class list alone incomplete'},
 'B':{'meaning':'encoded3-file budget snapshot map of hash/size or UNKNOWN/error type; no ledger raw bytes nested',
   'verdict':'CONDITIONAL_ON_EXISTING_TCB','healthy_map_max':387,'general_formula':'69+3*max(106,29+T)',
   'assumptions':'64-hex hashes and size decimal<=20; file-scan volume is a separate work obligation'},
 'E':{'meaning':'encoded closure_persistence_error=repr(exception) from H.lifecycle_lock/RootIPC marker publication only',
   'verdict':'CONDITIONAL_ON_EXISTING_TCB','numeric_max':None,
   'scope_correction':'stop_tree systemctl call is after this try; arbitrary manager stderr is not a proven path intoE',
   'exact_missing':'finite pinned file/ACL/clock/JSON error representation profile and bounded generated filenames; raw exception text has no source wire cap'},
 'sumV':{'meaning':'JSON tokens for12 raw cgroup files read by cg_snapshot; token/null, UTF8 pretty serialization',
   'verdict':'CONDITIONAL_ON_EXISTING_TCB','numeric_max':None,
   'files':['pids.current','pids.max','pids.events','memory.current','memory.peak','memory.max','memory.swap.max','memory.events','memory.oom.group','cgroup.events','cgroup.procs','cgroup.threads'],
   'enforced_parts':'12 selected filenames; TasksMax4 and MemoryMax4294967296 configured; stat metadata widths inherited',
   'exact_missing':'pinned kernel exported-key/cardinality/decimal-width profile including process/thread listing semantics during churn; raw read_text has no limit',
   'caution':'TasksMax4 bounds simultaneous tasks, not by itself all seq-file rows during concurrent change; parent slice input does not set MemorySwapMax'},
 'no_new_default_lengths':True,'normalization_required':'compact ensure_ascii=True vs RootIPC UTF8 ensure_ascii=False tokens kept separate; a common bound must cover both',
 'encoding_facts':{'source_ASCII':'one byte per char; quotes/escapes counted','compact_general_codepoint_growth_max':12,
  'UTF8_JSON_general_codepoint_growth_max':6,'bytes_vs_codepoints':True},
 'new_partial_formulas':{'Root_MR_first':'<=25092+T+B','cleanup_line':'<=998+11T+B','stop_result':'<=1151+E+sumV'},
 'whole_close_numeric':None})
classes=[]
for f,t in sources.items():
    for n in ast.walk(ast.parse(t)):
        if isinstance(n,ast.ClassDef) and any(isinstance(b,ast.Name) and (b.id.endswith('Error')or b.id.endswith('Exception')) for b in n.bases):
            classes.append({'file':f,'line':n.lineno,'name':n.name,'JSON_ASCII_token_bytes':len(n.name)+2})
assert max(x['JSON_ASCII_token_bytes'] for x in classes)==18
save('SOURCE_EXCEPTION_CLASS_CENSUS.json',{'classes':classes,'complete_TCB_class_bound':False,
  'note':'source-owned class tokens<=18; this does not bound imported/pinned runtime classes'})
childids=list(read(RUNTIME/'inputs/child_contracts.json')['tasks'])
syntheticids=[j['task_id']+suffix for j in cfg['jobs'] for suffix in (('.L','.R') if j['kind']=='concurrent' else ('',))]
save('FIXED_INPUT_WIDTHS.json',{'production_task_ids':childids,'production_task_id_ASCII_max':max(map(len,childids)),
 'synthetic_task_id_ASCII_max_with_LR':max(map(len,syntheticids)),
 'native_C09_has_task_id':False,'batch_id_ASCII':7,'hash_hex':64,'boot_UUID':36,
 'source_numeric_profile':'pid10/start_ticks20/clock_ns20/binary64_JSON25/stat_ctime_ns29 are inherited explicit ABI/codec conditions',
 'not_generic_new_API_limits':True})

# A concrete minimal cardinality witness uses mandatory distinct paths, not an
# upper bound like4450. No model or calibration job is executed.
c09=read(RUNTIME/'inputs/c09_contract.json');ipc=read(RUNTIME/'inputs/root_ipc_contract.json')
hpaths=[]
for job in c09['jobs']:
    hpaths.extend(f"out/c09_tests/{job['case_id']}/{i:03d}.json" for i in range(len(job['events'])))
    hpaths.append(f"out/c09_tests/{job['case_id']}/oracle.json")
assert len(hpaths)==len(set(hpaths))==238 and len(ipc['jobs'])==56
native_raw=hpaths+[f'inputs/root_private/ipc_case_{i:03d}.json' for i in range(19)]
admin_raw=hpaths+[f'inputs/root_private/ipc_case_{i:03d}.json' for i in range(17)]
assert len(set(native_raw))==257 and len(set(admin_raw))==255
save('CURRENT_CAPACITY_UNSAT_WITNESSES.json',{
 'verdict':'CURRENT_CONTRACT_UNSAT','formal_status':'FULLCHAIN_UNSAT_UNDER_CURRENT_CAPACITY_CONTRACT',
 'target':'complete requested full-chain success INCLUDING all mandatory raw evidence/native seal/admin export, not mere business process start',
 'C09H_source':'c09_regression.py:59-72; c09_contract jobs34:204 events+34 oracle',
 'IPC_source':'root_ipc_regression.py:222-244; frozen56 jobs; full chain requires both suites',
 'native':{'raw_witness_paths':native_raw,'raw_distinct':257,'manifest_members':1,'minimum_members':258,'cap':257,
  'MUS':['fullchain success requires these257 distinct raw paths','native archive contains all required raw plus one manifest','accepted native member count<=257'],
  'delete_any_clause_count_satisfiable_examples':{'without_required_paths':{'raw':0,'members':1},'without_completeness':{'raw':257,'members':257},'without_cap':{'raw':257,'members':258}}},
 'admin':{'raw_witness_paths':admin_raw,'raw_distinct':255,'native_manifest_and_ZIP':2,'minimum_export_files':257,'cap':256,
  'MUS':['fullchain success requires these255 distinct raw paths','postexit export includes raw plus native manifest and nativeZIP','export file count<=256'],
  'delete_any_clause_count_satisfiable_examples':{'without_required_paths':{'raw':0,'export':2},'without_completeness':{'raw':255,'export':256},'without_cap':{'raw':255,'export':257}}},
 'minimality_scope':'inclusion-minimal three-clause arithmetic cores and cardinality-minimal witness subsets for each reader; not a minimal program/configuration theorem',
 'larger_old_lower_bounds':'887 calibration raw;1082 full raw retained as prior evidence, not needed for contradiction',
 'upper4450_used_to_prove_UNSAT':False,'coarse_byte_upper_exceedances_used_as_counterexample':False,
 'no_mutation_or_runtime':True})

save('AMBIENT_PROCESS_COUNTEREXAMPLE.json',{
 'gap_id':'G12','verdict':'COUNTEREXAMPLE_IN_FROZEN_SCOPE',
 'target_claim':'current slice TasksMax4 would bound admin discovered role metadata to<=4',
 'source':'startup_lifecycle.py:386-410,441-491',
 'initial':'all actual batch roles exited; current ROOT writers frozen; current payload slice empty; trusted kernel/Root and same source files',
 'input_family':'P_n: n live ordinary different-UID processes outside the slice with cmdline containing exact current source/guard.py, --batch-root and current ROOT; actual executable is another benign interpreter/program',
 'concrete_n':5,'concrete_environment_example':{'uid':1000,'cgroup':'outside dclr6batch14.slice',
    'executable':'/bin/sh (ordinary unrelated process, not executed in this review)',
    'argv':['/var/lib/dcl-r6/ra01/src/guard.py','-c','sleep 60; :','--batch-root','/var/lib/dcl-r6/batch14']},
 'reachability':'spawn after valid native preflight/batch exit and before admin scan; no DCL function call, ROOT file write or privileged TCB update required',
 'result':'scanner uses argv membership without UID/InvocationID check in role branch; roles length>=5 while slice current tasks=0<=4',
 'byte_growth':'each role retains args array; role metadata has a positive per-row contribution and any allowed extra argv; L>=c*n for c>0',
 'scope_assumption':'old fixed-writer/once activation contract does not freeze all unrelated global /proc metadata; if a new whole-host quiescence/no-lookalike premise is adopted, classify that stronger domain separately',
 'not_claimed':['actual32MiB overrun','unlimited physical process space','a completed native fault test','a forged raw PASS'],
 'minimum_contract':'bound global scan/process and cmdline/error bytes, OR approve known-identity/current-cgroup discovery with equivalent escaped-role detection; limits remain null',
 'dynamic_execution':0})

# Preserve exactly the fifteen existing responsibilities, with a single terminal
# verdict per row. Numerical upper products never become attainability proofs.
gap_specs=[
 ('G01','COUNTEREXAMPLE_IN_FROZEN_SCOPE','O_native_pending','native single handoff/delayed parent witness','current no record quota; draft256/263 only',None,
  'existing stutter257 under same finite-prefix timing/storage premises; no new replay','approve native observation quota and encoded schema; stop after full256th PENDING'),
 ('G02','REQUIRES_NEW_CONTRACT','H;R_budget','fixed budget threads and filesystem/JSON failures','H<=52, core<=212; STOP one path',None,
  'arbitrary reason=x_n direct API is outside frozen callers; no native large-text witness','TCB diagnostic wire profile or separately approved bounded control/raw-acquisition policy'),
 ('G03','REQUIRES_NEW_CONTRACT','E;sumV','H lock/RootIPC errors and12kernel file exports','stop_tree<=23; stop_result path<=23',None,
  'TasksMax alone does not establish kernel-export byte bound; no frozen arbitraryV_n witness','pinned kernel/file-error wire profiles; producer size/read limits and exact failure/UNKNOWN semantics'),
 ('G04','CONDITIONAL_ON_EXISTING_TCB','R_MR;T;B','closed MR callers and pinned runtime exception catalogue','abort<=16; first path1; cleanup rows<=16','25092+T+B; B<=69+3max(106,29+T)',
  'R_MR token<=38 newly closed; source exception token<=18 only; imported classes unresolved','bind complete reachable exception catalogue/T_max or approve typed finite error profile'),
 ('G05','REQUIRES_NEW_CONTRACT','SEAL_ERROR_repr;helper_output','actual fixed helper executions and TCB errors','<=4 SEAL_ERROR writes; one path',None,
  'stderr_m is an interface-domain family; pinned native attainability unverified and kept outside','bound helper response acquisition and persisted diagnostic bytes; overflow cannot claim complete evidence'),
 ('G06','REQUIRES_NEW_CONTRACT','terminal_report','fixed reader plus four possible embedded bounded JSON roots','exclusive saved review<=1; reader capped roots4MiB',None,
  'acceptance caps yield conditional finite serialization input, not matching full saved-output cap','typed terminal output composition/byte envelope preserving required raw provenance'),
 ('G07','REQUIRES_NEW_CONTRACT','timing_error;stdout/stderr;traceback','locked roles/helpers and allowed faults','finite file slots;timing first_samples<=8 per key',None,
  'arbitrary external stderr_m not promoted to native growth counterexample','raw stream/acquisition/per-error/aggregate bounds plus explicit incomplete/UNKNOWN policy'),
 ('G08','REQUIRES_NEW_CONTRACT','per-record-to-total aggregation','existing readiness/S34/IPC/MR producers','fixed jobs and source caps; old4450 envelope','local cap products only',
  '78905344/50331648 are upper products, not attained raw-set witnesses','versioned aggregate reservation/acceptance contract and producer/exception-staging union'),
 ('G09','REQUIRES_NEW_CONTRACT','journal_total_bytes','frozen budget schemas and accepted healthy ledger','global visits<=1m; candidate conditional471876988','old conditional journal formula',
  'upper>32MiB alone is not a frozen actual violating instance','align generated journal byte/row limits with mandatory validators and preserve unspent/ambiguous semantics'),
 ('G10','UNRESOLVED_WITH_EXACT_REASON','model_state/trace/strategy_wire','fixed model inputs and visit slices, no business execution authorized','fixed jobs and budget; neighbour generation/serialization constants not certified',None,
  'no model run performed; no physical-memory-based application bound used','frozen model wire profile with per-output/trace/serialization limits and incomplete-on-limit semantics; keep numeric fields null'),
 ('G11','REQUIRES_NEW_CONTRACT','raw/native/admin bytes;memory;FD','old fixed paths and archives','old4450/4451/4452 conditional; current257/256 unsatisfiable for full target','native manifest coarse7436121',
  'concrete minimal count UNSAT witnesses; byte/ZIP coarse products not actual-overrun proof','versioned counts only after delta; derived raw/manifest/ZIP/working-set/FD limits before effective capacity'),
 ('G12','COUNTEREXAMPLE_IN_FROZEN_SCOPE','ambient_roles/args;admin views','global /proc inputs outside current slice, no extra ROOT writers','samples<=128; P5 gives roles>=5 despite slice<=4',None,
  'P5 refutes slice-task bound on admin discovery; no observed byte overrun claimed','choose global environment/input envelope or equivalent scoped discovery, preserving all genuine exit checks'),
 ('G13','OUTSIDE_FROZEN_SCOPE','new implementation/test/oracle deltas','future artifacts not currently created','current新增运行producer0; future delta unknown',None,
  'cannot prove a future unimplemented diff delta by re-reading old source','explicit maintenance scope + concrete diff/set/byte/visit delta review; no same-scope repeat audit'),
 ('G14','UNRESOLVED_WITH_EXACT_REASON','syscall/scheduler/IO_latency','trusted OS with no quantitative response-time guarantee','existing deadlines are attempts/refusal guards, not success WCET',None,
  'finite work + arbitrarily delayed allowed scheduling/IO does not prove completion by5/30/300/1800','approve environment latency envelope/measurement objective or preserve timeout/UNKNOWN; strict guarantee remains unproved'),
 ('G15','REQUIRES_NEW_CONTRACT','host finalization error/embedded audit','fixed Windows parent and post-exit error path','one extra error path, outside admin ZIP preimage',None,
  'finite output count does not bound repr or embedded audit bytes','post-seal control/raw/error envelope, explicit preimage scope and aggregate limit')]
oldgap=read(PREV/'evidence/FULL_CAPACITY_GAP_TABLE.json')['gaps'];mapping={g['id']:g for g in oldgap}
matrix=[]
for gid,ver,var,domain,occur,byte,ce,minimum in gap_specs:
    g=mapping[gid]
    matrix.append({'gap_id':gid,'producer':g['producer'],'source':g['site'],'unresolved_variable':var,
      'input_domain':domain,'occurrence_bound':occur,'byte_bound':byte,'trusted_assumption':'inherited closed writers/once roles/Root/kernel/storage/runtime profile; additional quantitative assumptions explicitly absent',
      'existing_evidence':str(PREV/'evidence/FULL_CAPACITY_GAP_TABLE.json'),'counterexample':ce,'minimum_constraint':minimum,'verdict':ver})
assert len(matrix)==15
save('RESIDUAL_15_GAP_MATRIX.json',{'rows':matrix,'same_scope_static_audit_closed':True,
 'reopen_only_for':'new user decision, approved quantitative contract, exact diff or new TCB/evidence input; never automatic repetition'})

save('FINAL_BOUND_STATUS.json',{
 'H_max':52,'core_attempt_upper':212,'stable_core_path_upper':54,
 'R_MR_token_max':38,'Root_MR_marker_max':194,'quota_marker_fixed43':189,
 'B_healthy':387,'B_general':'69+3*max(106,29+T)',
 'close_core_formula':'A<=16,S<=23,W<=2,H<=52; use old nonoverlapping record formula with Root marker<=194, first<=25092+T+B, cleanup<=997+11T+B, result<=1151+E+sumV, and H budget STOP records with R_budget',
 'B_close':None,'B_C09_total':None,'B_full_raw':None,'native_ZIP':None,'admin_ZIP':None,
 'C09_total_formula':'345148+B_close+B_other_disjoint; main345148 remains prior proposed quota condition',
 'FULL_BYTE_BOUND':'FULL_BYTE_BOUND_UNRESOLVED','capacity':'CAPACITY_CONTRACT_NOT_READY',
 'work':'conditional accepted-oracle O(N+B); full producer/archive/hash/memory/FD/syscalls unclosed',
 'WALL_TIME_BOUND':'WALL_TIME_BOUND_UNRESOLVED','decision':'CONTRACT_REVISION_REQUIRED',
 'current_contract':'CURRENT_CONTRACT_UNSAT','strict_separation':0,'dynamic_runs':0})
assert 16*(194+25092+260+237+194+998+997)+23*(194+1151)+2*1223+52*144==488421
save('CLOSE_CORE_REDUCED_FORMULA.json',{
 'status':'CONDITIONAL_BOUND','scope':'core production-byte sum upper-bounds retained core data and failed staging; not full close/system bytes',
 'substitutions':{'A':16,'S':23,'W':2,'H':52,'root_marker':194,'first_constant_after_R_MR':25092,
    'external':260,'ABORTING':237,'cleanup_line_constant':998,'cleanup_state_constant':997,'stop_result_constant':1151,'waitpid_max':1223},
 'generated_core_bytes_formula':'488421 + 368*T + 48*B + 23*E + 23*sumV + 52*R_budget',
 'constant_bytes':488421,'coefficients':{'T':368,'B':48,'E':23,'sumV':23,'R_budget':52},
 'B_formula':'69+3*max(106,29+T)','full_close_bytes':None,
 'exclusions':['main/quota metadata already in prior350166 subset','normal MR review/raw ledger originals','extra exit/terminal/stdio/native/admin evidence'],
 'not_selected_as_new_cap':True})

save('TERMINAL_REENCODING_LEMMA.json',{
 'scope':'each successfully parsed plain JSON input tree, no custom object hook/cycle; compact ensure_ascii=True reserialization',
 'bound':'encoded(tree)<=25*raw_input_bytes',
 'proof':['container punctuation/keys consume raw bytes; duplicate keys only discard earlier members',
  'one Unicode codepoint needs>=1 source byte and<=12 escaped output bytes',
  'integer lexeme reserialization does not expand its decimal width; accepted float lexeme emits<=25 bytes, and source token has>=1 byte',
  'sum leaf/key/container costs and preserve their disjoint source-token spans'],
 'terminal_embedded_raw_roots':['closed','stop_request','waitpid witness','SEAL_ERROR error_record when present'],
 'source_each_root_accept_cap':4194304,'maximum_embedded_root_contribution':4*25*4194304,
 'control_metadata':'K(namespace, validated numeric widths, fixed hash slots, exception-name profile); full output total not selected',
 'not_proved':['heap allocation bound','matching producer output cap','all root contents attainable simultaneously','full report fits32MiB'],
 'result':'CONDITIONAL_BOUND; resource acceptance still requires exact output/profile contract'})

boundparts=read(PREV/'evidence/MANIFEST_ZIP_BOUND_ARITHMETIC.json')
save('RESOURCE_TERMINATION_DECISION.json',{
 'raw_objects':{'old_upper':4450,'condition':'unchanged frozen writer set; new diff deltas unresolved'},
 'native_manifest':{'coarse_conditional_upper':boundparts['conditional_native_manifest_upper'],'accept_cap':4194304},
 'native_zip':{'output_upper':None,'formula':'ZIP(R_raw+M_native,N,F,pinned_codec)',
   'accepted_U32MiB_stored_conditional':47628516,'accepted_U32MiB_deflate_conditional':47696620},
 'admin_zip':{'output_upper':None,'formula':'ZIP(R_raw+M_native+Z_native+host_raw+source_locks+M_admin)'},
 'reading':{'accepted_oracle':'O(N+B) with named path/metadata dimensions','full_pipeline_max':None,
   'budget_snapshot_scans':32,'terminal_incremental_listed_FD':13},
 'working_memory':None,'full_FD_max':None,'all_syscalls_max':None,'storage_IO_max':None,
 'wall_time':{'terminal_reader_seconds':5,'admin_child_seconds':30,'calibration_seconds':300,'batch_seconds':1800,
  'stop_policy_seconds':1740,'meaning':'deadline/refusal/attempt parameters; not unconditional success or physical-exit WCET'},
 'time_scope_corrections':{'five_seconds':'terminal_evidence.read_terminal_evidence only; guard.seal includes separate runtime verification,stop wait up to20,and archive build without a5s whole-seal envelope',
   'thirty_seconds':'Linux admin child alarm; host parent waits32/35 for this child, then host ZIP/hash work has no single30s total envelope',
   'host_active_wait':'windows_entry.process.wait has no timeout in that function'},
 'exact_time_missing':['bounded kernel scheduling delay','maximum filesystem/read/write/fsync latency','manager/subprocess response/termination latency','host active WSL wait completion'],
 'strict_time_status':'WALL_TIME_BOUND_UNRESOLVED','full_byte_status':'FULL_BYTE_BOUND_UNRESOLVED',
 'stop_repeating_same_scope_audit':True})

(OUT/'proposals').mkdir(exist_ok=True)
params=[]
def param(id,value,source,family,derivation,overflow,safety,files,negative,effective):
    params.append(dict(zip(['parameter_id','value','producer_source','input_family','derivation','overflow','safety_effect','candidate_files','negative_tests','effective_prerequisites'],
        [id,value,source,family,derivation,overflow,safety,files,negative,effective])))
param('MAIN_OBSERVATIONS',256,'c09_handoff.observe_exit','one valid handoff, delayed parent witness',
 'explicit engineering policy inherited from prior v2, not a source implicit or liveness-derived maximum',
 'retain complete256th PENDING, deny257 without per-rejection main log, then existing abort path',
 'may close legitimate delayed witness early; never upgrades handoff PASS',['src/c09_handoff.py','src/guard.py','inputs/c09_quota_contract.json'],
 ['last credit competition','256th raw retained','257 no append','crash/short write burns credit'],
 ['explicit policy approval','separate source-change authorization','new static lock and delta review; no dynamic authority'])
param('MAIN_ROWS',263,'six actual publish calls +oneACK +classification slots','same native handoff',
 '256+6+1=263; stage/ACK one-use bits and terminal latch required',
 'same token refused, partial raw kept, no refund/reinitialize','existing identities/ACK/witness/once-resume guards retained',
 ['src/c09_handoff.py','inputs/c09_contract.json'],['duplicate stage','duplicate ACK','terminal cleanup gap','process restart'],['approved v2 logic and reviewed slot persistence'])
param('MAIN_BYTES',345148,'native compact JSON codec','fixed source ASCII/scalar profile',
 '256*1322+6*948+1028; encoded LF included',
 'burn reserved slot on failed append; out-of-profile input stops/UNKNOWN',
 'all computed accepted observations preserve raw facts; no summary substitution',['src/c09_handoff.py','inputs/c09_quota_contract.json'],
 ['field width','Unicode/out-of-profile keys','LF and partial writes','total-byte exhaustion'],['validated schema and binding; no activation in this review'])
param('CLOSE_BYTES',None,'M.abort/G.stop_tree/waitpid/terminal/host','all required closure paths',
 'H52/core212 now finite; old close byte formula still depends on quantitative TCB/kernel/stream/model/admin profiles',
 'deny more work; preserve emitted data; missing proof stays UNKNOWN; no claim full native seal',
 'process cleanup and complete evidence remain separate axes',['src/guard.py','src/manager_recovery.py','affected terminal/admin readers'],
 ['simultaneous close','missing shared marker','EIO','parent witness loss','failed seal receipt'],['all required numeric profiles instantiated and admitted before effective capacity'])
param('TCB_DIAGNOSTIC_PROFILE',None,'R_budget/T/E and SEAL_ERROR','actual reachable pinned runtime errors; arbitrary API x_n outside frozen callers',
 'source-owned name token18; MRreason38; imported/full message catalog and repr widths uninstantiated',
 'bounded control code plus full raw under approved acquisition envelope; overflow marks incomplete/UNKNOWN',
 'no silent loss of already captured raw; no incomplete-to-PASS conversion',
 ['src/guard.py','src/manager_recovery.py','inputs/close_reserve_contract.json'],
 ['all enumerated error types','localized/Unicode text','max+1 bytes','nested failure of diagnostic sink'],['pinned catalogue or explicit approved typed error/acquisition contract'])
param('CGROUP_WIRE_PROFILE',None,'cg_snapshot12 raw files','pinned kernel exports including churn/listing semantics',
 '12 selected files and existing TasksMax/MemoryMax do not instantiate all encoded file maxima',
 'stop and retain captured original/UNKNOWN when source exceeds declared profile',
 'do not equate cap with group-empty/exit proof',['src/guard.py','inputs/close_reserve_contract.json'],
 ['all12wireformats','transient PID/thread changes','missing/malformed files','profile mismatch'],['kernel ABI binding and exact byte profiles'])
param('MANDATORY_WIRE_AND_RAW_STREAMS',None,'timing,TR,model outputs,Root/host pipes and post-seal receipts','G05-G07/G10/G15 producers',
 'source file counts/reader caps/finite samples alone do not yield selected complete output totals',
 'new policy must explicitly choose bounded acquisition with incomplete/UNKNOWN OR guaranteed input-profile bounds; keep all already acquired original bytes',
 'full success possible only inside approved lossless input envelope; over-limit cannot claim original-complete seal',
 ['src/guard.py','src/terminal_evidence.py','src/startup_lifecycle.py','host/startup_finalize.py','host/windows_entry.py','relevant model output writers'],
 ['stream max+1','incompressible data','trace growth','error on overflow recording','no recursive archive'],['numeric per-source/aggregate limits and explicit evidence-completeness policy approval'])
param('ADMIN_SCOPE',None,'startup_lifecycle._postexit_roles','P5 unrelated-process metadata, or declared global scan domain',
 'slice TasksMax4 does not bound global/proc role candidates; samples<=128 only',
 'unknown/defer rather than a false exit result',
 'if changing to known-identity/cgroup discovery, preserve equivalent genuine escaped-role detection',
 ['src/startup_lifecycle.py','inputs/startup_contract.json'],['P5 lookalikes','genuine escaped roles','PID reuse','cmdline length/error rows'],
 ['approve explicit global process/argv bounds OR precise equivalent scoped-discovery contract'])
for id,source,expr,files in [
 ('RAW_FILES','all unique runtime paths','4450+Delta_raw',['inputs/startup_contract.json','inputs/terminal_contract.json']),
 ('NATIVE_MEMBERS','raw+native manifest','4451+Delta_raw',['inputs/terminal_contract.json']),
 ('ADMIN_EXPORT_FILES','raw+native manifest+nativeZIP','4452+Delta_raw+Delta_export',['inputs/startup_contract.json'])]:
    param(id,None,source,'complete fixed workflow plus future exact diff',expr+'; selected numeric guard remains null',
      'refuse overflow, preserve actual originals and UNKNOWN; no path coalescing/deletion to pass',
      'old256/257 unchanged until separate approved version',files,['missing/extra/duplicate members','namespace drift','full mandatory file set'],['exact diff/set delta and complete byte/work proof'])
param('TOTAL_BYTES_AND_WORK',None,'full raw/native/admin pipeline','all fifteen existing gap families',
 'R_raw/M_native/Z_native/host/nesting plus heap/FD/IO/syscalls; conditional accepted-oracle O(N+B) retained',
 'safe refusal/UNKNOWN under declared limits; no fullchain admission from an archive subset',
 'all raw/source/identity/budget completeness checks preserved',['versioned capacity inputs','affected builders/readers only after separate authority'],
 ['full worst-case producer union','compressed expansion','central-directory/JSON allocation','FD/IO overflow'],['all component numeric profiles, delta, physical-storage and system envelope reviewed'])
param('WALL_TIME_OBJECTIVE',None,'5/30/300/1800 deadline and scheduler/storage/manager environment','allowed delayed scheduling or blocking IO',
 'finite operations cannot instantiate a worst response-time constant',
 'existing deadline/timeout and UNKNOWN retained; successful WCET remains unclaimed',
 'approve environment assumptions or measurement/timeout objective separately',['execution/terminal/startup contracts; no deadline relaxation now'],
 ['latency budget breach','slow fsync/manager','unreaped child','host wait nonreturn'],['explicit environment envelope or scope-limited empirical validation plan; new dynamic authority required'])

optionA={'schema':'DCL-RBD-OPTION-A/1','status':'CURRENT_CONTRACT_UNSAT','user_approved':False,'approved':False,'effective':False,'runtime_enabled':False,
 'keep':['old256 admin','old257native','old C09 source','old execution locks','MR proposed only'],
 'permitted_decision':'retain frozen contract and accept that complete requested fullchain success is unsatisfiable; no further same-scope static audit or dynamic fullchain attempt',
 'UNSAT_witness':str(E/'CURRENT_CAPACITY_UNSAT_WITNESSES.json'),'business_start_vs_success':'no claim arbitrary business process cannot start; complete success/evidence objective is UNSAT',
 'source_changes':False,'dynamic_authority':False}
optionB={'schema':'DCL-RBD-OPTION-B/1','status':'CONTRACT_REVISION_REQUIRED','version':'ResidualBounds-Decision/review-1',
 'approved':False,'user_approved':False,'effective':False,'runtime_enabled':False,'parameters':params,
 'ready_for_principle_review':['MAIN_OBSERVATIONS','MAIN_ROWS','MAIN_BYTES','versioned isolated counts','lossless-within-approved-envelope and incomplete-on-overflow policy','independent full raw oracle'],
 'effective_capacity_approval':'BLOCKED_NULL_PARAMETERS','source_mutation_permission':'SEPARATE_EXPLICIT_AUTHORIZATION_REQUIRED',
 'dynamic_permission':'NOT_GRANTED','MR_cross_instance':'PROPOSED_NOT_EFFECTIVE',
 'minimum_main_quota_diff_request':{'behavior_files':['src/c09_handoff.py','src/guard.py'],
  'prepay':'existing scalar reserve before C09 controller/ready/counter fixation; no budget-core edits',
  'existing_abort':'reuse current exception-to-M.abort wrappers; no new cross-instance gate',
  'inputs':['inputs/c09_contract.json','proposed inputs/c09_quota_contract.json','new static manifest/execution review lock'],
  'boundary':'isolated static maintenance diff only if explicitly approved; old namespace/locks/windows not executable/reopened'},
 'no_arbitrary_default_limits':True,'same_scope_audit_closed':True}
for name,obj in [('OPTION_A_KEEP_CURRENT.json',optionA),('OPTION_B_MINIMAL_REVISION.json',optionB)]:
    (OUT/'proposals'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save('FOUR_AUTHORIZATION_DECISIONS.json',{'CAPACITY_CONTRACT_APPROVAL':{'current':'NOT_APPROVED','logical_subclauses':'REVIEW_READY','effective_total_capacity':'BLOCKED_NULL_PARAMETERS'},
 'MR_CROSS_INSTANCE_APPROVAL':{'current':'PROPOSED_NOT_EFFECTIVE','original_rule_sha256':'9c7524d7af3530b27f4c35d4fef92d9f2f3e431633967b555483b0b58085d069','decision':'SEPARATE_PRINCIPLE_REVIEW_ONLY'},
 'NATIVE_IMPLEMENTATION_AUTHORIZATION':{'current':'NOT_GRANTED','limited_main_quota_maintenance_request':'PREPARED_FOR_EXPLICIT_APPROVAL','full_capacity_implementation':'NOT_READY'},
 'FULLCHAIN_DYNAMIC_AUTHORIZATION':{'current':'NOT_GRANTED','A':'REFUSE_COMPLETE_SUCCESS_ATTEMPT_UNSAT','B':'BLOCKED_UNTIL_ALL_REQUIRED_APPROVALS_LOCKS_AND_CURRENT_GATES'},
 'auto_resume_or_approval':False})
save('DECISION_BINDINGS.json',{'A':row(OUT/'proposals/OPTION_A_KEEP_CURRENT.json'),'B':row(OUT/'proposals/OPTION_B_MINIMAL_REVISION.json'),
 'prior_close_draft':row(PREV/'proposals/CLOSE_RESERVE_REVIEW_DRAFT.json'),
 'prior_capacity_draft':row(PREV/'proposals/CAPACITY_REVIEW_DRAFT.json'),
 'MR_rule':row(ROOT/'DCL-R6-C09-BoundClosure/proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json')})
mrpath=ROOT/'DCL-R6-C09-BoundClosure/proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json'
mrtext=ROOT/'DCL-R6-C09-BoundClosure/MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md'
mr=read(mrpath);assert sha(mrpath)=='9c7524d7af3530b27f4c35d4fef92d9f2f3e431633967b555483b0b58085d069'
items=re.findall(r'^(\d+)\. ',mrtext.read_text(encoding='utf-8'),re.M);assert items==[str(i) for i in range(1,15)]
assert mr['user_approved']is False and mr['runtime_enabled']is False and mr['evidence_usable_now']is False
save('MR_RULE_RECHECK.json',{'rule':row(mrpath),'text':row(mrtext),'numbered_rules':14,
 'user_approved':False,'runtime_enabled':False,'evidence_usable_now':False,'status':'PROPOSED_NOT_EFFECTIVE',
 'categories':['one observed native failure capability only','B current qualification independent','exact source/runtime pair',
  'real native failure','primary automatic close and role/group exit','budget andnative/admin/raw oracle',
  'scope/version/boot/revocation/use freshness','mandatory rejection of missing/fallback-only/UNKNOWN'],
 'capacity_approval_transferred':False})
ex={}
for f,ranges in {'src/guard.py':[(52,91),(334,349),(629,716),(842,904),(1084,1097),(1130,1281)],
  'src/range_core.py':[(112,193)],'src/range_fixtures.py':[(39,69),(234,307)],'src/guard_probe.py':[(24,56),(123,139)],
  'src/c09_regression.py':[(52,74)],'src/root_ipc_regression.py':[(212,246)],
  'src/startup_lifecycle.py':[(386,410),(441,519)],'src/terminal_evidence.py':[(143,186),(193,266)],
  'host/windows_entry.py':[(35,60)],'host/startup_finalize.py':[(52,121)]}.items():
    lines=(RUNTIME/f).read_text(encoding='utf-8-sig').splitlines()
    ex[f]=[{'start':a,'end':min(b,len(lines)),'lines':[{'line':i,'text':lines[i-1]} for i in range(a,min(b,len(lines))+1)]} for a,b in ranges]
save('TARGETED_SOURCE_EXCERPTS.json',ex)
print({'H_max':H,'core_attempts':160+H,'MR_reason_token':38,'MR_marker':194,
 'native_minimal_witness':258,'admin_minimal_witness':257,'gaps':15,'decision':'CURRENT_CONTRACT_UNSAT / CONTRACT_REVISION_REQUIRED'})
