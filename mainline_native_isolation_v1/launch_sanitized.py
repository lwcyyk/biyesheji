"""Launch M6 provisioning/scoring/measurement with an explicit environment."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--authorization-id',required=True)
    p.add_argument('--preflight',action='store_true');p.add_argument('--preflight-evidence')
    a=p.parse_args();report=Path(__file__).resolve().parent
    repo=Path(r'D:\毕业设计\auth-lifecycle')
    system=os.environ.get('SystemRoot',r'C:\Windows')
    env={'SystemRoot':system,'PATH':system+r'\System32;'+system+';'+system+r'\System32\WindowsPowerShell\v1.0',
         'PYTHONPATH':str(repo/'src'),'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1',
         'TEMP':str(report/'tmp'),'TMP':str(report/'tmp')}
    command=[sys.executable,'-B','-X','utf8',str(repo/'scripts/native_isolation.py'),'--out',a.out,
             '--authorization-id',a.authorization_id]
    if a.preflight:command.append('--preflight')
    else:command += ['--allow-native','--preflight-evidence',a.preflight_evidence]
    label='SANITIZED_PREFLIGHT' if a.preflight else 'SANITIZED_NATIVE'
    lock={'command':command,'environment':{k:{'value':v,'sha256':hashlib.sha256(v.encode()).hexdigest()} for k,v in env.items()},
          'close_fds':True,'creation_flags':'CREATE_NO_WINDOW','launcher_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (report/(label+'_LAUNCH.json')).write_text(json.dumps(lock,indent=2))
    with (report/(label+'.log')).open('wb') as log:
        child=subprocess.Popen(command,cwd=repo,env=env,close_fds=True,stdout=log,stderr=log,
                               creationflags=subprocess.CREATE_NO_WINDOW)
        lock['pid']=child.pid
        (report/(label+'_LAUNCH.json')).write_text(json.dumps(lock,indent=2))
        code=child.wait()
    print(json.dumps({'pid':child.pid,'exit_code':code,'log':str(report/(label+'.log'))}))
    return code


if __name__=='__main__':raise SystemExit(main())
