"""Fixed A/B algorithms used on an explicitly limited native binding profile."""
from copy import deepcopy
from dataclasses import asdict
from functools import lru_cache
from ..b import fixtures as b, search, baselines, checker
from ..b.engine import setup
from ..a import compiler, candidate, audit, joint_reference
from ..checker import check_policy


def model(provider, mode, query_client, goal, tasks, cap=64):
    names=[f"t{i}" for i in range(tasks)];m=b.base(names);b.env(m)
    m["environments"]["broker"]["stop"]["requests"]=1
    b.grant(m,"shared")
    for task in names:
        b.grant(m,task);b.path(m,task+"_shared",task,["shared"]);b.path(m,task+"_own",task,[task])
    m["budgets"].update(requests=cap,approvals=8,units=8);m["horizon"]=8
    for item in m["tasks"].values():item["account"]="owned-test-account"
    for item in m["credentials"].values():item.update(account="owned-test-account",type="native_oidc_access_refresh_pair",token_labels=["native_material_reference"])
    if goal=="local":sc={"local":["t0"],"remote":[],"preserve":names[1:]}
    elif tasks==4:sc={"local":["t1"],"remote":["t0"],"preserve":names[2:]}
    else:sc={"local":[],"remote":["t0"],"preserve":names[1:]}
    m["scenarios"]={"stop":sc}
    for native in m["revocations"].values():
        native["coverage"]="all_material" if mode=="online" else "refresh_only"
        native["evidence"]="survey01:"+provider+":grant_revoke+signed-resource-profile"
    if provider=="keycloak" and query_client==1:
        # This configured RP cannot initially authorize the required operation.
        # It does NOT mean the native token is invalid for its issuing audience.
        for c in m["credentials"].values():c["scope"]=[]
    return m


@lru_cache(maxsize=128)
def plan(provider,mode,query_client,goal,hypothesis,method,cap=64):
    tasks=4 if hypothesis=="H-B" else 2;m=model(provider,mode,query_client,goal,tasks,cap)
    if hypothesis=="H-B":
        result=(search if method=="B" else baselines).solve(m)
        return {"status":result.status,"model":m,"delivery":result.delivery,"work":result.stats,
                "check":checker.check_delivery(m,result.delivery) if result.delivery else None,
                "binding_profile":"known-contract-single-path/v1","query_needed_profile":False}
    source={"schema":"auth-lifecycle-a/1","account":"owned-test-account","caller":"agent-client","worlds":{"registered":m},
            "initial":["registered"],"scenario":"stop","probes":{},"cleanups":{},"faults":{},
            "budget":{"requests":cap,"approvals":8},"horizon":4}
    built=compiler.compile_model(source)
    if built.status!="COMPILED":return {"status":built.status,"model":m,"reason":built.reason}
    checked=audit.check_compilation(built.bundle)
    if checked["verdict"]!="ACCEPTED":raise RuntimeError("native nominal projection audit failed")
    result=joint_reference.solve(built.bundle) if method=="R-J" else candidate.solve(built.bundle,method="B-A" if method=="B-A" else "A1",feedback=method=="AB1")
    delivery=None
    if result.policy:
        policy_check=check_policy(built.bundle["l0"],result.policy)
        if policy_check.verdict!="ACCEPTED":raise RuntimeError("nominal policy check failed")
        node=result.policy;config=None;stops=[]
        while node["kind"]!="done":
            action=node["action"];meta=built.bundle["catalog"][action]
            if meta["kind"]=="configure":config=meta["configuration"]
            elif meta["kind"]=="stop":stops.append(meta["native"])
            else:raise RuntimeError("this native calibration binding does not implement query-dependent policies")
            node=node["children"]["ok"]
        delivery={"configuration":config,"setup":[x for x,_ in setup(m,config)],"plans":{"stop":stops}}
    return {"status":result.status,"model":m,"delivery":delivery,"work":result.stats,"nominal_policy":result.policy,
            "binding_profile":"known-contract-single-path/v1","query_needed_profile":False,
            "formal_H_A_H_AB_eligible":False,"reason":"negative control: no uncertain contract; faults fail closed outside nominal atomic policy"}
