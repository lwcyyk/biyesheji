"""Apply the frozen 18:03:39 incremental audit to both report sources."""
from pathlib import Path
import json,hashlib
def apply(data,survey,tech,equations):
 W=data.WORK;SN=W/'终检增量快照'
 data.ref(45,'A q-Polymatroid Framework for Information Leakage in Secure Linear Network Coding','Eimear Byrne; Johan Vester Dinesen; Ragnar Freij-Hollanti; Camilla Hollanti',2026,'预印本 v2 2026-10-08','https://arxiv.org/abs/2601.07567','本轮原始摘要、作者与版本；r3曾读v1定理另记','子空间格/熵泄漏与普通列拟阵/TV不同；不声称全文覆盖排除','10.48550/arXiv.2601.07567')
 data.ref(46,'On Secure Network Coding With Nonuniform or Restricted Wiretap Sets','Tao Cui; Tracey Ho; Jörg Kliewer',2013,'IEEE TIT期刊论文 59(1)','https://web.njit.edu/~jkliewer/wp/paper/CKH_IT0113.pdf','本轮作者PDF首页、摘要和引言','nonuniform指窃听集/链路条件，不等于非均匀核采样','10.1109/TIT.2012.2216936')
 data.ref(47,'The Value Equivalence Principle for Model-Based Reinforcement Learning','Christopher Grimm; André Barreto; Satinder Singh; David Silver',2020,'NeurIPS论文/作者预印本','https://arxiv.org/abs/2011.03506','本轮原始摘要、作者、版本及NeurIPS标记','价值等价原理为先例；本轮未逐定理映射A4','10.48550/arXiv.2011.03506')
 e=data.evidence[17];e['claim']='AB3在v1.1阶段的提案';e['limitation']='此条仅描述旧阶段；终检v1.2实现及scope缺口见E39/E40'
 e=data.evidence[35]
 e.update(claim='r3双行非均匀核与表示敏感性',status='源码已实现；已运行有限验证；条件性数学论证；优先权未确认',
 source_path='研究/密码学辅助_一致性核验/revisions/multirow_explore_2026-11-03_r3/THEOREM.md',locator='THEOREM；REPRESENTATION_SEPARATION；check_representation_cert.check',
 result='四列三维标架尖锐界；GF7同U3,6两表示11/204与31/576；本轮两份有理数证书重核通过',
 scope='双行输入独立、无抹除、全部≤3支持、任意非零幅值；只限指定线性观察',
 limitation='非大域部署协议；采样类别公开增泄漏；一般归约手工证明；完整优先权未确认')
 data.ev(37,'A4价值单元与单例精化','源码已实现；已运行有限开发验证；条件性数学论证','research_v12/a4.py','Cells.key/add/find；FORMAL §3','同安全菜单、并集策略重放、成员下界等值；structure gate历史920断言','仅任务最优值/一个最优策略/当前资格，不保全部策略或未来任务','通用证书抽象同机制；未自动提炼最小谓词；dev01与快照源码有差异')
 data.ev(38,'B4零费用路径类压缩','源码已实现；已运行有限开发验证；条件性数学论证','research_v12/b4.py','partition/expand/check_compression/solve','48个B开发输入与参考值一致；全局字典序展开','相同task/grants/env/delegate且delegate费为0；否则单例','有界接口路线仅诊断/全局回退；通用presolve同机制；非普遍优势')
 data.ev(39,'AB3控制证书传递及完整B接口','源码已实现；已运行有限开发验证；条件性数学论证','research_v12/oracle.py','FullB.native/solve；independent.Checker.transfer','完整单世界B及全K control_solve；123/86历史门断言；dev01 22联合输入','control含configure/stop/cleanup、排除probe；联合仍可probe','见证复用需新下界闭合；共享参考内核；scope缺口E40阻止无条件证书健全性')
 data.ev(40,'AB3可行证书scope绕过反例','本轮已运行有限反例；对应安全主张需收缩','research_v12/independent.py','Checker.replay/check_certificate','simple_acquisition：control精确无解；含probe:z_native且Q=4策略被标control-only后仍VALID','冻结快照SHA736440ac…；仅公共证书合同','未证明原生越权；生成器正常路径不必触发；本轮只报告未修原算法')
 data.ev(41,'r4六弧关联结构极值','源码已实现；已运行有限验证；条件性数学论证；优先权未确认','研究/密码学辅助_一致性核验/revisions/incidence_structure_2026-11-03_r4/INCIDENCE_THEOREM.md','§1—9；check_analytic.check；check_geometry','q≥13闭式、核边缘唯一；GF16端点3/271与10/903；本轮8份有理数证书重核','3×6任意三列独立、双行、无抹除、全部≤3支持、输入独立；手工归约','不称frame唯一；GF7三类另有限证书；无恶意采样/净成本优势；几何先例查新未闭合')
 for e in data.evidence:
  p=SN/e['source_path']
  if p.is_file():e['source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 data.conflicts.extend([
 ('K17','封装期间新增research_v12与r3/r4使旧未完成结论过时','18:03:39冻结894文件增量；新增源码/原始行/10份精确证书','新旧分阶段登记；正文更新A4/B4/AB3和多行结果；不追改历史','E36—E41'),
 ('K18','control-only可行证书被认为已完整限制动作类别','本轮构造含probe策略且control无解，check_certificate仍VALID','登记scope合同反例；修复前不得无条件宣称该证书健全；不修改原算法','E40'),
 ('K19','r3先例表列q-polymatroid v1','本轮官方abs为2026-10-08 v2','v1阅读定位保留；新增v2仅摘要/题录核验；不混版本','R45'),
 ('K20','v12 dev01计时/验证可能被当作当前快照同源码结果','dev01注册哈希与快照joint/test_ab3/test_structures/worker共4项不同','688行按当时开发记录统计；不移植为当前全部源码验证；后续dev02不在冻结增量中','核验附件/增量v12源码版本差异.json')])
 data.contributions.extend([
 ('C-V12','A4/B4/AB3及完整B调用','R47、普通压缩/证书重放/增量规划','E37—E40','明确可执行机制；dev01强对照同目标值','通用版本同机制；当前scope反例须先修；版本差异需闭合'),
 ('C-CR7','双行非均匀核与同拟阵表示分离','R29/R36/R40/R45/R46','E36','更具体的独立理论候选；有精确有限最优证书','不是所有协议下界；差值很小；未获优先权/一般归约独立审定'),
 ('C-CR8','六弧关联结构尖锐界与核边缘唯一','射影几何/LP对偶/域嵌入先例','E41','一般条件公式、无限族和端点候选','q≥13；不声称frame唯一；有限检查不证一般定理，部署未实现')])
 data.next_items[5]=('N06','AB3证书scope修复及回归','保留本轮含probe伪control证书反例；逐节点核对control动作','正常正例、篡改和新观察/义务/预算失效均复核；原件另版本修复后才恢复健全性主张','优先1，新增阻塞')
 data.next_items.append(('N15','r3/r4数学与几何先例复核','核分布归约、对偶提升、q≥13正性及域嵌入','外部/机器复核与逐命题优先权；大域差值和秘密采样全成本独立评价','理论优先，非本轮新MPC'))
 data.contributions[4]=('C-AB','冲突反馈与DRD下界','R08/R09及通用联合规划','E08/E09/E17/E18/E39/E40','旧静态界可检查；v1.2已有传递实现','投影敏感、同Q；v1.2证书scope缺口，尚未产品集成')
 data.next_items[0]=('N01','规范与证据基线','原文档及K01—K20签认；保留历史版本/哈希和增量截止','37项需求与当前能力一一映射；无状态/成本偷换','优先1，文档层')
 def replace_all(bs,pairs):
  for i,b in enumerate(bs):
   if b[0] not in ('p','code','h2'):continue
   x=list(b)
   for j in range(1,len(x)):
    if isinstance(x[j],str):
     for a,c in pairs:x[j]=x[j].replace(a,c)
   bs[i]=tuple(x)
 replace_all(survey,[
 ('递归索引登记9,713项文件条目，公开可读内容中8,508项具有SHA-256，形成6,462组不同内容哈希。','递归索引最初登记9,713项；终检再纳入894项增量，共10,607项，公开可读内容9,402项具有SHA-256，形成7,354组不同内容哈希。增量已于2026年11月3日18:03:39（Asia/Shanghai）固定字节快照；之后仍在变化的开发目录不并入本轮完成结论。'),
 ('AB3目前只有规格和动态反例，未实现。','v1.1阶段AB3只有规格和动态反例；终检v1.2已出现实现及完整B接口，但发现可行证书动作scope未强制核对，见第6.1节。'),
 ('r3目前仅见探索脚本，没有可采信的一般多行最优结论链。','终检r3/r4已形成双行尖锐界、表示分离和六弧关联结构一般公式，详见第8.7节；任意r,d,n的一般最优问题仍未解决。'),
 ('新原型调用B2Select目录适配器，并未在每个联合节点运行完整B2/B3搜索；三模块改进是否能传递到端到端系统尚无证据。','v1.1原型调用B2Select目录适配器，未在每个节点执行完整B搜索；终检v1.2的FullB已改用完整条件子问题及全K控制策略，须按其新版本和证书缺口另评，不能借旧结果宣告完成。'),
 ('一般规划、CEGIS和增量约束推理','一般规划、CEGIS和增量约束推理')])
 # New sections inserted without renumbering historical main chapters.
 ix=next(i for i,b in enumerate(survey) if b[0]=='h1' and b[1].startswith('7 '))
 survey[ix:ix]=[
 ('h2','6.1 终检新增A4 B4与AB3及范围反例'),
 ('p','终检发现research_v12已实现A4任务相对价值单元、B4零费用路径类压缩与AB3证书重放。A4只在安全菜单相同、并集策略可重放且各成员下界与上界相等时共享最优策略，失败精化为单例；这不等于保持全部未来行为。B4按完全相同且零费用的delegate路径成类，以全局名称前缀展开保持原字典序，避免只挑每类最小名的反例。AB3将旧control证书在完整新Post重放，无效或未定即回退；FullB实际调用完整条件B及统一控制策略。[E37—E39；R47]'),
 ('p','冻结增量内dev01共有70输入、688方法行，与注册作业数相同：400 FEASIBLE、251 IMPOSSIBLE_IN_MODEL、37 UNKNOWN；22联合输入和48静态B输入的决定性参考值未见差异。八组合均同最优Q；B4与通用presolve同目标值，AB开启与GENERIC_REPLAY同值。开发计时不作确认性优势：dev01的4份源码哈希与增量快照不同，后续dev02不属于该冻结增量，不把旧运行移作当前代码全部通过。[K20]'),
 ('p','本轮新增反例必须影响结论：在simple_acquisition中，独立control参考返回IMPOSSIBLE_IN_MODEL，joint策略首步probe:z_native、总Q=4；把该策略封装成control_only_bounded_completion可行证书后，Checker.check_certificate仍返回VALID。原因是可行树重放未在每个动作节点检查control类别。此反例针对不可信证书合同，不证明原生越权，也不修改原算法；它否定该快照下无条件的scope健全性，应在继续性能主张前修复并回归。[E40/K18]')]
 ix=next(i for i,b in enumerate(survey) if b[0]=='h1' and b[1].startswith('9 '))
 survey[ix:ix]=[
 ('h2','8.7 终检多行结果与表示结构的进展'),
 ('p','r3把问题推进到双行无抹除掩码。对四列三维标架[e₁,e₂,e₃,(1,1,1)]、全部≤3支持、任意非零幅值、输入独立2×3矩阵且允许秩1/2混合，给出最优模拟误差(q−2)/[(q−1)(q²−3)]的手工下界及非均匀核构造。q>3严格优于均匀合法核，但相对改善仅O(q⁻²)，不能宣传大域实际加速。公开高/低密度核类别会把误差放大至(q−1)倍，说明输入独立的采样分支仍可能与输出联合泄漏。[E36]'),
 ('p','GF7两个同U₃,₆字典的最优误差分别11/204和31/576，差1/9792；本轮以不调用优化器/生成器的原独立检查器重核两份有理数原始—对偶证书通过。因此普通列拟阵、秩函数及特征多项式不能决定此双行统计隐私最优值。这与旧完美隐私分量定理不矛盾，亦不反驳使用更丰富子空间格的q-polymatroid泄漏框架。[R45；E36]'),
 ('p','r4进一步对任意q≥13素数幂的六弧字典给出由三割线共点完全匹配数t决定的尖锐公式：δ*=3(12q−57+t)/[(q−1)(12q²+(t−33)q+2t−105)]。最优核边缘分布唯一、秩1质量为0，但不主张条件frame唯一。GF16有t=0/15实际端点，其最优误差3/271和10/903；域嵌入给GF(16^m)全局表示端点及GF(7^m)严格分离。GF7归一化190候选中70合法，存在三种共点关系类；初始“两旧例覆盖全部类”失败被保留。[E41]'),
 ('p','本轮另重核r4的8份精确证书均通过，和r3合计10份；74项新增manifest哈希匹配。它们验证指定公开LP上下界，不替代一般核归约、对偶提升、唯一性或域嵌入的手工证明。群平均、射影几何和LP对偶有先例，受限窃听网络编码也有不同的线性优化目标；新具体极值的优先权仍未闭合。本轮新检索工具曾连接失败，不能把失败写成没有先例。当前多行成果较旧组件组合更有明确理论对象，但没有恶意安全采样、MPC净成本或主线部署证据。[R40/R45/R46]')]
 replace_all(tech,[
 ('独立研究目录新增A2/A3、B2/B3、AB2与Z3对照。','独立研究目录新增A2/A3、B2/B3、AB2与Z3对照；终检v1.2进一步出现A4/B4/AB3及完整条件B接口。'),
 ('新AB只用B2Select目录接口，未每节点执行完整B2/B3，不可把独立B优化假装已传导到端到端。','v1.1 AB只用B2Select；终检v1.2 FullB已改为完整条件B与全K控制策略，但新scope反例见8.2，不能借旧结果认定新实现全部健全。'),
 ('AB3拟议路线','AB3版本边界'),
 ('AB3拟议，尚未实现：','v1.1的AB3提案（v1.2实现见8.2）：'),
 ('r3只有探索脚本，未登记一般定理。','终检r3/r4已有指定双行模型的一般条件定理与精确证书，见11.5；任意维数的一般问题仍未解决。')])
 # Replace explicit table cell outdated current status.
 for i,b in enumerate(tech):
  if b[0]=='table' and b[1].startswith('表1 '):
   rows=[list(r) for r in b[3]]
   for row in rows:
    if row[0]=='RQ-A':row[2]='有限K与义务；A1—A4及反例'
    if row[0]=='RQ-B':row[2]='枚举、B2割、B3前沿、B4路径类；Z3/R-B'
    if row[0]=='RQ-AB':row[2]='AB1排序、AB2静态界、AB3传递与scope反例'
    if row[0]=='RQ-AB':row[3]='当前AB3证书scope健全性、正式收益与产品接入'
    if row[0]=='RQ-C':row[2]='条件定理、修复、AES/gate；双行/六弧精确证书'
   tech[i]=(b[0],b[1],b[2],rows)
 ix=next(i for i,b in enumerate(tech) if b[0]=='h1' and b[1].startswith('9 '))
 tech[ix:ix]=[
 ('h2','8.2 终检v1.2的A4 B4与AB3实现'),
 ('p','本节依据18:03:39冻结增量，不取最大版本号为权威。A4的Cells先按资源/会话/配置等粗摘要找候选，要求两状态及其并集具有相同W安全动作集；同一策略在并集完整重放且总Q=v，并且各成员独立下界=v，才重绑定最优策略。失败记录反例类别并单例精化，不自动生成最小谓词。该条件只保持当前任务最优值、一个策略及安全资格；价值等价和通用证书抽象是强先例。[E37/R47]'),
 ('p','B4仅合并相同task、grant集合、environment和delegate，且delegate请求/批准费为0的路径，其他保持单例。选定类后按全局名称升序加入别名，直到所有所选类首次出现即停止，才保持原配置字典序；例如{a,b}与{c}应展开[a,b,c]，不是[a,c]。搜索从2^p变为2^k但仍用原完整停止规划和检查。非零接口分解仅诊断/回退，不宣称实现新完备局部DP。[E38]'),
 ('p','AB3的FullB先实际求每可能状态的完整原生配置或已配置残余BFS，其(G,字典序)输出只作排序建议；随后control_solve对整个K求统一configure/stop/cleanup策略。旧证书先在旧根核验，再独立计算完整Post，重放策略/反证；仅可行值与新control下界相等或完整反证仍成立时复用，否则重新求解。control无解不等于含probe的joint无解。下界传递使用新计算，不能搬运旧数值剪枝。[E39]'),
 ('code','算法5 v1.2已实现传递及本轮发现的阻塞','输入旧证书、parent、动作a、观察o和child\n1 用独立Post确认child等于全部可见后继且r递减。\n2 在旧根验证模型摘要、scope、目标、引用和证书。\n3 对可行树重放新guard/全部观察/终态；对反证重覆盖全部control。\n4 VALID仅允许适用结论；见证值未与新下界闭合则回退完整B。\n5 缺新分支、旧阻断消失或界不适用返回INVALID/INCONCLUSIVE。\n审计缺口：第2—3步可行树没有逐节点强制动作属于control；\n含probe策略可被错误接受为control-only。修复前该合同健全性未成立。'),
 ('p','本轮以simple_acquisition构造scope反例：精确control无解，joint首步probe:z_native且Q=4；伪装为SCCP/1 control-only可行证书后检查器返回VALID。冻结independent.py哈希736440acc5d135ae913f69b62db656a26d4f288fc7d46035cbc15ea2753c62ba。这里只审计公共证书，不证明原生越权；原生成器正常路径可不触发。原代码保持，只将“逐节点scope校验、伪证书拒绝及正常回归”列为验收阻塞。[E40]'),
 ('p','冻结dev01含22联合输入×16方法与48个B输入×7方法，共688行；400可行、251界内不可行、37UNKNOWN，决定性参考值重计无差异。八组合保留相同联合Q目标和完整B接口。GENERIC_REPLAY/ABSTRACTION/PRESOLVE享有同机制；不以命名证明独立优势。dev01与冻结joint/test_ab3/test_structures/worker四文件哈希不同，故这些运行只支持当时开发版本，不能据此关闭当前源码所有验证。dev02不属于本轮固定增量。[K20]')]
 ix=next(i for i,b in enumerate(tech) if b[0]=='h1' and b[1].startswith('12 '))
 tech[ix:ix]=[
 ('h2','11.5 终检双行与六弧结构定理'),
 ('p','r3的四列三维标架V=[e₁,e₂,e₃,(1,1,1)]使用输入独立双行M，要求全部列无抹除、所有≤3支持的逐位置任意非零幅值，允许秩1/2混合。左GL₂平均把矩阵分布归约到秘密核状态及均匀frame；全部基的乘法轨道共同约束给出L_q=(q−2)/[(q−1)(q²−3)]下界，非均匀核分布达到。两条对边上的合法核密度较高，其余较低；q>3优于均匀合法核，但相对差O(q⁻²)。公开高/低类别后误差变为(q−1)L_q，采样内部信息不能视为免费公开。[E36]'),
 ('p','r3的GF7两个U₃,₆表示在同一成功域与泄漏合同下最优值11/204和31/576，差1/9792。独立checker重建2675变量、4580不等式和21等式的有限LP，验证原始可行、对偶符号/松弛及上下界相等。本轮两份证书重核通过；一般矩阵到核LP归约仍是手工证明。普通列拟阵不决定多行统计隐私，不与完美隐私C3或更丰富q-polymatroid框架冲突。'),
 ('p','r4限定3×6字典任意三列独立，全部≤3支持、双行输入独立、无抹除且幅值任意；q≥13为素数幂。t为15个六点完全匹配中三条割线共点的数量。合法割线并集大小U=15q−60+t，外部合法点数O=q²−14q+55−t。令D=12q−57+t、Z=12q²+(t−33)q+2t−105；高/低核密度分别(D+3)/[(q−1)Z]与D/[(q−1)Z]，秩1质量0。'),
 ('eq_extra',r'\delta^*(q,t)=\frac{3(12q-57+t)}{(q-1)[12q^2+(t-33)q+2t-105]},\quad q\ge13'),
 ('p','上界由每基三条割线和三个禁止点的概率补偿给出；下界由所有20基的显式有理数对偶分配给出。对偶约束在有理数上计算，分母2/3/12不是有限域求逆。将组对偶提升到逐点LP并用互补松弛，可得最优核边缘唯一；不声称条件frame或整个M分布唯一。q≥13外不套一般证明，GF7另用有限分类/证书。[E41]'),
 ('p','GF7对190归一化候选枚举得70合法，三种共点关系类(30,10,30例)，t为4/6/6，最优31/576或11/204；初始“两旧例覆盖全部类”断言失败原样保留。GF16有t=0与15真实字典，最优分别3/271和10/903、差1/244713；正确域嵌入得到GF(16^m)全局表示端点及GF(7^m)严格分离。整数编码不能原样冒充任意扩域嵌入。'),
 ('p','本轮重核r4八份有理数证书通过，检查器只支持q=16/49/343及登记共点结构，表示前提由几何证据/域嵌入另供。有限证书不证明一般归约、唯一性或优先权。秘密非均匀采样、固定预算必达、恶意MPC及完整成本均未实现；概率分布存在不等于主线H步内可部署。此次进展应保留为更强的受限理论候选，不能混为A/B/AB收益。')]
 # Update current claims and future gates without deleting old counterexamples.
 for bs in [survey,tech]:
  replace_all(bs,[('新增K01—K16','新增K01—K20'),('N01—N14配套台账','N01—N15配套台账')])
 for i,b in enumerate(survey):
  if b[0]=='table' and b[1].startswith('表6 '):
   rows=[list(r) for r in b[3]]
   rows[0][1]='认证副作用规约；A2完整成本；A4价值单元'
   rows[1][1]='原生效果域、分离割；B4零费路径类'
   rows[2][1]='排序、静态界；v1.2证书传递'
   rows[2][3]='机制存在；scope反例阻塞，净增量未立'
   rows.append(['双行/六弧','非均匀核、表示分离与尖锐极值','群平均、射影几何、LP对偶及R45','更具体理论候选；一般证明独立审定及优先权未闭合'])
   survey[i]=(b[0],b[1],b[2],rows)
 ix=next(i for i,b in enumerate(survey) if b[0]=='h2' and b[1].startswith('11.3'))+1
 survey.insert(ix,('p','终检后首要工程门是修复AB3逐节点动作scope，并使开发结果与待验源码哈希闭合；首要理论门是独立审定r3/r4的一般核归约、几何条件与对偶提升，再完成精确先例映射。十份有限证书通过不能替代这两类进入条件。[E36—E41；N06/N15]'))
 ix=next(i for i,b in enumerate(tech) if b[0]=='h1' and b[1].startswith('16 '))+1
 tech.insert(ix,('p','终检新增验收门：先在另立修订中修复AB3可行树的逐节点control范围核对，拒绝本轮含probe反例并保留正常证书回归；再按同一源码快照重建开发结果。r3/r4另须核分布归约、对偶提升、域嵌入及优先权审定。原始算法与历史数据本轮保持不变。[E40；N06/N15]'))
 # Index/cutoff note is prominent and self-contained.
 survey.insert(3,('p','终检更新：本报告纳入18:03:39固定的research_v12及密码学r3/r4增量。A4/B4/AB3已出现源码与开发记录，双行/六弧理论已有新条件结果；同时本轮发现AB3可行证书scope反例。旧阶段“未实现”仅按其时点保留，当前判断以新增第6.1、第8.7节及E36—E41为准。'))
 tech.insert(3,('p','资料版本边界：工作期间项目持续更新，本报告以2026年11月3日18:03:39（Asia/Shanghai）的894项增量字节快照补足初始审计。新增A4/B4/AB3及r3/r4见8.2、11.5；AB3 scope反例列为阻塞。快照后开发结果不借用为本轮已核验结论。'))

