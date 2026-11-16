# R6-F1有限状态规格（待生成模型代码）

2026-11-10。数学/表格规格，执行状态UNRUN_PERMISSION。依据D1-PBFT-SEAL/1.1、R3证明及R5矩阵，保留普通重试/迟到行为和旧钥分层。未来F1显式状态BFS按本合同生成；本文件本身不属于已经执行的模型。

## 1. 参数与输入族

|输入族|配置/故障有限域|初态与覆盖|
|---|---|---|
|F1-SMOKE|O、C两Cfg，各4节点、f1/q3；每组坏身份∅或四选一，共25组合|旧O ACTIVE；新C WAIT；初态族empty或一条A已Release/UNKNOWN；单child仅作流程冒烟，INV2分支覆盖标NOT_EXERCISED|
|F1-BRANCH|O、候选C/D三Cfg，同父O、同epoch1、成员均无交集；各坏身份∅或四选一，共125组合|两份治理候选均允许提案；各自新状态独立。正常Seal选择其一；此族是INV1/2与双child变异的必检范围|
|F1-CHAIN|O(e0)→C(e1)→E(e2)，三组各4节点，共125组合|检查两次接续、退休、迟到结果及原来源/额度；成员完全无交集|
|F1-KEY|F1-BRANCH加旧O泄露集合∈{∅,{o0},{o0,o1,o2}}、observer anchor∈{O,C具体摘要,D具体摘要}|基础≤f集与旧quorum泄露扩展集分开；治理/目标激活证据的有无分别登记|

任务{A,B}、intent{iA,iB}、每intent两个attempt槽、generation∈{0,1}、两个执行者/两个Gate身份、boot∈{0,1}。每intent limit取固定夹具值1或2，reserved/charged∈0…2；同intent跨代次仍用原quota_id，批准不自行充值。opid与body各有两个固定业务值，异正文重用为冲突。

每Cfg应用提交位置seq∈0…12。每类用户命令/attempt用预登记有限槽，精确重复同body可折为无新业务事实的重放步；若该抽象不能保留真实seq/守卫顺序，列ABSTRACTION_GAP。任何需要第13位置、第三attempt、第三boot或未登记对象的后继，显式记录DOMAIN_OVERFLOW。出现该标记时不得把其后行为解释为安全；相关全域结果标INCONCLUSIVE_DOMAIN，已完成更小前缀可单独报告范围。禁止静默截断以获得PASS。

## 2. 完整状态元组

|变量|有限表示/用途|
|---|---|
|cfgState[c]|phase∈{ACTIVE,PREPARING,SEALED,WAIT_ACTIVATE,RECOVERING}；pending∈{none,r0,r1}；child∈{none,C,D,E}；seq与退休位|
|log[c]/genesis[c]|该Cfg内有序命令/结果、固定初态引用；每Cfg单独保存，避免全局单头结构排除分叉|
|StopFacts/ActivateFacts|认证body、签名身份集合、完整snapshot/parent/root引用；集合追加且保持历史；状态归属逐项区分real_commit和forged_auth|
|acceptedHeads[v]|observer∈{old_anchor,pin_C,pin_D}各自曾接纳的Cfg/genesis/祖先集合；current只作集合的显示投影|
|grant/owner|任务批准active/revoked、generation、用户授权body、owner、boot；Q业务命令取当前有序状态|
|attempts/quota/dedup|四个槽状态∈{empty,queued,released,unknown,recorded,closed}；origin/intent/body/generation；额度与跨Cfg去重|
|Obl|attempt×{OUTCOME,DERIVATION}的子集；关闭需匹配kind和证据，UNKNOWN本身不清空责任|
|Hist/CreatorCaps|两材料×两执行域披露bit；两执行域×{password,refresh,session}能力bit；未知外部创建保留unknownCreator|
|objects/snapshots|四引用对象的内容/取得位；snapshot绑定完整逻辑元组，root采用无碰撞规范元组身份，不含自身外部证书/自身摘要|
|readyState/readyUse|每新副本的完整对象证明集合；V/Gate准备证明含部署/Cfg/genesis、scope、boot、材料版本及预条件。准备度可失效，始终不是单独业务发放权|
|rights/messages|每attempt发送权∈{none,unconsumed,consumed,maybe_sent}，原持有Gate/boot；消息槽∈{none,release_reply,inflight,result}、来源/结果字段；新旧消息均保留|
|availability/recovery|每Cfg可达成员子集、崩溃成员子集；节点故障受身份预算约束，网络分区另计；durable应用版本/Seal/head及oracle稳定约束引用|
|ghostIssued/ghostOrigin|Release时独立追加的事件与原origin；移交F不写这两者|
|ghostClose/ghostSpent|合法Close证据事件、同quota累计消费；从原始事件核对，禁止由迁移后RHO反推|
|audit flags|首个违反性质、域溢出、被拒命令、所见边界事件、已执行mutant标签；不得参与业务放行守卫|

相同snapshot/root表示相同全部逻辑内容；不同物理签名、密钥值和PBFT局部投票日志不放共同root。oracle承诺同Cfg内有序服务、已执行状态和稳定恢复，跨Cfg唯一性、child选择、F字段保持及observer验链均由下面关系检查。

## 3. 初态

O为已认可genesis、ACTIVE；新Cfg仅有模板/成员和WAIT_ACTIVATE，尚无认证Activate。所有正确节点持久状态与O一致。empty族两任务初始未批准/空槽；unknown族A已合法批准、Release一次且结果UNKNOWN，charged1、两类责任开放、原来源/去重/发送权均存在，ghost账独立初始化为同一事实。B保留自己的intent/quota。

初始治理批准、schema/code、材料引用及scope均在具体夹具中固定。原生效果真值不假设已经完整枚举；F1不以unknownCreator=false推断全部外部路径关闭。

## 4. 转换关系

|事件|守卫/后态；拒绝与重放|
|---|---|
|Approve/Admit|合法当前治理/用户批准；ACTIVE及原业务规则；登记代次/来源、去重与reserve。精确重试返回历史，异body冲突；同quota余额不因owner/epoch变化而重置|
|Release|oracle在该Cfg当前有序状态执行：ACTIVE、grant/gen/owner/body/profile/预算匹配；同提交建立attempt/Obl/right与charged。ghostIssued/Origin/Spent独立记该线性化事件|
|Revoke|有序置该grant撤回，取消未放行队列，保留已放行责任；PREPARING允许，SEALED旧方仅返回MOVED，未取得当前提交不能称LOCAL_ACK|
|Propose/Prepare/Abort|有权提案、正确父模板/代码/配置；冻结新放行。Seal前可Abort并保留责任；已Abort opid仅返回历史。候选C/D都必须在某合法前缀可被选择|
|Seal|PREPARING且提案匹配、尚无成功Seal；提交SEALED、固定child、完整snapshot；Stop签名收据引用该已执行持久内容。SEALED后普通业务写及改child拒绝|
|Transfer/ReadyState|逐对象取得/验规范root及确定性F；缺对象/责任/引用/代码拒签。只有实际完整的新副本可签；q个同body证明就绪|
|Activate|目标Cfg匹配Stop/治理/父祖先及ReadyState；从唯一指定F(snapshot)初始化该Cfg，首条有序Activate到RECOVERING。不能把“全局只有一child”直接放进Activate守卫替代旧Seal证明|
|ReadyUse/Takeover|V/Gate条件准备证明与目标boot/scope/材料匹配；当前新Q处理Revoke/Record可先进行，业务开放还需Takeover及当前Release。复制状态不把秘密明文交Q|
|Retire/next reconfig|退休只减少旧服务资源，Seal仍吸收；下一次重配由已激活当前Cfg提案。分支/顺序两族分别验|
|Gate consume/send/deliver|只用可追溯的原Release和该attempt唯一right；重复/跨body/跨boot不得变成新权利。消费、HTTP开始、Provider到达/结果分步；Seal/Revoke前已放行的同一attempt可以迟到，继续记UNKNOWN/费用|
|Record/Close|当前Cfg按原origin/attempt/body登记迟到结果；撤回则隔离。Close须匹配证据kind/scope，不从timeout或迁移补出成功|
|Partition/crash/recover|可达/崩溃位变化；无quorum不新提交。正常恢复核durable log/Seal/head，不能重开旧ACTIVE；Gate可能已消费的权利保持UNKNOWN，新boot重验身份。PBFT view-change只通过oracle进展/稳定状态接口体现|
|Replay/cert acceptance|验成员去重/域/body/祖先/摘要pin；历史Stop可验历史事实，旧QC不自动产生新Release。K1中泄露钥可签的body与真实oracle提交事实分别记录|

这些关系未增加Provider原子撤销或效果fence。网络超时只改观察/未知状态，不删除真实inflight；允许无限stutter/分区时仅检查安全，不报告最终或有界响应。

## 5. 八个不变量与独立监视器

|性质|从事件/状态计算的断言|
|---|---|
|INV1 UniqueHistory|对同可信引导及正常故障前提下的acceptedHeads，任意两有效业务历史在共同祖先之后可比较为前缀；同Cfg同提交位置内容相同。检测冲突head集合，不能只查单一current字段|
|INV2 UniqueChild|对每个父Cfg，由认证StopFacts导出的有效child集合基数≤1；同父已激活child也≤1。历史记录不因后写覆盖而消失|
|INV3 SealSafety|成功Seal之后，旧Cfg的新Release/新发送权事件集合为空；旧ACTIVE备份不能新增这些事件。已有attempt的迟到IO保持合法范围和一次权利|
|INV4 RHOConservation|每个ghostIssued创建、尚无匹配ghostClose的义务，在当前接收责任状态或未接续冻结源中有同来源/类型条目；移交F不消除它，存在完整责任承载者|
|INV5 BudgetConservation|各quota reserved+charged≤limit；charged与ghostSpent/已取消reserve按固定规则匹配；更换owner/Cfg/gen不抹去已耗费槽或生成第二机会|
|INV6 OriginPreservation|Record/材料/关闭证据的origin等于ghostOrigin[a]；改owner/当前批准不改原g/task/i/generation/body；撤回后的结果隔离|
|INV7 ReadySeparation|新Q ReadyState需完整对象；业务Release须该scope已Takeover、有效ReadyUse及当前授权；仅ReadyState或仅ReadyUse均不能单独产生业务right|
|INV8 CurrentAuthority|每个新Release在其线性化点匹配当前Cfg/批准/代次/owner/请求；历史重放最多返回原事实，不建立新attempt/right。它属于C_local，不量化已经发放权利的所有未来IO为“当前新授权”|

辅助检查：recovered application与独立durable/oracle已承诺状态一致，Hist单调，全局dedup单值，发送权消费至多一次。monitor与业务关系模块分离，mutant只改指定关系，不同步修改断言或ghost来源。

## 6. 必须覆盖的见证与变异

|ID|最小域/轨迹预期（纸面）|应如何解释|
|---|---|---|
|N-DISJOINT|O4/C4；Seal→Transfer→ReadyState→Activate→ReadyUse/Takeover|正常可达流程；不可因无交集直接拒绝；当前未运行|
|N-U2|Release→Revoke/Seal→原right消费/IO/结果，或先consume再延迟IO|验证旧attempt仍在RHO，INV3/8不能错误禁止全部迟到IO。实际V若追加使用时重验，另列更强profile，不冒称1.1已实现|
|M-CHILD|O/C/D；形成第一Stop后允许同父第二Seal，两个目标分别Activate|INV2应在双认证child时首先命中，INV1在双激活时可命中；删除守卫不能同时覆盖旧Stop记录|
|M-ROLLBACK|O已经Seal，恢复旧ACTIVE并再Release|辅助恢复一致性或INV3/8；正常恢复应拒绝|
|M-RHO|初态有A UNKNOWN；Transfer/F删Obl/Hist/来源之一|INV4/6或辅助Hist；ghost账不跟随删除|
|M-BUDGET|A已有charged=limit；接续时把额度重置，再放行一次|INV5；必须存在第二机会槽以让错误行为可表达|
|M-READY|只取得状态、V未ReadyUse，仍发新业务right|INV7；正模型应保留RECOVERING而拒业务|
|M-STALE|撤回/Seal后，用旧缓存/QC为另一attempt或boot新发权|INV3/8；与原right的U2分开|
|M-ORIGIN|迟到A结果写成当前B/新generation|INV6；原来源为独立常量|
|K1a/b/c|旧O泄露3钥→假Stop；分别缺/有治理与新Cfg Activate；observer仅O锚/具体D摘要|正常≤f与扩展泄露集分开。旧Stop可伪造性、完整激活和pin接纳分别出轨迹，不预填机器结论|

## 7. 覆盖与停止

每个job记初态/转换可达性、各守卫成功/拒绝、两个候选各自被Seal/Activate的覆盖、8个monitor调用数、mutant首条最短BFS轨迹及独立重放结果。某转换/错误域不可达，相关性质标NOT_EXERCISED，不以零命中充任mutation通过。基础、branch、chain和key族共享单批资源；域溢出和访问限额保持显式结果。

当前所有访问状态/轨迹长度/峰值/耗时执行统计为null；本文件的事件串为待查最小结构，未承诺机器最短长度。LEVEL-3检查与LEVEL-4证明均尚待取得。
