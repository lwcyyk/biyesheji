"""Targeted primary-source retrieval; not an automated novelty certification."""
import bootstrap
import urllib.request,json,hashlib
from pathlib import Path
SOURCES=[
 ('value_equivalence','https://arxiv.org/abs/2011.03506'),
 ('lumping','https://proceedings.neurips.cc/paper/2021/hash/ae3f4c649fb55c2ee3ef4d1abdb79ce5-Abstract.html'),
 ('drd','https://proceedings.mlr.press/v33/javdani14.html'),
 ('multi_cost','https://proceedings.mlr.press/v286/bork25a.html'),
 ('lbbd2025','https://link.springer.com/article/10.1007/s10601-025-09382-1'),
 ('cegar','https://www.cs.cmu.edu/~emc/papers/Books%20and%20Edited%20Volumes/Counterexample-Guided%20Abstraction%20Refinement.pdf'),
 ('incremental_z3','https://microsoft.github.io/z3guide/docs/logic/basiccommands/')]
def main():
    out=bootstrap.ROOT/'literature';out.mkdir(exist_ok=True);records=[]
    for name,url in SOURCES:
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 research source verification'})
            with urllib.request.urlopen(req,timeout=15) as res:data=res.read();ct=res.headers.get('Content-Type','')
            path=out/(name+('.pdf' if 'pdf' in ct else '.html'));path.write_bytes(data)
            records.append({'id':name,'url':url,'status':'RETRIEVED_NOT_YET_READ','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'file':path.name})
            print(name,len(data),flush=True)
        except Exception as e:records.append({'id':name,'url':url,'status':'UNAVAILABLE','reason':str(e)});print(name,type(e).__name__,flush=True)
    (out/'retrieval.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
