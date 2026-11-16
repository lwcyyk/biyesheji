# R6-F1阶段B实际结果

2026-11-10。专项授权已取得；**UNRUN_RESOURCE_GATE**。资源校准在memory测试失败，控制器未启动run_batch，F1模块也未被正式检查进程导入。

|字段|实际状态|
|---|---|
|源码|f1_model.py与f1_check.py已创建，v1/v2快照及SHA-256保留|
|baseline/mutant/反例重放运行|0 / 0 / 0|
|INV1–INV8|全部UNRUN_RESOURCE_GATE|
|F1实际访问/生成/不同状态数|未测，null；批次27次计数全部来自资源校准|
|F1执行时间/峰值/退出码|未测，null；资源控制器退出码另列|
|机器反例/最短轨迹|0条已观察；轨迹与最短长度null|
|PASS_BOUNDED性质|空集合|

已写源码采用每Cfg日志/Stop历史、独立ghost账和原发送权持久状态，尚无运行结果认证其正确性或完整域覆盖。节点故障的逐副本展开、全部数据接续交错及实际PBFT/原生精化仍需单独核对；程序文件存在不授予PASS_BOUNDED。

实际阻碍见[资源校准分析](R6_RESOURCE_CALIBRATION_REPORT.md)与[evidence/stage_B/RUN_RESULTS.json](evidence/stage_B/RUN_RESULTS.json)。初版设置错误与后续内存校准均保留。当前0条模型反例只表示正式验证尚未进行，不能据此推断协议无缺陷。

D1-PBFT-SEAL/1.1保持原纸面条件结论，无运行证据要求其升级。本阶段未新增F1的LEVEL-3或LEVEL-4证据。
