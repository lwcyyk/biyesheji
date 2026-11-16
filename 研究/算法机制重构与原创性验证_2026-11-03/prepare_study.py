from pathlib import Path
import json,hashlib,sys
from docx import Document
BASE=Path(__file__).resolve().parent;ROOT=Path('D:/毕业设计');P=ROOT/'auth-lifecycle'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
if (BASE/'protocol.json').exists():raise SystemExit('Existing study: never silently overwrite protocol or baseline')
files={}
for sub in ['src','tests','scripts','docs','examples','experiments','results']:
 for p in (P/sub).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:files[str(p)]=sha(p)
docs=list((ROOT/'实现四阶段').glob('*.docx'))+[ROOT/'研究/主线研究论证深化_2026-11-03/认证语义与凭据配置_主线研究论证深化_v1.0.docx',ROOT/'研究/当前与四阶段及密码学融合_2026-11-02/认证语义与凭据配置_四阶段及密码学融合总稿_v1.0.docx']
passport=[]
for p in docs:
 files[str(p)]=sha(p);d=Document(p);text='\n'.join([x.text for x in d.paragraphs]+[' | '.join(c.text for c in row.cells) for t in d.tables for row in t.rows])
 dump(BASE/'working'/(p.stem+'.json'),{'path':str(p),'sha256':sha(p),'text':text,'math_note':'OMML retained in original DOCX; earlier ordered math extraction remains authoritative'})
 passport.append({'path':str(p),'sha256':sha(p),'review_scope':'full prior authored report and current text check' if '研究论证' in p.name or '融合总稿' in p.name else ('full requirements' if p.name.startswith('阶段一') else 'targeted workflows/modules/algorithm/constraints; not a line-by-line SQL appendix audit')})
dump(BASE/'baseline.json',{'files':files,'git_commit':None,'scope':'read-only project excluding runtime/pycache and specified DOCX'})
dump(BASE/'material_passport.json',{'materials':passport,'missing':['DD independent schemas/sql/traceability source attachments not in specified four-stage folder','CS03 historical source attachments remain unlocated'],'human_read_attestation':False})
decisions=json.loads((ROOT/'研究/当前与四阶段及密码学融合_2026-11-02/融合决策与研究登记.json').read_text(encoding='utf-8'))['decisions']
dump(BASE/'D01_D15对照.json',{'rule':'original documents immutable; draft reconciliations not silently promoted to approved specification','items':[dict(x,new_candidate_disposition='preserved; optional algorithm revisions are separate study versions') for x in decisions]})
dump(BASE/'protocol.json',{'version':'mechanism-reconstruction-dev/0.1','created_before_first_run':True,'status':'DEVELOPMENT_NOT_PREREGISTRATION','formal_H_A_H_B_H_AB':'NOT_TESTED','targets':{'A2':'complete legal Q with fixed B catalog/early-commit rule; compare property heuristic AND generic exact BB/DP','B2':'fixed min G; computational cost and valid lower/upper bounds','AB2':'same A search/B catalog/joint policy class, only DRD certificate bound switch; runtime/work primary in this new exploratory profile'},'metrics':['U','refusal','UNKNOWN','INCONCLUSIVE','TIMEOUT','C_Q full failure penalty','G','lower_bound','gap','wall_seconds_including_compile_audit_solve_check','cpu_seconds','peak_working_set','work_counts'],'W0':{'logical_cpu_affinity':4,'per_worker_memory_GiB':8,'tasks_max':4,'semantic_worlds_max':8,'probes_max':8,'horizon_max':3,'cycle_seconds':30,'scope':'offline model worker; not full product W0 admission/service/model deployment acceptance'},'extension':'H4/H5 cases recorded separately, cannot replace W0','statistical_thresholds':None,'family_rules':'all generated variants retained, no winner selection','comparison_fairness':'same source, identity projection/all future dependencies, same shield and generic optimistic bound/caches; B generic BB receives same native necessary cuts; R-J independent reference retained','not_run':['native endpoints','real AI','confirmation statistics','new CCT']})
print('Protected files',len(files))
