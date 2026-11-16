# CI-01 完整权限框架离线回归与最小修复验证

**结果：真实权限链复现了一项实现缺陷，最小修复消除了登记的3个违例实例，原50项明确合同的正反例保持。** 该实例归档为论文支撑性安全发现，当前证据不足以承担独立高强度主创新；本轮结束其继续扩展。

基准和修复版使用同一固定提交、Go1.26.10、真实Beego/Casbin/控制器和隔离存储。认证服务调用与真实账户操作均为0。未决合同保持60项，其中M033/M034/M082改变了实际行为，独立登记兼容性影响。

|交付|内容|
|---|---|
|[BASELINE_INTEGRATION.md](BASELINE_INTEGRATION.md)|完整选定权限调用链、原始反例、观察插桩与替代范围|
|[DEPENDENCY_AND_TOOLCHAIN.json](DEPENDENCY_AND_TOOLCHAIN.json)|固定源码、官方工具链、273项编译闭包模块和校验|
|[POLICY_INVARIANTS.md](POLICY_INVARIANTS.md)|已确认不变量、D1决定、修复充分性与功能边界|
|[SPEC_GAPS.md](SPEC_GAPS.md)|60项未决规范逐项清单|
|[MINIMAL_PATCH.diff](MINIMAL_PATCH.diff)|仅一个产品源文件的普通正确性修复|
|[PAIRED_RESULTS.json](PAIRED_RESULTS.json)|113历史输入＋4框架控制的两版逐项阶段、效果及成本|
|[REGRESSION_ANALYSIS.md](REGRESSION_ANALYSIS.md)|原始违例消除、合法功能保持、未知行为变化、身份残留|
|[PRIORITY_AND_GENERALIZATION.md](PRIORITY_AND_GENERALIZATION.md)|先例检索、两个上下文入口对照和主创新资格判断|
|[FINAL_DECISION.json](FINAL_DECISION.json)|限定范围的最终裁决与停止状态|

复现：[REPRODUCIBILITY.md](REPRODUCIBILITY.md)。原始完整链见`raw/baseline01`，实施门见[PATCH_GATE.json](PATCH_GATE.json)，最终配对见`raw/paired02_baseline`与`raw/paired02_fixed`。真实浏览器、生产影响及并发安全仍未验证。
