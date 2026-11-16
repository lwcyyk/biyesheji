# R30执行范围与来源锁

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助真实离线调用及只读证据审查；工程源/Runner/测试/fixture修改0，自动重跑与额外测试0；独立外部核验待取得。

**本轮唯一直接入口调用已完成，native退出1。原68项断言全部通过，完整回归来源/资源/收尾验收尚未完成。** 唯一额度消耗，剩余0，未二次运行、改码或更换argv。

## 正式授权与静态准入

研究者本轮附件明确批准R29冻结版本一次68及其资源。实际原文保存于sources/RESEARCHER_RUN_AUTHORIZATION.txt；新receipt放在冻结R29验证根，绑定真实回复、command/resource SHA、source digest、一次/零重跑及全部真实权限false。R29历史execution_authorized=false等字段保持原字节。

执行前完整读取R29原25份材料，17组最后核验全部满足：42工程源、24runtime、Runner、原3测试/10fixture、394代码读取清单、原38/33静态核对与manifest、控制锁、版本、68和顺序、旧结果及新root。没有用重算期望或修改锁解决差异。

## 实际版本/命令

Runner SHA：`27c29f6e8b346799b9ac0492d2e7377326113dbe3a44c53dd33207fec8dd9514`。工程摘要：`621f69552f8fcb20aa0db142c5d3b7783e5bd9a641a03559a25b1247099cffb9`。Python固定基准3.12.14 AMD64。当前42/24/3/10以及Runner执行后也匹配。

```text
["C:\\Users\\a1887\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe", "-I", "-B", "-X", "utf8", "D:\\毕业设计\\auth-lifecycle\\scripts\\run_dsat_current_build_regressions.py", "--suite", "regression68", "--output-root", "D:\\毕业设计\\research_g2_dsat_implementation\\2026-11-12_r29\\verification_runs", "--approval-ref", "D:\\毕业设计\\research_g2_dsat_implementation\\2026-11-12_r29\\verification_runs\\RUN_APPROVAL_RECEIPT.json"]
```

工作目录：`D:\毕业设计\auth-lifecycle`。argv与RUN_START及包装记录逐项相同。调用时窗`2026-11-12T08:30:57.6809082+00:00`至`2026-11-12T08:31:18.9757787+00:00`（UTC），外层约21.295s。PowerShell包装的最后JSON输出状态与Python native状态分别处理，验收采用native=1。

结果固定于`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r29\verification_runs\r29_regression68_001`。R30目录仅保存后续报告/索引/重建数据，原run文件未改写；没有把重建结果写成原run的RESULTS。

## 执行边界

三组原unittest依次完成20/24/24，A17和D24实际执行。随后在D1A_finished依赖来源核验失败。最终RUN_START、suite log、EARLY_FAILURE与两个D24副本保留，RESULTS/RESOURCE_LEDGER/MODULE_ORIGINS/TEST_RUNS尚缺。

真实服务、业务DB/key/RPC、P1/P2及S3-B2/S5不属于冻结测试程序，没有新授权或实测生产操作；原测试为自有内存SQLite、公开AES向量、假Store/transport/codec。最终audit计数器缺件，未伪造其完整运行数值。
