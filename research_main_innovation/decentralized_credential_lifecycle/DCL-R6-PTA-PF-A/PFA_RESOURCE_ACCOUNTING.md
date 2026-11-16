# 访问账、时间与资源观测

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

**实际R=1907，等于冻结正常完成计费，低于阶段A硬界2689。** 预算只建立一次，未重置或追加窗口。

|指标|实际值/范围|
|---|---|
|C00/PT64/PF48|1 / 1089 / 817；17变异已包含在两套suite|
|journal|1907 PREPARED/COMMITTED事务，3814行，831310字节；每次amount1，连续0→1907|
|counter/intent|BRNGv001/24字节，cap1000000，used1907，COMMITTED after1907；与自动快照和独立导出一致|
|T0/deadline/stop_at|88.190295781 / 1888.190295781 / 1828.190295781|
|T0→CLOSED|43.088269160秒|
|active WSL host耗时|48.559493700秒，含其启动开销；外层host含自动收尾52.982416秒|
|自动post|3.890178100秒；正式窗口与单独行政30/35秒界分别保留|
|Payload charged memory峰观测|44924928字节＝42.84375MiB，parent该代memory.peak；与RSS分别统计|
|Payload tasks最大已保存观测|3；parent TasksMax/pids.max4，实际第五任务拒绝测试本轮未执行|
|C00 Payload RLIMIT_AS|实际soft/hard均1073741824；process RSS异步观测见原件|
|Root/全树RSS或tasks高水位|UNKNOWN；Root角色在Payload slice外|
|行政Root RLIMIT直接数值|UNKNOWN；设置先行由成功控制流与继承检查支持，实际Live字段未单列|
|120秒预窗TCB|原ticket/ctx真实绑定；本次T0正常创建，真实到期故障未额外注入|

资格文件预算区间PT1→1090、PF1090→1907。每项raw记录driver16，另外Root审查1与suite entry1均由同账预付。独立审计只验证pair/连续性/原件hash及输入映射，正式oracle/参考重放0。

完整校准访问硬界仍66770，软界100000；全批1000000/1800、校准300、提前1740、AS1GiB/父4tasks保持。43秒是当前最小前缀，无法直接按访次数量线性外推完整校准；C09/MR/S/门18及完整300秒可行性继续UNRESOLVED。

[完整账审计](evidence/BUDGET_AUDIT.json) · [准入界证明](evidence/RESOURCE_ADMISSION_PROOF.json) · [112项预算/时间细目](evidence/TEST_CASE_RESULTS.json) · [实际资源](evidence/ACTUAL_RESULTS.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
