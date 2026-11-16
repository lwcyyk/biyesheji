# 反例、范围与待准入验证

本文件均为纸面轨迹/计划，本轮新执行0。使用固定账户u、客户端c、甲批准gA、乙gB、有效父材料P；调用者由服务鉴别。未给出真实密码/token值，使用满足固定源验证的符号材料即可；实际源码字节与位置见evidence。

## 1. CE01：一次预记账并不证明发送

完整局部状态：gA active、budget≥1，原source_rid=P已同origin登记为RESULT_AVAILABLE。请求r=refresh(P)通过admit/release，reserved归0、spent=1，attempt=i。NativeHTTP.reserve INSERT一条refresh/i/r/digest记录后，进程在open前崩溃。

此时actual_sends=1、客户端完整发送=0、AS处理=0、新单位=0，权威为DISPATCHED_UNKNOWN。它否定H=1推出创建下界1。正确合同保留潜在0/1；若能可靠证明此时控制进程永久无发送且无其他创建，再另作无效果结论，不能仅靠COUNT。

## 2. CE02：合法release后撤回仍可创建

状态同上，release提交成功但尚未原生发送。用户revoke(gA)提交active=false及ACK，随后原已放行链继续POST；AS看到仍有效的P，检查通过，Insert C，删除P，返回。record以原origin登记并因当前inactive置QUARANTINED。

全部本地规则保持，C_local无新放行也保持；“AS插入时批准仍active”“ACK后绝不发送/创建”失败。需提交前强栅栏才可承诺后者；本轮未实现。

## 3. CE03：同父两次刷新产生两子代

一个gA预算至少2，P已登记。同一caller提交r1≠r2、source_rid均P，各经release成为i1/i2，原生轮换开启。

手工交错：h1和h2均在Go586读取P，均在599/610/667/696等检查通过；h1生成u、h2生成v，name各异；h1 Insert u，h2 Insert v；h1 Delete P成功；h2 Delete P返回affected=0,err=nil；两线程都只检查err并返回新束。

最终u/v均可存在，P已删。每attempt创建≤1正确，每父≤1错误。该反例依无额外AS父消费锁/事务的已读源码及标准并发DB语义，不声称已执行该原生时序。

## 4. CE04：父撤销不终止已检查的handler

gA已放行r。AS读P并通过有效性/用户/scope检查，暂停在生成/Insert前。用户本地撤回；原生revoke(P)将P.ExpiresIn设0；AT UserInfo拒绝、RT内省inactive均可已观察。旧handler使用已加载父对象继续生成/Insert C，之后按配置删P并返回/丢响应。

父材料的失效观察不能终结该在途创建槽。若错误地把全部甲责任仅投影为P失效，会错误CLOSED。现有协议把r保留DISPATCHED_UNKNOWN；待观察同源C并饱和容量、处置C后才可能关闭。该反例强化了保留latent pc/义务的必要性。

## 5. CE05：复制整个处理破坏单H容量

放宽A06，令一次已预记账的原生请求被中间层复制为两个handler，均读取尚有效P。按CE03执行得到u/v。H=1但C=2，排除无单dispatch前提的c_i=1。当前固定loopback无该中间层；反例只裁定去掉A06的合同。

provider.perform直接重放也可多次执行，但各次NativeHTTP会另预记账；其H可能变2，必须扩attempt/处理上界，不能再以单放行自带原生幂等为依据。

## 6. CE06：传递后代无统一有限界

固定正有效期，C的RT持有者在到期前调用下一次refresh，新生成的RT再次从当前时刻取得有效期。对任意d重复d次，每次用新的有效父且成功创建一代。无固定总调用/派生限制的域不存在统一有限传递容量。

受控有限grant/原生预算可使经登记入口的总调用有界；额外持有者/批准/绕行须纳入或排除。此例不否定有限I中每attempt的直接容量1。

## 7. CE07—CE10：语义、费用及映射

| 案例 | 输入/轨迹 | 失败推论与正确责任 |
|---|---|---|
| CE07 乙强化 | gA未知刷新、账户window active、gB active、B材料已知；乙申请refresh | admit/release被窗口拒绝；乙过去UserInfo成功不保证刷新/全业务持续 |
| CE08 宏低估 | 合同cleanup.requests=1；实际dispose三步均发出 | 真实3>抽象1；应按3计且另加query/B验证；不证明候选比强G更优 |
| CE09 纯probe映射 | refresh(P)被标为只读、无sessions/义务；源实际Insert C后响应丢失 | 模型后继遗漏C/潜在创建，可假成功；需完整副作用状态或退出当前A语法 |
| CE10 F为空 | I={i},c_i=1，两个不同U={u,v}，E只连i | F=空，不能用空集全称关闭；身份/容量/来源冲突待解 |

**CE11：单宏有限决策不界定全部等待/计算。** 对已启用hold_before_native_refresh的合法fixture配置，perform写屏障后循环等待.release文件；外部永不释放且没有额外终止规则时，provider线程可一直每10ms检查文件。调用者RPC超时仍不终止该线程。原生请求数可以保持0，本地循环工作和墙钟等待却无统一有限上界。它排除“h有界或RPC有timeout即单操作全成本有界”，不否定06的原生请求计数包络。

CE01—CE11均约束明确推论或表示；未证明所有抽象/所有算法不可能，也未给最强G相对候选的必要更高代价。

## 8. 最小验证计划：全部NOT_RUN

| 计划 | 已有证据/待检 | 批准与接口 | 故障/可见/真值 | 预期与费用/资格 |
|---|---|---|---|---|
| V1 release及reserve间隙 | M1/M2已有局部；确认CE01/02当前边界 | 先源/依赖审查；原生需新账户/预算授权 | release提交前后、reserve后open前；运行看权威/账本，评分看实际服务记录 | spent和责任保持；计拒绝/RPC/原生机会/清理；NOT_RUN |
| V2 两rid同父 | CE03源推导，无本轮原生 | 同批准预算≥2及父材料；原生并发另准入 | 两handler读父后屏障；运行仅获准响应，评分核两个不同创建 | 按每attempt入I；完整2调用/查询/处置/乙检查；NOT_RUN |
| V3 父撤销在途 | CE04及既有未知对账 | 撤回/处置/读范围全部明确 | AS已读父而未Insert；运行看P失效，评分看迟到C | 不提前关闭，所有后继责任计费；NOT_RUN |
| V4 传输/dispatch前提 | 历史stdlib片段和源码 | 优先只读绑定实际CPython/框架/部署配置 | 无需账户即可核版本、handler与middleware；若实验再单列 | 确定A05/A06边界；本轮未新运行验证工具/网络 |
| V5 响应和持久故障 | M2—M6有限证据 | 保持同profile/批准，故障与数据隔离 | Insert后错误、部分响应、inbox/record前后；真值封存不回流 | UNKNOWN/隔离/有条件饱和；计全部失败/读取/清理；NOT_RUN |
| V6 乙保留范围 | 当前合成窗口用例与M6 UserInfo | 乙UserInfo与refresh分别声明 | 最后处置后B操作及到期边界 | 历史成功/当前可用/持续完成分别评分；NOT_RUN |
| V7 L0及source接入 | 本轮纸面编码、当前schema/参考 | 先完成07桥接，后按工程/候选资格分列 | 同观察全部分支、空K/模型外/宏价目/部分setup | 检查原生映射和成本；求解器/测试重跑本轮均0 |

共同强基线为人工完整合同＋标准有限规划/模拟＋当前持久控制器＋标准流；双方共享源、观察、结构、缓存、批准及费用。分母分别统计可评价准入/关闭/责任/合法业务，以及UNKNOWN、拒绝、超限、中止、未触发和NOT_RUN。安全真值不足记INCONCLUSIVE。当前计划不提供实现、原生批次或外发授权。
