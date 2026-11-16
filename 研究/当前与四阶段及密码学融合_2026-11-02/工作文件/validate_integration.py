from pathlib import Path
import json, hashlib, zipfile, re
from lxml import etree

BASE=Path(__file__).resolve().parents[1]
PROJECT=Path('D:/毕业设计/auth-lifecycle')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
req=read(BASE/'需求与实现映射.json')
expected={f'{g}{i:02}' for g,n in [('G',10),('A',6),('B',7),('N',10),('R',4)] for i in range(1,n+1)}
checks['37_requirement_ids']=len(req['requirements'])==37 and {x['id'] for x in req['requirements']}==expected
checks['no_product_acceptance_inferred']=all(x['system_acceptance']=='NOT_ACCEPTED' for x in req['requirements'])
reg=read(BASE/'融合决策与研究登记.json')
checks['15_decisions']=len(reg['decisions'])==15
checks['12_modules']=len(reg['modules'])==12
checks['5_crypto_amendments']=len(reg['crypto_requirements'])==5
contracts=read(BASE/'密码学接口与计划测试增补.json')
checks['14_tests_remain_planned']=len(contracts['tests'])==14 and all(x['execution_status']=='PLANNED_NOT_RUN' and x['actual'] is None for x in contracts['tests'])
checks['interfaces_not_claimed_executable']=contracts['format']=='DESIGN_FIELD_CATALOG_NOT_EXECUTABLE_SCHEMA' and not contracts['implements_crypto']
checks['crypto_properties_unproven']=all(x['status']=='NOT_PROVEN' for x in reg['proof_obligations'])
checks['formal_hypotheses_unclaimed']=all(reg['primary_hypotheses'][x]=='NOT_TESTED_FORMALLY' for x in ['H-A','H-B','H-AB'])
checks['no_runtime_change_declared']=not reg['original_algorithms_modified'] and not reg['formal_experiments_started']
changed=[]
baseline=read(BASE/'工作文件/保留基线哈希.json')
for rel,digest in baseline.items():
 p=PROJECT/rel
 if not p.exists() or sha(p)!=digest:changed.append(rel)
checks['preserved_baseline_hashes']=not changed
sources=read(BASE/'来源与保留核验.json')['sources']
checks['preserved_original_documents']=all(Path(x['path']).exists() and sha(Path(x['path']))==x['sha256'] for x in sources)
docpath=BASE/'认证语义与凭据配置_四阶段及密码学融合总稿_v1.0.docx'
with zipfile.ZipFile(docpath) as z:
 xml=etree.fromstring(z.read('word/document.xml'))
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
 text='\n'.join(xml.xpath('//w:t/text()',namespaces=ns))
 math=xml.xpath('//m:oMath',namespaces=ns)
 checks['native_equations']=len(math)==7
 checks['no_chat_citation_placeholders']='chatgpt-content-reference' not in text
 checks['no_raw_latex']=not re.search(r'\\(?:begin|frac|operatorname|Sigma|mathsf)',text)
 checks['bibliography_ids']={f'R{i:02}' for i in range(1,10)}<={s['id'] for s in reg['sources']}
result={'scope':'DESIGN_ARTIFACT_STATIC_VALIDATION_ONLY','checks':checks,'passed':all(checks.values()),'changed_baseline_files':changed,'baseline_files_checked':len(baseline),'docx_sha256':sha(docpath),'native_equation_count':len(math),'not_run':['A/B algorithm regression (runtime code unchanged)','new native authentication experiment','CCT implementation or cryptographic security proof','formal H-A/H-B/H-AB test'],'warning':'Static consistency and unchanged hashes are not algorithm correctness, novelty, security, or statistical evidence.'}
(BASE/'静态核验结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(0 if result['passed'] else 1)
