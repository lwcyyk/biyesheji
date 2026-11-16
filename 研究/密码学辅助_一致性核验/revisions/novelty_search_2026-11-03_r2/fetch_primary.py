"""Fetch fixed public research sources; no uploads or author contact."""
from pathlib import Path
import hashlib
import json
import re
import urllib.request

BASE=Path(__file__).resolve().parent
SOURCES=[('ottow','https://www.lirmm.fr/lucas-ottow/'),
         ('stanley','https://static.ias.edu/pcmi/2004/program/Stanleynotes.pdf'),
         ('lowrank2026','https://arxiv.org/html/2609.18876v1')]


def main():
    folder=BASE/'sources';folder.mkdir(exist_ok=False);rows=[]
    for name,url in SOURCES:
        row={'id':name,'url':url}
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(request,timeout=15) as reply: data=reply.read();final=reply.url
            suffix='.pdf' if data.startswith(b'%PDF') else '.html'
            with (folder/(name+suffix)).open('xb') as out:out.write(data)
            row.update(status='FETCHED_NOT_FULL_READ',sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),final_url=final)
            if name=='ottow':row['relevant_links']=[x for x in re.findall(r'href=[\"\x27]([^\"\x27]+)',data.decode(errors='replace')) if any(y in x for y in ('cic.iacr','eprint','dagstuhl','doi.org'))]
        except Exception as error:row.update(status='UNAVAILABLE',error=str(error))
        rows.append(row)
    (folder/'access_log.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))


if __name__=='__main__':main()
