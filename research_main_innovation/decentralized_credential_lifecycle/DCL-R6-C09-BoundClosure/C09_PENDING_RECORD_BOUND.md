# 记录数上界与可达自环

Material Passport：DCL-R6-C09-BoundClosure；C09-BoundClosure/review-1；2026-11-15（Asia/Shanghai）；有限源码/历史原件/数学合同审查。


结论：**C09_PENDING_RECORD_BOUND_UNPROVABLE_UNDER_CURRENT_CONTRACT**。单handoff的合法状态转换数量有限；同一状态的PENDING观察次数缺少数值上界。

初态为已PREPARE/COMMIT/持久ACK、Receiver已在sender活着时取得pidfd、sender随后os._exit(23)，父协调者仍存活但尚未发布waitpid见证。当前boot/身份、票据/ready、counter/ACK/window匹配，STOP/CLOSED均缺，handoff.observe_until仍有正余量。

第一次observe_exit把stage从HANDOFF_COMMITTED发布为LAUNCHER_EXIT_OBSERVED，revision从3变4。check_base(require_sender_live=False)允许已退出sender，self.durable核验ACK，witness=None；classify得到PENDING，277行追加/fsync后278行返回。

guard._external_stop_impl的799–805行仅在VERIFIED关闭/清空pidfd，CLOSED触发停止；PENDING分支保留就绪fd，也不进入else的sleep。下一轮Receiver.poll无socket请求可立即返回，M.supervision只核当前责任和deadline，然后重走相同路径。stage/revision4/classification_count0/resume_count0与R都可保持。

对任何底层存储/表示允许的有限n，选择正余量tau小于剩余12秒/校准/stop截止，在tau内延迟父协调者，安排n次Receiver路径，其余监督保持健康。当前合同没有给这条立即返回/编码/append/fsync路径可靠的最短耗时；故无法从tau推得固定n上界。该结论针对源码与合同调度模型，未声称固定物理机器无限吞吐，也没有执行新的调度/故障实验。

完整成功日志总记录可写作N_pending＋8：6个stage＋1ACK＋1终态分类；首次失败前缀不超过对应进度类别，但N_pending项仍无界。classification_count约束成功交接只分类一次，未对此前反复判断计数。当前无自动创建第二handoff/第二恢复/新预算窗口。

历史CalDiag的同字节C09源码实际产生17 PENDING＋1 VERIFIED；无RESUMED，故总24=17＋7。17条都处于revision4、同一handoff_id，原全局journal在该PENDING区间追加0条。历史支持该自环可达，不能给出其最坏最大次数。

[可复核状态与调度族](evidence/COUNTEREXAMPLE_FAMILY.json) · [状态/记录公式](evidence/NATIVE_STATE_RECORD_PROOF.json) · [历史原件统计](evidence/HISTORICAL_NATIVE_LOG_ACCOUNTING.json)。

附加表示边界：若另行采用Linux signed64 off_t及单文件只追加/不轮转假设，则完整PENDING行每条至少1099字节，可给N≤floor((2^63−1)/1099)=8392513227347384的极粗上界。它来自ABI/文件容量，未成为受审的资源配额。反例族对真实存储许可的有限n成立，未越过EFBIG/ENOSPC或声称物理无限吞吐。具体n=30532的合同前缀已使仅PENDING的固定部分超过32MiB，但当前未进行此规模原生执行。

[表示边界与量词范围](evidence/REPRESENTATION_LIMIT_CAVEAT.json)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。
