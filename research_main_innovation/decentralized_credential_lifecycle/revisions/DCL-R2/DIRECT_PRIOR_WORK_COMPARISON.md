# 直接机制与威胁模型对照：DCL-R2

2026-11-09。AID=[AID-Guard v1](https://arxiv.org/html/2608.21159v1)；RQ=[Root-Scoped Quiescence v1](https://arxiv.org/html/2609.21284v1)；EB=[EFFECTBOUND v1](https://arxiv.org/html/2609.02866v1)。本轮核读关键机制的完整段落及相关证明范围；全体附件/实现重放为0。原版完整题录沿用 SOURCE_AND_PRIOR_WORK。

## 1. 阅读范围与重要限定

|来源|本轮实际核读范围|影响裁决的限定|
|---|---|---|
|AID|§II威胁/TCB、§III-A–F、§IV-A–E，含恢复合同、证明草图及作用域|可信host/authority/effect boundary被攻陷时对应保证失去前提；恢复需原生稳定身份、竞争终态、查询与保留。原生能力不足时保留uncertain/charged，不会凭空生成fence|
|RQ|§§3.1–3.5、4.1–4.6、5.1–5.7；附录A.1–A.5中切断、支持、通道、合成、安全恢复与收敛证明段|root cut与sink barrier分域；每个carrier的实际选定支持、独立rebind、精确channel token与closed frontier均是条件。失陷可信gateway/伪造provider证据及未登记路径超出定理|
|EB|§§II-C、III-A–D、IV；附录C-A/B/D/E中post-invariant、配置历史、源到博弈与部署保持|有限契约、观察/控制双向精确性与真实Provider符合性各自负责；新配置复制旧issued/live store。动态部署保持仍需单独证明|
|SC-A2A|出版方索引摘要、Crossref；作者公开出版列表定向检索|IEEE摘要索引补得发表日2026-10-13、IEEE Access14:163751–163772；正式正文/实现仍缺。作者页仍标Under Review，与正式出版记录有更新时间差异|

SC-A2A摘要描述session/delegated grant、链上承诺和撤销状态、链下gateway及新鲜度/状态读取权衡。直接PDF、stamp与Crossref提供的staging链接均不可取得。本轮为该项保留 SOURCE_INSUFFICIENT，既未据摘要裁定全部覆盖，也未据全文缺失推断创新。

本轮正文定位和失败记录见 evidence/r2/web。shell直取三个arXiv HTML均超时，改由连接的公开阅读工具分段核读；记录保存的是返回段落，完整原文归档尚有缺口。AID证明仍是其自述proof sketches；RQ附录是其纸面条件证明；EB报告机器检查，本轮执行检查为0。

## 2. 17项机制比较

标记 D=先例直接覆盖；C=标准组合可覆盖；P=部分覆盖/额外前提；U=来源不足。此表的C是构造范围内的功能对照，发表优先权另审。

|机制|AID|RQ|EB|对D1/D2与G的裁决|
|---|---|---|---|---|
|原生结果未知|D §III-E|D UNKNOWN carrier/leaf|D hidden state|带费UNKNOWN与完整K可组合覆盖|
|已发送、回复丢失|D submitted/outbox|D 在途token/持久carrier|D hidden transitions|Casdoor缺稳定原生k时，双方禁自动创建重放|
|旧域崩溃|D 持久恢复|D A9及A.4|P 部署前提|C：共享当前权威/可用状态与成熟恢复|
|旧域恶意失陷|P 可信边界失陷超scope|P gateway失陷超scope|P Byzantine超scope|威胁模型有可核差异；G加入同等BFT/V/Gt后覆盖可行子域，泄露旁路仍双方受阻|
|旧域持有效bearer|P D0需要完整中介|P 需manifest/fence覆盖|P 排除alternate channel|按真实接受路径建模；Casdoor仅本地owner变化仍MODEL_BLOCKED|
|意图跨域继承|D immutable request/effect|D op/env不变及handoff|D source/carrier/history|C：持久i/o及转移对象|
|预算保持|D reservation lineage|P 全局预算非主定理|P 费用可输入|C：事务quota＋AID谱系，成本同口径|
|派生来源保持|D authority/effect evidence graph|D A4 provenance/support|D issued/live carriers|本地来源可保持；Casdoor原生父子元数据缺口双方都承担|
|未决责任迁移/关闭|D uncertain recovery|D §§4.3/5.4/5.5|D typed closure|C：工作流责任转移＋匹配原生证据|
|A撤销|D 当前授权与提交顺序|D cut＋barrier|D future/instance/lineage类型|本地新放行与原生各LP分列，无跨域原子魔法|
|B独立支持|P 新独立批准|D complete witness＋atomic rebind|P AND/OR语义可表示|RQ已直接覆盖独立充分支持；Casdoorcohort冲突由D2检查|
|多Provider效果前沿|P 按integration contract|D 各leaf＋channel/cutset|P 多边界建模需对应|C：RQ合成；实际provider接口仍需证据|
|证据范围完整性|D evidence graph/D0条件|D manifest/scan/token全集|D grounding/exactness|来源完整性是前提，签名/哈希只固定内容|
|新鲜度与接受端截止|D commit/recovery fence|D causal barrier/watermark|D boundary/frontier与I_post|Casdoor普通审计/查询无法直接生成等价fence|
|历史秘密暴露|P credential inventory|P 可建credential carrier，但无自动擦除|P 可将旁路放入P|C：历史能力闭包与原生状态；新增领域变量的系统化价值待独立查新|
|动态故障域|P 多region/可信失陷未闭合|P 固定manifest/可信profile为前提|P Byzantine排除|D2模型可表达；通用鲁棒博弈同样可表达，实际部署证明仍缺|
|配置→执行、共识→原生顺序|P store TCB及D2|D 分域因果序/配置header|D C-E条件模拟，跨版本另证|C：相同快照证书、BFT当前性、逐微步骤模拟；原生仍独立提交域|

## 3. 相同与不同的关键点

本轮增加的是具体Casdoor能力矩阵、原生handler缓存状态、shared-RT footprint和部署故障对应。它们为本项目具体精化提供证据；通用语义模板、关闭证书、来源/义务和有限博弈已有直接近邻。

RQ证书的主保证是退休root无法产生新的受保护commitment，允许其已接受且已准确记账的后果结算。D1若要求此后完全无被禁止物理/业务效果，需额外定义真实效果前沿并关闭已接受载体；提高目标与提供新机制分别审查。

以旧域失陷或动态故障作为差异时，需展示候选如何在相同native能力下阻断攻击。当前裸Bearer/密码的Casdoor路径仍给双方同一障碍；它无法成为候选单独满足的性质。
