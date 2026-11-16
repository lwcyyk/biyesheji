"""Four read-only configuration/audit-session HTTP calls; no protection code."""
from pathlib import Path
from hashlib import sha256
import json,sys,shutil
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'ci01_contract_audit'))
import collect_evidence as e
sys.path.insert(0,str(e.PROJECT/'src'))
from auth_lifecycle.experiment import providers

def main():
    out=ROOT/'raw/config01';out.mkdir(parents=True,exist_ok=False)
    rec=e.Recorder(out);rec.limits={'setup':1,'measurement':2,'cleanup':1,'method':0}
    old=rec.instrument(providers.HTTP);p=providers.Casdoor()
    result={'status':'UNKNOWN','read_only':True}
    snap=[]
    for src in [Path(__file__),ROOT/'READ_ONLY_ADDENDUM.md',ROOT.parent/'ci01_contract_audit/collect_evidence.py',e.PROJECT/'src/auth_lifecycle/experiment/providers.py']:
        dst=out/'source_snapshot'/src.name;dst.parent.mkdir(exist_ok=True);shutil.copyfile(src,dst)
        snap.append({'source':str(src),'snapshot':str(dst.relative_to(out)),'sha256':sha256(dst.read_bytes()).hexdigest()})
    (out/'source_hashes.json').write_text(json.dumps(snap,indent=2),encoding='utf-8')
    try:
        with rec.stage('setup','admin_login','fixture'):p.admin_login()
        with rec.stage('measurement','organization_configuration','observer_only'):
            r=providers.required(p.admin('GET','get-organization?id=admin/l1-study'))
        if r.get('status')!='ok' or not isinstance(r.get('data'),dict):raise RuntimeError('read org failed')
        result['organization']={k:r['data'].get(k) for k in ['owner','name','dcrPolicy','defaultApplication','defaultTokenFormat']}
        with rec.stage('measurement','template_configuration','observer_only'):
            r=providers.required(p.admin('GET','get-application?id=admin/app-l1-0'))
        if r.get('status')!='ok' or not isinstance(r.get('data'),dict):raise RuntimeError('read app failed')
        result['application']={k:r['data'].get(k) for k in ['owner','name','grantTypes','enableSigninSession','enableSignUp','enableGuestSignin','enablePassword','enableConsent','cookieExpireInHours','enableExclusiveSignin','maxSessions','disableRefreshRotation']}
        rec.emit('configuration_projection',result)
        result['status']='OBSERVED'
    except Exception as error:
        result['error_type']=type(error).__name__
    finally:
        if p.logged_in:
            try:
                with rec.stage('cleanup','admin_logout','fixture'):
                    result['admin_logout']=e.public_response(p.admin_http.call('POST',p.base+'/api/logout'))
            except Exception as error:result['cleanup_error_type']=type(error).__name__
        result['http_costs']=dict(rec.counts);result['http_total']=sum(rec.counts.values())
        (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        rec.close();providers.HTTP.call=old
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
