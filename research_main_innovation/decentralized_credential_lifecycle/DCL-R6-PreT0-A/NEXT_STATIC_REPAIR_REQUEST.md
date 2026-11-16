# 下一轮最小静态审查范围

Material Passport：DCL-R6-PreT0-A；batch11；PreT0Recovery-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；实际入口1次，重跑0，源码修复0。

当前为请求范围说明，本轮动态批次已经关闭，源码修复及新测试执行均为0。

1. 为phase与公开runtime checkpoint定义可审查的提交、读取与版本一致性合同，构造READY→ARMED及ARMED→RUNNING的reader/writer交错；真实缺点、破损、身份失配和终态守卫继续严格拒绝。
2. 审查冻结post-exit实际`-I -S -B`入口的模块装载路径，保留精确源目录和摘要校验。将“语法可编译”与“精确隔离入口可装载”分别验证；动态测试须下一独立许可。
3. 自动post审计等待真实受控角色/写者收敛时使用原合同的剩余期限及更小行政上界，保留DEFERRED/UNKNOWN，控制导出上限；active调用返回与全部systemd角色退出分别见证。
4. 错误来源补足：保留冻结首错槽位，另外记录触发STOP的角色、原始异常及阶段，使后续的STOP拒绝与最初因果错误可同时审查。
5. 对齐r3版本、控制目录r5和残留r1说明，保持历史原文。若下一修复涉及身份/路径，采用新批次与新摘要，当前batch11维持CLOSED。
6. 保持预算核心、D1/D2、五份业务源、RootIPC权限/C09持久交接、资源限额及原MR审查边界；先提交最小静态差异、保护语义证明、回归清单和锁。

后续正常初始化/PT64与PREWINDOW_ABORT分别需要独立身份/授权，完成后再审查C09后MR及完整资源资格；当前授权不自动延伸。通用基础设施修复不构成原创候选机制实施，STRICT_SEPARATION_INSTANCES仍为0。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原条件结论与强G覆盖裁决保持。
