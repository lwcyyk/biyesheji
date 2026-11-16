from pathlib import Path
import os, json, csv, hashlib, zipfile, collections, re
from lxml import etree as E
ROOT=Path(r'D:\毕业设计'); OUT=ROOT/'当前方案双报告_2026-11-03'; WORK=OUT/'工作底稿'; WORK.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''): h.update(b)
 return h.hexdigest()
def cat(p):
 s=p.as_posix().lower(); parts=set(p.parts)
 if re.search(r'(^|/)(\.env[^/]*|id_rsa|id_ed25519|credentials[^/]*|secrets?[^/]*|private[^/]*\.key)$',s) or p.suffix.lower() in ['.pem','.key','.pfx']: return '潜在秘密 仅元数据'
 if any(x in s for x in ['/vendor/','/node_modules/','/.deps/','/.runtime/','/.venv/','/mp-spdz/','/venv/']):return '第三方或运行环境'
 if '/.git/' in s or '/__pycache__/' in s or p.suffix in ['.pyc','.o','.exe','.bc']: return '缓存或构建产物'
 if p.suffix.lower() in ['.zip','.7z','.tar','.gz']:return '历史压缩包'
 if '/working/' in s or '/工作文件/' in s or '/qa/' in s or '/render' in s:return '派生工作文件与版面核验'
 if p.suffix.lower() in ['.docx','.md','.pdf','.bib']:return '研究文档与文献'
 if p.suffix.lower() in ['.py','.mpc','.sh','.ps1','.toml','.ts','.js']:return '源码与脚本'
 if any(x in s for x in ['/results/','/runs/','/logs/','/snapshots/','/证据/']) or p.suffix.lower() in ['.json','.jsonl','.csv','.log']:return '证据结果或配置'
 return '附件或其他'
rows=[]; errors=[]; archives=[]; docs=[]
for base, dirs, files in os.walk(ROOT,followlinks=False):
 dirs[:]=[d for d in dirs if (Path(base)/d)!=OUT and not (Path(base)/d).is_symlink()]
 for fn in files:
  p=Path(base)/fn; rel=p.relative_to(ROOT); c=cat(rel)
  try:
   st=p.stat(); digest='' if c=='潜在秘密 仅元数据' else sha(p)
   rows.append({'path':str(rel),'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'category':c,'sha256':digest,'read_scope':'索引与哈希；正文另记'})
   if p.suffix.lower()=='.zip':
    try:
     with zipfile.ZipFile(p) as z:
      for i in z.infolist():archives.append({'archive':str(rel),'member':i.filename,'bytes':i.file_size,'crc32':f'{i.CRC:08x}','encrypted':bool(i.flag_bits&1)})
    except Exception as e:errors.append({'path':str(rel),'error':str(e)})
   if p.suffix.lower()=='.docx' and c=='研究文档与文献':docs.append(p)
  except Exception as e:errors.append({'path':str(rel),'error':str(e)})
def write_csv(path,rs):
 if not rs:return
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
write_csv(OUT/'资料索引与来源哈希清单.csv',rows);write_csv(OUT/'历史压缩包成员索引.csv',archives)
groups=collections.defaultdict(list)
for r in rows:
 if r['sha256']:groups[r['sha256']].append(r['path'])
(WORK/'重复内容组.json').write_text(json.dumps({k:v for k,v in groups.items() if len(v)>1},ensure_ascii=False,indent=2),encoding='utf-8')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
ex=[]
for n,p in enumerate(docs,1):
 with zipfile.ZipFile(p) as z:
  root=E.fromstring(z.read('word/document.xml')); lines=[]
  for j,par in enumerate(root.xpath('//w:body//w:p',namespaces=ns),1):
   t=''.join(par.xpath('.//w:t/text()|.//m:t/text()',namespaces=ns))
   if t.strip(): lines.append(f'P{j:04d} '+t)
  for extra in ['word/footnotes.xml','word/endnotes.xml']:
   if extra in z.namelist():lines.append(extra+'\n'+''.join(E.fromstring(z.read(extra)).xpath('//w:t/text()',namespaces=ns)))
  name=f'D{n:03d}_{p.stem}.txt'; (WORK/name).write_text('\n'.join(lines),encoding='utf-8')
  ex.append({'id':f'D{n:03d}','source':str(p.relative_to(ROOT)),'extraction':name,'paragraphs':len(lines),'tables':len(root.xpath('//w:tbl',namespaces=ns)),'omml':len(root.xpath('//m:oMath',namespaces=ns)),'objects':len(root.xpath('//w:object',namespaces=ns)),'images':len(root.xpath('//w:drawing',namespaces=ns)),'characters':sum(map(len,lines))})
write_csv(WORK/'docx提取目录.csv',ex)
summary={'file_count':len(rows),'bytes':sum(r['bytes'] for r in rows),'categories':dict(collections.Counter(r['category'] for r in rows)),'docx':ex,'archives':len(set(r['archive'] for r in archives)),'archive_members':len(archives),'errors':errors}
(WORK/'索引摘要.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
