"""Run ONLY the R09-approved synthetic S3-A suite or an owned child worker.

No native services, old test discovery, optimizer, network or dependency install.
"""
import argparse
import _thread
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import threading
import traceback
import unittest
from urllib.parse import unquote


PROJECT = Path(__file__).absolute().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(PROJECT/"src"))
from auth_lifecycle.online_state.dsat_commit_types import (
    Actor, CommitError, DB_ROOT, PROJECT, RUN_ROOT, SCOPE_PATH, canonical, strict_load,
)
from auth_lifecycle.online_state.dsat_commit import FrozenRegistry, artifact_path
from auth_lifecycle.online_state.dsat_synthetic_store import SyntheticStore


RECORD_ROOT = SCOPE_PATH.parent.parent/"2026-11-10_r10"
AUDIT = {"sqlite_connections":0,"subprocesses":0,"blocked_accesses":[]}


def safety_audit(event,args):
    if event.startswith("socket."):
        AUDIT["blocked_accesses"].append(event)
        raise RuntimeError("network outside S3-A scope")
    if event=="open" and isinstance(args[0],(str,bytes,os.PathLike)):
        text=os.fsdecode(args[0]).replace("\\","/").lower()
        if "/.runtime/" in text or text.endswith("/authority.db"):
            AUDIT["blocked_accesses"].append(event)
            raise RuntimeError("real-state file outside S3-A scope")
    if event=="sqlite3.connect":
        text=unquote(str(args[0])).split("?")[0]
        if text.startswith("file:///"):text=text[8:]
        path=Path(text)
        if path.parent!=DB_ROOT or not path.match("dsat_s3a_*.sqlite3"):
            AUDIT["blocked_accesses"].append(event)
            raise RuntimeError("SQLite outside owned synthetic subtree")
        AUDIT["sqlite_connections"]+=1
    if event=="subprocess.Popen":
        command=args[1]
        approved=(PROJECT/"scripts/check_dsat_certificate.py",PROJECT/"scripts/run_dsat_s3a_tests.py")
        if isinstance(command,str):
            # Windows emits its already quoted command line in this audit event.
            allowed=any(command.startswith(subprocess.list2cmdline([sys.executable,"-B",str(script)])+" ") for script in approved)
        else:
            allowed=len(command)>=3 and Path(command[0])==Path(sys.executable) and command[1]=="-B" and Path(command[2]) in approved
        if not allowed:
            AUDIT["blocked_accesses"].append(event)
            raise RuntimeError("child outside approved Python/checker/runner")
        AUDIT["subprocesses"]+=1


def write(path, value):
    path = artifact_path(path)
    temporary = path.with_suffix(path.suffix+".tmp")
    with temporary.open("wb") as handle:
        handle.write(canonical(value)); handle.flush(); os.fsync(handle.fileno())
    os.replace(temporary, path)


def wait_flag(folder, name):
    deadline = time.monotonic()+10
    while not (folder/name).is_file():
        if time.monotonic()>deadline:
            raise TimeoutError("owned worker handshake deadline")
        time.sleep(.01)


def worker(config_path):
    config_path = artifact_path(config_path)
    conf = strict_load(config_path.read_bytes())
    folder = artifact_path(conf["folder"])
    if folder != config_path.parent:
        raise CommitError("DB_PATH_DENIED")
    registry = FrozenRegistry(folder/"checker_cache")
    registry.load_ready(conf["ready_registry"])
    store = SyntheticStore(conf["database"])
    snapshot = store.recover()
    anchor = store._connect()  # Each simultaneously live worker owns its own connection.
    try:
        write(folder/"prepared.json", {"pid":os.getpid(), "a":snapshot["a"],
              "instance":snapshot["world"]["authority_instance"], "connection":id(anchor),
              "action":conf["action"], "stage":conf["stage"]})
        wait_flag(folder,"go")
        def hook(stage, connection):
            if stage == conf["stage"]:
                write(folder/"hook.json", {"stage":stage, "pid":os.getpid(),
                    "in_transaction":bool(connection.in_transaction) if connection is not None else False,
                    "observed_a":connection.execute("SELECT version FROM s3a_state").fetchone()[0] if connection is not None else snapshot["a"]})
                wait_flag(folder,"go_hook")
        if conf["action"]=="handoff":
            hook(conf["stage"],None)
            result={"status":"HANDOFF_ONLY_NO_WORLD_WRITE"}
        elif conf["action"]=="submit":
            result=store.commit(conf["body"],Actor(conf["actor"]),registry,conf["now"],hook)
        elif conf["action"]=="event":
            result=store.domain_event(conf["event"])
        elif conf["action"]=="external":
            write(folder/"external_model.json",conf["event"])
            result={"status":"EXTERNAL_MODEL_ONLY","local_a_unchanged":store.read()["a"]}
        else:
            raise CommitError()
        write(folder/"output.json",{"result":result,"metrics":store.metrics,"scope_audit":AUDIT})
    finally:
        anchor.close()


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight():
    lock = strict_load((SCOPE_PATH.parent/"SOURCE_LOCK.json").read_bytes())
    for item in lock["checks"]:
        if sha(Path(item["path"])) != item["expected_sha256"]:
            raise RuntimeError("old-file conflict: "+item["path"])
    qa = strict_load((SCOPE_PATH.parent/"sources/DELIVERY_QA.json").read_bytes())
    for item in qa["outputs"]:
        if sha(Path(item["path"])) != item["sha256"]:
            raise RuntimeError("R09 lock conflict: "+item["path"])
    approval = strict_load((RECORD_ROOT/"APPROVAL_RECEIPT.json").read_bytes())
    if approval["approved"] is not True or approval["stage"]!="R09 frozen S3-A only":
        raise RuntimeError("missing R10 scope approval")
    if sha(Path(approval["task_path"])) != approval["task_sha256"]:
        raise RuntimeError("approval source changed")
    anchors = strict_load((SCOPE_PATH.parent/"sources/PATH_ANCHOR_REVIEW.json").read_bytes())
    for item in anchors["paths"]:
        if item.get("exists"):
            st=Path(item["path"]).stat()
            if [st.st_dev,st.st_ino] != [item["st_dev"],item["st_ino"]]:
                raise RuntimeError("parent identity changed")
    return lock


def copy_fixtures(scope):
    root=PROJECT/"tests/fixtures/dsat_commit"
    for node in (root,*root.parents):
        if node.exists() and (node.is_symlink() or node.lstat().st_file_attributes & 0x400):
            raise CommitError("DB_PATH_DENIED")
    if root.absolute()!=root.resolve():
        raise CommitError("DB_PATH_DENIED")
    root.mkdir(exist_ok=True)
    refs=scope["frozen_inputs"]["fixtures"]+scope["frozen_inputs"]["proofs"]
    manifest=[]
    for ref in refs:
        source=Path(ref["path"]);target=root/source.name
        if sha(source)!=ref["sha256"]:
            raise RuntimeError("input hash conflict")
        if target.exists():
            if sha(target)!=ref["sha256"]:raise RuntimeError("new fixture changed: "+str(target))
        else:
            with target.open("xb") as handle:handle.write(source.read_bytes())
        manifest.append({"source":str(source),"copy":str(target),"sha256":ref["sha256"]})
    path=root/"FROZEN_INPUTS.json"
    data=canonical({"scope":"SYNTHETIC_CONTRACT","inputs":manifest,"variant_recipe":scope["frozen_inputs"]["variant_source"]})
    if path.exists():
        if path.read_bytes()!=data:raise RuntimeError("fixture manifest conflict")
    else:
        with path.open("xb") as handle:handle.write(data)
    return manifest


class RecordingResult(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.rows=[];self.stamp=time.perf_counter_ns();self.suite_start=time.monotonic()
    def startTest(self,test):
        self.stamp=time.perf_counter_ns();super().startTest(test)
    def addSuccess(self,test):
        super().addSuccess(test);self.rows.append({"id":test._testMethodName.split("_")[1],"status":"PASS","elapsed_ns":time.perf_counter_ns()-self.stamp})
    def addFailure(self,test,err):
        super().addFailure(test,err);self.rows.append({"id":test._testMethodName.split("_")[1],"status":"FAIL","traceback":self._exc_info_to_string(err,test)})
    def addError(self,test,err):
        super().addError(test,err);self.rows.append({"id":test._testMethodName.split("_")[1],"status":"ERROR","traceback":self._exc_info_to_string(err,test)})
    def addSkip(self,test,reason):
        super().addSkip(test,reason);self.rows.append({"id":test._testMethodName.split("_")[1],"status":"SKIP","reason":reason})
    def stopTest(self,test):
        super().stopTest(test)
        if time.monotonic()-self.suite_start>=180:self.stop()


def main():
    start=time.perf_counter_ns();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    preflight()
    artifact_path(RUN_ROOT).mkdir(exist_ok=True);artifact_path(DB_ROOT).mkdir(exist_ok=True)
    runs=artifact_path(RUN_ROOT/"runs");runs.mkdir(exist_ok=True)
    index=1
    while (runs/("run_%03d"%index)).exists():index+=1
    run_dir=runs/("run_%03d"%index);run_dir.mkdir()
    write(run_dir/"RUN_START.json",{"command":[sys.executable,"-B",str(Path(__file__).absolute())],"start_utc":utc,
        "python":sys.version,"sqlite":sqlite3.sqlite_version,"scope":"R09 S3-A only","owned_runner_pid":os.getpid()})
    snapshot=run_dir/"code_snapshot";snapshot.mkdir()
    for rel in strict_load(SCOPE_PATH.read_bytes())["new_relative_paths"]:
        source=PROJECT/rel
        if source.suffix==".py":(snapshot/(source.name+".txt")).write_bytes(source.read_bytes())
    timer=threading.Timer(max(.01,180-(time.perf_counter_ns()-start)/1e9),_thread.interrupt_main)
    timer.daemon=True;timer.start()
    try:
        scope=strict_load(SCOPE_PATH.read_bytes());copy_fixtures(scope)
        matrix=strict_load((SCOPE_PATH.parent/"S3A_TEST_MATRIX.json").read_bytes())
        registry=FrozenRegistry(run_dir/"checker");registry.verify_all()
        ready=run_dir/"trusted_ready.json";registry.save_ready(ready)
        sys.path.insert(0,str(PROJECT/"tests"))
        modules=[]
        for name in ("contract","store","recovery"):
            module_name="test_dsat_commit_"+name
            spec=importlib.util.spec_from_file_location(module_name,PROJECT/"tests"/(module_name+".py"))
            module=importlib.util.module_from_spec(spec);sys.modules[module_name]=module;spec.loader.exec_module(module);modules.append(module)
        helper=modules[0];helper.configure(registry,run_dir,ready,matrix)
        suite=unittest.TestSuite()
        for module,cls in zip(modules,("ContractCases","StoreCases","RecoveryCases")):
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(module,cls)))
        if suite.countTestCases()!=46:raise RuntimeError("unexpected top-level test denominator")
        with (run_dir/"stdout.log").open("w",encoding="utf-8") as output:
            result=unittest.TextTestRunner(stream=output,verbosity=2,resultclass=RecordingResult).run(suite)
        rows={x["id"]:x for x in result.rows};details={x["id"]:x for x in helper.RESULTS}
        subrows=[]
        for case in matrix["cases"]:
            executed={x["index"]:x for x in details.get(case["id"],{}).get("subassertions",[])}
            for i,description in enumerate(case["mandatory_subcases"],1):
                subrows.append({"id":case["id"],"index":i,"description":description,"status":executed.get(i,{}).get("status","NOT_RUN")})
        old=preflight()
        totals={status:sum(x["status"]==status for x in rows.values()) for status in ("PASS","FAIL","ERROR","SKIP")}
        totals["NOT_RUN"]=46-len(rows)
        new_sources=[PROJECT/x for x in scope["new_relative_paths"] if x.endswith(".py")]
        actual={"schema":"dsat-s3a-actual-run/1","run_directory":str(run_dir),"start_utc":utc,
            "end_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"elapsed_ns":time.perf_counter_ns()-start,
            "python":sys.version,"sqlite":sqlite3.sqlite_version,"command":[sys.executable,"-B",str(Path(__file__).absolute())],
            "totals":totals,"top_level_denominator":46,"rows":list(rows.values()),"mandatory_subassertions":subrows,
            "mandatory_subassertion_denominator":39,"details":helper.RESULTS,"checker_records":registry.checks,
            "code_hashes":[{"path":str(x),"sha256":sha(x)} for x in new_sources],
            "old_hashes_checked":len(old["checks"]),"old_mismatches":[],"native_operations":0,"S3B_operations":0,
            "C_native":"NOT_MEASURED","S3B_performance":"NOT_RUN"}
        actual["scope_audit"]=AUDIT
        actual["passed"]=totals["PASS"]==46 and sum(x["status"]=="PASS" for x in subrows)==39 and len(subrows)==39
        write(run_dir/"RESULTS.json",actual)
    except BaseException:
        error={"status":"EARLY_FAILURE","traceback":traceback.format_exc(),"run_directory":str(run_dir)}
        write(run_dir/"EARLY_FAILURE.json",error)
        history_path=RECORD_ROOT/"TEST_RUNS.json"
        history=strict_load(history_path.read_bytes()) if history_path.exists() else {"schema":"r10-actual-runs/1","runs":[]}
        history["runs"].append({"path":str(run_dir/"EARLY_FAILURE.json"),"sha256":sha(run_dir/"EARLY_FAILURE.json"),"status":"EARLY_FAILURE","passed":False})
        history_path.write_bytes(canonical(history))
        print(json.dumps(error,ensure_ascii=True));raise
    finally:
        timer.cancel()
    history_path=RECORD_ROOT/"TEST_RUNS.json"
    history=strict_load(history_path.read_bytes()) if history_path.exists() else {"schema":"r10-actual-runs/1","runs":[]}
    history["runs"].append({"path":str(run_dir/"RESULTS.json"),"sha256":sha(run_dir/"RESULTS.json"),"totals":totals,"passed":actual["passed"]})
    history_path.write_bytes(canonical(history))
    print(json.dumps({"run":str(run_dir),"totals":totals,"subassertions":{"PASS":sum(x["status"]=="PASS" for x in subrows),"denominator":39},"passed":actual["passed"]}))
    return 0 if actual["passed"] else 1


if __name__=="__main__":
    sys.addaudithook(safety_audit)
    parser=argparse.ArgumentParser();parser.add_argument("--worker");args=parser.parse_args()
    if args.worker:worker(args.worker)
    else:raise SystemExit(main())
