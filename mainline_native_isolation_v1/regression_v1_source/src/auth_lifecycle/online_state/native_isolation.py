"""M6 native profile wired to M5 restricted processes. Mature composition only."""
from concurrent.futures import ThreadPoolExecutor
import base64
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
import subprocess
import sys
import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from .isolation_acceptance import Agent, IsolationLab, source_lock, current_sid
from .lab import protect_directory
from .native_acceptance import preflight, create_actor, native_request, observe, cleanup_actor, require
from .native_http import NativeHTTP, create_budget, private_http_records, budget_path
from .protocol import canonical, write_json
from .reconciliation_acceptance import source_model
from .unidentified_acceptance import setup_scope, cleanup_scope
from .windows_isolation import set_acl, inspect_file_acl, inspect_process_acl


LIMITS = {"environment":50, "method":60, "measurement":50, "cleanup":60}
LEGACY = Path(r"D:\毕业设计\auth-lifecycle\.runtime\l1")
SCENARIOS = ["M6-01", "M6-02"]


class SecurityViolation(RuntimeError): pass


def protect_tree(path, owner, grants=()):
    for p in [Path(path), *Path(path).rglob("*")]: set_acl(p, owner, grants)


def prepare_transport(root, authorization, synthetic=False):
    root = Path(root).resolve(); root.mkdir(parents=True, exist_ok=False)
    set_acl(root, current_sid()); (root / "secure").mkdir(); protect_directory(root / "secure")
    nonce = secrets.token_hex(5)
    names = ["l1-m6-" + nonce + "-1", "l1-m6-" + nonce + "-2"]
    scope = {"organization":"l1-m6-org-"+nonce, "application_name":"app-m6-"+nonce,
             "client_id":"m6-client-"+nonce, "dedicated_scope":True, "organization_scope_read_enabled":True,
             "page_size":100, "record_upper_bound":40, "audit_mode":"sealed_to_scorer",
             "budget_subdirectory":"http_budget",
             "execution_domain":"SYNTHETIC_ZERO_NATIVE_PREFLIGHT" if synthetic else "NATIVE_APPROVED"}
    create_budget(root, authorization, names, LIMITS, 220, 2, 2, 2700, scope=scope)
    protect_tree(root / "scorer_secret", current_sid())
    return names, scope


class NativeIsolationLab(IsolationLab):
    def __init__(self, root, profile, model, fixture=None):
        super().__init__(root)
        self.profile, self.model = profile, model
        self.service_module = "auth_lifecycle.online_state.native_isolation_service"
        target = self.code / "auth_lifecycle" / "online_state"
        for name in ("native_http.py", "native_provider.py", "enumeration.py", "native_isolation_service.py", "native_isolation_fixture.py"):
            shutil.copy2(Path(__file__).with_name(name), target / name)
        self.lab.configs["provider"].pop("synthetic_application_secret", None)
        self.lab.configs["provider"]["native_profile"] = str(self.lab.root / "secure" / "native_profile.json")
        self.lab.configs["provider"]["permissions"]["adapter"] += ["dispose", "reconcile_query"]
        self.lab.configs["authority"]["permissions"]["controller"] += ["prepare_disposal", "record_disposal",
            "begin_reconciliation", "reconciliation_context", "save_reconciliation"]
        self.lab.configs["controller"]["reconciliation_model"] = model
        write_json(self.lab.root / "secure" / "native_profile.json", profile)
        if fixture:
            write_json(self.lab.root / "secure" / "synthetic_fixture.json", fixture)
            self.lab.configs["provider"]["synthetic_transport_fixture"] = str(self.lab.root / "secure" / "synthetic_fixture.json")
        for role, config in self.lab.configs.items(): write_json(self.lab.root / "secure" / (role + ".json"), config)
        (self.scorer/"private.key").unlink(missing_ok=True)
        write_json(self.scorer/"expected.json",{"purpose":"M6 scorer-only material evidence; actual values collected from private audit"})
        self.transport = Path(profile["batch"])
        # Shared budget and ciphertext output are writable. The batch parent and
        # scorer key stay outside the R writable directory.
        root_grants = [(self.sids["R"], "GRGX")]
        existing = getattr(self, "_transport_grants", [])
        # All cases have different private R SIDs; accumulate only public-parent
        # traversal. Mutable shared subdirectories carry the registered R SIDs.
        registry_path = self.transport.parent / "TRANSPORT_R_SIDS.json"
        registered = json.loads(registry_path.read_text()) if registry_path.exists() else []
        registered.append(self.sids["R"]); write_json(registry_path, registered)
        set_acl(self.transport, self.owner, [(s,"GRGX") for s in registered])
        set_acl(self.transport / "BUDGET_AND_AUTHORIZATION.json", self.owner, [(s,"GR") for s in registered])
        set_acl(self.transport / "secure" / "http-audit-public.pem", self.owner, [(s,"GR") for s in registered])
        protect_tree(self.transport / "http_budget", self.owner, [(s,"FA") for s in registered])
        protect_tree(self.transport / "secure" / "http", self.owner, [(s,"FA") for s in registered])
        # Secrets written by environment setup retain private ACLs even when
        # the transport parent acquires read permission.
        for p in (self.transport / "secure").glob("*.json"): set_acl(p, self.owner)
        protect_tree(self.transport / "scorer_secret", self.owner)
        (self.lab.root / "provider" / "operational_inbox.bin").unlink(missing_ok=True)
        write_json(self.lab.root/"control/environment.json",{"contract":"ONLINE_TRUSTED_STATE_V1",
            "profile":"CASDOOR_NATIVE_ISOLATED_V1","process_isolation":"restricted primary tokens with independent agent/R SIDs",
            "native_cost_source":str(self.transport/"http_budget/native_budget.db"),
            "fault_scope":"owned controller/authority processes and trusted/cache/view.json",
            "keys_and_authority_data_outside_cache_rollback":True})

    def start(self):
        self.lab.start_all()
        self.user = self.lab.client("user", timeout=15)
        self.recovery = self.lab.client("recovery", timeout=15)
        self.agent_objects = {n:Agent(self,n) for n in ("A","B")}
        self.rprobe = Agent(self,"R_probe",self.sids["R"],8192)
        self.setup_identity = {n:a.ask("identity") for n,a in self.agent_objects.items()}
        self.setup_identity["R_probe"] = self.rprobe.ask("identity")
        self.old_cache = self.lab.snapshot_cache()
        self.grants = {}
        for task, gen in [("A","g0"),("B","g1")]:
            login = {"schema":2,"kind":"casdoor_login","issuer":self.profile["base"],"client":self.profile["client_id"],
                     "expected_account":self.profile["actor"]["id"],"username":self.profile["actor"]["name"],
                     "password":self.profile["actor"]["password"]}
            self.grants[task] = require(self.user.call("grant", {"approval_op":"approve_"+task,"caller":"agent"+task,
                "task":task,"account":self.profile["actor"]["id"],"audience":self.profile["client_id"],"generation":gen,
                "operations":["issue","refresh","userinfo"],"budget":10,"material":login}),"GRANTED")
        write_json(self.root / "SETUP_CONTROLS.json", {"identities":self.setup_identity})
        self.freeze_environment()

    def freeze_environment(self):
        metadata = {"contract":"ONLINE_TRUSTED_STATE_V1","crypto":"FROZEN","profile":"CASDOOR_NATIVE_ISOLATED_V1",
            "owner_sid":self.owner,"restricting_sids":self.sids,"support_sids":["S-1-5-32-545","S-1-1-0","S-1-5-12"],
            "inherit_handles":False,"role_permissions":{r:c["permissions"] for r,c in self.lab.configs.items()},
            "ports":{r:c["port"] for r,c in self.lab.configs.items()},"processes":[{"pid":p.pid,**p.facts,
                "object_sddl":inspect_process_acl(p.handle)} for p in self.owned],
            "audit_private_key":str(self.transport/"scorer_secret/http-audit-private.pem"),
            "inbox_enabled":self.profile["durable_inbox"],"identifier_journal":self.profile["identifier_journal"],
            "fixture":bool(self.lab.configs["provider"].get("synthetic_transport_fixture"))}
        paths = [self.lab.root/"secure/native_profile.json", self.lab.root/"secure/authority.key",
                 self.transport/"scorer_secret/http-audit-private.pem", self.transport/"secure/http-audit-public.pem"]
        metadata["file_sddl"] = {str(p):inspect_file_acl(p) for p in paths}
        write_json(self.root/"ENVIRONMENT_LOCK.json", metadata)

    def rpc(self, task, rid, operation, source=None, **changes):
        req = native_request(self.grants[task]["handle"],self.profile,task,"g0" if task=="A" else "g1",rid,operation,source)
        req.update(changes)
        return self.agent_objects[task].rpc("call",req)

    def close(self):
        super().close()
        path=self.root/"CLEANUP.json"
        if path.exists():
            data=json.loads(path.read_text());data.pop("native_requests",None)
            data["native_cost_source"]=str(self.transport/"http_budget/native_budget.db")
            data["retained"]="protected native evidence/state/source; owned processes stopped"
            write_json(path,data)


def result(response): return response.get("result",{})


def must(response,status):
    if response.get("reached") is not True: raise RuntimeError("AGENT_REQUEST_DID_NOT_REACH_SERVICE")
    return require(result(response),status)


def access(env, actor, paths, mode="read"):
    return actor.ask(mode,targets=[{"object":label,"path":str(path)} for label,path in paths])


def permissions(env, management):
    private=env.transport/"scorer_secret/http-audit-private.pem"
    denied=[("scorer_key",private),("management_copy",management),("legacy_management",LEGACY/"secrets.json"),
            ("native_database",LEGACY/"casdoor-l1.db")]
    checks={"targets_exist":{k:p.exists() for k,p in denied},"R_denials":{},"A_denials":{},"B_denials":{},"R_positive":{}}
    for label,path in denied:
        checks["R_denials"][label]=access(env,env.rprobe,[(label,path)])
        for n in ("A","B"): checks[n+"_denials"][label]=access(env,env.agent_objects[n],[(label,path)])
    for label,path in [("native_profile",env.lab.root/"secure/native_profile.json"),
                       ("authority_key",env.lab.root/"secure/authority.key"),
                       ("audit_public",env.transport/"secure/http-audit-public.pem")]:
        checks["R_positive"][label]=access(env,env.rprobe,[(label,path)])
    checks["gate_pass"]=all(checks["targets_exist"].values()) and all(
        len(rows)==1 and rows[0].get("allowed") is False and rows[0].get("winerror")==5
        for group in ("R_denials","A_denials","B_denials") for rows in checks[group].values())
    return checks


def collect_private(env):
    records=[r for r in private_http_records(env.transport) if r["actor"]==env.profile["actor"]["name"]]
    write_json(env.scorer/"actual_responses.json",records)
    return records


def run_case(env, scenario, management, synthetic=False):
    out={"scenario":scenario,"status":"RUNNING","synthetic":synthetic}
    started=time.monotonic()
    try:
        env.start()
        # Mandatory guard precedes any real request; synthetic preflight records
        # existing permission gaps while continuing only through the fake opener.
        out["permission_precheck"]=permissions(env,management)
        write_json(env.root/"PERMISSION_PRECHECK.json",out["permission_precheck"])
        if not out["permission_precheck"]["gate_pass"] and not synthetic:
            out["status"]="BLOCKED_ENVIRONMENT";return out
        for n in ("A","B"):
            out[n+"_issue"]=env.rpc(n,n+"0","issue");must(out[n+"_issue"],"RESULT_AVAILABLE")
        write_json(env.lab.root/"runner/initial_visible.json",env.snapshot())
        if not synthetic: observe(env.transport,env.lab.root,"initial")
        if scenario=="M6-01":
            out["A_refresh"]=env.rpc("A","A1","refresh","A0");must(out["A_refresh"],"RESULT_AVAILABLE")
            out["B_initial_use"]=env.rpc("B","B_initial","userinfo","B0");must(out["B_initial_use"],"RESULT_AVAILABLE")
            out["A_status"]=env.agent_objects["A"].rpc("status",{})
            out["B_status"]=env.agent_objects["B"].rpc("status",{})
            out["parse_error"]=env.agent_objects["A"].ask("rpc",operation="call",raw='{"rid":"duplicate","rid":"duplicate2"}')
            collect_private(env)
            objects=[("native_profile",env.lab.root/"secure/native_profile.json"),
                     ("authority_database",env.lab.root/"authority/authority.db"),
                     ("operational_inbox",env.lab.root/"provider/native_inbox.jsonl"),
                     ("audit_private_key",env.transport/"scorer_secret/http-audit-private.pem"),
                     ("private_response_evidence",env.scorer/"actual_responses.json"),
                     ("management_capability",env.lab.root/"secure/admin.cap"),
                     ("environment_management",management)]
            out["attack_targets"]={k:{"path":str(p),"exists":p.exists(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in objects}
            if not all(v["exists"] for v in out["attack_targets"].values()): raise RuntimeError("ATTACK_TARGET_MISSING")
            out["file_reads"]=access(env,env.agent_objects["A"],objects)
            if any(x.get("allowed") for x in out["file_reads"]):raise SecurityViolation("UNAUTHORIZED_FILE_READ")
            out["file_writes"]=access(env,env.agent_objects["A"],objects[:3],"write")
            if any(x.get("allowed") for x in out["file_writes"]):raise SecurityViolation("UNAUTHORIZED_FILE_WRITE")
            out["process_attacks"]=env.agent_objects["A"].ask("process",pids={r:p.pid for r,p in env.lab.processes.items()},canary_handle=env.canary_handle)
            if any(x.get("allowed") for x in out["process_attacks"]["processes"] if x["operation"]!="QUERY_LIMITED"):
                raise SecurityViolation("UNAUTHORIZED_PROCESS_ACCESS")
            out["B_handle_attack"]=env.agent_objects["A"].rpc("call",native_request(env.grants["B"]["handle"],env.profile,"B","g1","A_with_B_handle","userinfo","B0"))
            if result(out["B_handle_attack"]).get("status") not in {"REJECTED","UNKNOWN"}:
                raise SecurityViolation("CROSS_CALLER_HANDLE_ACCEPTED")
            out["role_attacks"]=[]
            for op,payload in [("recover",{}),("begin_reconciliation",{"rid":"A1","window_id":"evil"}),
                 ("reconcile",{}),("deliver",{"rid":"B0"}),("dispose",{"rid":"B0","disposal_op":"evil"}),("material",{})]:
                row={"operation":op,**env.agent_objects["A"].rpc(op,payload)};out["role_attacks"].append(row)
                if result(row).get("status") not in {"REJECTED","UNKNOWN"}:raise SecurityViolation("UNAUTHORIZED_ROLE_CALL")
            out["R_private_evidence_denial"]=access(env,env.rprobe,[("private_response",env.scorer/"actual_responses.json")])
        else:
            env.lab.restart_controller("after_effect")
            with ThreadPoolExecutor(max_workers=1) as pool:
                pending=pool.submit(env.rpc,"A","A1","refresh","A0")
                env.lab.wait_barrier("after_effect")
                out["fault_pid"]=env.lab.processes["controller"].pid
                env.lab.stop("controller");out["lost_response"]=pending.result(timeout=15)
            env.lab.restore_cache(env.old_cache)
            env.lab.stop("authority");env.lab.start("controller")
            out["A_alive_during_recovery"]=env.agent_objects["A"].process.poll() is None
            out["A_outage"]=env.rpc("A","A_outage","issue")
            out["B_outage"]=env.rpc("B","B_outage","userinfo","B0")
            must(out["A_outage"],"UNKNOWN");must(out["B_outage"],"UNKNOWN")
            env.lab.start("authority")
            out["recovered"]=require(env.recovery.call("recover",{}),"RECOVERED")
        out["ack"]=require(env.user.call("revoke",{"revoke_op":"withdraw_A","grant_id":env.grants["A"]["grant_id"]}),"LOCAL_REVOKE_COMMITTED")
        out["A_after_ack"]=env.rpc("A","A_after_ack","issue");must(out["A_after_ack"],"REJECTED")
        if scenario=="M6-01":
            out["disposals"]={rid:env.user.call("dispose",{"disposal_op":"dispose_"+rid,"rid":rid}) for rid in ("A0","A1")}
        else:
            require(env.user.call("begin_reconciliation",{"rid":"A1","window_id":"window1"}),"WINDOW_OPEN")
            out["B_creation_paused"]=env.rpc("B","B_create_paused","refresh","B0");must(out["B_creation_paused"],"REJECTED")
            out["B_inside_window"]=env.rpc("B","B_inside","userinfo","B0");must(out["B_inside_window"],"RESULT_AVAILABLE")
            out["pre_query_inputs"]={"runtime_projection":env.snapshot(),"lookup":env.user.call("deliver",{"rid":"A1"}),
                "identifier_journal_exists":(env.lab.root/"provider/identifier_receipts.jsonl").exists(),
                "operational_inbox_exists":(env.lab.root/"provider/native_inbox.jsonl").exists(),
                "audit_private_loaded":False,"synthetic_fixture_truth_available":synthetic}
            write_json(env.lab.root/"runner/pre_query_inputs.json",out["pre_query_inputs"])
            out["discovery"]=env.user.call("reconcile",{"rid":"A1","window_id":"window1","step":"discover","B_rid":""})
            if out["discovery"].get("status")=="SAFETY_FAILURE":raise SecurityViolation("QUERY_SCOPE_ESCAPED")
        out["B_after"]=env.rpc("B","B_after","userinfo","B0");must(out["B_after"],"RESULT_AVAILABLE")
        if scenario=="M6-02":
            out["closure"]=env.user.call("reconcile",{"rid":"A1","window_id":"window1","step":"finish","B_rid":"B_after"})
            if "receipt" in out["closure"]:write_json(env.lab.root/"runner/closure_receipt.json",out["closure"]["receipt"])
        out["final_state"]=env.snapshot()
        write_json(env.lab.root/"runner/final_visible.json",out["final_state"])
        collect_private(env)
        if not synthetic:observe(env.transport,env.lab.root,"final")
        out["status"]="OBSERVED"
    except Exception as error:
        out["status"]="SAFETY_FAILURE" if isinstance(error,SecurityViolation) else "ABORTED";out["exception_type"]=type(error).__name__
        out["safe_reason"]=str(error) if isinstance(error,RuntimeError) and str(error).replace('_','').isalnum() else "DETAILS_WITHHELD"
    finally:
        try:env.freeze_environment()
        except Exception as error:
            out["environment_lock_error"]=type(error).__name__
            if out["status"]=="OBSERVED":out["status"]="ABORTED"
        finally:
            out["elapsed_seconds"]=time.monotonic()-started
            write_json(env.lab.root/"runner/outcome.json",out)
            env.close()
    return out


def synthetic_fixture(profile):
    def b64(data):return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    pub=key.public_key().public_numbers()
    profile["jwks"]={"keys":[{"kid":"fixture","kty":"RSA","n":b64(pub.n.to_bytes(256,"big")),"e":b64(pub.e.to_bytes(3,"big"))}]}
    entries=[]
    for i in range(3):
        name="fixture_"+profile["actor"]["id"]+"_"+str(i);unit="admin/"+name
        def jwt(kid):
            header={"alg":"RS256","typ":"JWT"}
            if kid:header["kid"]="fixture"
            claims={"iss":profile["base"],"sub":profile["actor"]["id"],"aud":[profile["client_id"]],"exp":int(time.time())+3600,"jti":unit}
            signed=b64(canonical(header))+"."+b64(canonical(claims))
            return signed+"."+b64(key.sign(signed.encode(),padding.PKCS1v15(),hashes.SHA256()))
        body={"access_token":jwt(True),"refresh_token":jwt(False),"token_type":"Bearer","expires_in":3600,"scope":"openid","id_token":None}
        row={"owner":"admin","name":name,"organization":profile["organization"],"application":profile["application_name"],
             "user":profile["actor"]["name"],"accessToken":body["access_token"],"refreshToken":body["refresh_token"],
             "tokenType":"Bearer","expiresIn":3600,"scope":"openid","idToken":None}
        entries.append({"body":body,"row":row})
    return {"account_id":profile["actor"]["id"],"entries":entries}


def make_model(root, scope, names, actors):
    model=source_model(root,Path(__file__).resolve().parents[3])
    model.update(evidence_origin="AUTHORIZED_SCOPE_ENUMERATION",organization=scope["organization"],
        application_name=scope["application_name"],client_id=scope["client_id"],account_names=names,
        account_id_by_name={a["name"]:a["id"] for a in actors},approved_scope_budgets=[10,10,10,10],record_upper_bound=40,
        source_lemma_ref="NATIVE_ISOLATION_PROFILE.md:four-grants-single-Find-single-effect")
    write_json(root/"MODEL.json",model)
    return model


def score_case(case, synthetic=False):
    script=Path(__file__).resolve().parents[3]/"scripts/score_native_isolation.py"
    command=[sys.executable,"-B",str(script),"--case",str(case)]
    if synthetic:command.append("--synthetic")
    r=subprocess.run(command,capture_output=True,timeout=40)
    (case/"scorer_private/console.log").write_bytes(r.stdout+r.stderr)
    path=case/"scorer_private/result.json"
    return json.loads(path.read_text()) if path.exists() else {"status":"SCORER_ABORTED"}


def run_preflight(output, authorization):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False);set_acl(output,current_sid())
    names,scope=prepare_transport(output/"transport",authorization,True)
    actors=[{"name":n,"id":"m6_synthetic_account"+str(i),"password":"synthetic_login_"+secrets.token_hex(12)} for i,n in enumerate(names)]
    private=output/"management_private";private.mkdir();set_acl(private,current_sid())
    management=private/"credentials.json";write_json(management,{"password":"synthetic_management_"+secrets.token_hex(16)})
    model=make_model(output,scope,names,actors)
    records=[]
    for i,scenario in enumerate(SCENARIOS):
        profile={"enabled":True,"version":"4.25.0","base":"http://127.0.0.1:18081",**scope,"batch":str(output/"transport"),
            "actor":actors[i],"client_secret":"synthetic_application_"+secrets.token_hex(16),
            "native_database":str(LEGACY/"casdoor-l1.db"),"durable_inbox":i==0,"identifier_journal":i==0,
            "query_mode":"AUTHORIZED_SCOPE_ENUMERATION","measurement_no_refresh":True}
        fixture=synthetic_fixture(profile)
        env=NativeIsolationLab(output/scenario,profile,model,fixture)
        outcome=run_case(env,scenario,management,True)
        scored=score_case(output/scenario,True)
        records.append({"scenario":scenario,"status":scored["status"],"runtime":outcome["status"]})
        if scored["status"] not in {"PASS_KNOWN_DISPOSAL","PASS_CLOSED"}:break
    result={"scope":"ZERO_NATIVE_PREFLIGHT","records":records,"native_requests":0,
            "synthetic_http_calls":sum(1 for _ in private_http_records(output/"transport")),
            "source":source_lock(),"gate_pass":len(records)==2 and all(r["status"].startswith("PASS_") for r in records)}
    write_json(output/"PREFLIGHT_RESULT.json",result)
    return result


def run_native(output,authorization,preflight_evidence,allow_native=False):
    if not allow_native:raise ValueError("EXPLICIT_NATIVE_ENABLE_REQUIRED")
    pre=Path(preflight_evidence).resolve()
    evidence=json.loads((pre/"PREFLIGHT_RESULT.json").read_text())
    if evidence.get("gate_pass") is not True or evidence.get("native_requests")!=0:
        raise ValueError("ZERO_NATIVE_PREFLIGHT_MUST_PASS")
    # Source and credential ACLs must still match the successful preflight.
    if evidence["source"]["files"]!=source_lock()["files"]:raise ValueError("PREFLIGHT_SOURCE_CHANGED")
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False);set_acl(output,current_sid())
    write_json(output/"PLAN.json",{"authorization_id":authorization,"scenarios":SCENARIOS,"plan_denominator":2,
        "preflight":str(pre),"source_lock":source_lock(),"native_http_limits":LIMITS,"total":220,"wall_seconds":2700})
    transport=output/"transport";names,scope=prepare_transport(transport,authorization)
    private=output/"management_private";private.mkdir();set_acl(private,current_sid())
    credentials=json.loads((LEGACY/"secrets.json").read_text())
    management=private/"credentials.json";write_json(management,{"casdoor_password":credentials["casdoor_password"]})
    admin=None;template=None;actors=[];records=[];started=time.monotonic();stopped=False
    try:
        # Last local gate, before the first native HTTP request.
        acl=inspect_file_acl(LEGACY/"secrets.json")
        if ";;;BU)" in acl or ";;;AU)" in acl:raise RuntimeError("LEGACY_CREDENTIAL_ACL_NOT_HARDENED")
        admin,original,_=preflight(transport,LEGACY)
        template=setup_scope(admin,transport,original,scope)
        loaded=admin.call("owned_application")["body"].get("data")
        if (not isinstance(loaded,dict) or loaded.get("tokenFormat")!="JWT" or loaded.get("tokenSigningMethod")!="RS256"
                or loaded.get("expireInHours")!=1 or loaded.get("refreshExpireInHours")!=1
                or loaded.get("disableRefreshRotation") is True or loaded.get("isShared") is True
                or not {"password","refresh_token"}.issubset(loaded.get("grantTypes",[]))):
            raise RuntimeError("DEDICATED_APPLICATION_PROFILE_MISMATCH")
        for name in names:actors.append(create_actor(admin,transport,name))
        basic=base64.b64encode((template["client_id"]+":"+template["client_secret"]).encode()).decode()
        empty=NativeHTTP(transport,"environment",enabled=True).call("get_tokens",headers={"Authorization":"Basic "+basic})
        if empty["http"]!=200 or empty["body"].get("data")!=[]:
            raise RuntimeError("DEDICATED_SCOPE_NOT_INITIALLY_EMPTY")
        write_json(output/"INITIAL_SCOPE.json",{"native_sequence":empty["sequence"],"records":[],
            "scope":scope["organization"],"phase":"after new accounts, before any OAuth issuance"})
        # Environment-only credentials stay private; R sees only its own native
        # profile and the audit public key.
        for p in (transport/"secure").glob("*.json"):set_acl(p,current_sid())
        model=make_model(output,scope,names,actors)
        write_json(output/"SOURCE_LOCK.json",source_lock())
        for i,scenario in enumerate(SCENARIOS):
            if stopped or time.monotonic()-started>2550:
                records.append({"scenario":scenario,"status":"NOT_RUN"});continue
            profile={**template,"actor":actors[i],"durable_inbox":i==0,"identifier_journal":i==0,
                     "query_mode":"AUTHORIZED_SCOPE_ENUMERATION","measurement_no_refresh":True}
            env=NativeIsolationLab(output/scenario,profile,model)
            outcome=run_case(env,scenario,management)
            scored=score_case(output/scenario)
            records.append({"scenario":scenario,"status":scored["status"],"runtime":outcome["status"],
                            "closure":scored.get("closure"),"obligations":scored.get("remaining_obligations")})
            stopped=scored["status"] not in {"PASS_KNOWN_DISPOSAL","PASS_CLOSED"}
            write_json(output/"RESULTS.json",{"records":records,"stopped":stopped})
    except Exception as error:
        stopped=True;write_json(output/"ERROR.json",{"exception":type(error).__name__,"message":"SETUP_OR_EXECUTION_ABORTED",
            "safe_reason":str(error) if isinstance(error,RuntimeError) and str(error).replace('_','').isalnum() else "DETAILS_WITHHELD"})
    finally:
        # Preserve B evidence before account cleanup. Extra audit knowledge is
        # consumed only by this separate cleanup role.
        if admin and template:
            known_names={a["name"] for a in actors}
            for name in names:
                intent_path=transport/"secure"/(name+".json")
                if name in known_names or not intent_path.exists():continue
                intent=json.loads(intent_path.read_text())
                if not intent.get("precheck_absent") or not intent.get("creation_attempted"):continue
                admin.category="cleanup";found=admin.call("get_user",actor=name)["body"].get("data")
                if found and found.get("name")==name and found.get("owner")==scope["organization"]:
                    intent["id"]=found["id"];actors.append(intent)
            for i,actor in enumerate(actors):
                case=output/SCENARIOS[names.index(actor["name"]) ]/"trusted"
                (case/"scorer").mkdir(parents=True,exist_ok=True)
                try:cleanup_actor(admin,transport,{**template,"actor":actor},case)
                except Exception as error:write_json(output/(SCENARIOS[i]+"_CLEANUP_ERROR.json"),{"exception":type(error).__name__})
        if admin:
            try:cleanup_scope(admin,transport)
            except Exception as error:write_json(output/"SCOPE_CLEANUP_ERROR.json",{"exception":type(error).__name__})
    seen={r["scenario"] for r in records};records += [{"scenario":s,"status":"NOT_RUN"} for s in SCENARIOS if s not in seen]
    policy=json.loads((transport/"BUDGET_AND_AUTHORIZATION.json").read_text())
    with sqlite3.connect(budget_path(transport,policy)) as c:
        costs=dict(c.execute('SELECT category,COUNT(*) FROM requests GROUP BY category'))
        body_bytes=c.execute('SELECT COALESCE(SUM(request_bytes),0),COALESCE(SUM(response_bytes),0) FROM requests').fetchone()
    result={"authorization_id":authorization,"planned":2,"records":records,"counts":dict(Counter(r["status"] for r in records)),
            "HTTP_categories":costs,"HTTP_total":sum(costs.values()),"request_body_bytes":body_bytes[0],"response_body_bytes":body_bytes[1],
            "elapsed_seconds_including_cleanup":time.monotonic()-started,"automatic_resampling":0,"stopped_early":stopped}
    write_json(output/"RESULTS.json",result);return result
