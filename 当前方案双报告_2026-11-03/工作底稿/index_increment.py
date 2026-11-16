from pathlib import Path
import csv,json,hashlib
R=Path(r'D:\毕业设计');O=R/'当前方案双报告_2026-11-03';W=O/'工作底稿';SN=W/'终检增量快照'
manifest=json.loads((W/'增量快照清单.json').read_text(encoding='utf-8'))
p=O/'资料索引与来源哈希清单.csv';rows=list(csv.DictReader(p.open(encoding='utf-8-sig')));known={r['path'] for r in rows}
for x in manifest['files']:
 if x['path'] in known:continue
 suff=Path(x['path']).suffix.lower();c='源码与脚本' if suff=='.py' else ('研究文档与文献' if suff in ['.md','.pdf','.html','.txt'] else '证据结果或配置')
 rows.append({'path':x['path'],'bytes':x['bytes'],'mtime_ns':x['mtime_ns'],'category':c,'sha256':x['sha256'],'read_scope':'18:03:39增量字节快照；核心报告/理论/函数核读，重复原始行机器核对'})
with p.open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)
checks=[]
for rev in ['multirow_explore_2026-11-03_r3','incidence_structure_2026-11-03_r4']:
 b=SN/'研究/密码学辅助_一致性核验/revisions'/rev;m=json.loads((b/'manifest.json').read_text())
 files=m['files']
 if isinstance(files,dict):records=[{'path':k,'sha256':v} for k,v in files.items()]
 else:records=files
 for x in records:
  name=x['path'];expected=x.get('sha256');p2=b/name
  if not p2.exists():p2=R/'研究/密码学辅助_一致性核验/revisions'/rev/name
  if expected and p2.is_file():actual=hashlib.sha256(p2.read_bytes()).hexdigest();checks.append({'revision':rev,'path':name,'expected':expected,'actual':actual,'match':expected==actual})
(W/'增量来源哈希核对.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
stats={'entries':len(rows),'hashed':sum(bool(x['sha256']) for x in rows),'unique_hashed_contents':len({x['sha256'] for x in rows if x['sha256']}),'increment_entries':len(manifest['files']),'cutoff':'2026-11-03 18:03:39 Asia/Shanghai','hash_records':len(checks),'matched':sum(x['match'] for x in checks)}
(W/'索引最终统计_含增量.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print(stats)

