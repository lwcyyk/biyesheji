# 工程接口、后续验收与完整费用

全部为P类实施评审材料；本轮无源码修改、检查器或测试执行。

## 1. 五个入口及最小接线

| 入口/现有模块 | 现有方法/字段 | 所需补充与输出 | 调用者/验证/失败 |
|---|---|---|---|
| 1 AuthorityStore/Controller | recover、state_projection、request_projection；五元/批准/phase/spent | 可信typed snapshot：operation/source_rid、结果/处置ref、完整grant operations和创建窗口/未来入口、O revision | 可信Controller内部；原子读同一权威状态；缺字段不猜，拒绝或保守UNKNOWN |
| 2 native_provider/materials | lookup、token_bundle、identifier日志、get-token/get-tokens、现有UserInfo | 无秘密evidence bundle导出：原五元、全部相关inbox条目/冲突、journal条目/缺口范围、命名查询typed结果、参数和scope | 经批准Collector；原生/本地权限双检；不开放raw secret给AI |
| 3 evidence_semantics/投影视图 | normalize_material/query已有观察分型 | 03 typed投影，历史创建、相容来源、容量、D按scope、开放前沿和issues | 可信纯数据阶段；输入限可信refs；未知保持未知 |
| 4 reconciliation/权威提交 | 旧make_receipt、begin/save_reconciliation单未知 | 新版本分scope对账提案/原子提交、O转换、依赖校验；原单未知API不改义 | 可信管理者/Controller；CAS式重基准；不擅关旧window |
| 5 A/B/AB研究适配 | raw L0/K/O及旧A/B接口 | 同scope的可靠K过近似、来源图/界/配置依赖、模型外标记 | 研究执行边界；当前语法不足则SOURCE_OR_REFINEMENT_GAP，禁塞虚构DIAG |

operation/source_rid也可从完整可信请求正文重算原digest连接；它包含handle等能力材料，只能在可信域校验后导出最小字段。无法取得正文时，typed snapshot是必要的最小接口改动。

独立命名内省尚未公共接线；unknown Issue不能走旧refresh-only helper；多未知/第三grant不能绕过旧2/20守卫。应提供版本化证据读取/提案入口，保留旧行为和兼容测试，不把保护条件直接删除。

## 2. 当前性、事务与隐私

取得权威基准→合法读取→无I/O投影→提交前重核依赖→同事务保存O/历史/费用/证书ref。读AS与权威无法现有原子统一，故原生前沿/路径/时间仍需显式frame。冲突时重读或继续UNKNOWN，不回滚真实已付机会。

受控材料仓持raw Token，结果给AI采用opaque ref及scope内结论。原生组织GET可能含其他账户秘密，Collector权限/留存和审计要覆盖整个返回；不能以“密码管理器内部”免除范围批准。评分密钥/真实响应封存不进入ProjectEvidence。

## 3. 标准计算与完整成本

令h=|U|、k=|I|、e=|E|，V=h+k+2、M=h+k+e，整数位长b。标准整数流值h与F双向对应；按D∩T放费用1求d_T，按T放费用1求m_T。保守逐次增广+Bellman–Ford包络O(hVM)算术操作，位费用乘poly(b+log(h+k+2))；图建立/读取及流/势证书核验O(V+M)加整数费用。逐边固定求Γ至多e次可行性调用；G可复用更快允许边/流算法和缓存。容量不按数值展开槽，原C_T保留二进制c。

此处仅给成熟工具费用，未实现/调用求解器。原生语义不足、无界I、D或边缺证时，算法不能替代来源证明。

现有AuthorityStore每次read_state读取/解密整份单行快照，mutation重新规范化、加密并写全量状态；令序列化状态大小S，至少完整扫描的O(S)处理与相应字节I/O必须记账。C03重启扫描inbox，现有点读helper也逐次解析全部journal；多attempt逐次重扫会重复承担日志大小费用。成熟批量索引可以复用，索引构建/存储/失效/恢复照计。A/B/AB后续状态编译与规划费用另外记录，字段投影不提供免费最优策略或显式世界全集。

| 账轴 | 费用口径 |
|---|---|
| Q_model | 形式动作次数/权重，必须绑定动作到真实请求包络；与AS次数一般不等 |
| C_native | 每次AS预记账机会、字节/物理发送、分页、失败/重试及历史获取前缀；各单列 |
| C_compute | 规范化/连接/别名/构图/匹配、K/策略适配、更新与恢复；时间/内存均计 |
| C_storage | 日志/密文/索引/历史tombstone/证书及保留期，累计读写字节和事务 |
| C_verify | 真实性/权限/digest/源合同/失效frame/证书当前性及每次重核 |
| 其他 | 用户批准、可信组件/秘密范围、RPC、等待、对账、维护和错误处理 |

纯投影新增AS=0但前缀证据成本和本地成本保留。一个model快照若要p页则付p次及一致性责任；若当前wrapper只支持p=1，p>1不能假定已可执行。无限UNKNOWN下区分有限安全退出与无统一有限最坏完成费用。

## 4. 四阶段验证计划

**S 静态投影。** 冻结24个纸面输入、字段版本、源/权限清单和预期结果；未来取得实施/运行资格后才做schema/纯投影/标准流证书验证。先覆盖非空F、别名、O守恒和权限拒绝。当前NOT_RUN。

**F 受控故障。** 单活可信权威/Provider，缓存恢复不回滚权威；现有after_release/after_effect、before_native_refresh、identifier后/收件前等屏障按源码适用类型使用。Issue响应丢失需要另行批准的传输故障手段；当前refresh专用hook不能直接声称覆盖Issue。Go检查后/Insert前的精确暂停无现成原生注入证明，保留纸面交错，新增hook另审。

**N 原生验证。** 新的专用测试组织/app、两个明确批准测试账户，固定v4.25.0映像/配置/source锁，普通本地账户、JWT/RS256及轮换开启；password grant仅为实验对象。M6旧授权不继承为本轮新账号/API资格。验证源到二进制仍须独立绑定，缺可复现证明时保留条件性。

命名提案为组织`r04-ro-<approved_run>`、应用`r04-ro-app-<approved_run>`、账户`actor-main`与`actor-control`，仅在审批后实例化。甲乙/V同属main账户，control默认不发行Token，供权限/范围边界检查；若需control材料，先重新计算创建/查询/清理预算并冻结新case。批准范围逐项包含专用对象建删与复核、main的指定五项创建、命名读/内省/UserInfo、整个专用组织Token读取和已知材料处置。真实secret由可信保管者提供，研究文稿只留引用。

**AB 接线。** 仅将允许输入投影送入模型，比较所有相容来源/未知和局部B守卫；输出模型外状态不得许可真实操作。检查旧W全终态与局部进展分工、预算/迟到/证书scope。没有新增隐藏真值或oracle。

## 5. 每个未来原生案例的预算提案

这是待审批上限，当前无调用授权：environment≤12、method≤40、measurement≤8、cleanup≤16，总≤76机会；一次性案例、不自动重采。主轨迹最多5次创建调用：p/b初始发行、两旧refresh、V的issue。其余method预算用于至多12次读取、3次B读取、4次只读失败重试机会及已知Token处置最多15次，共不超过39；第40次作显式余量。此批次禁止额外创建重试，避免把直接单位上界从5扩到9；4次重试按单HTTP机会计算，不代表4个多请求dispose宏。处置失败后的额外调用必须在剩余额度和独立审批内处理，否则保留UNKNOWN。

重要接口事实：当前Provider的dispose也使用method类别，cleanup类别余额不能保证Token清理可用。计划必须在method中保护15个处置机会；当前没有可证明独立强制的method子预留API。可信调度阶段上限与排他调用为条件，若需要更强保留需单独资源规格，不能免费声称已实现。cleanup16只用于已批准环境对象清理/复核。

五项创建是可信、排他的案例调度约束，grant的操作集合/总预算本身不强制该顺序。理论快照界仍按全部允许创建计算；发现额外放行、来源或重放时扩I/O并停止当前有限case，不能继续以“五材料清理”宣称完备。

预算是硬停止上限，不是失败后一定完成的保证。AS迟到/未知材料无法有界清理时，保留O、隔离环境、停止复用；账户级关闭影响B只能在B评分和保留目标完成、获明确批准后执行。外部RT/无限后代情形不得进入此有限预算承诺。

## 6. 审计和评分隔离

运行前锁输入/原生映像/配置/版本/预期、权限/额度、持有者和写入者清单；确认真实对象/必要账号授权及清理责任。运行中记录authority版本、rid/attempt/H、实际HTTP结果/错误、本地RPC、证据获取/投影/提交及O前后。运行后固定哈希、差异、未知/失败分母、B与各scope证书、清理状态。

独立评分角色只读封存真值，不向Controller/选择器回流。评分权/密码学封存沿成熟M6能力，不假定本轮已搭好环境。每个case记录NOT_RUN/PASS_WITHIN_SCOPE/FAIL/INCONCLUSIVE，保留空结果和预算失败。

## 7. 实施门

当前只有规格可评审。新代码、现有模块执行、故障测试、账号和原生操作各须单独执行资格。候选创新机制还须用户规定的严格分离实例；本轮未取得。成熟工具接线不被重新命名成独立算法创新，也不借READY状态绕开原门。
