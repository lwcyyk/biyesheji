# G1 首个受限原生 profile

版本：G1-LP-CASDOOR-r01；状态：既有实现事实与拟议精化合同并列，端到端精化尚待完成。深入范围为发行/刷新→持久放行→返回或丢响应→撤回→隔离/处置→条件对账→当前在线权威恢复。完整产品目录见02。

## 1. 版本、边界与输入输出

**源码事实。** 采用选定26份源码，均与 `mainline_research_closure_v1/SOURCE_LOCK.json`匹配。既有Casdoor参照4.25.0、源commit `528a0213f01caf70b9f41009cbf7b2f67bdd67ec`。M6发行二进制摘要与其登记发行物匹配；源码到该二进制的可复现构建仍为UNPROVED。每批账户、应用、签名公钥、JWT配置、预算及权限依各批冻结记录，跨批差异保留。[S04、S06、S08]

受限部署为受信任单机、单活控制器、当前在线权威和受保护密钥；代理隔离采用登记的OS/API边界。原生HTTP固定loopback；任意远程AS、网站cookie、其他RP、离线JWT接受、后台业务提交和管理员越权分别需要合同。本profile的“原生关闭”只涉及声明原生材料与接受路径。

| 项目 | 输入 | 输出 | 状态 |
|---|---|---|---|
| 实现身份 | 源码锁、AS参照、二进制/配置、profile与批准摘要 | 适用范围和待证关联 | 元数据已有；形式化源精化待证 |
| 生命周期调用 | 已鉴别caller、task/account/audience/generation、handle、rid、operation、payload | 拒绝/排队/放行、结果或UNKNOWN、责任记录 | 已有 |
| 原生观察 | 获准响应、来源绑定、验签/账户/client校验、只读查询 | 类型化观察、材料引用、证据范围 | 已有受限实现 |
| 合同生成 | 上述版本、允许接口、失败位置、创建上界 | 有限状态与全部允许后继、观察/费用映射 | 本轮纸面草案；自动生成未实现 |
| 审计或恢复 | 当前权威、原来源、未结attempt、当前查询与处置 | C_local、限定C_native、条件CLOSED或缺证 | 已有局部；统一接口拟议 |

## 2. 安全外包络与A可识别信息

执行前应可靠确定：当前身份/批准、账户与站点、允许操作和字段、材料托管位置、调用路径、最坏创建/派生机会、预算、清理资格、读取授权和失败后继。这个外包络覆盖待考虑语义假设的并集。若其中仍有安全相关未知，控制器维持停止或申请补合同。

A可以在外包络内进一步区分：登记假设中的撤销关联、材料来源候选、当前可见状态或配置前提。只有其最坏副作用已获得批准且可记账的查询，才进入A动作集。刷新会创建材料/可能删除父材料，需按真实动作纳入；将它当纯读取需要额外证明。[S11 E7]

`a/compiler.py`中的`__model_internal__`批准标记用于有限编译语义。真实用户批准来自受信任批准入口；内部标记不授予实际能力。

## 3. 合同字段及已有字段复用

| 字段组 | 已有具体字段/对象 | 合同要求与新增责任 |
|---|---|---|
| 身份批准 | grant_id、caller、task、account、audience、generation、operations、active、handle | 绑定同一批准实例；批准的用户含义/期限与UI另交付 |
| 请求来源 | rid、请求规范化digest、origin、approval_op | 重放同体与冲突异体区分；origin由权威构造 |
| 尝试 | attempt_id、release_version、phase | 每次外部责任绑定原请求；原生效果身份与本地attempt分别保存 |
| 材料 | casdoor_login/casdoor_oauth、native、expected_account、client、verified_claims、derived | 原生AT/RT/ID token与本地推导字段区分；jti为单位候选，需实际单位映射 |
| 当前资格 | active、phase、source_rid、当前来源 | 仅当前有效批准和允许来源可供使用；旧代次结果隔离 |
| 责任预算 | reserved、spent、limit、pending/disposal/window | UNKNOWN继续消耗已放行预算；处置、查询及后代责任另计 |
| 证据 | query_ref、source_lemma_ref、identifier/enumeration引用、typed观察 | 指定版本/材料/范围/时间，运行证据与评分真值隔离 |
| 拟议接口元数据 | authority_version、profile/model摘要、snapshot引用、scope | 使用已有事务版本及摘要组合；只为防陈旧和绑定映射引入封装，不另造一套权威 |

当前JWT验证包括RS256及issuer/sub/aud/exp/nbf等；RT在登记源中借同次AT的kid选择公钥。签名通过支持其验证范围；原生行身份、撤销影响域及所有接受者仍有独立责任。[materials.py；S06]

## 4. 真实微步骤与故障包络

| 序号 | 具体阶段 | 持久事实 | 允许真实后继 | 合同处理 |
|---|---|---|---|---|
| P0 | 服务鉴别与请求校验 | 无新放行 | 拒绝、重放、继续 | caller来自鉴别；错误不发原生 |
| P1 | admit | QUEUED、reserved+1 | 撤回取消、release、崩溃 | 预算预留与外部效果分开 |
| P2 | release提交 | DISPATCHED_UNKNOWN、attempt、version、spent+1 | 发送前崩溃、发送、迟到 | 责任已经存在；继续保持UNKNOWN |
| P3 | NativeHTTP reserve | 发送机会账本插入并计费 | 构造/连接前失败、实际发送 | actual_sends按预记账含义解释 |
| P4 | 传输/AS处理 | 本地可能无新增真值 | 未送达、拒绝、创建后失败、父删除/轮换 | 所有源允许后继均保留；SDK重试另扩容量 |
| P5 | 接收/解析/验签 | 可选provider日志/标识 | 结果通过、解析/验签失败、控制器未收到 | 非200/解析失败保持UNKNOWN；不能由此消除创建 |
| P6 | inbox/标识/权威登记 | 可选持久inbox或标识；最终record | RESULT_AVAILABLE或QUARANTINED | 全部绑定原rid/attempt/origin，不迁移到乙 |
| P7 | 撤回/处置 | active=false；处置先持久后调用 | 已知材料失效或处置未知 | C_local与C_native分开 |
| P8 | 对账/乙检查/保存收据 | window/context/证据和收据 | 满足条件CLOSED，否则UNKNOWN | 仅声明attempt；无普遍业务停止 |
| P9 | 服务恢复 | 从当前权威读状态 | 权威不可达UNKNOWN、当前状态恢复 | 旧显示缓存不授权；丢失权威另处理 |

若撤回先于P2，队列请求取消；若P2先于撤回，当前实现仍允许该已放行请求继续到AS。故C_local的截止点定义为“撤回提交后无新的受控放行”；“撤回后线上永无发送”属于更强性质，需要额外栅栏与微步骤证明。

## 5. 创建、派生与丢响应

本地同rid去重建立一次`send=true`放行；NativeHTTP源码没有显式SDK重试循环。AS端单创建上界还依赖传输和固定源profile。每个已放行调用都需同时考虑创建0或最多规定数量、响应已知或未知、父材料保留或失效、后代产生与可见记录删除等分支。

`actual_sends`在当前query实现中来自`requests`表COUNT；表记录发生在`opener.open`之前。合同将其称为**预记账外发机会**。在无额外重试且每机会至多一个单位的源合同下，可将一个机会计为容量1；观察到一个可靠、不同且可归属的单位，才能用于该容量的饱和。孤立计数1不证明已经发送或创建。[native_http.py:101—113,189—209；native_provider.py:155—158,195—208]

inbox只恢复适配器已可靠保存的结果。identifier journal只覆盖启用后的已验证响应。两者关闭且未知新标识时，FakeProvider的通用lookup能力不能移植到真实AS。

## 6. 对账合同及保留边界

| 分支 | 实际读取能力 | 完整性与来源前提 | 未满足时 |
|---|---|---|---|
| 标识点读 | 先有可靠标识，再精确读取原生记录 | 标识与attempt绑定、单位身份/材料匹配、固定scope | UNKNOWN；当前点读代码硬绑定旧l1-study/app-l1-0，不作任意profile通用入口 |
| 授权范围枚举 | 专用组织整体读取，再按账户与应用等值筛选 | 获准范围、记录上界≤单页容量、单读取快照、唯一未知来源及外部写入者排除 | UNKNOWN/范围失败；共享组织账户级读取问题保留 |
| 条件收据 | `make_receipt`及AuthorityStore当前context | source_lemma_ref、单机会/单效果、观察到1个不同效果、目标撤回、未来重试排除、已知甲失效、乙后续指定操作 | 任一缺项保留UNKNOWN |

当前窗口以账户为单位暂停issue/refresh。`B_preserved_after_disposal`要求独立grant的UserInfo结果可用、批准active且release_version晚于最后处置；它保留一个实际声明操作，不能扩张为乙所有未来行为。需要乙继续刷新时需更强合同和新证明。[storage.py:214,240,346—415；tests/test_reconciliation.py:89—112]

源码`save_reconciliation`还要求唯一未知creator、目标DISPOSED、来源绑定及当前context一致。该局部实现承担单未知条件实例；一般多尝试流另见04，当前未实现。

## 7. 终态与费用

| 声明 | 当前可用依据 | 保留限制 |
|---|---|---|
| C_local | 当前权威撤回提交；后续admit/release按同批准重核 | 已放行操作继续有责任；所有绕行入口要由profile排除 |
| C_native | 指定材料/单位的撤销响应及接受路径证据，加源合同 | AT UserInfo、AT内省、RT内省、实际刷新逐项标材料与方法；持续性/后代需源前提 |
| 条件attempt关闭 | 源容量饱和、可靠归属、失效、封口与乙保留 | 只覆盖该attempt及声明接受路径；共享/多尝试不自动推广 |
| C_effect | 还需sink接纳栅栏、在途/派生前沿、可靠终态 | 当前资料未建立一般业务效果停止 |

一次issue/refresh/userinfo按现有适配器各一次显式原生调用。一次完整dispose为RT revoke、AT UserInfo、AT introspect，最多3次；中途失败可能更少。一次成功query通常1次GET，后续每份材料处置、乙验证、失败读取、环境和最终清理分别计入。预算预记账、真实网络发送、AS创建效果和历史批次“HTTP计数”各保留定义。

当前每次权威变更解密/加密整个状态，成本需计完整序列化字节、事务、事件、材料验证及锁等待。h为有限决策步，8秒HTTP超时只限制当前等待，均不直接给出AS效果终止时间。
