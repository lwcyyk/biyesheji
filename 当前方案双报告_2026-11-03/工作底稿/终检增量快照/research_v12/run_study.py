"""Every run is a fresh four-CPU/8GB worker, parent timeout and immutable inputs.
All variants are development data. Does not use or create confirmation samples.
"""
import bootstrap
import argparse,json,subprocess,sys,time,hashlib,itertools
from pathlib import Path
from generators import joint_cases,b_cases
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--kind',choices=['J','B','all'],default='all');a=ap.parse_args()
    root=bootstrap.ROOT;out=root/a.out;out.mkdir(parents=True,exist_ok=False);(out/'inputs').mkdir();(out/'raw').mkdir()
    registry={'created_before_runs':True,'protocol_sha256':sha(root/'protocol.json'),'source_sha256':{p.name:sha(p) for p in root.glob('*.py')},'jobs':[]}
    for kind,items,methods in [('J',[(n,s) for n,s,_ in joint_cases()],['F'+''.join(map(str,x)) for x in itertools.product([0,1],repeat=3)]+['RJ_FRESH','RJ_MEMO','Z3_INCREMENTAL','GENERIC_REPLAY','GENERIC_ABSTRACTION','OLD_AB2','OLD_A2','OLD_A3']),('B',list(b_cases()),['B4','B2','B3','R_B','GENERIC_BB','Z3_OPTIMIZE','GENERIC_PRESOLVE'])]:
        if a.kind not in [kind,'all']:continue
        for name,spec in items:
            p=out/'inputs'/f'{kind}_{name}.json';p.write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
            for method in methods:registry['jobs'].append({'kind':kind,'case':name,'method':method,'input':p.name,'sha256':sha(p)})
    (out/'registry.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=[]
    for i,job in enumerate(registry['jobs']):
        dest=out/'raw'/f"{job['kind']}_{job['case']}_{job['method']}.json"
        cmd=[sys.executable,'-B',str(root/'worker.py'),'--kind',job['kind'],'--method',job['method'],'--input',str(out/'inputs'/job['input']),'--out',str(dest)]
        start=time.perf_counter()
        try:
            run=subprocess.run(cmd,capture_output=True,timeout=32,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            row=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {'status':'ERROR','stderr':run.stderr.decode('utf-8',errors='replace')}
        except subprocess.TimeoutExpired:row={'status':'TIMEOUT','reason':'32s parent kill including process start; 30s worker shared cycle'}
        elapsed=time.perf_counter()-start
        row.update(case=job['case'],method=job['method'],kind=job['kind'],process_inclusive_seconds=elapsed)
        dest.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');rows.append({k:row.get(k) for k in ['kind','case','method','status','total_seconds','process_inclusive_seconds']})
        if (i+1)%16==0 or row['status']=='ERROR':print(i+1,'/',len(registry['jobs']),job['case'],job['method'],row['status'],flush=True)
    (out/'index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print('finished',len(rows),flush=True)
if __name__=='__main__':main()
