# G2-R46：最终裁决与唯一下一步

本轮已完成八类资源身份冻结、Supervisor全调用图成本、Pipe/Base64/JSON算术、T20与父子Job边界、时间成本分区及独立审批矩阵。结论为 **`R46_STATIC_PREFLIGHT_BLOCKED`**。八类完整候选和批准上限均为null，`EXECUTION_AUTHORIZED=false`；原28项均NOT_RUN。

## 决定性新证据

- 成功启动至ResumeThread共63次封装调用，28个声明API中27个主图可达；普通调用共享A−32门、清理共享A门。
- 自有句柄至多8个Win32+1个witness FileIO；全生命周期cleanup标记封装调用≤28，32槽预留足够容纳这些封装尝试。原生关闭成功与耗时另证。
- QPC前存在20次控制读取、K次来源哈希和70B PE读取。K可由输入文档得粗界32768，显式open≤32789；来源累计字节与耗时仍未闭合。
- Pipe记录精确长264+d(seq)+d(n)+4⌈n/3⌉；单Pipe行≤87672B。分片产生独立填充与头开销；Raw已读与fsync确认尚缺持久前缀对应。
- 单最大Pipe帧可见负载分量包络875180B，整进程/内核Pipe/双进程峰值另有未知项。
- 最后api快照遗漏其后至多5次封装QPC以及FileIO与退出成本。最终receipt仍受115秒准入，120秒新关闭门无法提供父全生命周期完成保证。

## 准入门

| 门 | 结果 | 证据 |
|---|---|---|
| G1 RESOURCE_SCHEMA_COMPLETE | true | 8项名称/单位/必需列齐全 |
| G2 SUPERVISOR_COST_STATIC_BOUND | false（部分界已证） | 封装界可核算；完整bootstrap/native/预检字节/时延缺口 |
| G3 T20_FULL_IO_BOUNDARY_PROVED | false | 主操作保留；持久分阶段/观察完整性/结果进度桥接缺失 |
| G4 PIPE_AND_ARTIFACT_CAPACITY_PROVED | false | 帧算术成立；内核Pipe与完整L0/receipt需求未证 |
| G5 PROCESS_MEMORY_BOUND_PROVED | false | 父/子/退出尾部整进程峰值额度null |
| G6 HARD_DEADLINE_SUPERVISION_PROVED | false | 起点前成本、阻塞native和终止滞后尚未覆盖 |
| G7 RUNTIME_ORIGIN_ADMISSION_PROVED | false | 三份源码匹配；完整加载来源与旧差异继续待核 |

此处G1–G7为R46资源门编号；继承的G2完整L0、G3证据批准和G4运行时来源使用各自全称标识，分别管理。

`R46_SUPERVISOR_API_BOUNDS_PROVED=true`只限封装接纳上界。Base64/帧长度和单帧可见负载分量公式单独标为PROVED。完整 `R46_PIPE_RAW_BASE64_BOUNDS_PROVED`、`R46_WITNESS_CAPACITY_PROVED`、`R46_T20_FULL_IO_BOUNDARY_PROVED`、`R46_MEMORY_BUDGET_PROVED`、`R46_PROCESS_TREE_PEAK_PROVED`、`R46_DEADLINE_COST_MODEL_PROVED`、`R46_EIGHT_RESOURCE_PROPOSALS_GROUNDED`、`R46_RESOURCE_LIMITS_APPROVED`、`R46_STATIC_PREFLIGHT_PASSED`、`R46_EXECUTION_READY`均为false。明确分量候选有据，八项完整总界仍缺失。

## Q1—Q16

| 问题 | 答复 |
|---|---|
| Q1 原始名称/单位保持？ | 是，逐字继承R44的8项unit；中文计量说明单列。 |
| Q2 哪些源码候选可复用？ | 23 arm、68 clock、55 fixture/RLock、2活动域、71模型流、Child2目录、8文件933888B及固定120秒约束。各自保留原作用域。 |
| Q3 父新增多少类资源？ | 全部8类均有父参与的计费或控制边界；新增测试arm/虚拟clock为0，监督状态转换单列；新对象/Pipe/输出/调用/内存/时间均已建模。类别计数无法代表总调用量。 |
| Q4 API次数静态可界定？ | 封装总≤A、普通≤A−32、cleanup全生命周期≤28；成功启动63。隐式加载/native/系统调用总数继续未证。 |
| Q5 父、Child、Job I/O区分？ | 是，父和子为独立owner，Job与Child重叠；harness/evidence为owner内子集。 |
| Q6 最坏共存空间？ | 单最大Pipe帧可见负载包络875180B；另加Kout+Kerr、对象/分配器/native、receipt/policy及Child并发项。完整数值null。 |
| Q7 witness和receipt完整容量？ | 未证。Pipe帧界成立；36字段宽度递推已列，错误文字、实际路径、完整L0、重复展开和失败后缀仍待补齐。 |
| Q8 父Peak WS如何计量？ | K32GetProcessMemoryInfo的OS生命周期PeakWorkingSetSize及时间戳；父最后查询后的tail需外部观察。本轮NOT_MEASURED。 |
| Q9 进程树同时峰值可证明？ | 当前UNKNOWN；完整双峰之和只能作CONSERVATIVE_AGGREGATE_UPPER_BOUND，无法充当实测同时峰值。 |
| Q10 T20主操作与全程独立？ | 是，保持原单次observe_result和零write断言；全Child/父/Job生命周期另计。 |
| Q11 六维I/O盲区？ | Python API、全内核调用、物理写盘、后台/其他进程、T20精确phase与未采样父尾部均无法仅由六维计数推出。 |
| Q12 90/115/120覆盖父全部成本？ | 当前未覆盖。bootstrap/preflight/DLL/QPF在锚点前；native/终止/close完成与退出tail缺有限界。 |
| Q13 八类候选分别多少？ | 完整proposed_maximum全为null；02稿和审批矩阵逐项列有据分量。R4显式路径组合为3，属于明确路径作用域。8项approved均null。 |
| Q14 需要T20桥接或外部补充？ | 需要父显式成本/Raw持久前缀记录、后续独立T20持久phase/进度桥接和父尾部/启动锚点合同；三项分别授权。 |
| Q15 可以形成准确执行命令？ | 当前argv=null。现有接口模板为Supervisor --policy及Child --execution-lock；批准policy/来源/资源/完整证据缺失，无法形成可执行冻结命令。 |
| Q16 唯一最小下一任务？ | 独立审定并实施Supervisor显式I/O与证据覆盖计量的最小静态补充；详见下文申请。 |

## 唯一下一步

提交 [R46_MINIMAL_SUPERVISOR_ACCOUNTING_REQUEST.json](R46_MINIMAL_SUPERVISOR_ACCOUNTING_REQUEST.json)：**只补Supervisor显式I/O/来源读取计费、Raw到已确认witness前缀的对应及receipt覆盖截止说明，并静态计入新增字段费用**。目标仍为单个监督器文件的最小变更申请；R46中该申请未获批准、未执行。

其成功可解除父显式成本与Raw持久前缀接口缺失，支持后续来源目录固定和完整容量推导。若在原表示、2MiB和截止门内无法容纳，保留RESOURCE_BOUND_UNRESOLVED/ARTIFACT_BUDGET_UNPROVEN并精确收缩可承诺的证据合同。外部完整退出、内存、T20和来源责任仍独立存在。

资源批准、T20 Driver桥接、产物容量证明、G4实际来源核验、外部父生命周期监督和动态28项测试逐项列于 [R46_NEXT_AUTHORIZATION_REQUEST.json](R46_NEXT_AUTHORIZATION_REQUEST.json)，没有合并成笼统授权；本轮动态运行申请0。

## 完整性与保留状态

历史2561项、R45新增30项及46份既有SOURCE_LOCK的最终比较见sources/HISTORY_AFTER；三份工程源码保持冻结。所有实际资源指标NOT_MEASURED。源码/Driver/Supervisor改动0，新Python文件0，Job/Child/采样/ETW/动态测试0。最终锁绑定全部新交付，根摘要以外部读回为准。

`R46_DYNAMIC_TESTS_ZERO`、`R46_28_TESTS_NOT_RUN`、`R44_RESOURCE_LIMITS_APPROVED_FALSE`保持。`G2_COMPLETE_L0_CAPACITY_UNPROVEN`、`G3_BOUNDED_CONTRACT_PARTIALLY_APPROVED`、`G4_RUNTIME_ORIGIN_ADMISSION_PENDING`及`D1B1_PARTIAL_IMPLEMENTATION`继续。D1-B2、P1a、P1b、P2、S3-B2、S5均未获本轮授权。

本轮限当前对话内知情模型辅助静态研究。发表优先权、外部核验、机制实现资格及所有既有研究限制继续按原状态管理。
