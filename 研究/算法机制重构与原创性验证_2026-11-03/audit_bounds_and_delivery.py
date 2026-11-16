from pathlib import Path
import sys,json,hashlib
from copy import deepcopy
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE/'prototype'))
from common import Meter
from auth_lifecycle.a import compiler,joint_reference
from b_units import solve,check_lower_bound
from auth_lifecycle.b import fixtures as bf
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
 rows=[]
 for p in sorted((BASE/'runs/final02/raw').glob('A_*_AB_ON.json')):
  raw=read(p);name=p.stem[:-len('_AB_ON')];source=read(BASE/'runs/final02/inputs'/(name+'.json'));compiled=compiler.compile_model(source)
  if compiled.status!='COMPILED':continue
  bundle=compiled.bundle
  for i,c in enumerate(raw.get('result',{}).get('diagnostics',[])):
   data=deepcopy(bundle['l0']);data['initial']=c['refs'];depth=bundle['points']['/'.join(c['refs'][0])]['depth'];data['horizon']=source['horizon']-depth
   other=dict(bundle,l0=data);ref=joint_reference.solve(other)
   good=ref.status=='IMPOSSIBLE' or (ref.status=='FEASIBLE' and c['bound']<=ref.worst_requests)
   rows.append({'case':name,'certificate':i,'bound':c['bound'],'reference_status':ref.status,'reference_total_Q':ref.worst_requests,'pass':good})
 m=bf.local_only(2);x=solve(m);bad=deepcopy(x['certificate']);bad['cuts'][0]['refs']=[]
 tamper={'valid':check_lower_bound(m,x['certificate'],Meter()),'bad_reference_accepted':check_lower_bound(m,bad,Meter())}
 old=read(BASE/'baseline.json')['files'];changed=[p for p,h in old.items() if not Path(p).exists() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
 depfiles={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'.deps').rglob('*') if p.is_file() and (p.suffix=='.dll' or p.name=='METADATA')}
 sourcefiles={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.glob('*.py')}
 sourcefiles.update({str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'prototype').glob('*.py')})
 allmain=all(read(BASE/'runs'/name/'summary.json')['pass'] for name in ['final02','secondary01','components01','smt02','mechanisms01'])
 out={'bound_checks':rows,'bound_checks_pass':all(x['pass'] for x in rows),'tamper':tamper,'main_and_secondary_pass':allmain,'preserved_original_files':len(old),'changed_originals':changed,'source_hashes':sourcefiles,'dependencies':{'z3-solver':'4.15.4.0','binary_and_metadata_hashes':depfiles},'pass':allmain and all(x['pass'] for x in rows) and tamper['valid'] and not tamper['bad_reference_accepted'] and not changed,'scope':'finite implementation/development checks; not general proof, native acceptance, novelty verification completion or formal statistical support'}
 (BASE/'最终验证.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'pass':out['pass'],'DRD_bounds_checked':len(rows),'changed':changed,'guards':'see original rows'},ensure_ascii=False))
if __name__=='__main__':main()
