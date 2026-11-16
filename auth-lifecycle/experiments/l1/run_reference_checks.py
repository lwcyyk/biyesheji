"""Supplementary R-J/A1 native negative-control checks, never primary-study rows."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"));sys.path.insert(0,str(ROOT/"scripts"))
from l1_pilot import execute,source_hashes
from auth_lifecycle.experiment.providers import connect
from auth_lifecycle.experiment.journal import canonical,fingerprint


def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);a=p.parse_args();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=False)
    (out/"events").mkdir();(out/"models").mkdir()
    lock=json.loads((ROOT/"experiments/l1/environment.lock.json").read_text(encoding="utf-8"));source=source_hashes()
    source_digest=fingerprint(canonical(source));rng=random.Random(20261102);rows=[]
    for name in ["keycloak","casdoor"]:
        provider=connect(name);methods=["A1","R-J"];rng.shuffle(methods)
        for order,method in enumerate(methods):
            meta={"run_id":"ref-"+name+"-"+method,"pair_id":"ref-"+name,"phase":"L1_REFERENCE_CALIBRATION","formal":False,"hypothesis":"H-A","method":method,
                "implementation":name,"version":provider.version,"family_id":"online_issuer_client","lineage":"password-grant-and-resource-validator-v1","independence_attested":False,
                "goal":"remote_or_mixed","fault":"none","repeat":0,"randomized_order":order,"seed":20261102,"Q_cap":64,"G_cap":8,"approval_cap":8,"timeout_seconds":30,
                "code_commit":None,"source_sha256":source_digest,"driver_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),"environment_digest":fingerprint(canonical(lock)),
                "approved_operations_initial":["configure","probe","stop","cleanup","refresh"],"formal_effect_distribution_eligible":False}
            row=execute(provider,meta,{"mode":"online","query_client":0},out);rows.append(row)
            print(name,method,row['metrics']['status'],row['metrics']['Q_total'],flush=True)
    (out/"runs.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"source_hashes.json").write_text(json.dumps(source,indent=2),encoding="utf-8")


if __name__=="__main__":main()
