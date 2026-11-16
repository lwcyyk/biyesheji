# 最终静态裁决

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

**已完成两个已观察缺陷的有限静态修复并冻结PTA-PhaseFinalizer-static-1/r3；全部新Native行为仍待独立授权。**

|验收门|结果|范围|
|---|---|---|
|PF-G1 阶段根因|PARTIAL|抛错位置/角色/组合条件和合法源码反例已定位；历史精确操作数继续UNKNOWN，保留PT_RUNTIME_PHASE_DRIFT_ROOT_CAUSE_UNRESOLVED|
|PF-G2 阶段一致性|CONDITIONAL_PASS|Root成对发布/读取同锁，seq/digest/writer/WORK/终态条件保留；OS并发与性能待验|
|PF-G3 行政收尾|CONDITIONAL_PASS|固定隔离入口、装载前资源界、当前回执/角色身份、独立native/admin保存及主机5探针齐备；Native导入/IO待验|
|PF-G4 自动关闭|CONDITIONAL_PASS|原M.abort/stop/reap/seal异常链保持；新错误及post退出条件未动态验收|
|PF-G5 执行准备|PASS_STATIC|55文件/38程序、PT64保持、PF48/8mutant、独立oracle、访问界及最小下一申请完整|

最终38程序语法及3.12文法/内存compile通过，28项静态断言、最终5项主机惰性/受控导入通过；三个候选累计15项主机探针。13关键文件字节及57成员AST保持，整个RootIPC归一AST和原slice字节保持。没有把静态构造或主机stub装载计为PT/PF动态结果。

本轮WSL、部署、Launcher/服务、真实预算、PT64、PF48、独立oracle及模型执行均0；本轮T0/R=null。55份最终源仅存在Windows工作区与静态交付副本。完整访问硬界66770≤100000，正常A硬2689；真实300秒全链时间继续UNRESOLVED。

历史batch11的native seal成功、R=0、早期UNKNOWN与后续关闭confirmed、自动post导入失败均保留；原MRA预T0失败与native失败、CalDiag真实C09及旧预算同样保留。旧报告较强的“竞态根因”表述未重写，本轮对原始操作数缺口作独立审计裁决。

下一步仅审阅[新的正常A申请](NEXT_DYNAMIC_AUTHORIZATION.md)。根因细化、锁/IO、模块装载、真实自动关闭及行政完整性都须按具体证据独立裁决。后续原生批次和完整资格链需要新的明确授权。

[根因](PHASE_DRIFT_ROOT_CAUSE.md) · [实现](PHASE_FINALIZER_FIX_IMPLEMENTATION.md) · [静态结果](STATIC_VERIFICATION_RESULTS.md) · [源码锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
