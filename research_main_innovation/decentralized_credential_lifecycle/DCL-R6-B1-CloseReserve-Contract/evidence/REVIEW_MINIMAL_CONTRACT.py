"""Review artifact coverage, independent byte arithmetic and inactive flags."""
import json
import re
from pathlib import Path
from READ_INPUTS import ROOT, PREVIOUS, OUT, E, RUNTIME, read, sha, save

required_reports = [
    'B1_CLOSE_CALL_GRAPH.md','B1_REQUIRED_CLOSE_EVIDENCE.md','B1_CLOSE_RECORD_COUNT_PROOF.md',
    'B1_CLOSE_BYTE_BOUND_PROOF.md','B1_MAIN_AND_CLOSE_QUOTA_SEPARATION.md','B1_PHYSICAL_RESERVE_AUDIT.md',
    'B1_PERSISTENCE_FAILURE_MATRIX.md','B1_FAILURE_RESPONSIBILITY.md','B1_MINIMAL_CLOSE_RESERVE_CONTRACT.md',
    'B1_SECURITY_PROPERTIES.md','B1_REGRESSION_AND_ORACLE_PLAN.md','B1_RESOURCE_IMPACT.md',
    'B1_IMPLEMENTATION_ADMISSION_REQUEST.md','FINAL_DECISION.md']
assert all((OUT/name).is_file() for name in required_reports)
answers = read(E/'FINAL_TWENTY_ANSWERS.json')['answers']
assert [item['number'] for item in answers] == list(range(1,21))
graph = read(E/'B1_CLOSE_CALL_GRAPH.json')
assert len(graph['nodes']) == 18
fields = {'function','caller','return_or_result','preconditions','lock_state','possible_records','budget_effect','failure_exit'}
assert all(fields <= set(item) for item in graph['nodes'])
assert {'A_return_EXHAUSTED','B_map_to_CLOSED','C_fixed_exception'} == set(graph['alternatives'])
evidence = read(E/'B1_CLOSE_REQUIRED_EVIDENCE.json')
assert len(evidence['items']) == 18 and evidence['all4450_required_in_close_pool'] is False
assert evidence['safety_capture_before_admin_archive_required'] is True
for item in evidence['items']:
    assert {'necessity','producer','when','persistence','repeat_rule','main_log','independent_source','on_loss'} <= set(item)
count = read(E/'SCOPED_CLOSE_COUNT_PROOF.json')
incident = count['whole_incident_E']
assert incident['A_abort'] == 4+2 == 6
assert incident['S_stop_tree'] == 6+2 == 8
assert incident['W_waitpid'] == 1 and incident['H'] == 0 and incident['Q_seal_attempts'] == 3
assert incident['core_production_attempts'] == 7*6+2*8+1 == 59
assert incident['stable_core_paths_no_staging'] == 5+2*8+1+1 == 23
assert incident['failed_staging_path_upper'] == 3*6+2*6+2*8+1 == 47
assert incident['stable_plus_failed_staging_path_upper'] == 70
assert count['receiver']['clean_serialized_prefix']['total'] == 14
assert count['receiver']['clean_serialized_prefix']['stable_core_paths'] == 9

def combine(terms):
    result = {}
    for factor, expression in terms:
        for key,value in expression.items():
            result[key] = result.get(key,0)+factor*value
    return result

marker = {'constant':194}
first = {'constant':25092,'T':1,'B':1}
delegate = {'constant':260}
aborting = {'constant':237}
line = {'constant':998,'T':11,'B':1}
state = {'constant':997,'T':11,'B':1}
result = {'constant':1151,'E':1,'sumV':1}
wait = {'constant':1223}
production = combine([(6,marker),(6,first),(6,delegate),(6,aborting),(6,marker),
                      (6,line),(6,state),(8,marker),(8,result),(1,wait)])
assert production == {'constant':179815,'T':138,'B':18,'E':8,'sumV':8}
stable = combine([(1,marker),(1,first),(1,delegate),(1,state),(6,line),
                  (1,marker),(8,marker),(8,result),(1,wait)])
assert stable == {'constant':44708,'T':78,'B':8,'E':8,'sumV':8}
staging = combine([(6,delegate),(6,aborting),(6,state),(6,marker),(6,marker),
                   (8,marker),(8,result),(1,wait)])
assert staging == {'constant':23275,'T':66,'B':6,'E':8,'sumV':8}
assert combine([(1,stable),(1,staging)]) == {'constant':67983,'T':144,'B':14,'E':16,'sumV':16}

stamp = {'boottime':0,'utc_ns':0,'boot_id':'b'*36}
identity = {'pid':0,'start_ticks':0,'boot_id':'b'*36}
budget = {name:{'sha256':'a'*64,'bytes':0} for name in ('visits.bin','visits.bin.intent.json','visits.bin.journal.jsonl')}
first_example = {'schema':'MANAGER-RECOVERY/1','reason':'C09_OR_SUPERVISOR_FAILURE',
    'error_type':'AdmissionBlocked','error':'C09_PENDING_ALLOWANCE_EXHAUSTED','expected_diagnostic':False,
    'sample':stamp,'batch_id':'batch14','actor':identity,'window':{'T0':0,'deadline':0,'stop_at':0},'budget':budget}
first_bytes = len(json.dumps(first_example,sort_keys=True,separators=(',',':')).encode())+28+4*24+19+3*19
assert first_bytes == 941
assert len('MR_CRITICAL:C09_OR_SUPERVISOR_FAILURE')+2+144 == 183
assert 941+2*260+2*237+3*183+2*1155+4*1119+2 == 9272
assert 3+2+2+2+3+3+1+2 == 18
assert 2+2+3+3+1+2 == 13 and 18+13 == 31
normal = read(E/'NORMAL_HANDOFF_BYTE_MODEL.json')
assert normal['stable_carrier_bound']['constant_bytes'] == 7098
assert normal['generated_six_publication_bound']['constant_bytes'] == 11189
assert normal['cleanup_copies_in_stable_carriers'] == 3
partition = read(E/'PREPAY_AND_CLOSE_PARTITION.json')
assert 122112+142592+2048 == partition['write_volume_partition']['total'] == 266752
assert partition['prepay']['journal_rows'] == 512
assert partition['prepay']['fsync_calls_healthy_root'] == 2304
assert partition['prepay_is_close_reserve'] is False
storage = read(E/'PHYSICAL_STORAGE_AUDIT.json')
assert storage['PHYSICAL_STORAGE_RESERVED'] == 'NOT_OBTAINED'
assert storage['trusted_provider'] is None and storage['reserved_inodes'] is None
assert storage['source_allocation_or_free_space_calls_in_close_modules'] == []
counterexample = read(E/'MINIMAL_STORAGE_COUNTEREXAMPLE.json')
assert counterexample['admission_status'] == 'B1_CLOSE_RESERVE_COUNTEREXAMPLE'
assert counterexample['new_tests'] == 0 and counterexample['root_files_mutated'] == 0
contract = read(OUT/'proposals/B1_MINIMAL_CLOSE_RESERVE_DRAFT.json')
assert [item['number'] for item in contract['fields']] == list(range(1,21))
for flag in ('approved','user_approved','effective','runtime_enabled'):
    assert contract[flag] is False
assert contract['B_B1_close'] is None and contract['admission'] == 'B1_BLOCKED_BY_CLOSE_RESERVE'
assert contract['source_implementation_request'] == 'SUSPENDED'
binding = read(E/'CONTRACT_BINDING.json')
for item in binding.values():
    if isinstance(item,dict) and 'path' in item:
        assert sha(item['path']) == item['sha256']
cases = read(E/'REGRESSION_ORACLE_SPEC.json')
assert [item['id'] for item in cases['cases']] == [f'CR-{index}' for index in range(1,13)]
test_fields = {'normal_input','failure_input','concurrent_input','crash_interleaving',
               'expected_state','expected_bytes','independent_oracle','mutation_target'}
assert all(test_fields <= set(item) for item in cases['cases'])
assert cases['executed'] == 0 and cases['current_oracle_or_harness_code_written'] is False
links = 0
errors = []
for path in OUT.glob('*.md'):
    text = path.read_text(encoding='utf-8')
    assert '不是' not in text,path.name
    for value in re.findall(r'\]\(([^)]+)\)',text):
        links += 1
        target = re.sub(r':\d+$','',value.strip('<>'))
        if not Path(target).exists() and target != str(E/'DELIVERY_CHECK.json').replace('\\','/'):
            errors.append({'report':path.name,'target':target})
assert not errors,errors
assert not list(OUT.glob('*.patch')) and not list(OUT.glob('*.diff'))
save('DELIVERABLE_REVIEW.json', {'status':'PASS_RESEARCH_ARTIFACTS_ONLY','required_reports':14,'index':1,
    'final_answers':20,'call_nodes':18,'evidence_items':18,'contract_fields':20,'CR_specifications':12,
    'scope_E':incident,'independent_algebra_route':{'production':production,'stable':stable,'staging':staging},
    'healthy_first941_checked':True,'healthy_14write_constant':9272,'healthy_receiver_fsync':31,
    'prepay_partition_checked':True,'logical_physical_equivalence_claim':False,
    'B_B1_close':None,'physical_reserved':False,'caller_exit_provider':None,
    'admission':'B1_BLOCKED_BY_CLOSE_RESERVE','close_status':'B1_CLOSE_RESERVE_COUNTEREXAMPLE',
    'links_checked':links,'link_errors':errors,'DCL_dynamic_tests':0,'source_implementation_edits':0,
    'review_provenance':'same-agent independent algebra/coverage/contract checks; no independent native oracle execution'})
print(json.dumps({'review':'PASS_RESEARCH_ONLY','reports':14,'answers':20,'CR_specs':12,'links':links,
                  'close':'B1_CLOSE_RESERVE_COUNTEREXAMPLE','source_runs':0}))
