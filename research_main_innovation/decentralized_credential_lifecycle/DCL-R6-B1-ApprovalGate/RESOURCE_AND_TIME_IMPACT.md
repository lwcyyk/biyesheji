# B1资源与时间影响

## Material Passport

DCL-R6-B1-ApprovalGate，B1-ApprovalGate/review-1，2026-11-16，Asia/Shanghai。本阶段完成合同、语义差异规划与实施准入审查。证据为冻结源码/输入、既有证明和两项分开执行的只读源审查。

本次为语法长度和源码调用次数分析，新增执行数为0。预付、local quota和完整关闭/归档各有原件与成本责任，准确模型见资源文件。[RESOURCE_IMPACT_MODEL.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-ApprovalGate/evidence/RESOURCE_IMPACT_MODEL.json)

|组件|条件成本|来源与范围|
|---|---:|---|
|Root健康预付|256次scalar事务，global R增加256|当前calibration/global限额和有效C00 ticket约束|
|新增global journal|512行，编码字节≤122112|PREPARED每行≤238、COMMITTED≤239，含LF|
|intent数据写|512次、字节≤142592|RootIPC pretty编码，P≤278、C≤279|
|counter数据写|256次×8=2048 bytes|同一原counter持久递增|
|上述预付数据总量|1280次数据写，≤266752 bytes|两个intent、两个journal、counter各一项|
|上述Root预付fsync|2304次|每事务两次跨目录intent各3次sync、journal两次、counter一次，共9次|
|旧v2 local模型|cursor1198、更新522，局部retained350166、写量971216、durability1316|仅旧声明集合和正确codec/调用/失败owner条件|

预付行长由guard597的compact codec、624的LF、658/670固定record及已有数值ABI推导。RootIPC的file/destination/private三次sync用于两个Root intent发布。该表按健康成功前缀计算，失败前缀保留已发生写入和预算消耗，完整失败责任继续计入关闭子合同。[src/guard.py:597](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:597) [src/guard.py:624](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:624) [src/root_ipc.py:115](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/root_ipc.py:115)

local1316包含主日志及声明marker的一些既有写路径，预付2304为新增加的256事务成本。需要准确diff才能给出与原程序的净增量和全系统syscall、heap、FD、读写/存储成本。新增quota源输入、五个未来评审对象及其结果/失败staging须按真实保存层分别计数。当前full_runtime_raw_delta和新export/member cap为null。

上轮访问模型68498加新预付256为68754，尚需新增检查Δ。各phase和原全局1m/calibration100k及原票据deadline继续约束任何未来运行。旧MR256属于独立预付责任，额度转移没有本轮审批对象。主log345148与预付journal成本均需进入完整字节合同。

256次scalar会增加顺序持久化延迟。已有5/30/300/1800窗口、Root停止策略和AS/TasksMax并不提供所需动作的最坏成功时延。当前全部TCB/文件系统/syscall latency与完整native/host时间仍未闭合。[冻结时间裁决](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-ResidualBounds-Decision/WALL_TIME_ASSUMPTIONS.md)

H≤52/core≤212来自原冻结角色图。候选在相同线程图内增加scalar调用仍需按精确diff复核单调HALTED入口和异常包络，当前源证明保持其原作用域。原件完整、真实退出、UNKNOWN和所有资格来源均为后续检查保持式。


RESOURCE_GATE_PASS=NOT_OBTAINED

F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE

STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
