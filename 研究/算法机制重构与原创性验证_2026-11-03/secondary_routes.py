"""Predeclared second A route probes and negative controls; no winner filtering."""
from pathlib import Path
import sys,json,subprocess,hashlib
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE/'prototype'))
import common
from auth_lifecycle.a import fixtures as af
def main(out=None):
 out=Path(out) if out else BASE/'runs/secondary01';out.mkdir(parents=True,exist_ok=False)
 s=af.acquisition(nuisance=2,horizon=3);s['probes'].pop('a_scope')
 cases=[('duplicate_semantics',s),('no_quotient_gain',af.acquisition(horizon=3)),('side_effect_extension',af.side_effect())]
 registry={'version':'A3-route-probes/1','created_before_runs':True,'cases':[x[0] for x in cases],'methods':['A_QUOTIENT','GENERIC_QUOTIENT','A2','ACQUIRE_DP'],'status':'DEVELOPMENT','third_case':'H4 extension, not W0','code_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'prototype').glob('*.py')}}
 (out/'registry.json').write_text(json.dumps(registry,indent=2),encoding='utf-8');rows=[]
 for name,s in cases:
  path=out/(name+'_input.json');path.write_text(json.dumps(s),encoding='utf-8')
  for method in registry['methods']:
   dest=out/(name+'_'+method+'.json')
   r=subprocess.run([sys.executable,str(BASE/'prototype/worker.py'),'--kind','A','--input',str(path),'--out',str(dest),'--method',method],capture_output=True,text=True,timeout=32,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
   data=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {'status':'ERROR','stderr':r.stderr}
   rows.append({'case':name,'method':method,'status':data['status'],'Q':data.get('evaluation',{}).get('external_requests'),'U':data.get('evaluation',{}).get('completion'),'work':data.get('meter'),'seconds':data.get('total_wall_seconds')});print(rows[-1]['case'],method,data['status'],flush=True)
 (out/'summary.json').write_text(json.dumps({'rows':rows,'pass':all(x['status']=='FEASIBLE' and x['U']==1 for x in rows) and all(len({x['Q'] for x in rows if x['case']==n})==1 for n,_ in cases)},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out');args=ap.parse_args();main(args.out)
