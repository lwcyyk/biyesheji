# C09根因增量裁决

Material Passport：历史证据复核；不覆盖batch04原裁决；新增动态复现0。

H1需要拆分：退出意图已持久发布有证据；完整成功交接已经建立缺少证据。C09.ready来自payload，STOP_ARMED证明外部停止器已运行，这两者尚未形成针对此次Launcher退出的接收承诺。

H2成立：Launcher按源码在发布意图后exit23，但成功收据和接收确认尚未完成。旧停止器只持有pidfd退出事件，无法由非子进程pidfd直接取得真实退出码；exit23由外层命令结果记录。

同时存在分类竞态：旧guard656在select之前读取s，674在select返回后继续使用该快照。允许“取None→等待→发布C09→exit23→按旧None关闭”的交错。真实UNEXPECTED分支、最终C09标记及源码顺序支持该分析；本地s的读取时刻没有日志。

必须分别裁决：
- 旧快照可能造成意图观察遗漏，属于实现缺陷。
- 当成功交接证据不完整时，拒绝继续和关闭符合fail-closed；不能据退出23推定责任已转移。
- batch04恢复检查看到CLOSED后拒绝是正确行为，窗口不能恢复。

新修复显式补齐收据、接收确认、真实退出见证与版本语义，避免只修fresh-read后把单方意图直接当成完整成功。evidence/HYPOTHESIS_DECISION.json保存逐项结论，原94 native文件、40 journal记录及原包保持。
