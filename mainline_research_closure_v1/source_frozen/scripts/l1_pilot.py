"""Randomized paired native calibration pilot. No confirmatory execution path."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import time
import uuid
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from auth_lifecycle.experiment.providers import connect,required,NativeError
from auth_lifecycle.experiment.journal import Journal,Gate,ApprovalDenied,BudgetDenied,ResponseLost,canonical,fingerprint
from auth_lifecycle.experiment.witness import Witness
from auth_lifecycle.experiment.resource import Resource
from auth_lifecycle.experiment.planning import plan
from auth_lifecycle.experiment.scoring import score
from auth_lifecycle.b.engine import resources

ROOT=Path(__file__).resolve().parents[1]
PAIRS={"H-A":["A1","B-A"],"H-B":["B","B-B"],"H-AB":["AB1","B-AB"]}


def source_hashes():
    paths=[p for folder in ["src","scripts","tests"] for p in (ROOT/folder).rglob("*.py")]
    return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def execute(provider,meta,family,output):
    started_all=time.perf_counter()
    start_native_calls=provider.http.count+provider.admin_http.count
    provider.admin_login();actor=provider.create_actor("l1-"+uuid.uuid4().hex[:20])
    path=output/"events"/(meta["run_id"]+".jsonl");log=Journal(path,meta)
    log.emit("run_start","fixture",metadata=meta,actor_ref=fingerprint(actor["id"]),fixture_provisioning_excluded_from_method_cost=True)
    gate=Gate(log,meta["Q_cap"],meta["approval_cap"],meta["fault"]);w=Witness(provider,log)
    gate.on_credential=lambda body:w.native_unit(body["access_token"],actor) if w.signed_access(body["access_token"],subject=actor["id"]) else None
    provider.transport=gate.transport;resource=None;outcome="UNKNOWN";initial_access=[];stop_access=[];keep_access=[];opaque=[];expected_g=0;recovery_attempted=False
    started=time.perf_counter();planning_start=time.perf_counter();cache_hits=plan.cache_info().hits
    proposal=plan(provider.name,family["mode"],family["query_client"],meta["goal"],meta["hypothesis"],meta["method"],meta["Q_cap"])
    planning_seconds=time.perf_counter()-planning_start;cache_hit=plan.cache_info().hits>cache_hits;model=proposal["model"];delivery=proposal.get("delivery");issued={}
    model_path=output/"models"/(fingerprint(canonical(model))+".json")
    if not model_path.exists():model_path.write_text(json.dumps(model,indent=2),encoding="utf-8")
    log.emit("plan_result",status=proposal["status"],binding_profile=proposal.get("binding_profile"),model_digest=fingerprint(canonical(model)),solver_work=proposal.get("work",{}))
    try:
        if proposal["status"] in {"IMPOSSIBLE","NO_BASELINE_SOLUTION"}:outcome="REFUSED"
        elif proposal["status"]!="FEASIBLE":outcome=proposal["status"]
        else:
            config=delivery["configuration"];grants,_,units=resources(model,config);expected_g=len(units)
            by_task={t:[p for p in config if model["paths"][p]["task"]==t] for t in model["tasks"]}
            if any(len(ps)!=1 or len(model["paths"][ps[0]]["grants"])!=1 for ps in by_task.values()):raise NativeError("unsupported multi-support L1 binding")
            for grant in sorted(grants):
                if time.perf_counter()-started>meta["timeout_seconds"]:raise TimeoutError()
                log.emit("bound_action",action="configure:"+grant,interface="password_grant",endpoint_class="native_auth")
                issued[grant]=required(provider.issue(actor))
                if "access_token" not in issued[grant]:raise NativeError("native issuance did not return credentials")
            resource=Resource(w,actor,family["mode"],log,family["query_client"])
            resource.bind({t:issued[model["paths"][ps[0]]["grants"][0]]["access_token"] for t,ps in by_task.items()})
            # Workload/scorer observation, also primes the declared RP cache.
            # Never branch the method on this privileged verification result.
            initial_access=[resource.evaluate(t) for t in sorted(model["tasks"])]
            for action in delivery["plans"]["stop"]:
                if time.perf_counter()-started>meta["timeout_seconds"]:raise TimeoutError()
                fields=action.split(":")
                log.emit("bound_action",action=action,endpoint_class="resource_fixture" if fields[0]=="gate" else "native_auth")
                if fields[0]=="gate":gate.call("stop",lambda t=fields[2]:resource.close_task(t),endpoint_class="resource_fixture")
                elif fields[0]=="revoke":required(provider.revoke(issued[fields[1]]["refresh_token"]),200)
                else:raise NativeError("unregistered L1 operation binding")
            outcome="COMPLETED"
    except ApprovalDenied:outcome="REFUSED"
    except BudgetDenied:outcome="UNKNOWN"
    except ResponseLost:
        outcome="UNKNOWN"
        # The loss occurs on the first issuance, before any preserve task is
        # installed. Account cleanup cannot destroy an already-delivered keeper.
        if issued:raise RuntimeError("loss recovery would require a preserve-aware state mapping")
        recovery_attempted=True
        try:
            provider.root_stop(actor);log.emit("recovery_dispatched",operation="owned_account_root")
        except Exception as error:log.emit("recovery_failed",error_type=type(error).__name__)
    except TimeoutError:outcome="TIMEOUT"
    except Exception as error:
        outcome="UNKNOWN";log.emit("execution_error",error_type=type(error).__name__,reason=str(error)[:160])
    finally:
        if outcome in {"UNKNOWN","TIMEOUT"} and resource is None and not recovery_attempted and (issued or gate.uncertain_creation_requests):
            recovery_attempted=True
            try:provider.root_stop(actor);log.emit("recovery_dispatched",operation="owned_account_root_after_uncommitted_setup")
            except Exception as error:log.emit("recovery_failed",error_type=type(error).__name__)
        if time.perf_counter()-started>meta["timeout_seconds"]:outcome="TIMEOUT"
        log.emit("method_end",status=outcome,elapsed_seconds=time.perf_counter()-started)
        # From this point only the independent scorer uses private observations;
        # no further method dispatch or replanning is possible.
        if recovery_attempted or gate.uncertain_creation_requests:
            opaque=[w.accepted(body["access_token"],family["mode"],subject=actor["id"],query_client=family["query_client"]) for body in gate.private_effects]
            log.emit("material_disposition_observed","witness",registered_resource_mode=family["mode"],still_accepted=opaque,
                     unresolved_inflight=gate.uncertain_creation_requests)
        if resource:
            scenario=model["scenarios"]["stop"]
            stop_access=[resource.evaluate(t,False) for t in scenario["local"]]+[resource.evaluate(t,True) for t in scenario["remote"]]
            keep_access=[resource.evaluate(t) for t in scenario["preserve"]]
        if meta["fault"]!="none" and not gate.triggered:log.emit("fault_not_triggered","fault",fault=meta["fault"])
        measured=score(path,meta,outcome,initial_access,stop_access,keep_access,opaque,expected_g,gate.uncertain_creation_requests)
        measured.update(planning_seconds=planning_seconds,planning_cache_hit=cache_hit,wall_seconds=time.perf_counter()-started,feedback_calls=proposal.get("work",{}).get("feedback_calls",0),probe_selection_count=0)
        log.emit("independent_score","scorer",metrics=measured)
        provider.transport=None
        try:
            provider.root_stop(actor);provider.remove_actor(actor)
            log.emit("fixture_reset","fixture",actor_deleted=True,reason="paired isolation after immutable scoring; keeper task may now be removed",counted=False)
        except Exception as error:log.emit("fixture_reset_failed","fixture",error_type=type(error).__name__)
        log.emit("infrastructure_accounting","fixture",native_HTTP_calls_including_witness_and_setup=provider.http.count+provider.admin_http.count-start_native_calls+w.http.count,
                 method_Q=measured["Q_total"],measurement_and_fixture_not_hidden=True,total_run_seconds_including_fixture=time.perf_counter()-started_all)
        if resource:resource.shutdown()
        log.close()
    return {"metadata":meta,"metrics":measured,"proposal":{"status":proposal["status"],"configuration":delivery["configuration"] if delivery else None,"work":proposal.get("work",{}),
            "binding_profile":proposal.get("binding_profile"),"query_needed_profile":False},"event_file":path.relative_to(output).as_posix()}


def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);p.add_argument("--plan",default="experiments/pilot-plan.json");p.add_argument("--environment-lock",default=str(ROOT/"experiments/l1/environment.lock.json"));p.add_argument("--max-pairs",type=int);p.add_argument("--phase",choices=["pilot","confirmatory"],default="pilot");args=p.parse_args()
    if args.phase!="pilot":raise SystemExit("CONFIRMATORY BLOCKED: researcher freeze and native query-dependent/held-out mappings are not complete")
    plan_data=json.loads(Path(args.plan).read_text(encoding="utf-8"));lock=Path(args.environment_lock).resolve()
    for key in ["repetitions","request_cap","grant_cap","approval_cap","method_timeout_seconds"]:
        if type(plan_data[key])is not int or plan_data[key]<=0:raise SystemExit("invalid pilot budget/count")
    if plan_data["formal"]is not False or plan_data["grant_cap"]!=8 or plan_data["approval_cap"]!=8:raise SystemExit("unsupported or non-pilot profile")
    if not lock.exists():raise SystemExit("native capability/version lock required before pilot")
    environment=json.loads(lock.read_text(encoding="utf-8"))
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=False);(out/"events").mkdir();(out/"models").mkdir();hashes=source_hashes();code_hash=fingerprint(canonical(hashes))
    (out/"source_hashes.json").write_text(json.dumps(hashes,indent=2),encoding="utf-8")
    with zipfile.ZipFile(out/"source_bundle.zip","x",zipfile.ZIP_DEFLATED) as archive:
        for name in hashes:archive.write(ROOT/name,name)
        for path in (ROOT/"experiments").glob("*.json"):archive.write(path,path.relative_to(ROOT).as_posix())
    (out/"plan.json").write_text(json.dumps(plan_data,indent=2),encoding="utf-8")
    rng=random.Random(plan_data["seed"]);cases=[]
    for implementation in plan_data["implementations"]:
        for hypothesis in plan_data["hypotheses"]:
            for family_id in plan_data["families"]:
                for goal in plan_data["goals"]:
                    for fault in plan_data["faults"]:
                        for repeat in range(plan_data["repetitions"]):cases.append((implementation,hypothesis,family_id,goal,fault,repeat))
    rng.shuffle(cases)
    if args.max_pairs is not None:cases=cases[:args.max_pairs]
    queue=[]
    for i,case in enumerate(cases):
        methods=list(PAIRS[case[1]]);rng.shuffle(methods);queue.append({"pair_id":f"p{i:04}","case":list(case),"order":methods})
    (out/"scheduled_pairs.json").write_text(json.dumps(queue,indent=2),encoding="utf-8")
    from l1_freeze_environment import public_config
    providers={name:connect(name) for name in plan_data["implementations"]};rows=[]
    for name,provider in providers.items():
        if fingerprint(canonical(public_config(provider)))!=environment["implementations"][name]["configuration_sha256"]:raise SystemExit("native configuration drift: "+name)
    import platform,cryptography
    (out/"environment.json").write_text(json.dumps({"python":sys.version,"platform":platform.platform(),"cryptography":cryptography.__version__,"native_lock":environment,
        "source_sha256":code_hash,"command":[sys.executable,*sys.argv],"code_commit":None,"started_utc":datetime.now(timezone.utc).isoformat()},ensure_ascii=False,indent=2),encoding="utf-8")
    pilot_started=time.perf_counter()
    with (out/"runs.jsonl").open("x",encoding="utf-8") as log:
        for item in queue:
            implementation,hypothesis,family_id,goal,fault,repeat=item["case"];family=plan_data["families"][family_id]
            for order,method in enumerate(item["order"]):
                meta={"run_id":item["pair_id"]+"-"+method,"pair_id":item["pair_id"],"phase":"PILOT_CALIBRATION","formal":False,
                      "hypothesis":hypothesis,"method":method,"implementation":implementation,"version":providers[implementation].version,
                      "family_id":family_id,"lineage":family["lineage"],"independence_attested":False,"goal":goal,"fault":fault,"repeat":repeat,
                      "randomized_order":order,"seed":plan_data["seed"],"Q_cap":plan_data["request_cap"],"G_cap":plan_data["grant_cap"],"approval_cap":plan_data["approval_cap"],
                      "timeout_seconds":plan_data["method_timeout_seconds"],"code_commit":None,"source_sha256":code_hash,
                      "environment_digest":fingerprint(canonical(environment)),"approval_package":"same configure/stop/cleanup permissions for owned actor; withdrawal fault explicit",
                      "available_interfaces_digest":fingerprint(canonical(environment["native_interfaces"])),"initial_state_contract":"fresh owned actor; zero pre-existing test grants; no reset within method",
                      "approval_charge_kind":"pre-authorized grant slots, not observed human prompts","human_approval_interactions":0,
                      "approved_operations_initial":["configure","probe","stop","cleanup","refresh"],
                      "formal_effect_distribution_eligible":False}
                row=execute(providers[implementation],meta,family,out);rows.append(row);log.write(canonical(row)+"\n");log.flush()
            print(item["pair_id"],implementation,hypothesis,family_id,goal,fault,[x["metrics"]["status"] for x in rows[-2:]],flush=True)
    summary={"phase":"PILOT_CALIBRATION","pairs":len(queue),"runs":len(rows),"complete":sum(r["metrics"]["U"] for r in rows),
             "safety_E":sum(r["metrics"]["E"] for r in rows),"false_assurance_FA":sum(r["metrics"]["FA"] for r in rows),
             "source_unchanged":hashes==source_hashes(),"source_sha256":code_hash,"formal_hypotheses":"NOT_TESTED",
             "wall_seconds_including_native_runs":time.perf_counter()-pilot_started,
             "limitations":["known-contract calibration; query-needed A/AB L1 mapping not implemented","four related RP families, no attested independent family population","no confirmatory threshold approved"]}
    (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps(summary,ensure_ascii=False))


if __name__=="__main__":main()
