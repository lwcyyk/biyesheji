# 静态验收与对抗案例

全部为X类手工设计，未运行项目检查器、流求解或原生操作。完整逐字段输入/权限/事实/相容状态/O/证书/费用位于同名JSON。预期结论是验收要求，当前机器通过数为NOT_RUN。

## 1. 共同符号与成本

基础I={i_p,i_b,i1,i2,j}，c均1；T_A={i_p,i1,i2}、T_V={j}。此处j为j_issue简写。p/b已知历史来源；i1/i2是A，j是V。gA已撤回，默认gB active；gV与未来入口状态逐例说明。材料标识均为纸面代号，均为非秘密标识。

F中的手工排列/极值只用于所列小图；一般费用交标准流包络。证据获取的历史AS请求保留在C_prefix。纯Project新增AS=0，需本地读/构图/验证/存储；未来若重新查询，按所列接口实际机会计，不能把获取价格标成0。

## 2. 十类必需案例

| ID | 主要输入/相容状态与预期 | O/证书 |
|---|---|---|
| A01 双Refresh可靠终态 | p,b,c1,c2,u；c1/c2可交换i1/i2，u→j；D={p,c1,c2,u}；F两种，H_A=H_V=0；前沿/路径frame齐 | ACCEPT_WITHIN_SCOPE；A/V限定C_native，B保留；全局完成仍按其他义务 |
| A02 一成功一未知 | c1→i1且已失活，i2无结果，j未知；D含p/c1 | H_A=1，UNKNOWN_PENDING；settle:i2/j保持，已知可处理 |
| A03 双未知且空收件 | i1/i2/j仍可0或1，p已失活、b有效 | H_A=2；空Inbox不消容量；无C_native |
| A04 未知Issue后新材料 | v既可来自i1/i2也可j，三条相容边；D含p/v | d_A最小1、H_A=2，H_V=1；保留所有来源和分组风险 |
| A05 第三批准改范围 | 旧manifest仅两grant/20，新gV active有创建余量 | INSUFFICIENT_COVERAGE；旧全域证书不可扩张；V前沿托管 |
| A06 完整快照但journal缺项 | 三新单位都只可来自三未知，三槽饱和，D含p及全部三单位；各新单位E连接三未知 | F六种，H_A=H_V=0；不唯一来源仍可组级关闭，依完整来源排除及D；日志缺项不伪造精确映射 |
| A07 分页/快照不全 | 一页无新项但理论界超page/第二页无一致性 | INSUFFICIENT_COVERAGE；保留潜在未见/迟到；无完整关闭 |
| A08 迟到成功 | 可信五元属于撤回A的i2；已有gA inactive | 原origin隔离，U/O更新；ACCEPT_WITHIN_SCOPE指迟到登记，旧任务仍无新许可 |
| A09 B独立支持 | A/j未知，b有当前gB同源支持、独立域与共享资源frame | B_ELIGIBLE后真实release再核；不删A/V O；UserInfo未知加exec:rB |
| A10 B共享撤销域 | A/B独立发行、RT不同但属同账户；候选计划以disable/delete user撤A保B | 账户级动作同时影响B，计划阻断；UNKNOWN_PENDING指尚未选得安全计划，纯独立B读须另核 |

## 3. 八类指定对抗及补充

| ID | 输入/攻击 | 验收结果 |
|---|---|---|
| A11 伪造origin | 未鉴别片段把V结果冒作A | REJECT_UNAUTHORIZED，不能缩旧K/O |
| A12 重放旧B许可 | 旧eligible后gB已撤回 | 当前调用REJECT_UNAUTHORIZED；旧事实保留/许可陈旧 |
| A13 跨批准source_rid | gV请求引用gA的p | REJECT_UNAUTHORIZED，沿C01同origin守卫，无发出请求 |
| A14 时间倒退/迟到旧观察 | 新收到旧active，不能覆盖较晚已核inactive；不可比较clock | 当前用法STALE_EVIDENCE；历史两观察都保留 |
| A15 删除不利创建历史 | 新快照删去旧U，要求恢复容量/抹责任 | 保留旧U/tombstone；无合法历史更正证明不得删除；缺基准时只能报告完备性缺口 |
| A16 RT内省inactive→刷新失败 | 没有实际Refresh结果、仅内省false | UNKNOWN_PENDING；creation_effect_excluded保持未证 |
| A17 ACK→原生关闭 | 仅LOCAL_REVOKE_COMMITTED | C_local范围可接受，C_native/C_effect仍UNKNOWN |
| A18 有O却签全完成 | 尚有未封i2/j，要求全局COMPLETE | UNKNOWN_PENDING；拒绝不支持的完整证书；独立局部结论可保留 |
| A19 F为空 | 两互异可靠创建都唯一指向容量1的同一尝试 | EVIDENCE_CONFLICT，保留证据/原O，不签关闭 |
| A20 证据过期 | b旧active已过适用窗口 | STALE_EVIDENCE，重核当前B；历史成功不删除 |
| A21 重复观察 | inbox/journal/点读重复同birth；UserInfo再次返回b | 去重，U不增长；ACCEPT_WITHIN_SCOPE，不伪饱和 |
| A22 无界派生/外部RT持有者 | 有未受控刷新能力、没有有限上界 | SOURCE_OR_REFINEMENT_GAP，全域H不认证，开放前沿保留 |
| A23 未获组织读取权 | 拟议全组织GET仅获本账户任务许可 | REJECT_UNAUTHORIZED；不能把事后筛选当批准 |
| A24 饱和但审计未终态 | 材料H_A=0及持续frame成立，尚有结果/handler审计要求 | 限定材料C_native可接受；await_terminal保留，COMPLETE未成立 |

## 4. 关键排错说明

A04只得到一个可能属于V的失活新单位：最坏它归V，A只由已失活p消费一个目标槽，所以H_A=3−1=2。不能把这份材料同时计给i1、i2和j。

A06三个互异新见证、三个容量1来源，任何f均饱和三槽。目标A的新部分一定占2，V占1；加已失活p得d_A=3。该全称计数允许保留精确来源歧义。前提是没有遗漏第四来源和未计后代，且D为持续路径证据；普通快照本身不提供这些前提。

A19是真实采纳约束不可共存，返回证据冲突；A18是待签声明不受支持，保留非空相容世界，不能为此人为清空K。伪造片段先被拒绝，不允许攻击者借假证据污染所有独立权威动作。

A10在固定轮换开启profile下也成立：RT撤销域独立不等于账户禁用动作独立，G08的账户访问终止会影响两份材料。非轮换配置中不同AT共享RT hash可作另一个版本化拓展，当前不以该拓展替代固定域实例。

对A15，现有普通日志无法保证发现一切删行；案例只要求在已知历史/检查点存在时保留它。没有这些证据时不得声称篡改已被完全检测。

## 5. 验收记录要求

未来每例记录输入哈希、合同/权限/版本、实际输出、预期对照、差异、O前后、证书scope、实际机会/本地成本、NOT_RUN/FAIL/PASS_WITHIN_SCOPE。隐藏评分真值不得进入选择器输入。当前仅填写预期，不填写真实PASS。
