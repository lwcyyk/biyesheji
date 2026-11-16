# batch04授权与冻结核验

Material Passport：BF-static-2/r4 / export_lock_revision=1；2026-11-11；真实动态执行，首次关键失败后关闭。

本次授权原文保存在evidence/TASK_REQUEST.txt，SHA-256=a452f87ca27c570cbe08f31b931e8377c0671072dcf622fea7a791e518df1c91。scope=CALIBRATE_S1S9_THEN_F1_F4，test_mode=RANGE_ONLY/1；C/S/证据与门检查全部通过后自动F1→F4已获明确许可。

|冻结项|实际摘要|
|---|---|
|manifest|4c488e52869d58b14b59721c0cdbd3a068a5fcda256891256c2c9f3e649bf103|
|execution_lock|aa9c4a84451a1c5053eb9dd6850254fd7efc5c560889dd017540cc827f5c0e9b|
|safety_contract|358cf611aabdc71499723056d51765edc47084b9b7a88102c72a28ab0b1e178a|
|Python3.12.3|e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f|

host30项、Linux1274唯一路径（22源缓存、输入、32关键文件、1224树锁及旧单位重叠去重）核验通过。五业务、runner及原探针仍用冻结字节。runtime为Ubuntu24.04.5、kernel6.18.33.2-microsoft-standard-WSL2/x86_64、systemd255.4-1ubuntu8.18、UID999/GID989、cgroup2fs、4096页。未知运行实体为空；唯一既有失败为mnt-e.mount。

按锁安装batch04目录及slice，verify和daemon-reload成功，slice inactive时TasksMax4、MemoryMax4GiB、Delegate=no；源/输入root:root0755/0644，新授权root:9890640，out为999:9890700。运行中实际约束由各ticket/startup/kernel/probe另行保存。

初次预检boot4a2309dd…后，T0前观察boot99fbdfbd-f0b9-4cf2-8914-0d71867b6138；完成全文件、内核、manager和身份刷新后才初始化唯一窗口。本会话未发出发行版重启/关闭命令。后续观察boota896a9f7…发生在运行关闭之后；其manager默认属性单列，不充当运行时属性。

首次入口为命令29，原argv逐字匹配执行锁，Linux退出23属于预定C09退出。外部停止器随后错误关闭；恢复准入发现CLOSED，未调用resume。执行收据、许可原文及所有实际命令双流均保留。程序、输入和判据未改，batch05未创建。
