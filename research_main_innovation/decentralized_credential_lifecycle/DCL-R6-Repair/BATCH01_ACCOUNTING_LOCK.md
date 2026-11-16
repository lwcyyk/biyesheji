# batch01历史账与到期锁

2026-11-10。只读核对记录在[evidence/BATCH01_ACCOUNTING_VIEW.json](evidence/BATCH01_ACCOUNTING_VIEW.json)。

|字段|原值/实际检查|
|---|---|
|历史访问|27，visits.bin偏移8的uint64，原cap为1000000|
|历史实际消耗时间|118.7340827秒至v2退出，原BATCH.2记录保持|
|原start_monotonic_ns|706251332907000|
|原deadline_monotonic_ns|708051332907000|
|原UTC deadline|2026-11-10 05:32:39.337 UTC，即13:32:39.337 Asia/Shanghai|
|本轮只读观察|05:55 UTC之后，QPC换算值已大于原deadline|
|关闭状态|CLOSED_RESOURCE_GATE_FAILED|
|原文件/ZIP|62个批次文件、60项ZIP，59条manifest＋manifest本身均核对|
|本轮新校准/模型|0 / 0|

数字上尚未用完的999973次访问不构成有效运行资格；原绝对时间窗和关闭状态同时约束执行。历史118.7340827不会改写为本轮静态分析到现在的累计墙钟，更不会换成新的1800秒起点。

本轮只在versions/v3新增静态候选和版本文件，没有修改batch01/src、inputs/batch01.json、visits.bin、BATCH_STATE、原raw/calibration/reports、v1/v2或原ZIP。证据manifest原条目SHA继续固定；新v3不自动纳入原ZIP，也不追改旧manifest。新版本另用V3_SOURCE_LOCK登记。

v3修补为启动前先检查关闭/deadline/授权root；缺状态不建新窗口；global counter不由普通程序自动初始化。该拒绝路径目前只完成源码审查，没有借到期批次实际测试它。

新批次必须有自己的明确授权/编号/目录/资源账，并披露原27次失败成本。当前未创建batch02。所有新额度、适配器和运行行为仍待技术前置及授权，旧许可不自动生成新账。
