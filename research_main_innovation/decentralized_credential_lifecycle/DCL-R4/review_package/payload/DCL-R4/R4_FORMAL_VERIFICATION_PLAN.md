# DCL-R4：机器验证准备合同（待执行）

2026-11-10。只定义模型与验收，无TLA+/PlusCal/Alloy/求解器程序创建或运行。机器证明次数0，IMPLEMENTATION_GATE=CLOSED。以后启动需明确覆盖模型代码/工具执行的授权，并满足适用研究门槛；本文件提供审查对象。

## 1. 选择与分层

TLA+/PlusCal适合状态、消息与公平性；Alloy适合有限结构、身份/父链/依赖关系；有限费用博弈可用独立枚举或SMT交叉检查。工具和版本在未来运行前锁定。当前工具选型仅为建议。

|阶段|状态/关系|目标|抽象边界|
|---|---|---|---|
|F1 复制应用层|每epoch静态PBFT作为唯一提交oracle；八步Seal协议与21业务转换按相关投影保留|P1/P2/P3-local/P4的应用安全|oracle已假定PBFT；通过F1不能宣布PBFT实现获证|
|F2 原生相位|父行/子行、handler缓存、Gate发送权、ACK/消息与环境闭包|NC1/2、迟到操作、CreationCut与P5对应|固定源码合同；二进制符合性另证|
|F3 支持路径|Q/Gate/V/P、故障域、根/期限、预算、footprint、前缀坏状态监视器|S1/S2(T)、B-ROT、共享cut与独立路径|保留网络/期限中间态；无界实时保证另证|
|F4 费用知识博弈|真实(x,z)、合法观察、累计Post、非空后继、共同策略|COST1、W可靠/完备、Markov压缩条件|有限精确模型交叉对照；程序正确性仍需审查|

最终组合需给各层关系与费用/进展保持证明；分层各自通过仍留组合责任。若选一个真实PBFT库，另建该库到F1 oracle的证明/测试层，逐核view-change、checkpoint、身份与持久恢复。

## 2. 状态变量与初态

|变量组|取值/含义|初态|
|---|---|---|
|Cfg/head|epoch、规范成员/公钥、f、父Cfg身份、父Stop、code/schema、可信anchor|旧epoch ACTIVE；新epoch WAIT_ACTIVATE，唯一可信初始head|
|RSM|phase、proposal、Seal位置、unique_child、logical_root、local_durable|无pending/child；各正确副本应用状态一致；oracle提交线性化|
|共识恢复投影|view/seq、已签约束、stable_log、checkpoint/pin|持久约束有效；重启不会清空投票/Seal|
|责任|origin i/o/generation、request/attempt、Obl、global_dedup、quota reserved/charged|两个任务A/B各独立意图；可预置一个A UNKNOWN，其责任全字段固定|
|材料/能力|NativeRows、RTcohort、期限、Hist/MaySeen、CreatorCaps、secret_ref、V权限|给定完整合同输入；E只句柄或显式LEAK分支|
|发送/native|gate_boot、send_right、consumed、network、handler_phase、audit_pending|无发送或一条可追溯在途；状态与费用匹配|
|就绪|ReadyState签名/manifest、ReadyUse角色/版本/预条件|均空；副本只验密文/引用，不接收秘密明文|
|支持/故障|fault_set、reachability、Gate/V/P状态、clock、roots、path_dependencies|满足选定配置；故障集合从初态允许轨迹生成|
|费用/知识|z、cost_labels、Obs、belief B、decision j、budget m|B非空且覆盖真实(x,z)；z含已发生尝试，j≤h|
|前缀监视器|bad_seen、old_claim_scope/post_inv|bad_seen=false；每微步骤一旦失安全/支持即吸收为true|

## 3. 转换关系及纸面对应

- F1按R3八逻辑步逐步建模：Propose、Prepare、Seal、Transfer/ReadyState、Activate、Takeover、Reconcile、Retire；Seal前Abort、精确重试、异正文冲突、Revoke跨Seal、连续两次重配与崩溃恢复单列。完整F逐字段保持UNKNOWN、预算、Hist和去重。
- Release原子登记责任；Gate消费发送权；网络发送/超时；P读取父/校验/缓存生成/子Insert/父Delete/响应；Revoke读取/期限化/ACK；Record/Close分别为转换。它们交错，不压为一个原子native调用。
- ReadyState需完整数据和确定性genesis；ReadyUse由V/Gate给条件证明；相关业务Release需当时有效ReadyUse和当前Q批准。新委员会在ReadyUse缺失时仍可RECOVERING处理元数据。
- 环境可乱序/丢响应、按F失陷/崩溃/恢复、期限推进、披露、审计迟到；每步更新能力与费用并检测bad_seen。Seal后的P继续推进。
- F3含主Q冻结、独立Q_B继续、Gate切换、材料轮换空窗及A处置footprint；静态路径与有状态材料共同决定Support。
- F4按同一历史累计z更新知识：每个合法观察取所有相容segment的末态及累计费用；空Post代表模型/观察缺口。越界溢出返回UNKNOWN。

## 4. 安全、活性与费用性质

安全：UniqueHistory/UniqueChild；SealAbsorbing；完整RHO来源/UNKNOWN/预算/Hist保持；当前批准守卫；至多一次受控发送；新genesis及完整ReadyState；无秘密输出给Q/E的接口约束；真实native相位覆盖；声明scope的PostInvariant；所有受保护前缀Support(B)。形式上bad_seen始终false，禁止仅验段末态。

费用：每个实际native尝试带ΔC_N=1或合同明确的权重，包含失败、查询、验证/清理；内部stutter不能隐藏这些费用。真实z与知识元素沿同一历史一致，策略在每个同观察知识状态选择同动作。

活性分开检查：静态Q最终进展、数据可达、V/P响应、公平提交/调度、有限内部实现段或下降rank、足够预算和原生可关闭性。网络最终同步可证明相应最终恢复；S2(T)所有前缀及时支持需更强全区间网络/服务约束。h约束决策步，墙钟T/δ用有界计时/明确时延假设另验。安全规格允许永久停顿时，结果标签只支持安全。

## 5. 初始有界范围与状态空间

F1先取旧4/新4，f≤1，各委员会故障身份集合为“无故障或四选一”，共5×5=25组合；B支持另设Q_B4时有125种Q故障组合，Gate崩溃和网络故障再乘，分别分层检查。拜占庭与崩溃的归类需固定，不能免费超出每委员会故障界。

初始业务两任务、每任务至多两个attempt；两个epoch及连续重配扩展；native最多四材料槽/两个缓存handler；Gate一或二；每信道消息槽有界且显式溢出；费用m=0…5、h=0…4。COST1另取m=10/15/20以匹配原反例。材料/消息溢出轨迹保留UNKNOWN，不据截断宣称现实无遗漏。

宽松乘积示例：25个故障赋值×25个phase组合×81个材料/期限分类×49个handler相位×9个义务态×36个预算组合×2^24个消息选择，约1.35×10^16；再乘16个节点/对象持有标志位（2^16）约为8.84×10^20。该估算只是变量域笛卡尔积，未报告实际可达状态数。

先分层、固定故障集合、消除规范身份对称、仅压缩证明同观察/同未来的状态、按因果独立性减少交错。保留跨层反例和Ready/发送/Seal/native关键间隙；每项削减需说明被保持性质，尤其活性/公平性不能直接沿用安全削减。建议未来单次上限10^6访问状态、30分钟、4GiB，触及任一上限登记INCONCLUSIVE并保存统计/前沿，授权外扩另行计划。

## 6. 预期反例与变异检查

|变异/输入|预期见证|验证意义|
|---|---|---|
|取消Seal吸收或unique_child绑定|旧Q重开或两个child|P1必要守卫|
|回滚Seal/投票稳定日志|旧ACTIVE再授权或冲突投票|CE1恢复前提|
|缺全对象即签ReadyState|漏UNKNOWN/数据不可用|完整性/活性边界|
|F省略Obl/quota/Hist/dedup|责任丢失、预算重置或旧批准复用|P2逐字段保持|
|把旧无序f+1缓存回复作当前许可|CE2 stale ACTIVE越过Seal|区分有序正常PBFT回复|
|证书阈值降至≤f|失陷签名者可自行伪造|阈值必要性；f+1正常有序回复另属PBFT语义|
|把native作为Q锁内原子步|消失NC1/NC2；与已核相位轨迹不相容|检查抽象是否错误排除真轨迹|
|Seal后清除handler/费用|迟到子创建或实际成本失配|EnvClosure与P5|
|费用查询标成零stutter|CE4超过实际预算|费用标签保持|
|遗漏隐藏模式r后只留最大z|CE5错误阈值可行|Markov压缩前提|
|主Q单/双Gate、忽略轮换中间态|Seal或B-ROT使Support失败|S2全前缀检查|
|允许无限内部stutter|安全成立、目标永不达成|CE3安全与进展分列|

变异命中只能证明检查器发现了预期错误；原模型无有界反例只能给该边界内结果。更强结论须另附归纳不变量/细化证明与外部复核。

## 7. 未来最小运行包与报告

优先F1应用层、F2两个handler、F3单Gate失败与有限正例、F4 COST1/CE5。每次保存完整模型/工具版本/哈希、命令、输入范围、退出码、状态数/资源上界、全部反例与解析、削减说明及纸面映射。独立实现或工具交叉检查另标来源，不把同一生成器的多个输出计为独立证明。

当前交付为模型合同和反例预期。所有执行统计、工具运行和正式机器证明仍为0。
