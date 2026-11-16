# G2-R46：八类资源的完整计费边界

八类原始英文名称和 `unit` 从 R44 矩阵逐字继承；R46请求中的中文计量说明单列，避免更换历史单位。完整必需列见 [R46_EIGHT_RESOURCE_COST_MATRIX.json](R46_EIGHT_RESOURCE_COST_MATRIX.json)，独立审批表见 [R46_RESOURCE_LIMIT_APPROVAL_MATRIX.json](R46_RESOURCE_LIMIT_APPROVAL_MATRIX.json)。

每个数值均标明作用域。`STATIC_UPPER_BOUND`、`CONDITIONAL_UPPER_BOUND`、`CANDIDATE_LIMIT`、`APPROVED_LIMIT` 和 `RUNTIME_MEASUREMENT` 分别管理。本轮八项完整 `proposed_maximum=null`、八项 `approved_maximum=null`；可证明的局部候选单列在 `grounded_component_candidates`。候选分量足以继续推导，完整进程额度仍待补齐。

| ID | 原始名称 | 可复用或新增的有据分量 | 完整上界仍缺什么 |
|---|---|---|---|
| R1 | fault injection/clock-transition arms total | Driver23次callback arm；68次虚拟时钟写入=55初始化+7直接赋值+6回调交付；Supervisor无新增测试arm/虚拟时钟写入 | mode/ledger/input配置事件总口径；监督状态转换与测试故障分开计量 |
| R2 | metadata/read/write/flush/fsync/open/close call ceilings | Child10次显式输入open、至多8次产物write、18次显式close；父20次控制读取+K次来源哈希+70B PE；封装API共享上限A、成功启动63次、清理至多28次 | 全部模型操作向量、加载器/隐式I/O、前置读取与异常路径、尾部观测 |
| R3 | lock objects and in-memory fixture/stream counts | 55个fixture和owned RLock、2个活动域、71个模型流；父8个Win32句柄+1个FileIO；Job1、root Child1、Pipe2 | 运行时隐式对象/句柄、实际内核Pipe分配与完整存活峰值 |
| R4 | maximum newly created directories | Child2目录+Supervisor1目录=3个明确运行路径 | 此3界覆盖显式 mkdir；来源闭包/隐式运行时影响继续受G4限制 |
| R5 | whole interpreter RSS/working-set budget and enforcement | 每次read chunk≤65536B，单帧Base64≤87384字符；父/子分别可查询WS与OS生命周期Peak WS | 完整CPython/native/双进程/退出尾部峰值；全部字节额度null |
| R6 | actual total cumulative payload write-byte ceiling | Child8个一次性文件cap之和933888B；父witness≤W，条件式933888+W≤2097152 | 完整producer需求、stdio传输、隐式写入和未知持久化；1163264为剩余容量 |
| R7 | complete normal/failure evidence demand within each artifact cap | 每个Pipe记录≤87672B；原9个保留名cap和999424B，实际8个显式文件 | 完整L0、错误/路径/重复字段/父异常和最终receipt适配 |
| R8 | 120s external supervision/abort/cleanup contract | 保留90/115/120准入门和0额外grace | QPC前启动/预检、阻塞native调用、终止滞后、父退出尾部 |

## R1：避免单位重叠

Driver `FaultSchedule.arm/fire` 与fixture初始化为故障计量来源；Supervisor 158–375 的策略核验采用普通循环，无策略回调注入接口。`DeadlineController` 读取真实QPC，不能计入虚拟时钟写入。`termination_requested` 与fallback请求均在调用前置位，成功确认另记；失败会保留请求与未确认状态。Job终止与fallback进程终止在可达生命周期中互斥，整体终止请求至多1次。sample递增≤S、witness序号按成功追加递增，重复检查同一flag保持原事件身份。全部状态写入总量需要先确定计数单位，当前保留null。

## R2：操作分层

父进程 `.read` 调用20次的输入总量，在稳定完整准入路径上≤41943040B；来源文件另计K次哈希，PE头另计70B，重复读取照计。K由2MiB运行时JSON与每项64字符哈希可得粗界32768，因而显式open≤32789。实际来源文件大小之和仍未冻结。读取调用、Python文件方法、封装Win32 API、OS六维计数和物理I/O各有独立单位。

`Output.append` 每次至多1个write/flush/fileno/fsync，清理另有1个FileIO close。Python flush在unbuffered FileIO上的效果不能据调用名直接推成内核刷盘次数。源码守卫在完整序列化后检查大小，内存分配先于该拒绝门。

## R3、R4：构造数、存活数与所有权

2表示活动fixture域数。延迟回收可保留更多锁；保守保留55个owned RLock的存活分量界。模型流71为累计构造界，无法自动转成物理句柄峰值。

父可获取Job1、NUL1、Pipe端4、进程1、线程1，共8个Win32句柄；额外witness FileIO1，合计9个明确自有句柄。主控制器实例6个（Api/Deadline/Job/Output/Child/Observer），另有PolicyValidator1。borrowed pseudo-handle单列。Child继承的三个stdio句柄具有Child自身生命周期；句柄数与内核对象数分开。

显式运行目录为 `observer_run_001`、`verification_runs`、`verification_runs/poison28_001`。没有自动复用、失败重建、临时目录或清理删目录分支。R46报告目录属于文档交付空间；本轮测试运行目录创建0。

## R5—R8：保留完整性缺口

OS生命周期PeakWorkingSetSize有条件覆盖查询前峰值；最后查询后的父尾部继续未知。Job提交峰值与WS驻留页分开。Raw、Base64、JSON及receipt的瞬间内存共存详见04稿；分量字节界无法推出整进程RSS。

R6文件cap守卫限制明确write请求之和，R7负责证明完整证据需求能装入各cap。来源失败、超时、Child未退出、最终写入失败均可能仅留下前缀。前缀可审计性和完整验收分别登记。R37未批准的9组有损条款全部保持关闭。

R8是固定时间约束，当前具备合作式准入检查；120秒内全部退出清理的完备证明尚缺。所有测量、批准和后续实施分别申请，本轮结束后执行门继续关闭。
