from pathlib import Path
import json,hashlib,zipfile
from lxml import etree
BASE=Path(__file__).resolve().parent
SRC=Path('D:/毕业设计/研究/算法机制重构与原创性验证_2026-11-03/A、B与AB三项算法原创性突破及优势验证研究报告_v1.0.docx')
DOC=BASE/'A、B与AB三项算法研究报告_v1.1_密码学机制融合版.docx'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=read(BASE/'保留基线.json')['files'];changed=[p for p,h in baseline.items() if not Path(p).exists() or sha(Path(p))!=h]
expected=read(BASE/'working/source_package.json')
with zipfile.ZipFile(DOC) as z:
 changed_parts=[n for n in z.namelist() if expected.get(n)!=hashlib.sha256(z.read(n)).hexdigest()]
 removed_parts=sorted(set(expected)-set(z.namelist()))
 root=etree.fromstring(z.read('word/document.xml'))
with zipfile.ZipFile(SRC) as z:original=etree.fromstring(z.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
before=list(original.find('w:body',ns))[:-1];after=list(root.find('w:body',ns))
prefix_changes=[]
for i,(a,b) in enumerate(zip(before,after)):
 if etree.tostring(a,method='c14n')!=etree.tostring(b,method='c14n'):prefix_changes.append(i)
diffs=read(BASE/'修改说明.json')['edits'];allowed_before={x['before'] for x in diffs}
prefix_ok=len(prefix_changes)==len(diffs) and all(''.join(before[i].itertext()) for i in prefix_changes)
# Confirm the three changed XML blocks are the intended original text slots.
def paragraph_text(el):
 parts=[]
 for n in el.iter():
  if n.tag=='{'+ns['w']+'}t':parts.append(n.text or '')
  elif n.tag=='{'+ns['w']+'}br':parts.append('\n')
 return ''.join(parts)
prefix_ok &= {paragraph_text(before[i]) for i in prefix_changes}==allowed_before
replay=[]
for name in ['summary.json','provenance.json','support_range.json','public_certificates.json']:
 replay.append({'file':name,'identical':(BASE/'checks/run02'/name).read_bytes()==(BASE/'checks/run03'/name).read_bytes()})
equations=len(root.xpath('//m:oMath',namespaces=ns))
checks={'source_files_unchanged':not changed,'integration_assertions':read(BASE/'checks/run03/summary.json')['pass'],'old_MPC_output_recheck':read(BASE/'checks/mpc_logs_rechecked.json')['pass'],'deterministic_replay':all(x['identical'] for x in replay),'preserve_only_parts_unchanged':not removed_parts and set(changed_parts)<={'word/document.xml','word/_rels/document.xml.rels','docProps/core.xml'},'only_three_original_paragraphs_edited':bool(prefix_ok),'nine_native_equations':equations==9,'diagnostic_interface_non_authorizing':read(BASE/'PublicDiagnosticEvidence_接口增补.json')['authorizes_execution'] is False,'formal_hypotheses_not_promoted':read(BASE/'最新研究进展登记.json')['original_H_A_H_B_H_AB']=='NOT_TESTED'}
result={'scope':'DOCUMENT_AND_EVIDENCE_INTEGRATION_ONLY','pass':all(checks.values()),'checks':checks,'protected_files':len(baseline),'changed_original_files':changed,'changed_docx_parts':changed_parts,'original_body_block_changes':prefix_changes,'replay':replay,'docx_sha256':sha(DOC),'source_docx_sha256':sha(SRC),'MPC_new_execution':False,'runtime_integration':'NOT_IMPLEMENTED','source_script_hashes':{p.name:sha(p) for p in BASE.glob('*.py')}}
(BASE/'交付核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
if not result['pass']:raise SystemExit(json.dumps(result,ensure_ascii=False))
dest=BASE/'融合规范与核验附件.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for p in BASE.iterdir():
  if p.is_file() and p.suffix in {'.docx','.json','.py','.txt'}:z.write(p,p.name)
 for sub in ['checks/run02','checks/run03','checks']:
  for p in (BASE/sub).glob('*.json'):
   if sub=='checks' and p.name!='mpc_logs_rechecked.json':continue
   z.write(p,p.relative_to(BASE).as_posix())
print(json.dumps({'pass':True,'protected_files':len(baseline),'native_equations':equations,'original_paragraph_changes':len(prefix_changes),'zip_bytes':dest.stat().st_size,'docx_sha256':result['docx_sha256']},ensure_ascii=False))
