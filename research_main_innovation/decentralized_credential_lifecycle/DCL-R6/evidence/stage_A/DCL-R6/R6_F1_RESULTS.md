# R6-F1结果登记

2026-11-10。**UNRUN_PERMISSION**。

|字段|实际状态|
|---|---|
|模型程序/显式checker|未创建|
|baseline运行次数|0|
|mutant运行次数|0|
|访问/生成/不同状态数|未测，null|
|实际执行时间/进程树内存峰值|未测，null|
|实际反例/最短轨迹/退出码|未产生，null|
|INV1–INV8机器判定|均UNRUN_PERMISSION|
|PASS_BOUNDED/LEVEL-3授予|尚待实际执行|

已完成的是[F1有限规格](R6_F1_SPECIFICATION.md)、[模型映射与遗漏审查](R6_FORMAL_MODEL_MAPPING.md)、[反例输入登记](R6_COUNTEREXAMPLE_REGISTER.md)及[工具/权限/资源合同](R6_TOOLCHAIN_AND_PERMISSION.md)。Java/Python版本检查及工件哈希不属于F1运行。

本轮静态审计避免三类错误验证：单一current结构强制排除双头；RHO/监视器共同遗漏同字段；把撤销后的已登记迟到IO全部判错或从模型删掉。它们是模型构造责任，尚无工具轨迹支持或否定某一实现。

协议D1-PBFT-SEAL/1.1保持原CONDITIONAL_PROTOCOL_COMPLETE纸面范围，未提升真实部署、无界安全或正式机器证明等级。专项许可、资源门与代码/输入锁齐备后，再按F1顺序记录真实结果。
