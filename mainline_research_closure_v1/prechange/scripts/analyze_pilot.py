"""Rebuild paired pilot statistics without dropping refusals, unknowns or missing arms."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from hashlib import sha256
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from auth_lifecycle.experiment.statistics import analyze,sample_size_sensitivity
from auth_lifecycle.experiment.journal import read_verified,canonical


def load(path):
    rows=[json.loads(line) for line in (path/"runs.jsonl").read_text(encoding="utf-8").splitlines()] if (path/"runs.jsonl").exists() else []
    schedule=json.loads((path/"scheduled_pairs.json").read_text());plan=json.loads((path/"plan.json").read_text())
    expected={(item["pair_id"],method) for item in schedule for method in item["order"]}
    actual={(r["metadata"]["pair_id"],r["metadata"]["method"]) for r in rows}
    if len(actual)!=len(rows) or not actual<=expected:raise ValueError("duplicate or unscheduled run")
    for row in rows:
        events=read_verified(path/row["event_file"])
        start=[x["payload"]["metadata"] for x in events if x["event"]=="run_start"]
        if len(start)!=1 or canonical(start[0])!=canonical(row["metadata"]):raise ValueError("run metadata differs from event ledger")
        scheduled=next(x for x in schedule if x["pair_id"]==row["metadata"]["pair_id"])
        if [row["metadata"][f] for f in ["implementation","hypothesis","family_id","goal","fault","repeat"]]!=scheduled["case"]:raise ValueError("run relabeled across family or condition")
        scored=[x["payload"]["metrics"] for x in events if x["event"]=="independent_score"]
        if not scored or canonical(scored[-1])!=canonical(row["metrics"]):raise ValueError("summary differs from independent event score")
        q=sum(e["event"]=="request_sent" and e["payload"].get("counted") is True for e in events)
        if q!=row["metrics"]["Q_total"]:raise ValueError("request accounting mismatch")
        if row["metrics"]["C_Q"]!=(q if row["metrics"]["U"] else row["metadata"]["Q_cap"]+1):raise ValueError("failure cost omitted")
        units={e["payload"]["native_unit_ref"] for e in events if e["event"]=="credential_created" and e["payload"].get("native_unit_ref")}
        if row["metrics"]["C_G"]!=(len(units) if row["metrics"]["U"] else row["metadata"]["G_cap"]+1):raise ValueError("native-unit cost mismatch")
    missing=[]
    for item in schedule:
        provider,hypothesis,family,goal,fault,repeat=item["case"]
        for method in item["order"]:
            if (item["pair_id"],method) in actual:continue
            # Analysis-only penalty placeholder, explicitly not a fabricated run.
            peer=next((r for r in rows if r["metadata"]["pair_id"]==item["pair_id"]),None)
            meta=dict(peer["metadata"]) if peer else {"implementation":provider,"hypothesis":hypothesis,"family_id":family,"goal":goal,"fault":fault,"repeat":repeat,
                "lineage":plan["families"][family]["lineage"],"independence_attested":False,"Q_cap":plan["request_cap"],"G_cap":plan["grant_cap"],"approval_cap":plan["approval_cap"],"source_sha256":"missing","environment_digest":"missing"}
            meta.update(pair_id=item["pair_id"],method=method,run_id=item["pair_id"]+"-"+method)
            rows.append({"metadata":meta,"metrics":{"U":0,"C_Q":meta["Q_cap"]+1,"C_G":meta["G_cap"]+1,"status":"UNKNOWN_MISSING_RECORD"},"analysis_placeholder_not_execution":True})
            missing.append(meta["run_id"])
    return rows,missing


def main():
    parser=argparse.ArgumentParser();parser.add_argument("directory");parser.add_argument("--out",required=True);parser.add_argument("--bootstrap",type=int,default=10000);args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];directory=Path(args.directory).resolve();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=False)
    registry=json.loads((root/"experiments/registry.json").read_text());runs,missing=load(directory)
    sources=[root/"src/auth_lifecycle/experiment/statistics.py",Path(__file__).resolve(),root/"experiments/registry.json"]
    (out/"analysis_source_hashes.json").write_text(json.dumps({p.relative_to(root).as_posix():sha256(p.read_bytes()).hexdigest() for p in sources},indent=2),encoding="utf-8")
    with zipfile.ZipFile(out/"analysis_sources.zip","x",zipfile.ZIP_DEFLATED) as archive:
        for p in sources:archive.write(p,p.relative_to(root).as_posix())
    results=analyze(runs,registry,args.bootstrap);results["missing_runs_penalized"]=missing
    results["raw_status_counts"]=dict(Counter(r["metrics"]["status"] for r in runs))
    (out/"analysis.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
    rows=[]
    for hypothesis in ["H-A","H-B","H-AB"]:
        threshold=registry["hypotheses"][hypothesis]["proposed_ratio_bound"]
        for ratio in [threshold,.70 if hypothesis!="H-AB" else .75]:
            for sigma in [.20,.40]:
                for correlation in [0,.5]:
                    for intraclass in [.05,.2,.5]:
                        for baseline_completion in [.5,.8,.95]:rows.append({"hypothesis":hypothesis,**sample_size_sensitivity(threshold,ratio,sigma,baseline_completion=baseline_completion,pair_correlation=correlation,icc_value=intraclass)})
    power={"status":"NO_DEFENSIBLE_EMPIRICAL_SAMPLE_SIZE_YET","reason":"too few unverified independent families; current calibration often yields zero paired variance and no observed superiority",
           "observed_effect_is_not_a_design_assumption":True,"sensitivity":rows,"formal_status":"NOT_TESTED"}
    (out/"power.json").write_text(json.dumps(power,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"rows":len(runs),"missing":len(missing),"formal_status":"NOT_TESTED","power":power["status"]}))


if __name__=="__main__":main()
