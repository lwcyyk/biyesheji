from pathlib import Path
import hashlib, json

BASE = Path(r'D:\毕业设计')
OUT = BASE/'crypto_fi_640_probability_review'/'review_01a1c4ed'
OUT.mkdir(parents=True, exist_ok=True)
(OUT/'evidence').mkdir(exist_ok=True)
records = []
for dirname in ('crypto_fi_640_correctness_audit', 'crypto_fi_640_joint_correctness', 'crypto_fi_640_probability_review'):
    for p in sorted((BASE/dirname).rglob('*')):
        if not p.is_file() or OUT in p.parents:
            continue
        raw = p.read_bytes()
        records.append(dict(path=str(p), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), scope='historical_read_only'))
for name in ('CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','REVIEW_RESPONSE_AND_READINESS.md','MANIFEST.json'):
    p=BASE/'crypto_fi_research_manuscript_v1'/name
    raw=p.read_bytes()
    records.append(dict(path=str(p), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), scope='manuscript_read_only'))
(OUT/'evidence'/'INPUT_SNAPSHOT.json').write_text(json.dumps(dict(schema='fi640-review/input-snapshot/2',records=records),ensure_ascii=False,indent=2),encoding='utf-8')
print('Frozen historical files:', len(records))
