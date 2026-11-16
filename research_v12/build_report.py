"""Research report from frozen raw results, preserving limitations and negatives."""
import bootstrap
import json,re,statistics
from collections import defaultdict,Counter
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
R=bootstrap.ROOT
def load(p):return json.loads((R/p).read_text(encoding='utf-8'))
def main():
    data=load('runs/dev02/analysis.json');repeat=load('runs/replay_report.json');dyn=load('runs/dynamic01/summary.json');fuzz=load('runs/fuzz01/analysis.json');gate=load('runs/ab3_gate02/result.json');struct=load('runs/structure_gate02/result.json');corpus=load('runs/transfer_corpus01/summary.json');reg=load('runs/regression/result.json')
    d=Document();sec=d.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11);sec.top_margin=sec.bottom_margin=Inches(.72);sec.left_margin=sec.right_margin=Inches(.76)
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
        s=d.styles[name];s.font.name='Times New Roman';s.font.color.rgb=RGBColor(0,0,0);s.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体' if name=='Normal' else '黑体')
        s.font.size=Pt(11.5 if name=='Normal' else {'Title':23,'Subtitle':12,'Heading 1':16,'Heading 2':13,'Heading 3':12}[name])
        s.paragraph_format.space_after=Pt(6);s.paragraph_format.line_spacing=1.15
        for node in list(s.element.xpath('.//w:pBdr')):node.getparent().remove(node)
    d.styles['Normal'].paragraph_format.widow_control=True
    def p(text,bold=False):
        pp=d.add_paragraph();rr=pp.add_run(text);rr.bold=bold;return pp
    def h(text,level=1):return d.add_heading(text,level)
    def eq(text):
        pp=d.add_paragraph();pp.alignment=WD_ALIGN_PARAGRAPH.CENTER
        math=OxmlElement('m:oMath')
        def mr(text):
            run=OxmlElement('m:r');tx=OxmlElement('m:t');tx.text=text;run.append(tx);return run
        if 'Q*(U)' in text:
            before,after=text.split('Q*(U)',1);math.append(mr(before))
            sup=OxmlElement('m:sSup');base=OxmlElement('m:e');base.append(mr('Q'));power=OxmlElement('m:sup');power.append(mr('*'));sup.append(base);sup.append(power);math.append(sup);math.append(mr('(U)'+after))
        else:math.append(mr(text))
        pp._p.append(math)
    def table(headers,rows,widths=None):
        t=d.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
        widths=widths or [6.98/len(headers)]*len(headers)
        for i,w in enumerate(widths):t.columns[i].width=Inches(w)
        for i,x in enumerate(headers):t.rows[0].cells[i].text=str(x)
        for row in rows:
            cells=t.add_row().cells
            for i,x in enumerate(row):cells[i].text=str(x)
        for ri,row in enumerate(t.rows):
            for i,cell in enumerate(row.cells):
                cell.width=Inches(widths[i]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                tcPr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
                for edge in ['top','left','bottom','right']:
                    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
                tcPr.append(borders);mar=OxmlElement('w:tcMar')
                for edge in ['top','bottom','left','right']:
                    e=OxmlElement('w:'+edge);e.set(qn('w:w'),'90');e.set(qn('w:type'),'dxa');mar.append(e)
                tcPr.append(mar)
                if ri==0:
                    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'DCE6F1');tcPr.append(shade)
                for pp in cell.paragraphs:
                    pp.paragraph_format.space_after=Pt(3);pp.paragraph_format.line_spacing=1.05
                    pp.paragraph_format.keep_with_next=ri<2
                    for rr in pp.runs:rr.font.size=Pt(10);rr.bold=ri==0
            no=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(no)
        rep=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(rep);d.add_paragraph()
    d.add_paragraph('A、B与AB结构性算法深化及\n动态核心传递验证研究报告',style='Title')
    d.add_paragraph('v1.2 · 有限实现、强对照与条件性贡献',style='Subtitle')
    p('面向 AI 代理的认证语义安全识别与可撤销性驱动凭据配置系统',True)
    p('2026年11月3日｜开发研究交付｜独立目录 research_v12')
    p('本阶段已将 AB3 从规范推进为可运行、可检查的动态证书传递原型，接入完整原生 B 与统一控制策略求解；A4 和 B4 均形成最小正确实现。主批次完成两轮各688次运行，八组合与精确参考在声明输入内一致。最强可保留结构结果是 B4 对零费用语义等价路径的类数压缩与全局字典序保持；通用相同预处理能够复现，三项独立原创算法优势尚未成立。')
    table(['层次','本轮判断'],[
        ['算法与参考一致','已取得有限开发证据；所有正式假设仍未测试'],
        ['机制与旧版本不同','AB3动态重放、A4价值证书单元、B4语义类压缩已实现'],
        ['运行更快','B4在别名丰富子族有净计算收益；整体/通用等价优势不成立'],
        ['可证明结构性质','B4由原路径数指数枚举降为类数指数枚举；其余为条件性充分条件'],
        ['原创性','尚未排除价值抽象、增量证明复用和通用预处理等效']],[1.6,5.3])
    h('1 继承依据、真实基线与未修改范围')
    p('完整阅读 v1.1 及代码审查的范围沿本会话材料记录继承。权威 v1.1 SHA256 为 7ba78ed7c1ce45a73872a8c82b95f18c2624680ebbaa512aff3932883a67ebe4。新增目录不改 auth-lifecycle、v1.0/v1.1 源码、历史实验和成本函数。无可用 Git 提交，以源码哈希定位；旧 Keycloak H2 文件因运行占用无法读取，单列为未核验。')
    p('交付时5393个可读历史文件中，5392个与起始哈希一致；auth-lifecycle/.runtime/l1/processes.json已发生变动。本轮没有写入该路径，变更来源未归因，亦未恢复或覆盖它；因此全体可读文件保留检查明确为false。除该运行时元数据之外，本轮核对的源码、报告及历史结果未发现变化。')
    table(['对象','实际入口／机制','必须保留的负结果'],[
        ['A2/A3','旧 a_ab_search.py；早承诺/完整未来签名','A2被通用BB复现；A3旧3例零命中'],
        ['B2/B3','旧 b_units.py / b_components.py','B2预处理偏高；B3旧20例仅3次分解'],
        ['AB2','旧 drd_bound；静态下界及动态回退','下界有效但无净收益'],
        ['旧联合B','common.py:fixed_b_choice','B2Select目录入口，非完整B求解'],
        ['AB3','本轮 oracle.py / independent.py','此前没有已验证实现'],
        ['密码学','v1.1第13—19节原件完整保留','等效分块、成功域损失和端到端成本缺口']],[.9,3.0,3.0])
    p('原 v2.15、v2.16、四阶段融合与历史证据的限制继续有效。四阶段独立 schema/SQL 附件未取得；不由文件名推断实现。原有40输入/260运行及密码学898/70/21断言、32个MPC场景均为历史结果，不计入本轮新增数量。')
    h('2 共同模型、条件性论证与算法实现')
    eq('U = (K, z, O, V, Γ, r),     K ≠ ∅')
    eq('L(U) ≤ Q*(U) ≤ Q(π, U)')
    # Full proof narrative; markdown headings become document subheadings.
    formal=(R/'FORMAL.md').read_text(encoding='utf-8')
    for block in formal.split('\n\n'):
        if block.startswith('# ') or block.startswith('以下为'):continue
        if block.startswith('## '):h(re.sub(r'^(\d+)\.',r'2.\1',block[3:]),2)
        elif block.strip():p(block.replace('`','').replace('2^p','2ᵖ').replace('2^k','2ᵏ').replace('d^w','dʷ'))
    h('3 开发协议、范围与计算成本口径')
    p('protocol.json 在 v1.2 测量前登记。本轮为算法开发；所有生成输入均是开发集，没有使用确认性留出配置。H-A/H-B/H-AB 原建议阈值保持待确认，不计算正式支持判定。H-S 的模型、实现与真实服务符合性分开登记。')
    p('每个主运行限制4个逻辑CPU、8GiB进程内存、30秒共享周期；父进程32秒含启动兜底。该限制已由运行器记录，宿主机并非独占。主比较计入编译、独立源映射审计、原生B构建、缓存、证书、求解、最终检查和评分；另列含Python启动的时间。模型中同一成本价格表可见于所有方法，未增加原生接口。')
    p('联合22个输入：12个核心/边界案例、8个任务参数组合、1个迟到停止故障、1个价值合并正例。最多2任务、4语义、2探测、深度3。原生B48输入：24个别名参数组合、3个费用/预算反例、21个沿用形状但重新声明H≤3的回归输入；最多4任务、12路径。后续24个固定种子结构输入为补充开发诊断。原语法只支持4探测和6联合路径，未覆盖W0允许的全部8探测范围。')
    p('所有 FEASIBLE、界内 IMPOSSIBLE、UNKNOWN 均保留。未完成按原开发评分器使用 budget+1 惩罚；这是模型评分，不是实际服务费用。TIMEOUT/INCONCLUSIVE若发生也保留，不从分母删除。本轮未发生这两类主批次结果不代表实现可处理任意规模。原生服务、AI运行者、非原子配置和实际恢复仍未测试。')
    h('4 自动化正确性、证书与重复运行')
    table(['证据','范围','结果'],[
        ['AB3最小门','12源模型；先于A4/B4性能测量',f"{gate['assertions']}条断言通过"],
        ['结构门','原配置掩码、字典序、反例精化',f"{struct['assertions']}条断言通过"],
        ['传递语料','21非空根的全部即时后继',f"{sum(x['transitions'] for x in corpus['rows'])}次传递；{corpus['assertions']}条核对通过"],
        ['旧核心回归','core与abstraction；不重算原全部实验',f"{reg['tests']}测试；失败{reg['failures']}、错误{reg['errors']}"],
        ['主批次','22×16联合 + 48×7原生B',f"两轮各{data['count']}次；参考一致"],
        ['语义重放','状态/Q/G/配置/策略及安全结果',f"{repeat['count']}条一致={repeat['pass']}"],
        ['固定种子结构','24×7原生B',f"{fuzz['count']}次；参考一致={fuzz['all_decisive_reference_checks_pass']}"],
        ['动态同序列','12家族×6方法',f"{len(dyn['rows'])}批；一致={dyn['pass']}"]],[1.25,3.55,2.1])
    sums=Counter()
    for x in corpus['rows']:
        for k in ['valid','invalid','inconclusive']:sums[k]+=x[k]
    p(f"79次传递分别为 VALID {sums['valid']}、INVALID {sums['invalid']}、INCONCLUSIVE {sums['inconclusive']}。在这份已检查语料中错误复用为0；未推广到所有模型。每份原始JSON含输入、旧证书、完整Post、新结论与控制参考。过期模型版本、删除同观察后继、伪造费用、遗漏证明作用域等拒绝测试保留。")
    p('S1、S2、S3、S4均有合法复用与必须撤回/重算案例。新授权使旧阻塞失效；收缩到三世界核心的某个世界对后可行；新增会话或预算不足使旧见证不能直接使用。控制不可行仍允许探测后成功。UNKNOWN观察标签和空K分别处理，模型外原生重叠效果返回UNKNOWN。')
    h('5 联合八组合：计算收益不能重复归因')
    joint_rows=[]
    for meth in ['F000','F001','F100','F101','F010','F011','F110','F111']:
        m=data['metrics']['J_'+meth];joint_rows.append([meth,f"{m['status'].get('FEASIBLE',0)}/{m['n']}",f"{m['median_seconds']*1000:.1f}",f"{m['p95_seconds']*1000:.1f}",m['counts'].get('native_B_calls',0),m['counts'].get('B_proof_reuses',0),m['counts'].get('abstraction_hits',0)])
    table(['组合','完成/总数','中位ms','p95 ms','原生B调用','核心复用','A4命中'],joint_rows,[.65,.8,.95,.9,1.0,.9,.7])
    p('组合三位依次为新A、新B、动态AB开关。每组均11可行、10界内不可行、1空K UNKNOWN，完成率分母22；所有可行策略无未决义务或安全反例。八组合的最优Q一致，因此没有本轮任务成本Q下降证据。原生G也独立评分，不用token标签计数。A4和AB3若复用了同一子问题，只能作为替代/交互节省，不分拆重复归功。')
    for left,right in [('F001','F000'),('F100','F000'),('F010','F000'),('F111','F000')]:
        q=next(x for x in data['pairs'] if x['candidate']==left and x['baseline']==right)
        p(f"{left}相对{right}：逐输入完整时间比的中位数 {q['median_paired_time_ratio']:.3f}；{q['wins']}/{q['n']}输入更快。这是开发描述量，无显著性或置信区间结论。")
    p('A4在“非必要未来观察不同”正例命中，证明比A3的充分条件更宽；主样本仅一处实际命中，资格检查/重放抵消了节省，尚无完整成本改善。GENERIC_ABSTRACTION得到同一机制。旧A2/A3的策略类含早承诺，单列历史对照，不以跨策略类Q差异证明新A的优势。')
    h('6 AB3与通用增量、R-J及Z3')
    dr=defaultdict(list)
    for x in dyn['rows']:dr[x['method']].append(x)
    table(['方法','同序列批数','中位总ms','合计查询','核心复用'],[[k,len(v),f"{statistics.median(x['seconds'] for x in v)*1000:.1f}",sum(x['query_count'] for x in v),sum(x['counts'].get('B_proof_reuses',0) for x in v)] for k,v in dr.items()],[1.65,.95,1.35,1.2,1.1])
    p('动态对照对所有方法提交同一公开根及全部即时probe后继，包括最优策略本来不会选择的probe，因而是重规划诊断，不是线上请求轨迹。普通联合BB逐根重算；通用增量和SCCP保留相同精确缓存；Z3复用同一约束图。每个查询目标均为完整联合Q，并逐根与R-J核对。')
    pairs=[]
    for x in dr['SCCP']:
        other=next(y for y in dr['INCREMENTAL'] if y['case']==x['case']);pairs.append(x['seconds']/other['seconds'])
    p(f"同序列SCCP相对通用增量的逐家族时间比中位数为{statistics.median(pairs):.3f}。缓存已经覆盖的查询不会再获得核心复用收益。GENERIC_REPLAY使用同一证明机制，因此不能据命名区分原创性。即使减少B调用，也须以完整总时间和内存判断。")
    p('dev01 的Z3行还查询额外即时后继，原日志完整保留；dev02已统一单根工作量，dynamic01另做同序列。旧AB2保持静态检查及正确回退，但仍使用旧目录适配，不能替代八组合的完整B成本。')
    h('7 B4：结构界、实际收益与退化')
    table(['方法','可行/无解/未知','计算中位ms','计算p95 ms','含启动中位ms'],[[k,data['metrics']['B_'+k]['status'].get('FEASIBLE',0).__str__()+'/'+str(data['metrics']['B_'+k]['status'].get('IMPOSSIBLE_IN_MODEL',0))+'/'+str(data['metrics']['B_'+k]['status'].get('UNKNOWN',0)),f"{data['metrics']['B_'+k]['median_seconds']*1000:.2f}",f"{data['metrics']['B_'+k]['p95_seconds']*1000:.2f}",f"{data['metrics']['B_'+k]['process_median_seconds']*1000:.2f}"] for k in ['B4','B2','B3','R_B','GENERIC_BB','Z3_OPTIMIZE','GENERIC_PRESOLVE']],[1.75,1.4,1.1,1.1,1.3])
    cases=['alias_t3_a3_coupled0','alias_t3_a3_coupled1','alias_t4_a3_coupled0','alias_t4_a3_coupled1']
    vals=[]
    for case in cases:
        rr=[]
        for method in ['B4','B2','GENERIC_BB','R_B','GENERIC_PRESOLVE']:
            obj=load(f'runs/dev02/raw/B_{case}_{method}.json');rr.append(f"{obj['total_seconds']*1000:.2f}")
        vals.append([case.replace('alias_','')]+rr)
    table(['参数子族','B4 ms','B2 ms','BB ms','R-B ms','同预处理ms'],vals,[2.0,.9,.9,.9,.9,1.25])
    p('此表列的是预先登记参数网格中的高重复路径子族，不据此删除不获胜输入。4任务×3同语义别名有p=12、k=4：4096个原配置子集压缩为16个类子集，再按全局字典序展开并核验完整计划。非零delegate费用、批准差异和真实不同保留路径不能合并；模型仍可能退化为2^p。')
    for bas in ['GENERIC_BB','R_B','GENERIC_PRESOLVE']:
        q=next(x for x in data['pairs'] if x['kind']=='B' and x['baseline']==bas)
        p(f"全48输入B4相对{bas}的逐输入计算时间比中位数{q['median_paired_time_ratio']:.3f}，更快{q['wins']}/48；含进程启动的时间比中位数{q['median_process_inclusive_ratio']:.3f}。")
    p('计算区间的计时始于共同依赖导入之后，方法特有的加载、求解及检查计入；含启动指标还覆盖进程启动、共同导入与结果写盘。两种口径并列，不能把冷启动开销隐藏为算法收益。动态同序列表采用共同计算区间，不作宿主产品时延验收。')
    p('固定种子增补含不同AND支持、原生共享根、隔离/代理/直连环境、预算和别名数量，完整保留所有结果。该集合用于检查压缩是否依赖纯手工正例，仍不是确认集。它支持模型内正确性，不自动支持总体加速。B4-1的非零接口分解仍未实现，不能把接口宽度诊断当作完成分解。')
    for q in fuzz['pairs']:
        if q['baseline'] in ['GENERIC_BB','R_B','GENERIC_PRESOLVE']:p(f"结构增补相对{q['baseline']}：时间比中位数{q['median_paired_time_ratio']:.3f}，更快{q['wins']}/{q['n']}。")
    h('8 近邻文献与贡献定位')
    p('文献工具连接失败后改用官方原文，原始抓取和失败记录留在literature/。没有把抓取成功、书目提及或文件名当成全文阅读；错误URL返回MEST论文已排除。以下为会改变贡献判断的核验材料，完整台账见LITERATURE.md。')
    for title,body in [
      ('价值保持近邻','Grimm等，The Value Equivalence Principle for Model-Based Reinforcement Learning，2020，https://arxiv.org/abs/2011.03506；DOI 10.48550/arXiv.2011.03506。阅读原文§1—3，未全面审核附录。按规划用途弱化模型等价已有先例；本轮增加的是全分支批准/义务的可检查充分条件。'),
      ('部分可观测资源约束','Bork等，Multi-Cost-Bounded Reachability Analysis of POMDPs，2025，https://proceedings.mlr.press/v286/bork25a.html。核对官方元数据并阅读原文引言；多维实际成本及成本可观测性已有明确研究。本轮鲁棒有限目标不同，但不能断言对方不支持认证应用。'),
      ('决策域与高阶冲突','Javdani等，Near Optimal Bayesian Active Learning for Decision Making，2014，https://proceedings.mlr.press/v33/javdani14.html。阅读§1—2；重叠决策域和超边已有经典来源。有状态核验必须重新证明，三世界例本身不是原创性证据。'),
      ('组合分解与通用增量','Zhang与Beck，Solving logic-based benders decomposition master problems with constraint programming and domain-independent dynamic programming，2025，DOI 10.1007/s10601-025-09382-1。仅出版社摘要/书目，全文未读。Z3官方Basic Commands的Using Scopes已核对：https://microsoft.github.io/z3guide/docs/logic/basiccommands/。'),
      ('继承的安全与账户图工作','Carr等2023部分可观测shielding，DOI 10.1609/aaai.v37i12.26723；Junges等2021 almost-sure reachability，DOI 10.1007/978-3-030-81688-9_28；Tactics for Account Access Graphs，2024出版/ESORICS2023，DOI 10.1007/978-3-031-51479-1_23。阅读范围沿用v1.1，未提升等级。'),
      ('仍未决的直接先例','Transition dominance in domain-independent dynamic programming（2025）由出版社参考文献定位，直接原文连接失败；本轮未验证具体定理。CEGAR原文请求亦失败。不得以未取得全文论证本轮首次。')]:
        h(title,2);p(body)
    h('9 密码学成果继承与重启门槛')
    p('v1.1第13—19节及其原始修订目录完整保留。本轮没有新密码学实验。Crypto-C1保留关系位置的条件不等式，Crypto-C2保留自由行数下允许支持独立的条件，Crypto-C3保留完整独立族下块群不变性、最小行数与轨道熵的条件刻画；均未取得外部/证明助手复核或完整优先权确认。Crypto-C4与Gate仍是公开模型/本地诚实执行的辅助证据研究。')
    p('C3匹配构造等效于简单独立分块；GF(4)限制族拒绝原契约67个可接受输入中的18个；gate后直接公开既有零标志新增秘密乘法为0，但通信/开值非零。原898/70/21断言、32个MPC场景只继承，不作为本轮结果。真实来源保证、组合/恶意安全、原成功域保持、同泄漏/接收者和端到端优势仍缺失，因此证据继续支持暂缓扩大MPC。')
    h('10 反方审查、未完成项与下一阶段进入条件')
    p('本审查由当前研究辅助流程执行，非外部独立同行评审。最强反对意见是：AB3为有限证明重放，A4为证书价值抽象，B4为语义去重；领域化和实现不同不能替代优先权证明。通用对照获得同机制后等效，当前不能宣称三个独立原创算法优势。')
    table(['审查问题','判定与后续门槛'],[
      ['完整B是否真实接入','是；原生单世界全求解+全K控制策略，所有八组合计入。两层目标不同已公开。'],
      ['是否有一般安全证明','否；仅条件手工论证、有限参考和源表一致。需可信原生来源及状态覆盖证据。'],
      ['AB3是否独立优于增量方法','未成立；需更大动态家族及等价通用复用的严格比较，不能只数B调用。'],
      ['A4是否带来净收益','未成立；命中少、资格与重放成本高。需更便宜且充分的合法抽象证据。'],
      ['B4的结构成果','固定等价路径条件下完整目标保持与2^k界成立；相同通用预处理等效。'],
      ['B4-1、L1、真实恢复','仍未完成；非零接口动态规划、原生部署、并发及恢复需独立规格与测试。'],
      ['正式实验进入条件','冻结代码/主要指标/阈值/统计脚本/家族划分/留出配置；先确认独立家族数及功效。']],[2.1,4.7])
    p('下一阶段优先补查直接近邻全文，研究能利用非零费用或跨类保留结构而仍可证明安全的压缩；AB3寻求比完整反驳重放更便宜的依赖充分条件；A4研究可复用的精化谓词。每项都应先给反例与通用等价对照。没有这些证据时，将本轮定位为领域建模、可检查证据和可复现系统研究，而非新通用规划理论。')
    h('11 交付与复现索引')
    p('源码入口：kernel.py、independent.py、oracle.py、joint.py、a4.py、b4.py、smt_joint.py。协议与论证：protocol.json、AUDIT.md、FORMAL.md、LITERATURE.md。原始结果：runs/dev01、dev02、dynamic01、fuzz01、transfer_corpus01及各测试门。README.md给出可复制PowerShell命令。SOURCE_MANIFEST.json、DELIVERY.json与historical_verification.json绑定源码、结果和旧材料状态。')
    for node in list(d.element.xpath('.//w:pBdr')):node.getparent().remove(node)
    for sty in d.styles:
        for node in list(sty.element.xpath('.//w:pBdr')):node.getparent().remove(node)
    path=R/'A、B与AB结构性算法深化及动态核心传递验证研究报告_v1.2.docx';d.save(path)
    print(path)
if __name__=='__main__':main()
