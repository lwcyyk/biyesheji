# batch04首次失败与反例分类

Material Passport：真实监督器失败；协议搜索0；当前代码及输入未修复/重跑。

## 观察到的实现缺陷
launcher命令29真实退出23；这是冻结C09预定退出。持久batch_state保留expected_launcher_exit=C09、resume_count=0。C09.ready存在、counter37021。外部停止器却在209.077071432写UNEXPECTED_LAUNCHER_EXIT，随后实际exit125；root result_C09没有产生。

guard.py:656在pidfd等待前读取s；673执行最长0.1秒select；674使用旧s决定预定退出；684把其他值判为意外。launcher在781先持久写C09、782再exit23。故存在下列交错：
1. 停止器读取尚无C09标记的状态。
2. 停止器等待pidfd。
3. launcher持久写C09并exit23。
4. pidfd可读，停止器仍用先前快照关闭。

实际误关闭、最终状态、真实退出和源码顺序均有证据。停止器读状态的精确时刻没有单独日志；上述交错来自源码推导，本轮没有附加复现试验。属于SUPERVISOR_STALE_STATE_RACE；F1/F4协议反例搜索覆盖为空。

## 最小修复建议（尚未实施）
在pidfd readiness后重新读取可信状态，重新校验同boot/T0、被监测launcher身份、一次恢复计数及已持久的预定退出承诺；必要时采用带身份/代次的双向持久handoff。保留真正意外退出的立即关闭规则，避免把任意旧C09标记当成许可。增加受界竞态回归：预定退出跨读/等待、未预告退出、陈旧/跨boot标记、关闭后恢复等；冻结新hash后再申请动态范围。

当前batch04的CLOSED、37021账及全部原件保持，未尝试resume、重置、源码修复或batch05。后续工作应先修复该具体失败，F2/F3保持待进入。
