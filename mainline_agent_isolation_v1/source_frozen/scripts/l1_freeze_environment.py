"""Pin observed native versions/configuration for PILOT only, not hypothesis thresholds."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from auth_lifecycle.experiment.providers import connect,required,PRIVATE
from auth_lifecycle.experiment.journal import canonical,fingerprint

ROOT=Path(__file__).resolve().parents[1]


def public_config(provider):
    if provider.name=="keycloak":
        realm=required(provider.admin("GET","/"+provider.realm))
        config={k:realm.get(k) for k in ["realm","enabled","sslRequired","accessTokenLifespan","revokeRefreshToken","refreshTokenMaxReuse"]}
        config["clients"]=[]
        for c in provider.clients:
            raw=required(provider.admin("GET",f"/{provider.realm}/clients/{c['native_id']}"))
            config["clients"].append({k:raw.get(k) for k in ["clientId","enabled","publicClient","directAccessGrantsEnabled","fullScopeAllowed","protocolMappers"]})
        return config
    return {"organization":provider.organization,"clients":[{k:c["configuration"].get(k) for k in ["name","clientId","organization","grantTypes","expireInHours","refreshExpireInHours","tokenFormat","cert"]} for c in provider.clients]}


def main():
    p=argparse.ArgumentParser();p.add_argument("--survey",required=True);p.add_argument("--out",default="experiments/l1/environment.lock.json");args=p.parse_args()
    survey=Path(args.survey).resolve();observed=json.loads((survey/"observations.json").read_text(encoding="utf-8"))
    if any(r["status"]!="OBSERVED" for r in observed["rows"]):raise SystemExit("survey contains unreviewed errors")
    implementations={}
    for name in ["keycloak","casdoor"]:
        provider=connect(name);config=public_config(provider)
        rows=[r for r in observed["rows"] if r["implementation"]==name]
        grants=[r for r in rows if r["case"]=="grant_revoke"]
        if not grants or not all(r["observation"]["before_access"]==[True,True] and r["observation"]["native_units_distinct"] is True and r["observation"]["after"]=={"target_access":False,"target_refresh":False,"sibling_access":True,"sibling_refresh":True} for r in grants):raise SystemExit("grant-local binding not established")
        implementations[name]={"version":provider.version,"kind":"complete_independent_native_identity_implementation",
            "issuer":provider.issuer,"public_configuration":config,"configuration_sha256":fingerprint(canonical(config)),
            "discovery":{k:v for k,v in provider.discovery().items() if k in {"issuer","token_endpoint","introspection_endpoint","revocation_endpoint","jwks_uri","grant_types_supported"}},
            "native_record_kind":provider.native_record_kind,"independent_native_grant_units_confirmed_in_profile":True,
            "root_action_kind":provider.root_action_kind,
            "queryer_other_client_active":next(r["observation"]["other_client_active"] for r in rows if r["case"]=="queryer_scope")}
    document={"schema":"auth-l1-environment-lock/1","status":"PINNED_FOR_NATIVE_PILOT_ONLY","created_utc":datetime.now(timezone.utc).isoformat(),
        "survey":str(survey),"survey_sha256":sha256((survey/"observations.json").read_bytes()).hexdigest(),"implementations":implementations,
        "distributions":json.loads((ROOT/"experiments/l1/distributions.json").read_text()),
        "formal_threshold_confirmation":False,"native_interfaces":"password grant, refresh, token/access revocation, introspection, owned-account root stop",
        "authorization":"new generated users in dedicated local realm/organization; never production accounts",
        "binding":"single selected support per task, controlled broker, nominal deterministic setup; A/AB query-needed mapping remains incomplete"}
    with Path(args.out).open("x",encoding="utf-8") as f:json.dump(document,f,ensure_ascii=False,indent=2)
    print(json.dumps({"status":document["status"],"implementations":{k:v["version"] for k,v in implementations.items()}},ensure_ascii=False))


if __name__=="__main__":main()
