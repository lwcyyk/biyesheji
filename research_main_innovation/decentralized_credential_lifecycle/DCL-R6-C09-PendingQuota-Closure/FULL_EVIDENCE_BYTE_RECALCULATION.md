# 完整证据数量、分层字节和处理量重算

## Material Passport

DCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。验证方式为 ANALYZED；原生动态验收未开展。

**PQ-6=PARTIAL；CAPACITY_CONTRACT_NOT_READY。** 旧4450/4451/4452为冻结完整scope的条件数量包络；345148的主日志子项成立不会替代其他生产族的字节责任。见[CAPACITY_RECALCULATION.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/CAPACITY_RECALCULATION.json)与[evidence/COUNT_SCOPE_COVERAGE_REVIEW.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-BoundClosure/evidence/COUNT_SCOPE_COVERAGE_REVIEW.json)。

|集合/层级|旧数量上界|C09计数方式|
|---|---:|---|
|封存前raw原件|4450|inputs/root_private/c09_events.jsonl已占一个文件槽；263行仍是一份文件|
|Native ZIP成员|4451|raw集合＋native manifest1|
|行政导出原件|4452|raw集合＋native manifest1＋native ZIP1|
|行政ZIP成员|4467|导出原件＋旧host/source sidecars与行政manifest；仅适用于旧scope|

上轮修正已包含mr_events.lock；完整CALIBRATE_S1S9_THEN_F1_F4 scope不可达的pt_expected_abort槽退出覆盖表。该修正和旧数字保持，新scope/新配额代码不得自动继承全部前提。

假设将来实施v2，原main/STOP/CLOSED路径继续属于旧集合。新cursor和失败摘要最多2个稳定文件，另有cursor失败staging2和摘要失败staging1，共新增集合Q≤5；标记失败staging若已有旧RootIPC异常族覆盖则不新增，若覆盖之外需另加Δ_close。新的源码/测试/授权收据及集成差额也单独计量：

\[K_{new}\le4450+|Q\setminus K_{old}|+\Delta_{close,uncovered}+\Delta_{integration/tests}.\]

集成前尚未固定这些集合，故4455/4456/4457仅能成为特定零增量假设下的算式，当前未签为新容量。增量记录数与文件数分别计算，不新增263个raw文件，不重复增加旧三个路径。

用集合差而非无条件叠加重算字节：先从B_other_raw中拿出已计的STOP/CLOSED及其staging，再把一次main＋cursor/失败/staging＋一次STOP/CLOSED/staging纳入局部350166包络，随后加其余原始C09/MR/回收/系统/测试对象。这样B_total不重算同一raw路径；行政层实际又复制原件并包含native ZIP，实际物理复制成本须保留。

\[U_N=R_{raw}+M_N,\quad Z_N=ZIP(U_N;paths,codec),\quad E_A=R_{raw}+M_N+Z_N.\]
\[U_A=E_A+H_{host}+S_{locks}+M_A.\]

|完整生产族|可用局部事实|完整资源缺口|
|---|---|---|
|C09|主日志345148；局部v2子集350166|cursor/配额尚未实施；commit.resources、cleanup和其他原件需逐schema界|
|C00–C12|counter24、C03固定16MiB等|局部journal、结果、快照与输出需同scope总和|
|RootIPC/Boot/readiness|4MiB/128KiB读取接受cap，readiness602×131072=78905344的cap乘积|生成/异常staging与aggregate匹配未闭合；cap乘积超32MiB不证明极值同时可达|
|ManagerRecovery|event32KiB、query接受8192/2048|接受限制位于capture之后；close/errors/预算snapshot聚合仍需界|
|S1–S9|48×256×4096=50331648 trace cap乘积|registry/metadata/journal/snapshot和其余证据另计|
|Global journal|旧完整校准条件15441008；全1m窗口条件471876988|writer与range/terminal后验32MiB接受义务尚未统一|
|Gate、F1/F4|固定槽位/访问额|状态树、策略、trace/report和序列化字节未完备；模型运行0|
|Metadata/封存/行政|manifest/ZIP接受cap与流式部分checker|raw generator、整文件哈希、压缩膨胀、嵌套复制、host stdout/stderr/traceback的总量与峰值未闭合|

这些数值为上一轮源码条件界/接受cap的复核延续，见[evidence/TOTAL_BYTE_FAMILY_AUDIT.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-BoundClosure/evidence/TOTAL_BYTE_FAMILY_AUDIT.json)、[evidence/GLOBAL_JOURNAL_BYTE_MODEL.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-BoundClosure/evidence/GLOBAL_JOURNAL_BYTE_MODEL.json)、[evidence/ZIP_BOUND_ALGEBRA.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-BoundClosure/evidence/ZIP_BOUND_ALGEBRA.json)。没有把高于cap的保守上界误作必然实际超限。

native收集会遍历ROOT内全部常规文件，完整性仍要求无symlink/错路径/缺件/重复/跨实例成员，逐件hash/size以及真实quiescence。旧256/257拒绝线保持，新材料不授予大包许可。对已接纳且总字节受限的包，独立oracle具有O(N+B)条件工作量；native生成前处理、环境扫描和admin整体尚未闭合，CAPACITY_CONTRACT_NOT_READY继续成立。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
