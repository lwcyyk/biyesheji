"""Stratified family-paired analysis. Pilot output never supports a formal hypothesis."""
from collections import defaultdict
import math
import random
from statistics import mean,variance,NormalDist


def quantile(values,p):
    if not values:raise ValueError("empty bootstrap distribution")
    data=sorted(values);position=(len(data)-1)*p;lower=int(position);weight=position-lower
    return data[lower]*(1-weight)+data[min(lower+1,len(data)-1)]*weight


def pair_runs(runs,hypothesis,candidate,baseline):
    grouped=defaultdict(dict)
    for row in runs:
        meta=row["metadata"]
        if meta["hypothesis"]!=hypothesis:continue
        if meta["method"] in grouped[meta["pair_id"]]:raise ValueError("duplicate method/pair")
        grouped[meta["pair_id"]][meta["method"]]=row
    pairs=[]
    for pair_id,methods in sorted(grouped.items()):
        if set(methods)!={candidate,baseline}:raise ValueError("missing paired arm; retain/impute from scheduled manifest before analysis")
        c,b=methods[candidate],methods[baseline]
        for field in ["implementation","family_id","goal","fault","repeat","Q_cap","G_cap","approval_cap","source_sha256","environment_digest"]:
            if c["metadata"][field]!=b["metadata"][field]:raise ValueError("paired condition mismatch: "+field)
        pairs.append((c,b))
    return pairs


def family_table(pairs,cost):
    by=defaultdict(list)
    for c,b in pairs:by[(c["metadata"]["implementation"],c["metadata"]["family_id"])].append((c,b))
    strata=defaultdict(list)
    for (implementation,family),items in sorted(by.items()):
        strata[implementation].append({"family":family,"pairs":len(items),"candidate_cost":mean(c["metrics"][cost] for c,b in items),
            "baseline_cost":mean(b["metrics"][cost] for c,b in items),"candidate_U":mean(c["metrics"]["U"] for c,b in items),
            "baseline_U":mean(b["metrics"]["U"] for c,b in items),"lineage":items[0][0]["metadata"]["lineage"],
            "independence_attested":all(c["metadata"].get("independence_attested") for c,b in items)})
    return dict(strata)


def estimate(strata):
    if not strata or any(not x for x in strata.values()):raise ValueError("missing implementation stratum")
    c=mean(mean(x["candidate_cost"] for x in rows) for rows in strata.values())
    b=mean(mean(x["baseline_cost"] for x in rows) for rows in strata.values())
    du=mean(mean(x["candidate_U"]-x["baseline_U"] for x in rows) for rows in strata.values())
    return {"candidate_mean_cost":c,"baseline_mean_cost":b,"ratio":c/b if b>0 else None,"completion_difference":du}


def bootstrap(strata,replicates=10000,seed=20261102,alpha=.05/3):
    rng=random.Random(seed);ratios=[];differences=[]
    for _ in range(replicates):
        sample={key:[rng.choice(rows) for _ in rows] for key,rows in sorted(strata.items())}
        value=estimate(sample)
        if value["ratio"] is None:return {"status":"UNDEFINED_ZERO_BASELINE_COST"}
        ratios.append(value["ratio"]);differences.append(value["completion_difference"])
    return {"status":"DESCRIPTIVE_BOOTSTRAP_QUANTILES_NOT_FORMAL_SUPPORT","replicates":replicates,"seed":seed,
            "alpha_per_hypothesis":alpha,"one_sided_confidence":1-alpha,
            "ratio_upper":quantile(ratios,1-alpha),"completion_difference_lower":quantile(differences,alpha),
            "ratio_two_sided_95":[quantile(ratios,.025),quantile(ratios,.975)],
            "completion_difference_two_sided_95":[quantile(differences,.025),quantile(differences,.975)]}


def icc(groups):
    groups=[list(g) for g in groups if g];k=len(groups);n=sum(map(len,groups))
    if k<2 or n<=k:return {"status":"INSUFFICIENT_CLUSTERS_OR_REPEATS","estimate":None}
    grand=sum(sum(g) for g in groups)/n
    ms_between=sum(len(g)*(mean(g)-grand)**2 for g in groups)/(k-1)
    ms_within=sum(sum((v-mean(g))**2 for v in g) for g in groups)/(n-k)
    effective_m=(n-sum(len(g)**2 for g in groups)/n)/(k-1)
    denominator=ms_between+(effective_m-1)*ms_within
    if denominator==0:return {"status":"DEGENERATE_ZERO_VARIATION","estimate":None}
    raw=(ms_between-ms_within)/denominator
    return {"status":"DESCRIPTIVE_ANOVA_UNEQUAL_CLUSTER_ICC","estimate":raw,"nonnegative_for_sensitivity":max(0,min(1,raw)),
            "families":k,"observations":n,"effective_cluster_size":effective_m}


def analyze(runs,registry,replicates=10000):
    result={"phase":"PILOT_ONLY","formal_status":"NOT_TESTED","hypotheses":{}}
    for hypothesis in ["H-A","H-B","H-AB"]:
        spec=registry["hypotheses"][hypothesis];pairs=pair_runs(runs,hypothesis,spec["candidate"],spec["baseline"])
        if not pairs:continue
        strata=family_table(pairs,spec["cost"]);summaries={}
        for implementation,rows in strata.items():
            selected=[(c,b) for c,b in pairs if c["metadata"]["implementation"]==implementation]
            groups=defaultdict(list);raw_cost=defaultdict(list);raw_completion=defaultdict(list)
            for c,b in selected:
                family=c["metadata"]["family_id"]
                groups[family].append(c["metrics"][spec["cost"]]-b["metrics"][spec["cost"]])
                raw_cost[family].append(b["metrics"][spec["cost"]]);raw_completion[family].append(b["metrics"]["U"])
            summaries[implementation]={"operational_families":len(rows),"lineage_groups":len({x["lineage"] for x in rows}),
                "independence_attested_families":sum(x["independence_attested"] for x in rows),"paired_cost_difference_ICC":icc(groups.values()),
                "paired_cost_difference_variance":variance([c["metrics"][spec["cost"]]-b["metrics"][spec["cost"]] for c,b in selected]) if len(selected)>1 else None,
                "family_completion_difference_variance":variance([x["candidate_U"]-x["baseline_U"] for x in rows]) if len(rows)>1 else None}
            summaries[implementation].update(baseline_cost_ICC=icc(raw_cost.values()),baseline_completion_ICC=icc(raw_completion.values()),
                baseline_cost_variance=variance([b["metrics"][spec["cost"]] for c,b in selected]) if len(selected)>1 else None)
        result["hypotheses"][hypothesis]={"pairs":len(pairs),"family_weighted":estimate(strata),"strata":strata,"adequacy":summaries,
            "strata_complete":set(strata)==set(registry.get("implementations",strata)),
            "bootstrap":bootstrap(strata,replicates,registry["bootstrap"]["seed"]),
            "formal_inference_allowed":False,"formal_status":"NOT_TESTED",
            "reasons":["thresholds unconfirmed","no approved independent family population","few related operational families","pilot calibration is excluded from holdout","A/AB query-needed L1 mapping incomplete"]}
    return result


def sample_size_sensitivity(threshold,assumed_ratio,paired_log_sd,baseline_completion=.95,pair_correlation=.5,icc_value=.2,repeats=12,alpha=.05/3,power=.80):
    # paired_log_sd is the assumed SD of the paired influence
    # C/mu_C - B/mu_B for log(mean(C)/mean(B)), NOT sd(log(C/B)).
    if not (0<threshold<1 and assumed_ratio>0 and 0<baseline_completion<1 and 0<=pair_correlation<=1 and 0<=icc_value<1 and type(repeats)is int and repeats>1 and 0<alpha<.5 and .5<power<1):raise ValueError("invalid power assumptions")
    if assumed_ratio>=threshold:return {"status":"NO_FINITE_N_FOR_POWER_AT_OR_INSIDE_NULL","families_per_implementation":None}
    if paired_log_sd<=0:return {"status":"DEGENERATE_VARIANCE_CANNOT_JUSTIFY_SAMPLE_SIZE","families_per_implementation":None}
    marginal_power=(1+power)/2
    z=NormalDist().inv_cdf(1-alpha)+NormalDist().inv_cdf(marginal_power)
    gap=math.log(threshold)-math.log(assumed_ratio)
    design_effect=1+(repeats-1)*icc_value
    # Equal two-implementation weighting; normal/design-effect approximation,
    # a sensitivity calculation, not a substitute for a validated bootstrap power simulation.
    cost=math.ceil(z*z*paired_log_sd**2*design_effect/(2*repeats*gap*gap))
    v=2*baseline_completion*(1-baseline_completion)*(1-pair_correlation)
    completion=math.ceil(z*z*v*design_effect/(2*repeats*.05**2))
    return {"status":"CONDITIONAL_NORMAL_APPROXIMATION_ONLY","families_per_implementation":max(cost,completion),
            "cost_families_per_implementation":cost,"noninferiority_families_per_implementation":completion,
            "design_effect":design_effect,"assumed_true_ratio":assumed_ratio,"assumed_paired_log_cost_sd":paired_log_sd,
            "SD_interpretation":"paired influence C/mu_C - B/mu_B for log ratio of means, not individual log ratios",
            "assumed_true_completion_difference":0,"assumed_baseline_completion":baseline_completion,
            "assumed_pair_correlation":pair_correlation,"assumed_ICC":icc_value,"paired_runs_per_family":repeats,
            "alpha":alpha,"target_joint_IUT_power":power,"marginal_power_used":marginal_power,
            "power_allocation":"each component beta <= (1-joint_power)/2; conditional union-bound protection, normal approximation still requires validation",
            "not_an_empirically_estimated_recommendation":True}


def confirmation_gate(registry,approval):
    missing=[]
    if registry.get("confirmatory_execution_enabled") is not True:missing.append("confirmatory_execution_enabled")
    if not approval or approval.get("decision")!="APPROVED_BY_RESEARCHER":missing.append("explicit researcher approval")
    for field in registry["required_researcher_freeze"]:
        if not approval or not approval.get(field):missing.append(field)
    if approval and approval.get("native_binding_profile")=="known-contract-single-path/v1":missing.append("query-needed A/AB native mapping")
    return {"allowed":not missing,"missing":missing,"external_preregistration_claimed":False}
