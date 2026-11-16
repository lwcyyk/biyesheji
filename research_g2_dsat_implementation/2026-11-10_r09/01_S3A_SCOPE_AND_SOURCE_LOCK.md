# G2-R09：S3-A 范围与来源锁

日期：2026-11-10，Asia/Shanghai。当前对话内知情模型辅助工程审定；外部独立审查待取得。

## 1. 审定结果与授权状态

`S3A_SCOPE_APPROVABLE`；`S3A_AUTHORIZATION_PENDING`；`S3B_IMPLEMENTATION_BLOCKED`；`S5_NOT_AUTHORIZED`。

本轮交付为实施申请及静态验收规格。新 S3-A 代码、SQL、数据库连接、测试与故障注入均为 0。46 个顶层测试全部 `NOT_RUN`，S3 性能全部 `NOT_MEASURED`。范围可批准表示合同和验收条件已经足够明确，实际工程结果须在另行授权后的执行记录中产生。

## 2. 基线及来源

完整继承 R08 的八稿、九份根 JSON 和 sources，共 27 件；同对话既有全文核读继续有效，本轮重读核心合同、事务审计、义务转换、依赖边界、实施计划及申请。`sources/R08_BINDING.json` 固定全部字节；其中 26 件匹配 R08 交付 QA，QA 自身另固定。

R07 实际结果沿用：115 PASS / 0 FAIL / 0 ERROR / 0 SKIP；23 份自动证明通过独立 CLI，4 份篡改包被拒；S1/S2 已完成。此轮只核对资料哈希，未重复运行上述测试。固定环境为 `D:/毕业设计/auth-lifecycle/.venv-dsat-r07-networkx-3.7/Scripts/python.exe`，既有 CPython 3.12.14、NetworkX 3.7。S3-A 使用标准库 SQLite 与原独立检查器，NetworkX 求解调用和新增安装均排除在申请之外。

`SOURCE_LOCK.json` 对 R08 的 502 项当前工程/历史记录、229 项 R07 交付、21 项核心来源和本轮任务分别记录实际哈希及比对。哈希用于字节固定；原有证据的实际阅读范围、测试口径和模型辅助参与情况沿原记录。

关键源码定位沿 R08 短 ID：

| 定位 | 审定所依据的事实 |
|---|---|
| C01 `storage.py:122–159` | 旧包装器对正常返回的拒绝/重复也增世界版本；S3-A 使用独立入口 |
| C01:24–43、C02 `services.py:94–102` | 旧 O 为 phase/window 派生视图，旧代理端会重建自身 O |
| C09 `dsat_flow.py:246–263` | 包内 `bindings.O_before` 来自 `obligations_proposed` |
| C11 `check_dsat_certificate.py:341–364` | 独立标准库 CLI；固定包、预期摘要和结果文件可显式绑定 |
| C07/C08 migrations；C01:47–91 | 真实库支持原 schema 0/1/2，S3-A 采用另一专用数据库 |
| C14 `score_agent_isolation.py:175–177` | 旧顶层字段白名单影响兼容；本申请保持旧接口 |

## 3. 本轮澄清及冻结细节

1. A08/A24 的输入 O 各 5 项，证据来自合成 fixture 声明。当前尚无 S3-A 数据库。这 5 项需在后续批准执行时先作为种子持久化，再由事务读取成为 `O_before`。A08 投影新增 `close:c2`，A24 新增 `await_terminal:i1`，各为 6 项。
2. a 为 SQL `version`，o 唯一存于 `payload.dsat.obligation_revision`，沿 R08 原选择。一次读取及同一次状态更新取得二者。回执里的版本仅表示历史快照。
3. 幂等查询先于旧 base CAS 和新 ID 容量检查。只提交终态 ACCEPTED/REJECTED 提案行，暂存过程留在事务内。
4. 合法拒绝只写提案簿中的受限回执；世界行、世界事件、接受对象和 O 均保持。畸形/无权请求保留入口诊断，ID 留给合法主体使用。
5. 固定覆盖规则保留旧义务完整描述或其可解析不可变副本。`close:u` 只覆盖指定材料；原 unseen/source/descendant/audit 债务由旧项或 `pending_source` 继续持有。
6. 46 项按原 ID 执行化。K1–K6 为前置阶段边界模拟，K4 只模拟未交付的求解输出；K8/K9 在未来执行中须取得真实专用 SQLite 子进程的终止/恢复证据。
7. 物理文件预算分为 SQLite 可强制的主库逻辑页上限与运行监测阈值。WAL、shm、总目录监测阈值只承担停止新工作职责，硬实时磁盘配额保证另需操作系统设施。

这些细节只追加在 R09。R08 原文保持原字节；数学算法、创新资格和真实原生精化结论沿用。

## 4. 允许范围与旧文件保护

拟新增文件、输入输出和副作用逐项见 02；允许执行及 46 项矩阵见 03 和 `S3A_TEST_MATRIX.json`；准确授权文字见 04 与 `S3A_AUTHORIZATION_REQUEST.json`。

主工程现有全部文件、原 115 项测试、25 件原夹具及既有研究记录保持原字节。尤其保护 storage/services/native_provider/reconciliation、dsat_types/projection/flow、原检查器和 migrations。主工程无 Git 元数据，采用逐文件哈希核对。当前八个拟新增路径均不存在，拟执行根和 DB 子目录也不存在，检查结果收入本轮来源锁。

未来执行以 `-B` / 禁写 bytecode 方式启动 Python；临时 JSON、日志、IPC 和测试数据库集中于专用执行根。任何需要修改旧文件的发现，都形成最小差异并重新审定。

## 5. 历史约束

成熟 SQLite 事务、CAS、持久幂等与工作流工具的归属保持原判；本申请属于限定范围的工程集成。新增候选机制仍须单独满足具体输入族、固定度量、最强适用通用方法、必要代价和严格差距的分离门。

T3、A/B/AB/W、旧 CLOSED/1 原义和既有淘汰结论沿用；COL2026 主动检索暂停，FS23 延期，VPass 废弃。S3-A 只记录数学/条件性历史与保守责任，`native_admission=SOURCE_OR_REFINEMENT_GAP`，`global_complete=false`。
