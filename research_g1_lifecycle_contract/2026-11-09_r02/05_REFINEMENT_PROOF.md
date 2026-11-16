# 真实源模型到微步骤合同：P1—P8

## 1. 抽象与模拟

M_P由锁定Python/Go主路径、标准传输/数据库及04 A01—A12组成，未量化任意AS实现。α保存02的控制位置、身份等式/顺序、批准/预算、P/B/C及已加载父、响应/日志/权威phase和未结责任。未知原生ID映成固定槽，托管侧保留原ID恢复关系与代次依据。

obs只输出运行者获准数据；α中的AS内部位是证明ghost。K为与同一运行历史相容的全部α状态或其可靠上近似，算法不能选真实ghost。

固定M_P内，对每个可达s、允许微步骤a和真实s'，有相应合同转移（可含有限τ步）满足α(s')∈Post_C(α(s),a)。证明按本地事务、原生调用前、AS检查/生成、唯一插入、插入后更新/删除、响应/验证/日志、record/revoke/对账/恢复分类；02列逐步关系，03列故障后继，04界定容量。所有中间状态也保持安全/义务。发现未覆盖的外部创建、复制处理或额外派生时须退出当前合同或扩模型，保留真实责任。隐藏的部署违约并无自动检测证明；这类执行不属于满足假设的M_P，边界标志不能补救失真的前提。

这是人工关系证明，未生成/运行机器检查表；source到部署忠实保持显式前提。

## 2. P1 初始覆盖

**命题。** A01/A07且全部既有材料、批准、预算、pending入初态时，α(s_0)∈K_0且K_0非空。

**证明。** 固定身份/角色映射；来源已知项放对应槽，未定项取全部相容来源；按真实phase放入排队/已放行/结果/隔离/处置位；未知网络/AS位置取全部允许状态；预算来自同一权威快照，既有费用为前缀常量。真实投影按构造被包含。

**缺口。** 这提供纸面初始化，当前无统一自动snapshot构造器。recover投影缺request正文/operation/source_rid、材料及批准操作字段，需要受权原请求引用并校验或专用投影。缺字段可保留更多可能性，不能假定其值已知。命题CONDITIONAL_ON_ASSUMPTIONS；实际接口SOURCE_OR_REFINEMENT_GAP。

## 3. P2 前提与批准

**P2-local。** A01/A02下，成功release的caller、grant/task/account/audience/generation、operation、source_rid满足源码当前active/窗口/预算检查。

证明：admit核handle/caller和全部绑定；release从权威请求/同origin RESULT_AVAILABLE源取材料。revoke/release按同一事务顺序，先撤回则取消，先放行则保留责任。并发同rid只有一次send=true。状态PROVED_WITHIN_PROFILE。

**强化反例。** release后撤回，再由已放行handler插入C是合法轨迹；AS无本地批准版本与提交栅栏。“AS插入时批准仍active”不被当前链保持，状态COUNTEREXAMPLE_FOUND。C_local按新放行截止定义；抽象动作要求提交时批准时必须拒绝该映射或增加原生前提。

## 4. P3 失败后继

**命题。** M_P中02覆盖03所列、满足固定前提的故障类别/交错，UNKNOWN保留未创建、已创建及以后可能创建等全部相容分支。F18/F19及F20中的整体重入在放宽传输/dispatch前提时需扩模型；本定理不将那些越界执行强纳入c_i=1。

证明按pc：创建前没有唯一Insert；Insert保留0/1提交；插入后错误保留C与P删除独立状态；超时仅改变本地观察，AS可继续；日志/权威提交回执丢失保留两种提交事实；恢复读当前权威；重放/并发按本地串行和原生交错处理。逐步包含归纳得到全部前缀覆盖。

限制：helper效果、框架dispatch、二进制忠实等依A03—A06；模型外分支必须边界退出，空K不能成功。状态CONDITIONAL_ON_ASSUMPTIONS。

## 5. P4 创建容量

在A01—A07下每放行直接创建≤c_i=1，证明见04。首次发送尚未发生仍保留一个潜在槽；可靠不同创建见证饱和上界后该handler不再新增第二单位。后续RT调用必须入I或封口。每父1/无限后代1的强化由08反例排除。

状态：直接容量CONDITIONAL_ON_ASSUMPTIONS；相应扩大范围COUNTEREXAMPLE_FOUND。

## 6. P5 观察保持

| 观察 | 可采用结论 | 仍需独立责任 |
|---|---|---|
| actual_sends=1 | 预记账机会1，A02/A05/A06下给直接上界 | 已发送/已处理/已创建的下界 |
| 非200/UNKNOWN | 对应pc允许后继的并集 | 无创建或返还spent |
| RT内省inactive | 指定时点/路径inactive及相容原因 | 实际刷新已执行、旧handler终止、全部后代失效 |
| 实际refresh错误 | 已调用该端点，按源分支解释 | 通用错误不证明零创建；探测需计副作用 |
| AT UserInfo拒绝 | 该AT在cookie-free指定路径的观察 | 其他AT/RT/RP/cookie及业务效果 |
| revoke成功响应 | 执行了源revoke处理 | 找不到/非本client记录也可成功；关联关闭另证 |
| 可靠journal/点读/集合见证 | 合法范围/代次/来源成立时加入U、约束E | 签名JTI单独不证明任务来源或全集完整性 |
| B后处置检查 | 处置后一次乙UserInfo成功、检查时grant active | 当前/未来全部能力持续可用 |

证据：introspect可因记录缺失/ExpiresIn≤0/JWT或用户无效而inactive；revoke对不存在或非本client单位也返回成功；ExpireToken不终止已加载父的刷新线程；UserInfo经AutoSigninFilter的记录/过期/用户检查。中间件注册、cookie-free、标准time及响应忠实均须固定。材料签名验证与任务来源证明分开。状态CONDITIONAL_ON_ASSUMPTIONS。

## 7. P6 预算与费用

P6-local：reserved等于QUEUED数，spent等于历史成功release数；admit增加预留，release转spent，取消只退reserved，其余不退spent。事务回滚/重放不重复改变计数。状态PROVED_WITHIN_PROFILE。

P6-cost：合同采用06完整微步骤价目及重试界，分开计RPC/本地维护时，任意前缀实际费用≤已收费/预留上界；按一步费用求和归纳。状态CONDITIONAL_ON_ASSUMPTIONS。现有A/B/AB Q尚未绑定新价目，C_compute/字节/时间无统一现成换算，端到端实际费用映射仍SOURCE_OR_REFINEMENT_GAP。

## 8. P7 终态

C_closed(T,paths)要求：目标入口封口；全部潜在创建/派生入I；真实f∈F≠空；U为累计不同见证，D持续失效且覆盖paths/声明后代；H_T=C_T−min_f|D∩f^{-1}(T)|=0；其他严格义务分别终结。

**命题及证明。** A01—A11和上述条件下，固定真实f，已见仍可用目标≤|f^{-1}(T)\D|，未见/未来目标≤C_T−|f^{-1}(T)|，合计≤H_T=0。因此该材料范围无剩余可用或迟到创建。该充分证明不需C6的全可实现性；必要性另需C6。F空表示证据冲突。

单attempt取c=1，可靠同源C见证使直接余额0，再处置全部相关已知甲单位、排除其他甲来源/后代可关闭。make_receipt/save_reconciliation核结构和提交事实关系，源忠实、外部创建者排除及持续失效仍依合同。C_local是新放行截止；C_effect、全RP或无限后代尚未得到此证明。状态CONDITIONAL_ON_ASSUMPTIONS。

## 9. P8 乙保留

**P8-obs。** B_preserved_after_disposal为真时，存在独立grant的一次乙UserInfo，其release_version晚于最后甲处置completed_version，结果phase为RESULT_AVAILABLE，保存context时grant active。在A01和provider响应忠实下，该调用在执行时通过UserInfo检查。

证明展开storage.reconciliation_context及provider的sub核对。该标志证明一个已发生操作，旧成功不自动保证当前/未来可用；材料可能随后到期。

**强化反例。** 对账窗口暂停同账户全部issue/refresh，乙申请refresh被拒。共享父/共享效果域也可能损害乙；窗口关闭后的业务完成仍需时间、服务和任务合同。“乙持续刷新并完成全部业务”为COUNTEREXAMPLE_FOUND；P8-obs限已发生的UserInfo操作。

## 10. 总体保持范围

M_P→C_refresh有上述局部证明与条件性源关系；一般L0纸面编码见07。当前A source/B/AB语法、运行输入投影、原生动作接线和完整价目仍有具体桥接责任。本轮未声称现有运行源码已实现端到端全部保持，创新状态独立管理。
