# batch07真实启动连续性证据与边界

Material Passport：DCL-R6-batch07；BootContinuity-static-1/r4；真实启动后首次失败；2026-11-11；复跑0。

预检至exec/Guard接入的同boot、同PID/starttime前缀已取得真实证据；服务阶段首次失败，完整服务准入未通过。

|检查项|实际结果|
|---|---|
|单会话预检|实际执行；15条内部预检/准备命令均exit0|
|当前boot|060a08fc-fceb-48ff-a264-50c34312f97a|
|exec前后Owner|PID828/start_ticks7252，两侧完全一致|
|同进程exec|ACTIVATION_REQUESTED_ONLY后仍由相同身份记录ENTRY_VERIFIED；新Guard traceback进一步见证接入|
|sealed凭据|实际生成；seals=15，SHA-256 4d6dcbb61c3f8e31ccfb8a2f530c441f1b74546b8839408deaf0c741a4f81422|
|一次认领|initial_entered=true，resume_issued=false；本次消费一次，重复拒绝专项测试UNRUN|
|Root子进程|PID886/start_ticks7372，boot一致|
|初始入口复核|ENTRY_VERIFIED；20份Linux源码native3.12 compile路径已完成，当前静态对象hash重新校验|
|服务内完整复核|C00发生BC_SERVICE_IDENTITY_OR_LIMITS，BOOT_START未发布|
|Preflight.boot=Service.boot完整证书|NOT_VERIFIED_SERVICE；不以Root入口证据替代服务通过|
|整体结论|OBSERVED_SAME_BOOT_EXEC_PREFIX；FAIL_SERVICE_CONFIRMATION|

首次PREFLIGHT_BEGIN=72.567562110，ENTRY_VERIFIED事件=73.720548237，同BOOTTIME前缀耗时1.152986127秒。ticket issued=73.432524364、expires=83.432524625；Root私有entry记录在73.713268609，早于失效点。120秒预检期限为192.567445037。

memfd封印、设备/inode与摘要验证由实际read_capability路径完成后才记录ENTRY_VERIFIED。普通日志仅包含摘要和验证状态；原ticket/认领只在LinuxRoot:Root/0600的private目录，原始私有证据按同一private相对路径归档，不把nonce输出到本报告。memfd与持锁fd随Owner退出结束，持久认领及CLOSED保留。

事后导出观察boot=786c0971-c8ca-4a10-8c0d-a62817ae0a17，用于清理/文件观察；它不参与活动资格，也未被写回旧票据。活动34条BC日志的Owner均为上述同一身份。当前没有观察到batch06式的活动预检跨boot；尚无物理重启/重复认领通过证据。

[脱敏启动摘要](evidence/BOOT_CONTINUITY_ACTUAL.json)、[实际entry文件](<../../../DCL-R6-isolated-verification/batch07/native_snapshot/inputs/root_private/boot/entry_initial.json>)、[原始活动日志](evidence/windows_entry.stdout.raw)、[首次失败](BATCH07_COUNTEREXAMPLES.md)。
