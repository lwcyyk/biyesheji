from pathlib import Path
import json,hashlib,zipfile,re
from lxml import etree
BASE=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cross=read(BASE/'D01_D15对照.json')
details={
'D01':'新增候选仅在本研究目录实现；不倒填四阶段完整产品已实现。',
'D02':'B2/B3/Z3保持min G及字典序配置；A/AB的Q档单列，不更改H-B。',
'D03':'原B-AB未改；新AB_OFF具有完整联合策略空间，仅缺DRD界。',
'D04':'界内穷尽无解与计算限额分离；新限额检查返回INCONCLUSIVE。',
'D05':'主批空K返回UNKNOWN，未用空集全称真放行。',
'D06':'合法完成必须义务结清；故意义务遗漏被原审计和评分器拒绝。',
'D07':'仍为同一初态的替代停止场景，B3合并不提供连续停止保证。',
'D08':'原B枚举名称保持；本轮确实新增独立Z3编码，不将旧代码重标为SMT。',
'D09':'未改变Keycloak/Casdoor锁，也未新部署Django或两业务站。',
'D10':'仍使用可靠原子configure模型；真实微步骤V-Q/V-R未关闭。',
'D11':'每worker共用30秒周期与资源守卫；检查和下界构造计入，不在子调用重置。',
'D12':'遵从本轮用户W0命名；W0_L0工作负载与数学W下标0区分，未验收完整产品W0。',
'D13':'不实现或宣称CCT明文保护后端。',
'D14':'不借密码学安全中止推导无条件必达。',
'D15':'F1/F2/F3继续分离；合成verified不当原生证据。'}
for x in cross['items']:x['new_candidate_disposition']=details[x['id']]
(BASE/'D01_D15对照.json').write_text(json.dumps(cross,ensure_ascii=False,indent=2),encoding='utf-8')
doc=BASE/'A、B与AB三项算法原创性突破及优势验证研究报告_v1.0.docx'
with zipfile.ZipFile(doc) as z:
 root=etree.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
 text='\n'.join(root.xpath('//w:t/text()',namespaces=ns));equations=len(root.xpath('//m:oMath',namespaces=ns))
old=read(BASE/'baseline.json')['files'];changed=[p for p,h in old.items() if not Path(p).exists() or sha(Path(p))!=h]
checks={'old_files_preserved':not changed,'main_260_pass':read(BASE/'runs/final02/summary.json')['pass'],'replay_260_semantics':read(BASE/'结果分析.json')['semantic_replay']['all_same'],'independent_A_reference':read(BASE/'runs/acquisition_reference01/summary.json')['pass'],'Z3_20':read(BASE/'runs/smt02/summary.json')['pass'],'components_20':read(BASE/'runs/components01/summary.json')['pass'],'second_A_route':read(BASE/'runs/secondary01/summary.json')['pass'],'mechanism_checks':read(BASE/'runs/mechanisms01/summary.json')['pass'],'bound_checks':read(BASE/'最终验证.json')['pass'],'five_native_equations':equations==5,'no_placeholder_citations':'chatgpt-content-reference' not in text,'D01_D15_preserved':len(cross['items'])==15,'no_formal_claim':read(BASE/'protocol.json')['formal_H_A_H_B_H_AB']=='NOT_TESTED'}
manifest={'scope':'finite research prototype / artifact QA only','checks':checks,'pass':all(checks.values()),'docx_sha256':sha(doc),'preserved_files':len(old),'changed_originals':changed,'source_hashes':{str(p.relative_to(BASE)):sha(p) for p in list(BASE.glob('*.py'))+list((BASE/'prototype').glob('*.py'))},'not_completed':['three established novel algorithmic advantages','general machine proof','native V-Q/V-R','full A2 B2/B3 AB integration','formal statistics','full product W0 acceptance'],'post_run_changes':'CLI output-path options and documentation only; exact measured core versions archived per run'}
(BASE/'交付清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
if not manifest['pass']:raise SystemExit(json.dumps(checks))
dest=BASE/'源码规范与原始结果.zip'
selected=['final02','secondary01','components01','smt02','mechanisms01','acquisition_reference01']
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for p in BASE.iterdir():
  if p.is_file() and p.suffix in {'.py','.json','.txt','.docx'}:z.write(p,p.name)
 for p in (BASE/'prototype').glob('*.py'):z.write(p,p.relative_to(BASE).as_posix())
 for name in selected:
  for p in (BASE/'runs'/name).rglob('*'):
   if p.is_file():z.write(p,p.relative_to(BASE).as_posix())
 # Only readonly Python dependency source, never runtime accounts/tokens or services.
 dep=Path('D:/毕业设计/auth-lifecycle/src')
 for p in dep.rglob('*.py'):z.write(p,'readonly_dependency/'+p.relative_to(dep).as_posix())
print(json.dumps({'pass':True,'equations':equations,'protected_files':len(old),'zip_bytes':dest.stat().st_size,'docx_sha256':manifest['docx_sha256']},ensure_ascii=False))
