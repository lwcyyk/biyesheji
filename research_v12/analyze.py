import bootstrap
import json,argparse,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
def quantile(xs,q):
    xs=sorted(xs);return xs[min(len(xs)-1,max(0,math.ceil(q*len(xs))-1))] if xs else None
def objective(r):
    result=r.get('result',{})
    if r['status']!='FEASIBLE':return None
    if r['kind']=='J':return result.get('value')
    return [result.get('metrics',{}).get('G'),result.get('configuration',result.get('delivery',{}).get('configuration'))]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('run');a=ap.parse_args();d=bootstrap.ROOT/a.run
    rows=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((d/'raw').glob('*.json'))];lookup={(r['kind'],r['case'],r['method']):r for r in rows}
    checks=[];metrics={};by=defaultdict(list)
    for r in rows:
        by[(r['kind'],r['method'])].append(r);ref=lookup.get((r['kind'],r['case'],'RJ_MEMO' if r['kind']=='J' else 'R_B'))
        if ref and r['method'] not in ['OLD_A2','OLD_A3']:
            decisive=r['status'] not in ['TIMEOUT','INCONCLUSIVE','ERROR'] and ref['status'] not in ['TIMEOUT','INCONCLUSIVE','ERROR']
            checks.append({'case':r['case'],'method':r['method'],'kind':r['kind'],'pass':r['status']==ref['status'] and objective(r)==objective(ref) if decisive else None,'actual':objective(r),'expected':objective(ref),'status':r['status']})
        if r['status']=='FEASIBLE':
            valid=r.get('evaluation',{}).get('completion')==1 if r['kind']=='J' else r.get('delivery_check',{}).get('verdict')=='ACCEPTED'
            checks.append({'case':r['case'],'method':r['method'],'kind':r['kind'],'check':'legal policy/delivery','pass':valid})
    for (kind,method),rr in by.items():
        times=[r.get('total_seconds',30) for r in rr];proc=[r['process_inclusive_seconds'] for r in rr];mem=[r.get('memory',{}).get('peak_working_set_bytes',0) for r in rr]
        counts=Counter()
        for r in rr:counts.update(r.get('counts',{}))
        metrics[kind+'_'+method]={'n':len(rr),'status':dict(Counter(r['status'] for r in rr)),'median_seconds':statistics.median(times),'p95_seconds':quantile(times,.95),'max_seconds':max(times),'process_median_seconds':statistics.median(proc),'max_peak_memory_bytes':max(mem),'counts':dict(counts),'completion':sum(r.get('evaluation',{}).get('completion',0) for r in rr),'sum_CQ_with_refusal_penalty':sum(r.get('evaluation',{}).get('C_Q',0) for r in rr)}
    pairs=[]
    for kind,left,right in [('J','F001','F000'),('J','F100','F000'),('J','F010','F000'),('J','F111','F000'),('J','F001','GENERIC_REPLAY'),('B','B4','B2'),('B','B4','B3'),('B','B4','GENERIC_BB'),('B','B4','Z3_OPTIMIZE'),('B','B4','R_B'),('B','B4','GENERIC_PRESOLVE')]:
        ratios=[];process_ratios=[];case_rows=[]
        for (k,name,method),r in lookup.items():
            if k!=kind or method!=left:continue
            other=lookup[(kind,name,right)];t=r.get('total_seconds',30);b=other.get('total_seconds',30)
            pr=r['process_inclusive_seconds']/other['process_inclusive_seconds'];process_ratios.append(pr)
            ratios.append(t/b);case_rows.append({'case':name,'ratio':t/b,'process_inclusive_ratio':pr,'candidate_seconds':t,'baseline_seconds':b,'status':[r['status'],other['status']]})
        if ratios:pairs.append({'kind':kind,'candidate':left,'baseline':right,'n':len(ratios),'median_paired_time_ratio':statistics.median(ratios),'median_process_inclusive_ratio':statistics.median(process_ratios),'wins':sum(x<1 for x in ratios),'ties_exact':sum(x==1 for x in ratios),'all_rows':case_rows})
    out={'run':a.run,'count':len(rows),'all_decisive_reference_checks_pass':all(c['pass'] is not False for c in checks),'failed':[c for c in checks if c['pass'] is False],'unresolved':[c for c in checks if c['pass'] is None],'errors':[{'case':r['case'],'method':r['method'],'reason':r.get('reason',r.get('stderr'))} for r in rows if r['status']=='ERROR'],'metrics':metrics,'pairs':pairs,'checks':checks,'statistics':'development descriptive only; no confidence interval/hypothesis acceptance; all statuses retained'}
    (d/'analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['count','all_decisive_reference_checks_pass','failed','unresolved','errors']},ensure_ascii=False))
if __name__=='__main__':main()
