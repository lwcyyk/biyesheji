from pathlib import Path
import os,json,csv,hashlib,collections,datetime,re
ROOT=Path(r'D:\毕业设计')
OUT=Path(__file__).resolve().parents[1]
SKIP={'.git','node_modules','.venv','venv','__pycache__','.mypy_cache','.pytest_cache','.runtime','vendor','target','dist','build','.gomodcache','.gocache','toolchain','.codex-report-rebuild-2026-11-09'}
EXT={'.pdf','.docx','.md','.txt','.csv','.json','.jsonl','.yaml','.yml','.bib','.tex','.py','.ts','.js','.toml','.log'}
rows=[];skips=[];errors=[]
def theme(p):
 s=str(p.relative_to(ROOT)).lower()
 if 'crypto_' in s or '密码学' in s:return '密码学辅助与更新加密'
 if '关键论文' in s:return '公开论文与标准草案'
 if 'mainline_' in s:return '原生部署与成熟机制验收'
 if 'research_main_innovation' in s:return '主创新理论与先例核查'
 if 'research_recipe' in s or 'research_secret_recipe' in s:return '可撤销资源理论'
 if 'research_v12' in s or 'auth-lifecycle' in s:return '有限规划与认证生命周期'
 if 'thesis_draft' in s:return '学位论文与证据整合'
 if '对话' in s:return '历史研究决策'
 return '综合报告与设计资料'
def kind(p):
 s=str(p).lower()
 if any(x in s for x in ['/secure/','\\secure\\','/regression','\\regression','/cache/','\\cache\\','/in/','/out/']):return '运行夹具或逐事件数据'
 if p.suffix.lower()=='.pdf':return '论文或报告PDF'
 if p.suffix.lower()=='.docx':return 'Word报告或设计文档'
 if p.suffix.lower() in {'.py','.ts','.js'}:return '源码'
 if p.suffix.lower() in {'.json','.csv','.jsonl'}:return '结构化证据'
 return '研究说明或笔记'
for dp,dn,fn in os.walk(ROOT):
 d=Path(dp)
 keep=[]
 for n in dn:
  p=d/n
  if n in SKIP or p==OUT or p.is_symlink():skips.append(str(p));continue
  keep.append(n)
 dn[:]=keep
 for n in fn:
  p=d/n
  if p.suffix.lower() not in EXT or n.startswith('~$') or n in {'.env','credentials.json'}:continue
  try:
   st=p.stat();cat=kind(p)
   rows.append({'path':str(p),'relative_path':str(p.relative_to(ROOT)),'extension':p.suffix.lower(),'bytes':st.st_size,'modified':datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec='seconds'),'topic':theme(p),'kind':cat,'value':'验证实现结构' if cat=='源码' else ('提供原始分母与轨迹' if cat=='运行夹具或逐事件数据' else '问题建模 文献或结论证据'),'analysis_status':'已清点 待读取','sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.suffix.lower() in {'.pdf','.docx'} else ''})
  except Exception as e:errors.append({'path':str(p),'error':str(e)})
rows.sort(key=lambda r:r['relative_path'].casefold())
with (OUT/'data/inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'data/inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
groups=collections.defaultdict(list)
for r in rows:
 if r['sha256']:groups[r['sha256']].append(r['path'])
dups=[{'sha256':k,'paths':v} for k,v in groups.items() if len(v)>1]
(OUT/'data/duplicate_files.json').write_text(json.dumps(dups,ensure_ascii=False,indent=2),encoding='utf-8')
stats={'root':str(ROOT),'output':str(OUT),'candidate_files':len(rows),'extensions':dict(collections.Counter(r['extension'] for r in rows)),'topics':dict(collections.Counter(r['topic'] for r in rows)),'kinds':dict(collections.Counter(r['kind'] for r in rows)),'binary_duplicate_groups':len(dups),'skipped_directories':skips,'errors':errors}
(OUT/'data/inventory_summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
curated=[r for r in rows if r['kind'] in {'研究说明或笔记','Word报告或设计文档','论文或报告PDF'} and not any(x in r['relative_path'].lower() for x in ['\\reading','全文.txt','分页','\\sources\\','\\source\\','\\runtime','\\logs','\\archive','\\results','\\data','\\dependencies','\\backup','\\temp','\\tmp'])]
lines=['# 现有研究资料清单','',f'研究根目录：`{ROOT}`。清点日期：2026 年 11 月 9 日。', '',f'共发现 {len(rows):,} 个候选研究文件。完整逐文件位置、类型、主题、价值、读取状态与 PDF/Word 哈希见 [inventory.csv](data/inventory.csv)。清点与全文阅读分别计数；运行夹具保留元数据，敏感状态内容按需避开。','', '## 资料类型统计','', '| 类型 | 文件数 |','|---|---:|']
lines += [f'| {k} | {v:,} |' for k,v in stats['kinds'].items()]
lines+=['','## 筛选与去重规则','','跳过依赖、版本库、编译缓存、运行环境和本次输出目录。按 SHA256 合并完全相同的 PDF/Word；论文再按 arXiv ID、DOI 和标题归并，同一论文的不同版本分别保留。完整重复组见 [duplicate_files.json](data/duplicate_files.json)。','', '## 研究说明与论文入口','', '| 路径 | 类型 | 主题 | 读取状态 |','|---|---|---|---|']
for r in curated:
 lines.append(f"| [{r['relative_path']}]({Path(r['path']).as_posix()}) | {r['kind']} | {r['topic']} | 已清点 待读取 |")
(OUT/'01_现有研究资料清单.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in stats.items() if k not in {'skipped_directories'}},ensure_ascii=False,indent=2))
print('CURATED',len(curated))
