# TR-A2最终动态裁决

Material Passport：DCL-R6-TR-A2；batch14-r1；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、源码修改/测试重跑0。

**正常最小TR-A2取得CONDITIONAL_PASS：新运行时、WORK/C00、四套184项/33变异、真实CLOSED只读、活动拒绝、native与自动行政均完成；来源/内部/范围条件继续保留。**

|验收门|状态|范围|
|---|---|---|
|RA-D1 运行时身份|PASS_DYNAMIC|本批Root/Payload检查点3组件/路径/包/Build-ID/自身映射匹配|
|RA-D2 原生兼容|PASS_DYNAMIC|获批正常A2 Python/资源接口/启动及封存；非全部ABI/完整资源链|
|TR-D1 终态只读|PASS_DYNAMIC|CLOSED后VALID原window/R/journal/phase/退出；关键摘要三侧相同|
|TR-D2 安全守卫|CONDITIONAL_PASS|实际IPC_CLOSED_DOMINATES，其他破坏性真实请求未执行，模型覆盖单列|
|TR-D3 TR40|PASS_DYNAMIC|TR-SIMULATION/1：32safe＋8变异检出|
|TR-D4 PT/PF兼容|PASS_DYNAMIC|PT55/9、PF40/8；另RA24/8，均当前版本原生模型结果|
|TR-D5 native|PASS_DYNAMIC|233 manifest/234 ZIP entries，原始输入与CRC/SHA完整|
|TR-D6 自动行政|CONDITIONAL_PASS|自动249/250完整，资源先行成功控制流支持，精细原始回执缺项保留|
|TR-D7 内部终态|UNKNOWN|缺正常MR关闭收据，原UNKNOWN保持|
|TR-D8 资源|CONDITIONAL_PASS|R3133、正常约65秒、实际C00限额/观测符合，完整资格/峰/300秒未证明|

关键事实：新batch14/当前boot/一次认领/同PID有效，T0只创建一次；C00八项全部MATCH。PT64/PF48/TR40/RA32共184项接受，151safe＋33mutant，所有预期变异检出。R3133、3133事务/6266行，读取和封存不改变原账。

CLOSED后终态review读取真实37.238567090/1837.238567090/1777.238567090、R3133；原活动接口实际IPC_CLOSED_DOMINATES。Native包与行政包独立完成并逐流验证，extra fallback/manual0。角色/组空，counter/window/claim与CLOSED保留，未在当前窗口继续MR或模型。

RUNTIME_PROVENANCE_CONDITIONAL持续，缺新.deb payload及path→exec原子边界未升级。internal UNKNOWN可与真实原件封存同时存在；本批没有修改内部状态或旧native未决。旧PFA112/17与R1907、TR-A preflight失败、TerminalRead静态和所有旧锁保持。

本批具备准备下一独立MR/C09有限验证申请的正常前缀依据，仍需新批次/完整锁及fresh准入和明确许可；完整C00–C09/C09/MR64/C10–C12/S34/门18资格链未执行。当前不授予RESOURCE_GATE_PASS或F1/F4运行资格。

[实际全量结果](evidence/ACTUAL_RESULTS.json) · [未决边界](TRA2_COUNTEREXAMPLES.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性裁决保持。
