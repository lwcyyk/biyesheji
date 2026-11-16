# 证据数量约束的结构性冲突

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


**EVIDENCE_COUNT_CONTRACT_UNSAT。** 在现有逐件原件/逐成员ZIP合同及完整链输入下，全部必需证据与256/257同时满足的解集为空。

|证据层|确定数量|证据意义|
|---|---:|---|
|TR-A2真实native manifest|233原件/234成员|既有最小路径的确切实际数量|
|TR-A2真实行政manifest|249行/250成员|235个运行文件＋10个host侧件＋4个source lock＋manifest|
|FullChain-B原证明|至少312原件/313成员|六组C00后回归，最小缺口56|
|本轮扩展校准证明|至少887原件/888成员|增加C09H238、IPC56、BC40、S34最少170、ledger71|
|含完整F1/F4轨迹|至少1082原件/1083成员|另加195个模型输入/输出；最低缺口826|

312＋238＋56＋40＋170＋71=887；887＋195=1082。全部路径互异；额外输入、票据、锁、结果、时序、registry、快照、错误/临时文件、原生包与manifest开销尚未计入。1082/1083继续作为下界，完整实际数及最大必要数保持UNKNOWN。

实际manifest逐项核验已完成。新的完整运行尚未存在，其sha256/size字段均null。依据本轮“新上限应依据完整manifest的实际最大必要数量”“禁止任意设定过大的宽松上限”，当前材料不足以选定生产新上限。把313或1083直接用作上限将遗漏后续必需文件。

[794条原清单](evidence/EVIDENCE_CATALOG.json) · [1082条扩展路径](evidence/EXPANDED_FULLCHAIN_LOWER_WITNESS.json) · [261个源写入/读取/路径调用站点](evidence/PRODUCER_SITE_CENSUS.json)。源站点清点含读操作与别名，需沿语义调用路径闭合其基数；清点本身未充当完整上界。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
