from pathlib import Path
import sys,json,subprocess,hashlib,time
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE/'prototype'))
from common import Meter
from resource_guard import install,peak_memory
from b_components import solve
def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--input');ap.add_argument('--out');args=ap.parse_args()
 if args.input:
  guard=install();meter=Meter();m=json.loads(Path(args.input).read_text(encoding='utf-8'))
  try:r=solve(m,meter)
  except Exception as e:r={'status':'ERROR','reason':str(e)}
  r.update(seconds=meter.elapsed(),cpu_seconds=time.process_time()-meter.cpu_start,guards=guard,memory=peak_memory());Path(args.out).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');return
 out=Path(args.out) if args.out else BASE/'runs/components01';out.mkdir(parents=True,exist_ok=False);files=sorted((BASE/'runs/final02/inputs').glob('B_*.json'))
 (out/'registry.json').write_text(json.dumps({'version':'B3-independent-component-route/1','created_before_runs':True,'inputs':[p.name for p in files],'objective':'same min G and lexical configuration','profile':'all same original B inputs; exact coupling fallback','code_sha256':hashlib.sha256((BASE/'prototype/b_components.py').read_bytes()).hexdigest()}))
 rows=[]
 for p in files:
  dest=out/p.name
  try:
   rr=subprocess.run([sys.executable,__file__,'--input',str(p),'--out',str(dest)],capture_output=True,text=True,timeout=32,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));r=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {'status':'ERROR','reason':rr.stderr}
  except subprocess.TimeoutExpired:r={'status':'TIMEOUT'};dest.write_text(json.dumps(r))
  ref=json.loads((BASE/'runs/final02/raw'/(p.stem+'_R-B.json')).read_text(encoding='utf-8'));good=r['status']==ref['status']
  if r['status']=='FEASIBLE':good &= r['configuration']==ref['result']['configuration'] and r['metrics']['G']==ref['result']['metrics']['G']
  rows.append({'case':p.stem,'status':r['status'],'G':r.get('metrics',{}).get('G'),'seconds':r.get('seconds'),'decomposition':r.get('decomposition'),'pass':bool(good)});print(rows[-1],flush=True)
 (out/'summary.json').write_text(json.dumps({'rows':rows,'pass':all(r['pass'] for r in rows)},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
