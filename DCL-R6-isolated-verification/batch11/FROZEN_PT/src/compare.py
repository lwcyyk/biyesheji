"""Frozen-input construction and result comparison. No truth labels in inputs."""
import sys,copy,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from itertools import product
import f4_dp as DP
import f4_reference as REF
from guard import ROOT,write,digest

OBS=['same','low','high','done'];ACT=['a','b','c','STOP']
REPORT_ROOT=ROOT/'reports'
INPUT_ROOT=ROOT/'inputs'

def state(phase,mode=0,goal=False,obl=None,quota=1):
    return {'phase':phase,'mode':mode,'goal':goal,'safe':True,'post_inv':True,
            'obligations':[] if obl is None else obl,'quota_mode':quota,'actions':{}}

def edge(d,s,a,t,cost,obs='same',safe=True):
    row=d['states'][s]['actions'].setdefault(a,{'enabled':True,'segments':[]})
    row['segments'].append({'to':t,'obs':obs,'steps':[{'cost':cost,'safe':safe}]})

def base(name):return {'id':name,'actions':ACT[:],'observations':OBS[:],'initial':[],'states':{}}

def cost_game(name,fees=(10,0,0,10),alternative=15,visible=False):
    d=base(name)
    for w in range(2):
        x,u,t=f'x{w}',f'u{w}',f't{w}'
        d['states'][x]=state('start',w);d['states'][u]=state('after_a',w);d['states'][t]=state('done',w,True)
        d['initial'].append({'world':w,'state':x,'cost':0})
        edge(d,x,'a',u,fees[w],('low' if fees[w]==0 else 'high') if visible else 'same')
        edge(d,u,'b',t,fees[2+w],'done');edge(d,x,'c',t,alternative,'done')
    return d

def fixtures():
    out=[cost_game('COST1')]
    d=base('CE5_FULL');d['states']={'x0':state('start',0),'x1':state('start',1),'t':state('done',0,True)}
    d['initial']=[{'world':0,'state':'x0','cost':5},{'world':1,'state':'x1','cost':0}]
    edge(d,'x0','a','t',0,'done');edge(d,'x1','a','t',10,'done');out.append(d)
    d=base('COMP_SAME_X');d['states']={'x':state('start'),'t':state('done',goal=True)}
    d['initial']=[{'world':0,'state':'x','cost':0},{'world':1,'state':'x','cost':5}];edge(d,'x','a','t',5,'done');out.append(d)
    for partial in (False,True):
        d=base('PARTIAL_POST_INVALID' if partial else 'EMPTY_POST_INVALID')
        d['states']={'x0':state('start',0),'x1':state('start',1),'t':state('done',goal=True)}
        d['initial']=[{'world':0,'state':'x0','cost':0},{'world':1,'state':'x1','cost':0}]
        for x in ('x0','x1'):d['states'][x]['actions']['a']={'enabled':True,'segments':[]}
        if partial:edge(d,'x0','a','t',0,'done')
        out.append(d)
    d=base('OPEN_UNKNOWN');d['states']={'x':state('done',goal=True,obl=['UNKNOWN'])};d['initial']=[{'world':0,'state':'x','cost':0}];out.append(d)
    d=base('NONUNIFORM');d['states']={'x0':state('start',0),'x1':state('start',1),'ok':state('done',goal=True),'bad':state('done',goal=True,obl=['UNKNOWN'])}
    d['initial']=[{'world':w,'state':f'x{w}','cost':0} for w in range(2)]
    for w in range(2):
        edge(d,f'x{w}','a','ok' if w==0 else 'bad',0,'done');edge(d,f'x{w}','b','ok' if w==1 else 'bad',0,'done')
    out.append(d)
    d=base('REAL_QUERY_COST');d['states']={'x':state('start'),'u':state('after_a'),'t':state('done',goal=True)};d['initial']=[{'world':0,'state':'x','cost':0}]
    edge(d,'x','a','u',1);edge(d,'u','b','t',1,'done');out.append(d)
    d=base('ZERO_INTERNAL');d['states']={'x':state('start'),'t':state('done',goal=True)};d['initial']=[{'world':0,'state':'x','cost':0}]
    edge(d,'x','a','x',0);edge(d,'x','b','t',0,'done');out.append(d)
    d=base('PREFIX_BAD');d['states']={'x':state('start'),'t':state('done',goal=True)};d['initial']=[{'world':0,'state':'x','cost':0}]
    edge(d,'x','a','t',0,'done',False);d['states']['x']['actions']['a']['segments'][0]['steps'].append({'cost':0,'safe':True})
    edge(d,'x','c','t',15,'done');out.append(d)
    d=cost_game('VISIBLE_COST',(0,10,0,15),15,True)
    edge(d,'u0','c','t0',15,'done');edge(d,'u1','c','t1',0,'done')
    # Remove the initial direct shortcut, exposing the genuine observed-cost decision.
    for x in ('x0','x1'):del d['states'][x]['actions']['c']
    out.append(d)
    d=base('QUOTA_MODE');d['states']={'x0':state('start',quota=1),'x1':state('start',quota=0),'t':state('done',goal=True)}
    d['initial']=[{'world':w,'state':f'x{w}','cost':0} for w in range(2)]
    edge(d,'x0','a','t',0,'done');d['states']['x1']['actions']['a']={'enabled':False,'segments':[]}
    edge(d,'x0','c','t',15,'done');edge(d,'x1','c','t',15,'done');out.append(d)
    d=base('MISSING_OBSERVATION');d['states']={'x':state('start'),'t':state('done',goal=True),'bad':state('done',goal=True,obl=['UNKNOWN'])};d['initial']=[{'world':0,'state':'x','cost':0}]
    edge(d,'x','a','t',0,'low');edge(d,'x','a','bad',0,'high');out.append(d)
    return out

def generated():
    out=[]
    for i,(fees,c,visible) in enumerate(product(product((0,10),repeat=4),(5,15),(False,True))):
        out.append(cost_game(f'G64_{i:02}',fees,c,visible))
    return out

def save_input(d):
    path=INPUT_ROOT/'F4'/(d['id']+'.json')
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8'))!=d:raise RuntimeError('INPUT_VERSION_COLLISION')
    else:write(path,d)
    return {'file':str(path.relative_to(ROOT)),'sha256':digest(path)}

def check_case(d,budget):
    lock=save_input(d);results=[];refs={};min_dp={};min_comp={};valid=True
    for h in (0,1,2):
        ref=REF.solve(d,h,budget);refs[str(h)]=ref
        dp_values=[];cp_values=[]
        for m in range(21):
            dp=DP.decide(d,h,m,budget);cp=DP.decide(d,h,m,budget,compression=True)
            expected=ref['optimum'] is not None and ref['optimum']<=m if ref['valid'] else None
            row={'h':h,'m':m,'reference_feasible':expected,'dp':dp,'compressed':cp}
            if dp['valid']!=ref['valid'] or cp['valid']!=ref['valid'] or (ref['valid'] and (dp['feasible']!=expected or cp['feasible']!=expected)):
                row['mismatch']='FEASIBILITY_OR_INPUT_VALIDITY';valid=False
            for name,value in (('dp',dp),('compressed',cp)):
                if value['valid'] and value['feasible']:
                    replay=REF.interpret(d,h,value['strategy'],budget,tree=True)
                    row[name+'_reference_replay']=replay
                    if not replay['ok'] or replay['worst_cost']>m or replay['worst_cost']!=value['strategy']['claimed_worst_cost']:
                        row['mismatch']='WITNESS_COST_TERMINAL_OR_UNIFORMITY';valid=False
            if dp.get('feasible'):dp_values.append(m)
            if cp.get('feasible'):cp_values.append(m)
            results.append(row)
            if not valid:break
        min_dp[str(h)]=min(dp_values) if dp_values else None;min_comp[str(h)]=min(cp_values) if cp_values else None
        if not valid:break
    report={'category':'REFERENCE_CROSSCHECK','input':lock,'id':d['id'],
        'status':'PASS_BOUNDED' if valid else 'MODEL_ERROR','reference':refs,'threshold_rows':results,
        'dp_minimum_0_20':min_dp,'compressed_minimum_0_20':min_comp,
        'independence':'Separate semantic validators, DP belief recursion vs exhaustive fixed policy tables and concrete BFS traces; shared data generator and administrative budget only.'}
    write(REPORT_ROOT/'F4'/(d['id']+'.json'),report)
    return {'id':d['id'],'status':report['status'],'input':lock,'dp_minimum_0_20':min_dp,
            'reference_optima':{h:r['optimum'] for h,r in refs.items()},'rows':len(results)}

def mutant_case(d,mutant,budget):
    lock=save_input(d)
    for h in (0,1,2):
        ref=REF.solve(d,h,budget)
        for m in range(21):
            bad=DP.decide(d,h,m,budget,compression=mutant in ('drop_mode','drop_permission'),mutant=mutant)
            expected=ref['optimum'] is not None and ref['optimum']<=m if ref['valid'] else None
            mismatch=bad['valid']!=ref['valid'] or (ref['valid'] and bad['feasible']!=expected)
            replay=None
            if bad['valid'] and bad['feasible']:
                replay=REF.interpret(d,h,bad['strategy'],budget,tree=True)
                mismatch=mismatch or not replay['ok'] or replay['worst_cost']>m or replay['worst_cost']!=bad['strategy'].get('claimed_worst_cost')
            if mismatch:
                result={'category':'MUTATION_CHECK','id':d['id'],'mutant':mutant,'status':'COUNTEREXAMPLE_FOUND',
                    'input':lock,'h':h,'m':m,'candidate':bad,'reference':ref,'reference_replay':replay,
                    'minimality':'First h then m in complete declared loops; reference witnesses include concrete trajectories; not a global protocol minimum',
                    'classification':'Injected candidate semantic defect, not a newly observed paper-protocol defect'}
                write(REPORT_ROOT/'F4_MUTANTS'/(d['id']+'__'+mutant+'.json'),result)
                return {'mutant':mutant,'id':d['id'],'status':result['status'],'h':h,'m':m}
    result={'mutant':mutant,'id':d['id'],'status':'MUTATION_NOT_DETECTED','input':lock}
    write(REPORT_ROOT/'F4_MUTANTS'/(d['id']+'__'+mutant+'.json'),result);return result
