"""Supplemental frozen M6 offline check: no network or runtime mutations."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0,r'D:\毕业设计\auth-lifecycle\src')
from auth_lifecycle.online_state.native_http import private_http_records,budget_path


def check(root):
    root=Path(root);batch=root/'transport';records=private_http_records(batch)
    policy=json.loads((batch/'BUDGET_AND_AUTHORIZATION.json').read_text())
    with sqlite3.connect('file:'+str(budget_path(batch,policy))+'?mode=ro',uri=True) as c:
        rows=c.execute('SELECT seq,http,error_type FROM requests ORDER BY seq').fetchall()
    checks=[{'name':'every_reserved_call_has_sealed_audit','pass':{r['sequence'] for r in records}=={r[0] for r in rows}},
            {'name':'all_budget_rows_have_outcome','pass':all(r[1] is not None for r in rows)}]
    details=[]
    for scenario in ('M6-01','M6-02'):
        case=root/scenario;trusted=case/'trusted'
        if not (trusted/'secure/native_profile.json').exists():continue
        profile=json.loads((trusted/'secure/native_profile.json').read_text())
        own=[r for r in records if r['actor']==profile['actor']['name'] and r['category']=='method' and r['operation'] in {'issue','refresh'}]
        secrets_to_check=[];counts={'access_token':0,'refresh_token':0,'id_token':0}
        for record in own:
            body=record['response'].get('body')
            if isinstance(body,dict):
                for field in counts:
                    value=body.get(field)
                    if isinstance(value,str) and value:
                        secrets_to_check.append(value.encode());counts[field]+=1
        files=[p for p in (trusted/'authority').glob('authority.db*')]
        inbox=trusted/'provider/native_inbox.jsonl'
        if inbox.exists():files.append(inbox)
        leaks=[]
        for p in files:
            data=p.read_bytes()
            if any(value in data for value in secrets_to_check):leaks.append(str(p))
        checks.append({'name':scenario+'_tokens_not_plaintext_in_database_or_inbox','pass':not leaks and bool(secrets_to_check)})
        details.append({'scenario':scenario,'actual_material_fields':counts,'files_checked':[str(p) for p in files],'leaks':leaks})
    return {'checks':checks,'details':details,'audit_record_count':len(records),'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL',
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'network_calls':0}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();r=check(a.root)
    print(json.dumps(r,indent=2));raise SystemExit(2 if r['status']=='FAIL' else 0)
