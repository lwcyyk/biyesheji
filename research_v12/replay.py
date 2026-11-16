"""Deterministic semantic replay comparison; timings are deliberately excluded."""
import bootstrap
import json,hashlib,platform,sys
from pathlib import Path
def normalize(r):
    x=r.get('result',{});kind=r['kind']
    if r['status']!='FEASIBLE':return {'status':r['status']}
    if kind=='J':
        return {'status':r['status'],'Q':x.get('value'),'policy':x.get('policy'),'completion':r['evaluation']['completion'],'G':r['evaluation'].get('max_G'),'side_effects':r['evaluation'].get('probe_side_effects'),'obligations':r['evaluation'].get('unresolved_obligations')}
    return {'status':r['status'],'G':x['metrics']['G'],'configuration':x.get('configuration',x.get('delivery',{}).get('configuration'))}
def main():
    root=bootstrap.ROOT;a=root/'runs/dev01/raw';b=root/'runs/dev02/raw';checks=[]
    for p in sorted(a.glob('*.json')):
        other=b/p.name;old=json.loads(p.read_text(encoding='utf-8'));new=json.loads(other.read_text(encoding='utf-8'))
        checks.append({'file':p.name,'pass':normalize(old)==normalize(new)})
    result={'pass':all(x['pass'] for x in checks),'count':len(checks),'checks':checks,'scope':'status/Q/G/configuration/policy + outcome safety; no timing identity claim','method_change':'dev02 exposes common solver session and limits single-root Z3 to same single root; dev01 retained'}
    (root/'runs/replay_report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('semantic replay',result['pass'],len(checks))
if __name__=='__main__':main()
