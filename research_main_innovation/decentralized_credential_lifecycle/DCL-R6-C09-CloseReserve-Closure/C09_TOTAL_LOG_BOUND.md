# 主日志、关闭和其他C09对象的无重复组合

## Material Passport

DCL-R6-C09-CloseReserve-Closure；CloseReserve-Closure/review-1；2026-11-16（Asia/Shanghai）；只读源码、冻结输入、字节代数和抽象轨迹审查。结论类型ANALYZED；运行实例、原生故障和模型检查均未启动。

345148是待批主日志预留，N_main≤263依赖256次尝试、七个生命周期/ACK类别位、持久预扣/完成和终态锁存。冻结代码尚未实施这些约束；继承[C09_RECORD_COUNT_BOUND_PROOF.md](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/C09_RECORD_COUNT_BOUND_PROOF.md)和[C09_TOTAL_BYTE_BOUND_PROOF.md](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/C09_TOTAL_BYTE_BOUND_PROOF.md)的条件范围。

以真实路径定义互不重叠的三个集合：M为c09_events.jsonl；C为选定完整关闭原件及其实际失败staging；O为C09其他原件及未计入C的配额元数据。令B(X)按唯一路径/实际保留版本求和：

\[B_{C09,total}=B(M)+B(C)+B(O)\le345148+B_{close,max}+B_{other,max}.\]

|对象|组合归属|计量注意|
|---|---|---|
|PENDING/CHECK/六stage/ACK|M|CHECK可能含FAILED或在途晚于STOP，均消耗原主槽；无额外HANDOFF_FAILED生产者|
|STOP/CLOSED、mr_first、mr_close_state、attempts、stop_event/result、关闭staging|C|STOP/CLOSED独立于主行；ABORTING/final同一文件，attempts多行一个文件|
|quota摘要/cursor/各自staging|按最终划分放C或O一次|旧350166已经包含main、这些对象、两标记及声明staging；不能再完整叠加345148或完整C|
|handoff state、commit/resources、exit_witness、ticket/ready及源/输入授权|O或既有raw族|native/admin读取和复制原件；未通过读取就绪/证明的字段仍有字节责任|
|global counter/intent/journal|既有全局raw族|预算快照只是hash/size映射，不再复制整份journal到MR记录；原journal本身仍保留一次|
|native manifest/ZIP|独立native派生层|哈希/归档会再读取M/C/O；数据流工作量另计|
|admin audit/stdout/快照/manifest/ZIP/最终收据|独立行政层|原件复制和包内nativeZIP产生真实新增字节，不能因内容重现而省略|

主日志不承担STOP/CLOSED、ABORTING、回收结果、MR关闭、父waitpid或native/admin的空间责任。旧局部350166的独立差额5018继续保留其原声明作用域；本轮新增237/260/1223等schema子界没有替完整关闭池选定总cap。

原始交接安全仍依赖真实ACK/commit、身份/boot/预算绑定、pidfd与直接父waitpid、一次验证/恢复以及当前监督。额度耗尽只给资源失败停止，无法把延迟witness变成VERIFIED。父见证缺失、raw部分行、角色退出未证或任意必要UNKNOWN均保持真实失败强度。主日志有界本身不能推出整个交接最终成功。

最终B_close、B_other及B_C09,total数值均为UNRESOLVED，见[CLOSE_TOTAL_FORMULA.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-CloseReserve-Closure/evidence/CLOSE_TOTAL_FORMULA.json)。既有off_t64表示界只用于区分表示空间与资源合同，没有满足32MiB或1GiB准入的作用。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；PASS_BOUNDED=[]；IMPLEMENTATION_GATE=CLOSED。
