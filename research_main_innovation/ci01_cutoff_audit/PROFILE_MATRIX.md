# 截止合同与原生 profile 矩阵

## Material Passport

2026-11-05；研究阶段为原生能力核验与纸面组合审计。实际新增采样88 HTTP、3名新用户、3个独立新应用。结果入口为 [DECISION.json](DECISION.json)，证据核对为 [EVIDENCE_AUDIT.json](EVIDENCE_AUDIT.json)。当前结果支持限定profile的已有组合、经典边界实例和明确的能力未决项；严格分离候选数为0。

## 研究对象与冻结内容

Casdoor 4.25.0，commit `528a0213f01caf70b9f41009cbf7b2f67bdd67ec`，本机 `127.0.0.1:18081`，l1-study组织。运行exe SHA256为`ddbab07cbe0a913e3bf3b3fbb09b0a1fa3b4abc5127c6b3156930aa77a37ad5c`，与既有发行ZIP内exe相同；源码—二进制绑定采用发行版本对应，未进行可复现构建。原始锁见 [run01/environment.lock.json](raw/run01/environment.lock.json)，本阶段解释见 [STAGE_ENVIRONMENT.json](STAGE_ENVIRONMENT.json)。

当前批准可信且最新。A只获得其自身AT/RT及公开client_id；密码、客户端secret、管理凭据、B材料留在可信执行侧。默认A可以直接调用冻结刷新接口。完全托管、A持secret、原生隔离配置分别计入不同profile。恢复和旧快照尚未进入本轮运行。[规格](TRANSITION_MODEL.md)

原 `app-l1-0` 仅作只读模板。C10在新非轮换应用N中运行；C11使用新轮换应用A/B；C12在新B应用、另一新账户运行。新配置初始grantTypes为password/refresh_token，AT与RT均1小时，JWT；C11中途把A的grantTypes改为仅password再删除A。原模板字段运行前后读回一致。当前组织DCR=disabled，模板enableSigninSession=false、enableSignUp=false、enableGuestSignin=false；这些字段由追加的只读记录支持。[profile锁](raw/run01/profiles.lock.json) [只读结果](raw/config01/result.json)

## 五项截止谓词

|谓词|量词与时点|足以支持结论的证据|
|---|---|---|
|K：已知清单关闭|所列每个已知材料在检查时失效|该路径接受检查＋原生处置效果；只覆盖清单|
|P：截止前全部材料关闭|所有在停止意图c之前生成的A材料，在承诺q后对声明路径失效|完整范围或穷尽清单、准确来源及相应处置|
|N：未来派生关闭|q之后，旧A支持无法产生对声明资源有效的新材料|全部可达发行路径上的持久守卫，或绝对期限及在途排空条件|
|R：资源拒绝|q后新发起的声明资源请求，对全部A后代闭包拒绝|资源路径完整、每次新鲜检查、P和N及派生路径闭包|
|B：保留任务|从c至声明终点，B始终具有获准可用路径|处置效果独立＋期限覆盖/提前合法续期；采样只检验离散切点|

q前已在服务器通过接受点、q后才返回的请求，按先前接受事件登记。若目标要求“q之后无响应/无效果”，需增加排空或提供方承诺点证据。客户端响应时序只给出观察偏序。[观察与调度](ADVERSARIAL_SCHEDULES.md)

## 配置机会及结论

|ID|原生配置和攻击能力|B条件/额外单位|可用结论|研究分类|
|---|---|---|---|---|
|P0|同应用password，轮换开，A直接持RT|同账户B独立fresh grant；同应用范围处置影响B|F_closed可逐项收尾；F_active下枚举追赶缺少持久截止；完整平台能力尚未穷尽|PROFILE_COVERED限F_closed；KNOWN_BOUNDARY_INSTANCE限追赶反例；广义CAPABILITY_UNRESOLVED|
|P1|同应用password，轮换关；A族共享RT hash，B另一个RT hash|授权方记录数可以增加，撤销效果单位保持按hash分组；配置由双方同等获得|C10无在途、全活跃初态下，一次撤销清除A三个AT且B接受；一般有限组需用活跃AT定位代表或保证RT查找命中活跃行|PROFILE_COVERED：F_closed、hash来源可靠、定位前提成立|
|P2|P1＋有限RT绝对期限、禁止其他再发行路径|B须覆盖等待区间或获得提前重授权；等待/批准/发行成本另计|可靠时钟和延迟界δ下等待至E+δ+L_A之后关闭所声明材料族；无δ只得逐执行最终性|PROFILE_COVERED限条件模型；完整原生闭包CAPABILITY_UNRESOLVED|
|P3|授权码/浏览器登录，独立非空SessionId|至少两个独立session/批准单元；原password材料sid为空|现有session删除可覆盖当时匹配行；已验证刷新可以迟到插入同sid，关闭session缺少终态存在性守卫|CAPABILITY_UNRESOLVED：真实session子域；KNOWN_BOUNDARY_INSTANCE：快照竞态|
|P4|A/B预先独立应用，管理员可删除A|两个应用/授权单元、独立发行批准；退休标识持续不复用|对始终appA绑定的材料，新Bearer和新refresh被拒；C11中Cookie继续接受|PROFILE_COVERED限app-bound Bearer/refresh子模型；扩展Cookie合同的删除单动作已失败|
|P5|所有A可派生材料均由可信中介持有，A无法绕过|完整材料托管、持久来源/pending，双方同享；B支持独立|停派发→有限排空→完整枚举/已知清单→逐项处置，条件性覆盖F_closed|PROFILE_COVERED：既有正确组合|
|P6|confidential authorization_code RT，A无secret|secret保护适用于该GrantType；AT→Cookie/PKCE等路径仍需闭包审计|checkRefreshClientSecret要求secret；原password的无secret结论不外推到此profile|CAPABILITY_UNRESOLVED：完整闭包及实际授权流程|
|P7|用户禁用/全用户失效|同账户B也被影响；改为中断后恢复是另一个合同|本次作为清理成功；持续B合同中不能用作选择性截止完成点|KNOWN_BOUNDARY_INSTANCE：效果范围与B冲突|
|P8|A额外持应用client_secret|应用Basic查询等权限扩大攻击闭包；同应用列表可能直接取得B材料|历史列表见证表明默认“B材料仅可信方可见”需重新证明；当前停止结论不直接转移到此能力集|CAPABILITY_UNRESOLVED：扩大能力配置|

PROFILE_COVERED的量词始终与表中前提共同使用；单条成功观测没有升级为全Casdoor覆盖。P4的窄合同刻意列出闭包前提，实际A可达Cookie已证明该前提需要额外限制。当前未把该限制当成已部署的网络围栏。

## 来源与身份

相同user/organization描述身份，相同application描述部分原生作用域，任务批准代次由可信账本描述。P1的同hash可定位该RT共享组；P0轮换后缺少父字段，应用/用户相同无法自动区分A/B。A取得B的新材料仍超出当前攻击能力；AT在原生服务内派生Cookie属于本次已核实扩展能力。[来源审计](ENUMERATION_AND_PROVENANCE.md)
