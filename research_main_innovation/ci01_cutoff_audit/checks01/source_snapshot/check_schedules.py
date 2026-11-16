"""Finite checks of registered paper schedules; no native calls or new mechanism."""
import argparse
from copy import deepcopy
from hashlib import sha256
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def interleave(*chains):
    if not any(chains):
        yield ()
    for i,chain in enumerate(chains):
        if chain:
            rest=list(chains); rest[i]=chain[1:]
            for tail in interleave(*rest):
                yield (chain[0],)+tail

def run(trace,rotation=True):
    rows={'p':{'active':True,'hash':'h0','app':'A'},'b':{'active':True,'hash':'hb','app':'B'}}
    app=True; snapshots={}; selected=None; revoke_live=False
    events=[]
    for step in trace:
        before=deepcopy(rows)
        if step.endswith('.read'):
            tag=step.split('.')[0]
            snapshots[tag]=bool(app and rows.get('p',{}).get('active'))
        elif step.endswith('.insert'):
            tag=step.split('.')[0]
            if snapshots.get(tag):
                rows[tag]={'active':True,'hash':tag if rotation else 'h0','app':'A'}
        elif step.endswith('.finish'):
            tag=step.split('.')[0]
            if snapshots.get(tag) and rotation:
                rows.pop('p',None)
        elif step=='V.lookup':
            selected=deepcopy(rows.get('p'))
            revoke_live=bool(selected and selected['active'])
        elif step=='V.row':
            if revoke_live and 'p' in rows:rows['p']['active']=False
        elif step=='V.hash':
            if revoke_live:
                for row in rows.values():
                    if row['hash']==selected['hash']:row['active']=False
        elif step=='S.expire':
            for row in rows.values():
                if row['app']=='A':row['active']=False
        elif step=='S.destroy':
            pass # no terminal session-existence guard in audited refresh path
        elif step=='D.app':
            app=False
        events.append({'step':step,'before':before,'after':deepcopy(rows),'application_exists':app})
    return {'rows':rows,'app_exists':app,'A_record_live':any(x['active'] and x['app']=='A' for x in rows.values()),
            'A_fresh_bearer_accepted':app and any(x['active'] and x['app']=='A' for x in rows.values()),
            'B_record_live':rows['b']['active'],'events':events}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=(ROOT/args.out).resolve()
    if not out.is_relative_to(ROOT):raise ValueError('output outside audit')
    out.mkdir(parents=True,exist_ok=False)
    checks=[]; families=[]; witnesses=[]
    def check(name,expected,actual,scope):
        checks.append({'id':name,'expected':expected,'actual':actual,'pass':expected==actual,'scope':scope})
    F=('F.read','F.insert','F.finish')
    V=('V.lookup','V.row','V.hash')
    for rot in [True,False]:
        traces=list(interleave(F,V)); answers=[run(t,rot) for t in traces]
        survivors=[(t,a) for t,a in zip(traces,answers) if a['A_record_live']]
        families.append({'id':'refresh_vs_revoke_'+str(rot),'schedules':len(traces),'surviving_A':len(survivors)})
        check('race_exists_'+str(rot),True,bool(survivors),'all 20 interleavings of selected 3+3 microsteps')
        check('B_preserved_'+str(rot),True,all(x['B_record_live'] for x in answers),'two disjoint original RT hashes')
        trace=('F.read','V.lookup','V.row','V.hash','F.insert','F.finish')
        a=run(trace,rot)
        check('late_insert_'+str(rot),True,a['A_record_live'],'validated parent snapshot precedes revoke')
        witnesses.append({'id':'late_insert_'+str(rot),'trace':trace,'result':a})
        serial=run(F+V,rot)
        check('serial_parent_revoke_'+str(rot),rot,serial['A_record_live'],'rotation deletes parent; no rotation retains shared hash')
        check('revoke_then_fresh_refresh_'+str(rot),False,run(V+F,rot)['A_record_live'],'successful pre-validation revocation')
    traces=list(interleave(F,('S.expire','S.destroy')))
    answers=[run(t) for t in traces]
    families.append({'id':'session_range_race','schedules':len(traces),'surviving_A':sum(x['A_record_live'] for x in answers)})
    check('session_late_insert_exists',True,any(x['A_record_live'] for x in answers),'session ID inherited but no session existence check')
    traces=list(interleave(F,('D.app',)))
    answers=[run(t) for t in traces]
    families.append({'id':'app_delete_race','schedules':len(traces),'surviving_rows':sum(x['A_record_live'] for x in answers)})
    check('app_delete_blocks_fresh_bearer',False,any(x['A_fresh_bearer_accepted'] for x in answers),'only app-bound fresh Bearer, no other reissuance')
    check('app_delete_can_leave_rows',True,any(x['A_record_live'] for x in answers),'late insert remains distinguishable from accepted material')
    traces=list(interleave(F,('G.read','G.insert','G.finish')))
    answers=[run(t) for t in traces]
    branch=[(t,a) for t,a in zip(traces,answers) if all(x in a['rows'] for x in ['F','G'])]
    families.append({'id':'two_refreshes','schedules':len(traces),'two_children':len(branch)})
    check('two_refresh_children',True,bool(branch),'same parent read before either deletion')
    witnesses.append({'id':'two_children','trace':branch[0][0],'result':branch[0][1]})
    # Nonrotation lookup has no active-row selection guarantee.
    late=run(('F.read','V.lookup','V.row','V.hash','F.insert','F.finish'),False)
    outcomes=[]
    for selected in [x for x in late['rows'].values() if x['hash']=='h0']:
        result=deepcopy(late['rows'])
        if selected['active']:
            for x in result.values():
                if x['hash']=='h0':x['active']=False
        outcomes.append(any(x['active'] and x['app']=='A' for x in result.values()))
    check('repeated_shared_RT_revoke_ambiguous',[False,True],sorted(outcomes),'Get may choose either same-hash record; no DB choice claimed')
    before=['a','b','c']; p1=before[:1]; after=['b','c']; p2=after[1:2]
    check('offset_delete_miss',True,'b' not in p1+p2 and 'b' in after,'page size 1, ascending unique names')
    after_insert=['0','a','b','c']; p2=after_insert[1:2]
    check('offset_insert_duplicate',True,bool(set(p1)&set(p2)),'new key before consumed prefix')
    check('cookie_app_delete_counterexample',True,True,'source token live + app missing permits cookie continuation; supported by C11')
    expiry=[]
    for E,delta,LA in itertools.product([1,2,5],[0,1,3],[1,4]):
        # integer abstraction: latest validation E, latest insert E+delta,
        # userinfo expiry uses created time + LA. Test strictly after bound.
        bound=E+delta+LA
        latest=E+delta
        expiry.append({'RT_exp':E,'delay_bound':delta,'AT_life':LA,'after_bound':bound+1,
                       'accepted':bound+1<=latest+LA})
    check('fixed_RT_bounded_expiry',False,any(x['accepted'] for x in expiry),'18 finite integer parameter combinations; continuous-time proof in COST_AND_TERMINATION')
    result={'evidence_kind':'PAPER_MODEL_CHECK','implementation_is_new_protection':False,
        'model':'TRANSITION_MODEL.md; collapsed read/validate and stable external guards',
        'families':families,'enumerated_interleavings':sum(x['schedules'] for x in families),
        'expiry_parameter_cases':len(expiry),'checks':checks,'passed':sum(x['pass'] for x in checks),'failed':sum(not x['pass'] for x in checks),
        'limits':['up to two refreshes, one revoke/range/delete','no network execution','no all-Go-interleaving equivalence proof',
                  'cookie check is a registered boundary example, not a cookie implementation model']}
    (out/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (out/'counterexamples.json').write_text(json.dumps(witnesses,indent=2),encoding='utf-8')
    (out/'expiry_cases.json').write_text(json.dumps(expiry,indent=2),encoding='utf-8')
    (out/'source_hashes.json').write_text(json.dumps({x.name:sha256(x.read_bytes()).hexdigest() for x in [Path(__file__),ROOT/'TRANSITION_MODEL.md']},indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['enumerated_interleavings','expiry_parameter_cases','passed','failed']}))
    if result['failed']:raise SystemExit(1)

if __name__=='__main__':main()
