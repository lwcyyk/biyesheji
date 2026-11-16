# 校准300秒可行性裁决

Material Passport：B09-AdmissionFix-static-1/r1；2026-11-12；**TIME_FEASIBILITY_UNRESOLVED；BS-3=UNRESOLVED。**

本轮完成完整关键路径、持久化原语及历史性能范围审查。访问硬界62,546≤100,000成立；完整校准300秒成功完成的充分时间依据继续缺失。

|证据类别|本轮核验结果|适用范围|
|---|---|---|
|静态已知配置|300校准、1,800全批、1,740停止；14就绪、12交接及各局部超时|约束与拒绝条件；调度/阻塞IO保留既有假设|
|历史实测|batch04 C02 child 2.578066387秒；batch05 C02 child 2.720971054秒|各自spawn请求至wait返回，CLOCK_BOOTTIME同域|
|历史同域journal|batch04 C02 Starting→Deactivated为2.897138秒|journal MONOTONIC服务包络|
|历史约2.932秒参考|与journal起点至Root结果的跨度相符|旧摘要的服务参考口径；跨时钟跨度单列|
|历史实测|batch08 C00＋READY64至关闭10.267560352秒|只覆盖该最小诊断和原版本|
|旧失败性能|batch05约20.91秒Payload关闭、约300.04秒Root收敛|旧权限/停止缺陷路径；新修订已有静态差异|
|推导计数|新ledger631访问、至多5,800次新增相关fsync；全局事务上界25,556|静态操作计数，与秒数分开|
|未知|新RootIPC56/BC40/真实C09/S34/门18完整耗时，当前存储/调度最坏延迟|完整成功关键路径尚待真实证据|

旧约2.932秒保留参考归属。本轮使用同一journal时钟重算得到2.897138秒，并将child时段单列，避免混合CLOCK_BOOTTIME与journal MONOTONIC建立上界。所有源字节SHA、原始测量字段和fsync聚合见[历史性能证据](evidence/HISTORICAL_PERFORMANCE_EVIDENCE.json)。host静态检查时间另行登记。

当前资料足以证明单项路径曾快速完成，完整链尚有未测阶段及新持久化开销。全链数值估计缺足够输入，因此整体采用UNRESOLVED；局部经验值仍按历史实测呈现。静态超时相加或单项耗时外推均无法补齐全链成功时间证明。

推荐下一步方案B：新r1的单次完整校准诊断窗口，保留原300秒软截止、100,000校准访问及全部硬限，按实际冻结依赖测量；首个关键失败或截止即关闭封存。B从源码scope到--calibrate-only接线均排除FORMAL自动执行。B取得当前源版本的充分证据后，再审阅A及未来独立身份/锁。当前两方案均仅为申请，动态执行0。

[关键路径](FULL_CALIBRATION_CRITICAL_PATH.md) · [两方案申请](NEXT_DYNAMIC_AUTHORIZATION.md)。
