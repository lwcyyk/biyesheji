"""Recover raw PFA originals and known dependency; no target replay."""
from pathlib import Path
import json,hashlib,shutil
E=Path(__file__).resolve().parent;B=E.parent.parent;P=B/'DCL-R6-PTA-PF-A/evidence'
N=Path(r'D:\毕业设计\DCL-R6-isolated-verification\batch12\native_snapshot')
def load(p):return json.loads(Path(p).read_bytes())
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
dest=E/'PFA_ORIGINALS';dest.mkdir();copies=[]
host_names=['NATIVE_SEAL_GAP.json','ACTUAL_RESULTS.json','AUTOMATIC_ADMIN_VERIFICATION.json','STARTUP_FINALIZATION.json','STARTUP_POSTEXIT_PLAN.json',
 'STARTUP_POSTEXIT.stdout.raw','STARTUP_POSTEXIT.stderr.raw','windows_entry.stdout.raw','windows_entry.stderr.raw','EXECUTION_TIMELINE.json','JOURNAL_MESSAGE_INDEX.json','BUDGET_AUDIT.json']
native_names=['inputs/CLOSED.json','inputs/batch_state.json','inputs/PT_RUNTIME_CHECKPOINT.json','inputs/STOP_ARMED.json',
 'inputs/root_private/waitpid_838.json','inputs/root_private/boot/pt_phase.json','inputs/root_private/boot/pt_runtime_intent.json',
 'inputs/root_private/boot/pt_seal_disposition.json','out/visits.bin','out/visits.bin.intent.json','out/visits.bin.journal.jsonl']
for p in [*[P/name for name in host_names],*[N/name for name in native_names]]:
    rel=('host/'+p.relative_to(P).as_posix()) if p.is_relative_to(P) else 'native/'+p.relative_to(N).as_posix();q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    copies.append({'original':str(p),'copy':q.relative_to(E).as_posix(),'sha256':h(p),'bytes':p.stat().st_size})
r=load(P/'ACTUAL_RESULTS.json');facts={'historical_batch':'batch12','source_revision':'PTA-PhaseFinalizer-static-1/r3',
 'boot_id':r['boot_id'],'owner':r['owner'],'scheduler':r['scheduler'],'stopper':r['stopper'],'T0':r['T0'],'R':r['R'],
 'deadline':r['deadline'],'stop_at':r['stop_at'],'closed':r['CLOSED'],'STOP_REQUEST_present':r['STOP_REQUEST_present'],
 'native_disposition':r['native_seal_gap']['native_disposition'],'native_seal':'NATIVE_SEAL_UNRESOLVED','native_zip_created':False,
 'direct_dependency':'Confirmed by frozen call graph and persistent CLOSED; caught exception lacks independent traceback',
 'blocked_path':['M.seal','P.seal_applicability','P.runtime_checkpoint(terminal_inspection=True)','P._phase_guard','P._phase_deadline','G.state','validate_state_document/stopped -> BATCH_STOPPED'],
 'throw_time':'UNKNOWN; CLOSED131.278564941 precedes disposition131.332716174',
 'native_downstream_IO_execution':'UNRUN due applicability rejection; future seal success remains UNRESOLVED',
 'internal_UNKNOWN_source':'mr_close_state.json absent in normal shutdown; admin fallback reads UNKNOWN; no evidence that deadline failure created this absence',
 'internal_close_record_exists':False,'budget':'CONSISTENT1907/1907transactions/3814lines','admin':'ADMIN_EVIDENCE_SEALED171/172',
 'controlled_roles':'EMPTY with original waitpid/stop/journal/automatic audit','originals':copies}
(E/'HISTORICAL_FAILURE_FACTS.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'original_copies':len(copies),'direct_native_dependency':'CONFIRMED_SOURCE_PATH','internal_UNKNOWN':'MISSING_CLOSE_RECORD','target_replay':0},ensure_ascii=False))
