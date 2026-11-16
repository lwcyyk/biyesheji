"""Isolated live-MASCOT runner and committed-output verifier."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import threading
import time
import traceback
from public_models import ROOT, BASE, get_model, aes_parameters, save_json
from source_fixtures import make_input, share_inputs, source_for
from prepare import prepare, consume, F, multiply

BACKEND=BASE/'vendor/mp-spdz-0.4.4'
BINARY=BACKEND/'bin/Linux-adx/mascot-party.x'
LOCKS={}


def capture(command,cwd,log,env,timeout):
    started=time.monotonic_ns()
    with log.open('w') as stream:
        try:
            result=subprocess.run(command,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=timeout)
            code=result.returncode
            timed_out=False
        except subprocess.TimeoutExpired:
            code=None;timed_out=True
    return {'command':list(map(str,command)),'exit_code':code,'timeout':timed_out,
            'wall_ns':time.monotonic_ns()-started}


def compiler_cache(context,timeout):
    encoded=json.dumps(context,sort_keys=True).encode()
    source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'mpc').glob('*')) if p.is_file()}
    digest=hashlib.sha256(encoded+json.dumps(source_hashes,sort_keys=True).encode()).hexdigest()
    directory=ROOT/'compile_cache'/digest[:24]
    lock=LOCKS.setdefault(digest,threading.Lock())
    with lock:
        meta=directory/'compile_result.json'
        if meta.exists():return directory,json.loads(meta.read_text()),True
        for sub in ['Programs/Source','Programs/Bytecode','Programs/Schedules']:(directory/sub).mkdir(parents=True,exist_ok=True)
        source='pscd_'+context['profile'].lower()
        shutil.copyfile(ROOT/'mpc'/(source+'.mpc'),directory/'Programs/Source'/(source+'.mpc'))
        save_json(directory/'public_context.json',context)
        env=os.environ.copy()
        env.update(PYTHONDONTWRITEBYTECODE='1',PSCD_LIBRARY=str(ROOT/'mpc'),PSCD_PUBLIC_CONTEXT=str(directory/'public_context.json'))
        arguments=[str(context['model']['n']),context['method'],context['model']['variant']]
        command=['python3','-B',str(BACKEND/'compile.py'),'--galoissize','128','--preserve-mem-order',source]+arguments
        result=capture(command,directory,directory/'compile.log',env,timeout)
        result.update(program_name='-'.join([source]+arguments),source_hashes=source_hashes,
                      context_sha256=hashlib.sha256(encoded).hexdigest(),success=result['exit_code']==0)
        save_json(meta,result)
        return directory,result,False


def public_values(log):
    found=re.findall(r'PSCD_OUT index=(\d+) value=(0x[0-9a-fA-F]+|[0-9a-fA-F]+)',log)
    values={int(index):int(value,16) for index,value in found}
    if len(values)!=len(found) or sorted(values)!=list(range(len(values))):raise ValueError('output indices')
    status=re.findall(r'PSCD_STATUS value=(0x[0-9a-fA-F]+|[0-9a-fA-F]+)',log)
    return [values[i] for i in range(len(values))],None if not status else int(status[0],16),len(status)


def verify_outputs(directory,context,fixture,material):
    outputs=[]
    for party in (0,1):
        log=(directory/f'party{party}.log').read_text(errors='replace')
        if 'PSCD_DONE' not in log:raise ValueError('completion marker absent')
        outputs.append(public_values(log))
    if outputs[0]!=outputs[1]:raise ValueError('parties disagree')
    data,status,status_lines=outputs[0]
    model=context['model'];n=model['n'];profile=context['profile'];method=context['method']
    raw=fixture['frozen']['residuals']
    support=[i for i,x in enumerate(raw) if x]
    accepted=fixture['frozen']['case']!='bad_domain'
    if context['gate_enabled']:
        accepted=accepted and len(support)<=model['k'] and all(not(raw[i] and raw[j]) for i,j in context['forbidden_pairs'])
    expected=raw if accepted else [0]*n
    if profile=='P0':
        if status_lines:raise ValueError('P0 publicly exposed status')
        if len(data)!=len(material['pads']):raise ValueError('P0 length')
        clear=[a^b for a,b in zip(data,material['pads'])]
        if clear[-1]!=int(accepted):raise ValueError('private status')
        decoded=[]
        for i in range(n):
            if method=='pscd':
                weights=multiply(material['matrix'],model['dictionary'][i])
                pivot=next(j for j,w in enumerate(weights) if w)
                value=F.mul(clear[pivot*n+i],F.inverse(weights[pivot]))
                if any(clear[j*n+i]!=F.mul(weights[j],value) for j in range(model['r'])):raise ValueError('masked row disagreement')
            elif method=='coordinate_nonzero':
                value=F.mul(clear[i],F.inverse(material['multipliers'][i]))
            else:value=clear[i]
            decoded.append(value)
        if decoded!=expected:raise ValueError('private residual mismatch')
        private_result={'accepted':accepted,'residuals':decoded if accepted else None,
                        'support':support if accepted else None}
        save_json(directory/'private_receiver_result.json',private_result)
    else:
        if status_lines!=1 or status!=int(accepted):raise ValueError('public status')
        if profile=='P2':expected_output=expected
        elif method=='pscd':expected_output=[F.mul(multiply(material['matrix'],model['dictionary'][i])[row],expected[i]) for row in range(model['r']) for i in range(n)]
        elif method=='coordinate_nonzero':expected_output=[F.mul(x,rho) for x,rho in zip(expected,material['multipliers'])]
        else:expected_output=[sum(int(bool(expected[i]))<<(i-start) for i in range(start,min(start+128,n))) for start in range(0,n,128)]
        if data!=expected_output:raise ValueError('public output mismatch')
    transcript={'profile':profile,'method':method,'n':n,'field_output':[format(x,'x') for x in data],
                'public_status':status if profile!='P0' else None,
                'commit_condition':'both parties terminated successfully and output verification completed'}
    save_json(directory/'public_transcript.json',transcript)
    return {'pass':True,'accepted':accepted,'expected_support':support,'output_field_elements':len(data),
            'P0_public_status_absent':profile!='P0' or status_lines==0,
            'scope':'honest functional test on synthetic records, oracle knows all private inputs'}


def metrics(log):
    result={}
    patterns={'global_data_sent_MB':r'^Global data sent = ([\d.e+-]+) MB',
              'reported_seconds':r'^Time = ([\d.e+-]+) seconds',
              'triples_consumed':r'^\s+(\d+)\s+Triples$',
              'squares_consumed':r'^\s+(\d+)\s+Squares$',
              'inverses_consumed':r'^\s+(\d+)\s+Inverses$',
              'party0_total_rounds':r'^Data sent = [\d.e+-]+ MB in ~(\d+) rounds'}
    for key,pattern in patterns.items():
        match=re.search(pattern,log,re.M)
        result[key]=(int(match.group(1)) if key.endswith(('consumed','rounds')) else float(match.group(1))) if match else None
    match=re.search(r'Spent ([\d.e+-]+) seconds \([^\n]*?, (\d+) rounds[^\n]*?\) on the online phase and ([\d.e+-]+) seconds \([^\n]*?, (\d+) rounds',log)
    if match:
        result.update(online_seconds=float(match.group(1)),online_rounds=int(match.group(2)),
                      offline_seconds=float(match.group(3)),offline_rounds=int(match.group(4)))
    return result


def run_cell(cell,directory,timeout=300):
    directory=Path(directory).resolve()
    if not directory.is_relative_to(ROOT) or directory==ROOT:raise ValueError('isolated directory required')
    directory.mkdir(parents=True,exist_ok=False)
    result={'cell':cell,'status':'STARTED','run_directory':str(directory),'attempts':[],
            'visibility':'PRIVILEGED_SYNTHETIC_LAB_AUDIT_NOT_VERIFIER_OUTPUT'}
    save_json(directory/'result.json',result)
    try:
        model=get_model(cell['n'],cell.get('variant','r5'))
        model_hash=hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest()
        checked=json.loads((ROOT/'public/MODEL_VERIFICATION.json').read_text())
        if not any(x.get('model_sha256')==model_hash and x['verified'] for x in checked['models']):
            raise ValueError('PUBLIC_MODEL_VERIFICATION_MISSING')
        fixture=make_input(model,cell['repeat'],cell.get('case','scheduled'))
        save_json(directory/'private_fixture.json',fixture)
        policy={'gate_enabled':cell.get('gate_enabled',True),'forbidden_pairs':cell.get('forbidden_pairs',[])}
        receipt,material=prepare(directory/'prepare',cell['profile'],cell['method'],model,fixture['reference'],policy)
        context={'model':model,'profile':cell['profile'],'method':cell['method'],
                 'public_records':fixture['public_records'],'aes_parameters':aes_parameters(),
                 'gate_enabled':cell.get('gate_enabled',True),'forbidden_pairs':cell.get('forbidden_pairs',[])}
        save_json(directory/'public_context.json',context)
        cache,compiled,hit=compiler_cache(context,timeout)
        result['compile']=compiled;result['compile_cache_hit']=hit
        if not compiled['success']:
            result['status']='COMPILE_FAILED'
            return result
        for sub in ['Programs/Bytecode','Programs/Schedules']:
            shutil.copytree(cache/sub,directory/sub)
        (directory/'Player-Data').mkdir()
        for party,values in enumerate(share_inputs(fixture,material)):
            (directory/f'Player-Data/Input-P{party}-0').write_text(' '.join(format(x,'x') for x in values)+'\n')
        env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
        ssl=capture(['bash',str(BACKEND/'Scripts/setup-ssl.sh'),'2'],directory,directory/'ssl.log',env,timeout)
        result['ssl']=ssl
        if ssl['exit_code']!=0:
            result['status']='SETUP_FAILED';return result
        consume(directory/'prepare',cell['profile'],directory.name,policy)
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
        processes=[];handles=[];started=time.monotonic()
        try:
            for party in (0,1):
                command=[str(BINARY),'-N','2','-p',str(party),'-h','127.0.0.1','-pn',str(port),
                         '-lg2','128','-e','-v','-b','1000','-S','40','-OF','.',compiled['program_name']]
                handle=(directory/f'party{party}.log').open('w');handles.append(handle)
                processes.append(subprocess.Popen(command,cwd=directory,env=env,stdout=handle,stderr=subprocess.STDOUT))
                result['attempts'].append({'party':party,'command':command})
            for party,process in enumerate(processes):
                result['attempts'][party]['exit_code']=process.wait(timeout=max(1,timeout-(time.monotonic()-started)))
        except subprocess.TimeoutExpired:
            result['status']='TIMEOUT'
            for process in processes:
                if process.poll() is None:process.kill()
            for process in processes:process.wait()
        finally:
            for handle in handles:handle.close()
            result['runtime_wall_seconds']=time.monotonic()-started
        if result['status']=='TIMEOUT':return result
        if any(item.get('exit_code')!=0 for item in result['attempts']):
            result['status']='BACKEND_FAILED';return result
        result['verification']=verify_outputs(directory,context,fixture,material)
        result['metrics']=metrics((directory/'party0.log').read_text(errors='replace'))
        result['prepare_metrics']={k:material[k] for k in ['protocol_random_bits_drawn','input_share_random_bits_drawn','matrix_field_elements','coordinate_field_elements','pad_field_elements','prepare_ns']}
        result['source_share_random_bits']=16*8+len(fixture['frozen']['claims_hex'])*128
        result['status']='PASS' if result['verification']['accepted'] else 'EXPECTED_REJECT'
        return result
    except Exception as error:
        result['status']='FAILED'
        result['error']=type(error).__name__+': '+str(error)
        (directory/'exception.txt').write_text(traceback.format_exc())
        return result
    finally:
        save_json(directory/'result.json',result)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    parser.add_argument('--n',type=int,default=8)
    parser.add_argument('--profile',default='P1')
    parser.add_argument('--method',default='pscd')
    parser.add_argument('--repeat',type=int,default=1)
    parser.add_argument('--variant',default='r5')
    parser.add_argument('--case',default='scheduled')
    parser.add_argument('--timeout',type=int,default=300)
    args=parser.parse_args()
    cell={k:getattr(args,k) for k in ['n','profile','method','repeat','variant','case']}
    result=run_cell(cell,ROOT/args.out,args.timeout)
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(0 if result['status'] in ['PASS','EXPECTED_REJECT'] else 1)
