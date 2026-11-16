from pathlib import Path
import sys,json,hashlib,subprocess,zipfile,argparse,time
from copy import deepcopy
BASE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(BASE/'prototype'))
from common import ROOT
from auth_lifecycle.a import fixtures as af
from auth_lifecycle.b import fixtures as bf
def dump(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def cases():
 for name,s,status in af.cases():
  if name in ['simple_acquisition','local_only_no_learning_negative_control','joint_planning_cheaper_than_early_configure','empty_K','unknown_not_success','lost_probe_unknown_handle']:
   s['horizon']=3;yield 'A',name,s,'W0_L0'
 old=Path('D:/毕业设计/研究/主线研究论证深化_2026-11-03/runs/final02/inputs/A_different_ranking_equal_total.json')
 for coarse in [1,2,3]:
  for fine in [1,3]:
   for effects in [False,True]:
    s=json.loads(old.read_text(encoding='utf-8'));s['horizon']=3
    s['probes']['coarse']['operation']['requests']=coarse;s['probes']['fine']['operation']['requests']=fine
    if not effects:
     for schedule in s['probes']['coarse']['outcomes'].values():
      for outcomes in schedule:
       for edge in outcomes:edge['sessions']=[]
    yield 'A',f'acquire_c{coarse}_f{fine}_e{int(effects)}',s,'W0_L0_HAND_GENERATED'
 for h in [4,5]:
  s=json.loads(old.read_text(encoding='utf-8'));s['horizon']=h;yield 'A',f'obligation_extension_h{h}',s,'EXTENSION_NOT_W0'
 for n in [2,3,4]:
  for shared in [True,False]:
   s=bf.local_only(n);s['horizon']=3
   if not shared:
    for p in list(s['paths']):
     if p.endswith('_shared'):del s['paths'][p]
   yield 'B',f'local_n{n}_shared{int(shared)}',s,'W0_L0'
 for name,s in bf.structural_models(count=12,seed=20261103):
  s['horizon']=3;yield 'B',name,s,'W0_L0_GENERATED'
 for line in (ROOT/'results/b/final02/structural.jsonl').read_text(encoding='utf-8').splitlines():
  x=json.loads(line)
  if x['case'].endswith(('-034','-084')):
   s=x.get('input',x.get('source',x.get('model')));s=deepcopy(s);s['horizon']=3;yield 'B',x['case'],s,'W0_L0_INHERITED'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--smoke',action='store_true');a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
 protocol=json.loads((BASE/'protocol.json').read_text());selected=list(cases())
 if a.smoke:selected=[selected[0],selected[2],selected[6],next(x for x in selected if x[0]=='B')]
 dump(out/'environment.json',{'command':[sys.executable,*sys.argv],'python':sys.version,'protocol_sha256':sha(BASE/'protocol.json'),'protocol_addendum_sha256':sha(BASE/'protocol_addendum.json') if (BASE/'protocol_addendum.json').exists() else None,'code':{str(p.relative_to(BASE)):sha(p) for p in BASE.rglob('*.py') if 'runs' not in p.parts},'formal':'NOT_TESTED'})
 with zipfile.ZipFile(out/'source.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in BASE.rglob('*.py'):
   if 'runs' not in p.parts:z.write(p,p.relative_to(BASE).as_posix())
 rows=[]
 for kind,name,s,profile in selected:
  inp=out/'inputs'/f'{kind}_{name}.json';dump(inp,s)
  methods=['BA_PROPERTY','A2','ACQUIRE_DP','GENERIC_A_BB','AB_OFF','AB_ON','GENERIC_DRD','R-J'] if kind=='A' else ['B2','GENERIC_BB','B_OLD','B-B','R-B']
  for method in methods:
   dest=out/'raw'/f'{kind}_{name}_{method}.json';dest.parent.mkdir(exist_ok=True)
   cmd=[sys.executable,str(BASE/'prototype/worker.py'),'--input',str(inp),'--out',str(dest),'--kind',kind,'--method',method]
   try:
    r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=32,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    value=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {'status':'ERROR','stderr':r.stderr}
   except subprocess.TimeoutExpired:value={'status':'TIMEOUT','reason':'parent watchdog 32s includes process startup; decision budget remains 30s'};dump(dest,value)
   if kind=='A':
    ev=value.get('evaluation',{});u=int(value['status']=='FEASIBLE' and ev.get('completion')==1)
    row={'kind':kind,'case':name,'profile':profile,'method':method,'status':value['status'],'U':u,'Q':ev.get('external_requests'),'C_Q':ev.get('external_requests') if u else s['budget']['requests']+1,'G':ev.get('max_G'),'O_end':ev.get('unresolved_obligations'),'safety':len(ev.get('safety_counterexamples',[])),'value':value.get('result',{}).get('worst_requests')}
   else:
    rr=value.get('result',{});ck=value.get('delivery_check') or {};metrics=rr.get('metrics') or {};u=int(value['status']=='FEASIBLE' and ck.get('verdict')=='ACCEPTED')
    row={'kind':kind,'case':name,'profile':profile,'method':method,'status':value['status'],'U':u,'G':metrics.get('G'),'C_G':metrics.get('G') if u else s['budgets']['units']+1,'LB':rr.get('lower_bound'),'gap':rr.get('gap'),'bound_check':value.get('lower_bound_check'),'safety':int(bool(rr.get('delivery')) and ck.get('verdict')!='ACCEPTED')}
   row.update(seconds=value.get('total_wall_seconds'),cpu_seconds=value.get('total_cpu_seconds'),memory=value.get('peak_memory'),work=value.get('meter'),guards=value.get('guards'));rows.append(row)
   print(kind,name,method,row['status'],'Q/G',row.get('Q',row.get('G')),flush=True)
   dump(out/'rows.json',rows)
 old=json.loads((BASE/'baseline.json').read_text(encoding='utf-8'))['files'];changed=[p for p,v in old.items() if not Path(p).exists() or sha(Path(p))!=v]
 comparisons=[]
 for kind,name,s,profile in selected:
  rr={r['method']:r for r in rows if r['kind']==kind and r['case']==name};ok=not any(r['status']=='ERROR' or r['safety'] for r in rr.values())
  if kind=='A':
   ok &= len({rr[x]['status'] for x in ['A2','ACQUIRE_DP','GENERIC_A_BB','AB_OFF','AB_ON','GENERIC_DRD','R-J']})==1
   if rr['A2']['U']:
    ok &= rr['A2']['Q']==rr['ACQUIRE_DP']['Q']==rr['GENERIC_A_BB']['Q']
    ok &= rr['AB_OFF']['Q']==rr['AB_ON']['Q']==rr['GENERIC_DRD']['Q']==rr['R-J']['Q']
  else:
   if rr['R-B']['status'] not in ['INCONCLUSIVE','TIMEOUT']:
    ok &= all(rr[x]['status']==rr['R-B']['status'] for x in ['B2','GENERIC_BB','B_OLD'])
    if rr['R-B']['U']:ok &= all(rr[x]['G']==rr['R-B']['G'] for x in ['B2','GENERIC_BB','B_OLD'])
   ok &= all(rr[x]['bound_check'] is True for x in ['B2','GENERIC_BB'] if rr[x]['status'] not in ['INCONCLUSIVE','TIMEOUT'])
  comparisons.append({'kind':kind,'case':name,'pass':bool(ok)})
 dump(out/'summary.json',{'cases':len(selected),'runs':len(rows),'comparisons':comparisons,'pass':all(x['pass'] for x in comparisons) and not changed,'changed_original_files':changed,'protected_files':len(old),'formal_hypotheses':'NOT_TESTED','W0_product_acceptance':'NOT_RUN','rows':'rows.json'})
if __name__=='__main__':main()
