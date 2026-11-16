# R6-B 本地证据：从这里开始

本包为实际资源校准失败记录，RESOURCE_GATE_FAILED。F1/F4未启动；源码存在与模型检查通过分别登记。

1. 阅读 [机器结果](reports/RUN_RESULTS.json) 和 [校准记录](reports/RESOURCE_CALIBRATION.s2.json)。
2. v1首次API设置失败见 [首次失败](reports/RESOURCE_SETUP.s1.json) 及raw/launch.s1.txt；v2原始资源报告见 [批次](reports/BATCH.2.json)。
3. AUTHORIZATION_RECEIPT/TEXT记录明确许可；EXECUTION_COMMANDS记录两次实际命令。统一起点/绝对deadline在BATCH_STATE，visits.bin为带锁计数原件（27次均校准）。
4. src含八程序，versions/v1和v2保存源码/锁；F1/F4模型输入生成器未执行，inputs中实际物化的是批计划，calibration下有实际probe输入/响应/局部计数。
5. EVIDENCE_MANIFEST逐文件锁定包内工件；包外EVIDENCE_SHA256记录ZIP摘要及流式校验。

本批峰值判据失败，剩余独立WS/异常/时间/子树校准与正式模型均未执行。BATCH.2中的配置推导树界未通过认证；树WS采样为下界，精确聚合峰值null。v1初始化前峰值缺测。当前没有协议PASS_BOUNDED，也没有观察到协议模型反例。

本包只在本地保存，未上传。源码/日志/计划/失败可供复查；未来运行仍需遵守对应资源门及批次范围，不能以复现为由清零原计数/时间或启动原生操作。