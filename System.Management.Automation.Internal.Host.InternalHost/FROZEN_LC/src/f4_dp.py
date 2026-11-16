"""D2 cumulative-cost belief DP. No imports of the independent reference."""
import json
from functools import lru_cache

def validate(d):
    if not d.get('initial'):return 'EMPTY_INITIAL'
    states=d['states']
    for sid,s in states.items():
        for a,row in s.get('actions',{}).items():
            if row.get('enabled'):
                if not row.get('segments'):return 'EMPTY_SUCCESSOR'
                for seg in row['segments']:
                    if seg['to'] not in states or seg['obs'] not in d['observations']:return 'UNKNOWN_SUCCESSOR'
                    if any(step['cost']<0 for step in seg['steps']):return 'NEGATIVE_COST'
    return None

def decide(d,h,m,budget,compression=False,mutant='none'):
    invalid=validate(d)
    if invalid and mutant!='empty_post':return {'valid':False,'error':invalid,'feasible':None,'strategy':None}
    states=d['states']
    def normalized(B):
        if not compression and mutant not in ('drop_mode','drop_permission'):return tuple(sorted(set(B)))
        best={}
        for sid,z in sorted(B):
            s=states[sid]
            if mutant=='drop_mode':key=(s['phase'],tuple(s['obligations']),s['quota_mode'])
            elif mutant=='drop_permission':key=(s['phase'],s['mode'],tuple(s['obligations']))
            else:key=sid
            if key not in best or z>best[key][1]:best[key]=(sid,z)
        return tuple(sorted(best.values()))
    def terminal(B):
        return bool(B) and all(z<=m and states[sid]['goal'] and states[sid]['safe'] and states[sid]['post_inv']
            and (not states[sid]['obligations'] or mutant=='ignore_unknown') for sid,z in B)
    memo={}
    def win(B,j):
        budget.visit();B=normalized(B);key=(B,j)
        if key in memo:return memo[key]
        if terminal(B):memo[key]={'stop':True,'claimed_worst_cost':max(z for _,z in B)};return memo[key]
        if not B or j==0:memo[key]=None;return None
        if any(not states[sid]['safe'] for sid,_ in B):memo[key]=None;return None
        for a in d['actions']:
            if a=='STOP':continue
            posts={};costs=[];segments=[];legal=True
            for sid,z in B:
                row=states[sid].get('actions',{}).get(a)
                if not row or not row['enabled']:legal=False;break
                for seg in row['segments']:
                    if mutant=='omit_observation' and seg['obs']=='high':continue
                    if mutant!='ignore_prefix' and any(not q['safe'] for q in seg['steps']):legal=False;break
                    fee=0 if mutant=='zero_query_cost' else sum(q['cost'] for q in seg['steps'])
                    costs.append(fee);segments.append((seg,z,fee))
                if not legal:break
                if not row['segments'] and mutant!='empty_post':legal=False;break
            if not legal:continue
            for seg,z,fee in segments:
                total=(max(v for _,v in B)+max(costs)) if mutant=='stagewise_max' else z+fee
                if total>m:legal=False;break
                posts.setdefault(seg['obs'],[]).append((seg['to'],total))
            if not legal:continue
            if not posts and mutant!='empty_post':continue
            branches={};ok=True
            for obs,post in sorted(posts.items()):
                result=win(tuple(post),j-1)
                if result is None:ok=False;break
                branches[obs]=result
            if ok:
                memo[key]={'action':a,'next':branches,'claimed_worst_cost':max((v['claimed_worst_cost'] for v in branches.values()),default=max(z for _,z in B))};return memo[key]
        memo[key]=None;return None
    initial=tuple((x['state'],x['cost']) for x in d['initial'])
    if mutant=='worldwise':
        parts=[win((x,),h) for x in initial]
        feasible=all(x is not None for x in parts)
        strategy={'per_world':parts} if feasible else None
    else:
        strategy=win(initial,h);feasible=strategy is not None
    return {'valid':True,'error':invalid,'feasible':feasible,'strategy':strategy,'memo_states':len(memo)}
