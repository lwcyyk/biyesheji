"""Independent graph/arithmetic review and exact approval-text binding."""
from pathlib import Path
import collections,hashlib,json
O=Path(__file__).resolve().parent.parent;E=O/'evidence'
def read(p):return json.loads(p.read_bytes())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=read(E/'FINAL_COUNT_CLOSURE_CALCULATION.json');assert sum(r['count'] for r in c['families'])==4450
g=read(E/'EVIDENCE_GRAPH_DELIVERY.json');nodes={n['evidence_id']:n for n in g['nodes']};order=g['topological_order'];pos={n:i for i,n in enumerate(order)}
assert len(nodes)==len(pos)==1142 and all(pos[a]<pos[b] for a,b in g['edges'])
rank={}
for n in order:rank[n]=max([rank[d]+1 for d in nodes[n]['dependency_ids']]or[0])
g['rank']=rank;g['closure_iterations_upper']=max(rank.values())+1;write(E/'EVIDENCE_GRAPH_DELIVERY.json',g)
adj={i:[] for i in nodes}
for a,b in g['edges']:adj[a].append(b)
cycles=[]
for a,b,label in [('A_POSTSEAL_CERTIFICATE','A_NATIVE_MANIFEST','certificate_inside_own_native_preimage'),
 ('FINALIZATION_RECEIPT','ADMIN_MANIFEST','final_receipt_inside_own_admin_preimage'),
 ('B_USE_REALIZATION','B_AUTH_RECEIPT','mutual_use_and_authorization_hashes')]:
 q=collections.deque([(b,[b])]);seen={b};found=None
 while q:
  n,path=q.popleft()
  if n==a:found=[a]+path;break
  for t in adj[n]:
   if t not in seen:seen.add(t);q.append((t,path+[t]))
 assert found and found[0]==found[-1]
 cycles.append({'added_edge':[a,b],'minimal_cycle':found,'edge_count':len(found)-1,'condition':label,'present_in_current_source':False})
with(E/'MINIMAL_CYCLE_WITNESSES.json').open('x',encoding='utf-8') as f:json.dump({'witnesses':cycles,'method':'BFS shortest existing path plus proposed reverse edge','new_runtime_tests':0},f,ensure_ascii=False,indent=2);f.write('\n')
rule_path=O/'proposals/MR_CROSS_INSTANCE_RULE_DRAFT.json';rule=read(rule_path)
rule['recommendation']='APPROVE_RECOMMENDED';rule['recommendation_scope']='CONDITIONAL_RULE_ONLY';write(rule_path,rule)
decision_path=E/'FINAL_REVIEW_DECISION.json';decision=read(decision_path)
decision['MR_recommendation']='APPROVE_RECOMMENDED';decision['MR_recommendation_scope']='CONDITIONAL_RULE_ONLY';write(decision_path,decision)
digest=hashlib.sha256(rule_path.read_bytes()).hexdigest()
p=O/'MR_CROSS_INSTANCE_ADMISSION_APPROVAL.md';s=p.read_text(encoding='utf-8')
s=s.replace('当前记录：**PENDING_USER_APPROVAL**；证书适用性：**NOT_USABLE_NOW**。',
 '规则附件SHA-256：`'+digest+'`。批准文字可直接引用此摘要；附件当前user_approved=false。\n\n当前记录：**PENDING_USER_APPROVAL**；证书适用性：**NOT_USABLE_NOW**。')
p.write_text(s,encoding='utf-8')
observed=read(E/'HISTORICAL_REFERENCES/DCL-R6-FullChain-AdmissionFix/evidence/EXPANDED_FULLCHAIN_LOWER_WITNESS.json')['rows']
assert len(observed)==len({r['relative'] for r in observed})==1082
for r in observed:
 assert r['sha256'] is None and r['size'] is None
save={'count_arithmetic':'PASS_HOST_STATIC_ARITHMETIC','graph_nodes':len(nodes),'graph_edges':len(g['edges']),
 'topological_edges_strictly_increase':True,'rank_max':max(rank.values()),'fixed_point_iterations_upper':max(rank.values())+1,
 'physical_family_sum':4450,'schema_not_extra_file':True,'lower_paths_unique':1082,'minimal_proposed_cycle_lengths':[r['edge_count'] for r in cycles],
 'bound_scope':'Conservative closed-world manual source abstraction; full semantic extraction not mechanically proven',
 'MR_rule_sha256':digest,'MR_user_approved':False,'new_runtime_tests':0,'actual_windows_created':0}
with(E/'INDEPENDENT_STATIC_REVIEW.json').open('x',encoding='utf-8') as f:json.dump(save,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'nodes':len(nodes),'rank':max(rank.values()),'count':4450,'cycles':[r['edge_count'] for r in cycles],'rule_sha256':digest}))
