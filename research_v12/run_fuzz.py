"""Additional seeded structural diagnostics, fixed generation before runs.
Not a held-out confirmation set: algorithm and family rules are still development.
"""
import bootstrap
import json,sys,subprocess,argparse,hashlib
from copy import deepcopy
from random import Random
from auth_lifecycle.b.fixtures import structural_models
def inputs():
    rng=Random(471209)
    for i,(name,m) in enumerate(structural_models(24,seed=471209)):
        m['horizon']=min(m['horizon'],3)
        # Vary duplicate classes while preserving all originals, prices and scopes.
        for p in list(sorted(m['paths'])):
            if rng.randrange(3)==0 and len(m['paths'])<12:
                m['paths']['z_alias_'+p]=deepcopy(m['paths'][p])
        yield f'generated_{i:02d}',m
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();out=bootstrap.ROOT/a.out
    out.mkdir(parents=True,exist_ok=False);(out/'inputs').mkdir();(out/'raw').mkdir()
    jobs=[]
    for name,m in inputs():
        p=out/'inputs'/('B_'+name+'.json');p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
        for method in ['B4','B2','B3','R_B','GENERIC_BB','Z3_OPTIMIZE','GENERIC_PRESOLVE']:jobs.append((name,p,method))
    reg={'seed':471209,'development_only':True,'cases':24,'jobs':len(jobs),'before_runs':True,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/'registry.json').write_text(json.dumps(reg,indent=2),encoding='utf-8');rows=[]
    for i,(name,p,method) in enumerate(jobs):
        dest=out/'raw'/f'B_{name}_{method}.json';cmd=[sys.executable,'-B',str(bootstrap.ROOT/'worker.py'),'--kind','B','--method',method,'--input',str(p),'--out',str(dest)]
        import time
        t=time.perf_counter()
        try:
            run=subprocess.run(cmd,capture_output=True,timeout=32,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));r=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {'status':'ERROR','stderr':str(run.stderr)}
        except subprocess.TimeoutExpired:r={'status':'TIMEOUT'}
        r.update(case=name,kind='B',method=method,process_inclusive_seconds=time.perf_counter()-t);dest.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');rows.append({k:r[k] for k in ['case','method','status']})
        if (i+1)%28==0:print(i+1,len(jobs),flush=True)
    (out/'index.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
from pathlib import Path
if __name__=='__main__':main()
