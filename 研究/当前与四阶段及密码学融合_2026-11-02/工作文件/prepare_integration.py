from pathlib import Path
import hashlib, json, re, subprocess
from docx import Document

ROOT=Path('D:/毕业设计')
OUT=ROOT/'研究/当前与四阶段及密码学融合_2026-11-02'
WORK=OUT/'工作文件'
PROJECT=ROOT/'auth-lifecycle'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

original=json.loads((OUT/'输入清单.json').read_text(encoding='utf-8'))
rows=[]
for x in original:
 p=Path(x['path']); row=dict(x); row['current_sha256']=sha(p); row['unchanged']=row['current_sha256']==x['sha256']; rows.append(row)
for p in [ROOT/'硕士研究_v2.15_创新性验证与假设驱动研究报告.docx',ROOT/'研究/创新性验证与假设驱动研究_2026-11-02/研究假设与创新性核验登记表.json']:
 rows.append({'path':str(p),'sha256':sha(p),'status':'LOCATED'})
duplicates=[]
for p in (ROOT/'实现四阶段').glob('*.docx'):
 q=ROOT/p.name
 duplicates.append({'authoritative':str(p),'duplicate':str(q),'exists':q.exists(),'identical':q.exists() and sha(p)==sha(q)})
snapshot={}
for folder in ['src','tests','scripts','experiments','results']:
 for p in (PROJECT/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix.lower() in {'.py','.json','.jsonl','.toml','.yaml','.yml','.zip'}:
   snapshot[p.relative_to(PROJECT).as_posix()]=sha(p)
for name in ['README.md','pyproject.toml']:
 snapshot[name]=sha(PROJECT/name)
dump(WORK/'保留基线哈希.json',snapshot)
dump(OUT/'来源与保留核验.json',{'date':'2026-11-02','sources':rows,'duplicates':duplicates,'git_status':'NOT_A_GIT_REPOSITORY','git_commit':None,'snapshot_files':len(snapshot),'snapshot':'工作文件/保留基线哈希.json','scope':'Hashes only; no credential contents exported. Historical results not rerun.'})

extracted=json.loads(next(WORK.glob('阶段一*完整提取.json')).read_text(encoding='utf-8'))
requirements=[]
mapping={
 'G01':('M01 M07','C01 C03 C06','PARTIAL','有限账户/原生范围字段已有；持久账户登记与UI未实现'),
 'G02':('M02','C05 C06','MISSING','真实加密保险库及解锁流程未实现；CCT不能替代存储工程'),
 'G03':('M03 M08 M10','C01 C04','PARTIAL','有限批准语义已有；可信用户入口及事务撤回未集成'),
 'G04':('M04 M08 M10','C02 C04 C05','PARTIAL','有限绑定检查已有；OS身份与生产句柄系统未实现'),
 'G05':('M09 M12','C05 C06 C08','PARTIAL','Keycloak/Casdoor原生校准已有；密码会话与授权码业务路径仍缺'),
 'G06':('M02 M04 M09','C02 C05 C06','PARTIAL','研究运行使用受控客户端；不等价完整秘密隔离或CCT'),
 'G07':('M10','INTERNAL C06','PARTIAL','JSONL实验日志已有；M10唯一写入事务库未实现'),
 'G08':('M03 M08 M10','C01 C04 INTERNAL','PARTIAL','有限撤回和原生故障调查已有；整体原子准入未实现'),
 'G09':('M07 M11 M12','C06 C07 C08','PARTIAL','实验日志/独立评分已有；可信人类审计UI未实现'),
 'G10':('M04 M09','C02 C05','MISSING','两个真实AI任务及跨服务业务验收未完成'),
}
for obj in extracted:
 match=re.match(r'^(G\d{2}|A\d{2}|B\d{2}|N\d{2}|R\d{2})\s',obj['text'])
 if not match and obj['style']=='Table': match=re.search(r'/ (R\d{2}) \|',obj['text'])
 if not match: continue
 rid=match.group(1)
 if rid in {x['id'] for x in requirements}:continue
 if rid in mapping: modules,interfaces,status,note=mapping[rid]
 elif rid.startswith('A'): modules,interfaces,status,note='M05 M07 M08 M09 M10','C03 C04 C05 C06','PARTIAL','A1/B-A有限算法和参考已有；查询驱动原生L1及完整产品集成未验收'
 elif rid.startswith('B'): modules,interfaces,status,note='M06 M08 M09 M10','C03 C04 C05 C06','PARTIAL','B/B-B有限算法与证书已有；真实配置微步骤及连续多次停止未验收'
 elif rid.startswith('N'): modules,interfaces,status,note='M02 M03 M04 M07 M08 M09 M10 M11 M12','C01 C02 C04 C05 C06 C07 C08 INTERNAL','NOT_SYSTEM_ACCEPTED','实验子集有相关工具；不得将局部测试自动映射为此需求通过'
 else: modules,interfaces,status,note='M05 M06 M12','C03 C08','NOT_TESTED_FORMALLY','保留H-S与H-A/H-B/H-AB分别登记；无正式统计支持'
 requirements.append({'id':rid,'source_locator':obj['locator'],'original_text':obj['text'],'modules':modules.split(),'interfaces':interfaces.split(),'status':status,'integration_note':note,'crypto_effect':'OPTIONAL_BACKEND_ONLY; does not discharge native semantics or product acceptance','system_acceptance':'NOT_ACCEPTED'})
expected={f'{g}{i:02}' for g,n in [('G',10),('A',6),('B',7),('N',10),('R',4)] for i in range(1,n+1)}
assert {x['id'] for x in requirements}==expected, expected-{x['id'] for x in requirements}
dump(OUT/'需求与实现映射.json',{'schema':'ab-integration-crosswalk/1','status':'DESIGN_RECONCILIATION_ONLY','source':'实现四阶段/阶段一_需求规格说明书_A+B认证语义与凭据配置_v1.0.docx','requirements':requirements,'count':len(requirements)})
print(json.dumps({'originals_unchanged':all(x.get('unchanged',True) for x in rows),'duplicates':duplicates,'snapshot_files':len(snapshot),'requirements':len(requirements)},ensure_ascii=False,indent=2))
