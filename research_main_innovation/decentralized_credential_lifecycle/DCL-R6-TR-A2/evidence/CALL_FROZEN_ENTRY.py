"""One authorized frozen host entry call; no retry/resume or target-source edits."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime,timezone

E=Path(__file__).resolve().parent
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\ra01')
entry=W/'host/windows_entry.py'
lock=json.loads((W/'inputs/execution_lock.json').read_bytes())
assert hashlib.sha256(entry.read_bytes()).hexdigest()==lock['windows_entry_sha256']
assert json.loads((E/'DEPLOYMENT_RESULT.json').read_bytes())['status']=='PASS_STATIC_DEPLOYMENT_ONLY'
auth=json.loads((E/'execution_authorization.json').read_bytes())
assert auth['scope']=='PT_STARTUP_DIAGNOSTIC_ONLY' and auth['Full_conditional_chain_explicitly_approved'] is False
argv=[sys.executable,'-X','utf8',str(entry),'--activate']
started=datetime.now(timezone.utc).isoformat();tick=time.perf_counter()
row={'argv':argv,'start_utc':started,'scope':auth['scope'],'max_calls':1,'call_number':1,'retry':False,'host_env_delta':{'PYTHONDONTWRITEBYTECODE':'1'},'native_argv':lock['windows_single_call']}
with (E/'ACTIVE_ENTRY_INVOCATION.json').open('x',encoding='utf-8') as f:json.dump(row,f,ensure_ascii=False,indent=2)
env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
with (E/'active_host.stdout.raw').open('xb') as out,(E/'active_host.stderr.raw').open('xb') as err:
    process=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=env)
    code=process.wait()
result={**row,'exit_code':code,'host_entry_pid':process.pid,'end_utc':datetime.now(timezone.utc).isoformat(),'host_elapsed_seconds':time.perf_counter()-tick}
(E/'ACTIVE_ENTRY_RETURN.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False),flush=True)
raise SystemExit(code)
