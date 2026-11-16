# 现有资产与证据复核

日期为2026-11-04。此次复核采用贡献入口、相关源码和原始结果的定向核查。文件数量与实现成熟度分别登记。当前新增候选机制实现数、原生实验运行数和密码学协议运行数均为0。

## 1 十组材料的读取与判断

|输入组|实际核读及源码/结果检查|本轮可采用的事实|限制|
|---|---|---|---|
|workspace_asset_review|REPORT、RESEARCH_ROUTES、RAG_UPDATE及CS03缺失记录|十二类旧资产已分类，较广问题集中于恢复、历史隐私和联合观测|路线卡仍缺强通用方法上的严格差距。[报告](D:/毕业设计/workspace_asset_review_2026-11-04/REPORT.md)|
|research_novelty_review|REPORT、GAP_CARDS，直接核读对应部分原文|C-LABEL已归约为策略区域覆盖，受限资格可用带代价布尔约束表达|接口可识别性本身仍受通用不可区分性和安全规划覆盖。[纸面审查](D:/毕业设计/research_novelty_review_2026-11-04/GAP_CARDS.md)|
|research_v12|报告相关定义、README，kernel、oracle、independent、a4、b4、joint、smt_joint及dev02原始行|完整联合策略、通用重放/抽象/预处理均有实现。重计688行，400可行、251界内不可行、37 UNKNOWN|运行一致性没有消除证书scope缺口，旧机制等效裁决继续有效。[源码](D:/毕业设计/research_v12/independent.py) [原始结果](D:/毕业设计/research_v12/runs/dev02/raw)|
|research_recipe_r3|延用已核读定理、量词表与原生审计，核对expanded01摘要|268,310预算查询、5,000随机需求族、500较大固定配置族和224谱构造有原始记录|36谱例完整下界枚举，188例依赖手工引理前提。本轮未重跑。[数学复核](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md)|
|CAPABILITIES|能力表、原生planning绑定及关键旧RT竞争记录|两平台13条件各两重复，共52次观察。真实副作用和查询者限制有数据|旧RT竞争的AS内省结果与共享账户根、业务RP接受分别解释。[能力表](D:/毕业设计/auth-lifecycle/docs/experiments/CAPABILITIES.md)|
|RESULTS|结果报告及pilot02全量JSONL重计|576运行，六方法各96次，各20完成/56拒绝/20 UNKNOWN，query与feedback均0|已知契约负控制，无法支撑补证优势。[原始行](D:/毕业设计/auth-lifecycle/results/experiments/pilot02/runs.jsonl)|
|ARS_V2深化|阅读入口、综合报告及研究点修订的关键模型/卡片|旧而有效证据的双世界、见证交集、最后提交与联合视图已有规范|这些主要是条件推导和未执行案例，正式冻结数为0。[综合报告](D:/毕业设计/研究/ARS_V2深化研究_2026-10-16/03_综合研究报告.md)|
|CS03|按OOXML顺序提取全部226个非空段落及公式文字|固定仿射响应的历史关联分离、公共加性修复与完整协议提升义务可核读|报告记载的32,768项、48份、96份等运行仍属历史报告转述，源码和原始转录未定位。[原件](D:/毕业设计/CS03_密码学贡献重构与历史隐私刷新_2026-10-23.docx)|
|final_closure|ARCHIVE_STATEMENT、贡献映射、MODEL_REDUCTION相关定义、VALIDATION/VERIFICATION_RESULTS及verify_dual关键函数|独立检查器固定q=4099、d=k=4、n=5，使用Fraction核对原始/对偶。当前检查器摘要及模型摘要与证书一致|分类为限定模型刻画，机制优势NOT_ESTABLISHED，状态MAINTENANCE。[归档](D:/毕业设计/研究/密码学辅助_一致性核验/revisions/final_closure_2026-11-04/ARCHIVE_STATEMENT.md)|
|关键论文与可行性核查|直接核读RAG、Root-Scoped Quiescence、AID-Guard及私密策略求值相关章节|RAG全文当前可用，定义15、17—20及恢复/攻击模型均已进入比较|本轮没有运行GROOVE或外部论文的工件。[RAG全文](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P08_全文.txt)|

## 2 影响方向选择的源码事实

`experiment/planning.py::plan`把原生A/AB输入构造为单一registered世界，probes、cleanups和faults均为空，返回query_needed_profile=false与formal_H_A_H_AB_eligible=false。后续还显式拒绝query-dependent policy。因此，现有认证HTTP部署可以复用为接口调查工具，其数据尚未证明安全补证在真实未知契约下有效。[源码](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/experiment/planning.py)

`kernel.control_solve`对统一K求configure/stop/cleanup策略，`oracle.FullB.native`的逐世界原生B结果仅用于排序。`joint.solve`继续完整min/max搜索，`smt_joint.Incremental`用相同有限图编码并复用push/pop。A4向通用证书抽象开放相同机制，B4只合并相同语义且零delegate费用路径。它们构成本轮强对照能力，候选须同时计入其预处理、共享图、缓存和证书复用。[控制求解](D:/毕业设计/research_v12/kernel.py) [完整B接口](D:/毕业设计/research_v12/oracle.py) [联合求解](D:/毕业设计/research_v12/joint.py) [SMT](D:/毕业设计/research_v12/smt_joint.py) [A4](D:/毕业设计/research_v12/a4.py) [B4](D:/毕业设计/research_v12/b4.py)

`independent.Checker.check_certificate`检查control-only头部后调用`replay`，而`replay`对动作直接调用原始expand，未逐节点使用action_set限制probe。这与已登记scope反例一致。正常生成路径和任意不可信证书的接收合同各有证明责任，此缺口属于正确性维护。[检查器源码](D:/毕业设计/research_v12/independent.py) [既有反例](D:/毕业设计/research_secret_recipe/SCOPE_AUDIT.json)

密码学`verify_dual.verify`重新建立字典、轨道计数、原始/对偶可行性及互补松弛，直接绑定MODEL_REDUCTION摘要。它支持固定公开数学profile，authorizes_execution=false。本轮只核对源/结果绑定和已有输出，全部一般归约仍依赖手工论证。[检查器](D:/毕业设计/研究/密码学辅助_一致性核验/revisions/final_closure_2026-11-04/verify_dual.py) [原始核验结果](D:/毕业设计/研究/密码学辅助_一致性核验/revisions/final_closure_2026-11-04/VERIFICATION_RESULTS.json)

## 3 原始结果与缺失项

本轮重计v1.2 dev02的688份raw JSON与688个index条目，读取分析状态为决定性参考一致。原生52行调查和576行校准重新计数，六方法的选择器与反馈激活数均为0。R3结果与密码学两组精确值只按原始记录核对来源，全部重计详情保存在RAW_RESULT_AUDIT.json。[本轮重计](D:/毕业设计/research_main_innovation/evidence/RAW_RESULT_AUDIT.json)

dev02登记的18项源码全部与其source_snapshot匹配，当前目录只有14项匹配。analyze.py、preserve.py、test_ab3.py和test_structures.py与该批登记不同，差异来源本轮未归因。因此688行结果继续绑定当时快照，当前检查器和算法的代码阅读单列。此核对范围限于registry中的18项，共享依赖沿用各自记录。[逐文件对照](D:/毕业设计/research_main_innovation/evidence/V12_SOURCE_BINDING.json)

CS03原件存在，但本轮精确文件名搜索仍未找到run_models.py、run_local_separator.py、run_balanced_history.py及balanced_history_run1.json。旧复审对39个ZIP的成员检索作为继承证据，当前缺失状态限定于这些已查范围。后续可独立重新推导模型，历史运行数字仍需原始文件才能提升证据等级。[归档搜索](D:/毕业设计/workspace_asset_review_2026-11-04/CS03_ARCHIVE_SEARCH.json) [本轮提取](D:/毕业设计/research_main_innovation/sources/cs03.txt)

VBP公开下载入口本轮返回403，用户随后提供`D:\毕业设计\研究\usenixsecurity25-fabrega-partitioning.pdf`。已取得21页全文并核读§2—4、§6.1—6.3及Theorem 1—2，全文缺口现已关闭，早先失败请求保留。[本地原文](D:/毕业设计/research_main_innovation/sources/vbp.pdf) [取得记录](D:/毕业设计/research_main_innovation/sources/vbp_local_retrieval.json)

## 4 证据等级

本轮产出属于资料核查、纸面实例和先例映射。同一研究辅助流程完成审查，外部同行或证明助手审定仍待开展。已执行历史结果、历史报告声称、纸面可证结论、待证机制和实际部署分别登记。新问题的重要性从使用场景与现有事实判断，主创新资格仍要求独立的技术差距证据。
