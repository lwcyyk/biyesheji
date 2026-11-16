# G2-R02 范围、版本与证据

2026-11-10，Asia/Shanghai。主课题：《面向用户与 AI 智能体的全生命周期密码与凭据管理系统》。本轮为知情模型辅助纸面研究，外部数学/系统核验待取得。

## 1. 继承

G2-R01十份主稿/静态数据在当前对话已完整编写核读；20项旧输出与原QA匹配，QA回执另固定。G1-R01/R02/R03、静态流C1—C7/P1—P4/E1—E7、11月9日R2课题修订和严格分离判废沿用各自范围。局部进展组合已被成熟方法覆盖，G1/G2接口仍有真实接线缺口，本轮不重新包装该架构。

单次旧refresh直接容量1、同父并发可两子代、父失效后旧handler仍可创建、actual_sends为发送前记账机会等结论继续。所有目标后代须计入或封口，B的UNKNOWN有自己的执行责任，原W完整终态不改。

## 2. 三层模型

| 层 | 内容 | 本轮结论范围 |
|---|---|---|
| NATIVE_CHECKED | 已核Casdoor与当前Controller能力 | 两项未知可建保守模型；完整q/恢复/原生前沿能力未接通 |
| SYN_BOUNDED | 明确合成的有界诊断/幂等恢复/围栏服务 | 完整实例与精确最优费用手算只对此层成立 |
| FORMAL_DYNAMIC_AB | 有限、显式或有界因子化状态/转移输入 | 到通用AND/OR精确编译；来源若只是过近似则到真实服务只得单向安全结论 |

合成能力对候选和G完全相同；其数值结果不作为Casdoor实验、部署能力或新协议验证。无界失败版本保留UNKNOWN/安全退出，不能借正例有界假设删去真实不利后继。

## 3. 本轮核读

来源与哈希见 [SOURCE_LOCK.json](evidence/SOURCE_LOCK.json)；范围/原文定位见evidence/SOURCE_INDEX.json。

- 当前L0/A/B/AB、参考与检查器按G1已读字节复用；定向读research_v12的README/REVIEW/AUDIT/ledger、A4、B4、独立证书transfer和旧反例。FullB.native指有限B问题，保持与原生HTTP消歧。
- 新定点读DRD原文物理p2—4，Shielding p2—4，多成本POMDP p3—5（p2绪论定点），Value Equivalence p3—4。四份PDF结构预检PASS；POMDP p5及Shield p4目视核对。公式/保证按已读范围，附录证明与全篇实验未核。
- P10署名顺序采用固定PDF首页Carr/Junges/Jansen/Topcu；旧汇总作者顺序差异保留原字节。P11正式卷号沿既有官方记录286，局部PDF旧页脚差异继续登记。

## 4. 权限与过程

只读定位/文本/AST/哈希/PDF取证、纸面推导、静态数据与报告。新候选/参考代码、求解/穷尽、项目模块执行、schema/证书检查器调用、测试重跑、原生/账号/外发及新代理均0。静态实例和转移规则由手工填写，工具只解析JSON文本/检查文档，不求解或枚举数学状态。

沿用academic-research-suite与PDF阅读流程。COL2026主动检索暂停，FS23延期，VPass废弃。旧源码、结果、UNKNOWN/失败/历史分母及A4/B4/AB3强基线覆盖保持。

## 5. 交付导航

| 文件 | 内容 |
|---|---|
| [01](01_DYNAMIC_AB_PROBLEM.md) | q原生能力审查、完整问题与初态 |
| [02](02_TRANSITIONS_AND_OBSERVATIONS.md) | 动作、全部观察、后继/责任规则 |
| [03](03_SAFETY_AND_COST_CONTRACT.md) | 完整/部分目标和固定费用口径 |
| [04](04_GENERIC_ANDOR_COMPILATION.md) | 精确通用编译和最优递推 |
| [05](05_POLICY_AND_COST_PRESERVATION.md) | 双向策略/费用及真实服务限制 |
| [06](06_DYNAMIC_INSTANCES.md) | 完整正例、五对照和手算最优值 |
| [07](07_COMPLEXITY_AND_STRUCTURAL_ANALYSIS.md) | N/信念规模及全流程复杂度 |
| [08](08_STRONG_BASELINES_AND_NOVELTY.md) | 原文、结构方向和九项准入卡 |
| [09](09_G2_R02_VERDICT_AND_NEXT_STEP.md) | 十问及唯一下一步 |
