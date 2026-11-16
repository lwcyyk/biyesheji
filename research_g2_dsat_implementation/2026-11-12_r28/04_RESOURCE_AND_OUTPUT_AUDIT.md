# 资源与输出审计

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助实际离线调用与只读证据审查；独立外部核验待取得。本轮源码、Runner、测试及fixture修改均为0。

**R28_RESOURCE_BUDGET_SATISFIED=true；RESOURCE_BUDGET_EXCEEDED=false。** 本轮入口因读取策略错误失败，已声明数值额度均未超额；预算内与测试成功分别登记。

| 计量 | 本轮实际 | 上限 | 判定 |
|---|---:|---:|---|
| direct_runner_invocations | 1 | 1 | 满足 |
| memory_SQLite_A1 | 0 | 32 | 满足 |
| memory_SQLite_H1 | 0 | 0 | 满足 |
| memory_SQLite_D1A | 0 | 8 | 满足 |
| memory_SQLite_total | 0 | 40 | 满足 |
| memory_SQLite_peak | 0 | 32 | 满足 |
| execute_calls | 0 | 376 | 满足 |
| rollback_calls | 0 | 1 | 满足 |
| file_SQLite | 0 | 0 | 满足 |
| subprocesses | 0 | 0 | 满足 |
| network | 0 | 0 | 满足 |
| Python_threads_created | 1 | 12 | 满足 |
| Python_thread_peak | 2 | 6 | 满足 |
| main_seconds | 6.639436 | 120 | 满足 |
| all_output_paths | 11 | 13 | 满足 |
| all_output_directories | 2 | 2 | 满足 |
| all_output_logical_bytes | 50090 | 2097152 | 满足 |
| max_log_bytes | 251 | 65536 | 满足 |

主进程峰值working set39,211,008B（约37.39MiB）；RAM数值硬额原合同未设，nativeOS线程峰值、VFS/物理磁盘IO仍未测。源码计量6.639436s，外层约7.059s；该值是失败入口成本，未取得完整68回归成本。

内存连接A1/H1/D1-A各0、execute0、rollback0、文件DB0、测试子进程0、测试工作线程0、新secret key/TLS0。只创建watchdog1，Python峰值2；mainfinally取消watchdog并恢复Thread.start的结论由已到达的冻结控制流及最终结果生成支持；本轮额外OS清理实验0。

## 输出路径

实际生成11个文件、2个目录（根+run）、50,090B逻辑内容，全部位于13路径白名单；D24两文件缺席。receipt只读，调用槽/新run独占，索引只写新R26根。原始manifest在sources/RUN_ARTIFACT_MANIFEST.json，后处理未改写运行文件。

全部新结果文件nlink=1，且底层(st_dev,st_ino)均不与旧T33对象重合。outside_writes=0，未观察到旧目录fallback。R28_OUTPUT_ISOLATION_VERIFIED仅指本次实际失败路径的输出，D24成功路径未被动态覆盖。

读取策略发生一次READ_SCOPE_REFUSED，阻断导入cache探测；该异常已保留，没有通过扩大白名单、改源码或重试规避。具体被拒绝路径未进入原始audit，证据局限明确保留。

## 成本分层

- C_regression_68：一次失败入口约6.639s，用例执行0，完整68成本NOT_OBTAINED。
- C_special_54_historical：R25原计量38.4438399s，当前未重测。
- C_joint_evidence_review：本轮只读日志/源码/hash/组合与报告窗口，非孤立性能计量；窗口边界和NOT_ISOLATED状态见资源JSON。

真实部署、真实P1/P2成本均NOT_MEASURED，操作次数0。没有把离线框架数据当成生产性能。
