# 关闭保留量最终表达式

## Material Passport

DCL-R6-ResidualBounds-Decision；ResidualBounds-Decision/review-1；2026-11-16（Asia/Shanghai）；最后一轮既有15项责任的定向静态证明与合同决策。ANALYZED：未启动DCL业务、原生故障或模型执行。

**CONDITIONAL_BOUND已精化；完整关闭量为UNRESOLVED_EXACT。** 新结果消去了H与固定MR reason这两项自由量，未选定新的容量数字。机器等式见[CLOSE_CORE_REDUCED_FORMULA.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/evidence/CLOSE_CORE_REDUCED_FORMULA.json)。

继承A≤16、S≤23、W≤2，代入H≤52、Root MR marker≤194、first≤25092＋T＋B、external260、ABORTING237、cleanup line998＋11T＋B、cleanup state997＋11T＋B、stop_result1151＋E＋ΣV和waitpid≤1223，可得：

\[W_{core}\le488421+368T+48B+23E+23\sum_jV_j+52R_{budget}.\]

B≤69＋3max(106,29＋T)。W_core为212次核心生产尝试的字节总和包络，可以保守上界这些目标/实际失败staging的保留量。ABORTING和final共用mr_close_state；STOP固定路径、attempt多行单文件；生产成本多次计，保留文件按路径/实际版本只计一次。式中没有把字节系数选为新quota。

关闭分区按原producer矩阵去重：core已经包含MR first/cleanup、stop_event/result、两个phase的waitpid及预算hash/size映射；exit额外项仅指尚未计入core的外部/行政退出原件；normal MR review、terminal/native/admin和其他raw流另列。完整量：

\[B_{close}\le W_{core}+B_{exit,extra}+B_{MR,normal}+B_{terminal}+B_{other,disjoint}.\]
\[B_{C09,total}\le345148+B_{close}+B_{otherC09,disjoint}.\]

旧350166局部集合已含main、cursor、首错摘要、两个标记及声明staging。组合时把这些对象分配到各集合一次，不能把350166完整再叠加345148或完整close集合。global ledger原件只保留一次，core中的B是嵌入摘要，不复制原始ledger全体。

完整数值仍需R_budget/T/E/V的定量TCB profile，以及exit/terminal/stdio/model/admin等既有字段包络。任一必需对象未闭合，保持CLOSE_RESERVE_UNRESOLVED、FULL_BYTE_BOUND_UNRESOLVED和CAPACITY_CONTRACT_NOT_READY。已得到的212、194、387、488421等都不授予动态准入。

短写/模糊持久化下，已消耗额度烧掉、已捕获raw保留，缺共享取消/父见证/组空/完整包时保留UNKNOWN。关闭池需要足够空间及隔离，普通存储成功前提须明确；任意存储故障下完成native seal的承诺保持关闭。此处的未决量已转为精确合同责任，旧范围证明到此终结。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
