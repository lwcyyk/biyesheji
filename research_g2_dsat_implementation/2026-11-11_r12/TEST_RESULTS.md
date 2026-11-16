# B1实际测试结果

最终来源：`../2026-11-10_r12_b1/run_004/RESULTS.json`及stdout.log。

| 口径 | 实际结果 |
|---|---|
| 冻结ID总数 | 36 |
| 获准B1执行 | 33 |
| PASS / FAIL / ERROR / SKIP | 33 / 0 / 0 / 0 |
| BLOCKED | 3：B15、B27、B28，R11明确属于B2 |
| 获准范围未执行 | 0 |
| 内部断言 | 551项满足 |

33项分别覆盖原矩阵B01–B14、B16–B26、B29–B36。B2三项未建立可执行测试方法，ID及原始期望仍在结果中，登记executed=false。R12要求沿用更窄的R11边界，因此本轮没有以合成执行名义开展B2。

## 运行历史

| run | 结果 | 修改或用途 |
|---|---|---|
| 001 | 32 PASS、1 FAIL、3 BLOCKED | 缺attempt_id的拒绝码与tuple期望不符；保留全部记录 |
| 002 | 33 PASS、3 BLOCKED | 缺失放行tuple统一为SOURCE_BINDING_CONFLICT |
| 003 | 33 PASS、3 BLOCKED | 费用改用高分辨率perf_counter，来源观察时钟继续monotonic |
| 004 | 33 PASS、3 BLOCKED | 并行用例增加4线程起始barrier和线程身份记录，最终冻结版本 |

没有删除、合并或重写R11矩阵。全部源码快照、输入/代码SHA、命令、解释器、时间、错误与业务状态均保留在各run。原R07/R10用例未重跑，历史分母未并入本轮。

## 业务状态与测试结果

最终75个Staging输出含54个STAGING_READY_WITH_GAPS和21个按预期拒绝/缺口结果。66次源读取尝试，其余在权限、scope、请求或配额门前拒绝。UNKNOWN/REJECT类结果在满足断言时记测试PASS，业务状态仍按原码记录。

全部公开sink哨兵扫描CLEAN，日志哨兵脱敏次数0。安全审计sqlite/network/process/private-file计数均0。Schema嵌套未知字段、对象分离、跨scope元数据和强关闭请求阻断均实际检查。

## 费用

最终完整运行0.763910秒，含预检/后检921次哈希及模块加载等。63次常规接口调用累计39.481ms；4线程12次批次墙钟10.593ms。75个输出中的源读计时累计0.0306ms、投影提取8.9309ms；接口总计时还包括校验、摘要、Schema与对象序列化，区间不能机械相加。

费用用QueryPerformanceCounter（分辨率1e-7秒）；来源观察用GetTickCount64的monotonic（分辨率0.015625秒）。早期run的短读观察差为0属于时钟分辨率，本轮没有把它解释为读取免费。

以上均为reader-double CPU测试数据。真实整状态解密、key访问、SQL/锁等待、日志fsync和网络成本NOT_MEASURED；S2优化器与数学检查器本轮NOT_RUN。
