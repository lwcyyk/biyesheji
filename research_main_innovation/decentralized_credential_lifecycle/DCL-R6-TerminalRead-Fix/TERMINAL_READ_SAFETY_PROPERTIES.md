# TR-1至TR-10安全性质

Material Passport：DCL-R6-TerminalRead-Fix；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；HOST_STATIC_ONLY。

|性质|源码/字段及静态证据|裁决边界|
|---|---|---|
|TR-1 TerminalReadOnly|read_terminal_evidence调用闭包无写/创建/预算/阶段/进程动作，打开原件O_RDONLY|PASS_STATIC，原生字节前后核验待验|
|TR-2 ActiveGuardPreserved|G.state/validate_state_document/root_checkpoint与原PF函数保持；caller记录CLOSED实际拒绝|PASS_STATIC，下一Native实际拒绝待验|
|TR-3 NoTerminalReactivation|read结果runtime_authority=NONE，无work/预算/phase/Launcher资格；历史模式不授native资格|PASS_STATIC|
|TR-4 EvidenceAuthenticity|固定namespace、原activation/receipt/源码/锁、元数据/原boot/关键摘要|CONDITIONAL_PASS，继承原TCB信任假设|
|TR-5 DeadlineConsistency|原T0/deadline/stop_at直接索引、固定关系，观察boot单列|PASS_STATIC，无默认时间|
|TR-6 BudgetConservation|counter SH→phase SH；同一写锁对象；journal pair/终点/COMMITTED intent一致；读取不debit|PASS_STATIC，原生一致性/锁延迟待验|
|TR-7 SealPreconditionCorrectness|原退出等待后调用只读前提，稳定角色/waitpid/window/budget有效才native_ready|CONDITIONAL_PASS，后续原生IO未知|
|TR-8 NoFalseSealSuccess|ready与completed分开；既有ZIP成员/当前关键证据逐流校验，错误保留|PASS_STATIC，真实IO故障路径待验|
|TR-9 UnknownPreservation|缺件/坏数据抛具体错误，internal缺收据保留UNKNOWN，无组空升级|PASS_STATIC|
|TR-10 FinalizerCompatibility|host entry/finalizer逐字节相同，bootstrap除namespace外AST保持；原30/35/256/32MiB界保持|PASS_STATIC，新包联调待验|

28项静态断言、13份关键程序逐字节与70项受保护成员归一AST核对完成。整个RootIPC及MR模块归一AST保持，活动态预算/phase机制没有被替换。文件锁为内核瞬态状态，原始数据、预算和生命周期记录无修改调用。

原生flock、文件系统IO、退出与封存性能仍受原kernel/调度/存储返回假设约束，本轮没有实时系统或全链性能证明。

[断言与行号](evidence/SYNTAX_CONTROL_FLOW_READONLY_CHECK.json) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与原创性裁决保持。
