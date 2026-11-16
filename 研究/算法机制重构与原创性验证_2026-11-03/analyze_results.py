from pathlib import Path
import json,statistics,math,hashlib
BASE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def quantile(v,q):
 s=sorted(v);return s[max(0,math.ceil(q*len(s))-1)] if s else None
def main():
 rows=read(BASE/'runs/final02/rows.json');summary=read(BASE/'runs/final02/summary.json');groups={}
 for method in sorted({x['method'] for x in rows}):
  for profile in ['W0','EXTENSION']:
   rr=[x for x in rows if x['method']==method and (x['profile'].startswith('EXTENSION')==(profile=='EXTENSION'))]
   if not rr:continue
   groups[method+'/'+profile]={'N':len(rr),'complete':sum(x['U'] for x in rr),'statuses':{s:sum(x['status']==s for x in rr) for s in sorted({x['status'] for x in rr})},'mean_failure_penalty_cost':statistics.mean(x.get('C_Q',x.get('C_G')) for x in rr),'mean_wall':statistics.mean(x['seconds'] for x in rr),'p95_wall_nearest_rank':quantile([x['seconds'] for x in rr],.95),'max_wall':max(x['seconds'] for x in rr),'max_memory':max((x['memory'] or {}).get('peak_working_set_bytes',0) for x in rr),'all_resource_guards':all(x['guards']['affinity_set'] and x['guards']['job_memory_guard_set'] for x in rr)}
 comparisons={}
 for left,right,kind in [('A2','BA_PROPERTY','A'),('A2','GENERIC_A_BB','A'),('AB_ON','AB_OFF','A'),('B2','GENERIC_BB','B'),('B2','B_OLD','B'),('B2','R-B','B')]:
  pairs=[]
  for case in sorted({r['case'] for r in rows if r['kind']==kind}):
   a=next(r for r in rows if r['case']==case and r['method']==left);b=next(r for r in rows if r['case']==case and r['method']==right)
   cost='C_Q' if kind=='A' else 'C_G';pairs.append({'case':case,'profile':a['profile'],'left_cost':a[cost],'right_cost':b[cost],'left_seconds':a['seconds'],'right_seconds':b['seconds'],'left_U':a['U'],'right_U':b['U']})
  comparisons[left+'/'+right]={'all_pairs':pairs,'cost_less':sum(p['left_cost']<p['right_cost'] for p in pairs),'cost_equal':sum(p['left_cost']==p['right_cost'] for p in pairs),'cost_more':sum(p['left_cost']>p['right_cost'] for p in pairs),'time_ratio_sum_all':sum(p['left_seconds'] for p in pairs)/sum(p['right_seconds'] for p in pairs),'interpretation':'descriptive, all cases retained; single process run, not population/causal speed proof'}
 # Repeated executions compare semantic outcomes and policies, not wall/CPU/RSS.
 replay=[]
 for p in sorted((BASE/'runs/final02/raw').glob('*.json')):
  a=read(p);b=read(BASE/'runs/final01/raw'/p.name)
  def core(x):return {'status':x['status'],'result':x.get('result'),'evaluation':x.get('evaluation'),'delivery_check':x.get('delivery_check'),'lower_bound_check':x.get('lower_bound_check')}
  replay.append({'file':p.name,'same':core(a)==core(b)})
 old=read(BASE/'baseline.json')['files'];changed=[p for p,h in old.items() if not Path(p).exists() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
 result={'main_pass':summary['pass'],'groups':groups,'comparisons':comparisons,'semantic_replay':{'N':len(replay),'all_same':all(x['same'] for x in replay),'details':replay},'preserved_files':len(old),'changed':changed,'formal_hypotheses':'NOT_TESTED','p95_is_development_description_only':True,'native_product_W0':'NOT_ACCEPTED','timing_limitations':['4 logical CPU affinity, no dedicated physical cores','8GiB per worker, not entire native deployment','final01 overlapped secondary route worker, use final02 timings','single-pass timings and dependent generated families; no formal statistical inference']}
 dump(BASE/'结果分析.json',result)
 print(json.dumps({'pass':result['main_pass'],'replay_all_same':result['semantic_replay']['all_same'],'comparisons':{k:{x:v[x] for x in ['cost_less','cost_equal','cost_more','time_ratio_sum_all']} for k,v in comparisons.items()},'changed':changed},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
