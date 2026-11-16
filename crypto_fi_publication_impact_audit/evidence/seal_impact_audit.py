from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,re,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(r'D:\毕业设计');OUT=BASE/'crypto_fi_publication_impact_audit';EV=OUT/'evidence';V2=BASE/'crypto_fi_research_manuscript_v2'
def jd(p):return json.loads(Path(p).read_text('utf-8-sig'))
def rec(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
qa=[]
def check(name,c):
    qa.append(dict(name=name,passed=bool(c)))
    assert c,name
v=jd(OUT/'VERDICT.json')
texts={n:(OUT/n).read_text('utf-8') for n in v['required_deliverables'] if n.endswith('.md')}

# Promote the source/file references in prose to clickable, absolute local paths.
names=['ORIGINAL_CLAIM_AND_PARAMETER_MAPPING.md','APPLICATION_PRIORITY_AND_IMPACT.md','HUMAN_REVIEW_ENTRY.md']
evidence_names=['INPUT_FINGERPRINT_VERIFICATION.json','SOURCE_LEDGER.json','SEARCH_LEDGER.json','PUBLIC_ACQUISITION.json','SCALAR_SOURCE_ACCOUNTING.json']
for name,s in texts.items():
    # All prose paths here are literal file mentions. Existing Markdown targets are left intact.
    for en in evidence_names:
        old='evidence/'+en;target=str(EV/en).replace('\\','/')
        s=re.sub(r'(?<![/\w\[])'+re.escape(old)+r'(?![\w\]])',lambda m:f'[{old}]({target})',s)
    for other in names:
        if other==name:continue
        s=re.sub(r'(?<![\w/\[\\])'+re.escape(other)+r'(?![\w\]\)])',lambda m:f'[{other}]({str(OUT/other).replace(chr(92),"/")})',s)
    (OUT/name).write_text(s,'utf-8');texts[name]=s

local_links=[];table_errors=[]
for n,s in texts.items():
    check(n+' control characters',all(ord(c)>=32 or c=='\n' for c in s))
    check(n+' requested Chinese style','不是' not in s and '而是' not in s)
    check(n+' math display pairs',s.count('\\[')==s.count('\\]'))
    expected=None
    for i,l in enumerate(s.splitlines(),1):
        if l.startswith('|'):
            count=len(re.split(r'(?<!\\)\|',l))-2
            if expected is None:expected=count
            elif count!=expected:table_errors.append(dict(file=n,line=i,count=count,expected=expected))
        else:expected=None
    for target in re.findall(r'\]\(([^)]+)\)',s):
        if re.match('https?://',target):continue
        p=Path(target);local_links.append(dict(source=n,path=target,exists=p.is_file(),absolute=p.is_absolute()))
check('Markdown table columns',not table_errors)
check('All local Markdown targets exist and are absolute',all(x['exists'] and x['absolute'] for x in local_links))
check('Core conclusions retain bounded-priority language','全球' in texts['APPLICATION_PRIORITY_AND_IMPACT.md'] and all('范围' in texts[n] for n in names[:2]))
check('Both source theorem scopes explicit','前提之外' in texts[names[0]] and 'H_rich' in texts[names[0]] and 'H_fixed' in texts[names[0]])
check('Finite n versus asymptotic correctness distinguished','单个固定n=640' in texts[names[0]] and '单个有限n' in texts[names[1]])
check('Human entry contains all decisive questions',all(h in texts['HUMAN_REVIEW_ENTRY.md'] for h in ['H1','H2','H3','n<64','ε_n=1','99.9969655%','3n+1']))
check('Actual performance verification status bounded',v['original_claim_summary']['post_update_decryption_comparison'].startswith('NOT_REPORTED'))

# All initially snapshotted historical bytes remain intact.
initial=jd(EV/'INPUT_LOCK.json');end=[]
for old in initial:
    new=rec(old['path']);end.append(dict(path=old['path'],match=new==old))
check('All17 original historical snapshot records unchanged',len(end)==17 and all(x['match'] for x in end))
ref=jd(EV/'INPUT_FINGERPRINT_VERIFICATION.json')
for r in ref['reference_records']:check('Referenced hash '+r['path'],rec(r['path'])==r['actual'])

# Verify every additional historical file used as a local source link against an existing seal.
vm=jd(V2/'MANIFEST.json');expected={}
for r in initial:expected[str(Path(r['path']))]=r
for r in vm['input_verification']['snapshot']:expected[str(Path(r['path']))]=r
for r in ref['reference_records']:expected[str(Path(r['path']))]=r['actual']
v1=BASE/'crypto_fi_research_manuscript_v1';v1m=jd(v1/'MANIFEST.json')
for r in v1m['files']:expected[str(v1/r['path'])]=dict(path=str(v1/r['path']),bytes=r['bytes'],sha256=r['sha256'])
adopted=[]
for p in sorted({Path(x['path']) for x in local_links}):
    if p.is_relative_to(OUT):continue
    actual=rec(p);want=expected.get(str(p))
    check('Adopted historical link sealed '+str(p),want is not None and actual==want)
    adopted.append(actual)

acq=jd(EV/'PUBLIC_ACQUISITION.json');check('All nine public version/PDF acquisitions succeeded',len(acq)==9 and all(x['status']==200 and x.get('saved_path') for x in acq))
pdfhash=rec(OUT/'sources/arxiv_v4.pdf')['sha256']
check('Publisher equals current v4 equals frozen target',pdfhash==rec(OUT/'sources/publisher_current.pdf')['sha256']==rec(v1/'sources/FI_journal_20261110.pdf')['sha256'])
check('Current source TeX equals frozen target',rec(OUT/'sources/arxiv_v4_source/articlev08.tex')['sha256']==rec(v1/'sources/articlev08.tex')['sha256'])
com=jd(EV/'VERSION_AND_SOURCE_COMPARISON.json')
check('Four versions preserve normalized TG/Upd',len(com)==4 and all(x['TG_UPD_normalized']==com[-1]['TG_UPD_normalized'] for x in com))
pre=jd(EV/'PREFLIGHT_SUMMARY.json')+[jd(EV/'SPEC2023_PREFLIGHT.json')]
check('Seven structural PDF preflights PASS',len(pre)==7 and all(x['verdict']=='PASS' for x in pre))
check('Search scope exact',jd(EV/'SEARCH_LEDGER.json')['web_query_count']==31)
s=jd(EV/'SCALAR_SOURCE_ACCOUNTING.json')
check('640 source sufficient premise fails',s['source_conditions'][0]['printed_sufficient_premise_satisfied'] is False)
check('CF128 finite printed sufficient premise holds',s['source_conditions'][1]['printed_sufficient_premise_satisfied'] is True)
check('INC976 exact display total and source CDF match',s['incidental976']['v2_display_total']==65718 and s['incidental976']['official_total']==65536 and s['incidental976']['cdf_derived_matches_official'])

json_errors=[]
for p in OUT.rglob('*.json'):
    try:jd(p)
    except Exception as e:json_errors.append(dict(path=str(p),error=str(e)))
check('All delivery/source JSON parses',not json_errors)
check('Four required core deliverables present',all((OUT/n).is_file() for n in v['required_deliverables']))

qa_record=dict(all_checks_passed=True,checks_count=len(qa),checks=qa,local_link_count=len(local_links),table_errors=[],broken_links=[],json_errors=[],historical_first_snapshot_count=len(initial),historical_first_snapshot_end_checks=end,referenced_record_count=ref['record_count'],adopted_historical_link_sources=adopted,new_visual_source_pages_inspected=['FI_v4 PDF11','FI_v4 PDF13','FI_v4 PDF14','FI_v4 PDF15','FI_v4 PDF19','FI_v4 PDF20','FI_v4 PDF21','KLR PDF44','Frodo2021 PDF25'],scope='Document/source verification and printed-constant accounting; no new independent mathematical review')
dump(EV/'FINAL_QA.json',qa_record)
v['status']='SEALED_COMPLETE_WITH_EXPLICIT_SOURCE_GAPS_AND_REOPEN_CONDITIONS'
v['sealed_at_asia_shanghai']=datetime.now(timezone(timedelta(hours=8))).isoformat()
v['historical_inputs_preserved']=True
v['source_qa']=dict(all_checks_passed=True,checks_count=len(qa),input_snapshot_records=len(initial),referenced_records=ref['record_count'],seven_PDF_preflights_pass=True,version_TG_Upd_blocks_match=True,local_link_count=len(local_links),final_QA=rec(EV/'FINAL_QA.json'))
v['adopted_historical_sources']=adopted
v['files_exclude_VERDICT_itself']=True
v['files']=[rec(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p!=OUT/'VERDICT.json']
v['self_integrity_definition']='SHA256 of UTF8 canonical JSON with payload_sha256 omitted; json.dumps(ensure_ascii=False,sort_keys=True,separators=(comma,colon)). Distinct from VERDICT file-byte hash.'
v['payload_sha256']=hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
dump(OUT/'VERDICT.json',v)
sealed=jd(OUT/'VERDICT.json');want=sealed.pop('payload_sha256')
assert want==hashlib.sha256(json.dumps(sealed,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
for x in sealed['files']:assert rec(x['path'])==x
print(json.dumps(dict(status=v['status'],core=[rec(OUT/n) for n in v['required_deliverables']],sealed_files=len(v['files']),qa_checks=len(qa),history_unchanged=True,payload_sha256=want),ensure_ascii=False))
