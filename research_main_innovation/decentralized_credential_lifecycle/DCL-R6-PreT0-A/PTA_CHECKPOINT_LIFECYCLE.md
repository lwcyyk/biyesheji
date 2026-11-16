# 检查点生命周期与顺序证据

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

**intent先于T0、counter先于运行检查点的顺序已取得实际证据；READY→ARMED的跨对象发布暴露并发一致性缺口。**

|对象/动作|实际结果与计时精度|
|---|---|
|sealed capability/一次认领|预检、same-PID exec、Owner/child核验通过；原nonce仅保留私有原件及证据包|
|预窗ctx|绑定本批/boot/manifest/执行锁/授权/Owner，期限185.510243359；T0/R=null|
|runtime intent|sample66.885179620；exclusive存储返回先于INITIALIZING sample66.888638365；fsync完成的精确时点缺少独立打点|
|T0/deadline/state|T0=66.896850269；真实发布先于READY；具体state fsync时点仅由执行顺序及持久原件限定|
|预算账|BRNGv001、used0、cap1,000,000；COMMITTED after0；创建在T0之后、READY之前|
|初次runtime checkpoint|READY事件之后写入，原生停止服务启动之前完成；初次READY文件随后被armed版本更新，原件未提供逐次公开checkpoint历史|
|严格运行检查首次调用|精确调用时间未打点；P.arm及Receiver.poll实际到达，前置真实state/counter存在；预窗manager查询成功发生在T0之前|
|armed/work|phase序号5及公开检查点存在；work服务0、RUNNING0；完整拒绝用例UNRUN|
|关闭后|CLOSED/STOP优先，保留原T0、intent、counter及phase；无新建账或重新初始化|

实际竞态可由以下允许调度解释：停止服务读取公开q.phase=READY；Launcher持久化私有phase=ARMED；停止服务读取新私有phase并比较旧q，抛PT_RUNTIME_PHASE_DRIFT；Launcher完成公开armed检查点。另一允许调度是读取发生在两个文件发布之间。原件没有记录每次读取值，因此具体交错保持推断；最终两个phase均为ARMED、initialization_id一致，且真实trace指向该跨对象比较。

下一静态验收应规定phase与公开checkpoint的统一提交/读取一致性义务，保留真实缺失/损坏拒绝和单调阶段约束。本轮实现改动0。

[初始化结果](PTA_INITIALIZATION_RESULTS.md) · [原生源码锁](evidence/FROZEN_SOURCE_REFERENCE/inputs/static_manifest.json) · [结果重核](evidence/ACTUAL_RESULTS.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
