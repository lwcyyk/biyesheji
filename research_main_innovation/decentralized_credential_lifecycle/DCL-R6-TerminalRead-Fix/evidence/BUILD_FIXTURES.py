"""Construct static TR40 fixtures. No subject/oracle execution."""
from pathlib import Path
import copy,json
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\tr01')
def frame(name,**changes):
    facts=dict(purpose='REVIEW',closed=True,stop=False,identity=True,window=True,budget=True,version=True,required_records=True,
        same_boot=True,window_live=True,exit_proof=True,internal_status='UNKNOWN',native_verified=False,seal_error=False,partial_archive=False)
    facts.update(changes);return {'op':name,'facts':facts}
cases=[
 ('active_running',frame('active_check',purpose='ACTIVE',closed=False)),
 ('stop_denies_work',frame('active_check',purpose='ACTIVE',closed=False,stop=True)),
 ('closed_read_T0',frame('read_T0')),('closed_read_deadline',frame('read_deadline',window_live=False)),
 ('closed_read_R',frame('read_budget')),('closed_reason',frame('read_reason')),('closed_journal',frame('read_journal')),
 ('closed_admin',frame('admin_read',purpose='HISTORICAL_AUDIT',same_boot=False)),
 ('missing_T0',frame('missing_T0',window=False)),('missing_deadline',frame('missing_deadline',window=False)),
 ('journal_corrupt',frame('corrupt_journal',budget=False)),('boot_mismatch',frame('wrong_boot',identity=False)),
 ('batch_mismatch',frame('wrong_batch',identity=False)),('execution_lock_mismatch',frame('wrong_lock',identity=False)),
 ('version_rollback',frame('rollback',version=False)),('missing_CLOSED',frame('no_terminal',closed=False)),
 ('missing_exit',frame('no_exit',purpose='NATIVE_SEAL',exit_proof=False)),
 ('incomplete_native_input',frame('incomplete_seal',purpose='NATIVE_SEAL',required_records=False)),
 ('closed_new_work',frame('request_work',purpose='ACTIVE')),('closed_budget_rebuild',frame('request_budget_init')),
 ('closed_phase_write',frame('request_phase_write')),('closed_launcher',frame('request_launcher')),
 ('cross_batch_read',frame('request_other_batch',identity=False)),('originals_unchanged',frame('readonly_comparison')),
 ('native_complete_inputs',frame('native_preconditions',purpose='NATIVE_SEAL')),
 ('native_deadline_read',frame('native_window',purpose='NATIVE_SEAL')),
 ('native_budget_read',frame('native_budget',purpose='NATIVE_SEAL')),
 ('native_missing_record',frame('native_missing',purpose='NATIVE_SEAL',required_records=False)),
 ('native_persistence_failure',frame('native_write_error',purpose='NATIVE_SEAL',seal_error=True)),
 ('native_repeat',frame('native_repeat',native_verified=True)),
 ('native_completed_review',frame('native_completed',purpose='HISTORICAL_AUDIT',same_boot=False,native_verified=True)),
 ('native_admin_unsynchronised',frame('admin_already_sealed',internal_status='UNKNOWN'))]
assert len(cases)==32
jobs=[{'case_id':'TR_SAFE_'+name,'mutant':None,'expected_violation':None,'allowed_violations':[],'frames':[f]} for name,f in cases]
pairs=[('grant_terminal_work','TERMINAL_WORK_GRANTED','closed_read_T0'),('rebuild_budget','BUDGET_REBUILT','closed_budget_rebuild'),
 ('skip_identity','IDENTITY_CHECK_SKIPPED','cross_batch_read'),('default_deadline','DEFAULT_DEADLINE_USED','missing_deadline'),
 ('ignore_journal','JOURNAL_CORRUPTION_IGNORED','journal_corrupt'),('upgrade_unknown','UNKNOWN_UPGRADED','native_admin_unsynchronised'),
 ('false_seal','FALSE_SEAL_SUCCESS','native_missing_record'),('write_original','ORIGINAL_EVIDENCE_MODIFIED','originals_unchanged')]
by_name=dict(cases)
for mutant,violation,safe in pairs:
    jobs.append({'case_id':'TR_MUTANT_'+mutant,'mutant':mutant,'expected_violation':violation,'allowed_violations':[violation],
        'safe_control':'TR_SAFE_'+safe,'frames':[copy.deepcopy(by_name[safe])]})
cfg={'schema':'TR-CONTRACT/1','version':'TerminalRead-static-1/r1','batch_id':'batch13','origin':'TR-SIMULATION/1',
    'jobs':jobs,'driver_prepay':16,'completed_visits':681,'hard_visits':960,'max_frames':4,'read_seconds':5,'lock_seconds':2,'lock_attempts':512,
    'journal_max_bytes':33554432,'journal_max_line':32768,'journal_max_records':'2*original_cap+1 EOF probe','native_archive_members':257,
    'native_archive_uncompressed_bytes':33554432,'originals_modified':False,'dynamic_status':'UNRUN',
    'scope':'Synthetic policy/permission observations. Actual readonly byte conservation, native IO and post-CLOSED denial require the separate native seal hook.'}
assert len(jobs)==40 and sum(bool(j['mutant']) for j in jobs)==8
(W/'inputs/terminal_contract.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('TR40 static input constructed:32 safe +8 mutants; no test/oracle run')
