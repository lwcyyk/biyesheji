# G2-R04：范围、继承与来源锁

2026-11-10。主课题：《面向用户与 AI 智能体的全生命周期密码与凭据管理系统》。本轮为当前对话内知情模型辅助源码核读、纸面规格、条件证明与静态验收设计。外部核验待取得。

## 1. 裁决摘要

在合法读取、可信当前权威、真实来源包含、有限创建容量及明确持续失效合同下，可以保守投影双未知Refresh、未知Issue和第三批准：保留全部相容来源，按范围输出已知事实、潜在创建、材料责任、缺证和冲突。

**条件可靠规格成立；一般真实原生关闭仍缺证。** 当前代码缺多尝试/Issue通用对账、操作/source_rid的受控快照、跨来源冲突保留、证书依赖及完整派生前沿接口。规范提供的UNKNOWN结果可以可靠托管这些缺口，无法把未知字段填成已证明的关闭。

状态：`READONLY_EVIDENCE_SPEC_READY / FIELD_PROJECTION_DEFINED / CONDITIONAL_SOUNDNESS / ENGINEERING_SPECIFICATION / ANALYSIS_ONLY`。`READY_FOR_IMPLEMENTATION_REVIEW`仅限进入实施评审，当前执行资格保持未取得。

## 2. 连续继承

G2-R03十稿、八份根JSON及全部evidence共24件在当前对话已完整生成核读，本轮按字节绑定复用。其中23件与R03 QA内输出清单匹配，QA本身另锚定。R03来源锁、G2-R02有限动态编译、G2-R01局部/全局组合、G1容量/精化及历史M2—M6范围一并继承；索引/实际范围见SOURCE_INDEX和evidence。

关闭的主动Issue→Refresh旧任务诊断候选继续关闭。不会以本轮投影名称恢复它。actual_sends保持发送前机会账本H的原义；直接c_i=1限单次受控发送/handler等G1前提。未知、失败、历史分母与源到二进制UNPROVED均保留。

## 3. 本轮限定对象

固定Casdoor v4.25.0源码参考提交`528a0213f01caf70b9f41009cbf7b2f67bdd67ec`。一个账户上A的i1/i2已release未知；gA撤回；p为旧父材料；独立B有b；gV为第三批准，其j_issue未知。示例把j_issue归gV，实际来源必须由权威记录确定，不能按叙事猜测。

批准本身不等于一次已发生创建；active且允许创建的剩余额度代表未来入口，必须记录或暂停。新gV不会把旧A责任迁走。轻率把I固定成三项会遗漏p、b的来源、重试与派生；02给出完整模型。

## 4. 来源编号

沿用R03短ID，绝对路径和哈希见SOURCE_INDEX：C01 storage，C02 services.Controller，C03 native_provider，C04 native_http，C05 enumeration，C06—C09角色/隔离，C10 materials。G01—G12为R03同批Go入口、模型、账户与UserInfo链；H01—H04为M6/M4/M3及历史语义。

新增重点：

| ID | 定位/用途 |
|---|---|
| C11 | protocol.py：19—70规范摘要/原请求，86—98 EventLog持久写 |
| C12 | reconciliation.py全文：单未知、单发送、单效果旧收据条件 |
| C13 | evidence_semantics.py全文：观察归一、内省与实际刷新分开、count非共同快照 |
| M01 | 多尝试PAPER_MODEL_AND_CASES.json：C1—C7、P1—P4及E1—E7，标准容量/流 |
| M02 | G1-R02 04_CREATION_CAPACITY_PROOF：A01—A12、直接容量与无限派生边界 |
| M03—M05 | G2-R01局部证书、全局O、T-COMP原文 |
| M06 | G1-R03裁决：raw L0/当前A接口与原生精化限制 |

C01本轮补读24—45、93—159、397—415；C02补读42—81、153—217；C03补读19—39、114—149；C04补读161—181。源码/历史输入哈希在SOURCE_LOCK，后验字节检查在DOCUMENT_QA。锁入材料不表示本轮重读全部前轮论文。

## 5. 证据等级与执行

S=源码事实；H=固定历史批次事实；D=前提明确的纸面推导；P=拟议接口/验收设计；X=静态手工样例。本轮全部JSON仅为静态资料，未被项目检查器解释或求解。

工具限文本、哈希、静态AST/JSON和文档取证。没有项目导入执行、实现/检查器/求解器/穷尽、测试重跑、原生请求、账户授权操作、秘密读取导出、外发或新代理。源文件与历史报告保持原字节。

COL2026主动检索暂停；FS23延期；VPass废弃；T3及既有数学/淘汰结论沿用。机制实现继续服从用户的严格分离门，成熟工程接线也须单独实施评审与执行授权。
