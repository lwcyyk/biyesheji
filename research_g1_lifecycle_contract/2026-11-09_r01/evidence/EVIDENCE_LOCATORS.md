# 关键论断到原证据的定位

字节身份见SOURCE_INDEX.json；以下行号绑定当前选定源码。文档中S编号的绝对路径均在该索引。历史验收文件内继续指向原批次，不读取秘密响应作为运行输入。

| 论断 | 原始位置 | 采用范围 |
|---|---|---|
| 有限链与当前持久链缺少研究选择接口 | [ALGORITHM_RUNTIME_MAP](D:/毕业设计/mainline_research_closure_v1/ALGORITHM_RUNTIME_MAP.md:25)、[serve](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/services.py:277)、STATIC_IMPORT_INSPECTION.json | 选定源码/入口；动态扩展另审 |
| 有限关系检查不证明外部适配器 | [check_relation](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/abstraction.py:6) | finite_table_relation_only；bindings callable检查 |
| 模型证据是条件证据 | [contract](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/a/evidence.py:18) | 登记假设、当前scope，MODEL_CONDITIONAL |
| B原生效果域必须分区 | [分区检查](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/b/model.py:56) | overlapping/correlated不在当前语法 |
| 接纳、来源、预算与放行 | [admit](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/storage.py:197)、[release](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/storage.py:227) | 本地事务；原生效果上界单列 |
| 结果绑定与撤回隔离 | [record](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/storage.py:261)、[revoke](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/storage.py:284) | 原origin、当前active及指定phase |
| 发送机会先记账 | [reserve](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/native_http.py:101)、[call](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/native_http.py:189) | reserve先于open；AS效果另证 |
| actual_sends的计数来源 | [reconcile_query](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/native_provider.py:155)、[reconcile_enumeration](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/native_provider.py:195) | 本地requests COUNT |
| dispose完整调用最多三请求 | [dispose分支](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/native_provider.py:53)、[record_disposal](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/storage.py:329) | RT revoke，AT UserInfo/内省；非实际RT刷新 |
| 同账户乙的创建暂停 | [admit](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/storage.py:214)、[release](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/storage.py:240)、[合成用例](D:/毕业设计/auth-lifecycle/tests/test_reconciliation.py:89) | issue/refresh暂停，已有UserInfo可接纳 |
| 乙保留与条件关闭 | [context](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/storage.py:379)、[save](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/storage.py:397)、[make_receipt](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/reconciliation.py:10) | 单未知、指定操作/路径与源前提 |
| 当前在线恢复 | [Controller.recover](D:/毕业设计/auth-lifecycle/src/auth_lifecycle/online_state/services.py:70) | 当前权威、显示缓存；通用备份恢复另证 |
| M2报警修订与UNKNOWN保留 | [M2验收](D:/毕业设计/mainline_native_casdoor_v1/ACCEPTANCE_REPORT.md:7) | 原4轨迹、原报警、离线修订与单独补核分别保持 |
| 576校准及A/AB未激活 | [RESULTS](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md:24)、S03连接图 | 历史known-contract单路径，当前0重跑 |
| 一般多尝试容量与标准流 | [PAPER_MODEL_AND_CASES](D:/毕业设计/research_main_innovation/main_topic_selection/ae_multi_attempt_revocation_review_2026_11_09/PAPER_MODEL_AND_CASES.json) | C1—C7、P1/P2/E1—E7；当前未接一般流实现 |
| WC-2最新裁决 | [DECISION](D:/毕业设计/research_main_innovation/main_topic_selection/ae_account_workcopy_contract_audit_2026_11_09/DECISION.json) | 工程保留；强组合覆盖与严格实例缺失 |

PDF相关页、版本关联与哈希见PDF_READ_SCOPE.md。实际阅读范围和工具边界见READ_SCOPE_AND_TOOLING.md。
