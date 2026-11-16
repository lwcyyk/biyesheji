"""Record exact native argv and raw streams; invoke only the approved frozen workflow."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import subprocess
import sys

E=Path(__file__).resolve().parent
P=E.parent
PREFIX=[r'C:\Windows\System32\wsl.exe','--distribution','Ubuntu-24.04','--exec']
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))


def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def call(argv,purpose,classification):
    plan=load(E/'COMMAND_PLAN.json') if (E/'COMMAND_PLAN.json').exists() else {'schema':'B06-command-plan/1','commands':[]}
    order=len(plan['commands'])+1
    exact=PREFIX+argv
    row={'order':order,'argv':exact,'purpose':purpose,'classification':classification,
         'start_utc':datetime.now(timezone.utc).isoformat(),'automatic_retry':False}
    plan['commands'].append(row.copy());dump(E/'COMMAND_PLAN.json',plan)
    base=E/'commands'/f'{order:02}'
    with Path(str(base)+'.stdout.raw').open('xb') as out,Path(str(base)+'.stderr.raw').open('xb') as err:
        process=subprocess.Popen(exact,stdin=subprocess.DEVNULL,stdout=out,stderr=err)
        row['wsl_client_pid']=process.pid
        row['exit_code']=process.wait()
    row['end_utc']=datetime.now(timezone.utc).isoformat()
    row['elapsed_ms']=(datetime.fromisoformat(row['end_utc'])-datetime.fromisoformat(row['start_utc'])).total_seconds()*1000
    for name in ['stdout','stderr']:
        q=Path(str(base)+'.'+name+'.raw');raw=q.read_bytes()
        row[name]=raw.decode('utf-8',errors='replace');row[name+'_sha256']=hashlib.sha256(raw).hexdigest()
        row[name+'_file']=q.relative_to(P).as_posix()
    dump(str(base)+'.result.json',row)
    print(json.dumps({'order':order,'exit_code':row['exit_code'],'elapsed_ms':row['elapsed_ms'],
                      'purpose':purpose,'stdout':row['stdout']},ensure_ascii=False),flush=True)
    return row


ENV=r'''
import hashlib,json,os,platform,pwd,grp,resource,sys
from pathlib import Path
e=Path('/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-batch06/evidence')
lock=json.loads((e/'BASELINE_LOCK.json').read_text());rows=[]
for row in lock['source_files']:
 p=Path('/var/lib/dcl-r6/ri01')/row['relative'];s=p.stat()
 rows.append({'path':str(p),'uid':s.st_uid,'gid':s.st_gid,'mode':s.st_mode&0o777,
              'regular':p.is_file(),'symlink':p.is_symlink(),
              'acl':[n for n in os.listxattr(p) if n.startswith('system.posix_acl_')]})
dirs=[]
for name in ['/var','/var/lib','/var/lib/dcl-r6','/var/lib/dcl-r6/ri01','/var/lib/dcl-r6/ri01/src','/var/lib/dcl-r6/ri01/src/__pycache__','/var/lib/dcl-r6/ri01/inputs']:
 p=Path(name);s=p.stat();dirs.append({'path':name,'uid':s.st_uid,'gid':s.st_gid,'mode':s.st_mode&0o777,
                                  'symlink':p.is_symlink(),'acl':[n for n in os.listxattr(p) if n.startswith('system.posix_acl_')]})
uids={}
for uid in [999,65534]:
 p=pwd.getpwuid(uid);uids[str(uid)]={'name':p.pw_name,'uid':p.pw_uid,'gid':p.pw_gid,
                                   'groups':os.getgrouplist(p.pw_name,p.pw_gid)}
processes=[];root_roles=[]
for p in Path('/proc').glob('[0-9]*'):
 try:
  fields=dict(s.split(':',1) for s in (p/'status').read_text().splitlines() if ':' in s)
  ids=list(map(int,fields['Uid'].split()));args=(p/'cmdline').read_bytes().decode(errors='replace').split('\0')
  if 999 in ids:processes.append({'pid':int(p.name),'uids':ids,'args':args})
  if '--role' in args and any(s.startswith('/var/lib/dcl-r6/') and s.endswith('/guard.py') for s in args):root_roles.append({'pid':int(p.name),'uids':ids,'args':args})
 except (OSError,KeyError,ValueError):pass
history={}
for name in ['batch04','batch05']:
 root=Path('/var/lib/dcl-r6')/name
 value={'exists':root.exists(),'closed':None,'counter':None}
 if (root/'inputs/CLOSED.json').exists():value['closed']=json.loads((root/'inputs/CLOSED.json').read_text())
 if (root/'out/visits.bin').exists():
  import struct
  raw=(root/'out/visits.bin').read_bytes();value['counter']=list(struct.unpack('<QQ',raw[8:]))
 history[name]=value
mounts=Path('/proc/self/mountinfo').read_text().splitlines()
device=os.stat('/var/lib/dcl-r6').st_dev;device=str(os.major(device))+':'+str(os.minor(device))
print(json.dumps({'schema':'B06-env/1','python':list(sys.version_info[:3]),'python_executable':sys.executable,
 'python_sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
 'kernel':platform.release(),'machine':platform.machine(),'os_release':Path('/etc/os-release').read_text(),
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'page_size':os.sysconf('SC_PAGE_SIZE'),
 'euid':os.geteuid(),'Root_admin_rlimit_as':list(resource.getrlimit(resource.RLIMIT_AS)),
 'uid_identities':uids,'payload_processes':processes,'existing_root_roles':root_roles,
 'source_files':rows,'source_directories':dirs,'batch06_exists':Path('/var/lib/dcl-r6/batch06').exists(),
 'batch06_installed_unit_exists':Path('/etc/systemd/system/dclr6batch06.slice').exists(),
 'batch06_cgroup_exists':Path('/sys/fs/cgroup/dclr6batch06.slice').exists(),
 'historical':history,'filesystem_mountinfo':[s for s in mounts if s.split()[2]==device],
 'cgroup_mountinfo':[s for s in mounts if s.split()[4]=='/sys/fs/cgroup']},ensure_ascii=False))
'''


def preflight():
    rows=[]
    rows.append(call(['/usr/bin/sha256sum','--check','--strict','--quiet',
      '/mnt/d/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-batch06/evidence/LINUX_EXPECTED.sha256'],
      'Verify1326 unique Linux frozen/runtime/historical hashes before initialization','PREFLIGHT_READ_ONLY'))
    if rows[-1]['exit_code']:
        dump(E/'PREFLIGHT_RESULT.json',{'schema':'B06-preflight/1','status':'PREFLIGHT_FAILED','failure':'HASH_MISMATCH','T0':None,'counter':None})
        return
    rows.append(call(['/usr/bin/python3.12','-I','-S','-B','-c',ENV],
                     'Read current runtime, identity, files/ACL, historical closed ledgers and process absence','PREFLIGHT_READ_ONLY'))
    if rows[-1]['exit_code']:
        dump(E/'PREFLIGHT_RESULT.json',{'schema':'B06-preflight/1','status':'PREFLIGHT_FAILED','failure':'ENV_QUERY_FAILED','T0':None,'counter':None})
        return
    env=json.loads(rows[-1]['stdout']);dump(E/'PREFLIGHT_ENV.json',env)
    rows.append(call(['/usr/bin/systemctl','show','--property=Version','--value'],
                     'Read live systemd Version','PREFLIGHT_READ_ONLY'))
    rows.append(call(['/usr/bin/systemctl','list-units','dclr6batch06*','--all','--no-pager','--no-legend'],
                     'Read batch06 unit conflicts before preparation','PREFLIGHT_READ_ONLY'))
    rows.append(call(['/usr/bin/systemctl','list-units','--state=failed','--all','--no-pager','--no-legend'],
                     'Read failed units against frozen launcher allowed set mnt-e.mount','PREFLIGHT_READ_ONLY'))
    failed=[]
    for line in rows[-1]['stdout'].splitlines():
        fields=line.replace('●','').split()
        if fields and fields[0]!='mnt-e.mount':failed.append(fields[0])
    m=load(E/'static_manifest.json')
    checks={
      'all_native_exit_zero':all(r['exit_code']==0 for r in rows),
      'hashes':rows[0]['exit_code']==0,
      'python':env['python']==[3,12,3] and env['python_executable']=='/usr/bin/python3.12' and env['python_sha256']==m['runtime_files']['/usr/bin/python3.12'],
      'kernel_architecture':env['kernel']==m['kernel'] and env['machine']==m['architecture'],
      'ubuntu':'24.04' in env['os_release'], 'systemd':rows[2]['stdout'].strip()==m['systemd'],
      'uid_gid':env['uid_identities']['999']['uid']==999 and env['uid_identities']['999']['gid']==989 and env['uid_identities']['999']['groups']==[989],
      'probe_uid':env['uid_identities']['65534']['uid']==65534 and env['uid_identities']['65534']['gid']==65534,
      'source_permissions':all(r['uid']==0 and r['gid']==0 and r['mode']==0o644 and not r['symlink'] and r['regular'] and not r['acl'] for r in env['source_files']),
      'directory_permissions':all(r['uid']==0 and not r['mode']&0o022 and not r['symlink'] and not r['acl'] for r in env['source_directories']),
      'page_cgroup':env['page_size']==4096 and any(' - cgroup2 ' in s for s in env['cgroup_mountinfo']),
      'new_batch_absent':not env['batch06_exists'] and not env['batch06_installed_unit_exists'] and not env['batch06_cgroup_exists'] and not rows[3]['stdout'].strip(),
      'no_residual_processes':not env['payload_processes'] and not env['existing_root_roles'],
      'historical_closed':all(v['closed'] is not None for v in env['historical'].values()) and env['historical']['batch05']['counter']==[37293,1000000] and env['historical']['batch04']['counter']==[37021,1000000],
      'manager_failed_units_match_frozen_rule':not failed}
    result={'schema':'B06-preflight/1','status':'PREFLIGHT_BASE_PASS' if all(checks.values()) else 'PREFLIGHT_FAILED',
            'checks':checks,'failed_checks':[k for k,v in checks.items() if not v],
            'unreviewed_manager_failed_units':failed,'boot_id':env['boot_id'],'T0':None,'counter':None,
            'dynamic_launcher_calls':0,'native_batch06_created':False,'source_version':'RootIPC-static-1/r4'}
    dump(E/'PREFLIGHT_RESULT.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='preflight':preflight()
    elif mode=='argv':
        spec=load(sys.argv[2]);call(spec['argv'],spec['purpose'],spec['classification'])
    else:raise SystemExit('unknown invocation mode')
