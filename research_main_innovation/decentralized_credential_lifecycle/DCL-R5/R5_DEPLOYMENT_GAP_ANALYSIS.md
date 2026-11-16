# R5部署缺口闭合表

2026-11-10。复用[R4 A/B/C部署映射](../DCL-R4/R4_DEPLOYMENT_REFINEMENT.md)，本轮只登记变化和未决验收。实际仍单机单活权威；跨管理域Q_B/PBFT部署0。

|边/编号|新证据或当前可核内容|缺口与最小补证|状态|
|---|---|---|---|
|D01 Commit→官方包→本地exe|官方ZIP/checksum摘要与本地一致，R4 ZIP内部exe哈希保留|官方签名/发行供应链认证另列；当前摘要环已闭合|PASS于发布工件字节对应|
|D02 dirty编译输入|固定配方版本hook写tracked变量，有明确候选diff|取得真实构建前后diff和完整日志；go mod tidy/生成物单列|PARTIAL|
|D03 源→实际handler|已核依赖/flags、固定源码正常并发交错|其他dirty文件及实效代理/锁/入口；未来隔离调度|BUILD_CORRESPONDENCE_CONDITIONAL|
|D04 DB/连接|配置sqlite/cache=shared；主文件格式/旁文件静态视图|同driver/实际业务连接的版本/PRAGMA/Stats、事务及锁|DEPLOYMENT_BEHAVIOR_UNVERIFIED|
|D05 Q授权复制|纸面唯一Seal、固定F/genesis、完整RHO|选定PBFT实现、共识状态/投票稳定存储和真实故障控制面|PROOF_GAP|
|D06 旧证书/恢复锚|Stop没有自动到期，K1区分伪Stop/激活/摘要pin|证书有效生命周期策略、近期摘要可信取得与抗回滚；旧钥处理|CONDITIONAL|
|D07 Q/V秘密边界|1.1角色分离已定义；实际AuthorityStore仍保存整包秘密，Controller持钥|逐字段序列化/日志/调试流检查，Q只获密文引用；V/Gate限制及恢复|PROOF_GAP|
|D08 V当前使用|ReadyUse与Release各自绑定scope/版本/boot等|具体V验收实现、代次变更/延迟/崩溃相位；区分已放行在途与新授权|CONDITIONAL|
|D09 全部原生创建/效果|登记责任和历史能力建模；NC1/2、GetAccount等入口|完整强制中介或权威原生全集、在途余量和异步效果载体合同|CONDITIONAL / UNKNOWN|
|D10 B持续路径|有限正例有依赖图和费用；冷备用资格条件见本轮S2审查|实际管理员/OS/KMS/V/P/网络/DB/恢复服务控制矩阵和服务界|CONDITIONAL；实际实例0|
|D11 观察/费用/进展|1.1逐尝试计费、EnvClosure、有限段义务|真实方法/scorer隔离、所有尝试与隐含I/O、超时/资源边界映射|CONDITIONAL|

验收区分：状态恢复证明覆盖逻辑对象/责任/根；秘密使用证明覆盖V的实际能力/输出/当前批准；原生停止再检查接受端和未来载体。任意一项缺失，其他层的PASS仍保留原作用域。

D01已由静态公开证据解决。D02从泛称dirty推进到可定位stamp写入，但实际修改全集持续未还原。D04补齐了配置/旁文件快照，尚无运行连接事实。D05–D11以具体接口、相位和证据对象登记，避免用“部署已分散”替代验收。

R5-B采用PARTIAL：完整未决清单已形成，静态证据有增量；真实跨域与原生行为继续待证。
