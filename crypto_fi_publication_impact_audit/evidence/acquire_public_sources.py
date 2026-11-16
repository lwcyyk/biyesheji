from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone,timedelta
import requests,hashlib,json,tarfile,sys
sys.stdout.reconfigure(encoding='utf-8')
OUT=Path(__file__).resolve().parents[1]
jobs=[('publisher_current.pdf','https://fi.episciences.org/17222/pdf')]
for v in range(1,5):
    jobs += [(f'arxiv_v{v}.pdf',f'https://arxiv.org/pdf/2410.03948v{v}'),(f'arxiv_v{v}_source.tar',f'https://arxiv.org/src/2410.03948v{v}')]
records=[]
def acquire(job):
    name,url=job
    row=dict(name=name,url=url,retrieved_at_asia_shanghai=datetime.now(timezone(timedelta(hours=8))).isoformat())
    try:
        r=requests.get(url,timeout=25,headers={'User-Agent':'Mozilla/5.0 (academic public-source verification)'})
        row.update(status=r.status_code,final_url=r.url,content_type=r.headers.get('Content-Type'),bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest())
        p=OUT/'sources'/name
        if r.ok and (r.content.startswith(b'%PDF') if name.endswith('.pdf') else 'text/html' not in r.headers.get('Content-Type','')):
            p.write_bytes(r.content);row['saved_path']=str(p)
            if name.endswith('.tar'):
                try:
                    with tarfile.open(p) as t:
                        members=[dict(name=m.name,size=m.size,type=str(m.type)) for m in t.getmembers()]
                        row['archive_members']=members
                        # Source audit only: extract data bytes from regular TeX/Bib/README files to new paths.
                        extracted=[]
                        for m in t.getmembers():
                            if m.isfile() and Path(m.name).suffix.lower() in ['.tex','.bib','.json','.txt','.md']:
                                target=(OUT/'sources'/name.removesuffix('.tar')/m.name).resolve()
                                root=(OUT/'sources'/name.removesuffix('.tar')).resolve()
                                if not target.is_relative_to(root):raise ValueError('unsafe archive member')
                                target.parent.mkdir(parents=True,exist_ok=True)
                                b=t.extractfile(m).read();target.write_bytes(b)
                                extracted.append(dict(path=str(target),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
                        row['text_files_extracted']=extracted
                except (tarfile.TarError,ValueError) as e:row['archive_error']=str(e)
        else:row['body_prefix']=r.text[:160]
    except Exception as e:row['error']=type(e).__name__+': '+str(e)
    return row
with ThreadPoolExecutor(max_workers=4) as pool:
    for f in as_completed([pool.submit(acquire,j) for j in jobs]):
        row=f.result();records.append(row)
        print(json.dumps({k:v for k,v in row.items() if k not in ['archive_members','text_files_extracted']},ensure_ascii=False),flush=True)
        (OUT/'evidence/PUBLIC_ACQUISITION.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),'utf-8')
