# PreT0最终静态裁决

Material Passport：PreT0Recovery-static-1/r3；2026-11-12（Asia/Shanghai）；新增动态0。

**已完成预窗/运行态检查点拆分、认证启动期限、初始化intent/armed/work守卫，以及自动host退出后行政封存的有限静态修复。新增原生行为仍待动态许可。**

|验收门|裁决|完成证据与范围|
|---|---|---|
|PT-1 初始化根因|PASS_STATIC|query(record=True)最先调用要求state的RootIPC点；state创建在health之后，旧循环依赖准确定位|
|PT-2 生命周期|CONDITIONAL_PASS|活体sealed预窗scope、单调intent、真实state/counter/point/armed顺序、运行缺点严格拒绝均已实现|
|PT-3 停止/封存|CONDITIONAL_PASS|继承120秒启动期限、预算未初始化真实null、native适用性及自动post行政包分开；真实退出/IO/未知模型待验|
|PT-4 回归/准备|CONDITIONAL_PASS|35程序/51文件、PT64/9mutant、独立oracle、资源65,618及两个互斥A模式精确锁齐备；B身份/最终摘要待A后形成|

13份关键程序字节保持（五业务、原probe、range_core、S驱动、runner、C00Ready、C09、MR驱动/oracle）；40个既有预算/Boot/门18/正常MR函数AST及RootIPC原权限/发布/等待方法保持。原systemd资源slice字节相同。新增测试实际UNRUN，host语法/3.12文法/内存compile通过35程序。

PT完成1,089/硬1,536，完整校准硬65,618≤100,000；最小NORMAL_START硬1,537，纯PREWINDOW_ABORT无T0/R。原全批1,000,000/1,800、校准300、提前1,740、AS1GiB/父4tasks不扩。新增只读post导出30秒/host35秒及256文件/32MiB作为行政收尾条件列下一动态申请。全链时间仍UNRESOLVED。

最终manifest SHA `34c9c4642c4ff8c68183845b66f49f1670efa3349ec82e07d80e8bbabfd86ab7`，execution_lock SHA `af8de2c099813d2e3018c6d46b2e95b435c2e75a122d32b73b3f96e3c47b58ec`。r1/r2候选源码/锁保留，最终r3为唯一下一授权目标；原r5与MRA原件冻结。

本轮WSL/新服务/校准/故障/测试/参考/模型运行0，T0/deadline/R均null。没有假造checkpoint或运行资格。历史MRA退出125、STOP/CLOSED、父停止成功、内部UNKNOWN、原生seal失败及行政ZIP完整性分别保持；CalDiag真实C09及38,729账保持。

RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE，PASS_BOUNDED=[]，D1/D2原条件/强G/STRICT_SEPARATION_INSTANCES=0及IMPLEMENTATION_GATE=CLOSED保持。此次属于通用验证基础设施修复，协议机制新增0。

[下一有限动态申请](NEXT_DYNAMIC_AUTHORIZATION.md) · [静态结果](STATIC_VERIFICATION_RESULTS.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
