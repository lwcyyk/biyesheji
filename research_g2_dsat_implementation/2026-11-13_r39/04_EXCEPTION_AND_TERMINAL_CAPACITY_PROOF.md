# 异常、终止与提交顺序

原R38共56类异常全部按原ID保留，本轮增加X57，矩阵共57类。全部失败路径的完整必需字节上界仍为UNPROVEN。

保守调用图需求上包络为329+O+C<=8521：包含逐项272、snapshot对16、wrapper16、库存超限1及原主异常/清理/发布/entry记录。结合单failfast回调图可收窄至8454，但两者都没有被称为可达到最大值。实际进入journal构造的尝试guard为8320，门前拒绝/关闭后的调用另属有限调用图，不等于已写记录。

普通write/短写/flush/fsync失败保持全请求扣费；实际持久化未知为UNKNOWN，保留charge-confirmed上界。用户态缓冲0、额外磁盘临时副本0。失败receipt、核心JSON与journal允许共存，未假定不同故障必然互斥。

## X57：已知未write的失败也poison

输入族为已匹配原fixtures/源码并到达首个A01真实PASS、且该原结果可适配工作journal剩余额度的前缀。可允许的调度延迟发生于observe_result已保存原结果之后、commit检查时间之前；整个进程/看门狗调度允许主线程先检查截止，interrupt尚未递交。前缀本身及原结果值不变。

恢复于t=90.001：reserve_bytes按工作90截止拒绝，尚无新write/debit，delta(write_attempted)=0。commit_case_record明确标为RESULT_PERSISTENCE_FAILED，却仍无条件poison原健康journal。进入terminal后，原计划CASE_EVIDENCE/最终检查点被EVIDENCE_STREAM_POISONED先行拒绝，尽管尚有约24.999秒及预留65KiB。

令已确认journal前缀P，原本可适配的结果行X，P+X<=983040。相同结果payload移到terminal，phase A1→TERMINAL增加6B，ISO时间长度最多增7B，其他固定长度不变，故最多X+13：

`P+(X+13)<=983053<1048576`。

其他12文件即使取全部份额也为951591B，故这种单记录提交的全局包络<=1934644B，距2MiB至少162508B。此反模型的global overflow=0，问题为现有状态机不能使用足够的剩余预留；没有用压缩率假设。

惰性原结果样例按实际codec结构的终止行890B，仅用于独立序列化算术，seq/哈希样值未被宣称是某真实466行前缀。该模型严格保留“已达到且原记录可适配”的前提，完整冻结运行的输入级可达性/全局尺寸超额反例未在本轮证明。因此R39_COUNTEREXAMPLE_FOUND=false，local countermodel=true。

## 时间模型

新用例准入90、terminal读写115、显式关闭准入120保持。新读取/metadata有前后门；已经确认的旧结果不会被迟返时间门撤销。当前正在执行的测试/原生I/O仍可能晚返回，cooperative watchdog并非硬实时抢占。

可靠存储本身不足以推出限时全部完成，还需要可检查的执行/调度/I/O延迟前提。持续拒写只支持安全拒绝和确认前缀；本轮没有把任意磁盘故障下完整持久化列为已证。

X57最小修复提案只区分“已证无payloadwrite”的拒绝与“partial/uncertain write/身份冲突”，保持所有后者poison；不自动重试不确定写，不扩大时间/字节，不删原失败事实。
