# 资源准入、未初始化预算与环境漂移

Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。

**TR-A8=FAIL：完整运行时摘要合同未满足，正式资源窗口未建立。**

|指标|实际值|
|---|---|
|计划完成/阶段A硬界|2588 / 3649；完整硬67730≤100000，静态证明已核齐|
|实际T0/deadline/stop_at/R|全部null，counter/journal未创建|
|PT/PF/TR/变异/模型运行|全部0；没有给未初始化账填0|
|active host|0.259492000秒，原生exit125|
|自动post|0.241365600秒，exit0|
|全部host入口|0.873294800秒|
|Payload资源|无工作负载；峰RSS/charged memory/tasks不适用，Root高水位未测|
|原合同|1000000/1800、校准100000/300、预T0120、提前1740、AS1GiB、父TasksMax4均未放宽|

只读审计核对1241个冻结运行时文件，3项不同，源/输入0失配。当前Python3.12.3、kernel/systemd/UID/GID基础字段仍匹配；加载器/libc/libm变化足以拒绝整个闭包，基础字段相同不能取代字节资格。

当前包查询libc6及libc-bin均2.39-0ubuntu8.12。dpkg.log原文记录2026-11-13 13:26:52–53从2.39-0ubuntu8.9升级至8.12，日志时区没有单列，按原样保存；本轮只做读取/hash/包元数据查询，没有安装、降级、更新源锁或重启。辅助/lib路径包归属查询未命中，完整版本和升级日志独立保留。

新环境下映射、启动、资源与协议前提尚未重新审查。没有进入完整300秒校准，性能可行性仍UNRESOLVED。

[准入预算证明](evidence/RESOURCE_ADMISSION_PROOF.json) · [全部实际差异与包日志](evidence/RUNTIME_DRIFT_AUDIT.json) · [3份现行二进制导出锁](evidence/DRIFTED_RUNTIME_EXPORT_LOCK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。
