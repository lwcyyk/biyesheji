# R31范围与R30事实绑定

本轮为当前对话内的模型辅助工程修复及静态审查。授权来自用户R31全文和R30最小修复申请。独立外部核验待取得。当前 `actual_suite_runs=0`、`execution_authorized=false`。

| R30实际事实 | 继承处理 |
|---|---|
| 唯一Runner调用1次，native退出1，自动重跑0 | R30额度剩余0，记录原字节保留 |
| A1/H1/D1A原断言20/24/24 PASS | 68 PASS的日志重建证据继续有效；每例原日志行号保留于R30 |
| A17原断言和D24正例实际通过，双JSON摘要匹配 | 本轮保持原测试、装配顺序和双JSON边界 |
| D1A结束后的来源检查触发DEPENDENCY_ORIGIN_MISMATCH | 完整回归和联合122合同继续未验收 |
| RESULTS、MODULE_ORIGINS、RESOURCE_LEDGER及TEST_RUNS缺件 | R30缺失计数保持UNKNOWN，R31资料与旧运行分开 |

完整读取R30目录22份材料，索引见 `sources/R30_READING_MANIFEST.json`。原始失败位置和原堆栈继续引用R30 `sources/FAILURE_ANALYSIS.json` 与旧run的 `EARLY_FAILURE.json`。本轮单文件工程修改为 `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py`，修改前原始字节保存在 `sources/RUNNER_BEFORE.py.bin`。

修改前SHA-256：`27c29f6e8b346799b9ac0492d2e7377326113dbe3a44c53dd33207fec8dd9514`。修改后SHA-256：`7cc4821cb8316f3f7c4fc88b889a9a648c66e8e1ba6181b34ef6ef80d2ca9a7e`。完整差异见 `sources/R31_RUNNER.patch`，函数范围见 `R31_CODE_DIFF.json`。

历史基线在修改前核对了R30原2146项。该清单包含本轮获准修改的Runner；后续将这一项单列为可变源锁，并保留最初清单 `sources/INITIAL_PREPATCH_BASELINE.json`。移除这项可变源后，历史及新增R29/R30保护范围共2176份文件，全部按原SHA核对。R30失败记录、原stdout、SOURCE_LOCK和R25结果均原字节保持。

42份工程源码、3份原测试、10份fixture、5份扩展源、24份运行时指纹和394份有限读取目录项已核对；修改数均为0。唯一Runner变化属于测试基础设施维护，范围覆盖来源诊断、失败持久化、日志fsync和新命名空间；原授权消费协议保持。

本轮执行的是文件读取、哈希、AST分析和文档生成。Runner、测试模块、测试子进程、SQLite连接、密钥生成、真实服务、网络监听、RPC及P1/P2操作均为0。候选机制实现门保持原合同。
