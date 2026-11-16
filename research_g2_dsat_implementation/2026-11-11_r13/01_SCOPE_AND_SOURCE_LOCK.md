# G2-R13：范围、来源与继承

日期：2026-11-11，Asia/Shanghai。当前对话内知情模型辅助静态源码审查。外部独立安全核验待取得。本轮为 H0，交付设计和授权申请；工程源码修改、项目模块执行、项目测试、数据库连接、真实密钥读取和服务调用均为 0。

## 当前结论

可信读取位置确定为 **`services.serve(role="authority")` 内部已经初始化的 `AuthorityStore` 所在进程**。Controller 当前持有 `protocol.Client`，缺少 Store 对象引用。推荐在 Authority 可信域内复用 R12 适配器，新增内部宿主守卫及最小摘要出口。现有 HTTP/RPC 和 Controller 保持原合同。[S02:42–56,277–320]

`TRUSTED_HOST_INTERFACE_READY` 表示静态接线规格可供 H1 离线实施审查。真实身份发行、运行实例、调用入口和授权值仍待固定，`REAL_READONLY_CALL_READY_FOR_AUTHORIZATION=false`。H2 当前适合审查申请模板，尚未达到可执行授权申请的条件。

## 授权来源

本轮请求原文为 `C:/Users/a1887/.codex/attachments/e986e483-9ddd-47de-93ba-4543b75b9731/已粘贴的文本.txt`，其 SHA-256 见 `SOURCE_LOCK.json`。

请求第十一节规定 H0 当前允许，H1 需要独立代码和测试授权，H2 需要单独真实数据读取授权；第十二节限制服务启动、真实数据库与密钥访问、真实 Staging 调用、新在线端点、Schema 修改、项目测试、B2 和 S5。因这些明确限制，本轮将 H1/H2 固定为申请，等待相应后继授权。

用户 AGENTS 规定的创新分离门继续有效。本轮属于成熟读取与净化接口的工程接线审查，算法创新资格沿既有裁决。

## R12 实际证据复核

R12 目录实际有 20 个文件；全部报告和差异文本已读取，全部 JSON 完整解析。大体量 JSON 逐记录核对结果、范围、字段和调用元数据；原始秘密夹具以既有摘要固定，公开报告避免复写哨兵值。记录在 `sources/R12_EVIDENCE_REVIEW.json`。

| 项目 | 实际核对结果 | 本轮证据性质 |
|---|---|---|
| 最终原始结果 | `2026-11-10_r12_b1/run_004/RESULTS.json` 与 R12 的 `B1_TEST_RESULTS.json` 摘要一致 | 静态文件核对 |
| 冻结用例 | 36 项；33 项 B1 PASS；B15/B27/B28 为 BLOCKED 且 executed=false | 继承 R12 离线结果 |
| 内部检查 | 551 条，全部 satisfied=true | 重新汇总历史 JSON |
| 差异与当前代码 | diff 的 579/416/191 行分别与当前三个新 Python 文件逐行相同 | 文本比较，未执行代码 |
| 历史版本 | R12 锁定的 921 次历史哈希比对全部一致 | 本轮再次计算文件哈希 |
| 敏感出口、来源、并发 | 继承 canary CLEAN、来源绑定、4 线程 12 读结果 | 合成 reader/lock 范围 |
| 实际运行 | R12 真实 Authority 读取、生产写回、B2、S5 均为 0 | 保留原执行范围 |

R12 四轮失败/修复历史继续保留。run_001 为 32 PASS/1 FAIL，run_002–004 为 33 PASS；本轮未重跑这些用例。S1/S2 的历史 115 项、S3-A 的 46 项/39 子断言继续按原记录继承。

四轮RESULTS均已完整解析，stdout.log全文静态核读，结果摘要与原TEST_RUNS逐项比对，见 `sources/R12_RUN_RECORD_REVIEW.json`。失败记录保持原样。

R11 的 18 接口、40 字段、36 冻结用例和 B1/B2 分界已核读。R12 的 40 字段实际状态及 18 接口状态完整保留于证据 JSON；其中 16 项有 Staging/部分映射，1 项敏感 handle 扣留，23 项未导出或延期。生产 typed O、独立 o、CAS 和真实 S1 入口缺口持续存在。

## 本轮来源与定位规则

源码根：`D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/`。以下短 ID 仅用于本轮；行号绑定当前哈希。

| ID | 文件 | 核读范围 |
|---|---|---|
| S01 | storage.py | 全文，尤其 47–159 与 197–415 |
| S02 | services.py | 全文，尤其 Controller 42–159、serve 277–349 |
| S03 | protocol.py | 全文 |
| S04 | lab.py | 1–170；生命周期、密钥生成、配置权限及启动路径 |
| S05 | dsat_authority_read.py | 全文 579 行 |
| S06 | cli.py | 全文；现有命令与真实调用缺失 |
| S07/S08 | migration.sql / migration_2.sql | 全文 |
| S09/S10 | isolation_service.py / native_isolation_service.py | 全文；启动包装器副作用 |
| S11 | windows_isolation.py | 文件哈希与定向符号定位；延用 R11 的隔离前提，不声称重新完整核读或运行验证 |
| T01/T02 | test_dsat_authority_read.py / run_dsat_authority_read_tests.py | 全文；静态核对测试范围及审计边界 |

`sources/SOURCE_EXCERPTS.md` 保存关键带行号摘录；`SOURCE_LOCK.json` 固定源文件、请求和继承材料摘要。`sources/PRECHECK_LOCK.json` 保存初始 921 次比较和 280 个限定工程/历史文件快照。交付时再次比较这些范围，结果见 `sources/DELIVERY_QA.json`。

SQLite 官方滚动文档已定向读取并保存四份 HTML，获取时间、URL、哈希和阅读段落见 `sources/OFFICIAL_SQLITE_SOURCES.json`。这些资料支持接口机制判断，实际运行 SQLite 版本、编译选项、文件 ACL、WAL 状态和部署身份保持待验证。

## 状态分层

继承：`S1_S2_OFFLINE_COMPLETE`、`S3A_SYNTHETIC_TESTS_PASSED`、`S3B1_IMPLEMENTED`、`B1_SYNTHETIC_TESTS_PASSED`。

本轮取得：`TRUSTED_HOST_IDENTIFIED`、`READONLY_CALL_GRAPH_REVIEWED`、`B1_SECRET_BOUNDARY_REVIEWED`、`HOST_WIRING_SPEC_READY`、`H1_READY_FOR_IMPLEMENTATION_REVIEW`，范围均为静态规格。

继续保留：`H2_AUTHORIZATION_PENDING`、`REAL_READONLY_CALL_NOT_RUN`、`S3B2_IMPLEMENTATION_BLOCKED`、`S5_NOT_AUTHORIZED`、`SOURCE_OR_REFINEMENT_GAP`、`ANALYSIS_ONLY`。`H2_READY_FOR_AUTHORIZATION_REVIEW` 的可执行含义当前为 false。

A/B/AB/T3、数学正确性、算法原创性和实现资格沿原判。COL2026 主动获取暂停，FS23 延期，VPass 淘汰状态沿用。
