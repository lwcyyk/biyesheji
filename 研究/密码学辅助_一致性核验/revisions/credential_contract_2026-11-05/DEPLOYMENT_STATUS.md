# 凭据交付、中介闭包与密码学需求裁决

2026-11-05，Asia/Shanghai。主系统选择auth-lifecycle与ci01所用的本机Casdoor 4.25.0。当前端到端结论为PROTOTYPE。本文区分已运行组件、源码能力、研究者确认、拟议合同和未知事项。

## 1. 部署状态

| 对象 | 状态 | 已有代码、配置及轨迹 | 边界 |
|---|---|---|---|
| 本机Casdoor AS及其UserInfo端点 | DEPLOYED，限定实验环境 | 2026-11-05 01:28:32本地只读进程/端口核对，PID18456监听127.0.0.1:18081，二进制摘要与采样锁相同 | 本轮没有重查数据库应用配置，也没有据此声称生产部署 |
| auth-lifecycle原生适配器与有限规划器 | PROTOTYPE | providers、planning、Gate、Resource、BoundedController及L1脚本实际存在 | 有限模型、固定原生绑定、实验批准预算与评分流程 |
| ci01材料交付与对照流程 | PROTOTYPE | N01/W01/C01/C02，三批511事件、44接受观察、199次HTTP | A/B为逻辑角色，同一取证进程中分配变量与可见投影 |
| 生产R、独立代理进程及凭据交付服务 | UNKNOWN | 尚无证明全部原生材料仅在R边界内流动的实现/配置 | 真实部署边界此前由研究者确认为未确定 |
| 仅交付任务绑定本地句柄的全托管合同P-MED | PROPOSED | 本轮拟议主profile，待研究者选择确认 | 合同文本及充分性论证，候选机制实现为0 |
| 代理持有Bearer AT/RT的P-EXPORT | PROPOSED反方合同，原生能力已有实例证据 | C01证明具备相应RT/client_id时可无secret刷新，UserInfo接受有效Bearer | 证明的是所测能力，独立代理的实际交付仍未知 |
| 生产批准UI、持久接纳事务、恢复防回滚实现 | UNKNOWN | 实验g0/g1及内存状态存在，真实批准服务和崩溃恢复尚未验收 | 日志标识及哈希不构成可信最新状态 |
| PSCD | PROTOTYPE，开发档案 | 既有三档MPC与受限模型证书，当前无主线共享MV消费接口 | 候选A已淘汰，候选B本轮停止作为当前主线候选 |

DEPLOYED仅用于已经运行的本机组件。PROTOTYPE表示存在可执行代码和受限轨迹。PROPOSED表示本轮合同或未实现设计。UNKNOWN表示当前证据无法确定。

## 2. 冻结证据与当前工作树

三批source_hashes.json共25项快照全部与记录摘要相符。对应当前取证程序和providers/witness/journal代码相符，三个MODEL_AND_CONTRACT.md冻结副本与当前文档不同，当前版本追加了能力说明。历史轨迹继续按自己的冻结副本解释。

auth-lifecycle目录没有可用Git仓库元数据，HEAD与status返回not a git repository。因此本轮以87项输入文件的SHA-256登记当前状态，不编造代码提交号。Casdoor上游仓库HEAD为528a0213f01caf70b9f41009cbf7b2f67bdd67ec，工作树检查为空。源码到二进制的可复现构建仍未证明。

本机可执行文件SHA-256为ddbab07cbe0a913e3bf3b3fbb09b0a1fa3b4abc5127c6b3156930aa77a37ad5c。实时进程指纹与历史环境锁一致。应用配置的依据仍是各次采样锁及采样后读回一致，保持时间作用域。

收尾发现ci01的DECISION.json和SOURCE_RECONCILIATION.json在本轮期间更新，已重新读取并在evidence/INPUT_UPDATES.json固定前后摘要和当前副本。新增汇总记录包括3批4条件、26次只读数据库查询和25项源码核验；原始轨迹继续绑定各自冻结代码。

相关工件为evidence/INPUT_MANIFEST.json、SOURCE_BINDING_AUDIT.json、RAW_RECHECK.json和CURRENT_RUNTIME.json。哈希链及日志对应检查证明工件自洽，来源真实性仍依赖声明的可信实验环境。

## 3. 固定原生配置

实验组织l1-study、应用app-l1-0、client_id为l1-client-0。采样锁中grantTypes包含password、refresh_token、authorization_code，tokenFormat为JWT，disableRefreshRotation=false，AT与RT配置有效期均为1小时。实际资源范围为无Cookie的GET /api/userinfo，以及对应refresh接口。127.0.0.1监听只提供同机实验可达性证据，远程代理的网络路由和访问控制仍未知。

所测请求采用可信loopback上的HTTP。生产TLS、Cookie/浏览器SSO、其他RP、ID token跨RP使用和外部业务效果不在这批接受证据范围。RFC9700 §2.4要求停用password grant，该实验配置保留为版本化研究对象，生产登录方式需要另行冻结。[RFC9700](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.4)

## 4. 已确认事实与设计状态

| 类别 | 内容 |
|---|---|
| USER_CONFIRMED | R可信，掌握其已收到的令牌、来源记录和当前批准 |
| USER_CONFIRMED_UNKNOWN | 生产旧代理是否能够绕过R尚未确定 |
| OBSERVED | C01省略client_secret的两次刷新成功；C02应用Basic凭据取得两项记录及原生AT/RT；已知子代逐项撤销有有限实例正例 |
| SOURCE_DERIVED | 请求材料的别名/摘要对应；raw字符串在适配器和取证字典内存在；分页、DPoP、会话分支的代码行为 |
| PROPOSED_PENDING_RESEARCHER | P-MED把全部相关原生材料保留在R可信边界，仅向代理提供经过当前批准校验的任务绑定句柄 |
| UNKNOWN | 独立代理实际收到哪些原文、生产密钥/会话权限、完整导出路径、恢复后当前状态、跨信任域私密输入职责 |

本轮已向研究者提出一个架构选择问题。收到明确选择前，P-MED只是本轮用于分析的拟议主合同。P-EXPORT为唯一必要反方profile。三种合同分支是对这两个profile及未知跨信任需求的判断，不扩展平台实现。

## 5. 源码证据索引

| 编号 | 入口及用途 |
|---|---|
| S1 | auth-lifecycle/src/auth_lifecycle/experiment/providers.py，HTTP、Casdoor.issue/refresh/introspect/revoke及应用凭据内存状态 |
| S2 | auth-lifecycle/scripts/l1_pilot.py，issued保存完整响应，Resource.bind传入原生AT，方法与评分阶段分离 |
| S3 | auth-lifecycle/src/auth_lifecycle/experiment/resource.py，use/remote路径、AT匹配与本地closed集合 |
| S4 | auth-lifecycle/src/auth_lifecycle/experiment/journal.py，Gate.call的许可/预算锁及锁外dispatch，private_effects评分者视图 |
| S5 | auth-lifecycle/src/auth_lifecycle/controller.py及adapters.py，L0有限表适配与内存pending，非生产凭据托管服务 |
| S6 | ci01/raw各批source_snapshot，collect_evidence/secretless/listing及冻结依赖 |
| S7 | Casdoor object/token_oauth_util.go、token.go，发行/刷新/撤销与记录字段 |
| S8 | Casdoor controllers/token.go与object/ormer_session.go，get-tokens分页、过滤和排序 |
| S9 | Casdoor routers/auto_signin_filter.go、controllers/account.go，原生UserInfo最后接受路径 |
| S10 | Casdoor object/token_dpop.go，DPoP验证和刷新绑定；本批未启用的源码能力 |
| S11 | Casdoor routers/session_provider.go及ci01/POST_CLEANUP_DB.json，会话持久性范围和清理后保留记录 |
| S12 | ci01 sources/authz__authz.go与routers/authz_filter.go，应用凭据组织级权限与对象作用域 |

完整绝对路径、定位和摘要由evidence/SOURCE_LOCATORS.json固定。
