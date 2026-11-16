from pathlib import Path
import re, json, hashlib
from copy import deepcopy
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(r'D:\毕业设计')
WORK = ROOT / '.codex_work/chapter4_20261109'
SOURCE = ROOT / '面向AI智能体的认证语义感知与可撤销凭据管理_调研报告_论证重构版_v2_2026-11-04.docx'
MD = ROOT / '关键论文与可行性核查_2026-11-04/论文与草案逐篇速览_2026-11-04.md'
OUT = ROOT / '面向AI智能体的认证语义感知与可撤销凭据管理_调研报告_第四章更新版_2026-11-09.docx'
WORK.mkdir(parents=True, exist_ok=True)
source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
md = MD.read_text(encoding='utf-8-sig')
doc = Document(SOURCE)
paras = doc.paragraphs
start = next(p for p in paras if p.style.name == 'Heading 1' and p.text.startswith('4 '))
end = next(p for p in paras if p.style.name == 'Heading 1' and p.text.startswith('5 '))
body = doc.element.body
children = list(body)
si, ei = children.index(start._p), children.index(end._p)
before = [deepcopy(x) for x in children[:si]]
after = [deepcopy(x) for x in children[ei:]]
old_heading = deepcopy(start._p)
for x in children[si:ei]:
    body.remove(x)
new = []

def plain(text):
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    return text.strip()

replacements = {
    '不判断指令内容是否有害，而是校验每条指令是否服务于用户目标':'通过校验每条指令对用户目标的贡献判断任务对齐情况',
    'agent 不直接发工具调用，而是生成表达意图的 Scala 3 代码':'agent 通过生成表达操作意图的 Scala 3 代码发起工具使用',
    'CaMeL 不改模型，而是在模型外建保护层':'CaMeL 在模型外建立保护层',
    '当一个平台同时替用户管理多个第三方应用的OAuth授权时，如何保证某次授权从发起、重定向、授权码兑换到令牌保存，始终属于同一个应用和同一个用户授权会话？':'在平台同时管理多个第三方应用的 OAuth 授权时，授权发起、重定向、授权码兑换和令牌保存需要持续绑定到同一应用及用户授权会话。',
    '如果攻击者在MCP工具的描述信息中植入恶意指令，即使Agent从未调用过这个恶意工具，是否仍然能够被诱导去调用其他合法工具，执行用户没有授权的操作。':'MCPTox 考察 MCP 工具描述中的恶意指令对后续调用的影响。攻击者可以借助被投毒的描述信息，诱导 agent 调用其他合法工具执行超出用户授权的操作；投毒工具自身可以始终处于未调用状态。',
    '用户改口之后，先前的授权如何选择性更新？现有方法要么不维护授权状态（只查单次调用），要么整单重新授权。':'用户修改任务要求后，已有授权需要随之选择性更新。ACG 针对逐调用检查和整单重新授权之间的更新粒度问题开展研究。',
    '核心思想：将Agent安全从依赖大模型判断的概率性防护，推进到由独立安全策略和形式化验证支撑的可验证安全约束。':'该研究将独立安全策略与形式化验证引入 agent 工具使用过程。',
    '中科院信工所目前国内互联网中心一把手':'中科院信工所',
    'ACM 新会，主要研究AI 智能体、复合 AI 系统、系统优化、安全性与工程化，水平较高。':'该会议主要关注 AI 智能体、复合 AI 系统、系统优化、安全性与工程化。',
    'ICSE 是CCF A':'CCF A。',
    '它攻匿名凭证系统的':'该研究关注匿名凭证系统的',
    '实验很说明问题：':'作者的实验进一步比较了授权信息的可获得性。',
    '（追加推理也绕不过）':'',
    '——失败在"信息获取"，不在推理':'。这一结果表明，可信授权信息的可获得性会直接影响判断结果',
    '堵幻觉/注入的工具名':'检查幻觉或注入产生的工具名',
    '单击':'单击',
    '今天的 agent 运行时要启用动作，就得把':'现有部分 agent 运行时在执行动作前需要把',
    '先做 205 人情景模拟用户研究':'首先开展 205 人情景模拟用户研究',
    '拿到记录的签名证书':'取得记录的签名证书',
    '拿到验证者份额':'取得验证者份额',
    '进模型上下文':'进入模型上下文',
    '全部精确为 0%':'均为 0%',
    '压到':'降至',
    '反而超过':'高于',
    '做到 4.76% 成功率':'将攻击成功率降至 4.76%',
    '拉完了':'',
    '三个 Qwen 变体':'三个 Qwen 变体',
    '挡 得住部分直接攻击、防不了精心构造的特权劫持':'能够阻断部分直接攻击，面对精心构造的特权劫持仍存在明显风险',
    '无一份进入工作组正式文本':'各文档的采纳状态和成熟度仍需按对应版本分别核对',
    '核心论断："重试与恢复是权威转移，而非传输细节。"':'作者将重试与恢复视为授权权威转移的一部分，要求恢复过程持续遵守原有批准与效果约束。',
    '绝不铸造替代授权':'持续保留原批准的唯一性',
    '攻击者不劫持控制流，只污染数据流（篡改工具调用参数）就能实现数据外泄':'攻击者可以通过污染数据流、篡改工具调用参数造成数据外泄，控制流在此过程中仍可能保持原有结构',
    '凭证从不是 agent 持有的值':'凭证保存在可信执行边界内',
    '而非依赖模型行为':'，由授权结构独立强制执行',
    '全文是路线图而非实验或形式化证明。':'论文以研究路线和协议框架论证为主，实验评估与形式化证明仍有待补充。',
    '而非 agent 委托凭证':'，与 agent 委托凭证具有不同的管理粒度',
    '同时破坏授权与认证两大安全目标':'同时影响授权与认证安全目标',
    '——事实上的委托链格式锚点':'，为两份草案之间的互操作提供统一格式',
    '最完整标准化文本':'较完整的标准化框架',
    '最完整的一份':'较完整的文档之一',
    '最强的草案（作者阵容含 Okta/Cisco/阿里）':'较具体的草案',
}

relations = {
'P19':'对于本课题，SAGA 将用户对 agent 的控制落实为身份登记、一次性密钥、过期时间与请求配额，可以作为系统能力层的直接对照。P01 的相关工作比较也纳入了该系统。',
'P21':'这一工作为动态授予与撤销提供了用户行为依据。其过度授权测量、偏好学习和置信度门控，可以用于设计授权交互与评价基线。',
'P22':'本课题可以借鉴其委托凭证框架，组织签发、验证、过期和跨 agent 传递过程，并明确 OIDC、OAuth 与可验证凭证之间的衔接关系。',
'P27':'这项工作将多跳委托的权限衰减与时间窗结合，能够为委托凭证的颁发、收窄和到期处理提供实现参照。',
'P28':'APEX 的 RAD 模型为受限委托授权提供了形式化依据。其加密资源注册、检索、密钥重封装和删除流程，也可用于分析凭证保密与资源访问之间的关系。',
'P35':'对于本课题，AGentVLM 可支持授权策略生成、部署前验证和修正反馈。其研究对象是组织级访问控制策略，具体应用时还需建立与 agent 委托凭证之间的映射。',
'P37':'CapChain 在编排器状态转移层实现了能力令牌与可验证溯源，可作为代理间授权、委托收窄、防重放和审计的直接比较对象。',
'P23':'Task Shield 为动作与用户任务之间的关系提供了形式化描述及拦截反馈机制。本系统可以据此将意图检查与凭证验证结合。',
'P25':'这项实证研究支持在 MCP 工具发现和调用环节设置独立授权执行点，为凭证使用过程中的工具访问控制提供基础设施层的实现依据。',
'P26':'该研究把工具能力、数据保密性和信任级别纳入形式化约束，能够支持本课题建立可验证的工具使用模型。其未来工作还涉及过度委托，适合继续追踪。',
'P29':'AgentBound 展示了 MCP 服务器从权限声明、用户同意到沙箱执行的完整过程。本系统可以据此明确 API Key、环境变量和本地文件等凭证资源的访问需求。',
'P30':'这一方法把能力的授予、传递、捕获和作用域到期纳入静态类型检查，为凭证生命周期管理提供了语言层的实现路线。',
'P31':'该基准可用于评价 agent 的最小权限工具选择。其训练方法也说明，授权层的强制控制可以与 agent 侧的行为改进共同开展。',
'P32':'AgentSpec 提供可执行的运行时规则及轨迹语义，可以作为权限边界和凭证使用策略的落地组件。P06 的比较基线也包含该工作。',
'P39':'ProbGuard 为危险或越权操作发生前的风险预警提供了概率模型与 PAC 分析依据。它与 P32 出自同一团队，可结合比较主动预测和运行时强制的适用条件。',
'P36':'GrantBox 直接测量 agent 持有真实凭证时的特权滥用后果。其真实服务、容器隔离和攻击用例设计，可以作为本课题端到端实验的方法参照。',
'P38':'MCPTox 将工具元数据纳入威胁模型，并提供工具调用前授权校验的可复用攻击基准。评价时需要同时检查工具发现过程与实际调用过程。',
'P20':'该工作揭示了 agent 类平台代用户完成 OAuth 委托时的跨应用绑定风险。它与 P07 构成同一研究团队在集成平台和连接器生态中的两组测量依据。',
'P08':'RAG 将账号、凭据及访问依赖的动态变化纳入自动模型检测，可为本课题验证凭证生命周期策略提供完整的方法参照。',
'P24':'PRC 将凭证撤销扩展到大规模、隐私保护的状态校验基础设施，可用于分析 agent 持有匿名凭证或可验证凭证时的撤销与出示成本。',
'P14':'DECO 支持把 Web 账号中已有的数据转化为可验证声明，为凭证来源证明和隐私化出示提供基础。其后续实用化路线可结合总览中的 P15 继续比较。',
'P01':'SUDP 是凭证交付与执行边界的直接对照。它把授权具体化为一次性、操作绑定的许可，可用于分析长期秘密保管与单次授权执行之间的关系。',
'P02':'PAuth 为任务要求与具体操作参数之间的绑定提供直接参照，其 AuthBench 也可用于评价任务级授权与最小充分委托。',
'P40':'ASTRA 将任务语义匹配放在 OAuth 授权服务器侧，通过最小 scope 签发和任务结束回收约束凭证生命周期，可与 P02 的逐工具规则路线比较。',
'P41':'CASA 把确定性结构检查与语义任务匹配结合，并扩展到多轮及多 agent 场景。它与 P02、P45 共同构成本课题任务级授权的重要比较集合。',
'P42':'弹性最小特权模型为基线、权限包络、租约、预算和回收提供统一描述，可用于组织本课题的动态权限管理。其机制价值仍需结合后续实现与实证检验。',
'P43':'Progent 通过策略生成、SMT 判定与显式批准管理权限更新，是动态授予与最小权限收敛的直接比较对象，也是 P06 的基线之一。',
'P45':'意图凭证与本课题的请求级最小权限管理紧密相关。它与 P03 出自同一作者团队，两项工作分别覆盖请求级签发和授权生命周期终止，适合结合分析。',
'P05':'AID-Guard 关注准入之后至效果落地之前的授权状态，能够支持本系统处理重试、丢响应、配额预留和唯一后继等执行问题。',
'P06':'ACG 为授权修订提供了版本化、选择性失效和最小修复机制，可作为本课题处理用户指令变化及旧授权重验证的运行时对照。',
'P13':'CaMeL 的能力标签与信息流强制为凭证和敏感数据的受控流动提供系统参照。比较时需要记录其任务完成率、攻击覆盖及额外 token 成本。',
'P44':'不可逆性预算将逐次授权扩展到跨 agent、工作流和租户的累积核算。其预算、预留和冻结机制可与 P05 的效果闭环及 P11 的代价有界验证结合分析。',
'P03':'根域授权静止为撤回授权后的残余能力提供可验证的收尾协议，可直接支持本课题区分令牌处置、后代终止和在途效果处理。',
'P04':'ResidualAuth 从信息论角度刻画撤销后必须持续保留的可信授权信息，为本课题确定状态记录、授权来源和补证需求提供理论依据。',
'P17':'HBHC 提供基于签名心跳的离线新鲜度验证，可用于比较在线撤销与离线校验的传播条件、认证成本和确定性终止窗口。',
'P18':'Vault 中介执行边界从保管、注入与轮换环节补充凭证生命周期分析。其阴性结果也要求本系统分别检查集中托管能力与配置正确性。',
'P07':'OASIS 为 agent 和连接器获取凭证时的账号错链风险提供实测依据，其用户、租户与连接器绑定要求可进入本系统的接入检查。',
'P33':'受众注入攻击补充了客户端认证和签发阶段的协议威胁模型。其受众绑定规则可用于检查 agent 使用的 OAuth 与 OIDC 凭证流程。',
'P34':'该研究为本课题提供覆盖 MCP 生命周期的威胁分类，其中凭证窃取、版本升级后的权限残留及越权访问与当前研究直接相关。引用时需保留预印本和愿景论文属性。',
'D1':'D1 提供按 agent 发起批量撤销的在线接口路线。D8 进一步描述撤销传播后的完成条件，两者可以结合分析撤销请求与最终状态之间的关系。',
'D2':'D2 可作为委托衰减、链式凭证和离线验证的协议比较对象。D6 采用其令牌格式实现互操作，为两份草案之间的组合提供了具体依据。',
'D3':'Mission 将一次批准组织为持久、可审计且可撤销的授权对象，并区分签发治理与逐动作执行。它在八份草案中具有较完整的配套协议描述。',
'D4':'D4 将批准记录、披露内容和撤销状态连接为可核验的证据对象，可支持本课题的授权问责与审计设计。历史批准证据还需与当前有效权限分别核对。',
'D5':'D5 连接凭证、执行证据发现与单次调用准入，可作为委托链记录和可验证审计的配套机制。其依赖草案与实现成熟度需要一并登记。',
'D6':'D6 覆盖身份引导、委托签发、代理行使、子委托、撤销和审计，并与 D2 明确互操作，是本课题凭证全生命周期的重要标准化比较对象。',
'D7':'D7 把授权限制到具体对话，并通过上下文哈希和持有者绑定约束跨对话重放，为凭证使用场景提供会话粒度的协议依据。',
'D8':'D8 为撤销后委托权限的闭环判定给出明确条件，其 epoch、barrier、闭环谓词与保守判定同 P03 具有直接对应关系，可用于比较论文与标准草案的保证范围。',
}

def revise(text, key=None):
    text = plain(text)
    for a,b in replacements.items():
        text = text.replace(a,b)
    text = text.replace('。它研究', '。该工作研究')
    text = text.replace('核心机制：', '具体机制包括：').replace('机制：', '其实现机制为：')
    text = text.replace('两步走：', '研究分为两个阶段。').replace('三步路线：', '研究路线分为三个步骤。')
    text = text.replace('实验：', '作者报告的实验结果为：').replace('评估：', '评估中，')
    text = text.replace('结果：', '作者报告，').replace('它的核心论点是三者区分：', '该草案区分三个完成条件：')
    text = text.replace('它针对的是', '该研究针对').replace('它针对', '该研究针对').replace('它解决', '该工作研究')
    text = text.replace('它提出', '该工作提出').replace('它指出', '该研究指出').replace('它研究', '该工作研究')
    text = text.replace('它形式化', '该工作形式化').replace('它标准化', '该草案规定').replace('它把', '该工作将')
    text = text.replace('它论证', '该论文论证').replace('它首次', '该研究首次').replace('它补 ', '该草案补充 ')
    text = text.replace('它是首个', '该工作提出首个')
    text = text.replace('——', '，').replace(' vs ', ' 与 ')
    text = re.sub(r'，{2,}', '，', text).replace('。，', '。')
    return text

def formatted_runs(p, text, base_size=None):
    # Preserve inline emphasis and code typography from the source.
    parts = re.split(r'(\*\*.*?\*\*|`[^`]+`|\*[^*]+\*)', text)
    for part in parts:
        if not part: continue
        bold = part.startswith('**') and part.endswith('**')
        italic = not bold and part.startswith('*') and part.endswith('*')
        code = part.startswith('`') and part.endswith('`')
        val = part[2:-2] if bold else part[1:-1] if italic or code else part
        r=p.add_run(val)
        if bold: r.bold=True
        if italic: r.italic=True
        if code: r.font.name='Consolas'
        if base_size: r.font.size=Pt(base_size)
    return p

def addp(text, style='Normal', kind=None):
    p=doc.add_paragraph(style=style)
    # Move to the exact original chapter position immediately.
    body.remove(p._p)
    end._p.addprevious(p._p)
    new.append(p._p)
    formatted_runs(p,text)
    f=p.paragraph_format
    if style.startswith('Heading'):
        f.first_line_indent=Pt(0); f.keep_with_next=True
        f.keep_together=True
        sizes={'Heading 1':16,'Heading 2':12.5,'Heading 3':11.5,'Heading 4':11}
        for r in p.runs:
            r.font.color.rgb=RGBColor(0,0,0);r.font.size=Pt(sizes[style]);r.bold=True;r.italic=False
            r.font.name='Times New Roman'
            r._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'黑体')
    else:
        f.keep_with_next=False; f.keep_together=False
        if kind=='meta':
            f.first_line_indent=Pt(0)
        elif style=='Normal':
            f.first_line_indent=Pt(22)
    return p

def addbody(text):
    # Separate long mechanism paragraphs at sentence boundaries for sustained reading.
    sentences=re.findall(r'.+?[。](?:[”"])?|.+$', text)
    acc=''
    for sentence in sentences:
        if len(acc)>175 and len(acc)+len(sentence)>320:
            addp(acc);acc=''
        acc+=sentence
    if acc: addp(acc)

def make_table(rows, caption):
    cap=addp(caption, 'Caption');cap.paragraph_format.keep_with_next=True
    table=doc.add_table(rows=0,cols=5)
    body.remove(table._tbl);end._p.addprevious(table._tbl);new.append(table._tbl)
    table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
    widths=[0.40,1.12,2.37,1.48,1.16]
    for c,w in zip(table.columns,widths):c.width=Inches(w)
    pr=table._tbl.tblPr
    borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
    pr.append(borders)
    margins=OxmlElement('w:tblCellMar')
    for side,value in [('top',65),('bottom',65),('left',75),('right',75)]:
        el=OxmlElement('w:'+side);el.set(qn('w:w'),str(value));el.set(qn('w:type'),'dxa');margins.append(el)
    pr.append(margins)
    for i,row in enumerate(rows):
        cells=table.add_row().cells
        trpr=table.rows[-1]._tr.get_or_add_trPr()
        cant=OxmlElement('w:cantSplit');trpr.append(cant)
        if i==0:trpr.append(OxmlElement('w:tblHeader'))
        for j,(cell,txt,w) in enumerate(zip(cells,row,widths)):
            cell.width=Inches(w);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p=cell.paragraphs[0];p.paragraph_format.first_line_indent=Pt(0)
            p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.08
            p.paragraph_format.keep_with_next=False
            p.alignment=WD_ALIGN_PARAGRAPH.CENTER if j==0 or i==0 else WD_ALIGN_PARAGRAPH.LEFT
            formatted_runs(p, plain(txt),10)
            shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'404040' if i==0 else ('F4F4F4' if i%2==0 else 'FFFFFF'))
            cell._tc.get_or_add_tcPr().append(shade)
            if i==0:
                for r in p.runs:r.bold=True;r.font.color.rgb=RGBColor(255,255,255)
    addp('')

chapter_title='4 关键论文与草案逐篇速览'
hp=addp(chapter_title,'Heading 1')
# Keep original Word bookmarks so existing references into chapter four continue resolving.
for el in list(old_heading):
    if el.tag in [qn('w:bookmarkStart'),qn('w:bookmarkEnd')]:
        hp._p.append(deepcopy(el))
addp('前一章沿代理任务说明了身份、授权范围和访问结束条件之间的关系。本章据已有论文与草案阅读记录，进一步整理这些环节对应的技术方法、实验依据和适用条件，为后续产品比较与选题论证提供具体参照。')
addp('本轮材料总览覆盖 45 篇论文和 8 份 IETF 互联网草案，共 53 份材料。论文按照所登记的发表载体分为正式发表工作与预印本、workshop 或出处待核对的工作，草案单独列示；各组内部继续按照授权、执行、撤销和凭证基础设施等主题组织，沿用 P01 至 P45 和 D1 至 D8 编号。')
addp('阅读时需要同时关注方法和证据范围。系统实现、有限模型验证、立场论证与标准草案分别提供不同层次的依据，文中数值保留对应论文报告的实验条件和比较口径，具体文献及草案状态随版本继续核对。')
addp('材料总览','Heading 2')

table_blocks=re.findall(r'(?m)^\| 编号.*?(?=\n\n)',md,re.S)
assert len(table_blocks)==3
captions=['表4a  正式发表论文总览','表4b  预印本及其他研究材料总览','表4c  IETF 互联网草案总览']
overview_ids=[]
for block,caption in zip(table_blocks,captions):
    rows=[]
    for line in block.splitlines():
        cells=[x.strip() for x in line.strip().strip('|').split('|')]
        if all(re.fullmatch(r'[-:]+',x) for x in cells):continue
        rows.append(cells)
        if re.fullmatch(r'[PD]\d+',cells[0]):overview_ids.append(cells[0])
    make_table(rows,caption)

parts={
'第一部分':'正式发表的相关研究',
'第二部分':'预印本及其他相关研究',
'第三部分':'IETF 互联网草案',
}
part_intro={
'第一部分':'首先考察已经登记正式发表载体的相关研究。这些工作分别从身份与授权、运行时约束、真实攻击测量和形式化建模等方面提供依据。将其放在同一访问生命周期中，可以识别已有能力之间的衔接位置。',
'第二部分':'在上述研究基础上，预印本和其他探索性工作进一步把任务意图、动态权限、在途效果与撤销后状态纳入分析。这部分材料与本课题的研究对象更为接近，比较时需要保留版本、实现成熟度及验证条件。',
'第三部分':'论文提出的能力还需要通过协议对象、接口和互操作规则进入实际系统。以下八份草案分别涉及任务绑定、委托传递、凭据代理使用、证据、对话上下文及撤销闭环，可与前述论文逐项对照。',
}
theme_intro={
'1':'授权建立是访问生命周期的起点。以下工作依次关注 agent 的登记与治理、用户授权决定、可验证委托、时间约束和策略生成，为凭证签发及权限传递提供不同层次的基础。',
'2':'授权关系建立后，还需要在工具使用时持续执行。相关研究分别约束任务对齐、工具可见性、服务器操作能力、数据流和运行轨迹，使批准范围能够落实到具体动作。',
'3':'运行时机制的必要性还需要真实攻击证据支持。以下两项工作把 MCP 服务和工具元数据纳入实验，说明有效凭证与合法工具仍可能被组合为超出用户授权的行为。',
'4':'进一步沿凭据取得过程向前检查，平台需要持续维护用户、应用与授权会话之间的绑定。跨应用攻击测量与动态账号生态模型分别提供协议层和状态演化层的分析依据。',
'5':'在访问与状态变化得到描述后，撤销还面临规模和隐私约束。PRC 从匿名凭证基础设施出发，给出了大规模状态查询与非撤销证明的实现方法。',
'6':'除访问是否有效之外，系统还可能需要证明凭证取得的数据来源，并限制证明过程中披露的信息。DECO 提供了这一方向的基础，相关后续工作及多方策略求值材料同时列入总览。',
'8':'这一组工作围绕任务要求与具体权限之间的关系展开。SUDP 约束秘密使用边界，PAuth、ASTRA、CASA 和意图凭证逐步细化任务匹配粒度，弹性最小特权与 Progent 则进一步处理权限的动态调整。',
'9':'任务级批准需要延续到实际效果落地。以下研究分别处理重试恢复、授权修订、数据传播和累积风险，说明逐次准入还需与持续状态及执行结果关联。',
'10':'当用户撤回授权时，系统还要处理后代能力和已经传播的状态。根域静止、残余授权状态、签名心跳与凭证托管分别从完成条件、信息需求、离线校验和秘密保管提供分析依据。',
'11':'最后回到接入协议与 MCP 生态，以下工作补充账号错链、客户端认证和工具生命周期中的攻击面，使本课题的威胁模型覆盖凭据取得、使用及维护过程。',
}
theme_titles={
'1':'授权建立与委托机制',
'2':'运行时强制与工具最小权限',
'3':'MCP 生态威胁与实证测量',
'4':'OAuth 账号绑定与动态生态建模',
'5':'撤销与凭证基础设施',
'6':'凭证数据的来源证明与隐私保护',
'8':'任务意图与动态权限管理',
'9':'运行时状态与效果闭环',
'10':'撤销后状态与凭证托管',
'11':'OAuth 与 MCP 的协议及生态威胁',
}

# Parse the actual saved Markdown, including all current per-item body paragraphs.
content=md[md.index('# 第一部分'):]
blocks=re.split(r'\n\s*\n',content)
current=None;current_name=None;part=None
detail_ids=[]
observations=False
for block in blocks:
    block=block.strip()
    if not block or block=='---':continue
    if block.startswith('# '):
        part=next(k for k in parts if k in block)
        addp(parts[part],'Heading 2');addp(part_intro[part]);current=None
    elif block.startswith('## 横向观察'):
        observations=True;break
    elif block.startswith('## '):
        raw=plain(block[3:]);num=re.match(r'(\d+)\.',raw).group(1)
        title=theme_titles[num]
        addp(title,'Heading 3');addp(theme_intro[num]);current=None
    elif block.startswith('### '):
        raw=plain(block[4:]).replace('（重要）','').replace('（拉完了）','').strip()
        current=re.match(r'([PD]\d+)',raw).group(1)
        current_name=raw.split('·',1)[-1].strip()
        detail_ids.append(current)
        addp(raw.replace(' · ',' '),'Heading 3' if part=='第三部分' else 'Heading 4')
    elif block.startswith('**标题/'):
        text=revise(block)
        text=text.replace('注意：PDF 页眉年份/DOI 为未替换的 ACM 模板占位符，引用以 ACM Reference Format 块为准。','其 PDF 页眉中的年份与 DOI 为模板占位信息，引用需依据 ACM Reference Format 块核对。')
        addp(text,kind='meta')
    elif block.startswith('**与课题关联'):
        addp(relations[current])
    else:
        text=revise(block,current)
        if text.startswith('该研究') or text.startswith('该工作') or text.startswith('该论文') or text.startswith('该草案'):
            subject='该草案' if current.startswith('D') else current_name+' '
            text=re.sub(r'^该(?:研究|工作|论文|草案)',subject,text,count=1)
        addbody(text)

addp('横向观察与后续比较依据','Heading 2')
observations=[
'从发表载体看，总览中的 45 篇论文有 27 篇登记为正式发表，占 60%。P01 至 P18 中的 12 篇 2026 年预印本仍集中讨论授权、委托与撤销，新增工作则扩展到软件工程和人工智能会议。安全会议、ICSE、FSE、ASE，以及 AAAI、ACL、EMNLP、ICML 和 CAIS 等渠道共同构成相关研究来源。正式版与预印本之间的版本对应关系仍需逐篇核对。',
'从标准化关系看，八份草案已经形成相互组合的线索。D6 采用 D2 的委托链令牌格式，D8 补充 D1 在撤销传播之后的完成条件，D5 连接 WIMSE AIMS 与执行证据，D3 则配有任务授权相关草案。它们分别覆盖签发门控、链上传递、证据审计、会话绑定与终止回收，具体采纳状态、依赖关系和实现成熟度需要按版本登记。',
'从撤销问题看，P03、P17、P04、P24 和 P18 分别提供静止判定、心跳校验、残余状态下界、大规模撤销基础设施与凭证托管依据；D1 和 D8 对应撤销请求和闭环状态。尤其 P03 与 D8 对权限纪元、围栏、完成谓词和证据不足时的保守判定具有直接对应关系，可以用于检查本课题停止目标及验证条件。',
'从威胁证据看，P07 与 P20 连接集成平台和连接器生态的账号绑定测量，P33 补充 aud 声明相关的协议攻击，P34、P38 和 P36 提供 MCP 生命周期分类及工具投毒、真实特权使用基准。材料记录的工具投毒最高攻击成功率为 72.8%，真实特权劫持总体平均为 84.8%；这些数值来自不同实验，应分别保留各自样本、环境与攻击条件。',
'从技术演进看，P40 与 P41 展示单任务语义匹配向多轮任务访问控制的扩展，P32 与 P39 连接运行时规则强制和概率预测，P03 与 P45 分别处理授权终止及请求级签发。P26 与 P30 在能力标签和可验证性方面具有方法关联，P02、P40 与 P45 则可围绕自然语言任务、scope 匹配和意图凭证展开同条件比较。这些关系有助于选择强近邻工作，并明确各自承担的系统职责。',
]
for text in observations:addp(text)
addp('以上材料说明，身份登记、凭据托管、任务授权、工具约束和撤销处理已经分别形成可复用方法。本课题接下来需要把这些能力放入同一个实际工作流，核对任务批准、凭据配置、远端状态与停止结果之间的对应关系。第五章据此比较现有产品和技术路线，进一步明确各项能力的适用边界。')

# Only the current chapter and its table numbering change; existing chapters retain their XML.
current_children=list(body)
new_start=current_children.index(hp._p);new_end=current_children.index(end._p)
assert len(before)==new_start
def signature(el):
    return (el.tag,tuple(sorted(el.attrib.items())),el.text,el.tail,tuple(signature(c) for c in el))
assert all(signature(a)==signature(b) for a,b in zip(before,current_children[:new_start]))
assert all(signature(a)==signature(b) for a,b in zip(after,current_children[new_end:]))
assert len(overview_ids)==53 and len(set(overview_ids))==53
assert len(detail_ids)==47 and len(set(detail_ids))==47
chapter_text='\n'.join(''.join(x.itertext()) for x in new)
assert '不是' not in chapter_text and '而是' not in chapter_text
# Questions within official English paper titles remain exact bibliographic data.
assert '？' not in chapter_text
assert len(doc.tables)==16
doc.save(OUT)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
report={
 'source_sha256':source_hash,'output':str(OUT),'overview_count':len(overview_ids),
 'detail_count':len(detail_ids),'overview_only':sorted(set(overview_ids)-set(detail_ids)),
 'chapter_paragraph_count':sum(x.tag==qn('w:p') for x in new),
 'outside_chapter_xml_unchanged':True,
 'original_table_count':14,'output_table_count':len(doc.tables),
}
(WORK/'edit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(WORK/'chapter4_text.txt').write_text('\n'.join(p.text for p in doc.paragraphs[new_start:]),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
