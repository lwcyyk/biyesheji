# 输出与资源隔离

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助单文件测试基础设施实现与静态审查；本轮未导入或执行新Runner，未运行--help、测试、SQLite或测试子进程。外部独立复核待取得。

## 固定根与13个路径

根：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r26\verification_runs`；唯一run：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r26\verification_runs\r26_regression68_001`。接受执行前，新根只能含RUN_APPROVAL_RECEIPT.json。Runner只读该批准，独占创建运行槽与run，x/xb创建结果，拒绝覆盖/未知run/旧目录fallback。

R26原12个运行路径加1份外置receipt调整为13个根内路径，总数仍13。receipt随所有运行记录统一进入新根，未增加净文件额度。精确清单见R27_REGRESSION_RESOURCE_LOCK及OUTPUT_ROUTE_AUDIT。

stdout/stderr/suite日志由Runner自己创建并重定向；未来命令不要再外部重定向到同名保留路径。所有接受执行后的失败、来源、fixture/源码摘要、统计、费用和索引均使用同一写入边界。未通过准入时只返回固定拒绝消息/exit2，未建立suite或输出状态。

checked校验绝对路径、规范组件、根/精确文件名、重解析点与硬链接。audit拒绝根外写入、非RUN目录创建、删除/移动/链接/权限修改、私密DB/key文件、网络和子进程。历史4个T33链接仅有只读hash核验例外，无法作为新输出或D24输入。

## 冻结限额

| 项目 | 上限/规则 |
|---|---|
| 直接suite / 自动重跑 | 1 / 0，需下一次独立批准 |
| 总soft时限 | main入口起120秒，包含控制/版本预检、测试与输出 |
| A1 / H1 / D1A memory SQLite | 32 / 0 / 8，总40，同时最多32，组间关闭 |
| SQL wrapper execute / rollback | 376 / 1，按R26原实测提案冻结 |
| 文件DB / 子进程 / 真实网络服务 / 新key/TLS | 0 |
| Python线程创建 / 峰值 | 总12（含watchdog1）/含主线程峰值6 |
| 目录 / 根内文件 | 根及run共2 / 13 |
| 输出逻辑字节 / 每日志 | 2MiB / 64KiB |
| 源码重复快照 | 0，只保存摘要与原定位 |

原始A1内存DDL/DML只在自有fixture库允许，H1 FakeConnection保持，D1A使用固定公开AES向量。SQL工厂只能在指定phase创建:memory:，禁止文件DB/ATTACH/DETACH/扩展及额外诊断SQL，原测试接口不变。

原合同没有RAM数值硬额，保留null并以本进程GetProcessMemoryInfo尽力计量；无法测量就记录NOT_MEASURED，不虚构值。Python线程界不代表全部OS原生线程界。VFS、断电、恶意同SID/管理员并发替换、卷回滚和不可中断I/O的硬退出时限没有由本轮静态分析取得证明。

预算耗尽或存储不可写会停止/保留不完整记录并非零退出；完整错误日志依赖可写且有额度的证据存储。既有原文和失败证据均不作为fallback写入目标。

本轮上述运行资源消耗均0，验证根、实际receipt、SQL连接、测试key/TLS、timer、投影副本及测试线程未创建。
