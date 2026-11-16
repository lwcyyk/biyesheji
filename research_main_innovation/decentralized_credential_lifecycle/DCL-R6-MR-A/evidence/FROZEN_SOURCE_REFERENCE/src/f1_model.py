"""Finite application-level D1 model, per-Cfg static PBFT commit oracle.
Fault identities affect certificate authentication, not oracle safety.
No real provider, secret, network request, or PBFT implementation is present.
"""
import copy, json, hashlib

def canonical(s): return json.dumps(s,sort_keys=True,separators=(',',':'))
def root(s): return hashlib.sha256(canonical(s).encode()).hexdigest()

def business(empty=False):
    attempts=[]
    for t in range(2):
        for k in range(2):
            attempts.append({'state':'empty','origin':[t,t,0,k],'right':'none','boot':0,'holder':0,'result_origin':None})
    b={'grants':[not empty,False],'generation':[0,0],'approvals':[0 if empty else 1,0],
       'reserved':[0,0],'charged':[0,0],'attempts':attempts,'obl':[], 'hist':0,
       'caps':[0,0],'dedup':{},'owner':0,'boot':0}
    if not empty:
        b['charged'][0]=1; b['attempts'][0]['state']='unknown'; b['attempts'][0]['right']='unconsumed'
        b['obl']=[[0,'OUTCOME'],[0,'DERIVATION']]; b['hist']=1; b['caps'][0]=1; b['dedup']['a0']='bodyA'
    return b

def initial(p):
    names=p['configs']; b=business(p.get('empty',False))
    cfg={c:{'phase':'ACTIVE' if c=='O' else 'WAIT_ACTIVATE','pending':None,'child':None,'seq':0,
            'log':[],'biz':copy.deepcopy(b) if c=='O' else None,'objects':0,'ready_state':False,
            'ready_use':c=='O','active':c=='O','retired':False,'online':True,'recovery_done':False,
            'transferred':None,'genesis':None} for c in names}
    for c,x in cfg.items():x['members']=[c+str(i) for i in range(4)];x['fault_bound']=1
    ghosts=[] if p.get('empty',False) else [{'kind':'Release','cfg':'O','a':0,'origin':[0,0,0,0],
        'grant_ok':True,'ready_ok':True,'phase':'ACTIVE','generation':0,'position':0}]
    return {'cfg':cfg,'stops':[],'activations':[{'cfg':'O','parent':None,'genesis':'GENESIS_O'}],
        'ghost':ghosts,'closed':[],'dedup_truth':{} if p.get('empty',False) else {'a0':'bodyA'},
        'exposure':0 if p.get('empty',False) else 1,'network':[0,0,0,0],
        'recorded':[],'events':[],'revoke_done':False,'gate_recovered':False,'aborted':[],
        'domain_overflow':False,'gate_rights':['none']*4 if p.get('empty',False) else ['unconsumed','none','none','none'],
        'send_facts':[]}

def heads(s):
    parents={a['parent'] for a in s['activations'] if a['parent'] is not None}
    return [c for c,x in s['cfg'].items() if x['active'] and c not in parents]

def children(p,c): return p['children'].get(c,[])

def commit(s,c,label):
    x=s['cfg'][c]
    if x['seq']>=12: s['domain_overflow']=True; return
    x['seq']+=1; x['log'].append(label)

def successors(s,p,mutant='none'):
    def emit(label,fn):
        n=copy.deepcopy(s); fn(n); return label,n
    def seal(n,c,target,second=False):
        x=n['cfg'][c]; x['phase']='SEALED'; x['child']=target; commit(n,c,'Seal:'+target)
        payload={'biz':copy.deepcopy(x['biz']),'parent':c,'child':target,'seq':x['seq'],'schema':1}
        n['stops'].append({'parent':c,'child':target,'snapshot':payload,'root':root(payload),
                           'signers':[c+'0',c+'1',c+'2'],'real_commit':True})
    for c,x in s['cfg'].items():
        if x['active'] and not x['retired']:
            if x['online']:
                yield emit('Partition:'+c,lambda n,c=c:n['cfg'][c].__setitem__('online',False))
            else:
                yield emit('RestoreNetwork:'+c,lambda n,c=c:n['cfg'][c].__setitem__('online',True))
        if not x['online']: continue
        b=x['biz']
        if x['phase']=='ACTIVE' and x['active']:
            if p.get('allow_business',False) and (not p.get('business_after_takeover') or c!='O'):
              for t in p.get('business_tasks',[0]):
                if not b['grants'][t] and b['approvals'][t]<(2 if p.get('renew',False) else 1):
                    def approve(n,c=c,t=t):
                        q=n['cfg'][c]['biz']; q['generation'][t]=q['approvals'][t];q['approvals'][t]+=1;q['grants'][t]=True
                        n['ghost'].append({'kind':'Approve','cfg':c,'task':t,'gen':q['generation'][t]});commit(n,c,'Approve')
                    yield emit('Approve:'+c+':'+str(t),approve)
                if b['grants'][t] and not s['revoke_done']:
                    def revoke(n,c=c,t=t):
                        q=n['cfg'][c]['biz'];q['grants'][t]=False;n['revoke_done']=True
                        for a in (t*2,t*2+1):
                            if q['attempts'][a]['state']=='queued':q['attempts'][a]['state']='closed';q['reserved'][t]-=1
                        n['ghost'].append({'kind':'Revoke','cfg':c,'task':t});commit(n,c,'Revoke')
                    yield emit('Revoke:'+c+':'+str(t),revoke)
                # Unknown creation has no successor. The second slot stays reserved
                # in the finite type but is not enabled without a native contract.
                for a in (t*2,):
                    at=b['attempts'][a]
                    if at['state']=='empty' and b['grants'][t] and sum((b['reserved'][t],b['charged'][t]))<p['limit']:
                        def admit(n,c=c,a=a,t=t):
                            q=n['cfg'][c]['biz'];q['attempts'][a]['state']='queued';q['reserved'][t]+=1
                            q['attempts'][a]['origin']=[t,t,q['generation'][t],a];commit(n,c,'Admit:'+str(a))
                            q['dedup']['a'+str(a)]='body'+str(t);n['dedup_truth']['a'+str(a)]='body'+str(t)
                        yield emit(f'Admit:{c}:{a}',admit)
                    if at['state']=='queued' and b['grants'][t] and at['origin'][2]==b['generation'][t]:
                        def release(n,c=c,a=a,t=t):
                            y=n['cfg'][c];q=y['biz'];z=q['attempts'][a];z['state']='released';z['right']='unconsumed';z['boot']=q['boot'];z['holder']=q['owner']
                            q['reserved'][t]-=1;q['charged'][t]+=1;q['obl']+= [[a,'OUTCOME'],[a,'DERIVATION']]
                            q['hist']|=1<<t;q['dedup']['a'+str(a)]='body'+str(t);n['dedup_truth']['a'+str(a)]='body'+str(t);n['exposure']|=1<<t
                            n['ghost'].append({'kind':'Release','cfg':c,'a':a,'origin':z['origin'][:],
                                'grant_ok':q['grants'][t],'ready_ok':y['ready_use'],'phase':y['phase'],'generation':q['generation'][t],'position':y['seq']+1})
                            n['gate_rights'][a]='unconsumed'
                            commit(n,c,'Release:'+str(a))
                        yield emit(f'Release:{c}:{a}',release)
            for target in children(p,c):
                if [c,target] not in s['aborted'] and x['pending'] is None:
                    def propose(n,c=c,target=target):n['cfg'][c]['pending']=target;commit(n,c,'Propose:'+target)
                    yield emit('Propose:'+c+'>'+target,propose)
            if x['pending']:
                def prepare(n,c=c):n['cfg'][c]['phase']='PREPARING';commit(n,c,'Prepare')
                yield emit('Prepare:'+c,prepare)
        if x['phase']=='PREPARING':
            target=x['pending']
            yield emit('Seal:'+c+'>'+target,lambda n,c=c,target=target:seal(n,c,target))
            if p.get('abort',False):
                def abort(n,c=c,target=target):
                    n['aborted'].append([c,target]);n['cfg'][c]['pending']=None;n['cfg'][c]['phase']='ACTIVE';commit(n,c,'Abort')
                yield emit('Abort:'+c,abort)
        if mutant=='double_child' and x['phase']=='SEALED':
            used={z['child'] for z in s['stops'] if z['parent']==c}
            for target in children(p,c):
                if target not in used: yield emit('BAD_SecondSeal:'+c+'>'+target,lambda n,c=c,target=target:seal(n,c,target,True))
        if mutant=='rollback' and x['phase']=='SEALED' and not x['recovery_done']:
            def rollback(n,c=c):n['cfg'][c]['phase']='ACTIVE';n['cfg'][c]['recovery_done']=True
            yield emit('BAD_RecoverActive:'+c,rollback)
        if x['phase']=='SEALED' and not x['retired'] and any(z['parent']==c for z in s['activations']):
            def retire(n,c=c):n['cfg'][c]['retired']=True
            yield emit('Retire:'+c,retire)
        if x['active'] and not x['recovery_done'] and p.get('recovery',False):
            def recover(n,c=c):n['cfg'][c]['recovery_done']=True
            yield emit('VerifiedRecover:'+c,recover)
        if x['active'] and mutant=='stale_cache' and (x['phase']=='SEALED' or (b and not b['grants'][0])):
            if not any(z.get('bad_stale') for z in s['ghost']):
                def stale(n,c=c):
                    y=n['cfg'][c];q=y['biz'];n['ghost'].append({'kind':'Release','cfg':c,'a':1,'origin':[0,0,0,1],
                        'grant_ok':q['grants'][0],'ready_ok':y['ready_use'],'phase':y['phase'],'generation':q['generation'][0],'bad_stale':True,'position':y['seq']+1})
                yield emit('BAD_StaleRelease:'+c,stale)
    for cert in s['stops']:
        c=cert['child']; x=s['cfg'][c]
        if x['transferred'] is None:
            def transfer(n,c=c,cert=cert):n['cfg'][c]['transferred']=copy.deepcopy(cert)
            yield emit('Transfer:'+c,transfer)
        elif not x['active']:
            for bit in range(4):
                if not(x['objects']>>bit&1):
                    yield emit(f'Fetch:{c}:{bit}',lambda n,c=c,bit=bit:n['cfg'][c].__setitem__('objects',n['cfg'][c]['objects']|1<<bit))
            if x['objects']==15 and not x['ready_state']:
                yield emit('ReadyState:'+c,lambda n,c=c:n['cfg'][c].__setitem__('ready_state',True))
            if x['ready_state']:
                def activate(n,c=c,cert=cert):
                    y=n['cfg'][c];q=copy.deepcopy(cert['snapshot']['biz'])
                    if mutant=='drop_rho':q['obl']=[]
                    if mutant=='drop_hist':q['hist']=0
                    if mutant=='drop_dedup':q['dedup']={}
                    if mutant=='reset_budget':q['charged']=[0,0]
                    y['biz']=q;y['phase']='RECOVERING';y['active']=True;y['pending']=None;y['child']=None
                    y['genesis']=root({'parent_stop':cert['root'],'payload':q,'cfg':c})
                    n['activations'].append({'cfg':c,'parent':cert['parent'],'genesis':y['genesis']})
                    commit(n,c,'Activate')
                yield emit('Activate:'+c,activate)
    for c in heads(s):
        x=s['cfg'][c];b=x['biz']
        if not x['online']:continue
        if x['phase']=='RECOVERING':
            if not x['ready_use']:
                yield emit('ReadyUse:'+c,lambda n,c=c:n['cfg'][c].__setitem__('ready_use',True))
            if x['ready_use'] or mutant=='ready_confusion':
                def takeover(n,c=c):
                    n['cfg'][c]['phase']='ACTIVE';n['cfg'][c]['biz']['owner']=1;commit(n,c,'Takeover')
                yield emit('Takeover:'+c,takeover)
            if mutant=='ready_confusion' and not x['ready_use']:
                def confused(n,c=c):
                    n['ghost'].append({'kind':'Release','cfg':c,'a':1,'origin':[0,0,0,1],
                        'grant_ok':True,'ready_ok':False,'phase':'ACTIVE','generation':0,'position':n['cfg'][c]['seq']+1})
                yield emit('BAD_ReadyStateAsUse:'+c,confused)
        for a,at in enumerate(b['attempts']):
            if at['right']=='unconsumed' and s['gate_rights'][a]=='unconsumed':
                def consume(n,c=c,a=a):
                    n['cfg'][c]['biz']['attempts'][a]['right']='consumed';n['gate_rights'][a]='consumed'
                    n['network'][a]=1;n['send_facts'].append({'a':a,'original_boot':n['cfg'][c]['biz']['attempts'][a]['boot'],
                        'original_holder':n['cfg'][c]['biz']['attempts'][a]['holder'],'new_attempt':False})
                yield emit(f'ConsumeOriginalRight:{c}:{a}',consume)
            if s['network'][a]==2 and a not in s['recorded']:
                def record(n,c=c,a=a):
                    q=n['cfg'][c]['biz'];z=q['attempts'][a];z['state']='recorded'
                    z['result_origin']=([1,1,1,a] if mutant=='relabel_origin' else z['origin'][:]);n['recorded'].append(a)
                    z['quarantined']=not q['grants'][z['origin'][0]] or q['generation'][z['origin'][0]]!=z['origin'][2]
                    commit(n,c,'Record:'+str(a))
                yield emit(f'Record:{c}:{a}',record)
            if at['state']=='recorded':
                for kind in ('OUTCOME','DERIVATION'):
                    if [a,kind] in b['obl']:
                        def close(n,c=c,a=a,kind=kind):
                            n['cfg'][c]['biz']['obl'].remove([a,kind]);n['closed'].append([a,kind]);commit(n,c,'Close:'+kind)
                        yield emit(f'Close:{c}:{a}:{kind}',close)
    for a,network in enumerate(s['network']):
        if network==1:
            yield emit(f'LateProviderResult:{a}',lambda n,a=a:n['network'].__setitem__(a,2))

def key_scenario(leaked,governance,activated,pin,epoch_only=False):
    """Authentication predicates, separated from actual old RSM commit history."""
    signers=set(leaked); forged_stop=len(signers)>=3
    child_ready=forged_stop and governance
    new_activate=child_ready and activated
    accepts=new_activate and (pin=='O' or epoch_only or pin=='C')
    return {'old_stop_forged':forged_stop,'new_ready':child_ready,'new_activate':new_activate,
            'observer_accepts_C':accepts,'anchor':pin,'leaked':sorted(signers),
            'assumption_violated':len(signers)>1,
            'trace':['real Seal(O,D)','retire O','leak old signing identities',
                     'attempt forged Stop(O,C)','check governance','check Ready/Activate','check concrete anchor']}
