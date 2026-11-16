# 选定架构：AS4-PAYLOAD/1 条件部署方案

2026-11-10。Material Passport：最小执行架构，STATIC_DESIGN_ONLY。选择 C，停止追加同类 Windows guard 修订；原 WS4 合同未闭合，替代合同未批准，平台尚未就绪。

## 1. 拓扑与角色

```text
Windows/WSL2/Linux kernel                      [外部 TCB]
  外部受信 Launcher ── systemd 系统 manager   [外部 TCB]
       │                  ├─ 绝对停止事件      [外部 TCB]
       │                  └─ pre-exec helper  [外部 TCB]
       └─ 单次批次身份         │ exec 成功
                     单批父 slice：pids.max=4（含全部子单位）
                       单个活跃 service（各自也设 TasksMax=4）
                       C：Controller＋顺序 Worker＋预算＋日志
                         ├─ C 监督线程（也占 task）
                         └─ W：独立 Watchdog
                       所有允许/意外子孙同组、继承 AS
```

payload 每进程 AS soft=hard=1,073,741,824 字节，最多 4 个任务，数学保守驻留和≤4 GiB 的前提见 [STRICT_MEMORY_BOUND_PROOF](STRICT_MEMORY_BOUND_PROOF.md)。C/W 两个普通 Python 进程、一个监督线程预期占 3 个 task；第四槽供明确校准，正式业务禁额外创建。任务与进程的差别已纳入上界。

破坏性校准需要结束整个 service，因此父 slice 持续覆盖同批所有子单位，防止多个 service 各获 4 个任务而突破合成界。校准 case 按固定清单逐个激活，前一单位确认空组后才激活下一项；所有 case 共用同一账/T0/deadline。预先声明的故障注入只关闭该 case；预期外失败关闭整个批次。没有 systemd 自动重启。正式 F1/F4 在最后一个 service 的同一 Worker 内顺序执行。

|职责|承担者|计量/证明责任|
|---|---|---|
|受信 Launcher|固定本地 systemd 管理入口|目标启动前属性/停止源、一次性身份；外部 TCB|
|Controller/Worker|C 一个 native Linux Python|首目标映像入口即受限，按 F1→F4 顺序|
|Watchdog|W 同组子进程|AS 继承、独立 deadline/心跳、C 稳定身份终止|
|预算服务|C 内同步组件|全局锁/持久预留/短写即停，所有校准/变异/参考/重放共享|
|日志组件|C 内组件，W 独立最小事件日志|同组内开销；同步失败导致关闭|
|异常/树清理|C/W＋预先武装的 manager 停止源|KillMode=control-group、退出确认、禁止自动重启|
|峰值/时间|C/W 观测＋manager 组记录|RSS 与 charged_peak 分列，boot_id/CLOCK_BOOTTIME/宿主时间对照|
|批次封存|所有 payload 退出后的外部管理步骤|原始字节、manifest/ZIP/hash；封存耗时单列，不追加模型工作|

## 2. 单位属性合同（非配置实现）

计划使用系统 service 的 Type=exec，直接 ExecStart 固定 native Python，禁止 shell/ExecStartPre/ExecStop 辅助角色；Restart=no、RemainAfterExit=no、Delegate=no。LimitAS=1073741824:1073741824，TasksMax=4，TasksAccounting/MemoryAccounting 打开。MemoryMax=4294967296、MemorySwapMax=0 作为额外 charge/交换保护，OOMPolicy=kill、OOMScoreAdjust=0、KillMode=control-group、KillSignal=SIGKILL、SendSIGKILL=yes。LimitCORE=0，core 路径和系统 coredump 行为需独立核对。

Type=exec 避开 oneshot 的 RuntimeMaxSec 无效情形；RuntimeMaxSec 仅作第二停止源，另安装绑定 T0 的绝对停止事件；TimeoutStartSec/TimeoutStopSec 明确有限值，RuntimeRandomizedExtraSec=0。所有属性依实际 systemd 版本解析与读回；目前只核验官方 v255 文档，并未观察本机版本。未知/忽略属性均阻止准入。

专用非特权 UID、空 capabilities、NoNewPrivileges、只读模型/runtime、单一账写入目录，以及阻断组管理/外部代理/Windows interop 的规则属于平台冻结清单。这里没有写出可加载 service 配置、Launcher 或 seccomp 实现；实现门和本轮范围均保持。

## 3. 文件与跨平台复用

八个历史程序及 v1/v2/v3 全保留。五个业务文件 `f1_model.py`、`f1_check.py`、`f4_dp.py`、`f4_reference.py`、`compare.py` 必须字节一致。它们并非全部平台无关：f1_check 导入 guard.LimitReached，compare 导入 guard.ROOT/write/digest；run_batch 和 guard 当前为 Windows 路径/资源实现，v3 还有主动拒绝入口。因此把现有 v3 直接移到 Linux 无法得到可运行资格。

未来若获匹配授权，仅在新批次资源三文件/启动接入实现 Linux 兼容 API；保持五文件 hash 和 F1/F4 调用顺序/参数/soft limit/收费点。旧三个资源程序保存原件；派生接入单独摘要、diff、审查，称为平台适配，避免继续无限编号 guard 版本。当前新增验证/适配程序 0。

建议 Linux 本地证据位置 `/var/lib/dcl-r6/batch02`，host 封存目标 `D:\毕业设计\DCL-R6-isolated-verification\batch02`，均尚未创建。Linux 原生文件系统的锁/fsync/rename 语义优先，DrvFS 直接活账须另行证明。外部复制保留原文件字节与摘要，禁止链接回旧 batch01 可写位置。

## 4. 独立检查与恢复路径

F1 保留模型/独立监视器模块，独立 ghost 来源账、候选 C/D、旧权利迟到 IO 和八个不变量。F4 DP 与参考保留各自的后继/终态/策略解释路径；共享冻结输入与统一访问预算。一个 Worker 顺序调用这些模块保留业务语义独立性，同时共享解释器/运行时故障域。若未来研究要求进程级隔离，需重新冻结拓扑和资源界。

先完整资格校准，再 F1 基线/9 个 mutant/独立重放/Key 表，再 F4 固定夹具＋G64＋变异。原 dispatcher 的具体输入参数、12,000/8,000 soft visit、m=0..20、h=0,1,2 均锁定；源码与规格覆盖差异继续列 ABSTRACTION_GAP/NOT_EXERCISED。单个 soft cutoff 产生 INCONCLUSIVE_LIMIT，无法因任务正常返回即授全域通过。

当前方案完成可评审静态角色/失败流程；实际平台配置、入口映像、权限封闭、适配接线、全命令摘要和动态证据仍缺。故 E3=STATIC_DESIGN_COMPLETE_CONDITIONAL，E4=PARTIAL_UNAUTHORIZED，RESOURCE_GATE 保持关闭。
