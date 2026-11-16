"""Seal the author erratum package after source/document/dependency checks."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re,sys
sys.set_int_max_str_digits(0)
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(r'D:\毕业设计');OUT=BASE/'crypto_fi_research_manuscript_v2_1';EV=OUT/'evidence';V2=BASE/'crypto_fi_research_manuscript_v2';AUD=BASE/'crypto_fi_publication_impact_audit'
def read(p):return Path(p).read_text('utf-8-sig')
def jd(p):return json.loads(read(p))
def rec(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
qa=[]
def check(name,condition):
    qa.append(dict(name=name,passed=bool(condition)))
    assert condition,name
def canonical(d):return json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def content(s,start,end):
    a=s.index(start);return s[a:s.index(end,a)]

required=['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','ERRATUM_AND_CERTIFICATE_AUDIT.md','HUMAN_REVIEW_ENTRY.md','MANIFEST.json']
md={n:read(OUT/n) for n in required if n.endswith('.md')}
m=jd(OUT/'CLAIM_EVIDENCE_MATRIX.json');oldm=jd(V2/'CLAIM_EVIDENCE_MATRIX.json');r=jd(EV/'REPLAY_976.json');binding=jd(EV/'DISPLAY_TABLE_BINDING.json');trace=jd(EV/'MATERIAL_AND_CLAIM_DEPENDENCY_TRACE.json');tables=jd(EV/'DISTRIBUTION_TABLES.json')
draft=md['CRYPTOANALYSIS_DRAFT.md'];old=read(V2/'CRYPTOANALYSIS_DRAFT.md')
check('Final deterministic checker243 passed',r['checks_passed']==243 and all(x['passed'] for x in r['checks']))
check('976 all1281 coefficients matched',r['convolution']['compared_coefficients']==1281 and r['convolution']['all_coefficients_match'] and r['convolution']['first_difference'] is None)
check('976 new coefficient bytes equal sealed original',rec(EV/'chi_976_64fold_coefficients.json')['sha256']==r['convolution']['legacy_coefficients']['sha256']==r['convolution']['new_coefficients']['sha256'])
check('976 epsilon complete two-term bound exact',r['probability']['epsilon_le_2_to_minus1118'] and r['probability']['sum_certificate']['largest_integer_k_with_value_le_2_to_minus_k']==1118)
check('Current replay source file fingerprints retained',all(rec(x['path'])==x for x in r['source_files']))

rows=[]
for name in ['640','976','1344']:
    matches=re.findall(r'^\| '+name+r' \| ([0-9,]+) \|$',draft,re.M)
    check('Exactly one active'+name+' mass row',len(matches)==1)
    actual=list(map(int,matches[0].split(',')));b=binding['profiles'][name];law=tables['profiles'][name]
    same=actual==b['parsed_display_mass']==b['official_mass']==b['certificate_input_mass']==law['mass_zero_then_each_signed_value']
    check(name+' actual displayed/CDF/producer-input identity',same)
    check(name+' sampler exhaustive finite input scope',law['sampler_input_words_exhausted']==65536 and law['sampler_matches_mass'])
    check(name+' input law normalization/support/symmetry',law['normalization']==65536 and law['support_size']==2*law['s']+1 and law['symmetric'])
    expected_parity=(32770,32766) if name=='1344' else (32768,32768)
    check(name+' actual declared parity',(law['even_numerator'],law['odd_numerator'])==expected_parity)
    rows.append('| '+name+' | '+matches[0]+' |')
check('Three display rows contiguous','\n'.join(rows) in draft)
check('Erroneous active976 row absent','| 976 | 11278,10277,7774,4882,2545,1131,426,138,38,8,1 |' not in draft)
check('Binding fingerprint equals final manuscript',binding['manuscript']==rec(OUT/'CRYPTOANALYSIS_DRAFT.md'))
check('Source location corrected','Table6' not in draft and '26 Table6' not in md['ERRATUM_AND_CERTIFICATE_AUDIT.md'])
check('2021 PMF formula and2023 numeric CDF explicitly separated','2021版由§2.2.4' in draft and '2023物理PDF16' in draft)

# The repaired surfaces do not regenerate the two main mathematical results.
preserved=[]
for name,start,end in [
 ('Abstract','## 摘要','## 1.'),
 ('Main original-game/CF1 proofs','## 2. 打印算法','## 7.'),
 ('Three-profile probability table','### 7.1','### 7.2'),
 ('640 proposition and software scope','### 7.2','## 8.'),
 ('Exact LWE premise and conditional theorem audit','## 8.','## 10.'),
 ('Complete bounded-error paper algorithm/proof','## 附录A','## 附录B')]:
    a,b=content(old,start,end),content(draft,start,end)
    check(name+' preserved byte-for-byte',a==b)
    preserved.append(dict(section=name,utf8_sha256=hashlib.sha256(b.encode()).hexdigest(),unchanged=True))
oldD=content(old,'## 附录D','## 参考文献')
newD=content(draft,'## 附录D','## 参考文献')
oldD=oldD.replace('仅交付四份v2文件，电子来源从历史只读路径引用。','本版交付五份核心文件，电子来源从历史只读路径及本版evidence目录引用。')
check('AppendixD mathematical chain preserved with delivery-count update only',oldD==newD)
check('640 exact probability payload unchanged',m['probability_results']==oldm['probability_results'])
check('Both frozen models/quantifiers unchanged',m['frozen_models']==oldm['frozen_models'])

claims={c['id']:c for c in m['claims']}
check('All36 claim impacts individually registered',{x['claim_id'] for x in m['erratum_impact_by_claim']}==set(claims) and len(claims)==36)
check('All claim source IDs resolve',all(set(c['source_ids'])<=set(m['source_registry']) for c in claims.values()))
check('All dependency IDs resolve',all(set(c['dependencies'])<=set(claims) for c in claims.values()))
def ancestors(cid,visiting=None,done=None):
    visiting=set() if visiting is None else visiting;done=set() if done is None else done
    if cid in visiting:raise AssertionError('dependency cycle '+cid)
    if cid in done:return done
    visiting.add(cid)
    for dep in claims[cid]['dependencies']:ancestors(dep,visiting,done)
    visiting.remove(cid);done.add(cid);return done
for cid in claims:ancestors(cid)
check('Claim dependency graph acyclic',True)
for label,root in [('A','C09'),('B','C25d')]:
    deps=sorted(ancestors(root))
    check(label+' transitive proof dependencies exclude976','C10_976' not in deps and deps==m['main_result_dependency_audit'][label]['transitive_claim_dependencies'])
check('A profile-specific certificate dependency','C10_640' in claims['C09']['dependencies'] and 'C10' not in claims['C09']['dependencies'])
check('Other-parameter decryption reliability unresolved',claims['C25b']['evidence_status']=='UNRESOLVED')
check('Original active theorem statements/quantifiers retained',all(all(claims[c['id']][k]==c[k] for k in ['claim','quantifiers','assumptions','evidence_status']) for c in oldm['claims']))
check('Eight current correction IDs closed in report',all(cid in md['ERRATUM_AND_CERTIFICATE_AUDIT.md'] for cid in m['v2_1_correction_ids']) and len(m['v2_1_correction_ids'])==8)
check('Human entry routes to v2.1 core files',str(OUT/'CRYPTOANALYSIS_DRAFT.md').replace('\\','/') in md['HUMAN_REVIEW_ENTRY.md'] and str(V2/'CRYPTOANALYSIS_DRAFT.md').replace('\\','/') not in md['HUMAN_REVIEW_ENTRY.md'])
check('Human entry retains full main-model restrictions',all(t in md['HUMAN_REVIEW_ENTRY.md'] for t in ['λ≥2','n=8λ','D=15','q=32768','未筛选','平局向上','预先固定','99.9969655%','3n+1','初始界逐固定A']))

local=[];table_errors=[]
for n,s in md.items():
    check(n+' control characters clean',all(ord(c)>=32 or c=='\n' for c in s))
    check(n+' requested Chinese style','不是' not in s and '而是' not in s)
    check(n+' math delimiter pairing',s.count('\\[')==s.count('\\]') and s.count('\\(')==s.count('\\)'))
    expected=None
    for line_no,line in enumerate(s.splitlines(),1):
        if line.startswith('|'):
            columns=len(re.split(r'(?<!\\)\|',line))-2
            if expected is not None and expected!=columns:table_errors.append(dict(file=n,line=line_no,expected=expected,actual=columns))
            expected=columns
        else:expected=None
    for t in re.findall(r'\]\(([^)]+)\)',s):
        if t.startswith('http') or not re.search(r'\.(?:md|json|pdf|py|txt|tex)$',t,re.I):continue
        p=Path(t);local.append(dict(in_file=n,path=t,exists=p.is_file(),absolute=p.is_absolute()))
check('Markdown table columns intact',not table_errors)
check('Local Markdown targets absolute and existent',all(x['exists'] and x['absolute'] for x in local))
tags=re.findall(r'\\tag\{([^}]+)\}',draft)
check('Equation tags unique',len(tags)==len(set(tags)))
check('Delivery description has five current core files','本版五份核心文件' in draft and '仅交付四份v2文件' not in draft)

# Check every inherited baseline and actual newly-used source fingerprint.
history=jd(EV/'INPUT_SNAPSHOT.json')+jd(EV/'ADDITIONAL_INPUT_LOCK.json')
final_history=[]
for x in history:final_history.append(dict(path=x['path'],match=rec(x['path'])==x))
check('All127 historical snapshot records unchanged',len(history)==127 and all(x['match'] for x in final_history))
v2manifest=jd(V2/'MANIFEST.json');want=v2manifest.pop('payload_sha256')
check('v2 canonical seal still valid',hashlib.sha256(canonical(v2manifest)).hexdigest()==want)
audit=jd(AUD/'VERDICT.json');want_audit=audit.pop('payload_sha256')
check('Prior publication-impact verdict seal still valid',hashlib.sha256(canonical(audit)).hexdigest()==want_audit)
sourcechecks=[]
def verify_records(x):
    if isinstance(x,dict):
        if isinstance(x.get('path'),str) and isinstance(x.get('sha256'),str) and len(x['sha256'])==64 and Path(x['path']).is_absolute():
            p=Path(x['path']);a=rec(p) if p.is_file() else None
            good=a is not None and a['sha256']==x['sha256'] and ('bytes' not in x or a['bytes']==x['bytes'])
            sourcechecks.append(dict(path=str(p),match=good));assert good,str(p)
        for v in x.values():verify_records(v)
    elif isinstance(x,list):
        for v in x:verify_records(v)
for key in ['S1','S2','S10','S11','E1','E2','E3','E7','E8','E9','V1']:verify_records(m['source_registry'][key])
check('Actual registered source fingerprint checks',all(x['match'] for x in sourcechecks))
json_errors=[]
for p in OUT.rglob('*.json'):
    try:jd(p)
    except Exception as e:json_errors.append(dict(path=str(p),error=str(e)))
check('All current JSON parses',not json_errors)
check('Four written files present before manifest',all((OUT/n).is_file() for n in required[:-1]))

qa_record=dict(schema='fi-v2.1/final-QA/1',all_checks_passed=True,checks=qa,checks_count=len(qa),preserved_main_proof_sections=preserved,historical_snapshot_count=len(history),historical_end_checks=final_history,source_fingerprint_check_count=len(sourcechecks),source_fingerprint_checks=sourcechecks,local_link_count=len(local),table_errors=[],broken_links=[],json_errors=[],current_replay_checks=243,convolution_coefficients_compared=1281,actual_source_visual_read_scope=['2021 PDF16 Algorithm5','2021 PDF25 Table3','2023 physicalPDF16 TableA4'],prior_structural_PDF_preflight_hashes_reverified=True)
dump(EV/'FINAL_QA.json',qa_record)

manifest=dict(schema='fi-research-manuscript/manifest/2.1',version='v2.1',date_asia_shanghai='2026-11-10',sealed_at_asia_shanghai=datetime.now(timezone(timedelta(hours=8))).isoformat(),status='INC976_CLOSED_976_EXACT_REPLAY_SEALED_READY_FOR_HUMAN_CRYPTOGRAPHIC_REVIEW',root=str(OUT),required_deliverables=required,identity=m['identity'],scope='Author manuscript erratum, impact-scope audit, official-source checks, and deterministic finite-distribution certificate replay',
 erratum=m['erratum_closed'],frozen_models=m['frozen_models'],main_result_dependency_audit=m['main_result_dependency_audit'],
 current_certificate_scope=dict(full976_convolution_and_epsilon=True,coefficients_compared=1281,new_coefficient_file_byte_identical=True,epsilon976_upper='2^-1118',checks_final_execution=243,full976_replay_executions=2,other_profiles='640/1344 CDF-PMF-display-producer-input and finite sampler-domain checks;64fold/epsilon inherited',profiles_with65536_input_words_enumerated=3),
 correction_status=[dict(id=x,status='CLOSED') for x in m['v2_1_correction_ids']],
 historical_inputs_read_only=True,input_snapshot=history,all_historical_bytes_unchanged=True,
 inherited_seals=dict(v2_payload_sha256=want,publication_impact_verdict_payload_sha256=want_audit),
 actual_source_records=dict(official2021=rec(BASE/'crypto_fi_research_manuscript_v1/sources/official_frodo_2021.pdf'),official2023=rec(AUD/'sources/official_frodo_2023.pdf'),official1344_erratum=[rec(EV/f'official_1344_erratum_{i}.json') for i in [0,1]],old_parameter_certificates=rec(BASE/'crypto_fi_research_manuscript_v1/sources/PARAMETER_CERTIFICATES.json'),producer_CDF_input=rec(BASE/'crypto_frodo_unconditional_support/sources/official_cdf_input.json'),producer_script=rec(BASE/'crypto_frodo_unconditional_support/sources/build_mathematical_certificates.py')),
 arithmetic_entrypoints=[rec(EV/n) for n in ['replay_976_and_check_tables.py','REPLAY_976.json','chi_976_64fold_coefficients.json','DISTRIBUTION_TABLES.json','DISPLAY_TABLE_BINDING.json','MATERIAL_AND_CLAIM_DEPENDENCY_TRACE.json','976_MENTION_INVENTORY.json']],
 qa=dict(all_checks_passed=True,checks_count=len(qa),evidence=rec(EV/'FINAL_QA.json'),main_proofs_and640_exact_probability_payload_preserved=True,all_three_display_tables_bind=True,source_fingerprint_check_count=len(sourcechecks)),
 external_evidence_pending=['Exact author UE commit/config, A generation, secret-noise seed/joint law, Ord/dtype/modulo/packing/rounding/failure mapping and message-checked full trace','FI parameterized full LWE reduction and exact nonempty hardness premise','CJL original/current PDF and Nishimaki extended Lemma5.7 version/source mapping','Global application priority and human cryptographic peer review'],
 adopted_application_priority=dict(source_verdict=rec(AUD/'VERDICT.json'),cutoff='2026-11-10',state='Search-bounded concrete-object application candidates; global priority unresolved',new_priority_searches_this_round=0),
 next_external_input='Author exact UE commit/config/randomness-and-arithmetic mapping plus one message-checked Enc->TG->Upd->Dec trace; human questionsH1-H3 retained',
 action_counts=m['action_counts'],files_exclude_manifest_itself=True,
 files=[rec(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p!=OUT/'MANIFEST.json'],
 manifest_integrity_definition='SHA256 of canonical UTF8 JSON omitting payload_sha256; json.dumps(ensure_ascii=False,sort_keys=True,separators=(comma,colon)). File-byte hash is distinct.')
manifest['payload_sha256']=hashlib.sha256(canonical(manifest)).hexdigest()
dump(OUT/'MANIFEST.json',manifest)
sealed=jd(OUT/'MANIFEST.json');expected=sealed.pop('payload_sha256')
assert expected==hashlib.sha256(canonical(sealed)).hexdigest()
for item in sealed['files']:assert rec(item['path'])==item
assert {p.name for p in OUT.iterdir() if p.is_file()}==set(required)
print(json.dumps(dict(status=manifest['status'],core=[rec(OUT/n) for n in required],sealed_file_count=len(manifest['files']),qa_checks=len(qa),historical_inputs_preserved=127,source_fingerprint_checks=len(sourcechecks),payload_sha256=expected),ensure_ascii=False))
