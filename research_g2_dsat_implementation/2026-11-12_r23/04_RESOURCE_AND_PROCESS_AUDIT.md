# R23资源、进程与历史保护

审查日期：2026-11-12（Asia/Shanghai）。过程：本对话内知情模型辅助静态源码、历史记录与文档取证；本轮运行证据为零，外部独立核验待取得。

## 授权额度与使用

研究者批准新增1次new54，自动重跑0，24/44回归本轮重跑0。实际suite启动0、剩余额度1；原3个SUITE_INVOCATION文件及其内容保持。没有第4个槽，也没有创建旧位置ADDITIONAL_APPROVAL_RECEIPT。

| 追加申请中的单次额度 | 上限 | 本轮测试实际 |
|---|---:|---:|
| own_children | 8 | 0 |
| concurrent_children | 2 | 0 |
| child_seconds_each | 10 | 0 |
| child_seconds_total | 60 | 0 |
| file_SQLite_connections | 104 | 0 |
| per_case_connections | 2 | 0 |
| state_test_keys | 2 | 0 |
| TLS_test_materials | 2 | 0 |
| SSLContext_loads | 2 | 0 |
| private_directories | 64 | 0 |
| file_paths | 512 | 0 |
| logical_output_bytes | 67108864 | 0 |
| test_threads_peak | 4 | 0 |
| threads_created | 16 | 0 |

两轮new54累计授权为：子进程16/并发2、窗口总120s、文件SQLite208、state key4、TLS材料4、SSLContext4、目录128、文件路径1024、逻辑输出128MiB、线程创建32/峰值4。原new54的历史数值保留，未算入R23新运行次数。历史败者17.953秒窗口的计量缺项沿用，追加预算没有将其改写为已验证的单进程10秒结论。

申请及R21补充合同没有单列new54聚合SQL语句数、内存字节数、锁申请次数上限。本轮如实标为未单列，没有从正常生命周期23条SQL或B2生产预算推造suite额度。静态源码有300秒timer、child剩余10秒wait、超时后5秒wait、每stream4096B、journal32768B、source64文件等约束；它们与申请数值分别登记。物理磁盘峰值、内核线程峰值和VFS开销保留NOT_MEASURED。

**RESOURCE_BUDGET_VALID=BLOCKED_BY_OUTPUT_SCOPE**；已声明单次额度与R21源申请一致，关键阻塞为当前输出路由。测试资源实际0，`RESOURCE_BUDGET_EXCEEDED=false`。

## 进程及清理

没有suite、测试子进程、SQLite连接/SQL、测试key/TLS材料、实例锁、Stop Event或测试线程创建。无需终止、wait或回收测试子进程；本轮清理对象集合为空。未枚举、终止历史进程。文档读取工具/Python摘要辅助进程单列为静态取证活动，未计成测试子进程或suite。

本轮输出仅R23报告及JSON/静态证据，无测试DB/key。文档数量和字节在`HISTORY_INTEGRITY_FINAL.json`单列，保持与测试资源计数分离。

## 真实边界

未启动Authority/Controller/Provider/Casdoor；网络监听、RPC、正式部署根读写、真实数据库、真实密钥、P1a/P1b/P2、S3-B2/S5操作均0。未安装依赖，未修改工程文件。历史合成秘密文件仅作元数据登记，内容与秘密摘要保持私有。

## 历史完整性

本轮基准保留R22目录39份文件、旧输出391份公开文件，及原1194份受保护文件；原始五份源码快照和13份当前源码/fixture锁也核对。前后SHA比较见`HISTORY_INTEGRITY_FINAL.json`。13份历史合成私有材料仅比较路径/长度，无内容字节保持声明。R22三份RESULTS、首轮stdout错误堆栈、8份首轮code_snapshot、旧索引、SOURCE_LOCK与三轮invocation均在公开字节保护清单中。
