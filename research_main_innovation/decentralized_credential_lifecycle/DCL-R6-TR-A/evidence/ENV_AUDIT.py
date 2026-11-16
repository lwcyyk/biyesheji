"""Read-only platform observation before the single frozen active entry."""
from EXEC_ADMIN import call,dump,E
import json
CODE=r'''
from pathlib import Path
import json,os,pwd,grp,subprocess,sys,resource
resource.setrlimit(resource.RLIMIT_AS,(1<<30,1<<30))
root=Path('/var/lib/dcl-r6/tr01');m=json.loads((root/'inputs/static_manifest.json').read_bytes())
def command(a):
 p=subprocess.run(a,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=5)
 return {'argv':a,'exit_code':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()}
version=command(['/usr/bin/systemctl','show','--property=Version','--value'])
failed=command(['/usr/bin/systemctl','list-units','--state=failed','--all','--no-pager','--no-legend'])
units=command(['/usr/bin/systemctl','list-units','dclr6batch13*','--all','--no-pager','--no-legend'])
assert version['exit_code']==0 and version['stdout'].strip()==m['systemd']
assert os.uname().release==m['kernel'] and os.uname().machine==m['architecture']
assert os.geteuid()==0 and sys.version_info[:3]==(3,12,3)
user=pwd.getpwuid(999);assert user.pw_gid==989 and os.getgrouplist(user.pw_name,989)==[989]
assert grp.getgrgid(989).gr_name=='dcl-r6'
assert not Path('/var/lib/dcl-r6/batch13').exists() and not Path('/etc/systemd/system/dclr6batch13.slice').exists()
assert not Path('/sys/fs/cgroup/dclr6batch13.slice').exists() and units['exit_code']==0 and not units['stdout'].strip()
roles=[];payload=[]
for p in Path('/proc').glob('[0-9]*'):
 try:
  status=dict(x.split(':',1) for x in (p/'status').read_text().splitlines() if ':' in x)
  args=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  if 999 in map(int,status['Uid'].split()):payload.append(int(p.name))
  if '--role' in args and any(a.startswith('/var/lib/dcl-r6/') and a.endswith('/guard.py') for a in args):roles.append(int(p.name))
 except (OSError,ValueError,KeyError):pass
assert not roles and not payload
assert any(x.split()[4]=='/sys/fs/cgroup' and ' - cgroup2 ' in x for x in Path('/proc/self/mountinfo').read_text().splitlines())
print(json.dumps({'status':'PASS_READ_ONLY_PLATFORM_AUDIT','boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'python':list(sys.version_info[:3]),'kernel':os.uname().release,'systemd':version,'failed_units':failed,'new_units':units,
 'payload_uid':999,'payload_gid':989,'groups':os.getgrouplist(user.pw_name,989),'payload_pids':payload,'root_roles':roles,
 'new_batch_absent':True,'cgroup_v2':True,'runtime_created':False},ensure_ascii=False))
'''
r=call(['/usr/bin/python3.12','-I','-S','-B','-c',CODE],'Read-only current platform, UID/GID, cgroup, failed units and fresh batch13 audit','READ_ONLY_PREFLIGHT')
if r['exit_code']!=0:
    dump(E/'ENVIRONMENT_AUDIT.json',{'status':'PREFLIGHT_FAILED','exit_code':r['exit_code']});print(r['stderr'][-3000:]);raise SystemExit(r['exit_code'])
q=json.loads(r['stdout']);dump(E/'ENVIRONMENT_AUDIT.json',q)
print(json.dumps({'status':q['status'],'boot_id':q['boot_id'],'failed_units':q['failed_units']['stdout'].strip()},ensure_ascii=False))
