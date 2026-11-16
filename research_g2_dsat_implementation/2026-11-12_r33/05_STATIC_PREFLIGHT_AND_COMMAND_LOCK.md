# 静态准入与禁用命令锁

48组静态检查中47组满足，1项关键容量条件未闭合：FULL_REQUIRED_OUTPUT_CAPACITY_BOUND。因此R33_STATIC_PREFLIGHT_BLOCKED=true，R33_STATIC_PREFLIGHT_PASSED=false，R33_REGRESSION_COMMAND_READY=false。

已有静态证据覆盖来源规则、未知来源拒绝、原始断言与框架分层、2MiB总额、统一路径预算、最终文件隔离、零磁盘临时空间、609条历史语义保留、UNKNOWN、历史及A17/D24等。Runner/test导入、单项/suite和测试子进程执行0。

当前Runner SHA：`5b751f4d6cf654f928d6c0053bab7fbc23caaaa1975a55816968f39aa35237c5`。已冻结精确12项argv、Python/cwd、42工程、24运行时、3测试、10fixture、68ID及20/24/24顺序，控制文件摘要绑定在 `R33_REGRESSION_COMMAND_LOCK.json`。字段command_executable=false、execution_authorized=false、actual_suite_runs=0、R32_RUN_BUDGET_REMAINING=0。

以下只展示禁用命令的准确目标，当前执行条件未满足：

```powershell
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -I -B -X utf8 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py' --suite regression68 --output-root 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r33\verification_runs' --approval-ref 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r33\verification_runs\RUN_APPROVAL_RECEIPT.json'
```

工作目录为 `D:\毕业设计\auth-lifecycle`。未来独立调用额度至多1、自动重跑0，时间120秒、13路径/2MiB、SQLite总40活跃32、SQL execute376/rollback1、线程创建12/峰值6等均沿用；当前预算未被扩大。

verification_runs/run/实际receipt均不存在。仅有blocked且approved=false的审阅模板，当前没有可供执行的批准凭据。解除容量阻塞后须重发相互一致的新锁并取得独立授权。

源码静态工具最初将既有str.replace误判为文件替换操作；后按调用对象及写入函数控制流修正。原3处字符串归一化/净化调用保持，文件rename/覆盖权限保持原禁令。此为审计检查器修正，动态测试次数持续为0。
