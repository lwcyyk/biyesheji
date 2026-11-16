# 分层证据、静态缓存与失效合同

Material Passport：BootContinuity-static-1/r4；host离线静态修复；2026-11-11；WSL查询/目标执行0。

|对象|层|适用条件|失效|
|---|---|---|---|
|源/输入/执行锁内容摘要|A|实际当前对象、规则版本、来源与锁匹配时可复用既有陈述；当前字节仍重新hash|文件变更、规则/锁变化失效|
|授权原文/静态许可范围|A|仅复用原文/摘要与已批准范围的事实；不沿用旧运行资格|原文/权限范围/版本变化停止|
|Python版本合同与单位配置内容|A|版本要求和静态配置陈述；当前解释器/单位状态另查|对象漂移停止|
|当前boot/PID/start_ticks/UID/GID/cgroup|B|每次启动同一会话fresh读取|任一身份或代次变化失效|
|systemd版本/manager失败/活动属性|B|入口及激活接入核查，服务启动后再核状态|属性/来源不确定拒绝|
|临时目录/IPC/Root/Launcher/Receiver及成员|B|当前实例对象、实际元数据/ACL和稳定身份|进程退出、对象/归属变化失效|
|预检ticket/memfd/一次认领|B|当前boot和同一Owner PID/start_ticks/锁fd，初始10秒有效|旧boot/新进程/重用/缺cap拒绝|
|C/S/门及RESOURCE_GATE_PASS|运行B|全套当前boot、T0、预算和当前身份联合核验|重启、关闭、漂移后失效，保留原始失败证据|

缓存格式固定`rule_version=BC-A/1`、对象路径与摘要、原始来源引用、当前执行锁、source_mode及复用条件。[boot_continuity.py:153 artifact_check](<../../../DCL-R6-isolated-verification/bc01/src/boot_continuity.py>)生成此层陈述；该版始终重新读取当前source/runtime/绑定输入摘要，不用静态缓存跳过当前文件验证。可以复用既有语法/来源的陈述身份，不能复用旧进程、单位或资源资格。

Layer B由同一Linux受信进程依次采集，第一次boot作为资格周期锚。每个命令前后和hash块之间核boot及120秒预检期限；最终快照覆盖当前boot、Root身份/cgroup、账户、残留、当前manager与父slice属性。Root入口在exec后再采集，子scheduler及实际C00/C10服务再核当前身份。

预检结果使用PREFLIGHT_QUALIFIED、ENTRY_VERIFIED、ACTUAL_SERVICE_CONFIRMED等不同状态，RESOURCE_GATE_PASS仅留给完整原资源资格门。新boot导致旧动态资格不可复用；源/输入/授权漂移直接停止，禁止重写旧boot或时间戳。持久认领及既存预算/窗口拒绝路径使跨boot自动补窗无法成立。

本轮静态检查适用host语法与AST，目标3.12编译/当前平台资格均UNRUN。Source-only包不携带旧pyc，未来在实际3.12入口`compile(source)`只检语法、不执行模型或写缓存；此差异列入新许可。
