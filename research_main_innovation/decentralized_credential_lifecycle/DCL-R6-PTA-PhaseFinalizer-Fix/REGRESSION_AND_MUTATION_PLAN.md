# 静态回归、PF48与变异计划

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

**原PT64/9mutant输入jobs保持；新增PF48/8mutant，全部实际UNRUN。** 独立oracle没有导入生产lifecycle、subject、guard或预算核心，按原始input/trace/binding/SHA重算差异类别。

|集合|内容|本轮检查范围|
|---|---|---|
|原PT64|55safe＋9mutant，原jobs相同，历史原件保留|输入等价与源保持；实际执行0|
|PF基础32|14 phase、12 admin、6 closure；含合法WORK、锁竞争/延迟观测、旧版本/跨批/回退/终态/非法阶段、导入/身份/无T0/native/UNKNOWN/权限/异常/重复及关闭分轴|schema、最多4帧、唯一ID、调用接线及静态路径审查|
|8组配对|每组同输入safe/mutant，各16项；总PF48＝40safe＋8mutant|输入配对与违规集合一致性静态审查|
|导入探针|最终5项，三个候选累计15项；惰性入口及可信stub，非默认cwd和错误传播|PASS_HOST_CONTROLLED；真实生命周期导入0|

八项变异：放行非法阶段（ILLEGAL_PHASE_ACCEPTED）、跳过WORK（PREMATURE_WORK）、旧快照（STALE_SNAPSHOT_ACCEPTED）、忽略版本（VERSION_MISMATCH_ACCEPTED）、不触发关闭（NO_AUTO_STOP）、吞导入错误（IMPORT_ERROR_SWALLOWED）、覆盖native（NATIVE_RESULT_OVERWRITTEN）、关闭后重入（REACTIVATION）。前四项允许与放行相伴的NO_AUTO_STOP，其余意外违规均拒绝接受。oracle先独立分类观测差异，再比对目标与允许集合，源码构造不会预填实际检出结果。

未来每job先预付16次，再持久化真实模型trace并由独立oracle重审；suite另有entry1和每job审查1。PF完成计费817，硬界1,152。首次缺件、错误safe、未检出或意外违规立即停止；原guard关闭链负责清理。没有窗口外重放checker或退费。

PF48的origin明确为PF-SIMULATION/1，只覆盖对应纯策略/合成观察轨迹。锁竞争/延迟帧表达观察合同，尚不等同于真实flock/fsync调度注入；admin导入失败帧也不等同于真实Root模块失败。实际锁、进程、文件权限、自动停止/导出/归档及无T0终止必须分别取得Native证据。下一正常A只覆盖真实正向最小链；独立真实预窗中止仍需新身份和授权。

[PF48输入](evidence/SOURCE_FINAL_R3/inputs/phase_finalizer_contract.json) · [独立oracle](evidence/SOURCE_FINAL_R3/src/phase_finalizer_oracle.py) · [静态变异矩阵](evidence/FIXTURE_ORACLE_STATIC_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
