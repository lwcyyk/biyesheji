"""M4 dedicated-organization enumeration. Existing scope remains read-only."""

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
import subprocess
import sys
import time

from .lab import protect_directory
from .native_acceptance import preflight, create_actor, configure_case, native_request, observe, cleanup_actor, require
from .native_http import create_budget
from .protocol import write_json
from .reconciliation_acceptance import source_model, wait_file


LIMITS = {"environment": 60, "method": 60, "measurement": 40, "cleanup": 60}


def setup_scope(admin, batch, template, scope):
    reference = admin.call("application")["body"].get("data", {})
    certificate = reference.get("cert")
    if not certificate:
        raise RuntimeError("EXTRA_CERTIFICATE_DEPENDENCY_UNSATISFIED")
    if admin.call("owned_organization")["body"].get("data") is not None:
        raise RuntimeError("OWNED_ORGANIZATION_ALREADY_EXISTS")
    intent = {"organization": scope["organization"], "application": scope["application_name"],
              "organization_attempted": True, "application_attempted": False}
    write_json(batch / "secure/scope_intent.json", intent)
    org = {"owner": "admin", "name": scope["organization"], "displayName": "Owned M4 isolated scope", "passwordType": "bcrypt"}
    if admin.call("add_organization", payload=org)["body"].get("status") != "ok":
        raise RuntimeError("ORGANIZATION_CREATE_UNCERTAIN")
    organization = admin.call("owned_organization")["body"].get("data")
    if not organization or organization.get("name") != scope["organization"]:
        raise RuntimeError("ORGANIZATION_READBACK_FAILED")
    if admin.call("owned_application")["body"].get("data") is not None:
        raise RuntimeError("OWNED_APPLICATION_ALREADY_EXISTS")
    secret = secrets.token_urlsafe(32)
    intent["application_attempted"] = True
    write_json(batch / "secure/scope_intent.json", intent)
    app = {"owner": "admin", "name": scope["application_name"], "displayName": "Owned M4 application",
        "organization": scope["organization"], "clientId": scope["client_id"], "clientSecret": secret,
        "cert": certificate, "tokenSigningMethod": reference.get("tokenSigningMethod") or "RS256",
        "tokenFormat": "JWT", "grantTypes": ["password", "refresh_token"], "expireInHours": 1,
        "refreshExpireInHours": 1, "disableRefreshRotation": False, "enablePassword": True,
        "enableSignUp": False, "isShared": False, "providers": []}
    if admin.call("add_application", payload=app)["body"].get("status") != "ok":
        raise RuntimeError("APPLICATION_CREATE_UNCERTAIN")
    loaded = admin.call("owned_application")["body"].get("data")
    if not loaded or loaded.get("organization") != scope["organization"] or loaded.get("clientId") != scope["client_id"]:
        raise RuntimeError("APPLICATION_READBACK_FAILED")
    profile = {**template, "organization": scope["organization"], "application_name": scope["application_name"],
        "client_id": scope["client_id"], "client_secret": secret, "durable_inbox": False, "identifier_journal": False,
        "query_mode": "AUTHORIZED_SCOPE_ENUMERATION", "measurement_no_refresh": True}
    write_json(batch / "secure/scope_profile.json", profile)
    write_json(batch / "SCOPE_ENVIRONMENT.json", {"organization": org, "application": {k:loaded.get(k) for k in
        ("name","organization","clientId","cert","tokenSigningMethod","tokenFormat","grantTypes","expireInHours","refreshExpireInHours","disableRefreshRotation")},
        "reused_existing_certificate": certificate, "new_native_objects_allowed": {"organization":1,"application":1,"accounts":3},
        "new_certificates_providers_or_policies":0,"read_scope":"ALL_TOKEN_RECORDS_IN_DEDICATED_ORGANIZATION"})
    return profile


def configure(root, profile, model):
    lab = configure_case(root, profile)
    lab.configs["provider"]["permissions"]["adapter"].append("reconcile_query")
    lab.configs["controller"]["permissions"]["user"] += ["begin_reconciliation", "reconcile"]
    lab.configs["controller"]["reconciliation_model"] = model
    lab.configs["authority"]["permissions"]["controller"] += ["begin_reconciliation", "reconciliation_context", "save_reconciliation"]
    for role, config in lab.configs.items():
        write_json(root / "secure" / (role + ".json"), config)
    return lab


def enroll(lab, profile, task, generation, caller=None):
    caller = caller or "agent" + task
    login = {"schema":2,"kind":"casdoor_login","issuer":profile["base"],"client":profile["client_id"],
        "expected_account":profile["actor"]["id"],"username":profile["actor"]["name"],"password":profile["actor"]["password"]}
    grant = require(lab.client(timeout=12).call("grant", {"approval_op":"approve_"+task,"caller":caller,"task":task,
        "account":profile["actor"]["id"],"audience":profile["client_id"],"generation":generation,
        "operations":["issue","refresh","userinfo"],"budget":10,"material":login}),"GRANTED")
    issued = lab.client(caller,timeout=12).call("call",native_request(grant["handle"],profile,task,generation,task+"0","issue"))
    require(issued,"RESULT_AVAILABLE")
    return grant


def check_interferer(lab, profile, grant, suffix):
    request = native_request(grant["handle"],profile,"I","i0","I_check_"+suffix,"userinfo","I0")
    return require(lab.client("agentB",timeout=12).call("call",request),"RESULT_AVAILABLE")


def run_case(batch, root, profile, model, scenario, interferer_lab, interferer_profile, interferer_grant):
    lab = configure(root,profile,model)
    outcome = {"scenario":scenario,"status":"RUNNING"}
    try:
        lab.start_all()
        user = lab.client(timeout=12)
        a = enroll(lab,profile,"A","g0")
        b = enroll(lab,profile,"B","g1")
        write_json(root/"runner/initial_visible.json",user.call("status",{}))
        initial = observe(batch,root,"initial")
        if not all(r["accepted"] is True for r in initial["rows"]):
            raise RuntimeError("INITIAL_ACCEPTANCE_FAILED")
        if scenario=="M4-01":
            lab.restart_controller("after_effect")
        pending=lab.async_call("agentA","call",native_request(a["handle"],profile,"A","g0","A1","refresh","A0"))
        if scenario=="M4-01":
            lab.wait_barrier("after_effect")
            lab.stop("controller")
            outcome["lost_response"]=pending.result(timeout=5)
            lab.start("controller")
        else:
            wait_file(root/"provider/before_native_refresh.json")
        require(user.call("revoke",{"revoke_op":"retireA","grant_id":a["grant_id"]}),"LOCAL_REVOKE_COMMITTED")
        require(user.call("begin_reconciliation",{"rid":"A1","window_id":"window1"}),"WINDOW_OPEN")
        outcome["B_creation_paused"]=require(lab.client("agentB").call("call",native_request(b["handle"],profile,"B","g1","B_create","refresh","B0")),"REJECTED")
        require(lab.client("agentB",timeout=12).call("call",native_request(b["handle"],profile,"B","g1","B_inside","userinfo","B0")),"RESULT_AVAILABLE")
        pre=user.call("status",{})
        outcome["pre_query_inputs"]={"runtime_projection":pre,"lookup":user.call("deliver",{"rid":"A1"}),
            "identifier_journal_exists":(root/"provider/identifier_receipts.jsonl").exists(),
            "operational_inbox_exists":(root/"provider/native_inbox.jsonl").exists(),
            "audit_private_key_loaded_by_runtime":False,"audit_mode":"sealed_to_scorer"}
        write_json(root/"runner/pre_query_inputs.json",outcome["pre_query_inputs"])
        query={"rid":"A1","window_id":"window1","step":"discover","B_rid":""}
        if scenario=="M4-02":
            empty=require(user.call("reconcile",query),"UNKNOWN")
            outcome["empty_candidates"]=empty
            write_json(root/"runner/empty_receipt.json",empty["receipt"])
            (root/"provider/before_native_refresh.release").touch()
            wait_file(root/"provider/response_ready_without_identifiers.json")
        found=user.call("reconcile",query)
        if found.get("status")=="SAFETY_FAILURE":
            raise RuntimeError("QUERY_SCOPE_SAFETY_FAILURE")
        outcome["discovery"]=found
        outcome["B_after"]=require(lab.client("agentB",timeout=12).call("call",native_request(b["handle"],profile,"B","g1","B_after","userinfo","B0")),"RESULT_AVAILABLE")
        outcome["interferer_preserved"]=check_interferer(interferer_lab,interferer_profile,interferer_grant,scenario)
        final=user.call("reconcile",{"rid":"A1","window_id":"window1","step":"finish","B_rid":"B_after"})
        outcome["closure"]=final
        if "receipt" in final:
            write_json(root/"runner/closure_receipt.json",final["receipt"])
        if scenario=="M4-02":
            (root/"provider/response_ready_without_identifiers.release").touch()
            outcome["late_response"]=pending.result(timeout=15)
        outcome["final_state"]=user.call("status",{})
        write_json(root/"runner/final_visible.json",outcome["final_state"])
        observe(batch,root,"final")
        outcome["status"]="OBSERVED"
    except Exception as error:
        outcome["status"]="UNKNOWN"
        outcome["exception_type"]=type(error).__name__
        try:write_json(root/"runner/final_visible.json",lab.client().call("status",{}))
        except Exception:pass
    finally:
        lab.close()
        write_json(root/"runner/outcome.json",outcome)
    return outcome


def cleanup_scope(admin,batch):
    intent_path=batch/"secure/scope_intent.json"
    result={"scope":"owned app/org only"}
    if not intent_path.exists():return result
    intent=json.loads(intent_path.read_text())
    admin.category="cleanup"
    if intent.get("application_attempted"):
        response=admin.call("delete_application",payload={"owner":"admin","name":intent["application"],"organization":intent["organization"]})
        result["application_delete_response_ok"]=response["body"].get("status")=="ok"
        result["application_absent"]=admin.call("owned_application")["body"].get("data") is None
        result["application_delete_ok"]=result["application_delete_response_ok"] and result["application_absent"]
    if intent.get("organization_attempted"):
        response=admin.call("delete_organization",payload={"owner":"admin","name":intent["organization"]})
        result["organization_delete_ok"]=response["body"].get("status")=="ok"
        result["organization_absent"]=admin.call("owned_organization")["body"].get("data") is None
    write_json(batch/"SCOPE_CLEANUP.json",result)
    return result


def run(output,authorization_id,allow_native=False):
    if not allow_native:raise ValueError("EXPLICIT_NATIVE_ENABLE_REQUIRED")
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    (output/"secure").mkdir();protect_directory(output/"secure")
    nonce=secrets.token_hex(5)
    names=["l1-m4-"+nonce+"-1","l1-m4-"+nonce+"-2"]
    names.append("extra-"+names[0]+"-tail")
    scope={"organization":"l1-m4-org-"+nonce,"application_name":"app-m4-"+nonce,"client_id":"m4-client-"+nonce,
           "dedicated_scope":True,"organization_scope_read_enabled":True,"page_size":100,"record_upper_bound":50,"audit_mode":"sealed_to_scorer"}
    create_budget(output,authorization_id,names,LIMITS,220,3,2,2700,scope=scope)
    repo=Path(__file__).resolve().parents[3]
    model=source_model(output,repo)
    model.update(evidence_origin="AUTHORIZED_SCOPE_ENUMERATION",organization=scope["organization"],application_name=scope["application_name"],
                 client_id=scope["client_id"],account_names=names,approved_scope_budgets=[10,10,10,10,10],record_upper_bound=50,
                 source_lemma_ref="COMPLETENESS_AND_ATTRIBUTION.md:approved-budget-sum-and-single-Find")
    files=list((repo/"src/auth_lifecycle/online_state").glob("*"))+list((repo/"scripts").glob("*unidentified*.py"))+[repo/"scripts/check_reconciliation_receipt.py",repo/"scripts/measure_native_casdoor.py"]
    write_json(output/"SOURCE_LOCK.json",{"authorization_id":authorization_id,"files":[{"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.is_file()]})
    admin=template=sentinel=None;actors=[];records=[];stopped=False;started=time.monotonic()
    try:
        admin,old_template,reference_public=preflight(output,repo/".runtime/l1")
        template=setup_scope(admin,output,old_template,scope)
        for name in names:
            actors.append(create_actor(admin,output,name))
        model["account_id_by_name"]={a["name"]:a["id"] for a in actors}
        write_json(output/"MODEL.json",model)
        sent_profile={**template,"actor":actors[2]}
        sentinel=configure_case(output/"INTERFERER",sent_profile)
        sentinel.start_all()
        sent_grant=enroll(sentinel,sent_profile,"I","i0","agentB")
        write_json(output/"INTERFERER/runner/initial_visible.json",sentinel.client().call("status",{}))
        for index,scenario in enumerate(["M4-01","M4-02"]):
            if stopped or time.monotonic()-started>2550:
                records.append({"scenario":scenario,"status":"NOT_RUN"});continue
            root=output/scenario
            profile={**template,"actor":actors[index],"hold_before_native_refresh":scenario=="M4-02",
                     "hold_response_without_identifiers":scenario=="M4-02"}
            try:
                outcome=run_case(output,root,profile,model,scenario,sentinel,sent_profile,sent_grant)
                script=repo/"scripts/score_unidentified.py"
                with (root/"scorer/console.txt").open("wb") as stream:
                    subprocess.run([sys.executable,"-B",str(script),"--case",str(root)],stdout=stream,stderr=stream,timeout=40)
                path=root/"scorer/result.json"
                score=json.loads(path.read_text()) if path.exists() else {"status":"ABORTED"}
                records.append({"scenario":scenario,"status":score["status"],"closure":outcome.get("closure",{}).get("status")})
                stopped=score["status"] not in {"PASS_CLOSED","PASS_CONSERVATIVE_UNKNOWN"}
            except Exception as error:
                records.append({"scenario":scenario,"status":"ABORTED","error_type":type(error).__name__});stopped=True
            finally:
                cleanup=cleanup_actor(admin,output,{**template,"actor":actors[index]},root)
                if not cleanup.get("account_absent") or not cleanup.get("all_observed_access_rejected",False):stopped=True
            write_json(output/"RESULTS.json",{"records":records,"counts":dict(Counter(r["status"] for r in records))})
        outcome_i={"status":"OBSERVED","role":"interferer"}
        write_json(output/"INTERFERER/runner/final_visible.json",sentinel.client().call("status",{}))
        write_json(output/"INTERFERER/runner/outcome.json",outcome_i)
    except Exception as error:
        stopped=True
        write_json(output/"ERROR.json",{"exception_type":type(error).__name__,"reason":"SCOPE_SETUP_OR_EXECUTION_UNAVAILABLE"})
    finally:
        if sentinel:sentinel.close()
        if admin and template:
            known_names={actor["name"] for actor in actors}
            for name in names:
                path=output/"secure"/(name+".json")
                if name in known_names or not path.exists():continue
                intent=json.loads(path.read_text())
                if not intent.get("precheck_absent"):continue
                admin.category="cleanup"
                found=admin.call("get_user",actor=name)["body"].get("data")
                if found and found.get("name")==name and found.get("owner")==scope["organization"]:
                    intent["id"]=found["id"]
                    actors.append(intent)
            # Also clean accounts whose planned trajectory was never sampled.
            for actor in actors:
                existing=next((output/s for s in ["M4-01","M4-02","INTERFERER"] if (output/s/"secure/native_profile.json").exists() and json.loads((output/s/"secure/native_profile.json").read_text())["actor"]["id"]==actor["id"]),None)
                if existing is not None and (existing/"scorer/cleanup.json").exists():continue
                root=existing or output/("UNSAMPLED_"+actor["name"])
                cleanup_actor(admin,output,{**template,"actor":actor},root)
        if admin:cleanup_scope(admin,output)
    seen={r["scenario"] for r in records}
    records.extend({"scenario":s,"status":"NOT_RUN"} for s in ["M4-01","M4-02"] if s not in seen)
    with sqlite3.connect(output/"native_budget.db") as con:cost=dict(con.execute('SELECT category,COUNT(*) FROM requests GROUP BY category'))
    result={"authorization_id":authorization_id,"records":records,"counts":dict(Counter(r["status"] for r in records)),
            "HTTP_categories":cost,"HTTP_total":sum(cost.values()),"elapsed_seconds_including_cleanup":time.monotonic()-started,
            "stopped_early":stopped,"automatic_resampling":0}
    write_json(output/"RESULTS.json",result);print(json.dumps(result),flush=True);return result
