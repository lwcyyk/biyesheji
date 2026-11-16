"""Replay unmodified copies, strictly within the new review directory."""
from pathlib import Path
import json, hashlib, subprocess, sys, os, time
R=Path(__file__).resolve().parents[1]; E=R/'evidence'
S=Path('D:/毕业设计/crypto_fi_official_profile_correctness')
T=E/'author_replay/crypto_fi_official_profile_correctness'
sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
logs=[]
for name in ['compute_profile_certificates','verify_profile_certificates']:
 start=time.perf_counter()
 with (T/'evidence'/f'{name}.replay.log').open('wb') as f:
  p=subprocess.run([sys.executable,str(T/'evidence'/f'{name}.py')],cwd=T,
    stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8'})
 logs.append(dict(script=name,exit_code=p.returncode,seconds=time.perf_counter()-start))
 print(name,'exit',p.returncode,'seconds',logs[-1]['seconds'])
 if p.returncode: break
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
same=(T/'OFFICIAL_PROFILE_CERTIFICATES.json').exists() and (T/'OFFICIAL_PROFILE_CERTIFICATES.json').read_bytes()==(S/'OFFICIAL_PROFILE_CERTIFICATES.json').read_bytes()
out=dict(status='PASS' if all(x['exit_code']==0 for x in logs) and len(logs)==2 and same else 'FAIL',
 scripts=logs,entire_certificate_byte_identical=same,
 original_certificate_sha256=sha(S/'OFFICIAL_PROFILE_CERTIFICATES.json'),
 original_generator_sha256=sha(S/'evidence/compute_profile_certificates.py'),
 copied_generator_sha256=sha(T/'evidence/compute_profile_certificates.py'),
 original_verifier_sha256=sha(S/'evidence/verify_profile_certificates.py'),
 copied_verifier_sha256=sha(T/'evidence/verify_profile_certificates.py'),
 original_paths_read_only=True,output_root=str(T))
(E/'AUTHOR_REPLAY_RESULT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out['status'],'entire certificate byte-identical:',same)
