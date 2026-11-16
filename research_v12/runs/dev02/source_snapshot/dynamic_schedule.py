"""Equal public query-sequence cost comparison; no execution of probing online.
The common model is compiled once per method; root and ALL immediate probe roots
are queried, even when an optimal policy would not probe. Report diagnostic scope.
"""
import bootstrap
import argparse,json,time,subprocess,sys,traceback
from pathlib import Path
from generators import controlled

def worker(name,source,method):
    from resource_guard import install,peak_memory
    guard=install()
    from kernel import Meter,State,Graph
    from independent import exact,Checker
    from auth_lifecycle.a.compiler import compile_model
    from auth_lifecycle.a.audit import check_compilation
    from auth_lifecycle._reference_kernel import expand
    from auth_lifecycle.checker import check_policy
    from joint import solve,session
    m=Meter();c=compile_model(source);m.tick('compiled',c.nodes);assert check_compilation(c.bundle)['verdict']=='ACCEPTED'
    g=Graph(c.bundle,m);queries=[(None,None,g.root)]
    for a in sorted(g.d['actions']):
        if not a.startswith('probe:'):continue
        groups,err=expand(g.d,g.root.knowledge,a)
        if not err and g.root.remaining>0:queries.extend((a,o,State(k,g.root.remaining-1)) for o,k in sorted(groups.items()))
    ctx=session(c.bundle,ab=method in ['SCCP','GENERIC_REPLAY'],meter=m) if method in ['JOINT_BB','INCREMENTAL','SCCP','GENERIC_REPLAY'] else None
    if method=='Z3_INCREMENTAL':
        from smt_joint import Incremental
        z=Incremental(c.bundle,m)
    answers=[]
    for a,o,state in queries:
        t=time.perf_counter()
        if method=='RJ_FRESH':r=exact(c.bundle,state,meter=m,cache=False)
        elif method=='Z3_INCREMENTAL':r=z.solve(state)
        else:
            if method=='JOINT_BB':ctx=session(c.bundle,meter=m)
            receipt=None
            if a and g.root in ctx['oracle'].cache:receipt=(g.root,a,o,ctx['oracle'].cache[g.root])
            r=solve(c.bundle,ab=method in ['SCCP','GENERIC_REPLAY'],context=ctx,root=state,incoming=receipt)
        elapsed=time.perf_counter()-t
        if r['status']=='FEASIBLE':assert check_policy(g.d,r['policy'],knowledge=state.knowledge,horizon=state.remaining).verdict=='ACCEPTED'
        answers.append({'action':a,'observation':o,'root':g.head(state),'status':r['status'],'Q':r.get('value'),'query_seconds':elapsed})
    return {'case':name,'method':method,'answers':answers,'total_seconds':m.elapsed(),'counts':dict(m.counts),'guards':guard,'memory':peak_memory(),'scope':'same diagnostic root + immediate probe successor sequence, all points public'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--input');ap.add_argument('--method');ap.add_argument('--case');a=ap.parse_args()
    if a.input:
        try:res=worker(a.case,json.loads(Path(a.input).read_text(encoding='utf-8')),a.method)
        except Exception:res={'status':'ERROR','traceback':traceback.format_exc()}
        Path(a.out).write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8');return
    out=bootstrap.ROOT/a.out;out.mkdir(parents=True,exist_ok=False);rows=[]
    for name,s,_ in controlled():
        inp=out/(name+'_input.json');inp.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
        baseline=None
        for method in ['RJ_FRESH','JOINT_BB','INCREMENTAL','Z3_INCREMENTAL','SCCP','GENERIC_REPLAY']:
            dest=out/(name+'_'+method+'.json');cmd=[sys.executable,'-B',__file__,'--input',str(inp),'--out',str(dest),'--case',name,'--method',method]
            try:
                sub=subprocess.run(cmd,capture_output=True,timeout=32,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));r=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {'status':'ERROR','stderr':str(sub.stderr)}
            except subprocess.TimeoutExpired:r={'status':'TIMEOUT'};dest.write_text(json.dumps(r),encoding='utf-8')
            values=[(x['status'],x['Q']) for x in r.get('answers',[])]
            if method=='RJ_FRESH':baseline=values
            rows.append({'case':name,'method':method,'pass':bool(values) and values==baseline,'seconds':r.get('total_seconds'),'counts':r.get('counts',{}),'query_count':len(values)})
        print(name,flush=True)
    res={'rows':rows,'pass':all(x['pass'] for x in rows),'scope':'12 families, same full joint roots; no native requests'}
    (out/'summary.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8');print('dynamic',res['pass'])
if __name__=='__main__':main()
