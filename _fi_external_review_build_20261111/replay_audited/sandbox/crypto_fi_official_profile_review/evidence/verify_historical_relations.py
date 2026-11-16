"""Deterministic relation check for earlier source-event certificates.
No attack implementation or cryptographic execution occurs.
"""
from pathlib import Path
import os
from fractions import Fraction as F
import json,hashlib,math,sys
sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)
sys.set_int_max_str_digits(2000000)
B=Path(os.environ['FRODO_FI_SANDBOX']); E=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(x): return F(int(x['numerator']),int(x['denominator']))
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pc=B/'crypto_fi_research_manuscript_v1/sources/PARAMETER_CERTIFICATES.json'
files=[pc,B/'crypto_fi_research_manuscript_v2_1/evidence/chi_976_64fold_coefficients.json',B/'crypto_fi_research_manuscript_v1/sources/chi_1344_64fold_coefficients.json']
dump(E/'ADDITIONAL_INPUT_SNAPSHOT.json',[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in files])
cert=json.loads(pc.read_text(encoding='utf-8')); rows=[]
tables={976:[11278,10277,7774,4882,2545,1101,396,118,29,6,1],1344:[18286,14320,6876,2023,364,40,2]}
for n in [976,1344]:
 table=tables[n]; s=len(table)-1; w=[table[abs(x)] for x in range(-s,s+1)]; a=[1]
 for step in range(64):
  nxt=[0]*(len(a)+2*s)
  for i,v in enumerate(a):
   for j,m in enumerate(w): nxt[i+j]+=v*m
  a=nxt
 p=next(x for x in cert['profiles'] if int(x['profile'])==n)['fixed_A_primary']
 source=files[1 if n==976 else 2]; conv=json.loads(source.read_text(encoding='utf-8'))
 assert a==list(map(int,conv['coefficients'])) and int(conv['denominator'])==65536**64 and conv['offset']==-64*s
 assert sha(source)==p['convolution_sha256'] and sum(a)==65536**64
 mu=F(max(a),65536**64); assert mu==rd(p['mu64']) and [i-64*s for i,c in enumerate(a) if c==max(a)]==[0]
 epsilon=math.comb(n,63)*F(table[0],65536)**(n-63)+((2*s+1)*mu)**n
 e=epsilon.denominator.bit_length()-epsilon.numerator.bit_length()
 while epsilon.numerator<<e>epsilon.denominator: e-=1
 while epsilon.numerator<<(e+1)<=epsilon.denominator: e+=1
 assert e==(1118 if n==976 else 1532)
 rows.append(dict(n=n,source_event='Fresh false acceptance in source-distinguishing analysis',
  bound_expression='binom(n,63)*a^(n-63)+((2*s+1)*mu64)^n',certified_exponent=e,
  complete_64fold_coefficients=len(a),convolution_reconstructed=True,peak_matches=True,
  frozen_convolution_sha256=sha(source),model_relation='Same exact scalar chi and fixed-A printed-algorithm contract; event differs from Decode success',
  full_attack_theorem_re_reviewed=False))
 print(n,'source epsilon <=2^-'+str(e),'complete convolution matches',len(a),'coefficients')
dump(E/'HISTORICAL_EVENT_RELATIONS.json',dict(status='PASS',profiles=rows,
 scope='Full finite convolution and scalar source-event epsilon recomputation; structural attack/game proofs inherited with disclosed scope'))
