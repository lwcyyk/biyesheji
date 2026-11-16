# 运行时变化与历史阻断时间线

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

**旧TR-A的PREFLIGHT_FAILED_RUNTIME_DRIFT保持；本轮只读确认变化属于Ubuntu glibc包修订。**

|阶段|时间/主体|可复核事实|
|---|---|---|
|旧冻结8.9|旧runtime_critical/runtime_files与历史TR前缀|loader/libc/libm旧SHA固定，Python3.12.3固定|
|本机包日志|原文2026-11-13 13:26:52–53|libc6/libc-bin 2.39-0ubuntu8.9→2.39-0ubuntu8.12；安装/配置记录完整|
|旧TR-A入口|UTC2026-11-13 09:28:55.908611；Bootstrap2271/start43611|PREFLIGHT_BEGIN后loader摘要首次失配，active exit125|
|旧TR-A保全|UTC09:28:56.510318；行政Root2275|自动14清单/15ZIP，T0/R=null，正式实例未创建|
|本轮来源核验|7次只读WSL查询，各boot/time/argv单列|dpkg、签名/索引、ELF/静态依赖、旧包成员、最终文件访问核验|
|本轮重冻结|新r1/新batch14静态身份|仅3项已观察运行时pin变化；实际动态窗口0|

当前系统/etc/localtime指向Asia/Shanghai；历史包日志未带时区，原文时间与host/guest UTC分别保留，避免构造未经记录的精确跨时钟关系。各只读查询可以处于不同boot，原始boot列表保留，均不成为后续运行资格。

升级执行者和具体自动机制未被本轮证明，报告不归因到某个进程。任务期间网络下载、安装/升级/降级、库文件写入、WSL重启均0。

[原TR-A首错/包日志](../DCL-R6-TR-A/evidence/RUNTIME_DRIFT_AUDIT.json) · [本轮原生结果](evidence/PROVENANCE_AUDIT.json) · [查询boot/最终绑定](evidence/FINAL_BINDING_REVIEW.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
