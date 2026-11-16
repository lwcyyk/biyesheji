# B09补充任务最终裁决

Material Passport：B09-AdmissionFix-static-1/r1；2026-11-12（Asia/Shanghai）；STATIC_ONLY；动态0。

**两个确定性阻断已完成静态修订：独立batch09身份与预算账异常资格用例均已实现、接线并冻结。完整校准300秒充分时间依据仍为TIME_FEASIBILITY_UNRESOLVED，下一步推荐方案B有限完整校准诊断。**

|验收门|裁决|证据范围|
|---|---|---|
|BS-1 独立批次|PASS_STATIC|结构化精确身份、独立cr09/控制路径、有效包旧身份命中0、回执/boot/一次认领隔离|
|BS-2 预算异常检测|PASS_STATIC|原17项保持，第18项聚合含健康控制/13异常/4mutant，生产门和独立原始参考共同评估；实际检出UNRUN|
|BS-3 时间可行性|UNRESOLVED|关键路径/持久原语/旧性能审查完成；当前全链成功耗时与最坏IO/调度依据尚缺|
|BS-4 动态恢复|CONDITIONAL_PASS|42文件/28程序、完整diff/锁/argv/18项门/资源重算和A/B申请齐备；新版本动态批准仍待产生|

28程序host语法、3.12文法与内存compile通过；10份受保护程序字节一致，17个Guard预算/状态函数及8个Boot基础函数AST一致。RootIPC/C09的权限/交接函数除必要身份和固定资格注册外保持。五业务、probe、预算核心、S34驱动、runner及原14秒/八字段实现保持。

新ledger完成计费631，专项640；RANGE完成上界由19,229变为19,861≤20,000，使用新专项硬额时为19,870≤20,000。总校准硬访问维持62,546≤100,000，1,000,000/1,800/300/1,740、AS1GiB、Payload4tasks均保持。所有新增Root原始重算已计费。

42项manifest SHA为`c7bed9528ea4a6ada08882d02be23dd37c62e8ee79fbb70a9445ddcc361ea127`，执行锁SHA为`fcc70f0d78aefc1ccc1fcc96489a3984417c6b4b7f203c78162c910b64746b81`。完整原/新源码和diff可供审阅，原r2、batch09旧阻断、batch08通过证据及全部历史文件保持冻结。

本轮Launcher/Root/service/目标测试/参考解释执行均0，T0/deadline/R及运行峰值均null。当前平台资格与新代码的实际DAC、fsync、pidfd、交接及故障行为均待动态证据；静态PASS仅覆盖已列静态责任。batch08的FIELD_EVIDENCE_PARTIAL及batch07具体失配未决保持。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；D1-PBFT-SEAL/1.1、D2有限模型条件结论、强G覆盖、STRICT_SEPARATION_INSTANCES=0及IMPLEMENTATION_GATE=CLOSED保持。当前修订属于通用验证基础设施，协议机制实现新增0。

[两方案执行申请](NEXT_DYNAMIC_AUTHORIZATION.md) · [静态验证](STATIC_VERIFICATION_RESULTS.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
