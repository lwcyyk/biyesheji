# R6阶段B当前范围与结果

2026-11-10。专项授权EXPLICITLY_AUTHORIZED。八程序创建完成，资源设置/校准已实际执行；资源门RESOURCE_GATE_FAILED，F1/F4状态UNRUN_RESOURCE_GATE。正式baseline/变异/参考/重放均0，协议PASS_BOUNDED为空。

当前完成的是授权范围内的资源执行证据和失败分支交付。原生、构建、外发及主系统机制0，R1–R5保持冻结，IMPLEMENTATION_GATE=CLOSED。[实际裁决](R6_FINAL_DECISION.md)与[资源报告](R6_RESOURCE_CALIBRATION_REPORT.md)优先；下方为阶段A范围历史。

---
# R6验证范围与准入状态

2026-11-10，Asia/Shanghai。阶段A已获当前任务授权；阶段B需要另行明确许可。当前会话及R5登记材料中未取得范围匹配的F1/F4专项执行收据，故`VERIFICATION_STATUS=UNRUN_PERMISSION`、`IMPLEMENTATION_GATE=CLOSED`。

## 1. 本轮实际工作

读取R5合同/裁决、D1业务与PBFT接续规格、D2费用语义及组合合同；核对历史锁；检查PATH和常见已存在目录的工具文件；仅运行现有Java/Python版本查询；读取官方工具/Windows资源管理说明；形成精确有限关系、反例预期、独立参考合同与待授权命令。模型/参考/监督代码创建0，模型运行0，依赖下载0，原生请求0。

工具版本查询属于阶段A的可执行性检查，分别登记为TOOL_VERSION_ONLY；文件哈希、JSON和路径检查属于ADMIN_CHECK。两类均不进入模型检查次数、访问状态数或LEVEL-3统计。

## 2. 允许申请的最小阶段B

拟采用现有Python3.14.0和标准库，在`D:/毕业设计/DCL-R6-isolated-verification/batch01`创建资源监督/校准、F1显式状态检查、F4阈值算法、F4独立策略穷举与证据审计程序；无依赖下载。先校准硬资源门，合格后顺序F1→F4。F1是自编显式状态检查器，不能登记为TLC执行或通用定理证明；其转换、监视器与反例重放须可审。

单批合计访问状态≤1,000,000、墙钟≤1800秒、进程树峰值内存≤4GiB；baseline、mutant、参考枚举、校准及失败均共享资源，不自动重置。内存口径和硬限制资格见[R6_TOOLCHAIN_AND_PERMISSION.md](R6_TOOLCHAIN_AND_PERMISSION.md)。工具/模型源码实际生成后锁哈希；尚未生成的摘要保持null。

## 3. 证据边界

F1以每Cfg内静态PBFT oracle为前提，检查跨Cfg连接与应用不变量，不实现PBFT网络/密码学。原生事件只抽象为有来源的发送/到达/结果；具体缓存handler、NC1/2、NativeCreationCut属于F2/原生精化。B实际S2(T)、时钟与服务界属于F3。Casdoor dirty对应、Gate/V秘密流及真实部署继续待证。

F4检查精确有限模型中算法与独立轨迹参考的一致性；结果不能外推到未编码原生行为、无限h、未来效果或公开原创性。强G获同能力/观察/工具，严格分离0、I1/I2/I3归档保持。

|结果标签|授予条件|
|---|---|
|UNRUN_PERMISSION|当前状态；实际检查字段null、运行计数0|
|PASS_BOUNDED|获准运行，完整指定域、所有声明监视器和覆盖/变异校准完成；范围写明|
|COUNTEREXAMPLE_FOUND|保存输入、完整事件/选择/费用轨迹和首次失败；再分类协议/假设/抽象/实现问题|
|INCONCLUSIVE_LIMIT|任一批次资源界触发；保留已查子域，未完成范围不记PASS|
|ABSTRACTION_GAP / INVALID_MODEL|漏真实步骤、观察/后继不完整、域溢出或不合法输入，分别登记|

## 4. 当前验收

Gate R6-A=CONDITIONAL_PASS于规格/映射准备，代码对照与运行覆盖待授权；R6-B=UNRUN_PERMISSION；R6-C=CONDITIONAL_PASS于证明责任分解；R6-D=PASS于路线决策。当前LEVEL-1/2资料保留，LEVEL-3/4/5新增证据均0。独立参考指未来实现逻辑不同，不赋予同会话外部审稿独立性。
