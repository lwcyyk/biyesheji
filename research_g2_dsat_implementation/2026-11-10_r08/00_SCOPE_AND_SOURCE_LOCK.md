# R08：范围、基线与来源锁

2026-11-10（Asia/Shanghai）。当前对话内知情模型辅助源码审查、条件证明、并发/崩溃反例和实施设计。外部独立审计待取得。

## 当前结论

定义最小`dsat-commit/1`合同：全局状态/O双版本、独立提案幂等簿、不可变证明对象、原子义务覆盖变换和受限回执。S3-A只面向专用合成数据库，保存数学/条件结论及保守责任；真实C_native属于S3-B独立门。

S3_CONTRACT_READY、TRANSACTION_MODEL_DEFINED、OBLIGATION_PRESERVATION_CONDITIONAL、CRASH_RECOVERY_SPEC_READY均指本轮纸面规格。S3A_READY_FOR_IMPLEMENTATION_REVIEW；S3B_IMPLEMENTATION_BLOCKED、S5_NOT_AUTHORIZED、ANALYSIS_ONLY保持。

## 继承

R07原始229件资料逐件绑定，228件与其交付QA清单匹配，QA本身另锚定。S1/S2已实现、115项PASS、23自动包接受及4篡改包拒绝均只引用原记录；本轮项目测试/求解器/检查器运行0。其SYNTHETIC_CONTRACT、原生来源/持续D/前沿/部署缺口和成熟方法归属保留。

R05有限容量/流证明、R06实现、R04投影、R01局部证书/O/T-COMP及G1单次容量按已有实际阅读范围继承。T3与原A/B/AB/W语义不改；COL2026暂停、FS23延期、VPass废弃。

## 核读源

主工程`D:/毕业设计/auth-lifecycle`。C01 storage.py全文及精确窗口；C02 services.py的Controller/权限/恢复；C03 protocol.py；C04 reconciliation.py；C05 evidence_semantics.py；C06 native_provider.py；C07/C08 migration.sql与migration_2.sql；C09 dsat_flow.py的make_bindings/证明装配；C10 dsat_projection.py；C11独立检查器；C12/C13相关旧测试与消费者。

当前源码符号、行号、哈希/摘录及R07绑定见sources。SOURCE_LOCK仅文件/文档取证；不会连接真实数据库。实际运行SQLite/WAL配置仍是既有记录与源码声明，当前未重新测量。

## 三项关键发现

1. 当前只有authority_state.version；O由phase/window投影得到，独立O revision与S3 CAS不存在。
2.旧AuthorityStore.call对正常返回的拒绝/重复也继续写state/event并增版本。新S3拒绝/幂等语义不能直接套这层包装器。
3. R07证明的bindings.O_before来自投影提案，不是持久O读取。A08、A24的静态文件比较均显示5项输入O对应6项证明上下文O；必须分开base_O_digest和proof_context_O_digest。

## 权限与取证

仅文本、静态AST、JSON/哈希和文档处理；无新S3源码、SQL执行/迁移、运行状态读取、故障注入、项目模块导入/测试、NetworkX或检查器执行、原生API、秘密/账号操作、外发、新代理。静态表全部NOT_RUN，S3性能全部NOT_MEASURED。新材料只写本轮目录，旧源码/研究/实验不变。
