# batch04最终裁决

Material Passport：真实执行；首次关键失败已关闭；RESOURCE_GATE_FAILED；2026-11-11。

## 结果
预检通过：30项host静态文件、1274唯一Linux摘要、runtime/boot/UID/cgroup及专用单位均按冻结合同核验。唯一窗口在boot99fbdfbd-f0b9-4cf2-8914-0d71867b6138初始化，T0=199.727213695。

C00–C08共9项取得冻结root PASS。C02实际单笔预留32896，核心预留27.617904ms，内存child实际完成；其root结果在T0后3.977400525秒。目标预留/claim的11次fsync合计16.141648ms；17991次操作、14905未用信用持续占用。

C09预定launcher退出23后，停止器以UNEXPECTED_LAUNCHER_EXIT误关闭，缺少成功交接收据。源码显示pidfd等待后使用早先状态快照的竞态。恢复准入拒绝CLOSED，未执行resume。全批关闭elapsed9.349857737秒，组空确认elapsed9.362411078秒。

## 用户要求的最终分类
|项目|实际结果|
|---|---|
|预检|PREFLIGHT_PASS；T0前boot变化已全量刷新，窗口只初始化1次|
|C00–C12|9 PASS；C09 FAIL_SUPERVISOR/无root成功收据；C10–C12 UNRUN|
|34个S job|执行0、完成0、通过0，全部UNRUN_RESOURCE_GATE|
|17个门负向|执行0、实际检出0|
|RESOURCE_GATE_PASS|NOT_OBTAINED；资源结果RESOURCE_GATE_FAILED|
|C02/校准耗时|C02服务2.932093220秒；结果T0+3.977400525；全批9.349857737秒关闭|
|账与资源|37021/1000000，31 PREP/31 COMMIT配对健康；观测charged peak125067264B，pids4，树RSS峰值未认证|
|F1/F4|均UNRUN_RESOURCE_GATE，实际模型状态访问/搜索0|
|PASS_BOUNDED|授予0|
|反例/缺陷|观察到C09监督器实现竞态；协议搜索0，缺少协议结论|
|下一阶段|先修复具体监督器失败，F2/F3尚缺资源/模型前置证据|

## 证据及边界
保存所有首次失败原件、40条限定unit journal、命令双流、原始账、94个native文件与30个冻结源/输入/缓存。程序原生seal因C09退出路径未执行；行政快照及打包逐字节核对，未制造native自动封存结果。关闭后专用UID进程为空、parent组不存在。后续观察boot变化与运行boot分开，manager事后默认值不用于证明运行限制。

本次没有修改源码/业务输入/判据、放宽资源、恢复已关闭窗口或创建batch05。旧batch01、batch02的32191及原失败、batch03预检、BF各版本、误副本及blocked by policy全部保持。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE。
IMPLEMENTATION_GATE=CLOSED；STRICT_SEPARATION_INSTANCES=0。
D1-PBFT-SEAL/1.1与强G既有条件裁决保持。

[授权锁](BATCH04_AUTHORIZATION_AND_LOCK.md)、[校准](BATCH04_RESOURCE_CALIBRATION.md)、[C02性能](BATCH04_C02_PERFORMANCE.md)、[预算](BATCH04_RESOURCE_ACCOUNTING.md)、[首次失败与修复建议](BATCH04_COUNTEREXAMPLES.md)、[证据索引](EVIDENCE_INDEX.md)、[交付检查](evidence/DELIVERY_CHECK.json)。
