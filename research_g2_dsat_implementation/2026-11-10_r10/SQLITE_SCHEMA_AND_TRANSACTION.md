# 实际 SQLite 结构与事务

环境：获批隔离CPython 3.12.14，标准库SQLite 3.53.1。独立新库application_id为 `0x44534133`、user_version为1、世界schema为 `dsat-s3a-world/1`，codec为 `SyntheticJsonCodec/1`。这一版本号仅属于专用库。

## 四表

| 表 | 实际实现 |
|---|---|
| s3a_state | id=1，version为signed64的a，规范JSON payload包含唯一o、typed O、合成来源/策略/权限、证明/历史/work引用 |
| s3a_events | version主键、event_id唯一；operation/projection/event_digest；只记录接受的世界变化 |
| s3a_proposals | instance/id复合主键；owner、完整正文摘要、ACCEPTED/REJECTED、不可变receipt及摘要 |
| s3a_objects | object_digest主键；kind/完整规范内容/字节数；接受对象同库写入 |

后三表设UPDATE/DELETE拒绝触发器；接受逻辑使用INSERT或同内容复用。a唯一保存在SQL列，o唯一保存在 `payload.dsat.obligation_revision`。拒绝提案只新增终态簿行，world/events/objects保持。无效入口和无权请求不占ID。

新建采用排他文件创建、文件身份及creation ticket，初始化成功才将ticket改为READY。恢复以rw-existing方式打开，未知现存文件在连接前拒绝；头、mode、实例和引用均核对。初始化中断、坏schema/codec、缺O、错实例都有实际拒绝测试。

## 实际顺序

T0严格解析/资源/身份→T1 BEGIN IMMEDIATE与当前快照→T2持久ID/owner/body/历史读权→T3新ID容量/当前写权/版本与摘要→T4固定证明/可信独立检查记录/投影/依赖/覆盖/work→T5对象、world/O、a/o、事件和receipt→T6 COMMIT→T7交付。

同体重放直接读取原receipt，独立报告历史资格；旧base与满簿都排在其后。版本不符使用冻结码 `REJECTED_REVISION`（R10所述CAS_CONFLICT语义）；同版本摘要不符为 `REJECTED_BASE_DIGEST`。拒绝ID已持久时始终绑定原正文，新基准用新ID。

配置实际执行WAL、FULL、foreign_keys=ON、temp_store=MEMORY、busy_timeout1000ms及主库页上限。每次已知库打开核WAL/头和世界；K8/K9直接验证其事务结果。64MiB逻辑主库页配额有实际触发拒绝；WAL/shm/目录阈值承担监测停止职责，物理磁盘瞬时硬配额另需OS设施。

## 版本与原子性

接受世界提交a+1；O成员/覆盖/状态/依赖变动才o+1。合成domain writer同事务维护来源epoch和O依赖epoch，撤回、迟到、第三批准、B和O事件均走此约束。所有新提案严格全局CAS；a/o均禁止回卷。逻辑work ID跨proposal去重，实际每次提交/重试仍计时。

K8在对象插入、世界更新、事件/回执暂存三个SQL边界分别终止新worker；重开后四表与旧状态一致。K9在COMMIT成功返回后、ACK前终止，重开得到完整状态和原回执。同体重试的逻辑效果和work均保持一次。

`UNKNOWN_COMMIT_OUTCOME`需以同ID查询；存储无法写拒绝行时返回 `REJECTION_NOT_PERSISTED` 并明确未绑定。两种结果均有实际注入检查。崩溃末端遥测与SQLite事务分别管理。

恢复核事件版本连续性、末端世界摘要、对象内容/引用和回执摘要。信任前提为受控单主测试根、可信OS/SQLite/存储；恶意整体回滚、设备虚假fsync和断电语义继续在当前证据范围之外。
