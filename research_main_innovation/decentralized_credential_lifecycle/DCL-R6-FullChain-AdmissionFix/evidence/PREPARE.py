"""Host-only collection and immutable source/manifest audit."""
from pathlib import Path
import hashlib,json,shutil,zipfile,ast
from datetime import datetime,timezone
P=Path(r'D:\毕业设计\research_main_innovation\decentralized_credential_lifecycle')
I=Path(r'D:\毕业设计\DCL-R6-isolated-verification')
O=P/'DCL-R6-FullChain-AdmissionFix';E=O/'evidence';E.mkdir(parents=True,exist_ok=True)
def h(p):
 s=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):s.update(b)
 return s.hexdigest()
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):
 with(E/n).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def cp(p,q):
 q.parent.mkdir(parents=True,exist_ok=True)
 with p.open('rb') as r,q.open('xb') as w:shutil.copyfileobj(r,w)
cp(Path(r'C:\Users\a1887\.codex\attachments\f4d0be5e-cc69-414b-83d2-268cd6ad1399\已粘贴的文本.txt'),E/'TASK_REQUEST.txt')
nav=['CURRENT_VERDICT.md','NEXT_ACTION.md','README.md','DECISION_HISTORY.md']
for n in nav:cp(P/n,E/'NAV_ORIGINALS'/n)
history=[]
for root in [P,I]:
 for p in sorted(root.rglob('*')):
  if p.is_file() and not p.is_relative_to(O) and not(root==P and p.parent==P and p.name in nav):history.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h(p)})
save('HISTORY_BASELINE.json',{'files':history})
lock=j(P/'DCL-R6-RuntimeAdapt-Fix/evidence/STATIC_WORKSPACE_LOCK.json');source=[]
for r in lock['files']:
 p=I/'ra01'/r['relative'];assert p.stat().st_size==r['bytes'] and h(p)==r['sha256']
 cp(p,E/'FROZEN_RA_ORIGINALS'/r['relative']);source.append(r)
assert len(source)==64
save('SOURCE_BASELINE_LOCK.json',{'source':str(I/'ra01'),'version':'RuntimeAdapt-static-1/r1','files':source})
refs=['DCL-R6-FullChain-B/FULLCHAIN_FINAL_DECISION.md','DCL-R6-FullChain-B/FULLCHAIN_VERSION_INTEGRATION.md',
 'DCL-R6-FullChain-B/FULLCHAIN_AUTHORIZATION_AND_LOCK.md','DCL-R6-FullChain-B/FULLCHAIN_COUNTEREXAMPLES.md',
 'DCL-R6-FullChain-B/evidence/SEAL_CAPACITY_STATIC_WITNESS.json','DCL-R6-FullChain-B/evidence/RESOURCE_BOUND_INDEPENDENT.json',
 'DCL-R6-TR-A2/TRA2_FINAL_DECISION.md','DCL-R6-ManagerRecovery-Fix/FINAL_DECISION.md',
 'DCL-R6-ManagerRecovery-Fix/SOURCE_AND_INPUT_LOCK.md','DCL-R6-ManagerRecovery-Fix/NEXT_DYNAMIC_AUTHORIZATION.md',
 'DCL-R6-CalDiag/CALDIAG_FINAL_DECISION.md','DCL-R6-B09-Supplement/FINAL_DECISION.md','DCL-R6-RuntimeAdapt-Fix/FINAL_DECISION.md']
for r in refs:cp(P/r,E/'HISTORICAL_REFERENCES'/r)
zp=P/'DCL-R6-FullChain-B/FULLCHAIN_EVIDENCE.zip'
with zipfile.ZipFile(zp) as z:
 m=json.loads(z.read('FULLCHAIN_MANIFEST.json'));assert z.testzip() is None
 for r in m['files']:assert hashlib.sha256(z.read(r['relative'])).hexdigest()==r['sha256']
 assert len(z.namelist())==len(m['files'])+1==123
assert h(zp)=='fc988fbf962b55515c6bd647a464b0336896487ddf1c8229be8c7d50db42d41d'
save('FULLCHAIN_B_ZIP_CHECK.json',{'sha256':h(zp),'entries':123,'manifest_files':122,'status':'PASS_HASH_STRUCTURE'})
native=I/'batch14/native_snapshot';nm=j(native/'out/EVIDENCE_MANIFEST.json')
identity=j(I/'ra01/inputs/batch_identity.json');control=Path(identity['host_control'])
am=j(control/'STARTUP_ADMIN_MANIFEST.json')
cp(native/'out/EVIDENCE_MANIFEST.json',E/'ACTUAL_NATIVE_MANIFEST.json');cp(control/'STARTUP_ADMIN_MANIFEST.json',E/'ACTUAL_ADMIN_MANIFEST.json')
catalog=[]
for k,(rel,r) in enumerate(nm['files'].items()):
 p=native/rel;assert h(p)==r['sha256']
 catalog.append({'evidence_id':f'ACTUAL-N-{k:04}','producer':'TR-A2:'+rel.split('/')[-1],
 'source_path':str(p),'relative':rel,'sha256':r['sha256'],'size':r['bytes'],
 'required_by':'Frozen native manifest, source/identity/budget/terminal/replay provenance',
 'admin_required':True,'native_required':True,'replay_required':True,'independently_verified':'CURRENT_HOST_SHA_AND_HISTORICAL_MANIFEST',
 'equivalence_class':r['sha256'],'origin':'ACTUAL_HISTORICAL_FILE'})
for k,r in enumerate(am['files']):
 p=Path(r['host']);assert h(p)==r['sha256']
 catalog.append({'evidence_id':f'ACTUAL-A-{k:04}','producer':'TR-A2 automatic host finalizer','source_path':str(p),
 'relative':r['archive_path'],'sha256':r['sha256'],'size':r['bytes'],'required_by':'Existing administrative manifest/export binding',
 'admin_required':True,'native_required':r['archive_path'].startswith('startup/'),'replay_required':True,
 'independently_verified':'CURRENT_HOST_SHA_AND_HISTORICAL_MANIFEST','equivalence_class':r['sha256'],'origin':'ACTUAL_HISTORICAL_FILE'})
w=j(P/'DCL-R6-FullChain-B/evidence/SEAL_CAPACITY_STATIC_WITNESS.json')
for k,r in enumerate(w['raw_paths']):
 catalog.append({'evidence_id':f'PLANNED-FULL-{k:04}','producer':r['suite']+':'+r['case_id'],
 'source_path':'<new-batch>/'+r['relative'],'relative':r['relative'],'sha256':None,'size':None,
 'required_by':'Frozen complete C00-post suite inputs and independent oracle replay',
 'admin_required':True,'native_required':True,'replay_required':True,'independently_verified':'STATIC_PRODUCER_PATH_ONLY; bytes UNRUN',
 'equivalence_class':'UNPROVEN_CONTENT_EQUIVALENCE','origin':'STATIC_PATH_WITNESS'})
save('EVIDENCE_CATALOG.json',{'schema':'FC-EVIDENCE-CATALOG/1','rows':catalog,
 'actual_native_files':len(nm['files']),'actual_native_zip_members':len(nm['files'])+1,'actual_admin_manifest_rows':len(am['files']),
 'actual_admin_zip_members':len(am['files'])+1,'planned_full_raw_lower_bound':312,'planned_full_native_members_lower_bound':313,
 'full_success_manifest_available':False,'full_exact_counts':None,'full_max_counts':None,
 'note':'Historical byte identities and planned current files have distinct origins. Equal historical hashes do not authorize deletion or cross-batch substitution.'})
# Extract real pure/archive functions for authorized host parser checks. No role bootstrap.
snips={}
for filename,names in {'terminal_evidence.py':['_native_artifact','terminal_policy'],
 'manager_recovery.py':['classify','closure_status']}.items():
 src=(I/'ra01/src'/filename).read_text();t=ast.parse(src)
 for node in t.body:
  if isinstance(node,ast.FunctionDef) and node.name in names:snips[node.name]={'file':filename,'line':node.lineno,'source':ast.get_source_segment(src,node),'source_sha256':h(I/'ra01/src'/filename)}
save('REAL_CHECKER_SLICES.json',snips)
save('COLLECTION_RESULT.json',{'utc':datetime.now(timezone.utc).isoformat(),'history_files':len(history),'source_files':64,
 'native_rows':len(nm['files']),'admin_rows':len(am['files']),'catalog_rows':len(catalog),'WSL_calls':0,'dynamic_entries':0})
print(json.dumps({'history':len(history),'source':64,'actual_native':len(nm['files']),'actual_admin':len(am['files']),'catalog':len(catalog)}))
