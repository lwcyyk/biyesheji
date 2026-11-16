"""AB3 prerequisite gate. Run before A4/B4 development measurements."""
import bootstrap
import json,time,hashlib
from copy import deepcopy
from kernel import Graph,Meter,State,control_solve
from independent import Checker,exact
from joint import solve
from generators import controlled
from smt_joint import Incremental
from auth_lifecycle.a.compiler import compile_model
from auth_lifecycle.a.audit import check_compilation
from auth_lifecycle.checker import check_policy

def run():
    rows=[];attacks=[];assertions=0
    for name,source,expected in controlled():
        c=compile_model(source);assert c.status=='COMPILED',(name,c.reason)
        assert check_compilation(c.bundle)['verdict']=='ACCEPTED';assertions+=2
        m=Meter();g=Graph(c.bundle,m);checker=Checker(c.bundle,m)
        ref=exact(c.bundle,meter=m);assert ref['status']==expected,(name,ref,expected);assertions+=1
        smt=Incremental(c.bundle,m).solve();assert (smt['status'],smt['value'])==(ref['status'],ref['value']);assertions+=1
        for flag in [False,True]:
            ans=solve(c.bundle,ab=flag,meter=Meter())
            assert (ans['status'],ans.get('value'))==(ref['status'],ref['value']),(name,flag,ans,ref);assertions+=1
        row={'case':name,'expected':expected,'actual':ref['status'],'Q':ref['value'],'source':source,'compiled_states':c.nodes,'transfers':[]}
        if not g.root.knowledge:rows.append(row);continue
        cert=control_solve(g,g.root);assert checker.check_certificate(cert,g.root)[0]=='VALID';assertions+=1
        for a,cs in g.edges(g.root).items():
            if not a.startswith('probe:'):continue
            for o,child in cs.items():
                fresh=exact(c.bundle,child,scope='control',meter=m)
                tr=checker.transfer(cert,g.root,a,o,child,bound=cert.get('value'))
                if tr['verdict']=='VALID':
                    cc=tr['certificate'];assert checker.check_certificate(cc,child)[0]=='VALID';assertions+=1
                    assert cc['status']==fresh['status'];assertions+=1
                    if cc['status']=='FEASIBLE':assert cc['value']>=fresh['value'];assertions+=1
                row['transfers'].append({'action':a,'observation':o,'verdict':tr['verdict'],'reason':tr['reason'],'fresh_status':fresh['status'],'bound_verdict':tr.get('bound_verdict'),'successors':len(child.knowledge)})
                forged=deepcopy(cert);forged['model_digest']='stale'
                attack=checker.transfer(forged,g.root,a,o,child)
                assert attack['verdict']=='INVALID';assertions+=1
                attacks.append({'case':name,'attack':'stale version','verdict':attack['verdict']})
                if len(child.knowledge)>1:
                    dropped=State(frozenset([sorted(child.knowledge)[0]]),child.remaining)
                    attack=checker.transfer(cert,g.root,a,o,dropped)
                    assert attack['verdict']=='INVALID';assertions+=1
                    attacks.append({'case':name,'attack':'drop same-observation successor','verdict':attack['verdict']})
        rows.append(row)
    # Every pair of P1,P2,P3 has a plan but the triple has none.
    from generators import source
    s=source();c=compile_model(s);g=Graph(c.bundle,Meter());refs=sorted(g.root.knowledge)
    from itertools import combinations
    for pair in combinations(refs,2):assert exact(c.bundle,State(frozenset(pair),3),scope='control')['status']=='FEASIBLE';assertions+=1
    assert exact(c.bundle,scope='control')['status']=='IMPOSSIBLE_IN_MODEL';assertions+=1
    # Mislabeling control-only proof as all-strategy impossibility is rejected.
    cert=control_solve(g,g.root);cert['scope']='joint';assert Checker(c.bundle).check_certificate(cert,g.root)[0]=='INVALID';assertions+=1
    return {'gate':'AB3_MINIMUM','pass':True,'assertions':assertions,'rows':rows,'attacks':attacks,'scope':'12 declared synthetic source models; finite H=3; no general/native guarantee'}

if __name__=='__main__':
    dest=bootstrap.ROOT/'runs/ab3_gate01';dest.mkdir(parents=True,exist_ok=False)
    try:r=run()
    except Exception:
        import traceback
        (dest/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
    (dest/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print('AB3 gate:',r['pass'],'assertions:',r['assertions'])
