# DCL-R6阶段B当前入口

2026-11-10。专项许可已取得，八个程序已创建，**RESOURCE_GATE_FAILED**。正式F1/F4均为**UNRUN_RESOURCE_GATE**，未取得任何PASS_BOUNDED。

主要入口：[最终裁决](R6_FINAL_DECISION.md)、[资源校准报告](R6_RESOURCE_CALIBRATION_REPORT.md)、[机器清单](evidence/stage_B/RUN_RESULTS.json)、[F1结果](R6_F1_RESULTS.md)、[F4结果](R6_F4_RESULTS.md)、[失败登记](R6_COUNTEREXAMPLE_REGISTER.md)。

两轮资源控制器共享27次校准访问与原计时起点；v1参数设置失败，v2正常/计数通过、内存峰值判据失败。按授权失败分支停止，原生/构建/下载/外发0。源码与全部失败在独立batch01和versions目录保存；阶段A原件在evidence/stage_A锁存。

F1/F4规格与映射保留阶段A冻结内容，其中旧状态词仅描述当时；当前许可/执行以本页、结果和证据索引为准。主机制门CLOSED、严格分离0、强G覆盖保持。

下方为阶段A索引历史。

---
# DCL-R6阶段A索引

2026-11-10。[最终裁决](R6_FINAL_DECISION.md)为当前入口。F1/F4尚无专项执行许可，均UNRUN_PERMISSION；机制实现门CLOSED。当前只完成只读工具/规格预审与待授权合同。

|材料|用途|
|---|---|
|[验证范围](R6_VERIFICATION_SCOPE.md)|权限、证据等级与准入标签|
|[形式化映射](R6_FORMAL_MODEL_MAPPING.md)|纸面协议→对象/转换→性质→未来证据及抽象缺口|
|[F1规格](R6_F1_SPECIFICATION.md)|多Cfg/独立RHO监视、INV1–8及有限族|
|[F4规格](R6_F4_SPECIFICATION.md)|D2-DP/TRACE-REF、夹具、G64与交叉规则|
|[工具与专项申请](R6_TOOLCHAIN_AND_PERMISSION.md)|本机版本、资源硬界/校准、八程序和具体命令|
|[执行清单](R6_EXECUTION_MANIFEST.md)|真实阶段A操作与待授权字段|
|[反例登记](R6_COUNTEREXAMPLE_REGISTER.md)|纸面预期与未来首次失败保留|
|[F1结果](R6_F1_RESULTS.md)、[F4结果](R6_F4_RESULTS.md)|明确UNRUN_PERMISSION，不预填执行值|
|[来源索引](R6_SOURCE_INDEX.json)|基线/工具/许可/公开文档证据|

R5及此前资料直接复用，盲审第一阶段包与答案继续隔离。当前没有验证代码、模型结果日志、下载、原生调用或外发。若之后取得专项许可，执行输出置于新隔离目录，按本轮合同锁版本/资源并保存失败。
