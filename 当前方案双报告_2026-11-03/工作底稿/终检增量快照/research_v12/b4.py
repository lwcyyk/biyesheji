"""Safe semantic frontier compression for the inherited monotone B model.
No native-API changes. Global lexical expansion preserves the original objective.
"""
import bootstrap
from itertools import combinations
from auth_lifecycle.b.model import prepare,ModelError
from auth_lifecycle.b import engine,checker
from auth_lifecycle.schema import canonical,digest
from b_units import SharedWork
from kernel import Meter,Cutoff

def partition(m,meter):
    groups={}
    for name,p in sorted(m['paths'].items()):
        meter.tick('class_path_checks')
        op=p['delegate'];can_merge=op['requests']==op['approvals']==0
        key=canonical(dict(p,grants=sorted(p['grants']))) if can_merge else 'singleton:'+name
        groups.setdefault(key,[]).append(name)
    return list(groups.values())

def expand(classes,chosen):
    """Lex-min list covering exactly chosen classes. Include global prefix aliases
    until every selected class has appeared. Not 'one minimum per class'."""
    lookup={p:i for i in chosen for p in classes[i]};seen=set();out=[]
    for p in sorted(lookup):
        out.append(p);seen.add(lookup[p])
        if seen==set(chosen):break
    return out

def check_compression(spec,certificate):
    """Raw-path checker, no partition/expand/solve calls."""
    try:
        m=prepare(spec)
        if certificate.get('schema')!='B4-classes/1' or certificate.get('model_digest')!=digest(m):return False
        groups=certificate['classes'];flat=[p for g in groups for p in g]
        if sorted(flat)!=sorted(m['paths']) or any(not g for g in groups):return False
        for g in groups:
            if len(g)==1:continue
            first=m['paths'][g[0]]
            for name in g:
                p=m['paths'][name]
                if p['task']!=first['task'] or set(p['grants'])!=set(first['grants']) or p['environment']!=first['environment'] or p['delegate']!=first['delegate']:return False
                if p['delegate']['requests'] or p['delegate']['approvals']:return False
        selected=certificate.get('selected_classes');out=certificate.get('expanded_configuration')
        if selected is not None:
            if len(selected)!=len(set(selected)) or any(type(i)!=int or not 0<=i<len(groups) for i in selected):return False
            remaining=set(selected);expected=[]
            for name in sorted(p for i in selected for p in groups[i]):
                expected.append(name)
                for i in list(remaining):
                    if name in groups[i]:remaining.remove(i)
                if not remaining:break
            if out!=expected:return False
        return True
    except (ModelError,KeyError,TypeError,ValueError):return False

def interfaces(m):
    """B4-1 diagnostic: balanced task split, explicit shared effects/envs.
    Nonzero interfaces use a complete global solve; no unjustified local gluing.
    """
    tasks=sorted(m['tasks']);left=set(tasks[:max(1,len(tasks)//2)]);right=set(tasks)-left
    def resources(ts):
        paths=[p for p in m['paths'].values() if p['task'] in ts]
        gs={g for p in paths for g in p['grants']};es={p['environment'] for p in paths}
        us={u for u,x in m['revocations'].items() if gs&set(x['affects'])}
        return us,es
    lu,le=resources(left);ru,re=resources(right)
    shared_envs=[e for e in le&re if m['environments'][e]['kind']=='isolated' or m['environments'][e]['create']['requests'] or m['environments'][e]['create']['approvals']]
    return {'task_partition':[sorted(left),sorted(right)],'shared_native_effect_units':sorted(lu&ru),'shared_environment_effects':sorted(shared_envs),'interface_width':len(lu&ru)+len(shared_envs),'shared_global_budgets':True,'implementation':'diagnostic only; global planner always verifies; B3 zero-interface comparator retained'}

def solve(spec,meter=None):
    meter=meter or Meter()
    try:
        m=prepare(spec);classes=partition(m,meter);cert={'schema':'B4-classes/1','model_digest':digest(m),'classes':classes}
        if not check_compression(m,cert):raise AssertionError('invalid class certificate')
        meter.tick('compression_certificate_checks');best=None;work=SharedWork(meter)
        for mask in range(1<<len(classes)):
            meter.tick('quotient_configurations');chosen=[i for i in range(len(classes)) if mask&(1<<i)];C=expand(classes,chosen)
            if {m['paths'][p]['task'] for p in C}!=set(m['tasks']):continue
            # G lower bound is exact for this configuration; safe incumbent pruning.
            G=len(engine.resources(m,C)[2])
            if best and (G,C)>=best[0]:meter.tick('quotient_objective_prunes');continue
            delivery=engine.deliver(m,C,work)
            if delivery is None:continue
            ck=checker.check_delivery(m,delivery,work=work)
            if ck['verdict']!='ACCEPTED':raise AssertionError(ck)
            best=((ck['metrics']['G'],C),delivery,ck['metrics'],chosen)
        if best is None:return {'status':'IMPOSSIBLE','optimal':True,'certificate':cert,'stats':dict(meter.counts),'interface':interfaces(m)}
        cert.update(selected_classes=best[3],expanded_configuration=best[1]['configuration'])
        if not check_compression(m,cert):raise AssertionError('invalid expansion')
        return {'status':'FEASIBLE','configuration':best[1]['configuration'],'delivery':best[1],'metrics':best[2],'optimal':True,'certificate':cert,'stats':dict(meter.counts),'interface':interfaces(m),'original_paths':len(m['paths']),'semantic_classes':len(classes)}
    except ModelError as e:return {'status':'UNKNOWN','reason':str(e)}
    except Cutoff as e:return {'status':'INCONCLUSIVE','reason':str(e),'stats':dict(meter.counts)}
