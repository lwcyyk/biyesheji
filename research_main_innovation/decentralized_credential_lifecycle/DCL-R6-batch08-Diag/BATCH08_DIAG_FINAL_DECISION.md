# batch08-Diag最终裁决

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

**最小诊断成功完成并正常关闭；C00_PASS。RESOURCE_GATE_PASS仍NOT_OBTAINED，F1/F4均UNRUN_RESOURCE_GATE。**

|裁决轴|结果|边界|
|---|---|---|
|D08-1 预检|PREFLIGHT_PASS|原生3.12/源/锁/当前身份及单会话预检通过|
|D08-2 连续性|SAME_BOOT_CONFIRMED|预检/exec/Root/scheduler/C00服务自查同boot|
|D08-3 八项资格|C00_PASS|真实STARTING后READY，最终8项全部MATCH，原probe PASS|
|D08-4 诊断完整性|FIELD_EVIDENCE_PARTIAL|8项与双源原件完整；pidfd独立时刻/后侧stat及精确wait返回点缺打点|
|D08-5 模型资格|NOT_OBTAINED|最小权限范围；其余资格链和模型未启动|

|用户最终问题|实际回答|
|---|---|
|1 新批次|成功建立并按最小范围正常关闭|
|2 同boot/身份|Same boot，Root438/start4792跨exec；C00自查811/start4978|
|3 原八字段|Uid/Gid/Groups/CapEff/NoNewPrivs/LimitAS/LimitASSoft/ControlGroup|
|4 实值|最终双侧[999]/[989]/[989]/0/1/1073741824/1073741824/规定服务CG，全部MATCH|
|5 首次STARTING|CR-01…05 defer为NOT_READY；CR-06…08已MATCH|
|6 稳定失配|本轮0|
|7 双样本|两次READY字段/版本/身份和kernel辅助值一致；原始状态、时间均存|
|8 pidfd|冻结检查路径成功，无身份变化；独立每次时间/后侧stat未记录|
|9 等待|wait返回区间0.149840881–0.155141782秒；再次验证结束0.185783023秒|
|10 C00|原生Root机器PASS|
|11 最早失败|本轮无失败字段；旧batch07失配项仍UNRESOLVED|
|12 资源|R450、450事务、T0后10.267560352秒正常关闭、charged peak43937792B|
|13 新缺陷|未见稳定字段/接口拒绝；精细pidfd/返回点可观测性缺口保留|
|14 下一步|准备新的独立完整链准入；不恢复CLOSED batch08，不猜测修正某个字段|

获准64项全部有效：47 PASS＋17 MUTATION_DETECTED，Root独立oracle与host只读reference一致，未命中/额外错误0。实际单会话入口1、重试0、源码/判据/权限现场修复0、主动WSL shutdown0。Full批准位false，BC40/RootIPC56/C09H34/C09/C01–C12/S34/门17及F1/F4均UNRUN_UNAUTHORIZED，保持本次边界。

本批boot 0cc7ff50-243e-41d0-bf3f-ba45b3f95695，T0=49.529730421，R450，CLOSED reason=C00_DIAGNOSTIC_COMPLETE。101 native文件、36最终文件、原生100条目包及run-boot journal已保存；受控进程为空、父cgroup不存在。原batch07聚合拒绝不改，旧字段仍C00_FAILED_FIELD_UNRESOLVED；本轮没有倒填历史observed。

当前代码/输入/全部历史工件与原包hash保持；47误路径副本只读/hash，blocked by policy保持。完整条件链仍需独立批准与匹配新批次版本/锁，当前batch08不可复用，也未创建后续批次。

PASS_BOUNDED授予0；D1-PBFT-SEAL/1.1原条件、强G覆盖、严格分离实例0与IMPLEMENTATION_GATE=CLOSED保持。原生诊断成功和完整资源/协议性质分别裁决。

[字段证据](BATCH08_C00_FIELD_RESULTS.md)、[时序](BATCH08_C00_READINESS_TIMELINE.md)、[回归](BATCH08_C00_REGRESSION_RESULTS.md)、[账](BATCH08_RESOURCE_ACCOUNTING.md)、[观测边界](BATCH08_DIAG_COUNTEREXAMPLES.md)、[证据索引](EVIDENCE_INDEX.md)、[交付核验](evidence/DELIVERY_CHECK.json)。
