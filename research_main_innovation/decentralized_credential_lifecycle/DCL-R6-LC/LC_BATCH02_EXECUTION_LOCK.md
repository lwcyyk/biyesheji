# LC：batch02精确执行锁（未授权）

2026-11-10。Material Passport：REVIEWABLE_EXECUTION_PLAN，UNAUTHORIZED。完整机器可读argv见[evidence/LC_EXECUTION_LOCK.json](evidence/LC_EXECUTION_LOCK.json)，实际Linux只读副本为/var/lib/dcl-r6/lc01/inputs/execution_lock.json。

静态manifest SHA256：`cf9442307d99f82dcec8fb542373340f9c2531ca58e9c7aa8be09edf2eab0ebd`。
执行锁SHA256：`85cd66643b0ee1f933bb035e220591ef0ce4c106e7cc71bf632702cd3b5c0be9`。

## 实际对象与后续准备

现有源码/缓存位于/var/lib/dcl-r6/lc01/src，解释器/usr/bin/python3.12，UID999/GID989，manager255.4-1ubuntu8.18、kernel6.18.33.2-microsoft-standard-WSL2。部署boot_id快照保存在命令09/49，二者不同；批次启动时必须记录新实际boot_id，并以相同标识约束整个批次，禁止复用LC时标。

下一授权才创建/var/lib/dcl-r6/batch02及inputs/reports/out，host封存根D:\毕业设计\DCL-R6-isolated-verification\batch02；只复用已冻结LC源码，不改业务文件。未来安装的新父slice为dclr6batch02.slice（复制已验证slice模板），另有dclr6batch02-stop.service及14个固定case/formal瞬态service。其全部名称/属性/argv均已列入JSON锁，当前均未创建/启动。

准备argv为JSON中的preparation_commands：仅install目录、复制slice、verify及daemon-reload。新Root许可文本与execution_authorization.json由TCB在收到实际用户许可后按真实原文hash写入；当前没有提前生成许可。所需字段、固定profile/limits及source/执行锁摘要在JSON中完整列出，原文hash只有取得真实许可后才计算。

## 两条外层执行命令

以下可执行argv均为待批准动作，当前未调用：

```text
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/lc01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch02
```

仅在C09计划故障导致首命令exit23、外部停止者已确认空组并标记AWAIT_EXPECTED_RESUME时，允许以下唯一恢复：

```text
wsl.exe --distribution Ubuntu-24.04 --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/lc01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch02 --resume
```

恢复必须保持同boot_id、T0、stop_at、deadline及counter，resume_count最多1；任何未知退出、关闭、时间/源漂移拒绝恢复。Restart=no仍适用于全部service，此项是预声明故障校准的有限续接，不产生新窗口。

## 覆盖阶段与调度锁

|顺序|真实入口/工作|锁定依据|
|---|---|---|
|启动前|root Launcher核许可/runtime/manager/源码/组；安装独立停止事件后再激活payload|launch_command、external_stop_command及固定源码|
|C00–C12|payload_commands.C00至.C12，13组完整字面量argv；逐case结束/空组后进入下一项|36项属性逐项源码提取比对；每次启动票据绑定MainPID/start_ticks/boot|
|F1基线/变异|payload_commands.FORMAL，同一Worker的原run_batch顺序；9个原mutant|五业务hash＋资源调度源码，原soft12000/8000|
|F1重放/Key|遇原trace时原独立monitor重放；固定Key表随后执行|原调用/参数保持；重放同转换关系的局限继续注明|
|F4固定夹具/参考|FORMAL继续原fixtures、DP/独立REF、压缩/重放比较|h0..2、m0..20，独立业务实现不共享|
|F4 G64/变异|原G64次序及10个原mutant|未改五业务与调度常量|
|关闭/封存|停止父树→确认空组→等待独立停止写入者结束→manifest/ZIP|ROOT/out完整来源链；异常保留不确定/失败记录|

同一FORMAL argv覆盖连续F1→F4，未开放跳过资格或任意分阶段重排的CLI。W的PID/start_ticks来自实际MainPID票据，在运行记录中保存真实内部argv；编造静态PID会破坏启动身份，因此这些内生身份由冻结源码产生，外层argv没有占位符。子探针仅C02/C03/C04固定有限子角色，预付操作数有上界。

## 资源与停止

总访问≤1,000,000；总窗口1800秒、1740秒提前停止；校准软额度100,000/300秒包含在总额内；每payload进程AS≤1GiB、父总tasks≤4。所有语义访问/参考/重放/变异及校准预付占同账，不回收模糊或未用信用。

条件内存定理仅覆盖AS4批准的普通AS计账用户驻留映射。kernel特殊VMA单列、未知PFN/IO/hugetlb标志拒绝准入；特殊区审查、初始映像覆盖、TCB/无特权并发更新、调度/挂起/终止响应假设继续显式保留。cgroup charge与RSS分别记录，C09组代次变化导致峰值计数范围变化必须注明；观测值无法冒充所有瞬时RSS峰值。

任何关键校准FAIL/INCONCLUSIVE、丢日志/短写/错误身份/额度/时间不足均关闭，资格未取得便没有业务import或模型运行。封存阶段仅剩外部TCB操作，真实时间另列；停止未确认或封存未完备保持失败/不完整状态。
