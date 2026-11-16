# R25执行范围与版本锁

执行与审查日期：2026-11-12（Asia/Shanghai）。证据类型：本对话内知情模型辅助实际离线运行、源码/日志核对；外部独立核验待取得。

## 授权与唯一执行

研究者通过本轮附件明确批准R24冻结版本的一次new54及其临时资源。真实批准原文完整保存于`sources/RESEARCHER_RUN_AUTHORIZATION.txt`，其字节与原附件相同。新`R24/RUN_APPROVAL_RECEIPT.json`绑定该实际回复摘要、准入稿摘要、解释器摘要、输出根、run ID、一次额度和自动重跑0；它是本次获准的新增控制记录，原历史批准文件未改。

实际执行 **1次**；自动重跑 **0**；本轮源码、fixture修改 **0**；原68项及122项完整suite执行 **0**。唯一额度已经消耗，剩余 **0**。

## 最后静态准入

完整读取R24原有22份材料并完成14组最终核验：准入摘要、8份指定代码/5份fixture/42份源闭包、原SOURCE_LOCK、冻结命令、28项历史QA及清单、R22/R23/1194份保护文件、54项ID与预期、AST、Python、工作目录、新结果与receipt尚未存在、预算、一次额度及新R25总结根。全部满足后才创建本轮receipt并执行。

准入稿SHA：`3635abfb2d6c02e26fb76da547ba947bb45865dc7cf7afca416a5c9e93bb3698`。解释器：`C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`，版本`3.12.14 (main, Aug 25 2026, 14:01:42) [MSC v.1944 64 bit (AMD64)]`；摘要`f8b45d63047da9d9adf09892e4cc4317b859e86a93a478cc9616bc69d3b176e5`。实际源码与RESULTS.code、fixture与RESULTS.inputs逐字节对应。

| 文件 | 本轮实际SHA-256 |
|---|---|
| dsat_authority_live.py | `9c1099dd9ea83feeb60c92bf106a3c4a4ec88df58c10ca0cba94e0da7aba81bd` |
| dsat_authority_lifecycle.py | `4a1f361713e4e8a56766cebfc91284e4e0ae2012f58f698efe82ef90f13b16b7` |
| dsat_windows_runtime.py | `d0e6f281df41335c9aada15b1f700a8eb8decb6b2a13dae6ad21101645602e81` |
| test_dsat_authority_live_lifecycle.py | `7b0564964a880746db58df9adfb611d5ce3be8f4aef2b976c96c2992e5e5ba91` |
| run_dsat_authority_live_lifecycle_tests.py | `527e9728b0485ce3b01a1b555b39a121085505d017ad8598c8923056257c1847` |
| services.py | `b4589916889a1c287a19560cc94fbb2b3dd0b058d6f08314d8f60997f50c86f6` |
| storage.py | `6026d4ef80295aa1a0ede4114253eeb7c2850244a51020b3e4caa7d6c4ec960e` |
| run_h2_authority_service.py | `dfada9a27fb5be95919775bda345478a6df50fd2930a9999d5e98710e7a7f25b` |

## 实际命令与路径

调用了已锁定的`sources/VERIFICATION_COMMAND.ps1`一次，其内部Python argv与R24准入逐项完全相同：

```text
["C:\\Users\\a1887\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe", "-B", "D:\\毕业设计\\auth-lifecycle\\scripts\\run_dsat_authority_live_lifecycle_tests.py", "--suite", "new54", "--output-root", "D:\\毕业设计\\research_g2_dsat_implementation\\2026-11-12_r24\\verification_runs"]
```

工作目录：`D:\毕业设计\auth-lifecycle`。输出根：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs`。唯一run：`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r24\verification_runs\r24_new54_001`。外层包装仅额外保存开始/结束与真实`$LASTEXITCODE`，没有改变测试argv、拆分suite或调用其他测试。

主入口时窗：2026-11-12T10:51:41.315852+08:00 至 2026-11-12T10:52:19.758530+08:00。解释器实际退出码 **0**；外层包装记录见`sources/EXECUTION_WRAPPER.json`，测试stdout/stderr保存在冻结根。

## 历史与真实边界

执行前固定R22/R23/R24原有73份记录，执行后全部同SHA。R22旧3个调用槽、原TEST_RUNS、F24 ERROR与跨进程见证保持；新TEST_RUNS只在R24独立验证根创建。

真实Authority/Controller/Provider/Casdoor服务、真实业务DB/key、网络监听/RPC、正式部署根、P1a/P1b/P2、S3-B2/S5操作均0。临时合成DB、测试key/TLS及8个有限worker均属于已批准的new54合同。运行曾导入materials/storage/services源码来完成离线验证；这与启动真实服务分别记录。
