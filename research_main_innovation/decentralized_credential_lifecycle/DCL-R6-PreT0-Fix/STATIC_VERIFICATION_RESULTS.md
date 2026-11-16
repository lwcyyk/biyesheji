# 静态检查与验收缺口

Material Passport：PreT0Recovery-static-1/r3；HOST_STATIC_ONLY。

|检查|结果与范围|
|---|---|
|源码/输入/历史|51项最终锁及前后diff；旧MRA/Manager归档及6068旧baseline/184磁盘成员匹配|
|Python语法/3.12文法/内存compile|35程序PASS_STATIC；目标import/执行0，原生compile UNRUN|
|初始化顺序/依赖|显式pre-scope；intent→真实state→counter→ready→armed→work，静态顺序PASS|
|运行缺点拒绝|原严格RootIPC＋当前Root checkpoint；缺失/损坏/身份错继续fail-closed|
|预窗期限|原sealed120秒TCB；无新T0或免费期限；正常Root运行deadline后备保持|
|停止/封存分类|进程、内部应用、行政、native分开；自动host收尾与原native入口不同|
|保护语义|13程序字节、40预算/Boot/门18/MR函数AST及原RootIPC方法/资源slice保持|
|回归/oracle|64唯一ID、9mutant、≤11帧，独立reference无生产导入，实际UNRUN|
|资源重算|PT完成1089/硬1536，完整硬65618≤100000；原总/软时限/AS/任务不扩|
|原生行为/性能|UNRUN；35/30秒行政收尾上界与目录资源限列下一申请，完整300秒仍UNRESOLVED|

Gate PT-1=PASS_STATIC；PT-2/3/4=CONDITIONAL_PASS。已解决代码/规格的循环前提和阶段区分，真实Root/系统调用/停止/归档、未知故障与各模式完整性仍需新的有限动态许可。

[语法/调用图](evidence/SYNTAX_CALL_GRAPH.json) · [生命周期静态义务](evidence/LIFECYCLE_STATIC_CHECKS.json) · [语义保护](evidence/PROTECTED_SEMANTICS_CHECK.json) · [资源](evidence/RESOURCE_BOUND_RECALCULATION.json)。
