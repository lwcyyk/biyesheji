# batch09最终裁决

Material Passport：DCL-R6-batch09；2026-11-12（Asia/Shanghai）；静态准备完成；目标执行0。

**BLOCKED_STATIC_ADMISSION：本轮止于准备阶段，当前执行锁runnable=false。** 完整条件执行授权已经收到；原36份冻结文件及batch08归档完整性通过。新batch09身份与原batch08固定绑定冲突、完整校准300秒成功完成依据尚缺、预算账异常负向资格测试缺项，三项责任已具体化并提交最小补充申请。

|最终验收项|实际结论|
|---|---|
|1 完整执行锁|原r2字节及交叉摘要通过；新batch09运行锁BLOCKED_STATIC_ADMISSION|
|2 启动连续性|UNRUN_STATIC_ADMISSION；WSL/exec/认领0|
|3 C00八项|本轮UNRUN；batch08历史C00_PASS及双样本保持|
|4 pidfd观测缺口|保留；独立时刻/后侧stat/精确wait返回点属于冻结门以外的额外记录|
|5 BC40|30 safe＋10 mutant输入齐备；本轮执行0|
|6 C00–C12|13项均UNRUN_STATIC_ADMISSION|
|7 RootIPC56|48 safe＋8 mutant输入齐备；本轮执行0|
|8 C09H34/真实C09|输入28 safe＋6 mutant；本轮均UNRUN，ACK/Receiver/waitpid实际值null|
|9 S1–S9|34项输入齐备；本轮执行0|
|10 门17|输入齐备，实际检出null；本轮新增要求的预算异常负向项缺失|
|11 RESOURCE_GATE_PASS|NOT_OBTAINED|
|12 F1/F4启动|均0；均UNRUN_RESOURCE_GATE|
|13 PASS_BOUNDED|[]|
|14 反例/验证缺陷|正式协议反例0；发现静态批次绑定冲突和必需负向覆盖缺项；时间为准入证据不足|
|15 资源/停止|访问硬额静态62,546≤100,000；实际T0/R/deadline/耗时/峰值均null；静态准备停止|
|16 F2/F3条件|尚待完整资源资格及F1/F4结果；本轮范围继续排除F2/F3|

本轮host行政活动包括文件读取、hash、AST解析、ZIP逐流核对及交付材料写入。原cr01及所有历史运行目录保持冻结；目标模块导入/目标测试/系统配置修改/权限修复/重试/预算重置/旧批恢复/自动batch10均0。运行Payload及Root角色创建0，运行CLOSED/退出清理收据不适用。

访问上界由当前代码和输入重新拆算：C00–C12 37,034＋READY硬限512＋C09H/IPC/BC共同硬限5,000＋RANGE/原始重算/门17硬限20,000=62,546。该结果只适用当前冻结清单；新增测试后须重锁。300秒完整成功完成与F1/F4穷尽尚待相应证据。

batch07具体失败字段继续C00_FAILED_FIELD_UNRESOLVED。batch08的C00_PASS、64项接受、R450、正常关闭及FIELD_EVIDENCE_PARTIAL保持历史归属；本轮没有将其升级为batch09资格。

下一步为审阅[最小补充申请](BATCH09_MINIMAL_SUPPLEMENT_REQUEST.md)，范围仅包含独立命名空间静态适配、预算异常负向覆盖、300秒准入责任精化。D1-PBFT-SEAL/1.1、D2有限模型条件结论、强G覆盖、严格分离实例0与IMPLEMENTATION_GATE=CLOSED保持。

[静态准入](BATCH09_STATIC_ADMISSION.md) · [资源核算](BATCH09_RESOURCE_ACCOUNTING.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)
