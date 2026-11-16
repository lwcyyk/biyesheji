# S3-A/S3-B最小实施、验收与费用

全部为P类设计；新文件/数据库/测试尚未创建或执行。

## 1. S3-A范围与物理格式

采用新专用合成SQLite库，与真实AuthorityStore对齐逻辑版本/状态/事件，明确使用`SyntheticJsonCodec`，不声明AES-GCM物理格式兼容或保密能力。仅SYNTHETIC_CONTRACT、无密码/Token；不导入/实例化运行AuthorityStore或Provider。此选择避免为了合成事务测试额外安装cryptography，原真实加密设计不改。

建议最小表：s3a_state(id=1,version,payload)、s3a_events(version,projection)、s3a_proposals(instance,id唯一,owner,digest,status,receipt)、s3a_objects(digest,kind,bytes)。o在payload.dsat中，和a由一次读/同一更新取得；不可变proof/费用工作对象可与回执同库写，避免外部ref悬空。拒绝仅登记proposal/档案，不改world行a/o；成功world/event/O/回执同事务。

DB强制受控路径、合成application_id/mode/实例marker，文件名禁止authority.db，只允许新测试根下dsat_s3a_*.sqlite3；已存在非合成库拒绝。WAL/FULL配置仅在将来授权的临时库使用。清理前核实绝对路径在获准子树内；当前没有删除/移动。

## 2. 文件级清单

主工程根D:/毕业设计/auth-lifecycle：

| 拟新增/后续修改 | 函数/字段/兼容责任 |
|---|---|
| 新dsat_commit_types.py | proposal、delta/covers、version/read-context、receipt；严格JSON/整数/大小、域分离摘要；复用dsat_types风格不改旧Schema |
| 新dsat_commit.py | Prepare/Validate的纯数据部分、O覆盖/来源/费用计划、受信验证适配；数学算法不复制 |
| 新dsat_synthetic_store.py | 专用SyntheticStore.read/commit/recover、BEGIN IMMEDIATE/CAS/幂等簿、同库对象，固定NO_NATIVE/NO_GLOBAL_COMPLETE |
| 新tests/test_dsat_commit_contract.py | typed输入/绑定/O/currentness/权限拒绝的合成例 |
| 新tests/test_dsat_commit_store.py | 双版本、ID/replay/CAS、逻辑费用去重及旧视图隔离 |
| 新tests/test_dsat_commit_recovery.py | 受控子进程终止、ACK丢失/恢复、合成旧状态/坏模式 |
| 新tests/fixtures/dsat_commit/ | 从R06/R07冻结数据派生并带SHA的新夹具，原25份不动 |
| 新scripts/run_dsat_s3a_tests.py | 只运行这三模块/专用库/固定proof，限制目录/资源并保存日志 |
| 后续storage.py/services.py | 仅S3-B允许新dispatcher、受控快照/typed读写和全部O事件钩子；当前不改 |
| reconciliation.py/旧检查器 | 原义保持，不放宽single_unknown条件；新协议独立命名 |

使用已批准CPython3.12.14环境及标准库sqlite3；数学检查复用原标准库check_dsat_certificate，S1/S2/NetworkX源码不改、不发明新解法。当前无新依赖安装申请。

## 3. 静态验收组

S3_IMPLEMENTATION_TASKS包含逐文件副作用/风险/授权。未来测试均NOT_RUN：正常首提交/同体回放/独立ID/数学与条件归档；双proposal竞争、撤回/迟到/gV/O版本/时效变化；UNKNOWN保留、保守settle→close+source-hold、R饱和D不足、A24审计、B独立进展；十四崩溃位置；伪造来源/跨批准/旧版本/坏证明/空F/缺D/外部当前性/错误COMPLETE。

预期字段为输入、a/o、操作/故障点、持久state、O前后、证书、费用/状态/回归影响。S3-A源前提用显式合成模型，所有Native风险仍保守；安全拒绝/UNKNOWN是预期，不伪填PASS。

## 4. 兼容/资源/停止

S3-A不修改storage/services，不连接已有DB，不跑原115或原生CLI。新原型种子从白名单合成JSON导入，缺typed O时生成保守初始化/缺口，不能把缺字段解释成空O。损坏/不支持schema/实例/codec拒绝恢复，不用旧缓存替代。

初始建议界：proof≤4MiB、世界状态≤8MiB、O≤1024、风险组件≤4096、提案簿≤256个保留ID；达到上限拒绝新工作，不逐出仍承诺幂等的tombstone。revision用SQLite有符号64位且不回卷，耗尽返回REVISION_EXHAUSTED。旧SQL schema/计费没有免费容量。

受控崩溃只终止专用合成子进程，不碰运行服务。新代码/测试/临时DB均需下一轮明确授权。S3-B另审真实权限/导出/加密/迁移/进程fence/当前性和客户端兼容，S5独立门。

## 5. 完整费用模型

C_compute计S1/S2或可证明的不可变包复用；C_verify计数学检查、真实来源/依赖/当前守卫；C_storage计全state读取/解密、O规范化/摘要、对象/历史、状态序列化/加密/SQL/磁盘持久；C_commit计写锁等待、CAS/覆盖/费用/ID检查及一次COMMIT；C_recovery计WAL恢复、解码、索引/证书重新验证和重试；C_native另列。

若加密state大小S、proof B、O描述L、图V/M，当前整快照读写至少扫描S并付相应I/O；verify算术O(V+M)加位长及输入B，O覆盖/全摘要付L及组件引用成本，proposal/对象索引也有查询/维护成本。不能据单个version比较称提交O(1)。

CAS失败仍付读取/解密/校验/锁等待与已发生计算；不同ID重用同work不重复逻辑记账，但实际重算仍计。幂等回放要认证/读簿/校验摘要，非零成本；如果当前权限需读state，仍可有O(S)工作。日志遥测不与SQLite自动原子，崩溃最后阶段实际纳秒可能不可重建，标缺测，不杜撰精确账。

本轮所有S3数值NOT_MEASURED。R07的C_flow/C_verify历史值不当作S3锁/加密/fsync/恢复时延。
