"""Source-review refinement of the count envelope and stage-specific DAG."""
from pathlib import Path
import collections,copy,json
E=Path(__file__).resolve().parent
def read(n):return json.loads((E/n).read_bytes())
def save(n,x):
 with(E/n).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
c=read('COUNT_CLOSURE_CALCULATION.json');families={r['id']:r for r in c['families']}
actors=sum(r['actors'] for r in c['S34_table']);barriers=sum(r['barriers'] for r in c['S34_table'])
for r in c['S34_table']:
 r['G_atomic_metadata_targets']+=r['barriers'];r['range_core_temp_slots']=3*r['actors']
 r['core_temp_proof']='At most one current intent temp plus its retained counterpart and one fact temp per actor; fixed PID/TID. Retain then recreate is included.'
families['S_CORE_TEMP']['count']=3*actors;families['S_CORE_TEMP']['basis']='3*48 actor slots: current intent, retained intent, fact temp. No double counting with G.atomic non-core targets.'
families['PAYLOAD_FIXED_TEMP']['count']+=2*barriers
families['PAYLOAD_FIXED_TEMP']['basis']='2*759 non-core atomic target slots (including12 rendezvous files) +31 shared global-intent writers +6 global fact owner/claim writers'
c['raw_nonarchive_upper']=sum(r['count'] for r in c['families']);K=c['raw_nonarchive_upper']
assert K==4450
c.update(native_members_upper=K+1,admin_originals_upper=K+2,admin_zip_members_upper=K+17)
c['review_refinement']={'draft_raw_upper':4378,'retained_intent_recreation_delta':actors,'rendezvous_atomic_temp_delta':2*barriers,'final_delta':72,
 'status':'Final source review includes both effects; draft files retained as analysis history, not final bound'}
c['scope_limits']={'runtime_root_only':True,'archive_on_success_is_guard_conditional':True,
 'external_journal_export':'Lock contains an exact command; no current automatic ROOT producer for a separate full journal export. Keep as separately specified post-exit evidence node; no arbitrary folding into ROOT capacity.',
 'convenience_reports':'Outside runtime ROOT/control collector preimages; additions update research delivery manifest, not native closure recursively',
 'host_failure_frontend':'Separate fixed-name frontend-abort archive; K+17 describes the ordinary post-exit admin ZIP when it exists, not a fabricated successful archive for all failures'}
save('FINAL_COUNT_CLOSURE_CALCULATION.json',c)
g=read('EVIDENCE_DEPENDENCY_GRAPH.json');remove={'POSTSEAL_MR_CERTIFICATE','B_USE_SPEC','B_AUTH_RECEIPT','B_USE_REALIZATION','B_CURRENT_QUALIFICATION'}
nodes={n['evidence_id']:n for n in g['nodes'] if n['evidence_id'] not in remove}
for n in nodes.values():n['contract_scope']='CURRENT_FROZEN_NORMAL_COMPLETE_TRACE';n['dependency_ids']=[d for d in n['dependency_ids'] if d not in remove]
def add(i,dep,kind,scope,path):
 nodes[i]={'evidence_id':i,'producer':i,'source_path':path,'content_hash':None,'evidence_type':kind,
 'required_by':'Explicit pending contract or selected failure-prefix scope','verification_rule':'Separate raw/source/identity/hash/oracle obligations; this is a contract model, not an executed gate',
 'storage_requirement':'Outside previous seal preimage when created after that seal','retention_requirement':'PRESERVE_REQUIRED_ORIGINALS',
 'dependency_ids':dep,'contract_scope':scope}
scope='FROZEN_FAILURE_PREFIX_ALTERNATIVE'
add('FAILURE_PREFIX_RAW',['CURRENT_RUNTIME','PROGRAM_BYTES','STATIC_INPUTS'],'native_raw_fact',scope,'<ROOT>/prefix-originals')
add('FAILURE_TERMINAL_REVIEW',['FAILURE_PREFIX_RAW'],'derived_verification',scope,'<ROOT>/terminal-review-if-applicable')
add('FAILURE_NATIVE_MANIFEST',['FAILURE_TERMINAL_REVIEW'],'manifest_integrity',scope,'<ROOT>/out/EVIDENCE_MANIFEST.json')
add('FAILURE_NATIVE_ZIP',['FAILURE_NATIVE_MANIFEST'],'archive_seal_metadata',scope,'<ROOT>/out/EVIDENCE.zip')
add('FAILURE_ADMIN_ZIP',['FAILURE_NATIVE_ZIP','FAILURE_PREFIX_RAW'],'archive_seal_metadata',scope,'<CONTROL>/STARTUP_ADMIN_EVIDENCE.zip')
scope='PENDING_CROSS_INSTANCE_RULE_NOT_IMPLEMENTED'
add('APPROVED_RULE_DESCRIPTOR',[],'test_input_and_identity',scope,'<approval>/policy.pending')
add('A_ARTIFACT_LOCK',['PROGRAM_BYTES','STATIC_INPUTS','APPROVED_RULE_DESCRIPTOR'],'test_input_and_identity',scope,'<A-source>/locks')
add('A_NATIVE_FAULT_RAW',['A_ARTIFACT_LOCK'],'native_raw_fact',scope,'<A-root>/mr_native_case + raw journals')
add('A_STOP_AND_EXIT_RAW',['A_NATIVE_FAULT_RAW'],'native_raw_fact',scope,'<A-root>/STOP/CLOSED/waitpid/ledger')
add('A_NATIVE_MANIFEST',['A_STOP_AND_EXIT_RAW'],'manifest_integrity',scope,'<A-root>/out/EVIDENCE_MANIFEST.json')
add('A_NATIVE_ZIP',['A_NATIVE_MANIFEST'],'archive_seal_metadata',scope,'<A-root>/out/EVIDENCE.zip')
add('A_ADMIN_MANIFEST',['A_NATIVE_ZIP','A_STOP_AND_EXIT_RAW'],'manifest_integrity',scope,'<A-control>/STARTUP_ADMIN_MANIFEST.json')
add('A_ADMIN_ZIP',['A_ADMIN_MANIFEST'],'archive_seal_metadata',scope,'<A-control>/STARTUP_ADMIN_EVIDENCE.zip')
add('A_FINALIZATION_RECEIPT',['A_ADMIN_ZIP','A_NATIVE_ZIP'],'administrative_report',scope,'<A-control>/STARTUP_FINALIZATION.json')
add('A_POSTSEAL_CERTIFICATE',['A_FINALIZATION_RECEIPT','A_NATIVE_ZIP','A_ADMIN_ZIP','A_NATIVE_FAULT_RAW','APPROVED_RULE_DESCRIPTOR'],
 'derived_verification',scope,'<outside-A-root-and-sealed-control-preimage>/certificate.pending')
add('SOURCE_PAIR_EQUIVALENCE_REVIEW',['A_ARTIFACT_LOCK','EXECUTION_LOCK'],'derived_verification',scope,'<review>/exact-pair-projection.pending')
add('B_USE_SPEC',['A_POSTSEAL_CERTIFICATE','SOURCE_PAIR_EQUIVALENCE_REVIEW','APPROVED_RULE_DESCRIPTOR'],'test_input_and_identity',scope,'<B-control>/preauthorization-use-spec.pending')
add('B_AUTH_RECEIPT',['B_USE_SPEC','EXECUTION_LOCK'],'test_input_and_identity',scope,'<B-control>/authorization.pending')
add('B_USE_REALIZATION',['B_AUTH_RECEIPT','B_USE_SPEC'],'native_raw_fact',scope,'<B-root>/realized-use.pending')
add('B_PENDING_RESOURCE_GATE',['RESOURCE_QUALIFICATION','B_USE_REALIZATION','APPROVED_RULE_DESCRIPTOR'],'derived_verification',scope,'<B-root>/pending-gate-result')
add('B_PENDING_F1_F4',['B_PENDING_RESOURCE_GATE'],'test_execution_raw_fact',scope,'<B-root>/future-formal-output')
edges=[[d,n['evidence_id']] for n in nodes.values() for d in n['dependency_ids']]
adj={n:[] for n in nodes};degree={n:0 for n in nodes}
for a,b in edges:assert a in nodes;adj[a].append(b);degree[b]+=1
q=collections.deque(i for i in nodes if not degree[i]);order=[];rank={}
while q:
 a=q.popleft();order.append(a);rank[a]=max([rank[d]+1 for d in nodes[a]['dependency_ids']]or[0])
 for b in adj[a]:
  degree[b]-=1
  if degree[b]==0:q.append(b)
assert len(order)==len(nodes)
save('FINAL_EVIDENCE_DEPENDENCY_GRAPH.json',{'nodes':list(nodes.values()),'edges':edges,'topological_order':order,'rank':rank,'acyclic':True,
 'scope_rule':'Choose current normal or failure-prefix realization; proposed A is a distinct pre-C11 scope. Pending B is not an implemented change to the old gate.',
 'candidate_cycles':g['candidate_cycles'],'raw_current_leaf_count':1082,'family_bound':K,
 'failure_prefix_rule':'Only evidence actually produced before failure is required; missing scheduled later tests remain UNRUN and prevent resource admission. Do not require F1/F4 output before failure seal.',
 'namespace_boundary':'Native ROOT, host CONTROL, source package, external post-seal certificates and research reports are separate collections.'})
save('FINAL_ANALYSIS_SUMMARY.json',{'raw_upper':K,'native_upper':K+1,'admin_originals_upper':K+2,'admin_zip_upper':K+17,
 'dependency_nodes':len(nodes),'edges':len(edges),'DAG_rank':max(rank.values()),'DAG_acyclic':True,
 'raw_bytes':'EVIDENCE_MAX_BOUND_UNRESOLVED','end_to_end_work':'EVIDENCE_MAX_BOUND_UNRESOLVED','normal_complete_lower':1082,
 'C_abort':16,'C_stop':23,'C_seal':7,'new_capacity_effective':False,'cross_rule_effective':False,'runtime_code_edits':0,'dynamic_tests':0})
print(json.dumps({'raw_upper':K,'native_upper':K+1,'admin_upper':K+2,'admin_zip_upper':K+17,'DAG_nodes':len(nodes),'rank':max(rank.values()),'bytes':'UNRESOLVED'}))
