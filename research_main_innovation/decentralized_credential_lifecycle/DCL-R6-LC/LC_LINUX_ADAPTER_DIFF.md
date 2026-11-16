# LC：三资源文件Linux适配

2026-11-10。Material Passport：实现仅限获准的验证基础设施；主凭据机制IMPLEMENTATION_GATE仍CLOSED、严格分离0。完整diff与源hash在[evidence/LC_DIFF_INDEX.json](evidence/LC_DIFF_INDEX.json)、[源锁](evidence/LC_SOURCE_LOCK.json)。旧v1/v2/v3完全保留。

|旧接口|Linux对应|合同与代码处理|静态检查|待动态验证|
|---|---|---|---|---|
|WinDLL/Job/_winapi/msvcrt|guard Linux标准库与外部systemd|新工作区替换资源层；原五业务API保持；Windows版归档|依赖/源码审查及py_compile|原生导入/OS接口行为|
|HardWS/Job提交与数量|RLIMIT_AS＋父/子pids4＋二级memory/swap/OOM|每次准入读取实际UID/CapEff/NoNewPrivs/软硬AS/组归属/限制与可写权限|字段/目录/36属性与执行argv对照|exec前生效、映像/特殊映射、第五task拒绝|
|FILETIME/进程handle|boot_id、start_ticks、pidfd|双读身份、W握手、Controller上下文；独立启动模型入口拒绝|调用/票据链审查|退出/PID复用/子孙与失效联动|
|QPC/Job关闭|CLOCK_BOOTTIME＋C/W＋root外部停止者＋manager|T0/1740/1800固定；未知退出关闭；C09一次同窗恢复|固定角色与时序审查|挂起/调度/终止延迟|
|Windows账锁/文件替换|线程锁＋fcntl、短写检查、journal/intent/fsync/目录fsync|统一cap；模糊额度占用；局部注入无法作用于真实总账|路径/事务顺序/错误传播审查|C05/C11真实校准|
|Windows资源probe|guard_probe C00–C12及有限子角色|内存/共享映射/任务/额度/故障/拒绝路径；观测/预期分别记录|全部mode有入口；源码/语法通过|13项均UNRUN|
|Windows run_batch资源接线|Linux准入/OUT/来源锁|原F1→F4顺序/参数/收费点；生成输入改为out；整体缺口状态显式传播|三文件diff＋五业务hash相同|语义/参考/重放/变异真实运行|

guard提供root-owned许可/票据/资格链，并验证原生事实，缺任何依赖即拒绝。普通UID可写out无法编辑Root许可；资格要求13项完整原件hash、相同boot/源锁和当前实际限制，未提供单布尔字段通行入口。TCB包括受信root管理员/内核/manager，未声称抵抗恶意TCB。

guard_probe使用已冻结的C00–C12目的。C02/C03/C04子操作先从总账预付，操作数有固定上界；C11仅在预付局部镜像账注入短写/阶段中断；C12调用生产校验函数测试错误boot/到期/关闭/根/重复初始化/正式入口。所有测试实际结果尚空，代码中的PASS分支仅用于未来真实运行。

run_batch变更只涉及资源目录、哈希定位及整体结果分类。FINISHED_WITH_GAPS避免将soft cutoff/漏变异登记成完成；模型转换、不变量、DP、独立参考和夹具构造仍在原五文件。行政JSON排序/平台路径变化不改变M.canonical或输入语义。

AS4普通映射/内核特殊区、源/依赖TOCTOU、真实文件持久性及任意代码沙箱边界仍需明确审查。当前源码为静态候选，编译通过尚无导入/运行正确性认证。
