"""One-off owned-app cleanup repair. Shares the original cleanup budget."""
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0,r'D:\毕业设计\auth-lifecycle\src')
from auth_lifecycle.online_state.native_http import NativeHTTP
from auth_lifecycle.online_state.protocol import write_json

batch=Path(r'D:\毕业设计\mainline_native_unidentified_v1\raw\batch01')
policy=json.loads((batch/'BUDGET_AND_AUTHORIZATION.json').read_text())
client=NativeHTTP(batch,'cleanup',cookies=True,enabled=True)
credentials=json.loads(Path(r'D:\毕业设计\auth-lifecycle\.runtime\l1\secrets.json').read_text())
login=client.call('admin_login',payload={'type':'login','organization':'built-in','username':'admin',
    'password':credentials['casdoor_password'],'application':'app-built-in','autoSignin':True})
if login['http']!=200 or login['body'].get('status')!='ok':raise RuntimeError('CLEANUP_AUTH_UNAVAILABLE')
response=client.call('delete_application',payload={'owner':'admin','name':policy['application_name'],'organization':policy['organization']})
confirmed=client.call('owned_application')
result={'scope':'only original owned application','organization_field_added':True,
        'delete_response_http':response['http'],'delete_response_status':response['body'].get('status'),
        'application_absent':confirmed['http']==200 and confirmed['body'].get('status')=='ok' and confirmed['body'].get('data') is None,
        'original_cleanup':'raw/batch01/SCOPE_CLEANUP.json','sampling_repeated':False,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
write_json(batch.parent.parent/'cleanup_repair_RESULT.json',result)
print(json.dumps(result))
