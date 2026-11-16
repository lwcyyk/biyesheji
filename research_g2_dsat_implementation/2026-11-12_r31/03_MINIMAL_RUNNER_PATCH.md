# 单文件补丁与保持性质

批准范围内仅修改Runner一个已有工程文件。新增13个内部辅助函数，改动9个既有函数；原42份工程文件、测试和fixture保持。逐函数范围及行号见 `R31_CODE_DIFF.json`；逐行补丁见 `sources/R31_RUNNER.patch`。

| 改动 | 定位与责任 |
|---|---|
| 原始来源观察、文件来源和派生模块分类 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:460`、`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:483`、`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:512` |
| 快照与拒绝诊断先落盘 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:569` |
| 有界追加检查点、分层错误及独立发布 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:203`、`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:234`、`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:276` |
| 每个原断言的持久化 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:819` |
| 分阶段收尾、最终逻辑提交 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:898`、`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:996` |
| 日志flush/fsync与最末异常边界 | `D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:729`、`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:1096` |

`controls`、`State.preflight`、`load_group`反向替换R31命名空间后，其AST与原版本逐项相同。A1→H1→D1A顺序、A17前置导入检查、测试ID和原测试配置保持。新增导入仅为已在394目录中的 `importlib.machinery` 与解释器内建 `_imp`，对cryptography的提前导入数为0。

以下函数AST与旧版本完全相同：`State.audit`、`State.block_bound_cache_probe`、`State.deny_read`、`checked`、`State.connect_memory`、`State.sql`、`State.close_connections`、D24Projection进入/退出、ProjectionFile写入、ProjectionRead读取、OrderedSuite运行以及原SQL包装关键方法。原EACCES缓存回退、未知读取拒绝及生产读取白名单保持。

D24继续只生成并投影两份原JSON，目标字节SHA保持，原输入只读；Path及CONFIG恢复路径保持原AST。来源检查仅按冻结规则识别，运行中来源锁扩展数为0。

静态审查额外处理了内存测量的延迟导入：先执行原peak_memory观测，再取得最终来源快照，保证ctypes.wintypes被纳入最终集合。对整个文件仅做AST解析与源码审查；修复的实际Windows行为待动态验证。
