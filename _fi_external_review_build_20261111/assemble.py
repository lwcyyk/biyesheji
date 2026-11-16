"""Local assembly only. Historical inputs are read-only; public replay lives in replay/run.py."""
from pathlib import Path
import hashlib,json,re,os,shutil,sys,urllib.parse,difflib

B=Path(r'D:\毕业设计')
O=B/'crypto_fi_external_review_package'
W=Path(__file__).resolve().parent
V=B/'crypto_fi_research_manuscript_v3'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write(rel,s):
 p=O/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def rel(p):return p.relative_to(B).as_posix()
def abs_local(x,p):
 x=urllib.parse.unquote(x.strip('<>'))
 if not x or x.startswith('#') or re.match(r'^[a-z]+://',x,re.I):return None,None,None
 if re.match(r'^1-\\',x):return None,None,None  # display-math factor, not a Markdown link
 file,sep,fragment=x.partition('#');line=None
 hit=re.search(r':(\d+)$',file)
 if hit:line=int(hit[1]);file=file[:hit.start()]
 if not file:return None,None,None
 q=(Path(file) if re.match(r'^[A-Za-z]:[/\\]',file) else p.parent/file).resolve()
 return q,fragment,line
# Require a real Markdown label; this excludes display-math ](1-epsilon) sequences.
LINK=re.compile(r'(?<!!)\[([^\[\]\n]+)\]\(([^)\n]+)\)')
sel=set(p for p in V.rglob('*') if p.is_file())
matrix=read(V/'CLAIM_EVIDENCE_MATRIX.json')
def visit(x):
 if isinstance(x,dict):
  if 'path' in x and 'sha256' in x:
   p=Path(x['path'])
   if p.is_file():sel.add(p)
  else:
   for v in x.values():visit(v)
 elif isinstance(x,list):
  for v in x:visit(v)
for key in ['S1','S2','S3','S4','S5','S6','S7','S8','S10','E2','E5','E6','E7','E8','E9','E10','E11','E12','E13','E15','E16']:
 visit(matrix['source_registry'][key])
for root in ['crypto_fi_official_profile_review','crypto_fi_author_implementation_audit','crypto_fi_lwe_independent_review']:
 sel.update(p for p in (B/root).glob('*') if p.suffix in ('.md','.json'))
extras=[
 'crypto_branch_monitor/round_005/THEOREM_FOR_CITATION.md',
 'crypto_branch_monitor/round_005/independent_review_packet/INPUT_MANIFEST.json',
 'crypto_branch_monitor/round_005/independent_review_packet/REVIEW_REQUEST.md',
 'crypto_branch_monitor/round_005/independent_review_packet/STATEMENT_ONLY.md',
 'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/PHASE1_DERIVATION.md',
 'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/PHASE1_VERDICT.json',
 'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/exact_certificates.json',
 'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/math_verify.py',
 'crypto_fi_official_profile_review/evidence/recompute_review.py',
 'crypto_fi_official_profile_review/evidence/verify_historical_relations.py',
 'crypto_fi_official_profile_review/evidence/HISTORICAL_EVENT_RELATIONS.json',
 'crypto_fi_official_profile_review/evidence/OFFICIAL_1344_ERRATUM_LIVE_RECEIPT.json',
 'crypto_fi_official_profile_review/evidence/SOURCE_PAGES.json',
 'crypto_fi_official_profile_review/evidence/CURRENT_THREAD_SNAPSHOT.json',
 'crypto_fi_official_profile_review/evidence/AUTHOR_PROFILE_THREAD_SNAPSHOT.json',
 'crypto_fi_official_profile_review/evidence/PRIOR_FIXED_A_REVIEW_THREAD_SNAPSHOT.json',
 'crypto_fi_640_probability_review/review_01a1c4ed/evidence/recompute_probability_chain.py',
 'crypto_fi_640_fixed_A_review/evidence/recompute_certificates.py',
 'crypto_fi_640_fixed_A_review/evidence/RECOMPUTED_CERTIFICATES.json',
 'crypto_fi_research_manuscript_v1/sources/chi_640_64fold_coefficients.json',
 'crypto_fi_research_manuscript_v1/sources/chi_976_64fold_coefficients.json',
 'crypto_fi_research_manuscript_v1/sources/chi_1344_64fold_coefficients.json',
]
for x in extras:
 p=B/x
 if p.exists():sel.add(p)
for p in (B/'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase2').glob('*'):
 if p.suffix in ('.md','.json'):sel.add(p)
# All records actually dereferenced by the unchanged author verifier.
for x in read(B/'crypto_fi_official_profile_correctness/evidence/INPUT_SNAPSHOT.json'):
 p=Path(x['path']);assert p.is_file(),p;sel.add(p)
for x in read(B/'crypto_fi_official_profile_correctness/evidence/SOURCE_PAGES.json'):
 sel.add(Path(x['path']))
 if Path(x['png']).is_file():sel.add(Path(x['png']))
for p in (B/'crypto_fi_official_profile_review/evidence').glob('*'):
 if p.suffix in ('.txt','.png') or 'PREFLIGHT' in p.name:sel.add(p)
seen=set();line_anchors={};directory_links=[]
while True:
 todo=[p for p in sel if p.suffix=='.md' and p not in seen]
 if not todo:break
 for p in todo:
  seen.add(p)
  for m in LINK.finditer(p.read_text(encoding='utf-8-sig')):
   q,fragment,line=abs_local(m[2],p)
   if q is None:continue
   if q.is_file():
    assert q.is_relative_to(B),q
    sel.add(q)
    if line:line_anchors.setdefault(q,set()).add(line)
   elif q.is_dir():directory_links.append((p,q))
   else:raise ValueError(('missing local Markdown dependency',p,m[2]))

O.mkdir(exist_ok=True)
assert not (O/'MANIFEST.json').exists(),'Refuse to overwrite an already sealed package'
entries=[]
for p in sorted(sel):
 dst=O/'frozen'/rel(p);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
 entries.append(dict(original_path=str(p),relative_origin=rel(p),frozen='frozen/'+rel(p),source_bytes=p.stat().st_size,source_sha256=sha(p),frozen_sha256=sha(dst),historical_bytes_unchanged=True))
lookup={str(p).casefold():p for p in sel}
conversions=[]
for p in sorted(sel):
 if p.suffix not in ('.md','.json'):continue
 dst=O/'reading'/rel(p);dst.parent.mkdir(parents=True,exist_ok=True)
 original=p.read_text(encoding='utf-8-sig');changes=[]
 if p.suffix=='.md':
  def convert(m):
   q,fragment,line=abs_local(m[2],p)
   if q is None:return m[0]
   assert q in sel or q.is_dir(),q
   target=O/('reading' if q.suffix=='.md' else 'frozen')/rel(q)
   value=os.path.relpath(target,dst.parent).replace('\\','/')
   if line:value+='#source-line-'+str(line)
   elif fragment:value+='#'+fragment
   changes.append(dict(old=m[2],new=value))
   return '['+m[1]+']('+value+')'
  body=LINK.sub(convert,original)
  # Exact inverse substitution proves every original character outside link destinations is retained.
  restored=body
  for c in reversed(changes):restored=restored.replace(']('+c['new']+')',']('+c['old']+')',1)
  # A per-token transformation invariant avoids ambiguity from repeated link destinations.
  invariant=LINK.sub(lambda m:'['+m[1]+'](<DEST>)',original)==LINK.sub(lambda m:'['+m[1]+'](<DEST>)',body)
  assert invariant,p
  if p in line_anchors:
   lines=body.splitlines(keepends=True)
   for n in sorted(line_anchors[p],reverse=True):lines.insert(n-1,'<a id="source-line-'+str(n)+'"></a>\n')
   body=''.join(lines)
  back=os.path.relpath(O/'frozen'/rel(p),dst.parent).replace('\\','/')
  header='> 可移交阅读副本。数学正文、章节和式号沿用冻结原件；仅转换链接、添加行定位锚点及本说明。[冻结原件]('+back+')。历史命令按来源记录保留；本包公开重放入口为根目录 REPLAY.md。\n\n'
  dst.write_text(header+body,encoding='utf-8')
  scope='Link destinations, optional source-line anchors, and a clearly separated portability preface only'
 else:
  x=json.loads(original)
  def cv(v,jp=''):
   if isinstance(v,dict):return {k:cv(a,jp+'/'+str(k).replace('~','~0').replace('/','~1')) for k,a in v.items()}
   if isinstance(v,list):return [cv(a,jp+'/'+str(i)) for i,a in enumerate(v)]
   if isinstance(v,str):
    key=v.replace('/','\\').casefold()
    if key in lookup:
     q=lookup[key];new=os.path.relpath(O/'frozen'/rel(q),dst.parent).replace('\\','/')
     changes.append(dict(json_pointer=jp,old=v,new=new));return new
   return v
  transformed=cv(x);restored=json.loads(json.dumps(transformed))
  for c in changes:
   node=restored;parts=c['json_pointer'].split('/')[1:]
   parts=[v.replace('~1','/').replace('~0','~') for v in parts]
   for a in parts[:-1]:node=node[int(a)] if isinstance(node,list) else node[a]
   if isinstance(node,list):node[int(parts[-1])]=c['old']
   else:node[parts[-1]]=c['old']
  invariant=restored==x;assert invariant,p;dump(dst,transformed)
  scope='Exact full-string local paths to carried frozen files only; numerical and all other JSON values preserved'
 conversions.append(dict(source='frozen/'+rel(p),reading='reading/'+rel(p),source_sha256=sha(p),reading_sha256=sha(dst),change_scope=scope,serialization='UTF-8 without BOM; universal newline normalization on read, Windows CRLF on write. JSON reserialized with ensure_ascii=False, indent=2 and final newline.',source_utf8_BOM=p.read_bytes().startswith(b'\xef\xbb\xbf'),source_CRLF_count=p.read_bytes().count(b'\r\n'),changes=changes,source_line_anchors=sorted(line_anchors.get(p,[])),mathematical_content_invariant=invariant,check='Markdown complete non-destination text equality after newline normalization; JSON exact inverse path substitution and whole-object equality'))
for e in entries:
 if (O/'reading'/e['relative_origin']).is_file():e['reading']='reading/'+e['relative_origin']
dump(O/'provenance/PATH_MAP.json',dict(schema='fi-external-review/path-map/1',entries=entries,archival_absolute_strings='Embedded historical paths without a carried target remain provenance identifiers. They are outside the public replay dependency set; their original records remain frozen.',directory_links=[dict(source=rel(p),directory=rel(q)) for p,q in directory_links]))
dump(O/'provenance/READING_TRANSFORMATIONS.json',dict(schema='fi-external-review/reading-transformations/1',all_mathematical_content_invariants_passed=all(x['mathematical_content_invariant'] for x in conversions),conversions=conversions))

# Three small path-only adapters. Everything else runs byte-identical scalar copies.
adapters=[
 ('crypto_fi_official_profile_review/evidence/recompute_review.py',[("from pathlib import Path","from pathlib import Path\nimport os"),("SOURCE=Path('D:/毕业设计/crypto_fi_official_profile_correctness/OFFICIAL_PROFILE_CERTIFICATES.json')","SOURCE=Path(os.environ['FRODO_FI_SANDBOX'])/'crypto_fi_official_profile_correctness/OFFICIAL_PROFILE_CERTIFICATES.json'"),("Path('D:/毕业设计/crypto_fi_640_fixed_A_correctness/FINITE_CERTIFICATES.json')","(Path(os.environ['FRODO_FI_SANDBOX'])/'crypto_fi_640_fixed_A_correctness/FINITE_CERTIFICATES.json')")]),
 ('crypto_fi_official_profile_review/evidence/verify_historical_relations.py',[("from pathlib import Path","from pathlib import Path\nimport os"),("B=Path('D:/毕业设计')","B=Path(os.environ['FRODO_FI_SANDBOX'])")]),
 ('crypto_fi_640_probability_review/review_01a1c4ed/evidence/recompute_probability_chain.py',[("from pathlib import Path","from pathlib import Path\nimport os"),("BASE=Path(r'D:\\毕业设计')","BASE=Path(os.environ['FRODO_FI_SANDBOX'])")]),
]
adapter_records=[]
for name,replacements in adapters:
 src=O/'frozen'/name;text=src.read_text(encoding='utf-8');after=text
 for a,b in replacements:assert after.count(a)==1,(name,a);after=after.replace(a,b)
 dst=O/'replay/adapted'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(after,encoding='utf-8')
 diff=''.join(difflib.unified_diff(text.splitlines(True),after.splitlines(True),fromfile='frozen/'+name,tofile='replay/adapted/'+name))
 diffname='provenance/script_diffs/'+name.replace('/','__')+'.diff';write(diffname,diff)
 adapter_records.append(dict(source='frozen/'+name,source_sha256=sha(src),adapted='replay/adapted/'+name,adapted_sha256=sha(dst),diff=diffname,replacements=[dict(before=a,after=b) for a,b in replacements],scope='Import os and root/path expressions only, plus Windows CRLF serialization. All remaining scalar mathematical statements are identical after newline normalization.'))
dump(O/'provenance/SCRIPT_ADAPTATIONS.json',dict(schema='fi-external-review/script-adaptations/1',adapters=adapter_records,unchanged_scripts=['crypto_fi_official_profile_correctness/evidence/compute_profile_certificates.py','crypto_fi_official_profile_correctness/evidence/verify_profile_certificates.py','crypto_fi_640_fixed_A_review/evidence/recompute_certificates.py','crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/math_verify.py'],runtime_metadata_rewrites=['INPUT_SNAPSHOT.json: path fields rebased to copied sandbox files, hashes unchanged','SOURCE_PAGES.json: path/png fields rebased when carried, hashes unchanged'],candidate_mechanism_implementations=0))
for p in W.glob('*PREFLIGHT.json'):
 dst=O/'provenance'/p.name;dst.write_bytes(p.read_bytes())
for p in W.glob('*EXTRACT.txt'):
 dst=O/'provenance'/p.name;dst.write_bytes(p.read_bytes())
dump(O/'provenance/REVIEW_SOURCE_REGISTRY.json',matrix['source_registry'])
# Capture entry-stage source state. Rechecked at final seal.
dump(O/'provenance/HISTORICAL_INPUT_FINGERPRINTS.json',dict(files=[dict(path=e['original_path'],sha256=e['source_sha256'],bytes=e['source_bytes']) for e in entries],scope='All actually carried historical files, including v3; initial fingerprint at package assembly'))
print(json.dumps(dict(status='ASSEMBLED',historical_files=len(entries),reading_copies=len(conversions),bytes=sum(p.stat().st_size for p in O.rglob('*') if p.is_file())),ensure_ascii=False))
