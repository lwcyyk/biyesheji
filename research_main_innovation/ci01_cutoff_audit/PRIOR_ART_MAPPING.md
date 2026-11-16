# 先例映射与分离门审计

## Material Passport

核读范围采用原文文本行/章节定位，文献结论与原生实现能力分别登记。前三篇全文已在项目取得；本轮复读相关假设/性质/恢复契约。RFC和SQLite原文通过官网HTTPS取得并保存摘要；检索连接器返回传输错误，回退记录见[ADDITIONAL_SOURCES.json](ADDITIONAL_SOURCES.json)。本轮未复现外部论文工件，也未重新搜索新研究方向。

## 直接先例

|原文与定位|已覆盖原理|本轮实例与准确边界|
|---|---|---|
|Zhu、Wang，**Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution**，2026，arXiv:2609.21284v1；Table2 A1–A11、Thm1/2/3/6。[入口](https://arxiv.org/abs/2609.21284v1) [取得全文](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P03_全文.txt)|完整中介、可信cut、支持来源、资源fence/前沿、独立支持保持及有限排空；Thm2讨论不完整枚举/不可执行前沿下的观察边界|本轮找到get-tokens，但其分页/来源/截止水位不足以直接实例化全部前提。Cookie说明manifest应覆盖衍生载体。没有给出满足全部A1–A9仍失败的反例|
|Tong、Dai、Guo，**AID-Guard: Stateful Authorization for Delegated Agent Effects**，2026，arXiv:2608.21159v1；§III的提交/Conservative Recovery、§IV P2。[入口](https://arxiv.org/abs/2608.21159v1) [全文](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P05_全文.txt)|原子或受控幂等提供方；明确未知保留计费；no-effect需要稳定attempt、与提交线性化的终态化、权威终态查询、持久保留与delivery fence|OAuth列表缺attempt终态；枚举空页不能释放未知义务。可取得迟到成功结果时按原来源收尾；一般保护原则已有覆盖|
|Murphy、Radomirović，**Verifying Account Ecosystems With Graph Transformations**，IEEE EuroS&P 2026，DOI 10.1109/EuroSP68448.2026.00038；§3/5及Definitions18/20、§6案例。[DOI](https://doi.org/10.1109/EuroSP68448.2026.00038) [全文](D:/毕业设计/关键论文与可行性核查_2026-11-04/阅读记录/P08_全文.txt)|资源/主体/访问方法图，供应商规则与对手动作图转换；完整性与AG EF可恢复访问；可用通用模型检查|将token/Cookie/应用节点和微步骤输入通用转换系统即可表达本轮反例。持续B与部分观察统一安全策略需另给目标量词，当前没有算法分离|
|Lodderstedt等，**OAuth 2.0 Token Revocation**，RFC7009，2013；§2.1/2.2/3。[原文](https://www.rfc-editor.org/rfc/rfc7009.html) [取得文本](sources/rfc7009.txt)|200也可对应无效token；同grant级联按服务策略；AT的在线/自包含验证影响撤销传播|父RT已消费后200无法证明整族截止；资源端只验签也不能免费获得即时R。本文沿用该语义边界|
|Lodderstedt等，**Best Current Practice for OAuth 2.0 Security**，RFC9700，2025；§2.4、§4.14.2。[原文](https://www.rfc-editor.org/rfc/rfc9700.html) [取得文本](sources/rfc9700.txt)|刷新轮换重放检测要求保留旧新关系；发送者约束与安全事件撤销已有原则；ROPC在当前安全建议中已弃用|Casdoor所查轮换删除父行，本轮缺少任务族持久关联；记录来源/族截止是既有需求。password仅作项目历史可复现profile，真实AI部署适用性需另由授权码等子域证据承担|
|SQLite官方 **Isolation In SQLite**，在线文档，无论文优先权主张。[原文](https://sqlite.org/isolation.html) [取得页](sources/sqlite_isolation.html)|读事务隔离与写序列化；事务边界由应用实际调用决定|单SELECT可有固定读视图；count、offset页和撤销属于不同操作，不能把数据库隔离提升成跨HTTP完整截止|

前三篇书目信息沿用已取得的项目全文/元数据；本轮重点复读上述模型和命题，未宣称逐页外部复核。以文本行定位避免把未经本轮PDF结构预检的页码当作新校验结果。RFC原文只用于规范对照；实测结果以本机原始事件为准。

## 剩余命题的先例距离

|本轮命题|最强适用通用方法|判定|
|---|---|---|
|静止有限域完整清单＋逐项撤销|完整枚举、可信来源、有限排空、逐项处置；可由通用状态规划选择|PROFILE_COVERED；既有方法的条件性实例|
|非轮换hash组批量失效|原生ExpireToken组更新，辅以活跃代表查找|已有接口能力；没有候选机制或严格收益比较|
|固定RT绝对期限＋最长AT寿命|通用过期等待，计可靠时间与B续期资源|经典期限边界实例|
|活动刷新追赶/页间修改|通用状态展开/图转换可发现；完整中介、持久fence或已知最终静止可解决相应前提|KNOWN_BOUNDARY_INSTANCE，当前未形成新紧刻画|
|独立应用删除仅覆盖部分资源路径|作用域完整性与派生载体闭包检查；再加原生token/session处置|C11为真实能力反例；补齐闭包后可能仍是既有正确组合|
|多路径下保留B且完整截止A|先冻结全部可达路径/配置权限、逐项实例化原生闭包及RQ/AID条件|CAPABILITY_UNRESOLVED；尚缺可比较的封闭输入族与一般充分性/下界|

## 严格分离门

输入族：本轮只有F_closed、若干带额外条件的F_active子域，以及批量清扫的对抗调度族。度量已显式包含HTTP、输出、持久状态、授权单位、等待、B续期和失败清理。最强通用组合G1–G5已纳入原生配置与管理接口，没有给未来候选额外能力。

预测严格差距：尚未建立。存在通用方法必须支付更大代价、而某候选能在相同安全/功能/信任前提下更低代价完成的实例数为0。S1/S2等表明某些简单错误组合失败；它们无法充当最强通用方法的下界。因此NEW_CHARACTERIZATION_CANDIDATE和SEPARATION_CANDIDATE均保持空，候选机制实现门关闭。

七种已淘汰A2/A3/B2/B3/AB2/AB3重放/B4压缩继续沿用既有结论。当前成果新增了原生profile证据和组合前提定位，未宣称新的同步、撤销或信息获取原理。
