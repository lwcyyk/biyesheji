# 预检失败与自动封存时间线

Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。

|事件|原始时间|事实|
|---|---|---|
|外层host开始|UTC2026-11-13 09:28:55.656703|冻结入口唯一一次|
|active WSL开始|UTC09:28:55.908611|--activate固定argv|
|PREFLIGHT_BEGIN|BOOTTIME436.167570765；guest UTC ns1794562136086751893|Root2271/start43611；120秒deadline来源已开始|
|hash拒绝|精确抛出时刻UNKNOWN|ld-linux摘要不符；stderr保存原错误|
|active返回|UTC09:28:56.168099|exit125；0.259492秒|
|自动行政进程|PID2275/start43638|固定Root入口，post exit0|
|行政审计|BOOTTIME436.452127342|无runtime对象、角色/组空|
|自动封存|UTC09:28:56.510318|行政14/15，SEALED|
|外层返回|UTC09:28:56.529977|exit125，总0.8732948秒|

工作、TR/PT/PF、CLOSED后读取、原生seal时间均未产生。guest BOOTTIME/UTC、host UTC和包日志时间分开保留；不由包日志未记录的时区推定精确跨时钟先后。

[原始全量时间线](evidence/EXECUTION_TIMELINE.json) · [active退出](evidence/WINDOWS_ENTRY_EXIT.json) · [自动post计划](evidence/STARTUP_POSTEXIT_PLAN.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。
