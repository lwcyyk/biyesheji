"""Deterministic review arithmetic and file binding; no cryptographic mechanism."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
import hashlib
import json

ROOT = Path(r'D:\毕业设计\crypto_fi_final_internal_review')
V3 = Path(r'D:\毕业设计\crypto_fi_research_manuscript_v3')
PACKAGE = Path(r'D:\毕业设计\crypto_fi_external_review_package')

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def rf(x):
    return F(int(x['numerator']), int(x['denominator']))

def frac(x):
    return {'numerator': str(x.numerator), 'denominator': str(x.denominator)}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def decimal(x):
    with localcontext() as ctx:
        ctx.prec = 55
        return str(Decimal(x.numerator) / Decimal(x.denominator))

# Constants transcribed from v3 sections 7.3 and G.1, checked against selectors.
data = {
    '640': [(4559006261671696450341, 1208925819614629174706176, 26, '0.005043360'),
            (27303052442598203493, 2417851639229258349412352, 25, '0.000030345')],
    '976': [(82530945983948211008059, 1208925819614629174706176, 39, '0.078020625'),
            (72513186667423518510453, 4835703278458516698824704, 38, '0.017137631')],
    '1344': [(934417956505301732296527, 4835703278458516698824704, 39, '0.206115312'),
             (750864811440080469446307, 9671406556917033397649408, 38, '0.082813443')],
}
selector = read(V3 / 'certificates/UNIFIED_RESULT_SELECTORS.json')
matrix = read(V3 / 'CLAIM_EVIDENCE_MATRIX.json')
rows = []
for n, entries in data.items():
    profile = selector['profiles'][n]
    pi = rf(profile['parameters']['pi0'])
    alpha = F(1, 2 ** profile['initial']['full_failure_power'])
    C = sum((pi ** j for j in range(8)), F(0))
    for mode, entry in zip(['fixed_A', 'uniform_Setup'], entries):
        zn, zd, delta_power, display = entry
        Z = F(zn, zd)
        delta = F(1, 2 ** delta_power)
        good = pi ** 8 + C * Z
        assert 0 <= good < 1
        U = (1 - delta) * good + delta
        Uc = U / (1 - alpha)
        s = profile[mode]
        assert matrix['official_profile_results'][n][mode] == s
        assert Z == rf(s['Z']) and delta == rf(s['adopted_delta'])
        assert U == rf(s['full_correct_upper']) == rf(s['row_correct_upper'])
        assert Uc == rf(s['conditioned_on_initial']['full_correct_upper'])
        assert Uc == rf(s['conditioned_on_initial']['row_correct_upper'])
        assert U <= Uc < F(display)
        pct = (1 - F(display)) * 100
        assert pct == F(s['display']['full_error_percent_lower'].rstrip('%'))
        if n != '640':
            groups = s['frequency_groups']
            covered = [t for g in groups for t in range(g['range'][0], g['range'][1] + 1)]
            assert covered == list(range(1, 32769))
            assert all(g['count'] == g['range'][1] - g['range'][0] + 1 for g in groups)
            Zgroups = 2 * pi * sum((g['count'] * rf(g['R_power_n_up']) for g in groups), F(0))
            assert Zgroups == Z
        rows.append({'n': int(n), 'mode': mode, 'pi': frac(pi), 'C8': frac(C),
                     'Z': frac(Z), 'delta': frac(delta), 'initial_failure_upper': frac(alpha),
                     'U': frac(U), 'U_conditioned': frac(Uc),
                     'U_approximation': decimal(U), 'U_conditioned_approximation': decimal(Uc),
                     'display_upper': display, 'outward_margin': frac(F(display) - Uc),
                     'outward_margin_approximation': decimal(F(display) - Uc),
                     'error_percent_lower': s['display']['full_error_percent_lower'],
                     'all_equalities_and_outward_comparisons_passed': True})

# Bind the six manuscript G.1 fractions, including I-conditioned values.
draft = (V3 / 'CRYPTOANALYSIS_DRAFT.md').read_text(encoding='utf-8-sig')
g1 = draft.split('### G.1 ', 1)[1].split('### G.2 ', 1)[0]
for row in rows:
    for field in ['U', 'U_conditioned']:
        f = row[field]
        assert f["numerator"] + ' / ' + f["denominator"] in g1

# Current source directory and portable package must represent the same submission.
core = []
for name in ['CRYPTOANALYSIS_DRAFT.md', 'CLAIM_EVIDENCE_MATRIX.json',
             'HUMAN_REVIEW_ENTRY.md', 'REVISION_AND_READINESS.md', 'MANIFEST.json']:
    actual, frozen = V3 / name, PACKAGE / 'frozen/crypto_fi_research_manuscript_v3' / name
    assert actual.read_bytes() == frozen.read_bytes()
    core.append({'file': name, 'sha256': sha(actual), 'bytes': actual.stat().st_size,
                 'original_and_frozen_byte_equal': True})

manifest = read(V3 / 'MANIFEST.json')
payload = {k: v for k, v in manifest.items() if k != 'payload_sha256'}
canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
assert hashlib.sha256(canonical).hexdigest() == manifest['payload_sha256']
for item in manifest['files']:
    p = Path(item['path'])
    assert p.stat().st_size == item['bytes'] and sha(p) == item['sha256']

# General CF-1 inequality is symbolic; this checks its minimum-n coefficient.
at16 = F(1152) + F(3504, 16) + F(144, 16 ** 2) + F(288, 16 ** 3) + F(12, 16 ** 4)
assert at16 < 1372
cf_n, cf_D, s = 128, 56, 12
B0 = 2 * cf_n * s ** 2 + s
W = 2 * cf_n ** 2 * cf_D * s ** 2 + 2 * cf_n ** 2 * s ** 3 + cf_n * cf_D * s + cf_n * s ** 2
assert B0 + cf_n * W == 41084030988 < 2 ** cf_D // 8

report = {'schema': 'frodo-fi-final-review/direct-scalar-checks/1', 'status': 'PASS',
          'scope': 'Exact endpoint reconstruction, G.1 binding, complete grouped frequency coverage, submission identity, manifest and CF-1 scalar checks',
          'six_endpoints': rows, 'submission_binding': core,
          'v3_manifest_entries_verified': len(manifest['files']),
          'v3_manifest_canonical_payload_verified': True,
          'six_complete_matrix_selector_modes_equal': True,
          'CF1_minimum_n_coefficient': frac(at16),
          'CF1_n128_full_residual_upper': B0 + cf_n * W,
          'candidate_mechanisms_implemented': 0, 'cryptographic_samples_generated': 0}
(ROOT / 'evidence/FINAL_SCALAR_CHECKS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': 'PASS', 'six_endpoints': len(rows), 'v3_manifest_entries': len(manifest['files'])}))
