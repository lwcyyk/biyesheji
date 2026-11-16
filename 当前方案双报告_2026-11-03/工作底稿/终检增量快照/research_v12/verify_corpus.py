"""Independent transfer/refutation audit across every immediate public successor.
Saves concrete inputs, proofs and expected/actual answers; not a timing benchmark.
"""
import bootstrap
import json,time,argparse
from copy import deepcopy
from generators import joint_cases
from kernel import Graph,Meter,control_solve,State
from independent import Checker,exact
from auth_lifecycle.a.compiler import compile_model
from auth_lifecycle.checker import check_policy
from auth_lifecycle.schema import prepare

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
    dest=bootstrap.ROOT/a.out;dest.mkdir(parents=True,exist_ok=False);rows=[];assertions=0
    start=time.perf_counter()
    for name,src,_ in joint_cases():
        comp=compile_model(src);assert comp.status=='COMPILED';g=Graph(comp.bundle,Meter(seconds=30));ck=Checker(comp.bundle,g.meter)
        if not g.root.knowledge:continue
        core=control_solve(g,g.root);assert ck.check_certificate(core,g.root)[0]=='VALID';assertions+=1
        item={'case':name,'input':src,'parent_certificate':core,'transitions':[]}
        for a,cs in g.edges(g.root).items():
            for o,c in cs.items():
                tr=ck.transfer(core,g.root,a,o,c,bound=core.get('value'))
                fresh=exact(comp.bundle,c,scope='control')
                if tr['verdict']=='VALID':
                    x=tr['certificate'];assert x['status']==fresh['status'];assertions+=1
                    if x['status']=='FEASIBLE':
                        assert x['value']>=fresh['value'];assertions+=1
                        assert check_policy(comp.bundle['l0'],x['policy'],knowledge=c.knowledge,horizon=c.remaining).verdict=='ACCEPTED';assertions+=1
                # A bad cost is not an admissible old witness claim.
                forged=deepcopy(core)
                if forged['status']=='FEASIBLE':
                    forged['value']=-1;assert ck.check_certificate(forged,g.root)[0]=='INVALID';assertions+=1
                item['transitions'].append({'action':a,'observation':o,'post':g.head(c),'transfer':tr,'fresh_control_reference':fresh})
        (dest/(name+'.json')).write_text(json.dumps(item,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
        rows.append({'case':name,'transitions':len(item['transitions']),'valid':sum(t['transfer']['verdict']=='VALID' for t in item['transitions']),'invalid':sum(t['transfer']['verdict']=='INVALID' for t in item['transitions']),'inconclusive':sum(t['transfer']['verdict']=='INCONCLUSIVE' for t in item['transitions'])})
    summary={'pass':True,'assertions':assertions,'rows':rows,'seconds':time.perf_counter()-start,'false_reuse_in_checked_corpus':0,'scope':'all immediate successors of 21 nonempty declared roots; not all possible bounded auth models'}
    (dest/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(summary['pass'],assertions,sum(r['transitions'] for r in rows))
if __name__=='__main__':main()
