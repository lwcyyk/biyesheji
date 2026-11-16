"""Package the authorized B1 research review and prepend navigation records."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import time
import zipfile
from AUDIT_INPUTS import ROOT, PREVIOUS, OUT, EVIDENCE, RUNTIME, ISOLATED, NAVIGATION, read_json, digest, file_record, save, copy_file

started = time.perf_counter()
assert not (EVIDENCE / 'DELIVERY_CHECK.json').exists()
review = read_json(EVIDENCE / 'DELIVERABLE_REVIEW.json')
assert review['status'] == 'PASS_ADMINISTRATIVE_REVIEW_ONLY'
bindings = read_json(EVIDENCE / 'APPROVAL_OBJECT_BINDINGS.json')
for item in bindings['files']:
    assert digest(item['path']) == item['sha256']

inputs = [
    (PREVIOUS, 'FINAL_DECISION.md'),
    (PREVIOUS, 'APPROVAL_DECISION_PACKAGE.md'),
    (PREVIOUS, 'CURRENT_CONTRACT_UNSAT_PROOF.md'),
    (PREVIOUS, 'RESIDUAL_15_GAP_MATRIX.md'),
    (PREVIOUS, 'MINIMAL_CONTRACT_REVISION.md'),
    (PREVIOUS, 'GENERAL_BASELINE_AND_SEPARATION.md'),
    (PREVIOUS, 'evidence/DECISION_BINDINGS.json'),
    (PREVIOUS, 'proposals/OPTION_B_MINIMAL_REVISION.json'),
    (ROOT/'DCL-R6-C09-PendingQuota-Closure', 'FINAL_DECISION.md'),
    (ROOT/'DCL-R6-C09-CloseReserve-Closure', 'FINAL_DECISION.md'),
    (ROOT/'DCL-R6-FullChain-AdmissionFix', 'FINAL_DECISION.md'),
    (ROOT/'DCL-R6-ManagerRecovery-Fix', 'FINAL_DECISION.md'),
    (ROOT/'DCL-R6-C09-BoundClosure', 'MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md'),
    (ROOT/'DCL-R6-C09-PendingQuota-Closure', 'evidence/QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json'),
    (ROOT/'DCL-R6-C09-PendingQuota-Closure', 'evidence/RECORD_BYTE_ALGEBRA.json')]
copied = []
for base, relative in inputs:
    original = base / relative
    destination = EVIDENCE / 'PRIOR_INPUT_COPIES' / base.name / relative
    copy_file(original, destination)
    assert digest(original) == digest(destination)
    copied.append({'original': file_record(original), 'copy': str(destination)})
save('PRIOR_INPUT_COPY_LOCK.json', {'files': copied,
                                  'draft_alias_resolution': read_json(EVIDENCE/'DRAFT_HASH_AND_STATUS_CHECK.json')['requested_path_resolution']})
save('ADMIN_REVIEW_NOTES.json', {
    'administrative_edit_attempt': 'One research-script apply_patch hunk had a context mismatch. The call made no edits. A subsequent patch used the actual source context and the review passed.',
    'runtime_or_protocol_failure_tests': 0,
    'final_review': 'PASS_ADMINISTRATIVE_REVIEW_ONLY',
    'planning_decisions': [
        'Existing AdmissionBlocked route is the selected natural-language exhaustion candidate',
        'Two behavioral candidates and manager_recovery as an interface dependency',
        'Separate sibling future review directory and five proposed filenames',
        'runtime_tree_lock is a read-only stdlib dependency under the same-runtime premise']})

gates = read_json(EVIDENCE / 'FINAL_GATE_DECISIONS.json')
save('FINAL_MACHINE_DECISION.json', {
    'schema': 'DCL-B1-APPROVAL-GATE-DECISION/1',
    'client_date': '2026-11-16', 'timezone': 'Asia/Shanghai',
    'task_status': 'REVIEW_PLANNING_AND_APPROVAL_MATERIAL_COMPLETE',
    'B1_admission': 'B1_BLOCKED_BY_CLOSE_RESERVE', 'BG': gates['gates'],
    'direct_blocker': 'necessary exhaustion-close subset retention, space/isolation and failure responsibility',
    'logical_clauses_reviewable': ['B-C1','B-C2','B-C3','B-C4 order','B-C5 rejection'],
    'full_capacity': 'CAPACITY_CONTRACT_NOT_READY', 'B_close': None, 'B_other': None,
    'full_raw_native_admin_bytes': None, 'full_memory_FD_IO_syscalls': None,
    'strict_native_host_time': None,
    'four_permissions': read_json(OUT/'proposals/FOUR_PERMISSION_REVIEW_DRAFT.json'),
    'source_modified': 0, 'runnable_patch_generated': False,
    'new_execution_instance': None, 'T0': None, 'deadline': None, 'R': None,
    'WSL_calls': 0, 'dynamic_tests': 0, 'native_faults': 0, 'F1_runs': 0, 'F4_runs': 0,
    'RESOURCE_GATE_PASS': 'NOT_OBTAINED', 'F1': 'UNRUN_RESOURCE_GATE', 'F4': 'UNRUN_RESOURCE_GATE',
    'MR_CROSS_INSTANCE_ADMISSION': 'PROPOSED_NOT_EFFECTIVE', 'PASS_BOUNDED': [],
    'STRICT_SEPARATION_INSTANCES': 0, 'IMPLEMENTATION_GATE': 'CLOSED',
    'task_end_action': 'Stop after delivery and await actual user approval decisions'})

def report_link(name):
    return '[' + name + '](' + str(OUT/name).replace('\\','/') + ')'

prefix = (
    '## DCL-R6-B1-ApprovalGate 审批材料与实施准入（2026-11-16）\n\n'
    '**B1_BLOCKED_BY_CLOSE_RESERVE。** 本轮完成12份合同/语义差异/审批报告，BG-1/4/5/6为PASS_STATIC，'
    'BG-3为CONDITIONAL_PASS，BG-2为BLOCKED。256、263、345148及持久顺序/前置拒绝的逻辑要求可独立审议，'
    'B1耗尽后的必要停止信息保留、空间/隔离及失败责任仍需充分关闭子合同。\n\n'
    '行为候选为c09_handoff.py和guard.py，manager_recovery.py为必须核验的接口依赖。'
    '文件表含16既有文件摘要和5个PROPOSED_ABSENT未来位置，语义计划覆盖全部sink、caller耗尽消费、H锁释放、256次scalar预付及独立原件oracle。'
    'runtime_tree_lock当前绑定标准库，列为只读TCB输入。\n\n'
    '四类许可各有独立表单和user_decision=null。CAPACITY_CONTRACT_NOT_READY，MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE。'
    '现行完整成功目标CURRENT_CONTRACT_UNSAT及各null责任按原证明记录。'
    '运行源/预算核心/256与257/D1和D2改动0，可运行补丁0，新批次/T0/预算0，WSL/动态/真实故障/F1和F4运行0。'
    'RESOURCE_GATE_PASS=NOT_OBTAINED，STRICT_SEPARATION_INSTANCES=0，IMPLEMENTATION_GATE=CLOSED。\n\n'
    + report_link('FINAL_DECISION.md') + ' · ' + report_link('B1_SCOPE_AND_DEPENDENCY.md') + ' · '
    + report_link('USER_APPROVAL_CHECKLIST.md') + ' · ' + report_link('EVIDENCE_INDEX.md') + '\n\n'
    '本轮交付后等待用户逐条决定。下文完整保留先前导航字节。\n\n---\n\n')
navigation = read_json(EVIDENCE / 'NAVIGATION_BASELINE.json')['files']
for item in navigation:
    path = Path(item['path'])
    old = Path(item['copy']).read_bytes()
    assert path.read_bytes() == old and digest(item['copy']) == item['sha256']
    path.write_bytes(prefix.encode('utf-8') + old)

baseline = read_json(EVIDENCE / 'ALL_PRIOR_BASELINE.json')['files']
assert len(baseline) == 10454
mismatches = []
for item in baseline:
    path = Path(item['path'])
    if not path.is_file() or path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
        mismatches.append(str(path))
assert not mismatches, mismatches
expected = {item['path'] for item in baseline}
actual = {str(path) for base in (ROOT, ISOLATED) for path in base.rglob('*')
          if path.is_file() and not path.is_relative_to(OUT)
          and not (path.parent == ROOT and path.name in NAVIGATION)}
extra = sorted(actual - expected)
missing = sorted(expected - actual)
assert not extra and not missing, (extra, missing)
sources = read_json(EVIDENCE / 'FROZEN_SOURCE_LOCK.json')['files']
for item in sources:
    assert digest(item['path']) == digest(item['copy']) == item['sha256']
mispath = read_json(ROOT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json')
mispath_errors = [item['relative'] for item in mispath['files']
                  if digest(Path(mispath['path'])/item['relative']) != item['duplicate_sha256']]
assert len(mispath['files']) == 47 and not mispath_errors
nav_check = []
for item in navigation:
    assert Path(item['path']).read_bytes().endswith(Path(item['copy']).read_bytes())
    nav_check.append({'path': item['path'], 'old_suffix_sha256': item['sha256'],
                      'suffix_preserved': True, 'current_sha256': digest(item['path'])})
save('FINAL_IMMUTABILITY_CHECK.json', {
    'historical_files_unchanged': 9867, 'prior_delivery_files_unchanged': 587,
    'all_prior_unchanged': 10454, 'mismatches': mismatches, 'missing': missing, 'extra_outside_delivery': extra,
    'runtime_source_inputs_unchanged': 64, 'prior_maintenance_objects': 8, 'prior_contract_review_objects': 21,
    'mispath_files': 47, 'mispath_errors': mispath_errors, 'navigation': nav_check})

json_count = 0
for path in OUT.rglob('*.json'):
    read_json(path)
    json_count += 1
links = 0
link_errors = []
for path in OUT.glob('*.md'):
    content = path.read_text(encoding='utf-8')
    assert '不是' not in content
    for value in re.findall(r'\]\(([^)]+)\)', content):
        links += 1
        target = re.sub(r':\d+$', '', value.strip('<>'))
        if not Path(target).exists() and target != str(EVIDENCE/'DELIVERY_CHECK.json').replace('\\','/'):
            link_errors.append({'report': path.name, 'target': target})
assert not link_errors, link_errors
future = read_json(EVIDENCE/'FUTURE_FILE_SLOTS.json')
assert not Path(future['future_review_root']).exists()
for item in future['files']:
    assert not Path(item['file']).exists()

manifest_path = OUT / 'B1AG_MANIFEST.json'
archive_path = OUT / 'B1AG_EVIDENCE.zip'
excluded = {'B1AG_MANIFEST.json','B1AG_EVIDENCE.zip','B1AG_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json'}
members = []
for path in sorted(OUT.rglob('*')):
    relative = path.relative_to(OUT).as_posix()
    if path.is_file() and '__pycache__' not in path.parts and relative not in excluded:
        members.append({'relative': relative, 'bytes': path.stat().st_size, 'sha256': digest(path)})
manifest = {
    'schema': 'DCL-B1AG-RESEARCH-MANIFEST/1', 'client_date': '2026-11-16',
    'scope': 'Contract review, natural-language semantic plan, frozen read inputs and pending approval objects',
    'status': 'ADMINISTRATIVE_REVIEW_DELIVERY_ONLY', 'files': members, 'excluded': sorted(excluded)}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
with zipfile.ZipFile(archive_path, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for item in members:
        archive.write(OUT/item['relative'], item['relative'])
    archive.write(manifest_path, manifest_path.name)
with zipfile.ZipFile(archive_path) as archive:
    names = archive.namelist()
    assert len(names) == len(set(names)) == len(members)+1
    assert set(names) == {item['relative'] for item in members} | {manifest_path.name}
    assert archive.read(manifest_path.name) == manifest_path.read_bytes()
    for item in members:
        data = archive.read(item['relative'])
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
archive_digest = digest(archive_path)
(OUT/'B1AG_EVIDENCE.zip.sha256').write_text(archive_digest+'  B1AG_EVIDENCE.zip\n', encoding='ascii')
impact = read_json(EVIDENCE/'RESOURCE_IMPACT_MODEL.json')
save('DELIVERY_CHECK.json', {
    'schema': 'DCL-B1AG-DELIVERY/1', 'client_date': '2026-11-16', 'timezone': 'Asia/Shanghai',
    'status': 'PASS_ADMINISTRATIVE_REVIEW_DELIVERY_ONLY',
    'task_status': 'CONTRACT_REVIEW_PLANNING_APPROVAL_PACKAGE_COMPLETE',
    'B1_admission': 'B1_BLOCKED_BY_CLOSE_RESERVE', 'BG': gates['gates'],
    'reports': 12, 'index': 1, 'logical_clauses': 13, 'existing_file_rows': 16, 'future_file_slots': 5,
    'semantic_steps': 10, 'negative_obligations_planned': 15, 'negative_obligations_executed': 0,
    'separate_agent_source_reviews': 2, 'future_review_directory_created': False,
    'historical_files_unchanged': 9867, 'prior_delivery_files_unchanged': 587, 'all_prior_files_unchanged': 10454,
    'runtime_source_inputs_unchanged': 64, 'historical_mismatches': mismatches, 'extra_outside_delivery': extra,
    'prior_maintenance_objects_unchanged': 8, 'prior_contract_review_objects_unchanged': 21,
    'mispath_files_unchanged': 47, 'navigation_original_suffixes_preserved': 4,
    'prior_archive_members_rechecked': 134, 'approval_objects': bindings['files'],
    'MR_rule_sha256': bindings['MR_original_rule']['sha256'], 'MR_rules': 14,
    'approval_received': False, 'drafts_effective': False, 'drafts_runtime_enabled': False,
    'B_close': None, 'B_other': None, 'full_raw_native_admin_bytes': None, 'full_memory_FD_IO_syscalls': None,
    'capacity': 'CAPACITY_CONTRACT_NOT_READY', 'old_capacity_guards': '256/257_UNCHANGED',
    'prepay_conditional_journal_increment_upper': impact['prepay']['journal_byte_increment_upper'],
    'prepay_conditional_data_write_bytes_upper': impact['prepay']['total_data_write_bytes_upper'],
    'prepay_conditional_fsync_calls': impact['prepay']['fsync_calls_healthy_root'],
    'runtime_mechanism_edits': 0, 'budget_core_edits': 0, 'D1_D2_edits': 0, 'runnable_patches_generated': 0,
    'new_execution_instances': 0, 'T0': None, 'deadline': None, 'R': None, 'new_budget_accounts': 0,
    'WSL_calls': 0, 'dynamic_tests': 0, 'native_faults': 0, 'F1_runs': 0, 'F4_runs': 0,
    'RESOURCE_GATE_PASS': 'NOT_OBTAINED', 'F1': 'UNRUN_RESOURCE_GATE', 'F4': 'UNRUN_RESOURCE_GATE',
    'MR_CROSS_INSTANCE_ADMISSION': 'PROPOSED_NOT_EFFECTIVE', 'STRICT_SEPARATION_INSTANCES': 0,
    'PASS_BOUNDED': [], 'IMPLEMENTATION_GATE': 'CLOSED',
    'native_seal': 'NOT_APPLICABLE_NO_RUNTIME', 'administrative_runtime_seal': 'NOT_APPLICABLE_NO_ENTRY',
    'research_archive': 'SEALED_AND_VERIFIED', 'JSON_parsed': json_count, 'links_checked': links, 'link_errors': link_errors,
    'manifest_files': len(members), 'ZIP_members': len(names), 'manifest_sha256': digest(manifest_path),
    'ZIP_sha256': archive_digest, 'ZIP_bytes': archive_path.stat().st_size,
    'receipt_excluded_from_preimages': True, 'await_user_decision_after_delivery': True,
    'utc_recorded': datetime.now(timezone.utc).isoformat(), 'administrative_packaging_seconds': time.perf_counter()-started})
print(json.dumps({'delivery':'PASS_REVIEW_ONLY','reports':12,'clauses':13,'files':16,'future_slots':5,
                  'all_prior':10454,'source64':'UNCHANGED','B1_admission':'B1_BLOCKED_BY_CLOSE_RESERVE',
                  'ZIP_members':len(names),'ZIP_bytes':archive_path.stat().st_size,'ZIP_sha256':archive_digest,
                  'approval_received':False,'runtime_runs':0},ensure_ascii=False))
