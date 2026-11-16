"""New static namespace only; original pf01/batch12 stay frozen."""
from pathlib import Path
W=Path(r'D:\毕业设计\DCL-R6-isolated-verification\tr01');S=Path(__file__).resolve().parent/'SOURCE_BEFORE'
for p in sorted(S.rglob('*')):
    if not p.is_file():continue
    raw=p.read_bytes()
    for old,new in [('DCL-R6-PTA-PhaseFinalizer-Fix/authorization/batch12-r3','DCL-R6-TerminalRead-Fix/authorization/batch13-r1'),
        ('PTA-PhaseFinalizer-static-1/r3','TerminalRead-static-1/r1'),('PTA-PhaseFinalizer-static-1','TerminalRead-static-1'),
        ('pf01','tr01'),('batch12','batch13'),('BATCH12','BATCH13')]:raw=raw.replace(old.encode(),new.encode())
    dest=W/p.relative_to(S).as_posix().replace('dclr6batch12.slice','dclr6batch13.slice');dest.write_bytes(raw)
old=W/'inputs/dclr6batch12.slice'
if old.exists():old.unlink()
print('tr01/batch13-r1 static identity prepared; native calls0')
