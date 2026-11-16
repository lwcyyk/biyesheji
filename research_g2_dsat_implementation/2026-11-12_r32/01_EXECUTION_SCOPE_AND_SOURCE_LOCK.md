# R32执行范围与来源锁

本轮实际启动一次冻结的68项离线Runner，native退出1，自动重跑0，剩余额度0。执行授权来自用户R32全文，原文与其原字节副本分别绑定于 `sources/PREEXECUTION_AND_HISTORY.json`、`sources/RESEARCHER_RUN_AUTHORIZATION.txt`。当前对话内模型辅助执行和只读审查；外部独立核验待取得。

20组执行前核验全部通过：42工程源、Runner、24运行时指纹、394项有限运行时文件目录、3原测试、10fixture、68项身份、命令及历史均匹配。完整读取R31目录30份静态材料。工程源码、Runner、测试和fixture修改数均为0。

Runner SHA-256为 `7cc4821cb8316f3f7c4fc88b889a9a648c66e8e1ba6181b34ef6ef80d2ca9a7e`。42工程源摘要为 `621f69552f8fcb20aa0db142c5d3b7783e5bd9a641a03559a25b1247099cffb9`，与R25的42项source_closure逐路径/摘要相同。R31修改前原始字节及原差异锁保持。

工作目录为 `D:\毕业设计\auth-lifecycle`。本轮实际argv与冻结命令、SUITE_INVOCATION_01和RUN_START逐项相同：

```powershell
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -I -B -X utf8 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py' --suite regression68 --output-root 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r31\verification_runs' --approval-ref 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r31\verification_runs\RUN_APPROVAL_RECEIPT.json'
```

实际运行目录为 `D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r31\verification_runs\r31_regression68_001`，沿用R31冻结名称；R32总结资料存入本目录。受信准备只新建R31 verification_runs及一份绑定新授权的只读receipt；Runner独占创建唯一调用槽和后续证据。命令没有新增参数、外部重定向或失败重试。

Runner开始时间 `2026-11-12T09:49:23.851686+00:00`；退出观测时间 `2026-11-12 09:50:17 UTC`，后者精度为秒。直接工具返回的native退出码为1，见 `sources/NATIVE_INVOCATION_RESULT.json`。该次调用额度已用；R30旧额度继续为0。

静态审查脚本最初读取了R25实际结果中不存在的source_digest顶层字段，随后按真实source_closure清单完成比较。该只读取证修正发生在Runner启动前，suite额度当时仍为0，过程记入准入资料。

本轮真实部署、网络监听、业务数据库、真实密钥、RPC和P1/P2执行均为0。保留既定实现分离门；本次仅执行已经冻结的离线验收。
