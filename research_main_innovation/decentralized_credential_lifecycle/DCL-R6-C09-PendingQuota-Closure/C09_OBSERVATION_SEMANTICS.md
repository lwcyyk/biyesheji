# 观察语义、重复轨迹与耗尽规则

## Material Passport

DCL-R6-C09-PendingQuota-Closure；PendingQuota-Closure/review-1；2026-11-16（Asia/Shanghai，承接11月15日开始的审查）；冻结源码、历史原件、序列化代数与逻辑合同的静态审查。验证方式为 ANALYZED；原生动态验收未开展。

现行代码的“观察”是[guard.py:800](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:800)调用Receiver.observe_exit；classify仅在[c09_handoff.py:276](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:276)计算一次，随后一条CHECK。poll/socket等待、已有VERIFIED的早返回和已CLOSED的早返回均不属于新分类。现行classification_count只约束成功推进HANDOFF_VERIFIED，PENDING返回时保持0。

最小轨迹族X_n：一个有效handoff，Receiver在Sender活着时取得pidfd；COMMITTED/ACK已经持久，Sender退出23；Root父进程存活，waitpid见证发布暂延。在deadline正余量内，Receiver重复“检查相同绑定/计数→witness缺→PENDING→append/fsync”。首次stage从revision3变4，此后handoff/revision4/classification_count0/resume_count0/R均不变。就绪pidfd保持就绪，PENDING分支没有清fd或else sleep，见[guard.py:781](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/guard.py:781)及[c09_handoff.py:252](D:/毕业设计/DCL-R6-isolated-verification/ra01/src/c09_handoff.py:252)。

X_257是反驳现行256政策界的具体合同调度前缀；它仅改变调度次序，原生重放0。量词限于底层表示、存储和时间环境允许的有限n。源码合同未给每轮可靠最短耗时，因此12秒窗口无法推导256上界。Linux signed64 off_t等附加假设只给极粗表示界；上一轮n=30,532的固定骨架超过32MiB示例继续作为抽象规模反例，当前未验证它在实际12秒内可达。[evidence/COUNTEREXAMPLE_FAMILY.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-BoundClosure/evidence/COUNTEREXAMPLE_FAMILY.json)、[evidence/REPRESENTATION_LIMIT_CAVEAT.json](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-BoundClosure/evidence/REPRESENTATION_LIMIT_CAVEAT.json)保持原字节。

待批v2将一次“新观察尝试”定义为：当前认证Receiver通过基本身份/终态门后，进入一次新的observe_exit检查。**在完整check_base/事实采集/分类前持久消费1个分类槽**；随后失败也烧掉该槽。异实例、过期、重复ordinal、已停止和缓存VERIFIED返回获得0个新槽。每个通过准入的不同ordinal消耗一次；相同ordinal重发只拒绝/返回既有状态，不再append，也不重新发额度。

分类额度256覆盖所有已准入尝试，包含产生PENDING、VERIFIED、FAILED、在事实构造或I/O阶段失败的尝试。因此“256个成功接纳的日志行”不能代替尝试计数。失败尝试可能0行或1个保留的部分行，行数始终受已预扣槽数约束。

第256次若仍PENDING：完整原始facts/结果先写入已预留槽并fsync，持久完成cursor并进入EXHAUSTED_FAIL_CLOSED，再保留单份固定失败摘要和请求停止。第257次获得0额度、0分类、0主日志、0重复紧急记录。若第256次得到VERIFIED，终态锁存先持久，再解锁回收；其余源码资格保持。任何有限配额都可能先于一个合法的延迟witness耗尽，合同接受资源耗尽关闭，未给成功活性保证。

正式条款和宽度示例见[C09配额v2草案](D:/毕业设计/research_main_innovation/decentralized_credential_lifecycle/DCL-R6-C09-PendingQuota-Closure/proposals/C09_PENDING_QUOTA_FINAL_PROPOSAL.json)。当前代码未接线，状态为RECORD_BOUND_CONDITIONAL / PROPOSED_NOT_EFFECTIVE。


RESOURCE_GATE_PASS=NOT_OBTAINED；F1=UNRUN_RESOURCE_GATE；F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；MR_CROSS_INSTANCE_ADMISSION=PROPOSED_NOT_EFFECTIVE；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
