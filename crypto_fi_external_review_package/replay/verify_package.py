"""Verify sealed bytes and all local Markdown links in the portable reading surface."""
from pathlib import Path
import argparse,hashlib,json,re,unicodedata,urllib.parse

P=Path(__file__).resolve().parents[1]
LINK=re.compile(r'(?<!!)\[([^\[\]\n]+)\]\(([^)\n]+)\)')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def slug(t):
 t=t.strip().lower();t=re.sub(r'[^\w\-\s]','',t);return t.replace(' ','-')
def anchors(p):
 text=p.read_text(encoding='utf-8-sig');ids=set(re.findall(r'<a\s+id="([^"]+)"',text));counts={}
 for line in text.splitlines():
  if re.match(r'^#{1,6} ',line):
   key=slug(re.sub(r'^#{1,6} ','',line));n=counts.get(key,0);counts[key]=n+1;ids.add(key+('-'+str(n) if n else ''))
 return ids
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True);args=ap.parse_args();out=Path(args.output).resolve()
 assert not out.is_relative_to(P),'Output must be outside package'
 assert not out.exists(),'Use a new report filename'
 m=json.loads((P/'MANIFEST.json').read_text(encoding='utf-8'));records=m['files']
 assert m['self_exclusion']==['MANIFEST.json']
 actual={f.relative_to(P).as_posix() for f in P.rglob('*') if f.is_file()}
 assert actual-{'MANIFEST.json'}=={r['path'] for r in records}
 for r in records:
  f=P/r['path'];assert f.is_file() and f.stat().st_size==r['bytes'] and sha(f)==r['sha256'],r['path']
 docs=sorted(P.glob('*.md'))+sorted((P/'reading').rglob('*.md'))
 checked=[];externals=[]
 for f in docs:
  for match in LINK.finditer(f.read_text(encoding='utf-8-sig')):
   dest=urllib.parse.unquote(match[2].strip('<>'))
   if re.match(r'^1-\\',dest):continue # display-math ](1-epsilon) factor
   if re.match(r'^[a-z]+://',dest,re.I):externals.append(dict(document=f.relative_to(P).as_posix(),url=dest));continue
   assert not re.match(r'^[A-Za-z]:[/\\]',dest),(f,dest,'absolute link')
   name,sep,fragment=dest.partition('#');target=(f.parent/name).resolve() if name else f
   assert target.is_relative_to(P) and target.exists(),(f,dest,'missing or escaped target')
   if fragment and target.suffix=='.md':assert fragment in anchors(target),(f,dest,'unresolved anchor')
   checked.append(dict(document=f.relative_to(P).as_posix(),target=dest,resolved=target.relative_to(P).as_posix(),fragment_checked=bool(fragment and target.suffix=='.md')))
 transforms=json.loads((P/'provenance/READING_TRANSFORMATIONS.json').read_text(encoding='utf-8'))
 assert transforms['all_mathematical_content_invariants_passed']
 for item in transforms['conversions']:
  assert sha(P/item['source'])==item['source_sha256'] and sha(P/item['reading'])==item['reading_sha256']
  original=(P/item['source']).read_text(encoding='utf-8-sig')
  portable=(P/item['reading']).read_text(encoding='utf-8-sig')
  if item['source'].endswith('.md'):
   body=portable.split('\n\n',1)[1]
   for n in item['source_line_anchors']:body=body.replace('<a id="source-line-'+str(n)+'"></a>\n','')
   mask=lambda s:LINK.sub(lambda m:'['+m[1]+'](<DEST>)',s)
   assert mask(body)==mask(original),item['reading']
  else:
   obj=json.loads(portable)
   for change in item['changes']:
    node=obj;parts=[x.replace('~1','/').replace('~0','~') for x in change['json_pointer'].split('/')[1:]]
    for key in parts[:-1]:node=node[int(key)] if isinstance(node,list) else node[key]
    key=int(parts[-1]) if isinstance(node,list) else parts[-1]
    assert node[key]==change['new'];node[key]=change['old']
   assert obj==json.loads(original),item['reading']
 adaptations=json.loads((P/'provenance/SCRIPT_ADAPTATIONS.json').read_text(encoding='utf-8'))
 for item in adaptations['adapters']:
  assert sha(P/item['source'])==item['source_sha256'] and sha(P/item['adapted'])==item['adapted_sha256']
  restored=(P/item['adapted']).read_text(encoding='utf-8')
  for change in reversed(item['replacements']):
   assert restored.count(change['after'])==1
   restored=restored.replace(change['after'],change['before'])
  assert restored==(P/item['source']).read_text(encoding='utf-8'),item['adapted']
 pathmap=json.loads((P/'provenance/PATH_MAP.json').read_text(encoding='utf-8'))
 for e in pathmap['entries']:assert sha(P/e['frozen'])==e['source_sha256']
 report=dict(schema='fi-external-review/package-verification/1',status='PASS',root=str(P),manifest_sha256=sha(P/'MANIFEST.json'),manifest_file_count=len(records),all_payload_hashes_match=True,reading_document_count=len(docs),local_link_count=len(checked),all_local_links_resolve_inside_package=True,local_links=checked,external_links_not_required_for_offline_replay=externals,reading_transformations=len(transforms['conversions']),original_source_file_count=len(pathmap['entries']),all_source_copy_hashes_match=True)
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if not isinstance(v,list)},ensure_ascii=False))
if __name__=='__main__':main()
