# 第5章 验证体系与实现证据

## 5.1 分层验证结构

本项目用L0有限模型检查规格、策略和证书，再用L1原生记录核对限定profile的语义。源码实现、一次历史运行、有限枚举、手工证明和原生保持具有各自的证据范围。本文只组装既有结果，新增工作为来源核对和章节编辑。[证据分层](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md) [本轮范围](D:/毕业设计/thesis_draft/TASK_SCOPE.md)

候选采用记忆化AND/OR递归，R-I从同一输入展开可达(r,K)后自底向上判定。检查器逐节点验证策略或反证并重新解释前置条件。R-I和检查器共享_reference_kernel与schema，B参考和B检查器另共享b/_kernel，独立性相对候选成立，共同规格错误仍有可能。[R-I定义](D:/毕业设计/auth-lifecycle/docs/SEMANTICS.md) [检查器边界](D:/毕业设计/auth-lifecycle/docs/CERTIFICATES.md) [实现依赖审计](D:/毕业设计/thesis_draft/sources/technical_report.txt)

## 5.2 L0有限域与关键回归

|历史验证批次|范围|结果|
|---|---|---|
|v2.16 final01|41个unittest方法、27个命名场景|0失败、0错误、0跳过，候选/R-I一致|
|L0参数穷尽|两世界、每世界s/done、两动作、观察0/1、费用0，1,296参数模型×H=0…3|5,184查询，928 FEASIBLE、4,256 IMPOSSIBLE，证书通过|
|边界单元|H=8及四任务单独场景|支持输入边界回归，整体参数域未全穷尽|
|后续主线测试|原生实验工具扩展后的regression03|历史96项自动测试通过|

表内计数来自各自历史文档与原始汇总，1,296模型包含行为等价参数重复。[L0原始范围](D:/毕业设计/auth-lifecycle/docs/VALIDATION.md) [L0汇总](D:/毕业设计/auth-lifecycle/results/v2.16/final01/summary.json) [后续测试记录](D:/毕业设计/auth-lifecycle/docs/experiments/RESULTS.md)

具名回归覆盖stay、三世界及五世界冲突、错账户、原生根不独立、受限active、会话创建、响应丢失、未知句柄、批准撤回、预算不足、空K和外部可观察冲突。它们包括合法正例和故意不安全输入，期望状态与实际状态保存在regressions.json。[测试定位](D:/毕业设计/auth-lifecycle/docs/VALIDATION.md) [逐项结果](D:/毕业设计/auth-lifecycle/results/v2.16/final01/regressions.json)

## 5.3 资源谱验证

R2以公式和直接任务移动搜索核对11,154个预算查询及16,453个小需求族。R3扩展到268,310个预算查询，加入5,000个随机全局需求族及500个较大固定配置族，并覆盖k=2…8、r=1…4的224个谱构造。224例中36例完成低于已验证上界的全部配置枚举，188例核对上界执行与下界引理前提。两次重放的确定性结果一致。[R2批次](D:/毕业设计/research_recipe_r2/REPORT.md) [R3原始摘要](D:/毕业设计/research_recipe_r3/results/expanded01/summary.json) [范围与重放](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md)

公式与BFS分离了最优化表达和具体移动解释，但仍共享输入编码和分区生成器。R3隔离上下文重推导由同模型完成，属于内部独立上下文检查。手工证明、有限实现一致性与外部人工复核分别登记。[数学复核与独立性](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md)

## 5.4 证书攻击与失败证据

v2.16曾出现把整数0替换为JSON false仍被检查器接受的开发失败，随后以规范化JSON比较修正并保留原失败记录。证书篡改测试还覆盖删动作、删观察、替换预算与摘要、空核心及伪称最小核心。[开发失败记录](D:/毕业设计/auth-lifecycle/docs/VALIDATION.md) [攻击面](D:/毕业设计/auth-lifecycle/docs/CERTIFICATES.md)

另一条独立审计针对research_v12的AB3。含probe的联合策略被重新标注为control-only后，冻结检查器返回VALID，而control-only参考为IMPOSSIBLE_IN_MODEL。原因是可行树重放缺少逐节点动作类别校验。当前核对的independent.py摘要仍为`736440acc5d135ae913f69b62db656a26d4f288fc7d46035cbc15ea2753c62ba`，该合同的修复状态继续登记为待验收。[反例输入及结果](D:/毕业设计/research_secret_recipe/SCOPE_AUDIT.json) [本轮源码摘要](D:/毕业设计/thesis_draft/SOURCE_MANIFEST.json)

两条失败分别属于不同版本和检查路径。v1.2 scope反例限制其control-only证书健全性，资源谱的手工数学命题另有证明链。修复路径为递归绑定scope允许动作、保持完整Post、拒绝伪装策略并对正常证书回归，工程执行列入待完成项。[scope分析](D:/毕业设计/research_secret_recipe/REPORT.md) [待办](D:/毕业设计/thesis_draft/POSTPONED_UPGRADES.md)

## 5.5 原始材料与复现

L0原始目录保存输入、策略、反证、逐查询结果、环境和源码哈希。R3保存随机输入、执行见证、谱实例、量词回归和确定性重放。报告中的源码摘要只标识实际文件版本，历史数据与当前源码的差异通过快照解释。[L0工件](D:/毕业设计/auth-lifecycle/docs/VALIDATION.md) [R3命令与文件解释](D:/毕业设计/research_recipe_r3/MATH_REVIEW.md)

本轮交付的SOURCE_MANIFEST记录被引用历史材料的摘要，DELIVERY_CHECK记录组装一致性。有限测试支持登记范围中的实现行为，真实服务抽象保持、外部复核和正式统计效应仍依各自状态使用。[组装来源](D:/毕业设计/thesis_draft/SOURCE_MANIFEST.json) [原生边界](D:/毕业设计/research_recipe_r3/NATIVE_PREMISES.md)
