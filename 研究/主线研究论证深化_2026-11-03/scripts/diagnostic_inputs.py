from copy import deepcopy
from auth_lifecycle.a import fixtures as af

def five_worlds(*, side_effect=False, harder=False):
 """Hand-designed diagnostic; not a sampled/native family or efficacy evidence."""
 s=af.acquisition(requests=12,horizon=5)
 template=deepcopy(s['worlds']['m0n0'])
 # Every world has some valid job stop; z semantics is also exposed by properties().
 bits=[(1,0,0),(1,0,1),(1,1,0),(0,1,0),(0,1,1)]
 s['worlds']={}
 for i,values in enumerate(bits):
  m=deepcopy(template)
  for g,v in zip(['x','y','z'],values):m['revocations'][g]['coverage']='all_material' if v else 'refresh_only'
  s['worlds'][f'w{i}']=m
 s['initial']=list(s['worlds']);s['probes']={}
 af.probe(s,'fine',{w:w for w in s['worlds']},requests=3)
 groups=[0,0,1,0,1] if harder else [0,0,0,1,1]
 af.probe(s,'coarse',{f'w{i}':str(v) for i,v in enumerate(groups)},requests=2,sessions=['verification'] if side_effect else [])
 if side_effect:af.cleanup(s)
 return s

def feedback_diagnostic():
 s=af.acquisition(nuisance=2,requests=12,horizon=5)
 for w,m in s['worlds'].items():m['revocations']['z']['coverage']='all_material' if w.endswith('0') else 'refresh_only'
 s['probes']={}
 # The XOR query wins the shared lexical tie; B-specific pairs prefer native mode.
 af.probe(s,'a_xor',{w:str(int(w[1]) ^ int(w[-1])) for w in s['worlds']})
 af.probe(s,'z_native',{w:w[:2] for w in s['worlds']})
 return s

def diagnostic_cases():
 for name,s,expected in af.cases():
  yield name,s,expected,'INHERITED_REGRESSION'
 yield 'A_different_ranking_equal_total',five_worlds(side_effect=True),'FEASIBLE','PROJECTION_DIAGNOSTIC_NOT_H_A'
 yield 'A_different_ranking_worse_total',five_worlds(harder=True),'FEASIBLE','HAND_DESIGNED_COUNTEREXAMPLE'
 yield 'AB_ranking_changes_projection_sensitive',feedback_diagnostic(),'FEASIBLE','PROJECTION_DIAGNOSTIC_NOT_H_AB'
