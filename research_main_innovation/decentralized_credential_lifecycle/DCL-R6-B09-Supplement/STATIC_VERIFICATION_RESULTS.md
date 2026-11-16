# 静态验证结果

Material Passport：B09-AdmissionFix-static-1/r1；HOST_STATIC_ONLY；动态UNRUN。

|检查|结果|具体证据|
|---|---|---|
|Python语法、3.12文法、内存compile|PASS_STATIC|28程序，目标模块导入0，native编译UNRUN|
|调用关系|PASS_STATIC|AST调用图，ledger生产/驱动/oracle及资格再准入路径|
|批次绑定|PASS_STATIC|有效包中batch08/BATCH08/cr01命中0；配置完整等于固定SPEC|
|原17项保持|PASS_STATIC|逐项JSON等价，新增1项，总18唯一ID|
|新ledger覆盖/独立性|PASS_STATIC|1健康＋13异常＋4mutant；oracle只导入标准库|
|执行/验收一致|PASS_STATIC|调度分支、18项审核、18内部ID、4mutant及原件SHA强制|
|预算核心|PASS_STATIC|17个Guard预算/状态函数AST保持|
|sealed/身份基础函数|PASS_STATIC|另8个Boot函数AST保持；准备/入口只改命名、回执/模式绑定|
|受保护程序字节|PASS_STATIC|五业务、probe、range_core、range_fixtures、runner、service_readiness共10份一致|
|RootIPC/C09协议|PASS_STATIC|除Root命名/固定资格注册/Receiver单位查找外函数AST保持|
|资源重算|PASS_STATIC|RANGE完成19,861≤20,000；新专项640；全校准硬62,546≤100,000|
|崩溃与失败接线|PASS_STATIC|exclusive原件、首次错误抛出、缺件/未检出拒绝、原窗截止与停止流程|
|时间关键路径|完成分析；UNRESOLVED|当前全链300秒成功完成依据尚缺|
|原件/输入/摘要|PASS_STATIC|旧归档80/246清单成员核验；前后锁与全量diff保持|

BS-1=PASS_STATIC，BS-2=PASS_STATIC，BS-3=UNRESOLVED，BS-4=CONDITIONAL_PASS。BS-2表示实现、覆盖、原始解释独立性与门接线完成静态验收；实际故障触发/拒绝/变异检出继续UNRUN。

复核中发现并修正了回执自摘要循环、FORMAL读取私有原件的权限接线、Root重算计费和资格发布后的校准截止责任。最终冻结源及diff包含这些修正，旧研究文件和原锁保持原样。本轮没有执行新程序正文、负向夹具、故障或参考解释。

[语法/调用图](evidence/SYNTAX_AND_CALL_GRAPH.json) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json) · [绑定与门](evidence/BINDING_AND_GATE_STATIC_CHECK.json) · [资源重算](evidence/RESOURCE_BOUND_RECALCULATION.json)。
