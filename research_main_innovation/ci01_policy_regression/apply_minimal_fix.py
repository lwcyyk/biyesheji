"""Apply ordinary correctness maintenance only after the recorded full-chain gate."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,shutil,difflib
ROOT=Path(__file__).resolve().parent
def main():
    raw=ROOT/'raw/baseline01/chain_results.json';data=json.loads(raw.read_text(encoding='utf-8'))
    ids=['M081','B02','B04'];by={x['id']:x for x in data['results']};witnesses=[]
    for name in ids:
        r=by[name]
        required=['route_resolved','subject_identified','global_permission_result','controller_dispatch','controller_enter','controller_permission_pass']
        if not r['synthetic_display_changed'] or r['actual']!='ALLOW':raise RuntimeError('effect witness absent')
        if not all(any(x['stage']==s and x['passed'] for x in r['stages']) for s in required):raise RuntimeError('full-chain gate incomplete')
        witnesses.append({'id':name,'required_stages':required,'synthetic_effect':True})
    if data['runtime_HTTP_attempts']!=0:raise RuntimeError('offline boundary violated')
    gate={'utc':datetime.now(timezone.utc).isoformat(),'source':str(raw),'source_sha256':sha256(raw.read_bytes()).hexdigest(),
      'gate':'CONFIRMED_FULL_OFFLINE_CHAIN_INCONSISTENCY','witnesses':witnesses,'maintenance_class':'ordinary existing-policy correctness fix','new_protocol_or_algorithm':False}
    (ROOT/'PATCH_GATE.json').write_text(json.dumps(gate,indent=2),encoding='utf-8')
    if (ROOT/'fixed').exists():raise RuntimeError('fixed copy already exists')
    shutil.copytree(ROOT/'baseline',ROOT/'fixed')
    old='if application == nil || isClientSessionApiAllowed(application, getSessionUser(ctx), urlPath) {'
    new='''if application == nil {
		// A missing application cannot turn its token-derived identity into an
		// unrestricted login. Reuse anonymous continuation for the login UI.
		if err := clearSessionOfToken(ctx); err != nil {
			responseError(ctx, err.Error())
			return false
		}
		return true
	}
	if isClientSessionApiAllowed(application, getSessionUser(ctx), urlPath) {'''
    target=ROOT/'fixed/routers/authz_filter.go';text=target.read_text(encoding='utf-8')
    if text.count(old)!=1:raise RuntimeError('unexpected patch anchor')
    target.write_text(text.replace(old,new),encoding='utf-8',newline='\n')
    original=(ROOT/'originals/routers/authz_filter.go').read_text(encoding='utf-8')
    fixed=original.replace(old,new)
    diff=''.join(difflib.unified_diff(original.splitlines(True),fixed.splitlines(True),fromfile='a/routers/authz_filter.go',tofile='b/routers/authz_filter.go'))
    (ROOT/'MINIMAL_PATCH.diff').write_text(diff,encoding='utf-8',newline='\n')
    (ROOT/'PATCH_HASHES.json').write_text(json.dumps({'file':'routers/authz_filter.go','pristine_sha256':sha256(original.encode()).hexdigest(),
      'pristine_plus_minimal_fix_sha256':sha256(fixed.encode()).hexdigest(),'instrumented_baseline_sha256':sha256(text.encode()).hexdigest(),
      'instrumented_fixed_sha256':sha256(target.read_bytes()).hexdigest(),'patch_sha256':sha256(diff.encode()).hexdigest()},indent=2),encoding='utf-8')
    print('gate passed; isolated minimal fix written')
if __name__=='__main__':main()
