# 主日志预留与全PENDING证据字节裁决

## Material Passport

DCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。验证方式为 ANALYZED；原生动态验收未开展。

**PQ-3=PARTIAL；PENDING_BYTE_BOUND_PARTIAL。** 345,148 bytes可以作为受审主日志的条件预留，完整PENDING及关闭/封存证据仍需独立项。当前运行源码缺次数配额，当前总量为PENDING_BYTE_BOUND_UNRESOLVED。

从真实3个原生调用点和六个stage得到：

\[B_{main,reserved}=256\times1322+6\times948+1\times1028=338432+5688+1028=345148.\]

主行LF已包含；metadata/reserve不能隐含为0。全部schema采用更紧1318及实际六stage时可得344084的条件包络，合同继续保留345148。正常ACK缺witness自环的成功路径上界255×1298＋1322＋6×948＋1028=339028；它的6120字节余量只用于比较，额度已预扣且不退款，未给关闭生产者发放新授权。

|需覆盖对象|345148中的位置|本轮精确结果|
|---|---|---|
|最多263个主行/部分尾部|已含256分类槽、6stage槽、1ACK槽|CONDITIONAL_PROVED|
|quota cursor、类别位、终态锁存、预付桥接|独立元数据|v2 cursor≤1198；旧956缺新字段与持久完成责任|
|首份失败摘要|独立紧急对象|≤334；全局只写一次，固定代码，原始facts仍在主行|
|STOP_REQUEST / CLOSED|独立既有路径|限定ASCII reason≤43、RootIPC原编码下各≤189，稳定标记合计预留378缺席于345148|
|必要恢复/回收收据|独立stop_result、mr_close_state等|含snapshot/errors/roles；整体最大字节尚未闭合|
|native seal输入|原ACK/commit/witness/预算/角色退出/阶段/终态等|主日志之外；完整输入集合仍有未决项|
|native/admin manifest、ZIP、host原始流|独立派生与复制层|全局容量另算；345148从未覆盖这些对象|

新cursor按旧字段加lifecycle_mask、terminal_latched、ordinal、prepay_before/after、journal-prefix bytes/hash构造封闭schema：骨架1107＋三浮点72＋journal字节计数19=1198。七类位提供生命周期幂等；每次分类追加后有一笔持久completion，终态先锁存再解锁cleanup。旧合同保留原字节，新字段及工作量只存在于v2待批附件。

限于cursor/首错/两个标记的最小子项，稳定保留量为345148＋1198＋334＋2×189=347058；再保留两份失败cursor staging、一份失败摘要staging、两个标记失败staging，得到：

\[B_{local}\le345148+3\times1198+2\times334+4\times189=350166.\]

相对主日志的独立子项差额为5018；其中378是STOP/CLOSED稳定预留。相对旧348684局部提案的变化为1482。**350166仅为明确列出的局部集合界**；stop_result、MR、seal/admin尚有正的附加责任，完整关闭差额写作5018＋B_other_required_close＋B_seal/admin，后两项UNRESOLVED。这里保留345148原数，逐项说明缺失，不把新子项合计当作完整证据配额。

[QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/QUOTA_AND_MINIMAL_MARKER_ALGEBRA.json)给出每个模板和编码等式。逻辑reservation与磁盘物理预分配分别登记，当前无物理保留证明。内核/存储EIO下，即使字节额度足够也可能无法保存标记，真实状态保持UNKNOWN。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
