"""Construct fixed PF inputs only; subject and oracle are never imported/run."""
from pathlib import Path
import copy,json
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\pf01')
def phase(**changes):
    f=dict(closed=False,stop=False,binding=True,identity=True,deadline=True,lock_acquired=True,phase='RUNTIME_ARMED',sequence=5,
        committed=True,checkpoint_integrity=True,initialization_match=True,root_reader=True,private_phase='RUNTIME_ARMED',private_sequence=5,
        record_hash_match=True,work=False);f.update(changes);return {'domain':'phase','facts':f,'critical':True}
def admin(**changes):
    f=dict(roles_empty=True,group_absent=True,audit_error=False,any_runtime=True,native_verified=False,native_error=False,
        internal_status='UNKNOWN',module_ready=True,permission_ok=True,evidence_integrity=True,exception=False,repeated=False,repeat_valid=False)
    f.update(changes);return {'domain':'admin','facts':f,'critical':False}
def close(**changes):
    f=dict(critical=True,roles_empty=True,group_absent=True,audit_error=False,internal_status='UNKNOWN',
        native_status='NATIVE_SEAL_UNRESOLVED',admin_status='ADMIN_EVIDENCE_UNRESOLVED');f.update(changes)
    return {'domain':'closure','facts':f,'critical':True}
cases=[
 ('ready_inspection',[phase(phase='RUNTIME_READY',sequence=4,private_phase='RUNTIME_READY',private_sequence=4)]),
 ('armed_work',[phase(work=True)]),('running_work',[phase(phase='RUNNING',sequence=6,private_phase='RUNNING',private_sequence=6,work=True)]),
 ('transition_lock_interleaving',[phase(lock_acquired=False),phase()]),
 ('delayed_publication',[phase(lock_acquired=False),phase(lock_acquired=False),phase()]),
 ('old_version',[phase(private_phase='RUNNING',private_sequence=6)]),
 ('cross_batch',[phase(binding=False)]),('sequence_rollback',[phase(sequence=4)]),('closed_transition',[phase(closed=True,work=True)]),
 ('illegal_phase',[phase(phase='RUNTIME_INITIALIZING',sequence=3)]),('missing_checkpoint',[phase(checkpoint_integrity=False)]),
 ('owner_mismatch',[phase(identity=False)]),('stop_during_wait',[phase(lock_acquired=False),phase(stop=True,lock_acquired=False)]),
 ('transition_expired',[phase(lock_acquired=False,deadline=False)]),
 ('admin_normal_import_model',[admin(internal_status='CLOSED_CLEANUP_CONFIRMED')]),
 ('admin_nondefault_cwd_model',[admin()]),('admin_absolute_entry_model',[admin()]),
 ('admin_root_identity_failure',[admin(permission_ok=False)]),('admin_no_T0',[admin(any_runtime=False)]),
 ('admin_native_completed',[admin(native_verified=True)]),('admin_native_failed',[admin(native_error=True)]),
 ('admin_internal_UNKNOWN',[admin(internal_status='UNKNOWN')]),('admin_dependency_missing',[admin(module_ready=False)]),
 ('admin_file_permission',[admin(permission_ok=False)]),('admin_exception',[admin(exception=True,native_verified=True)]),
 ('admin_repeat_valid',[admin(repeated=True,repeat_valid=True,native_verified=True)]),
 ('close_phase_failure',[close()]),('close_native_success',[close(native_status='NATIVE_SEAL_COMPLETED')]),
 ('close_admin_success',[close(admin_status='ADMIN_EVIDENCE_SEALED')]),
 ('close_admin_failure_native_preserved',[close(native_status='NATIVE_SEAL_COMPLETED')]),
 ('close_empty_internal_UNKNOWN',[close(internal_status='UNKNOWN')]),('close_external_stop',[close(roles_empty=False,group_absent=False)]),
]
assert len(cases)==32
jobs=[]
for name,frames in cases:jobs.append({'case_id':'PF_SAFE_'+name,'mutant':None,'violation_class':'NONE','allowed_violations':[],'frames':frames})
pairs=[
 ('allow_illegal_phase','ILLEGAL_PHASE_ACCEPTED',phase(phase='RUNTIME_INITIALIZING',sequence=3)),
 ('skip_work','PREMATURE_WORK',phase(phase='RUNTIME_READY',sequence=4,private_phase='RUNTIME_READY',private_sequence=4,work=True)),
 ('stale_snapshot','STALE_SNAPSHOT_ACCEPTED',phase(private_phase='RUNNING',private_sequence=6)),
 ('ignore_version','VERSION_MISMATCH_ACCEPTED',phase(private_sequence=4)),
 ('no_auto_stop','NO_AUTO_STOP',phase(phase='RUNTIME_INITIALIZING',sequence=3)),
 ('swallow_import_error','IMPORT_ERROR_SWALLOWED',admin(module_ready=False)),
 ('overwrite_native','NATIVE_RESULT_OVERWRITTEN',admin(native_verified=True)),
 ('reactivate_closed','REACTIVATION',phase(closed=True,work=True)),
]
for mutant,violation,frame in pairs:
    allowed=[violation]+(['NO_AUTO_STOP'] if mutant in ('allow_illegal_phase','skip_work','stale_snapshot','ignore_version') else [])
    for selected in [None,mutant]:jobs.append({'case_id':'PF_PAIR_'+mutant+('_mutant' if selected else '_safe'),
        'mutant':selected,'violation_class':violation,'allowed_violations':allowed if selected else [],'frames':[copy.deepcopy(frame)]})
assert len(jobs)==48 and sum(bool(j['mutant']) for j in jobs)==8
cfg={'schema':'PF-CONTRACT/1','version':'PTA-PhaseFinalizer-static-1/r1','batch_id':'batch12','profile':'PF-SIMULATION/1',
    'driver_prepay':16,'completed_visits':817,'hard_visits':1152,'max_frames':4,'dynamic_status':'UNRUN','jobs':jobs,
    'scope':'Synthetic policy/observation fixtures; real OS phase mutex, import and automatic finalization require separate actual receipts',
    'phase_mutex_seconds':2,'phase_mutex_attempts':512,'postexit_quiescence_seconds':5,'postexit_quiescence_samples':128,
    'postexit_native_alarm_seconds':30,'postexit_host_wait_seconds':35}
(W/'inputs/phase_finalizer_contract.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PF48 constructed:40 safe +8 mutants; subject/oracle executions0')
