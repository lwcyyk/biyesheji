# batch09 S1–S9结果

Material Passport：DCL-R6-batch09；2026-11-12；静态核对34 job；动态0。

|责任|冻结覆盖|本轮|
|---|---|---|
|S1|预留前退出与提前grant变异|UNRUN_STATIC_ADMISSION|
|S2|三个PREP确认层次及保守占用|UNRUN_STATIC_ADMISSION|
|S3|持久化后发放前退出/重复派发|UNRUN_STATIC_ADMISSION|
|S4|信用认领后退出/信用重复发放|UNRUN_STATIC_ADMISSION|
|S5|相同/冲突task_id请求|UNRUN_STATIC_ADMISSION|
|S6|双actor并发屏障与重叠范围变异|UNRUN_STATIC_ADMISSION|
|S7|短写原字节及合成fsync EIO|UNRUN_STATIC_ADMISSION|
|S8|CLOSED、过期、boot/锁漂移、重初始化|UNRUN_STATIC_ADMISSION|
|S9|第N+1及N+2次拒绝|UNRUN_STATIC_ADMISSION|

34项由17 safe及17 mutant构成。生产预算核心与局部合成账分离，故障只作用受锁RANGE镜像。本轮fault_triggered、oracle_detected、原始轨迹及实际访问均null，未作NOT_EXERCISED或MUTATION_NOT_DETECTED的动态裁决。

RANGE硬限20,000包含driver、worker、即时检查、Root原始重算及17项门审核的计费。旧合同声明完成路径19,229；本轮资源准入采用20,000硬上界。局部合成账故障覆盖和“当前全局账异常时资源资格门拒绝”的独立负向覆盖分别登记，后者尚待补齐。

[完整case_id](evidence/FROZEN_TEST_INVENTORY.json)；[负向覆盖缺项](BATCH09_GATE_NEGATIVE_RESULTS.md)。
