# 静态准入与准确命令

静态结论为 `R31_STATIC_PREFLIGHT_PASSED`：38组检查通过。方法为AST等价、明确的异常/路径/调用流审查及源文件SHA；结果见 `R31_STATIC_PREFLIGHT.json`。可重现静态工具存于 `sources/STATIC_AUDIT.py.txt`，其目标输入只被读取和AST解析。动态测试次数为0。

原manifest的物理行顺序为D/A/H，原执行顺序由PHASES分组过滤确定为A1/H1/D1A。静态检查按实际执行规则对照68项ID，完整保留原manifest行。旧历史清单中的可变Runner也单列处理，2176项其余文件全部保持。

新源码SHA：`7cc4821cb8316f3f7c4fc88b889a9a648c66e8e1ba6181b34ef6ef80d2ca9a7e`。
命令锁SHA：`4aa868673cfb67abf02fabce326aa1300c61c160603b621e31209a65d92a9888`。
工作目录：`D:\毕业设计\auth-lifecycle`。
Python：`C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`，3.12.14 AMD64；SHA `f8b45d63047da9d9adf09892e4cc4317b859e86a93a478cc9616bc69d3b176e5`。

以下准确argv仅用于下一轮独立授权，当前未执行：

```powershell
Set-Location -LiteralPath 'D:\毕业设计\auth-lifecycle'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -I -B -X utf8 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py' --suite regression68 --output-root 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r31\verification_runs' --approval-ref 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r31\verification_runs\RUN_APPROVAL_RECEIPT.json'
```

Runner独占管理日志，未来调用保持原命令，无额外runner参数或外部重定向。批准后由受信准备步骤新建verification_runs，并放置绑定命令锁、资源锁、源码摘要及新用户答复哈希的receipt。当前只有 `sources/APPROVAL_TEMPLATE.json`，其approved=false且有明确待填授权字段；未来运行目录和实际receipt均未创建。准确argv本身无占位符。

| 未来单次上限 | 冻结值 |
|---|---|
| suite / 自动重跑 | 1 / 0 |
| 原测试 | 68，20/24/24 |
| 时间 | 120秒，含main准入；合作式watchdog及每次写入截止 |
| 内存SQLite | A1≤32，H1=0，D1A≤8；总≤40，活跃≤32 |
| execute / rollback | ≤376 / ≤1 |
| Python线程 | 创建≤12，峰值≤6，含watchdog |
| 子进程、文件DB、真实网络/RPC、真实密钥/TLS | 0 |
| 运行路径、目录、输出 | 13、2、总≤2MiB，每日志≤64KiB |
| RAM字节硬限 | 原合同未分配；实际测量按可得范围记录 |

来源、fixture、命令、摘要、未知读取、缓存绑定、投影、清理或资源条件失败均使调用停止并保留非零或未完成状态。唯一额度一经启动即消耗，自动恢复重跑数为0。实际运行资源尚未产生，future实际数据继续UNKNOWN。

当前 `execution_authorized=false`、`actual_suite_runs=0`、`R30_RUN_BUDGET_REMAINING=0`。下一次运行的独立批准要求来自本轮用户合同第十一节和第十五节。
