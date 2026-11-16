# 反例与A01—A24实施前评审

本稿及DSAT_CASE_MATRIX均为手工预期，全部NOT_RUN。R04的REF_ONLY_DIGEST、C_prefix和合同引用是符号占位，不能直接当完整可执行原生样本。R05给逐项实例化要求与独立评分依据，原R04文件保留。

## 1. 十六种失败边界

| ID/前提→可信观察 | 可能执行/违反条件 | 预期状态、保留义务、最小修复 |
|---|---|---|
| F01 三观察其中两同birth | 一次创建被inbox/journal重复计；违反互异U | UNKNOWN/去重；旧settle保持；以同birth引用合并，再算R/H |
| F02 三原生行缺birth映射 | PK重用/代次不明，三条观察未必三次互异创建 | INSUFFICIENT_COVERAGE；保留别名/风险；取得代次/源映射，未证部分不计U下界 |
| F03 c=1但多发送/handler | 两handler通过同父检查各AddToken；容量前提失效 | SOURCE_OR_REFINEMENT_GAP/CONFLICT；保留额外创建；绑定传输/实际次数或用可靠更大容量 |
| F04 E漏真实来源 | 实际新单位来自V或外部，模型硬给A | 来源真实性失败；停关闭、保O；有证据才补I/E并重核 |
| F05 第三批准有创建余量 | gV在旧三槽之后合法新release | OPEN_FRONTIER；加V入口/O；限定旧attempt证书或覆盖新调用 |
| F06 旧refresh仍可创建 | 空Find后handler从V插入c | UNKNOWN_PENDING；settle保留；容量饱和或真实无效果/创建全集证据 |
| F07 父删后旧handler续写 | handler已通过检查，删p不阻后续AddToken | 不给全系关闭；保后代/O；单独覆盖全部旧attempt |
| F08 D只有点时false | 用户状态/配置恢复或其他未约束写入重新允许使用 | INSUFFICIENT_COVERAGE；close:u保留；补持续frame/失活源分支 |
| F09 P漏一接受者 | Token表删行但离线RP接受JWT，或已有cookie有效 | SOURCE_OR_REFINEMENT_GAP；保未覆盖路径；缩P或取得该路径合同 |
| F10 两birth挤同cap1 | A19不足割3<4 | EVIDENCE_CONFLICT；保两证据/原O；核代次、c、I/E和权威基准 |
| F11 删除历史U | u已创建后删行，重建只取当前存活列表 | 容量会被错误恢复；保tombstone；重建历史引用，缺失保持UNKNOWN |
| F12 AS变本地version不变 | 旧i自行完成AddToken，无权威事务 | 当前证书依赖失效/重核；保新风险；独立检查AS前沿/frame |
| F13 跨原生合同重放 | 旧P/轮换/接受路径版本与当前不同 | STALE/SOURCE_GAP；历史事实保留；重新绑定证据和失活范围 |
| F14 冲突后清旧O | F空被当真值，或较晚条目覆盖早来源 | EVIDENCE_CONFLICT；原O不删；导出全相关条目并停止强关闭 |
| F15 A/B共享影响 | 同账户disable/delete或同RT hash组同时影响b | 阻断不保B的计划；B保护与O保持；按动作影响域选择/缩目标 |
| F16 H_A=0但审计/效果未结 | 尚有await_terminal或已接纳业务效果 | 可限材料C_native；全局COMPLETE未得；保审计/effect义务或独立终态合同 |

这些轨迹反驳特定错误推断，保守UNKNOWN/拒绝是正确边界行为；未证明所有算法或所有原生操作不可能完成。

## 2. 24例分组与处置模块

R04基础模型保持p/b真实来源；R05实例化显式D，不以default字段代替证据。以下数值均条件于有效有限组合输入，阻断类不伪造R/H=0。

| 例/组 | 资格与预期 | 拒绝/检查模块；未来路线 |
|---|---|---|
| A01/G1正例 | D_sat且D_close；R_A/H_A=0/0、V=0/0 | 流/源/证书；离线先验，原生前提另验 |
| A06/G1正例 | 六种归属仍0/0；无需唯一来源 | 同上；缺D/第四来源变体亦纳入 |
| A02/G2缺口 | R_A/H_A=1/1，V=1/1 | 投影/O；可靠一成功与两未知字段补齐 |
| A03/G2缺口 | p已持续失活时A=2/2、V=1/1 | 空收件/终态不抹历史风险；投影/O |
| A04/G2缺口 | 单新v连三源，A=2/2、V=1/1 | 来源图/流；保留多边，不硬归Issue |
| A05/G2缺口 | 当前全域有开放V入口，R/H不认证 | scope/frame/manifest；不扩用旧2/20 |
| A07/G2缺口 | 完整当前集合未得；不签关闭 | 查询coverage；正向见证可保留，空页无额外排除 |
| A19/G2缺口 | F空，R/H未定义 | 独立割核验与冲突托管 |
| A20/G2缺口 | B当前性陈旧，相关使用不评R/H | 依赖/权限；历史状态与新许可分开 |
| A21/G2缺口 | 去重后仅c1→i1，D仅p时A=1/2 | birth/成本；不能用三观察假饱和 |
| A22/G2缺口 | 无界/未覆盖后代，全域R/H不认证 | 前沿/合同准入；有限直接切片另列 |
| A11/G3拒绝 | origin伪造片段拒绝，旧知识不缩 | 证据入口/原请求绑定；无新原生读 |
| A12/G3拒绝 | gB撤回后旧eligible不许可新调用 | 最终权威守卫；历史release可保留 |
| A13/G3拒绝 | 跨批准source_rid拒绝 | C01同origin；不形成新creator |
| A14/G3拒绝 | 迟到旧active不覆盖较晚状态 | 时间/来源归一；不可比较时UNKNOWN/STALE |
| A15/G3拒绝 | 不删历史c1；显式c1→i1且D仅p时A=1/2 | 历史/O；缺检查点不声称能检出全部删行 |
| A16/G3拒绝 | RT inactive不排除创建；仍旧风险 | 观察分型；不作新Refresh探测 |
| A17/G3拒绝 | 仅ACK、D为空：R_A=2、H_A=3 | 证书scope；C_local可成立，原生仍未决 |
| A23/G3拒绝 | 无全组织权则拒绝原生列表 | 权限入口；无需先读取再决定 |
| A08/G4责任 | 迟到c2→i2，若仅p∈D，A=1/2 | 原origin隔离/投影/O；无旧任务恢复 |
| A09/G4责任 | A未闭，B有自身合法frame可局部准入 | 当前B守卫；A/V O不变，B执行未知另记 |
| A10/G4责任 | 账户级cut伤B，拒绝该保留计划 | 动作影响域；静态拒绝先行，避免真实伤B求PASS |
| A18/G4责任 | 显式i1已闭而i2/j待定时A=1/1；无COMPLETE | O/证书；未提供的字段不得自填成功 |
| A24/G4责任 | R_A/H_A=0/0但await_terminal仍在 | 材料证书可限scope；全局Goal/O另验 |

## 3. 从符号案例到可执行输入

每例需冻结：完整typed snapshot与query/event interval；原请求/批准/证据真实或明确合成来源；I/T/c/U/E及birth别名；显式D_P与frame；O_before/expected_O；输入/合同/证据/费用摘要；期望R/H或阻断原因；可行流/势或割；模块级预期状态与独立评分oracle。

S4可以对全部24例建立**合成合同**离线夹具，独立检查数学/权限/状态转换；其结果只属于离线规格验证。A01/A06/A08等真实创建/失活/迟到、A05/A07实际范围/分页和A10原生影响域还需要独立源/部署或授权实验。A19的数学冲突不必故意在真实系统制造。

R04占位摘要、C_prefix、D/持有者排除和event time必须实例化。所有案例当前保持NOT_RUN，不能把本轮手工流/势当机器检查PASS。
