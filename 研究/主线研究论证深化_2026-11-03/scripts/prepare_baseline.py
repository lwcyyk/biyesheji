from pathlib import Path
import json, hashlib
BASE=Path(__file__).resolve().parents[1]
ROOT=Path('D:/毕业设计'); PROJECT=ROOT/'auth-lifecycle'
target=BASE/'baseline_hashes.json'
if target.exists():raise SystemExit('Baseline already exists; never rebaseline to conceal changes')
files={}
for sub in ['src','tests','scripts','docs','examples','experiments','results']:
 for f in (PROJECT/sub).rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts:files[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
for f in ROOT.glob('*.docx'):files[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
for sub in [ROOT/'实现四阶段',ROOT/'研究/当前与四阶段及密码学融合_2026-11-02',ROOT/'研究/创新性验证与假设驱动研究_2026-11-02']:
 for f in sub.rglob('*'):
  if f.is_file():files[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
BASE.mkdir(exist_ok=True,parents=True)
target.write_text(json.dumps({'scope':'Project excluding .runtime and pycache; original docx and two prior research packages','git_commit':None,'files':files},ensure_ascii=False,indent=2),encoding='utf-8')
print('Preserved baseline files:',len(files))
