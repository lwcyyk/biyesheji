"""Final component hashes, repeated regression after list-manifest support."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json
O=Path(__file__).resolve().parent.parent;E=O/'evidence';R=E/'HOST_ATTEMPT_R2'
def module(n,p):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
A=module('final_archive_check',O/'maintenance/archive_check.py');B=module('final_archive_oracle',O/'maintenance/archive_oracle.py')
rows=json.loads((R/'ARCHIVE_HOST_RESULTS.json').read_bytes())['cases'];checks=[]
for r in rows:
 p=R/r['raw_directory']/'input.zip';raw=(p.parent/'manifest.json').read_bytes()
 try:A.verify(p,raw,r['cap'],expected_binding={'batch_id':'HOST-FIXTURE','boot_id':'HOST-FIXTURE'});accepted=True
 except (ValueError,KeyError,OSError,RuntimeError,NotImplementedError):accepted=False
 ref=B.inspect(p,raw,r['cap'],binding={'batch_id':'HOST-FIXTURE','boot_id':'HOST-FIXTURE'})
 assert accepted==r['expected_accept']==(ref['decision']=='ACCEPT')
 checks.append({'case_id':r['case_id'],'accepted':accepted,'reference':ref})
P=O.parent;I=Path(r'D:\毕业设计\DCL-R6-isolated-verification');identity=json.loads((I/'ra01/inputs/batch_identity.json').read_bytes())
observed=[]
for name,p,raw,cap,mn in [('TR-A2_NATIVE',I/'batch14/native_snapshot/out/EVIDENCE.zip',(E/'ACTUAL_NATIVE_MANIFEST.json').read_bytes(),257,'out/EVIDENCE_MANIFEST.json'),
 ('TR-A2_ADMIN',Path(identity['host_control'])/'STARTUP_ADMIN_EVIDENCE.zip',(E/'ACTUAL_ADMIN_MANIFEST.json').read_bytes(),271,'STARTUP_ADMIN_MANIFEST.json')]:
 result=A.verify(p,raw,cap,mn);ref=B.inspect(p,raw,cap,mn)
 assert ref['decision']=='ACCEPT' and result['members']==ref['members']
 observed.append({'name':name,'path':str(p),'subject':result,'oracle':ref,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
mutants=[]
for previous in json.loads((R/'MUTATION_HOST_RESULTS.json').read_bytes())['mutants']:
 disabled=set(previous['disabled'])
 class Remove(ast.NodeTransformer):
  def visit_Raise(self,n):
   if isinstance(n.exc,ast.Call) and n.exc.args and isinstance(n.exc.args[0],ast.Constant) and n.exc.args[0].value in disabled:return ast.Pass()
   return n
 t=ast.fix_missing_locations(Remove().visit(ast.parse((O/'maintenance/archive_check.py').read_text(encoding='utf-8'))));ns={};exec(compile(t,'final_mutant_'+previous['mutant'],'exec'),ns)
 r=next(r for r in rows if r['case_id']==previous['trigger']);p=R/r['raw_directory']/'input.zip';raw=(p.parent/'manifest.json').read_bytes()
 got=ns['verify'](p,raw,r['cap'],expected_binding={'batch_id':'HOST-FIXTURE','boot_id':'HOST-FIXTURE'});ref=B.inspect(p,raw,r['cap'],binding={'batch_id':'HOST-FIXTURE','boot_id':'HOST-FIXTURE'})
 assert got['status']=='ACCEPT_ARCHIVE_ONLY' and ref['decision']=='REJECT'
 mutants.append({'mutant':previous['mutant'],'trigger':r['case_id'],'detected':True,'actual_mutant_result':got,'oracle':ref})
syntax=[]
for p in sorted((O/'maintenance').glob('*.py')):
 raw=p.read_bytes();t=ast.parse(raw.decode('utf-8-sig'),feature_version=(3,12));compile(t,str(p),'exec')
 syntax.append({'relative':str(p.relative_to(O)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'python312_grammar':'PASS','host_compile':'PASS'})
assert len(syntax)==4
# Native entry is AST/compile checked only. Import would require Linux resource.
facts={'archive_fixture_rechecks':checks,'historical_archive_rechecks':observed,'final_archive_mutations':mutants,
 'components':syntax,'MR_native_entry_imports':0,'native_OS_events':0,'runtime_hooks':0,'selected_new_capacity':None}
with(E/'FINAL_COMPONENT_CHECKS.json').open('x',encoding='utf-8') as f:json.dump(facts,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'fixture_rechecks':len(checks),'historical_archives':len(observed),'archive_mutations':len(mutants),'syntax':len(syntax),'native_entry_imports':0}))
