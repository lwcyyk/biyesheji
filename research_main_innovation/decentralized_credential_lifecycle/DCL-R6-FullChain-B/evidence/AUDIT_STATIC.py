"""Administrative static audit only. Never import or execute frozen programs."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone

PROJECT = Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
ISOLATED = Path(r'D:\毕业设计\DCL-R6-isolated-verification')
SOURCE = ISOLATED / 'ra01'
OUT = PROJECT / 'DCL-R6-FullChain-B'
E = OUT / 'evidence'
REQUEST = Path(r'C:\Users\a1887\.codex\attachments\bdce24e8-b94b-4feb-b328-6ee3496500ec\已粘贴的文本.txt')
NAV = ['CURRENT_VERDICT.md', 'NEXT_ACTION.md', 'README.md', 'DECISION_HISTORY.md']

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def save(name, data):
    p = E / name
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def copy(p, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('xb') as w, p.open('rb') as r:
        shutil.copyfileobj(r, w)

E.mkdir(parents=True, exist_ok=True)
copy(REQUEST, E / 'TASK_REQUEST.txt')
for n in NAV:
    copy(PROJECT / n, E / 'NAV_ORIGINALS' / n)

# Freeze historical byte identities before any permitted navigation prefix update.
history = []
for root in [PROJECT, ISOLATED]:
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.is_relative_to(OUT) or (root == PROJECT and p.parent == PROJECT and p.name in NAV):
            continue
        history.append({'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)})
save('HISTORY_BASELINE.json', {'scope': 'All pre-existing project and isolated files, except four navigation files saved separately', 'files': history})

lock = read(PROJECT / 'DCL-R6-RuntimeAdapt-Fix/evidence/STATIC_WORKSPACE_LOCK.json')
checks = []
for row in lock['files']:
    p = SOURCE / row['relative']
    current = {'relative': row['relative'], 'bytes': p.stat().st_size, 'sha256': sha(p)}
    current['matches_static_lock'] = current['bytes'] == row['bytes'] and current['sha256'] == row['sha256']
    ref = PROJECT / 'DCL-R6-RuntimeAdapt-Fix/evidence/SOURCE_FINAL_R1' / row['relative']
    current['matches_final_snapshot'] = ref.is_file() and sha(ref) == current['sha256']
    copy(p, E / 'FROZEN_RA_ORIGINALS' / row['relative'])
    checks.append(current)
assert len(checks) == 64 and all(r['matches_static_lock'] and r['matches_final_snapshot'] for r in checks)
manifest = read(SOURCE / 'inputs/static_manifest.json')
execution = read(SOURCE / 'inputs/execution_lock.json')
assert execution['static_manifest_sha256'] == sha(SOURCE / 'inputs/static_manifest.json')
assert all(sha(SOURCE / 'src' / n) == h for n, h in manifest['source_hashes'].items())
assert all(sha(SOURCE / n) == h for n, h in manifest['bound_inputs'].items())
syntax = []
trees = {}
for p in sorted(SOURCE.rglob('*.py')):
    raw = p.read_text(encoding='utf-8-sig')
    t = ast.parse(raw, filename=str(p), feature_version=(3, 12))
    compile(t, str(p), 'exec')  # code object only; no execution and no pyc
    trees[p.name] = t
    syntax.append({'relative': str(p.relative_to(SOURCE)), 'python312_grammar': 'PASS', 'host_in_memory_compile': 'PASS'})
save('SOURCE_LOCK_VERIFICATION.json', {'status': 'PASS_STATIC_BYTES_ONLY', 'version': lock['version'], 'files': checks,
     'manifest_sha256': sha(SOURCE/'inputs/static_manifest.json'), 'execution_lock_sha256': sha(SOURCE/'inputs/execution_lock.json'),
     'programs': syntax, 'target_imports': 0, 'new_execution_lock': 'NOT_ISSUED_STATIC_BLOCKER'})

preferred = [
 'DCL-R6-TR-A2/TRA2_FINAL_DECISION.md', 'DCL-R6-RuntimeAdapt-Fix/FINAL_DECISION.md',
 'DCL-R6-RuntimeAdapt-Fix/SOURCE_AND_INPUT_LOCK.md', 'DCL-R6-TerminalRead-Fix/FINAL_DECISION.md',
 'DCL-R6-TerminalRead-Fix/SOURCE_AND_INPUT_LOCK.md', 'DCL-R6-PTA-PF-A/PFA_FINAL_DECISION.md',
 'DCL-R6-PTA-PhaseFinalizer-Fix/FINAL_DECISION.md', 'DCL-R6-PreT0-Fix/FINAL_DECISION.md',
 'DCL-R6-ManagerRecovery-Fix/FINAL_DECISION.md', 'DCL-R6-ManagerRecovery-Fix/SOURCE_AND_INPUT_LOCK.md',
 'DCL-R6-CalDiag/CALDIAG_FINAL_DECISION.md', 'DCL-R6-CalDiag/CALDIAG_CASE_DURATION_REPORT.md',
 'DCL-R6-B09-Supplement/FINAL_DECISION.md',
 'DCL-R6-RuntimeAdapt-Fix/evidence/PROTECTED_SEMANTICS_CHECK.json',
 'DCL-R6-RuntimeAdapt-Fix/evidence/RESOURCE_BOUND_RECALCULATION.json',
 'DCL-R6-RuntimeAdapt-Fix/evidence/PROVENANCE_DECISION.json',
 'DCL-R6-B09-Supplement/evidence/RESOURCE_BOUND_RECALCULATION.json',
 'DCL-R6-TR-A2/evidence/ACTUAL_RESULTS.json', 'DCL-R6-TR-A2/evidence/DELIVERY_CHECK.json',
 'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json']
prior = []
for rel in preferred:
    p = PROJECT / rel
    assert p.is_file(), str(p)
    copy(p, E / 'HISTORICAL_REFERENCES' / rel)
    prior.append({'relative': rel, 'bytes': p.stat().st_size, 'sha256': sha(p)})
save('HISTORICAL_REFERENCE_INDEX.json', prior)
zpath = PROJECT / 'DCL-R6-TR-A2/TRA2_EVIDENCE.zip'
with zipfile.ZipFile(zpath) as z:
    names = z.namelist()
    assert len(names) == len(set(names))
    members = [{'name': n, 'bytes': z.getinfo(n).file_size, 'sha256': hashlib.sha256(z.read(n)).hexdigest()} for n in names]
    bad = z.testzip()
assert bad is None and sha(zpath) == '50297a4af1bc0d0a339a3e960993d8f65c277a2c9c03c1c3a8598b701d18d9d2'
save('TRA2_ZIP_RECHECK.json', {'path': str(zpath), 'sha256': sha(zpath), 'entries': len(names), 'CRC_failure': bad, 'members': members})

# Construct a filename witness using frozen JSON counts and actual Store.put names.
# These paths are predictions on a successful trace, never fabricated runtime files.
suite_specs = [
 ('PT64', 'startup_contract.json', 'startup_regression.py', 'pt_case_%03d.json'),
 ('PF48', 'phase_finalizer_contract.json', 'phase_finalizer_regression.py', 'pf_case_%03d.json'),
 ('TR40', 'terminal_contract.json', 'terminal_regression.py', 'tr_case_%03d.json'),
 ('RA32', 'runtime_regression_contract.json', 'runtime_regression.py', 'ra_case_%03d.json'),
 ('READY64', 'readiness_contract.json', 'readiness_regression.py', 'ready_case_%03d.json'),
 ('MR64', 'manager_contract.json', 'manager_recovery_regression.py', 'mr_case_%03d.json')]
witness = []
summaries = []
for label, contract_name, driver, pattern in suite_specs:
    cfg = read(SOURCE/'inputs'/contract_name)
    constants = [n.value for n in ast.walk(trees[driver]) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert pattern in constants
    for i, job in enumerate(cfg['jobs']):
        witness.append({'suite': label, 'case_id': job['case_id'], 'relative': 'inputs/root_private/boot/' + pattern % i,
                        'origin': 'STATIC_PREDICTED_PATH_ONLY'})
    summaries.append({'suite': label, 'jobs': len(cfg['jobs']), 'driver': driver, 'contract': contract_name,
                     'mutants': sum(bool(j.get('mutant')) or j.get('variant') == 'mutant' for j in cfg['jobs'])})
assert len(witness) == len({r['relative'] for r in witness}) == 312
admin_cap = read(SOURCE/'inputs/startup_contract.json')['admin_max_files']
terminal_tree = trees['terminal_evidence.py']
native_compare = [ast.unparse(n) for n in ast.walk(terminal_tree) if isinstance(n, ast.Compare) and
                  ast.unparse(n.left) == 'len(names)' and any(isinstance(c, ast.Constant) and c.value == 257 for c in n.comparators)]
assert admin_cap == 256 and native_compare
save('SEAL_CAPACITY_STATIC_WITNESS.json', {
 'status': 'STATIC_CONTRACT_CONFLICT', 'assumption': 'All mandatory six C00-post suites complete successfully; original evidence retained',
 'suites': summaries, 'raw_file_lower_bound': 312, 'raw_paths': witness,
 'admin_max_files': admin_cap, 'minimum_admin_excess': 312-admin_cap,
 'native_max_members': 257, 'minimum_native_members': 313, 'minimum_native_excess': 313-257,
 'native_compare': native_compare, 'other_artifacts_counted': 0, 'models_counted': 0,
 'dynamic_test_status': 'UNRUN_STATIC_REVIEW', 'expected_admin_failure_if_successful_prefix': 'PT_ADMIN_EVIDENCE_BOUND',
 'expected_terminal_native_failure_if_zip_created': 'TR_NATIVE_MEMBER_SET'})

cfg = {n: read(p) for p in (SOURCE/'inputs').glob('*.json') for n in [p.stem]}
probes = [1,1,1+128*(1+1048576//4096),1+16777216//4096,2,19,1,1,1,1,1,5,7]
assert sum(probes) == 37034
parts = [
 {'phase':'C00_C12','hard':sum(probes),'proof':'13 entry visits + 32896 + 4096 + 1 exact credits +18 C05 attempts +4 C11 +6 C12; page4096 required'},
 {'phase':'READY64','hard':cfg['readiness_contract']['regression_hard_visits']},
 {'phase':'C09H_IPC_BC_joint','hard':cfg['c09_contract']['synthetic_charge_cap']},
 {'phase':'RANGE34_gate18_ledger_raw','hard':cfg['safety_contract']['global_safety_charge_cap']},
 {'phase':'MR64_native_prepaid','hard':cfg['manager_contract']['phase_hard_visits']},
 {'phase':'PT64','hard':cfg['startup_contract']['regression_hard_visits']},
 {'phase':'PF48','hard':cfg['phase_finalizer_contract']['hard_visits']},
 {'phase':'TR40','hard':cfg['terminal_contract']['hard_visits']},
 {'phase':'RA32','hard':cfg['runtime_regression_contract']['hard_visits']}]
range_cfg=cfg['safety_contract'];jobs=range_cfg['jobs'];ledger_cfg=cfg['ledger_gate_contract']
actors=sum(j['max_actors'] for j in jobs)
actor_bound=range_cfg['actor_event_cap']+sum(range_cfg['max_calls_per_actor'].values())+1+max(j['max_semantic_ops_per_actor'] for j in jobs)
ledger_completed=1+len(ledger_cfg['jobs'])*(ledger_cfg['prepay_per_job']+1)+2*len(ledger_cfg['jobs'])
range_completed=1+actors*actor_bound+2*len(jobs)+len(jobs)+1+len(range_cfg['gate_negative_cases'])+ledger_completed
assert ledger_completed==631 and range_completed==19861
c09_bound=1+len(cfg['c09_contract']['jobs'])*(cfg['c09_contract']['max_events_per_job']+2)
assert c09_bound==2245
visits=sum(p['hard'] for p in parts)
assert visits==68498
save('RESOURCE_BOUND_INDEPENDENT.json', {
 'status':'PASS_STATIC_VISIT_CAP_ONLY', 'scope':'Frozen reachable calibration path; requested missing native anomaly plan has no extra authorized budget proof',
 'parts':parts,'C00_C12_by_case':dict(zip(['C%02d'%i for i in range(13)],probes)),
 'page_bytes_assumption':4096,'current_page_bytes_check':'UNRUN_STATIC_BLOCKER',
 'C09H_raw_completed_exact':1+sum(len(j['events']) for j in cfg['c09_contract']['jobs'])+2*len(cfg['c09_contract']['jobs']),
 'C09H_completed_upper':c09_bound,'IPC_completed':1+sum(j['driver_charge_bound'] for j in cfg['root_ipc_contract']['jobs'])+len(cfg['root_ipc_contract']['jobs']),
 'BC_completed':1+len(cfg['boot_contract']['jobs'])*(cfg['boot_contract']['driver_prepay']+1),
 'joint_conservative_bound':c09_bound+cfg['root_ipc_contract']['hard_visits']+cfg['boot_contract']['test_hard_visits'],
 'RANGE_actor_count':actors,'RANGE_per_actor_success_bound':actor_bound,
 'RANGE_completed':range_completed,'RANGE_using_ledger_hard':range_completed-ledger_completed+ledger_cfg['hard_visits'],
 'ledger_initial':1+len(ledger_cfg['jobs'])*(ledger_cfg['prepay_per_job']+1), 'ledger_reaudit_calls':2,'ledger_reaudit_visits':36,'ledger_completed':ledger_completed,
 'calibration_hard':visits,'calibration_soft':100000,'margin':100000-visits,
 'global_visits':1000000,'global_remaining_after_hard_calibration':1000000-visits,
 'formal_admission_pre_business_extra_visits':2,'wall':1800,'calibration_wall':300,'stop_relative':1740,'preT0_TCB':120,
 'AS_bytes':1073741824,'parent_tasks':4,'observed_time':None,'time_status':'UNRUN_STATIC_ADMISSION',
 'historical_descriptive_totals': {k:cfg[k].get('full_calibration_hard_visits',cfg[k].get('global_calibration_hard_bound')) for k in ['boot_contract','root_ipc_contract','readiness_contract']},
 'note':'Three inherited descriptive totals65618 differ from current independently summed68498; semantic caps unchanged. Main admission blockers are output capacity and native anomaly execution coverage.'})

excerpts = {}
ranges = {'guard.py':[(1038,1042),(1072,1078),(1084,1138),(993,1027),(513,544),(1230,1239)],
 'startup_lifecycle.py':[(493,510)],'terminal_evidence.py':[(151,173),(245,262)],
 'manager_recovery.py':[(207,242),(469,491)],'manager_recovery_regression.py':[(1,8),(24,39),(45,78)],
 'boot_continuity.py':[(70,100)],'ledger_gate_regression.py':[(75,137)]}
for name, spans in ranges.items():
    lines=(SOURCE/'src'/name).read_text(encoding='utf-8-sig').splitlines()
    excerpts[name]={'sha256':sha(SOURCE/'src'/name),'spans':[{'start':a,'end':b,'lines':[f'{i}: {lines[i-1]}' for i in range(a,min(b,len(lines))+1)]} for a,b in spans]}
save('SOURCE_EXCERPTS.json',excerpts)
save('NATIVE_ANOMALY_COVERAGE.json', {
 'status':'REQUIRED_NATIVE_EXCEPTION_PATH_MISSING_FROM_FULL_SCOPE',
 'MR64_origin':'MR-SIMULATION/1','MR64_count':64,'MR64_mutants':8,
 'native_success_path':'manager_recovery.resume -> health(True) -> review_case(C06,C07,C09) -> H.resume_admission -> MR_RECOVERY_REVIEW',
 'native_anomaly_path':'guard._launcher_work C10 -> diagnostic_marker only for MR_RECOVERY_DIAGNOSTIC_ONLY; exits78 and permanently closes batch',
 'native_anomaly_checker':'guard coordinator diagnostic_report only on exit78 and MR_RECOVERY_DIAGNOSTIC_ONLY',
 'full_scope':'CALIBRATE_S1S9_THEN_F1_F4','full_scope_native_injection_reachable':False,
 'simulated_close_proves_real_role_exit':False,'historical_MR_native_acceptance':'Not established by TR-A2 normal minimal path',
 'decision':'Missing required execution coverage under request sections7.4/11. No runtime alteration or second scope under current batch.'})
mis=read(PROJECT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json')
misrows=[]
for row in mis['files']:
    p=Path(mis['path'])/row['relative']
    misrows.append({'relative':row['relative'],'sha256':sha(p),'matches':sha(p)==row['duplicate_sha256']})
assert len(misrows)==47 and all(r['matches'] for r in misrows)
save('MISPATH47_READ_ONLY_CHECK.json', {'files':misrows,'mutations':0})
save('STATIC_DECISION.json', {
 'decision':'BLOCKED_STATIC_ADMISSION','utc':datetime.now(timezone.utc).isoformat(),
 'first_confirmed_blocker':'FC-S01_ADMIN_CAPACITY_312_GT_256',
 'other_blockers':['FC-S02_TERMINAL_NATIVE_CAPACITY_313_GT_257','FC-S03_NATIVE_EXCEPTION_PATH_NOT_IN_FULL_SCOPE'],
 'source_status':'64_OF_64_EXACT','source_version':'RuntimeAdapt-static-1/r1',
 'new_runtime_batch_id':None,'new_dynamic_receipt':None,'new_execution_lock':None,'source_edits':0,
 'WSL_calls':0,'deployment':0,'active_entries':0,'model_imports':0,'dynamic_tests':0,'test_retries':0,
 'new_budget_initialized':False,'T0':None,'deadline':None,'R':None,'new_visits_consumed':0,
 'current_runtime':'UNRUN_STATIC_ADMISSION','current_boot_id':None,'current_roles':'NOT_CREATED',
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'protocol_counterexamples':0,'static_configuration_witnesses':2,'internal_UNKNOWN':'HISTORICAL_PRESERVED_CURRENT_NOT_CREATED',
 'native_seal':'NOT_APPLICABLE_NO_RUNTIME','automatic_admin':'NOT_APPLICABLE_NO_ENTRY','research_archive':'PENDING',
 'STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED'})
print(json.dumps({'status':'BLOCKED_STATIC_ADMISSION','source_files':len(checks),'programs':len(syntax),'raw_lower_bound':len(witness),'hard_visits':visits,'history_files':len(history)},ensure_ascii=False))
