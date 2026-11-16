# 八类资源逐项审定

R42八类原名称逐项保留，没有合并单位。R43_EIGHT_RESOURCE_BUDGET_MATRIX含maximum_allowed、边界、操作、源码counter、STATIC_BOUND、峰值、清理和超额行为。原准确批准上限缺失的值继续为null，RESOURCE_BUDGET_UNRESOLVED=true。

| ID | R42原名称 | 源码审查状态 |
|---|---|---|
| R1 | fault injection/clock-transition arms total | CONDITIONALLY_PROVED |
| R2 | metadata/read/write/flush/fsync/open/close call ceilings | UNPROVEN |
| R3 | lock objects and in-memory fixture/stream counts | CONDITIONALLY_PROVED |
| R4 | maximum newly created directories | PROVED_STATIC_BOUND |
| R5 | whole interpreter RSS/working-set budget and enforcement | RUNTIME_MEASUREMENT_REQUIRED |
| R6 | actual total cumulative payload write-byte ceiling | PROVED_STATIC_BOUND |
| R7 | complete normal/failure evidence demand within each artifact cap | UNPROVEN |
| R8 | 120s external supervision/abort/cleanup contract | UNPROVEN |

## 源级部分上界

- 固定54变体路径最多调用23次FaultSchedule.arm。其余直接时钟、模式及输入配置采用独立计量；全部故障控制总量仍需接受计数定义。实际发生次数NOT_MEASURED。
- 夹具和自有RLock总准入上界55，包含T26的独立嵌套夹具；逻辑并存最多2。模型流实例保守总上界71、单夹具文件最多4；文件缓冲cap包络1703936B。隐式运行时锁/句柄及Python分配峰值另列未知。
- reserve_owned_output固定创建两个新层级，exist_ok=false，拒绝现有目标。原申请没有目录总额度，批准值仍null。
- 8个可达native产物各最多一次payload-write；未实现的physical_journal不分配。从原999424九份cap减65536，得到933888B累计显式驱动payload条件上界。短写/未知保持整请求charge，无覆盖、退款、temp或rename。
- 当前明确控制读取最多10个文件，显式Native文件close至多18次。此数没有覆盖importer、linecache、隐式loader和OS内部操作，不能当全程I/O上界。

上述值登记为控制流/整数STATIC_BOUND；实际发生量保持NOT_MEASURED，批准额度另行审定。

## 仍未闭合

R1需要故障arm、直接配置和时钟更新的统一计量定义与批准值；R2仍缺完整逐操作及隐式native界；R3需对显式/隐式资源和失败并存峰值分别批准；R4缺原目录额度；R5缺整进程批准上限和硬预防机制；R6缺针对累计写入单位的明确批准；R7缺正常与所有失败负载的联合适配；R8缺从真实进程启动到安全收尾的硬监督证明。

内存已实现只读OS生命周期peak采样，实际仍NOT_MEASURED。旧32MiB请求只覆盖测试自有数据；不能用它替代整个解释器峰值。采样检测与硬内存限制分别管理。

真实120秒门从观察器初始化计时，bootstrap之前及inflight原生阻塞/close需外部监督。driver要求未来packet声明监督已批准，但本轮没有提供对应可执行监督证据，硬保证仍UNPROVEN。

9个cap之和、guard拒绝和933888B显式写包络各保留其范围。完整异常文字和未预期故障可能使某个artifact不适配，R7保持UNPROVEN；没有通过截断、删字段或自动重跑制造通过。

全部8项批准最大值仍缺，因此R43_EIGHT_RESOURCE_BUDGETS_CLOSED=false。当前实际临时运行资源0、动态0，本轮没有扩大2MiB或120秒合同。
