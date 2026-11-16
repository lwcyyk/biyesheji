# batch05 持久预算与停止资源核算

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

最终 R=**37,293/1,000,000**。原始 24 字节 counter、606 行 journal、COMMITTED intent 内容一致。303 笔事务为 303 PREPARED+303 COMMITTED：300 笔单信用、3 笔 exact range；独立行政 parser 导入目标模块 0，错误 0。

|task|before|amount|after|
|---|---|---|---|
|C02.memory.v1|3|32896|32899|
|C03.shared.v1|32900|4096|36996|
|C04.fifth-task.v1|36997|1|36998|

总量等式：300+32,896+4,096+1=37,293。C02 实际使用17,991/32,896，剩余14,905保持占用；退款0、预算重置0、resume0、新窗口1。C09H 基线37,020，driver239+Root34=273，最终37,293。真实 C09 在分配其入口信用前 EACCES，因此没有后续事务。最终 intent before=37,292/after=37,293/status=COMMITTED，boottime=3898.266588342。

原始内容一致性与访问权限分别裁决：counter及journal为999:989/0600；共享intent为0:0/0600。euid0审查能写入该intent，下一uid999读入失败。该缺陷导致全局预算运行健康准入失败；`PASS_RAW_ACCOUNTING`仅表示本次停止前账内容核对。

boot `8f92c77b-39bb-4526-a85c-174189b689ce`，原T0/deadline/stop_at保持。首次请求停止+20.861903589，闭合+20.909951317，payload组空+20.927591657；Root最终清理+300.043546214，外层300.5839319秒。父组观察charged峰值125,554,688 B、pids上限4；树RSS峰值与Root CPU/RSS为未测量。

历史batch04 R=37,021、batch02 R=32,191已从host原始counter再次读取；历史、源及47误副本字节核对见[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)。先前 `blocked by policy` 保留；误副本仅只读/hash。

[counter原件](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/visits.bin>)、[intent原件](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/visits.bin.intent.json>)、[journal原件](<../../../DCL-R6-isolated-verification/batch05/native_snapshot/out/visits.bin.journal.jsonl>)、[独立核算](evidence/BUDGET_AUDIT.json)、[原始权限](evidence/commands/26.result.json)。
