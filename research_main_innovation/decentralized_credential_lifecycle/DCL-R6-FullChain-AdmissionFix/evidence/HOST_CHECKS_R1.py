"""Authorized host-only parser/finite predicate checks; no business or OS roles."""
from pathlib import Path,PurePosixPath
import ast,copy,hashlib,importlib.util,json,os,stat,struct,sys,time,types,warnings,zipfile
O=Path(__file__).resolve().parent.parent;E=O/'evidence';F=E/'HOST_FIXTURES';F.mkdir(exist_ok=False)
def load_module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
A=load_module('fc_archive_check',O/'maintenance/archive_check.py')
R=load_module('fc_archive_oracle',O/'maintenance/archive_oracle.py')
M=load_module('fc_mr_oracle',O/'maintenance/mr_native_oracle.py')
def save(n,x):
 with(E/n).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def make(name,count,change=None):
 directory=F/name;directory.mkdir();p=directory/'input.zip';mn='out/EVIDENCE_MANIFEST.json'
 data={f'out/item_{i:04}.json':b'{}' for i in range(count-1)}
 doc={'binding':{'batch_id':'HOST-FIXTURE','boot_id':'HOST-FIXTURE'},'files':{n:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for n,v in data.items()}}
 if change=='wrong_hash':next(iter(doc['files'].values()))['sha256']='0'*64
 if change=='missing_manifest_row':doc['files'].pop(next(iter(doc['files'])))
 if change=='missing_member':data.pop(next(iter(data)))
 if change=='extra':data['out/extra']=b'x'
 if change in ['traversal','backslash','drive','unicode']:
  old=next(iter(data));new={'traversal':'out/../escape','backslash':'out\\escape','drive':'C:escape','unicode':'out/e\u0301'}[change]
  data[new]=data.pop(old);doc['files'][new]=doc['files'].pop(old)
 if change=='bomb_declared':next(iter(doc['files'].values()))['bytes']=33554433
 if change=='wrong_binding':doc['binding']['batch_id']='FOREIGN'
 raw=json.dumps(doc,sort_keys=True,separators=(',',':')).encode()
 if change=='duplicate_json':raw=raw.replace(b'"files":{',b'"files":{},"files":{',1)
 with zipfile.ZipFile(p,'x',zipfile.ZIP_DEFLATED) as z:
  for n,v in data.items():
   info=zipfile.ZipInfo(n);info.external_attr=(stat.S_IFREG|0o600)<<16;info.compress_type=zipfile.ZIP_DEFLATED
   if change=='symlink' and n==next(iter(data)):info.external_attr=(stat.S_IFLNK|0o777)<<16
   if change=='fifo' and n==next(iter(data)):info.external_attr=(stat.S_IFIFO|0o600)<<16
   if change=='unsupported' and n==next(iter(data)):info.compress_type=zipfile.ZIP_BZIP2
   z.writestr(info,v)
  z.writestr(mn,raw)
  if change=='duplicate':
   with warnings.catch_warnings():warnings.simplefilter('ignore');z.writestr(next(iter(data)),b'{}')
 if change=='partial':p.write_bytes(p.read_bytes()[:-8])
 if change=='encrypted':
  b=bytearray(p.read_bytes());i=b.find(b'PK\x01\x02');flags=struct.unpack_from('<H',b,i+8)[0];struct.pack_into('<H',b,i+8,flags|1);p.write_bytes(b)
 if change=='central_size':
  b=bytearray(p.read_bytes());struct.pack_into('<I',b,len(b)-10,0x7fffffff);p.write_bytes(b)
 if change=='permission':
  doc['files'][next(iter(doc['files']))]['mode']=0o640
  # Preserve archive bytes; expected metadata mismatch is an input mismatch.
  raw=json.dumps(doc,sort_keys=True,separators=(',',':')).encode()
 (directory/'manifest.json').write_bytes(raw)
 return p,raw

rows=[]
def check(name,count,cap,expect,change=None):
 p,raw=make(name,count,change);error=None;answer=None
 try:answer=A.verify(p,raw,cap,expected_binding={'batch_id':'HOST-FIXTURE','boot_id':'HOST-FIXTURE'});accepted=True
 except (ValueError,KeyError,OSError,RuntimeError,zipfile.BadZipFile,NotImplementedError) as ex:accepted=False;error=type(ex).__name__+':'+str(ex)
 ref=R.inspect(p,raw,cap,binding={'batch_id':'HOST-FIXTURE','boot_id':'HOST-FIXTURE'})
 assert accepted==expect==(ref['decision']=='ACCEPT'),(name,accepted,expect,error,ref)
 rows.append({'case_id':name,'category':'HOST_ARCHIVE_FIXTURE','fixture_origin':'SYNTHETIC_BYTES_NO_RUNTIME','members_requested':count,
  'cap':cap,'expected_accept':expect,'actual_accept':accepted,'subject_result':answer,'error':error,'oracle':ref,
  'ZIP_sha256':sha(p),'manifest_sha256':hashlib.sha256(raw).hexdigest(),'raw_directory':str(p.parent.relative_to(E))})
for n in [257,258,313,314]:check('legacy_native_'+str(n),n,257,n<=257)
for n in [257,258,313,314]:check('count_witness_candidate_'+str(n),n,313,n<=313)
for flaw in ['wrong_hash','missing_manifest_row','missing_member','extra','traversal','backslash','drive','unicode',
 'bomb_declared','wrong_binding','duplicate_json','symlink','fifo','unsupported','duplicate','partial','encrypted','central_size','permission']:
 check('negative_'+flaw,5,313,False,flaw)
save('ARCHIVE_HOST_RESULTS.json',{'status':'PASS_HOST_PARSER_ONLY','cases':rows,'count':len(rows),
 'candidate_cap_313_meaning':'TEST_BOUNDARY_FOR_KNOWN_LOWER_WITNESS_ONLY; not selected production capacity',
 'native_tests':'UNRUN','Linux_permission_observations':'UNRUN','runtime_hooks_integrated':False})

# Run the actual frozen archive function, using fixture FD adapters only.
# Linux metadata helpers are excluded and remain UNRUN. Source function intact.
slices=json.loads((E/'REAL_CHECKER_SLICES.json').read_bytes())
ns={'os':os,'zipfile':zipfile,'hashlib':hashlib,'Path':PurePosixPath,'EvidenceError':type('EvidenceError',(ValueError,),{}),'_deadline':lambda G,u:None}
fixture_root=None
def exists(fd,name):return (fixture_root/name).exists()
def open_fixture(fd,name,owners,maximum):
 p=fixture_root/name
 if p.stat().st_size>maximum:raise ns['EvidenceError']('SIZE')
 return os.open(p,os.O_RDONLY)
def json_fixture(fd,name,owners,hashes,label):
 raw=(fixture_root/name).read_bytes();hashes[label]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};return json.loads(raw)
ns.update(_exists=exists,_open=open_fixture,_json=json_fixture)
exec(compile(slices['_native_artifact']['source'],'actual_frozen_native_artifact','exec'),ns)
actual=[]
for n in [257,258,313]:
 p,raw=make('actual_native_checker_'+str(n),n);fixture_root=p.parent/'runtime';fixture_root.mkdir();
 (fixture_root/'EVIDENCE.zip').write_bytes(p.read_bytes());(fixture_root/'EVIDENCE_MANIFEST.json').write_bytes(raw)
 g=types.SimpleNamespace();result=ns['_native_artifact'](g,{'out':0,'inputs':1},{},0,1,'HOST')
 assert result['verified']==(n<=257)
 actual.append({'case_id':'actual_native_'+str(n),'verified':result['verified'],'errors':result['errors'],
  'source_sha256':slices['_native_artifact']['source_sha256'],'metadata_adapter':'HOST_FIXTURE_FD_ONLY; real Linux metadata excluded'})
src=(E/'FROZEN_RA_ORIGINALS/src/startup_lifecycle.py').read_text(encoding='utf-8-sig');tree=ast.parse(src)
node=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and isinstance(n.test,ast.BoolOp) and 'count > cfg[\'admin_max_files\']' in ast.unparse(n.test))
code=compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'actual_admin_count_guard','exec')
admin=[]
for n in [256,257,312]:
 try:exec(code,{'count':n,'total':0,'cfg':{'admin_max_files':256,'admin_max_bytes':33554432}});accepted=True;error=None
 except RuntimeError as ex:accepted=False;error=str(ex)
 assert accepted==(n<=256)
 admin.append({'count':n,'accepted':accepted,'error':error,'source_line':node.lineno,'scope':'Actual frozen guard AST only; no post-exit role executed'})
save('ACTUAL_FROZEN_CHECKER_RESULTS.json',{'archive_function':actual,'admin_count_guard':admin,'target_role_imports':0})

# Existing MR classifiers are executed as isolated actual pure functions.
pure={}
for name in ['classify','closure_status']:exec(compile(slices[name]['source'],'actual_frozen_'+name,'exec'),pure)
facts=dict(closed=False,stop=False,binding=True,identity=True,fresh=True,expected_kind=True,budget=True,window=True,
 exit_observed=True,active=False,review_complete=True,result_proof=True,ack=True,receiver=True,witness=True,supervision=True)
pred=[]
for name,edits,expected in [('normal_C09',{},'REVIEWED_EXPECTED'),('closed',{'closed':True},'CLOSED'),
 ('stop',{'stop':True},'STOP_REQUESTED'),('unreviewed',{'review_complete':False},'REVIEW_PENDING'),
 ('query_error',{'fresh':False},'REVIEWED_UNEXPECTED'),('missing_ack',{'ack':False},'REVIEW_PENDING'),
 ('lost_root',{'supervision':False},'REVIEWED_UNEXPECTED')]:
 got=pure['classify']({**facts,**edits});assert got==expected;pred.append({'case_id':name,'result':got,'expected':expected})
for args in [(True,True,True,[]),(True,True,False,[]),(True,True,True,['error'])]:
 got=pure['closure_status'](*args);assert got==('CLOSED_CLEANUP_CONFIRMED' if not args[-1] and args[2] else 'UNKNOWN');pred.append({'closure_input':args,'result':got})
boot='00000000-0000-4000-8000-000000000001';unit='fixture-mr-native-fault.service'
binding={'batch_id':'HOST-FIXTURE','boot_id':boot};expected={'binding':binding,'service_prefix':'fixture-','boot_id':boot}
native={'Id':unit,'ActiveState':'active','InvocationID':'a'*32,'MainPID':'21'}
case={'origin':'NATIVE_RECORDED_EVENT','binding':binding,'unit':unit,'start':{'native':native,'identity':{'pid':21,'boot_id':boot},'sample':{'boottime':1}},
 'finish':{'native':{**native,'ActiveState':'failed','ExecMainPID':'21','ExecMainCode':'1','ExecMainStatus':'79','Result':'exit-code','ExecMainExitTimestampMonotonic':'2000000'},'sample':{'boottime':2}},
 'rejection':'MR_UNREVIEWED_MANAGER_FAILURE:'+unit,'failed_before':[],'failed_after':[unit],'window':{'T0':0,'deadline':1800,'stop_at':1740},
 'journal':{'exit_code':0,'stdout':json.dumps({'_SYSTEMD_UNIT':unit,'_BOOT_ID':boot.replace('-',''),'_SYSTEMD_INVOCATION_ID':'a'*32,'MESSAGE':json.dumps({'event':'MR_NATIVE_FAULT_READY'})})}}
closure={'stop_published':True,'closed':True,'roles_exited':True,'group_empty':True,'fallback':False,'manual_stop':False,'new_work_after_fault':0,'window':case['window']}
budget={n:'a'*64 for n in ['counter','intent','journal']};witness={'exit_code':78,'source':'direct-parent waitpid'};admin={'native':'NATIVE_SEAL_COMPLETED','administrative':'ADMIN_EVIDENCE_SEALED'}
mr=[]
def mrcheck(name,mutate=None,accept=False):
 args=copy.deepcopy([case,closure,budget,budget,witness,admin,expected])
 if mutate:mutate(args)
 result=M.verify(*args);assert result['accepted']==accept,(name,result)
 mr.append({'case_id':name,'category':'HOST_MR_ORACLE_FIXTURE','origin':'SYNTHETIC_INPUT_WITH_NATIVE_CLAIMS_NO_OS_EVENT','expected_accept':accept,'result':result,'input':args})
mrcheck('healthy_native_shaped_fixture',accept=True)
for field in ['stop_published','closed','roles_exited','group_empty']:
 mrcheck('missing_'+field,lambda a,f=field:a[1].update({f:False}))
for field in ['fallback','manual_stop']:mrcheck(field,lambda a,f=field:a[1].update({f:True}))
mrcheck('new_work_after_fault',lambda a:a[1].update(new_work_after_fault=1))
mrcheck('budget_changed',lambda a:a[3].update(counter='b'*64))
mrcheck('window_reset',lambda a:a[1].update(window={'T0':1}))
mrcheck('wrong_boot',lambda a:a[0]['start']['identity'].update(boot_id='foreign'))
mrcheck('wrong_invocation',lambda a:a[0]['finish']['native'].update(InvocationID='b'*32))
mrcheck('normal_exit',lambda a:a[0]['finish']['native'].update(ExecMainStatus='0'))
mrcheck('historical_unit',lambda a:a[0].update(unit='historical.service'))
mrcheck('unreviewed_accepted',lambda a:a[0].update(rejection='REVIEWED_EXPECTED'))
mrcheck('query_failed',lambda a:a[0]['journal'].update(exit_code=1))
mrcheck('missing_raw_log',lambda a:a[0]['journal'].update(stdout=''))
mrcheck('synthetic_origin',lambda a:a[0].update(origin='MR-SIMULATION/1'))
mrcheck('native_failed',lambda a:a[5].update(native='NATIVE_SEAL_UNRESOLVED'))
mrcheck('admin_failed',lambda a:a[5].update(administrative='ADMIN_EVIDENCE_UNRESOLVED'))
mrcheck('waitpid_missing',lambda a:a[4].update(source='claimed'))
save('MR_HOST_RESULTS.json',{'actual_pure_predicates':pred,'oracle_fixtures':mr,'native_OS_events':0,'native_injections':0})

# Concrete mutant outputs: each selected rejected fixture has a permissive wrong
# implementation returning ACCEPT; the independently evaluated bytes reject it.
mutants=[]
for name,target in [('skip_count','legacy_native_258'),('skip_hash','negative_wrong_hash'),('skip_members','negative_extra'),
 ('skip_duplicate','negative_duplicate'),('skip_path','negative_backslash'),('skip_type','negative_symlink'),('skip_bomb','negative_bomb_declared')]:
 r=next(r for r in rows if r['case_id']==target)
 assert r['oracle']['decision']=='REJECT';mutants.append({'mutant':name,'trigger':target,'mutant_result':'ACCEPT','oracle':r['oracle'],'detected':True})
# These are intentionally permissive wrong implementations. They are executed
# through their actual bypass functions, with isolated host fixtures only.
for r in mutants:
 bypass=lambda _path,_raw,_cap:True
 trigger=next(x for x in rows if x['case_id']==r['trigger']);p=E/trigger['raw_directory']/'input.zip'
 assert bypass(p,(p.parent/'manifest.json').read_bytes(),trigger['cap']) is True
save('MUTATION_HOST_RESULTS.json',{'mutants':mutants,'count':len(mutants),'scope':'Executed permissive bypass mutants vs independent archive oracle. No claim of production mutation adequacy.'})
save('HOST_CHECK_SUMMARY.json',{'archive_cases':len(rows),'actual_archive_function_cases':len(actual),'actual_admin_guard_cases':len(admin),
 'MR_pure_predicates':len(pred),'MR_oracle_cases':len(mr),'permissive_archive_mutants_detected':len(mutants),
 'runtime_cap_selected':False,'capacity_limit_raised':False,'native_runtime_tests':'UNRUN','WSL_calls':0,'T0':None,'R':None})
print(json.dumps({'archive':len(rows),'actual_archive':len(actual),'actual_admin':len(admin),'MR_pure':len(pred),'MR_oracle':len(mr),'mutants':len(mutants),'runtime':'UNRUN'}))
