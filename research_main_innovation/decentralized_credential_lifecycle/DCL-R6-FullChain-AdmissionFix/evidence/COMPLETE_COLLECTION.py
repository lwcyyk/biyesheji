"""Resume only the unfinished AST collection with explicit UTF-8."""
from pathlib import Path
import ast,hashlib,json
from datetime import datetime,timezone
O=Path(__file__).resolve().parent.parent;E=O/'evidence';S=E/'FROZEN_RA_ORIGINALS/src'
def put(n,x):
 with(E/n).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
put('COLLECTION_ADMIN_ERROR.json',{'phase':'Host administrative collection only','failure':'PREPARE.py default Windows GBK read_text decoding of UTF-8 source failed before AST slices were written',
 'completed_before_failure':'History baseline, source64 copies, prior references, archive and actual manifest/catalog checks',
 'correction':'This resume reads existing immutable snapshots with explicit UTF-8; no repeated target operations',
 'runtime_tests':0,'source_edits':0,'dynamic_retries':0})
snips={}
for filename,names in {'terminal_evidence.py':['_native_artifact','terminal_policy'],
 'manager_recovery.py':['classify','closure_status']}.items():
 raw=(S/filename).read_bytes();src=raw.decode('utf-8-sig');t=ast.parse(src)
 for n in t.body:
  if isinstance(n,ast.FunctionDef) and n.name in names:snips[n.name]={'file':filename,'line':n.lineno,'source':ast.get_source_segment(src,n),'source_sha256':hashlib.sha256(raw).hexdigest()}
put('REAL_CHECKER_SLICES.json',snips)
catalog=json.loads((E/'EVIDENCE_CATALOG.json').read_bytes());history=json.loads((E/'HISTORY_BASELINE.json').read_bytes())
put('COLLECTION_RESULT.json',{'utc':datetime.now(timezone.utc).isoformat(),'history_files':len(history['files']),
 'source_files':64,'native_rows':233,'admin_rows':249,'catalog_rows':len(catalog['rows']),
 'admin_collection_errors':1,'WSL_calls':0,'dynamic_entries':0})
print(json.dumps({'status':'COLLECTION_COMPLETE_UTF8','history_files':len(history['files']),'catalog_rows':len(catalog['rows'])}))
