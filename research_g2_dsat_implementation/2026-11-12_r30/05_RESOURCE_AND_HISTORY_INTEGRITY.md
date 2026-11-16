# 资源与历史完整性

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助真实离线调用及只读证据审查；工程源/Runner/测试/fixture修改0，自动重跑与额外测试0；独立外部核验待取得。

## 资源证据

R30_RESOURCE_BUDGET_SATISFIED=false表示完整资源审计未取得；没有观察到RESOURCE_BUDGET_EXCEEDED。可直接核查的调用、时间、文件/字节界满足：

| 指标 | 实际 | 上限 | 状态 |
|---|---:|---:|---|
| direct_runner_calls | 1 | 1 | 已核对 |
| wrapper_wall_seconds | 21.29487 | 120 | 已核对 |
| output_paths | 9 | 13 | 已核对 |
| output_directories | 2 | 2 | 已核对 |
| logical_output_bytes | 11530 | 2097152 | 已核对 |
| max_log_bytes | 5745 | 65536 | 已核对 |

SQLite连接数、SQL/rollback次数、线程计数、主进程峰值RAM未持久化，保留null/NOT_PERSISTED。原历史19连接/376execute只能作参考，不作为本次实测数值。原32/0/8、总40、376/1、线程12/6的guard源和版本保持；该源层约束与缺失的actual counters分别记载。

mainfinally关闭自有连接、取消timer并恢复Thread.start位于已写EARLY_FAILURE之前，可由冻结控制流支持；缺少直接关闭计数和postcleanup meter。没有另做OS泄漏、库导入或P1/P2实验。

成本分开：R25_HISTORICAL_54_COST采用原38.4438399s且未重跑；R30_CURRENT_68_COST有外层约21.295s及各组三个unittest窗口，完整成功收尾成本未取得；R30_JOINT_REVIEW_COST为后续只读审查窗口，非孤立性能计量。真实部署和真实P1/P2成本NOT_MEASURED。

## 历史

2146份保护文件全部SHA匹配，变化0、缺失0。原42源、24criticalruntime、原3测试/10fixture、394清单以及Runner均保持冻结版本。R25原54PASS、R28退出1/68NOT_RUN、R29静态资料及历史SOURCE_LOCK均未改。

四份T33的内容hash、st_dev/st_ino、nlink、mode和FileAttributes前后一致；只读核验。所有9新输出nlink1且与旧对象身份不交叉。访问时间未冻结，比较范围不被扩大。

本轮获准新增为R29验证根9文件及R30报告/索引，合法新增单列，未误判为历史篡改。原私有合成材料继续元数据范围，没有读取秘密值或输出其摘要。
