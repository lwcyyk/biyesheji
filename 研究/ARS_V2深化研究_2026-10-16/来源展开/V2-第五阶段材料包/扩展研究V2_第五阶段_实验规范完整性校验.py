#!/usr/bin/env python3
# Python >= 3.9; standard library only. This checks design-manifest integrity, NOT protocol security.
import json, sys, pathlib
if len(sys.argv) != 2:
    raise SystemExit('Usage: python check_design.py <manifest.json>')
doc=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
assert doc['execution_status']=='DESIGN_ONLY_NOT_EXECUTED'
cs={c['id'] for c in doc['claims']}
bs=set(doc['baselines'])
seen=set()
for e in doc['experiments']:
    assert e['id'] not in seen, f"duplicate experiment: {e['id']}"
    seen.add(e['id'])
    assert e['phase'] in {'E0','E1','E2','E3','E4'}
    assert set(e['claim']) <= cs, e['id']
    assert set(e['baselines']) <= bs, e['id']
    assert e['trace'] in {'TL1','TL2','TL3','TL4','TL5','TL6','ALL'}
    for k in ('metric','predict_h1','predict_h2','oracle'):
        assert e[k], (e['id'],k)
for c in doc['claims']:
    assert c['experiment'] in seen, c['id']
assert {'B2','B3','B4','B5','W_STAR','P3'} <= bs
print(f"VALID DESIGN SPECIFICATION: {len(cs)} claims; {len(seen)} experiments; {len(bs)} baselines")
print('NOTE: no security experiments were executed or verified.')
