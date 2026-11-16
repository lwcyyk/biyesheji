# CASDOOR_NATIVE_ISOLATED_V1

2026-11-06。ONLINE_TRUSTED_STATE_V1 的单机、单活、可信在线权威、专用组织部署。密码学辅助线 FROZEN。使用成熟事务、OS 受限主令牌、DACL、TLS、RSA-OAEP 与 AES-GCM；新增候选机制为 0。

## 固定配置与接受合同

Casdoor 4.25.0，http://127.0.0.1:18081。启动前核对运行映像与既有发行 ZIP SHA-256；源码参照 528a0213f01caf70b9f41009cbf7b2f67bdd67ec，可复现源到二进制构建保持 UNPROVED。既有 l1-study/app-l1-0 仅读取参照。新建一个组织、一个应用、两个账户，复用已有签名证书。JWT、RS256、password/refresh_token、AT/RT 一小时、刷新轮换开启、isShared=false。密码流程作为版本化实验对象，生产授权流程另行验收。

每个账户一条轨迹，A.g0/B.g1 独立批准与初始发行。代理持自己的 Bearer 服务能力和任务句柄；R 持新应用能力与该账户登录材料。服务接纳绑定 caller、task、account、audience、generation、rid、正文摘要及预算。单活恢复须先确认旧 R 退出，权威、密钥和数据在 cache 回滚范围之外。

本地 ACK 为 LOCAL_REVOKE_COMMITTED，承诺旧批准的新放行停止。原生接受是 fresh、cookie-free UserInfo，HTTP 200 且 sub 正确；AT/RT 内省分别保存。已知材料处置、未知创建关闭和任意 RP/外部业务效果分别判断。

## 同批权限布局

A/B 为独立限制 SID、Low IL 主令牌。R、权威和原生适配器共享该轨迹的 R 限制 SID、Medium IL。支持限制 SID 继承 M5：BUILTIN Users、Everyone、Restricted Code。每条轨迹的实际 SID、PID、TokenUser、默认 DACL、进程对象 DACL、文件 DACL 与重启记录保存在各 ENVIRONMENT_LOCK、SETUP_CONTROLS 和 trusted/control 下。

既有 .runtime/l1 管理凭据和 AS 数据库曾继承 Users 读取。研究者明确追加授权后，备份目录与所有子对象 ACL，再用 SetNamedSecurityInfo 收紧根 DACL 并传播继承权限：可信当前用户与 SYSTEM 完整控制，OWNER RIGHTS 为 RC。相关原文件内容未由 ACL 脚本修改。后续原生操作产生的数据库变化按本批请求计费。该 ACL 前提属于当前联合 profile；M5 的旧适用域保留。

R 只读传输根与审计公钥，可写 http_budget 和密文输出子目录。评分 RSA 私钥、私有响应和环境管理凭据在独立 DACL 域。受限进程对原始及复制的管理凭据、原生数据库、评分私钥执行实际访问检查。所有服务 bInheritHandles=False；顶层与辅助程序使用显式环境白名单。新 SAM 用户为 0。

## 两条一次性轨迹

- M6-01：完整 operational inbox=true、identifier_journal=true；代理真实发行、A 刷新、B UserInfo；对象存在后做文件/进程/管理入口/B 句柄攻击；撤回 A、处置已知 A0/A1、B 继续。
- M6-02：上述两种收件渠道均关闭；after_effect、权威登记前终止 R；A 进程存活，恢复旧缓存并短暂中断权威；恢复后旧 A 拒绝，B 既有材料可用，新创建在窗口内暂停；获准范围枚举后关闭或继续 UNKNOWN。

评分通道对 HTTP 响应单向封存；R 不加载私钥。M6-02 查询前保存原 pending 与允许输入投影，独立评分比对 A1 AT/RT/jti/原生 ID 的缺失。独立真值和清理知识均不回流运行决定。

## four-grants-single-Find-single-effect

全批四项批准，各预算 10，原生记录生命周期上界 40。页容量 100、p=1、owner=admin、organization 等值、空 field/value、name 升序。来源和效果论证复用 M4：一个账户恰两批准、已知来源完整、唯一未知 A 刷新、一个发送槽、单请求至多一个新单位，窗口暂停新创建，其他写入者排除。完整性只属于单个 Find 读快照，count 分开取样。

整个新组织的令牌读取授权给可信 R。客户端在范围内按账户与应用等值选择。首次发行前另查整个范围为空；已完成上一条轨迹的进程退出，其他原生写入由受控夹具排除。未知尝试发现唯一可归属单位后，结合单效果上界使剩余创建能力为 0。处置及 B 保留成立后才能提交条件性 CLOSED。空观察、来源歧义、额外发送或来源不完整继续 UNKNOWN。

原共享组织账户级子串过滤问题保持原判断。源模型、外部写入者排除、AS 执行符合性均属于明确前提；当前材料不证明任意 provider、跨机器/多活、恶意 R、无限资源耗尽或任意 RP 的关闭。

## 预算与停止

授权 M6-NATIVE-ISOLATION-20261106-01：环境/建户50、方法60、独立测量50、清理60，总220。每次失败、查询、重试在发送前记账；非清理分项之和160，独立预留清理60。采样与测量上限45分钟。两条各一次，不自动重采。越权、泄露、错误放行/关闭、配置或对象范围冲突时停止后续采样并清理。

源码、配置、评分规则和额外只读存储检查在原生运行前冻结。原始证据、事务版本、PID 退出/启动和单向封存分别支持其实际作用域。B 保留在账户级清理前评分。清理逐项回读账户、应用和组织；应用删除包含正确 organization。
