# G2-R11：范围、来源与继承

2026-11-10，Asia/Shanghai。当前对话内知情模型辅助静态源码/接口审计；外部独立安全核验待取得。

## 本轮结论

已形成18项接口清单、40项字段映射、18类writer/外部变化、12项迁移门和36项未来用例。最小B1方案限定为**可信域内的非秘密staging导出适配器开发及离线reader-double测试**。当前工程源码、运行状态和既有结果保持原字节。

`S3B_INTERFACE_INVENTORY_COMPLETE`、`REAL_STATE_MAPPING_DEFINED`、`WRITER_COVERAGE_REVIEWED`、`S3B_READONLY_SPEC_READY`、`S3B1_READY_FOR_IMPLEMENTATION_REVIEW`适用于本稿明确的静态范围；实际部署writer全集仍为`WRITER_COVERAGE_GAP`。B1执行授权待取得，B2仍阻塞，S5未授权。

## R10继承

完整读取R10七份报告与四份主要JSON，核对其21件QA清单条目及QA自身；清单条目全部匹配。五轮原始结果文件按既有哈希核验。继承779项旧输入再次逐件匹配，R10新增源码与夹具另行固定。

R10最终run_005的46/46顶层测试、39/39必需子断言、10项并发、14个崩溃位置及失败历史沿实际记录继承。本轮测试/检查器/求解器运行0，数据库文件内容读取和SQLite连接0；R10数据库清单仅按JSON资料阅读，未重新检查数据库内部。R10的67.640秒等数值保留合成工程口径。

## 来源索引

`sources/SOURCE_INDEX.json`记录28项源码/合同的路径、SHA-256、行号/符号与阅读范围。R10三个模块的完整源码复用本对话实施时的阅读，当前哈希和完整AST再次核对。源码定位在本轮使用独立短ID：

| ID | 来源 |
|---|---|
| C01–C03 | storage.py、services.py、protocol.py |
| C04–C07 | native_provider.py、native_http.py、materials.py、enumeration.py |
| C08–C10 | dsat_types.py、dsat_projection.py、dsat_flow.py |
| C11–C13 | R10 dsat_commit_types、dsat_commit、dsat_synthetic_store |
| C14/C15 | migration.sql、migration_2.sql |
| C16–C18 | lab.py、reconciliation.py、evidence_semantics.py |
| C19–C23 | isolation启动/配置/夹具及旧代码复制入口 |
| C24/C25 | 独立checker、旧agent评分消费者 |
| M01–M03 | G1-R02容量证明、精化证明及裁决 |

`STATIC_CALL_GRAPH.json`包含226个函数的静态调用语法与手工dispatcher连接，属于候选调用关系。它不证明实际加载副本、全部进程或AS执行图。

## 授权及历史边界

本轮只进行文本/JSON/哈希、静态AST、字段设计与文档取证。无项目模块导入、服务初始化、运行配置/密钥读取、SQL、备份、迁移、进程操作、测试、原生API、依赖安装或外部联系。新增文件仅在R11记录目录，未来B1新路径当前均不存在。

所有未来用例保持`NOT_RUN`，S3-B费用保持`NOT_MEASURED`。S1/S2/S3-A结果与A/B/AB/T3创新资格沿原裁决；成熟接线工作按工程集成管理。COL2026暂停、FS23延期、VPass废弃继续有效。
