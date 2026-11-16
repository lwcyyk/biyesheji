from pathlib import Path
import sys,json,importlib.util,hashlib,collections,math
from fractions import Fraction
sys.dont_write_bytecode=True
R=Path(r'D:\毕业设计');O=R/'当前方案双报告_2026-11-03';W=O/'工作底稿';SN=W/'终检增量快照'
def loadmod(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(W/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
r3=SN/'研究/密码学辅助_一致性核验/revisions/multirow_explore_2026-11-03_r3'
r4=SN/'研究/密码学辅助_一致性核验/revisions/incidence_structure_2026-11-03_r4'
c3=loadmod('audit_r3',r3/'check_representation_cert.py');c4=loadmod('audit_r4',r4/'check_analytic.py')
proofs=[]
for p in sorted((r3/'results/representation_cert01').glob('certificate_*.json')):
 proofs.append({'path':str(p.relative_to(SN)),'result':c3.check(j(p))})
reps=j(r4/'results/classify02/summary.json')['class_representatives']
expect={tuple(sorted(tuple(sorted(tuple(e) for e in t)) for t in rr['concurrent_perfect_matchings'])) for rr in reps}
allm=tuple(sorted(c4.matchings(tuple(range(6)),3)))
for folder in ['analytic01','gf16_exact01']:
 for p in sorted((r4/'results'/folder).glob('q*.json')):
  cert=j(p);proofs.append({'path':str(p.relative_to(SN)),'result':c4.check(cert,{(),allm} if cert['q']==16 else expect)})
save('增量密码学证书独立重核.json',{'scope':'仅公开精确LP证书；不执行MPC，不证明一般归约或优先权','checks':proofs,'pass':all(x['result']['status']=='VERIFIED' for x in proofs)})
v=SN/'research_v12';counts={}
for folder in ['dev01','dev02']:
 if not (v/'runs'/folder/'registry.json').exists():
  counts[folder]={'status':'NOT_IN_FROZEN_INCREMENT_SNAPSHOT'};continue
 rows=[j(p) for p in (v/'runs'/folder/'raw').glob('*.json')];registry=j(v/'runs'/folder/'registry.json')
 by=collections.defaultdict(dict)
 for x in rows:by[(x['kind'],x['case'])][x['method']]=x
 pairs=[];mismatches=[]
 def value(r):
  if r['status']!='FEASIBLE':return None
  ans=r.get('result',{})
  return ans.get('value') if r['kind']=='J' else (ans.get('metrics',{}).get('G'),ans.get('configuration',ans.get('delivery',{}).get('configuration')))
 for k,m in by.items():
  ref=m.get('RJ_MEMO' if k[0]=='J' else 'R_B')
  if ref:
   for method,x in m.items():
    if method in ['OLD_A2','OLD_A3']:continue
    if x['status'] in ['TIMEOUT','INCONCLUSIVE','ERROR'] or ref['status'] in ['TIMEOUT','INCONCLUSIVE','ERROR']:continue
    if x['status']!=ref['status'] or value(x)!=value(ref):mismatches.append({'case':k,'method':method,'actual':value(x),'reference':value(ref)})
 for left,right in [('F001','F000'),('F100','F000'),('F010','F000'),('F111','F000'),('F001','GENERIC_REPLAY'),('B4','GENERIC_PRESOLVE'),('B4','B2')]:
  common=[m for m in by.values() if left in m and right in m]
  if common:
   pairs.append({'left':left,'right':right,'N':len(common),'same_status_value':sum(m[left]['status']==m[right]['status'] and value(m[left])==value(m[right]) for m in common),'time_sum_ratio':sum(m[left].get('total_seconds',30) for m in common)/sum(m[right].get('total_seconds',30) for m in common)})
 counts[folder]={'raw_rows':len(rows),'registered_jobs':len(registry['jobs']),'cases':len(by),'statuses':dict(collections.Counter(x['status'] for x in rows)),'methods':dict(collections.Counter(x['method'] for x in rows)),'decisive_mismatches':mismatches,'pairs':pairs}
save('增量v12原始行重核.json',counts)
# Adversarial certificate scope audit using original compiler/reference only.
# Frozen independent.py imports bootstrap; register a no-op bootstrap and explicit read-only paths.
import types
sys.modules['bootstrap']=types.ModuleType('bootstrap')
sys.path.insert(0,str(R/'auth-lifecycle/src'))
from auth_lifecycle.a import compiler,joint_reference
from auth_lifecycle.schema import prepare,refs_json,digest
check=loadmod('audit_v12_independent',v/'independent.py')
source=j(R/'auth-lifecycle/examples/a_ab/simple_acquisition.json')
compiled=compiler.compile_model(source);bundle=compiled.bundle
_,root=prepare(bundle['l0']);joint=joint_reference.solve(bundle)
cert={'schema':'SCCP/1','model_digest':digest(bundle['l0']),'root':{'belief':refs_json(root.knowledge),'remaining':root.remaining},'scope':'control_only_bounded_completion','objective':'total_Q','constraint_refs':['account','approval','budgets','native_effects','all_observations','strict_obligations','remaining_steps','version'],'status':'FEASIBLE','policy':joint.policy,'value':joint.worst_requests}
actual=check.Checker(bundle).check_certificate(cert,root)
only=check.exact(bundle,scope='control')
result={'profile':'simple_acquisition','source_sha256':hashlib.sha256((v/'independent.py').read_bytes()).hexdigest(),'certificate_scope':cert['scope'],'root_action':joint.policy.get('action'),'joint_status':joint.status,'joint_Q':joint.worst_requests,'exact_control_status':only['status'],'checker_verdict':actual,'finding':'scope未强制在可行证书的全部策略节点排除probe；此测试针对公开检查合同，不是主线实际越权或原生漏洞','certificate':cert}
save('新增AB3证书scope反例.json',result)
print(json.dumps({'crypto':[x['result'] for x in proofs],'v12':counts,'scope_counterexample':{k:val for k,val in result.items() if k!='certificate'}},ensure_ascii=False,indent=2))

