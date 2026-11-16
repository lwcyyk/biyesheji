# CI-01 认证上下文与访问控制策略的一致性审计

本轮完成限定范围的源码审计与离线回归：**发现一处应用查询为空时跳过既有限制的源码级不一致，3个合成用例复现；真实部署效果与独立新颖性保持未决。**

全程没有调用本机认证服务、建立真实账户/应用或修改显示名；网络只读取官方公开资料。转换字段控制通过，未将AT→Cookie本身一概视为权限扩张。

|必交付文件|内容|
|---|---|
|[POLICY_CONTRACT.md](POLICY_CONTRACT.md)|可靠产品限制、规则ID、正常语义及SPEC_UNRESOLVED边界|
|[AUTH_CONTEXT_FLOW.md](AUTH_CONTEXT_FLOW.md)|认证→属性→策略数据流，M081最小合成反例|
|[OFFLINE_CASES.json](OFFLINE_CASES.json)|96格矩阵＋17边界例；每项预期关联依据|
|[TEST_RESULTS.json](TEST_RESULTS.json)|50契约符合、3不一致、60未决；测试退出码1保留|
|[SOURCE_LOCATIONS.md](SOURCE_LOCATIONS.md)|原路径、函数、行号、源码摘要与mock边界|
|[REMEDIATION_ANALYSIS.md](REMEDIATION_ANALYSIS.md)|已有策略的最小修正规则、功能影响与证明义务|
|[NOVELTY_ASSESSMENT.md](NOVELTY_ASSESSMENT.md)|六项裁决、上游已公开先例、主创新定位|

复现入口：[REPRODUCIBILITY.md](REPRODUCIBILITY.md)。测试代码：[policy_test.go](offline/routers/policy_test.go)；原样提取器：[extract.go](offline/tools/extract.go)；独立工件核对：[audit_offline.py](audit_offline.py)。

现有源token失效清理已能阻断对应离线状态；缺失应用分支仍需补齐普通上下文检查。该发现提高了具体实现问题的可复核性，当前证据不足以支撑新通用协议、独立算法优势或高强度主创新。后续优先做固定版本完整权限框架的mock集成回归。
