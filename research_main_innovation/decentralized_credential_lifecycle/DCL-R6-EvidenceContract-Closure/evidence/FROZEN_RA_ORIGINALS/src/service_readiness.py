"""C00Ready/1: native field diagnostics, bounded exec-ready barrier and minted lease."""
import hashlib
import json
import os
from pathlib import Path
import select
import subprocess
import time
import boot_continuity as BC

PROFILE='C00-READY/1'
_NATIVE=object()
_LEASE=object()
IDS=('CR-01','CR-02','CR-03','CR-04','CR-05','CR-06','CR-07','CR-08')
UNIT_FIELDS=('Id','Type','ActiveState','SubState','MainPID','ControlGroup','User','Group',
 'LimitAS','LimitASSoft','TasksMax','NoNewPrivileges','Restart','InvocationID',
 'StateChangeTimestampMonotonic','ActiveEnterTimestampMonotonic','Result','ExecMainStatus','Job')
VERSION_FIELDS=('Id','Type','ActiveState','SubState','MainPID','ControlGroup','LimitAS','LimitASSoft',
 'TasksMax','NoNewPrivileges','Restart','InvocationID','StateChangeTimestampMonotonic','Job')


class ReadFailure(RuntimeError):
    def __init__(self,source,exc):
        self.source=source;self.detail={'type':type(exc).__name__,'message':str(exc),'errno':getattr(exc,'errno',None)}
        super().__init__(source+':'+str(exc))


def expected(G,unit):
    return {'CR-01':[999],'CR-02':[989],'CR-03':[989],'CR-04':0,'CR-05':1,
            'CR-06':str(G.AS_CAP),'CR-07':str(G.AS_CAP),'CR-08':'/'+G.PARENT+'/'+unit}


def policy(d):
    """Shared pure classifier; a READY result alone cannot create a native lease."""
    if d['error'] is not None:return 'FAILED'
    if d['boot_before']!=d['expected_boot'] or d['boot_after']!=d['expected_boot'] or d['stopped']:return 'FAILED'
    if not d['binding_valid'] or not d['hard_aux_valid'] or d['expired']:return 'FAILED'
    phases=d['phases']
    if phases[0]=='STARTING' and phases[1] in ('STARTING','READY'):
        # Live credentials are not sampled before the Type=exec barrier.
        return 'STARTING' if all(r['result'] in ('MATCH','NOT_READY') for r in d['checks']) else 'FAILED'
    if phases!=['READY','READY'] or not d['coherent']:return 'FAILED'
    return 'READY' if all(r['result']=='MATCH' for r in d['checks']) else 'FAILED'


def contract(G):
    a,m=G.authorization();p=G.SOURCE.parent/'inputs/readiness_contract.json'
    if G.digest(p)!=m['readiness_contract_sha256'] or a.get('readiness_contract_sha256')!=G.digest(p):raise G.AdmissionBlocked('READY_CONTRACT_BINDING')
    cfg=G.trusted(p)
    if cfg['profile']!=PROFILE or cfg['future_batch_id']!=G.ROOT.name:raise G.AdmissionBlocked('READY_CONTRACT_VERSION')
    return cfg,a


def unit_read(G,unit,until):
    G.root_checkpoint();begin=G.stamp()
    try:
        remain=until-G.now()
        if remain<=0:raise TimeoutError('READINESS_DEADLINE')
        argv=['/usr/bin/systemctl','show','--all','--no-pager',unit,*['--property='+f for f in UNIT_FIELDS]]
        r=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                         timeout=min(1.0,remain),check=False)
        if len(r.stdout)+len(r.stderr)>32768:raise ValueError('UNIT_OUTPUT_LIMIT')
        if r.returncode:raise OSError('UNIT_QUERY_EXIT_%s:%s'%(r.returncode,r.stderr.decode(errors='replace')))
        values=dict(s.split('=',1) for s in r.stdout.decode().splitlines() if '='in s)
        if any(k not in values for k in UNIT_FIELDS):raise KeyError('UNIT_PROPERTY_MISSING')
        return {'values':values,'before':begin,'after':G.stamp(),'argv':argv,
                'stdout_hex':r.stdout.hex(),'stderr_hex':r.stderr.hex(),'exit_code':r.returncode}
    except BaseException as exc:
        error=ReadFailure('systemd:'+unit,exc)
        if 'r' in locals():error.detail['raw_result']={'stdout_hex':r.stdout[:32768].hex(),'stderr_hex':r.stderr[:32768].hex(),'exit_code':r.returncode}
        raise error from exc


def phase(values):
    if values['Type']!='exec':return 'FAILED'
    job=values['Job'].split()
    if (values['ActiveState']=='inactive' and values['SubState']=='dead' and values['MainPID']=='0' and
        job and job[0].isdigit() and int(job[0])>0):return 'STARTING'
    if values['ActiveState']=='activating' and values['SubState'] in ('start','start-pre','start-post'):
        return 'STARTING'
    if values['ActiveState']=='active' and values['SubState']=='running' and int(values['MainPID'])>0:
        return 'READY'
    return 'FAILED'


def read_file(G,p):
    before=G.stamp()
    try:
        fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            raw=os.read(fd,65537)
            if len(raw)>65536:raise ValueError('READINESS_FILE_LIMIT')
        finally:os.close(fd)
        return {'path':str(p),'raw':raw.decode(),'before':before,'after':G.stamp()}
    except BaseException as exc:raise ReadFailure(str(p),exc) from exc


def process_read(G,pid):
    partial={}
    try:
        status=read_file(G,Path('/proc')/str(pid)/'status');partial['status']=status
        limits=read_file(G,Path('/proc')/str(pid)/'limits');partial['limits']=limits
        cg=read_file(G,Path('/proc')/str(pid)/'cgroup');partial['cgroup']=cg
        fields=dict(s.split(':',1) for s in status['raw'].splitlines() if ':'in s)
        if len(fields['Uid'].split())!=4 or len(fields['Gid'].split())!=4:raise ValueError('PROC_IDENTITY_ARITY')
        converted={'CR-01':sorted(set(map(int,fields['Uid'].split()))),'CR-02':sorted(set(map(int,fields['Gid'].split()))),
                   'CR-03':sorted(set(map(int,fields['Groups'].split()))),'CR-04':int(fields['CapEff'].strip(),16),
                   'CR-05':int(fields['NoNewPrivs'].strip())}
        line=next(s for s in limits['raw'].splitlines() if s.startswith('Max address space'))
        actual_as=line[len('Max address space'):].split()[:2]
        if len(actual_as)!=2:raise ValueError('PROC_AS_ARITY')
        as_pair=[int(x) if x.isdigit() else x for x in actual_as]
        cgroup=next(s[3:] for s in cg['raw'].splitlines() if s.startswith('0::'))
        return {'status':status,'limits':limits,'cgroup':cg,'converted':converted,'actual_AS':as_pair,'actual_cgroup':cgroup}
    except BaseException as exc:
        error=ReadFailure('/proc/%s read/conversion'%pid,exc);error.detail['partial_raw']=partial
        raise error from exc


def parent_read(G):
    base=Path('/sys/fs/cgroup')/G.PARENT
    pids=read_file(G,base/'pids.max');memory=read_file(G,base/'memory.max')
    try:
        st=base.stat()
        return {'pids':pids,'memory':memory,'pids_max':int(pids['raw'].strip()),'memory_max':int(memory['raw'].strip()),
                'device':st.st_dev,'inode':st.st_ino}
    except BaseException as exc:raise ReadFailure(str(base),exc) from exc


def check_row(cid,want,values,source,times,identity,state_phase,version):
    good=all(v==want for v in values)
    return {'check_id':cid,'expected':want,'observed':values,'evidence_source':source,'read_time':times,
            'process_identity':identity,'state_phase':state_phase,'status_version':version,
            'read_success':True,'result':'MATCH' if good else 'MISMATCH','error':None}


class Observation:
    def __init__(self,key,data,pidfd):
        if key is not _NATIVE:raise TypeError('NATIVE_OBSERVATION_REQUIRED')
        self.key=key;self.data=data;self.pidfd=pidfd
    def close(self):
        if self.pidfd is not None:os.close(self.pidfd);self.pidfd=None


def collect_native(G,case,unit,until,anchor,sequence):
    d={'schema':'C00-READY-DIAGNOSTIC/1','origin':'NATIVE_OS/1','batch_id':G.ROOT.name,'service_unit':unit,'case':case,
       'sample_sequence':sequence,'check_time_begin':G.stamp(),'check_phase':'UNKNOWN','expected_boot':anchor,
       'boot_before':G.boot_id(),'boot_after':None,'process_identity':None,'checks':[],
       'error':None,'binding_valid':False,'hard_aux_valid':False,'coherent':False,'expired':False,
       'stopped':G.stopped(),'phases':['FAILED','FAILED'],'raw':{},'aux_checks':[]}
    pidfd=None;want=expected(G,unit)
    def aux(cid,want_value,actual_value,source):
        d['aux_checks'].append({'check_id':cid,'expected':want_value,'observed':actual_value,
          'evidence_source':source,'read_time':G.stamp(),'result':'MATCH' if actual_value==want_value else 'MISMATCH'})
        return actual_value==want_value
    try:
        G.root_checkpoint();cfg,a=contract(G)
        d['binding_valid']=G.digest(G.SOURCE.parent/'inputs/execution_lock.json')==a['execution_lock_sha256']
        d['execution_lock_sha256']=a['execution_lock_sha256']
        u0=unit_read(G,unit,until);d['raw']['unit_before']=u0;v0=u0['values'];p0=phase(v0)
        required=[aux('CR-A-UNIT',unit,v0['Id'],'systemd.Id'),aux('CR-A-TYPE','exec',v0['Type'],'systemd.Type'),
          aux('CR-A-RESTART','no',v0['Restart'],'systemd.Restart'),aux('CR-A-USER','dcl-r6',v0['User'],'systemd.User'),
          aux('CR-A-GROUP','dcl-r6',v0['Group'],'systemd.Group'),aux('CR-A-TASKS','4',v0['TasksMax'],'systemd.TasksMax'),
          aux('CR-A-NNP','yes',v0['NoNewPrivileges'],'systemd.NoNewPrivileges')]
        if not all(required):raise ValueError('UNIT_CONTRACT_MISMATCH')
        if p0=='FAILED':
            aux('CR-A-SERVICE-PHASE','Type=exec activating/start* or active/running',v0['ActiveState']+'/'+v0['SubState'],'systemd state')
            raise ValueError('SERVICE_STATE_FAILED')
        if p0=='READY' and not v0['InvocationID']:raise ValueError('INVOCATION_MISSING_WHEN_ACTIVE')
        pid=int(v0['MainPID']);ident=G.identity(pid) if pid and p0 in ('STARTING','READY') else None;d['process_identity']=ident
        if pid:
            pidfd=os.pidfd_open(pid)
            if G.identity(pid)!=ident or select.select([pidfd],[],[],0)[0]:raise ProcessLookupError('TARGET_EXIT_OR_PID_REUSE')
        proc0=proc1=parent0=parent1=None
        if p0=='READY':
            proc0=process_read(G,pid);parent0=parent_read(G);d['raw'].update(proc_before=proc0,parent_before=parent0)
        u1=unit_read(G,unit,until);d['raw']['unit_after']=u1;v1=u1['values'];p1=phase(v1)
        if v1['Id']!=unit or v1['Type']!='exec' or v1['Restart']!='no':raise ValueError('UNIT_IDENTITY_CHANGED')
        if v1['MainPID']!=v0['MainPID'] and not(p0=='STARTING' and v0['MainPID']=='0' and int(v1['MainPID'])>0):
            aux('CR-A-PID-VERSION',v0['MainPID'],v1['MainPID'],'systemd.MainPID');raise ValueError('MAINPID_CHANGED_IN_SAMPLE')
        for key,w in [('User','dcl-r6'),('Group','dcl-r6'),('TasksMax','4'),('NoNewPrivileges','yes')]:
            aux('CR-A-AFTER-'+key,w,v1[key],'systemd.'+key)
        if any(r['result']=='MISMATCH' for r in d['aux_checks']):raise ValueError('UNIT_CONFIG_CHANGED')
        d['phases']=[p0,p1];d['check_phase']='PRE_EXEC' if p0=='STARTING' else 'EXEC_READY_SAMPLE'
        versions=[[v[k] for k in VERSION_FIELDS] for v in [v0,v1]]
        for cid,key in [('CR-06','LimitAS'),('CR-07','LimitASSoft'),('CR-08','ControlGroup')]:
            values=[v0[key],v1[key]]
            if cid=='CR-08' and p0=='STARTING' and any(x=='' for x in values) and all(x in ('',want[cid]) for x in values):
                d['checks'].append({'check_id':cid,'expected':want[cid],'observed':values,'evidence_source':'systemd.ControlGroup',
                  'read_time':[u0['after'],u1['after']],'process_identity':ident,'state_phase':d['check_phase'],
                  'status_version':versions,'read_success':True,'result':'NOT_READY','error':'cgroup creation pending before exec-ready'})
            else:d['checks'].append(check_row(cid,want[cid],values,'systemd.'+key,[u0['after'],u1['after']],ident,d['check_phase'],versions))
        if p0=='STARTING':
            for cid in IDS[:5]:d['checks'].append({'check_id':cid,'expected':want[cid],'observed':None,
                'evidence_source':'/proc credentials deferred until Type=exec active/running','read_time':None,
                'process_identity':ident,'state_phase':'PRE_EXEC','status_version':versions,'read_success':False,
                'result':'NOT_READY','error':'target exec not confirmed; no credential mismatch is accepted'})
            d['hard_aux_valid']=True
        elif p0=='READY':
            proc1=process_read(G,pid);parent1=parent_read(G);d['raw'].update(proc_after=proc1,parent_after=parent1)
            for cid in IDS[:5]:d['checks'].append(check_row(cid,want[cid],[proc0['converted'][cid],proc1['converted'][cid]],
                '/proc/%s/status'%pid,[proc0['status']['after'],proc1['status']['after']],ident,'EXEC_READY_SAMPLE',versions))
            aux('CR-A-PROC-AS',[[G.AS_CAP,G.AS_CAP]]*2,[proc0['actual_AS'],proc1['actual_AS']],'/proc/limits')
            aux('CR-A-PROC-CG',[want['CR-08']]*2,[proc0['actual_cgroup'],proc1['actual_cgroup']],'/proc/cgroup')
            aux('CR-A-PARENT-PIDS',[4,4],[parent0['pids_max'],parent1['pids_max']],'cgroup.pids.max')
            aux('CR-A-PARENT-MEMORY',[4*G.AS_CAP]*2,[parent0['memory_max'],parent1['memory_max']],'cgroup.memory.max')
            aux('CR-A-PARENT-IDENTITY',[parent0['device'],parent0['inode']],[parent1['device'],parent1['inode']],'cgroup inode/device')
            d['hard_aux_valid']=all(r['result']=='MATCH' for r in d['aux_checks'])
        if pid and (G.identity(pid)!=ident or select.select([pidfd],[],[],0)[0]):raise ProcessLookupError('TARGET_EXIT_DURING_SAMPLE')
        d['coherent']=versions[0]==versions[1] and (p0!='READY' or (proc0['converted']==proc1['converted']))
        d['binding_valid']=d['binding_valid'] and G.digest(G.SOURCE.parent/'inputs/execution_lock.json')==a['execution_lock_sha256']
    except BaseException as exc:
        d['error']={'type':type(exc).__name__,'source':getattr(exc,'source','readiness control'),
                    'detail':getattr(exc,'detail',{'message':str(exc),'errno':getattr(exc,'errno',None)})}
    existing={r['check_id'] for r in d['checks']}
    for cid in IDS:
        if cid not in existing:d['checks'].append({'check_id':cid,'expected':want[cid],'observed':None,
          'evidence_source':'not acquired; see raw_error','read_time':None,'process_identity':d['process_identity'],
          'state_phase':d['check_phase'],'status_version':None,'read_success':False,'result':'READ_ERROR','error':d['error']})
    d['checks'].sort(key=lambda r:r['check_id']);d['boot_after']=G.boot_id();d['stopped']=G.stopped();d['expired']=G.now()>=until
    if d['boot_before']!=anchor or d['boot_after']!=anchor:aux('CR-A-BOOT',[anchor,anchor],[d['boot_before'],d['boot_after']],'boot_id')
    if d['stopped']:aux('CR-A-STOP',False,True,'STOP_REQUEST/CLOSED')
    if d['expired']:aux('CR-A-DEADLINE',False,True,'CLOCK_BOOTTIME/current window')
    if 'FAILED' in d['phases']:aux('CR-A-PHASE','STARTING transition or READY/READY',d['phases'],'systemd ActiveState/SubState')
    if d['phases']==['READY','READY'] and not d['coherent']:aux('CR-A-SNAPSHOT',True,False,'two-bookend status/identity version')
    d['check_time_end']=G.stamp();d['overall_result']=policy(d)
    d['all_failed_checks']=[r['check_id'] for r in d['checks']+d['aux_checks'] if r['result'] in ('MISMATCH','READ_ERROR')]
    mismatches=[r['check_id'] for r in d['checks']+d['aux_checks'] if r['result']=='MISMATCH']
    d['first_failed_check']=mismatches[0] if mismatches else d['all_failed_checks'][0] if d['all_failed_checks'] else None
    if d['overall_result']=='FAILED' and not d['all_failed_checks']:d['first_failed_check']='CR-AUX_OR_PHASE'
    d['raw_error']=d['error']
    d['process_pid']=d['process_identity']['pid'] if d['process_identity'] else None
    d['process_starttime']=d['process_identity']['start_ticks'] if d['process_identity'] else None
    d['boot_id']=d['boot_before']
    return Observation(_NATIVE,d,pidfd)


def persist(G,row):
    name='ready_%s_%04d.json'%(row['case'],row['sample_sequence'])
    try:
        if len(BC.canon(row))>131072:raise ValueError('READINESS_DIAGNOSTIC_ROW_LIMIT')
        with BC.Store() as store:store.put(name,row,exclusive=True)
    except BaseException as exc:
        BC.emit('READINESS_DIAGNOSTIC_WRITE_FAILED',case=row['case'],error=repr(exc),qualification='CLOSED')
        raise G.AdmissionBlocked('READINESS_DIAGNOSTIC_WRITE_FAILED') from exc


class Lease:
    def __init__(self,key,G,case,unit,until,anchor,observation):
        if key is not _LEASE or observation.key is not _NATIVE or observation.data['overall_result']!='READY':raise TypeError('NATIVE_READY_LEASE_REQUIRED')
        self.key=key;self.case=case;self.unit=unit;self.until=until;self.anchor=anchor;self.obs=observation
        self.identity=observation.data['process_identity'];self.info=observation.data['raw']['unit_after']['values']
        self.sequence=observation.data['sample_sequence'];self.closed=False
    def confirm(self,G,t):
        if self.closed or self.key is not _LEASE or t['case']!=self.case or t['unit']!=self.unit or t['main_identity']!=self.identity:raise G.AdmissionBlocked('READINESS_LEASE_BINDING')
        G.root_checkpoint()
        if G.now()>=self.until or G.boot_id()!=self.anchor or select.select([self.obs.pidfd],[],[],0)[0] or G.identity(self.identity['pid'])!=self.identity:raise G.AdmissionBlocked('READINESS_LEASE_EXPIRED_OR_EXIT')
        check=collect_native(G,self.case,self.unit,self.until,self.anchor,self.sequence+1)
        try:
            persist(G,check.data)
            if check.data['overall_result']!='READY' or check.data['process_identity']!=self.identity:raise G.AdmissionBlocked('READINESS_RECHECK_FAILED')
            certificate={'schema':PROFILE,'origin':'NATIVE_OS/1','case':self.case,'unit':self.unit,'boot_id':self.anchor,
              'process_identity':self.identity,'execution_lock_sha256':G.digest(G.SOURCE.parent/'inputs/execution_lock.json'),
              'sample':check.data,'readiness_until':self.until,'resource_gate':'NOT_OBTAINED'}
            with BC.Store() as store:store.put(self.case+'_READINESS.json',certificate,exclusive=True,public=True)
            if G.now()>=self.until or G.stopped():raise G.AdmissionBlocked('READINESS_LATE_CERTIFICATE')
            self.info=check.data['raw']['unit_after']['values'];return certificate
        finally:check.close()
    def close(self):
        if not self.closed:self.obs.close();self.closed=True
    def ticket_admit(self,G,t):
        G.root_checkpoint()
        if (self.closed or self.key is not _LEASE or t['main_identity']!=self.identity or G.boot_id()!=self.anchor or
            G.now()>=self.until or select.select([self.obs.pidfd],[],[],0)[0] or G.identity(self.identity['pid'])!=self.identity):
            raise G.AdmissionBlocked('READINESS_TICKET_IDENTITY_OR_DEADLINE')


def wait_native(G,case,unit,started):
    if case not in ('C00','C10') or os.geteuid()!=0:raise G.AdmissionBlocked('READINESS_ROOT_CASE_ONLY')
    cfg,a=contract(G);s=G.state();anchor=s['boot_id']
    until=min(started+cfg['readiness_seconds'],s['T0']+300,s['stop_at'],s['deadline'])
    last_pid=None;last_invocation=None;last_identity=None
    for sequence in range(cfg['sample_cap']):
        obs=collect_native(G,case,unit,until,anchor,sequence);row=obs.data
        try:
            unit0=row['raw'].get('unit_before',{}).get('values',{})
            pid=unit0.get('MainPID');inv=unit0.get('InvocationID')
            if pid and pid!='0':
                if last_pid is not None and last_pid!=pid:row['error']={'message':'MAINPID_CHANGED_ACROSS_SAMPLES'};row['overall_result']='FAILED'
                last_pid=pid
            current_identity=row['process_identity']
            if current_identity is not None:
                if last_identity is not None and last_identity!=current_identity:
                    row['error']={'message':'PROCESS_IDENTITY_CHANGED_ACROSS_SAMPLES','before':last_identity,'after':current_identity}
                    row['overall_result']='FAILED';row['first_failed_check']='CR-A-CROSS-SAMPLE-IDENTITY'
                    row['all_failed_checks'].append('CR-A-CROSS-SAMPLE-IDENTITY')
                last_identity=current_identity
            if inv:
                if last_invocation is not None and last_invocation!=inv:row['error']={'message':'INVOCATION_CHANGED_ACROSS_SAMPLES'};row['overall_result']='FAILED'
                last_invocation=inv
            persist(G,row)
            if row['overall_result']=='READY':return Lease(_LEASE,G,case,unit,until,anchor,obs)
            if row['overall_result']=='FAILED':raise G.AdmissionBlocked('BC_SERVICE_IDENTITY_OR_LIMITS:'+str(row['first_failed_check']))
        except BaseException:obs.close();raise
        obs.close()
        if G.now()>=until:raise G.LimitReached('READINESS_TIMEOUT')
        time.sleep(min(cfg['poll_seconds'],max(0,until-G.now())))
    raise G.LimitReached('READINESS_SAMPLE_CAP')


def require_lease(G,t,lease):
    if type(lease) is not Lease or lease.key is not _LEASE:raise G.AdmissionBlocked('READINESS_NATIVE_LEASE_REQUIRED')
    return lease.confirm(G,t)


def formal_gate(G):
    cfg,a=contract(G)
    if a['scope']!='CALIBRATE_S1S9_THEN_F1_F4' or a.get('Full_conditional_chain_explicitly_approved') is not True:raise G.AdmissionBlocked('READY_FULL_CHAIN_NOT_APPROVED')
    q=G.trusted(G.ROOT/'inputs/C00_READY_QUALIFICATION.json')
    if q['binding']!=G.safety_binding() or q['contract_sha256']!=G.digest(G.SOURCE.parent/'inputs/readiness_contract.json') or q['checker_sha256']!=G.digest(G.SOURCE/'readiness_oracle.py') or not q['accepted']:raise G.AdmissionBlocked('READY_QUALIFICATION')
    if len(q['results'])!=len(cfg['jobs']) or {r['case_id'] for r in q['results']}!={j['case_id'] for j in cfg['jobs']}:raise G.AdmissionBlocked('READY_QUALIFICATION_SET')
    expected_jobs={j['case_id']:j for j in cfg['jobs']}
    for r in q['results']:
        j=expected_jobs[r['case_id']];target='PASS' if j['variant']=='safe' else 'MUTATION_DETECTED'
        if not r['accepted'] or r['status']!=target or not set(r['violations']).issubset(j['allowed_violations']):raise G.AdmissionBlocked('READY_QUALIFICATION_RESULT')
    for case in ('C00','C10'):
        c=G.trusted(G.ROOT/('inputs/'+case+'_READINESS.json'))
        if (c['origin']!='NATIVE_OS/1' or c['boot_id']!=G.boot_id() or c['execution_lock_sha256']!=G.digest(G.SOURCE.parent/'inputs/execution_lock.json') or
            len(c['sample']['checks'])!=8 or {r['check_id'] for r in c['sample']['checks']}!=set(IDS) or
            any(r['result']!='MATCH' for r in c['sample']['checks'])):raise G.AdmissionBlocked('READY_NATIVE_CERTIFICATE')
