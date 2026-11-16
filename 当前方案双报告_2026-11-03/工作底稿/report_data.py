from pathlib import Path
import csv,json,hashlib
ROOT=Path(r'D:\毕业设计');OUT=ROOT/'当前方案双报告_2026-11-03';WORK=OUT/'工作底稿'
refs=[]
def ref(n,title,authors,year,kind,url,scope,limit='',doi=''):
 refs.append(dict(id=f'R{n:02}',title=title,authors=authors,year=str(year),type=kind,url=url,doi=doi,read_scope=scope,limitation=limit,verified_on='2026-11-03'))
ref(1,'Planning and acting in partially observable stochastic domains','Leslie Pack Kaelbling; Michael L. Littman; Anthony R. Cassandra',1998,'期刊论文','https://doi.org/10.1016/S0004-3702(98)00023-X','继承v2.15元数据与摘要；本轮未新增全文阅读','仅作经典框架归属，不作完整能力排除','10.1016/S0004-3702(98)00023-X')
ref(2,'Safe Reinforcement Learning via Shielding under Partial Observability','Steven Carr; Nils Jansen; Sebastian Junges; Ufuk Topcu',2023,'AAAI论文；预印本另版','https://arxiv.org/pdf/2204.00755','原文Definition 2、Theorem 2/3、§4.1脚注2；AAAI元数据','arXiv作者排序与出版版不同；书目采用出版版顺序','10.1609/aaai.v37i12.26723')
ref(3,'Enforcing Almost-Sure Reachability in POMDPs','Sebastian Junges; Nils Jansen; Sanjit A. Seshia',2021,'CAV论文','https://link.springer.com/chapter/10.1007/978-3-030-81688-9_28','出版社摘要及方法入口','未复现Storm/RLShield工件','10.1007/978-3-030-81688-9_28')
ref(4,'Automata Learning meets Shielding','Martin Tappler; Stefan Pranger; Bettina Könighofer; Edi Muškardin; Roderick Bloem; Kim Guldstrand Larsen',2022,'ISoLA论文','https://arxiv.org/abs/2212.01838','作者、题名、摘要；沿用既有章节定位','本轮未通读证明','10.1007/978-3-031-19849-6_20')
ref(5,'Inference of finite automata using homing sequences','Ronald L. Rivest; Robert E. Schapire',1989,'STOC论文','https://people.csail.mit.edu/rivest/pubs/RS89.pdf','作者原文入口及出版元数据','不把后续1993期刊版混作1989版','10.1145/73007.73047')
ref(6,'Black Box Checking','Doron Peled; Moshe Y. Vardi; Mihalis Yannakakis',1999,'会议论文','https://www.cs.rice.edu/~vardi/papers/pstv99.pdf','作者全文摘要、引言与reset和状态上界设定','未复现工具')
ref(7,'Generalized Binary Search For Split-Neighborly Problems','Stephen Mussmann; Percy Liang',2018,'AISTATS论文','https://proceedings.mlr.press/v84/mussmann18a.html','PMLR摘要和元数据','本项目B-A不是该算法完整复现')
ref(8,'Near-Optimal Bayesian Active Learning with Noisy Observations','Daniel Golovin; Andreas Krause; Debajyoti Ray',2010,'NeurIPS论文','https://proceedings.neurips.cc/paper/2010/hash/1e6e0a04d20f50967c64dac2d639a577-Abstract.html','会议摘要和题录；原项目§2—3定位仅继承','不移植贝叶斯/自适应次模近似保证')
ref(9,'Near Optimal Bayesian Active Learning for Decision Making','Shervin Javdani; Yuxin Chen; Amin Karbasi; Andreas Krause; J. Andrew Bagnell; Siddhartha Srinivasa',2014,'AISTATS论文','https://proceedings.mlr.press/v33/javdani14.html','原文引言、§3及Theorem 1的重叠区域/超边条件','期望成本与本项目最坏成本不同')
ref(10,'Tactics for Account Access Graphs','Luca Arnaboldi; David Aspinall; Christina Kolb; Saša Radomirović',2024,'ESORICS 2023会议论文 2024出版','https://www.pure.ed.ac.uk/ws/portalfiles/portal/478371898/ArnaboldiEtalESORICS2023TacticsForAccountAccessGraphs.pdf','机构作者稿摘要、§3、Definition 5','未运行其工件','10.1007/978-3-031-51479-1_23')
ref(11,'Verifying Account Ecosystems With Graph Transformations','Freya Murphy; Saša Radomirović',2026,'EuroS&P论文','https://researchportal.hw.ac.uk/en/publications/verifying-account-ecosystems-with-graph-transformations/','机构摘要、出版状态、页470—490和DOI','AAM全文下载403，精确覆盖未决','10.1109/EuroSP68448.2026.00038')
ref(12,'Position: AI Agents Need Authenticated Delegation','Tobin South; Samuele Marro; Thomas Hardjono; Robert Mahari; Cedric Deslandes Whitney; Alan Chan; Alex Pentland',2025,'ICML立场论文','https://proceedings.mlr.press/v267/south25a.html','PMLR原始摘要和题录','方向性论证，不作系统已实现证明')
ref(13,'SUDP: Secret-Use Delegation Protocol for Agentic Systems','Xiaohang Yu; Hejia Geng; Xinmeng Zeng; William Knottenbelt',2026,'预印本 v4 2026-10-21','https://arxiv.org/abs/2604.24920','arXiv摘要、版本及官方仓库入口','本轮未复现协议与性能；旧正文定位沿用','10.48550/arXiv.2604.24920')
ref(14,'AID-Guard: Stateful Authorization for Delegated Agent Effects','Yingzhe Tong; Leyu Dai; Songhui Guo',2026,'预印本 v1','https://arxiv.org/abs/2608.21159','原始摘要、威胁/提供方契约描述和版本','作者实验不作为本项目结果','10.48550/arXiv.2608.21159')
ref(15,'Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution','Genliang Zhu; Chu Wang',2026,'预印本 v1','https://arxiv.org/abs/2609.21284','原始摘要、支持反链、栅栏、精确重绑与作用域','完整证明未独立审定','10.48550/arXiv.2609.21284')
ref(16,'OAuth 2.0 Token Revocation','Torsten Lodderstedt; Sven Dronia; Marius Scurtescu',2013,'RFC 7009 标准轨','https://www.rfc-editor.org/rfc/rfc7009.html','§2.1—2.2撤销关联和200响应','','10.17487/RFC7009')
ref(17,'OAuth 2.0 Token Introspection','Justin Richer',2015,'RFC 7662 标准轨','https://www.rfc-editor.org/rfc/rfc7662.html','§2.2查询者受限active:false语义','','10.17487/RFC7662')
ref(18,'OAuth 2.0 Token Exchange','Michael Jones; Anthony Nadalin; Brian Campbell; John Bradley; Chuck Mortimore',2020,'RFC 8693 标准轨','https://www.rfc-editor.org/rfc/rfc8693.html','§2.1输入输出不自动形成紧密生命周期联系','','10.17487/RFC8693')
ref(19,'Best Current Practice for OAuth 2.0 Security','Torsten Lodderstedt; John Bradley; Andrey Labunets; Daniel Fett',2025,'RFC 9700 BCP 240','https://www.rfc-editor.org/rfc/rfc9700.html','状态、摘要和安全基线范围','不宣称原型全面合规','10.17487/RFC9700')
ref(20,'MP-SPDZ: A Versatile Framework for Multi-Party Computation','Marcel Keller',2020,'CCS论文及持续更新项目文档','https://mp-spdz.readthedocs.io/en/latest/readme.html','官方README的协议分类、引用与使用前提','本项目底座固定v0.4.4；网页不等同该版本审计','10.1145/3372297.3417872')
ref(21,'MASCOT: Faster Malicious Arithmetic Secure Computation with Oblivious Transfer','Marcel Keller; Emmanuela Orsini; Peter Scholl',2016,'CCS论文/ePrint','https://eprint.iacr.org/2016/505','原始摘要、作者、算术与主动安全目标','未独立核验全部安全证明')
ref(22,'Advanced Encryption Standard (AES)','NIST',2023,'FIPS 197 更新版','https://csrc.nist.gov/pubs/fips/197/final','官方标准入口和元数据；项目AES关系对照','不宣称通过NIST实现认证','10.6028/NIST.FIPS.197-upd1')
ref(23,'Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC','Morris Dworkin; NIST',2007,'NIST SP 800-38D','https://csrc.nist.gov/pubs/sp/800/38/d/final','官方标准入口和GCM关系定位','修订规划不等于新标准已发布','10.6028/NIST.SP.800-38D')
ref(24,'DECO: Liberating Web Data Using Decentralized Oracles for TLS','Fan Zhang; Deepak Maram; Harjasleen Malvai; Steven Goldfeder; Ari Juels',2020,'CCS论文 扩展作者稿','https://research.chain.link/deco.pdf','作者稿首页、摘要、来源证明目标','本轮未逐算法复现','10.1145/3372297.3417239')
ref(25,'Oblivious TLS via Multi-Party Computation','Damiano Abram; Ivan Damgård; Peter Scholl; Sven Trieflinger',2021,'CT-RSA论文','https://eprint.iacr.org/2021/318','ePrint摘要与出版信息、主动腐化/预处理模型','未读取全部协议证明','10.1007/978-3-030-75539-3_3')
ref(26,'Arithmetic Sketching','Dan Boneh; Elette Boyle; Henry Corrigan-Gibbs; Niv Gilboa; Yuval Ishai',2023,'CRYPTO论文','https://ntt-research.com/wp-content/uploads/2023/08/Arithmetic-Sketching.pdf','52页原文：摘要、Construction 21、Theorem 22、Corollary 23、随机化归属','选读，不宣称全论文逐式核验','10.1007/978-3-031-38557-5_6')
ref(27,'Randomizing Polynomials: A New Representation with Applications to Round-Efficient Secure Computation','Yuval Ishai; Eyal Kushilevitz',2000,'FOCS论文 扩展摘要','https://doi.org/10.1109/SFCS.2000.892118','本地11页PDF：§2.1、§2.2、Lemma 3.2—3.4、Theorem 3.5；结构预检PASS','双边随机化不直接给出全部独立族的单边最小熵分类','10.1109/SFCS.2000.892118')
ref(28,'Constant-Round Secure Distributed Decoding and HQC Threshold Decryption','Pascal Giorgi; Fabien Laguillaumie; Lucas Ottow; Damien Vergnaud',2026,'IACR Communications in Cryptology 3(3)期刊版；ePrint另版','https://doi.org/10.62056/ay4fvu7sf','本地3-3-4.pdf 43页：§2.2、§6.1—6.2、Algorithm 13、Protocol 14、Theorem 7；结构预检PASS','ePrint页仍标Preprint；不混淆版本。其安全/成本依ABB模型','10.62056/ay4fvu7sf')
ref(29,'Matroid Theory','James Oxley',2011,'专著 第二版','https://www.math.ens.psl.eu/~benoist/refs/Oxley.pdf','本地已有原文与r1定位：§4.1—4.3；本轮核查分量/直和对应','本轮未通读722页专著；经典数学归属，不作新颖性证明')
ref(30,'Geometry of 1-tori in GL(n,T)','Nikolai Vavilov',2008,'期刊论文 俄文2007英文2008','https://www.mathnet.ru/eng/aa122','本轮原始元数据/摘要；r1俄文§1/5—7选读记录','英文全文及完整分类归约仍未完成','10.1090/S1061-0022-08-01004-2')
ref(31,'Linear Groups Generated by Reflection Tori','A. M. Cohen; H. Cuypers; H. Sterk',1999,'期刊论文','https://www.cambridge.org/core/journals/canadian-journal-of-mathematics/article/linear-groups-generated-by-reflection-tori/E482441E1C778AB599846D116B87D92A','出版摘要与原文入口；r1§1定理1.1/1.2记录','网页上线2018不是出版年；未完成q=3/4/5例外逐项归约','10.4153/CJM-1999-051-7')
ref(32,'Communication Theory of Secrecy Systems','Claude E. Shannon',1949,'期刊论文','https://doi.org/10.1002/j.1538-7305.1949.tb00928.x','沿用r1原文§10/Theorem 6核验记录','本轮未重读；此处仅为完美保密和随机性背景','10.1002/j.1538-7305.1949.tb00928.x')
ref(33,'Numerical Sparsity Determination and Early Termination','Zhiwei Hao; Erich L. Kaltofen; Lihong Zhi',2016,'ISSAC论文','https://users.cs.duke.edu/~elk27/bibliography/16/HKZ16.pdf','本地原文存在；沿用项目§4/§6定位并核对特征二边界','本轮在线PDF403；不作原创新发现','10.1145/2930889.2930924')
ref(34,'Communication Efficient Secure Linear Algebra','Kobbi Nissim; Enav Weinreb',2006,'TCC论文','https://link.springer.com/chapter/10.1007/11681878_27','出版社原始摘要与元数据：522—541页','全文仍未取得；历史526—541页已纠正','10.1007/11681878_27')
ref(35,'Common Complements of Linear Subspaces and the Sparseness of MRD Codes','Anina Gruica; Alberto Ravagnani',2022,'论文预印本v2；期刊版另有DOI','https://arxiv.org/abs/2011.02993','作者摘要、版本记录','CS03完整归约未完成；未通读','10.48550/arXiv.2011.02993')
ref(36,'Low-Rank Masking for Single-Server Matrix Multiplication','Alejandro Cohen; Rafael G. L. D’Oliveira; Alex Sprintson',2026,'预印本v1','https://arxiv.org/abs/2609.18876','原始摘要、模型、版本；旧r2正文定位另记','加性低秩/最大相关性或DP不同于本项目乘法幅值TV','10.48550/arXiv.2609.18876')
ref(37,'Multi-Cost-Bounded Reachability Analysis of POMDPs','Alexander Bork; Joost-Pieter Katoen; Tim Quatmann; Svenja Stein',2025,'UAI论文','https://proceedings.mlr.press/v286/bork25a.html','PMLR摘要和工件入口','未运行Storm工件；概率目标不等于所有轨迹保证')
ref(38,'Security Analysis of Master-Password-Protected Password Management Protocols','Yihe Duan; Ding Wang; Yanduo Fu',2025,'IEEE S&P论文','https://wangdingg.weebly.com/uploads/2/0/3/6/20366987/ieeesp25-pm-full.pdf','作者原文入口、会议接收列表和作者出版页','原版本/威胁模型有效；不评价当前产品修复状态')
ref(39,'An Introduction to Hyperplane Arrangements','Richard P. Stanley',2004,'作者讲义','https://static.ias.edu/pcmi/2004/program/Stanleynotes.pdf','Lecture 5有限域方法定位；r2 Theorem 5.15阅读记录','特征0约化需交格保持；项目应以实际域秩计数')
ref(40,'Global optimality under amenable symmetry constraints','Peter Orbanz',2024,'预印本v2','https://arxiv.org/html/2402.07613v2','原文摘要与§1群平均/凸性框架','有限群平均属于标准优化步骤，非项目原创','10.48550/arXiv.2402.07613')
ref(41,'Lightweight Authentication of Web Data via Garble-Then-Prove','Xiang Xie; Kang Yang; Xiao Wang; Yu Yu',2024,'USENIX Security论文','https://www.usenix.org/conference/usenixsecurity24/presentation/xie-xiang','会议原始摘要、机构与作者','未复现通信/运行成本')
ref(42,'Encryption, Decryption, and MAC Computation','TLSNotary contributors','持续更新','项目文档','https://tlsnotary.org/docs/protocol/mpc-tls/encryption/','当前页面MPC加解密和明文接收者','未锁源码提交；不能当作两执行域均不见明文的实现')
ref(43,'Solving logic-based benders decomposition master problems with constraint programming and domain-independent dynamic programming','Jiachen Zhang; J. Christopher Beck',2025,'期刊论文','https://link.springer.com/article/10.1007/s10601-025-09382-1','出版社摘要、作者、卷期及工件入口','未通读、未运行DIDP/CP比较','10.1007/s10601-025-09382-1')
ref(44,'A research agenda for active automata learning','Sophie Fortz; Fatemeh Ghassemi; Léo Henry; Falk Howar; Thomas Neele; Jurriaan Rot; Marnix Suilen',2026,'期刊论文','https://link.springer.com/article/10.1007/s10009-026-00839-z','本轮出版信息与原文入口；既有材料Concurrency/Unobservability/Resets定位','本轮未通读全部议程；开放挑战不是本项目已解决证据','10.1007/s10009-026-00839-z')

evidence=[]
def ev(i,claim,status,path,locator,result,scope,limit):
 p=ROOT/path
 evidence.append(dict(id=f'E{i:02}',claim=claim,status=status,source_path=path,locator=locator,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else '',result=result,scope=scope,limitation=limit))
ev(1,'有界语义与W_r安全菜单','源码已实现；已运行有限验证；条件性数学论证','auth-lifecycle/src/auth_lifecycle/a/candidate.py','Shield.winning/menu；solve','本轮96项离线单元测试通过；历史5184查询','有限表、非空K、H≤8','实现一般证明与原生保持未完成')
ev(2,'A契约证据与保守更新','源码已实现；已运行有限验证','auth-lifecycle/src/auth_lifecycle/a/evidence.py','update/contract/usable','模型外观察围栏；仅全部存活假设共同性质','已登记有限假设；账户/调用者/epoch/预算','不是开放网站学习或服务签名证明')
ev(3,'A1与B-A等成本排序等效','条件性数学论证；已运行有限验证；贡献已收缩','研究/主线研究论证深化_2026-11-03/认证语义与凭据配置_主线研究论证深化_v1.0.docx','§3；a/candidate.py choose','11968次历史有理数比较；19场景策略一致','相同菜单/投影/决胜规则和有效分母；每可达状态满足才能推出策略等同','浮点实现极端值未机器证明；不含AB权重分支')
ev(4,'A排序不同不保证完整成本改善','已运行有限验证；被反例否定或贡献已收缩','研究/主线研究论证深化_2026-11-03/认证语义与凭据配置_主线研究论证深化_v1.0.docx','§4；runs/final02','不同排序Q=6/6；更差反例8/6','5世界手工诊断，计清理成本','不是正式总体H-A判定')
ev(5,'B最小原生单元配置搜索','源码已实现；已运行有限验证；条件性数学论证','auth-lifecycle/src/auth_lifecycle/b/search.py','solve/visit','384参数积与96结构输入历史参考一致','确定、可靠setup；替代停止情形；min(G,路径字典序)','不是SMT/CEGIS；没有一般连续恢复')
ev(6,'B-B强组合及等效子域','源码已实现；已运行有限验证；贡献已收缩','auth-lifecycle/src/auth_lifecycle/b/baselines.py','structural_rules/solve','共享broker和静态子域等效；034/084规则遗漏','四规则预固定；同计划器/检查器','规则内无解不等于全局无解')
ev(7,'规则遗漏的完整枚举回退','源码已实现；已运行有限验证；贡献已收缩','研究/主线研究论证深化_2026-11-03/认证语义与凭据配置_主线研究论证深化_v1.0.docx','§5；B-B_enum_supplement','034/084均G=2，与B/R-B同配置','独立研究目录补充对照','与R-B共享BFS/内核，未写回历史B-B')
ev(8,'AB1具体冲突排序','源码已实现；已运行有限验证','auth-lifecycle/src/auth_lifecycle/a/bridge.py','Feedback.get/_configured','反馈改变选择，投影诊断Q5→4；R-J同4','配置前逐世界条件诊断；配置后立即停止守卫','投影敏感；两世界对不是完整多世界证书')
ev(9,'R-J同策略空间精确参考','源码已实现；已运行有限验证','auth-lifecycle/src/auth_lifecycle/a/joint_reference.py','solve','L0 Q5/4且G相同；原生已知契约Q5/3','完整有限图；最坏总Q','不一般同时最小G；与R-I/检查器共享_reference_kernel')
ev(10,'参考与检查器独立性','源码已实现；已运行有限验证；贡献已收缩','auth-lifecycle/src/auth_lifecycle/b/checker.py','check_delivery/check_conflict；b/reference.py','不调用候选生成器；本轮依赖隔离测试通过','B参考与检查器共用b/_kernel；主线共用schema','不是三套完全独立实现')
ev(11,'有限抽象保持及回译','源码已实现；已运行有限验证；条件性数学论证','auth-lifecycle/src/auth_lifecycle/abstraction.py','check_relation/lift_policy','七组有限关系条件、正例及篡改负例','有限表→有限表','真实原生C→M尚未证明')
ev(12,'A2完整后续成本搜索','源码已实现；已运行有限验证；条件性数学论证','研究/算法机制重构与原创性验证_2026-11-03/prototype/a_ab_search.py','solve','20输入与通用同下界BB同Q；W0一个6→5相对启发式','A模式保持早承诺；AB模式不同策略类','不能宣称新AND/OR原理或独立优势')
ev(13,'A3严格后续商键','源码已实现；已运行有限验证；贡献已收缩','研究/算法机制重构与原创性验证_2026-11-03/prototype/a_ab_search.py','continuation_signature/lift','3诊断quotient_hits=0','只商化缓存键，回译再检查','未实现完整商图；无压缩收益')
ev(14,'B2原生单元分层和必要割','源码已实现；已运行有限验证；条件性数学论证','研究/算法机制重构与原创性验证_2026-11-03/prototype/b_units.py','relaxed_reject/solve/check_lower_bound','20例与参考同结果；15可行LB=UB；本批整体更慢','忽略部分约束的乐观必要条件','下界证书不总是完整不可行证明')
ev(15,'B3组件前沿组合','源码已实现；已运行有限验证；条件性数学论证','研究/算法机制重构与原创性验证_2026-11-03/prototype/b_components.py','solve','20例一致；3例分解、17例回退','无未记录共享原生/有价环境耦合；不可逆停止','无通用FPT定理；未完整接入AB')
ev(16,'Z3直接优化对照','源码已实现；已运行有限验证','研究/算法机制重构与原创性验证_2026-11-03/smt_comparator.py','solve','Z3 4.15.4.0；20例同状态/G/配置','确定单调B模型，SAT交付另检','非主线B已换SMT；UNSAT未导出证明')
ev(17,'AB2静态DRD下界','源码已实现；已运行有限验证；条件性数学论证','研究/算法机制重构与原创性验证_2026-11-03/prototype/a_ab_search.py','drd_bound/solve','20例开关同Q；50个下界检查；343关系矩阵','静态确定前置查询、无故障/义务/世界变化','状态改变回退；额外开销；同原理DRD可复现')
ev(18,'AB3动态核心传递','文档提出；仅为未来计划；一般证明尚未完成','研究/算法机制重构与原创性验证_2026-11-03/A、B与AB三项算法原创性突破及优势验证研究报告_v1.0.docx','§7','只有动态反例与拟议伪代码','待证前像/后像约束有效性','没有可运行AB3或优势数据')
ev(19,'原生校准与正式统计','已运行有限验证；原生实现已验证（限定校准）；正式假设未运行','auth-lifecycle/results/experiments/pilot02/runs.jsonl','metadata/metrics；源码快照','本轮重计576行288对；120完成336拒绝120UNKNOWN；156未决','Keycloak26.8.1/Casdoor4.25.0已知契约负控制','A查询/AB反馈均0；独立性确认家族0')
ev(20,'阈值与确认入口','文档提出；仅为未来计划','auth-lifecycle/docs/experiments/FREEZE_CHECKLIST.md','主要阈值/正式进入清单','0.80/0.80/0.85和−0.05未确认；入口关闭','研究者确认加技术映射/功效门','开发结果不得填正式通过')
ev(21,'四阶段完整产品','文档提出；尚未集成；原生实现未验证（该产品）','实现四阶段/阶段四_核心数据模型、接口契约与A+B算法详细设计说明书_v1.0.docx','14对象；M01—M12/C01—C08；附录A','43表DDL/148计划测试为设计；缺独立源附件','SC1—SC3、PJ/NT业务规格','当前JSONL实验账本不等于M10权威运行库')
ev(22,'旧v2.13与CS03运行','文档提出；资料缺失、无法核实','CS03_密码学贡献重构与历史隐私刷新_2026-10-23.docx','§7及D01—D03；v2.13 E213','旧报告32768/324/48/96及14案例3退出仅历史记载','已索引历史ZIP及限定嵌套ZIP未找到所引源码','不算本轮复现、当前集成或完整协议证据')
ev(23,'一般掩码与行空间诊断','源码已实现；已运行有限验证；条件性数学论证','研究/密码学辅助_一致性核验/ROWSPACE_2026-11-03.md','construction/rowspace.py；mpc/rowspace2.mpc','k=2历史真实MPC；一般k有限检查','稀疏gate、合法GL采样、幅值隐藏','不是整个协议零错误；无稳定整体加速')
ev(24,'掩码秩与随机性界','条件性数学论证；已运行有限验证；一般证明尚未独立核验','研究/密码学辅助_一致性核验/RANK_PRIVACY_TRADEOFF_2026-11-03.md','§1—7','r≥k、GL不变性、遗漏概率、k−r固定检查','q>2、2≤k<n、满火花、全部≤k支持、输入独立、可逆等价观察','非所有密码协议下界；不包括输入相关/非线性输出')
ev(25,'两故障单遗漏修复','源码已实现；已运行有限验证；条件性数学论证','研究/密码学辅助_一致性核验/mpc/seed_repair2.mpc','非零种子；z0/z1分支','历史359805对、41400修复；正常随机9批；固定种子分支另列','成功采样且真实支持≤2；新鲜σ；单遗漏承诺','未接AES前端；稠密gate/底座仍有误差和中止')
ev(26,'AES-GCM残差来源关系','源码已实现；已运行有限验证；原生MPC已验证（记录关系）','研究/密码学辅助_一致性核验/source_binding/build_experiment.py','base_path=mpc/rowspace2.mpc；generated01/bind_gcm.mpc','2条16字节记录、8场景、三方法；新方法16297 triples','AES-128-GCM、96位nonce、给定共享密钥/上下文','rowspace接入；非seed-repair；非完整TLS/身份/时效真实性')
ev(27,'结构C1冲突界','条件性数学论证；已运行有限验证；贡献已收缩','研究/密码学辅助_一致性核验/revisions/structural_audit_2026-11-03_r1/PROOFS.md','§2','ε_S+η_j≥1；模拟2δ+η_j≥1','j必须在非零系数依赖关系中；q>2；任意非零幅值；线性可见','不能让余单元素也强制抹除；属于TV事件推论')
ev(28,'结构C2一般族存在性','条件性数学论证；已运行有限验证','研究/密码学辅助_一致性核验/revisions/structural_audit_2026-11-03_r1/PROOFS.md','§3','存在完美隐藏且不抹除掩码 iff 每个允许支持独立','行数自由；仅活跃列；空族/空支持另处理','不是给定r资源判据；非新GL原理')
ev(29,'结构C3分布与资源分类','条件性数学论证；已运行有限验证；一般证明尚未独立核验；贡献已收缩','研究/密码学辅助_一致性核验/revisions/structural_audit_2026-11-03_r1/PROOFS.md','§4—6','有效矩阵Z=MB的块GL直积不变；rmin=max d_j；熵界','允许族恰为全部独立集；q>2；无抹除才有资源界','完整优先权未决；匹配构造与独立分块等效')
ev(30,'公开结构编译与证书','源码已实现；已运行有限验证；尚未集成','研究/密码学辅助_一致性核验/revisions/structural_audit_2026-11-03_r1/checker.py','profile_check/check；compiler.components/find_conflict','本轮正确证书接受、行数篡改拒绝、依赖支持冲突接受','GF3/GF4；m≤4,n≤8；完整族与可信expected profile','不验证来源；runtime_support_verified=false；无执行权')
ev(31,'秘密支持结构gate','源码已实现；已运行有限验证；尚未集成','研究/密码学辅助_一致性核验/revisions/structural_audit_2026-11-03_r1/gate_mpc/support_gate.mpc','nonzero_bit/gate_case；gate_release.mpc','历史32场景，本轮离线32场景重核；67/49成功域反例','GF(2^128)合成固定残差；S40；诚实本地执行','不是结构优化掩码全流程，不是来源保证/恶意审计')
ev(32,'通用gate后直接公开支持','源码已实现；已运行有限验证；贡献已收缩','研究/密码学辅助_一致性核验/revisions/structural_audit_2026-11-03_r1/RUNTIME_GATE_AND_INTERFACE.md','§4；gate_release.mpc','相同profile新增秘密乘法0；开值仍增通信与轮次','支持允许向两计算方披露','否定当前组合成本优势，不否定全部未来gate')
ev(33,'主线密码学连接','文档提出；尚未集成；仅为未来计划','研究/主线与密码学机制融合_2026-11-03/PublicDiagnosticEvidence_接口增补.json','请求/响应及authorizes_execution=false','主线src/scripts未检出辅助MPC/AES/修复模块调用链','拟接M07/M08，经M10预算/批准','代数定位不等于AB语义补证；不能授予R/E能力')
ev(34,'主动安全与实现审计','已运行有限验证；恶意实现安全未验证','研究/密码学辅助_一致性核验/mpc/run_backend.py','MASCOT runner；各manifest phases','固定v0.4.4、live预处理、GF(2^128)、S40','两同机参与方；数据域≠统计安全强度','侧信道、恶意偏离、WAN、并发/恢复未完整审计')
ev(35,'单行最优统计隐私新profile','条件性数学论证；已运行有限验证；贡献未确立','研究/密码学辅助_一致性核验/revisions/novelty_search_2026-11-03_r2/EXACT_SIMULATION_FRONTIER.md','§1—8','δ*=1−χ(q)/(q−1)^d；最优分布与三列ε–η特例','单行、全独立集、无抹除、合法掩码集合非空','改变隐私契约；未实现认证采样器，r>1未完成')
ev(36,'多行继续探索','源码存在；资料不足、无法确认结论','研究/密码学辅助_一致性核验/revisions/multirow_explore_2026-11-03_r3/kernel_minimax.py','另有full_matrix_check/mixture_reference/arc_scan','目录仅见4个探索脚本，未见同版正式报告/manifest结果链','截止本轮索引快照','不得从文件名推断一般最优定理完成')

conflicts=[
('K01','申报讲解稿称传统方法均依赖reset、无代理退场机制、已有三方完全代码隔离','v2.15审查、主线源码及R02/R05/R14/R15','采用受限问题定位；参考/检查器共享内核，宽泛首次性删除','D006 P0039/0052/0112/0145；D007 P0037/0098'),
('K02','四阶段写A/B待实现，当前主线已有有限实现','auth-lifecycle/src与历史结果','前者指设计阶段及完整产品；按能力层次登记，不用时间新版一票覆盖','D01沿用'),
('K03','DD采用新增批准/授权/隔离/请求词典序','b/search.py与OBJECTIVE_LOCK','历史B保持min G及路径字典序；DD成本仅拟议新profile','D02沿用'),
('K04','固定日程/完整识别被称无反馈基线','a/candidate.py feedback唯一开关','主要B-AB保留相同性质投影、W和缓存；日程仅次要消融','D03沿用'),
('K05','H耗尽与资源截断混写未定；空K可被全称真误释','schema/semantics/checker','完整界内无策略=IMPOSSIBLE；搜索耗尽=INCONCLUSIVE；空K=UNKNOWN','D04/D05沿用'),
('K06','替代停止、原子configure被写成连续/非原子生命周期','b/model与a/plant','只承诺同一初态的替代场景；微步骤、CP恢复为拟议','D07/D10沿用'),
('K07','主线B未用SMT，与新增Z3对照似矛盾','主线search与独立smt_comparator','主线B仍枚举；独立目录有Z3直接编码对照，非已接通CEGIS','D08补充'),
('K08','顶层CURRENT_STATUS称结构gate尚未实现','r1 gate_mpc源码及四批日志','参考gate已实现运行；结构掩码完整流程、来源绑定及主线接入未完成','新增2026-11-03审计解释'),
('K09','AES前端与最新seed-repair被合并描述','build_experiment.py base_path','实际接rowspace2；seed-repair没有该前端新运行','新增'),
('K10','r1/r2称两篇关键全文未取得','研究根下两个PDF、哈希和结构预检','Ishai–Kushilevitz与共享解码全文附件已取得并选读；精确优先权仍未全部解决','新增；不改原失败记录'),
('K11','ePrint2026/946仍标Preprint，本地3-3-4为期刊版','本地首页及ePrint元数据','分别登记期刊43页版本与ePrint；不混用同一版本声明','新增'),
('K12','Nissim–Weinreb历史页码526—541','出版社原始元数据','更正为522—541；正文仍未取得','R34'),
('K13','pilot02源码哈希与当前两脚本不同','快照两文件匹配历史；本轮diff','历史运行采用归档；当前差异为下载幂等锁和environment-lock参数，不追改历史','l1_fetch/l1_pilot'),
('K14','每记录至多一错被当作来源保证','AES历史tag/claim同错及GF4完整计数','原成功域67，限制域49；18个原合法输入被排除，不能跨域比较收益','r1及本轮公开计数'),
('K15','运行于MASCOT被写成完成恶意安全审计','runner/日志与MPC模型','只确认所选底座和诚实本地执行；一般组合/恶意实现审计未完成','E34'),
('K16','0.80/0.80/0.85/−0.05及W0被当冻结验收','FREEZE_CHECKLIST与四阶段原文','仍为建议阈值；W0仅局部worker检查，完整部署/1000准入未验','E20/E21')]

contributions=[
('C-A1','安全契约与W_r','R01—R06/R37','E01—E04/E11','标准屏障实例化；有认证域语义和反例价值','真实抽象与强基线同条件增量未建立'),
('C-A2','完整后续Q与商键','AND/OR、同下界通用BB','E12/E13','A2可运行；A3无命中','不能以启发式更差证明新原理'),
('C-B1','生命周期最小G配置','R10/R11；简单正确共享/独立授权','E05—E07','域规约、证书和覆盖边界','共享broker等效；规则遗漏被回退补齐'),
('C-B2','原生分离割与组件前沿','分支定界、分解DP、R43','E14—E16','必要条件及实现候选','没有净效率优势；Z3同最优'),
('C-AB','冲突反馈与DRD下界','R08/R09及通用联合规划','E08/E09/E17/E18','可检查静态界；动态传递待研','投影敏感、开关同Q、未完整三模块耦合'),
('C-CR1','依赖支持隐私冲突','TV事件界与线性关系','E27','直接推论或自然组合','ε/δ区分、关系内位置、受限观察'),
('C-CR2','一般族可行性','GL对独立frame传递','E28','自包含条件刻画','自由r存在性，非一般协议下界'),
('C-CR3','拟阵分量资源刻画','R29—R32及随机编码R26/R27/R34','E29/E30','完整优先权未决；保守自然组合定位','匹配构造=分块；群分类精确归约未闭合'),
('C-CR4','两故障修复','稀疏插值、固定残差线性核验','E24/E25','具体专用构造与有限实现','一般k与整体最优未证；固定种子不私密'),
('C-CR5','AES记录关系','R22—R26/R41/R42','E26','记录关系工程连接','不是TLS来源全证；未接最新修复'),
('C-CR6','单行统计隐私边界','R36/R39/R40；群平均与补集计数','E35','明确限定模型研究候选','隐私要求改变；采样完整成本无优势证据'),
('C-CS03','历史隐私刷新','R35；既有随机编码/安全复用','E22','历史文档条件推导','源码与原始运行缺失；完整转录映射未完成')]

next_items=[
('N01','规范与证据基线','D01—D15及K01—K16签认；保留历史版本/哈希','37项需求与当前能力一一映射；无状态/成本偷换','优先1，文档层'),
('N02','补齐缺失工件','取得v2.13、CS03、四阶段同版Schema/SQL/图源','包内来源/哈希可验证；未取得前维持缺失','优先1'),
('N03','先例精确归约','R34全文、R11全文；群分类小域条件逐项映射','给出可复查定理到定理归约，确认覆盖则降级','优先1，研究门'),
('N04','决定保持抽象','固定相同动作/投影/预算/义务和通用抽象基线','证明值界/策略保持；表示构造成本与原始精确参考同时计量','优先2，拟议A路线'),
('N05','组件前沿压缩','真实共享结构或预冻结结构参数','与优化枚举/Z3/DIDP同条件比较；保留17例回退负控制','优先2，拟议B路线'),
('N06','有状态核心传递','先明确转换前后约束有效性与证书','动态反例通过；失效重查成本计入；未证明不剪枝','优先2，拟议AB3'),
('N07','最小可信产品闭环','M01—M04/M10/M11、真实批准/进程边界','SC1正常正例、AT06/07边界；不能以L0测试替产品验收','优先2，产品门'),
('N08','原生未知契约绑定','普通用户合法Q1/Q2、F3先审定','V-Q真实初始不确定→观察→配置变化；V-R范围正反例','优先3'),
('N09','非原子配置与恢复','拆发行/提交微步骤；CP0/CP1/CP-STAGE/CP2','迟到/撤回/并发下证据与义务不丢；合法恢复正例','优先3'),
('N10','密码学来源与合规','真实支持来源或不缩成功域的私密gate','原67输入不因压缩删18；域/接收者/输入固定一致','条件性辅助门'),
('N11','密码学完整成本与安全','同来源/gate/预处理/泄漏；正常新鲜随机','比gate直接输出/分块/seed-repair；恶意偏离及中止前泄漏审计','达门后才扩MPC'),
('N12','主线接口集成','PublicDiagnosticEvidence及来源/epoch验证','真实调用链、预算/UNKNOWN/ABORTED后继和无自动放行测试','尚未授权本轮实施'),
('N13','独立预实验与统计冻结','独立配置家族、目标效应方差、功效与留出','研究者确认建议阈值/α/统计脚本；所有技术门也通过','正式实验进入门'),
('N14','完整W0与L2','4核8GB全部署、真实模型两代理、1000准入/30规划','完整链计时、正常任务成功、留出配置；原生与增强分开','产品验收而非创新判据')]

def export():
 for name,rows in [('当前实现与证据状态表',evidence),('文献核验表',refs),('关键矛盾及处理记录',[dict(zip(['id','conflict','evidence','resolution','trace'],x)) for x in conflicts]),('贡献主张—先例—证据—限制对应表',[dict(zip(['id','claim','prior_art','evidence','judgment','limitation'],x)) for x in contributions]),('未完成项及下一阶段进入条件',[dict(zip(['id','work','prerequisite','acceptance','order'],x)) for x in next_items])]:
  (OUT/(name+'.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
  with (OUT/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 bib=[]
 for r in refs:
  fields={'title':r['title'],'author':r['authors'].replace(';',' and'),'year':r['year'],'url':r['url'],'note':r['type']+'; 核验日期2026-11-03; 实际阅读范围见配套核验表'}
  if r['doi']:fields['doi']=r['doi']
  bib.append('@misc{'+r['id']+',\n'+',\n'.join('  '+k+' = {'+v.replace('&','\\&')+'}' for k,v in fields.items())+'\n}')
 (OUT/'统一参考文献.bib').write_text('\n\n'.join(bib),encoding='utf-8')
