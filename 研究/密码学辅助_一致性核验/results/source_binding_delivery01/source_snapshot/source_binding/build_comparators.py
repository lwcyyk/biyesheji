"""Attach the identical native AES/GCM computation to the existing baselines.

This keeps earlier generated source immutable. No comparator receives extra
interfaces or oracle values. All party inputs/public records are byte-identical.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    generated = (ROOT / 'source_binding/generated01/bind_gcm.mpc').read_text()
    rowspace = (ROOT / 'mpc/rowspace2.mpc').read_text()
    prefix = rowspace.split('@for_range(batches)\ndef batch(index):\n')[0]
    assert generated.startswith(prefix)
    body = generated[len(prefix):]
    aes_body, old_diagnostic = body.split('\ndef diagnose(index, values):\n', 1)
    tail = old_diagnostic[old_diagnostic.index('\n@for_range(len(PUBLIC_CASES))'):]
    baseline = (ROOT / 'mpc/locate2.mpc').read_text()
    prefix2 = baseline.split('@for_range(batches)\ndef batch(batch_index):\n')[0]
    tree = ast.parse(baseline)
    batch = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'batch')
    assert isinstance(batch.body[0], ast.Assign) and batch.body[0].targets[0].id == 'values'
    batch.name = 'diagnose'; batch.args.args.append(ast.arg(arg='values'))
    batch.decorator_list = []; batch.body = batch.body[1:]
    ast.fix_missing_locations(batch)
    diagnostic = ast.unparse(batch)
    manifest = {'fixture_sha256': hashlib.sha256((ROOT / 'source_binding/generated01/fixture.json').read_bytes()).hexdigest(),
                'baseline_source_sha256': hashlib.sha256(baseline.encode()).hexdigest(), 'programs': {}}
    for method in ('moments', 'coordinate'):
        original_line = "mode = program.args[3] if len(program.args) > 3 else 'moments'"
        assert original_line in prefix2
        new_prefix = prefix2.replace(original_line, 'mode = ' + repr(method))
        result = new_prefix + '\nfrom Compiler.library import runtime_error_if\n' + aes_body + '\n' + diagnostic + '\n' + tail
        filename = f'binding_{method}.mpc'
        (out / filename).write_text(result)
        manifest['programs'][filename] = hashlib.sha256(result.encode()).hexdigest()
    shutil.copyfile(ROOT / 'source_binding/generated01/fixture.json', out / 'fixture.json')
    (out / 'build.json').write_text(json.dumps(manifest, indent=2)); print(json.dumps(manifest))


if __name__ == '__main__': main()
