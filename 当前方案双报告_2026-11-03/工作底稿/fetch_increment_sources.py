import urllib.request,json,concurrent.futures
from pathlib import Path
from html.parser import HTMLParser
W=Path(__file__).parent
urls=[('R45','https://arxiv.org/abs/2601.07567'),('R46','https://web.njit.edu/~jkliewer/wp/paper/CKH_IT0113.pdf'),('R47','https://arxiv.org/abs/2011.03506')]
class Text(HTMLParser):
 def __init__(self):super().__init__();self.data=[]
 def handle_data(self,d):self.data.append(d)
def get(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 research-source-audit'})
  with urllib.request.urlopen(req,timeout=20) as r:b=r.read(5000000)
  (W/(name+('.pdf' if b.startswith(b'%PDF') else '.html'))).write_bytes(b)
  if b.startswith(b'%PDF'):return {'id':name,'url':url,'bytes':len(b),'status':'PDF取得'}
  parser=Text();parser.feed(b.decode('utf-8','replace'));t='\n'.join(x.strip() for x in parser.data if x.strip());(W/(name+'.txt')).write_text(t,encoding='utf-8')
  pos=t.find('Title:');return {'id':name,'url':url,'bytes':len(b),'status':'HTML取得','excerpt':t[max(0,pos):max(0,pos)+3600]}
 except Exception as e:return {'id':name,'url':url,'status':'UNAVAILABLE','error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:rows=list(ex.map(get,urls))
(W/'增量来源获取.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for x in rows:print(json.dumps(x,ensure_ascii=False))

