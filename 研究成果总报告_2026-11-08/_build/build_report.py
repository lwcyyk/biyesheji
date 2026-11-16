from pathlib import Path
import re, json, hashlib, sys
from datetime import datetime, timezone
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from content import SECTIONS

ROOT=Path('D:/毕业设计')
OUT=ROOT/'研究成果总报告_2026-11-08'
DEST=OUT/'AI智能体授权与凭证管理研究历程及成果总报告_2026-11-08.docx'
TOP='research_main_innovation/main_topic_selection/'
sources=[]; source_map={}
def register(rel):
    rel=rel.replace('\\','/')
    if rel not in source_map:
        p=ROOT/rel
        if not p.is_file(): raise FileNotFoundError(p)
        sid=f'S{len(sources)+1:03}'
        source_map[rel]=sid
        sources.append({'id':sid,'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size})
    return source_map[rel]

STAGES=[
('早期方案与工程资产','当前方案双报告_2026-11-03','双报告与需求、贡献、证据及矛盾清单；早期方案状态。'),
('四阶段设计','实现四阶段','需求、场景、架构及数据接口；设计能力与实际验收分列。'),
('原生与算法项目','auth-lifecycle','有限 A/B/AB、原生调查与校准资产；历史实现保留。'),
('论文与证据组织','thesis_draft','早期论文材料和章节组织；结论采用后继裁决。'),
('原始文献库','关键论文与可行性核查_2026-11-04','论文、草案、索引与逐篇速览；全文取得和实际阅读范围分列。'),
('v1.2有限算法','research_v12','价值单元、路径类、动态证书与强对照；开发数据保留。'),
('资源谱初稿','research_secret_recipe','固定绑定、资源与分离模型；由R2/R3澄清。'),
('资源谱R2','research_recipe_r2','并发合同、定理和实证；原版本保留。'),
('资源谱R3','research_recipe_r3','完整谱、量词、隔离重推导与原生前提审计。'),
('扩展查新','research_novelty_review_2026-11-04','机制近邻、七项旧淘汰及可保留贡献。'),
('资产复核','workspace_asset_review_2026-11-04','源码、原始结果、缺失工件与研究路线索引。'),
('在线状态M1','mainline_online_state_v1','成熟本地权威状态与有限故障域实现。'),
('Casdoor原生M2','mainline_native_casdoor_v1','固定password/refresh流程、来源和未知后继。'),
('标识化恢复M3','mainline_native_reconciliation_v1','完整标识、持久绑定及单次效果合同下成熟组合闭环。'),
('未知结果M4','mainline_native_unidentified_v1','专用组织额外授权子域；共享账户枚举限制分列。'),
('代理隔离M5','mainline_agent_isolation_v1','合成隔离、ACL与权限边界证据。'),
('联合隔离M6','mainline_native_isolation_v1','联合原生轨迹、存储与审计及版本化回归。'),
('系统研究收口','mainline_research_closure_v1','27项主张8类；算法与持久层连接限制明确。'),
('主创新复审','research_main_innovation','CI三候选、强近邻、资产和下一问题。'),
('CI合同审计','research_main_innovation/ci01_contract_audit','原生能力、真实轨迹、强组合与费用合同。'),
('CI截止审计','research_main_innovation/ci01_cutoff_audit','有限闭包覆盖，派生Cookie及枚举边界。'),
('CI策略一致性','research_main_innovation/ci01_policy_consistency_review','nil应用分支源码问题；部署与披露另核。'),
('证明缓存文献','research_main_innovation/ci02_cost_literature_review','Vega等预计算和成本依据。'),
('证明缓存选题','research_main_innovation/ci02_cost_problem_screen','Q1/Q2归约已知缓存与选择；主创新归档。'),
('预测重物化','research_main_innovation/prediction_rematerialization_screen','模型修正、已知子域和接口缺口；停止主动主创新投入。'),
('工作负载取证','research_main_innovation/authorization_workload_evidence','单订单batch覆盖；独立多执行器证据缺口。'),
('授权拓扑核查','research_main_innovation/authorization_topology_check','Temporal两例由成熟工作流覆盖；路线重定向。'),
('理论问题重建','research_main_innovation/main_question_reset','饱和与恢复，保留A-E定位责任。'),
]
AE={
'ae_branching_proof':('A-E分支证明','T1/T2构造、冲突二择一、完整正确性与费用。'),
'ae_priority_audit':('初轮先例审查','冻结定理身份，等价表述与直接先例矩阵。'),
'ae_math_review':('分阶段数学复核','陈述输入尝试与知情核读分列，正域和恢复澄清。'),
'ae_pm2020_check':('PM2020正式核验','期刊全文缺口关闭；T2部分重叠；六项澄清整合。'),
'ae_col2026_check':('COL2026来源','正式正文未取得；当前主动获取暂停。'),
'ae_local_edit_priority':('局部修改来源','KU作者稿和D13预览；模型与参数映射。'),
'ae_external_review_pack':('外审材料','英文自含短稿、审查问题及具体资料请求；外部意见待取得。'),
'ae_parameter_refinement':('T3加强','从标签枚举到代表修复及结构历史计数。'),
'ae_t3_closure_audit':('T3闭环审查','PR-C3、全部前缀和费用知情复核支持。'),
'ae_t3_p26_coverage':('P26与会议版','P26来源未决；COL2020正式版指定路径已核。'),
'ae_t3_alternative_frameworks':('其他框架','n-fold精确表示与费用，FS21及有限子域。'),
'ae_r1_nfold_compilation':('半径一编译','重复支撑森林与承诺子域；一般残余接口。'),
'ae_sc_residual_interface':('单列残余','两条简化反例、硬投影及承诺子域。'),
'ae_sc_t3_transfer':('成本域迁移','T+依赖T3闭合，完整SC数学责任完成。'),
'ae_tplus_priority_screen':('T+先例','跨表述和成本列表规范化；后继MT-1收窄FPT主张。'),
'ae_tplus_eth_lower_bound':('ETH下界','同阶子图归约，YES真正半径1及指数阶匹配。'),
'ae_tplus_list_partitions_check':('列表划分','精确基底覆盖；两条半径1编译参数未保持。'),
'ae_main_theorem_package':('主定理包','上界下界自含整合，P13/P14强参考补回。'),
'ae_m1_profile_refinement':('M₁应用精化','当前Casdoor限定profile无法提供原子重绑合同。'),
'ae_theory_investment_decision':('理论投入判断','纯理论候选保留，应用和实现门独立。'),
'ae_fs23_version_check':('FS23版本','完整期刊正文未取得；延期状态保留。'),
'ae_strict_separation_gate':('严格分离审查','两冻结族被更强组合覆盖，无存活严格实例。'),
'ae_heavy_type_general_radius':('变半径高型','二端与低维正规形；初期一般计数后由CT-1更新。'),
'ae_heavy_type_cut_tree':('割树统一计数','k_r≤2s−1紧界及全高型枚举推论。'),
'ae_three_mode_radius3_normal_form':('三模式半径3','一般森林反例；残余界与紧单圈。'),
'ae_three_mode_radius4_cycle_form':('三profile各半径','统一循环交换、逐行单调及完整紧环数表。'),
'ae_four_profile_radius3_cycle_form':('四profile半径3','三支撑类完整处理，紧二环与单调强化。'),
'ae_scenario_reanchoring':('真实场景重锚','双站发票基础能力覆盖；主要数学在此场景封存。'),
'ae_two_year_research_outlook':('两年展望','基于论文与草案的候选与阶段工作责任。'),
'ae_new_line_deception_exploration':('诱饵初筛','普通honeytoken已有直接近邻，未选主线。'),
'ae_agent_enrollment_ownership':('自主开户','用户独立接管与旧代理退出合同。'),
'ae_enrollment_research_agenda':('开户后续','基础机制受先例收缩，故障接管候选待核。'),
'ae_paradigm_exploration':('范式初探','任务授权与更广控制对象的候选定义。'),
'ae_authorization_necessity_exploration':('扩权必要性','区分四种必要性量词和形成过程。'),
'ae_inference_authority_exploration':('推理权限','近似编译候选；共享量化机制已有先例。'),
'ae_decentralized_authority_exploration':('去中心化委托','证据发现恢复与受限清理权候选。'),
'ae_private_authorization_recovery_audit':('私密恢复核查','标准功能覆盖、路径数论据反例和主动撤销泄漏界。'),
'ae_broad_paradigm_exploration_2026_11_08':('六类开放候选','联合推断、形成过程、责任、争议、退出与资源治理。'),
'ae_new_claim_exploration_2026_11_08':('三个新命题对象','撤销预算、授权前提因果完整性、私密异议资格。'),
'ae_creative_divergence_2026_11_08':('四项创造性构想','清单隐私、模型升级、技能复用及私密诊断。'),
'ae_agent_collaboration_ideas_2026_11_08':('代理协作','私密偏好审核、数据报价与待确认额度。'),
'ae_cross_platform_exploration_2026_11_08':('跨平台探索','反例迁移、最小重确认及d维连续询问界。'),
'ae_structured_consent_exploration_2026_11_08':('结构偏好','二元等幅与正参照结果，标准保持条件。'),
'ae_robust_consent_exploration_2026_11_08':('抗误差询问','Θ(1+dη)、单问门槛和不可区分；先例及真实模型待核。'),
}
STAGES += [(label,TOP+d,summary) for d,(label,summary) in AE.items()]
CRYPTO={
'crypto_expiring_ue_research':('到期UE初探','受限类攻击、提升接口与条件密码分析。'),
'crypto_expiring_ue_proof_r2':('到期UE第二轮','精确本地模拟、条件重标记与证明迁移障碍。'),
'crypto_expiring_ue_proof_r3':('到期UE第三轮','节点、根槽与配对公式审计；来源未决。'),
'crypto_expiring_ue_external_review':('到期UE交接包','问题与来源固定，等待完整外部规范；实际发送0。'),
'crypto_unidirectional_ue_randomness':('单向UE随机性','固定GP实例增强接口证明与FI候选。'),
'crypto_unidirectional_ue_adaptive_r2':('自适应单向UE','未来钥匙与共享后台的条件模拟。'),
'crypto_unidirectional_ue_review_r3':('单向UE复核','事件权重、正常桥接与停止量词澄清。'),
'crypto_select_independent_r4':('SELECT阶段尝试','输入与审阅身份按内部子目录记录。'),
'crypto_select_external_math_review':('SELECT数学审查','采样和有限规格修订责任；AI审阅来源单列。'),
'crypto_select_sampler_revision_v2':('SELECT采样修订','理想与有限SPEC2采样、失败及终局评分。'),
'crypto_select_priority_audit':('SELECT先例裁决','已有构造有限证明扩展与规格化归档。'),
'crypto_frodo_support_review':('FI基础复核','合法性、可逆性、辅助信息与概率范围。'),
'crypto_frodo_priority_audit':('FI优先权','v1至v4、原算法与具体攻击近邻映射。'),
'crypto_frodo_hybrid_audit':('FI混合审计','命名混合区分证书与前作继承责任。'),
'crypto_frodo_adaptive_attack':('FI自适应','首次可逆选择与联合视图；后继直接界更新。'),
'crypto_frodo_common_parameter_closure':('FI共同参数族','正确性与攻击兼容族；历史条件版本保留。'),
'crypto_frodo_unconditional_support':('FI直接概率','固定A小支持界、有限表与无LWE证明。'),
'crypto_fi_original_game_decision':('FI最终引用稿','指定发表对象原游戏攻击与完整范围。'),
'crypto_linear_token_exposure':('线性token暴露','MATRIX-SELECT模作用学习与合法接口限制。'),
'crypto_token_exposure_priority':('线性token先例','合并作用及具体已发表算法的增强接口边界。'),
'crypto_secret_coin_compiler':('秘密带编译','PRP包装被成熟基底覆盖；通用升级反例。'),
'crypto_hidden_token_noise_audit':('隐藏token噪声','残差平均有直接先例，具体作用映射保留。'),
'crypto_ue_rerandomization_boundary':('计算重随机化','标准LWE推论与局部组合；完整参数责任。'),
'crypto_rtr_original_game_audit':('RtR游戏审计','条件模型攻击、参数与正式来源映射。'),
'crypto_rtr_independent_review':('RtR审阅记录','封存条件命题的分阶段核对，独立性按原记录。'),
'crypto_rtr_priority_decision':('RtR贡献裁决','成熟组合覆盖，B级条件构造应用归档。'),
'crypto_branch_monitor':('密码学监督索引','轮次、状态与停止回执；ROUND-005及后续分项记录。'),
}
STAGES += [(label,d,summary) for d,(label,summary) in CRYPTO.items()]

doc=Document()
sec=doc.sections[0]
sec.page_height=Cm(29.7); sec.page_width=Cm(21)
sec.top_margin=Cm(2.25);sec.bottom_margin=Cm(2.15);sec.left_margin=Cm(2.35);sec.right_margin=Cm(2.35)
sec.header_distance=Cm(1.0);sec.footer_distance=Cm(1.0)
for st in doc.styles:
    for border in list(st.element.findall('.//'+qn('w:pBdr'))):border.getparent().remove(border)
    if st.type==1 or st.type==2:
        st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
        rp=st.element.get_or_add_rPr()
        f=rp.find(qn('w:rFonts'))
        if f is None:f=OxmlElement('w:rFonts');rp.insert(0,f)
        f.set(qn('w:eastAsia'),'宋体')
        for attr in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
            f.attrib.pop(qn('w:'+attr),None)
normal=doc.styles['Normal'];normal.font.size=Pt(11)
pf=normal.paragraph_format;pf.line_spacing=1.32;pf.space_after=Pt(6);pf.widow_control=True
for name,size,before,after in [('Title',25,0,14),('Subtitle',15,0,10),('Heading 1',18,16,10),('Heading 2',13,12,7),('Heading 3',11.5,9,5)]:
    st=doc.styles[name];st.font.size=Pt(size);st.font.bold=name!='Subtitle';st.font.italic=False
    st.paragraph_format.space_before=Pt(before);st.paragraph_format.space_after=Pt(after)
    st.paragraph_format.keep_with_next=True
    st.element.get_or_add_rPr().find(qn('w:rFonts')).set(qn('w:eastAsia'),'黑体')
for name in ['Caption','Header','Footer']:
    doc.styles[name].font.size=Pt(9)
doc.styles['Caption'].font.color.rgb=RGBColor(0,0,0)
header=sec.header.paragraphs[0];header.text='AI智能体授权与凭证管理研究历程';header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
footer.add_run('第 ')
def field(p,code,text=''):
    r=OxmlElement('w:r');f=OxmlElement('w:fldChar');f.set(qn('w:fldCharType'),'begin');r.append(f);p._p.append(r)
    r=OxmlElement('w:r');t=OxmlElement('w:instrText');t.set(qn('xml:space'),'preserve');t.text=code;r.append(t);p._p.append(r)
    r=OxmlElement('w:r');f=OxmlElement('w:fldChar');f.set(qn('w:fldCharType'),'separate');r.append(f);p._p.append(r)
    p.add_run(text)
    r=OxmlElement('w:r');f=OxmlElement('w:fldChar');f.set(qn('w:fldCharType'),'end');r.append(f);p._p.append(r)
field(footer,' PAGE ','1');footer.add_run(' 页')
sec.different_first_page_header_footer=True

def hyperlink(p,text,target,size=9):
    h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(target,RT.HYPERLINK,is_external=True))
    r=OxmlElement('w:r');rp=OxmlElement('w:rPr')
    fonts=OxmlElement('w:rFonts');fonts.set(qn('w:eastAsia'),'宋体');fonts.set(qn('w:ascii'),'Calibri');rp.append(fonts)
    color=OxmlElement('w:color');color.set(qn('w:val'),'000000');rp.append(color)
    sz=OxmlElement('w:sz');sz.set(qn('w:val'),str(int(size*2)));rp.append(sz)
    r.append(rp);t=OxmlElement('w:t');t.text=text;r.append(t);h.append(r);p._p.append(h)

def resolve(text):
    return re.sub(r'\{ref:([^}]+)\}',lambda m:'['+register(m.group(1))+']',text)

def paragraph(text,style=None):
    text=resolve(text)
    text=text.replace('O(w2^w)','O(w·2ʷ)').replace('Ω_t','Ωₜ').replace('D_k','Dₖ').replace('N_r','Nᵣ').replace('p_i','pᵢ').replace('θ_j','θⱼ')
    math_replacements={'M_r':'Mᵣ','μ_a':'μₐ','k_r':'kᵣ','S_j':'Sⱼ','D_j':'Dⱼ','x_j':'xⱼ','x_k':'xₖ','y_j':'yⱼ','y_t':'yₜ','s_i':'sᵢ','τ_i':'τᵢ','b_i':'bᵢ','P_i':'Pᵢ','E_i':'Eᵢ','Δ_n':'Δₙ','ε_n':'εₙ','μ_{w₀}':'μw₀','k_η':'kη','K_η':'Kη','t_C':'t꜀','q_C':'q꜀','X_aℓ':'Xₐℓ','X_bℓ':'Xᵦℓ'}
    for a,b in math_replacements.items():text=text.replace(a,b)
    p=doc.add_paragraph(style=style)
    for j,part in enumerate(re.split(r'\*\*(.*?)\*\*',text)):
        pos=0
        for mm in re.finditer(r'\^\{([^{}]+)\}|\^([−-]?[A-Za-z0-9ε]+)',part):
            r=p.add_run(part[pos:mm.start()]);r.bold=bool(j%2)
            r=p.add_run(mm.group(1) or mm.group(2));r.font.superscript=True;r.bold=bool(j%2)
            pos=mm.end()
        r=p.add_run(part[pos:]);r.bold=bool(j%2)
    if text.startswith('来源：'):
        p.paragraph_format.space_before=Pt(4);p.paragraph_format.space_after=Pt(7)
        for r in p.runs:r.font.size=Pt(9)
    if text.endswith(('定义：','计算：','时间为：','结论为：')):
        p.paragraph_format.keep_with_next=True
    return p

def table(rows):
    count=len(rows[0]); t=doc.add_table(rows=0,cols=count);t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    widths={2:[4.2,12.1],3:[3.7,6.4,6.2],4:[2.2,4.6,4.7,4.8]}.get(count,[16.3/count]*count)
    for c,w in zip(t.columns,widths):c.width=Cm(w)
    pr=t._tbl.tblPr
    borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        b=OxmlElement('w:'+side);b.set(qn('w:val'),'single');b.set(qn('w:sz'),'4');b.set(qn('w:color'),'D9D9D9');borders.append(b)
    pr.append(borders)
    for idx,row in enumerate(rows):
        rr=t.add_row();rpr=rr._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');rpr.append(cant)
        if idx==0:
            repeat=OxmlElement('w:tblHeader');rpr.append(repeat)
        for c,txt,w in zip(rr.cells,row,widths):
            c.width=Cm(w);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp=c._tc.get_or_add_tcPr();mar=OxmlElement('w:tcMar')
            for side,v in [('top',90),('bottom',90),('left',110),('right',110)]:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),str(v));e.set(qn('w:type'),'dxa');mar.append(e)
            cp.append(mar)
            if idx==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E7E6E6');cp.append(sh)
            p=c.paragraphs[0];p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.15
            if idx==0:p.paragraph_format.keep_with_next=True
            r=p.add_run(resolve(txt));r.font.size=Pt(9.5);r.bold=idx==0
    doc.add_paragraph().paragraph_format.space_after=Pt(0)

def mr(s):
    r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=s;r.append(t);return r
def sup(base,exp):
    s=OxmlElement('m:sSup');e=OxmlElement('m:e');e.append(mr(base));p=OxmlElement('m:sup');p.append(mr(exp));s.extend([e,p]);return s
def sub(base,index):
    s=OxmlElement('m:sSub');e=OxmlElement('m:e');e.append(mr(base));p=OxmlElement('m:sub');p.append(mr(index));s.extend([e,p]);return s
def subsup(base,lo,hi):
    s=OxmlElement('m:sSubSup');e=OxmlElement('m:e');e.append(mr(base))
    a=OxmlElement('m:sub');a.append(mr(lo));b=OxmlElement('m:sup');b.append(mr(hi));s.extend([e,a,b]);return s
def group_sup(nodes,exp):
    s=OxmlElement('m:sSup');e=OxmlElement('m:e')
    for x in nodes:e.append(x)
    a=OxmlElement('m:sup');a.append(mr(exp));s.extend([e,a]);return s
def binom(n,k):
    d=OxmlElement('m:d');dp=OxmlElement('m:dPr')
    for name,val in [('begChr','('),('endChr',')')]:
        a=OxmlElement('m:'+name);a.set(qn('m:val'),val);dp.append(a)
    d.append(dp);e=OxmlElement('m:e');f=OxmlElement('m:f');pr=OxmlElement('m:fPr')
    tp=OxmlElement('m:type');tp.set(qn('m:val'),'noBar');pr.append(tp);f.append(pr)
    num=OxmlElement('m:num');num.append(mr(n));den=OxmlElement('m:den');den.append(mr(k));f.extend([num,den]);e.append(f);d.append(e);return d
MATH={
'T3_CONTRACT':[mr('∀i ∈ [m]   '),sub('∑','t=1…n'),mr(' [Aᵢₜ ≠ '),subsup('ρ','sᵢ','yₜ'),mr('] ≤ r')],
'T2_BOUND':[sup('2','O(L² + Lr log(Lr+2))'),mr(' · poly(mn + qL)')],
'T3_BOUND':[sup('2','O(L log(L+2) + Lr log(Lr+2))'),mr(' · poly(mn + qL)')],
'TPLUS_CONTRACT':[mr('ηₜ ∈ Ωₜ   ∀i ∃pᵢ   τᵢ(pᵢ) + '),sub('∑','t=1…v'),mr(' [Aᵢₜ ≠ Q[pᵢ,ηₜ]] ≤ 1')],
'TPLUS_BOUND':[sup('2','O(w log(w+2))'),mr(' · Nᶜ')],
'HEAVY_BOUND':[sub('k','r'),mr(' ≤ 2s−1 ≤ 2w₀−1 ≤ 2w−1')],
'FI_RECOVERY':[mr('r̂ = (y − HP₁)'),sup('P₂','−1'),mr('  mod q')],
'FI_EPSILON':[sub('ε','n'),mr(' = min{1, '),binom('n','w₀−1'),sup('a','n−w₀+1'),mr(' + '),group_sup([mr('(h'),sub('μ','w₀'),mr(')')],'n'),mr('}')],
'FI_GAP':[mr('β ≤ αεₙ     Δ = α−β ≥ α(1−εₙ)')],
'QUERY_BOUND':[mr('⌈d / '),sub('K','η'),mr('⌉ ≤ Q(d,η) ≤ ⌈d / '),sub('k','η'),mr('⌉    0 < η < 1')],
'QUERY_ORDER':[mr('Q(d,η) = Θ(1+dη)    0 ≤ η < 1')],
}
def equation(key):
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before=Pt(6);p.paragraph_format.space_after=Pt(9)
    p.paragraph_format.keep_with_next=True
    op=OxmlElement('m:oMathPara');om=OxmlElement('m:oMath')
    for x in MATH[key]:om.append(x)
    op.append(om);p._p.append(op)

def blocks(body):
    lines=body.splitlines();i=0;pending=[]
    def flush():
        if pending:paragraph('\n'.join(pending));pending.clear()
    while i<len(lines):
        line=lines[i].strip()
        if not line:flush();i+=1;continue
        if line.startswith('## '):flush();doc.add_heading(line[3:],2);i+=1;continue
        if line.startswith('@math '):flush();equation(line.split()[1]);i+=1;continue
        if line.startswith('|'):
            flush();rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                rows.append([x.strip() for x in lines[i].strip().strip('|').split('|')]);i+=1
            table(rows);continue
        pending.append(line);i+=1
    flush()

doc.add_paragraph('研究历程与成果总报告',style='Subtitle')
doc.add_paragraph('AI智能体授权与凭证管理',style='Title')
doc.add_paragraph('从初期选题到当前研究进度',style='Subtitle')
paragraph('截至 2026 年 11 月 8 日  ·  Asia/Shanghai')
paragraph('研究主题包括认证语义、可撤销配置、参数算法、高型结构、可更新加密分析，以及授权与隐私的新方向。')
paragraph('当前重点：保留可核查的成果与负结果，准确呈现证据等级、先例差异和未完成责任。')
doc.add_paragraph('阅读建议',style='Heading 2')
paragraph('了解总体进度：先读研究总览与第15章。\n核查数学成果：重点读第5至8章。\n核查密码分析：重点读第9至11章。\n选择后续场景：重点读第12至14章。\n追溯依据：使用附录的阶段入口与来源索引。')
paragraph('本报告保留早期计划、历史实验与最新裁决的版本区分。外部数学复核、发表优先权、实际性能和候选实现资格分别登记。')
doc.add_page_break()
doc.add_paragraph('目录',style='TOC Heading')
tocp=doc.add_paragraph()
field(tocp,' TOC \\o "1-1" \\h \\z \\u ','目录将在文档更新后显示')
doc.add_page_break()
for title,body in SECTIONS:
    doc.add_heading(title,1)
    blocks(body)

doc.add_page_break();doc.add_heading('附录A 全部阶段目录与回查入口',1)
paragraph('本表按研究阶段列出当前研究树中的主路线、平行分支与裁决入口。正文聚合相互依赖的结果；下列条目保留每个阶段的版本身份。sources、原始实验与监督记录由对应目录继续回查。目录链接指向本地原件，本报告生成过程中原件保持只读。')

preferred=['DECISION.md','VERDICT.md','CONTRIBUTION_VERDICT.md','FINAL_THEOREM_AND_CONTRIBUTION.md','EXPLORATION_STATUS.md','REPORT.md','README.md','FINAL_STATUS.json','VERDICT.json','REVIEW_VERDICT.json','RESEARCH_CONCLUSION.md','NOVELTY_ASSESSMENT.md','NOVELTY_DECISION.md','RESEARCH_DECISION.md','ROUTE_DECISION.md','FINAL_DECISION.md','PROOF_DECISION.md','REVIEW_DECISION.md','PRIORITY_VERDICT.md','PRIORITY_UPDATE.md','MATH_MAPPING_AND_DECISION.md','NOVELTY_AND_DECISION.md','SOURCE_AND_VERSION.md','PARADIGM_PROPOSAL.md','NEW_HYPOTHESIS.md','RESEARCH_OUTLOOK.md','PRIOR_ART_AND_STATUS.md','MAIN_THEOREM.md','MODEL_AND_REDUCTION.md','DECISION.json','CURRENT_STATUS.md','FINAL_VERIFICATION.json']
stage_records=[]
for ix,(label,rel,summary) in enumerate(STAGES,1):
    d=ROOT/rel
    if not d.is_dir():raise FileNotFoundError(d)
    candidates=[d/n for n in preferred if (d/n).is_file()]
    if not candidates:
        candidates=sorted(d.glob('*.md'))+sorted(d.glob('*.docx'))+sorted(d.glob('*.json'))
    target=candidates[0] if candidates else d
    p=doc.add_paragraph();p.paragraph_format.keep_with_next=True
    r=p.add_run(f'{ix:02d}  {label}');r.bold=True;r.font.size=Pt(10.5)
    p.paragraph_format.space_after=Pt(3);p.paragraph_format.line_spacing=1.15
    summary_p=paragraph(summary);summary_p.paragraph_format.keep_with_next=True
    summary_p.paragraph_format.space_after=Pt(3);summary_p.paragraph_format.line_spacing=1.15
    for rr in summary_p.runs:rr.font.size=Pt(10)
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(8);p.paragraph_format.line_spacing=1.0
    display=rel.replace('research_main_innovation/main_topic_selection/','R2/').replace('research_main_innovation/','R1/')
    hyperlink(p,display.replace('_','_\u200b').replace('/','/\u200b'),d.as_uri(),9)
    if target.is_file():
        sid=register(str(target.relative_to(ROOT)))
        r=p.add_run('  入口 ['+sid+']');r.font.size=Pt(9)
    stage_records.append({'index':ix,'label':label,'directory':rel,'summary':summary,'entry':str(target.relative_to(ROOT))})

doc.add_page_break();doc.add_heading('附录B 来源与版本索引',1)
paragraph('来源编号对应正文及附录A。R0 表示 D:/毕业设计；R1 表示 R0/research_main_innovation；R2 表示 R1/main_topic_selection。路径链接打开原始文件。每条显示本次读取时的 SHA256 前16位，完整摘要保存在报告构建记录中；摘要仅承担版本固定。原始论文的来源 URL、DOI、完整摘要及实际核读页码继续以各 sources 阅读记录为准。')
for s in sources:
    rel=s['path'];display=rel
    if rel.startswith(TOP):display='R2/'+rel[len(TOP):]
    elif rel.startswith('research_main_innovation/'):display='R1/'+rel[len('research_main_innovation/'):]
    else:display='R0/'+rel
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(1);p.paragraph_format.keep_with_next=True
    r=p.add_run('['+s['id']+'] ');r.bold=True;r.font.size=Pt(9)
    hyperlink(p,display.replace('_','_\u200b').replace('/','/\u200b'),(ROOT/rel).as_uri(),9)
    p=doc.add_paragraph('SHA256 '+s['sha256'][:16]+'…  |  '+str(s['size'])+' bytes')
    p.paragraph_format.space_after=Pt(7)
    for r in p.runs:r.font.size=Pt(8)

doc.add_page_break();doc.add_heading('附录C 主要术语与阅读边界',1)
table([
['术语','本报告含义'],
['共同关系 R','所有坐标共享的显式允许二元模式集合；逐坐标域版本另列。'],
['模式与标签','模式决定某列所有中心的预测；标签决定一行由哪个中心解释。'],
['实际 profile','固定行标签后，某个模式在所有原行上的预测列。'],
['高型','原观测列型重数严格大于当前半径r；重数按原输入计。'],
['β','支撑图独立环数，等于边数减点数加连通分量数。'],
['M_r','原子单任务重绑、独立根及完整退役等假设下的条件资源模型。'],
['FPT','参数函数乘输入固定次数多项式；函数和参数映射必须明确。'],
['T3 与 T+','T3为一般半径共同关系上界；T+为半径一成本、列表和模式域推广。'],
['显示上界差','已推导算法保证的表达式差别；最强方法必要代价另证。'],
['原游戏攻击','查询、暴露、结束与闭包均满足被分析论文的准确游戏。'],
['增强接口攻击','增加普通随机带等权限后的分析；原论文范围分别核对。'],
['知情模型辅助','已接触项目证明或历史推导的AI参与分析；外部人工审阅另记。'],
['先例未决','已核读范围有限或桥接未闭合；保持具体来源责任。'],
['历史实验','已有记录中的运行；本次汇总没有重新执行。'],
['候选实现门','具体族、统一度量、最强G及同能力严格必要代价实例先行。'],
])
paragraph('版本更新要点：本文采用2026年11月8日的FI最终引用状态、MT-1补回强参考后的贡献口径、B4-1四profile紧二环结果及最新有界误差询问结果。较早稿中的建议和未决状态，结合对应后继目录阅读。')

props=doc.core_properties
props.title='AI智能体授权与凭证管理研究历程及成果总报告'
props.subject='从初期选题到2026年11月8日的研究结果与进度'
props.author='研究者与模型辅助整理'
props.keywords='AI智能体 授权 凭证管理 参数算法 可更新加密 研究历程'
props.comments='历史来源保持原字节；数学、先例、外审、应用及实现资格分层。'
doc.save(DEST)
(OUT/'_build'/'source_manifest.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'_build'/'stage_index.json').write_text(json.dumps(stage_records,ensure_ascii=False,indent=2),encoding='utf-8')
full='\n'.join(p.text for p in doc.paragraphs)
issues=[]
if '不是' in full or '而是' in full:issues.append('prohibited contrast wording')
if '{ref:' in full:issues.append('unresolved reference')
report={'output':str(DEST),'sources':len(sources),'stages':len(STAGES),'sections':len(SECTIONS),'paragraphs':len(doc.paragraphs),'tables':len(doc.tables),'characters_main_paragraphs':len(full),'checks':issues}
(OUT/'_build'/'build_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
