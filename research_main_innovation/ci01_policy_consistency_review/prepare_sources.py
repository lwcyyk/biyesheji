"""Read-only source extraction and public-document acquisition, no native calls."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,shutil,urllib.request

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'ci01_contract_audit'
SRC=OLD/'sources/casdoor-v4.25.0'
PREV=ROOT.parent/'ci01_cutoff_audit'

def h(p):return sha256(p.read_bytes()).hexdigest()

def main():
    if (ROOT/'INPUT_HASHES.json').exists():raise RuntimeError('already frozen')
    paths=[SRC/x for x in ['routers/authz_filter.go','routers/auto_signin_filter.go','routers/base.go','routers/session_provider.go',
        'routers/timeout_filter.go','object/user_util.go','object/application.go','object/oauth_dcr.go','object/oauth_cimd.go',
        'object/token.go','object/user.go','controllers/base.go','controllers/auth.go','controllers/user.go','main.go','go.mod']]
    paths += [OLD/'sources/authz__authz.go',PREV/'sources/casdoor-v4.25.0/util/time.go',PREV/'sources/casdoor-v4.25.0/util/string.go']
    paths += [PREV/x for x in ['REPORT.md','DECISION.json','NATIVE_CUTOFF_PATHS.md','SIMPLE_COMPOSITIONS.md','PRIOR_ART_MAPPING.md',
        'collect_cutoff.py','raw/run01/http_and_events.jsonl','raw/run01/result.json','raw/run01/source_hashes.json',
        'raw/run01/source_snapshot/collect_cutoff.py','STAGE_ENVIRONMENT.json']]
    hashes=[]
    for p in paths:
        if not p.is_file():raise FileNotFoundError(p)
        hashes.append({'path':str(p),'sha256':h(p),'bytes':p.stat().st_size})
        if p.is_relative_to(SRC):
            q=ROOT/'sources/frozen'/p.relative_to(SRC)
        elif p.name=='authz__authz.go':q=ROOT/'sources/frozen/authz/authz.go'
        elif 'util' in p.parts:q=ROOT/'sources/frozen/util'/p.name
        else:continue
        q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    (ROOT/'INPUT_HASHES.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf-8')
    events=[json.loads(l) for l in (PREV/'raw/run01/http_and_events.jsonl').read_text(encoding='utf-8').splitlines()]
    c11=[x for x in events if x['case']=='C11_application_cutoff']
    (ROOT/'HISTORICAL_C11_INDEX.json').write_text(json.dumps({'source':str(PREV/'raw/run01/http_and_events.jsonl'),'sha256':h(PREV/'raw/run01/http_and_events.jsonl'),
      'evidence_kind':'HISTORICAL_REDACTED_OBSERVATION','events':c11,'new_native_calls':0},ensure_ascii=False,indent=2),encoding='utf-8')
    fetches=[]
    urls=[('website_tree.json','https://api.github.com/repos/casdoor/casdoor-website/git/trees/master?recursive=1'),
      ('authz_upstream_master.go','https://raw.githubusercontent.com/casdoor/casdoor/master/routers/authz_filter.go'),
      ('authz_history.json','https://api.github.com/repos/casdoor/casdoor/commits?path=routers/authz_filter.go&per_page=30')]
    for name,url in urls:
        item={'url':url,'utc':datetime.now(timezone.utc).isoformat()}
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'local-research-readonly-audit'})
            with urllib.request.urlopen(req,timeout=20) as response:data=response.read();item['http']=response.status
            dest=ROOT/'sources/public'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
            item.update(path=str(dest.relative_to(ROOT)),sha256=sha256(data).hexdigest(),bytes=len(data))
        except Exception as error:item.update(status='UNAVAILABLE',exception_type=type(error).__name__,http=getattr(error,'code',None))
        fetches.append(item)
    (ROOT/'PUBLIC_FETCHES.json').write_text(json.dumps({'tool_failures':[{'action':'search_service: OASIS/Casdoor public search','error':'MCP transport HTTP request failed'},
      {'action':'github.search_prs: casdoor/casdoor dynamic client session token','error':'MCP transport HTTP request failed'}],
      'fallback':'public official HTTPS only; no local service access','fetches':fetches},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'frozen_files':len(hashes),'historical_C11_events':len(c11),'public_fetches':fetches},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
