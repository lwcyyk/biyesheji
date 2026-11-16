"""R12 bounded B1-only runner; denies SQLite, network, native services and children."""
import argparse
import ast
import _thread
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback
import unittest


PROJECT = Path(__file__).absolute().parent.parent
R11 = PROJECT.parent/"research_g2_dsat_implementation/2026-11-10_r11"
RECORD_ROOT = PROJECT.parent/"research_g2_dsat_implementation/2026-11-11_r12"
ARTIFACT_ROOT = PROJECT.parent/"research_g2_dsat_implementation/2026-11-10_r12_b1"
FIXTURES = PROJECT/"tests/fixtures/dsat_authority_read"
sys.dont_write_bytecode = True
AUDIT = {"sqlite_attempts":0,"network_attempts":0,"process_attempts":0,"forbidden_file_attempts":0,"violations":[]}
SECRETS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def checked_artifact(path):
    path=Path(path).absolute()
    if not path.is_relative_to(ARTIFACT_ROOT):
        raise RuntimeError("ARTIFACT_PATH_DENIED")
    for part in (path,*path.parents):
        if part.exists() and (part.is_symlink() or part.lstat().st_file_attributes & 0x400):
            raise RuntimeError("ARTIFACT_REPARSE_DENIED")
    if path.resolve()!=path:
        raise RuntimeError("ARTIFACT_PATH_DENIED")
    return path


def audit(event,args):
    if event.startswith("sqlite3.connect"):
        AUDIT["sqlite_attempts"]+=1;AUDIT["violations"].append("SQLITE_DENIED")
        raise RuntimeError("SQLITE_DENIED")
    if event.startswith("socket."):
        AUDIT["network_attempts"]+=1;AUDIT["violations"].append("NETWORK_DENIED")
        raise RuntimeError("NETWORK_DENIED")
    if event in {"subprocess.Popen","os.system","os.startfile"}:
        AUDIT["process_attempts"]+=1;AUDIT["violations"].append("CHILD_PROCESS_DENIED")
        raise RuntimeError("CHILD_PROCESS_DENIED")
    if event=="open" and isinstance(args[0],(str,bytes,os.PathLike)):
        raw=os.fsdecode(args[0]);path=Path(raw).absolute();text=raw.replace("\\","/").lower()
        if "/.runtime/" in text or "/secure/" in text or path.suffix.lower() in {".db",".sqlite3",".sqlite",".key",".aes",".pem",".pfx"}:
            AUDIT["forbidden_file_attempts"]+=1;AUDIT["violations"].append("PRIVATE_OR_DATABASE_FILE_DENIED")
            raise RuntimeError("PRIVATE_OR_DATABASE_FILE_DENIED")
        mode,flags=args[1],args[2]
        writing=(type(mode)is str and any(c in mode for c in "wax+")) or (type(flags)is int and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if writing and not path.is_relative_to(ARTIFACT_ROOT):
            AUDIT["forbidden_file_attempts"]+=1;AUDIT["violations"].append("WRITE_OUTSIDE_ARTIFACT_ROOT")
            raise RuntimeError("WRITE_OUTSIDE_ARTIFACT_ROOT")


def write(path,data):
    path=checked_artifact(path)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def preflight():
    approval=load(RECORD_ROOT/"APPROVAL_RECEIPT.json")
    if approval["approved"] is not True or approval["stage"]!="R11 frozen B1 development and offline doubles only":
        raise RuntimeError("B1_APPROVAL_REQUIRED")
    if sha(Path(approval["task_path"]))!=approval["task_sha256"]:
        raise RuntimeError("APPROVAL_SOURCE_CHANGED")
    baseline=load(RECORD_ROOT/"sources/PRECHECK_LOCK.json")
    for entry in baseline["checks"]:
        if sha(Path(entry["path"]))!=entry["expected"]:
            raise RuntimeError("OLD_SOURCE_OR_HISTORY_CHANGED")
    plan=load(R11/"S3B_TEST_PLAN.json")
    if len(plan["cases"])!=36 or sum(x["stage"]=="B1" for x in plan["cases"])!=33:
        raise RuntimeError("FROZEN_TEST_SCOPE_CHANGED")
    return plan,baseline


class Result(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.rows=[];self.started=0;self.redactions=0
    def startTest(self,test):
        self.started=time.perf_counter_ns();super().startTest(test)
    def _exc_info_to_string(self,err,test):
        text=super()._exc_info_to_string(err,test)
        for value in SECRETS:
            if value in text:
                text=text.replace(value,"[REDACTED_SYNTHETIC_CANARY]");self.redactions+=1
        return text
    def record(self,test,status,detail=None):
        row={"id":test._testMethodName.split("_")[1],"status":status,"executed":True,
             "elapsed_ns":time.perf_counter_ns()-self.started}
        if detail:row["detail"]=detail
        self.rows.append(row)
    def addSuccess(self,test):super().addSuccess(test);self.record(test,"PASS")
    def addFailure(self,test,err):
        super().addFailure(test,err);self.record(test,"FAIL",self._exc_info_to_string(err,test))
    def addError(self,test,err):
        super().addError(test,err);self.record(test,"ERROR",self._exc_info_to_string(err,test))
    def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,"SKIP",reason)


def main():
    start=time.perf_counter_ns();started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    plan,baseline=preflight()
    checked_artifact(ARTIFACT_ROOT).mkdir(exist_ok=True)
    index=1
    while (ARTIFACT_ROOT/("run_%03d"%index)).exists():index+=1
    run=checked_artifact(ARTIFACT_ROOT/("run_%03d"%index));run.mkdir()
    source_paths=[PROJECT/"src/auth_lifecycle/online_state/dsat_authority_read.py",
                  PROJECT/"tests/test_dsat_authority_read.py",Path(__file__).absolute()]
    code=[{"path":str(p),"sha256":sha(p)} for p in source_paths]
    inputs=[{"path":str(p),"sha256":sha(p)} for p in sorted(FIXTURES.glob("*.json"))]
    snapshot=run/"code_snapshot";snapshot.mkdir()
    for path in source_paths:(snapshot/(path.name+".txt")).write_bytes(path.read_bytes())
    write(run/"RUN_START.json",{"command":[sys.executable,"-B",str(Path(__file__).absolute())],
          "python":sys.version,"date_china":"2026-11-11","started_utc":started,"code":code,"inputs":inputs,
          "record_root":str(RECORD_ROOT),"artifact_root_frozen_R11":str(ARTIFACT_ROOT)})
    SECRETS.extend(load(FIXTURES/"CANARIES.json")["sensitive_values"])
    timer=threading.Timer(max(.01,120-(time.perf_counter_ns()-start)/1e9),_thread.interrupt_main)
    timer.daemon=True;timer.start()
    try:
        sys.path.insert(0,str(PROJECT/"src"))
        name="test_dsat_authority_read"
        spec=importlib.util.spec_from_file_location(name,PROJECT/"tests"/(name+".py"))
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
        module.configure(plan,FIXTURES)
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.B1Cases)
        if suite.countTestCases()!=33:
            raise RuntimeError("B1_TEST_DENOMINATOR_CHANGED")
        with (run/"stdout.log").open("w",encoding="utf-8") as output:
            actual=unittest.TextTestRunner(stream=output,verbosity=2,resultclass=Result).run(suite)
        rows={x["id"]:x for x in actual.rows}
        final=[]
        for case in plan["cases"]:
            if case["stage"]=="B2":
                row={"id":case["id"],"status":"BLOCKED","executed":False,"reason":"R11_B2_NOT_AUTHORIZED"}
            else:row=rows.get(case["id"],{"id":case["id"],"status":"NOT_RUN","executed":False})
            final.append({**row,"R11_original_case":case})
        counts={s:sum(x["status"]==s for x in final) for s in ["PASS","FAIL","ERROR","SKIP","BLOCKED","NOT_RUN"]}
        preflight()
        if any(sha(Path(x["path"]))!=x["sha256"] for x in code):raise RuntimeError("CODE_CHANGED_DURING_TEST")
        sink_text=(run/"stdout.log").read_text(encoding="utf-8")+json.dumps(module.DETAILS,ensure_ascii=True)
        clean=all(value not in sink_text for value in SECRETS)
        result={"schema":"r12-b1-actual-run/1","run":str(run),"started_utc":started,
                "finished_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"date_china":"2026-11-11",
                "python":sys.version,"command":[sys.executable,"-B",str(Path(__file__).absolute())],
                "elapsed_ns":time.perf_counter_ns()-start,"frozen_denominator":36,"authorized_B1_denominator":33,
                "executed":len(actual.rows),"counts":counts,"cases":final,"details":module.DETAILS,
                "code_hashes":code,"input_hashes":inputs,"historical_hashes_checked":len(baseline["checks"]),
                "scope_audit":AUDIT,"public_sink_scan":"CLEAN" if clean else "FAIL",
                "failure_log_canary_redactions":actual.redactions,
                "measurement_clocks":{name:{"implementation":time.get_clock_info(name).implementation,
                     "resolution_seconds":time.get_clock_info(name).resolution,
                     "monotonic":time.get_clock_info(name).monotonic} for name in ["perf_counter","monotonic"]},
                "B2_cases_not_executed":["B15","B27","B28"],"S2_solver_or_checker_runs":0,
                "real_authority_reads":0,"production_writes":0,"S3B2_operations":0,"S5_operations":0}
        result["passed_authorized_scope"]=counts=={"PASS":33,"FAIL":0,"ERROR":0,"SKIP":0,"BLOCKED":3,"NOT_RUN":0} and clean and not AUDIT["violations"]
        write(run/"RESULTS.json",result)
        from auth_lifecycle.online_state.dsat_authority_read import staging_schema
        write(run/"B1_STAGING_SCHEMA.json",staging_schema())
    except BaseException:
        text=traceback.format_exc()
        for value in SECRETS:text=text.replace(value,"[REDACTED_SYNTHETIC_CANARY]")
        write(run/"EARLY_FAILURE.json",{"status":"EARLY_FAILURE","traceback":text,"scope_audit":AUDIT})
        raise
    finally:timer.cancel()
    history_path=ARTIFACT_ROOT/"TEST_RUNS.json"
    history=load(history_path) if history_path.exists() else {"schema":"r12-b1-runs/1","runs":[]}
    history["runs"].append({"path":str(run/"RESULTS.json"),"sha256":sha(run/"RESULTS.json"),"counts":counts,"passed":result["passed_authorized_scope"]})
    write(history_path,history)
    print(json.dumps({"run":str(run),"counts":counts,"executed":len(actual.rows),"passed_authorized_scope":result["passed_authorized_scope"]}))
    return 0 if result["passed_authorized_scope"] else 1


if __name__=="__main__":
    sys.addaudithook(audit)
    argparse.ArgumentParser(description=__doc__).parse_args()
    raise SystemExit(main())
