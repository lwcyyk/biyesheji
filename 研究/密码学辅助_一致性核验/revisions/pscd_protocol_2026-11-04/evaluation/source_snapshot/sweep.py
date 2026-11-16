"""Complete 135-cell descriptive sweep. Every attempted cell is retained."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import argparse
import hashlib
import json
import time
from public_models import ROOT,get_model,save_json
from source_fixtures import source_for
from run_protocol import run_cell

METHODS=['pscd','coordinate_nonzero','private_zero','full_shared_reference','pad_only']


def plan():
    cells=[]
    for n in [8,64,256]:
        for repeat in range(3):
            for profile in ['P0','P1','P2']:
                order=METHODS[repeat:]+METHODS[:repeat]
                if repeat%2:order=order[::-1]
                for method in order:
                    cells.append({'id':f'{profile}_n{n}_{method}_rep{repeat}','profile':profile,'n':n,
                                  'repeat':repeat,'method':method,'variant':'r5','case':'scheduled','gate_enabled':True})
    return cells


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--timeout',type=int,default=600)
    parser.add_argument('--retry-failed',action='store_true')
    args=parser.parse_args()
    directory=ROOT/'evaluation'
    directory.mkdir(exist_ok=True)
    cells=plan()
    plan_path=directory/'PLAN.json'
    if plan_path.exists():
        assert json.loads(plan_path.read_text())['cells']==cells
    else:
        save_json(plan_path,{'planned_cells':135,'workers':args.workers,'cell_timeout_seconds':args.timeout,
                            'security_parameter':40,'data_field_bits':128,'stage':'DEVELOPMENT_ONLY',
                            'parallel_load_is_a_limit':True,'cells':cells})
    for n in [8,64,256]:get_model(n);source_for(n)
    jobs=[]
    for cell in cells:
        folder=directory/'runs'/cell['id']
        previous=sorted(folder.glob('attempt*/result.json')) if folder.exists() else []
        if previous:
            latest=json.loads(previous[-1].read_text())
            if latest['status'] in ('PASS','EXPECTED_REJECT') or not args.retry_failed:continue
        jobs.append((cell,folder/f'attempt{len(previous)+1:02d}'))
    started=time.monotonic_ns()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(run_cell,cell,path,args.timeout):cell for cell,path in jobs}
        for future in as_completed(futures):
            result=future.result()
            with (directory/'ATTEMPTS.jsonl').open('a') as stream:stream.write(json.dumps(result,ensure_ascii=False)+'\n')
            statuses={}
            done=0
            for cell in cells:
                records=sorted((directory/'runs'/cell['id']).glob('attempt*/result.json'))
                status=json.loads(records[-1].read_text())['status'] if records else 'NOT_RUN'
                statuses[status]=statuses.get(status,0)+1
                done+=status not in ('STARTED','NOT_RUN')
            save_json(directory/'PROGRESS.json',{'planned':135,'terminal_cells':done,'statuses':statuses,
                                                  'elapsed_ns':time.monotonic_ns()-started})
            print(json.dumps({'cell':futures[future]['id'],'status':result['status'],'terminal':done,
                              'planned':135,'statuses':statuses}),flush=True)
