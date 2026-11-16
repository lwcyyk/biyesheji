"""Author-authorized local adoption patches and thesis prose; no mechanism code."""
from pathlib import Path
from fractions import Fraction as F
import copy,difflib,hashlib,json
B=Path(r'D:\毕业设计');V=B/'crypto_fi_research_manuscript_v3';R=B/'crypto_fi_final_internal_review';O=B/'crypto_fi_adopted_release_v3_1'
TITLE='对FI已发表构造的来源隐藏密码分析，以及三组官方数值参数的一次更新可靠性分析'
ROLE='INFORMED_AUTHOR_ADOPTION_LOCAL_REVISION_AND_RESEARCH_RESULT_ARCHIVAL'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rec(p):
 b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def sh(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def rd(x):return F(int(x['numerator']),int(x['denominator']))
base=load(V/'CLAIM_EVIDENCE_MATRIX.json');m=copy.deepcopy(base);prov=load(R/'REVIEW_PROVENANCE.json');local=load(R/'evidence/LOCAL_SCOPE_CORRECTIONS.json')
selectors=load(O/'certificates/UNIFIED_RESULT_SELECTORS.json')
assert selectors['profiles']==base['official_profile_results']
assert prov['verdict']=='PASS_WITHIN_STATED_SCOPE'
assert prov['review_type']=='SINGLE_AI_COMPREHENSIVE_INTERNAL_REVIEW_AUTHOR_PROOF_AND_PRIOR_REVIEWS_VISIBLE'
identity=dict(status=ROLE,description_zh='知情作者采用、局部修订与研究结果归档',author_proofs_and_all_prior_positive_review_records_visible=True,final_internal_decision_visible=True,declared_model_family='Codex based on GPT-6 per visible developer context',exact_backend_model_id=None,exact_weights_version=None,new_comprehensive_internal_reviews=0,new_independent_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_blind_reviews=0,new_subagents=0,formal_proof_assistant_checks=0,model_error_process_independence_established=False,calibration='NOT_CALIBRATED')
m['schema']='frodo-fi-claim-evidence-matrix/v3.1-adopted';m['version']='v3.1';m['date_asia_shanghai']='2026-11-11'
m['inherited_v3_identity']=m['identity'];m['identity']=identity
m['inherited_action_counts_v3']=m['action_counts']
m['action_counts']=dict(local_scope_corrections_adopted=3,new_scalar_script_replays=0,new_deterministic_endpoint_consistency_comparisons=6,new_comprehensive_internal_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_blind_reviews=0,new_subagents=0,new_independent_error_process_certifications=0,formal_proof_assistant_checks=0,cryptographic_samples_generated=0,Monte_Carlo_runs=0,LWE_solver_implementations=0,candidate_mechanism_implementations=0,author_UE_executions=0,new_live_priority_searches=0,external_model_calls=0,author_contacts_or_messages=0,native_AS_RP_requests=0,historical_input_writes=0)
m['manuscripts']='CRYPTOANALYSIS_DRAFT.md; THESIS_ADOPTION.md; RELEASE_NOTES.md'
m['core_proof_status']='PASS_WITHIN_STATED_SCOPE adopted from final single-AI comprehensive internal review. A/B mathematical statements and all frozen exact/display payloads unchanged;L1-L3 registry scopes repaired. External software,conditional reduction,global-first and business-game mappings retain their stated evidence status.'
claims={c['id']:c for c in m['claims']}
original_claims={c['id']:copy.deepcopy(c) for c in base['claims']}
for entry in local['corrections']:
 c=claims[entry['claim_id']]
 for change in entry['changes']:
  field=change['json_pointer'].split('/')[-1]
  assert c[field]==change['old'],(entry['id'],field,c[field],change['old'])
  c[field]=copy.deepcopy(change['adopted'])
claims['C25b']['remaining_scope']=dict(official_profile_depths='Reliability at t>=2 or under nonfresh parent distributions needs its own residual/joint-law analysis;CF-1 correctness throughn updates is already proved under its separate growing-parameter contract',filtering_selection_reuse='Protocol-level rank/success filtering,retries,token selection/reuse or multiple correlated outputs require their induced joint laws;the existing final conditioning on initial correctness remains proved for the frozen original experiment',exact_full64='Current full-message row-containment upper bounds and separate all-zero lower witnesses are proved;exact64-coordinate joint success remains a precision question',software='All6 author UE configurations remain UNRESOLVED/WAITING_FOR_AUTHOR_ARTIFACT pending authenticated source,conditional secret-noise law,algorithm/arithmetic mapping or finite-loss transfer')
claims['C25b']['model_selectors']=[f'official_profile_results.{n}' for n in ['640','976','1344']]
claims['C25b']['semantic_distribution_inputs']=['chi640','chi976','chi1344']
claims['C25d']['precise_object']='Three proved finite ideal one-update high-error propositions for640/976/1344,each with its own exact distribution and separate fixed-A/uniform-Setup quantifier'
claims['C25d']['semantic_distribution_inputs']=['chi640','chi976','chi1344']
claims['C25d']['semantic_input_selectors']=[f'official_profile_results.{n}.{mode}' for n in ['640','976','1344'] for mode in ['fixed_A','uniform_Setup']]
claims['C25d']['theorem63_relation']=dict(sufficient_premise='W_print < q/(T*2^(B+1)),integerT>=1',profiles={'640':dict(W_print=22649448960,right_numerator=4096),'976':dict(W_print=32387837760,right_numerator=4096),'1344':dict(W_print=13265908992,right_numerator=2048)},meaning='All three fixed configurations lie outside the printed sufficient premise;the adopted probability theorems describe their actual ideal one-update behavior. The conditional theorem at a satisfied premise is separately evaluated.',author_software='WAITING_FOR_AUTHOR_ARTIFACT;all6 actual configurations require artifact-based correspondence')
claims['C24']['precise_object']='Search-bounded application value for the same frozen FI object:original-game source hiding and finite-profile one-update reliability,with mature tools attributed'
claims['C24']['limitations']='Global first unestablished;source/search coverage limited to inherited through2026-11-08,E13 through2026-11-10 andE15 receipts registered2026-11-11. Final internal review and this adoption add0 live priority searches;missing predecessor full/version evidence retains its stated scope.'
claims['C24']['evidence_status']='SEARCH_BOUNDED_APPLICATION_CANDIDATE'
for id in ['C24','C25b','C25d']:
 for source in (['E13','E15','E18'] if id=='C24' else ['E18']):
  if source not in claims[id]['source_ids']:claims[id]['source_ids'].append(source)
 claims[id]['review_identity_and_scope']='Final E18: SINGLE_AI_COMPREHENSIVE_INTERNAL_REVIEW_AUTHOR_PROOF_AND_PRIOR_REVIEWS_VISIBLE;PASS_WITHIN_STATED_SCOPE. Current E19: informed author adoption and local consistency checks,not a new mathematical review;exact backend IDs null and no human/cross-model/blind/formal/error-process-independence certification.'
m['priority_search_cutoff']='2026-11-11'
m['priority_search_cutoff_basis']='Latest inherited registered receipt date only;coverage is the explicit three-segment source/search chain,not a new exhaustive search.'
timeline=[dict(id='E3',through='2026-11-08',source=rec(B/'crypto_fi_original_game_decision/APPLICATION_PRIORITY_AUDIT.md'),scope='Inherited original-game application-priority audit and its actual source/receipt range'),dict(id='E13',through='2026-11-10',source=rec(B/'crypto_fi_publication_impact_audit/APPLICATION_PRIORITY_AND_IMPACT.md'),scope='Application/publication-impact audit;31 webpage queries and recorded repository routes within its actual coverage'),dict(id='E15',registered='2026-11-11',source=rec(B/'crypto_fi_official_profile_correctness/evidence/PUBLIC_PRECEDENT_SEARCH_RECEIPT.json'),scope='Six targeted queries and bibliographic checks as registered by the profile author package;no enlarged coverage inferred')]
m['priority_scope']=dict(timeline=timeline,inherited_original_game_cutoff='2026-11-08',historical_application_audit_cutoff='2026-11-10',newer_inherited_profile_queries_date='2026-11-11',newer_query_count_as_recorded=6,final_internal_review_new_live_priority_searches=0,new_network_searches_this_revision=0,global_priority='SEARCH_BOUNDED_APPLICATION_CANDIDATE',global_first_established=False)
claims['C24']['priority_scope_selector']='priority_scope.timeline'
m['adopted_publication_impact_audit']['role_in_current_time_chain']='E13 segment through2026-11-10;whole adopted priority chain additionally retains E3 through2026-11-08 andE15 registered2026-11-11'
claims['C27']['source_ids']+=['E18','E19'];claims['C27']['precise_object']+=';E18 final comprehensive single-AI internal review;E19 informed author adoption and archival'
claims['C52']['claim']='976/1344 targeted review identity and v3 exact replay scope (historical)'
claims['C53']['precise_object']=TITLE
claims['C53']['quantifiers']='Formally adopted for a thesis cryptanalysis chapter under PASS_WITHIN_STATED_SCOPE;possible independent paper contribution and editorial judgment retain external evaluation'
claims['C53']['source_ids']+=['E18','E19']
m['stage_verdict']=dict(adoption='PASS_WITHIN_STATED_SCOPE',passed_result_name=TITLE,theory='MATHEMATICAL_RESULTS_ACCEPTED_WITHIN_FROZEN_CONTRACTS',author_software='WAITING_FOR_AUTHOR_ARTIFACT',global_priority='SEARCH_BOUNDED_APPLICATION_CANDIDATE',global_first_established=False,business_mapping='SOURCE_OR_REFINEMENT_GAP / INDEPENDENT_CRYPTOANALYSIS_CHAPTER',nonempty_hardness_premise_counterexample='UNRESOLVED',current_stage='ADOPTED_V3_1_AND_ARCHIVED',external_reopen='Specific contract-respecting mathematical counterexample;formal target revision;dated same-object precedent;authenticated author UE artifact/trace;full parameterized FI reduction;new business-game mapping')
m['adoption_record']=dict(status='PASS_WITHIN_STATED_SCOPE',passed_result_name=TITLE,final_decision=rec(R/'FINAL_INTERNAL_DECISION.md'),review_provenance=rec(R/'REVIEW_PROVENANCE.json'),review_manifest=rec(R/'MANIFEST.json'),local_scope_corrections=rec(R/'evidence/LOCAL_SCOPE_CORRECTIONS.json'),review_type=prov['review_type'],reviewer=prov['reviewer'],exposure=prov['exposure'],review_scope=prov['scope'],historical_verification=prov['verification'],historical_review_action_counts=prov['action_counts'],current_author_adoption_identity=identity,mathematical_payload_changed=False,global_priority_searches_added=0)
m['candidate_mechanism_implementation_gate']=dict(state='SEPARATE_STRICT_GAP_INSTANCE_REQUIRED',before_implementation=['Concrete input family','Fixed metric','Strongest general method with the same capabilities','Predicted strict gap','At least one concrete instance where that general method necessarily pays higher cost'],current_new_candidate_implementations=0)
m['source_registry']['E18']=dict(files=[rec(R/x) for x in ['FINAL_INTERNAL_DECISION.md','REVIEW_PROVENANCE.json','MANIFEST.json','evidence/LOCAL_SCOPE_CORRECTIONS.json','evidence/FINAL_SCALAR_CHECKS.json','evidence/scalar_replay/REPLAY_RESULT.json']],identity=prov['review_type'],reviewer=prov['reviewer'],exposure=prov['exposure'],verdict=prov['verdict'],scope=prov['scope'],verification=prov['verification'],current_use='Formal author adoption andL1-L3 registry correction;no new review or replay claimed')
m['source_registry']['E19']=dict(identity=ROLE,scope='Current local author adoption,thesis writing,byte-identical certificate archive and six exact endpoint consistency comparisons',files=[rec(O/'evidence/CERTIFICATE_ARCHIVE.json')],new_scalar_script_replays=0,new_priority_searches=0)
m['source_registry']['G1_HANDOFF']=dict(file=rec(B/'research_g1_lifecycle_contract/2026-11-09_r01/08_G1_VERDICT_AND_MAINLINE_HANDOFF.md'),version='G1-2026-11-09-r01',current_read_scope='Full handoff read;LimitedNativePrototype,SourceOrRefinementGap,actual lifecycle interface andstrict mechanism gate used;no code/system operation')
m['source_registry_inheritance_note']='All prior records retain their historical identities and execution/reading scopes. E18 is the final single-AI comprehensive review;E19 is the current adoption. Current work changes only local registry/governance/prose adoption;frozen models,proofs and numeric payloads retain v3 identities.'

# Thesis probability tables are generated only from the accepted selector/matrix.
params='| 配置 | n | D | q | m̄=n̄ | B | χ | 消息位数 |\n|---|---:|---:|---:|---:|---:|---|---:|\n'
table='| 配置／消息位数 | 初始完整失败≤（逐A） | 更新完整正确≤（逐A，不平均A） | 更新完整错误≥（逐A） | 更新完整正确≤（均匀Setup，平均A） | 更新完整错误≥（均匀Setup） |\n|---|---:|---:|---:|---:|---:|\n'
bindings=[]
for n,p in selectors['profiles'].items():
 par=p['parameters'];fa=p['fixed_A']['display'];un=p['uniform_Setup']['display'];power=p['initial']['full_failure_power']
 params+=f"| {n} | {par['n']} | {par['D']} | {par['q']} | {par['mbar']} | {par['B']} | χ{n} | {par['message_bits']} |\n"
 table+=f"| {n}／{par['message_bits']} | 2^-{power} | {fa['row_full_upper']} | {fa['full_error_percent_lower'].rstrip('%')}% | {un['row_full_upper']} | {un['full_error_percent_lower'].rstrip('%')}% |\n"
 for mode in ['fixed_A','uniform_Setup']:
  v=p[mode];alpha=F(1,2**power);u=rd(v['full_correct_upper']);uc=rd(v['conditioned_on_initial']['full_correct_upper']);display=F(v['display']['row_full_upper'])
  assert uc==min(F(1),u/(1-alpha)) and u<=uc<=display
  assert 100*(1-display)==F(v['display']['full_error_percent_lower'].rstrip('%'))
  bindings.append(dict(profile=n,mode=mode,selector=f'profiles.{n}.{mode}',initial_full_failure_power=power,parameters=par,exact_upper=v['full_correct_upper'],exact_conditional_upper=v['conditioned_on_initial']['full_correct_upper'],display_upper=v['display']['row_full_upper'],display_error_percent=v['display']['full_error_percent_lower'].rstrip('%')+'%',validated_by_exact_rational_comparison=True))
core='本章对FI已发表的FrodoPKE型可更新加密构造开展具体密码分析。在声明的Ord规范化与精确独立χ640合同下，我们给出原rand-ind-eu-cpa游戏的合法来源隐藏攻击，并构造初始加密及最长n次更新逐样本正确的CF-1参数族，使攻击以至多3n+1次调用取得1−negl(λ)优势。进一步，对官方640、976、1344数值参数，我们从真实残差与两层条件环境建立参数化行矩判据，结合全平移PGF和全频率有向证书，证明一次诚实未筛选更新的完整消息高错误率，并分别给出逐固定A、均匀Setup及初始完整消息已正确条件下的界。本章贡献定位为具体构造密码分析、有限参数可靠性和证明范围审计，采用的代数、概率、Fourier及采样工具按成熟来源归属。'
template=(O/'evidence/THESIS_ADOPTION.template.md').read_text(encoding='utf-8')
thesis=template.replace('{{CORE_CONTRIBUTION}}',core).replace('{{PARAMETER_TABLE}}',params.rstrip()).replace('{{RELIABILITY_TABLE}}',table.rstrip())
assert '{{' not in thesis
(O/'THESIS_ADOPTION.md').write_text(thesis,encoding='utf-8')
dump(O/'evidence/THESIS_NUMERIC_BINDING.json',dict(schema='frodo-fi-v31/thesis-numeric-binding/1',source_selector=rec(V/'certificates/UNIFIED_RESULT_SELECTORS.json'),archive_selector=rec(O/'certificates/UNIFIED_RESULT_SELECTORS.json'),source_matrix=rec(V/'CLAIM_EVIDENCE_MATRIX.json'),complete_profiles_equal=True,parameter_table=params,reliability_table=table,six_endpoint_comparisons=bindings,core_contribution=core))

# Exact prose patches: theorem/proof material remains unchanged after path normalization.
old=(V/'CRYPTOANALYSIS_DRAFT.md').read_text(encoding='utf-8-sig');draft=old;ops=[]
def change(a,b,why):
 global draft
 assert draft.count(a)==1,(why,draft.count(a));draft=draft.replace(a,b);ops.append(dict(reason=why,old_text=a,new_text=b,old_sha256=sh(a),new_sha256=sh(b)))
def paragraph(prefix,new,why):
 x=[p for p in draft.split('\n\n') if p.startswith(prefix)];assert len(x)==1,(prefix,len(x));change(x[0],new,why)
paragraph('研究稿v3，','正式采用版v3.1，2026-11-11（Asia/Shanghai）。身份：知情作者采用、局部修订与研究结果归档（'+ROLE+'）。通过成果名称为“'+TITLE+'”，采用裁决为**PASS_WITHIN_STATED_SCOPE**。[E18]最终内部裁决已核准A/B；本版落实L1—L3、形成毕业论文采用文本并归档，所有定理、精确端点及显示数字保持v3载荷。冻结对象仍为DOI **10.46298/fi.14425**、arXiv:2410.03948v4打印算法。','正式采用身份与状态')
change('> **v3修订说明。**','> **v3历史整合说明。**','历史整合记录归属')
change('## 摘要','> **v3.1采用说明。** L1统一C25b三组冻结一次更新合同；L2统一C25d对象、前提、三分布选择器、PROVED_UNDER_STATED_MODEL状态及Theorem6.3/软件范围；L3统一11月8日、E13截至11月10日、E15登记11月11日的优先权链。最终内审与本轮采用新增优先权检索均为0。数学证书已按原字节归档，本轮完成六个精确端点一致性比较，新增标量脚本重放0次。正文所述v3及更早重放按其历史执行解释。[采用文本](D:/毕业设计/crypto_fi_adopted_release_v3_1/THESIS_ADOPTION.md)、[采用说明](D:/毕业设计/crypto_fi_adopted_release_v3_1/RELEASE_NOTES.md)及本版MANIFEST固定采用链。\n\n## 摘要','采用说明与局部修正范围')
paragraph('应用优先权沿用[E13]截至2026-11-10的实际审计，','应用优先权按三段实际时间链采用：截至2026-11-08的既有审计[E3]、E13截至2026-11-10的应用与发表影响核查、E15登记2026-11-11的六条定向查询回执。已核材料内，同FI对象、同权限与完整等价命题的直接先例尚未定位，状态为SEARCH_BOUNDED_APPLICATION_CANDIDATE，全球首次保持待证。最终内部审阅[E18]和本轮采用[E19]新增联网优先权搜索均为0。KLR2019公开token一致性、官方基础PKE失败分析及成熟概率/Fourier工具保持其方法归属；Nishimaki与CJL的版本缺项各按原证据范围保留。','L3正文时间链')
paragraph('故本文可作为主论文的独立密码分析章节或核心案例：','本版将该成果正式采用为主论文的独立密码分析章节及组件选用案例。主系统的部署、权限与撤回安全继续由确认合同和工程证据承担；FI钥匙/token权限、来源隐藏需求与业务状态观察之间的游戏映射，由新增业务需求及保持证明建立。候选保护机制的实现资格另按严格差距实例要求核准。[E18]','主任务采用定位')
paragraph('本文的阶段定位为**已发表UE构造的来源隐藏密码分析与三组官方参数可靠性分析**，','本版通过成果为“'+TITLE+'”，正式采用裁决PASS_WITHIN_STATED_SCOPE。A/B的精确对象、量词、自含证明和有限证书已完成最终单一AI综合内部验收；本版据此采用为毕业论文独立密码分析章节。外部人工领域判断、投稿适配与发表决定保留各自证据责任。数学三尺寸覆盖与作者程序映射分别登记。[E18,E19]','采用后的贡献定位')
paragraph('理论阶段裁决为**THEORETICAL_RESULTS_INTEGRATED_AND_READY_FOR_HUMAN_CRYPTOGRAPHIC_REVIEW**。','正式采用状态为**PASS_WITHIN_STATED_SCOPE**，本阶段结果归档为ADOPTED_V3_1_AND_ARCHIVED。共同正确族的原游戏攻击与三组官方参数的一次更新可靠性均在冻结合同内通过。v3的9196/3194项及最终内审7个入口、11份完整载荷比较按历史执行引用；本轮采用新增标量重放0次，六个端点作精确一致性比较。人工、跨模型、盲审、形式化及模型错误过程独立性认证按原记录保留。后续判断由下表所列具体新材料触发。[E18,E19]','最终阶段归档状态')
paragraph('本文由知情AI整合，人工密码学同行意见待取得。','本文的最终内部采用依据为[E18]的PASS_WITHIN_STATED_SCOPE，身份为SINGLE_AI_COMPREHENSIVE_INTERNAL_REVIEW_AUTHOR_PROOF_AND_PRIOR_REVIEWS_VISIBLE。作者证明、用户目标、历史摘要及原核对代码可见；单独历史意见在初步判断后读取。精确后端ID、权重及turn ID为null，原会话01a1c951-f315-7fe2-8cf8-ec84f397d959；人工、跨模型、盲审、证明助手和模型错误过程独立性新增认证均为0。本版[E19]为知情作者采用与归档，新增综合数学审查0。当前主张及范围以[CLAIM_EVIDENCE_MATRIX.json](D:/毕业设计/crypto_fi_adopted_release_v3_1/CLAIM_EVIDENCE_MATRIX.json)为准。','最终审阅身份与采用角色')
change('**数据可用性与研究声明。**','**v3.1采用与局部修订。** 最终内审L1—L3已在本版主张矩阵逐字段采用；C25d为PROVED_UNDER_STATED_MODEL，三组冻结一次更新合同与软件/源充分前提关系明确。所有数学载荷和证明保持v3，当前六个精确端点比较及证书归档只承担一致性与字节身份。优先权三段时间链、实际审阅身份、旧/新值与重开条件见RELEASE_NOTES。[E18,E19]\n\n**数据可用性与研究声明。**','本版采用来源注记')
for oldroot,newroot in [(V/'certificates',O/'certificates')]:
 count=draft.count(oldroot.as_posix()+'/');draft=draft.replace(oldroot.as_posix()+'/',newroot.as_posix()+'/')
 ops.append(dict(reason='当前数学归档链接重定位',old_prefix=oldroot.as_posix()+'/',new_prefix=newroot.as_posix()+'/',replacements=count,bytes_of_targets_identical=True))
ref='''
- **[E18]** 最终内部验收：[FINAL_INTERNAL_DECISION.md](D:/毕业设计/crypto_fi_final_internal_review/FINAL_INTERNAL_DECISION.md)、[REVIEW_PROVENANCE.json](D:/毕业设计/crypto_fi_final_internal_review/REVIEW_PROVENANCE.json)、MANIFEST及LOCAL_SCOPE_CORRECTIONS，2026-11-11。PASS_WITHIN_STATED_SCOPE；SINGLE_AI_COMPREHENSIVE_INTERNAL_REVIEW_AUTHOR_PROOF_AND_PRIOR_REVIEWS_VISIBLE；实际曝光、7个入口/11份载荷比较及六端点核对按原记录，精确后端ID为null。
- **[E19]** v3.1知情作者采用、局部修订与归档：[THESIS_ADOPTION.md](D:/毕业设计/crypto_fi_adopted_release_v3_1/THESIS_ADOPTION.md)、[RELEASE_NOTES.md](D:/毕业设计/crypto_fi_adopted_release_v3_1/RELEASE_NOTES.md)及本版MANIFEST，2026-11-11。L1—L3已采用，数学载荷保持，新增数学审阅、标量脚本重放和优先权搜索均为0。
'''
idx=draft.index('<!--priority-scope:');draft=draft[:idx]+ref+'\n<!--priority-scope: E3截至2026-11-08；E13截至2026-11-10；E15登记2026-11-11；最终内审和v3.1采用新增检索0；全球首次待证。-->\n'
(O/'CRYPTOANALYSIS_DRAFT.md').write_text(draft,encoding='utf-8')
def normalize(s):return s.replace((O/'certificates').as_posix()+'/',(V/'certificates').as_posix()+'/')
theory_same=old[old.index('## 2. '):old.index('## 10. ')]==normalize(draft[draft.index('## 2. '):draft.index('## 10. ')])
appendices_same={x:old.split('## 附录'+x,1)[1].split('## 附录'+y,1)[0]==normalize(draft.split('## 附录'+x,1)[1].split('## 附录'+y,1)[0]) for x,y in [('A','B'),('B','C'),('D','E'),('E','F'),('F','G')]}
assert theory_same and all(appendices_same.values())
(O/'evidence/MANUSCRIPT_ADOPTION.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),draft.splitlines(True),fromfile=str(V/'CRYPTOANALYSIS_DRAFT.md'),tofile=str(O/'CRYPTOANALYSIS_DRAFT.md'))),encoding='utf-8')
dump(O/'evidence/MANUSCRIPT_PATCH_LEDGER.json',dict(authority='User explicitly adopts final internal decision andL1-L3,with thesis writing and archival;targeted exact patches only',base=rec(V/'CRYPTOANALYSIS_DRAFT.md'),adopted=rec(O/'CRYPTOANALYSIS_DRAFT.md'),operations=ops,theorem_sections_2_to_9_unchanged_after_link_normalization=theory_same,proof_appendices_unchanged_after_link_normalization=appendices_same,ARS_scope='Inline source-bound local patch principles;no claim of full ARS schema authorization certification'))
m['v3_1_corrections']=[dict(id=x['id'],claim_id=x['claim_id'],status='CLOSED_IN_ADOPTED_RELEASE',source=rec(R/'evidence/LOCAL_SCOPE_CORRECTIONS.json'),source_decision_section='FINAL_INTERNAL_DECISION §7',adopted_location='CLAIM_EVIDENCE_MATRIX.json claim '+x['claim_id']) for x in local['corrections']]
dump(O/'CLAIM_EVIDENCE_MATRIX.json',m)
field_changes=[]
def diffs(a,b,path=''):
 if a==b:return
 if isinstance(a,dict) and isinstance(b,dict):
  for k in sorted(a.keys()|b.keys()):
   q=path+'/'+k.replace('~','~0').replace('/','~1')
   if k not in a:field_changes.append(dict(json_pointer=q,operation='add',new=b[k]))
   elif k not in b:field_changes.append(dict(json_pointer=q,operation='remove',old=a[k]))
   else:diffs(a[k],b[k],q)
 elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b) and all(isinstance(x,dict) for x in a+b):
  for i,(x,y) in enumerate(zip(a,b)):diffs(x,y,path+'/'+str(i))
 else:field_changes.append(dict(json_pointer=path,operation='replace',old=a,new=b))
diffs(base,m)
dump(O/'evidence/MATRIX_ADOPTION_PATCH.json',dict(base=rec(V/'CLAIM_EVIDENCE_MATRIX.json'),adopted=rec(O/'CLAIM_EVIDENCE_MATRIX.json'),changes=field_changes,all_frozen_models_unchanged=base['frozen_models']==m['frozen_models'],all_official_profiles_unchanged=base['official_profile_results']==m['official_profile_results'],all_parametric_criterion_unchanged=base['parametric_criterion']==m['parametric_criterion']))
adopted=[]
for entry in local['corrections']:
 id=entry['claim_id'];before=original_claims[id];after=claims[id]
 adopted.append(dict(id=entry['id'],claim_id=id,status='CLOSED_IN_ADOPTED_RELEASE',source_decision=rec(R/'FINAL_INTERNAL_DECISION.md'),source_local_corrections=rec(R/'evidence/LOCAL_SCOPE_CORRECTIONS.json'),required_exact_changes=entry['changes'],all_changed_claim_fields=[dict(field=k,old=before.get(k),new=after.get(k)) for k in sorted(before.keys()|after.keys()) if before.get(k)!=after.get(k)]))
dump(O/'evidence/LOCAL_SCOPE_ADOPTION.json',dict(adoption_status='PASS_WITHIN_STATED_SCOPE',passed_result_name=TITLE,corrections=adopted,priority_top_level_changes=[v for v in field_changes if v['json_pointer'].startswith(('/priority_search_cutoff','/priority_scope','/adopted_publication_impact_audit/role'))],theorems_or_numerical_endpoints_changed=False))

notes='''# Frodo-FI正式采用版v3.1：采用说明与阶段归档

2026-11-11，Asia/Shanghai。当前身份：知情作者采用、局部修订与研究结果归档（INFORMED_AUTHOR_ADOPTION_LOCAL_REVISION_AND_RESEARCH_RESULT_ARCHIVAL）。

## 1. 正式采用状态

采用裁决：**PASS_WITHIN_STATED_SCOPE**。通过成果名称：**对FI已发表构造的来源隐藏密码分析，以及三组官方数值参数的一次更新可靠性分析**。

本版按最终内部裁决完成作者采用，阶段状态ADOPTED_V3_1_AND_ARCHIVED。影响核心A/B的已识别未决数学依赖为0；定理、完整证明、全部精确端点及显示数字保持v3。毕业论文采用文本已提供，独立密码分析章节及组件选用案例的定位正式登记。外部软件、条件归约、全球优先权与业务游戏映射按其实际状态保留。

## 2. L1—L3逐字段闭合

| 修正/字段 | v3旧值 | v3.1采用值及位置 | 依据/状态 |
|---|---|---|---|
| L1 C25b.assumptions | Current proof fixed640 and one update | 三组640/976/1344各自冻结的一次更新合同；深度、筛选/复用、精确64坐标和软件迁移各需自身分析 | 最终裁决§7及LOCAL_SCOPE_CORRECTIONS L1；CLOSED |
| L1 C25b.remaining_scope | 原行仅以统合文字列留项 | 明列官方有限参数t≥2、协议筛选/重试/复用、跨行精确概率和六配置软件；CF-1最长n次正确性已经通过 | 主张C25b、正文§7.4–7.5/§10；CLOSED |
| L2 C25d.evidence_status | COUNTEREXAMPLE_FOUND | PROVED_UNDER_STATED_MODEL | 最终裁决§§2/4/7；CLOSED |
| L2 C25d.assumptions | Probability and conditioning in C25a | 三组各自精确χ、同A两代、Ord/Tensor、一次诚实未筛选TG/Upd、半向上Decode，量词与I条件化分别绑定 | C25d及六个official_profile_results选择器；CLOSED |
| L2 C25d.limitations | Theorem6.3 sufficient premise unmet; finite640 behavior… | 三个分别冻结的有限一次更新配置；源充分前件均未满足；作者软件迁移仍待工件 | C25d、正文§7.4–7.5；CLOSED |
| L2 C25d语义输入 | semantic_distribution_inputs=[chi640]；semantic_input_selectors=[C25a] | [chi640,chi976,chi1344]及三尺寸×固定A/均匀Setup六个选择器 | 对象/前提/输入同步，数学载荷保持；CLOSED |
| L3 C24.quantifiers | Bounded historical search through2026-11-08 | 截至11月8日继承审计＋E13截至11月10日＋E15登记11月11日；最终内审新增0检索，全球首次待证 | 最终裁决§§6–7；CLOSED |
| L3顶层priority_search_cutoff | 2026-11-10 | 2026-11-11，仅表示最新继承登记回执日期；完整覆盖按三段时间链解释 | priority_scope.timeline与C24一致；CLOSED |
| L3全球优先权状态 | 顶层UNRESOLVED、C24候选状态 | 统一SEARCH_BOUNDED_APPLICATION_CANDIDATE，global_first_established=false | 未增加覆盖；本轮采用新增检索0；CLOSED |

逐项完整旧/新值、来源及JSON指针见[evidence/LOCAL_SCOPE_ADOPTION.json](evidence/LOCAL_SCOPE_ADOPTION.json)；全部机器字段差分见[evidence/MATRIX_ADOPTION_PATCH.json](evidence/MATRIX_ADOPTION_PATCH.json)。正文同步采用状态、优先权链和业务定位，数学段落只重定位到字节相同的本版证书副本。§§2—9及附录A/B/D/E/F证明在路径规范化后与v3文本相同。

## 3. 已采用的命题与概率对象

A：CF-1在λ≥2、n=8λ、D=8ceil(log₂n)、q=2^D、m̄=n̄=8、B=2、精确独立χ640、同A和Ord_n合同内，初始至最长n次更新逐样本正确；原游戏≤3n+1次调用，Δ→1。

B：三组官方数值参数在各自精确χ、同A两代、Ord_n、一次诚实未筛选TG/Upd及半向上Decode合同内，对任意预先固定合法消息，一次更新高错误率通过。两种A量词、128/192/256消息位数及初始已正确条件化分别携带。

'''+table+'''
该表直接由已通过的统一选择器生成。六个U/(1−α)精确分数向外比较均通过，本轮只作一致性核对，新增标量脚本重放0次。完整正确上界来自指定行事件包含；行下界与完整正下界各用其证明。来源事件ε与更新解码失败分别引用其定理。

Theorem6.3的三组打印左端分别22649448960、32387837760、13265908992，右端4096/T、4096/T、2048/T，整数T≥1均处于充分前件之外。已采用命题评价这些实例的模型内一步概率；源条件定理在前件成立域的关系分别评价。Theorem6.9沿用精确LWE审计：CF-1丰富独立同秘密样本前件失效，固定n/3n接口及FI完整参数化归约待核。

## 4. 最终审阅身份及当前采用身份

最终内审准确身份为**SINGLE_AI_COMPREHENSIVE_INTERNAL_REVIEW_AUTHOR_PROOF_AND_PRIOR_REVIEWS_VISIBLE**，裁决PASS_WITHIN_STATED_SCOPE。一个Codex上下文，声明家族为基于GPT-6；精确后端模型ID、权重版本和turn ID为null。chat_id为01a1c951-f315-7fe2-8cf8-ec84f397d959，由其原记录的CODEX_THREAD_ID识别。

作者证明、目标和历史正面摘要从初段可见；单独历史意见在初步判断后读取，原核对代码也在此前进入标量重放。fresh_proof_blind_review=false，模型错误过程独立性未认证，经验校准NOT_CALIBRATED。该轮新增综合AI审阅1；人工、跨模型、盲审、子代理、证明助手和独立错误过程认证均为0。七个标量入口、十一份完整载荷比较及六端点直接重建按原执行范围引用。

本轮为知情作者采用、局部修订与归档，新增综合数学审查0，精确后端ID/权重按可见证据为null。新增人工、跨模型、盲审、形式化、模型错误过程独立性认证及外部模型调用均为0。原9196/3194/385/303等检查与最终7入口各按历史身份引用，本轮未重跑这些标量脚本。

## 5. 优先权时间链与方法归属

1. 截至2026-11-08：E3的原游戏应用优先权审计，使用其实际核读、历史查询与新增路线。
2. 截至2026-11-10：E13应用/发表影响审计，新增31条网页查询及其登记的仓库/issue路线按原回执解释。
3. 登记2026-11-11：E15的六条定向查询与题录核对，保持该包实际返回/读取范围。

最终内部审阅新增联网优先权检索0，本轮采用新增0。状态SEARCH_BOUNDED_APPLICATION_CANDIDATE，全球首次待证；数据库引用数、搜索未命中和全文缺失各保留其证据含义。new_metadata_check_date=2026-11-10是继承的题录核对日期，分别于最新回执日期解释。

KLR公开token一致性与分布匹配、官方Frodo初始残差/卷积、AG/CJL有界误差路线及经典Fourier、Chernoff、Cauchy–Schwarz、弦线/Jensen按成熟来源归属。采用成果的增量在于具体FI对象的原游戏、真实分布、共同正确性和三参数可靠性证明。独立论文发表和外部领域贡献评价各自处理。

## 6. 历史对应、数学载荷与归档执行

v3五份核心文件及原MANIFEST固定为本版底稿；最终内审三份主文件与LOCAL_SCOPE_CORRECTIONS提供采用权威。两份源清单的规范化载荷哈希和全部实际引用指纹匹配。当前归档复制v3 certificates整树21个文件，逐字节一致；脚本、JSON内部的历史路径字符串保留原身份，当前副本位置由归档映射记录。

输入快照覆盖55个直接文件及其引用，4,100条嵌入路径/指纹核验均匹配，锁定836个唯一历史文件。指纹、机器解析与语义阅读分别登记。当前语义阅读以最终裁决/溯源/局部修正、v3对应主张与章节、统一数值选择器、优先权时间链及G1实际交接为范围；数学完整复核和原图阅读沿最终内审原记录引用。

当前执行包括局部文档补丁、论文采用写作、证书字节归档及六个有理端点比较；钥匙/密文/token抽样、Monte Carlo、LWE求解、候选保护机制实现、作者UE运行、作者联系和原生AS/RP请求均为0。终检与全部输出字节身份以MANIFEST及evidence/DOCUMENT_QA.json为准。

## 7. 外部事项与具体重开条件

| 新输入 | 核验入口与必要判据 | 可改变的判断 |
|---|---|---|
| 满足冻结合同的数学反例或击中关键推导的明确错误 | 指明目标版本、参数、A/消息时序、合法游戏/支持样本或概率不等式；对概率界给相关联合律与违反依据 | A/B证明、特定证书或适用范围；单次轨迹只承担其路径事实 |
| 改变算法、游戏、参数或类型解释的正式修订 | 固定版本/日期/哈希，逐式比较四块、更新、Ord及游戏权限 | 目标对象和新版本适用性 |
| 同对象、日期可核的直接先例 | 完整原文、公开日期、同构造/权限/事件/参数及高效直接推导对应 | 方法归属、应用优先权及贡献定位 |
| 认证作者UE工件与消息比对轨迹 | 论文/作者/机构关联的不可变commit/archive；配置、依赖、随机流、同A、TG/Upd、Ord、筛选和算术；含原消息及两次比较的未筛选轨迹 | 六配置MAPPED/DIFFERS/UNRESOLVED及有限损失软件迁移 |
| FI完整参数化归约及版本化前驱 | 同秘密样本数、χ/秘密先验、全部辅助视图、时间/对手、abort和损失 | 精确困难前提及条件安全蕴含；固定n/3n范围 |
| 新业务需求与游戏映射 | 明确来源隐藏需求、钥匙/token权限及实际状态/观察到游戏的保持证明 | 从独立密码分析章节连接到具体业务合同 |
| 外部人工领域意见或六配置性能日志 | 提出逐式/逐对象判断；计时日志含原100次、预处理/缓存、消息检查和分母 | 外部可信范围、发表评价及原性能实验解释 |

当前软件保持WAITING_FOR_AUTHOR_ARTIFACT，全球首次待证，已认证非空困难前提下的条件安全反例资格为UNRESOLVED，业务游戏映射为SOURCE_OR_REFINEMENT_GAP。更多官方参数更新深度、筛选/复用和精确64坐标概率按新命题开展；当前已采用结果保持自己的依赖闭包。

候选保护机制的实现资格继续单列：具体输入族＋固定指标＋同能力最强通用方法＋预测严格差距，并先构造至少一个该通用方法必须承担更高代价的实例。本轮文档/有限一致性工作未引入候选密码机制实现。

## 8. 采用文件与引用入口

- [CRYPTOANALYSIS_DRAFT.md](CRYPTOANALYSIS_DRAFT.md)：正式采用的自含稿件，证明及数学载荷保持。
- [CLAIM_EVIDENCE_MATRIX.json](CLAIM_EVIDENCE_MATRIX.json)：L1—L3逐字段采用、优先权链及最终身份。
- [THESIS_ADOPTION.md](THESIS_ADOPTION.md)：研究问题、贡献、两定理、结果表、方法来源、局限、小结及主任务定位。
- [MANIFEST.json](MANIFEST.json)：输入、全部输出、归档与采用状态的封存清单。
- [最终内部裁决](D:/毕业设计/crypto_fi_final_internal_review/FINAL_INTERNAL_DECISION.md)、[溯源](D:/毕业设计/crypto_fi_final_internal_review/REVIEW_PROVENANCE.json)、[局部采用原文](D:/毕业设计/crypto_fi_final_internal_review/evidence/LOCAL_SCOPE_CORRECTIONS.json)。
'''
(O/'RELEASE_NOTES.md').write_text(notes,encoding='utf-8')
print(json.dumps(dict(status='PASS_WITHIN_STATED_SCOPE',version='v3.1',corrections=3,claims=len(m['claims']),frozen_numeric_payload_unchanged=base['official_profile_results']==m['official_profile_results'],six_endpoint_comparisons=len(bindings),changed_matrix_fields=len(field_changes),proof_sections_unchanged=theory_same),ensure_ascii=False))
