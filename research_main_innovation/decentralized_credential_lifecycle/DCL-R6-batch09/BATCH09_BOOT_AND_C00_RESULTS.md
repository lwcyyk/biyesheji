# batch09启动连续性与C00结果

Material Passport：DCL-R6-batch09；2026-11-12；静态准入停止；本轮动态观察0。

**启动连续性和C00均为UNRUN_STATIC_ADMISSION。** Windows冻结入口调用0，WSL调用0，同进程exec0，sealed凭据生成0，认领0。当前boot_id/PID/starttime均null；本轮没有借用历史动态资格。

待运行八项为Uid=[999]、Gid=[989]、Groups=[989]、CapEff=0、NoNewPrivs=1、LimitAS=1073741824、LimitASSoft=1073741824，以及新批次对应的ControlGroup。最后一项在冻结r2中仍固定为batch08单位路径，新batch09期望尚待独立命名空间冻结。八项本轮observed均null。

batch08历史证据保留C00_PASS、STARTING→READY、最终八项双侧MATCH；屏障返回区间0.149840881–0.155141782秒。该结果只归属于旧批次。batch07具体失败字段继续C00_FAILED_FIELD_UNRESOLVED。

独立pidfd时刻、后侧stat及精确wait返回点观测缺口继续保留；冻结正式门依赖实际pidfd/identity控制流及原生READY证书，额外打点未成为必需schema。本轮诊断状态为UNRUN，旧batch08的FIELD_EVIDENCE_PARTIAL保持原裁决。

[准入说明](BATCH09_STATIC_ADMISSION.md)；[锁](evidence/STATIC_EXECUTION_LOCK.json)；[旧包直接核验](evidence/BATCH08_ARCHIVE_CHECK.json)。
