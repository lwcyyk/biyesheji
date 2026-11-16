"""Recover selected historical originals without target imports or WSL calls."""
from pathlib import Path
import hashlib,json,shutil,zipfile
E=Path(__file__).resolve().parent;B=E.parent.parent;OLD=B/'DCL-R6-PreT0-A/evidence'
N=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch11\native_snapshot')
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def put(name,x):(E/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dest=E/'PTA_ORIGINALS';dest.mkdir();rows=[]
for p in [*[OLD/n for n in ['windows_entry.stdout.raw','windows_entry.stderr.raw','STARTUP_POSTEXIT.stderr.raw','STARTUP_POSTEXIT_PLAN.json','STARTUP_FINALIZATION.json','RUN_BOOT_JOURNAL.stdout.raw','JOURNAL_MESSAGE_INDEX.json','ACTUAL_RESULTS.json','NATIVE_SEAL_VERIFICATION.json']],
 *[N/n for n in ['inputs/PT_RUNTIME_CHECKPOINT.json','inputs/batch_state.json','inputs/STOP_ARMED.json','inputs/CLOSED.json','out/STOP_REQUEST.json','out/visits.bin','out/visits.bin.intent.json','out/EVIDENCE_MANIFEST.json',
 'inputs/root_private/boot/pt_events.jsonl','inputs/root_private/boot/pt_phase.json','inputs/root_private/boot/pt_runtime_intent.json','inputs/root_private/boot/mr_first_failure.json','inputs/root_private/boot/mr_close_attempts.jsonl','inputs/root_private/boot/mr_close_state.json']]]:
    rel=('host/'+p.relative_to(OLD).as_posix()) if p.is_relative_to(OLD) else 'native/'+p.relative_to(N).as_posix()
    q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows.append({'original':str(p),'copy':q.relative_to(E).as_posix(),'sha256':h(p),'bytes':p.stat().st_size})
private=load(N/'inputs/root_private/boot/pt_phase.json');public=load(N/'inputs/PT_RUNTIME_CHECKPOINT.json');intent=load(N/'inputs/root_private/boot/pt_runtime_intent.json')
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
counter=(N/'out/visits.bin').read_bytes();actual=load(OLD/'ACTUAL_RESULTS.json')
facts={'historical_batch':'batch11','revision':'PreT0Recovery-static-1/r3','boot_id':actual['boot_id'],
 'raiser':'startup_lifecycle.runtime_checkpoint line184','checker_identity':actual['external_stop'],'writer_identity':actual['scheduler'],
 'predicate':"sha(initialization_intent)!=q.initialization_id OR private_phase.phase!=q.phase",
 'historical_expected_operand':None,'historical_observed_operand':None,'historical_init_digest_comparison_result':None,
 'historical_exact_operands':'UNKNOWN','historical_exact_root_cause':'PT_RUNTIME_PHASE_DRIFT_ROOT_CAUSE_UNRESOLVED',
 'source_defect':'Confirmed allowed two-file writer/reader interleaving without a common mutex; independent of exact historical schedule',
 'source_counterexample':[
  {'step':1,'actor':'reader892','action':'read public q','q_phase':'RUNTIME_READY','q_sequence':4},
  {'step':2,'actor':'writer887','action':'durably write private phase','private_phase':'RUNTIME_ARMED','sequence':5},
  {'step':3,'actor':'reader892','action':'read new private phase and compare old q','result':'PT_RUNTIME_PHASE_DRIFT'},
  {'step':4,'actor':'writer887','action':'publish public armed checkpoint','q_phase':'RUNTIME_ARMED','q_sequence':5}],
 'counterexample_class':'SOURCE_SCHEDULE_WITNESS_ONLY; no replay executed',
 'case_A':'Legal incomplete transition possible by source order; exact occurrence UNKNOWN',
 'case_B':'Mixed observation possible by source order; exact occurrence UNKNOWN',
 'case_C':'No preserved persistent illegal phase chain; instantaneous corruption/other combined predicate branch not excluded by missing operands',
 'final_snapshot_public_phase':public['phase'],'final_snapshot_private_phase':private['phase'],
 'final_snapshot_sequences':[public['sequence'],private['sequence']],
 'final_initialization_digest_matches':hashlib.sha256(canonical(intent)).hexdigest()==public['initialization_id'],
 'T0':actual['T0'],'R':actual['R'],'counter_sha256':h(N/'out/visits.bin'),'native_seal':'NATIVE_SEAL_COMPLETED',
 'native_zip_sha256':h(N/'out/EVIDENCE.zip'),'native_zip_bytes':(N/'out/EVIDENCE.zip').stat().st_size,
 'module_failure':{'type':'ModuleNotFoundError','module':'boot_continuity','file':'startup_lifecycle.py','line':11,
   'argv':load(OLD/'STARTUP_POSTEXIT_PLAN.json')['argv'],'cwd':'UNKNOWN','sys_path_snapshot':'UNKNOWN; isolation flag and import source are known',
   'interpreter':'/usr/bin/python3.12 3.12.3','identity':'Root via frozen WSL --user root argv; no native post audit produced',
   'permissions_at_failure':'No permissions traceback; boot_continuity.py present in49-file deployed snapshot',
   'outcome':load(OLD/'STARTUP_FINALIZATION.json')},'originals':rows}
put('HISTORICAL_FAILURE_FACTS.json',facts)
print(json.dumps({'historical_operands':'UNKNOWN','source_counterexample_steps':4,'original_copies':len(rows),'native_seal':'NATIVE_SEAL_COMPLETED','WSL_calls':0},ensure_ascii=False))
