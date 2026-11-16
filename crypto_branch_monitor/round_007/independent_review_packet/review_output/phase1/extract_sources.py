from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys
import fitz

out = Path(r'D:\毕业设计\crypto_branch_monitor\round_007\independent_review_packet\review_output\phase1')
packet = out.parent.parent
log = out / 'ACCESS_LOG.jsonl'

def record(path, purpose, evidence, operation='read'):
    path = Path(path)
    row = {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'path': str(path.resolve()), 'operation': operation, 'purpose': purpose, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size, 'evidence_level': evidence}
    with log.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + '\n')

for name in ['REVIEW_REQUEST.md', 'STATEMENT_ONLY.md', 'INPUT_MANIFEST.json']:
    record(packet/name, '第一阶段控制文件，先于作者证明访问；本日志补记首次读取', 'submitted_statement')
skills = [
    Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\SKILL.md'),
    Path(r'C:\Users\a1887\.codex\plugins\cache\openai-primary-runtime\pdf\26.1026.10807\skills\pdf\SKILL.md'),
    Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\academic-paper-reviewer\WORKFLOW.md'),
    Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\academic-paper-reviewer\agents\methodology_reviewer_agent.md'),
    Path(r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\scripts\pdf_read_preflight.py')
]
for path in skills:
    record(path, '操作技能或PDF结构检查工具；前两次技能批量输出部分截断，仅作为操作规范', 'operational_skill')
manifest = json.loads((packet/'INPUT_MANIFEST.json').read_text(encoding='utf-8-sig'))
for item in manifest['phase1_allowed_inputs']:
    path = Path(item['path'])
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == item['sha256'], (path, digest)
    if path.suffix.lower() != '.pdf':
        continue
    record(path, '读取并核准原始公开PDF，逐页文字提取与结构检查', 'primary_pdf')
    result = subprocess.run([sys.executable, str(skills[-1]), str(path)], capture_output=True, encoding='utf-8')
    try:
        preflight = json.loads(result.stdout)
    except json.JSONDecodeError:
        preflight = {'verdict': 'UNAVAILABLE', 'exit_code': result.returncode,
                     'stdout': result.stdout, 'stderr': result.stderr}
    (out/(path.stem+'.preflight.json')).write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding='utf-8')
    print(path.name, 'preflight', result.returncode, preflight.get('verdict'))
    document = fitz.open(path)
    pages = [{'pdf_page': i+1, 'text': page.get_text(sort=True)} for i, page in enumerate(document)]
    text_path = out/(path.stem+'.pages.json')
    text_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding='utf-8')
    (out/(path.stem+'.txt')).write_text('\n\n'.join(f'=== PDF PAGE {p["pdf_page"]} ===\n{p["text"]}' for p in pages), encoding='utf-8')
    print(path.name, len(pages), 'pages', digest)
record(__file__, '本次创建的受限PDF提取和访问记账脚本', 'reproducibility_utility', 'execute')
