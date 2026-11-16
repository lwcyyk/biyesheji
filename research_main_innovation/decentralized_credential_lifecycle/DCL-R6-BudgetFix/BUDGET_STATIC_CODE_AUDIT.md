# 静态代码安全审查
Material Passport：BF-static-1；单会话人工源代码审阅及文本一致性检查；动态import、动态探针、故障注入、F1/F4均0。独立审阅者/独立运行检查本轮均未建立。

## 审查范围
从正确batch02/FROZEN_LC原件到lc03源代码逐文件diff；guard.py与guard_probe.py有变化，run_batch.py与五业务文件字节相同。重点函数：guard._counter_lock、_task_contract、_reserve、ExactReservation.dispatch_once、claim_exact、LocalCredits.visit、Budget.visit/reserve_exact，以及guard_probe.prepaid_child/child。具体行号以源码锁版本为准。

|项目|结论|证据与限制|
|---|---|---|
|接口签名|PASS_STATIC|reserve_exact(task_id,N)、dispatch_once()、claim_exact(task_id,N,lease_id)、LocalCredits.visit()调用点一致；child argv/parser新增两身份参数|
|N来源/覆盖|PASS_STATIC|合同hash+页4096+源码公式三方核对，未知task/N拒绝；证明见C02精化|
|全局原子性|CONDITIONAL_PASS|余额+查重+持久事实在同一counter锁中；依赖Linuxflock、相同inode与合作writer|
|全局单调/限额|PASS_STATIC|检查used+n后才pwrite；没有减账/退款；cal100000、B1000000|
|局部上限|PASS_STATIC|先检查used>=N，再递增，随后调用点语义操作；fork身份拒绝|
|幂等事实|PASS_STATIC|task SHA路径+不可变request+半开区间+lease材料；重复created=False无法dispatch|
|一次认领|CONDITIONAL_PASS|UNCLAIMED→CLAIMED在同锁持久化，executor/parent绑定；依赖持久化与固定代码|
|崩溃分支|CONDITIONAL_PASS|所有持久缝隙无提前grant，未知状态关批；S1–S9动态证据仍缺|
|短写/fsync失败|CONDITIONAL_PASS|_full/pwrite检查，真实全局错误halt并请求STOP；局部C11隔离；真实错误传播待测|
|批/boot/源码|PASS_STATIC|SOURCE唯一lc03、manifest/runtime/ticket/request hash；新ROOTS为lc03/batch03，授权只接受batch03|
|deadline/stop|CONDITIONAL_PASS|grant/claim/debit逐点检查，越期预留烧掉；严格即时停止及OS调度延迟未认证|
|普通计费兼容|PASS_STATIC|Budget.visit仍全局先付，镜像失败也不会退款；run_batch收费点保持|
|主机/Linux一致|PASS_STATIC|八source与八pyc摘要冻结；最终guard通过order09编译|
|历史与业务|PASS_STATIC|五业务字节一致；历史账与失败原件保持；误副本只读|
|未来命令|PASS_STATIC|14 payload、stop/launch/resume及准备argv静态锁定；当前执行授权缺失，无法转为运行资格|

## 发现及处理
F-01 原COMMITTED复用PREP时标：已在新源中使用counter sync之后的新stamp，最终完成另记event。
F-02 范围重复派发：加入created/once/owner与持久claim；重复请求返回事实，无新完整cursor。
F-03 恢复owner变更会妨碍幂等事实：请求材料去除可变owner，原owner留在不可变事实与lease材料；恢复读取与执行资格分开。
F-04 构造器误建信用：内部工厂token+CLAIMED/executor检查；该防误用措施受固定代码TCB前提约束。
F-05 父PID复用：pid/start_ticks/boot双检围绕pidfd_open。
F-06 源目录与历史批名残留：仅SOURCE=/var/lib/dcl-r6/lc03/src，batch03授权文本及单位名统一。
F-07 静态“7同步”简化：按真实新增registry/claim修正为9+2=11。
F-08 C11局部注入影响全局可用性：局部镜像注入保留残片且仅该镜像毒化；真实Budget.visit全局/镜像异常仍halt。
F-09 记录器/复制行政错误：原事件、未捕获退出和order08旧稿编译明确保留，order09绑定最终guard，不把旧稿编译当最终证据。

## 未决前提
当前账目录归dcl-r6可写；安全模型面对固定可信payload。任意恶意同UID writer、root编辑、文件系统回滚、registry丢失/损坏、fsync合同之外的宿主故障均需额外隔离/存储证据。结束时R与不完整A的等式无法由遥测单独重建，采用保守占用。AS4普通映射条件、特殊内核VMA单列、绝对终止延迟、C02低AS遥测可用性保留未决。上述条件随版本锁一并交付，静态PASS的范围据此界定。
