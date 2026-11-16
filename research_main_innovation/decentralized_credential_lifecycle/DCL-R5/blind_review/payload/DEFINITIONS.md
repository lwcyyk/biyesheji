# 阶段一模型定义

## 1. 角色与共识

U签发用户/治理批准；Q_e为epoch e的固定成员委员会，n=3f+1，q=2f+1，使用签名版PBFT的完整normal/view-change/checkpoint确定性服务。假定每epoch正确成员从同一genesis执行唯一有序日志；崩溃恢复保存view/seq/签名约束。E为协调执行域；V/Gate为明确声明的受信秘密使用/发送边界；P为原生Provider。失陷E可保留所有曾见材料并走模型允许的原生路径。

Cfg包含部署、epoch、父配置身份、成员/公钥/FD、schema/code摘要和治理策略。公钥规范去重；签名域分隔。基本故障条件为证书被接纳的生命周期内每Cfg累计失陷≤f，网络安全允许延迟/乱序/重放/分区；进展需另给最终同步/公平/可达。扩展实例可放宽该故障条件，审查时请分开陈述结果。

## 2. 应用与业务转换

逻辑状态包含grants/代次、全局业务opid→正文映射、origin intent/operation、quota(limit,reserved,charged)、attempt、send_right、义务Obl、结果/材料来源、Hist/MaySeen、CreatorCaps、原生观察/证据、已有关闭声明及其保持条件。Hist单调；恢复/重新分片本身不删除披露历史。

|动作|守卫与后态定义|
|---|---|
|Approve/Admit|当前合法批准；同业务opid同正文返回历史槽，冲突拒绝；预算内reserve|
|Release|当前grant/代次/owner/配置/策略/原生前提合格；同一Q提交建立attempt、义务、发送权并reserved→charged|
|Send|可信Gate验对应Release、参数、调用者/boot及未消费权；消费持久化后启动HTTP；可能已发在崩溃后保留不确定|
|Result/Record|P可接受、拒绝、延迟、派生、丢响应；Record绑定原origin/attempt/body，当前批准无效时隔离|
|Revoke|有权用户有序提交撤回；禁止后续新Release；已有责任保留；本地ACK表示该提交事实|
|Successor|创建请求不确定时仅在原生精确重放或原终态无效果合同允许时单继任；读重试可另给无副作用合同；预算/来源保持|
|Close|按义务kind及匹配的来源/范围/因果/完整性证据关闭；不足保留UNKNOWN/DEFERRED|

## 3. 成员接续

phase为ACTIVE、PREPARING、SEALED；新方为WAIT_ACTIVATE、RECOVERING。Prepare冻结新Approve/Admit/Release等；允许Revoke、Record及本提案Abort。成功Seal固定唯一child且SEALED吸收；Seal之后不可Abort或从旧方另选child。旧节点之后只提供冻结证明/重定向。原生世界独立继续推进。

Stop=(旧Cfg、seq、Seal命令摘要、完整state_root/rho_root、new_cfg摘要、q旧签名)。正确旧节点仅在提交/执行/持久化后签同body。Stop结构未定义not-after字段。新Cfg模板先有父Cfg身份，实际父Stop另存于genesis，避免自指摘要。

Transfer交完整逻辑状态/密文引用/manifest；正确新节点取得全对象、验根、schema/code及确定性F后签ReadyState；q新签名形成证书。F保持所有原责任/历史/去重，只改变epoch/接续phase等元数据。新委员会从同一F(payload)的固定genesis提交首条Activate到RECOVERING。Takeover检查当前批准、owner、配置证书和V/Gate权限，再开放相应业务。Reconcile按原来源登记证据；Retire只处理旧资源生命周期。

ReadyUse由V/Gate签署profile、父Stop/genesis、迁移/目标boot、Gate代码、秘密namespace版本、scope、预条件、nonce及有效性；它描述受限使用准备条件。实际业务还需当前Q批准、预算、owner及发送权。Q只取得密文/引用；若现实给Q解密钥/明文，接收者能力须据实列入模型。

客户端从可信anchor引导并保存认可的head。审核具体pin校验应当包含哪些身份/摘要/祖先规则。新旧成员可无交集，治理批准的最终选择经过当前有序状态。Seal后指定child不可达时，旧侧没有紧急换child分支。

## 4. 原生与停止层次

所检原生profile：refresh读父行并缓存，检查有效/应用/秘密/用户/签名，生成子材料，独立Insert子行，rotation开启则Delete父行，返回子材料；父Delete的零影响行数本身未作为冲突错误。Revoke查Token/RT哈希cohort并期限化，返回ACK。普通审计在handler后异步写。fresh UserInfo查询实际行/有效性。接口没有假定跨Provider事务或统一未来效果fence。

C_local量化Q撤回后的新放行；C_native量化声明scope的原生创建/接受截止；C_effect量化已接受载体未来坏效果。责任完整性区分登记请求与全部外部事实。S/U/L分别为受控发送上界、每attempt最大创建数、可靠完整识别下界。秘密/RT/密码旁路、缓存handler、历史派生和异步载体按实际能力入图。

## 5. 知识、费用与支持

固定有限物理状态x含全部影响后续动力学/权限/费用/观察的变量；真实历史累计费用z非负。B为非空(x,z)集合，Obs只给合法观察；一次动作segment可含多个微步骤，记录所有中间前缀、末态、观察及同路径费用。Post按观察并入全部合法相容segment的末态和累计费用。Goal_full含指定停止、B完成、严格义务空及清理；Inv还约束声明后续保持。h指决策段数。

共同策略只依观察历史。阈值胜集W0要求B所有元素均满足完整目标、Inv和费用≤m；W(j+1)含Wj及存在同一合法动作、所有segment前缀安全/不过费、所有可能观察的非空Post均在Wj的B。模型外结果保持UNKNOWN。

Support(B,x)=存在一条合法路径，其材料/批准、当前Q/Gate、原生接受、网络/服务及预算等AND条件全部成立。路径之间OR。S1允许迁移暂停并保持状态/条件恢复；S2(T)要求规定故障/环境集合下每个真实受保护前缀均有Support，δ响应需单独的服务界。配置先选，运行策略基于共同观察，所有故障/环境轨迹普遍量化。成本包括业务/失败/重试/证据/处置/验证/清理及额外配置资源，预算预留和实际HTTP分列。
