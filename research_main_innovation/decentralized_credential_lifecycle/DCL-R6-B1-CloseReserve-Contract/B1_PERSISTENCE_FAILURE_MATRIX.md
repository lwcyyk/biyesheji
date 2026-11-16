# B1持久化失败矩阵

## Material Passport

DCL-R6-B1-CloseReserve-Contract，B1-CloseReserve-Contract/review-1，2026-11-16，Asia/Shanghai。证据为当前冻结文件、源码调用关系、字节语法和抽象失败轨迹。本轮DCL动态、原生故障和模型执行均为0。

本地准入停止、实际进程回收、最小证据持久/完整、native/admin完成是独立结果轴。允许UNKNOWN的故障模型与正常存储下的空间充分性分别记录，任意I/O故障下完整持久化的承诺为false。[PERSISTENCE_FAILURE_MATRIX.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-B1-CloseReserve-Contract/evidence/PERSISTENCE_FAILURE_MATRIX.json)

|失败|本地与外部停止|退出与预算|内部/native/admin|
|---|---|---|---|
|F01 short write|one raw prefix retained, no reappend grant，existing abort/manager and external guardian attempt close|actual pidfd/group facts needed，no refund; counter/intent preserved|partial evidence UNKNOWN，native incomplete/UNKNOWN，admin independent/UNKNOWN|
|F02 ENOSPC|deny new observations; local notes may lack persistence，manager stop can operate independently of application file creation|actual empty/exit facts independent，no new budget|shared marker may be missing，seal not guaranteed，retention/index needs independent source|
|F03 EIO|burn uncertain slot and stop current flow，existing fallback/root manager responsibility|persistence error not equivalent to process-live/dead，ambiguous health remains|UNKNOWN，UNKNOWN/FAILED，UNKNOWN|
|F04 fsync failure|written bytes may exist but durability uncertain，do not mint a completed marker from write return|fresh exit facts required，charged credit burned|UNKNOWN at failed barrier，no guaranteed complete seal，separate raw export result|
|F05 Root Receiver death|kernel closes owned descriptors on actual exit，owner/manager guardian must be named and fresh|own death receipt needs independent producer，old state/ledger retained|unpublished data UNKNOWN，native may remain unsealed，later audit cannot be assumed available|
|F06 BC.Store unavailable|cursor/first/final private state cannot be trusted as newly saved，existing RootIPC/manager attempts may still run|actual role/group proof required，prepay or quota state not rebuilt|UNKNOWN，defer/error，independent source required|
|F07 direct parent lost|original raw waitpid may be unavailable，Receiver can observe gone targets using trusted identity/pidfd source|exit status23 remains unknown absent genuine parent witness，no reset|code/parent evidence UNKNOWN，native ready false if requiredwaitpid absent，admin cannot invent parent status|
|F08 shared marker absent|local_HALTED is process scoped，supervision/deadline/manager can attempt remaining duty|global stop must be observed，existing intent health may separately block|UNKNOWN cancellation visibility，depends on genuine CLOSED/exit proofs，keep independent outcome axes|
|F09 unlock or close-fd error|normal __exit__ ordering is known; released=true cannot be fabricated，stop_treeH reacquisition has bounded attempt deadline but kernel completion separate|actual process death eventually closes owned lock fds under kernel model，no fresh credit|lock/cleanup UNKNOWN，native requires actual preconditions，independent raw failure report|
|F10 external guardian/store lost|caller has no guaranteed post-mortem self record，remaining independent sources only if actually available|final own-exit completeness UNKNOWN，no new windows|UNKNOWN，no universal seal promise，UNKNOWN|


RootIPC的_full短写会抛异常，完整write返回以后仍需对应fsync和目录barrier。持久化成功与数据存在于内存或page cache分别取证。_HALTED是本进程状态，共享STOP失败时其他Root/UID999 actor的停止事实仍需现有marker、intent健康、监督或独立退出证据。[src/guard.py:121](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:121) [src/guard.py:82](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:82)

父进程死亡前未保存的直接waitpid不能由Receiver补造。pidfd可提供目标已经退出的受信观察，精确exit code23和native门的必要输入继续按实际原件判定。当前caller_exit_pending=true也要求独立外部最终退出来源。

预算不因故障重建，已付prefix与模糊intent保留，缺失quota/close凭据拒绝恢复发新额度。固定source包装器有次数界，所有新增恢复/重试的策略都需要重新审批，当前未增加额外actor或调用。


RESOURCE_GATE_PASS=NOT_OBTAINED，F1=UNRUN_RESOURCE_GATE，F4=UNRUN_RESOURCE_GATE。

MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE，STRICT_SEPARATION_INSTANCES=0，PASS_BOUNDED=[]，IMPLEMENTATION_GATE=CLOSED。
