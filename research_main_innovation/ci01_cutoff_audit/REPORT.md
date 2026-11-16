# CI-01：可枚举派生材料的选择性截止能力核验

## Material Passport

完成日期2026-11-05。本阶段采用 academic-research-suite 的证据核验纪律，在当前辅助流程内完成源码审读、预先冻结命题、API取证和反方审计。没有外部同行评审或候选保护机制实现。

## 五项最终回答

**现有原生能力是否足以完成选择性截止？** 对F_closed及前提明确的非轮换同hash组，现有能力与正确组合足够。对A持续持有直接可刷新的RT、全部可达衍生路径均纳入R且B持续合法可用的广义合同，当前证据保留CAPABILITY_UNRESOLVED。只移除refresh grant或只删除独立应用都不能直接承担完整截止承诺。

**结论覆盖哪个输入族？** 覆盖“停止新派发＋有限完整pending＋稳定完整枚举/来源＋A/B效果独立”的F_closed条件族。非轮换固定期限在给定时钟/延迟/闭包/B续期前提下有等待上界。独立应用删除只覆盖始终绑定被删应用的新Bearer/refresh子模型；实际Cookie反例阻止其扩大到完整原生路径。

**剩余缺口是什么？** 在同账户、B持续可用的约束下，A旧支持是否能经AT→Cookie→现有授权码/PKCE/SSO等路径跨出原截止作用域，以及原生session/应用组合能否完整、持续关闭这一可达闭包。当前组织DCR已确认为disabled，排除了该组织的新增DCR路径；其他既有授权路径仍需准确能力闭包。任务批准来源仍需可信账本，原生列表缺任务代次和轮换父子边。

**是否超出已有正确组合与经典边界？** 当前发现可由完整中介、来源完备、枚举稳定性、期限和提交/资源检查的经典前提解释。RQ、AID-Guard和RAG已覆盖对应原则；本轮未得到满足其全部前提而失败的反例，也未得到新紧边界定理。

**是否已有严格分离对象？** 当前为0。候选机制实现门继续关闭；后续最有信息价值的查证是冻结一个实际授权码/session子域的全部A可达再发行路径，并测试同接口组合是否封闭。恢复/旧快照新鲜度仍作为独立后续依赖，当前主问题不靠它制造差距。

## 三项改变裁决的真实观察

1. C10：非轮换profile中A0/A1/A2共享RT，一次原生撤销使三个AT均拒绝，B独立RT支持继续接受。该原生替代进入强基线；并发迟到插入另需排空/期限条件。
2. C11：同一新应用移除refresh grant后，总入口拒绝，专用refresh接口仍发行；删除A应用后，新Bearer和两刷新入口拒绝，之前由当前AT创建的Cookie仍能访问同一userinfo，B保留。资源路径与衍生载体必须进入合同。
3. C12：三个新记录按唯一name升序分页，删除第1页记录后，第2页跳过一个仍存在的记录；失效记录继续出现在列表。枚举权限成立，完整截止水位仍需另外证明。

原始证据为[run01](raw/run01/result.json)及[配置只读补充](raw/config01/result.json)，离线核对见[EVIDENCE_AUDIT.json](EVIDENCE_AUDIT.json)。本轮88 HTTP、3新用户/3新应用，均清理；27接受检查，6只读SQL。391份登记历史文件哈希一致。计数属于本轮证据范围，不与历史199 HTTP、52次调查或576次校准合并。

## 交付索引

|文件|内容|
|---|---|
|[PROFILE_MATRIX.md](PROFILE_MATRIX.md)|截止谓词、攻击材料、配置/权限与覆盖范围|
|[NATIVE_CUTOFF_PATHS.md](NATIVE_CUTOFF_PATHS.md)|六类必查原生路径、期限、额外再发行路径与源码定位|
|[ENUMERATION_AND_PROVENANCE.md](ENUMERATION_AND_PROVENANCE.md)|分页、快照、字段、权限、来源账本及完整性条件|
|[TRANSITION_MODEL.md](TRANSITION_MODEL.md)|采样前冻结的微步骤模型、输入族与命题|
|[ADVERSARIAL_SCHEDULES.md](ADVERSARIAL_SCHEDULES.md)|六类调度、任意长度追赶的条件归纳、有限范围|
|[SIMPLE_COMPOSITIONS.md](SIMPLE_COMPOSITIONS.md)|五种现有组合、条件性充分性、RQ/AID/RAG逐项映射|
|[COST_AND_TERMINATION.md](COST_AND_TERMINATION.md)|全部费用、等待界、清理、复现与限制|
|[PRIOR_ART_MAPPING.md](PRIOR_ART_MAPPING.md)|先例原文映射与分离门|
|[DECISION.json](DECISION.json)|机器可读裁决、证据缺口与改变裁决的证据|

`collect_cutoff.py`和`collect_configuration.py`只封装已有API与观察；`check_schedules.py`只核验已冻结纸面命题；`audit_results.py`独立读取原始事件、快照和哈希。旧目录/原算法均未编辑。正常运行的原生服务数据库和服务日志会因已授权测试变化，与历史证据文件保持分别管理。

## 反方审查记录

“枚举到了两个token，能否证明全部？”——需要稳定域/单SELECT和来源闭包，C12提供实际漏项。

“删应用已经解决，何必继续？”——新Bearer路径确实被覆盖，C11的Cookie继续访问限制了更强承诺；额外两个应用和管理权限必须计入。

“非轮换存在固定RT期限，活动派生岂非总能结束？”——限定可达路径及延迟界后已有等待组合可以结束；若其他路径可发行新RT，则应重新定义闭包。B等待期间的支持也须计费保证。

“反例是否证明新协议必要？”——目前仅支持特定组合失败及已有边界。全接口能力未穷尽，没有新协议必要性或成本分离证明。

“有限模型是否验证真实并发？”——74交错属于所列微步骤子模型；真实API采样为固定顺序。两类证据分目录，模型没有声称穷尽服务器执行。

“A拥有应用secret时情况相同吗？”——同应用secret已有列表权限，可扩大到取得B材料等能力；该profile须重画攻击闭包。默认A无secret，秘密托管与全部材料托管分别登记。
