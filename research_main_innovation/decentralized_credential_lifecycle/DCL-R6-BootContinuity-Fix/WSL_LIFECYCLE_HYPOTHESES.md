# WSL生命周期假设及证据边界

Material Passport：BootContinuity-static-1/r4；host离线静态修复；2026-11-11；WSL查询/目标执行0。

**BOOT_CHANGE_CAUSE_UNRESOLVED**。三个不同boot_id证明发生了运行代次变化，当前记录不足以定位触发者。

|假设|已知证据|当前裁决/反证责任|
|---|---|---|
|H1 空闲生命周期|多次独立WSL exec、命令间隙、没有贯穿Linux进程的记录；命令6/16耗时较长|可行解释，尚待证；冷启动样式耗时不足以确证|
|H2 宿主或外部程序|已记录19条argv中没有--shutdown/--terminate；宿主休眠/服务重启/内核事件日志缺失|UNRESOLVED；无法排除未记录的外部事件|
|H3 编排跨实例|命令2/15/16观测不同boot；每条wsl调用独立退出，Host复用base结果直到最终same_boot检查|成立于观测边界；最终防线成功拒绝，未将旧动态资格授予Launcher|

Microsoft的2022年官方说明写明“systemd services will NOT keep your WSL instance alive”。这支持“PID1/systemd服务存在不足以证明实例持续存活”的一般判断；该文不能证明本机此次自动退出。[官方说明](https://devblogs.microsoft.com/commandline/systemd-support-is-now-available-in-wsl/)

LC历史裁决也记录过准备前后boot不同，且明确静态配置持久性与运行身份分列：[LC_FINAL_DECISION.md](<../DCL-R6-LC/LC_FINAL_DECISION.md>)。batch06当前事实为最终拒绝、Launcher0、T0/R=null；H3并非一次已经发生的越权启动。

本轮没有执行新的WSL查询、事件日志读取或诊断命令。WSL版本、宿主策略、空闲设置及当前boot均保持未查询状态；已知Ubuntu24.04.5、Python3.12.3、systemd255.4和kernel6.18.33.2是历史观测/未来合同。需要定位具体触发源时，另行申请明确的只读平台诊断范围。

[公开来源元数据](evidence/PRIMARY_SOURCES.json)、[原始时序](BOOT_CHANGE_TIMELINE.md)、[首次失败原件](../DCL-R6-batch06/evidence/FIRST_FAILURE.json)。
