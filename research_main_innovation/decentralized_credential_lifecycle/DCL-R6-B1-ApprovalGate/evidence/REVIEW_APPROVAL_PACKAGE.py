"""Check research deliverables and approval consistency without DCL execution."""
import ast
import json
import re
from pathlib import Path
from AUDIT_INPUTS import ROOT, OUT, EVIDENCE, RUNTIME, read_json, digest, save

required_reports = [
    'B1_SCOPE_AND_DEPENDENCY.md', 'B1_FILE_LEVEL_MAINTENANCE_REQUEST.md', 'B1_SEMANTIC_DIFF_PLAN.md',
    'CAPACITY_LOGICAL_CLAUSES_APPROVAL.md', 'CAPACITY_NULL_BLOCKERS.md',
    'MR_CROSS_INSTANCE_APPROVAL_DECISION.md', 'FOUR_PERMISSION_SEPARATION.md',
    'FULLCHAIN_ADMISSION_DEPENDENCY.md', 'RESOURCE_AND_TIME_IMPACT.md',
    'GENERAL_BASELINE_AND_SEPARATION.md', 'USER_APPROVAL_CHECKLIST.md', 'FINAL_DECISION.md']
assert all((OUT / name).is_file() for name in required_reports)
clauses = read_json(EVIDENCE / 'CAPACITY_CLAUSE_MATRIX.json')['clauses']
assert [item['id'] for item in clauses] == [f'B-C{number}' for number in range(1, 14)]
clause_fields = {'existing_proof','source_basis','input_scope','parameter','closure_status','dependencies',
                 'proposed_files','negative_tests','applicability','effectiveness'}
assert all(clause_fields <= set(item) for item in clauses)
assert [item['class'] for item in clauses] == ['A'] + ['B'] * 4 + ['C'] * 8
assert [clauses[index]['parameter'] for index in range(3)] == [256, 263, 345148]
assert all(item['parameter'] is None for item in clauses[5:])
assert 256 * 1322 + 6 * 948 + 1028 == 345148

files = read_json(EVIDENCE / 'B1_FILE_PLAN.json')
assert files['behavioral_candidates'] == ['src/c09_handoff.py', 'src/guard.py']
assert not Path(files['future_review_root']).exists()
file_fields = {'file','current_hash','affected_function','issue','proposed_delta','invariant',
               'regression','dependency','rollback'}
for item in files['files']:
    assert file_fields <= set(item)
    assert digest(item['file']) == item['current_hash']
    assert item['current_changes'] == 0
assert len(files['files']) == 16
mr_file = next(item for item in files['files'] if item['relative'] == 'src/manager_recovery.py')
assert mr_file['category'] == 'INTERFACE_REVIEW_REQUIRED_CHANGE_NOT_SELECTED'
slots = read_json(EVIDENCE / 'FUTURE_FILE_SLOTS.json')['files']
assert len(slots) == 5
for item in slots:
    assert file_fields <= set(item)
    assert item['current_hash'] is None and not Path(item['file']).exists()
    assert item['created_now'] is False and item['status'] == 'PROPOSED_ABSENT'
refinements = read_json(EVIDENCE / 'BINDING_SCOPE_REFINEMENTS.json')
assert refinements['runtime_tree_lock']['application_source_entries'] == []

gate = read_json(EVIDENCE / 'B1_INDEPENDENCE_GATE.json')
assert gate['status'] == 'B1_BLOCKED_BY_CLOSE_RESERVE' and gate['BG-2'] == 'BLOCKED'
assert len(gate['requirements']) == 5 and gate['current_B_close'] is None
assert len(gate['unlock_evidence_required']) == 5
requirements = {item['id']: item for item in gate['requirements']}
assert requirements['ID-2']['status'] == 'UNRESOLVED'

graph = read_json(EVIDENCE / 'DEPENDENCY_GRAPH.json')
indegree = {name: 0 for name in graph['nodes']}
for before, after in graph['edges']:
    assert before in indegree and after in indegree
    indegree[after] += 1
queue = [name for name, count in indegree.items() if count == 0]
order = []
while queue:
    node = queue.pop(0)
    order.append(node)
    for before, after in graph['edges']:
        if before == node:
            indegree[after] -= 1
            if indegree[after] == 0:
                queue.append(after)
assert len(order) == len(indegree)
assert order.index('exhaustion_close_subcontract') < order.index('B1_admission')
assert order.index('current_calibration') < order.index('RESOURCE_GATE_PASS') < order.index('F1_F4')
assert order.index('archive_resource_proof') < order.index('full_capacity_contract')

impact = read_json(EVIDENCE / 'RESOURCE_IMPACT_MODEL.json')['prepay']
assert impact['journal_rows'] == 512
assert impact['journal_byte_increment_upper'] == 256 * (238 + 239) == 122112
assert impact['intent_write_bytes_upper'] == 256 * (278 + 279) == 142592
assert impact['counter_write_bytes'] == 2048
assert impact['total_data_write_bytes_upper'] == 266752
assert impact['data_write_attempts'] == 1280 and impact['fsync_calls_healthy_root'] == 2304
tests = read_json(EVIDENCE / 'B1_TEST_OBLIGATIONS.json')
assert len(tests['cases']) == 15 and tests['tests_executed'] == 0
assert read_json(EVIDENCE / 'GENERAL_G_COMPARISON.json')['STRICT_SEPARATION_INSTANCES'] == 0

objects = read_json(EVIDENCE / 'APPROVAL_OBJECT_BINDINGS.json')
for item in objects['files']:
    assert digest(item['path']) == item['sha256']
    data = read_json(item['path'])
    for flag in ('approved','user_approved','effective','runtime_enabled'):
        assert data[flag] is False
    assert data['user_decision'] is None
permissions = read_json(OUT / 'proposals/FOUR_PERMISSION_REVIEW_DRAFT.json')
names = ['CAPACITY_CONTRACT_APPROVAL','MR_CROSS_INSTANCE_APPROVAL',
         'NATIVE_IMPLEMENTATION_AUTHORIZATION','FULLCHAIN_DYNAMIC_AUTHORIZATION']
assert set(permissions['decision_forms']) == set(names)
for name in names:
    assert permissions[name]['user_decision'] is None
    assert permissions['decision_forms'][name]['selected'] is None
assert permissions['decision_forms']['NATIVE_IMPLEMENTATION_AUTHORIZATION']['source_mutation_permission'] is False
assert permissions['decision_forms']['FULLCHAIN_DYNAMIC_AUTHORIZATION']['run_permission'] is False
assert permissions['decision_forms']['FULLCHAIN_DYNAMIC_AUTHORIZATION']['execution_identity'] is None
assert read_json(EVIDENCE / 'MR_APPROVAL_RECHECK.json')['rules'] == 14

gates = read_json(EVIDENCE / 'FINAL_GATE_DECISIONS.json')['gates']
assert [item['id'] for item in gates] == [f'BG-{index}' for index in range(1, 7)]
assert next(item for item in gates if item['id'] == 'BG-2')['status'] == 'BLOCKED'
links = 0
errors = []
for path in OUT.glob('*.md'):
    text = path.read_text(encoding='utf-8')
    assert '不是' not in text, path.name
    for value in re.findall(r'\]\(([^)]+)\)', text):
        links += 1
        target = re.sub(r':\d+$', '', value.strip('<>'))
        if not Path(target).exists() and target != str(EVIDENCE / 'DELIVERY_CHECK.json').replace('\\','/'):
            errors.append({'report': path.name, 'target': target})
assert not errors, errors
assert not list(OUT.glob('*.patch')) and not list(OUT.glob('*.diff'))

save('INDEPENDENT_SOURCE_REVIEW_NOTES.json', {
    'provenance': 'Two separate agent read-only source reviews with parent context provided. This is a same-family review, without blind or cross-provider independence claims.',
    'reviewers': [
        {'task':'/root/close_dependency','finding':'B1_BLOCKED_BY_CLOSE_RESERVE under current request section六',
         'source_anchors':['guard.py:799-818','c09_handoff.py:252-279','manager_recovery.py:317-400','root_ipc.py:91-129'],
         'writes':0,'runtime_imports':0,'WSL_calls':0,'dynamic_tests':0},
        {'task':'/root/file_scope','finding':'two behavioral candidates, MR interface dependency, scalar256 prepay before C09, source-schema and helper obligations',
         'source_anchors':['guard.py:629-691,1095-1096','boot_continuity.py:78-109','c09_handoff.py:75-89,196,277'],
         'writes':0,'runtime_imports':0,'WSL_calls':0,'dynamic_tests':0}],
    'root_synthesis':'Closed source/declared schema/caller and closing storage conditions all entered current clause/file/gate objects'})
save('DELIVERABLE_REVIEW.json', {
    'status':'PASS_ADMINISTRATIVE_REVIEW_ONLY','required_reports':12,'index':1,'clause_rows':13,
    'existing_file_rows':16,'future_file_slots':5,'semantic_steps':10,'planned_negative_obligations':15,
    'BG_statuses':gates,'dependency_graph_acyclic':True,'topological_order':order,
    'prepay_data_bytes_upper':266752,'prepay_journal_delta_upper':122112,'prepay_fsync_calls':2304,
    'B1_admission':'B1_BLOCKED_BY_CLOSE_RESERVE','actual_user_approval':False,
    'links_checked':links,'link_errors':errors,'runtime_imports':0,'DCL_test_runs':0,'runtime_implementation_edits':0,
    'known_remaining':'necessary close-subcontract sufficiency, full capacity nulls, source/dynamic authorization',
    'planning_choices':['existing AdmissionBlocked route selected for the semantic candidate',
                        'future review sibling directory and five filenames proposed for explicit adoption']})
print(json.dumps({'review':'PASS_RESEARCH_ONLY','reports':12,'clauses':13,'files':16,'future_slots':5,
                  'links':links,'B1_admission':'B1_BLOCKED_BY_CLOSE_RESERVE'}))
