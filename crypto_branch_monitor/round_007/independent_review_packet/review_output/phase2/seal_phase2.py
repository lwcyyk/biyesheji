"""Seal phase 2 and revalidate every historical integrity binding."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import platform
import re

OUT = Path(__file__).resolve().parent
PACKET = OUT.parent.parent
PHASE1 = OUT.parent / 'phase1'
AUTHOR = PACKET / 'author_input'
LOG = OUT / 'ACCESS_LOG.jsonl'
MANIFEST = OUT / 'PHASE2_MANIFEST.json'
EXPECTED_PHASE1 = '608e80fde59b4d14cc9acfe71a5374a053c90a4124ef4c3fb2cb0c03acda14e3'
EXPECTED_AUTHOR = 'f0d8e2e0012592329af2d2c0d1b99b7d46045c6ceff4690d49716d227ccbde08'


def metadata(path):
    data = path.read_bytes()
    return {'path': str(path.resolve()), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


def record(path, purpose, evidence, operation, **extra):
    entry = {'recorded_utc': datetime.now(timezone.utc).isoformat(),
             **metadata(path), 'operation': operation,
             'purpose': purpose, 'evidence_level': evidence, **extra}
    with LOG.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + '\n')


phase1_manifest_path = PHASE1 / 'PHASE1_MANIFEST.json'
author_manifest_path = AUTHOR / 'AUTHOR_INPUT_MANIFEST.json'
assert metadata(phase1_manifest_path)['sha256'] == EXPECTED_PHASE1
assert metadata(author_manifest_path)['sha256'] == EXPECTED_AUTHOR
phase1_manifest = json.loads(phase1_manifest_path.read_text(encoding='utf-8'))
author_manifest = json.loads(author_manifest_path.read_text(encoding='utf-8'))
assert author_manifest['phase1_manifest_sha256'] == EXPECTED_PHASE1

record(author_manifest_path, '本阶段先读控制清单并核准自哈希和六份作者输入绑定',
       'phase2_control', 'read_and_hash', access_timing='retrospective_initial_read_and_current_recheck')
author_inputs = []
for item in author_manifest['author_inputs']:
    path = Path(item['path'])
    info = metadata(path)
    assert info['sha256'] == item['sha256'] and info['bytes'] == item['bytes']
    info['role'] = item['role']
    author_inputs.append(info)
    record(path, '核准哈希后读取完整作者快照，逐项数学比对；封存时再次核准',
           'author_snapshot_informed', 'read_and_hash',
           role=item['role'], access_timing='retrospective_phase2_read_and_current_recheck',
           origin_path_referenced_only=item['origin_path'])

record(PHASE1 / 'FI_v4.txt', '本阶段检索单向密文更新的原文定位',
       'primary_pdf_extract', 'keyword_search_and_hash',
       access_timing='retrospective_phase2_read')
record(PHASE1 / 'FI_v4.pages.json', '本阶段完整读取FI物理第16页文字，核准原文的方向说明',
       'primary_pdf_extract', 'read_page_and_hash', pdf_pages=[16],
       access_timing='retrospective_phase2_read')

phase1_records = phase1_manifest['inputs'] + phase1_manifest['operational_skill_inputs'] + phase1_manifest['outputs']
assert len(phase1_records) == 40
verified_phase1 = []
for item in phase1_records:
    path = Path(item['path'])
    info = metadata(path)
    assert info['sha256'] == item['sha256'] and info['bytes'] == item['bytes'], str(path)
    verified_phase1.append(info)
    record(path, '按第一阶段封存清单逐份核准原字节，仅作完整性读取',
           'integrity_only', 'hash_integrity_check')
record(phase1_manifest_path, '核准第一阶段清单自哈希与40条记录',
       'integrity_control', 'read_and_hash')

comparison_path = OUT / 'COMPARISON.md'
comparison = comparison_path.read_text(encoding='utf-8')
assert re.search(r'不是[^\n]{0,100}而是', comparison) is None
verdict = json.loads((OUT / 'FINAL_REVIEW_VERDICT.json').read_text(encoding='utf-8'))
results = json.loads((OUT / 'FINITE_EXACT_RESULTS.json').read_text(encoding='utf-8'))
assert verdict['reviewer']['actual_model_id'] == ''
assert verdict['reviewer']['joint_supplement_first_visible_phase'] == 2
assert verdict['reviewer']['phase1_author_proofs_visible'] is False
assert len(results['joint_module_cases']) == 18 and results['checks_passed'] is True

for path in sorted(OUT.iterdir()):
    if not path.is_file() or path in [LOG, MANIFEST]:
        continue
    if path.name == 'COMPARISON.md':
        evidence, purpose = 'general_proof_and_informed_comparison', '本阶段自写比对、联合方法证明与最小修正文本，读回验证'
    elif path.name == 'FINAL_REVIEW_VERDICT.json':
        evidence, purpose = 'informed_review_verdict', '本阶段机器裁决，解析并核准身份与范围'
    elif path.name in ['finite_joint_checks.py', 'FINITE_EXACT_RESULTS.json']:
        evidence, purpose = 'finite_exact_check', '实际执行的有限数学核对及其原始标量结果'
    else:
        evidence, purpose = 'reproducibility_utility', '本阶段实际执行的封存工具'
    record(path, purpose, evidence, 'read_execute_or_validate_and_hash')

with LOG.open('a', encoding='utf-8') as stream:
    stream.write(json.dumps({
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'operation': 'phase2_seal',
        'purpose': '第一阶段40条记录及清单自哈希、作者6份快照及作者清单全部核准',
        'evidence_level': 'audit_metadata',
        'phase1_record_mismatches': [],
        'author_snapshot_mismatches': [],
        'historical_mutations': 0,
        'author_origin_path_reads': 0,
        'phase2_supplement_identity': 'informed_first_seen_phase2'
    }, ensure_ascii=False) + '\n')

outputs = [metadata(path) for path in sorted(OUT.iterdir())
           if path.is_file() and path != MANIFEST]
manifest = {
    'schema': 'round007.independent-review.phase2-manifest/1.0',
    'sealed_utc': datetime.now(timezone.utc).isoformat(),
    'phase': 2,
    'status': 'complete_sealed',
    'reviewer_actual_model_id': '',
    'reviewer_task': '/root/linear_token_blind_review',
    'phase1_manifest': metadata(phase1_manifest_path),
    'phase1_records_verified': verified_phase1,
    'phase1_record_count': 40,
    'author_manifest': metadata(author_manifest_path),
    'author_inputs': author_inputs,
    'author_snapshot_count': 6,
    'outputs': outputs,
    'manifest_self_hash': '最终回复提供本文件SHA-256，自身哈希采用外部登记',
    'integrity_results': {
        'phase1_self_hash_matches': True,
        'phase1_all_40_records_match': True,
        'author_manifest_hash_matches': True,
        'author_all_6_records_match': True,
        'historical_mutations': 0
    },
    'provenance': {
        'phase1_author_proof_visibility': False,
        'phase2_author_snapshots_read': True,
        'joint_supplement_first_seen_phase': 2,
        'joint_supplement_review_identity': 'PHASE2_INFORMED_REVIEW',
        'phase1_conclusions_rewritten': False,
        'original_source_paths_for_author_snapshots_read': False,
        'references_to_unprovided_files_followed': False,
        'new_pdf_text_review': {'FI_v4': [16]},
        'new_operational_skills_read': [],
        'global_priority_certified': False
    },
    'evidence': {
        'general_proof': 'COMPARISON.md',
        'finite_exact_script': 'finite_joint_checks.py',
        'finite_exact_results': 'FINITE_EXACT_RESULTS.json',
        'levels_separately_registered': True
    },
    'runtime': {'python': platform.python_version(), 'platform': platform.platform()},
    'output_validation': {'json_parse': 'PASS', 'requested_deliverables_present': True,
                          'language_pattern_check': 'PASS', 'finite_checks': 'PASS'},
    'implementation_scope': 'paper mathematics, source comparison, finite exact algebra and integrity utilities',
    'candidate_protection_protocol_or_attack_implementation_created': False
}
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({
    'manifest': metadata(MANIFEST),
    'comparison': metadata(comparison_path),
    'final_verdict': metadata(OUT / 'FINAL_REVIEW_VERDICT.json'),
    'access_log': metadata(LOG),
    'verified_phase1_records': 40,
    'verified_author_snapshots': 6,
    'output_count_excluding_manifest': len(outputs),
    'checks': 'PASS'
}, ensure_ascii=False))
