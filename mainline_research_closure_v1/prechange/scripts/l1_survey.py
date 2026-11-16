"""Native capability survey, separate from any A/B/AB efficacy experiment."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import threading
import time
import uuid
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from auth_lifecycle.experiment.providers import connect, required, claims
from auth_lifecycle.experiment.journal import Journal, Gate, ApprovalDenied, ResponseLost, BudgetDenied, fingerprint,canonical
from auth_lifecycle.experiment.witness import Witness, request_cost

ROOT = Path(__file__).resolve().parents[1]
CASES = ["grant_revoke", "access_revoke", "shared_root", "queryer_scope", "introspection_cache", "verification_effect",
         "unsupported_strong_stop", "approval_withdrawal", "response_loss", "late_request", "concurrent_race", "observable_drift", "budget_after_probe"]


def probe_case(p, actor, case, log, gate):
    w = Witness(p, log)
    def issue(client=0):
        body = required(p.issue(actor, client))
        if "access_token" not in body:raise RuntimeError("native token creation failed")
        if not w.signed_access(body["access_token"],client,actor["id"]):raise RuntimeError("native signature/account/audience binding failed")
        log.emit("native_unit_evidence", "witness", native_unit=w.native_unit(body["access_token"], actor), record_kind=p.native_record_kind)
        return body
    if case in {"grant_revoke", "access_revoke"}:
        a, b = issue(), issue(); before = [w.active(x["access_token"]) for x in [a,b]]
        units_before=[w.native_unit(x["access_token"],actor) for x in [a,b]]
        selected = "refresh_token" if case == "grant_revoke" else "access_token"
        response = p.revoke(a[selected], hint=selected)
        after = {"target_access": w.active(a["access_token"]), "target_refresh": w.active(a["refresh_token"], hint="refresh_token"),
                 "sibling_access": w.active(b["access_token"]), "sibling_refresh": w.active(b["refresh_token"], hint="refresh_token")}
        return {"before_access": before, "revocation_http": response["http"], "after": after,
                "target_signature_still_valid": w.signed_access(a["access_token"], subject=actor["id"]),
                "native_units_distinct":all(units_before) and len(set(units_before))==2}
    if case == "shared_root":
        a,b = issue(0),issue(1); result = p.root_stop(actor)
        return {"root_http": result["http"], "root_action_kind":p.root_action_kind,"after_access": [w.active(a["access_token"],0),w.active(b["access_token"],1)],
                "after_refresh": [w.active(a["refresh_token"],0,"refresh_token"),w.active(b["refresh_token"],1,"refresh_token")]}
    if case == "queryer_scope":
        a=issue();return {"issuing_client_active":w.active(a["access_token"],0),"other_client_active":w.active(a["access_token"],1),
                         "signed_resource_accepts":w.signed_access(a["access_token"],subject=actor["id"])}
    if case == "introspection_cache":
        a=issue();before=w.accepted(a["access_token"],"cached",subject=actor["id"],cache_ttl=.5)
        p.revoke(a["refresh_token"]); direct=w.active(a["access_token"]); stale=w.accepted(a["access_token"],"cached",subject=actor["id"])
        log.emit("cache_expiry_wait", "fixture", seconds=.6);time.sleep(.6)
        fresh=w.accepted(a["access_token"],"cached",subject=actor["id"])
        return {"before":before,"native_after":direct,"rp_cached_after":stale,"after_cache_expiry":fresh,"cache_layer":"self-written resource validator, not native AS"}
    if case == "verification_effect":
        before=len(p.native_sessions(actor));a=issue();created=len(p.native_sessions(actor));p.introspect(a["access_token"]);after=len(p.native_sessions(actor))
        return {"record_kind":p.native_record_kind,"before":before,"after_authentication_probe":created,"after_introspection":after}
    if case == "unsupported_strong_stop":
        a=issue();p.root_stop(actor)
        return {"online_after_root":w.active(a["access_token"]),"offline_after_root":w.signed_access(a["access_token"],subject=actor["id"]),
                "scope":"existing signed JWT at offline RP before expiry, using approved token/account revocations only"}
    if case == "approval_withdrawal":
        a=issue();gate.fault=case
        try:p.revoke(a["refresh_token"])
        except ApprovalDenied:pass
        return {"triggered":gate.triggered,"native_still_active":w.active(a["access_token"]),"denied_before_native_dispatch":True}
    if case == "response_loss":
        gate.fault=case
        try:issue()
        except ResponseLost:pass
        actual=gate.private_effects[-1];created=w.active(actual["access_token"]);p.root_stop(actor)
        closed=not w.active(actual["access_token"])
        log.emit("obligation_closed" if closed else "obligation_unresolved", "witness", kind="unknown_handle_after_loss")
        return {"agent_received_token":False,"server_created_credential":created,"root_cleanup_online_closed":closed,"triggered":gate.triggered}
    if case == "late_request":
        a=issue();log.emit("fault_armed","fault",fault=case,point="old_refresh_intent_queued_before_revoke")
        p.revoke(a["refresh_token"]);log.emit("fault_triggered","fault",fault=case,point="release_old_intent_after_revoke_response")
        late=p.refresh(a["refresh_token"])
        return {"late_http":late["http"],"late_created_access":bool(late["body"].get("access_token")),"target_active":w.active(a["access_token"])}
    if case == "concurrent_race":
        a=issue();barrier=threading.Barrier(2)
        def execute(kind):
            barrier.wait();return p.refresh(a["refresh_token"]) if kind=="refresh" else p.revoke(a["refresh_token"])
        log.emit("fault_triggered","fault",fault=case,point="two_real_HTTP_requests_released_at_barrier")
        with ThreadPoolExecutor(max_workers=2) as pool:refresh,revoke=list(pool.map(execute,["refresh","revoke"]))
        new=refresh["body"].get("access_token")
        return {"refresh_http":refresh["http"],"revoke_http":revoke["http"],"refresh_created_access":bool(new),
                "old_active_after":w.active(a["access_token"]),"new_active_after":w.active(new) if new else None}
    if case == "observable_drift":
        log.emit("fault_armed","fault",fault=case,point="before_native_policy_update")
        if p.name=="keycloak":
            required(p.set_rotation(False),204)
            log.emit("fault_triggered","fault",fault=case,point="native_rotation_policy_update_confirmed")
            try:
                a=issue();one=p.refresh(a["refresh_token"]);two=p.refresh(a["refresh_token"])
                return {"native_policy_changed":"revokeRefreshToken true -> false", "same_refresh_reuse_successes":sum(bool(x["body"].get("access_token")) for x in [one,two])}
            finally:
                required(p.set_rotation(True),204);log.emit("policy_restored","fixture",policy="revokeRefreshToken=true")
        app=p.clients[0]["configuration"];old=app["expireInHours"];updated=dict(app,expireInHours=old+1)
        try:
            response=required(p.admin("POST","update-application?id=admin/"+app["name"],updated))
            if response.get("status")!="ok":raise RuntimeError("native policy update rejected")
            log.emit("fault_triggered","fault",fault=case,point="native_token_lifetime_update_confirmed");a=issue()
            return {"native_policy_changed":"access lifetime", "old_hours":old,"new_hours":old+1,"observed_expires_in":a["expires_in"]}
        finally:
            restored=required(p.admin("POST","update-application?id=admin/"+app["name"],app))
            if restored.get("status")!="ok":raise RuntimeError("native policy restoration failed")
            log.emit("policy_restored","fixture",policy="original_token_lifetime")
    if case == "budget_after_probe":
        gate.cap=2;a=issue();p.introspect(a["access_token"])
        denied=False
        try:p.revoke(a["refresh_token"])
        except BudgetDenied:denied=True
        return {"budget_cap":2,"method_requests":gate.sent,"stop_budget_denied":denied,"native_still_active":w.active(a["access_token"])}
    raise ValueError(case)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--out",required=True);parser.add_argument("--repeats",type=int,default=2);args=parser.parse_args()
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=False);rows=[]
    files=[p for folder in ["src","scripts","tests"] for p in (ROOT/folder).rglob("*.py")]
    manifest={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    source_hash=fingerprint(canonical(manifest))
    (out/"source_hashes.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    with zipfile.ZipFile(out/"source_bundle.zip","x",zipfile.ZIP_DEFLATED) as archive:
        for name in manifest:archive.write(ROOT/name,name)
    for name in ["keycloak","casdoor"]:
        p=connect(name)
        for case in CASES:
            for repeat in range(args.repeats):
                p.admin_login();run_id=f"survey-{name}-{case}-{repeat}";actor=p.create_actor("l1-"+uuid.uuid4().hex[:18])
                meta={"run_id":run_id,"phase":"NATIVE_CAPABILITY_SURVEY","implementation":name,"version":p.version,"case":case,"repeat":repeat,"source_sha256":source_hash,"code_commit":None}
                log=Journal(out/(run_id+".jsonl"),meta);gate=Gate(log);p.transport=gate.transport
                log.emit("run_start","fixture",metadata=meta,actor_ref=fingerprint(actor["id"]),scope="new owned test actor")
                start=time.perf_counter()
                try:
                    observation=probe_case(p,actor,case,log,gate);status="OBSERVED"
                except Exception as error:
                    observation={"error_type":type(error).__name__,"message":str(error)[:180]};status="ERROR"
                finally:
                    p.transport=None
                    p.root_stop(actor);p.remove_actor(actor)
                    log.emit("fixture_reset","fixture",actor_deleted=True,counted=False,reason="isolated test teardown after observations")
                log.emit("run_end","scorer",status=status,observation=observation);log.close()
                row={**meta,"status":status,"observation":observation,"requests":request_cost(out/(run_id+".jsonl")),"wall_seconds":time.perf_counter()-start}
                rows.append(row);print(name,case,repeat,status,flush=True)
    payload={"phase":"NATIVE_CAPABILITY_SURVEY","started_formal_experiment":False,"rows":rows}
    (out/"observations.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"summary.json").write_text(json.dumps({"observations":len(rows),"errors":sum(x["status"]!="OBSERVED" for x in rows),"formal_hypotheses":"NOT_TESTED"},indent=2),encoding="utf-8")


if __name__=="__main__":main()
