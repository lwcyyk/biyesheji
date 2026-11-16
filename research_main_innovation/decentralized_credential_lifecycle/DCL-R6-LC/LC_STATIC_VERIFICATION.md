# LC：静态检查与边界

2026-11-10。Material Passport：STATIC_ONLY。原始命令、退出及双流见[evidence/LC_COMMAND_RESULTS.json](evidence/LC_COMMAND_RESULTS.json)。编译只处理目标语法/字节码，没有执行目标模块正文。

|检查|实际结果|强度|
|---|---|---|
|Python路径/版本/SHA|3.12.3/e50d…150f一致|运行时身份复核|
|八文件编译|首轮八文件及后续改动guard编译均exit0；最终版本通过|STATIC_SYNTAX_PASS|
|业务复制|v2/v3/host LC/Linux LC五文件SHA相同|SOURCE_HASH_MATCH|
|资源依赖|Linux标准库；Windows-only接口移除；guard兼容符号/先准入后业务import保留|静态依赖/对应审查|
|单位verify|exit0，无配置警告|STATIC_CONFIGURATION_PASS|
|加载/属性|授权daemon-reload一次；单位inactive/dead、MainPID0；36项候选属性与参数静态对照|配置读回，执行限制待验|
|权限|UID999/GID989、src/inputs/cache root-owned只读、out999:989/0700|实际模式/属主审查|
|命令锁|14组payload argv由源码字面量受限提取与冻结JSON对照，无差异；无目标模块执行|PASS_STATIC|
|输入/快照|原计划及1224代码文件树、31关键运行文件、16源/缓存条目冻结|文件快照，不是完整动态解析证明|

静态迭代中补齐了原生二级限制检查、Root记录group989、W命令记录、退出原因分类、关闭/封存屏障等资源接线；每次新改源码均重新编译，最终以源锁为准，旧Windows原件未改。UNC无法跟随的三个POSIX文件链接，通过Linuxreadlink/stat/sha补齐，原诊断保留。

已审的拒绝链包括：错误/缺失许可、源码/runtime漂移、错误boot/时间、组/AS/权限不符、W死亡、账短写/模糊意图及资格原件不全。该审查没有实际执行这些分支，潜在运行/并发/API问题须由下一阶段完整校准发现；关键FAIL/INCONCLUSIVE阻止正式模型。

当前六类结果：STATIC_SYNTAX_PASS、STATIC_CONFIGURATION_PASS、SOURCE_HASH_MATCH、RUNTIME_COMPATIBILITY_UNVERIFIED、RESOURCE_ENFORCEMENT_UNVERIFIED、MODEL_CHECK_UNRUN。没有RESOURCE_GATE_PASS、F1/F4结果或一般协议机器证明。

AS4条件定理仍以全部普通映射AS覆盖、任务封闭、kernel/TCB与调度/终止假设为前提。LinuxRSS/cgroup charge/WindowsWS字段区别保留，观察快照无法认证所有瞬时峰值。特殊kernel映射需独立审查并在新授权中明确范围，当前未将其默认为原WS指标通过。
