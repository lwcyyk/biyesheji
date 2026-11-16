# B1最小关闭合同最终裁决

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

**B1_CLOSE_RESERVE_COUNTEREXAMPLE，B1_BLOCKED_BY_CLOSE_RESERVE。** 本轮完成所授权的最小合同、scope计数/字节式、物理保障审查、失败责任与独立oracle规格。当前无物理保留的组合存在具体容量分配反例，源码实施申请暂停。

|证明面|状态|结果|
|---|---|---|
|调用链/推荐语义|CONDITIONAL_PROVED|固定异常通过H退出到808/817，保留normal close=False路径和原CLOSED事实|
|E域关闭次数|CONDITIONAL_PROVED|A6/S8/W1/Q3/H0，59生产尝试/23稳定路径/47失败staging粗界|
|Receiver健康串行例|CONDITIONAL_PROVED|14数据发布/9路径，first941、marker183、cleanup1119，数据≤9272＋2ΣV|
|完整最小encoded/physical数值|PARTIAL|B_B1-close、FS分配及外部witness/index参数继续null|
|保留空间可用性|COUNTEREXAMPLE|最后main/cursor持久后新close staging可ENOSPC，逻辑余额不提供物理底线|
|实施准入|BLOCKED|B1_BLOCKED_BY_CLOSE_RESERVE，停止本轮实施申请提交|

反例目标为当前无物理保留组合的必要停止信息保存承诺。它是source-bound候选组合推导，原生故障执行0，存储故障下UNKNOWN与现有模型一致。该不完整结果仍不足以达到本轮实施直接门。外部TCB需实际承担并保留可信停止/退出事实，不能通过可能无法执行的admin阶段弥补缺失来源。[MINIMAL_STORAGE_COUNTEREXAMPLE.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/MINIMAL_STORAGE_COUNTEREXAMPLE.json)

E域仅对应初始C09第256条PENDING、无VERIFIED/无恢复及无新预算操作。正常成功handoff另有6次发布/4载体，其他B1故障继续使用全scope212/54及原A16/S23/Q7/W2/H52。两层abort追加并非一般API完整幂等，当前没有单独close额度账。[B1_CLOSE_RECORD_COUNT_PROOF.md](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/B1_CLOSE_RECORD_COUNT_PROOF.md)

主log345148、预付266752和其内journal122112各有明确来源，数据按实际层/路径一次计量。累计预付写量不代表保留容量，关闭预算映射不重复复制journal。最小合同20字段中数值不足者保留null，所有approved/effective/runtime_enabled=false。[B1_MINIMAL_CLOSE_RESERVE_CONTRACT.md](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/B1_MINIMAL_CLOSE_RESERVE_CONTRACT.md) [B1_MAIN_AND_CLOSE_QUOTA_SEPARATION.md](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/B1_MAIN_AND_CLOSE_QUOTA_SEPARATION.md)

|序号|验收问题|答复|
|---:|---|---|
|1|真实调用链是否完整|18节点含normal/stopped/异常三分支、父进程旁路、两层abort与后层seal/admin，每节点有9个source属性。|
|2|EXHAUSTED循环风险|直接返回时caller未消费，会在其他deadline/异常前反复进入；无quota局部次数界。推荐固定异常消费。|
|3|H在abort前释放|正常valid-fd上下文finally先unlock/close再outer except；unlock/close失败或实际死亡延迟进入明确故障模型。|
|4|两层abort记录|第一层健康串行8写，外层复用STOP/first再6写，合计14写/9路径；一般本地每层最多9核心尝试。|
|5|必要集合|18项事实/载体涵盖身份/quota/首错/marker/回收/角色/预算/锁和后层引用，外部自身退出provider未绑定。|
|6|212与唯一数关系|212为全冻结包络生产尝试，稳定路径粗界54；本轮E域59尝试/23稳定路径，47失败stage粗界另计。|
|7|记录数量是否有限|CONDITIONAL_PROVED，E域A6/S8/W1/Q3/H0，局部Receiver两abort；域外调用和其他B1故障作用域分别处理。|
|8|关闭字节有无数值|B_B1-close=null。得到E域生产179815＋138T＋18B＋8E＋8ΣV和唯一/暂存公式，TCB/provider/index等未实例化。|
|9|345148与close是否独立|主log路径独立；当前close独立计数/物理底线尚未建立，旧350166组合按真实路径去重。|
|10|512行与122112归属|原global journal的256PREPARED和256COMMITTED，各238/239条件行界，已经包含在预付总写内。|
|11|266752是否重复|122112journal＋142592intent替换写＋2048counter覆盖写，一次相加。该值计量预付累计写入，关闭可用空间另需保留证明。|
|12|RootIPC/Store物理保障|权限/metadata/发布/fsync来源明确，data/inode/metadata/temp保留provider及排他凭据未取得。|
|13|耗尽时能保留停止记录吗|无保障组合存在ENOSPC最小反例，实际回收可尝试，必要持久信息无法保证，当前B1准入BLOCKED。|
|14|short/ENOSPC/EIO结果|拒绝新授权、烧掉模糊slot、保留raw/partial/staging与原账；共享取消/实际退出/native/admin按证据分别UNKNOWN/失败。|
|15|外部TCB责任|真实身份绑定stop/kill/pidfd/cgroup/manager观察及独立Receiver自身退出保留；provider、路径、byte和故障域需明确。|
|16|native/admin最低输入|原activation/state/checkpoint/phase/runtime-intent/budget/role/marker/waitpid及最小已保存事实索引；admin不能补造丢失亲子/退出事实。|
|17|B1可否独立实施|当前B1_BLOCKED_BY_CLOSE_RESERVE；充分受限子合同可成为直接门输入，其余完整容量null后层继续负责。|
|18|最小源码文件|未来具备条件时c09_handoff.py和guard.py；MR/runtime_tree_lock只读。当前额外allocator/helper变化须单独申请。|
|19|是否可提交实施申请|当前SUSPENDED，反例与关键null尚在。本轮保留条件索引和继承范围，源码/补丁写入0。|
|20|还缺哪些审批|主quota逻辑及本最小合同定量/存储/退出来源、原MR有限规则、独立源码和完整动态四类决定均未实际授予。|


强G比较为COVERED_BY_G，严格差距0、分离实例0。未升级架构原创性。四类实际批准均缺席，原MR14条摘要与状态按原绑定保留。当前完整native/admin容量、B_other和端到端资源/时间继续由后层负责，原256/257合同下完整成功目标的既有矛盾保持。[GENERAL_G_COMPARISON.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/GENERAL_G_COMPARISON.json)

本轮14报告、18证据项、18调用节点、12项CR规格、10类故障矩阵及最小合同准备完成。9867历史文件加此前728交付件合计10595旧文件、64源/输入及原导航字节后缀将由最终交付核验逐件核对。source/预算核心/C09/MR/Guard/native/admin/gate/D1/D2改动0，新批次/T0/预算/补丁0，WSL/动态/真实故障/F1/F4执行0。[DELIVERY_CHECK.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/DELIVERY_CHECK.json)

下一步限定为用户决定和缺失的定量wire、真实存储保留/排他及独立退出保留来源。当前暂停实施申请，等待充分子合同证据与独立权限。[B1_IMPLEMENTATION_ADMISSION_REQUEST.md](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/B1_IMPLEMENTATION_ADMISSION_REQUEST.md) [EVIDENCE_INDEX.md](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/EVIDENCE_INDEX.md)


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
