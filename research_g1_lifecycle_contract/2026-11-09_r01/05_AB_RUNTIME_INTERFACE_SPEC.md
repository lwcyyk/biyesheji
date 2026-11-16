# A/B/AB 与运行层接口草案

版本G1-r01；状态：DESIGN_ONLY。本文沿用S03的四类最小接口，补充字段含义、失效与审计接口。它们尚未接入现有服务；字段表属于纸面规格，当前实现能力以01、03为准。

## 1. 责任分配

运行层提供可信身份、当前权威、材料来源、观察和义务；G1负责把它们保守映射到可用有限模型。A只在安全外包络内选择补证；B消费已知或MODEL_CONDITIONAL且适用的配置关系；AB返回固定scope的阻塞/证书和建议补证。持久Controller始终保留原子准入、预算、来源和结果隔离责任。

模型层拿到的是经授权的最小投影。原始密码、AT/RT、cookie、私钥与评分真值继续留在原边界。动作建议、策略证书及审计收据均不自行生成真实批准。

## 2. RuntimeSnapshot：当前权威到研究输入

生产者：受信任运行投影器。消费者：G1模型构造与证据审计。原子性要求：来源于同一个当前权威版本；额外provider观察保留其独立时间与证据版本，不能拼成虚构同一时刻。

| 字段组 | 拟议内容 | 来自已有对象 | 校验/限制 |
|---|---|---|---|
| 身份 | caller/task/account/audience/generation、grant引用 | grant与origin | 调用者由服务鉴别；跨grant材料不可混入 |
| 版本 | authority_version、profile/source/model摘要、snapshot摘要 | 权威version、冻结配置/源码引用 | source/profile改变必须重建；摘要只固定字节 |
| 批准 | active、operations、批准实例/版本、scope | grant | 产品期限/撤回批准按实际支持表达 |
| 预算 | limit、reserved、spent、清理/查询费用包络 | grant及原生预算 | 不把spent UNKNOWN退回；单位分别标明 |
| 尝试 | rid、digest、origin、attempt_id、release_version、phase | requests | 原请求完整绑定；只输出必要投影 |
| 材料 | 类型、来源引用、创建代次、原生单位候选、接受路径 | materials/derived | 无原文秘密；jti到原生单位需来源依据 |
| 证据 | typed观察、材料/方法/时间/来源、新鲜度与授权范围 | evidence/receipt/query | 不输入评分真值；不将缺失观测写成false |
| 义务 | 未知创建、在途、处置、派生/窗口、乙保留条件 | pending/disposals/windows | 无法界定责任时保留UNKNOWN |

返回值：`SNAPSHOT_READY`或`SNAPSHOT_UNAVAILABLE`及原因，均为拟议接口状态。不可达、版本不一致或投影授权不足时不构造授权性的模型输入。

当前AuthorityStore已有recover与事务版本，但没有这一统一研究快照封装。现有grant、request、material数据继续复用，不建立平行状态权威。

## 3. ModelEnvelope：快照到有限知识状态

生产者：G1合同/映射层；消费者：有限编译器和A/B/AB。输入RuntimeSnapshot、固定有限source与动作/观察映射、映射证明引用。

| 项目 | 必需内容 |
|---|---|
| 有限域 | 明确登记的world/state集合、初始K、材料/责任抽象；K非空 |
| 目标 | 声明C_local/C_native/保留任务和支持路径；C_effect需额外已证合同 |
| 预算 | 剩余资源预算及决策步h，原生宏费用映射；尚未完成动作的责任 |
| 动作 | 每个模型动作对应的当前批准、微步骤、全部后继/观察、源引用 |
| 边界 | 允许假设、外部行为、版本/新鲜度、未支持结构 |
| 证明 | R/K/X/T义务覆盖引用；有限source审计报告；模型/快照摘要 |

成功状态`ENVELOPE_READY`只表示满足列出适用前提。重叠相关撤销域、未建模异步setup、未知源效果上界、未封口创建、超出有限语法/规模等，返回`UNSUPPORTED_OR_REBUILD_REQUIRED`；可能已发生效果的责任继续由运行层保留。

模型上限属于当前实现语法：例如B最多8任务、16项若干目录、h≤8（`b/model.py`）。超限应明确输出，不能以静默截断改变合同。未取得真实覆盖证明时可做分析性有限模型，但不将其策略作为实际派发资格。

## 4. PolicyProposal：研究建议到执行层

生产者：经检查的A/B/AB输出包装器；消费者：Controller拟议接入层。

| 字段 | 含义 |
|---|---|
| proposal_id、scope | 固定模型、快照版本、配置/目标/预算和证书适用域 |
| source/profile/model/snapshot摘要 | 防止把旧合同或别批证书套到当前调用 |
| action_template | 仅允许已登记动作；不允许模型提供任意URL、身份或secret |
| identity/approval/source绑定 | caller/task/account/audience/generation、grant/source_rid引用 |
| preconditions | 当前权威重核项、原生前提、允许观察、数据/会话范围 |
| microsteps/Post | 具体操作序列、所有已证明允许后继和迟到/部分失败处理 |
| cost_envelope | 请求/批准/计算/存储等分项最坏费用，含检查、拒绝和清理 |
| obligations | 当前与可能新增责任、cleanup资格及保留任务合同 |
| certificate | 原策略/证书与独立检查结果，包含scope及失效条件 |

执行次序合同：检查证书与映射适用性→读取当前权威→比较当前版本/批准/预算/来源→通过现有接纳与持久放行→原生微步骤→原来源登记/隔离→类型化反馈。任一步变化可导致重新规划或安全拒绝；已派发UNKNOWN的费用与责任保留。

现有API的`exact_fields`未接收上述完整提案，也没有通用“expected_snapshot_version”比较交换。后续若扩展，需要证明包装层与权威事务之间无过期授权窗口；单靠事前比较版本仍不充分。当前原子release能重核其已实现的绑定、active、来源与预算条件，profile/model新鲜度等新增义务要另行接入。

B可靠setup的每个具体创建都生成自己的持久尝试和责任。动作中途撤回、丢响应或部分成功时，返回已知/未知配置残余，禁止直接宣告完整setup成功。AB阻塞scope应准确列出固定配置/未来允许动作；扩展后续补证策略时需重检证书。

## 5. RuntimeObservation：执行结果到知识更新

生产者：Controller/适配器证据解释器；消费者：G1映射及研究层。

共同字段：原rid/attempt/digest/origin/release_version、当前authority_version、profile/source摘要、发生/接收时间、证据引用、可见来源、费用及义务变化。以下类型名为草案命名，现有源码status另作映射。

| 类型 | 可表达事实 | 不足项处理 |
|---|---|---|
| LOCAL_REJECTED | 当前请求未获新的受控放行及原因 | 旧同rid已放行责任另保留 |
| RELEASED_UNCERTAIN | 已放行、spent已计，外部阶段未知 | 保留所有允许创建/失败分支 |
| NATIVE_RESPONSE | 指定方法/材料/路径的实际响应 | HTTP、解析、验签、接受含义分别解释 |
| RESULT_REGISTERED | 原来源材料已登记且当前资格明确 | 陈旧或撤回结果进入隔离 |
| MATERIAL_QUARANTINED | 托管入口停止该结果使用 | 原生失效/后代另证 |
| DISPOSAL_OBSERVED | 指定材料处置响应及路径观察 | 保留未覆盖路径/持续性责任 |
| RECONCILIATION_CLAIM | 指定attempt的条件CLOSED或缺证 | 附条件、missing、scope；业务效果另列 |
| OUT_OF_MODEL/CONFLICT/STALE | 当前模型或证书失效 | 停止当前策略，保留责任，重建/补源合同 |

只要观察映射不能证明覆盖，就不继续使用当前K作为授权依据。拒绝、缺证、超限与模型内NO/IMPOSSIBLE分别展示；后两者也只对其已证明有限scope成立。

## 6. AuditRecoveryClaim：证据到审计/恢复

输入：声明scope（任务/代次、材料/后代、路径、时间/版本）、当前权威引用、历史与当前证据、源合同、明确读取授权。输出分四组：已确认事实、条件性结论、未结责任、缺失/陈旧/冲突原因。

恢复先取得当前权威和密钥资格，再处理旧缓存、材料、pending和处置。证据包/签名/链上检查点可固定声明历史；它们不生成新原生事实，也不自行恢复被撤回批准。若F为空或权威版本倒退，显示证据冲突/待恢复合同，不采用空集全称成功。

用户可见状态至少区分：本地已撤回、指定材料已观察失效、条件attempt已关闭、仍有未知责任、乙指定操作仍可用、业务效果停止未证。审计结果附材料与路径范围；秘密原文通过独立权限管理。

## 7. 接入验收责任

接口验收必须同时满足04的后继覆盖、知识包含、当前准入、终态反映和费用映射。单独序列化字段、打通RPC或显示证书都只完成工程连接。本轮没有产生接入代码或执行轨迹。后续工程与候选研究分别按08交接。
