from pathlib import Path
import json,hashlib,fitz
from datetime import datetime,timezone
out=Path(r'D:\毕业设计\crypto_branch_monitor\round_007\independent_review_packet\review_output\phase1')
manifest=json.loads((out.parent.parent/'INPUT_MANIFEST.json').read_text(encoding='utf-8-sig'))
selected={'FI_v4':[10,14], 'CANS2024':[7,9], 'IEICE2026':[4,6], 'official_frodo_2021_frozen':[16,25]}
for item in manifest['phase1_allowed_inputs']:
    path=Path(item['path'])
    if path.stem not in selected: continue
    data=json.loads((out/(path.stem+'.preflight.json')).read_text(encoding='utf-8'))
    print(path.name,'preflight',data.get('verdict'),data.get('declared_page_count'))
    doc=fitz.open(path)
    for p in selected[path.stem]:
        target=out/(path.stem+f'.p{p:02}.png')
        doc[p-1].get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(target)
        print(str(target))
for stem, indices in [('official_frodo_2021_frozen',[15,16,25])]:
    pages=json.loads((out/(stem+'.pages.json')).read_text(encoding='utf-8'))
    for i in indices: print('PAGE',i,pages[i-1]['text'])
