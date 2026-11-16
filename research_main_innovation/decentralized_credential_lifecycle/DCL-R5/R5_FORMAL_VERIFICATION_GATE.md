# R5机器验证最小执行合同

2026-11-10。只给规格/未来命令，不创建.tla/.cfg/.als/.py/监督程序，不运行验证器。F1–F4材料状态为PREPARED_FOR_AUTHORIZATION，执行状态NOT_AUTHORIZED。实现门CLOSED。验证工件属于后续专门授权范围，当前严格分离0，机制实现另受既有分离门限制。

## 1. 共用运行边界

未来工作区拟为`D:/毕业设计/DCL-R5-isolated-verification/<run-id>`，完全独立于冻结研究/主工程。模型、配置、输入、工具和监督器先供审阅并锁哈希。工具候选为TLC，F4附单独的有限策略枚举/递推对照器；具体JDK/TLC工件版本、来源、SHA-256和代码哈希需在执行批准时绑定。未绑定字段保持PENDING，当前没有可执行模型。

一个获准批次共用上限：累计访问状态10^6、总墙钟30分钟、整个进程树峰值4GiB，baseline与mutant、错误/重启均计入，顺序运行。Java堆建议3GiB，剩余给运行时/监督器；堆参数本身不能约束总RSS。监督器需基于进程树资源强制限额、记录状态计数；工具若无法提供足以执行访问状态上限的计数/停止接口，则先标该运行器不满足准入，不用低频轮询冒充精确硬限。可保守提前停止，报告INCONCLUSIVE。未获另批授权时不重置累计计数继续搜索。

本合同将“访问”定义为搜索实际取出并处理/展开的状态次数，跨子任务重复访问照计；生成后继数、不同状态数另列。运行器须能映射并强制这一计数，不能只用不同状态数代替。若工具接口只能给保守上界，可按该上界提前停止；计数无法认证时保持准入待绑定。

未来命令形式（仅审查清单，均未执行）：

|阶段|计划命令/操作|边界|
|---|---|---|
|版本/锁|`java -version`；`Get-FileHash <tla2tools.jar> -Algorithm SHA256`；核模型/配置清单|全部输出写新run目录；工件取得与安装需列入授权|
|监督器|`pwsh -NoProfile -File <reviewed-supervisor.ps1> -Plan <locked-plan.json>`|监督器尚未创建；须审资源硬界、子进程/退出和计数实现|
|TLC子命令|`java -Xmx3g -jar <pinned-tla2tools.jar> -workers 1 -config F1.cfg -metadir <run>/F1 F1.tla`|F2/F3同形；指定工作目录为新模型目录；默认deadlock检查保留|
|F4对照|`python <reviewed-F4-enumerator.py> --contract <locked-F4-input.json> --output <run>/F4`|仅在另获模型代码/解释器执行范围后创建/运行，输出非空后继与共同策略证据|

所有命令在外层监督器之下执行；单独复制TLC子命令不满足本准入合同。输出包括stdout/stderr、退出码、访问/不同状态数、峰值内存、时长、完整反例/检查点、工具/代码/模型哈希和停止原因。达到上限或状态溢出均INCONCLUSIVE。无反例仅适用于明确跑完的有界域。

## 2. F1：复制应用层与恢复

**变量/精确有限域**：基础epoch∈{0,1}，旧/选定新组各四固定成员ID，故障子集为∅或四选一，两组共25组合；竞争child案使用另一个四成员候选组，总三组共125组合，单独登记。连续重配扩展epoch∈{0,1,2}、三组各四不同ID、共125组合也单独登记。phase∈{ACTIVE,PREPARING,SEALED,WAIT_ACTIVATE,RECOVERING}；提案ID∈{r0,r1}；child∈{none,C,D}绑定两份明确的候选Cfg模板；每epoch序号域0…12，超出时明确BOUND_REACHED，不默删后继。

任务/意图为A/iA、B/iB，代次∈{0,1}；每意图两个attempt槽；grant∈{active,revoked}；每槽状态∈{empty,queued,released,unknown,recorded,closed}；quota limit=2，reserved/charged∈0…2且和≤2；origin保持固定映射。Hist为两个材料×两个执行域的bit集合；去重为两个业务opid→固定正文或conflict。引用对象四槽，持有/可用位为布尔；root定义为完整规范状态元组的无碰撞抽象，禁止用有限小hash域制造碰撞。发送权每attempt∈{none,unconsumed,consumed,maybe_sent}，Gate两ID、boot∈{0,1}。ReadyState/Activate签名者集合为委员会ID的子集；正确身份只签已执行持久内容，坏身份可对任意body签名。

Obl取四attempt×{OUTCOME,DERIVATION}的子集；CreatorCaps取两执行域×{password,refresh,session}的子集；每attempt原生观察∈{unknown,accepted,cut}，watermark∈{none,pre,post}。未自由变化的scope、code/schema、正文、批准签名/证据对象均为fixture中列明的有限常量；签名/根用不碰撞的逻辑认证关系。若某省略字段影响守卫/未来/观察，必须扩展域或给保持证明，不能继续按常量处理。

**初态**：e0 ACTIVE、e1待激活；批准/额度一致；一个A已Release且UNKNOWN，B可空；全局dedup含A原opid；正确副本恢复约束/近期head有效。第二个初态族为全部空槽，以覆盖Release建责任。K1另置旧泄露签名集合，分“累计≤f”正常集和“旧quorum已泄露”扩展攻击集，结果不混计。

**转换**：PBFT oracle逐epoch提供唯一有序提交；按21业务转换的相关投影保持其原守卫，八步重配/Seal前Abort、同body重试、错body拒绝、Revoke跨Seal、缺对象补取、ReadyUse缺失下的RECOVERING、Takeover、Retire、恢复与下一次重配逐步建模。被投影掉的业务动作须证明对所检不变量仅stutter或被保守覆盖。应用root不包含节点私钥/本地投票log；oracle自身的稳定view/seq约束作为假设，F1不能证明真实PBFT view-change实现。

**性质**：UniqueHistory/UniqueChild、SealAbsorbing、固定genesis/祖先pin、RHO各字段和去重保持、当前批准、新boot不能重用已消费创建权、缺ReadyUse阻业务但允许恢复元数据。Seal后永久child失效允许停顿。

**活性**：只在单列公平/最终同步、数据/V/quorum可达案检查最终Activate/Takeover。基本安全案允许无限等待；有界命令/搜索深度无法单独证明无界活性。持续等待用显式自环及循环反例检查。

**必须命中**：去掉child绑定的双目标；允许SEALED→ACTIVE；回滚应用Seal的恢复；漏Obl/quota/Hist/dedup任一字段；缺对象即Ready；把旧无序缓存当当前；误把ReadyUse当Release。K1伪Stop、只有旧钥而缺新Activate签名、可信具体摘要pin三种验收层分别测试。变异oracle假设的结果只说明前提必要性。

**缩减/资源/映射**：正常案可按委员置换作对称削减，保留正确/失陷、已pin摘要、发送权持有者等角色区别；多epoch顺序关系禁止合并。状态受共用10^6/30min/4GiB上限约束，无实际计数预报。结果映射到R5 P1/P2/P3-S/P4的应用层，PBFToracle精化和真实秘密流另证。

## 3. F2：原生handler微步骤

**域**：一个父行P、两个子槽C1/C2；行状态∈{absent,valid,revoked}；两个handler H1/H2；phase∈{idle,parent_read,validated_generated,inserted,parent_deleted,done,rejected}；本地缓存valid∈{false,true}；客户端观察∈{pending,ok,error,timeout}独立于handler。rotation∈{on,off}；DPoP关闭以固定当前最小profile；child ID互异或显式collision分案。请求槽两个，revoke至多一次，受控发送≤2；真实费用z∈0…6加overflow。

**初态**：父有效、子不存在、旧来源/两个attempt额度已登记；另一初态族在Release之前；LEAK对照允许一条未登记旁路。未知新生材料超过两槽时BOUND_REACHED/UNKNOWN，不能将其忽略后报安全。

**转换**：Release持久登记→Gate消费→Send（计C_N）→读取父副本→校验/生成→AddToken提交→可选父Delete→响应。Revoke读取/期限化/cohort更新/ACK独立交错；超时只改客户端观察，handler继续推进；审计待写→异步持久另步。Seal冻结Q但允许全部native/environment步。保留来源、责任、费用及迟到Record。

**性质/可达目标**：安全断言为登记/费用/EnvClosure保持及不假关闭；NC1、NC2是存在性见证，分别找“ACK后Insert”与“两不同子提交”，不能把预期可达状态写成应永远禁止的不变量。串行负控制、S/U/L或实际cut后的余量0分别检。ACK与fresh接受、材料关闭及C_effect分列。

**活性**：正常允许响应丢失与UNKNOWN；有界完成只在有限处理/调度/IO条件案检查。cached handler已校验后，撤销不会自动抹去该局部副本。

**必须命中/负控制**：原子化handler导致NC见证消失，应判模型失真；清空Seal时handler/费用使遗漏责任或假关闭；父Delete 0行当冲突的变异需与固定源码不同明确标记；日志查空当全集可命中延迟审计反例；撤销前的全新读取拒绝控制保留。

**缩减/映射**：只合并互不共享父/行/费用/证据的步骤；Read→ACK→Insert关键顺序全部保留。共用资源上限；结果只映射固定源码相位可行性/组合关系，实际二进制与锁条件需T1–T4。

## 4. F3：全前缀支持图与期限/预算

**域**：主迁移阶段0…7；Q_B四ID、坏集合∅或一ID；Gate1/2各state∈{current,unready,crashed}、boot0/1；V/P各up/down；网络∈{timely,gate1_cut,gate2_cut,all_cut}；材料父/子三槽、state∈{known_valid,unknown_valid,expired,absent}；rotation on/off。逻辑请求数0…10，每请求attempt数0…2；reserved、charged各0…24且和≤24；时间tick0…63，保护终点T=60、1tick=10秒，基准expiry=180tick，期限变异值∈{59,60,61}。抽象时钟误差∈{-1,0,1}tick、接纳后服务余量∈{0,1,2}tick，负时钟值取0；原生接受的严格/非严格比较按合同建模，包含恰到边界情形。63覆盖T后该余量/误差的后缀，越界标BOUND_REACHED。此离散域须证明保留相位/比较边界，不能用粗tick隐藏实际到期空窗。

**初态/故障族**：正例两Gate已current、Q_B ACTIVE、V/P up、网络timely、材料已知有效、quota24；Gate初始化准备证据绑定Q_B自身genesis/boot，父Stop=⊥并满足已批准初始化profile，不依赖主Q未来Stop；主Q可迁移。正例允许各Q一故障与一Gate崩溃，同时保持网络/V/P服务合同；扩展故障族逐项允许all_cut、V/P down、共享管理员或共享撤销原子。扩展结果不能被计作正例原假设内反例。

**转换**：主Q各中间阶段、Q_B有序授权/预算预留/发送、读响应丢失/新attempt、Gate故障、时间、轮换Insert/Delete/材料响应、A处置footprint与Provider排队/服务包络。真实微步后立即检Support，坏前缀监视器吸收。达到T不能删除尚未完成请求；只停止S2(T)前缀监视，后续请求/费用/已有claim仍保留。

**性质/活性**：全前缀Support及budget/responsibility；S1安全/条件恢复另检。服务时间保证用显式剩余服务界/排队界验证，公平性只用于最终完成；不存在实际δ测量。业务最多20次，quota24同时检查reserved+charged，额外证据/维护/清理独立预算和共享P负载。

**必须命中**：共主Q单/双Gate Seal；S2-COLD；B-ROT中间态；CUT-ALL/CUT-SHARED；expiry早于T+裕量；剩余额度只看HTTP completed而漏reserved；允许故障合成同时切断两路径。基准正例的NoBadPrefix是待验证目标，当前无机器结果。

**缩减/映射**：Gate只有角色完全相同且相同ready/boot/故障属性时才可互换；环境事件与tick若影响截止/接受，禁止并为stutter。时间缩放仅在证明其保留所有比较边界/事件顺序后使用；否则INCONCLUSIVE。共用上限，结果映射有限S2合同及其抽象输入，物理独立性/QoS由部署验收。

## 5. F4：费用知识与策略

**域**：world∈{0,1}、phase∈{start,after_a,done}、mode∈{0,1}、Obl∈{open,closed}，物理元组域大小24；仅初态/合法转换可达子集参与。累计z∈0…20及overflow；阈值m∈0…20，h∈0…2；a/b/c/STOP四动作；观察∈{same,after_a,done,notice}。夹具各自固定费用表、观察表和允许转换：COST1、CE5、空Post/开放严格义务、可观察费用对照。费用表值∈{0,5,10,15}；mode影响未来的夹具必须保留它。真实quota若另影响动作，另入x，禁止借z压缩遗漏它。

**初态/关系**：每夹具给精确两世界非空B0与原累计z；COST1为两个z0，CE5为(z5,mode0)/(z0,mode1)。Post取同一观察下全部合法segment及累计费用；策略只依观察历史，不读world/隐藏z。W0严格Obl为空、Goal/Inv成立，W(j+1)包含Wj与共同动作的所有安全非空后继。终态STOP仅在完整目标/后续Inv成立时吸收。

**对照与性质**：枚举h≤2共同观察策略与显式轨迹最坏费，另按阈值递推求胜集，逐项对照；固定策略的全部真实执行可交TLC检费用/前缀性质。策略树最多1+4个决策节点、4^5=1024个填表策略的宽松上界（未用观察分支仍统一处理）。这给有限独立路径的交叉校验计划；同会话生成两个程序仍不登记外部独立证明。

**必须命中**：逐阶段跨世界max对COST1给错误选择；删mode后最大z压缩误判CE5；空Post导致vacuum success；按world选各自不同动作违反同观察共同策略；开放Obl被终态接纳；真实查询标零费用；可观察费用对照不可人为隐藏已有信息。

**活性/缩减/映射**：h步终止只覆盖有限segment，墙钟/公平/无界维护另证。只有完整Markov/同观察同未来条件下取最大z；费用本来可见时纳入Obs。共用上限；有界表对照验证具体有限域，纸面可靠性/完备性仍需归纳及外审。

## 6. 正式准入表

|项|当前状态|执行前必须绑定|
|---|---|---|
|变量/域/初态/转换/性质/变异|PREPARED|模型到本合同的逐字段表；完整源码/配置哈希|
|权限|NOT_AUTHORIZED|模型/辅助枚举器/监督器创建、工具取得/运行、文件目录、总资源与所选子任务|
|工具与计数限额|PENDING_BINDING|JDK/TLC/解释器版本摘要；能强制访问状态/进程树界的监督器验收|
|结果归属|DEFINED|有界无反例、存在性轨迹、变异命中、INCONCLUSIVE、纸面证明分别记录|

技术材料足供申请最小验证授权；代码/工具/运行绑定尚需完成，当前机器程序数与运行数均为0。
