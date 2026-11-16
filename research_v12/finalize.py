"""Evidence ledger/manifest; never modifies historical sources or run payloads."""
import bootstrap
import json,hashlib,platform,sys,zipfile,importlib.metadata as im,ast
from pathlib import Path
R=bootstrap.ROOT
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    a=read('runs/dev02/analysis.json');f=read('runs/fuzz01/analysis.json');d=read('runs/dynamic01/summary.json');re=read('runs/replay_report.json')
    assert a['all_decisive_reference_checks_pass'] and f['all_decisive_reference_checks_pass'] and d['pass'] and re['pass']
    env={'python':sys.version,'platform':platform.platform(),'processor':platform.processor(),'runtime_path':sys.executable,'algorithm_dependencies':{'z3-solver':im.version('z3-solver')},'document_dependencies':{}}
    for package in ['python-docx','pypdf','pypdfium2']:
        try:env['document_dependencies'][package]=im.version(package)
        except im.PackageNotFoundError:env['document_dependencies'][package]='UNKNOWN'
    write('requirements-lock.json',env)
    source={}
    for p in sorted(R.glob('*.py')):
        tree=ast.parse(p.read_text(encoding='utf-8'));source[p.name]={'sha256':sha(p),'symbols':[{'name':n.name,'line':n.lineno} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef))]}
    write('SOURCE_MANIFEST.json',source)
    inherited=json.loads((bootstrap.OLD/'来源记录.json').read_text(encoding='utf-8'))
    write('literature/inherited_verification.json',{'source_path':str(bootstrap.OLD/'来源记录.json'),'source_sha256':sha(bootstrap.OLD/'来源记录.json'),'read_status':'INHERITED_NO_NEW_FULL_READ','records':inherited})
    papers=[
      {'id':'V12-L01','title':'The Value Equivalence Principle for Model-Based Reinforcement Learning','year':2020,'url':'https://arxiv.org/abs/2011.03506','doi':'10.48550/arXiv.2011.03506','read_scope':'abstract; sections 1-3 and proposition statements; not appendix proof audit','file':'value_equivalence_pdf.pdf','status':'SELECTED_FULLTEXT_READ'},
      {'id':'V12-L02','title':'Multi-Cost-Bounded Reachability Analysis of POMDPs','year':2025,'url':'https://proceedings.mlr.press/v286/bork25a.html','doi':None,'read_scope':'official metadata; fulltext introduction and beginning of related work','file':'multi_cost_pdf.pdf','status':'SELECTED_FULLTEXT_READ','metadata_conflict':'official volume 286; PDF first-page footer says 244; use official page'},
      {'id':'V12-L03','title':'Near Optimal Bayesian Active Learning for Decision Making','year':2014,'url':'https://proceedings.mlr.press/v33/javdani14.html','doi':None,'read_scope':'official metadata; fulltext sections 1-2','file':'drd_pdf.pdf','status':'SELECTED_FULLTEXT_READ'},
      {'id':'V12-L04','title':'Solving logic-based benders decomposition master problems with constraint programming and domain-independent dynamic programming','year':2025,'doi':'10.1007/s10601-025-09382-1','url':'https://link.springer.com/article/10.1007/s10601-025-09382-1','read_scope':'publisher abstract, metadata, data availability, references only','file':'lbbd2025.html','status':'ABSTRACT_ONLY'},
      {'id':'V12-L05','title':'Basic Commands — Z3 Guide','year':None,'url':'https://microsoft.github.io/z3guide/docs/logic/basiccommands/','read_scope':'commands and Using Scopes','file':'incremental_z3.html','status':'OFFICIAL_DOCUMENTATION_READ'},
      {'id':'V12-L06','title':'Transition dominance in domain-independent dynamic programming','year':2025,'url':None,'doi':None,'read_scope':'secondary title/author/year from publisher bibliography only','status':'FULLTEXT_UNAVAILABLE'},
      {'id':'EXCLUDED','file':'lumping.html','status':'WRONG_ARTICLE_EXCLUDED','actual_title':'MEST: Accurate and Fast Memory-Economic Sparse Training Framework on the Edge'}]
    for p in papers:
        if p.get('file') and (R/'literature'/p['file']).exists():p['sha256']=sha(R/'literature'/p['file'])
    write('literature/verification.json',{'checked_on':'2026-11-03','records':papers,'web_tool':'two transport failures; direct primary-URL retrieval used','novelty_status':'NOT_ESTABLISHED'})
    claims=[
      {'id':'AB3-WUL','type':['implementation','conditional_manual_proposition'],'claim':'full-Post witness/refutation replay and independently recomputed admissible bound','source':['oracle.py:FullB.solve','independent.py:Checker.transfer','kernel.py:control_solve'],'evidence':['runs/ab3_gate02/result.json','runs/transfer_corpus01/summary.json','runs/dynamic01/summary.json'],'conditions':['trusted finite model and complete source mapping','nonempty K','immutable model binding','all branches replayed'],'counterexamples':['S1_conflict_disappears','S3_obligation_invalidates_witness','lost_multiple_successors'],'novelty':'generic proof replay equivalent','speed':'not established beyond generic incremental'},
      {'id':'A4-V','type':['implementation','conditional_manual_proposition'],'claim':'weaker than future-trace equality: common union policy + equal member bound + equal safe eligibility','source':['a4.py:Cells.find'],'evidence':['runs/structure_gate02/result.json','runs/dev02/analysis.json'],'conditions':['same task/context','valid member lower bounds','complete union replay'],'counterexample':'different required configurations or obligations','novelty':'generic certificate abstraction equivalent','speed':'no supported overall net gain'},
      {'id':'B4-QLEX','type':['implementation','conditional_manual_proposition','development_measurement'],'claim':'semantic alias quotient reduces 2^p to 2^k; global lexical expansion preserves original (G,configuration)','source':['b4.py:partition','b4.py:expand','b4.py:check_compression'],'evidence':['runs/structure_gate02/result.json','runs/dev02/analysis.json','runs/fuzz01/analysis.json'],'conditions':['identical task/grants/environment/delegate','zero delegate requests and approvals','partitioned native effects'],'counterexamples':['nonzero delegation charges','approval difference','local lexical choice [a]+[c] loses to [a,b,c]'],'novelty':'same generic presolve equivalent','speed':'net gain in rich alias parameter families; no universal gain'},
      {'id':'B4-INTERFACE','type':['proposal','diagnostic'],'claim':'shared-interface diagnostic only','source':['b4.py:interfaces'],'status':'PARTIAL_NONZERO_INTERFACE_DP_NOT_IMPLEMENTED'},
      {'id':'NATIVE','status':'PENDING','missing':['real service model evidence','concurrent native traces','non-atomic configuration','recovery','full W0 product acceptance']},
      {'id':'CRYPTO','status':'INHERITED_NO_NEW_RUN','claim':'retain all v1.1 sections 13-19 and pause MPC expansion','entry':'../研究/主线与密码学机制融合_2026-11-03','conditions':['trusted structure source','original success domain','same leakage/recipients','end-to-end benefit']}]
    write('claims_ledger.json',{'version':'v1.2','claims':claims,'independent_peer_review':False})
    write('hypothesis_ledger.json',{'H-S':{'status':'CONDITIONAL_MODEL_ARGUMENT_AND_FINITE_TESTS','general_proof':False},'H-A':{'status':'NOT_TESTED','suggested_ratio':.80,'completion_difference':-.05,'preregistered':False},'H-B':{'status':'NOT_TESTED','suggested_ratio':.80,'completion_difference':-.05,'preregistered':False},'H-AB':{'status':'NOT_TESTED','suggested_ratio':.85,'completion_difference':-.05,'preregistered':False},'H-M':{'status':'PENDING_SECONDARY'},'H-D':{'status':'PENDING_OPTIONAL'},'new_runtime_metrics':'development mechanism efficiency only; do not replace original CQ/CG hypotheses'})
    files={str(p.relative_to(R)).replace('\\','/'):sha(p) for p in sorted(R.rglob('*')) if p.is_file() and p.name not in ['DELIVERY.json','research_v12_delivery.zip'] and 'qa' not in p.relative_to(R).parts}
    delivery={'version':'v1.2','report':'A、B与AB结构性算法深化及动态核心传递验证研究报告_v1.2.docx','main_runs':2*688,'additional_structural_runs':168,'dynamic_method_batches':72,'assertions_latest_gates':123+920+86,'legacy_unit_tests':34,'old_files':read('historical_verification.json'),'sha256':files,'uncompleted':['nonzero-interface B4 decomposition','minimal symbolic conflict-core extraction/preimage solver','native L1/W0 full acceptance','general proof/priority proof','formal confirmation experiments'],'source_edit_scope':'only research_v12; old bytes checked except declared unreadable runtime database'}
    write('DELIVERY.json',delivery)
    delivery['manifest_scope']='local research_v12; includes reading resources omitted from the portable archive'
    delivery['archive_exclusions']=['qa/ internal render intermediates','literature/*.pdf, *.html, *.txt primary-source reading copies; verification metadata retained']
    delivery['joint_B_limitation']='complete native B outputs currently guide order only; full uniform control search still repeated; joint objective is Q, not lex G then Q'
    delivery['certificate_cost_diagnostic']='runs/certificate_cost01/result.json'
    write('DELIVERY.json',delivery)
    with zipfile.ZipFile(R/'research_v12_delivery.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(R.rglob('*')):
            if not p.is_file() or p.name=='research_v12_delivery.zip':continue
            rel=p.relative_to(R)
            if 'qa' in rel.parts:continue
            # Raw articles are local reading resources, not needed to reproduce code.
            if rel.parts[0]=='literature' and p.suffix in ['.pdf','.html','.txt']:continue
            z.write(p,str(rel))
    print('delivery files',len(files),'archive bytes',(R/'research_v12_delivery.zip').stat().st_size)
if __name__=='__main__':main()
