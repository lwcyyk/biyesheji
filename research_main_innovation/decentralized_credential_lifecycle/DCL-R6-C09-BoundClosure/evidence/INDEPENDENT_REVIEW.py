"""Independent artifact/hash and numerical proof checks; no target functions."""
from pathlib import Path
import ast,hashlib,json
O=Path(__file__).resolve().parent.parent;E=O/'evidence';P=O.parent
def read(p):return json.loads(p.read_bytes())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
qpath=O/'proposals/C09_LOG_QUOTA_CONTRACT_PROPOSAL.json';q=read(qpath)
long_code=q['failure_record_schema']['reason']
if long_code not in q['allowed_failure_codes']:q['allowed_failure_codes'].append(long_code)
assert max(map(len,q['allowed_failure_codes']))==len(long_code)
write(qpath,q)
old=read(E/'HISTORICAL_REFERENCES/DCL-R6-CalDiag/evidence/FINAL_NATIVE_EXPORT_LOCK.json')
lookup={r['relative']:r for r in old['files']};checks=[]
for rel in ['inputs/root_private/c09_events.jsonl','inputs/c09_handoff.json','inputs/c09_commit.json','inputs/c09_exit_witness.json','inputs/CLOSED.json','out/visits.bin','out/visits.bin.intent.json','out/visits.bin.journal.jsonl']:
 p=E/'HISTORICAL_RAW'/rel
 if rel.endswith('/c09_events.jsonl'):p=E/'HISTORICAL_RAW/CALDIAG_c09_events.jsonl'
 r=lookup[rel];assert h(p)==r['sha256'] and p.stat().st_size==r['bytes']
 checks.append({'relative':rel,'matches_original_export_lock':True,'sha256':r['sha256'],'bytes':r['bytes']})
rows=[json.loads(b) for b in (E/'HISTORICAL_RAW/CALDIAG_c09_events.jsonl').read_bytes().splitlines(keepends=True)]
rawlines=(E/'HISTORICAL_RAW/CALDIAG_c09_events.jsonl').read_bytes().splitlines(keepends=True)
assert all(enc(r)==b for r,b in zip(rows,rawlines))
state=read(E/'HISTORICAL_RAW/inputs/c09_handoff.json');commit=read(E/'HISTORICAL_RAW/inputs/c09_commit.json');witness=read(E/'HISTORICAL_RAW/inputs/c09_exit_witness.json')
material={k:state[k] for k in ['nonce','window','sender','coordinator']}
hid=hashlib.sha256(json.dumps(material,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert hid==state['id'] and all(r['handoff_id']==hid and r['window']==state['window'] for r in rows)
assert h(E/'HISTORICAL_RAW/inputs/c09_commit.json')==state['commit_sha256'] and h(E/'HISTORICAL_RAW/inputs/c09_exit_witness.json')==state['witness_sha256']
assert commit['handoff_id']==hid and witness['handoff_id']==hid and witness['exit_code']==23
a=read(E/'NATIVE_RECORD_BYTE_ALGEBRA.json');L=a['record_upper_bytes']
assert L=={'pending':1298,'all_classification':1322,'state_transition':948,'ACK':1028,'common_all_native':1322}
sharp=max(256*L['pending'],255*L['pending']+L['all_classification'])+6*L['state_transition']+L['ACK'];assert sharp==339028
assert 256*L['all_classification']+6*L['state_transition']+L['ACK']==q['main_log_total_max_bytes']==345148
cursor=len(enc(q['quota_file_schema']))+3*(25-1);failure=len(enc(q['failure_record_schema']))+(25-1)+(20-1)
assert cursor==956==q['sidecar_max_bytes'] and failure==334==q['failure_record_max_bytes']
assert q['quota_total_write_upper']==345148+266*956+334==599778
assert q['total_quota_evidence_max_bytes']==345148+3*956+2*334==348684
assert q['fsync_attempts_upper']==266*2+263+2+1==798
assert not q['user_approved'] and not q['runtime_enabled']
# Acknowledge a very coarse ABI/file representation ceiling separately from an
# application quota. The source-state counterexample never overrides EFBIG/ENOSPC.
scope=read(E/'FROZEN_RA_ORIGINALS/inputs/execution_lock.json')['allowed_scopes']
small=copy_template=json.loads(json.dumps(a['templates']['pending']))
small['window']['execution_mode']=min((s for s in scope if s!='PT_STARTUP_DIAGNOSTIC_ONLY'),key=len)
Lmin=len(enc(small));Fmax=(1<<63)-1;Nabi=Fmax//Lmin;threshold=33554432//Lmin+1
represent={'category':'ADDITIONAL_FILE_ABI_HYPOTHESIS_NOT_AN_APPROVED_RESOURCE_QUOTA','assumptions':[
 'Linux regular-file append position/st_size limited by signed64 off_t','No truncation/rotation/recreation/external replacement of the one native log under frozen writers',
 'All completed rows include at least the fixed closed-schema skeleton; partial final writes do not increase complete-record count'],
 'Fmax':Fmax,'native_pending_line_lower':Lmin,'pending_complete_records_upper':Nabi,
 'preseal_raw_4450_files_representation_upper':4450*Fmax,
 'minimal_n_exceeding32MiB_from_skeleton':threshold,'raw_lower_at_that_n':threshold*Lmin,
 'status':'CONDITIONAL_PROVED_REPRESENTATIONAL_CEILING_ONLY',
 'scope_distinction':'State-machine contract lacks a numerical log quota. Abstract source loop admits arbitrary finite stutter if storage/time environment permits; actual ABI/file capacity limits real n. Do not claim physical infinite files/throughput.',
 'usefulness':'This enormous ceiling cannot close32MiB,1GiB or300s admission. Actual filesystem/space/time may stop much earlier; no new native execution proves attainable n.',
 'counterexample_scope':'One handoff self-loop and concrete admissible contract prefixes up to these additional storage hypotheses; source body itself has no bounded-observation guard.'}
with(E/'REPRESENTATION_LIMIT_CAVEAT.json').open('x',encoding='utf-8') as f:json.dump(represent,f,ensure_ascii=False,indent=2);f.write('\n')
family_p=E/'COUNTEREXAMPLE_FAMILY.json';family=read(family_p)
family['storage_qualification']=represent['scope_distinction'];family['concrete_32MiB_counterexample_parameter']=threshold
family['parameter']='Any finite n admitted by the abstract scheduler/storage environment; actual Linux ABI/filesystem capacity also constrains n. The source state machine has no observation quota.'
write(family_p,family)
tot_p=E/'TOTAL_BYTE_FAMILY_AUDIT.json';tot=read(tot_p)
tot['additional_representational_ceiling']=represent
tot['resource_compatible_B_raw_total']=None
write(tot_p,tot)
g_p=E/'BC_GATE_DECISIONS.json';g=read(g_p)
g['BC-1']['representation_qualification']='CONDITIONAL_PROVED coarse off_t64 ceiling; unprovable-current-contract status refers to missing usable producer quota, not the absence of every possible platform ceiling'
write(g_p,g)
with(E/'INDEPENDENT_MATHEMATICAL_REVIEW.json').open('x',encoding='utf-8') as f:json.dump({'historical_files':checks,'canonical_historical_lines':24,
 'native_identity_commit_witness_binding':'PASS_READ_ONLY_STRUCTURE','conditional_row_bound':1322,'quota_sharp':sharp,'quota_reserved':345148,'cursor':956,'failure':334,
 'retained_with_staging':348684,'quota_write_upper':599778,'quota_fsync_attempts':798,'Lmin':Lmin,'n_32MiB':threshold,'pending_ABI_ceiling':Nabi,
 'new_protocol_tests':0,'target_imports':0,'approval_effective':False},f,ensure_ascii=False,indent=2);f.write('\n')
for name,extra in {
 'C09_PENDING_RECORD_BOUND.md':f'''\n附加表示边界：若另行采用Linux signed64 off_t及单文件只追加/不轮转假设，则完整PENDING行每条至少{Lmin}字节，可给N≤floor((2^63−1)/{Lmin})={Nabi}的极粗上界。它来自ABI/文件容量，未成为受审的资源配额。反例族对真实存储许可的有限n成立，未越过EFBIG/ENOSPC或声称物理无限吞吐。具体n={threshold}的合同前缀已使仅PENDING的固定部分超过32MiB，但当前未进行此规模原生执行。''',
 'C09_PENDING_BYTE_BOUND.md':f'''\n表示上界与工程上界分别登记：附加off_t64假设给单原生日志B≤2^63−1、完整原件集粗界4450×(2^63−1)={4450*Fmax}字节。这些巨大表示界没有满足32MiB/1GiB/期限的证明作用；当前缺的是可用于准入的数值化生成与处理合同。''',
 'EVIDENCE_TOTAL_BYTE_BOUND.md':f'''\n在额外off_t64/封闭只追加假设下，可列极粗的单文件表示界2^63−1与raw4450文件乘积{4450*Fmax}；它未覆盖外部host控制文件的另外ABI，也未证明原件能装入一个合法包。本文的UNRESOLVED指资源兼容的可用字节/工作量界，不将物理表示空间描述为无限。''',
 'C09_PENDING_COUNTEREXAMPLES.md':f'''\n族X_n须服从真实存储可用空间/表示边界；状态机自身不设n配额。固定schema低界{Lmin}字节给出具体参数n={threshold}的32MiB合同反例候选，整个调度/存储环境约束均在附件列出；实际可达规模与时延没有由17条历史观测推断。'''
}.items():
 p=O/name;s=p.read_text(encoding='utf-8');marker='\nRESOURCE_GATE_PASS=NOT_OBTAINED'
 s=s.replace(marker,extra+'\n\n[表示边界与量词范围](evidence/REPRESENTATION_LIMIT_CAVEAT.json)。\n'+marker)
 s=s.replace('对任意有限n，选择','对任何底层存储/表示允许的有限n，选择')
 p.write_text(s,encoding='utf-8')
p=O/'FINAL_DECISION.md';s=p.read_text(encoding='utf-8')
s=s.replace('当前合同无可证统一数值上界；','当前状态机无可用记录配额；ABI可给极粗表示界，详见记录数报告；')
s=s.replace('UNRESOLVED；C09现行无配额且其他raw/aggregate/输出/模型/压缩/嵌套义务未闭合。',f'资源兼容界UNRESOLVED；附加off_t64仅有raw4450×(2^63−1)的极粗表示界；其他生成/压缩/嵌套义务未闭合。')
p.write_text(s,encoding='utf-8')
print(json.dumps({'historical_originals_verified':len(checks),'Lmin':Lmin,'n_32MiB':threshold,'ABI_record_ceiling':Nabi,
 'quota_pending_all':256,'quota_rows':263,'reserved_main':345148,'retained_with_staging':348684,'new_runtime_tests':0}))
