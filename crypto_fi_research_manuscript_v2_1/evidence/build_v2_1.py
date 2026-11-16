"""Author manuscript erratum and deterministic evidence integration only."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime,timezone,timedelta
import json,hashlib,re,copy,sys
sys.set_int_max_str_digits(0)
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(r'D:\毕业设计');OUT=BASE/'crypto_fi_research_manuscript_v2_1';EV=OUT/'evidence';V2=BASE/'crypto_fi_research_manuscript_v2';V1=BASE/'crypto_fi_research_manuscript_v1';AUD=BASE/'crypto_fi_publication_impact_audit'
def read(p):return Path(p).read_text('utf-8-sig')
def jd(p):return json.loads(read(p))
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def rec(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def link(p,label=None):return '['+(label or Path(p).name)+']('+str(p).replace('\\','/')+')'
def text_sha(s):return hashlib.sha256(s.encode()).hexdigest()

r=jd(EV/'REPLAY_976.json');tables=jd(EV/'DISTRIBUTION_TABLES.json');laws=tables['profiles']
assert r['all_checks_passed'] and r['convolution']['all_coefficients_match'] and r['probability']['epsilon_le_2_to_minus1118']
draft=read(V2/'CRYPTOANALYSIS_DRAFT.md')
original=draft
oldrow='| 976 | 11278,10277,7774,4882,2545,1131,426,138,38,8,1 |'
newrow='| 976 | '+','.join(map(str,laws['976']['mass_zero_then_each_signed_value']))+' |'
assert draft.count(oldrow)==1
draft=draft.replace(oldrow,newrow,1)
draft=draft.replace('研究稿v2，2026-11-10。作者修订、证明整合与学术写作；已审阅640概率结果并入版。','研究稿v2.1，2026-11-10。作者勘误、影响范围审计与确定性证书重放；INC976勘误及976证书闭合版。',1)
note='''
> **v2.1勘误说明（INC976）。** v2附录B的χ976显示行中，±5至±9的分子应由1131、426、138、38、8更正为1101、396、118、29、6，分母65536；其余显示点保持。发现来源为2026-11-10发表影响审计INC976，依据为官方2021/2023质量表、CDF及严格阈值采样规则。本版从正确CDF重新生成64重整数卷积，全部1281个系数与旧证书匹配，ε₉₇₆≤2^-1118经精确整数比较核准。两个主结果仅依赖χ640。完整逐点差异、依赖追踪与复算位置见 ERRATUM_LINK。

'''.replace('ERRATUM_LINK',link(OUT/'ERRATUM_AND_CERTIFICATE_AUDIT.md'))
draft=draft.replace('\n## 摘要\n',note+'## 摘要\n',1)
draft=draft.replace('## 附录B　有限误差表与电子证书的重放规范\n','## 附录B　有限误差表与电子证书的重放规范\n\n### B.1 CDF、显示质量与版本对应\n',1)
masspara=r'''

本表与电子输入建立逐项对应：令T为完整官方CDF，采样字r∈{0,…,65535}，t=r>>1，符号位为r mod2，绝对值e=Σ_(j=0)^(s−1)1[t>T(j)]。由严格比较及闭端点区间可得

\[
\chi(0)=\frac{2(T(0)+1)}{65536},\qquad
\chi(+j)=\chi(-j)=\frac{T(j)-T(j-1)}{65536}\quad(1\le j\le s).
\tag{B1}
\]

T(s)=32767是15位t的末端合同，循环仅访问T(0),…,T(s−1)。采样规则对应官方2021 PDF15–16 §2.2.4/Algorithm5及2023物理PDF8（印刷4）§7.4。质量表对应2021 PDF25 Table3及2023物理PDF15（印刷11）TableA.3。2021版由§2.2.4的CDF—质量公式及质量表重建数值CDF；640/976的直接CDF印表定位为2023物理PDF16（印刷12）TableA.4。1344的CDF采用[S10]于2024-11-27确认的勘误：T(5)=32765、T(6)=32767；2023旧版CDF印表缺项按历史版本保留。

| χ | 总质量分子 | 整数支持 | 偶数质量分子 | 奇数质量分子 | 最大原子 |
|---|---:|---|---:|---:|---|
| 640 | 65536 | [−12,12]，25点 | 32768 | 32768 | 1161/8192，唯一在0 |
| 976 | 65536 | [−10,10]，21点 | 32768 | 32768 | 5639/32768，唯一在0 |
| 1344 | 65536 | [−6,6]，13点 | 32770 | 32766 | 9143/32768，唯一在0 |

三表分母均65536且对称。本版逐一穷举每种CDF的65536个输入字，输出频数与式(B1)、原始质量表和旧证书生成输入逐点相同；本版实际显示行另经解析核对。机器对应见 TABLES_LINK 及主张矩阵distribution_table_binding。此次完整64重卷积与ε重算范围为976；640/1344沿用原卷积及概率证据，同时完成上述输入一致性检查。

### B.2 976完整重放与既有概率证书

χ976官方CDF固定为[5638,15915,23689,28571,31116,32217,32613,32731,32760,32766,32767]。以正确21点整数质量从p₀(0)=1递推64步，所得偏移−640、全部1281个系数、分母65536^64及总质量逐项匹配旧文件；唯一峰值在0，亦等于32重系数的平方和。q=65536>2·10·64=1280保证支持[−640,640]映入模群时逐点无合并。

置M为整数峰值、μ₆₄=M/65536^64，a=5639/32768，则

\[
\varepsilon_{976}=\binom{976}{63}a^{913}+(21\mu_{64})^{976}\le2^{-1118}.
\tag{B2}
\]

计算使用公共分母2^999424，比较整数N=binom(976,63)·11278^913·2^984816+(21M)^976与2^998306，结果N≤2^998306。完整M、重建系数、每阶段质量、整数比较身份与复算脚本见 REPLAY_LINK、COEFF_LINK 和 SCRIPT_LINK。ε是来源区分中真实fresh误接受事件的上界，976的解码可靠性仍属于§7.3的独立问题。
'''
masspara=masspara.replace('TABLES_LINK',link(EV/'DISTRIBUTION_TABLES.json')).replace('REPLAY_LINK',link(EV/'REPLAY_976.json')).replace('COEFF_LINK',link(EV/'chi_976_64fold_coefficients.json')).replace('SCRIPT_LINK',link(EV/'replay_976_and_check_tables.py'))
lastrow='| 1344 | 18286,14320,6876,2023,364,40,2 |'
assert draft.count(lastrow)==1
draft=draft.replace(lastrow+'\n',lastrow+'\n'+masspara+'\n',1)
# Route976 coefficients to the newly regenerated, byte-identical replay copy.
draft=draft.replace('D:/毕业设计/crypto_fi_research_manuscript_v1/sources/chi_976_64fold_coefficients.json',str(EV/'chi_976_64fold_coefficients.json').replace('\\','/'))
draft=draft.replace('总证书中的历史绝对路径作为来源标记保留；本版通过绝对本地路径引用v1冻结副本，按所列哈希对应。附录D的新增概率证书同样引用历史只读文件，复核输出写入临时目录。','总证书中的历史绝对路径作为来源标记保留；640/1344和总证书引用v1冻结副本，976引用本版重建且与旧文件逐字节相同的副本，按所列哈希对应。附录D的概率证书继续引用历史只读文件，复核输出写入指定新目录。')
draft=draft.replace('976/1344和更深更新、实际软件迁移','976/1344的更新解码可靠性、更深更新、实际软件迁移')
draft=draft.replace('该投影所指574字节environment.json哈希于本轮复核一致','该投影所指574字节environment.json哈希于v1/v2编稿阶段复核一致')
draft=draft.replace('**640概率审阅及本版整合。**','**640概率审阅及v2整合。**')
draft=draft.replace('本版身份为INFORMED_AUTHOR_REVISION_PROOF_INTEGRATION_AND_ACADEMIC_WRITING；作者稿与两次审阅全部可见。沿用v1行文和原有附录A的证明范围，当前确定性副本重放303项检查通过，结果与[E8]完整重算JSON相等；这登记为已知脚本重放。精确运行模型ID按当前可见记录为null，新增独立审阅、人工、跨模型、盲审、子代理及证明助手计数为0。','v2作者整合阶段的身份为INFORMED_AUTHOR_REVISION_PROOF_INTEGRATION_AND_ACADEMIC_WRITING；当时作者稿与两次审阅全部可见。该阶段沿用v1行文和原有附录A的证明范围，已知脚本副本重放303项检查通过，结果与[E8]完整重算JSON相等。该阶段精确运行模型ID为null，新增独立审阅、人工、跨模型、盲审、子代理及证明助手计数为0；v2.1当前执行范围另列如下。')
draft=draft.replace('本版四份文件、冻结来源、作者标量脚本和精确证书的访问路径与字节身份由MANIFEST固定','本版五份核心文件、冻结来源、作者标量脚本、976重放程序与精确证书的访问路径和字节身份由MANIFEST固定')
draft=draft.replace('仅交付四份v2文件，电子来源从历史只读路径引用。','本版交付五份核心文件，电子来源从历史只读路径及本版evidence目录引用。')
draft=draft.replace('D:/毕业设计/crypto_fi_research_manuscript_v2/CLAIM_EVIDENCE_MATRIX.json',str(OUT/'CLAIM_EVIDENCE_MATRIX.json').replace('\\','/'))
identity_note='''
**v2.1作者勘误与证书重放。** 本版身份为AUTHOR_ERRATUM_IMPACT_AUDIT_AND_DETERMINISTIC_CERTIFICATE_REPLAY。作者稿、两轮概率审阅、INC976及用户提供的既有复算结论均可见。本轮以公开采样规则、冻结CDF和新执行的确定性程序闭合976显示与证书对应，新增独立审阅、人工、跨模型、盲审、子代理与证明助手认证均为0。精确后端模型ID按可见记录为null。旧概率审阅及应用优先权状态按原身份和检索范围保留，作者程序与完整FI归约仍待外部材料。

'''
draft=draft.replace('**数据可用性与研究声明。**',identity_note+'**数据可用性与研究声明。**',1)
eref='\n- **[E9]** v2.1作者勘误与确定性重放：'+link(OUT/'ERRATUM_AND_CERTIFICATE_AUDIT.md')+'、'+link(EV/'REPLAY_976.json')+'及'+link(EV/'DISTRIBUTION_TABLES.json')+'，2026-11-10。INC976已闭合；976完整卷积与ε重算，640/1344输入一致性按实际执行范围登记。\n'
sref='- **[S11]** FrodoKEM. *Preliminary Standardization Proposal*，2023-03-14，21物理PDF页；'+link(AUD/'sources/official_frodo_2023.pdf')+'，SHA256 `4688192bf5f5ac29e622ef359860890d2e97c224216baea2216dc42ef8d1547f`。§7.4物理PDF8/印刷4，TablesA.3/A.4物理PDF15–16/印刷11–12；1344 CDF结合[S10]勘误。\n'
draft=draft.replace('\n<!--protected-hedges:',eref+sref+'\n<!--protected-hedges:',1)
(OUT/'CRYPTOANALYSIS_DRAFT.md').write_text(draft,'utf-8')

# Current machine bindings are keyed to exact display rows and source distributions.
bindings={}
for name,row in laws.items():
    pattern=r'^\| '+name+r' \| ([0-9,]+) \|$'
    match=re.search(pattern,draft,re.M);assert match,name
    actual=list(map(int,match.group(1).split(',')))
    assert actual==row['mass_zero_then_each_signed_value']
    bindings[name]=dict(manuscript_location='附录B.1',actual_display_row=match.group(0),actual_display_row_utf8_sha256=text_sha(match.group(0)),parsed_display_mass=actual,official_CDF=row['cdf'],official_mass=row['official_mass'],certificate_input_mass=row['mass_zero_then_each_signed_value'],sampler_input_histogram=row['signed_integer_mass'],denominator=65536,total_mass_numerator=row['normalization'],support=row['support'],symmetric=True,even_numerator=row['even_numerator'],odd_numerator=row['odd_numerator'],maximum_atom=row['maximum_atom'],three_way_exact_equality=True,full64fold_recomputed=(name=='976'),source_scope=row['source_scope'])
dump(EV/'DISPLAY_TABLE_BINDING.json',dict(schema='fi-v2.1/display-cdf-certificate-binding/1',profiles=bindings,all_three_profiles_match=True,manuscript=rec(OUT/'CRYPTOANALYSIS_DRAFT.md')))

m=jd(V2/'CLAIM_EVIDENCE_MATRIX.json')
m['schema']='fi-research-manuscript/claim-evidence/2.1';m['version']='v2.1'
m['inherited_v2_identity']=m['identity']
m['identity']=dict(status='AUTHOR_ERRATUM_IMPACT_AUDIT_AND_DETERMINISTIC_CERTIFICATE_REPLAY',author_and_prior_reviews_visible=True,expected_replay_conclusion_visible_in_user_request=True,exact_runtime_model_id=None,declared_model_family='Codex based on GPT-6 (visible declaration)',new_independent_reviews=0,new_human_reviews=0,new_cross_model_reviews=0,new_blind_reviews=0,new_subagents=0,formal_proof_assistant=0)
m['source_registry_inheritance_note']='Entries inherited from v2 retain their historical reading/identity dates and scopes. E9 and S11 register the current erratum/source/replay scope.'
m['source_registry']['E9']=dict(identity=m['identity']['status'],reading_scope='INC976, official2021/2023 sampler/table pages and old producer/input/phase1 scripts read; new976 exact convolution and epsilon executed; all-three scalar input tables checked; mathematical attacks and640 joint probability proof inherited',files=[rec(p) for p in [AUD/'ORIGINAL_CLAIM_AND_PARAMETER_MAPPING.md',AUD/'VERDICT.json',EV/'replay_976_and_check_tables.py',EV/'REPLAY_976.json',EV/'DISTRIBUTION_TABLES.json',EV/'DISPLAY_TABLE_BINDING.json',EV/'chi_976_64fold_coefficients.json',BASE/'crypto_frodo_unconditional_support/sources/official_cdf_input.json',BASE/'crypto_frodo_unconditional_support/sources/build_mathematical_certificates.py',BASE/'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/math_verify.py']])
m['source_registry']['S11']=dict(file=rec(AUD/'sources/official_frodo_2023.pdf'),version='2023-03-14 preliminary standardization proposal,21physicalPDFpages',reading_scope='section7.4 physicalPDF8;TablesA3/A4 physicalPDF15-16;1344CDF interpreted with official2024-11-27 erratum',evidence_grade='PRIMARY_FROZEN_PDF_WITH_EXPLICIT_OFFICIAL_ERRATUM')
m['source_registry']['S10']['current_primary_erratum_receipts']=[rec(EV/f'official_1344_erratum_{i}.json') for i in [0,1]]
m['distribution_table_binding']=bindings
m['certificate_replay_976']=r
m['inherited_action_counts_v2']=m['action_counts']
m['action_counts']=dict(deterministic976_convolution_and_epsilon_replays=2,final_execution_checks=r['checks_passed'],full_convolution_coefficient_comparisons_per_execution=1281,finite_sampler_input_words_enumerated_per_profile_per_execution=65536,profiles_with_sampler_consistency_checks=3,random_chi_samples=0,matrices_keys_tokens_ciphertexts_sampled=0,attack_prototypes=0,LWE_solvers=0,mechanism_implementations=0,large_crypto_experiments=0,native_AS_RP_requests=0,author_contacts=0,messages_or_emails=0,new_independent_reviews=0,new_subagents=0,public_primary_GitHub_read_calls=2,new_priority_searches=0)

claims={c['id']:c for c in m['claims']}
c10=claims['C10'];c10['dependencies']=['C10_640','C10_976','C10_1344'];c10['source_ids']+=['S11','E9'];c10['review_identity_and_scope']='v2.1:976 full deterministic replay;640/1344 prior convolution/bounds retained plus current table-input checks; no new independent mathematical review';c10['limitations']='Source-event false-acceptance upper bounds; independent of update decryption reliability. INC976 corrected display row, existing correct976 certificate unchanged.'
claims['C09']['dependencies']=['C10_640' if x=='C10' else x for x in claims['C09']['dependencies']]
for name in ['640','976','1344']:
    x=dict(id='C10_'+name,claim=name+' finite source-event probability certificate',manuscript_location='§7.1、附录B.1–B.2',precise_object='Ideal independent chi'+name+' from declared officialCDF and printed UE',quantifiers='Every fixed A; w0=64; exact first-row real-fresh upper expression',assumptions=['SourceCDF/sampler law and exact finite signed mass','No merges of64fold integer support in Rq','Convolution contraction for longer sums'],dependencies=['C05'],source_ids=['S2','E1','E3']+(['S10'] if name=='1344' else [])+['S11','E9'],evidence_status='EXACT976_CERTIFICATE_REPLAYED' if name=='976' else 'INHERITED_FINITE_CERTIFICATE_WITH_CURRENT_INPUT_CONSISTENCY',limitations='976 full convolution/epsilon newly replayed;640/1344 full convolution/epsilon not recomputed this round',review_identity_and_scope='Author erratum/source consistency and deterministic finite replay; all prior review identities retained',semantic_input_selectors=['distribution_table_binding.'+name,'E3.certificates.profiles[profile='+name+']'])
    if name=='976':x['certified_epsilon_upper']='2^-1118';x['current_exact_replay']='certificate_replay_976'
    else:x['certified_epsilon_upper']='2^-751' if name=='640' else '2^-1532'
    x['limitations']='Current exact976 source-event replay;976 decryption reliability remains a separate question' if name=='976' else 'OnlyCDF/display/producer-input/sampler checks performed this round;64fold convolution andepsilon bound retain historical evidence'
    claims[x['id']]=x

for cid in ['C08','C09','C11','C14','C15','C16','C17','C19','C20']:
    claims[cid]['semantic_distribution_inputs']=['chi640']
claims['C08']['semantic_input_selectors']=['frozen_models.CF1','distribution_table_binding.640']
claims['C09']['semantic_input_selectors']=['frozen_models.CF1','C10_640']
claims['C25a']['semantic_distribution_inputs']=['chi640']
claims['C25a']['semantic_input_selectors']=['frozen_models.640_ONE_UPDATE','probability_results.exact_certificate.mass','distribution_table_binding.640']
claims['C25d']['semantic_distribution_inputs']=['chi640'];claims['C25d']['semantic_input_selectors']=['C25a']
claims['C25b']['limitations']+=';976 source-event epsilon replay does not resolve976 decryption reliability'
claims['C27']['source_ids']+=['E9'];claims['C27']['precise_object']+='; v2.1 author erratum/impact audit/deterministic replay'
m['claims']=sorted(claims.values(),key=lambda x:(int(re.search(r'\d+',x['id'])[0]),x['id']))

def ancestry(cid,seen=None):
    seen=set() if seen is None else seen
    if cid in seen:return seen
    seen.add(cid)
    for dep in claims[cid]['dependencies']:ancestry(dep,seen)
    return seen
main_dependencies={}
for label,cid in [('A','C09'),('B','C25d')]:
    deps=sorted(ancestry(cid));assert 'C10_976' not in deps
    main_dependencies[label]=dict(root_claim=cid,transitive_claim_dependencies=deps,semantic_distribution='chi640',depends_on_chi976=False,shared_artifact_note='PARAMETER_CERTIFICATES contains multiple profiles; semantic selector is640 only. Shared file identity alone is not a976 mathematical dependency.')
m['main_result_dependency_audit']=main_dependencies
effects=[]
for c in m['claims']:
    cid=c['id']
    if cid=='C10':impact='Display976 corrected;976 subcertificate fully replayed; umbrella claims separated into profile-specific dependencies'
    elif cid=='C10_976':impact='All1281 coefficients,peak,denominator,no-alias andepsilon<=2^-1118 current exact replay confirms existing numeric conclusion'
    elif cid in ['C10_640','C10_1344']:impact='Current CDF/display/input consistency only; previous64fold andepsilon results retained'
    elif cid=='C09':impact='Numeric theorem unchanged; dependency narrowed from umbrellaC10 toC10_640'
    elif cid=='C27':impact='Provenance extended with current author erratum/replay identity'
    else:impact='Mathematical statement/status retained; no dependence on erroneous976 display mass'
    effects.append(dict(claim_id=cid,depends_on_C10_976=('C10_976' in ancestry(cid)),effect=impact,status=c['evidence_status']))
m['erratum_impact_by_claim']=effects
m['erratum_closed']=dict(id='INC976',scope='AppendixB976 display mass and its replay instructions; downstream source routing and machine profile dependencies',changed_abs_values=[5,6,7,8,9],signed_atoms=[-9,-8,-7,-6,-5,5,6,7,8,9],old_total=65718,new_total=65536,current_epsilon976_unchanged='2^-1118',full_replay_passed=True,history_modified=False)
m['v2_1_correction_ids']=[f'INC976-R{i:02}' for i in range(1,9)]
m['correction_ids']+=m['v2_1_correction_ids']
m['adopted_publication_impact_audit']=dict(verdict=rec(AUD/'VERDICT.json'),cutoff_asia_shanghai='2026-11-10',new_priority_searches_this_round=0,status='Prior search-bounded A/B application candidates retained; global priority unresolved')
m['core_proof_status']='v2 explicit A/B contracts retained; INC976 display and976 exact source-event certificate replay closed. Human cryptographic review and contract-external questions remain pending.'
dump(OUT/'CLAIM_EVIDENCE_MATRIX.json',m)

# Audit all source mentions without mutating the historical material.
mention_files=[V2/n for n in ['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','REVIEW_RESPONSE_AND_READINESS.md']]+[AUD/n for n in ['ORIGINAL_CLAIM_AND_PARAMETER_MAPPING.md','APPLICATION_PRIORITY_AND_IMPACT.md','HUMAN_REVIEW_ENTRY.md','VERDICT.json']]
mentions=[]
pattern=re.compile(r'χ976|chi_976|(?<![0-9a-f])976(?![0-9a-f])|1131[,、]')
for p in mention_files:
    for line_no,line in enumerate(read(p).splitlines(),1):
        if pattern.search(line):mentions.append(dict(path=str(p),line=line_no,text=line[:1200]))
dump(EV/'976_MENTION_INVENTORY.json',dict(scope='All976-related hits in required historical core manuscripts/matrix/readiness/impact/source mapping/human entry; JSON structural selectors and mathematical dependence audited separately',files=[rec(p) for p in mention_files],occurrences=mentions))

materials=[
 dict(material='Official2021/2023 PMF tables and976 CDF',used_input='CORRECT_OFFICIAL_CDF_DERIVED_MASS',evidence='PDF Table3/TableA3 andCDFTable6/TableA4, sampler strict boundaries',effect='Primary correction basis'),
 dict(material='official_cdf_input.json dated2026-11-06',used_input='CORRECT_CDF_AND_EXPLICIT_MASS',evidence=rec(BASE/'crypto_frodo_unconditional_support/sources/official_cdf_input.json'),effect='Actual producer input is correct'),
 dict(material='build_mathematical_certificates.py',used_input='CDF_DERIVED_CORRECT_MASS',evidence=rec(BASE/'crypto_frodo_unconditional_support/sources/build_mathematical_certificates.py'),effect='pmf_from_cdf andconv64 readCDF input, not manuscript display'),
 dict(material='PARAMETER_CERTIFICATES.json',used_input='CORRECT_CDF_AND_EXACT_PEAK',evidence=rec(V1/'sources/PARAMETER_CERTIFICATES.json'),effect='976 sourceCDF,a,mu,gamma,dyadic exponents all match current replay'),
 dict(material='chi_976_64fold_coefficients.json historical original andv1copy',used_input='CORRECT_CONVOLUTION_COEFFICIENTS',evidence=[rec(V1/'sources/chi_976_64fold_coefficients.json'),rec(BASE/'crypto_frodo_unconditional_support/sources/chi_976_64fold_coefficients.json')],effect='All1281 current coefficients match; newly regenerated bytes identical'),
 dict(material='ROUND005 phase1 math_verify.py',used_input='CORRECT_EXPLICIT976_MASS',evidence=rec(BASE/'crypto_branch_monitor/round_005/independent_review_packet/review_output/phase1/math_verify.py'),effect='Historical checker hardcodes the correct mass; no erroneous display dependency'),
 dict(material='v1/v2 AppendixB display row and from-table replay wording',used_input='ERRONEOUS_DISPLAY_TABLE',evidence=[rec(V1/'CRYPTOANALYSIS_DRAFT.md'),rec(V2/'CRYPTOANALYSIS_DRAFT.md')],effect='The row and replay instructions require current manuscript erratum; existing correct electronic certificate unchanged'),
 dict(material='v2 section7.1 probability table/C10',used_input='CORRECT_FROZEN_CERTIFICATE_OUTPUT',evidence='C10 points toE1/E3 source certificates and previously reviewed profile; gamma display is a rounded approximation',effect='976 epsilon bound retained and newly replayed; dependency selectors made explicit'),
 dict(material='Publication impact audit INC976 and old human entry',used_input='DISCOVERY_AND_SCOPE_RECORD',evidence=rec(AUD/'VERDICT.json'),effect='Historical discovery status retained in place; current entry routes toclosedv2.1 replay'),
 dict(material='A:C08/C09 andB:C25a/C25d',used_input='CHI640_ONLY',evidence=main_dependencies,effect='No976 law or erroneous display dependency; math statements and exact640 probability payload retained')]
dump(EV/'MATERIAL_AND_CLAIM_DEPENDENCY_TRACE.json',dict(materials=materials,main_results=main_dependencies,per_claim=effects,source_artifact_and_semantic_profile_separated=True))

diff_table='| 绝对值j | 旧的每点分子 | 正确每点分子 | 每个符号点变化（新−旧） | 两符号点合计变化 |\n|---:|---:|---:|---:|---:|\n'
old=tables['inc976']['old_mass'];new=laws['976']['mass_zero_then_each_signed_value']
for j in range(11):diff_table+=f'| {j} | {old[j]} | {new[j]} | {new[j]-old[j]} | {(1 if j==0 else 2)*(new[j]-old[j])} |\n'
M=r['convolution']['maximum_coefficient']
report=r'''
# INC976勘误、影响范围与确定性证书审计

2026-11-10，Asia/Shanghai。研究稿版本：**v2.1**。身份：**AUTHOR_ERRATUM_IMPACT_AUDIT_AND_DETERMINISTIC_CERTIFICATE_REPLAY**。状态：**INC976_CLOSED；976_CERTIFICATE_REPLAY_CONFIRMED；THREE_DISPLAY_TABLES_BOUND_TO_CDF_AND_INPUT**。

本轮成果为文稿勘误、影响范围审计和确定性有限分布证书重放。用户提供了已有“系数匹配、界成立”结论；本版另执行可追溯程序，并以实际输入、完整输出和整数比较记录作为当前交付依据。新增独立、人工、跨模型、盲审、子代理和证明助手认证均为0，精确后端ID按可见运行信息为null。历史稿和审阅材料保持只读。

## 1. 勘误的准确范围与来源

v2正文附录B（冻结件L708）的χ976质量显示行，把±5、±6、±7、±8、±9各点分子分别写成1131、426、138、38、8，正确值为1101、396、118、29、6。分母65536，其余点保持。旧显示行也出现于v1；本轮只认证实际读取到的这条沿用链，最早产生该转录差异的编辑过程未另行推断。

发现来源为发表影响审计INC976（ORIGINAL_CLAIM_AND_PARAMETER_MAPPING §7、VERDICT.incidental_finding）。旧显示总质量为65718/65536，正确总质量为1；更正十个有符号原子、五个绝对值列，总分子减少182。原显示的支持和对称形状保持，但其分母下总质量和声明的均匀奇偶质量无法成立。正确质量的逐点差异如下。

DIFF_TABLE

完整21点有符号差异也保存在DISTRIBUTION_TABLES.json。勘误落点包括附录B显示表、从表重放说明、976电子复算入口、机器主张的分布选择器，以及新版人工审阅入口。§7.1中的ε₉₇₆≤2^-1118保持原值，已有电子证书无需数值修订。

## 2. 官方采样规则、CDF与质量推导

| 原始来源 | 固定版本/位置 | 本轮使用 |
|---|---|---|
| 官方2021规范 | 2021-06-04，59页；PDF15–16 §2.2.4/Algorithm5，25 Table3 | 严格阈值反CDF、976质量及CDF—质量公式；该版未列CDF数值表 |
| 官方2023提案 | 2023-03-14，21物理页；物理PDF8/印刷4 §7.4，15–16/印刷11–12 TablesA.3/A.4 | 独立版本的规则、976质量和CDF对应 |
| 官方1344勘误 | issue35，Patrick Longa回复2024-11-27，comment2504969837 | 1344完整CDF的T(5)=32765、T(6)=32767；2023旧CDF印表缺项按旧版记录 |

两份冻结PDF的SHA256分别为`5c3440b311c7ee4fba8b9a12e0ff567eb75c29fef66843f3eecc16f137164f7d`和`4688192bf5f5ac29e622ef359860890d2e97c224216baea2216dc42ef8d1547f`。采样/表的本轮提取与图像在evidence/official_2021_*、official_2023_*；对应已有结构预检PASS的字节再次核验。1344官方回复本轮只读重新取得并保存原始工具回执。

把16位均匀字r写成符号位r₀与t=r>>1∈{0,…,32767}。绝对值e=Σ_(i=0)^(s−1)1[t>T(i)]，输出(−1)^r₀e。由于比较严格，t∈[0,T(0)]给0，t∈[T(j−1)+1,T(j)]给绝对值j；最后一段止于32767。因而分母65536下w₀=2(T(0)+1)，w_(+j)=w_(−j)=T(j)−T(j−1)。T(s)在循环中不访问，其值32767固定最后区间的完整15位输入合同。

976的官方CDF为

`[5638,15915,23689,28571,31116,32217,32613,32731,32760,32766,32767]`。

推得0及每个正负点的质量分子为

`[11278,10277,7774,4882,2545,1101,396,118,29,6,1]`。

零点只计一次；976支持为[−10,10]共21点，每点正质量，对称。总质量65536，偶/奇分子各32768，最大原子唯一在0，a=11278/65536=5639/32768。每个内部阈值T(i)与T(i)+1逐一核对；对全部65536个输入字的确定性穷举得到完全相同频数。这些是有限域内枚举，随机采样次数为0。

## 3. 976的64重整数卷积与概率界

递推采用p₀(0)=1、p_(t+1)(k)=Σ_(z=−10)^10w_zp_t(k−z)，t=0,…,63。每阶段均检查总质量65536^t和完整支持宽度。最终结果：

| 项目 | 本轮结果 |
|---|---|
| 偏移及支持 | offset=−640；[−640,640] |
| 系数数量与逐项比较 | 全部1281个系数匹配；首次差异null |
| 分母、总质量 | 65536^64=2^1024；总质量等于该分母 |
| 对称性与峰值 | 完全对称；唯一峰值在0 |
| 峰值另一核对 | M=Σ_k p₃₂(k)²，精确相同 |
| 模群无合并 | q=65536>1280；1281个支持点的模像互异 |
| 文件字节 | 重建文件与v1冻结系数文件逐字节相同 |

完整峰值整数M为：

`PEAK_M`

μ₆₄=M/2^1024，γ=21μ₆₄≈0.45181564799471987180061448706472，仅展示小数。a、μ和γ的约分后精确分数与PARAMETER_CERTIFICATES.json的976 profile逐项相同。旧γ显示0.4518156480是舍入近似；认证继续采用精确分数。

对

\[
\epsilon_{976}=\binom{976}{63}(11278/65536)^{913}+(21M/2^{1024})^{976},
\]

取公共分母2^999424，整数分子

\[
N=\binom{976}{63}\,11278^{913}\,2^{984816}+(21M)^{976}.
\]

本轮直接比较N≤2^998306，得到ε₉₇₆≤2^-1118。第一项还≤2^-1985；高重量项及总式的最大整数二进制上界指数均为1118，与旧证书ceil_log2_raw=−1118一致。总式不满足下一个2^-1119界，只描述这个上包络的松紧，实际误接受概率或解码错误率的下界各有不同责任。

REPLAY_976.json保留全部M/μ/γ、64个阶段记录、每项匹配结论、整数分子的因子化定义、位长、无符号大端字节SHA256以及正比较余量的身份。完整大整数由所列因子和指数唯一重建，无需依赖十进制近似。chi_976_64fold_coefficients.json保留全部1281个重建系数；replay_976_and_check_tables.py给可重放计算。来源位置校准后完成最终执行，FINAL_CHECK_COUNT项确定性检查通过；本阶段完整976重放执行2次，最终证据绑定当前脚本与输出。

## 4. 三个显示表的针对性一致性

| χ | 显示质量=CDF导出=旧证书输入 | 支持 | 总分子 | 偶/奇分子 | 本轮完整卷积/ε |
|---|---|---|---:|---|---|
| 640 | 逐点相同 | [−12,12]，对称25点 | 65536 | 32768 / 32768 | 沿用历史证据 |
| 976 | 逐点相同（本版已更正） | [−10,10]，对称21点 | 65536 | 32768 / 32768 | 64步、1281系数与ε完整重算 |
| 1344 | 逐点相同（CDF含官方勘误） | [−6,6]，对称13点 | 65536 | 32770 / 32766 | 沿用历史证据 |

本轮三种采样器各穷举65536个输入字，并核对端点、归一化、支持、对称性、奇偶和最大原子。640/1344的64重卷积和ε界保持既有审阅身份；本轮未作这两项完整重算。旧official_cdf_input.json的三组显式质量、PARAMETER_CERTIFICATES.json的source_cdf与最大原子/奇偶字段均匹配。DISPLAY_TABLE_BINDING.json直接解析本版附录B三行，把实际文本行、行哈希、CDF、官方质量、证书输入与采样频数绑定。

## 5. 输入来源链与逐主张影响

| 材料 | 实际输入类别 | 本次影响 |
|---|---|---|
| official_cdf_input.json及旧生成脚本 | 正确官方CDF导出的质量 | pmf_from_cdf/conv64使用CDF文件，未读取文稿错误表 |
| PARAMETER_CERTIFICATES.json | 正确CDF、a、μ₆₄、γ与精确比较结果 | 976的值全部复现，原数值保持 |
| 旧chi_976_64fold_coefficients.json | 正确质量的已封存卷积系数 | 新计算逐项匹配，并且文件字节相同 |
| ROUND-005 phase1/math_verify.py | 硬编码的正确三组质量 | 旧976复核使用正确输入；本轮只读代码和记录，未重新执行整套旧检查 |
| v1/v2附录B | 错误的显示表及从表重放说明 | 当前文稿显示及其复核入口修正 |
| v2 §7.1概率表与C10 | 已封存正确证书输出 | 976界保持；当前证据增强为可追溯完整重放 |
| A与B的原证明/概率包 | χ640及其各自参数合同 | 声明、模型、量词和精确640概率数据保持 |

机器矩阵把原C10总项展开为C10_640、C10_976、C10_1344。C09（A）的依赖由C10总项细化为C10_640；C08、C14–C20的χ640语义输入，以及C25a/C25d（B）的χ640精确概率输入另作选择器登记。共享的PARAMETER_CERTIFICATES文件含多个profile，语义依赖通过profile640选择，不把同文件的976字段并入A/B。

对每条现有主张及新增子项，CLAIM_EVIDENCE_MATRIX.erratum_impact_by_claim记录传递依赖、影响与当前证据状态；完整来源材料分类和依赖闭包见MATERIAL_AND_CLAIM_DEPENDENCY_TRACE.json。976的来源事件ε界与976更新解码可靠性分开，C25b保持原未决状态。

## 6. 本版修正闭合表

| ID | 旧版/来源位置 | v2.1落点 | 状态 |
|---|---|---|---|
| INC976-R01 | v2附录B L708错误显示行；影响审计INC976 | 版本说明、附录B.1与逐点差异表 | CLOSED |
| INC976-R02 | 官方2021 Algorithm5/2023 §7.4及CDF | 附录B.1(B1)、本报告§2、DISTRIBUTION_TABLES | CLOSED |
| INC976-R03 | 旧976系数与μ证书 | 附录B.2、本报告§3、重建全部系数 | CLOSED |
| INC976-R04 | 旧976两项概率上界 | 附录B.2(B2)、REPLAY_976整数比较 | CLOSED |
| INC976-R05 | 三个显示表/官方输入/证书输入 | 附录B.1、DISPLAY_TABLE_BINDING、三次有限采样域穷举 | CLOSED |
| INC976-R06 | C10总项与A/B依赖 | C10三子项、语义profile选择与逐主张影响表 | CLOSED |
| INC976-R07 | 影响审计人工入口指向v2及INC976待修说明 | 本版HUMAN_REVIEW_ENTRY指向v2.1并附闭合结果 | CLOSED |
| INC976-R08 | 版本、来源、计算记录及历史字节 | 本版五份核心文件、MANIFEST与最终QA | CLOSED |

## 7. 保持的证据边界与人工审阅就绪

本版保留A的CF-1逐样本正确性、≤3n+1调用和Δ→1；保留B在均匀Setup、iid χ640、既定Ord、一次诚实未筛选TG/Upd及官方舍入合同下的初始完整正确率≥1−2^-132、更新完整错误率≥99.9969655%及初始正确条件下显示下界。原游戏、LWE与概率证明的人工/模型审阅身份按原记录引用。

本轮没有新增应用优先权搜索，采用发表影响审计截至2026-11-10的有界检索状态；同对象应用候选、全球优先权未决及Nishimaki/CJL来源版本责任保持。作者实际程序、config、A与秘密噪声联合律、Ord/取模/舍入对应以及FI完整LWE归约继续需要外部证据。最高价值的外部输入仍是作者准确UE commit/config、随机带与算术说明，以及一条含消息相等断言的Enc→TG→Upd→Dec轨迹。

本版具备交给人工密码学审阅的完整入口、全文证明、主张依赖、来源与有限证书材料。该就绪状态描述送审材料的完整性，人工同行裁决和正式发表状态分别待取得。数据与材料路径、字节哈希、当前有限执行范围及历史起止一致性由MANIFEST固定。

## 8. 直接复核入口

LINKS
'''.replace('DIFF_TABLE',diff_table.strip()).replace('PEAK_M',M).replace('FINAL_CHECK_COUNT',str(r['checks_passed']))
entries=[OUT/'CRYPTOANALYSIS_DRAFT.md',OUT/'CLAIM_EVIDENCE_MATRIX.json',OUT/'HUMAN_REVIEW_ENTRY.md',EV/'replay_976_and_check_tables.py',EV/'REPLAY_976.json',EV/'chi_976_64fold_coefficients.json',EV/'DISTRIBUTION_TABLES.json',EV/'DISPLAY_TABLE_BINDING.json',EV/'MATERIAL_AND_CLAIM_DEPENDENCY_TRACE.json',EV/'976_MENTION_INVENTORY.json',V1/'sources/PARAMETER_CERTIFICATES.json',AUD/'sources/official_frodo_2023.pdf',V1/'sources/official_frodo_2021.pdf']
report=report.replace('LINKS','\n'.join('- '+link(p) for p in entries))
(OUT/'ERRATUM_AND_CERTIFICATE_AUDIT.md').write_text(report.strip()+'\n','utf-8')

human=read(AUD/'HUMAN_REVIEW_ENTRY.md')
human=human.replace('# 人工密码学审阅入口：Frodo-FI两项主结果','# 人工密码学审阅入口：Frodo-FI研究稿v2.1与INC976闭合',1)
human=human.replace('D:/毕业设计/crypto_fi_research_manuscript_v2/',str(OUT).replace('\\','/')+'/')
# Version names in prose, preserving exact filesystem identifiers and historical record names.
human=re.sub(r'v2(?![._0-9])','v2.1',human)
oldlast='原始阅读顺序为目标算法/游戏→命题A或B→对应完整证明→有限证书。人工审阅无需重读本项目业务系统材料。应用优先权的检索范围与缺项见同目录APPLICATION_PRIORITY_AND_IMPACT.md。旁支INC976仅涉及v2.1附录B的976显示表，两个主结果均使用χ640；当前历史文件保持只读。'
assert oldlast in human
human=human.replace(oldlast,'原始阅读顺序为目标算法/游戏→命题A或B→对应完整证明→有限证书。应用优先权范围沿用 '+link(AUD/'APPLICATION_PRIORITY_AND_IMPACT.md')+'。INC976现已在v2.1闭合，两个主结果继续只使用χ640；详见下节。历史文件保持只读。')
human=human.replace('| v2.1作者整合及本轮审计 | 知情作者整合；知情应用/原声明审计 | v2.1重放303项；本轮不新增独立概率证明认证 |','| v2作者整合及发表影响审计 | 知情作者整合；知情应用/原声明审计 | v2重放303项；其后发表影响审计完成有界来源比较 |\n| 当前v2.1勘误 | AUTHOR_ERRATUM_IMPACT_AUDIT_AND_DETERMINISTIC_CERTIFICATE_REPLAY | 976完整64重重算、全部1281系数和ε界；三表输入一致性；新增独立数学审阅0 |')
human+='''

## 8. INC976已闭合的勘误与证书依据

v2附录B的χ976分子在±5至±9列更正为1101、396、118、29、6；正确完整序列为[11278,10277,7774,4882,2545,1101,396,118,29,6,1]/65536。零点一次，其余正负各一次。官方2021/2023CDF和实际严格阈值规则导出该质量；总质量65536、支持[−10,10]、对称、偶奇各32768，最大原子5639/32768。

当前从该CDF完整重建976的64重整数卷积：偏移−640、全部1281系数、分母65536^64、总质量、唯一峰值在0及q=65536>1280无合并条件均通过；重建系数文件与旧文件逐字节相同。ε₉₇₆=binom(976,63)a^913+(21μ₆₄)^976≤2^-1118经精确整数比较成立。这是来源事件上界，976更新解码可靠性继续单列。

三表当前显示行、官方CDF导出质量和旧证书输入逐点相同；640/1344只完成输入一致性与有限采样域检查，完整卷积/ε沿用历史证据。1344采用官方2024-11-27勘误后的完整CDF。A的依赖已细化到C10_640，B使用χ640精确概率包，均无C10_976传递依赖。两个命题的模型和量词见本入口§2，完整证明在v2.1相同章节。

当前成果登记为作者勘误、影响范围审计及确定性证书重放。人工审阅、跨模型独立性、作者实际程序、FI完整归约、CJL/Nishimaki来源对应与应用优先权保留各自原有证据状态。下列材料可独立复核本次闭合：

'''
for p in [OUT/'ERRATUM_AND_CERTIFICATE_AUDIT.md',EV/'REPLAY_976.json',EV/'chi_976_64fold_coefficients.json',EV/'replay_976_and_check_tables.py',EV/'DISPLAY_TABLE_BINDING.json',EV/'MATERIAL_AND_CLAIM_DEPENDENCY_TRACE.json']:human+='- '+link(p)+'\n'
(OUT/'HUMAN_REVIEW_ENTRY.md').write_text(human,'utf-8')

dump(EV/'AUTHORING_RECORD.json',dict(version='v2.1',identity=m['identity'],new_corrections=m['v2_1_correction_ids'],main_result_dependency_audit=main_dependencies,new_claim_count=len(m['claims']),all_current_source_input_bindings_match=True,scope='Literal976 erratum,profile-specific dependency refinements,and deterministic replay documentation. Main A/B proofs inherited unchanged.'))
print(json.dumps(dict(written=[rec(OUT/n) for n in ['CRYPTOANALYSIS_DRAFT.md','CLAIM_EVIDENCE_MATRIX.json','ERRATUM_AND_CERTIFICATE_AUDIT.md','HUMAN_REVIEW_ENTRY.md']],active_claims=len(m['claims']),dependencies=main_dependencies),ensure_ascii=False))
