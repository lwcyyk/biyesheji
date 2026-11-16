# v1.2 开发前审计

基于本轮前半程的完整阅读与源码核对。v1.1 DOCX SHA256：7ba78ed7c1ce45a73872a8c82b95f18c2624680ebbaa512aff3932883a67ebe4。原项目无可用 Git 提交；用源码哈希标识版本。

|算法|源码入口（相对旧算法目录）|实际机制/目标|参考|负结果及缺口|
|---|---|---|---|---|
|A2|prototype/a_ab_search.py:solve|早承诺，完整继续代价 Q 搜索|受限 acquisition_reference|通用同语义 BB 复现；非 unrestricted 联合策略|
|A3|同文件 continuation_signature|完整未来行为签名及策略提升|同 DP|3 诊断零命中，构建非免费|
|B2|prototype/b_units.py:solve|原生单元层枚举，(G, configuration) 最小|b/reference.py，Z3 Optimize|预处理成本偏高|
|B3|prototype/b_components.py:solve|独立组件前沿及预算卷积|R-B|3 分解/17 耦合回退|
|AB2|prototype/a_ab_search.py:drd_bound|静态 DRD 下界，动态条件不满足时回退|R-J|有效但无净收益|
|AB3|旧规范而非实现|未实现|无|不得沿用旧结果声称本轮通过|
|联合 B|prototype/common.py:fixed_b_choice|B2Select 目录选择，非完整 B2/B3|W 已核验的目录|本轮必须替换为真实完整子问题接口|

旧 A/AB Q 计入 probe、configure、stop、cleanup；终态要求无严格义务。AB2 开关同状态、动作、安全核和缓存。旧研究已记录编译/检查成本，但不代表完整产品准入与原生部署验收。旧输入有静态、有状态、高阶冲突和未知结果。

本轮不修改上述机制或历史结果。新联合目标继续为 Q；完整 B 的原生 G 结果仅作条件配置建议，不能作为跨世界统一策略或据此删去联合可行动作。AB3 的 control-only 不可能证书不等于允许 probe 的整体不可能。

已取得：原模型/参考/检查器、旧输入原始 JSON、Z3 4.15.4.0、本地 Windows 资源约束。缺口：四阶段独立 schema/SQL 附件未取得；原生服务状态迁移及真实来源保证未完成；没有新留出集或确认性登记。旧材料阅读范围沿用 v1.1 材料护照，不虚构人类已读。

密码学继承：C3 与独立分块等效；GF(4) 限制拒绝原成功域 18 个输入；gate 已计算零标志；不扩大 MPC。代数分量不等于 G，自洽证书不证明来源，MPC 中止不证明外部请求未执行。
