"""Finish guard-deletion checks using already verified host fixtures."""
from pathlib import Path
import ast,copy,importlib.util,json
O=Path(__file__).resolve().parent.parent;E=O/'evidence';R=E/'HOST_ATTEMPT_R2'
def put(n,x):
 with(R/n).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
put('HOST_ITERATION_RECORD.json',{'R1_failure':'MR budget mutation fixture aliased before/after dict; deepcopy retained sharing. Input construction fixed to independent copies.',
 'R2_failure':'Deleting path guard on a backslash fixture still triggered MEMBER_SET because Windows ZIP writer normalized that name. Additional guard correctly rejected it.',
 'correction':'Use the preserved drive-relative path fixture to isolate path guard deletion; no production guard weakened.',
 'administrative_UTF8_collection_errors':1,'native_test_retries':0,'runtime_entries':0,'source_function_repairs':0})
rows=json.loads((R/'ARCHIVE_HOST_RESULTS.json').read_bytes())['cases'];mutants=[]
for name,target,disabled in [('skip_count','legacy_native_258',{'MEMBER_COUNT'}),('skip_hash','negative_wrong_hash',{'CONTENT_HASH'}),
 ('skip_duplicate','negative_duplicate',{'DUPLICATE_MEMBER'}),('skip_path','negative_drive',{'PATH'}),
 ('skip_type','negative_symlink',{'MEMBER_TYPE_OR_COMPRESSION'}),('skip_binding','negative_wrong_binding',{'BINDING'}),
 ('skip_permission','negative_permission',{'MEMBER_PERMISSION'})]:
 class Remove(ast.NodeTransformer):
  def visit_Raise(self,node):
   if isinstance(node.exc,ast.Call) and node.exc.args and isinstance(node.exc.args[0],ast.Constant) and node.exc.args[0].value in disabled:return ast.Pass()
   return node
 tree=ast.fix_missing_locations(Remove().visit(ast.parse((O/'maintenance/archive_check.py').read_text(encoding='utf-8'))));env={};exec(compile(tree,'isolated_mutant_'+name,'exec'),env)
 row=next(r for r in rows if r['case_id']==target);p=R/row['raw_directory']/'input.zip'
 result=env['verify'](p,(p.parent/'manifest.json').read_bytes(),row['cap'],expected_binding={'batch_id':'HOST-FIXTURE','boot_id':'HOST-FIXTURE'})
 assert result['status']=='ACCEPT_ARCHIVE_ONLY' and row['oracle']['decision']=='REJECT'
 mutants.append({'mutant':name,'trigger':target,'disabled':sorted(disabled),'actual_mutant_result':result,'independent_oracle':row['oracle'],'detected':True})
put('MUTATION_HOST_RESULTS.json',{'mutants':mutants,'count':len(mutants),'fixed_PASS_results':0})
mr=json.loads((R/'MR_HOST_RESULTS.json').read_bytes());mrm=[]
for name,target,code in [('ignore_budget','budget_changed','BUDGET'),('ignore_origin','synthetic_origin','ORIGIN'),
 ('ignore_closed','missing_closed','AUTO_STOP'),('false_cleanup','missing_roles_exited','CLEANUP'),
 ('ignore_native_seal','native_failed','NATIVE_SEAL'),('ignore_admin_seal','admin_failed','ADMIN_SEAL'),
 ('accept_unreviewed','unreviewed_accepted','UNREVIEWED'),('ignore_waitpid','waitpid_missing','WAITPID')]:
 class DropRequire(ast.NodeTransformer):
  def visit_Expr(self,n):
   if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='require' and len(n.value.args)==2 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==code:return ast.Pass()
   return self.generic_visit(n)
 t=ast.fix_missing_locations(DropRequire().visit(ast.parse((O/'maintenance/mr_native_oracle.py').read_text(encoding='utf-8'))));env={};exec(compile(t,'isolated_MR_mutant_'+name,'exec'),env)
 fixture=next(r for r in mr['oracle_fixtures'] if r['case_id']==target);result=env['verify'](*copy.deepcopy(fixture['input']))
 assert result['accepted'] and not fixture['result']['accepted']
 mrm.append({'mutant':name,'trigger':target,'disabled_requirement':code,'actual_mutant_result':result,'independent_expected_rejection':fixture['result'],'detected':True})
put('MR_MUTATION_HOST_RESULTS.json',{'mutants':mrm,'count':len(mrm),'native_events':0,'fixed_PASS_results':0})
put('HOST_CHECK_SUMMARY.json',{'archive_cases':len(rows),'actual_archive_function_cases':3,'actual_admin_guard_cases':3,
 'MR_pure_predicates':len(mr['actual_pure_predicates']),'MR_oracle_cases':len(mr['oracle_fixtures']),
 'archive_mutants_detected':len(mutants),'MR_mutants_detected':len(mrm),'runtime_cap_selected':False,
 'capacity_limit_raised':False,'runtime_hooks_integrated':False,'native_runtime_tests':'UNRUN','WSL_calls':0,'T0':None,'R':None})
print(json.dumps({'archive':len(rows),'actual_archive':3,'actual_admin':3,'MR_pure':len(mr['actual_pure_predicates']),
 'MR_oracle':len(mr['oracle_fixtures']),'archive_mutants':len(mutants),'MR_mutants':len(mrm),'runtime':'UNRUN'}))
