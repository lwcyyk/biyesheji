# DCL-R6-BudgetFix最终裁决
Material Passport：BF-static-1；已授权有限静态修复完成，预算安全与部署结论采用条件范围；动态验证0次。

## 交付结论
正确lc03准备区已交付真实修复：guard.py与guard_probe.py改变；run_batch.py及五业务源码保持字节一致。新机制采用冻结N的一次持久范围预留、一次持久claim、身份绑定局部扣减，重复请求只返回原事实；无退款、无恢复补发。协议EXACT-RANGE/1与新batch03命名隔离原batch02账。C02 N=32896，C03=4096，C04=1。

PREPARED/COMMITTED时标复用已修订；最终持久完成、派发、claim、局部扣减、子进程申请/退出观察均设测点。真实fsync耗时、未来速度和C02能否在300秒内完成仍未知。源码同步机会按原7N、新范围9+claim2=11统计，元数据/遥测另计。

## Gate
|Gate|状态|范围|
|---|---|---|
|BF-1 预算语义|CONDITIONAL_PASS|R/A/U与保守占用、S1–S9静态条件证明完整；存储/合作writer/时限调度假设与动态缺口保留|
|BF-2 代码修复|PASS_STATIC|仅两获准资源文件变化；接口/扣减调用点审查、八源语法及最终guard编译通过|
|BF-3 历史与源码|PASS_STATIC|五业务+run_batch相同；Perf/B02原件/47副本只读复核、31关键runtime与3旧unit字节匹配|
|BF-4 性能及准入准备|CONDITIONAL_PASS|真实新hash、完整主流程argv及独立batch03申请已冻结；S1–S9专用动态夹具仍需单独静态冻结和授权|

静态语法证据：order06八文件退出0；后续guard修订由order09最终退出0覆盖。记录器初次捕获失败、两条未启动计划、一次失败复制及旧稿order08均保留真实状态，最终源以工作区锁为准。未执行target import、校准探针、模型、性能基准、内存分配测试或故障注入。

## 当前状态
RESOURCE_GATE_PASS = NOT_OBTAINED
F1 = UNRUN_RESOURCE_GATE
F4 = UNRUN_RESOURCE_GATE
batch03 = UNAUTHORIZED
IMPLEMENTATION_GATE = CLOSED
STRICT_SEPARATION_INSTANCES = 0

batch02仍CLOSED_RESOURCE_GATE_FAILED，32191原消耗保持。C00/C01原PASS、C02原失败与child未启动事实保持。新静态模板未安装，新批根/账/窗口/执行receipt均缺失；系统配置修改与依赖安装0。此前47误副本只读登记，原blocked by policy保持，清理尝试0。

## 后续可审批事项
审阅[BATCH03_EXECUTION_REQUEST](BATCH03_EXECUTION_REQUEST.md)，其主流程真实锁可直接用于下一授权申请。若批准当前完整流程，须明确接受本版条件安全假设、S1–S9动态缺口及C12全PASS自动进入FORMAL；如要求先逐故障验证精确范围，先冻结相应有界夹具和额外准入门的新版本，再申请受限执行。当前静态许可不会产生动态资格。

[预算语义](BUDGET_RESERVATION_SEMANTICS.md)、[崩溃证明](BUDGET_CRASH_SAFETY_PROOF.md)、[代码审查](BUDGET_STATIC_CODE_AUDIT.md)、[锁定源码与输入](SOURCE_AND_INPUT_LOCK.md)、[交付核对](evidence/DELIVERY_CHECK.json)。
