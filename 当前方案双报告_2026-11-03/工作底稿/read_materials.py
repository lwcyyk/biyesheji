from pathlib import Path
import csv,json,re,sys
W=Path(__file__).parent
if len(sys.argv)==1:
 seen={}; stats=[]
 for f in sorted(W.glob('D*.txt')):
  lines=[];duplicate=[]
  for s in f.read_text(encoding='utf-8').splitlines():
   text=re.sub(r'^P\d+ ','',s);key=re.sub(r'\s+','',text)
   if not key:continue
   if key in seen:duplicate.append({'paragraph':s.split(' ',1)[0],'same_as':seen[key]});continue
   seen[key]=f.stem[:4]+':'+s.split(' ',1)[0];lines.append(s)
  (W/(f.stem+'.unique')).write_text('\n'.join(lines),encoding='utf-8')
  stats.append({'id':f.stem[:4],'unique_chars':sum(map(len,lines)),'duplicate_paragraphs':len(duplicate),'map':duplicate})
 (W/'去重阅读映射.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
 print([(x['id'],x['unique_chars'],x['duplicate_paragraphs']) for x in stats])
else:
 f=next(W.glob(sys.argv[1]+'*.unique'));a=int(sys.argv[2]);b=int(sys.argv[3]);print(f.read_text(encoding='utf-8')[a:b])
