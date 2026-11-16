# R28执行范围与来源锁

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助实际离线调用与只读证据审查；独立外部核验待取得。本轮源码、Runner、测试及fixture修改均为0。

**唯一冻结入口调用已执行，native退出码1；68项用例尚未开始。** 按本轮规则，该调用消耗唯一额度，剩余0；自动重跑、单项重跑和额外54项执行均0。

## 正式授权与准备

本次研究者附件明确批准R27当前源码/命令/资源的一次68项。实际原文保存于sources/RESEARCHER_RUN_AUTHORIZATION.txt，与原附件同SHA。新receipt依R27模板在冻结R26验证根内独占创建，绑定真实回复摘要、命令锁和资源锁、构建摘要、max_suite_runs=1/auto0，真实权限位全false。R27历史execution_authorized=false等字段未改。

执行前完整读取R27原22份文件，完成18组最后核对，CURRENT_BUILD_MATCH、RUNNER_HASH_MATCH、TEST_SOURCE_MATCH、FIXTURE_HASH_MATCH、PYTHON_RUNTIME_MATCH均true。原34项静态及33项最终QA资料保持。动态失败暴露该静态覆盖中的缓存读取漏项，未发现源版本漂移。

## 冻结版本与实际命令

工程42文件摘要：`621f69552f8fcb20aa0db142c5d3b7783e5bd9a641a03559a25b1247099cffb9`。Runner SHA：`a9cb35bcce7d1439f45b2593a16c7fb2884117dd63d515eac7cf40e5d75eda70`。原3测试、10fixture及24运行时指纹前后匹配R25/R27。

实际argv完全相同：

```text
["C:\\Users\\a1887\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe", "-I", "-B", "-X", "utf8", "D:\\毕业设计\\auth-lifecycle\\scripts\\run_dsat_current_build_regressions.py", "--suite", "regression68", "--output-root", "D:\\毕业设计\\research_g2_dsat_implementation\\2026-11-12_r26\\verification_runs", "--approval-ref", "D:\\毕业设计\\research_g2_dsat_implementation\\2026-11-12_r26\\verification_runs\\RUN_APPROVAL_RECEIPT.json"]
```

工作目录：`D:\毕业设计\auth-lifecycle`。实际主入口从`2026-11-12T06:53:42.812638+00:00`至`2026-11-12T06:53:49.503273+00:00`（UTC），源码计量约6.639436s；外层时窗和真实LASTEXITCODE见sources/EXECUTION_WRAPPER.json。PowerShell包装最后输出JSON的shell状态与Python native退出码分别保存，验收采用native=1。

## 路径与禁止范围

实际输出继续位于`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r26\verification_runs`，独立run为`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r26\verification_runs\r26_regression68_001`；R28目录只存本次总结、来源和证据索引。原SOURCE_LOCK和旧结果未改。完整原始RESULTS SHA：`250e882d9441abb945c4d7da3ef0260377a17a11319ab421abe06964613a2f5a`。

真实服务/业务DB/key/RPC、正式部署、P1a/P1b/P2、S3-B2/S5操作均0。memory SQL连接0、测试子进程0、新key/TLS0；只创建了合法框架/日志/receipt和一个watchdog。没有现场修码、安装依赖或第二次调用。
