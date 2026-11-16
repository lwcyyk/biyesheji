"""M6 one-shot entry: synthetic preflight or separately enabled native batch."""
import argparse
import json
from auth_lifecycle.online_state.native_isolation import run_preflight,run_native


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--authorization-id',required=True)
    p.add_argument('--preflight',action='store_true');p.add_argument('--allow-native',action='store_true')
    p.add_argument('--preflight-evidence')
    a=p.parse_args()
    r=run_preflight(a.out,a.authorization_id) if a.preflight else run_native(a.out,a.authorization_id,a.preflight_evidence,a.allow_native)
    print(json.dumps({k:v for k,v in r.items() if k!='source'}))
