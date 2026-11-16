from pathlib import Path
import json,csv,hashlib,zipfile,collections,re,difflib,subprocess,sys,os
sys.dont_write_bytecode=True
R=Path(r'D:\毕业设计');O=Path(__file__).parents[1];W=O/'工作底稿';C=R/'研究/密码学辅助_一致性核验';S=R/'研究/算法机制重构与原创性验证_2026-11-03'
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(W/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=j(W/'历史清单逐项重算.json'); resolutions=[]
for row in checks:
 if row['actual'] is None and row['path'].startswith('party'):
  candidates=list((C/'revisions/structural_audit_2026-11-03_r1/results').glob('*/'+row['path']))
  matches=[p for p in candidates if h(p)==row['expected']]
  if len(matches)==1:row.update(path=str(matches[0].relative_to(R)),actual=row['expected'],verdict='MATCH_RESOLVED_LOG_CONTEXT')
 if row['verdict']=='DIFF_CURRENT_OR_MISSING':
  name=str(Path(row['path']).relative_to('auth-lifecycle')).replace('\\','/')
  with zipfile.ZipFile(R/'auth-lifecycle/results/experiments/pilot02/source_bundle.zip') as z:
   member=next((n for n in z.namelist() if n.replace('\\','/').endswith(name)),None)
   b=z.read(member) if member else b'';matched=hashlib.sha256(b).hexdigest()==row['expected']
   diff=''.join(difflib.unified_diff(b.decode('utf-8-sig').splitlines(True),(R/row['path']).read_text(encoding='utf-8-sig').splitlines(True),fromfile='historical_snapshot',tofile='current'))
   (W/(Path(name).stem+'_历史差异.diff')).write_text(diff,encoding='utf-8')
   resolutions.append({'path':row['path'],'snapshot_member':member,'snapshot_matches_historical':matched,'current_diff_saved':True})
save('历史清单最终核对.json',{'counts':dict(collections.Counter(x['verdict'] for x in checks)),'snapshot_resolution':resolutions,'records':checks})
runs=[json.loads(s) for s in (R/'auth-lifecycle/results/experiments/pilot02/runs.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
stats=[]
for method in sorted({x['metadata']['method'] for x in runs}):
 a=[x for x in runs if x['metadata']['method']==method];stats.append({'method':method,'N':len(a),'U':sum(x['metrics']['U'] for x in a),'statuses':dict(collections.Counter(x['metrics']['status'] for x in a)),'C_Q_mean':sum(x['metrics']['C_Q'] for x in a)/len(a),'C_G_mean':sum(x['metrics']['C_G'] for x in a)/len(a),'O_end':sum(x['metrics']['O_end'] for x in a),'E':sum(x['metrics']['E'] for x in a),'FA':sum(x['metrics']['FA'] for x in a),'probe_selection_count':sum(x['metrics']['probe_selection_count'] for x in a),'feedback_calls':sum(x['metrics']['feedback_calls'] for x in a)})
rows=j(S/'runs/final02/rows.json');bycase=collections.defaultdict(dict)
for x in rows:bycase[(x['kind'],x['case'])][x['method']]=x
claims={}
for kind,methods,field in [('A',['A2','GENERIC_A_BB'],'Q'),('A',['AB_ON','AB_OFF'],'Q'),('B',['B2','GENERIC_BB'],'G')]:
 pairs=[(name,d) for (k,name),d in bycase.items() if k==kind and all(m in d for m in methods)]
 claims['/'.join(methods)]={'N':len(pairs),'equal':sum(d[methods[0]].get(field)==d[methods[1]].get(field) for _,d in pairs)}
save('原始结果再统计.json',{'pilot':stats,'pilot_pair_count':len({x['metadata']['pair_id'] for x in runs}),'pilot_total_O_end':sum(x['metrics']['O_end'] for x in runs),'pilot_independent_attested':sum(bool(x['metadata']['independence_attested']) for x in runs),'prototype_rows':len(rows),'prototype_cases':len(bycase),'prototype_methods':sorted({x['method'] for x in rows}),'prototype_pair_checks':claims})
# Local source PDF structural check via stdout because anchored output requires POSIX.
for i,name in enumerate(['Randomizing_polynomials_A_new_representation_with_applications_to_round-efficient_secure_computation.pdf','3-3-4.pdf'],1):
 p=subprocess.run([sys.executable,'-X','utf8',r'C:\Users\a1887\.codex\skills\academic-research-suite\ars\scripts\pdf_read_preflight.py',str(R/'研究'/name)],capture_output=True,text=True,encoding='utf-8');(W/f'paper{i}_preflight.json').write_text(p.stdout or json.dumps({'status':'UNAVAILABLE','stderr':p.stderr},ensure_ascii=False),encoding='utf-8')
# Public mathematical check only, no MPC/backend/services.
rev=C/'revisions/structural_audit_2026-11-03_r1';sys.path.insert(0,str(rev))
import profiles,compiler,checker,gate_reference
from itertools import product
original,restricted=profiles.record_profiles();counts=[]
for profile in [original,restricted]:
 circuit=gate_reference.build(profile)
 # Signature varies; independent count uses explicit policy membership.
 family={tuple(s) for s in profile['support_policy']['supports']}
 counts.append(sum(tuple(i for i,v in enumerate(d) if v) in family for d in product(range(4),repeat=4)))
cert=compiler.components(restricted);positive=checker.check(cert,restricted)
bad=json.loads(json.dumps(cert));bad['minimum_rows']+=1;negative=checker.check(bad,restricted)
conflict=checker.check(compiler.find_conflict(original),original)
save('本轮公开证书检查.json',{'scope':'PUBLIC_MODEL_ONLY','profile_counts_GF4_256':counts,'removed_inputs':counts[0]-counts[1],'positive':positive,'tampered_row_bound':negative,'dependency_conflict':conflict,'no_MPC_run':True})
print(json.dumps({'manifest':dict(collections.Counter(x['verdict'] for x in checks)),'pilot':stats,'prototype_methods':sorted({x['method'] for x in rows}),'public_counts':counts,'cert_verdicts':[positive['verification_status'],negative['verification_status'],conflict['verification_status']]},ensure_ascii=False,indent=2))
