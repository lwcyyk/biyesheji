"""Build a new static-only namespace; never touch historical source/runtime."""
from pathlib import Path
import json
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\pf01')
S=Path(__file__).resolve().parent/'SOURCE_BEFORE'
for p in sorted(S.rglob('*')):
    if not p.is_file():continue
    raw=p.read_bytes()
    for old,new in [('PreT0Recovery-static-1/r3','PTA-PhaseFinalizer-static-1/r1'),('PreT0Recovery-static-1','PTA-PhaseFinalizer-static-1'),
      ('DCL-R6-PreT0-Fix/authorization/batch11-r5','DCL-R6-PTA-PhaseFinalizer-Fix/authorization/batch12-r1'),
      ('pt01','pf01'),('batch11','batch12'),('BATCH11','BATCH12')]:raw=raw.replace(old.encode('utf-8'),new.encode('utf-8'))
    dest=W/p.relative_to(S).as_posix().replace('dclr6batch11.slice','dclr6batch12.slice')
    dest.write_bytes(raw)
identity=json.loads((W/'inputs/batch_identity.json').read_bytes())
assert identity['host_control'].endswith('DCL-R6-PTA-PhaseFinalizer-Fix/authorization/batch12-r1')
print('Static namespace pf01/batch12-r1 prepared; native entities uncreated')
