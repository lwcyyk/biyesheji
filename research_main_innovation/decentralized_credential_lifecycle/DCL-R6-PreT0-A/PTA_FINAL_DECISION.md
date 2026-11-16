# 阶段A最终裁决与十九项回答

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

**阶段A未取得完整动态验收：本批正常预窗及真实初始化推进到RUNTIME_ARMED，随后因PT_RUNTIME_PHASE_DRIFT自动关闭；PT64、九项变异及真实无T0异常路径均未执行。**

|最终问题|实际回答|
|---|---|
|1 是否真实启动|是；新batch11、真实预检/一次认领/same-PID exec/Root child，active入口1次、exit125|
|2 IPC_STATE_MISSING是否再现|本批未观察到；旧MRA失败原件保持|
|3 初始化前提|预窗认证通过；真实intent、state、counter和运行checkpoint按序创建，ARMED后并发一致性失败|
|4 预窗与运行点隔离|正向路径有实际证据；故障拒绝和全部回归覆盖仍缺|
|5 intent|真实exclusive创建，hash与公开initialization_id相符|
|6 armed/work|ARMED真实建立；C00前收到STOP，work/RUNNING0；完整守卫验收未完成|
|7 T0与账|真实T0=66.896850269，counter已建立、R=0、COMMITTED after0；没有重置|
|8 64项|执行0、接受0，UNRUN_BEFORE_C00|
|9 九项变异|触发0、检出0，全部NOT_EXERCISED|
|10 120秒期限|真实绑定原ticket/ctx；过期及无T0异常动态性质UNRUN|
|11 自动停止|实际运行态错误触发STOP/CLOSED，父stop成功，角色最终退出|
|12 外部兜底|额外兜底0、人工清理0；只读导出和行政打包单列|
|13 退出/组空|child直接waitpid125、Root角色退出观察、独立停止服务systemd退出125、停止结果及事后/proc/cgroup核验均保存|
|14 UNKNOWN|前两条关闭UNKNOWN保持；后续按冻结退出审查收敛CLOSED_CLEANUP_CONFIRMED；预算journal缺失UNKNOWN字段保持|
|15 两类封存|native实际包完整性NATIVE_SEAL_COMPLETED；冻结host自动post exit1，ADMIN_EVIDENCE_UNRESOLVED；本研究行政包独立封存|
|16 资源|R=0；active1.918233秒、全部host2.4388536秒；Payload空slice观测memory peak0/tasks0；Root RSS/全树精确峰值未测|
|17 阶段A完整通过|未取得；FIRST_UNEXPECTED_RUNTIME_ARMING_RACE，自动行政路径失败|
|18 恢复C09后MR条件|尚缺本轮缺陷静态修复、正常A/PT64及独立预窗中止证据、完整资格链与新授权|
|19 下一最小修复|phase/checkpoint提交读取一致性、隔离脚本入口导入、自动收尾有界退出屏障及标签/错误来源证据；先静态冻结后新身份授权|

native包44项/45entries校验成功只支持该包完整性；完整资源、全链性能、模型安全及原创性分别裁决。PREWINDOW_ABORT与正常模式互斥，本批已CLOSED且claim消耗，后续保持关闭。

原MRA启动前125/IPC_STATE_MISSING、无T0/R、内部UNKNOWN、native失败和行政归档继续保留；原CalDiag真实C09 PASS、194项/41变异及38,729账保持。r3源码和历史6,522份基线后续完整性核验见[交付核验](evidence/DELIVERY_CHECK.json)。

[首次反例](PTA_COUNTEREXAMPLES.md) · [封存细项](PTA_SEALING_RESULTS.md) · [资源](PTA_RESOURCE_ACCOUNTING.md) · [证据索引](EVIDENCE_INDEX.md) · [下一静态范围](NEXT_STATIC_REPAIR_REQUEST.md)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
