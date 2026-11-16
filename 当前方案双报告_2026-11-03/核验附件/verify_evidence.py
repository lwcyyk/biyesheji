from pathlib import Path
import csv,json,hashlib,ast,zipfile,io,collections,re,subprocess,sys,os
R=Path(r'D:\毕业设计');O=Path(__file__).parents[1];W=O/'工作底稿';C=R/'研究/密码学辅助_一致性核验';S=R/'研究/算法机制重构与原创性验证_2026-11-03'
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x):(W/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
rows=list(csv.DictReader((O/'资料索引与来源哈希清单.csv').open(encoding='utf-8-sig')))
orig=j(W/'索引摘要.json')
for e in orig['errors']:
 p=R/e['path'];rows.append({'path':e['path'],'bytes':'', 'mtime_ns':'','category':'不可读文件或WSL链接','sha256':'','read_scope':'未读内容；'+e['error'].split(':')[0]})
for row in rows:
 s=row['path'].lower().replace('\\','/')
 if '/player-data/' in s or s.endswith(('.db','.mv.db')) or '/.runtime/l1/' in s and not '/dist/' in s:
  row['category']='运行时秘密或私有状态 仅元数据';row['sha256']='';row['read_scope']='不读取正文、不再分发'
with (O/'资料索引与来源哈希清单.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)
save('索引最终统计.json',{'entries':len(rows),'hashed':sum(bool(x['sha256']) for x in rows),'unreadable':len(orig['errors']),'categories':dict(collections.Counter(x['category'] for x in rows)),'unique_hashed_contents':len({x['sha256'] for x in rows if x['sha256']})})
defs=[];imports=[]
for row in rows:
 if row['category']!='源码与脚本' or not row['path'].endswith('.py'):continue
 p=R/row['path']
 try:
  tree=ast.parse(p.read_text(encoding='utf-8-sig'))
  for n in ast.walk(tree):
   if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):defs.append({'path':row['path'],'symbol':n.name,'line':n.lineno,'end':n.end_lineno})
   if isinstance(n,ast.Import):imports.append({'path':row['path'],'line':n.lineno,'import':','.join(x.name for x in n.names)})
   if isinstance(n,ast.ImportFrom):imports.append({'path':row['path'],'line':n.lineno,'import':'.'*n.level+(n.module or '')+':'+','.join(x.name for x in n.names)})
 except Exception:pass
save('自写源码符号索引.json',defs);save('源码导入依赖索引.json',imports)
checks=[]
for f in [R/'auth-lifecycle/results/a_ab/final04/source_hashes.json',R/'auth-lifecycle/results/b/final02/source_hashes.json',R/'auth-lifecycle/results/experiments/pilot02/source_hashes.json']:
 data=j(f);base=R/'auth-lifecycle'
 for name,expected in data.items():
  if not isinstance(expected,str) or not re.fullmatch('[0-9a-f]{64}',expected):continue
  p=base/name;actual=h(p) if p.is_file() else None
  checks.append({'manifest':str(f.relative_to(R)),'path':str(p.relative_to(R)),'expected':expected,'actual':actual,'verdict':'MATCH_CURRENT' if actual==expected else 'DIFF_CURRENT_OR_MISSING'})
def scan_hashes(data):
 if isinstance(data,dict):
  if 'path' in data:
   for key in ['sha256','sha','expected']:
    if isinstance(data.get(key),str) and re.fullmatch('[0-9a-f]{64}',data[key]):yield data['path'],data[key];break
  for key,val in data.items():
   if isinstance(val,str) and re.fullmatch('[0-9a-f]{64}',val) and ('/' in key or '\\' in key or '.' in key):yield key,val
   elif isinstance(val,(list,dict)):yield from scan_hashes(val)
 elif isinstance(data,list):
  for x in data:yield from scan_hashes(x)
for f in [C/'results/rank_delivery01/manifest.json',C/'results/source_binding_delivery01/manifest.json',C/'results/structural_delivery01/manifest.json',C/'results/rowspace_delivery01/manifest.json',C/'revisions/structural_audit_2026-11-03_r1/delivery_manifest.json',C/'revisions/novelty_search_2026-11-03_r2/manifest.json',S/'最终验证.json']:
 for name,expected in scan_hashes(j(f)):
  if 'Player-Data' in name or any(x in name.lower() for x in ['secret','key.pem']):continue
  bases=[f.parent,f.parent.parent,C,S,R];p=next((b/name for b in bases if (b/name).is_file()),None)
  actual=h(p) if p else None
  checks.append({'manifest':str(f.relative_to(R)),'path':str(p.relative_to(R)) if p else name,'expected':expected,'actual':actual,'verdict':'MATCH_CURRENT' if actual==expected else 'DIFF_CURRENT_OR_UNRESOLVED'})
save('历史清单逐项重算.json',checks)
save('历史清单重算汇总.json',{'entries':len(checks),'counts':dict(collections.Counter(x['verdict'] for x in checks)),'mismatch_records':[x for x in checks if not x['verdict'].startswith('MATCH')]})
hits=[];nested=[];seen=set()
def az(data,label,depth=0):
 try:
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   for x in z.infolist():
    if re.search('handoff.py|run_v213|run_models.py|run_local_separator|run_balanced_history|CS0[123]|V5.1|schemas/|001_initial.sql',x.filename,re.I):hits.append({'archive':label,'member':x.filename})
    if x.filename.lower().endswith('.zip') and x.file_size<100_000_000 and depth<5:
     b=z.read(x);hh=hashlib.sha256(b).hexdigest();nested.append({'archive':label,'member':x.filename,'sha256':hh})
     if hh not in seen:seen.add(hh);az(b,label+'!'+x.filename,depth+1)
 except Exception as e:nested.append({'archive':label,'error':type(e).__name__})
for row in rows:
 if row['path'].lower().endswith('.zip') and row['category']=='历史压缩包':az((R/row['path']).read_bytes(),row['path'])
save('嵌套压缩包引用检索.json',{'hits':hits,'nested':nested,'scope':'all indexed historical zip archives; embedded ZIP <=100MB, depth<=5; no extraction'})
# Recompute public summaries from raw records. No raw runtime secrets are emitted.
raw={}
runfile=R/'auth-lifecycle/results/experiments/pilot02/runs.jsonl';runs=[json.loads(s) for s in runfile.read_text(encoding='utf-8').splitlines() if s.strip()]
raw['pilot']={'rows':len(runs),'keys':list(runs[0]),'methods':dict(collections.Counter(x.get('method') for x in runs))}
for label,path in [('b384','auth-lifecycle/results/b/final02/finite_results.jsonl'),('b96','auth-lifecycle/results/b/final02/structural.jsonl'),('a48','auth-lifecycle/results/a_ab/final04/finite.jsonl')]:
 rr=[json.loads(s) for s in (R/path).read_text(encoding='utf-8').splitlines() if s.strip()];raw[label]={'rows':len(rr),'keys':list(rr[0])}
raw['prototype']={}
for folder in ['final02','smt02','components02','acquisition_reference02']:
 p=S/'runs'/folder
 if p.exists():raw['prototype'][folder]={'files':len(list(p.glob('*.json'))),'summary':j(p/'summary.json') if (p/'summary.json').exists() else None}
save('原始数据重新计数.json',raw)
print(json.dumps({'inventory':j(W/'索引最终统计.json'),'manifest':dict(collections.Counter(x['verdict'] for x in checks)),'archive_hits':hits,'raw_counts':{k:v.get('rows') for k,v in raw.items() if isinstance(v,dict)},'pilot_keys':raw['pilot']['keys']},ensure_ascii=False,indent=2))
