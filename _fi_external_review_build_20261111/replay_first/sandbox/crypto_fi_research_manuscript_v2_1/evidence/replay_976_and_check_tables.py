"""Deterministic finite distribution replay; no UE, attack, LWE, or key sampling.
Rebuild chi976 from official CDF, reproduce all 1281 integer coefficients, and
certify epsilon by a common power-of-two denominator. Check all three sampler
tables using exhaustive enumeration of the finite 16-bit input domain.
"""
from pathlib import Path
from math import comb
from fractions import Fraction as F
from collections import Counter
from decimal import Decimal, localcontext
import json,hashlib,sys

sys.set_int_max_str_digits(0)
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(r'D:\毕业设计')
OUT=Path(__file__).resolve().parents[1]
EV=OUT/'evidence'
V1=BASE/'crypto_fi_research_manuscript_v1'
HIST=BASE/'crypto_frodo_unconditional_support'
profiles=json.loads((V1/'sources/PARAMETER_CERTIFICATES.json').read_text('utf-8'))['profiles']
registered_input=json.loads((HIST/'sources/official_cdf_input.json').read_text('utf-8'))['cdf_checks']
checks=[]
def check(name,c):
    checks.append(dict(name=name,passed=bool(c)))
    assert c,name
def ratio(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator))
def rf(x):return F(int(x['numerator']),int(x['denominator']))
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def fingerprint(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def big_identity(n):
    b=n.to_bytes((n.bit_length()+7)//8,'big')
    return dict(bits=n.bit_length(),unsigned_big_endian_sha256=hashlib.sha256(b).hexdigest(),encoding='minimal unsigned big-endian bytes; zero encoded as empty bytes')
def bound_certificate(num,e):
    k=e-(num-1).bit_length()
    check('dyadic tight exponent '+str(len(checks)),num<=(1<<(e-k)) and num>(1<<(e-k-1)))
    return dict(common_denominator_power_of_two=e,largest_integer_k_with_value_le_2_to_minus_k=k,numerator_identity=big_identity(num),bound_le_2_to_minus_k=True,next_integer_bound_fails_for_this_upper_expression=True)

TABLES={
 '640':dict(n=640,D=15,s=12,cdf=[4643,13363,20579,25843,29227,31145,32103,32525,32689,32745,32762,32766,32767],official_mass=[9288,8720,7216,5264,3384,1918,958,422,164,56,17,4,1],source_scope='2021 PDF25 Table3 andPDF15 section2.2.4 CDF-mass formula;2023 physicalPDF15 TableA3/16 TableA4 gives actual numericCDF'),
 '976':dict(n=976,D=16,s=10,cdf=[5638,15915,23689,28571,31116,32217,32613,32731,32760,32766,32767],official_mass=[11278,10277,7774,4882,2545,1101,396,118,29,6,1],source_scope='2021 PDF25 Table3 andPDF15 section2.2.4 CDF-mass formula;2023 physicalPDF15 TableA3/16 TableA4 gives actual numericCDF'),
 '1344':dict(n=1344,D=16,s=6,cdf=[9142,23462,30338,32361,32725,32765,32767],official_mass=[18286,14320,6876,2023,364,40,2],source_scope='2021 PDF25 Table3 and2023 physicalPDF15 TableA3;CDF corrected by official issue35 comment2504969837 dated2024-11-27; oldCDF table missing32765')}
old976=[11278,10277,7774,4882,2545,1131,426,138,38,8,1]
laws={}
for name,row in TABLES.items():
    cdf=row['cdf'];s=row['s']
    mass=[2*(cdf[0]+1)]+[cdf[i]-cdf[i-1] for i in range(1,s+1)]
    inverse_cdf=[row['official_mass'][0]//2-1]
    for w in row['official_mass'][1:]:inverse_cdf.append(inverse_cdf[-1]+w)
    check(name+' CDF reconstructed from official PMF',inverse_cdf==cdf)
    law={z:mass[abs(z)] for z in range(-s,s+1)}
    check(name+' strict CDF and final endpoint',len(cdf)==s+1 and all(a<b for a,b in zip([-1]+cdf,cdf)) and cdf[-1]==32767)
    check(name+' CDF derived equals official mass table',mass==row['official_mass'])
    check(name+' total mass',sum(law.values())==65536)
    check(name+' positive full support',all(w>0 for w in law.values()) and list(law)==list(range(-s,s+1)))
    check(name+' symmetry',all(law[z]==law[-z] for z in law))
    even=sum(w for z,w in law.items() if z%2==0);odd=65536-even
    expected=(32770,32766) if name=='1344' else (32768,32768)
    check(name+' stated parity mass',(even,odd)==expected)
    peak=max(law.values());maxsites=[z for z,w in law.items() if w==peak]
    check(name+' unique largest atom',maxsites==[0])
    profile=next(p for p in profiles if p['profile']==name)
    stored=next(p for p in registered_input if str(p['n'])==name)
    check(name+' certificate CDF input',profile['source_cdf']==cdf==stored['cdf'])
    check(name+' producer input mass',stored['probability_numerators_zero_then_each_signed_value']==mass)
    check(name+' certificate maximum atom',rf(profile['fixed_A_primary']['a'])==F(peak,65536))
    check(name+' certificate parity',rf(profile['a_j'][1]['a'])==F(max(even,odd),65536))
    # Exhaust the official finite input domain, not random samples.
    histogram=Counter()
    for word in range(65536):
        t=word>>1
        magnitude=sum(t>cut for cut in cdf[:-1])
        value=-magnitude if word&1 else magnitude
        histogram[value]+=1
    check(name+' all65536 sampler inputs equal CDF mass',dict(histogram)==law)
    boundaries=[]
    for i,cut in enumerate(cdf[:-1]):
        for t,expected_magnitude in [(cut,i),(cut+1,i+1)]:
            got=sum(t>x for x in cdf[:-1])
            check(f'{name} endpoint{i} t={t}',got==expected_magnitude)
            boundaries.append(dict(cdf_index=i,t=t,magnitude=got))
    laws[name]=dict(**row,denominator=65536,mass_zero_then_each_signed_value=mass,CDF_reconstructed_from_official_mass=inverse_cdf,signed_integer_mass={str(z):w for z,w in law.items()},normalization=65536,support=[-s,s],support_size=2*s+1,symmetric=True,even_numerator=even,odd_numerator=odd,maximum_atom=ratio(F(peak,65536)),maximizing_atoms=maxsites,sampler_input_words_exhausted=65536,sampler_matches_mass=True,threshold_boundaries=boundaries,certificate_input_matches=True,full_convolution_recomputed=(name=='976'))

mass=laws['976']['mass_zero_then_each_signed_value'];s=10
base=mass[:0:-1]+mass
coeff=[1];half=None;stage=[]
for depth in range(1,65):
    new=[0]*(len(coeff)+20)
    for j,w in enumerate(base):
        for i,x in enumerate(coeff):new[i+j]+=w*x
    coeff=new
    if depth==32:half=coeff[:]
    check(f'976 convolution depth{depth} mass',sum(coeff)==65536**depth)
    check(f'976 convolution depth{depth} support',len(coeff)==20*depth+1 and coeff[0]>0 and coeff[-1]>0)
    stage.append(dict(depth=depth,offset=-10*depth,coefficient_count=len(coeff),total_equals_65536_power_depth=True,peak=str(max(coeff))))

stored_path=V1/'sources/chi_976_64fold_coefficients.json'
stored=json.loads(stored_path.read_text('utf-8'))
den=65536**64
offset=-640
check('976 stored offset',stored['offset']==offset)
check('976 all1281 coefficient count',len(stored['coefficients'])==len(coeff)==1281)
mismatches=[]
for i,x in enumerate(coeff):
    old=int(stored['coefficients'][i])
    if old!=x:mismatches.append(dict(index=i,sum_value=offset+i,expected=str(x),stored=str(old)))
check('976 all1281 coefficients match',not mismatches)
check('976 denominator65536^64',int(stored['denominator'])==den==1<<1024)
check('976 convolution total',sum(coeff)==den)
check('976 convolution symmetry',coeff==coeff[::-1])
peak=max(coeff);modes=[i+offset for i,x in enumerate(coeff) if x==peak]
check('976 unique convolution peak',modes==[0])
check('976 peak equals32fold L2 identity',peak==sum(x*x for x in half))
q=65536
check('976 modular support has no merges',q>128*s and len({z%q for z in range(-640,641)})==1281)
new_path=EV/'chi_976_64fold_coefficients.json'
dump(new_path,dict(offset=offset,denominator=str(den),coefficients=list(map(str,coeff))))
profile=next(p for p in profiles if p['profile']=='976')['fixed_A_primary']
a=F(11278,65536);mu=F(peak,den);gamma=21*mu
check('976 a equals registered exact atom',a==rf(profile['a']))
check('976 mu equals registered exact peak',mu==rf(profile['mu64']))
check('976 gamma equals registered exact value',gamma==rf(profile['gamma_h_mu64']))
check('976 no alias string matches',profile['no_alias_condition']=='q=65536>2*s*64=1280')

n=976;E=1024*n
first_num=comb(n,63)*11278**(n-63)
first_e=16*(n-63)
second_num=(21*peak)**n
total_num=(first_num<<(E-first_e))+second_num
target_rhs=1<<(E-1118)
check('epsilon976 exact upper2^-1118',total_num<=target_rhs)
first_cert=bound_certificate(first_num,first_e)
second_cert=bound_certificate(second_num,E)
sum_cert=bound_certificate(total_num,E)
check('976 first term exponent matches legacy',first_cert['largest_integer_k_with_value_le_2_to_minus_k']==-profile['bad_parent_certificate']['ceil_log2_raw'])
check('976 high term exponent matches legacy',second_cert['largest_integer_k_with_value_le_2_to_minus_k']==-profile['high_weight_certificate']['ceil_log2_raw'])
check('976 epsilon exponent matches legacy',sum_cert['largest_integer_k_with_value_le_2_to_minus_k']==1118==-profile['B_fixed_A_certificate']['ceil_log2_raw'])
with localcontext() as c:
    c.prec=65
    gamma_display=str(Decimal(gamma.numerator)/Decimal(gamma.denominator))

differences=[dict(z=z,old_numerator=old976[abs(z)],correct_numerator=mass[abs(z)],correct_minus_old=mass[abs(z)]-old976[abs(z)],changed=old976[abs(z)]!=mass[abs(z)]) for z in range(-10,11)]
dump(EV/'DISTRIBUTION_TABLES.json',dict(schema='fi-distribution-tables/1',source_rule='2021 Algorithm5 PDF16 and2023 section7.4 physicalPDF8; t=word>>1, sign=word&1, loopCDF0..s-1 with t>CDF[i]',profiles=laws,inc976=dict(old_mass=old976,correct_mass=mass,old_total=old976[0]+2*sum(old976[1:]),correct_total=65536,all21_signed_point_differences=differences,changed_signed_atoms=[d['z'] for d in differences if d['changed']])))

result=dict(schema='fi976-erratum/exact-replay/1',identity='AUTHOR_ERRATUM_IMPACT_AUDIT_AND_DETERMINISTIC_CERTIFICATE_REPLAY',source_files=[fingerprint(stored_path),fingerprint(V1/'sources/PARAMETER_CERTIFICATES.json'),fingerprint(HIST/'sources/official_cdf_input.json'),fingerprint(HIST/'sources/build_mathematical_certificates.py')],
 input_profile=laws['976'],convolution=dict(iterations=64,integer_recurrence='p0(0)=1; p_(t+1)(k)=sum_z weight[z]*p_t(k-z)',stages=stage,offset=offset,coefficient_count=1281,compared_coefficients=1281,all_coefficients_match=True,first_difference=None,mismatches=[],denominator=str(den),total_equals_denominator=True,maximum_coefficient=str(peak),modes=modes,mu64=ratio(mu),mu64_unreduced=dict(numerator=str(peak),denominator=str(den)),peak_32fold_l2_identity=True,modular_support_interval=[-640,640],modulus=q,no_alias_condition='65536>1280',new_coefficients=fingerprint(new_path),legacy_coefficients=fingerprint(stored_path),new_file_byte_identical_to_legacy=new_path.read_bytes()==stored_path.read_bytes()),
 probability=dict(n=976,w0=64,h=21,a=ratio(a),mu64=ratio(mu),gamma=ratio(gamma),gamma_display_only=gamma_display,
  epsilon_expression='binom(976,63)*(11278/65536)^913+(21*M/65536^64)^976',
  exact_common_denominator_power_of_two=E,first_term_denominator_power_of_two=first_e,
  exact_total_numerator_definition='binom(976,63)*11278^913*2^(999424-14608)+(21*M)^976',M=str(peak),
  bound_comparison='N<=2^(999424-1118)',rhs_power_of_two=E-1118,comparison_passed=True,
  total_numerator_identity=big_identity(total_num),rhs_identity=big_identity(target_rhs),positive_margin_identity=big_identity(target_rhs-total_num),
  first_term_certificate=first_cert,high_weight_certificate=second_cert,sum_certificate=sum_cert,
  epsilon_le_2_to_minus1118=True,next_exponent1119_fails_for_this_upper_expression=True,
  endpoint_interpretation='These dyadic comparisons bound the exact algebraic fresh false-acceptance upper expression; they give no actual decryption-failure or false-acceptance lower bound'),
 full_recompute_scope=['97664fold integer convolution','976full two-term epsilon expression'],
 other_profiles_scope='640/1344 CDF/table/producer-input consistency, all65536 scalar-sampler inputs and parity/max-atom checks; no new64fold convolution or epsilon recomputation',
 algorithmic_random_samples=0,matrices_keys_tokens_ciphertexts_generated=0,checks=checks,checks_passed=len(checks),all_checks_passed=True)
dump(EV/'REPLAY_976.json',result)
print(json.dumps(dict(checks_passed=len(checks),coefficients_compared=1281,all_match=True,byte_identical=result['convolution']['new_file_byte_identical_to_legacy'],offset=offset,maximum_coefficient=str(peak),gamma_display_only=gamma_display,epsilon976_upper='2^-1118',dyadic_k=sum_cert['largest_integer_k_with_value_le_2_to_minus_k'],sampler_inputs_per_profile=65536),ensure_ascii=False))
