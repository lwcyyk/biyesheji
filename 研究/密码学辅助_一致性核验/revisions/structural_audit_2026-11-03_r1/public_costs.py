"""Small public compile/check cost observations, not a statistical benchmark."""
import argparse
import json
from pathlib import Path
import time
import tracemalloc
from compiler import components, find_conflict
from checker import check
from gate_reference import build
from profiles import record_profiles

REV = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); args = p.parse_args()
    out = (REV / args.out).resolve()
    if not out.is_relative_to(REV): raise ValueError('revision output only')
    rows = []
    for profile, generator in zip(record_profiles(), (find_conflict, components)):
        for repetition in range(5):
            tracemalloc.start(); start = time.perf_counter(); certificate = generator(profile)
            elapsed_compile = time.perf_counter() - start; _, compile_peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
            tracemalloc.start(); start = time.perf_counter(); checked = check(certificate, profile)
            elapsed_check = time.perf_counter() - start; _, check_peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
            assert checked['verification_status'] == 'VERIFIED'
            rows.append({'profile': profile['profile_id'], 'repetition': repetition,
                         'compile_seconds': elapsed_compile, 'check_seconds': elapsed_check,
                         'compile_python_traced_peak_bytes': compile_peak, 'check_python_traced_peak_bytes': check_peak,
                         'rank_checks': checked['rank_checks'],
                         'certificate_serialized_bytes': len(json.dumps(certificate, sort_keys=True).encode())})
    value = {'scope': '5 observations per n4 public profile; tracemalloc overhead included, no superiority inference',
             'costs': rows, 'L0_gate_metrics': [dict(profile=p['profile_id'], **build(p)['metrics']) for p in record_profiles()]}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x') as stream: json.dump(value, stream, indent=2)
    print(json.dumps({'observations': len(rows), 'output': str(out)}))


if __name__ == '__main__': main()
