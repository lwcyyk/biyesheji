# 并发、重放与十二类故障交错

## Material Passport

DCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。验证方式为 ANALYZED；原生动态验收未开展。

**PQ-5=PARTIAL。** v2具有条件性的额度安全归纳；冻结运行程序尚无该配额机制，原生故障验收0。完整矩阵与最小反例见[CRASH_AND_CONCURRENCY_MATRIX.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/evidence/CRASH_AND_CONCURRENCY_MATRIX.json)。

|交错|额度/记录裁决|关闭与证据裁决|
|---|---|---|
|I01 预扣前崩溃|新额度未发放；已完成全球预付前缀保留|原实例关闭，缺cursor不初始化重发|
|I02 预扣后、事实前崩溃|该槽永久烧掉；可无主行|cursor INFLIGHT或角色死亡触发关闭|
|I03 主行中途/短写|该槽保持已扣；仅保留原始部分行|原字节不整行重写，不继续观察；UNKNOWN|
|I04 full write后fsync前崩溃/EIO|持久性不确定，额度保持|失败证据不足仍UNKNOWN|
|I05 fsync后、完成cursor/确认前崩溃|完整行可能已经存在；不重发原token|INFLIGHT恢复路径只关闭；不凭未收到响应退款|
|I06 COMMITTED预扣或完成后崩溃|全球R和local ordinal保持，返回缺失不回滚|重启不重建T0/账/额度|
|I07 同task/ordinal重复提交|原生无task_id；绑定token复用获得0新额|不同ordinal为新观察，照常消耗剩余额|
|I08 两写者争最后额度|同一稳定H锁内fresh-read→durable debit，仅一者成功|后一者看到终态/256；拒绝无额外行|
|I09 global journal短写|沿用原预算核心halt与模糊intent拒绝|原journal部分字节保留，local cursor无权初始化|
|I10 cursor/log/STOP/CLOSED EIO|不退款；停止继续工作|固定错误码可尝试写；持久关闭/回收未知保持UNKNOWN|
|I11 CLOSED/STOP/terminal cleanup期间请求|吸收态，0新授权/0分类|原始终态标记不撤销，停止新入口|
|I12 native seal读取期间变化|需真实角色退出/写者静止，缺前提即拒绝|仅CLOSED存在尚不足够；禁止先hash后变更混包|

线性化次序：所有原生角色共享H生命周期锁；先核身份和当前cursor，原子持久预扣全部计数/类别位，才进行一次日志写入尝试。分类原始行fsync后再持久completion；对终态，在释放锁进入回收之前持久锁存。每笔模糊状态都烧额；角色/进程重启一律关闭该实例。两次持久更新避免把“已预扣”误写成“原始行已保存”。

TERMINAL_LATCHED只封闭新分类；VERIFIED后的未用HANDOFF_VERIFIED/RESUMED类别槽仍须按原始guard消费，计入六stage。FAILED进入POISONED；EXHAUSTED/STOP/CLOSED封闭全部新类别。这一区别避免把成功交接所需的最后两个stage一并阻断。

三个边界条件必须保留：锁文件inode受信且不可被并发Root替换；所有实际写者遵循相同锁和schema；文件及父目录fsync按受审存储模型生效。特权回滚、外部写者和任意重启属于证明域之外，遇到这些情况拒绝资格。正常代码单Receiver的事实不能自动推广到任意两个observer；v2要求锁存封闭cleanup间隙，见CE-TERMINAL。

与现有预算核心的关系：[guard.py:568](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:568)用线程RLock与flock检查健康counter/intent，[guard.py:629](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:629)的scalar reserve先PREPARED、journal、counter持久，再COMMITTED；模糊错误halt。[range_core.py:22](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/range_core.py:22)具备固定task的幂等range，但生产_task_contract目前限定C02/C03/C04，Root C09不能直接假定获得该能力。

v2建议在C09 controller/ready/counter固定之前，用既有scalar primitive预付256次，cursor记录before/after和journal前缀长度/hash；中断后关闭并烧掉已付前缀。初始化幂等采取“已有/残留/模糊即拒绝第二次初始化”，不再铸造新block。观察阶段只花已付local额度，全局R与C09 ACK counter保持。local cursor承担资源槽与类别位，不复制全局预算账或重新定义T0。

锁等待次数、辅助query输出及原停止链多角色交错仍需具体实现的静态证明。配额不变量给出有限授权写入工作量；它没有给任意外部请求洪泛/lock-spin次数或底层fsync时延上界。

522更新及两份cursor失败staging另依赖全局“失败写不重试、单首错/poison责任、后续拒绝不再写”的调用界。残留staging/INFLIGHT必须使所有角色拒绝后续工作；EIO连失败标记都未能发布时的跨角色传播仍属完整关闭/集成未决项。该调用界是待实现合同条件，当前未把它登记为冻结源码已有保证。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
