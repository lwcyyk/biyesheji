"""Fixed API evidence schedules T1-T5. No candidate protection mechanism.

Reuses the existing native adapter and redacting recorder. All mutable native
objects are created in this run. Authoritative DB reads occur after the schedules.
"""
import argparse
import base64
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import secrets
import shutil
import sqlite3
import sys
import uuid
from urllib.parse import urlencode

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'ci01_contract_audit'
PROJECT=Path(r'D:\毕业设计\auth-lifecycle')
sys.path.insert(0,str(OLD))
import collect_evidence as evidence
sys.path.insert(0,str(PROJECT/'src'))
from auth_lifecycle.experiment import providers

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',required=True)
    args=parser.parse_args()
    if not evidence.re.fullmatch(r'[a-zA-Z0-9_-]+',args.run_id):
        raise ValueError('invalid run id')
    out=ROOT/'raw'/args.run_id
    out.mkdir(parents=True,exist_ok=False)
    snap=[]
    for p in [Path(__file__),ROOT/'TRANSITION_MODEL.md',ROOT/'SAMPLING_PLAN.md',
              OLD/'collect_evidence.py',PROJECT/'src/auth_lifecycle/experiment/providers.py']:
        q=out/'source_snapshot'/p.name
        q.parent.mkdir(exist_ok=True)
        shutil.copyfile(p,q)
        snap.append({'source':str(p),'snapshot':str(q.relative_to(out)),'sha256':evidence.file_hash(q)})
    (out/'source_hashes.json').write_text(json.dumps(snap,indent=2),encoding='utf-8')
    rec=evidence.Recorder(out)
    rec.limits={'setup':45,'method':45,'measurement':85,'cleanup':45}
    original=rec.instrument(providers.HTTP)
    p=providers.Casdoor()
    actors=[]
    intents=[]
    apps=[]
    deleted=set()
    pairs=[]
    obs=[]
    scopes=[]
    result={'status':'UNKNOWN','new_mechanism':False,'cases':{},'cleanup':{},'constraints':'SAMPLING_PLAN.md'}
    app_fields=['owner','name','clientId','organization','grantTypes','expireInHours','refreshExpireInHours',
                'tokenFormat','cert','disableRefreshRotation','enableSignUp','isShared','enableExclusiveSignin','maxSessions']

    def call(cat,name,fn):
        with rec.stage(cat,name,'observer_only' if cat=='measurement' else 'fixture' if cat in {'setup','cleanup'} else 'runner'):
            response=fn()
            if cat=='method':
                rec.emit('runner_response',evidence.public_response(response),runner_visible=True)
            return response

    def ok(response):
        body=providers.required(response)
        if body.get('status')!='ok':
            raise RuntimeError('native business response not ok')
        return body

    def actor(case):
        name='l1-cut-'+uuid.uuid4().hex[:16]
        intents.append(name)
        rec.case=case
        rec.emit('fixture_account_intent',{'name':name})
        a=call('setup','create_'+case,lambda:p.create_actor(name))
        actors.append(a)
        return a

    def remember(label,response,a,client,origin):
        body=providers.required(response)
        if not body.get('access_token') or not body.get('refresh_token'):
            raise RuntimeError('expected issued pair missing')
        item={'label':label,'body':body,'actor':a,'client':client}
        pairs.append(item)
        ac,rc=providers.claims(body['access_token']),providers.claims(body['refresh_token'])
        rec.emit('material_observed',{'label':label,'origin':origin,'actor':a['name'],'app':p.clients[client]['native_id'],
            'access_ref':evidence.digest(body['access_token']),'refresh_ref':evidence.digest(body['refresh_token']),
            'at_exp':ac.get('exp'),'rt_exp':rc.get('exp'),'at_iat':ac.get('iat'),'rt_iat':rc.get('iat'),
            'jwt_fields_status':'decoded metadata; native acceptance checked separately'},runner_visible=True)
        return item

    def issue(label,a,client):
        return remember(label,call('method','issue_'+label,lambda:p.issue(a,client)),a,client,'fresh approved password grant')

    def refresh(label,item,endpoint='refresh_token',expect_pair=True):
        client=item['client']
        response=call('method','refresh_'+label+'_'+endpoint,lambda:p.http.call('POST',p.base+'/api/login/oauth/'+endpoint,
            form={'grant_type':'refresh_token','client_id':p.clients[client]['id'],'refresh_token':item['body']['refresh_token'],'scope':'openid'}))
        has_pair=bool(response.get('body',{}).get('access_token'))
        if expect_pair or has_pair:
            return remember(label,response,item['actor'],client,item['label']+'.RT')
        return evidence.public_response(response)

    def accepted(point,item,http=None,query=False,cookie_only=False):
        agent=http or providers.HTTP()
        url=p.base+'/api/userinfo'
        headers={}
        if query:
            url+='?'+urlencode({'accessToken':item['body']['access_token']})
        elif not cookie_only:
            headers={'Authorization':'Bearer '+item['body']['access_token']}
        response=call('measurement',point+'_'+item['label'],lambda:agent.call('GET',url,headers=headers))
        body=response.get('body',{})
        value=response['http']==200 and body.get('sub')==item['actor']['id']
        row={'point':point,'label':item['label'],'http':response['http'],'accepted':value,
             'subject_matches':body.get('sub')==item['actor']['id'],
             'path':'cookie_only' if cookie_only else 'AT_query' if query else 'fresh_Bearer',
             'response':evidence.public_response(response)}
        row['event_seq']=rec.emit('independent_acceptance',row)
        obs.append(row)
        return value

    def revoke(item):
        return call('method','revoke_'+item['label'],lambda:p.revoke(item['body']['refresh_token'],item['client']))

    def listing(a,page=1,size=100):
        client=p.clients[1]
        basic=base64.b64encode((client['id']+':'+client['secret']).encode()).decode()
        query=urlencode({'owner':'admin','organization':p.organization,'field':'user','value':a['name'],
                         'pageSize':size,'p':page,'sortField':'name','sortOrder':'ascend'})
        response=call('measurement',f'list_page_{page}_size_{size}',lambda:providers.HTTP().call('GET',p.base+'/api/get-tokens?'+query,
                              headers={'Authorization':'Basic '+basic}))
        body=ok(response)
        rows=body.get('data')
        if not isinstance(rows,list) or any(r.get('user')!=a['name'] or r.get('organization')!=p.organization for r in rows):
            raise RuntimeError('listing scope violation or missing rows')
        projected=[{'name':r['name'],'expiresIn':r.get('expiresIn'),'application':r.get('application'),
                    'sessionId_present':bool(r.get('sessionId')),
                    'access_ref':evidence.digest(r.get('accessToken','')),'refresh_ref':evidence.digest(r.get('refreshToken',''))} for r in rows]
        rec.emit('scoped_listing',{'actor':a['name'],'page':page,'size':size,'data2':body.get('data2'),'rows':projected})
        return rows

    try:
        evidence.load_environment(p,rec,out,providers.PRIVATE,providers)
        template=deepcopy(p.clients[0]['configuration'])
        original_config={k:template.get(k) for k in app_fields}
        p.clients=[]
        for label,nonrot in [('A',False),('B',False),('N',True)]:
            name='l1-cut-app-'+uuid.uuid4().hex[:14]
            a=deepcopy(template)
            a.update(name=name,displayName='Owned cutoff audit '+label,clientId='l1-cut-client-'+uuid.uuid4().hex[:14],
                     clientSecret=secrets.token_urlsafe(30),grantTypes=['password','refresh_token'],
                     disableRefreshRotation=nonrot,enableSignUp=False,isShared=False,expireInHours=1,refreshExpireInHours=1)
            apps.append(a)
            rec.emit('fixture_application_intent',{'name':name,'organization':a['organization']})
            ok(call('setup','add_app_'+label,lambda:p.admin('POST','add-application',a)))
            current=ok(call('setup','read_app_'+label,lambda:p.admin('GET','get-application?id=admin/'+name)))['data']
            if bool(current.get('disableRefreshRotation',False))!=nonrot:
                raise RuntimeError('rotation configuration readback mismatch')
            p.clients.append({'id':current['clientId'],'secret':current['clientSecret'],'native_id':name,'configuration':current})
            scopes.append({k:current.get(k) for k in app_fields})
        (out/'profiles.lock.json').write_text(json.dumps(scopes,ensure_ascii=False,indent=2),encoding='utf-8')

        a=actor('C10_nonrotation')
        a0=issue('C10_A0',a,2); b0=issue('C10_B0',a,2)
        a1=refresh('C10_A1',a0); a2=refresh('C10_A2',a1)
        before=[accepted('before_shared_hash_revoke',x) for x in [a0,a1,a2,b0]]
        revoke(a0)
        after=[accepted('after_shared_hash_revoke',x) for x in [a0,a1,a2,b0]]
        retry=refresh('C10_after_revoke',a2,expect_pair=False)
        result['cases']['C10']={'before':before,'after':after,
            'shared_rt':len({x['body']['refresh_token'] for x in [a0,a1,a2]})==1,
            'rt_exp_equal':len({providers.claims(x['body']['refresh_token']).get('exp') for x in [a0,a1,a2]})==1,
            'post_revoke_refresh_issued':isinstance(retry,dict) and 'body' in retry}

        a=actor('C11_application_cutoff')
        a0=issue('C11_A0',a,0); b0=issue('C11_B0',a,1)
        accepted('before_app_change',a0); accepted('before_app_change',b0)
        browser=providers.HTTP(cookies=True)
        accepted('cookie_seed_before_change',a0,http=browser,query=True)
        cookie_before=accepted('cookie_before_change',a0,http=browser,cookie_only=True)
        changed=deepcopy(p.clients[0]['configuration']); changed['grantTypes']=['password']
        ok(call('method','remove_refresh_grant_A',lambda:p.admin('POST','update-application?id=admin/'+changed['name'],changed)))
        readback=ok(call('measurement','read_grant_change',lambda:p.admin('GET','get-application?id=admin/'+changed['name'])))['data']
        generic=refresh('C11_generic_after_disable',a0,endpoint='access_token',expect_pair=False)
        # This sequence is frozen for the expected rejected generic branch. Any
        # unexpected issuance remains in the evidence and changes the next input.
        source=generic if isinstance(generic,dict) and 'body' in generic else a0
        a1=refresh('C11_dedicated_after_disable',source,expect_pair=False)
        if not (isinstance(a1,dict) and 'body' in a1):
            a1=source
        browser=providers.HTTP(cookies=True)
        accepted('cookie_seed_current',a1,http=browser,query=True)
        cookie_current=accepted('cookie_current_before_delete',a1,http=browser,cookie_only=True)
        ok(call('method','delete_owned_app_A',lambda:p.admin('POST','delete-application',{'owner':'admin','name':changed['name'],'organization':p.organization})))
        absent=ok(call('measurement','verify_app_A_absent',lambda:p.admin('GET','get-application?id=admin/'+changed['name'])))['data'] is None
        if absent:deleted.add(changed['name'])
        bearer_after=accepted('after_app_delete',a1)
        cookie_after=accepted('after_app_delete',a1,http=browser,cookie_only=True)
        b_after=accepted('after_app_delete',b0)
        r1=refresh('C11_dedicated_deleted',a1,expect_pair=False)
        r2=refresh('C11_generic_deleted',a1,endpoint='access_token',expect_pair=False)
        result['cases']['C11']={'readback_grantTypes':readback.get('grantTypes'),'generic_issued_after_disable':isinstance(generic,dict) and 'body' in generic,
            'dedicated_issued_after_disable':a1 is not source,'cookie_before':cookie_before,'cookie_current_before_delete':cookie_current,
            'app_absent':absent,'bearer_after_delete':bearer_after,'cookie_after_delete':cookie_after,'B_after_delete':b_after,
            'dedicated_issued_after_delete':isinstance(r1,dict) and 'body' in r1,'generic_issued_after_delete':isinstance(r2,dict) and 'body' in r2}

        a=actor('C12_pagination')
        pp=[issue('C12_T'+str(i),a,1) for i in range(3)]
        full_before=listing(a)
        page1=listing(a,page=1,size=1)
        if len(full_before)!=3 or len(page1)!=1 or page1[0]['name']!=full_before[0]['name']:
            raise RuntimeError('pagination precondition mismatch')
        first=page1[0]
        ok(call('method','delete_returned_first_row',lambda:p.admin('POST','delete-token',{
            'owner':first['owner'],'name':first['name'],'organization':first['organization']})))
        page2=listing(a,page=2,size=1)
        full_after=listing(a)
        missed=full_before[1]['name'] not in {r['name'] for r in page1+page2} and full_before[1]['name'] in {r['name'] for r in full_after}
        remaining=next(x for x in pp if x['body']['access_token']==full_after[0]['accessToken'])
        revoke(remaining)
        inactive=listing(a)
        result['cases']['C12']={'initial_count':len(full_before),'after_delete_count':len(full_after),
            'offset_skipped_still_present_row':missed,'page1_names':[r['name'] for r in page1],
            'page2_names':[r['name'] for r in page2],'missed_name':full_before[1]['name'],
            'invalidated_rows_still_listed':sum(r.get('expiresIn')==0 for r in inactive),
            'test_sort':'name ascend','source_ids_empty':all(not r.get('sessionId') for r in inactive)}
        rec.emit('declared_test_intervals_ended',{'cases':list(result['cases'])})
        after=ok(call('setup','verify_old_template_unchanged',lambda:p.admin('GET','get-application?id=admin/app-l1-0')))['data']
        result['shared_application_unchanged']=all(original_config[k]==after.get(k) for k in app_fields)
        result['status']='OBSERVED'
    except Exception as e:
        result['error_type']=type(e).__name__
        rec.emit('case_error',{'exception_type':type(e).__name__})
    finally:
        rec.case='cleanup'
        for name in intents:
            a=next((x for x in actors if x['name']==name),None)
            try:
                if a is None:
                    found=ok(call('cleanup','lookup_attempted_actor',lambda:p.admin('GET','get-user?id='+p.organization+'/'+name))).get('data')
                    if found:
                        a={'name':name,'id':found['id']}; p.owned[name]=a['id']; actors.append(a)
                if a:
                    call('cleanup','disable_owned_actor',lambda:p.root_stop(a))
                    call('cleanup','delete_owned_actor',lambda:p.remove_actor(a))
                    found=ok(call('cleanup','verify_actor_absent',lambda:p.admin('GET','get-user?id='+p.organization+'/'+name))).get('data')
                    result['cleanup'][name]={'deleted':found is None}
            except Exception as e:
                result['cleanup'][name]={'error_type':type(e).__name__}
        for item in pairs:
            try:
                accepted('after_fixture_cleanup',item)
            except Exception as e:
                rec.emit('cleanup_measurement_error',{'label':item['label'],'exception_type':type(e).__name__})
        for a in apps:
            try:
                if a['name'] not in deleted:
                    ok(call('cleanup','delete_owned_application',lambda:p.admin('POST','delete-application',{'owner':a['owner'],'name':a['name'],'organization':a['organization']})))
                found=ok(call('cleanup','verify_application_absent',lambda:p.admin('GET','get-application?id=admin/'+a['name']))).get('data')
                result['cleanup'][a['name']]={'deleted':found is None}
            except Exception as e:
                result['cleanup'][a['name']]={'error_type':type(e).__name__}
        if p.logged_in:
            try:
                result['admin_logout']=evidence.public_response(call('cleanup','logout_admin',lambda:p.admin_http.call('POST',p.base+'/api/logout')))
            except Exception as e:
                result['admin_logout']={'error_type':type(e).__name__}
        try:
            with sqlite3.connect('file:'+str(providers.PRIVATE/'casdoor-l1.db')+'?mode=ro',uri=True) as db:
                state=[]
                for a in actors:
                    rows=db.execute('SELECT name,application,expires_in,session_id FROM token WHERE organization=? AND user=?',(p.organization,a['name'])).fetchall()
                    users=db.execute('SELECT count(*) FROM user WHERE owner=? AND name=?',(p.organization,a['name'])).fetchone()[0]
                    state.append({'actor':a['name'],'user_rows':users,'token_rows':len(rows),'nonzero_token_rows':sum(x[2]>0 for x in rows),'nonempty_session_ids':sum(bool(x[3]) for x in rows)})
                    rec.local_counts['cleanup_readonly_sql']+=2
                result['cleanup_db']=state
                rec.emit('observer_cleanup_database',{'rows':state})
        except Exception as e:
            result['cleanup_db_error']=type(e).__name__
        result['http_costs']=dict(rec.counts); result['http_total']=sum(rec.counts.values())
        result['local_costs']=dict(rec.local_counts); result['limits']=rec.limits
        (out/'observations.json').write_text(json.dumps(obs,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        rec.close(); providers.HTTP.call=original
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
