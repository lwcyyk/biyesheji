from pathlib import Path
import json,hashlib,zipfile,re
from lxml import etree
BASE=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={};baseline=read(BASE/'baseline_hashes.json')['files']
changed=[p for p,h in baseline.items() if not Path(p).exists() or sha(Path(p))!=h]
checks['originals_unchanged']=not changed
s=read(BASE/'runs/final02/summary.json');r=read(BASE/'runs/replay02/replay.json')
checks['offline_checks']=s['pass'];checks['59_deterministic_files_replay']=r['pass'] and len(r['files'])==59
claims=read(BASE/'贡献与证据登记表.json')['claims'];sources=read(BASE/'文献核验表.json')['sources']
checks['12_claims_and_sources']=len(claims)==len(sources)==12
checks['source_locations_present']=all(x['line'] is not None and Path(x['path']).exists() and sha(Path(x['path']))==x['sha256'] for c in claims for x in c['code'])
checks['no_formal_support']=claims[-1]['status']=='NOT_TESTED_FORMALLY'
doc=BASE/'认证语义与凭据配置_主线研究论证深化_v1.0.docx'
with zipfile.ZipFile(doc) as z:
 root=etree.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
 equations=len(root.xpath('//m:oMath',namespaces=ns));text='\n'.join(root.xpath('//w:t/text()',namespaces=ns))
checks['six_native_equations']=equations==6
checks['no_placeholder_citations']='chatgpt-content-reference' not in text
checks['all_citations_registered']=set(re.findall(r'\[(L\d+)\]',text))<=set(x['id'] for x in sources)
negative=read(BASE/'runs/final02/boundaries.json')['omitted_obligation_negative']
checks['negative_control_rejected']=negative['audit']['verdict']=='REJECTED' and negative['scorer']['unresolved_obligations']>0
data={'scope':'ARTIFACT_AND_OFFLINE_EVIDENCE_VALIDATION','checks':checks,'passed':all(checks.values()),'preserved_files':len(baseline),'changed_files':changed,'docx_sha256':sha(doc),'algorithm_tests_scope':'22 A inputs x5 methods, 4 B inputs x4 methods, finite algebra and boundary diagnostics; not general proof','not_run':['native HTTP','real AI agents','formal hypotheses','machine checked general proof','CCT'],'files':{p.name:sha(p) for p in BASE.iterdir() if p.is_file() and p.name!='交付核验.json'}}
(BASE/'交付核验.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checks':checks,'passed':data['passed'],'preserved_files':len(baseline),'docx_sha256':data['docx_sha256']},ensure_ascii=False,indent=2))
raise SystemExit(0 if data['passed'] else 1)
