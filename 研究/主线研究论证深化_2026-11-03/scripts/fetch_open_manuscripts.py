from pathlib import Path
import urllib.request,json,hashlib
BASE=Path(__file__).resolve().parents[1]/'working/papers'
BASE.mkdir(parents=True,exist_ok=True)
sources={
 'RAG':'https://researchportal.hw.ac.uk/files/173709309/Verifying_Account_Ecosystems_AAM.pdf',
 'Tactics':'https://www.research.ed.ac.uk/files/478371898/ArnaboldiEtalESORICS2023TacticsForAccountAccessGraphs.pdf'}
log=[]
for key,url in sources.items():
 row={'id':key,'url':url,'method':'ordinary public URL retrieval, no credentials, no access-control bypass'}
 try:
  with urllib.request.urlopen(url,timeout=20) as r:data=r.read();row['http_status']=r.status
  if not data.startswith(b'%PDF'):raise ValueError('Not a PDF')
  path=BASE/(key+'.pdf');path.write_bytes(data)
  row.update(status='RETRIEVED',path=str(path),sha256=hashlib.sha256(data).hexdigest())
 except Exception as e:row.update(status='UNAVAILABLE',reason=str(e))
 log.append(row)
(BASE/'retrieval.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(log,ensure_ascii=False,indent=2))
