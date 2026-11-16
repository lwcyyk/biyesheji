# 创建机会、失败后继与全局责任

证据：G02:290—388、149—154；G03:562—769；C01:227—342；C03全文；C04:101—113、189—232。所有轨迹为源码推导，未发API。

## 1. 创建单位与容量

`j_issue=(originV,rV0,attempt0,release_version0)`；`j_refresh=(originV,rV1,attempt1,release_version1)`。每次放行与每次HTTP机会分别存在；本地spent、NativeHTTP reservation H、物理发送、AS处理、AddToken、结果持久登记是不同事件。

在单次受控发送、单次服务端handler、无隐式重试/代理复制、AddToken至多一次和模型符合源码的条件下，每项机会最多创建**一个原生持久Token单位**。一束含AT/RT/ID字符串；AT/RT共享本例原生单位标识，ID Token有其claims，不因此计成三个独立根。生成了但未持久/未交付的在进程JWT、日志和外泄风险需要另管。

正常轮换开启：issue产生z0；refresh产生z1并删z0父行。累计新增单位上界2；非事务顺序允许AddToken后、DeleteToken前同时存活2。z1仍有RT派生能力。当前预算2用尽/撤回gV只封受控新release；外部RT持有者、多活、已通过检查的handler仍需前提与责任。

轮换关闭拓展：z0与z1可共用同RT hash，最多两个原生行却可能属于同一RT失效组。因此 G_ever、G_peak、字符串数和撤销域数分别记。主profile已知轮换开启。

## 2. 全部主要后继

| 后继 | 可知事实与剩余责任 |
|---|---|
| Issue排队未release | 撤回可取消；未形成放行后的创建责任 |
| release后尚未reserve H=0 | 本地DISPATCHED_UNKNOWN；仍可能执行，除非有可靠未发送/取消终态 |
| H=1后尚未open | 已付机会费；配额耗尽不再阻止此请求，保留创建可能 |
| Issue在认证/策略检查前失败 | 可能无Token，但失败次数/冻结/账号写可能已发生；当前适配器一般记UNKNOWN |
| 生成JWT后RecordUserSignin失败 | 可有账号写/部分故障；不能声称完整无副作用 |
| Issue AddToken后、后写/响应失败 | 可能已有z0；j_issue保持未知容量 |
| Issue成功并可信登记 | 结果绑定gV；可作为同origin refresh源；旧i来源未变 |
| Refresh尚未release/未发送 | 分别按队列和H记录；只有可证取消才移除机会 |
| Refresh通过旧父检查后暂停V | 即使随后父撤销/其他验证成功，handler仍可创建 |
| Refresh AddToken后响应丢失 | z1可能有效；j_refresh保留；z0是否删另判 |
| AddToken成功、DeleteToken报错 | z0/z1都可能保留；返回错误无法排除子代 |
| gV变化后结果迟到 | 按原origin入QUARANTINED；不重新归甲或乙 |
| 清理请求失败/丢响应 | 记录独立disposal机会和不确定后继，保留材料责任 |
| 管理处置资格丢失 | 当前安全退出，待合法恢复；有界完成无保证 |
| z1持有者或已放行刷新仍在 | 增加派生前沿；命名材料失活不结清全部creator |

## 3. 持久义务模型与实现差距

纸面总账使用

`O = O_A_old ∪ O_B_execution ∪ O_V_issue ∪ O_V_refresh ∪ O_V_known ∪ O_V_derivation ∪ O_disposal ∪ O_account`。

每项至少保存origin、operation、rid/attempt/release version、预算/容量、证据引用、已发现单位、已处置路径、剩余创建可能和关闭前提。旧i1/i2的既有来源始终归A；新V机会归V。账户写属于共享影响，独立来源不能屏蔽它。

C01现有state_projection列出DISPATCHED_UNKNOWN/QUARANTINED及未闭window。它提供部分持久责任基础，尚未实现这份完整派生/账号/多尝试总账。因此“模型列齐”与“程序可靠覆盖全部责任”分开裁定。

同rid重复提交不会免费重新release；这不等于AS按本地rid幂等。新rid重试增加新容量。native lookup只回放已经持久收件的原结果；未收到响应时它无法从AS补造结果。identifier journal也只记已收到验签后的标识。

UNKNOWN Issue：当前begin_reconciliation仅接受未知refresh；点读SQL也固定refresh。因此即使Issue journal存在，已有对账入口仍缺接线。双旧未知及第三grant也超现有枚举证明前提。

## 4. 旧任务关闭边界

gV不重新激活gA，也不迁移甲的义务。若旧创建前沿曾凭完整source/fence终态关闭，独立新V在理想分来源模型中只扩V；本轮原生没有取得该完整Fence。

在实际账户级枚举证明中，V会扩材料宇宙、授权关系、计数上界和潜在来源，破坏旧的“唯一未知＋两批准/预算20”充分条件。需要重新建manifest和来源归属；已返回的旧scope证书不能在新scope下自动重放。

乙保留还依赖：b与A/V的RT hash组不同、处置动作局限于这些命名材料/组、普通账户保持有效、预算/时间足够。账户禁用、删除或更广登出可能同时毁乙，必须从安全动作集合排除或重新批准。

## 5. 处置与退出

先撤回gV，再处置已知QUARANTINED材料。正常dispose最多三次机会；每一次失败/重试分别计。Token已到期可能在本地验签阶段失败，当前程序缺到期事实到闭合状态的通用精化；不能靠异常删除义务。

有限安全退出：在当前本地事务/存储可用前提下，撤回、持久保存O并停发，预算可设为有限。原生完全关闭的最坏完成时间/费用在持续UNKNOWN、未封handler或管理失权后无统一有限界。UNKNOWN和SafeExit均不计COMPLETE。

裁决：新机会的纸面分类已列齐；现有程序的端到端完整义务精化为 `SOURCE_OR_REFINEMENT_GAP`。没有新增可靠终态协议或代码。
