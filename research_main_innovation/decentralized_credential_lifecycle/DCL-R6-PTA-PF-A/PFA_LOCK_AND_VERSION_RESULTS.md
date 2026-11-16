# 有界锁、版本与观测范围

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

**同锁接线得到冻结源码与实际正常调用路径支持；逐次flock时间、竞争及中断性质保持条件性。**

锁实际路径为/var/lib/dcl-r6/batch12/inputs/root_private/boot/pt_phase.lock。原生导出保存device/inode、Root:Root/0600、nlink1、ACL空；具体元数据保留原字段，见下方JSON。公开点和私有phase在最终快照均RUNNING/6，record digest及初始化ID一致。

|要求字段|原字段/实际观测|
|---|---|
|observed_phase|PT_RUNTIME_CHECKPOINT.phase=RUNNING，最终持久快照|
|expected_phase|pt_phase.phase=RUNNING，最终私有快照；各次读取期望未单列|
|phase_version|两侧sequence=6；私有完整事件seq0–6|
|batch_id/boot_id|batch12 / 6b12daf8-f8cc-4788-bcaa-382f2d3407fb|
|process_identity|scheduler838、Owner445、stopper849，start_ticks与boot见原件|
|lock_acquire_time/release_time|UNKNOWN，冻结程序没有相应逐次日志|
|read_result/decision|真实WORK、C00与112模型检查成功，最终状态一致；逐次读判定日志UNKNOWN|
|竞争次数|UNKNOWN；PF延迟/等待帧属于合成策略测试|
|超时/死锁|实际工作路径没有观察到锁超时错误或持续死锁；43秒前缀完成。锁故障/中断行为的真实OS测试未执行|

Root的读和成对发布均执行同一有界锁路径；批准代码字节、实际角色路径和最终版本链一致支持这一结论。中间半更新是否曾出现、每个读方的具体等待与锁释放时点缺少独立原生观测。代码在本次正常运行中完成不能替代所有调度的证明。

PF-A2=CONDITIONAL_PASS：冻结合成非法版本、错误身份、终态和WORK拒绝均按独立oracle接受；主实例没有被破坏或注入真实flock/IO故障。

[字段映射及UNKNOWN](evidence/FIELD_MAPPING_AND_UNKNOWN.json) · [锁元数据/phase链](evidence/LOCK_AND_PHASE_EVIDENCE.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
