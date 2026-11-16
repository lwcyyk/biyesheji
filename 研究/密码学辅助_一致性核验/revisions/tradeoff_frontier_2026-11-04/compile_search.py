"""Compile recorded bibliographic evidence. Does not make novelty decisions."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
NS = {'a': 'http://www.w3.org/2005/Atom', 'o': 'http://a9.com/-/spec/opensearch/1.1/'}
requests = [json.loads(line) for line in (ROOT / 'HTTP_REQUESTS.jsonl').read_text(encoding='utf8').splitlines()]
arxiv = []
for record in requests:
    if record.get('status') != 200 or 'export.arxiv.org/api/query' not in record['url']:
        continue
    tree = ET.parse(ROOT / record['saved'])
    entries = []
    for entry in tree.findall('a:entry', NS):
        entries.append(dict(url=entry.findtext('a:id', namespaces=NS),
                            title=' '.join(entry.findtext('a:title', default='', namespaces=NS).split()),
                            published=entry.findtext('a:published', namespaces=NS),
                            summary=' '.join(entry.findtext('a:summary', default='', namespaces=NS).split())))
    arxiv.append(dict(id=record['id'], matrix_id=record.get('matrix_id'), query=record.get('query', record['purpose']),
                      total=int(tree.findtext('o:totalResults', namespaces=NS)),
                      start=int(tree.findtext('o:startIndex', namespaces=NS)), entries=entries))
forward = []
for request_id, source in [('F01', 'Arithmetic Sketching'), ('F04', 'IK00'), ('F03', 'Giorgi2026')]:
    result = json.loads((ROOT / 'http' / (request_id + '.body')).read_text(encoding='utf8'))
    forward.append(dict(id=request_id, source=source, **result))
summary = dict(request_count=len(requests), expected_papers_fulltext=12,
               fulltext_targeted_read_papers=16, pdf_papers=15, html_papers=1,
               forward_sets=3, forward_records=sum(len(item['data']) for item in forward),
               q_matrix_valid_result_groups=15, arxiv_successful_response_pages=len(arxiv),
               arxiv_metadata_unique=len({e['url'] for item in arxiv for e in item['entries']}),
               forward_unique=len({p['citingPaper']['paperId'] for item in forward for p in item['data']}))
(ROOT / 'SEARCH_DATA.json').write_text(json.dumps(dict(summary=summary, arxiv=arxiv, forward=forward),
                                                   ensure_ascii=False, indent=2), encoding='utf8')

def esc(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')

lines = ['# S1–S5查新判定与检索闭合记录', '',
         '2026-11-04。判定范围为本轮取得全文并核读的章节。机器生成部分仅整理HTTP响应、书目和计数，命题判断来自MAPPING_UPDATE的人工分析。', '',
         '## 1. 逐项判定', '',
         '| 主张 | 本轮判定 | 已有部分与剩余差异 |', '|---|---|---|',
         '| S1 精确δ* | 未发现覆盖，限已核读分母 | NW06/IK02/Arithmetic Sketching涵盖矩阵盲化与随机编码。共享2×3、硬无抹除、全≤3、任意幅值、TV minimax的完整公式仍待优先权闭合 |',
         '| S2 唯一核边缘 | 未发现完整覆盖，对称化子项覆盖 | Orbanz有限群平均及IK02轨道不变性归入已有工具。h/l跨轨道权重唯一、秩2必然性与严格互补仍是单独候选 |',
         '| S3 表示敏感性 | 未发现精确δ*分离覆盖 | 拟阵多表示已有经典理论。r5中同一U₍₃,ₙ₎对应具体TV极值严格不同这一组合，在已读章节未见直接归约 |',
         '| S4 全局极值族 | 未发现完整覆盖，几何构造子项覆盖 | 经典二次曲线加核点、有限域零点界与域嵌入分别归属已有工具。T端点到δ*端点的结合继续依赖S1。扩展纯几何关键词检索受阻，优先权仍有明显缺口 |',
         '| S5 低故障完美幅值隐私/三故障最坏 | 覆盖，保留为构造推论 | 均匀frame轨道不变性及TV投影收缩给出结论。δ*具体数值归S1 |', '',
         '“未发现覆盖”表示在明确分母内取得的负检索结果，首次证明和强独立原创仍待确认。S1–S4的总体优先权状态均为UNRESOLVED。S4还保留纯有限几何原始文献缺口。', '',
         '## 2. 实际检索分母', '',
         '- 12篇指定论文均取得全文。另核读或复核IK00、Giorgi2026、Common Information…与P04，合计16篇，包含15份PDF和1份历史HTML。核读范围逐份列于MAPPING_UPDATE。',
         '- Q01–Q15每组均有arXiv有效返回，分页和零结果分别登记。另有A01组合检索及AQ12N术语补检。DBLP的15次搜索均未取得有效JSON结果。',
         '- 三组Semantic Scholar前向集合共有310条返回记录。它们为索引快照，正文覆盖判断仅使用已经取得并定位的论文。三份预期原始被引网页存档仍缺失。',
         '- Arithmetic Sketching参考表共50项，已读取所在PDF33–35页的书目文本。[33]/[34]已闭合到IK00/IK02正文。其他书目仅在已读原文条目范围内进入覆盖证据。',
         '- Giorgi2026参考表55项沿用历史登记。此次补齐其中MV24、HLPS26、GLOV24及CD01正文。全部55篇原始文献的全文核读仍待完成。', '',
         '机器统计如下。', '', '```json', json.dumps(summary, ensure_ascii=False, indent=2), '```', '',
         '检索库的分词可能扩展短语。AQ12实际返回大量随机多项式零点论文，故额外执行randomized encoding补检。arXiv对Arithmetic Sketching和Giorgi期刊论文的题名查询未定位到目标，正文通过其他入口取得。零结果只反映该检索式和该索引。', '',
         '## 3. Q01–Q15执行矩阵', '',
         '| 编号 | DBLP原始关键词 | DBLP执行 | arXiv实际检索式 | 取得记录/接口总数 |', '|---|---|---|---|---|']
for i in range(1, 16):
    query_id = f'Q{i:02d}'
    record = next(x for x in requests if x['id'] == query_id)
    pages = [x for x in arxiv if x.get('matrix_id') == query_id and x['id'] not in ['AQ12N']]
    entries = {e['url'] for page in pages for e in page['entries']}
    total = max(page['total'] for page in pages)
    query = pages[0]['query']
    failure = record.get('error') or f"HTTP {record['status']}，响应为HTML验证页"
    lines.append(f"| {query_id} | {esc(record['query'])} | {esc(failure)} | `{esc(query)}` | {len(entries)}/{total} |")
lines += ['', '### 补充检索', '', '| ID | 检索式 | 记录/总数 |', '|---|---|---|']
for item in arxiv:
    if item['id'] in ['A01', 'AQ12N']:
        lines.append(f"| {item['id']} | `{esc(item['query'])}` | {len(item['entries'])}/{item['total']} |")
lines += ['', 'AQ07N/AQ07NR尝试移除privacy关键词，仅查arc、secant/concurrent与finite/projective，两次均遇到TLS传输失败。该纯几何查询待PI或后续会话补取。', '',
          '## 4. 前向被引集合', '',
          '| 集合 | 接口记录数 | 分页 | 核验范围 |', '|---|---|---|---|']
for item in forward:
    lines.append(f"| {item['id']} {item['source']} | {len(item['data'])} | next={item.get('next', '缺省')} | 当前DOI对应索引快照，跨版本合并与全球完整性未核实 |")
lines += ['', 'F03的0条仅表示该期刊DOI当次接口无被引记录。ePrint版本可能另建记录，全球被引数仍未知。F04请求上限1000，返回300条且无next字段，按接口返回已结束处理。数据库遗漏、重复与版本拆分仍保留限制。', '',
          '下表完整保留API返回题名。所有“书目级”行均未用作覆盖或未覆盖的原文证据。', '',
          '| 来源集合 | 年份 | 题名 | 标识 | 阅读级别 |', '|---|---|---|---|---|']
for item in forward:
    for row in item['data']:
        paper = row['citingPaper']
        identifiers = paper.get('externalIds') or {}
        identity = identifiers.get('DOI') or identifiers.get('ArXiv') or paper['paperId']
        lines.append(f"| {item['id']} | {paper.get('year')} | {esc(paper['title'])} | {esc(identity)} | 书目级，正文判断另见N01–N16 |")
lines += ['', '## 5. 全部HTTP请求台账', '',
          'HTTP_REQUESTS.jsonl保存每次请求起止UTC时间、实际URL、状态、重定向终点、响应哈希和字节数。下表为完整索引。失败请求也保留原始错误。', '',
          '| ID | 起始UTC | URL | 结果 | 原始响应 |', '|---|---|---|---|---|']
for record in requests:
    outcome = record.get('error') or f"HTTP {record['status']} / {record.get('content_type')} / {record.get('bytes')} bytes"
    lines.append(f"| {record['id']} | {record['started_utc']} | {esc(record['url'])} | {esc(outcome)} | {esc(record.get('saved', '传输失败，无响应体'))} |")
lines += ['', '## 6. 强独立原创的建议口径', '',
          '可表述为“在16篇已核读全文、3组前向索引集合与Q01–Q15检索分母中，尚未发现对S1–S4完整命题的直接覆盖。若干证明工具及S5属于已有结论或直接推论。优先权仍需原始几何文献、三篇port/熵原文和后续引文全文核读”。', '',
          '当前支持的工作定位为受限模型中的精确极值候选。强独立密码学原创、通用支持隐私正误差下界以及同契约端到端优势，分别处于待建立状态。', '',
          '本报告各“覆盖”子项的死因为可写出变量代入的既有结论，见MAPPING_UPDATE。剩余候选的存活依据为本轮检索范围与命题差异，独立推导和查无同式均不足以确立优先权。', '']
(ROOT / 'SEARCH_CLOSURE.md').write_text('\n'.join(lines), encoding='utf8')
print(json.dumps(summary, ensure_ascii=False))
