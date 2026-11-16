"""Administrative decision delivery only. No runtime/native seal or activation."""
from INPUT_AUDIT import ROOT,PREV,OUT,E,RUNTIME,ISO,NAV,read,save,sha,row,cp
from pathlib import Path
import hashlib,json,re,zipfile,time
from datetime import datetime,timezone

tick=time.perf_counter();assert not(E/'DELIVERY_CHECK.json').exists()
check=read(E/'SECOND_PASS_DECISION_REVIEW.json');assert check['status']=='PASS_RESEARCH_ARTIFACTS_ONLY'
bindings=read(E/'DECISION_BINDINGS.json')
for x in bindings.values():assert sha(x['path'])==x['sha256']
inputs=[
 (PREV,'FINAL_DECISION.md'),(PREV,'UNRESOLVED_BOUND_CHECKLIST.md'),(PREV,'CLOSE_RECORD_PRODUCER_AUDIT.md'),
 (PREV,'CLOSE_RESERVE_BOUND_PROOF.md'),(PREV,'FULL_EVIDENCE_BYTE_CLOSURE.md'),(PREV,'ARCHIVE_WORK_AND_MEMORY_BOUND.md'),
 (PREV,'NEXT_STAGE_AUTHORIZATION_REQUEST.md'),(PREV,'proposals/CLOSE_RESERVE_REVIEW_DRAFT.json'),(PREV,'proposals/CAPACITY_REVIEW_DRAFT.json'),
 (ROOT/'DCL-R6-C09-PendingQuota-Closure','FINAL_DECISION.md'),(ROOT/'DCL-R6-EvidenceContract-Closure','FINAL_DECISION.md'),
 (ROOT/'DCL-R6-FullChain-AdmissionFix','FINAL_DECISION.md'),
 (ROOT/'DCL-R6-C09-BoundClosure','MR_CROSS_INSTANCE_FINAL_APPROVAL_TEXT.md'),
 (ROOT/'DCL-R6-C09-BoundClosure','proposals/MR_CROSS_INSTANCE_FINAL_RULE_DRAFT.json'),
 (ROOT/'DCL-R6-C09-BoundClosure','evidence/COUNT_SCOPE_COVERAGE_REVIEW.json'),
 (PREV,'evidence/CLOSE_SCHEMA_BYTE_ALGEBRA.json'),(PREV,'evidence/MANIFEST_ZIP_BOUND_ARITHMETIC.json')]
copies=[]
for base,n in inputs:
    p=base/n;q=E/'PRIOR_INPUT_COPIES'/base.name/n;cp(p,q);assert sha(p)==sha(q)
    copies.append({'original':row(p),'copy':str(q)})
save('PRIOR_INPUT_COPY_LOCK.json',{'files':copies,'required_priority_inputs':12})
save('ADMIN_REVIEW_NOTES.json',{'initial_report_style_check':{'status':'FLAGGED_AND_CORRECTED',
 'file':'WALL_TIME_ASSUMPTIONS.md','reason':'same-agent report checker conservatively rejected a negative Chinese wording',
 'impact':'wording only; mathematical/contract decisions unchanged'},'final_arithmetic_contract_link_check':'PASS_RESEARCH_ONLY',
 'not_native_test_or_runtime_retry':True})
save('FINAL_MACHINE_DECISION.json',{'schema':'DCL-RBD-DECISION/1','client_date':'2026-11-16','timezone':'Asia/Shanghai',
 'overall':['CURRENT_CONTRACT_UNSAT','CONTRACT_REVISION_REQUIRED'],'source_frozen_bounds':{'H':52,'core_attempts':212,'stable_core_paths':54,'MR_reason_token':38,'Root_MR_marker':194},
 'whole_close_bytes':None,'whole_C09_bytes':None,'whole_raw_bytes':None,'FULL_BYTE_BOUND':'FULL_BYTE_BOUND_UNRESOLVED',
 'capacity':'CAPACITY_CONTRACT_NOT_READY','WALL_TIME_BOUND':'WALL_TIME_BOUND_UNRESOLVED',
 'same_scope_static_audit_closed':True,'reopen_only':'new explicit user decision, quantitative profile, authorized exact diff or new source/evidence input',
 'A_fullchain':'FULLCHAIN_UNSAT_UNDER_CURRENT_CAPACITY_CONTRACT','B_effective_capacity':'BLOCKED_NULL_PARAMETERS',
 'four_authorizations':read(E/'FOUR_AUTHORIZATION_DECISIONS.json'),'source_implementation_edits':0,
 'WSL_calls':0,'dynamic_tests':0,'native_faults':0,'F1_runs':0,'F4_runs':0,'T0':None,'deadline':None,'R':None,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE','STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED'})

def L(n):return '['+n+']('+str(OUT/n).replace('\\','/')+')'
prefix=('## DCL-R6-ResidualBounds-Decision 终局静态决策（2026-11-16）\n\n'
 '**CURRENT_CONTRACT_UNSAT；CONTRACT_REVISION_REQUIRED。** 既有15项责任已逐项终局分类，同一冻结范围不再重复静态审计。'
 '完整角色图H≤52，关闭核心≤212次生产尝试、稳定核心路径54；MR固定reason token≤38、Root marker≤194。'
 '完整关闭/全证据字节和资源参数仍缺量化profile，保持null。\n\n'
 '计数矛盾有最小见证：257必需raw＋manifest⇒native至少258>257；255raw＋native两输出⇒admin至少257>256。'
 '结论针对全量成功验收，允许区分业务进程启动与验收结果。方案A保留当前合同并接受UNSAT；方案B仅有已知逻辑子条款可审，'
 '源码维护/总容量生效/MR/动态四类许可分开，尚未授予。下一输入应是明确A/B决定、定量profile或获准diff，停止同范围扩容猜测。\n\n'
 'FULL_BYTE_BOUND_UNRESOLVED；CAPACITY_CONTRACT_NOT_READY；WALL_TIME_BOUND_UNRESOLVED；'
 'MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE。现行256/257和64运行源/输入原字节保持；'
 '本轮实现/WSL/动态/真实故障/F1/F4均0，T0/R=null。RESOURCE_GATE_PASS=NOT_OBTAINED；'
 'STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。\n\n'
 +L('FINAL_DECISION.md')+' · '+L('CURRENT_CONTRACT_UNSAT_PROOF.md')+' · '+L('APPROVAL_DECISION_PACKAGE.md')+' · '+L('EVIDENCE_INDEX.md')+'\n\n'
 '下文完整保留先前导航字节。\n\n---\n\n')
nav=read(E/'NAV_BASELINE.json')['files']
for r in nav:
    p=Path(r['path']);old=Path(r['copy']).read_bytes();assert p.read_bytes()==old and sha(r['copy'])==r['sha256']
    p.write_bytes(prefix.encode('utf-8')+old)

prior=read(E/'ALL_PRIOR_BASELINE.json')['files'];assert len(prior)==10317
bad=[]
for r in prior:
    p=Path(r['path'])
    if not p.is_file()or p.stat().st_size!=r['bytes']or sha(p)!=r['sha256']:bad.append(str(p))
assert not bad,bad
expected={r['path']for r in prior}
actual={str(p)for base in [ROOT,ISO]for p in base.rglob('*')if p.is_file()and not p.is_relative_to(OUT)and not(p.parent==ROOT and p.name in NAV)}
extra=sorted(actual-expected);missing=sorted(expected-actual);assert not extra and not missing,(extra,missing)
src=read(E/'FROZEN_SOURCE_LOCK.json')['files']
for r in src:assert sha(r['path'])==sha(r['copy'])==r['sha256']
mis=read(ROOT/'DCL-R6-batch02-Perf/evidence/DUPLICATE_REGISTER.json')
miserr=[r['relative']for r in mis['files']if sha(Path(mis['path'])/r['relative'])!=r['duplicate_sha256']]
assert len(mis['files'])==47 and not miserr
ncheck=[]
for r in nav:
    assert Path(r['path']).read_bytes().endswith(Path(r['copy']).read_bytes())
    ncheck.append({'path':r['path'],'suffix_sha256':r['sha256'],'suffix_preserved':True,'current_sha256':sha(r['path'])})
save('FINAL_IMMUTABILITY_CHECK.json',{'historical9867':9867,'prior_delivery450':450,'all_prior10317':10317,
 'mismatches':bad,'new_files_outside_delivery':extra,'missing_prior':missing,'frozen_runtime64':'UNCHANGED',
 'prior_maintenance_objects8':'UNCHANGED','prior_contract_review_objects21':'UNCHANGED','mispath47_errors':miserr,'navigation':ncheck})

json_count=0;links=0;linkerr=[]
for p in OUT.rglob('*.json'):read(p);json_count+=1
for p in OUT.glob('*.md'):
    t=p.read_text(encoding='utf-8');assert '不是'not in t
    for v in re.findall(r'\]\(([^)]+)\)',t):
        links+=1;q=re.sub(r':\d+$','',v.strip('<>'))
        if not Path(q).exists()and q!=str(E/'DELIVERY_CHECK.json').replace('\\','/'):
            linkerr.append({'report':p.name,'target':q})
assert not linkerr,linkerr
mf=OUT/'RBD_MANIFEST.json';zp=OUT/'RBD_EVIDENCE.zip'
excluded={'RBD_MANIFEST.json','RBD_EVIDENCE.zip','RBD_EVIDENCE.zip.sha256','evidence/DELIVERY_CHECK.json'}
files=[]
for p in sorted(OUT.rglob('*')):
    rel=p.relative_to(OUT).as_posix()
    if p.is_file()and '__pycache__'not in p.parts and rel not in excluded:
        files.append({'relative':rel,'bytes':p.stat().st_size,'sha256':sha(p)})
manifest={'schema':'DCL-RBD-RESEARCH-MANIFEST/1','client_date':'2026-11-16','status':'STATIC_DECISION_DELIVERY_ONLY',
 'scope':'reports, frozen read inputs, static/count/byte proofs and inactive decision drafts; no runtime seal or executable authority',
 'files':files,'excluded':sorted(excluded)}
mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with zipfile.ZipFile(zp,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
    for r in files:z.write(OUT/r['relative'],r['relative'])
    z.write(mf,mf.name)
with zipfile.ZipFile(zp)as z:
    names=z.namelist();assert len(names)==len(set(names))==len(files)+1
    assert set(names)=={r['relative']for r in files}|{mf.name}
    assert z.read(mf.name)==mf.read_bytes()
    for r in files:
        b=z.read(r['relative']);assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256']
zsha=sha(zp);(OUT/'RBD_EVIDENCE.zip.sha256').write_text(zsha+'  RBD_EVIDENCE.zip\n',encoding='ascii')
save('DELIVERY_CHECK.json',{'schema':'DCL-RBD-DELIVERY/1','client_date':'2026-11-16','timezone':'Asia/Shanghai',
 'status':'PASS_ADMINISTRATIVE_RESEARCH_DELIVERY_ONLY','overall':['CURRENT_CONTRACT_UNSAT','CONTRACT_REVISION_REQUIRED'],
 'reports':13,'index':1,'gap_rows':15,'gap_properties':12,'final_answers':20,'same_scope_audit_closed':True,
 'H_frozen_bound':52,'core_attempt_upper':212,'MR_reason_token_upper':38,'Root_MR_marker_upper':194,
 'native_minimal_witness_members':258,'native_current_guard':257,'admin_minimal_witness_exports':257,'admin_current_guard':256,
 'whole_close_bytes':None,'whole_C09_bytes':None,'whole_raw_bytes':None,'FULL_BYTE_BOUND':'FULL_BYTE_BOUND_UNRESOLVED',
 'capacity':'CAPACITY_CONTRACT_NOT_READY','WALL_TIME_BOUND':'WALL_TIME_BOUND_UNRESOLVED',
 'historical9867_unchanged':9867,'prior_delivery450_unchanged':450,'all_prior10317_unchanged':10317,
 'mismatches':bad,'new_files_outside_delivery':extra,'runtime_source_inputs_unchanged':64,'old_maintenance_objects':8,
 'old_contract_review_objects':21,'mispath_unchanged':47,'navigation_original_byte_suffixes_preserved':4,
 'prior_archive_members_fully_rechecked':140,'Option_A_sha256':bindings['A']['sha256'],'Option_B_sha256':bindings['B']['sha256'],
 'prior_close_draft_sha256':bindings['prior_close_draft']['sha256'],'prior_capacity_draft_sha256':bindings['prior_capacity_draft']['sha256'],
 'MR_rule_sha256':bindings['MR_rule']['sha256'],'original_approved_field_note':'user_approved=false; literal approved field absent in two prior drafts',
 'new_options_approved':False,'new_options_effective':False,'any_draft_activated':False,'old_guards':'256/257_UNCHANGED',
 'four_authorizations':read(E/'FOUR_AUTHORIZATION_DECISIONS.json'),
 'runtime_mechanism_edits':0,'budget_core_edits':0,'C09_MR_guard_seal_finalizer_gate_edits':0,
 'WSL_calls':0,'dynamic_tests':0,'native_faults':0,'F1_runs':0,'F4_runs':0,'T0':None,'deadline':None,'R':None,
 'RESOURCE_GATE_PASS':'NOT_OBTAINED','F1':'UNRUN_RESOURCE_GATE','F4':'UNRUN_RESOURCE_GATE','PASS_BOUNDED':[],
 'MR_CROSS_INSTANCE_ADMISSION':'PROPOSED_NOT_EFFECTIVE','STRICT_SEPARATION_INSTANCES':0,'IMPLEMENTATION_GATE':'CLOSED',
 'native_seal':'NOT_APPLICABLE_NO_RUNTIME','administrative_runtime_seal':'NOT_APPLICABLE_NO_ENTRY',
 'research_archive':'SEALED_AND_VERIFIED','JSON_parsed':json_count,'links_checked':links,'link_errors':linkerr,
 'manifest_files':len(files),'ZIP_members':len(names),'manifest_sha256':sha(mf),'ZIP_sha256':zsha,'ZIP_bytes':zp.stat().st_size,
 'receipt_excluded_from_preimages':True,'utc_recorded':datetime.now(timezone.utc).isoformat(),
 'research_packaging_seconds':time.perf_counter()-tick})
print(json.dumps({'delivery':'PASS_RESEARCH_ONLY','reports':13,'gaps':15,'answers':20,'H':52,'core':212,
 'all_prior':10317,'source64':'UNCHANGED','ZIP_members':len(names),'ZIP_bytes':zp.stat().st_size,'ZIP_sha256':zsha,
 'overall':'CURRENT_CONTRACT_UNSAT / CONTRACT_REVISION_REQUIRED','runtime_runs':0},ensure_ascii=False))
