"""Separate functional denominator, outside the 135-cell performance sweep."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from public_models import ROOT,save_json
from run_protocol import run_cell


if __name__=='__main__':
    cells=[]
    for profile in ['P0','P1','P2']:
        for case in ['bad_tag','boundary','dense','bad_domain']:
            cells.append({'id':f'{profile}_{case}','profile':profile,'method':'pscd','variant':'r5','n':8,'repeat':1,'case':case})
    for variant in ['t2_r2','t2_r3']:
        for repeat in range(3):
            cells.append({'id':f'{variant}_{repeat}','profile':'P1','method':'pscd','variant':variant,'n':5,'repeat':repeat,'case':'scheduled' if repeat<2 else 'boundary'})
    for profile in ['P0','P1']:
        cells.append({'id':f'{profile}_forbidden_pair','profile':profile,'method':'pscd','variant':'r5','n':8,
                      'repeat':1,'case':'boundary','forbidden_pairs':[[0,1]]})
    out=ROOT/'supplemental';out.mkdir(exist_ok=True)
    save_json(out/'PLAN.json',{'planned_cells':len(cells),'kind':'FUNCTIONAL_NOT_MAIN_PERFORMANCE_DENOMINATOR','cells':cells})
    results=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(run_cell,cell,out/'runs'/cell['id'],600):cell for cell in cells}
        for future in as_completed(futures):
            result=future.result();results.append(result)
            save_json(out/'RESULTS.json',{'planned':len(cells),'results':results})
            print(json.dumps({'cell':futures[future]['id'],'status':result['status'],'completed':len(results),'planned':len(cells)}),flush=True)
