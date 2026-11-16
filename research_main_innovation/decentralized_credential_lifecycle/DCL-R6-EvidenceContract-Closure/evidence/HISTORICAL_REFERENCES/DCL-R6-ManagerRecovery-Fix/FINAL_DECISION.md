# ManagerRecovery最终静态裁决

Material Passport：ManagerRecovery-static-1/r5；2026-11-12（Asia/Shanghai）；新增动态0。

**已完成针对恢复健康分类及自动关闭缺口的有限静态修复、64项夹具和独立oracle、完整差异/摘要及阶段A申请。真实恢复、回收与性能继续待动态验收。**

|验收门|裁决|完成范围与剩余责任|
|---|---|---|
|MR-1 故障根因|PASS_STATIC|MANAGER=systemd failed-unit集合；当批预期c06/c07/c09被旧规则拒绝，C09真实ACK/退出证据保持；首个迭代单位未记录|
|MR-2 恢复语义|CONDITIONAL_PASS|实例/InvocationID/结果/完整ACK/Receiver/waitpid/窗口审查、只读历史关闭事实、当前Root责任和重复事实语义已实现；OS接口/时延待验|
|MR-3 自动关闭|CONDITIONAL_PASS|前言/普通非零返回/独立停止构造异常、STOP优先、幂等首错、pidfd回收及单sealer已接线；未发布/未回收/全部源失效保留UNKNOWN|
|MR-4 回归与下一批|CONDITIONAL_PASS|31程序/46输入源码、64夹具/8mutant、预算64,082和阶段A精确申请完成；B独立身份/摘要与动态证据待A后形成|

静态检查：31程序host语法、3.12文法和内存compile通过；11份关键程序字节及29个预算/Boot/门18函数AST一致。C09持久ACK模块、C00Ready、五业务、原probe、S34驱动和预算核心保持。RootIPC仅新对象固定注册与namespace适配，原权限/发布/等待方法保持。

新MR完成计费1,089，专项硬界1,536；全校准硬界64,082≤100,000，原总1,000,000/1,800/校准300/提前1,740、AS1GiB、Payload4tasks及原共同5,000/RANGE20,000保持。Root检查前置预付256，C09后使用有界Root游标，原handoff.counter与ACK协议保持一致；时间可行性仍TIME_FEASIBILITY_UNRESOLVED。

最终manifest SHA `e32453a883905db0089e7fd480f43283edeba2d87604407bbea55f4b14c2d395`，执行锁SHA `a8358f504248377340e86c5d0b79210fd18c7c3207096f9fe7c7e27e4b928c64`。r1/r2/r3/r4候选快照保留，所有下一授权只绑定最终r4。原CalDiag 38,729账、真实C09 PASS、194项/41变异及首次失败/补充关闭事实完整保留。

本轮只在独立mr01和本轮研究目录进行host文件/AST/hash操作；目标导入/夹具/参考/WSL/服务/故障注入均0，T0/deadline/R均null。Source源码中的PASS分支未登记为实际通过。下一步审阅新batch10-r5的有限恢复/关闭诊断A，旧batch09保持CLOSED；阶段B须A充分证据后另建身份和独立批准。

RESOURCE_GATE_PASS=NOT_OBTAINED，F1/F4=UNRUN_RESOURCE_GATE，PASS_BOUNDED=[]。D1/D2原条件、强G覆盖、STRICT_SEPARATION_INSTANCES=0及IMPLEMENTATION_GATE=CLOSED保持；本轮属于通用验证基础设施修复，协议机制新增0。

[阶段A/B申请](NEXT_DYNAMIC_AUTHORIZATION.md) · [静态结果](STATIC_VERIFICATION_RESULTS.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
