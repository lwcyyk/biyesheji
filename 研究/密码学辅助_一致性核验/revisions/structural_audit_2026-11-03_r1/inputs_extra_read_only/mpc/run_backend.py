"""Local two-process, live-preprocessing MP-SPDZ laboratory runner.

No fake/file preprocessing; the pinned official binary is used. Its build flags
are not independently attested by this runner. Synthetic inputs only.
All private fixture files are local and intentionally not claimed confidential
from this harness. Never use this runner for production credentials.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'vendor/mp-spdz-0.4.4'


def capture(command, cwd, path, timeout=180):
    start = time.monotonic()
    with path.open('w') as out:
        result = subprocess.run(command, cwd=cwd, stdout=out,
                                stderr=subprocess.STDOUT, timeout=timeout)
    return {'command': list(map(str, command)), 'exit_code': result.returncode,
            'elapsed_seconds': time.monotonic() - start}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--source', default='mpc/smoke.mpc')
    p.add_argument('--fixture')
    p.add_argument('--compiler-arg', action='append', default=[])
    p.add_argument('--timeout', type=int, default=180)
    # Release's auxiliary binary-field machinery rejects -S 128. Do not claim
    # that a GF(2^128) data field supplies 128-bit end-to-end statistical security.
    p.add_argument('--security', type=int, default=40)
    args = p.parse_args()
    out = (ROOT / args.out).resolve()
    if not out.is_relative_to(ROOT) or out == ROOT:
        raise ValueError('output must be below isolated research root')
    out.mkdir(parents=True, exist_ok=False)
    for sub in ('Programs/Source', 'Programs/Bytecode', 'Programs/Schedules', 'Player-Data'):
        (out / sub).mkdir(parents=True, exist_ok=True)
    source = (ROOT / args.source).resolve()
    program_name = '-'.join([source.stem] + args.compiler_arg)
    dest = out / 'Programs/Source' / source.name
    shutil.copyfile(source, dest)
    fixture = json.loads((ROOT / args.fixture).read_text()) if args.fixture else {
        'party_inputs': [[1 << 127], [2]], 'kind': 'synthetic_smoke'}
    for party, values in enumerate(fixture['party_inputs']):
        (out / f'Player-Data/Input-P{party}-0').write_text(
            ' '.join(format(x, 'x') for x in values) + '\n')
    binary = BACKEND / 'bin/Linux-adx/mascot-party.x'
    manifest = {
        'kind': 'LOCAL_TWO_PROCESS_LIVE_MPC_DEVELOPMENT_TEST',
        'backend': json.loads((ROOT / 'vendor/backend_release.json').read_text()),
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
        'fixture_kind': fixture.get('kind'), 'phases': [],
        'limitations': ['one physical host', 'synthetic inputs known to harness',
                       'honest execution of an active-security backend',
                       'no TLS residual-source binding or novelty validation']}
    manifest['phases'].append(capture(
        ['bash', str(BACKEND / 'Scripts/setup-ssl.sh'), '2'], out, out / 'ssl.log'))
    if manifest['phases'][-1]['exit_code']:
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2)); return 1
    manifest['phases'].append(capture(
        ['python3', str(BACKEND / 'compile.py'), '--galoissize', '128',
         '--preserve-mem-order', source.stem] + args.compiler_arg,
        out, out / 'compile.log', args.timeout))
    if manifest['phases'][-1]['exit_code']:
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2)); return 1
    # Two adjacent unused loopback ports, used by the framework's own coordination.
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0)); port = probe.getsockname()[1]
    processes = []; handles = []; start = time.monotonic()
    try:
        for party in (0, 1):
            cmd = [str(binary), '-N', '2', '-p', str(party), '-h', '127.0.0.1',
                   '-pn', str(port), '-lg2', '128', '-e', '-v', '-b', '1000',
                   '-S', str(args.security), '-OF', '.', program_name]
            handle = (out / f'party{party}.log').open('w'); handles.append(handle)
            process = subprocess.Popen(cmd, cwd=out, stdout=handle, stderr=subprocess.STDOUT)
            processes.append(process)
            manifest['phases'].append({'command': cmd, 'party': party})
        for i, process in enumerate(processes):
            manifest['phases'][i + 2]['exit_code'] = process.wait(
                timeout=max(1, args.timeout - (time.monotonic() - start)))
    except subprocess.TimeoutExpired:
        manifest['timeout'] = True
        for process in processes:
            if process.poll() is None: process.kill()
        for process in processes: process.wait()
    finally:
        for handle in handles: handle.close()
        manifest['runtime_wall_seconds'] = time.monotonic() - start
        manifest['success'] = not manifest.get('timeout') and all(
            x.get('exit_code') == 0 for x in manifest['phases'])
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'out': str(out), 'success': manifest['success'],
                      'runtime_wall_seconds': manifest['runtime_wall_seconds']}), flush=True)
    return 0 if manifest['success'] else 1


if __name__ == '__main__': raise SystemExit(main())
