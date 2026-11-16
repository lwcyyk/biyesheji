"""Second-pass research arithmetic/contract checks, not a DCL test runner."""
from INPUT_AUDIT import ROOT,PREV,OUT,E,RUNTIME,read,save,sha
import ast,json,re
from pathlib import Path

h=read(E/'H_FULL_SCOPE_PROOF.json')
assert [x['count'] for x in h['roles']]==[2,13,1,1,1,1,14,3]
assert sum(x['count'] for x in h['roles'])==36
assert sum(x['count']*x['halts_per_context'] for x in h['roles'])==52
assert h['core_attempt_max']==212
g=ast.parse((RUNTIME/'src/guard.py').read_text(encoding='utf-8-sig'))
rc=ast.parse((RUNTIME/'src/range_core.py').read_text(encoding='utf-8-sig'))
def fn(tree,name):return next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
def first_try(f):return min(n.lineno for n in f.body if isinstance(n,ast.Try))
def early_call(f,name):
    return min(n.lineno for n in ast.walk(f) if isinstance(n,ast.Call) and
      (n.func.id if isinstance(n.func,ast.Name) else n.func.attr if isinstance(n.func,ast.Attribute) else '')==name)
frontiers=[]
for tree,name,gate in [(g,'_reserve','budget_health'),(g,'visit','execution_deadline'),(rc,'reserve','valid'),(rc,'claim','valid')]:
    f=fn(tree,name);a=early_call(f,gate);b=first_try(f);assert a<b
    frontiers.append({'function':name,'gate':gate,'gate_line':a,'try_line':b})
reason=read(E/'REASON_AND_VARIABLE_DECISION.json')
assert reason['R_MR']['ASCII_content_max']==len('COORDINATOR_CHILD_RETURN_')+11==36
assert reason['R_MR']['token_max']==38 and reason['R_MR']['root_marker_bytes_max']==144+(36+12+2)==194
formula=read(E/'CLOSE_CORE_REDUCED_FORMULA.json')
assert formula['constant_bytes']==16*(194+25092+260+237+194+998+997)+23*(194+1151)+2*1223+52*144==488421
assert formula['coefficients']=={'T':16*23,'B':16*3,'E':23,'sumV':23,'R_budget':52}
u=read(E/'CURRENT_CAPACITY_UNSAT_WITNESSES.json')
for kind,paths,delta,cap in [('native',u['native']['raw_witness_paths'],1,257),('admin',u['admin']['raw_witness_paths'],2,256)]:
    n=len(paths);assert n==len(set(paths)) and n+delta==cap+1 and n-1+delta==cap
    assert all(s.startswith('out/c09_tests/') or s.startswith('inputs/root_private/ipc_case_') for s in paths)
gap=read(E/'RESIDUAL_15_GAP_MATRIX.json')['rows'];assert [x['gap_id'] for x in gap]==[f'G{i:02d}' for i in range(1,16)]
allowed={'PROVED_IN_FROZEN_SCOPE','CONDITIONAL_ON_EXISTING_TCB','COUNTEREXAMPLE_IN_FROZEN_SCOPE','REQUIRES_NEW_CONTRACT','OUTSIDE_FROZEN_SCOPE','UNRESOLVED_WITH_EXACT_REASON'}
fields=['gap_id','producer','source','unresolved_variable','input_domain','occurrence_bound','byte_bound','trusted_assumption','existing_evidence','counterexample','minimum_constraint','verdict']
assert all(set(fields)<=set(x) and x['verdict']in allowed for x in gap)
a=read(OUT/'proposals/OPTION_A_KEEP_CURRENT.json');b=read(OUT/'proposals/OPTION_B_MINIMAL_REVISION.json')
for d in [a,b]:
    for f in ['approved','user_approved','effective','runtime_enabled']:assert d[f]is False
assert a['status']=='CURRENT_CONTRACT_UNSAT' and b['status']=='CONTRACT_REVISION_REQUIRED'
assert len(b['parameters'])==13
pfields=['producer_source','input_family','derivation','overflow','safety_effect','candidate_files','negative_tests','effective_prerequisites']
assert all(set(pfields)<=set(x) for x in b['parameters'])
assert [(x['parameter_id'],x['value'])for x in b['parameters']if x['value']is not None]==[('MAIN_OBSERVATIONS',256),('MAIN_ROWS',263),('MAIN_BYTES',345148)]
assert read(E/'MR_RULE_RECHECK.json')['numbered_rules']==14
bind=read(E/'DECISION_BINDINGS.json')
for v in bind.values():assert sha(v['path'])==v['sha256']
req=['RESIDUAL_15_GAP_MATRIX.md','VARIABLE_R_T_B_E_V_BOUND_AUDIT.md','H_EVENT_BOUND_ANALYSIS.md','OTHER_PRODUCER_BYTE_BOUND.md',
 'CLOSE_RESERVE_FINAL_BOUND.md','FULL_EVIDENCE_BYTE_AND_WORK_BOUND.md','WALL_TIME_ASSUMPTIONS.md',
 'CURRENT_CONTRACT_UNSAT_PROOF.md','MINIMAL_CONTRACT_REVISION.md','GENERAL_BASELINE_AND_SEPARATION.md',
 'APPROVAL_DECISION_PACKAGE.md','NEXT_STAGE_AUTHORIZATION_REQUEST.md','FINAL_DECISION.md']
assert all((OUT/n).is_file()for n in req)
assert [x['number']for x in read(E/'FINAL_TWENTY_ANSWERS.json')['answers']]==list(range(1,21))
links=0;errors=[]
for p in OUT.glob('*.md'):
    s=p.read_text(encoding='utf-8');assert '不是'not in s,p.name
    for t in re.findall(r'\]\(([^)]+)\)',s):
        links+=1;q=re.sub(r':\d+$','',t.strip('<>'))
        if not Path(q).exists()and q!=str(E/'DELIVERY_CHECK.json').replace('\\','/'):errors.append({'file':p.name,'target':q})
assert not errors,errors
save('SECOND_PASS_DECISION_REVIEW.json',{'status':'PASS_RESEARCH_ARTIFACTS_ONLY','provenance':'same active agent; separate arithmetic/frontier/manifest/contract checks, no independent native checker claim',
 'frontier_checks':frontiers,'H_max':52,'core_attempts':212,'MR_reason_token':38,'MR_marker':194,'core_constant':488421,
 'native_minimal_members':258,'admin_minimal_export':257,'reports':13,'answers':20,'gaps':15,
 'parameters':13,'non_null_parameters':3,'null_parameters':10,'links_checked':links,'link_errors':errors,
 'retained_scope_caveats':['MUS is for accepted complete evidence, not process-start reachability','P5 targets a slice-to-admin-bound inference, not an observed byte overrun',
 'stderr_m/E_n not promoted to frozen native vulnerabilities','H bound does not broadcast HALTED','Rbudget/T/E/V remain quantitative-profile dependent',
 '5 and30 are component envelopes, not total native/host sealing WCET','same-scope audit closed; no contract activated'],
 'runtime_imports':0,'DCL_dynamic_tests':0,'source_edits':0})
print({'review':'PASS_RESEARCH_ONLY','H':52,'core':212,'UNSAT_native':258,'UNSAT_admin':257,'gaps':15,'links':links})
