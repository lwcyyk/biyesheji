# 精确批量预留语义
Material Passport：DCL-R6-BudgetFix / BF-static-1；静态资源设施修复；证据、条件推导及动态未决项分别登记。来源为用户专项授权及 batch02/Perf 冻结原件。主凭据机制严格分离实例仍为 0，IMPLEMENTATION_GATE=CLOSED。本工程采用既有范围预留方法，原创性主张保持关闭。

## 合同与计数
reserve_exact(task_id,N) 仅接受 child_contracts.json 中三个固定合同。N 是计费操作尝试的最大数量，覆盖成功、失败与提前退出分支。每个 case 的入口 Budget.visit() 另计一个信用。计费范围延续旧代码：分配尝试、显式页触碰、创建尝试；JSON、锁、遥测及管理操作没有新增“业务访问”收费点。

健康、完整且口径一致时，R=A+U，Q=B-R，0≤A≤R≤B；单任务 A_i≤N_i。R 是持久占用，A 包含已经发生的计费尝试，U 包含全部未使用且持续占用的信用。局部 debited 数 D 在语义操作前增长，故观察到的 A_obs≤D≤N。扣减后中断会产生 D-A_obs 间隙，该间隙保持占用。遥测缺失时只保留保守上界，不填造 A。

全局 B=1,000,000；校准累计 R≤100,000。全批 T0、boot_id、T0+1740 提前停及 T0+1800 总墙钟保持，校准共同截止 T0+300。各次申请在同一全局锁内检查 used+N≤min(B,phase_cap)，额度不足时整笔拒绝。无舍入、无自动退款；单任务闲置占用最大 N。

## 身份与发放
1. manifest/授权/票据/内核条件验证；SOURCE 唯一为 /var/lib/dcl-r6/lc03/src。
2. task_id、N、page=4096、合同哈希、源码manifest、batch03、boot_id、T0 形成不可变请求。
3. 全局 RLock 与 flock 串行化余额、registry、claim。PREPARED→counter→journal→registry→最终COMMITTED 的持久屏障全部完成后再派发。
4. ExactReservation 由内部工厂创建，created=True、原 owner(pid/start_ticks/boot)、内存 once 同时满足才可 dispatch_once。
5. 子进程核对真实父进程与票据，在同一全局锁内将 UNCLAIMED 原子持久更新为 CLAIMED，绑定 executor 身份。完成认领后才构造 LocalCredits。
6. 每次局部 visit 在锁内验证执行者、父 pidfd、批次/boot/停止/期限与余额，先扣减再操作。第 N+1 次在操作前拒绝。

局部计数器在内存中维护，校验仍读取状态文件、进程身份、时钟及 pidfd；每次局部扣减的真实成本待测。固定 Python 源码属于 TCB；内部 mint token 防止误用，安全论证范围为受审固定程序及内核隔离。相同 UID 的任意恶意 Python 能读写输出账与访问模块内部对象，该威胁模型须由独立权限隔离设计处理。

## 重复、恢复与格式
task_id 映射到 SHA-256 文件名；事实含请求、半开信用区间 [lo,hi)、owner、lease_id、delivery_state、executor。相同请求在健康、活动、账一致的条件下返回原事实 created=False；该对象 dispatch_once 被拒绝。不同请求拒绝。恢复不会补发原 N；已认领信用重启后保持烧掉。请求摘要排除可变 controller owner；原 owner 单独锁定，便于恢复时读取原事实。

新预算协议 EXACT-RANGE/1；24 字节 counter = BRNGv001 + 两个 little-endian uint64(used,cap)。intent 必须带新协议且为 COMMITTED、after==used、cap 匹配。旧格式直接阻断；batch02 保持原协议与原字节，迁移次数 0。PREPARED/短写/同步异常采用毒化和整批停止，原残片保留。模糊情况下 R_cons 取已持久事实及可能生效事务的保守占用，满足实际执行被覆盖；停止后 Q_operational=0，无法用普通健康账等式推算可再发余额。

## 可证伪的工程预测
输入族为原固定 C02 循环，页为4KiB，最大 N=32896；指标为信用预留/认领路径的持久同步调用机会数。旧冻结逐信用通用预付为7N，新实现为范围事务9加认领2，共11；预测此项随N从线性降至常数。当前最强通用方法包含成熟的范围租约/escrow批量方法，它同样可达常数同步；本工程据此保持严格原创性分离为0。该预测仅比较本项目冻结旧路径与修复路径，墙钟、资源资格和通用方法下界均待各自证据。

详见[崩溃证明](BUDGET_CRASH_SAFETY_PROOF.md)、[N精化](C02_RESERVATION_REFINEMENT.md)及[源码锁](SOURCE_AND_INPUT_LOCK.md)。
