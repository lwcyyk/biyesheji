"""Audit scalar subprocess file opens; allow data only in the new sandbox/work tree."""
from pathlib import Path
import json,os,runpy,sys

script=Path(sys.argv[1]).resolve();audit=Path(sys.argv[2]).resolve()
work=Path(os.environ['FRODO_FI_SANDBOX']).resolve().parent
runtime=Path(sys.base_prefix).resolve()
assert script.is_relative_to(work) and audit.is_relative_to(work)
with audit.open('w',encoding='utf-8') as log:
 def hook(event,args):
  if event=='open' and not isinstance(args[0],int):
   p=Path(os.fsdecode(args[0])).resolve();mode=args[1];flags=args[2]
   write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
   allowed=p.is_relative_to(work) or (not write and p.is_relative_to(runtime))
   log.write(json.dumps(dict(path=str(p),write=bool(write),runtime=p.is_relative_to(runtime),allowed=allowed),ensure_ascii=False)+'\n');log.flush()
   if not allowed:raise PermissionError('Scalar replay opened a path outside work/runtime: '+str(p))
  if event in ('subprocess.Popen','os.system','socket.connect','socket.getaddrinfo'):raise PermissionError('Scalar replay attempted an external action: '+event)
 sys.addaudithook(hook)
 sys.argv=[str(script)]
 runpy.run_path(str(script),run_name='__main__')
