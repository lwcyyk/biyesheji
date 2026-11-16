"""Validate and seal the bounded first-phase review artifacts."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import platform
import re

OUT = Path(__file__).resolve().parent
PACKET = OUT.parent.parent
LOG = OUT / 'ACCESS_LOG.jsonl'
MANIFEST_PATH = OUT / 'PHASE1_MANIFEST.json'


def metadata(path):
    content = path.read_bytes()
    return {
        'path': str(path.resolve()),
        'bytes': len(content),
        'sha256': hashlib.sha256(content).hexdigest()
    }


def log_access(path, purpose, level, operation='read_and_hash', **extra):
    entry = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        **metadata(path),
        'operation': operation,
        'purpose': purpose,
        'evidence_level': level,
        **extra
    }
    with LOG.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + '\n')


input_manifest = json.loads((PACKET / 'INPUT_MANIFEST.json').read_text(encoding='utf-8-sig'))
allowed_files = {Path(item['path']): item for item in input_manifest['phase1_allowed_inputs']}
controls = [PACKET / name for name in ['REVIEW_REQUEST.md', 'STATEMENT_ONLY.md', 'INPUT_MANIFEST.json']]
inputs = []
for path in dict.fromkeys(controls + list(allowed_files)):
    info = metadata(path)
    if path in allowed_files:
        assert info['sha256'] == allowed_files[path]['sha256']
    info['role'] = 'primary_pdf' if path.suffix == '.pdf' else 'control'
    inputs.append(info)
    log_access(path, '第一阶段封存时再次核准输入字节哈希', info['role'])

skill_paths = [
    Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\SKILL.md'),
    Path(r'C:\Users\a1887\.codex\plugins\cache\openai-primary-runtime\pdf\26.1026.10807\skills\pdf\SKILL.md'),
    Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\academic-paper-reviewer\WORKFLOW.md'),
    Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\academic-paper-reviewer\agents\methodology_reviewer_agent.md'),
    Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\scripts\pdf_read_preflight.py')
]
skills = [metadata(path) for path in skill_paths]

for path in OUT.glob('*.json'):
    if path == MANIFEST_PATH:
        continue
    json.loads(path.read_text(encoding='utf-8-sig'))
for line in LOG.read_text(encoding='utf-8').splitlines():
    json.loads(line)

report = (OUT / 'PHASE1_DERIVATION.md').read_text(encoding='utf-8')
assert re.search(r'不是[^\n]{0,100}而是', report) is None
verdict = json.loads((OUT / 'PHASE1_VERDICT.json').read_text(encoding='utf-8'))
assert verdict['reviewer']['actual_model_id'] == ''
assert verdict['reviewer']['author_proofs_visible_before_phase1_commit'] is False
results = json.loads((OUT / 'FINITE_EXACT_RESULTS.json').read_text(encoding='utf-8'))
assert results['finite_parameter_prefix']['count'] == 511

preflight = {}
for stem in ['FI_v4', 'CANS2024', 'IEICE2026', 'official_frodo_2021_frozen']:
    data = json.loads((OUT / (stem + '.preflight.json')).read_text(encoding='utf-8'))
    assert data['verdict'] == 'PASS'
    preflight[stem] = {'verdict': data['verdict'], 'pages': data['declared_page_count']}

reviewed_pages = {
    'FI_v4': {'text': list(range(7, 16)), 'visual': [10, 14]},
    'CANS2024': {'text': list(range(6, 11)), 'visual': [7, 9]},
    'IEICE2026': {'text': list(range(3, 7)), 'visual': [4, 6]},
    'official_frodo_2021_frozen': {'text': [15, 16, 25], 'visual': [16, 25]}
}

for path in sorted(OUT.iterdir()):
    if not path.is_file() or path in [LOG, MANIFEST_PATH]:
        continue
    if path.suffix == '.png':
        level = 'primary_pdf_visual'
        purpose = '实际渲染并经view_image目视核准的原文页面，随后封存'
    elif path.name.endswith('.pages.json') or path.suffix == '.txt':
        level = 'primary_pdf_extract'
        purpose = '实际用于受限全文检索或逐页读取的自行提取文件，随后封存'
    elif path.name.endswith('.preflight.json'):
        level = 'structural_validation'
        purpose = '原始PDF结构检查结果，实际读回核准PASS与页数'
    elif path.name == 'FINITE_EXACT_RESULTS.json':
        level = 'finite_exact_check'
        purpose = '有限精确数学原始结果，实际读回验证与封存'
    elif path.name == 'finite_math_checks.py':
        level = 'finite_exact_check'
        purpose = '实际运行的有限数学枚举和标量核对脚本'
    elif path.suffix == '.py':
        level = 'reproducibility_utility'
        purpose = '本次创建并实际执行的提取、渲染或封存工具'
    else:
        level = 'general_proof'
        purpose = '本代理第一阶段推导或裁决，实际读回验证与封存'
    log_access(path, purpose, level)

# The log receives its final append before its hash is placed in the manifest.
with LOG.open('a', encoding='utf-8') as stream:
    stream.write(json.dumps({
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'operation': 'phase1_seal',
        'purpose': '封存结束，ACCESS_LOG自身哈希由PHASE1_MANIFEST记录',
        'evidence_level': 'audit_metadata',
        'author_snapshot_accessed': False,
        'network_research_accesses': 0,
        'outside_allowlist_research_file_accesses': 0
    }, ensure_ascii=False) + '\n')

outputs = [metadata(path) for path in sorted(OUT.iterdir())
           if path.is_file() and path != MANIFEST_PATH]
manifest = {
    'schema': 'round007.independent-review.phase1-manifest/1.0',
    'sealed_utc': datetime.now(timezone.utc).isoformat(),
    'phase': 1,
    'status': 'sealed_waiting_for_phase2_author_snapshot',
    'reviewer_actual_model_id': '',
    'reviewer_task': '/root/linear_token_blind_review',
    'inputs': inputs,
    'operational_skill_inputs': skills,
    'outputs': outputs,
    'manifest_self_hash': '最终回复提供本文件SHA-256，自身哈希采用外部登记',
    'read_scope': {
        'pdf_machine_processing': '清单内四份PDF全页文字提取与结构解析',
        'model_full_page_review': reviewed_pages,
        'model_keyword_search': '只在本代理生成的四份PDF文字提取文件中检索',
        'skills_reading': '操作技能批量输出有截断，按可见的审阅规范和页码核准规则使用',
        'filesystem_enumeration': '仅封存自身phase1输出目录，无工作区全局枚举',
        'audit_file_boundary': '研究输入、操作技能和本次生成文件逐份登记，解释器与标准运行库作为运行时依赖登记版本'
    },
    'runtime': {'python': platform.python_version(), 'platform': platform.platform()},
    'pdf_preflight': preflight,
    'resolved_tool_failures': [
        'pdf_read_preflight --output在Windows缺少POSIX dirfd，使用其标准输出模式成功完成四份检查',
        '首次提取文字搜索的控制台GBK编码异常，后续设置PYTHONIOENCODING=utf-8完成读取'
    ],
    'proof_and_finite_evidence_separated': True,
    'author_proofs_read_before_commit': False,
    'implementation_scope': '纸面推导、PDF工具和有限数学核对',
    'candidate_protocol_or_attack_implementation_created': False,
    'open_items': verdict['formalization_notes'],
    'phase2_required_input': '主会话明确交付的作者证明快照'
}
MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({
    'manifest': metadata(MANIFEST_PATH),
    'derivation': metadata(OUT / 'PHASE1_DERIVATION.md'),
    'verdict': metadata(OUT / 'PHASE1_VERDICT.json'),
    'access_log': metadata(LOG),
    'output_count_excluding_manifest': len(outputs),
    'checks': 'PASS'
}, ensure_ascii=False))
