from pathlib import Path
import sys,json
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE/'prototype'))
import common
from acquisition_reference import solve
from auth_lifecycle.a import compiler
from auth_lifecycle.checker import check_policy
def main(out=None):
 out=Path(out) if out else BASE/'runs/acquisition_reference01';out.mkdir(parents=True,exist_ok=False);rows=[]
 for p in sorted((BASE/'runs/final02/inputs').glob('A_*.json')):
  s=json.loads(p.read_text(encoding='utf-8'));c=compiler.compile_model(s);ref=solve(c.bundle)
  ck=check_policy(c.bundle['l0'],ref['policy']).verdict if ref.get('policy') else None
  tested=json.loads((BASE/'runs/final02/raw'/(p.stem+'_A2.json')).read_text(encoding='utf-8'));ok=ref['status']==tested['status']
  if ref['status']=='FEASIBLE':ok &= ck=='ACCEPTED' and ref['Q']==tested['result']['worst_requests']
  (out/p.name).write_text(json.dumps({'reference':ref,'policy_check':ck,'pass':bool(ok)},ensure_ascii=False,indent=2),encoding='utf-8');rows.append({'case':p.stem,'status':ref['status'],'Q':ref.get('Q'),'pass':bool(ok)})
 (out/'summary.json').write_text(json.dumps({'rows':rows,'pass':all(r['pass'] for r in rows),'scope':'independent raw interpreter; shared schema and reference kernel disclosed'},indent=2),encoding='utf-8');print('Reference checks:',len(rows),all(r['pass'] for r in rows))
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out');args=ap.parse_args();main(args.out)
