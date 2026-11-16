"""Reinterpret saved synthetic MPC logs; does not start MPC or read Player-Data."""
from pathlib import Path
import argparse,json,re
CR=Path('D:/毕业设计/研究/密码学辅助_一致性核验/revisions/structural_audit_2026-11-03_r1')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
 if args.out.exists():raise SystemExit('Output exists; choose a new path')
 f=json.loads((CR/'gate_mpc/fixture.json').read_text(encoding='utf-8'));rows=[];phases=[];triples={}
 for method,profile in [('gate','original'),('gate','restricted'),('release','original'),('release','restricted')]:
  folder=CR/'results'/f'{method}_{profile}';log=(folder/'party0.log').read_text(encoding='utf-8');manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
  gates={int(i):int(v) for i,v in re.findall(r'^GATE case=(\d+) accepted=(\d+)$',log,re.M)}
  outputs={int(i):int(v) for i,v in re.findall(r'^SUPPORT case=(\d+) packed=(\d+)$',log,re.M)}
  phases.append({'batch':f'{method}_{profile}','pass':manifest['success'] and all(p['exit_code']==0 for p in manifest['phases']) and log.count('PROTOCOL_DONE')==1 and len(gates)==len(f['cases'])})
  triples[(method,profile)]=int(re.search(r'\n\s+(\d+)\s+Triples',log)[1])
  for i,case in enumerate(f['cases']):
   support=[j for j,x in enumerate(case['values']) if x!=0]
   approved=len(support)<=2 if profile=='original' else all(sum(j//2==record for j in support)<=1 for record in (0,1))
   expected=sum(1<<j for j in support) if method=='release' and approved else None
   row={'batch':f'{method}_{profile}','case':i,'expected_gate':int(approved),'actual_gate':gates.get(i),'expected_support_output':expected,'actual_support_output':outputs.get(i)}
   row['pass']=row['expected_gate']==row['actual_gate'] and expected==outputs.get(i);rows.append(row)
 delta={p:triples[('release',p)]-triples[('gate',p)] for p in ['original','restricted']}
 result={'scope':'OFFLINE_RECHECK_OF_ARCHIVED_HONEST_MPC; NOT_NEW_EXECUTION','scenarios':rows,'phase_checks':phases,'extra_secret_multiplications':delta,'pass':all(x['pass'] for x in rows+phases) and all(x==0 for x in delta.values()),'leakage_note':'program reveal reaches both computing parties; print routing is not recipient confidentiality'}
 args.out.parent.mkdir(exist_ok=True,parents=True)
 with args.out.open('x',encoding='utf-8') as out:json.dump(result,out,ensure_ascii=False,indent=2)
 print(json.dumps({'pass':result['pass'],'archived_scenarios_rechecked':len(rows),'new_MPC_executions':0}))
if __name__=='__main__':main()
