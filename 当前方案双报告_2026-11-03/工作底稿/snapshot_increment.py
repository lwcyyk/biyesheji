from pathlib import Path
import json,csv,hashlib,shutil,datetime,os
R=Path(r'D:\毕业设计');O=R/'当前方案双报告_2026-11-03';W=O/'工作底稿'
scan=json.loads((O/'核验附件/终检新增资料扫描.json').read_text(encoding='utf-8'))
S=W/'终检增量快照';S.mkdir(exist_ok=True)
rows=[];unstable=[]
for name in scan['new_paths']:
 p=R/name
 if not p.is_file():continue
 before=p.stat();b=p.read_bytes();after=p.stat()
 if before.st_mtime_ns!=after.st_mtime_ns:unstable.append(name)
 target=S/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
 rows.append({'path':name,'bytes':len(b),'mtime_ns':after.st_mtime_ns,'sha256':hashlib.sha256(b).hexdigest(),'snapshot':str(target.relative_to(O))})
record={'captured_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'封装前发现894项新增资料的只读字节快照；后续结论以此快照为准','files':rows,'unstable_during_copy':unstable}
(W/'增量快照清单.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(rows),sum(x['bytes'] for x in rows),record['captured_at_utc'],unstable)

