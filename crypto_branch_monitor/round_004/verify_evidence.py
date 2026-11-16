"""Read-only evidence/finite-scalar checks; no UE, LWE, or candidate implementation."""
import json
import hashlib
from fractions import Fraction
from pathlib import Path
from datetime import datetime, timezone

root = Path(r'D:\毕业设计\crypto_frodo_common_parameter_closure')
out = Path(__file__).parent
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

records = []
for name, rows in [
    ('source_manifest', read(root/'sources/source_manifest.json')),
    ('frozen_inputs', read(root/'sources/input_and_identity_record.json')['inputs']),
    ('deliverables', read(root/'sources/delivery_validation.json')['deliverables']),
]:
    for row in rows:
        data = Path(row['path']).read_bytes()
        got = hashlib.sha256(data).hexdigest()
        records.append(dict(register=name, path=row['path'], sha256=got,
                            hash_matches=got == row['sha256'],
                            size_matches=len(data) == row['bytes']))

scalar_rows = []
for r in read(root/'sources/exact_family_checks.json')['checks']:
    n = 8*r['lambda']
    D = 8*(n-1).bit_length()
    q = 1 << D
    b0 = 288*n+12
    w = 288*n*n*D + 3456*n*n + 12*n*D + 144*n
    e = b0+n*w
    expected = {'n':n, 'D':D, 'q':q, 'B0':b0, 'W':w,
                'one_update_noise_bound':b0+w, 'all_T_updates_noise_bound':e,
                'decode_radius':q//8, 'coarse_upper':4096*n**4,
                'T':n, 'k':n, 'Q':3*n+1}
    matching = all(int(r[key]) == val for key, val in expected.items())
    ratio = Fraction(e, q//8)
    matching = matching and str(ratio) == r['total_over_radius_exact']
    scalar_rows.append({'lambda':r['lambda'], 'n':n, 'D':D,
        'matches_reported_exact_fields':matching,
        'inequality_chain':e <= 2304*n**4+3552*n**3+144*n*n+288*n+12
            < 2529*n**4 < 4096*n**4 < n**8//8 <= q//8,
        'modulus_bounds':n**8 <= q < (2*n)**8,
        'support_decay_base':50 <= q})

rank_rows=[]
for r in read(root/'sources/normal_form_reduction_count_checks.json')['checks']:
    n=r['dimension_n']
    prod=Fraction(1)
    for i in range(n):
        prod *= 1-Fraction(1,1 << (2*n-i))
    fail=1-prod
    rank_rows.append({'n':n, 'failure':str(fail),
        'matches_reported':str(fail)==r['basis_failure_exact'],
        'failure_below_bound':fail < Fraction(1,1<<n),
        'sample_count_matches':r['source_samples']==3*n
            and r['anchor_samples']==2*n and r['remaining_target_samples']==n})

cdf=[4643,13363,20579,25843,29227,31145,32103,32525,32689,32745,32762,32766,32767]
mass=[2*(cdf[0]+1)] + [cdf[i]-cdf[i-1] for i in range(1,len(cdf))]
total=mass[0]+2*sum(mass[1:])
even=mass[0]+2*sum(mass[i] for i in range(2,len(mass),2))
odd=2*sum(mass[i] for i in range(1,len(mass),2))
declared=[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1]
cdf_ok=mass==declared and total==65536 and even==odd==32768

passed=(all(r['hash_matches'] and r['size_matches'] for r in records)
    and all(r['matches_reported_exact_fields'] and r['inequality_chain']
            and r['modulus_bounds'] and r['support_decay_base'] for r in scalar_rows)
    and all(r['matches_reported'] and r['failure_below_bound'] and r['sample_count_matches'] for r in rank_rows)
    and cdf_ok)
result={'created_utc':datetime.now(timezone.utc).isoformat(),
    'review_mode':'SUPERVISOR_INFORMED_AUDIT','status':'PASS' if passed else 'FAIL',
    'hash_record_count':len(records),'hash_records':records,
    'family_row_count':len(scalar_rows),'family_rows':scalar_rows,
    'rank_row_count':len(rank_rows),'rank_rows':rank_rows,
    'cdf':{'mass_numerators':mass,'total':total,'even':even,'odd':odd,'pass':cdf_ok},
    'limits':'Finite scalar rechecks and artifact integrity only. General proof and source interpretation are separately recorded in REVIEW.md. No protocol, cipher, attack, or service is executed.'}
(out/'AUDIT_CHECKS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','hash_record_count','family_row_count','rank_row_count','cdf']},ensure_ascii=False))
raise SystemExit(0 if passed else 1)
