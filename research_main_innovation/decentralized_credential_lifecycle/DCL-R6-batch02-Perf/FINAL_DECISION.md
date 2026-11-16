# batch02-Perf最终裁决

2026-11-10。Material Passport：离线证据诊断、纸面修复与准入准备。直接核验两个ZIP及batch02原始文件hash，未启动Linux/探针/校准/模型，未改代码/配置/旧结果/副本，batch03未创建。

## 核心结论

300秒起于共同T0。C00/C01结果只用T0后1.109256092秒；C02首预付PREP4至末PREP32191为298.626607199秒，占软窗99.5422%。32187个相邻预付周期均值9.277864ms、约107.783周期/s。这定位了逐信用持久预付这一真实控制流瓶颈；没有把全部时间归给磁盘fsync。

32191项拆为C00入口1、C01入口1、C02入口1、未启动child预付32188。模型状态/内存子操作均0。所有PREP/COMMIT对复用同一时标，不能算出同步耗时；每完整事务7同步是源码计数，225337是静态机会值，实际syscall/锁/序列化细分仍UNKNOWN_INTERVAL。

主选A0：已知N的有界child一次精确N持久范围、一次委派，不删持久屏障、不退款、不改普通模型visit，cal300/100000及总资源合同保持。4KiB下C02同步事务数从32896到1；墙钟收益尚未测。B/C均保留比较，秒级启动复用无法针对298秒主区间，窗口放宽须另批。

## Gate

|Gate|状态|含义|
|---|---|---|
|PERF-1 失败归因|PASS_STATIC|共享截止/里程碑与预付主区间已重建；未记时的细分明确UNKNOWN|
|PERF-2 预算成本|PASS_STATIC|32191来源/状态/配对、时间复用、O(1)逐次路径及混合分布有据|
|PERF-3 最小修复|CONDITIONAL_PASS|精确范围的BUD条件证明/失败/浪费与测试责任完整，尚无代码或动态验证|
|PERF-4 新批准入|PARTIAL|有限静态修复与B03申请已具体化；未获编程许可，实际新hash/完整执行锁尚缺|

原C00/C01局部PASS、C02原FAIL/分析INCONCLUSIVE_LIMIT不改。RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；原WS4 E2=UNRESOLVED；D1 1.1/D2条件结论、G覆盖/归档、严格分离0及主机制门CLOSED保持。新增机制代码、性能/资源探针、Linux命令和执行环境均0。

## 副本与后续决定

误路径47文件只读hash均与正确封存对应，原拒绝blocked by policy保留。本轮无清理/迁移/改名/覆盖/提权或替代接口尝试。未来批次只接受正确根和冻结hash，副本不作为正式输入；处置另提独立整理申请，不阻碍本轮研究。

下一项可审批决定是[BATCH03_AUTHORIZATION_REQUEST](BATCH03_AUTHORIZATION_REQUEST.md)中的P-R03有限静态修复；实际源/配置/命令锁完成后再申请B03动态资格及模型。若未来计时仍缺，按已列有界测点先诊断，保持窗口与安全性质分别验收。

[时间线](PERF_EXECUTION_TIMELINE.md)、[账审查](PERF_BUDGET_LEDGER_AUDIT.md)、[成本](PERF_PERSISTENCE_COST_ANALYSIS.md)、[安全证明](PERF_BUDGET_SAFETY_PROOF.md)、[来源索引](SOURCE_INDEX.json)、[交付核对](evidence/DELIVERY_CHECK.json)。
