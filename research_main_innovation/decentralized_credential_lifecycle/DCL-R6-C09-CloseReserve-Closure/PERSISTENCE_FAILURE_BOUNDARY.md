# 逻辑保留、I/O故障和外部停止边界

## Material Passport

DCL-R6-C09-CloseReserve-Closure；CloseReserve-Closure/review-1；2026-11-16（Asia/Shanghai）；只读源码、冻结输入、字节代数和抽象轨迹审查。结论类型ANALYZED；运行实例、原生故障和模型检查均未启动。

总体为**PARTIAL**：可证明的预算/日志动作不变量与实际停止、持久证据和封存结果分别报告。有限逻辑quota提供正常存储条件下的空间需求约束；未建立磁盘物理预分配、关闭池隔离或任意介质故障下的完成定理。

|事件/前提|仍可保留的保证|需要实际证据的部分|
|---|---|---|
|预扣完整持久，尚未append|待批v2槽烧掉；无重发授权|cursor真实持久性、恢复读与所有写者遵约|
|主行短写|当前_full一次write，短写抛异常；原部分字节保留|后续清理/终态/归档能否保存；部分行无法冒充完整事实|
|write成功、fsync EIO或确认前死亡|不退款，不据未收到返回再次append|完整行是否持久未知；cursor完成/退出收据须核原件|
|STOP/CLOSED已存在，即使内容损坏|RootIPC presence取消活动准入|该标记的身份/boot/格式、真实回收和native_ready另验|
|标记发布失败，只有_HALTED|当前进程的预算health拒绝；新配额需拒绝本角色新观察|跨进程可见停止尚未由内存flag推出；共享intent/监督/marker/退出证明必需|
|systemctl stop/kill报错或超时|现行代码尝试fallback并记录错误|payload_empty、已知Root角色退出、亲子waitpid分别确认；超时返回不保证全部退出|
|Root协调者死亡|外部停止器可按当前责任尝试回收|父waitpid若未保存，Receiver无法补造；native证据可保持UNKNOWN|
|native seal失败或部分ZIP|保留原raw与SEAL_ERROR/处置材料|完整包/hash/成员集合/版本校验，缺失保持NATIVE_SEAL_UNRESOLVED/FAILED|
|行政finalizer失败|host保留原始流、失败或finalization-error收据|行政归档独立UNRESOLVED；历史native结论按实际原件保留|

[src/manager_recovery.py:317](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/manager_recovery.py:317)的first_failure、ABORTING、回收、close_attempts与final状态按既有错误模型保留。其错误码/UNKNOWN不能替代真正退出。正常路径内部mr_close_state缺失时也可为UNKNOWN，与native/admin是否已封存分别呈现。

预留主日志、关闭记录、外部见证、native输出和行政输出是不同域。关闭池需要保证其他生产者不能先消耗其必要空间；当前只有数字草案，没有已部署的隔离/物理保留证据。外部host/control与Linux ROOT路径分离也未证明独立磁盘故障域。外部TCB的系统查询、原始日志或post-exit快照仅在自身确已取得并校验时可作停止证据。

T0、deadline、budget/R及旧关闭状态持续保留。停止/封存/terminal reader无预算初始化或新授权路径；异常不会产生新免费窗口。全局R在C09 idle关闭期间应保持，存在并发合法budget actor时还需核对最终原件。[COUNTEREXAMPLE_REGISTER.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/COUNTEREXAMPLE_REGISTER.json)登记缺共享标记和缺父见证边界。

本轮没有执行fsync/短写/EIO故障实验、真实组停止或Root注入。所有“可停止”结论保持对可信kernel/systemd/Root、可用当前监督、有效权限/期限和实际I/O结果的条件性；任意存储故障下成功native seal的承诺仍关闭。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；PASS_BOUNDED=[]；IMPLEMENTATION_GATE=CLOSED。
