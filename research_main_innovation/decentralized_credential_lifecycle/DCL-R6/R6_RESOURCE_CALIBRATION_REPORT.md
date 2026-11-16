# R6阶段B资源监督校准与失败分析

2026-11-10。专项许可已明确，执行依据保存在[evidence/STAGE_B_AUTHORIZATION.txt](evidence/STAGE_B_AUTHORIZATION.txt)。本批结果为**RESOURCE_GATE_FAILED**，正式F1/F4均未启动。八个授权程序已写入隔离目录，未修改主系统机制及R1–R5冻结工件。

## 1. 实际执行与资源账

执行目录为`D:/毕业设计/DCL-R6-isolated-verification/batch01`。共两次资源控制器启动，沿用同一BATCH_STATE起点、绝对deadline和visits.bin，未重置30分钟/100万计数。两次程序版本和锁各存versions/v1、versions/v2。

|项目|实际记录|
|---|---|
|Python/OS|Python3.14.0，MSC v1944，AMD64；Windows10.0.26200|
|授权总界|1,000,000访问；1800秒；4,294,967,296字节进程树峰值内存|
|从首次启动到v2退出|118.7340827秒，包含两次间的核对/修订间隔|
|统一访问计数|27；全部是校准入口/局部额度/内存分配探针处理，正式模型0|
|v2主Job报告的提交内存峰值|145,354,752字节；配置总提交限额4GiB|
|进程树working-set实测精确峰值|null；采样聚合值仅为下界，不能认证硬上界|
|所见树working-set采样最大下界|97,099,776字节|
|v2控制器退出|2，RESOURCE_GATE_FAILED；watchdog正常退出0|
|已记录存活进程复查|控制器/三个probe/watchdog所列PID均未发现继续运行；退出状态/等待另有记录|

原始报告中`enforced_tree_ws_upper_bound=3GiB`是“每进程768MiB×最多4进程”的配置推导值。本次校准未通过，该字段不能充任已验收的树峰值保证。实际Job提交峰值、单进程working-set峰值、采样树值及配置目标分列。

## 2. 首次失败与修订

v1在给空Job设置包含WORKINGSET的组合参数时，SetInformationJobObject返回Win32错误87；发生于关联根进程/启动校准之前。完整异常、启动命令和退出2已保留，首轮峰值因初始化提前失败未测，记null。

v2将Job用于总提交/活动进程数/KILL_ON_JOB_CLOSE，成员进程在Resume前单独设置并读取HARDWS_MAX标志。设置成功，实际进入正常/计数/内存三个校准。官方Job说明指出Job固定working-set范围后成员不能再改变范围；此处拆分职责有文档依据。当前未穷尽确认v1错误87的唯一根因，不能仅据v2成功就断言某一个参数是唯一原因。

|Failure → Root Cause → Fix → Recheck → Verdict|
|---|
|v1设置返回87 → 初版配置/参数问题，唯一原因未穷尽 → 分离Job聚合限制与成员HardWS → v2设置及前两探针成功 → 初始化层修正有实际证据，完整资源资格仍未通过|
|v2内存校准断言失败 → 峰值统计/失败预留/页粒度与限额口径未闭合 → 仅提出下节修复需求，未调整容差重跑 → 正式验证停止 → RESOURCE_GATE_FAILED|

## 3. 内存失败的精确观察

|指标|配置/目标|实际报告|差值|
|---|---:|---:|---:|
|测试Job提交限额/峰值|100,663,296字节（96MiB）|115,167,232字节（109.83203125MiB）|14,503,936字节|
|测试进程硬WS最大值/峰值|33,554,432字节（32MiB）|33,558,528字节|4,096字节|
|Python分配|有界16MiB块、最多16块|实际保留5块后捕获MemoryError|异常后释放并写证据，进程退出0|

OS查询返回HARDWS_MAX启用（flags=6），且记录了MemoryError；这两项成立仍不足以满足当前严格峰值断言。Job峰值可能涉及失败提交的暂态计账，working-set峰值可能涉及页面粒度/时序；这些是待核假说。本次未对它们作实际机制归因，也未把差值视为获准容差。

此观察没有显示实际整个批次超过4GiB。失败结论是监督器尚未给出与授权指标匹配的可核验保证；不能用采样较低、堆较小或只测commit来替代该保证后继续运行。

## 4. 校准覆盖

|校准项|实际结果|
|---|---|
|正常结束|PASS，退出0，有内存/退出记录|
|计数上限|局部cap17成功处理17、拒第18；同一reserve函数向批总账收费；全局当前27|
|内存超限/峰值匹配|FAIL：MemoryError已观测，峰值断言不满足|
|单独working-set探针|UNRUN，前一项失败后未继续|
|异常退出、超时强制终止|UNRUN|
|子树终止、父退出/中断后证据、breakaway|UNRUN|
|正式F1/F4|UNRUN_RESOURCE_GATE|

不能把已执行三项称为全部校准通过。尤其墙钟/子孙终止尚未动态校准，仍是资格缺口。

## 5. 最小修复需求

1. 对测试Job峰值是否计入失败/暂态预留，及hard-WS峰值页粒度作独立、可复查的计账取证，明确目标的聚合峰值口径。
2. 给出全部允许进程/子孙的硬WS、数量及瞬时/舍入上界组合，证明总峰值≤4GiB；不能只将4KiB差值写为容差。提交限额与物理WS仍分开。
3. 锁定修订监督器及资格判据，保留v1/v2原件，再完整校准未执行的异常/时间/子树/中断项。只有整体RESOURCE_GATE_PASS后才允许正式验证。
4. 原batch01的起点/计数不得清零；本次已按失败分支停止。若后续任务使用新的批次/时间预算或额外工具，须遵守相应明确范围，不能借修复自动扩额。

本次没有原生请求、构建、依赖安装、外部发送或F2/F3执行。资源失败属于验证基础设施/计账责任，尚无D1/D2原协议缺陷结论。

## 6. 证据入口

[实际机器清单](evidence/stage_B/RUN_RESULTS.json)、[首轮设置失败](evidence/stage_B/RESOURCE_SETUP.s1.json)、[v2校准记录](evidence/stage_B/RESOURCE_CALIBRATION.s2.json)、[v2批次资源](evidence/stage_B/BATCH.2.json)、[watchdog退出](evidence/stage_B/BATCH.2.watchdog.json)。隔离目录还保留raw、calibration二进制计数、两个源版本及完整文件锁；本地证据包与哈希见更新后的来源/交付索引。

[本地完整证据ZIP](D:/毕业设计/DCL-R6-isolated-verification/batch01/DCL-R6-B_EVIDENCE.zip)包含60项，59个manifest条目及manifest本身均已流式核验。[ZIP校验记录](evidence/stage_B/EVIDENCE_SHA256.json)属于ADMIN_CHECK，不承担资源资格或协议验证通过结论。
