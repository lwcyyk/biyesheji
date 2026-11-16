# PT固定输入、故障及变异计划

Material Passport：PreT0Recovery-static-1/r3；64固定job，55safe＋9mutant；actual=UNRUN。

46个正常/异常safe场景加9组safe/mutant配对。每项有固定op/facts、绑定/boot/Owner/期限、checkpoint完整性、实际对象/T0/R、进程退出、应用状态、行政完整性及native结果；最长11帧。原始input和subject观测/decision/grant/对象/终态均写Root私有pt_case_###，输入和原件SHA由独立oracle审查。

覆盖全新无运行点合法、正确创建state/counter/点/armed/work；预窗收据/boot/Owner/期限错误、Root/Launcher失败、预T0异常、账创建中断、停止源丢失/退出未知/行政写失败；运行点缺失/损坏/身份错、关闭重入/重复T0/counter；无运行态seal、行政部分/manifest/hash失败、进程确认而应用未知、native失败与重复seal。

|mutant|错误行为|实际违规应被独立发现|
|---|---|---|
|force_runtime_pre|初始化前使用运行态点|合法预窗被IPC缺state阻断（PREWINDOW_CYCLE）|
|delete_pre_validation|删除绑定/身份/启动点条件|无效预窗实际接受|
|missing_checkpoint_pass|只在运行阶段补缺点|缺真实checkpoint仍实际工作|
|no_auto_stop|失败不设置STOP/CLOSED|缺自动停止/终态回退|
|missing_deadline|忽略过期条件|过期仍被接受|
|unknown_as_success|未确认退出就报确认|FALSE_CLEANUP|
|admin_as_native|行政包冒充native|无运行条件却NATIVE_SEAL_COMPLETED|
|new_budget_after_fail|失败后重新建T0/预算|第二初始化或原window重置|
|reactivate_closed|清除终态继续工作|终态后实际发放|

oracle独立重算，不读取预填expected=false判实际通过；safe必须无违规，mutant必须命中指定违规且无越出声明的错误。首次非接受/缺件/未检出即停止，无自动重跑。当前MUTATION_DETECTED等只是将来分支，真实执行与检出数均未产生。

Root运行时费用1＋64×(16预付＋1总审)=1,089，专项硬1,536；在真实C00之后使用同一批账/300秒。最小正常A硬访问1,537（C00=1＋PT硬），完成计费1,090；预窗失败A无运行T0/R，不能将未初始化填0。完整继承链64,082＋PT硬1,536=65,618≤100,000，其他硬限及MR/S/门18判据保持。

下一原生A两个互斥模式，分别验证正常创建与预窗异常停止/行政封存；一个关闭实例不能承载第二次模式。合成64并不替代真实进程、fsync或自动post-finalizer验收。

[输入](evidence/SOURCE_FINAL_R3/inputs/startup_contract.json) · [独立reference](evidence/SOURCE_FINAL_R3/src/startup_oracle.py) · [一致性](evidence/FIXTURE_ORACLE_CONSISTENCY.json)。
