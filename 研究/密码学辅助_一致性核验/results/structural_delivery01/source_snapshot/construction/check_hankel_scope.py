"""Reproduce a KNOWN small-characteristic boundary; never claim a new paper flaw."""
import argparse
from pathlib import Path
import sys
import json
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from field import Field
import reference


def main():
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    a = p.parse_args(); out = (ROOT / a.out).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('isolated output')
    out.mkdir(parents=True, exist_ok=False)
    f = Field(4); rows = []
    for k in range(1, 5):
        d = [1] * (k + 2); m = k + 1
        counts = {'unshifted_zero': 0, 'shifted_zero': 0}
        values = []
        for u in range(16):
            determinants = []
            for shift in (0, 1):
                h = [[f.poly(d, f.power(u, r + c + shift)) for c in range(m)] for r in range(m)]
                determinants.append(reference.determinant(h, 4, f.modulus))
            counts['unshifted_zero'] += int(determinants[0] == 0)
            counts['shifted_zero'] += int(determinants[1] == 0)
            values.append({'u': u, 'unshifted': determinants[0], 'shifted': determinants[1]})
        assert counts['unshifted_zero'] == 16
        rows.append({'k': k, 'support_size': len(d), 'residuals': d, 'counts': counts, 'values': values})
    (out / 'counterexamples.json').write_text(json.dumps(rows, indent=2))
    summary = {'pass': True, 'field': 'GF16', 'thresholds': [1, 2, 3, 4],
               'matrix_determinants': 4 * 16 * 2,
               'prior_art': 'Hao, Kaltofen, Zhi, ISSAC 2016, section 4 and appendix 6',
               'doi': '10.1145/2930889.2930924',
               'novelty': 'KNOWN_PHENOMENON_EXCLUDED_FROM_ORIGINAL_CLAIMS',
               'scope': 'portability counterexample; not an attack on an implementation or a claim against an odd-characteristic theorem'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2)); print(json.dumps(summary))


if __name__ == '__main__': main()
