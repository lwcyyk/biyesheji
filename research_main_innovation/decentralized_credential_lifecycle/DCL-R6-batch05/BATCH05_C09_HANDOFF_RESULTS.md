# batch05 真实 C09 交接结果

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

真实 C09 入口结果为 **FAIL_ENTRY_PERMISSION**；交接协议结果为 **NOT_EXERCISED**。C09H 完成并通过 Root 重算后，C09 payload 在首次全局记账读取 `visits.bin.intent.json` 时发生 EACCES，随后请求停止。`C09.startup.json` 已保存；`C09.ready.json` 尚未生成。

|成功条件|本批真实链证据|
|---|---|
|当前 batch 交接意图|NOT_EXERCISED；成功证据待取得|
|receiver 取得有效交接状态|NOT_EXERCISED；成功证据待取得|
|同一活 receiver 的持久 ACK|NOT_EXERCISED；成功证据待取得|
|receiver 确认完成|NOT_EXERCISED；成功证据待取得|
|Root waitpid exit23 见证|NOT_EXERCISED；成功证据待取得|
|退出匹配稳定 Launcher 身份|NOT_EXERCISED；成功证据待取得|
|pidfd 后读取当前交接状态|NOT_EXERCISED；成功证据待取得|
|fresh-read 版本有效|NOT_EXERCISED；成功证据待取得|
|闭合/发布共锁的真实交错|NOT_EXERCISED；成功证据待取得|
|一次有效分类|NOT_EXERCISED；成功证据待取得|
|恢复保持预算和 deadline|NOT_EXERCISED；成功证据待取得|
|独立停止源覆盖交接/恢复|NOT_EXERCISED；成功证据待取得|

交接状态、prepare/commit、持久 ACK、receiver 完成确认及 `c09_exit_witness` 均缺失。Root fork、pidfd 初始化与 external-stop socket 已发生；这些启动事实只支持组件就绪范围。Launcher 最终 exit125，预定交接 exit23 尚未发生，恢复次数为 0。

原 T0/deadline/stop_at 与最终账保持；独立停止源实际处理了 STOP_REQUEST。H3 的该次权限故障停止路径有原始观察，完整 H1–H8 实际交接性质仍保留待验证。28 PASS+6 MUTATION_DETECTED 来自合成 C09H，见 [回归结果](BATCH05_C09_REGRESSION_RESULTS.md)。

B05-A：`NOT_EXERCISED / C09_ENTRY_FAILED`。C09Fix 对 batch04 真实持久 ACK、退出见证、fresh-read 及一次分类的修复效果尚待运行证据。首次失败见 [FIRST_FAILURE](evidence/FIRST_FAILURE.json) 与 [反例分析](BATCH05_COUNTEREXAMPLES.md)。
