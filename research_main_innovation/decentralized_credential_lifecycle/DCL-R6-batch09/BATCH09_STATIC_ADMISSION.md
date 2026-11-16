# batch09完整链静态准入复核

Material Passport：DCL-R6-batch09；HOST_STATIC_ADMISSION；2026-11-12；动态资格尚待建立。

## 三项准入责任

|ID|实际发现|裁决|后续最小工作|
|---|---|---|---|
|D09-A01|原36份文件字节完整，但固定batch08命名空间与新batch09要求冲突|BLOCKED_STATIC_NAMESPACE_BINDING|在新独立源包静态适配路径/批次/回执/argv/摘要，保护cr01及旧批次|
|D09-A02|完整访问容量可证明；现有记录缺完整校准≤300秒的成功完成依据|INCONCLUSIVE_STATIC_TIME_ADMISSION|补充可核验耗时假设，或明确允许同300秒界内的一次条件尝试|
|D09-A03|冻结17项负向门中缺预算账异常专门recipe|REQUIRED_TEST_MISSING|保留原17项，另行静态构造至少一个独立合成账异常的资格拒绝用例并重新冻结|

冻结版本一致性已通过，能够执行新独立批次的版本尚待形成。用户授权§3.2要求必需测试缺失时停于静态，§3.3要求无法证明资源适配时形成最小合同修订申请，§13给出准备阶段停止出口。本轮依据这些明确条件关闭行政准备工作。

## 精确命名空间证据

|文件/位置|现有约束|
|---|---|
|host/windows_entry.py:15|回执固定在DCL-R6-batch08/evidence；stdout/stderr以xb创建于同目录|
|src/boot_continuity.py:16、234、419|ROOT为/var/lib/dcl-r6/batch08，授权batch_id=batch08，CLI choices仅该ROOT|
|src/boot_continuity.py:206–208|旧批次根/单位存在时拒绝新启动|
|src/guard.py:35、222、676|可用根及授权检查绑定batch08；service单位固定batch08|
|src/root_ipc.py:73|Root/Payload目录策略只接受batch08|
|src/c09_handoff.py:96|Receiver单位固定dclr6batch08-stop.service|
|inputs/*contract.json|五份测试合同future_batch_id=batch08；S34内部job也固定该batch|
|inputs/execution_lock.json|启动、准备、payload、worker、日志和回执路径固定旧命名空间|

[命名空间审计](evidence/NAMESPACE_BINDING_AUDIT.json)记录215处内容命中；[迁移范围审阅表](evidence/NAMESPACE_MIGRATION_REVIEW.json)把源包cr01路径及slice文件名一并纳入，涉及16份文件的审阅责任。该表仅列拟议范围，实际变更0。单改CLI参数或复制回执无法满足多层绑定；别名、挂载和改写历史路径也超出当前冻结合同。

## 完整程序与依赖

继承的实际顺序为：单会话预检/exec → C00真实双次READY与probe → READY64及独立oracle → C01–C08 → C09H34及Root重算 → RootIPC56 → BC40 → 真实C09 ACK/Receiver/waitpid/fresh-read → 同一父进程内一次恢复 → C10原生READY → C11–C12 → S34 → 原始证据重算及门17 → 当前账健康及RESOURCE_GATE → F1 → F4 → 关闭封存。

上述既有程序/输入均存在，清单和原argv已保存至[FROZEN_TEST_INVENTORY](evidence/FROZEN_TEST_INVENTORY.json)，其argv属于batch08只读参考。预算异常负向资格用例为新增责任，当前冻结入口无法提供该项实际执行。

## pidfd观测责任

现有collector执行pidfd打开、select存活检查、前后identity比较、再次READY及票据前复核；formal_gate要求原生来源、当前boot/锁和八项MATCH。独立pidfd时刻、后侧原始stat和精确wait返回点属于额外审查记录，当前冻结正式门未把这些字段列为强制schema。本轮保持FIELD_EVIDENCE_PARTIAL，不以该缺口单独新增运行门槛。已有三项阻断仍然成立。

目标启动0，当前boot查询0，运行源码改动0，现场绕过0。研究目录DCL-R6-batch09仅含本轮准备材料；独立运行目录、T0、账及运行关闭收据均由后续真实准入建立。
