from pathlib import Path
import json,re,hashlib,collections
OUT=Path(__file__).resolve().parents[1]
summary=json.loads((OUT/'data/execution_summary.json').read_text(encoding='utf-8'))
records=json.loads((OUT/'data/source_records.json').read_text(encoding='utf-8'))
refids={r['id'] for r in records}
files=[OUT/n for n in summary['markdown_outputs']]
substitutions={
'进行轨迹重放比较':'重放轨迹并比较',
'对加密资源进行受限委托':'加密资源的受限委托',
'进行模型与技术片段定点分析':'按模型与技术片段定点分析',
'普通 scope、RAR 表达和任务蕴含的比较应按各自能力进行':'普通 scope、RAR 表达和任务蕴含应按各自能力比较',
'本次对全目录进行文件级清点':'本次清点了全目录的文件',
'14 篇进行定点机制核验':'14 篇核验了定点机制',
'未全部进行内容核读':'尚未全部完成内容核读',
}
for p in files:
 t=p.read_text(encoding='utf-8')
 for a,b in substitutions.items():t=t.replace(a,b)
 if p.name.startswith(('05_','08_')):t=re.sub(r'\*\*([^*]+)\*\*',r'\1',t)
 if p.name.startswith('05_'):
  pos=t.index('## P24 ');end=t.index('## P25 ',pos)
  part=t[pos:end].replace('物理页 2,5 的定点片段','物理页 2,5,7 的定点片段')
  t=t[:pos]+part+t[end:]
  pos=t.index('## P29 ');end=t.index('## P30 ',pos)
  part=t[pos:end].replace('物理页 1,4 的定点片段','物理页 1,4,6 的定点片段')
  t=t[:pos]+part+t[end:]
 # Preserve URLs, source targets, code, mathematics and literal document titles in references.
 p.write_text(t,encoding='utf-8')

checks=[]
def check(name,cond,detail=''):
 checks.append({'check':name,'status':'PASS' if cond else 'FAIL','detail':detail})
check('12个请求的Markdown文件',len(files)==12 and all(p.is_file() and p.stat().st_size>1000 for p in files))
check('主报告独立内容长度',files[0].stat().st_size>40000,str(files[0].stat().st_size))
check('统一来源ID唯一',len(refids)==len(records)==94)
usedall=set();bad=[];style=[];missing_links=[]
for p in files:
 t=p.read_text(encoding='utf-8')
 used=set(re.findall(r'\[((?:P|D|L|O|N|CN|Q)\d{2})\]',t));usedall|=used
 bad.extend({'file':p.name,'id':k} for k in used-refids)
 if '不是' in t or '而是' in t or re.search(r'不仅.{0,100}(?:而且|更)',t):style.append(p.name)
 for link in re.findall(r'\]\(([^\n]*?)\)',t):
  if link.startswith(('https://','http://','#')):continue
  clean=link.strip('<>').split('#')[0]
  target=Path(clean) if re.match(r'^[A-Za-z]:/',clean) else p.parent/clean
  if not target.exists():missing_links.append({'file':p.name,'target':link})
check('正文引用均已定义',not bad,json.dumps(bad,ensure_ascii=False))
check('94项来源在交付中可定位',usedall==refids)
check('本地Markdown链接可定位',not missing_links,json.dumps(missing_links[:15],ensure_ascii=False))
check('指定句式检查',not style,str(style))
check('主报告模板已展开',all(x not in files[0].read_text(encoding='utf-8') for x in ['<!--CORE_MAP-->','<!--REFERENCES-->','待更新']))
papers=[r for r in records if r['id'].startswith('P')]
check('45篇核心及14篇定点',len(papers)==45 and sum(bool(r.get('deep_analysis')) for r in papers)==14)
check('核心PDF结构与页数',all(r.get('preflight')=='PASS' for r in papers) and sum(r['pages'] for r in papers)==1072)
check('三种核验状态',dict(collections.Counter(r['verification_status'] for r in records))==summary['reference_status_counts'])
ledger=json.loads((OUT/'data/read_ledger.json').read_text(encoding='utf-8'))
changed=[]
for r in ledger:
 p=Path(r['path'])
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:changed.append(r['path'])
check('72项所用输入哈希复核',len(ledger)==72 and not changed,json.dumps(changed,ensure_ascii=False))
check('新增机制与原生实验边界',summary['candidate_code_created']==summary['native_auth_requests']==summary['experiments_rerun']==0)
scopefix=[]
for p in files:
 t=p.read_text(encoding='utf-8')
 if '全文已核验' in t:scopefix.append(p.name)
check('全文与局部核验表述区分',not scopefix,str(scopefix))
result={'checks':checks,'pass':sum(c['status']=='PASS' for c in checks),'fail':sum(c['status']=='FAIL' for c in checks),'scope':'文档结构、来源与路径一致性检查；不构成论文证明或源实验验证','files':[{ 'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(OUT/'data/quality_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if result['fail']:raise SystemExit(1)
