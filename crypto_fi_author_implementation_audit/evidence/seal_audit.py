"""Source/document integrity checks; no cryptographic code execution."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import ast,hashlib,json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(r'D:\毕业设计');OUT=BASE/'crypto_fi_author_implementation_audit';EV=OUT/'evidence';V=BASE/'crypto_fi_research_manuscript_v2_1';P=BASE/'crypto_fi_publication_impact_audit'
def jd(p):return json.loads(Path(p).read_text('utf-8-sig'))
def rec(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def canon(d):return json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
qa=[]
def check(name,c):
    qa.append(dict(name=name,passed=bool(c)))
    assert c,name
ver=jd(OUT/'VERDICT.json');required=ver['required_deliverables']
texts={n:(OUT/n).read_text('utf-8') for n in required if n.endswith('.md')}
check('Waiting status and completion coexist',ver['status']=='WAITING_FOR_AUTHOR_ARTIFACT' and ver['completion'].startswith('SOURCE_FORENSICS_AND_MODEL_CORRESPONDENCE_VERDICT_COMPLETE'))
check('No certified author UE artifact claimed',ver['authenticated_author_UE_artifact_obtained'] is False and ver['author_UE_artifact_exists_elsewhere'] is None)
check('All six author configurations unresolved',len(ver['author_config_mappings'])==6 and all(c['author_implementation_status']==c['result_A_transfer']==c['result_B_transfer']=='UNRESOLVED' and c['author_source_location'] is None for c in ver['author_config_mappings']))
check('No source or runtime mistaken for author UE',ver['upstream_code_is_author_UE'] is False and ver['author_configs_fully_statically_mapped']==0 and ver['actual_execution']['message_checked_author_UE_traces_acquired']==0)
check('Crypto execution and module imports0',all(ver['actual_execution'][k]==0 for k in ['author_UE_runs','upstream_crypto_code_runs','downloaded_crypto_modules_imported','dependencies_installed']))

u=jd(EV/'UPSTREAM_STATIC_FACTS.json');p=OUT/'sources/upstream_frodokem_2023.py';q=OUT/'sources/upstream_frodokem_2026.py'
check('Two pinned official source copies identical',p.read_bytes()==q.read_bytes())
b=p.read_bytes();g=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
check('Official source Gitblob andSHA256',g==u['git_blob_sha1']=='731cb0eae2c4cf2f01bb6ec4dc9fd7e1e322189f' and hashlib.sha256(b).hexdigest()=='61f38e04fa99605489f596f6c62275fc7e7d03052d0dd507cacdb606ef69a15e')
nodes=ast.parse(b.decode('utf-8'));methods={x.name:(x.lineno,x.end_lineno) for x in ast.walk(nodes) if isinstance(x,ast.FunctionDef)}
check('Actual method line positions match static registry',all(methods[k]==(v['line'],v['end_line']) for k,v in u['methods'].items()))
check('Selected baseline has noTG Upd Ord Tensor methods',all(not re.search(r'^(tg|upd|ord|tensor|ue_)',x,re.I) for x in methods))
check('Full upstream tree observed',u['tree_truncated'] is False)
expected={640:(640,15,32768,8,8,2),976:(976,16,65536,8,8,3),1344:(1344,16,65536,8,8,4)}
for n,params in expected.items():
    actual=tuple(u['parameter_facts'][str(n)][k]['value'] for k in ['n','D','q','mbar','nbar','B'])
    check('Upstream'+str(n)+' numeric subfields',actual==params)
check('Uniform-A support-size exponent arithmetic',640*640*15==6144000 and 6144000-128==6143872)
check('Migration scope caveats in mapping',all(t in texts['IMPLEMENTATION_MODEL_MAPPING.md'] for t in ['逐个A','公开seed','D≤w','D>w','η_E','一次输出','平局向上']))
check('Spec entrypoints remain null',ver['reproduction_spec']['author_entrypoint'] is None and ver['reproduction_spec']['author_argv'] is None)
fences=re.findall(r'```json\n([\s\S]*?)\n```',texts['MINIMAL_REPRODUCTION_SPEC.md'])
check('Exactly one parseable unexecuted template',len(fences)==1)
template=json.loads(fences[0])
check('Trace template contains no fabricated result',template['execution_status']=='NOT_EXECUTED' and template['messages']['initial_equal'] is None and template['messages']['updated_equal'] is None)
check('All entrypoints placeholders explicit',all(v is None for v in template['entrypoints'].values()))
check('Rate and timing denominators separated',all(t in texts['MINIMAL_REPRODUCTION_SPEC.md'] for t in ['initial_correct','N_KG','N_Dec_initial','N_Dec_updated','N_Upd','planned_attempts','preprocessing_and_cache']))

routes=jd(EV/'PUBLIC_ROUTE_LEDGER.json')['routes'];scope=jd(EV/'SEARCH_AND_RETRIEVAL_SCOPE.json')
check('Twelve grounded routes each carry receipts/reopen',len(routes)==12 and all(x['basis'] and x['receipt_files'] and x['reopen'] for x in routes))
check('All route receipt fingerprints match',all(rec(x['path'])==x for row in routes for x in row['receipt_files']))
check('Exact new query count',scope['new_web_query_count']==28 and scope['web_calls']==9 and scope['new_identity_code_queries']==3)
check('API errors retain unknown totals','Archive totals not obtained' in next(x['result'] for x in routes if x['id']=='R09'))

links=[];table_errors=[]
for n,s in texts.items():
    check(n+' controls',all(ord(c)>=32 or c=='\n' for c in s))
    check(n+' requested style','不是' not in s and '而是' not in s)
    check(n+' math display pairing',s.count('\\[')==s.count('\\]'))
    expected_columns=None
    for ln,l in enumerate(s.splitlines(),1):
        if l.startswith('|'):
            count=len(re.split(r'(?<!\\)\|',l))-2
            if expected_columns is not None and expected_columns!=count:table_errors.append(dict(file=n,line=ln,expected=expected_columns,actual=count))
            expected_columns=count
        else:expected_columns=None
    for target in re.findall(r'\]\(([^)]+)\)',s):
        if target.startswith('http'):continue
        fp=Path(target);links.append(dict(source=n,path=target,exists=fp.is_file(),absolute=fp.is_absolute()))
check('Tables intact',not table_errors)
check('Local Markdown sources exist and are absolute',all(x['exists'] and x['absolute'] for x in links))
history=jd(EV/'INPUT_LOCK.json');end=[]
for x in history:end.append(dict(path=x['path'],match=rec(x['path'])==x))
check('All144 historical source files unchanged',len(end)==144 and all(x['match'] for x in end))
seals=[]
for fp in [V/'MANIFEST.json',P/'VERDICT.json']:
    d=jd(fp);want=d.pop('payload_sha256');ok=hashlib.sha256(canon(d)).hexdigest()==want
    check('Historical seal '+str(fp),ok);seals.append(dict(path=str(fp),payload_sha256=want,match=ok))
json_errors=[]
for fp in OUT.rglob('*.json'):
    try:jd(fp)
    except Exception as e:json_errors.append(dict(path=str(fp),error=str(e)))
check('All source and delivery JSON parse',not json_errors)
check('Only four required root deliverables',{p.name for p in OUT.iterdir() if p.is_file()}==set(required))
result=dict(all_checks_passed=True,checks_count=len(qa),checks=qa,history_end_checks=end,source_seals=seals,table_errors=[],broken_links=[],json_errors=[],local_link_count=len(links),scope='Provenance, source static records and document integrity only; no downloaded crypto execution or new mathematical peer review')
dump(EV/'FINAL_QA.json',result)
ver['seal_state']='SEALED_COMPLETE'
ver['sealed_at_asia_shanghai']=datetime.now(timezone(timedelta(hours=8))).isoformat()
ver['historical_inputs_read_only']=True
ver['input_snapshot']=history
ver['all_historical_bytes_preserved']=True
ver['historical_canonical_seals']=seals
ver['qa']=dict(all_checks_passed=True,checks_count=len(qa),local_link_count=len(links),record=rec(EV/'FINAL_QA.json'))
ver['files_exclude_VERDICT_itself']=True
ver['files']=[rec(fp) for fp in sorted(OUT.rglob('*')) if fp.is_file() and fp!=OUT/'VERDICT.json']
ver['self_integrity_definition']='SHA256 canonical UTF8 JSON omitting payload_sha256, using ensure_ascii=False,sort_keys=True,separators=(comma,colon); differs from VERDICT file-byte hash.'
ver['payload_sha256']=hashlib.sha256(canon(ver)).hexdigest()
dump(OUT/'VERDICT.json',ver)
sealed=jd(OUT/'VERDICT.json');want=sealed.pop('payload_sha256');assert hashlib.sha256(canon(sealed)).hexdigest()==want
for x in sealed['files']:assert rec(x['path'])==x
print(json.dumps(dict(status=ver['status'],completion=ver['completion'],seal_state=ver['seal_state'],core=[rec(OUT/n) for n in required],qa_checks=len(qa),history_preserved=144,sealed_files=len(ver['files']),author_UE_configs_mapped=0),ensure_ascii=False))
