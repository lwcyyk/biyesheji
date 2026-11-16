# R45最终裁决

单文件Windows Supervisor已实现，局部AST、ABI、归属/继承、计数和拒绝门静态审查完成。整体R45_STATIC_PREFLIGHT_BLOCKED，当前八类资源批准值仍null，EXECUTION_AUTHORIZED=false。

## Q1—Q16

| 问题 | 本轮回答 |
|---|---|
| Q1 仅新增批准文件？ | 是，run_dsat_poison28_supervisor.py一个工程文件，取证目录另存报告/JSON/diff。 |
| Q2 Runner/Driver原SHA？ | 分别保持245a35…和28e9cc…，原五函数/helper、测试及fixture均按旧pin核验。 |
| Q3 独立父监督结构？ | 已实现策略、WindowsApi、Job、Child、Output、ResourceObserver和DeadlineController，实际运行待授权。 |
| Q4 Job API/ABI正确？ | 声明AMD64 ABI下字段/对齐/签名静态匹配，类型证书与官方来源齐备，实际OS验证0。 |
| Q5 恢复前Job归属？ | 创建时JOB_LIST配合suspended，恢复前检查membership、创建时间及镜像路径，失败走owned终止与清理。 |
| Q6 继承严格限定？ | 显式HANDLE_LIST只含3个stdio句柄，parent读端清inherit，Job和控制句柄位于清单外。 |
| Q7 六维IO支持哪些T20观察？ | 支持child/Job生命周期及parent成本会计，T20精确分段仍依赖Driver持久证据桥接。 |
| Q8 层次是否准确？ | Windows进程、Job、父API及ETW/物理IO字段分别有来源，重叠会计没有简单求和。ETW=NOT_ENABLED，物理证明false。 |
| Q9 内存指标和缺口？ | 工作集/峰值、PrivateUsage/提交峰值、Job提交峰值及父内存分列，Job当前提交和真实同时树峰值UNKNOWN，采样后尾部缺失显式保留。 |
| Q10 父成本怎样登记？ | 独立parent过程IO/内存、API次数、预检读取、pipe字节和witnesscharge，末次receipt后成本由外部观察承担。 |
| Q11 时间合同？ | 真实90秒请求终止ownedJob，115停止新取证读写，120为新关闭准入。Driver缺少协作停dispatch接口，因此可能中断活跃case。严格120完成仍false。 |
| Q12 null资源是否拒绝？ | 是，在WindowsApi、输出、Job、Child分配前抛RESOURCE_LIMIT_NOT_APPROVED。 |
| Q13 来源/输出/预算不完整？ | 来源批准/原pin/OSbuild、完整payload证书、输出独占和共同cap均为实际入口检查，失败即阻断。 |
| Q14 import副作用？ | 顶层允许标准库导入和数据/ctypes类型定义，显式DLL/API/文件/进程动作均在受控入口。当前未导入新模块。 |
| Q15 实际操作均0？ | 是，Job、Child、资源采样、ETW、28/68测试0，当前真实数据NOT_MEASURED。 |
| Q16 唯一下一项？ | 审定原八类候选及本Supervisor自身成本、失败reserve/pipe/产物证明，当前动态运行请求0。 |

## 限制与验收范围

R45实现使用创建时Job关联，满足R44明确的创建时归属范围。真实90秒截止采用终止Job请求，因R43实际接口缺少协作停止能力。此实现选择已进入策略常量和证据合同。

独立静态审查中修正了父进程伪句柄误入invalid-handle分支、关闭失败先清空句柄、EOF未确认成功及final receipt过早声称全部close确认等问题。当前文件采用修订后的逻辑，动态故障验证仍NOT_RUN。

ABI/源码证明基于冻结AMD64平台、可信不可变运行时与独占输出条件。原生调用后异步中断、OOM、OS句柄关闭效果和严格终止迟滞需要后续独立集成证据。辅助ABI审查在最终代码完成前结束，主审完成剩余源审查，不能将辅助任务当最终OS验收。

## 状态

R45_SINGLE_FILE_IMPLEMENTED、R45_IMPORT_SIDE_EFFECTS_STATICALLY_VERIFIED、R45_WIN32_ABI_STATIC_VERIFIED、R45_JOB_OBJECT_CONTRACT_VERIFIED、R45_CHILD_LIFECYCLE_STATIC_VERIFIED、R45_HANDLE_INHERITANCE_STATIC_VERIFIED、R45_PROCESS_IO_CONTRACT_READY、R45_MEMORY_OBSERVATION_CONTRACT_READY、R45_QPC_DEADLINE_CONTRACT_READY、R45_RESOURCE_FAIL_CLOSED_VERIFIED、R45_SOURCE_LOCK_VERIFIED在本轮静态范围成立。

R45_STATIC_PREFLIGHT_PASSED=false，R45_STATIC_PREFLIGHT_BLOCKED=true。资源批准、G2完整L0、G3、G4、D1-B1及各部署/读取授权分别由既有合同管理。28项全部NOT_RUN，Job/Child/采样/ETW/动态各0。

## 唯一下一步

R45_NEXT_AUTHORIZATION_REQUEST只申请审定八类资源候选及监督器成本。新的源码接口、API清理预留、pipe/raw/base64空间和witness产物条件已具体化，批准记录和运行策略仍待该审定形成。

本轮源代码实施授权已完成。用户R45第一、十一、十七节将OS资源与动态测试继续关闭，因此当前argv=null、运行申请0。成功取得资源/来源/完整负载依据后，再形成单独OS接口及28项执行申请。未知或失败路径继续保留精确责任和原证据。

当前对话内知情模型辅助实现与静态审查，外部独立验证待取得。
