# 实际预算、时间与资源

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**R=3133，等于冻结正常完成计费，低于阶段A硬4417。TR-D8=CONDITIONAL_PASS：当前最小前缀观测符合范围，完整资源校准尚未取得。**

|指标|实际值|
|---|---|
|C00/PT/PF/TR/RA|1 / 1089 / 817 / 681 / 545|
|journal|3133 PREPARED/COMMITTED对，6266行，连续0→3133，每次amount1|
|counter/intent|BRNGv001/cap1000000/used3133，COMMITTED after3133，字节在读取/封存后相同|
|T0/deadline/stop_at|37.238567090 / 1837.238567090 / 1777.238567090|
|T0→CLOSED|64.868817016秒|
|T0→terminal review|65.016418206秒|
|T0→native manifest|65.035256077秒|
|active host|79.446917700秒；含客户端开销/两侧时钟观察范围|
|全部host|86.799039300秒，含自动post|
|自动post|6.610676100秒|
|Payload charged peak|55844864字节＝53.2578125MiB；该parent代memory.peak，区别于RSS|
|Payload tasks保存观测|3，父TasksMax/pids.max4；C04第五任务测试未执行|
|C00 RLIMIT_AS|实际soft/hard均1GiB，原process值保留|
|Root/全树精确RSS/tasks峰|UNKNOWN；行政live RLIMIT数值未独立采样|

终态API是有界只读行政IO，不创建额度或debit R；四套模型测试按同一预算prepay计费。生产oracle在有效窗口内执行，退出后仅结构/SHA审查，没有checker重放。

完整硬68498≤100000、总1000000/1800、校准300、预T0120、提前1740及AS1GiB/父4tasks未放宽。当前约65秒是最小正常前缀，不能线性外推完整C/MR/S/门18链。新checker增加映射/包/文件IO，未来完整300秒时间可行性继续UNRESOLVED。

[3133事务审计](evidence/BUDGET_AUDIT.json) · [阶段A界证明](evidence/RESOURCE_ADMISSION_PROOF.json) · [每case访问/时间范围](evidence/TEST_CASE_RESULTS.json) · [真实资源](evidence/ACTUAL_RESULTS.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
