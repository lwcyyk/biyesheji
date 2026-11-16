"""Check outputs against independently derived supports, not runner exit alone."""
import argparse
import hashlib
import json
from pathlib import Path
import re

REV = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True); p.add_argument('--suffix', default='')
    args = p.parse_args(); target = (REV / args.out).resolve()
    if not target.is_relative_to(REV): raise ValueError('revision output only')
    fixture = json.loads((REV / 'gate_mpc/fixture.json').read_text())
    rows = []
    for method in ('gate', 'release'):
        for profile in ('original', 'restricted'):
            if not re.fullmatch(r'[A-Za-z0-9_-]*', args.suffix): raise ValueError('invalid result suffix')
            folder = REV / 'results' / (f'{method}_{profile}' + args.suffix)
            manifest = json.loads((folder / 'manifest.json').read_text())
            expected_gates = []; expected_supports = []
            for i, case in enumerate(fixture['cases']):
                support = [j for j, x in enumerate(case['values']) if x]
                # Use direct semantic predicates, not gate family or compiler.
                ok = len(support) <= 2 if profile == 'original' else all(sum(j // 2 == block for j in support) <= 1 for block in (0, 1))
                expected_gates.append((i, int(ok)))
                if ok: expected_supports.append((i, sum(1 << j for j in support)))
                actual_values = [fixture['party_inputs'][0][4*i+j] ^ fixture['party_inputs'][1][4*i+j] for j in range(4)]
                assert actual_values == case['values']
            for party in (0, 1):
                log = (folder / f'party{party}.log').read_text()
                # Framework directs application output to party 0 only.
                if party == 0:
                    gates = [tuple(map(int, m)) for m in re.findall(r'^GATE case=(\d+) accepted=(\d+)$', log, re.M)]
                    supports = [tuple(map(int, m)) for m in re.findall(r'^SUPPORT case=(\d+) packed=(\d+)$', log, re.M)]
                    assert gates == expected_gates, (folder, 'gates', gates)
                    assert supports == (expected_supports if method == 'release' else []), (folder, 'supports', supports)
                    assert log.count('PROTOCOL_DONE') == 1
            assert manifest['success'] and all(x['exit_code'] == 0 for x in manifest['phases'])
            log = (folder / 'party0.log').read_text()
            def metric(pattern, cast=float): return cast(re.search(pattern, log).group(1))
            online = re.search(r'Spent ([\d.]+) seconds \(([\d.]+) MB, (\d+) rounds.*?on the online phase and ([\d.]+) seconds \(([\d.]+) MB, (\d+) rounds', log)
            row = {'method': method, 'profile': profile, 'verified_cases': len(expected_gates),
                   'accepted': sum(x[1] for x in expected_gates), 'rejected': sum(1-x[1] for x in expected_gates),
                   'runtime_wall_seconds': manifest['runtime_wall_seconds'],
                   'backend_time_seconds_including_preprocessing': metric(r'\nTime = ([\d.]+) seconds'),
                   'global_data_sent_MB': metric(r'Global data sent = ([\d.]+) MB'),
                   'party0_rounds_including_preprocessing': metric(r'Data sent = [\d.]+ MB in ~(\d+) rounds', int),
                   'triples': metric(r'\n\s+(\d+)\s+Triples', int),
                   'input_tuples': metric(r'\n\s+(\d+)\s+Input tuples', int),
                   'compile_seconds': manifest['phases'][1]['elapsed_seconds'],
                   'ssl_setup_seconds': manifest['phases'][0]['elapsed_seconds'],
                   'peak_memory_bytes': None, 'peak_memory_status': 'NOT_MEASURED',
                   'failures': 0, 'recovery_experiments': 'NOT_RUN',
                   'source_sha256': manifest['source_sha256'],
                   'raw_logs_sha256': {f'party{j}.log': hashlib.sha256((folder / f'party{j}.log').read_bytes()).hexdigest() for j in (0,1)}}
            if online:
                row['party0_online'] = dict(zip(('seconds','MB','rounds'), (float(online[1]), float(online[2]), int(online[3]))))
                row['party0_preprocessing'] = dict(zip(('seconds','MB','rounds'), (float(online[4]), float(online[5]), int(online[6]))))
            rows.append(row)
    for profile in ('original', 'restricted'):
        pair = [x for x in rows if x['profile'] == profile]
        assert pair[0]['triples'] == pair[1]['triples']
    output = {'pass': True, 'runs': rows, 'extra_support_release_triples': 0,
              'scope': 'honest local execution / fixed fixtures; no malicious security or performance superiority claim',
              'backend_randomness': 'normal live preprocessing; fixed seed only constructs synthetic fixture'}
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x') as stream: json.dump(output, stream, indent=2)
    print(json.dumps(output))


if __name__ == '__main__': main()
