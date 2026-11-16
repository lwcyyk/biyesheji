import bootstrap
import json
from copy import deepcopy
from itertools import combinations
from kernel import Graph,Meter,State,control_solve
from independent import Checker,exact
from generators import alias_model,joint_cases,source
from b4 import solve as b4,partition,expand,check_compression
from auth_lifecycle.b.reference import solve as rb
from auth_lifecycle.a.compiler import compile_model
from auth_lifecycle.schema import digest
from a4 import Cells
from joint import solve

def run():
    rows=[];n=0
    for tasks,aliases in [(1,3),(2,3),(3,3),(4,2)]:
        for charged in [0,1]:
            m=alias_model(tasks,aliases,cost=charged);cand=b4(m);ref=rb(m)
            assert cand['status']==ref.status;n+=1
            if ref.status=='FEASIBLE':assert (cand['metrics']['G'],cand['configuration'])==(ref.metrics['G'],ref.configuration);n+=1
            assert check_compression(m,cand['certificate']);n+=1
            classes=partition(m,Meter());names=sorted(m['paths'])
            # Enumerate every concrete configuration; check lexical quotient theorem.
            buckets={}
            for mask in range(1<<len(names)):
                C=[p for i,p in enumerate(names) if mask&(1<<i)]
                key=tuple(i for i,group in enumerate(classes) if set(group)&set(C))
                if key not in buckets or C<buckets[key]:buckets[key]=C
            for key,expected in buckets.items():assert expand(classes,key)==expected;n+=1
            attack=deepcopy(cand['certificate']);attack['model_digest']='wrong';assert not check_compression(m,attack);n+=1
            if len(classes)>1:
                attack=deepcopy(cand['certificate']);attack['classes']=[sum(classes,[])];attack.pop('selected_classes',None)
                assert not check_compression(m,attack);n+=1
            rows.append({'case':f't{tasks}-aliases{aliases}-cost{charged}','status':cand['status'],'G':cand.get('metrics',{}).get('G'),'p':len(names),'k':len(classes),'all_masks':1<<len(names)})
    # Explicit lexical counterexample to naive local tie-breaking.
    assert expand([['a','b'],['c']],[0,1])==['a','b','c'];n+=1
    assert ['a','b','c']<['a','c'];n+=1
    # Changed approval/delegate price must prevent an otherwise tempting merge.
    m=alias_model(1,3);m['paths']['p1_0']['delegate']['approval']='issue'
    assert len(partition(m,Meter()))==2;n+=1
    m=alias_model(1,3);m['paths']['p1_0']['delegate']['requests']=1
    assert len(partition(m,Meter()))==2;n+=1
    # Value abstraction positive + rejected merge.
    s=next(s for name,s,_ in joint_cases() if name=='A4_irrelevant_future');bundle=compile_model(s).bundle
    g=Graph(bundle,Meter());ck=Checker(bundle,g.meter);children=g.edges(g.root)['probe:bootstrap'];left=children['left'];right=children['right']
    res=exact(bundle,left);cells=Cells(g,ck);cells.add(left,res['value'],res['policy']);hit=cells.find(right)
    assert hit and hit[0]==exact(bundle,right)['value'];n+=1
    from a_ab_search import continuation_signature
    assert continuation_signature(g,next(iter(left.knowledge)),left.remaining,{})!=continuation_signature(g,next(iter(right.knowledge)),right.remaining,{});n+=1
    candidate=solve(bundle,a4=True);ref=exact(bundle);assert candidate['value']==ref['value'];n+=1
    assert candidate['stats'].get('abstraction_hits',0)>0;n+=1
    rows.append({'case':'A4_weaker_than_future_trace','hits':candidate['stats'].get('abstraction_hits'),'Q':candidate['value']})
    s=source((('a',),('b',)));bundle=compile_model(s).bundle;g=Graph(bundle,Meter());ck=Checker(bundle);refs=sorted(g.root.knowledge)
    left=State(frozenset([refs[0]]),3);right=State(frozenset([refs[1]]),3);r=exact(bundle,left)
    cells=Cells(g,ck);cells.add(left,r['value'],r['policy']);assert cells.find(right) is None;n+=1
    assert cells.log[-1]['status']=='REFINED';n+=1
    rows.append({'case':'A4_different_required_configuration','refinement':cells.log})
    # Lower bound must be recomputed; a feasible cheaper witness rejects forged old bound.
    s=source((('a',),('a',)));from auth_lifecycle.a.fixtures import probe
    probe(s,'q',{w:w for w in s['worlds']});bundle=compile_model(s).bundle;g=Graph(bundle,Meter());ck=Checker(bundle)
    core=control_solve(g,g.root);o,c=next(iter(g.edges(g.root)['probe:q'].items()))
    tr=ck.transfer(core,g.root,'probe:q',o,c,bound=999);assert tr['bound_verdict']=='INVALID';n+=1
    return {'pass':True,'assertions':n,'rows':rows,'scope':'finite quotient/lexical tests plus declared value abstraction cases'}
if __name__=='__main__':
    gate=json.loads((bootstrap.ROOT/'runs/ab3_gate01/result.json').read_text(encoding='utf-8'));assert gate['pass']
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='runs/structure_gate01');args=ap.parse_args()
    out=bootstrap.ROOT/args.out;out.mkdir(parents=True,exist_ok=False)
    try:res=run()
    except Exception:
        import traceback
        (out/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
    (out/'result.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8');print('structure gate',res['pass'],res['assertions'])
