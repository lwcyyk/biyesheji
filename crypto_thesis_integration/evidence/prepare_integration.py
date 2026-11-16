"""Read-only source/version lock and bounded manuscript/source discovery."""
from pathlib import Path
import hashlib,json,subprocess,zipfile,xml.etree.ElementTree as ET
B=Path(r'D:\毕业设计');O=B/'crypto_thesis_integration';C=B/'crypto_fi_adopted_release_v3_1'
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
manifest=load(C/'MANIFEST.json');z=dict(manifest);expected=z.pop('payload_sha256')
assert hashlib.sha256(json.dumps(z,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()==expected
for x in manifest['files']:assert rec(Path(x['path']))==x,x['path']
assert manifest['adoption_verdict']=='PASS_WITHIN_STATED_SCOPE' and manifest['status']=='ADOPTED_V3_1_AND_ARCHIVED'
rel={
 'NAV':'research_main_innovation/decentralized_credential_lifecycle/README.md',
 'NAV_VERDICT':'research_main_innovation/decentralized_credential_lifecycle/CURRENT_VERDICT.md',
 'B05':'research_main_innovation/decentralized_credential_lifecycle/DCL-R6-batch05/BATCH05_FINAL_DECISION.md',
 'B05_CAUSE':'research_main_innovation/decentralized_credential_lifecycle/DCL-R6-batch05/BATCH05_COUNTEREXAMPLES.md',
 'G1_R01':'research_g1_lifecycle_contract/2026-11-09_r01/08_G1_VERDICT_AND_MAINLINE_HANDOFF.md',
 'G1_ARCH':'research_g1_lifecycle_contract/2026-11-09_r01/01_ACTUAL_ARCHITECTURE_AUDIT.md',
 'G1_CATALOG':'research_g1_lifecycle_contract/2026-11-09_r01/02_FULL_LIFECYCLE_CONTRACT_MAP.md',
 'G1_API':'research_g1_lifecycle_contract/2026-11-09_r01/05_AB_RUNTIME_INTERFACE_SPEC.md',
 'G1_R02':'research_g1_lifecycle_contract/2026-11-09_r02/09_G1_R02_VERDICT.md',
 'G1_R03':'research_g1_lifecycle_contract/2026-11-10_r03/08_G1_R03_VERDICT_AND_G2_HANDOFF.md',
 'DCL_R4':'research_main_innovation/decentralized_credential_lifecycle/DCL-R4/R4_THESIS_CONTRIBUTION_BOUNDARY.md',
 'DCL_R5':'research_main_innovation/decentralized_credential_lifecycle/DCL-R5/R5_RESEARCH_AND_THESIS_DECISION.md',
 'SYS_20261109':'research_main_innovation/decentralized_credential_lifecycle/CURRENT_STATE_AUDIT.md',
 'G2_R05':'research_g2_dsat_review/2026-11-10_r05/08_G2_R05_VERDICT_AND_IMPLEMENTATION_GATE.md',
 'G2_R16':'research_g2_dsat_implementation/2026-11-11_r16/06_FINAL_VERDICT_AND_NEXT_STEP.md',
 'G2_R17':'research_g2_dsat_implementation/2026-11-11_r17/05_FINAL_VERDICT_AND_AUTHORIZATION_REQUEST.md',
 'THESIS_SCOPE':'thesis_draft/TASK_SCOPE.md','THESIS_MAP':'thesis_draft/THESIS_MAP.md',
 'THESIS_DELIVERY':'thesis_draft/DELIVERY_CHECK.json',
 'R3_MR':'research_recipe_r3/VERDICT.md',
 'CORE_20261106':'mainline_research_closure_v1/THESIS_CORE_DRAFT.md',
 'MAP_20261106':'mainline_research_closure_v1/THESIS_UPDATE_MAP.md',
 'STATUS_20261106':'mainline_research_closure_v1/FINAL_STATUS.json',
 'ALGO_RUNTIME':'mainline_research_closure_v1/ALGORITHM_RUNTIME_MAP.md',
 'CURRENT_STORAGE':'auth-lifecycle/src/auth_lifecycle/online_state/storage.py',
 'CURRENT_DEPS':'auth-lifecycle/pyproject.toml',
 'CF_FINAL':'crypto_fi_final_internal_review/FINAL_INTERNAL_DECISION.md',
 'CF_PROVENANCE':'crypto_fi_final_internal_review/REVIEW_PROVENANCE.json'
}
paths={p.resolve() for p in C.rglob('*') if p.is_file()}
registry={key:rec(B/path) for key,path in rel.items()};paths.update(Path(r['path']) for r in registry.values())
for p in (B/'thesis_draft/chapters').glob('*.md'):paths.add(p.resolve());registry['OLD_'+p.stem]=rec(p)
pattern='Frodo|frodo|Ord_n|Tensor_D|FrodoPKE|updatable|可更新加密|来源隐藏|FI构造'
roots=[str(B/'auth-lifecycle/src'),str(B/'auth-lifecycle/docs'),str(B/'auth-lifecycle/pyproject.toml')]
r=subprocess.run(['rg','-n',pattern,*roots],capture_output=True,text=True,encoding='utf-8')
assert r.returncode in [0,1],r.stderr
fl=subprocess.run(['rg','--files',*roots],capture_output=True,text=True,encoding='utf-8');assert fl.returncode==0
searchfiles=[Path(s) for s in fl.stdout.splitlines() if s];paths.update(p.resolve() for p in searchfiles)
dump(O/'evidence/BOUNDED_UE_SOURCE_SEARCH.json',dict(command=['rg','-n',pattern,*roots],exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr,searched_inventory=[rec(p) for p in searchfiles],interpretation='Bounded literal discovery only;zero matches does not prove absence of aliased or other-deployment implementations. Combined selected storage/API evidence supports UE/FI integration not established in the reviewed system chain.',runtime_modules_imported_or_executed=0))
candidates=[]
for name in ['面向AI智能体的认证语义感知与可撤销凭据管理_调研报告_写作重构版_2026-11-09.docx','面向AI智能体的认证语义感知与可撤销凭据管理_调研报告_第四章更新版_2026-11-09.docx']:
 p=B/name;paths.add(p.resolve())
 with zipfile.ZipFile(p) as z:
  doc=ET.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};paras=[];heads=[]
  for item in doc.findall('.//w:body/w:p',ns):
   text=''.join(n.text or '' for n in item.findall('.//w:t',ns));style=item.find('w:pPr/w:pStyle',ns);style=style.get('{'+ns['w']+'}val','') if style is not None else ''
   if text:paras.append(text)
   if text and 'Heading' in style:heads.append(dict(style=style,text=text))
 candidates.append(dict(file=rec(p),first8=paras[:8],heading_first22=heads[:22],read_scope='Title/front matter and styles for authority discovery only;not complete report reading',authority='NO_CURRENT_THESIS_MASTER_CONFIRMATION_LOCATED'))
dump(O/'evidence/MASTER_DISCOVERY.json',dict(historical_confirmed_skeleton=registry['THESIS_MAP'],historical_scope=registry['THESIS_SCOPE'],historical_date='2026-11-04',historical_title='面向AI代理的认证语义安全识别与可撤销性驱动凭据配置方法研究',historical_chapters=7,later_patch=registry['MAP_20261106'],current_research_topic='面向用户与AI智能体的全生命周期密码与凭据管理系统',current_topic_basis=[registry['G1_R01'],registry['DCL_R4']],docx_candidates=candidates,current_whole_master_status='CURRENT_MASTER_UNCONFIRMED',decision_basis='Confirmed old skeleton and later chapter patches coexist with newer broad-topic research handoffs;no inspected handoff uniquely designates a whole current thesis master. Filesystem names/mtime alone do not supply that authority.',pending_fields=['authoritative_master_path','version_or_commit','authoritative_master_sha256','confirmed_outline_version','registered_thesis_title','final_crypto_chapter_number','global_bibliography_mapping','abstract_location','author_or_supervisor_confirmation_reference']))
dump(O/'evidence/SOURCE_REGISTRY.json',dict(sources=registry,adopted_release_manifest=rec(C/'MANIFEST.json'),adopted_manifest_payload_sha256=expected,adopted_manifest_files_verified=len(manifest['files']),adopted_profile_selector=rec(C/'certificates/UNIFIED_RESULT_SELECTORS.json'),scope_note='Versioned source/decision records and selected current source/negative-search inventory;no new system,protocol or cryptographic experiment. Original research proof/status scopes inherited.'))
dump(O/'evidence/INPUT_SNAPSHOT.json',dict(files=[rec(p) for p in sorted(paths)],scope='Adopted release,actually used navigation/handoffs/historical chapter baseline,source-discovery inventory andtwo report candidates;hashing distinct from semantic reading'))
print(json.dumps(dict(adopted_payload_files_verified=len(manifest['files']),source_ids=len(registry),locked_input_files=len(paths),UE_literal_matches=bool(r.stdout),current_master='CURRENT_MASTER_UNCONFIRMED'),ensure_ascii=False))
