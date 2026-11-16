# R6纸面协议—有限模型—性质—证据映射

2026-11-10。执行证据列目前统一UNRUN_PERMISSION。以下为非可执行的数学关系/数据合同，模型源码创建0。

|纸面来源|F1/F4对象及转换|待查性质|未来证据|
|---|---|---|---|
|D1 T01/T02/T03|Approve、Admit、Release；grant/gen、global_dedup、quota、attempt、独立ghost发放账|INV4/5/8|每次Release前后态、守卫、来源/额度和trace摘要|
|D1 T04–T07|Gate消费权、旧IO延迟/响应、Record、Revoke；权限线性化点与真实发送分开|INV3/6/7/8|U2正见证与旧QC重新发放变异；不可把全部迟到IO视作错误|
|R3八步1–3|Propose、Prepare、Abort、Seal；各Cfg独立phase/log、不可覆盖的Stop集合|INV1/2/3|分支Cfg C/D均可达性与双child变异|
|R3八步4–5、R4 1.1|Transfer对象、ReadyState、固定F/genesis、Activate；独立接受链集合|INV1/2/4/7|缺对象/root、错父/祖先、漏字段及两候选激活轨迹|
|R3八步6–8|ReadyUse、Takeover、Reconcile、Retire|INV4/6/7/8|按原attempt对账、缺V就绪拒业务、退休不能重开|
|R3 A1/A2/L1|每Cfg内唯一有序oracle、固定成员签名身份/故障界|oracle前提，不计为F1独立证明|模型假设清单；静态PBFT实现ABSTRACTION_GAP|
|R5 K1|旧钥集合、签名可生成性、治理、目标Cfg Ready/Activate及pin验证|INV1/2的正常/扩展条件分案|旧Stop、完整child、新pin三层分别记录|
|R3组合/R4费用进展|native消息/已放行责任，独立累计尝试；无限等待/分区|F1局部责任/费用保持；真实P5待证|内部stutter不隐藏新尝试；无活性/墙钟外推|
|D2 R3 §§3–5|完整x、同历史z、合法Obs、非空Post、共同动作与W递推|F4-P1–5|每夹具的阈值/最坏费用/策略与独立参考表|
|D2 R3 §6|按完整未来等价键取max z；可见费用进入Obs|F4-P6|压缩开/关与参考一致、CE5/费用可见/配额变异|

## 1. 防止假阳性的模型要求

1. **跨配置多头可表达**：分别保存每个候选Cfg的日志、genesis、已激活状态和每个验证者接受过的head集合。单一全局current变量只能容一个头时，UniqueHistory/UniqueChild可能由数据结构强制成立；它可作显示投影，不充任被检事实全集。
2. **守卫与断言分开**：唯一child由Seal守卫/持久状态得到，INV2从已认证Stop/Activate集合独立计算。正模型禁止的双签/丢RHO由mutant注入；性质函数不与mutant共用被删守卫。
3. **独立责任来源**：ghost ledger在原Release线性化时保存origin、预算事件与义务创建；迁移F不修改该ghost。若RHO和checker都从同一遗漏字段的投影重算，漏义务变异可能错误通过。
4. **旧权利与新发放分开**：INV3/8量化Seal/Revoke之后的新Release或新发送权；已经登记的同一次attempt可迟到，始终保留来源/费用/UNKNOWN。把“所有旧IO必须在Seal前完成”加进正模型会排除真实U2。
5. **Ready角色正确**：ReadyState是新Q副本的完整数据证明，E/Gate实际使用还需ReadyUse与相应Release。任务列表中“Gate ReadyState”按这个角色映射；不把Q取得秘密明文当作准备条件。
6. **后继与前缀完整**：空Post、动作在某可能状态失效、段中坏前缀、超时/未知和越界单列。F4只遍历真正可能的观察，无需为不可能观察制造虚假后继。
7. **关闭与成本独立**：终态检查完整Goal/Obl/Inv；实际路径成本另由原始微步累加。错误费用标签只修改被检实现，参考保留冻结输入。
8. **有界与超限区分**：预先声明的有限参数界与运行资源界分列。未保留某个现实步骤标ABSTRACTION_GAP；达到批次资源界标INCONCLUSIVE_LIMIT；两者均不缩成“未见反例所以通过”。

## 2. 当前明确的ABSTRACTION_GAP

PBFT view-change/磁盘日志实现、密码学签名/哈希碰撞与密钥保护、V/Gate明文/调试出口、Casdoor全handler/事务/审计/接受端、未来C_effect载体、真实网络/时钟/故障域及S2资源保证，均不由F1/F4的抽象检查自动消除。每项在后续F2/F3/原生/部署验收继续登记。

## 3. 有界输入族变化

R5给的是域上界建议，尚无执行。R6把单child冒烟、双候选、连续epoch及K1分成独立输入族，避免单候选模型使INV2缺少可挑战分支。F4增加完整前缀和输入完整性校准；这些变化只增强验证对象定义，未产生机器结论或新机制原创性。
